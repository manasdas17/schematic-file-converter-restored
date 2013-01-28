#!/usr/bin/env python2
""" The NC drill/ICP-NC-349 Format Writer """

# upconvert.py - A universal hardware design file format converter using
# Format:       upverter.com/resources/open-json-format/
# Development:  github.com/upverter/schematic-file-converter
#
# Copyright 2011 Upverter, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from sys import stdout
from os import path, mkdir, listdir, makedirs, stat
from shutil import rmtree
import logging

from upconvert.core.component_instance import FootprintPos
from upconvert.core.shape import Circle, Point, Line


log = logging.getLogger('writer.ncdrill')


# exceptions

class Unwritable(ValueError):
    """ Parent class for all gerber writer errors. """
    pass


# constants
#
# http://www.excellon.com/manuals/program.htm


LINE = '{0}\r\n'
REWIND_AND_STOP = '%'
TOOL_SELECT = 'T{code}'
END_FILE = 'M30'
END_FILE_OTHER = 'M00'
UNLOAD_TOOL = 'T00'
START_PATTERN = 'M25'
START_PATTERN_OTHER = 'M31'
END_PATTERN = 'M01'
LOCATION = 'X{x}Y{y}'
REPEAT_PATTERN = 'M02X{x}Y{y}'
MULTI_REPEAT_PATTERN = 'R{num}M02X{x}Y{y}'
SWAP_AXIS = 'M02X{x}Y{y}M70'
MIRROR_IMAGE_X_AXIS = 'M02X{x}Y{y}M80'
MIRROR_IMAGE_y_AXIS = 'M02X{x}Y{y}M90'
END_STEP_REPEAT = 'M08'
BLOCK_SEQUENCE_NUM = 'N{seq_num}'
BLOCK_DELETE = '/'
REPEAT_HOLE = 'R{num}X{x}Y{y}'
SELECT_DRILL_MODE = 'G05'
SELECT_DRILL_MODE_OTHER = 'G81'
VARIABLE_DWELL = 'G04X{x}' # ignored
ABSOLUTE_MODE = 'G90'
INCREMENTAL_MODE = 'G91'
SET_ZERO = 'G92X{x}Y{y}'
SET_ZERO_OTHER = 'G93X{x}Y{y}'
PROGRAM_HEADER_TO_FIRST_REWIND = 'M48'
OPERATOR_MESSAGE_CRT_DISPLAY = 'M47'
METRIC_MODE = 'M71'
IMPERIAL_MODE = 'M72'
SPINDLE_SPEED = 'S{rpm}'
Z_AZIS_FEED_SPEED = 'F{IPM}'
FORMAT_VERSION = 'FMAT,{ver}'
IMPERIAL_UNITS_LEADING_ZERO = 'M71,TZ'
METRIC_UNITS_LEADING_ZERO = 'M72,TZ'  # also seen as METRIC,TZ

TOOL_DEFINITION = 'T{code}C{diameter}'
TOOL_DEFINITION_SPEED = 'T{code}C{diameter}F{infeed}S{krpm}'


class Hole:
    def __init__(self, shape):
        self.shape = shape
        self.locations = []

# writer

class NCDrill:
    """ The Gerber Format Writer. """

    def __init__(self):
        self.coord_format = None
        self._reset()

    def _reset(self):
        # Map of holes keyed by radius
        self._holes = {}
        self.status = {'x':0,
                       'y':0,
                       'units':None,
                       'incremental_coords':None}


    def write(self, design, outfile_name=None):
        """ Entry point for producing a NC Drill file. """
        log.debug('starting NC Drill file write to %s', outfile_name)
        if outfile_name:
            dir_ = path.dirname(outfile_name)
            if dir_:
                try:
                    stat(dir_)
                except OSError:
                    makedirs(dir_)

        self._define_tools(design)

        with outfile_name and open(outfile_name, 'w') or stdout as f:
            self._write_header(design, f)
            self._write_body(f)

    def _add_hole(self, parent_attr, body_attr, shape):
        if not isinstance(shape, Circle):
            raise Unwritable('all holes must be circular')

        pos = Point(shape.x, shape.y)
        pos.shift(body_attr.x, body_attr.y)
        if parent_attr:
            if parent_attr.rotation != 0:
                pos.rotate(parent_attr.rotation)
            if parent_attr.flip_horizontal:
                pos.flip(parent_attr.flip_horizontal)
            pos.shift(parent_attr.x, parent_attr.y)

        if body_attr.rotation != 0:
            if parent_attr and parent_attr.flip_horizontal:
                pos.rotate(-body_attr.rotation, in_place=True)
            else:
                pos.rotate(body_attr.rotation, in_place=True)
        if body_attr.flip_horizontal:
            shape.flip(body_attr.flip_horizontal)

        log.debug('adding %d hole at %d, %d', shape.radius * 2, pos.x, pos.y)
        if shape.radius not in self._holes:
            self._holes[shape.radius] = Hole(shape)
        self._holes[shape.radius].locations.append(pos)


    def _define_tools(self, design):
        log.debug('building tool list for holes layer')
        hole_layer = 'hole'

        # Skipping segments, no holes

        # Generated objects in the design (vias, PTHs)
        log.debug('design generated objects')
        zero_pos = FootprintPos(0, 0, 0.0, False, 'top')
        for gen_obj in design.layout_objects:
            # XXX(shamer): body attr is only being used to hold the layer, other placement details are contained
            # elsewhere
            for body_attr, body in gen_obj.bodies(zero_pos, {}):
                if body_attr.layer == hole_layer:
                    for shape in body.shapes:
                        self._add_hole(None, body_attr, shape)

        # Component instance aspects
        log.debug('component instances')
        for component_instance in design.component_instances:
            component = design.components.components[component_instance.library_id]
            footprint_pos = component_instance.footprint_pos
            # Skip unplaced footprints
            if footprint_pos.side is None:
                continue

            for idx, footprint_attr in enumerate(component_instance.footprint_attributes):
                log.debug('footprint pos: %s, side %s, flip %s', footprint_attr.layer, footprint_pos.side, footprint_pos.flip_horizontal)
                if footprint_attr.layer:
                    footprint_attr.layer = footprint_attr.layer.replace('top', footprint_pos.side)
                if footprint_attr.layer == hole_layer:
                    footprint_body = component.footprints[component_instance.footprint_index].bodies[idx]
                    log.debug('adding footprint attribute: %s, %d shapes', footprint_attr, len(footprint_body.shapes))
                    for shape in footprint_body.shapes:
                        self._add_hole(footprint_pos, footprint_attr, shape)

            for idx, gen_obj_attr in enumerate(component_instance.gen_obj_attributes):
                gen_obj = component.footprints[component_instance.footprint_index].gen_objs[idx]
                # FIXME(shamer): check for unplaced generated objects.

                # XXX(shamer): body attr is only being used to hold the layer, other placement details are contained
                # elsewhere
                for body_attr, body in gen_obj.bodies(footprint_pos, gen_obj_attr.attributes):
                    if body_attr.layer == hole_layer:
                        log.debug('adding body for generated object: %s, %s', footprint_pos, gen_obj_attr)
                        for shape in body.shapes:
                            self._add_hole(footprint_pos, body_attr, shape)

    def _write_header(self, design, out_file):
        # Write out the file settings
        out_file.write(LINE.format(PROGRAM_HEADER_TO_FIRST_REWIND))
        out_file.write(LINE.format(METRIC_UNITS_LEADING_ZERO))
        out_file.write(LINE.format(FORMAT_VERSION.format(ver=2)))

        # Define tools used and assign codes
        hole_count = 1 # tool count starts at 1, 00 us used for 'unload'
        for hole_key, hole in self._holes.items():
            diameter = self._convert_units(hole.shape.radius * 2)
            hole.code = hole_count
            hole_count += 1
            out_file.write(LINE.format(TOOL_DEFINITION.format(code=hole.code, diameter=diameter)))
        out_file.write(LINE.format(REWIND_AND_STOP))

    def _write_body(self, out_file):
        """ Write all of the locations for the holes. """

        for hole_key, hole in self._holes.items():
            out_file.write(LINE.format(TOOL_SELECT.format(code=hole.code)))
            for pos in hole.locations:
                out_file.write(LINE.format(LOCATION.format(x=self._convert_units(pos.x), y=self._convert_units(pos.y))))

        # tidy up
        out_file.write(LINE.format(UNLOAD_TOOL))
        out_file.write(LINE.format(END_FILE))

    def _convert_units(self, num):
        """ Convert from the core units (nm) to those of the current gerber being written. """
        # FIXME(shamer): adjust to actual units of gerber, is hard coded to mm
        return num / 1000000.0
