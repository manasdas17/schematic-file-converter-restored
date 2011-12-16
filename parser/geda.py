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
    SCALE_FACTOR = 10 #maps 100 MILS to 10 pixels
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

        self.design = Design()

        self.segments = set()
        self.net_point = dict()
        self.net_names = dict()

        fh = open(filename, "r")

        typ, params = self.parse_element(fh)
        if typ != 'v':
            raise GEDAParserError("cannot convert file, not in gEDA format")

        ##TODO(elbaschid): handle parsing of the input file

        fh.close()
        return design

    def parse_schematic_file(self, filename):
        fh = open(filename, "r")

        typ, params = self.parse_element(fh)
        if typ != 'v':
            raise GEDAParserError("cannot convert file, not in gEDA format")

        self.parse_schematic(fh)

        fh.close()

    def parse_schematic(self, stream):
        self.design = Design()
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
                    self.design.add_design_attributes(key, value)

            elif obj_type == 'G' :
                ## picture/font types are not supported in upverter
                print "WARNING: ignoring picture/font in gEDA file. Not supported!"
            elif obj_type == 'C':
                ## ignore title components (not real components)
                if not params[-1].startswith('title'):
                    component, instance = self.parse_component(stream, *params)

            elif obj_type == 'N':
                self.parse_segment(stream, *params)
                ##TODO(elbaschid): check for attribute definitions in {}

            elif obj_type == 'U':
                ## bus (only graphical feature NOT component)
                ##TODO(elbaschid): process bus into NET
                ##TODO(elbaschid): check for optional attribute definition in {}
                raise NotImplementedError()

            obj_type, params = self.parse_element(stream)

    def parse_component(self, stream, x, y, selectable, angle, mirror, basename):

        ## component has not been parsed yet
        if basename in self.design.components.components:
            component = self.design.components.components[basename]

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
                        
            self.design.add_component(component.name, component)

        ## generate a component instance using attributes
        instance = ComponentInstance(component.name, basename, 0)
        self.design.add_component_instance(instance)

        comp_x, comp_y = self.conv_coords(x, y)

        symbol = SymbolAttribute(comp_x, comp_y, self.conv_angle(angle))
        instance.add_symbol_attribute(symbol)

        ##TODO(elbachid): add annotation for refdes
        symbol.add_annotation(
            Annotation('{{refdes}}', comp_x, comp_y, 0.0, 'true')
        )
        symbol.add_annotation(
            Annotation('{{device}}', comp_x, comp_y, 0.0, 'true')
        )

        attributes = self.parse_environment(stream)
        for key, value in attributes.items():
            instance.add_attribute(key, value)

        return component, instance

    def parse_embedded_component(self, stream, x, y, selectable, angle, mirror, basename, normalise=False):
        ## grab next line (should be '[' or 
        typ, params = self.parse_element(stream)

        if typ == '[':
            typ, params = self.parse_element(stream)

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
                elif key == 'device':
                    component.name = value
                else:
                    component.add_attribute(key, value)

            elif typ == 'L':
                body.add_shape(
                    self.parse_line(*params)
                )

            elif typ == 'B':
                body.add_shape(
                    self.parse_box(*params)
                )

            elif typ == 'C':
                body.add_shape(
                    self.parse_circle(*params) 
                )

            elif typ == 'A':
                body.add_shape(
                    arc = self.parse_arc(*params)
                )

            elif typ == 'P':
                body.add_pin(
                    self.parse_pin(stream, *params)
                )

            elif typ == 'H':
                #path
                raise NotImplementedError()   

            elif typ == 'G':
                print "WARNING: ignoring picture/font in gEDA file. Not supported!"

            else:
                pass

            typ, params = self.parse_element(stream)

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
        while typ != '}':
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

        #attributes = self.parse_environment(stream)
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
                attributes.get('pinlabel'), 
                connect_end[0],
                connect_end[1],
                'left',
                0.0
            )
        return components.Pin(
            attributes['pinnumber'], #pin number
            null_end,
            connect_end,
            label=label
        )

    def parse_element(self, stream):
        element_items = stream.readline().strip().split(self.DELIMITER)

        if len(element_items[0]) == 0:
            return None, []

        object_type = element_items[0].strip()

        if object_type == 'C':
            ## last parameter is string, do not convert
            params = [int(x) for x in element_items[1:-1]]
            params.append(element_items[-1])
        else:
            params = [int(x) for x in element_items[1:]]

        if object_type not in self.OBJECT_TYPES:
            raise GEDAParserError("unknown type '%s' in file" % object_type)
        
        return object_type, params 

    def conv_mils(self, mils):
        """ Converts *mils* from MILS (1/1000 of an inch) to 
            pixel units based on a scale factor. The converted 
            value is a multiple of 10px.
        """
        scaled = int(mils) / self.SCALE_FACTOR
        return int(scaled / 10.0) * 10

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
