#!/usr/bin/env python
""" The gEDA schematics are based on a grid in MILS (1/1000 of an inch).
"""

import os

from core import shape

from core.design import Design
from core.annotation import Annotation


class GEDAParserError(Exception):
    pass


class GEDA:
    """ The GEDA Format Parser """

    DELIMITER = ' '
    SCALE_FACTOR = 10 #maps 100 MILS to 10 pixels

    OBJECT_TYPES = {
        'v': None, # gEDA version
        'C': None, # component
        'N': None, # net segment
        'U': None, # bus (only graphical aid, not a component)
        # text or attribute (context)
        'T': None, 

        'P': None, # pin (in sym)
        'L': None, # line
        'G': None, # box
        'B': None, # circle
        'A': None, # arc
        'H': None, # SVG-like path
    }

    PATH_INSTRUCTION = {
        ## path related types
        'M': None, # moveto (absolute)
        'm': None, # moveto (relative)

        'L': None, # lineto (absolute)
        'l': None, # lineto (relative)

        'C': None, # curveto (absolute)
        'c': None, # curveto (relative)

        'Z': None, # closepath
        'z': None, # closepath
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
        if symbol_dirs is None:
            ##TODO: should default symdirs be used??
            symbol_dirs = []
            #    '/usr/share/gEDA/sym',
            #    '/usr/local/share/gEDA/sym',
            #]

        self.symbol_lookup = {}

        self.design = None 

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

        fh = open(filename, "r")

        version_line = fh.readline().split(self.DELIMITER)
        if version_line[0] != 'v':
            raise GEDAParserError("cannot convert file, not in gEDA format")



        fh.close()
        return design

    def parse_object(self, stream):
        params = stream.readline().split(self.DELIMITER)
        obj_type = params.pop(0)

        if obj_type not in self.OBJECT_TYPES:
            raise GEDAParserError("unknown type '%s' in file", obj_type)

        if obj_type == 'T':
            ##FIXME(elbaschid): if text has key=value form -> design level attribute

            ##Convert regular text into annotation
            annotation = self.parse_text(stream, *params)

        elif obj_type == 'G':
            ##(elbaschid): pictures are not supported in upverter
            print "WARNING: ignoring picture in gEDA file. Not supported!"
        elif obj_type == 'C':
            ##TODO(elbaschid): check if sym file is embedded or not 
            ##TODO(elbaschid): if EMBEDDED check for [] holding embedded definition
            ##TODO(elbaschid): check for optional attribute definition in {}
            raise NotImplementedError()
        elif obj_type == 'N':
            self.parse_segment(*params)
            ##TODO(elbaschid): process net segment into NET
            ##TODO(elbaschid): check for optional attribute definition in {}
            raise NotImplementedError()
        elif obj_type == 'U':
            ## bus (only graphical feature NOT component)
            ##TODO(elbaschid): process bus into NET
            ##TODO(elbaschid): check for optional attribute definition in {}
            raise NotImplementedError()

        ## object types of different environemnts
        elif obj_type == '{':
            ##Attribute lists
            raise NotImplementedError()
        elif obj_type == '[':
            ##embedded component
            raise NotImplementedError()
    
    def parse_text(self, stream, x, y, color, size, visiblity, 
                     show_name_value, angle, alignment, num_lines):

        text = []
        for idx in range(int(num_lines)):
            text.append(stream.readline())

        text_str = ''.join(text)

        return Annotation(
            text_str,
            self.conv_mils(x),
            self.conv_mils(y),
            self.conv_angle(angle),
            self.conv_bool(visiblity),
        )

    def parse_environment(self):
        raise NotImplementedError()

    def parse_embedded_component(self):
        raise NotImplementedError()

    def parse_component(self):
        raise NotImplementedError()

    def parse_segement(self):
        raise NotImplementedError()

    def parse_bus(self):
        raise NotImplementedError()

    def parse_path(self):
        raise NotImplementedError()

    def parse_arc(self, center_x, center_y, radius, start_angle, sweep_angle, *args):
        return shape.Arc(
            self.conv_mils(center_x),
            self.conv_mils(center_y),
            self.conv_angle(start_angle),
            self.conv_angle(start_angle + sweep_angle),
            self.conv_mils(radius),
        )
        raise NotImplementedError()

    def parse_line(self):
        raise NotImplementedError()

    def parse_box(self):
        raise NotImplementedError()

    def parse_circle(self):
        raise NotImplementedError()

    def parse_pin(self):
        raise NotImplementedError()

    def parse_element(self, stream):
        element_items = stream.readline().split(self.DELIMITER)
        object_type = element_items[0]
        params = [int(x) for x in element_items[1:]]

        ##TODO(elbaschid): check for valid object types
        
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
        return str(bool(value) == True).lower()

    def conv_angle(self, angle):
        """ Converts *angle* (in degrees) to pi radians."""
        angle = angle % 360.0
        return round(angle/180.0, 1)
