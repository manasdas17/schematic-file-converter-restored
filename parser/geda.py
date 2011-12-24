#! /usr/bin/env python
# 
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
""" This module provides a parser for the gEDA format into a 
    OpenJSON design. The OpenJSON format does not provide 
    color/style settings, hence, color/style data from the
    gEDA format is ignored. 
    The module provides a parser class :py:class:GEDA that 
    implements all parsing functionality. To parse a gEDA 
    schematic file into a design do the following:
    
    >>> parser = GEDA(auto_include=True)
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

import os
import warnings
import itertools

from core import shape
from core import components
from core import net

from core.design import Design
from core.annotation import Annotation
from core.component_instance import ComponentInstance
from core.component_instance import SymbolAttribute


class GEDAError(Exception):
    """ Exception class for gEDA parser errors """
    pass


class GEDA:
    """ The GEDA Format Parser """

    DELIMITER = ' '
    SCALE_FACTOR = 10 #maps 1000 MILS to 10 pixels


    OBJECT_TYPES = { 
        'v': ( # gEDA version
            ('version', int),
            ('fileformat_version', int),
        ),
        'C': ( #component
            ('x', int),
            ('y', int),
            ('selectable', int),
            ('angle', int),
            ('mirror', int),
            ('basename', str),
        ),
        'N': ( # net segment
            ('x1', int),
            ('y1', int),
            ('x2', int),
            ('y2', int),
        ),
        'U': ( # bus (only graphical aid, not a component)
            ('x1', int),
            ('y1', int),
            ('x2', int),
            ('y2', int),
            ('color', int),
            ('ripperdir', int),
        ),
        'T': ( # text or attribute (context)
            ('x', int),
            ('y', int),
            ('color', int),
            ('size', int),
            ('visibility', int),
            ('show_name_value', int),
            ('angle', int),
            ('alignment', int),
            ('num_lines', int),
        ),
        'P': ( # pin (in sym)
            ('x1', int),
            ('y1', int),
            ('x2', int),
            ('y2', int),
            ('color', int),
            ('pintype', int),
            ('whichend', int),
        ),
        'L': ( # line
            ('x1', int),
            ('y1', int),
            ('x2', int),
            ('y2', int),
        ),
        'B': ( # box
            ('x', int),
            ('y', int),
            ('width', int),
            ('height', int),
        ),
        'V': ( # circle
            ('x', int),
            ('y', int),
            ('radius', int),
        ),
        'A': ( # arc
            ('x', int),
            ('y', int),
            ('radius', int),
            ('startangle', int),
            ('sweepangle', int),
        ),
        'H': ( # SVG-like path
            ('color', int),
            ('width', int),
            ('capstyle', int),
            ('dashstyle', int),
            ('dashlength', int),
            ('dashspace', int),
            ('filltype', int),
            ('fillwidth', int),
            ('angle1', int),
            ('pitch1', int),
            ('angle2', int),
            ('pitch2', int),
            ('num_lines', int),         
        ),
        ## environments
        '{': [], 
        '}': [], # attributes
        '[': [], 
        ']': [], # embedded component
        ## valid types but are ignored
        'G': [], #picture
    }

    def __init__(self, symbol_dirs=None, auto_include=False):
        """ Constuct a gEDA parser object. Specifying a list of symbol 
            directories in *symbol_dir* will provide a symbol file 
            lookup in the specified directories. The lookup will be 
            generated instantly examining each directory (if it exists).

            Kwargs:
                symbol_dirs (list): List of directories containing .sym 
                    files
        """
        self.offset = shape.Point(40000, 40000)
        ## add flag to allow for auto inclusion
        if symbol_dirs is None:
            symbol_dirs = []

            if auto_include is True:
                symbol_dirs += [
                    '/usr/share/gEDA/sym',
                    '/usr/local/share/gEDA/sym',
                ]

        self.instance_counter = itertools.count()
        self.known_symbols = {}

        self.design = None 
        self.segments = None
        self.net_points = None
        self.net_names = None

        self.known_symbols = find_symbols(symbol_dirs)

        warnings.warn(
            "converter will ignore style and color data in gEDA format!"
        )

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
    
    def parse(self, filename):
        """ Parse a gEDA file into a design.

            Returns the design corresponding to the gEDA file.
        """

        f_in = open(filename, "r")

        typ, dummy = self._parse_command(f_in)
        if typ != 'v':
            raise GEDAError("cannot convert file, not in gEDA format")

        design = self.parse_schematic(f_in)

        basename, dummy = os.path.splitext(os.path.basename(filename))
        design.design_attributes.metadata.set_name(basename)

        f_in.close()

        return design

    def parse_schematic(self, stream):
        """ Parse a gEDA schematic provided as a *stream* object into a 
            design.
            
            Returns the design corresponding to the schematic.
        """
        self.design = Design()
        self.segments = set()
        self.net_points = dict() 
        self.net_names = dict() 

        obj_type, params = self._parse_command(stream)

        while obj_type is not None:

            if obj_type == 'T': ##Convert regular text or attribute
                key, value = self._parse_text(stream, params)
                
                if key is None: ## text is annotation
                    self.design.design_attributes.add_annotation(
                        self._create_annotation(value, params)
                    )

                elif key == 'use_license':
                    self.design.design_attributes.metadata.license = value
                else:
                    self.design.design_attributes.add_attribute(key, value)

            elif obj_type == 'G' : ## picture type is not supported
                warnings.warn(
                    "ignoring picture/font in gEDA file. Not supported!"
                )
            elif obj_type == 'C': ## command for component found
                basename = params['basename']

                ## ignore title since it only defines the blueprint frame
                if basename.startswith('title'):
                    pass 

                ## busripper are virtual components that need separate 
                ## processing 
                elif 'busripper' in basename:
                    self.segments.add(
                        self._create_ripper_segment(params)
                    )

                    ## make sure following environments are ignored
                    self.skip_embedded_section(stream)
                    self._parse_environment(stream)

                else:
                    self.parse_component(stream, params)

            elif obj_type == 'N': ## net segement (in schematic ONLY)
                self._parse_segment(stream, params)

            elif obj_type == 'H': ## SVG-like path
                ##TODO(elbaschid): is this a valid assumption?
                warnings.warn(
                    'ommiting path outside of component.'
                )
                ## skip description of path
                num_lines = params['num_lines']
                for dummy in range(num_lines):
                    stream.readline()

            elif obj_type == 'U': ## bus (only graphical feature NOT component)
                self._parse_bus(params)

            obj_type, params = self._parse_command(stream)

        ## process net segments into nets & net points and add to design
        self.divide_segments()
        calculated_nets = self.calculate_nets()

        for cnet in calculated_nets:
            self.design.add_net(cnet)

        return self.design

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

        if mirror == 1:
            angle = abs(angle - 90)

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

    def parse_component(self, stream, params):
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
        basename, dummy = os.path.splitext(params['basename'])
        ## component has not been parsed yet
        if basename in self.design.components.components:
            component = self.design.components.components[basename]
            ## skipping embedded data is required

            if basename.startswith('EMBEDDED'):
                self.skip_embedded_section(stream)

        else:
            ##check if sym file is embedded or referenced 
            if basename.startswith('EMBEDDED'):
                ## embedded only has to be processed when NOT in symbol lookup
                if basename not in self.known_symbols:
                    component = self.parse_component_data(stream, params)
            else:
                if basename not in self.known_symbols:
                    raise GEDAError(
                        "referenced symbol file '%s' unkown" % basename
                    )

                ## requires parsing of referenced symbol file
                f_in = open(self.known_symbols[basename], "r")

                typ, dummy = self._parse_command(f_in)
                if typ != 'v':
                    raise GEDAError(
                        "cannot convert file, not in gEDA format"
                    )

                component = self.parse_component_data(f_in, params) 

                f_in.close()
                        
            self.design.add_component(basename, component)

        ## get all attributes assigned to component instance
        attributes = self._parse_environment(stream)

        ## refdes attribute is name of component (mandatory as of gEDA doc)
        ## examples if gaf repo have components without refdes, use part of
        ## basename
        if attributes is not None:
            instance = ComponentInstance(
                attributes.get('_refdes', component.name),
                component.name, 
                0
            )
        else:
            instance = ComponentInstance(
                component.name, 
                component.name, 
                0
            )

        ## generate a component instance using attributes
        self.design.add_component_instance(instance)

        if attributes is not None:
            for key, value in attributes.items():
                instance.add_attribute(key, value)

        comp_x, comp_y = self.conv_coords(params['x'], params['y'])

        symbol = SymbolAttribute(
            comp_x, comp_y, 
            self.conv_angle(params['angle'])
        )
        instance.add_symbol_attribute(symbol)

        ## add annotation for refdes
        symbol.add_annotation(
            Annotation('{{refdes}}', comp_x, comp_y, 0.0, 'true')
        )
        symbol.add_annotation(
            Annotation('{{device}}', comp_x, comp_y+10, 0.0, 'true')
        )

        return component, instance

    def parse_component_data(self, stream, params):
        """ Creates a component from the component *params* and the 
            following commands in the stream. If the component data
            is embedded in the schematic file, all coordinates will
            be translated into the origin first. 
            Only a single symbol/body is created for each component
            since gEDA symbols contain exactly one description. 
            
            Returns the newly created Component object.
        """
        basename, dummy = os.path.splitext(params['basename'])

        saved_offset = self.offset
        self.offset = shape.Point(0, 0)

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

        while typ is not None:

            if typ == 'T':
                key, value = self._parse_text(stream, params)
                if key is None:
                    ##TODO(elbaschid): annotation text in component. what to do?
                    pass
                elif key == '_refdes' and '?' in value:
                    prefix, suffix = value.split('?') 
                    component.add_attribute('_prefix', prefix)
                    component.add_attribute('_suffix', suffix)
                else:
                    assert(key not in ['_refdes', 'refdes'])
                    component.add_attribute(key, value)
            elif typ == 'L':
                body.add_shape(
                    self._parse_line(params)
                )

            elif typ == 'B':
                body.add_shape(
                    self._parse_box(params)
                )

            elif typ == 'C':
                body.add_shape(
                    self._parse_circle(params)
                )

            elif typ == 'A':
                body.add_shape(
                    self._parse_arc(params)
                )

            elif typ == 'P':
                body.add_pin(
                    self._parse_pin(stream, params)
                )
            elif typ == 'H':
                for new_shape in self._parse_path(stream, params):
                    body.add_shape(new_shape)

            elif typ == 'G':
                warnings.warn(
                    "ignoring picture/font in gEDA file. Not supported!"
                )

            else:
                pass

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
    
    def _parse_text(self, stream, params):
        """ Parses text element and determins if text is a text object
            or an attribute. 
            Returns a tuple (key, value). If text is an annotation key is None. 
        """
        num_lines = params['num_lines']

        text = []
        for dummy in range(int(num_lines)):
            text.append(stream.readline())

        text_str = ''.join(text).strip()

        if num_lines == 1 and '=' in text_str:
            return self._parse_attribute(text_str, params['visibility'])

        return None, text_str
    
    def _create_annotation(self, text, params):
        """ Creates an Annotation object from *text* using position,
            rotation and visibility from *params*.
            Returns an Annotation object.
        """
        return Annotation(
            text,
            self.x_to_px(params['x']),
            self.y_to_px(params['y']),
            self.conv_angle(params['angle']),
            self.conv_bool(params['visibility']),
        )

    @staticmethod
    def _parse_attribute(text, visibility):
        """ Creates a tuple of (key, value) from the attribute text.
            If visibility is '0' the attribute key is prefixed with '_'
            to make it a hidden attribute.
            Returns a tuple of key and value.
        """
        key, value = text.split('=', 1)
        ## prefix attributes that are marked as invisible
        if visibility == 0:
            key = "_"+key
        ## these are special attributes that are treated differently
        elif key in ['netname', 'pinnumber', 'pinlabel', 'refdes']:
            key = "_"+key

        return key.strip(), value.strip()

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
        elif (pt_c.x-pt_a.x)*(pt_b.y-pt_a.y) == (pt_b.x-pt_a.x)*(pt_c.y-pt_a.y):
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
                key, value = self._parse_text(stream, params)
                attributes[key] = value

            typ, params = self._parse_command(stream)

        return attributes

    def calculate_nets(self):
        """ Calculate connected nets from previously stored segments
            and netpoints. The code has been adapted from the kiCAD 
            parser since the definition of segements in the schematic
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
            new_net.attributes['_name'] = net_name
            new_net.connect(seg)
            found = True

            while found:
                found = set()

                for seg in self.segments: # iterate over segments
                    if new_net.connected(seg): # segment touching the net
                        new_net.connect(seg) # add the segment
                        found.add(seg)

                for seg in found:
                    self.segments.remove(seg)

            nets.append(new_net)

        ## check if names are available for calculated nets 
        for net_obj in nets:
            annotation_x = annotation_y = 0
            for point_id, net_point in net_obj.points.items():
                ## check for stored net names based on pointIDs
                if point_id in self.net_names:
                    net_obj.net_id = self.net_names[point_id]
                    net_obj.attributes['_name'] = self.net_names[point_id]

                    annotation_x, annotation_y = net_point.x, net_point.y

            if '_name' in net_obj.attributes:
                annotation = Annotation(
                    "{{_name}}", ## annotation referencing attribute '_name' 
                    self.x_to_px(annotation_x),
                    self.y_to_px(annotation_y),
                    self.conv_angle(0.0),
                    self.conv_bool(1),
                )
                net_obj.add_annotation(annotation)

        return nets

    def _parse_bus(self, params): 
        """ Processing a bus instance with start end end coordinates
            at (x1, y1) and (x2, y2). *color* is ignored. *ripperdir*
            defines the direction in which the bus rippers are oriented
            relative to the direction of the bus. 
        """
        x1, x2 = params['x1'], params['x2']
        y1, y2 = params['y1'], params['y2']
        ripperdir = params['ripperdir']

        ## ignore bus when length or ripperdir is zero
        if (x1 == x2 and y1 == y2) or ripperdir == 0:
            return 

        pta_x, pta_y = self.conv_coords(x1, y1)
        ptb_x, ptb_y = self.conv_coords(x2, y2)

        self.segments.add((
            self.get_netpoint(pta_x, pta_y),
            self.get_netpoint(ptb_x, ptb_y)
        ))

    def _parse_segment(self, stream, params):
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
            if attributes.has_key('_netname'):
                net_name = attributes['_netname']
                if net_name not in self.net_names.values():
                    self.net_names[pt_a.point_id] = net_name

    def _parse_path(self, stream, params):
        """ Parses a SVG-like path provided path into a list
            of simple shapes. The gEDA formats allows only line
            and curve segments with absolute coordinates. Hence,
            shapes are either Line or BezierCurve objects. 
            The method processes the stream data according to 
            the number of lines in *params*. 
            Returns a list of Line and BezierCurve shapes.
        """
        num_lines = params['num_lines']
        command = stream.readline().strip().split(self.DELIMITER)

        if command[0] != 'M':
            raise GEDAError('found invalid path in gEDA file')

        def get_coords(string):
            """ Get coordinates from string with comma-sparated notation."""
            x, y = string.strip().split(',')
            return (self.x_to_px(int(x)), self.y_to_px(int(y)))

        shapes = []
        current_pos = initial_pos = (get_coords(command[1]))

        ## loop over the remaining lines of commands (after 'M')
        for dummy in range(num_lines-1):
            command = stream.readline().strip().split(self.DELIMITER)

            ## draw line from current to given position
            if command[0] == 'L':
                assert(len(command) == 2)
                end_pos = get_coords(command[1])

                line = shape.Line(current_pos, end_pos)
                shapes.append(line)

                current_pos = end_pos

            ## draw curve from current to given position
            elif command[0] == 'C':
                assert(len(command) == 4)
                control1 = get_coords(command[1])
                control2 = get_coords(command[2])
                end_pos = get_coords(command[3])

                curve = shape.BezierCurve(
                    control1,
                    control2,
                    current_pos,
                    end_pos
                )
                shapes.append(curve)

                current_pos = end_pos

            ## end of sub-path, straight line from current to initial position
            elif command[0] in ['z', 'Z']:
                shapes.append(
                    shape.Line(current_pos, initial_pos)
                )

            else:
                raise GEDAError(
                    "invalid command type in path '%s'" % command[0]
                )

        return shapes 
    
    def _parse_arc(self, params):
        """ Creates an Arc object from the parameter in *params*. All 
            style related parameters are ignored.
            Returns Arc object.
        """
        return shape.Arc(
            self.x_to_px(params['x']),
            self.y_to_px(params['y']),
            self.conv_angle(params['startangle']),
            self.conv_angle(params['startangle'] + params['sweepangle']),
            self.to_px(params['radius']),
        )

    def _parse_line(self, params):
        """ Creates a Line object from the parameters in *params*. All
            style related parameters are ignored.
            Returns a Line object.
        """
        return shape.Line(
            self.conv_coords(params['x1'], params['y1']),
            self.conv_coords(params['x2'], params['y2']),
        )

    def _parse_box(self, params):
        """ Creates rectangle from gEDA box with origin in bottom left
            corner. All style related values are ignored.
            Returns a Rectangle object.
        """
        return shape.Rectangle(
            self.x_to_px(params['x']+params['height']),
            self.y_to_px(params['y']),
            self.to_px(params['width']),
            self.to_px(params['height'])
        )

    def _parse_circle(self, params):
        """ Creates a Circle object from the gEDA parameters in *params. All
            style related parameters are ignored. 
            Returns a Circle object.
        """
        return shape.Circle(
            self.x_to_px(params['x']),
            self.y_to_px(params['y']),
            self.to_px(params['radius']),
        )

    def _parse_pin(self, stream, params):
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
            raise GEDAError('mandatory pin attributes missing')

        if '_pinnumber' not in attributes:
            raise GEDAError(
                "mandatory attribute '_pinnumber' not assigned to pin"
            )

        whichend = params['whichend']

        ## determine wich end of the pin is the connected end
        ## 0: first point is connector
        ## 1: second point is connector
        if whichend == 0:
            connect_end = self.conv_coords(params['x1'], params['y1']) 
            null_end = self.conv_coords(params['x2'], params['y2']) 
        else:
            null_end = self.conv_coords(params['x1'], params['y1'])
            connect_end = self.conv_coords(params['x2'], params['y2'])

        label = None
        if '_pinlabel' in attributes:
            label = shape.Label(
                connect_end[0],
                connect_end[1],
                attributes.get('_pinlabel'), 
                'left',
                0.0
            )

        return components.Pin(
            attributes['_pinnumber'], #pin number
            null_end,
            connect_end,
            label=label
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
        command_data = stream.readline().strip().split(self.DELIMITER)

        if len(command_data[0]) == 0 or command_data[0] in [']', '}']:
            return None, []

        object_type, command_data = command_data[0].strip(), command_data[1:]

        params = {}
        for idx, (name, typ) in enumerate(self.OBJECT_TYPES[object_type]):
            params[name] = typ(command_data[idx])

        assert(len(params) == len(self.OBJECT_TYPES[object_type]))

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

        if object_type not in self.OBJECT_TYPES:
            raise GEDAError("unknown type '%s' in file" % object_type)
        
        return object_type, params 

    @classmethod
    def to_px(cls, value):
        """ Converts value in MILS to pixels using the parsers
            scale factor. 
            Returns an integer value converted to pixels.
        """
        return int(value / float(cls.SCALE_FACTOR))

    def x_to_px(self, x_mils):
        """ Convert *px* from MILS to pixels using the scale
            factor and translating it allong the X-axis in 
            offset. 

            Returns translated and converted X coordinate.
        """
        return int((x_mils - self.offset.x) / self.SCALE_FACTOR)

    def y_to_px(self, y_mils):
        """ Convert *py* from MILS to pixels using the scale
            factor and translating it allong the Y-axis in 
            offset. 

            Returns translated and converted Y coordinate.
        """
        return int((y_mils - self.offset.y) / self.SCALE_FACTOR)

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
        """ Converts *angle* (in degrees) to pi radians."""
        angle = angle % 360.0
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
            for dirpath, dummy, filenames in os.walk(symbol_dir):
                for filename in filenames:
                    if filename.endswith('.sym'):
                        filepath = os.path.join(dirpath, filename)

                        filename, dummy = os.path.splitext(filename)
                        known_symbols[filename] = filepath

    return known_symbols
