#! /usr/bin/env python2
""" This module provides a parser for the gEDA format into a
    OpenJSON design. The OpenJSON format does not provide
    color/style settings, hence, color/style data from the
    gEDA format is ignored.
    The module provides a parser class :py:class:GEDA that
    implements all parsing functionality. To parse a gEDA
    schematic file into a design do the following:

    >>> parser = GEDA()
    >>> design = parser.parse('example_geda_file.sch')

    The gEDA format relies highly on referencing symbol files
    that are mostly provided in an installation directory of
    the gEDA tool chain. To parse these symbol files it is
    required to provide the symbol directories. Specify symbol
    directories as follows:

    >>> symbol_directories = ['/usr/share/gEDA/sym', './sym']
    >>> parser = GEDA(symbol_dirs=symbol_directories)
    >>> design = parser.parse('example_geda_file.sch')
"""

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
# 0) Extracting ONLY relevant data from gEDA format. ALL
#   color/style data is ignored
# 1) Parsing the schematic file to extract components & instances
# 2) Create components and instances as they occur in the file
# 2.1) Parse referenced symbol files (components) into components
# 2.2) Parse EMBEDDED symbols into components
# 3) Store net segments for later processing
# 4) Calculate nets from segments
#
# NOTE: The gEDA format is based on a 100x100 MILS grid where
# 1 MILS is equal to 1/1000 of an inch. In a vanilla gEDA file
# a blueprint-style frame is present with origin at
# (40'000, 40'000).

import os
import zipfile
import logging
import tempfile
import itertools

from StringIO import StringIO

from upconvert.core import shape
from upconvert.core import components
from upconvert.core import net

from upconvert.core.design import Design
from upconvert.core.annotation import Annotation
from upconvert.core.component_instance import ComponentInstance
from upconvert.core.component_instance import SymbolAttribute

from upconvert.parser import geda_commands

# Logging
log = logging.getLogger('parser.geda')


UNKNOWN_COMPONENT = """v 20110115 2
T 0 0 9 3 1 0 0 0 1
Symbol Unknown '%s'"""


class GEDAText(object):
    """ Class representation of text as in GEDA format. """

    def __init__(self, content, attribute=None, params=None):
        self.attribute = attribute
        self.content = content
        self.params = params or {}

    def is_attribute(self):
        """ Returns True when text is attribute. """
        return bool(self.attribute is not None)

    def is_text(self):
        """ Returns True when text is regular text. """
        return bool(self.attribute is None)

    def store_styles_in_label(self, label):
        """
        Store all available style parameters in ``styles``
        property of ``label``. Returns ``label``.
        """
        for key, value in self.params.items():
            if key.startswith(geda_commands.GEDAStyleParameter.TYPE):
                label.styles[key] = value
        return label

    def as_label(self):
        """
        Generate label from text object using parsed parameters.

        Returns ``Label`` instance.
        """
        text_x = self.params.get('x', 0)

        if self.params.get('mirrored', False):
            text_x = 0 - text_x

        label = shape.Label(
            text_x,
            self.params.get('y', 0),
            self.content,
            'left',
            self.params.get('angle', 0),
        )
        return self.store_styles_in_label(label)

    @classmethod
    def from_command(cls, stream, params):
        """
        Create a ``GEDAText`` instance from *stream* and previously
        parse *params*. The stream is expected to be as long as the
        ``numb_lines`` property in *params*. The same amount of lines
        are parsed in stream to make up the *attribute*, *content*
        properties of the ``GEDAText`` instance.

        Returns a newly created ``GEDAText`` instance.
        """
        num_lines = params['num_lines']

        attribute = None
        content = [stream.readline() for _ in range(int(num_lines))]
        content = ''.join(content).strip()

        ## escape special parameter sequence '\_'
        content = content.replace("\_", '')

        if num_lines == 1 and '=' in content:
            attribute, content = content.split('=', 1)

            ## prefix attributes that are marked as invisible
            if params['visibility'] == 0:
                attribute = "_" + attribute
            ## these are special attributes that are treated differently
            elif attribute in ['netname', 'pinnumber', 'pinlabel', 'refdes']:
                attribute = "_" + attribute

        return cls(content, attribute=attribute, params=params)


class GEDAError(Exception):
    """ Exception class for gEDA parser errors """
    pass


class GEDA:
    """ The GEDA Format Parser """

    DELIMITER = ' '
    SCALE_FACTOR = 10.0  # maps 1000 MILS to 10 pixels

    OBJECT_TYPES = {
        'v': geda_commands.GEDAVersionCommand(),
        'L': geda_commands.GEDALineCommand(),
        'B': geda_commands.GEDABoxCommand(),
        'V': geda_commands.GEDACircleCommand(),
        'A': geda_commands.GEDAArcCommand(),
        'T': geda_commands.GEDATextCommand(),
        'N': geda_commands.GEDASegmentCommand(),
        'U': geda_commands.GEDABusCommand(),
        'P': geda_commands.GEDAPinCommand(),
        'C': geda_commands.GEDAComponentCommand(),
        'H': geda_commands.GEDAPathCommand(),
        ## valid types but are ignored
        'G': geda_commands.GEDAPictureCommand(),
        ## environments
        '{': geda_commands.GEDAEmbeddedEnvironmentCommand(),
        '}': [],  # attributes
        '[': geda_commands.GEDAAttributeEnvironmentCommand(),
        ']': [],  # embedded component
    }

    def __init__(self, symbol_dirs=None):
        """ Constuct a gEDA parser object. Specifying a list of symbol
            directories in *symbol_dir* will provide a symbol file
            lookup in the specified directories. The lookup will be
            generated instantly examining each directory (if it exists).

            Kwargs:
                symbol_dirs (list): List of directories containing .sym
                    files
        """
        self.offset = shape.Point(40000, 40000)
        ## Initialise frame size with largest possible size
        self.frame_width = 0
        self.frame_height = 0

        # initialise PIN counter
        self.pin_counter = itertools.count(0)
        # initialise  PATH counter
        self.path_counter = itertools.count(0)

        ## add flag to allow for auto inclusion
        if symbol_dirs is None:
            symbol_dirs = ['./']

        symbol_dirs = symbol_dirs + \
            [os.path.join(os.path.dirname(__file__), '..', 'library', 'geda')]

        self.known_symbols = find_symbols(symbol_dirs)

        self.design = None
        self.segments = None
        self.net_points = None
        self.component_pins = None
        self.net_names = None
        self.geda_zip = None

    @staticmethod
    def auto_detect(filename):
        """ Return our confidence that the given file is an geda schematic """
        with open(filename, 'rU') as f:
            data = f.read()
        confidence = 0
        if data[0:2] == 'v ':
            confidence += 0.51
        if 'package=' in data:
            confidence += 0.25
        if 'footprint=' in data:
            confidence += 0.25
        if 'refdes=' in data:
            confidence += 0.25
        if 'netname=' in data:
            confidence += 0.25
        return confidence

    def set_offset(self, point):
        """ Set the offset point for the gEDA output. As OpenJSON
            positions the origin in the center of the viewport and
            gEDA usually uses (40'000, 40'000) as page origin, this
            allows for translating from one coordinate system to
            another. It expects a *point* object providing a *x* and
            *y* attribute.
        """
        ## create an offset of 5 grid squares from origin (0,0)
        self.offset.x = point.x
        self.offset.y = point.y

    def parse(self, inputfile):
        """ Parse a gEDA file into a design.

            Returns the design corresponding to the gEDA file.
        """
        inputfiles = []

        ## check if inputfile is in ZIP format
        if zipfile.is_zipfile(inputfile):
            self.geda_zip = zipfile.ZipFile(inputfile)
            for filename in self.geda_zip.namelist():
                if filename.endswith('.sch'):
                    inputfiles.append(filename)
        else:
            inputfiles = [inputfile]

        self.design = Design()

        ## parse frame data of first schematic to extract
        ## page size (assumes same frame for all files)
        with self._open_file_or_zip(inputfiles[0]) as stream:
            self._check_version(stream)

            for line in stream.readlines():
                if 'title' in line and line.startswith('C'):
                    obj_type, params = self._parse_command(StringIO(line))
                    assert(obj_type == 'C')

                    params['basename'], _ = os.path.splitext(
                        params['basename'],
                    )

                    log.debug("using title file: %s", params['basename'])

                    self._parse_title_frame(params)

        ## store offset values in design attributes
        self.design.design_attributes.attributes.update({
            '_geda_offset_x': str(self.offset.x),
            '_geda_offset_y': str(self.offset.y),
            '_geda_frame_width': str(self.frame_width),
            '_geda_frame_height': str(self.frame_height),
        })

        for filename in inputfiles:
            f_in = self._open_file_or_zip(filename)
            self._check_version(f_in)

            self.parse_schematic(f_in)

            basename, _ = os.path.splitext(os.path.basename(filename))
            self.design.design_attributes.metadata.set_name(basename)

            ## modify offset for next page to be shifted to the right
            self.offset.x = self.offset.x - self.frame_width

            f_in.close()

        return self.design

    def _parse_v(self, stream, params):
        """
        Only required to be callable when 'v' command is found.
        Returns without any processing.
        """
        return

    def _parse_G(self, stream, params):
        """
        Parse picture command 'G'. Returns without any processing but
        logs a warning.
        """
        log.warn("ignoring picture/font in gEDA file. Not supported!")
        return

    def parse_schematic(self, stream):
        """ Parse a gEDA schematic provided as a *stream* object into a
            design.

            Returns the design corresponding to the schematic.
        """
        # pylint: disable=R0912
        if self.design is None:
            self.design = Design()

        self.segments = set()
        self.net_points = dict()
        self.component_pins = dict()
        self.net_names = dict()

        obj_type, params = self._parse_command(stream)

        while obj_type is not None:

            objects = getattr(self, "_parse_%s" % obj_type)(stream, params)

            attributes = self._parse_environment(stream)
            self.design.design_attributes.attributes.update(attributes or {})

            self.add_objects_to_design(self.design, objects)

            obj_type, params = self._parse_command(stream)

        ## process net segments into nets & net points and add to design
        self.divide_segments()

        calculated_nets = self.calculate_nets()

        for cnet in sorted(calculated_nets, key=lambda n : n.net_id):
            self.design.add_net(cnet)

        return self.design

    def _parse_title_frame(self, params):
        """ Parse the frame component in *params* to extract the
            page size to be used in the design. The offset is adjusted
            according to the bottom-left position of the frame.
        """
        ## set offset based on bottom-left corner of frame
        self.offset.x = params['x']
        self.offset.y = params['y']

        filename = self.known_symbols.get(params['basename'])
        if not filename or not os.path.exists(filename):
            log.warn("could not find title symbol '%s'" % params['basename'])

            self.frame_width = 46800
            self.frame_height = 34000
            return

        ## store title component name in design
        self.design.design_attributes.add_attribute(
            '_geda_titleframe', params['basename'],
        )

        with open(filename, 'rU') as stream:
            obj_type, params = self._parse_command(stream)

            while obj_type is not None:

                if obj_type == 'B':
                    if params['width'] > self.frame_width:
                        self.frame_width = params['width']

                    if params['height'] > self.frame_height:
                        self.frame_height = params['height']

                ## skip commands covering multiple lines
                elif obj_type in ['T', 'H']:
                    for _ in range(params['num_lines']):
                        stream.readline()

                obj_type, params = self._parse_command(stream)

            ## set width to estimated max value when no box was found
            if self.frame_width == 0:
                self.frame_width = 46800

            ## set height to estimated max value when no box was found
            if self.frame_height == 0:
                self.frame_height = 34000

    def _create_ripper_segment(self, params):
        """ Creates a new segement from the busripper provided
            in gEDA. The busripper is a graphical feature that
            provides a nicer look for a part of a net. The bus
            rippers are turned into net segments according to the
            length and orientation in *params*.

            Returns a tuple of two NetPoint objects for the segment.
        """
        x, y = params['x'], params['y']
        angle, mirror = params['angle'], params['mirror']

        if mirror:
            angle = (angle + 90) % 360

        x, y = self.conv_coords(x, y)
        pt_a = self.get_netpoint(x, y)

        ripper_size = self.to_px(200)

        ## create second point for busripper segment on bus
        if angle == 0:
            pt_b = self.get_netpoint(pt_a.x+ripper_size, pt_a.y+ripper_size)
        elif angle == 90:
            pt_b = self.get_netpoint(pt_a.x-ripper_size, pt_a.y+ripper_size)
        elif angle == 180:
            pt_b = self.get_netpoint(pt_a.x-ripper_size, pt_a.y-ripper_size)
        elif angle == 270:
            pt_b = self.get_netpoint(pt_a.x+ripper_size, pt_a.y-ripper_size)
        else:
            raise GEDAError(
                "invalid angle in component '%s'" % params['basename']
            )

        return pt_a, pt_b

    def _parse_component(self, stream, params):
        """ Creates a component instance according to the component *params*.
            If the component is not known in the library, a the component
            will be created according to its description in the embedded
            environment ``[]`` or a symbol file. The component is added
            to the library automatically if necessary.
            An instance of this component will be created and added to
            the design.
            A GEDAError is raised when either the component file
            is invalid or the referenced symbol file cannot be found
            in the known directories.

            Returns a tuple of Component and ComponentInstance objects.
        """
        basename, _ = os.path.splitext(params['basename'])

        component_name = basename
        if params.get('mirror'):
            component_name += '_MIRRORED'

        if component_name in self.design.components.components:
            component = self.design.components.components[component_name]

            ## skipping embedded data might be required
            self.skip_embedded_section(stream)

        else:
            ##check if sym file is embedded or referenced
            if basename.startswith('EMBEDDED'):
                ## embedded only has to be processed when NOT in symbol lookup
                if basename not in self.known_symbols:
                    component = self.parse_component_data(stream, params)
            else:
                if basename not in self.known_symbols:
                    log.warn("referenced symbol file '%s' unknown" % basename)
                    ## create a unknown symbol reference
                    component = self.parse_component_data(
                        StringIO(UNKNOWN_COMPONENT % basename),
                        params
                    )
                    ## parse optional attached environment before continuing
                    self._parse_environment(stream)
                    return None, None

                ## requires parsing of referenced symbol file
                with open(self.known_symbols[basename], "rU") as f_in:
                    self._check_version(f_in)
                    component = self.parse_component_data(f_in, params)

            self.design.add_component(component_name, component)

        ## get all attributes assigned to component instance
        attributes = self._parse_environment(stream)

        ## refdes attribute is name of component (mandatory as of gEDA doc)
        ## examples if gaf repo have components without refdes, use part of
        ## basename
        if attributes is not None:
            instance = ComponentInstance(
                attributes.get('_refdes', component.name),
                component.name, 0
            )
            for key, value in attributes.items():
                instance.add_attribute(key, value)

        else:
            instance = ComponentInstance(
                component.name, component.name, 0
            )

        ## generate a component instance using attributes
        self.design.add_component_instance(instance)

        symbol = SymbolAttribute(
            self.x_to_px(params['x']),
            self.y_to_px(params['y']),
            self.conv_angle(params['angle']),
            False)
        instance.add_symbol_attribute(symbol)

        ## add annotation for special attributes
        for idx, attribute_key in enumerate(['_refdes', 'device']):
            if attribute_key in component.attributes \
               or attribute_key in instance.attributes:

                symbol.add_annotation(
                    Annotation(
                        '{{%s}}' % attribute_key,
                        0, 0+idx*10, 0.0, 'true'
                    )
                )

        ## parse all bodies of this component for pins and add them
        ## to the lookup with their corresponding instance. This is
        ## required to connect net points with components later on
        ## during the calculation of the nets.
        for index, body in enumerate(component.symbols[0].bodies):
            try:
                sym_attr = instance.symbol_attributes[index]
            except IndexError:
                continue

            for pin in body.pins:
                coords = (sym_attr.x + pin.p2.x, sym_attr.y + pin.p2.y)
                if coords not in self.component_pins:
                    self.component_pins[coords] = []

                self.component_pins[coords].append(net.ConnectedComponent(
                    instance.instance_id,
                    pin.pin_number
                ))

        return component, instance

    def _check_version(self, stream):
        """ Check next line in *stream* for gEDA version data
            starting with ``v``. Raises ``GEDAError`` when no version
            data can be found.
        """
        typ, _ = self._parse_command(stream)
        if typ != 'v':
            raise GEDAError(
                "cannot convert file, not in gEDA format"
            )
        return True

    def _is_mirrored_command(self, params):
        return bool(params.get('mirror', False))

    def parse_component_data(self, stream, params):
        """ Creates a component from the component *params* and the
            following commands in the stream. If the component data
            is embedded in the schematic file, all coordinates will
            be translated into the origin first.
            Only a single symbol/body is created for each component
            since gEDA symbols contain exactly one description.

            Returns the newly created Component object.
        """
        # pylint: disable=R0912
        basename = os.path.splitext(params['basename'])[0]

        saved_offset = self.offset
        self.offset = shape.Point(0, 0)

        ## retrieve if component is mirrored around Y-axis
        mirror = self._is_mirrored_command(params)
        if mirror:
            basename += '_MIRRORED'

        move_to = None
        if basename.startswith('EMBEDDED'):
            move_to = (params['x'], params['y'])

        ## grab next line (should be '['
        typ, params = self._parse_command(stream, move_to)

        if typ == '[':
            typ, params = self._parse_command(stream, move_to)

        component = components.Component(basename)
        symbol = components.Symbol()
        component.add_symbol(symbol)
        body = components.Body()
        symbol.add_body(body)

        ##NOTE: adding this attribute to make parsing UPV data easier
        ## when using re-exported UPV.
        component.add_attribute('_geda_imported', 'true')
        self.pin_counter = itertools.count(0)

        while typ is not None:

            params['mirror'] = mirror
            objects = getattr(self, "_parse_%s" % typ)(stream, params)

            attributes = self._parse_environment(stream)
            component.attributes.update(attributes or {})

            self.add_objects_to_component(component, objects)

            typ, params = self._parse_command(stream, move_to)

        self.offset = saved_offset

        return component

    def divide_segments(self):
        """ Checks all net segments for intersecting points of
            all other net segments. If an intersection is detected
            the net segment is divided into two segments with the
            intersecting point. This method has been adapted from
            a similar method in the kiCAD parser.
        """
        ## check if segments need to be divided
        add_segs = set()
        rem_segs = set()
        for segment in self.segments:
            for point in self.net_points.values():
                if self.intersects_segment(segment, point):
                    pt_a, pt_b = segment
                    rem_segs.add(segment)
                    add_segs.add((pt_a, point))
                    add_segs.add((point, pt_b))

        self.segments -= rem_segs
        self.segments |= add_segs

    def skip_embedded_section(self, stream):
        """ Reads the *stream* line by line until the end of an
            embedded section (``]``) is found. This method is used
            to skip over embedded sections of already known
            components.
        """
        pos = stream.tell()
        typ = stream.readline().split(self.DELIMITER, 1)[0].strip()

        ## return with stream reset to previous position if not
        ## an embedded section
        if typ != '[':
            stream.seek(pos)
            return

        while typ != ']':
            typ = stream.readline().split(self.DELIMITER, 1)[0].strip()

    def get_netpoint(self, x, y):
        """ Creates a new NetPoint at coordinates *x*,*y* and stores
            it in the net point lookup table. If a NetPoint does already
            exist, the existing point is returned.
            Returns a NetPoint object at coordinates *x*,*y*
        """
        if (x, y) not in self.net_points:
            self.net_points[(x, y)] = net.NetPoint('%da%d' % (x, y), x, y)
        return self.net_points[(x, y)]

    @staticmethod
    def intersects_segment(segment, pt_c):
        """ Checks if point *pt_c* lays on the *segment*. This code is
            adapted from the kiCAD parser.
            Returns True if *pt_c* is on *segment*, False otherwise.
        """
        pt_a, pt_b = segment

        #check vertical segment
        if pt_a.x == pt_b.x == pt_c.x:
            if min(pt_a.y, pt_b.y) < pt_c.y < max(pt_a.y, pt_b.y):
                return True
        #check vertical segment
        elif pt_a.y == pt_b.y == pt_c.y:
            if min(pt_a.x, pt_b.x) < pt_c.x < max(pt_a.x, pt_b.x):
                return True
        #check diagonal segment
        elif (pt_c.x-pt_a.x)*(pt_b.y-pt_a.y) \
              == (pt_b.x-pt_a.x)*(pt_c.y-pt_a.y):
            if min(pt_a.x, pt_b.x) < pt_c.x < max(pt_a.x, pt_b.x):
                return True
        ## point C not on segment
        return False

    def _parse_environment(self, stream):
        """ Checks if attribute environment starts in the next line
            (marked by '{'). Environment only contains text elements
            interpreted as text.
            Returns a dictionary of attributes.
        """
        current_pos = stream.tell()
        typ, params = self._parse_command(stream)

        #go back to previous position when no environment in stream
        if typ != '{':
            stream.seek(current_pos)
            return None

        typ, params = self._parse_command(stream)

        attributes = {}
        while typ is not None:
            if typ == 'T':
                geda_text = self._parse_T(stream, params)

                if geda_text.is_attribute():
                    attributes[geda_text.attribute] = geda_text.content
                else:
                    log.warn("normal text in environemnt does not comply "
                             "with GEDA format specification: %s", geda_text.content)

            typ, params = self._parse_command(stream)

        return attributes

    def calculate_nets(self):
        """ Calculate connected nets from previously stored segments
            and netpoints. The code has been adapted from the kiCAD
            parser since the definition of segments in the schematic
            file are similar. The segments are checked against
            existing nets and added when they touch it. For this
            to work, it is required that intersecting segments are
            divided prior to this method.

            Returns a list of valid nets and its net points.
        """
        nets = []

        # Iterate over the segments, removing segments when added to a net
        while self.segments:
            seg = self.segments.pop() # pick a point

            net_name = ''
            pt_a, pt_b = seg
            if pt_a.point_id in self.net_names:
                net_name = self.net_names[pt_a.point_id]
            elif pt_b.point_id in self.net_names:
                net_name = self.net_names[pt_b.point_id]

            new_net = net.Net(net_name)
            new_net.connect(seg)
            found = True

            if net_name:
                new_net.attributes['_name'] = net_name

            while found:
                found = set()

                for seg in self.segments: # iterate over segments
                    if new_net.connected(seg): # segment touching the net
                        new_net.connect(seg) # add the segment
                        found.add(seg)

                for seg in found:
                    self.segments.remove(seg)

            nets.append(new_net)

        # check if names are available for calculated nets
        for net_obj in nets:
            for point_id, point in net_obj.points.items():
                ## check for stored net names based on pointIDs
                if point_id in self.net_names:
                    net_obj.net_id = self.net_names[point_id]
                    net_obj.attributes['_name'] = self.net_names[point_id]

                ## check if net point is connected to component pins and
                ## add matching components to net point
                if (point.x, point.y) in self.component_pins:
                    for comp in self.component_pins[(point.x, point.y)]:
                        point.add_connected_component(comp)

            if '_name' in net_obj.attributes:
                annotation = Annotation(
                    "{{_name}}", ## annotation referencing attribute '_name'
                    0, 0,
                    self.conv_angle(0.0),
                    self.conv_bool(1),
                )
                net_obj.add_annotation(annotation)

        for net_obj in nets:
            if not net_obj.net_id:
                net_obj.net_id = min(net_obj.points)

        return nets

    def _open_file_or_zip(self, filename, mode='rU'):
        """
        Open the file with *filename* and return a file
        handle for it. If the current file is a ZIP file
        the filename will be treated as compressed file in
        this ZIP file.
        """
        if self.geda_zip is not None:
            temp_dir = tempfile.mkdtemp()
            self.geda_zip.extract(filename, temp_dir)
            filename = os.path.join(temp_dir, filename)

        return open(filename, mode)

    def add_text_to_component(self, component, geda_text):
        """
        Add the content of a ``GEDAText`` instance to the
        component. If *geda_text* contains ``refdes``, ``prefix``
        or ``suffix`` attributes it will be stored as special
        attribute in the component. *geda_text* that is not an
        attribute will be added as ``Label`` to the components
        body.
        """
        if geda_text.is_text():
            component.symbols[0].bodies[0].add_shape(geda_text.as_label())

        elif geda_text.attribute == '_refdes' \
             and '?' in geda_text.content:

            prefix, suffix = geda_text.content.split('?')
            component.add_attribute('_prefix', prefix)
            component.add_attribute('_suffix', suffix)
        else:
            component.add_attribute(
                geda_text.attribute,
                geda_text.content
            )

    def add_objects_to_component(self, component, objs):
        """
        Add a GEDA object to the component. Valid
        objects are subclasses of ``Shape``, ``Pin`` or
        ``GEDAText``. *objs* is expected to be an iterable
        and will be added to the correct component properties
        according to their type.
        """
        if not objs:
            return

        try:
            iter(objs)
        except TypeError:
            objs = [objs]

        for obj in objs:
            obj_cls = obj.__class__
            if issubclass(obj_cls, shape.Shape):
                component.symbols[0].bodies[0].add_shape(obj)
            elif issubclass(obj_cls, components.Pin):
                component.symbols[0].bodies[0].add_pin(obj)
            elif issubclass(obj_cls, GEDAText):
                self.add_text_to_component(component, obj)

    def add_text_to_design(self, design, geda_text):
        """
        Add the content of a ``GEDAText`` instance to the
        design. If *geda_text* contains ``use_license`` it will
        be added to the design's metadata ``license`` other
        attributes are added to ``design_attributes``.
        *geda_text* that is not an attribute will be added as
        ``Label`` to the components body.
        """
        if geda_text.is_text():
            design.add_shape(geda_text.as_label())
        elif geda_text.attribute == 'use_license':
            metadata = design.design_attributes.metadata
            metadata.license = geda_text.content
        else:
            design.design_attributes.add_attribute(
                geda_text.attribute,
                geda_text.content,
            )

    def add_objects_to_design(self, design, objs):
        """
        Add a GEDA object to the design. Valid
        objects are subclasses of ``Shape``, ``Pin`` or
        ``GEDAText``. *objs* is expected to be an iterable
        and will be added to the correct component properties
        according to their type.
        """
        if not objs:
            return

        try:
            iter(objs)
        except TypeError:
            objs = [objs]

        for obj in objs:
            obj_cls = obj.__class__
            if issubclass(obj_cls, shape.Shape):
                design.add_shape(obj)
            elif issubclass(obj_cls, components.Pin):
                design.add_pin(obj)
            elif issubclass(obj_cls, GEDAText):
                self.add_text_to_design(design, obj)

    def _parse_U(self, stream, params):
        """ Processing a bus instance with start end end coordinates
            at (x1, y1) and (x2, y2). *color* is ignored. *ripperdir*
            defines the direction in which the bus rippers are oriented
            relative to the direction of the bus.
        """
        x1, x2 = params['x1'], params['x2']
        y1, y2 = params['y1'], params['y2']

        ## ignore bus when length is zero
        if x1 == x2 and y1 == y2:
            return

        pta_x, pta_y = self.conv_coords(x1, y1)
        ptb_x, ptb_y = self.conv_coords(x2, y2)

        self.segments.add((
            self.get_netpoint(pta_x, pta_y),
            self.get_netpoint(ptb_x, ptb_y)
        ))

    def _parse_L(self, stream, params):
        """ Creates a Line object from the parameters in *params*. All
            style related parameters are ignored.
            Returns a Line object.
        """
        line_x1 = params['x1']
        line_x2 = params['x2']

        if self._is_mirrored_command(params):
            line_x1 = 0 - params['x1']
            line_x2 = 0 - params['x2']

        line = shape.Line(
            self.conv_coords(line_x1, params['y1']),
            self.conv_coords(line_x2, params['y2']),
        )
        ## store style data for line in 'style' dict
        self._save_parameters_to_object(line, params)
        return line

    def _parse_B(self, stream, params):
        """ Creates rectangle from gEDA box with origin in bottom left
            corner. All style related values are ignored.
            Returns a Rectangle object.
        """
        rect_x = params['x']
        if self._is_mirrored_command(params):
            rect_x = 0-(rect_x+params['width'])

        rect = shape.Rectangle(
            self.x_to_px(rect_x),
            self.y_to_px(params['y']+params['height']),
            self.to_px(params['width']),
            self.to_px(params['height'])
        )
        ## store style data for rect in 'style' dict
        self._save_parameters_to_object(rect, params)
        return rect

    def _parse_V(self, stream, params):
        """ Creates a Circle object from the gEDA parameters in *params. All
            style related parameters are ignored.
            Returns a Circle object.
        """
        vertex_x = params['x']
        if self._is_mirrored_command(params):
            vertex_x = 0-vertex_x

        circle = shape.Circle(
            self.x_to_px(vertex_x),
            self.y_to_px(params['y']),
            self.to_px(params['radius']),
        )
        ## store style data for arc in 'style' dict
        self._save_parameters_to_object(circle, params)
        return circle

    def _parse_A(self, stream, params):
        """ Creates an Arc object from the parameter in *params*. All
            style related parameters are ignored.
            Returns Arc object.
        """
        arc_x = params['x']
        start_angle = params['startangle']
        sweep_angle = params['sweepangle']

        if self._is_mirrored_command(params):
            arc_x = 0 - arc_x

            start_angle = start_angle + sweep_angle
            if start_angle <= 180:
                start_angle = 180 - start_angle
            else:
                start_angle = (360 - start_angle) + 180

        arc = shape.Arc(
            self.x_to_px(arc_x),
            self.y_to_px(params['y']),
            self.conv_angle(start_angle),
            self.conv_angle(start_angle+sweep_angle),
            self.to_px(params['radius']),
        )
        ## store style data for arc in 'style' dict
        self._save_parameters_to_object(arc, params)
        return arc

    def _parse_T(self, stream, params):
        """ Parses text element and determins if text is a text object
            or an attribute.
            Returns a tuple (key, value). If text is an annotation key is None.
        """
        params['x'] = self.x_to_px(params['x'])
        params['y'] = self.y_to_px(params['y'])
        params['angle'] = self.conv_angle(params['angle'])

        geda_text = GEDAText.from_command(stream, params)

        ## text can have environemnt attached: parse & ignore
        self._parse_environment(stream)
        return geda_text

    def _parse_N(self, stream, params):
        """ Creates a segment from the command *params* and
            stores it in the global segment list for further
            processing in :py:method:divide_segments and
            :py:method:calculate_nets. It also extracts the
            net name from the attribute environment if
            present.
        """
        ## store segement for processing later
        x1, y1 = self.conv_coords(params['x1'], params['y1'])
        x2, y2 = self.conv_coords(params['x2'], params['y2'])

        ## store segment points in global point list
        pt_a = self.get_netpoint(x1, y1)
        pt_b = self.get_netpoint(x2, y2)

        ## add segment to global list for later processing
        self.segments.add((pt_a, pt_b))

        attributes = self._parse_environment(stream)
        if attributes is not None:
            ## create net with name in attributes
            if '_netname' in attributes:
                net_name = attributes['_netname']
                if net_name not in self.net_names.values():
                    self.net_names[pt_a.point_id] = net_name

    def _parse_P(self, stream, params, pinnumber=0):
        """ Creates a Pin object from the parameters in *param* and
            text attributes provided in the following environment. The
            environment is enclosed in ``{}`` and is required. If no
            attributes can be extracted form *stream* an GEDAError
            is raised.
            The *pin_id* is retrieved from the 'pinnumber' attribute and
            all other attributes are ignored. The conneted end of the
            pin is taken from the 'whichend' parameter as defined in
            the gEDA documentation.

            Returns a Pin object.
        """
        ## pin requires an attribute enviroment, so parse it first
        attributes = self._parse_environment(stream)

        if attributes is None:
            log.warn('mandatory pin attributes missing')
            attributes = {
                '_pinnumber': pinnumber,
            }

        if '_pinnumber' not in attributes:
            attributes['_pinnumber'] = pinnumber
            log.warn("mandatory attribute '_pinnumber' not assigned to pin")

        whichend = params['whichend']

        pin_x1, pin_x2 = params['x1'], params['x2']
        if self._is_mirrored_command(params):
            pin_x1 = 0-pin_x1
            pin_x2 = 0-pin_x2

        ## determine wich end of the pin is the connected end
        ## 0: first point is connector
        ## 1: second point is connector
        if whichend == 0:
            connect_end = self.conv_coords(pin_x1, params['y1'])
            null_end = self.conv_coords(pin_x2, params['y2'])
        else:
            null_end = self.conv_coords(pin_x1, params['y1'])
            connect_end = self.conv_coords(pin_x2, params['y2'])

        label = None
        if '_pinlabel' in attributes:
            label = shape.Label(
                connect_end[0],
                connect_end[1],
                attributes.get('_pinlabel'),
                'left',
                0.0
            )

        pin = components.Pin(
            attributes['_pinnumber'], #pin number
            null_end,
            connect_end,
            label=label
        )
        ## store style parameters in shape's style dict
        self._save_parameters_to_object(pin, params)
        return pin

    def _parse_C(self, stream, params):
        """
        Parse component command 'C'. *stream* is the file stream
        pointing to the line after the component command. *params*
        are the parsed parameters from the component command.
        The method checks if component is a title and ignores it
        if that is the case due to previous processing. If the
        component is a busripper, it is converted into a net
        segment. Otherwise, the component is parsed as a regular
        component and added to the library and design.
        """
        ## ignore title since it only defines the blueprint frame
        if params['basename'].startswith('title'):
            self._parse_environment(stream)

        ## busripper are virtual components that need separate
        ## processing
        elif 'busripper' in params['basename']:
            self.segments.add(self._create_ripper_segment(params))

            ## make sure following environments are ignored
            self.skip_embedded_section(stream)
            self._parse_environment(stream)
        else:
            self._parse_component(stream, params)

    def _parse_H(self, stream, params):
        """ Parses a SVG-like path provided path into a list
            of simple shapes. The gEDA formats allows only line
            and curve segments with absolute coordinates. Hence,
            shapes are either Line or BezierCurve objects.
            The method processes the stream data according to
            the number of lines in *params*.
            Returns a list of Line and BezierCurve shapes.
        """
        params['extra_id'] = self.path_counter.next()
        num_lines = params['num_lines']
        mirrored = self._is_mirrored_command(params)
        command = stream.readline().strip().split(self.DELIMITER)

        if command[0] != 'M':
            raise GEDAError('found invalid path in gEDA file')

        def get_coords(string, mirrored):
            """ Get coordinates from string with comma-sparated notation."""
            x, y = [int(value) for value in string.strip().split(',')]

            if mirrored:
                x = -x

            return (self.x_to_px(x), self.y_to_px(y))

        shapes = []
        current_pos = initial_pos = (get_coords(command[1], mirrored))

        ## loop over the remaining lines of commands (after 'M')
        for _ in range(num_lines-1):
            command = stream.readline().strip().split(self.DELIMITER)

            ## draw line from current to given position
            if command[0] == 'L':
                assert(len(command) == 2)
                end_pos = get_coords(command[1], mirrored)

                shape_ = shape.Line(current_pos, end_pos)
                current_pos = end_pos

            ## draw curve from current to given position
            elif command[0] == 'C':
                assert(len(command) == 4)
                control1 = get_coords(command[1], mirrored)
                control2 = get_coords(command[2], mirrored)
                end_pos = get_coords(command[3], mirrored)

                shape_ = shape.BezierCurve(
                    control1,
                    control2,
                    current_pos,
                    end_pos
                )
                current_pos = end_pos

            ## end of sub-path, straight line from current to initial position
            elif command[0] in ['z', 'Z']:
                shape_ = shape.Line(current_pos, initial_pos)

            else:
                raise GEDAError(
                    "invalid command type in path '%s'" % command[0]
                )

            ## store style parameters in shape's style dict
            self._save_parameters_to_object(shape_, params)
            shapes.append(shape_)

        return shapes

    def _save_parameters_to_object(self, obj, params):
        """
        Save all ``style`` and ``extra`` parameters to the
        objects ``styles`` dictionary. If *obj* does not have
        a ``styles`` property, a ``GEDAError`` is raised.
        """
        parameter_types = [
            geda_commands.GEDAStyleParameter.TYPE,
            geda_commands.GEDAExtraParameter.TYPE,
        ]

        try:
            for key, value in params.items():
                if key.split('_')[0] in parameter_types:
                    obj.styles[key] = value
        except AttributeError:
            log.exception(
                "tried saving style data to '%s' without styles dict.",
                obj.__class__.__name__
            )

    def _parse_command(self, stream, move_to=None):
        """ Parse the next command in *stream*. The object type is check
            for validity and its parameters are parsed and converted to
            the expected typs in the parsers lookup table. If *move_to*
            is provided it is used to translate all coordinates into by
            the given coordinate.
            Returns a tuple (*object type*, *parameters*) where *parameters*
                is a dictionary of paramter name and value.

            Raises GEDAError when object type is not known.
        """
        line = stream.readline()

        while line.startswith('#') or line == '\n':
            line = stream.readline()

        command_data = line.strip().split(self.DELIMITER)

        if len(command_data[0]) == 0 or command_data[0] in [']', '}']:
            return None, []

        object_type, command_data = command_data[0].strip(), command_data[1:]

        if object_type not in self.OBJECT_TYPES:
            raise GEDAError("unknown type '%s' in file" % object_type)

        params = {}
        geda_command = self.OBJECT_TYPES[object_type]
        for idx, parameter in enumerate(geda_command.parameters()):
            if idx >= len(command_data):
                ## prevent text commands of version 1 from breaking
                params[parameter.name] = parameter.default
            else:
                datatype = parameter.datatype
                params[parameter.name] = datatype(command_data[idx])

        assert(len(params) == len(geda_command.parameters()))

        if move_to is not None:
            ## element in EMBEDDED component need to be moved
            ## to origin (0, 0) from component origin
            if object_type in ['T', 'B', 'C', 'A']:
                params['x'] = params['x'] - move_to[0]
                params['y'] = params['y'] - move_to[1]
            elif object_type in ['L', 'P']:
                params['x1'] = params['x1'] - move_to[0]
                params['y1'] = params['y1'] - move_to[1]
                params['x2'] = params['x2'] - move_to[0]
                params['y2'] = params['y2'] - move_to[1]

        return object_type, params

    @classmethod
    def to_px(cls, value):
        """ Converts value in MILS to pixels using the parsers
            scale factor.
            Returns an integer value converted to pixels.
        """
        return int(value / cls.SCALE_FACTOR)

    def x_to_px(self, x_mils):
        """ Convert *px* from MILS to pixels using the scale
            factor and translating it allong the X-axis in
            offset.

            Returns translated and converted X coordinate.
        """
        return int(float(x_mils - self.offset.x) / self.SCALE_FACTOR)

    def y_to_px(self, y_mils):
        """ Convert *py* from MILS to pixels using the scale
            factor and translating it allong the Y-axis in
            offset.

            Returns translated and converted Y coordinate.
        """
        return int(float(y_mils - self.offset.y) / self.SCALE_FACTOR)

    def conv_coords(self, orig_x, orig_y):
        """ Converts coordinats *orig_x* and *orig_y* from MILS
            to pixel units based on scale factor. The converted
            coordinates are in multiples of 10px.
        """
        orig_x, orig_y = int(orig_x), int(orig_y)
        return (
            self.x_to_px(orig_x),
            self.y_to_px(orig_y)
        )

    @staticmethod
    def conv_bool(value):
        """ Converts *value* into string representing boolean
            'true' or 'false'. *value* can be of any numeric or
            boolean type.
        """
        if value in ['true', 'false']:
            return value
        return str(bool(int(value)) is True).lower()

    @staticmethod
    def conv_angle(angle):
        """ Converts *angle* (in degrees) to pi radians. gEDA
            sets degree angles counter-clockwise whereas upverter
            uses pi radians clockwise. Therefore the direction of
            *angle* is therefore adjusted first.
        """
        angle = angle % 360.0
        if angle > 0:
            angle = abs(360 - angle)
        return round(angle/180.0, 1)


def find_symbols(symbol_dirs):
    """ Parses each directory in *symbol_dirs* searching for
        gEDA symbol files based on its extension (extension: .sym).
        It creates a symbol file lookup of basename (without
        extension) and absolute path to the symbol file.

        Returns a dictionary of file basename and absolute path.
    """
    known_symbols = {}

    for symbol_dir in symbol_dirs:
        if os.path.exists(symbol_dir):
            for dirpath, dirnames, filenames in os.walk(symbol_dir):
                dirnames.sort()
                for filename in filenames:
                    if filename.endswith('.sym'):
                        filepath = os.path.join(dirpath, filename)
                        filename, _ = os.path.splitext(filename)
                        if filename not in known_symbols:
                            known_symbols[filename] = filepath

    return known_symbols
