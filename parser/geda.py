#!/usr/bin/env python
""" The gEDA schematics are based on a grid in MILS (1/1000 of an inch).
"""

import os

from core import shape
from core import components
from core import net

from core.design import Design
from core.annotation import Annotation
from core.component_instance import ComponentInstance
from core.component_instance import SymbolAttribute


class GEDAParserError(Exception):
    pass


class GEDA:
    """ The GEDA Format Parser """

    DELIMITER = ' '
    SCALE_FACTOR = 10 #maps 1000 MILS to 10 pixels
    OBJECT_TYPES = set([ 
        'v', # gEDA version
        'C', # component
        'N', # net segment
        'U', # bus (only graphical aid, not a component)
        'T', # text or attribute (context)
        'P', # pin (in sym)
        'L', # line
        'B', # box
        'V', # circle
        'A', # arc
        'H', # SVG-like path
        ## path related types
        'M', # moveto (absolute)
        'm', # moveto (relative)
        'L', # lineto (absolute)
        'l', # lineto (relative)
        'C', # curveto (absolute)
        'c', # curveto (relative)
        'Z', # closepath
        'z', # closepath
        ## environments
        '{', '}', # attributes
        '[', ']', # embedded component
        ## valid types but are ignored
        'G', #picture
    ])

    def __init__(self, symbol_dirs=None):
        """ Constuct a gEDA parser object. Specifying a list of symbol 
            directories in *symbol_dir* will provide a symbol file 
            lookup in the specified directories. The lookup will be 
            generated instantly examining each directory (if it exists).

            Kwargs:
                symbol_dirs (list): List of directories containing .sym 
                    files
        """
        if symbol_dirs is None:
            ##TODO: should default symdirs be used??
            symbol_dirs = []
            #    '/usr/share/gEDA/sym',
            #    '/usr/local/share/gEDA/sym',
            #]

        self.symbol_lookup = {}

        self.design = None 
        self.segments = None
        self.net_points = None

        for symbol_dir in symbol_dirs:
            if os.path.exists(symbol_dir):
                for dirpath, files, filenames in os.walk(symbol_dir):
                    for filename in filenames:
                        if filename.endswith('.sym'):
                            filepath = os.path.join(dirpath, filename)
                            self.symbol_lookup[filename] = filepath

        print """WARNING: conversion will ignore style and color data in gEDA \
format!"""
    
    def parse(self, filename):
        """ Parse a gEDA file into a design """

        fh = open(filename, "r")

        typ, params = self.parse_element(fh)
        if typ != 'v':
            raise GEDAParserError("cannot convert file, not in gEDA format")

        design = self.parse_schematic(fh)

        fh.close()

        return design

    def parse_schematic(self, stream):
        self.design = Design()
        self.segments = set()
        self.net_points = dict() 

        obj_type, params = self.parse_element(stream)

        while obj_type is not None:

            if obj_type == 'T':
                ##Convert regular text or attribute
                key, value = self.parse_text(stream, *params)
                
                if key is None:
                    ## text is annotation
                    self.design.design_attributes.add_annotation(value)
                else:
                    ## text is attribute
                    self.design.design_attributes.add_attribute(key, value)

            elif obj_type == 'G' :
                ## picture/font types are not supported in upverter
                print "WARNING: ignoring picture/font in gEDA file. Not supported!"
            elif obj_type == 'C':
                ## ignore title components (not real components)
                if not params[-1].startswith('title'):
                    component, instance = self.parse_component(stream, *params)

            elif obj_type == 'N':
                self.parse_segment(stream, *params)

            elif obj_type == 'U':
                ## bus (only graphical feature NOT component)
                ##TODO(elbaschid): process bus into NET
                ##TODO(elbaschid): check for optional attribute definition in {}
                raise NotImplementedError()

            obj_type, params = self.parse_element(stream)

        self.divide_segments()
        nets = self.calculate_nets(self.segments)

        for net in nets:
            self.design.add_net(net)

        return self.design

    def parse_component(self, stream, x, y, selectable, angle, mirror, basename):

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
                if basename not in self.symbol_lookup:
                    component = self.parse_embedded_component(stream, x, y, selectable, angle, mirror, basename)
            else:
                if basename not in self.symbol_lookup:
                    raise GEDAParserError(
                        "referenced symbol file '%s' unkown" % basename
                    )

                ## requires parsing of referenced symbol file
                fh = open(self.symbol_lookup[basename], "r")

                typ, params = self.parse_element(fh)
                if typ != 'v':
                    raise GEDAParserError("cannot convert file, not in gEDA format")

                component = self.parse_embedded_component(fh, x, y, selectable, angle, mirror, basename)

                fh.close()
                        
            self.design.add_component(basename, component)

        ## get all attributes assigned to component instance
        attributes = self.parse_environment(stream)

        ## refdes attribute is name of component (mandatory as of gEDA doc)
        ## examples if gaf repo have components without refdes, use part of basename
        refdes = component.name.replace('.sym', '')
        if attributes is not None:
            refdes = attributes.get('refdes', refdes)

        ## generate a component instance using attributes
        instance = ComponentInstance(refdes, component.name, 0)
        self.design.add_component_instance(instance)

        if attributes is not None:
            for key, value in attributes.items():
                instance.add_attribute(key, value)

        comp_x, comp_y = self.conv_coords(x, y)

        symbol = SymbolAttribute(comp_x, comp_y, self.conv_angle(angle))
        instance.add_symbol_attribute(symbol)

        ##TODO(elbaschid): add annotation for refdes
        symbol.add_annotation(
            Annotation('{{refdes}}', comp_x, comp_y, 0.0, 'true')
        )
        symbol.add_annotation(
            Annotation('{{device}}', comp_x, comp_y, 0.0, 'true')
        )

        return component, instance

    def parse_embedded_component(self, stream, x, y, selectable, angle, mirror, basename):
        move_to = None
        if basename.startswith('EMBEDDED'):
            move_to = (x, y)

        ## grab next line (should be '[' or 
        typ, params = self.parse_element(stream, move_to)

        if typ == '[':
            typ, params = self.parse_element(stream, move_to)

        component = components.Component(basename)
        symbol = components.Symbol()
        component.add_symbol(symbol)
        body = components.Body()
        symbol.add_body(body)

        while typ is not None:

            if typ == 'T':
                key, value = self.parse_text(stream, *params)
                if key is None:
                    ##TODO(elbaschid): not sure what to do with text here??
                    pass
                else:
                    component.add_attribute(key, value)

            elif typ == 'L':
                line = self.parse_line(*params)
                body.add_shape(line)

            elif typ == 'B':
                rect = self.parse_box(*params)
                body.add_shape(rect)

            elif typ == 'C':
                circle = self.parse_circle(*params)
                body.add_shape(circle)

            elif typ == 'A':
                arc = self.parse_arc(*params)
                body.add_shape(arc)

            elif typ == 'P':
                pin = self.parse_pin(stream, *params)
                body.add_pin(pin)

            elif typ == 'H':
                #path, offset=offset
                raise NotImplementedError()   

            elif typ == 'G':
                print "WARNING: ignoring picture/font in gEDA file. Not supported!"

            else:
                pass

            typ, params = self.parse_element(stream, move_to)

        return component

    def divide_segments(self):
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
    
    def parse_text(self, stream, x, y, color, size, visiblity, 
                    show_name_value, angle, alignment, num_lines):
        """ Parses text element and determins if text is a text object
            or an attribute. 
            Returns a tuple (key, value) for attribute and (None, Annotation())
                otherwise.
        """
        text = []
        for idx in range(int(num_lines)):
            text.append(stream.readline())

        text_str = ''.join(text).strip()

        if num_lines == 1 and '=' in text_str:
            key, value = text_str.split('=', 1)
            return key.strip(), value.strip()

        return None, Annotation(
            text_str,
            self.conv_mils(x),
            self.conv_mils(y),
            self.conv_angle(angle),
            self.conv_bool(visiblity),
        )

    def skip_embedded_section(self, stream):
        typ = stream.readline().split(self.DELIMITER, 1)[0].strip()

        while typ != ']':
            typ = stream.readline().split(self.DELIMITER, 1)[0].strip()

    def parse_environment(self, stream):
        """ Checks if attribute environment starts in the next line
            (marked by '{'). Environment only contains text elements
            interpreted as text. 
            Returns a dictionary of attributes.
        """
        current_pos = stream.tell()
        typ, params = self.parse_element(stream)

        #go back to previous position when no environment in stream
        if typ != '{':
            stream.seek(current_pos)
            return None 

        typ, params = self.parse_element(stream)

        attributes = {}
        while typ is not None:
            if typ == 'T':
                key, value = self.parse_text(stream, *params)
                attributes[key] = value

            typ, params = self.parse_element(stream)

        return attributes

    def store_netpoint(self, x, y):
        if (x, y) not in self.net_points:
            self.net_points[(x, y)] = net.NetPoint('%da%d' % (x, y), x, y)
        return self.net_points[(x, y)]

    def intersects_segment(self, segment, pt_c):
        pt_a, pt_b = segment

        #check vertical segment
        if pt_a.x == pt_b.x == pt_c.x:
            if min(pt_a.y, pt_b.y) < pt_c.y < max(pt_a.y, pt_b.y):
                return True
        #check vertical segment
        elif pt_a.y == pt_b.y == pt_c.y:
            if min(pt_a.x, pt_b.x) < pt_c.x < max(pt_a.x, pt_b.x):
                return True
        ## point C not on segment
        return False

    def parse_segment(self, stream, x1, y1, x2, y2, color):
        #TODO(elbaschid): store segement for processing later
        x1, y1 = self.conv_coords(x1, y1)
        x2, y2 = self.conv_coords(x2, y2)

        ## store segment points in global point list
        pt_a = self.store_netpoint(x1, y1)
        pt_b = self.store_netpoint(x2, y2)

        ## add segment to global list for later processing
        self.segments.add((pt_a, pt_b))

        attributes = self.parse_environment(stream)
        #if attributes is not None:
        #    #TODO(elbaschid): create net with name in attributes 
        #    pass

    def calculate_nets(self, segments):
        nets = []

        # Iterate over the segments, removing segments when added to a net
        while segments:
            seg = segments.pop() # pick a point
            new_net = net.Net('')
            new_net.connect(seg)
            found = True

            while found:
                found = set()

                for seg in segments: # iterate over segments
                    if new_net.connected(seg): # segment touching the net
                        new_net.connect(seg) # add the segment
                        found.add(seg)

                for seg in found:
                    segments.remove(seg)

            nets.append(new_net)

        return nets

    def parse_bus(self):
        raise NotImplementedError()

    def parse_path(self):
        raise NotImplementedError()

    def parse_arc(self, center_x, center_y, radius, start_angle, sweep_angle, *style_args):
        return shape.Arc(
            self.conv_mils(center_x),
            self.conv_mils(center_y),
            self.conv_angle(start_angle),
            self.conv_angle(start_angle + sweep_angle),
            self.conv_mils(radius),
        )

    def parse_line(self, start_x, start_y, end_x, end_y, *style_args):
        return shape.Line(
            self.conv_coords(start_x, start_y),
            self.conv_coords(end_x, end_y),
        )

    def parse_box(self, x, y, width, height, *style_args):
        """ Creates rectangle from gEDA box with origin in bottom left
            corner. All style related values are ignored.
        """
        return shape.Rectangle(
            self.conv_mils(x+height),
            self.conv_mils(y),
            self.conv_mils(width),
            self.conv_mils(height)
        )

    def parse_circle(self, x, y, radius, *style_args):
        return shape.Circle(
            self.conv_mils(x),
            self.conv_mils(y),
            self.conv_mils(radius),
        )

    def parse_pin(self, stream, x1, y1, x2, y2, color, pintype, whichend):

        ## pin requires an attribute enviroment, so parse it first
        attributes = self.parse_environment(stream)
        
        if attributes is None:
            raise GEDAParserError('mandatory pin attributes missing')

        if 'pinnumber' not in attributes:
            raise GEDAParserError(
                "mandatory attribute 'pinnumber' not assigned to pin"
            )

        ## determine wich end of the pin is the connected end
        ## 0: first point is connector
        ## 1: second point is connector
        if whichend == 0:
            connect_end = self.conv_coords(x1, y1) 
            null_end = self.conv_coords(x2, y2) 
        else:
            null_end = self.conv_coords(x1, y1) 
            connect_end = self.conv_coords(x2, y2) 

        label = None
        if 'pinlabel' in attributes:
            label = shape.Label(
                connect_end[0],
                connect_end[1],
                attributes.get('pinlabel'), 
                'left',
                0.0
            )
        return components.Pin(
            attributes['pinnumber'], #pin number
            null_end,
            connect_end,
            label=label
        )

    def parse_element(self, stream, move_to=None):
        element_items = stream.readline().strip().split(self.DELIMITER)

        if len(element_items[0]) == 0 or element_items[0] in [']', '}']:
            return None, []

        object_type = element_items[0].strip()

        if object_type == 'C':
            ## last parameter is string, do not convert
            params = [int(x) for x in element_items[1:-1]]
            params.append(element_items[-1])
        else:
            params = [int(x) for x in element_items[1:]]

        if move_to is not None:
            ## element in EMBEDDED component need to be moved
            ## to origin (0, 0) from component origin
            if object_type in ['T', 'B', 'C', 'A']:
                params[0] = params[0] - move_to[0]
                params[1] = params[1] - move_to[1]
            elif object_type in ['L', 'P']:
                params[0] = params[0] - move_to[0]
                params[1] = params[1] - move_to[1]
                params[2] = params[2] - move_to[0]
                params[3] = params[3] - move_to[1]

        if object_type not in self.OBJECT_TYPES:
            raise GEDAParserError("unknown type '%s' in file" % object_type)
        
        return object_type, params 

    def conv_mils(self, mils):
        """ Converts *mils* from MILS (1/1000 of an inch) to 
            pixel units based on a scale factor. The converted 
            value is a multiple of 10px.
        """
        scaled = int(mils) / float(self.SCALE_FACTOR)
        return int(scaled)

    def conv_coords(self, orig_x, orig_y):
        """ Converts coordinats *orig_x* and *orig_y* from MILS
            to pixel units based on scale factor. The converted
            coordinates are in multiples of 10px.
        """
        orig_x, orig_y = int(orig_x), int(orig_y)
        return (
            self.conv_mils(orig_x),
            self.conv_mils(orig_y)
        )

    def conv_bool(self, value):
        """ Converts *value* into string representing boolean
            'true' or 'false'. *value* can be of any numeric or
            boolean type.
        """
        if value in ['true', 'false']:
            return value
        return str(bool(int(value)) == True).lower()

    def conv_angle(self, angle):
        """ Converts *angle* (in degrees) to pi radians."""
        angle = angle % 360.0
        return round(angle/180.0, 1)
