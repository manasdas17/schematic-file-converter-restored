#!/usr/bin/env python2
""" This module provides a writer class to generate valid Eagle
    file format data from an OpenJSON design.

    TODO more description

    TODO usage samples
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

# 
# Note: This writer saves file as a 5.11 version one.
#

import struct

#from parser.eagle import EagleBinConsts

class Eagle: # pylint: disable=R0902
    """ The Eagle format writer """

    class Header:
        """ A struct that represents a header """
        constant = 0x10
        template = "=4BI4B3I"

        def __init__(self, version="5.11", numofblocks=0):
            """ Just a constructor
                Num Of Headers has to be validated!
            """
            self.version = version # has to be of x.y (dot-separated) format
            self.numofblocks = numofblocks
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, 0, 0, 
                                   self.numofblocks,
                                   int(self.version.split('.')[0]),
                                   int(self.version.split('.')[1]),
                                   0, 0, 
                                   0, 0, 0
                                  )
            return _ret_val

    class Settings:
        """ A struct that represents ?? settings ??
        """
        constant = 0x11
        template = "=4BI4BII4B"

        # TODO if i need to synchronize access?..
        counter = 0

        def __init__(self, copyno=0, seqno=None):
            """ Just a constructor
            """
            if None == seqno:
                seqno = Eagle.Settings.counter
                Eagle.Settings.counter += 1
            else:
                Eagle.Settings.counter = 1 + seqno
            self.seqno = seqno # looks like first and second blocks
                               #  starts with the same byte set
                               #  but then the second set starts to evolve
            self.copyno = copyno # holds No of a 'Save As..' copy
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, 0, 0,
                                   0,
                                   0, 0xcd, 0, self.copyno,
                                   0x99207800,
                                   0xa9471aa0,
                                   0xcd, 0, 0, 0
                                  )
            return _ret_val

    class Grid:
        """ A struct that represents a grid
        """
        constant = 0x12
        template = "=4B5I"

        unitmask = 0x0f
        units = {
                 0x0f: "inch",
                 0x00: "mic",
                 0x05: "mm",
                 0x0a: "mil",
                }
        lookmask = 2
        look = {
                0: "lines",
                2: "dots",
               }
        showmask = 1
        show = {
                0: False,
                1: True,
               }

        def __init__(self, distance=0.1, unitdist="inch", unit="inch", # pylint: disable=R0913
                style="lines", multiple=1, display=False, altdistance=0.01, 
                altunitdist="inch", altunit="inch"):
            """ Just a constructor
            """
            self.distance = distance
            self.unitdist = unitdist
            self.unit = unit
            self.style = style
            self.multiple = multiple
            self.display = display
            self.altdistance = altdistance
            self.altunitdist = altunitdist
            self.altunit = altunit
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _look = 0
            for _dd in self.show:
                if self.show[_dd] == self.display:
                    _look += _dd
            for _ss in self.look:
                if self.look[_ss] == self.style:
                    _look += _ss

            _units = 0
            for _uu in self.units:
                if self.units[_uu] == self.unit:
                    _units += _uu
                if self.units[_uu] == self.altunit:
                    _units += (_uu << 4)

# strage float format here: 8 bytes ; no idea yet
# thus proceeding in 6.0.0 way: default values are used
# (but units are preserved; 6.0.0 uses default set -- with inches)
            _ret_val = struct.pack(self.template,
                                   self.constant, 0, 
                                   _look, _units,
                                   self.multiple,
                                   0x9999999a, 0x3fb99999,
                                   0x47ae147b, 0x3f847a1e,
                                  )
            return _ret_val

    class Layer:
        """ A struct that represents a layer
        """
        constant = 0x13
        template = "=7B2I9s"

        linkedsignmask = 0x10

        visactmask = 0x0e
        visact = 0x0e
        nvisact = 0x02

        max_embed_len = 9
        no_embed_str = b'\x7f'

#        colors = ['unknown','darkblue','darkgreen','darkcyan',
#                'darkred','unknown','khaki','grey',
## light variants x8
#                 ]
#        fill = ['none','filled',
## total 16; different line and dot patterns
#               ]

        def __init__(self, number, name, color, fill, visible, active, # pylint: disable=R0913
                     linkednumber=None, linkedsign=0):
            """ Just a constructor
            """
            self.number = number
            self.name = name
            self.color = color
            self.fill = fill
            self.visible = visible
            self.active = active
            self.linkedsign = linkedsign
            if None==linkednumber:
                linkednumber = number
            self.linkednumber = linkednumber
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _vis_act_link = 0x00
            if self.visible and self.active:
                _vis_act_link += self.visact
            elif not self.visible and self.active:
                _vis_act_link += self.nvisact
            if self.linkedsign:
                _vis_act_link += self.linkedsignmask

            _name = self.no_embed_str + b'\0\0\0\x09'
            if self.max_embed_len > len(self.name):
                _name = self.name

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, _vis_act_link, 
                                   self.number, self.linkednumber,
                                   self.fill, self.color,
                                   0, 0,
                                   _name,
                                  )
            return _ret_val

    class ShapeSet(object):
        """ A struct that represents a bunch of shapes
        """

        def __init__(self, numofshapes=0, shapes=None):
            """ Just a constructor
            """
            self.numofshapes = numofshapes
            if None == shapes:
                shapes = []
            self.shapes = shapes
            return

    class NamedShapeSet(ShapeSet):
        """ A struct that represents a *named* bunch of shapes
        """

        def __init__(self, name, numofshapes=0, shapes=None):
            """ Just a constructor
            """
            super(Eagle.NamedShapeSet, self).__init__(numofshapes, shapes)
            self.name = name
            return

    class Web(object):
        """ A base struct for a bunch of shapesets
            It's needed to uniform parsing and counting of members
        """

        def __init__(self, name, numofblocks=0, numofshapesets=0, 
                     shapesets=None):
            """ Just a constructor
            """
            self.name = name
            self.numofblocks = numofblocks
            self.numofshapesets = numofshapesets
            if None == shapesets:
                shapesets = []
            self.shapesets = shapesets
            return

    class AttributeHeader:
        """ A struct that represents a header of attributes
        """
        constant = 0x14
        template = "=4B3I3B5s"

        max_embed_len = 5
        no_embed_str = b'\x7f'

        def __init__(self, schematic, numofshapes=0, numofattributes=0):
            """ Just a constructor
            """
            self.schematic = schematic
            self.numofshapes = numofshapes # to be validated!
            self.numofattributes = numofattributes # to be validated!
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _schematic = self.no_embed_str + b'\0\0\0\x09'
            if self.max_embed_len > len(self.schematic):
                _schematic = self.schematic

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, 0, 0,
                                   0, 
                                   1 + self.numofshapes, # TODO recheck +1
                                   self.numofattributes,
                                   0, 0, 0,
                                   _schematic,
                                  )
            return _ret_val

    class Library:
        """ A struct that represents a library
        """
        constant = 0x15
        template = "=4B3I8s"

        max_embed_len = 8
        no_embed_str = b'\x7f'

        def __init__(self, name, numofdevsetblocks=0, devsets=None,
                     numofsymbolblocks=0, symbols=None,
                     numofpackageblocks=0, packages=None,):
            """ Just a constructor
            """
            self.name = name

            self.numofdevsetblocks = numofdevsetblocks
            if None == devsets:
                devsets = []
            self.devsets = devsets

            self.numofsymbolblocks = numofsymbolblocks
            if None == symbols:
                symbols = []
            self.symbols = symbols

            self.numofpackageblocks = numofpackageblocks
            if None == packages:
                packages = []
            self.packages = packages
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _name = self.no_embed_str + b'\0\0\0\x09'
            if self.max_embed_len > len(self.name):
                _name = self.name

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, 0, 0,
                                   self.numofdevsetblocks,
                                   self.numofsymbolblocks,
                                   self.numofpackageblocks,
                                   _name,
                                  )
            return _ret_val

    class DeviceSet(Web):
        """ Not a real "Web" but with a like structure
        """
        constant = 0x17
        template = "=4B3I8s"

        max_embed_len = 8
        no_embed_str = b'\x7f'

        def __init__(self, name, numofblocks=0, numofshapesets=0, 
                     shapesets=None):
            """ Just a constructor
            """
            super(Eagle.DeviceSet, self).__init__(name, numofblocks, 
                        numofshapesets, shapesets)
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _name = self.no_embed_str + b'\0\0\0\x09'
            if self.max_embed_len > len(self.name):
                _name = self.name

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, 0, 0,
                                   self.numofblocks,
                                   self.numofshapesets,
                                   0,
                                   _name,
                                  )
            return _ret_val

    class SymbolHeader(Web):
        """ A struct that represents a header of symbols
        """
        constant = 0x18
        template = "=4B3I8s"

        max_embed_len = 8
        no_embed_str = b'\x7f'

        def __init__(self, name, numofblocks=0, numofshapesets=0, 
                     shapesets=None):
            """ Just a constructor
            """
            super(Eagle.SymbolHeader, self).__init__(name, numofblocks, 
                        numofshapesets, shapesets)
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _name = self.no_embed_str + b'\0\0\0\x09'
            if self.max_embed_len > len(self.name):
                _name = self.name

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, 0, 0,
                                   self.numofblocks,
                                   self.numofshapesets,
                                   0,
                                   _name,
                                  )
            return _ret_val

    class PackageHeader(Web):
        """ A struct that represents a header of packages
        """
        constant = 0x19
        template = "=4B3I8s"

        max_embed_len = 8
        no_embed_str = b'\x7f'

        def __init__(self, name, numofblocks=0, numofshapesets=0, 
                     shapesets=None):
            """ Just a constructor
            """
            super(Eagle.PackageHeader, self).__init__(name, numofblocks, 
                        numofshapesets, shapesets)
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _name = self.no_embed_str + b'\0\0\0\x09'
            if self.max_embed_len > len(self.name):
                _name = self.name

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, 0, 0,
                                   self.numofblocks,
                                   self.numofshapesets,
                                   0,
                                   _name,
                                  )
            return _ret_val

    class Symbol(NamedShapeSet):
        """ A struct that represents a symbol
        """
        constant = 0x1d
        template = "=2BH3I8s"

        max_embed_len = 8
        no_embed_str = b'\x7f'

        def __init__(self, name, numofshapes=0, shapes=None):
            """ Just a constructor; shown for a sake of clarity
            """
            super(Eagle.Symbol, self).__init__(name, numofshapes, shapes)
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _name = self.no_embed_str + b'\0\0\0\x09'
            if self.max_embed_len > len(self.name):
                _name = self.name

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, 
                                   self.numofshapes,
                                   0, 0, 0,
                                   _name,
                                  )
            return _ret_val

    class Package(NamedShapeSet):
        """ A struct that represents a package
        """
        constant = 0x1e
        template = "=2BH2IB5s6s"

        max_embed_nlen = 5
        max_embed_dlen = 6
        no_embed_str = b'\x7f'

        def __init__(self, name, desc, numofshapes=0, shapes=None):
            """ Just a constructor
            """
            super(Eagle.Package, self).__init__(name, numofshapes, shapes)
            self.desc = desc
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _name = self.no_embed_str + b'\0\0\0\x09'
            if self.max_embed_nlen > len(self.name):
                _name = self.name
            _desc = self.no_embed_str + b'\0\0\0\x09'
            if self.max_embed_dlen > len(self.desc):
                _desc = self.desc

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, 
                                   self.numofshapes,
                                   0, 0, 0,
                                   _name,
                                   _desc
                                  )
            return _ret_val

    class Net(NamedShapeSet):
        """ A struct that represents a net
        """
        constant = 0x1f
        template = "=2BH3I8s"

        constantmid1 = 0x7fff7fff
        constantmid2 = 0x80008000

        max_embed_len = 8
        no_embed_str = b'\x7f'

        def __init__(self, name, nclass, numofshapes=0, shapes=None):
            """ Just a constructor
            """
            super(Eagle.Net, self).__init__(name, numofshapes, shapes)
            self.nclass = nclass
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _name = self.no_embed_str + b'\0\0\0\x09'
            if self.max_embed_len > len(self.name):
                _name = self.name

            _ret_val = struct.pack(self.template,
                                   self.constant, 0,
                                   self.numofshapes,
                                   self.constantmid1,
                                   self.constantmid2,
                                   self.nclass,
                                   _name,
                                  )
            return _ret_val

    class Bus(NamedShapeSet):
        """ A struct that represents a bus
        """
        constant = 0x3a
        template = "=2BH20s" 

        max_embed_len = 20
        no_embed_str = b'\x7f'

        def __init__(self, name, numofshapes=0, shapes=None):
            """ Just a constructor; shown for a sake of clarity
            """
            super(Eagle.Bus, self).__init__(name, numofshapes, shapes)
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _name = self.no_embed_str + b'\0\0\0\x09'
            if self.max_embed_len > len(self.name):
                _name = self.name

            _ret_val = struct.pack(self.template,
                                   self.constant, 0,
                                   self.numofshapes,
                                   _name,
                                  )
            return _ret_val

    class ShapeHeader(ShapeSet):
        """ A struct that represents a header of shapes
        """
        constant = 0x1a
        template = "=2BH5I"

        def __init__(self, numofshapes=0, shapes=None, 
                     numofpartblocks=0, parts=None,
                     numofbusblocks=0, buses=None,
                     numofnetblocks=0, nets=None,):
            """ Just a constructor
            """
            super(Eagle.ShapeHeader, self).__init__(numofshapes, shapes)

            self.numofpartblocks = numofpartblocks
            if None == parts:
                parts = []
            self.parts = parts

            self.numofbusblocks = numofbusblocks
            if None == buses:
                buses = []
            self.buses = buses

            self.numofnetblocks = numofnetblocks
            if None == nets:
                nets = []
            self.nets = nets
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, 
                                   self.numofshapes,
                                   0, 0, 
                                   self.numofpartblocks, 
                                   self.numofbusblocks, 
                                   self.numofnetblocks,
                                  )
            return _ret_val

    class Segment(ShapeSet):
        """ A struct that represents a segment
        """
        constant = 0x20
        template = "=2BHI4B3I"

        def __init__(self, numofshapes=0, shapes=None,
                     cumulativenumofshapes=0):
            """ Just a constructor
            """
            super(Eagle.Segment, self).__init__(numofshapes, shapes)
            self.cumulativenumofshapes = cumulativenumofshapes
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, 
                                   self.numofshapes,
                                   0,
                                   0, self.cumulativenumofshapes, 0, 0, # TODO recheck
                                   0, 0, 0
                                  )
            return _ret_val

    class Shape(object):
        """ A base struct for shapes, provides common codecs
             Although it provides two scaling methods, #2 has 
             to be used all the time
        """

        scale1a = 1000000.0
        scale1b = 2
        scale2 = 10000.0

        width_xscale = 2
        size_xscale = 2
        ratio_sscale = 2

        rotatemask = 0x0f
        rotates = {
                   0x00: None,
                   0x04: "R90",
                   0x08: "R180",
                   0x0c: "R270",
                  }

        fonts = {
                  0x00: "vector",
                  0x01: None, # "proportional",
                  0x02: "fixed",
                 }

        def __init__(self, layer):
            """ Just a constructor
            """
            self.layer = layer
            return 

        @staticmethod
        def encode_real(real, algo=2):
            """ Transforms given value to a binary representation
            """
            _ret_val = 0
            if 1 == algo:
                _ret_val = (int(real * Eagle.Shape.scale1a) >> 
                                                Eagle.Shape.scale1b)
            else:
                _ret_val = real * Eagle.Shape.scale2
                if 0 < _ret_val:
                    _ret_val += 0.01
                else:
                    _ret_val -= 0.01
            return int(_ret_val)

    class Circle(Shape):
        """ A struct that represents a circle
        """
        constant = 0x25
        template = "=4B4IH2B"

        def __init__(self, x, y, radius, width, layer): # pylint: disable=R0913
            """ Just a constructor
            """
            super(Eagle.Circle, self).__init__(layer)
            self.x = x
            self.y = y
            self.radius = radius
            self.width = width
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _ret_val = struct.pack(self.template,
                                   self.constant, 
                                   0, 0, self.layer,
                                   Eagle.Shape.encode_real(self.x),
                                   Eagle.Shape.encode_real(self.y),
                                   Eagle.Shape.encode_real(self.radius),
                                   Eagle.Shape.encode_real(self.radius),
                                   Eagle.Shape.encode_real(
                                       self.width / self.width_xscale),
                                   0, 0
                                  )
            return _ret_val

    class Rectangle(Shape):
        """ A struct that represents a rectangle
        """
        constant = 0x26
        template = "=4B4I4B"

        def __init__(self, x1, y1, x2, y2, layer, rotate): # pylint: disable=R0913
            """ Just a constructor
            """
            super(Eagle.Rectangle, self).__init__(layer)
            self.x1 = x1
            self.y1 = y1
            self.x2 = x2
            self.y2 = y2
            self.rotate = rotate
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _rotate = 0
            for _rr in Eagle.Rectangle.rotates:
                if Eagle.Rectangle.rotates[_rr] == self.rotate:
                    _rotate = _rr
                    break

            _ret_val = struct.pack(Eagle.Rectangle.template,
                                   Eagle.Rectangle.constant, 
                                   0, 0, self.layer,
                                   Eagle.Shape.encode_real(self.x1),
                                   Eagle.Shape.encode_real(self.y1),
                                   Eagle.Shape.encode_real(self.x2),
                                   Eagle.Shape.encode_real(self.y2),
                                   0, _rotate, 0, 0
                                  )
            return _ret_val

    class Wire(Shape):
        """ A struct that represents a wire
        """
        constant = 0x22
        template = "=4B4iH2B"

        arc_sign = 0x81

        def __init__(self, x1, y1, x2, y2, layer, width): # pylint: disable=R0913
            """ Just a constructor
            """
            super(Eagle.Wire, self).__init__(layer)
            self.x1 = x1
            self.y1 = y1
            self.x2 = x2
            self.y2 = y2
            self.width = width
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _ret_val = struct.pack(self.template,
                                   self.constant, 
                                   0, 0, self.layer,
                                   Eagle.Shape.encode_real(self.x1),
                                   Eagle.Shape.encode_real(self.y1),
                                   Eagle.Shape.encode_real(self.x2),
                                   Eagle.Shape.encode_real(self.y2),
                                   Eagle.Shape.encode_real(
                                       self.width / self.width_xscale),
                                   0, 0
                                  )
            return _ret_val

    class Junction(Shape):
        """ A struct that represents a junction
        """
        constant = 0x27
        template = "=4B5I"

        constantmid = 0x000013d8

        def __init__(self, x, y, layer):
            """ Just a constructor
            """
            super(Eagle.Junction, self).__init__(layer)
            self.x = x
            self.y = y
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, 0, self.layer,
                                   self.constantmid,
                                   Eagle.Shape.encode_real(self.x),
                                   Eagle.Shape.encode_real(self.y),
                                   0, 0
                                  )
            return _ret_val

    class Arc(Wire):
        """ A struct that represents an arc
        """
        capmask = 0x10
        caps = {
                0x00: None,
                0x10: "flat",
               }
        directionmask = 0x20
        directions = {
                      0x00: "clockwise",
                      0x20: "counterclockwise",
                     }

        def __init__(self, x1, y1, x2, y2, layer, width, curve, cap, direction): # pylint: disable=R0913
            """ Just a constructor
            """
            super(Eagle.Arc, self).__init__(x1, y1, x2, y2, layer, width)
            self.curve = curve
            self.cap = cap
            self.direction = direction
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _signs = 0
            for _dd in self.directions:
                if self.directions[_dd] == self.direction:
                    _signs += _dd
                    break
            for _cc in self.caps:
                if self.caps[_cc] == self.cap:
                    _signs += _cc
                    break

            _curve = self.encode_real(self.curve)

            _ret_val = struct.pack(self.template,
                                   self.constant, 
                                   0, 0, self.layer,
# TODO add curve...
                                   self.encode_real(self.x1),
                                   self.encode_real(self.y1),
                                   self.encode_real(self.x2),
                                   self.encode_real(self.y2),
                                   self.encode_real(
                                       self.width / self.width_xscale),
                                   _signs, 
                                   self.arc_sign
                                  )
            return _ret_val

    class Pad(Shape):
        """ A struct that represents a pad
            (no layer is available for pad ; base Shape class
            is used both for uniformity and convertors)
        """
        constant = 0x2a
        template = "=4B3I3B5s"

        max_embed_len = 5
        no_embed_str = b'\x7f'

        def __init__(self, name, x, y, drill):
            """ Just a constructor
            """
            super(Eagle.Pad, self).__init__(layer=-1)
            self.name = name
            self.x = x
            self.y = y
            self.drill = drill
# TODO shape (3:1==normal,3==long)
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _name = self.no_embed_str + b'\0\0\0\x09'
            if self.max_embed_len > len(self.name):
                _name = self.name

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, 0, 0,
                                   self.encode_real(self.x),
                                   self.encode_real(self.y),
                                   self.encode_real(self.drill),
                                   0, 0, 0,
                                   _name,
                                  )
            return _ret_val

    class Pin(Shape):
        """ A struct that represents a pin
            (no layer is available for pin ; base Shape class
            is used both for uniformity and convertors)
        """
        constant = 0x2c
        template = "=4B2I2B10s"

        max_embed_len = 10
        no_embed_str = b'\x7f'

        def __init__(self, name, x, y):
            """ Just a constructor
            """
            super(Eagle.Pin, self).__init__(layer=-1)
            self.name = name
            self.x = x
            self.y = y
# TODO visible len direction rotate(12:0xe0)
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _name = self.no_embed_str + b'\0\0\0\x09'
            if self.max_embed_len > len(self.name):
                _name = self.name

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, 0, 0,
                                   self.encode_real(self.x),
                                   self.encode_real(self.y),
                                   0, 0, 
                                   _name,
                                  )
            return _ret_val

    class Text(Shape):
        """ A struct that represents a text
        """
        constant = 0x31
        template = "=4B2IH4B6s"

        max_embed_len = 5
        delimeter = b'!'
        no_embed_str = b'\x7f'

        def __init__(self, value, x, y, size, layer, rotate, font, ratio): # pylint: disable=R0913
            """ Just a constructor
            """
            super(Eagle.Text, self).__init__(layer)
            self.value = value
            self.x = x
            self.y = y
            self.size = size
            self.rotate = rotate
            self.font = font
            self.ratio = ratio
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _font = 0
            for _ff in Eagle.Text.fonts:
                if Eagle.Text.fonts[_ff] == self.font:
                    _font = _ff
                    break
            _rotate = 0
            for _rr in Eagle.Text.rotates:
                if Eagle.Text.rotates[_rr] == self.rotate:
                    _rotate = _rr
                    break
            if self.max_embed_len >= len(self.value):
                _value = self.value
            else:
                _value = self.no_embed_str + b'\0\0\0\x09'
            _ret_val = struct.pack(self.template,
                                   self.constant, 0,
                                   _font, self.layer,
                                   self.encode_real(self.x),
                                   self.encode_real(self.y),
                                   self.encode_real(self.size /
                                       self.size_xscale),
                                   self.ratio << self.ratio_sscale,
                                   0, 0,
                                   _rotate,
                                   _value,
                                  )
            return _ret_val

        def construct2(self):
            """ Prepares a string block
                (Returns None if binary block is OK)
            """
            _ret_val = None

            if self.max_embed_len > len(self.value):
                pass # was embedded
            else:
                _ret_val = self.value + self.delimeter

            return _ret_val

    class Label(Shape):
        """ A struct that represents a label
        """
        constant = 0x33
        template = "=4B2I2H4BI"

        mirroredmask = 0x10
        onoffmask = 0x01

        def __init__(self, x, y, size, layer, rotate, ratio, font,  # pylint: disable=R0913
                     onoff, mirrored):
            """ Just a constructor
                Note: 6.0.0's xref is the same as onoff
            """
            super(Eagle.Label, self).__init__(layer)
            self.x = x
            self.y = y
            self.size = size
            self.xref = onoff
            self.rotate = rotate
            self.ratio = ratio
            self.font = font
            self.onoff = onoff
            self.mirrored = mirrored
            return #}}}

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _font = 0
            for _ff in Eagle.Text.fonts:
                if Eagle.Text.fonts[_ff] == self.font:
                    _font = _ff
                    break

            _ss = 0
            for _rr in Eagle.Label.rotates:
                if Eagle.Label.rotates[_rr] == self.rotate:
                    _ss += _rr
                    break
            if self.mirrored:
                _ss += self.mirroredmask

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, _font, self.layer,
                                   self.encode_real(self.x),
                                   self.encode_real(self.y),
                                   self.encode_real(self.size /
                                       self.size_xscale),
                                   self.ratio << Eagle.Text.ratio_sscale,
                                   0,
                                   _ss,
                                   self.onoffmask if self.onoff else 0,
                                   0, 0
                                  )
            return _ret_val

    class Attribute:
        """ A struct that represents an attribute
        """
        constant = 0x42
        template = "=3BI17s"

        max_embed_len = 17
        delimeter = b'!'
        no_embed_str = b'\x7f'

        def __init__(self, name, value):
            """ Just a constructor
            """
            self.name = name
            self.value = value
            return

        def _construct(self):
            """ Prepares a string
            """
            _ret_val = self.delimeter.join((self.name, str(self.value)))
            return _ret_val

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _str = self._construct()

            if self.max_embed_len > len(_str):
                _str2 = _str
            else:
                _str2 = self.no_embed_str + b'\0\0\0\x09'

            _ret_val = struct.pack(self.template,
                                   Eagle.Attribute.constant, 
                                   0, 0x2a, # <--- a kind of a marker?
                                   0,
                                   _str2
                                  )
            return _ret_val

        def construct2(self):
            """ Prepares a string block
                (Returns None if binary block is OK)
            """
            _ret_val = None

            _str = self._construct()
            if self.max_embed_len > len(_str):
                pass # was embedded
            else:
                _ret_val = _str

            return _ret_val

    class Schematic:
        """ A struct that represents "schematic"
        """
        defxreflabel = ":%F%N/%S.%C%R"
        defxrefpart = "/%S.%C%R"

        delimeter = b'\t'

        def __init__(self, xreflabel=None, xrefpart=None):
            """ Just a constructor
            """
            if None == xreflabel:
                xreflabel = Eagle.Schematic.defxreflabel
            if None == xrefpart:
                xrefpart = Eagle.Schematic.defxrefpart

            self.xreflabel = xreflabel
            self.xrefpart = xrefpart
            return

        def construct(self):
            """ Prepares a string block
            """
            _ret_val = None

            _ret_val = self.delimeter.join((self.xreflabel, 
                                            str(self.xrefpart)))
            return _ret_val

    class NetClass:
        """ A struct that represents a net class
        """
        template0 = "=3I" # header part read by _parse_file
        template1 = "=13I" # unpack the rest of chunk
        template2x = "=3I%ss13I" # pack the whole thing

        scale1 = 10000.0

        constant = 0x20000425
        constantmid = 0x87654321
        constantend = 0x89abcdef
        
        endmarker = 0x99999999

        def __init__(self, num, name='', width=0, drill=0, clearances=None, # pylint: disable=R0913
                     leadint=0):
            """ Just a constructor
            """ 
            self.num = num
            self.name = name
            self.width = width
            self.drill = drill
            if None == clearances:
                clearances = []
            self.clearances = clearances
            
            self.leadint = leadint # TODO decypher it..
            return

        @staticmethod
        def encode_real(real):
            """ Transforms given value to a binary representation
            """
            _ret_val = 0
            _ret_val = int(real * Eagle.NetClass.scale1)
            return _ret_val

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _ndx = 0
            _cls = []
            for _nn in range(8):
                _val = 0
                if (len(self.clearances) > _ndx and 
                            _nn == sorted(self.clearances)[_ndx]):
                    _val = Eagle.NetClass.encode_real(
                            sorted(self.clearances)[_ndx])
                    _ndx += 1
                _cls.append(_val)

            _name = self.name + b'\0'

            _ret_val = struct.pack(self.template2x % str(len(_name)),
                                   self.leadint, 
                                   self.constant,
                                   struct.calcsize(self.template1) + len(_name), 
                                   _name,
                                   self.num, 
                                   self.constantmid,
                                   self.encode_real(self.width), 
                                   self.encode_real(self.drill),
                                   _cls[0], _cls[1], _cls[2], _cls[3],
                                   _cls[4], _cls[5], _cls[6], _cls[7],
                                   self.constantend
                                  )
            return _ret_val

    blocksize = 24
    noregblockconst = b'\x13\x12\x99\x19'
    noregdelimeter = b'\0'

    def __init__(self):
        """ Construct a writer object and initialize it.
        """
        self.header = None
        self.layers = []
        self.settings = []
        self.grid = None
        self.attributeheader = None
        self.attributes = []
        self.libraries = []
        self.shapeheader = None
        self.shapes = []
        self.nets = []
        self.buses = []
        self.texts = []
        self.schematic = None
        self.netclasses = []
        return

    @staticmethod
    def _calculateweb(web):
        """ Calculates counters in web tree
        """
        _cumuno = 0
        for _nn in web:
            _cumuno += 1
            for _ss in _nn.segments:
                _ss.numofshapes = (len(_ss.wires) + 
                                   len(_ss.junctions) +
                                   len(_ss.labels))
                _cumuno += _ss.numofshapes
                _ss.cumulativenumofshapes = _cumuno
            _nn.numofblocks = (len(_nn.segments) + 
                        sum([_ss.numofshapes for _ss in _nn.segments]))
        return

    def _convert(self, design):
        """ Converts design into a set of Eagle objects
        """
        pass

    def _validate(self):
        """ Add extra structures required by an Eagle format and
            calculate section counters
        """

        if None == self.header:
            self.header = Eagle.Header()

        if None == self.settings:
            self.settings = []
        while 2 > len(self.settings):
            self.settings.append(Eagle.Settings())

        if None == self.grid:
            self.grid = Eagle.Grid()

        if None == self.attributeheader:
            self.attributeheader = Eagle.AttributeHeader()

        if None == self.shapeheader:
            self.shapeheader = Eagle.ShapeHeader()

        if None == self.schematic:
            self.schematic = Eagle.Schematic()

        if None == self.netclasses:
            self.netclasses = []
        if 0 == len(self.netclasses):
            self.netclasses.append(Eagle.NetClass(0, 'default'))
        while 8 > len(self.netclasses):
            self.netclasses.append(Eagle.NetClass(len(self.netclasses)))

# calculate num of blocks
        self._calculateweb(self.nets)
        self._calculateweb(self.buses)

        _numfromwebs = sum([_nn.getnumofblocks() for _nn in 
                            self.nets + self.buses])
        self.header.numofblocks = (1 + len(self.settings) +
                                   1 + len(self.layers) + 
                                   1 + len(self.attributes) + 
                                   1 + len(self.shapes) +
                                   _numfromwebs
                                  )
        self.attributeheader.numofshapes = len(self.shapes) + _numfromwebs
        self.attributeheader.numofattributes = len(self.attributes)
        self.shapeheader.numofshapes = len(self.shapes)

        return

    def write(self, design, filename):
        """ Save given design as an Eagle format file with a given name
        """

        self._convert(design)
        self._validate()

        with open(filename, 'wb') as _of:

            _of.write(self.header.construct())

            for _ss in self.settings:
                _of.write(_ss.construct())

            _of.write(self.grid.construct())

            for _ll in self.layers:
                _of.write(_ll.construct())

            _of.write(self.attributeheader.construct())

            for _aa in self.attributes:
                _of.write(_aa.construct())

            _of.write(self.shapeheader.construct())

            for _ss in self.shapes:
                _of.write(_ss.construct())

            for _nn in self.nets:
                _of.write(_nn.construct())

            _of.write(Eagle.noregblockconst)

            _xattr = []
            _xattr.append(self.schematic.construct())
            for _aa in self.attributes:
                _attr = _aa.construct2()
                if None != _attr: # None if it was embedded
                    _xattr.append(_attr)
            for _tt in self.texts:
                _textname = _tt.construct2()
                if None != _textname: # None if it was embedded
                    _xattr.append(_textname)
            _dta = self.noregdelimeter.join(_xattr+[self.noregdelimeter,])
            _of.write(struct.pack("I", len(_dta))) # length of noreg block
            _of.write(_dta) # noreg block itself

            for _cc in self.netclasses:
                _of.write(_cc.construct())

            _of.write(struct.pack(Eagle.NetClass.template0,
                                  0, Eagle.NetClass.constantend, 0
                                 ))
            return


