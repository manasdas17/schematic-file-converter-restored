#!/usr/bin/env python
""" The gEDA schematics are based on a grid in MILS (1/1000 of an inch).
"""

from core.design import Design


class GEDA:
    """ The GEDA Format Parser """

    DELIMITER = ' '

    OBJECT_TYPES = {
        'v': None, # gEDA version
        'L': None, # line
        'G': None, # box
        'B': None, # circle
        'A': None, # arc
        'T': None, # text
        'N': None, # net segment
        'U': None, # bus
        'P': None, # pin (in sym)
        'C': None, # component
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

    def __init__(self):
        pass

    def parse(self, filename):
        """ Parse a gEDA file into a design """
        design = Design()
        f = open(filename, "w")

        f.close()
        return design

    def parse_object(self, stream):
        line = stream.readline().split(self.DELIMITER)

        if line[0] not in self.
        print line
         

    def _parse_line(startx, starty, endx, endy, color, width, capstyle, dashstyle, dashlength, dashspace):
        pass
