#!/usr/bin/env python
""" The KiCAD Format Writer """

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


# Basic Strategy
# 0) converted file will be store in subdirectory
# 1) create subdirectory, symbol and project file
# 2) Write each component into a .sym file (even EMBEDDED components)
# 3) Write component instances to .sch file
# 4) Store net segments at the end of .sch file
#
# NOTE: The gEDA format is based on a 100x100 MILS grid where
# 1 MILS is equal to 1/1000 of an inch. In a vanilla gEDA file
# a blueprint-style frame is present with origin at 
# (40'000, 40'000). 


# Note: in a KiCAD schematic, the y coordinates increase downwards. In
# OpenJSON, y coordinates increase upwards, so we negate them. In the
# KiCAD library file (where components are stored) y coordinates
# increase upwards as in OpenJSON and no transformation is needed.

import time

from os.path import splitext

from parser.kicad import MATRIX2ROTATION

ROTATION2MATRIX = dict((v, k) for k, v in MATRIX2ROTATION.items())


class KiCAD(object):
    """ The KiCAD Format Writer """

    def write(self, design, filename, library_filename=None):
        """ Write the design to the KiCAD format """

        if library_filename is None:
            library_filename = splitext(filename)[0] + '-cache.lib'

        self.write_library(design, library_filename)

        f = open(filename, "w")

        self.write_header(f, design)
        self.write_libs(f, library_filename)
        self.write_eelayer(f)
        self.write_descr(f, design)
        for ann in design.design_attributes.annotations:
            self.write_annotation(f, ann)
        for inst in design.component_instances:
            self.write_instance(f, inst)
        for net in design.nets:
            self.write_net(f, net)
        self.write_footer(f)

        f.close()


    def write_header(self, f, design):
        """ Write a kiCAD schematic file header """
        f.write('EESchema Schematic File Version 2  date ')
        self.write_header_date(f, design)


    def write_header_date(self, f, design):
        """ Write the date portion of a kiCAD schematic header """
        bdt = time.localtime(design.design_attributes.metadata.updated_timestamp)
        f.write(time.strftime('%a %d %b %Y %H:%M:%S %p ', bdt))
        if time.daylight and bdt.tm_isdst:
            f.write(time.tzname[1])
        else:
            f.write(time.tzname[0])
        f.write('\n')


    def write_libs(self, f, library_filename):
        """ Write the LIBS section of a kiCAD schematic """
        f.write('LIBS:%s\n' % (splitext(library_filename)[0],))


    def write_eelayer(self, f):
        """ Write the EELAYER block of a kiCAD schematic """
        f.write('EELAYER 25  0\n')
        f.write('EELAYER END\n')


    def write_descr(self, f, design):
        """ Write the description block of a kiCAD schematic """
        bdt = time.localtime(design.design_attributes.metadata.updated_timestamp)
        datestr = time.strftime('%d %b %Y', bdt).lower()
        f.write('''\
$Descr A4 11700 8267
encoding utf-8
Sheet 1 1
Title ""
Date "%s"
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
''' % (datestr,))


    def write_annotation(self, f, ann):
        """ Write a design annotation to a kiCAD schematic """
        f.write('Text Label %d %d %d 60 ~ 0\n' %
                (ann.x, -ann.y, int(ann.rotation * 1800)))
        f.write(ann.value + '\n')

    def write_instance(self, f, inst):
        """ Write a $Comp component to a kiCAD schematic """
        f.write('$Comp\n')
        f.write('L %s %s\n' % (inst.library_id, inst.instance_id))
        f.write('U %d 1 00000000\n' % (inst.symbol_index,))
        f.write('P %d %d\n' % (inst.symbol_attributes[0].x,
                               -inst.symbol_attributes[0].y))
        f.write('\t1    %d %d\n' % (inst.symbol_attributes[0].x,
                                    -inst.symbol_attributes[0].y))
        f.write('\t%d    %d    %d    %d\n' %
                ROTATION2MATRIX[inst.symbol_attributes[0].rotation])
        f.write('$EndComp\n')


    def write_net(self, f, net):
        """ Write a Net as kiCAD Wires and Connections """
        segments = set() # ((x,y),(x,y))

        for point in net.points.values():
            for point2_id in point.connected_points:
                point2 = net.points[point2_id]
                seg = [(point.x, point.y), (point2.x, point2.y)]
                seg.sort() # canonical order
                segments.add(tuple(seg))

        for seg in sorted(segments):
            f.write('Wire Wire Line\n')
            f.write('\t%d %d %d %d\n' % (seg[0][0], -seg[0][1],
                                         seg[1][0], -seg[1][1]))


    def write_footer(self, f):
        """ Write the kiCAD schematic footer """
        f.write('$EndSCHEMATC\n')


    def write_library(self, design, filename):
        """ Write out a kiCAD cache library to the given filename """
        f = open(filename, 'w')
        self.write_library_header(f, design)
        for cpt in design.components.components.itervalues():
            self.write_library_component(f, cpt)
        self.write_library_footer(f)
        f.close()


    def write_library_header(self, f, design):
        """ Write the header line for a kiCAD cache library """
        f.write('EESchema-LIBRARY Version 2.3  Date: ')
        self.write_header_date(f, design)
        f.write('#encoding utf-8\n')


    def write_library_component(self, f, cpt):
        """ Write a single component to a kiCAD cache library """
        ref = cpt.attributes.get('_prefix', 'U')
        f.write('#\n')
        f.write('# ' + cpt.name + '\n')
        f.write('#\n')
        f.write('DEF %s %s 0 30 Y Y %d F N\n' %
                (cpt.name, ref, len(cpt.symbols[0].bodies)))
        f.write('F0 "%s" 0 0 60 H V L CNN\n' % (ref,))
        f.write('F1 "%s" 0 60 60 H V L CNN\n' % (cpt.name,))
        self.write_symbols(f, cpt.symbols)
        f.write('ENDDEF\n')


    def write_symbols(self, f, symbols):
        """ Write the DRAW portion (shapes and pins) of a kiCAD
        component symbol """
        f.write('DRAW\n')

        lines = {} # line template -> (symbol, set([units]), set([converts]))

        def add_line(line, symbol, unit, convert):
            """ Add a line with a given symbol, unit and convert """
            if line not in lines:
                lines[line] = (symbol, set(), set())
            lines[line][1].add(unit)
            lines[line][2].add(convert)

        for convert, symbol in enumerate(symbols[:2], 1):
            for unit, body in enumerate(symbol.bodies, 1):
                for shape in body.shapes:
                    add_line(self.get_shape_line(shape),
                             symbol, unit, convert)

                for pin in body.pins:
                    add_line(self.get_pin_line(pin), symbol, unit, convert)

        for line, (symbol, units, converts) in lines.items():
            if len(units) == len(symbol.bodies):
                units = (0,)
            if len(converts) == 2:
                converts = (0,)
            for unit in units:
                for convert in converts:
                    f.write(line % dict(unit=unit, convert=convert))

        f.write('ENDDRAW\n')


    def get_shape_line(self, shape):
        """ Return the line for a Shape in a kiCAD cache library """
        if shape.type == 'arc':
            # convert pi radians to tenths of degrees
            start = round(shape.start_angle * 1800)
            end = round(shape.end_angle * 1800)
            return ('A %d %d %d %d %d %%(unit)d %%(convert)d 0 N\n' %
                    (shape.x, shape.y, shape.radius, start, end))
        elif shape.type == 'circle':
            return ('C %d %d %d %%(unit)d %%(convert)d 0 N\n' %
                    (shape.x, shape.y, shape.radius))
        elif shape.type == 'line':
            return ('P 2 %%(unit)d %%(convert)d 0 %d %d %d %d N\n' %
                    (shape.p1.x, shape.p1.y, shape.p2.x, shape.p2.y))
        elif shape.type == 'polygon':
            return ('P %d %%(unit)d %%(convert)d 0 %s N\n' %
                    (len(shape.points),
                     ' '.join('%d %d' % (p.x, p.y) for p in shape.points)))
        elif shape.type == 'rectangle':
            return ('S %d %d %d %d %%(unit)d %%(convert)d 0 N\n' %
                    (shape.x, shape.y, shape.x + shape.width,
                     shape.y + shape.height))
        elif shape.type == 'label':
            angle = round(shape.rotation * 1800)
            align = shape.align[0].upper()
            return ('T %d %d %d 20 0 %%(unit)d %%(convert)d %s Normal 0 %s C\n' %
                    (angle, shape.x, shape.y,
                     shape.text.replace(' ', '~'), align))


    def get_pin_line(self, pin):
        """ Return the line for a Pin in a kiCAD cache library """
        x, y = pin.p2.x, pin.p2.y

        if x == pin.p1.x: # vertical
            length = y - pin.p1.y
            if length > 0:
                direction = 'D' # down
            else:
                direction = 'U' # up
        else:
            length = x - pin.p1.x
            if length > 0:
                direction = 'L' # left
            else:
                direction = 'R' # right

        if pin.label is None:
            name = '~'
        else:
            name = pin.label.text

        return ('X %s %s %d %d %d %s 60 60 %%(unit)d %%(convert)d B\n' %
                (name, pin.pin_number, x, y, abs(length), direction))


    def write_library_footer(self, f):
        """ Write a kiCAD library file footer """
        f.write('#\n#End Library\n')
