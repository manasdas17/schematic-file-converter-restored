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
import re
import math

from upconvert.core.shape import Line, Label, Rectangle, Arc, \
    BezierCurve, Circle, Polygon

#from upconvert.parser.eagle import EagleBinConsts


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
            if None == linkednumber:
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

            _name = self.no_embed_str + r'\0\0\0' + b'\x09'
            if None == self.name:
                _name = ''
            elif self.max_embed_len >= len(self.name):
                _name = self.name
            else:
                Eagle.attr_jar_append(self.name)

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

        defxreflabel = ":%F%N/%S.%C%R"
        defxrefpart = "/%S.%C%R"
        delimeter = b'\t'

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

            _schematic = self.no_embed_str + r'\0\0\0' + b'\x09'
            if None == self.schematic:
                _schematic = ''
            elif self.max_embed_len >= len(self.schematic):
                _schematic = self.schematic
            else:
                Eagle.attr_jar_append(self.schematic)

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

        def __init__(self, name, numofdevsetblocks=0, devsets=None, # pylint: disable=R0913
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

            _name = self.no_embed_str + r'\0\0\0' + b'\x09'
            if None == self.name:
                _name = ''
            elif self.max_embed_len >= len(self.name):
                _name = self.name
            else:
                Eagle.attr_jar_append(self.name)

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, 0, 0,
                                   self.numofdevsetblocks,
                                   self.numofsymbolblocks,
                                   self.numofpackageblocks,
                                   _name,
                                  )
            return _ret_val

    class DeviceSetHeader(Web):
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
            super(Eagle.DeviceSetHeader, self).__init__(name, numofblocks, 
                        numofshapesets, shapesets)
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _name = self.no_embed_str + r'\0\0\0' + b'\x09'
            if None == self.name:
                _name = ''
            elif self.max_embed_len >= len(self.name):
                _name = self.name
            else:
                Eagle.attr_jar_append(self.name)

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

            _name = self.no_embed_str + r'\0\0\0' + b'\x09'
            if None == self.name:
                _name = ''
            elif self.max_embed_len >= len(self.name):
                _name = self.name
            else:
                Eagle.attr_jar_append(self.name)

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

            _name = self.no_embed_str + r'\0\0\0' + b'\x09'
            if None == self.name:
                _name = ''
            elif self.max_embed_len >= len(self.name):
                _name = self.name
            else:
                Eagle.attr_jar_append(self.name)

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
        template = "=2BHI4BI8s"

        max_embed_len = 8
        no_embed_str = b'\x7f'

        def __init__(self, libid, name, numofshapes=0, shapes=None):
            """ Just a constructor; shown for a sake of clarity
            """
            super(Eagle.Symbol, self).__init__(name, numofshapes, shapes)
            self.libid = libid
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _name = self.no_embed_str + r'\0\0\0' + b'\x09'
            if None == self.name:
                _name = ''
            elif self.max_embed_len >= len(self.name):
                _name = self.name
            else:
                Eagle.attr_jar_append(self.name)

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, 
                                   self.numofshapes,
                                   0, 0, self.libid, 0, 0, 0,
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

            _name = self.no_embed_str + r'\0\0\0' + b'\x09'
            if None == self.name:
                _name = ''
            elif self.max_embed_nlen >= len(self.name):
                _name = self.name
            else:
                Eagle.attr_jar_append(self.name)

            _desc = self.no_embed_str + r'\0\0\0' + b'\x09'
            if None == self.desc:
                _desc = ''
            elif self.max_embed_dlen >= len(self.desc):
                _desc = self.desc
            else:
                Eagle.attr_jar_append(self.desc)

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
        template = "=2BH2I4B8s"

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

            _name = self.no_embed_str + r'\0\0\0' + b'\x09'
            if None == self.name:
                _name = ''
            elif self.max_embed_len >= len(self.name):
                _name = self.name
            else:
                Eagle.attr_jar_append(self.name)

            _ret_val = struct.pack(self.template,
                                   self.constant, 0,
                                   self.numofshapes,
                                   self.constantmid1,
                                   self.constantmid2,
                                   0, self.nclass, 0, 0,
                                   _name,
                                  )
            return _ret_val

    class Part(NamedShapeSet):
        """ A struct that represents a part
        """
        constant = 0x38
        template = "=2B3H3B5s8s" 

        max_embed_len1 = 5
        max_embed_len2 = 8
        no_embed_str = b'\x7f'

        val_sign_mask = 0x01

        def __init__(self, name, libid, devsetndx, symvar, techno, value='', # pylint: disable=R0913
                     numofshapes=0, shapes=None):
            """ Just a constructor
            """
            super(Eagle.Part, self).__init__(name, numofshapes, shapes)
            self.value = value
            self.libid = libid
            self.devsetndx = devsetndx
            self.symvar = symvar # within a devset!
            self.techno = techno
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _name = self.no_embed_str + r'\0\0\0' + b'\x09'
            if None == self.name:
                _name = ''
            elif self.max_embed_len1 >= len(self.name):
                _name = self.name
            else:
                Eagle.attr_jar_append(self.name)

            _value = self.no_embed_str + r'\0\0\0' + b'\x09'
            if None == self.value:
                _value = ''
            elif self.max_embed_len2 >= len(self.value):
                _value = self.value
            else:
                Eagle.attr_jar_append(self.value)

            _ret_val = struct.pack(self.template,
                                   self.constant, 0,
                                   self.numofshapes,
                                   self.libid, 
                                   self.devsetndx,
                                   self.symvar, 
                                   self.techno,
                                   self.val_sign_mask 
                                        if 'None' != self.value and
                                            0 != len(self.value) else 0,
                                   _name,
                                   _value,
                                  )
            return _ret_val

    class DeviceSet(NamedShapeSet):
        """ A struct that represents a deviceset
        """
        constant = 0x37
        template = "=2B2H2B5s5s6s" 

        max_embed_len1 = 5
        max_embed_len2 = 5
        max_embed_len3 = 6
        no_embed_str = b'\x7f'

        nopref_sign_mask = 0x02
        uservalue_sign_mask = 0x01

        def __init__(self, name, prefix, description, uservalue, # pylint: disable=R0913
                     numofshapes=0, shapes=None,
                     numofconnblocks=0, connblocks=None):
            """ Just a constructor
            """
            super(Eagle.DeviceSet, self).__init__(name, numofshapes, shapes)
            self.prefix = prefix
            self.description = description
            self.uservalue = uservalue

            self.numofconnblocks = numofconnblocks
            if None == connblocks:
                connblocks = []
            self.connblocks = connblocks
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _signs = 0
            if '' == self.prefix:
                _signs += self.nopref_sign_mask
            if self.uservalue:
                _signs += self.uservalue_sign_mask

            _prefix = self.no_embed_str + r'\0\0\0' + b'\x09'
            if None == self.prefix:
                _prefix = ''
            elif self.max_embed_len1 >= len(self.prefix):
                _prefix = self.prefix
            else:
                Eagle.attr_jar_append(self.prefix)

            _desc = self.no_embed_str + r'\0\0\0' + b'\x09'
            if None == self.description:
                _desc = ''
            elif self.max_embed_len2 >= len(self.description):
                _desc = self.description
            else:
                Eagle.attr_jar_append(self.description)

            _name = self.no_embed_str + r'\0\0\0' + b'\x09'
            if None == self.name:
                _name = ''
            elif self.max_embed_len3 >= len(self.name):
                _name = self.name
            else:
                Eagle.attr_jar_append(self.name)

            _ret_val = struct.pack(self.template,
                                   self.constant, 0,
                                   self.numofshapes,
                                   self.numofconnblocks,
                                   _signs, 0,
                                   _prefix,
                                   _desc,
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

            _name = self.no_embed_str + r'\0\0\0' + b'\x09'
            if None == self.name:
                _name = ''
            elif self.max_embed_len >= len(self.name):
                _name = self.name
            else:
                Eagle.attr_jar_append(self.name)

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

        def __init__(self, numofshapes=0, shapes=None, # pylint: disable=R0913
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

    class ConnectionHeader(ShapeSet):
        """ A struct that represents a header for 'connections' blocks
        """
        constant = 0x36
        template = "=2B2H13s5s"

        constantmid_def = "''"

        no_embed_str = b'\x7f'
        max_embed_len = 13

        delim_techs = b'\x04'
        delim_namesvals = b'\x04'
        delim_names = b'\x01'
        delim_vals = b'\x02'

        def __init__(self, sindex, attributes, technologies, name, # pylint: disable=R0913
                     numofshapes=0, shapes=None):
            """ Just a constructor
            """
            super(Eagle.ConnectionHeader, self).__init__(numofshapes, shapes)
            self.sindex = sindex
            
            if None == technologies:
                technologies = []
            self.technologies = technologies

            if None == attributes:
                attributes = []
            self.attributes = attributes
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _attrstechs = self.no_embed_str + r'\0\0\0' + b'\x09'
            if 0 < len(self.technologies):
                _at2 = self.delim_techs + self.delim_techs.join(self.technologies)
                if self.max_embed_len >= len(_at2):
                    _attrstechs = _at2
                else:
                    Eagle.attr_jar_append(_at2)
            elif 0 < len(self.attributes):
                _at2 = self.delim_namesvals.join((
                        self.delim_names + self.delim_names.join(
                                        [x for x, y in self.attributes]),
                        self.delim_names + self.delim_names.join(
                                        [y for x, y in self.attributes]),
                        ))
                if self.max_embed_len >= len(_at2):
                    _attrstechs = str(_at2)
                else:
                    Eagle.attr_jar_append(_at2)
            else:
                _attrstechs = ''

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, 
                                   self.numofshapes,
                                   self.sindex,
                                   _attrstechs,
                                   self.constantmid_def,
                                  )
            return _ret_val

    class Connections:
        """ A struct that represents a set of connection indexes
        """
        constant = 0x3c
        template = "=2B22B"

        connset_len = 22

        def __init__(self, connections=None):
            """ Just a constructor
            """
            if None == connections:
                connections = []
            self.connections = connections
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _indexes = self.connections + [0,] * (self.connset_len - 
                                            len(self.connections))

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, 
                                   *_indexes
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

        rotatemask = 0x0c # in some cases 0x0f works as well
        rotates = {
                   0x00: None,
                   0x01: "R40",
                   0x02: "R45",
                   0x04: "R90",
                   0x06: "R135",
                   0x08: "R180",
                   0x0a: "R225",
                   0x0c: "R270",
                   0x0e: "R315",
# ones below are possible for text & frame -- don't apply the mask there
                   0x10: "MR0",
                   0x12: "MR45",
                   0x14: "MR90",
                   0x16: "MR135",
                   0x18: "MR180",
                   0x1a: "MR225",
                   0x1c: "MR270",
                   0x1e: "MR315",

                   0x40: "SR0", #...
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

        @staticmethod
        def rotate2strings(rotate):
            """ Converts pi-radian number into 'rotates' string
                It could be implemented as a map, but a special handling for 
                 None as 0. would be needed..
            """
            _ret_val = None

            if 0.5 == rotate:
                _ret_val = 'R90'
            elif 1.0 == rotate:
                _ret_val = 'R180'
            elif 1.5 == rotate:
                _ret_val = 'R270'
            return _ret_val 

    class Polygon(ShapeSet, Shape):
        """ A struct that represents a polygon
        """
        constant = 0x21
        template = "=2BH2I2H4BI"

        def __init__(self, width, layer, numofshapes=0, shapes=None):
            """ Just a constructor
            """
            super(Eagle.Polygon, self).__init__(numofshapes, shapes)
            self.layer = layer # no Shape constructor will be called
            self.width = width
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _ret_val = struct.pack(self.template,
                                   self.constant, 0,
                                   self.numofshapes,
                                   0, # maybe a constant 0xfffeff05
                                   0,
                                   Eagle.Shape.encode_real(
                                       self.width / self.width_xscale),
                                   0,
                                   0, 0, self.layer, 0,
                                   0,
                                  )
            return _ret_val

    class Instance(ShapeSet, Shape):
        """ A struct that represents an instance
        """
        constant = 0x30
        template = "=2BH2iH6BI"

        smashed_mask = 0x01
        smashed2_mask = 0x02

        constantmid = 0xffff

        def __init__(self, x, y, smashed, rotate, numofshapes=0, # pylint: disable=R0913
                     shapes=None):
            """ Just a constructor
            """
            super(Eagle.Instance, self).__init__(numofshapes, shapes)
#            super(Eagle.Shape, self).__init__(-1)
            self.x = x
            self.y = y
            self.smashed = smashed
            self.rotate = rotate
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _rotate = 0
            for _rr in self.rotates:
                if self.rotates[_rr] == self.rotate:
                    _rotate = _rr
                    break

            _ret_val = struct.pack(self.template,
                                   self.constant, 0,
                                   self.numofshapes,
                                   self.encode_real(self.x),
                                   self.encode_real(self.y),
                                   self.constantmid,
                                   0, 0, 0,
                                   _rotate,
                                   self.smashed_mask if self.smashed
                                        else 0,
                                   0, 0
                                  )
            return _ret_val

    class Circle(Shape):
        """ A struct that represents a circle
        """
        constant = 0x25
        template = "=4B2i2IH2B"

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
        template = "=4B4i4B"

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

        stylemask = 0x0f
        styles = {
                  0x00: "Continuous",
                  0x01: "LongDash",
                  0x02: "ShortDash",
                  0x03: "DashDot",
                 }

        arc_sign = 0x81

        def __init__(self, x1, y1, x2, y2, style, layer, width): # pylint: disable=R0913
            """ Just a constructor
            """
            super(Eagle.Wire, self).__init__(layer)
            self.x1 = x1
            self.y1 = y1
            self.x2 = x2
            self.y2 = y2
            self.width = width
            self.style = style
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _signs = 0
            for _ss in self.styles:
                if self.styles[_ss] == self.style:
                    _signs += _ss
                    break

            _ret_val = struct.pack(self.template,
                                   self.constant, 
                                   0, 0, self.layer,
                                   Eagle.Shape.encode_real(self.x1),
                                   Eagle.Shape.encode_real(self.y1),
                                   Eagle.Shape.encode_real(self.x2),
                                   Eagle.Shape.encode_real(self.y2),
                                   Eagle.Shape.encode_real(
                                       self.width / self.width_xscale),
                                   _signs, 0
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

    class Hole(Shape):
        """ A struct that represents a hole
            (no layer is available for hole ; base Shape class
            is used both for uniformity and convertors)
        """
        constant = 0x28
        template = "=4B5I"

        def __init__(self, x, y, drill):
            """ Just a constructor
            """
            super(Eagle.Hole, self).__init__(-1)
            self.x = x
            self.y = y
            self.drill = drill
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, 0, 0,
                                   Eagle.Shape.encode_real(self.x),
                                   Eagle.Shape.encode_real(self.y),
                                   Eagle.Shape.encode_real(
                                       self.drill / self.width_xscale),
                                   0, 0
                                  )
            return _ret_val

    class SMD(Shape):
        """ A struct that represents an SMD (Surface Mount Device)
        """
        constant = 0x2b
        template = "=4B2i2H3B5s"

        max_embed_len = 5
        no_embed_str = b'\x7f'

        def __init__(self, name, x, y, dx, dy, layer): # pylint: disable=R0913
            """ Just a constructor
            """
            super(Eagle.SMD, self).__init__(layer)
            self.name = name
            self.x = x
            self.y = y
            self.dx = dx
            self.dy = dy
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _name = self.no_embed_str + r'\0\0\0' + b'\x09'
            if None == self.name:
                _name = ''
            elif self.max_embed_len >= len(self.name):
                _name = self.name
            else:
                Eagle.attr_jar_append(self.name)

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, 0, self.layer,
                                   Eagle.Shape.encode_real(self.x),
                                   Eagle.Shape.encode_real(self.y),
                                   Eagle.Shape.encode_real(
                                       self.dx / self.width_xscale),
                                   Eagle.Shape.encode_real(
                                       self.dy / self.width_xscale),
                                   0, 0, 0,
                                   _name,
                                  )
            return _ret_val

    class Arc(Wire):
        """ A struct that represents an arc
        """
        template = "=4B4IH2B" # 3-bytes long coords here..

        capmask = 0x10
        caps = {
                0x00: None,
                0x10: "flat",
               }
        directionmask = 0x20
        directions = {
                      0x00: "clockwise",        # == negative curve (angle)
                      0x20: "counterclockwise", # == positive curve (angle)
                     }

        def __init__(self, x1, y1, x2, y2, style, layer, width, # pylint: disable=R0913
                        curve, cap, direction):
            """ Just a constructor
            """
            super(Eagle.Arc, self).__init__(x1, y1, x2, y2, style, layer, width)
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
            for _ss in self.styles:
                if self.styles[_ss] == self.style:
                    _signs += _ss
                    break

# calculating circle's center coords
            _dp = math.sqrt(math.pow(self.x2 - self.x1, 2) + math.pow(self.y2 - self.y1, 2)) 
            _r = _dp / (2 * math.cos(math.radians((180 - self.curve) / 2)))

            _h = math.sqrt(_r * _r - math.pow(_dp / 2, 2))

            if 'counterclockwise' == self.direction:
                _x3 = self.x1 + abs(self.x2 - self.x1) / 2 + _h * abs(self.y2 - self.y1) / _dp
                _y3 = self.y1 + abs(self.y2 - self.y1) / 2 - _h * abs(self.x2 - self.x1) / _dp
            else:
                _x3 = self.x1 + abs(self.x2 - self.x1) / 2 - _h * abs(self.y2 - self.y1) / _dp
                _y3 = self.y1 + abs(self.y2 - self.y1) / 2 + _h * abs(self.x2 - self.x1) / _dp

            if abs(self.x1 - self.x2) < abs(self.y1 - self.y2):
                _curve = _x3
            else:
                _curve = _y3

            _curve = self.encode_real(int((_curve + 0.005) * 100) / 100.) # rounding..

            _ret_val = struct.pack(self.template,
                                   self.constant, 
                                   0, 0, self.layer,
                                   ((self.encode_real(self.x1) & 0xffffff) +
                                       ((_curve & 0xff) << 24)),
                                   ((self.encode_real(self.y1) & 0xffffff) +
                                       ((_curve & 0xff00) << 16)),
                                   ((self.encode_real(self.x2) & 0xffffff) +
                                       ((_curve & 0xff0000) << 8)),
                                   self.encode_real(self.y2) & 0xffffff,
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

            _name = self.no_embed_str + r'\0\0\0' + b'\x09'
            if None == self.name:
                _name = ''
            elif self.max_embed_len >= len(self.name):
                _name = self.name
            else:
                Eagle.attr_jar_append(self.name)

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
        template = "=4B2i2B10s"

        max_embed_len = 10
        no_embed_str = b'\x7f'

        visiblemask = 0xf0
        visibles = {
                    0x00: "off",
                    0x40: "pad",
                    0x80: "pin",
                    0xc0: None, # default
                   }
        dirmask = 0x0f
        directions = {
                      0x00: "nc",
                      0x01: "in",
                      0x02: "out",
                      0x03: None, # default
                      0x04: "oc",
                      0x05: "pwr",
                      0x06: "pas",
                      0x07: "hiz",
                      0x08: "sup",
                     }
        lengthmask = 0x30
        lengths = {
                   0x00: "point",
                   0x10: "short",
                   0x20: "middle",
                  }
        funcmask = 0x0f
        functions = {
                     0x00: None, # default
                     0x01: "dot",
                     0x02: "clk",
                     0x03: "dotclk",
                    }
 
        def __init__(self, name, x, y, visible, direction, rotate, length, # pylint: disable=R0913
                     function=None, swaplevel=0): 
            """ Just a constructor
            """
            super(Eagle.Pin, self).__init__(layer=-1)
            self.name = name.encode('ascii', 'replace') if None != name else ''
            self.x = x
            self.y = y
            self.visible = visible
            self.direction = direction
# rotation codes direction: R0 means left, R90 - down, R180 - right, R270 - up
            self.rotate = rotate
            self.length = length
            self.function = function
            self.swaplevel = swaplevel
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _name = self.no_embed_str + r'\0\0\0' + b'\x09'
            if None == self.name:
                _name = ''
            elif self.max_embed_len >= len(self.name):
                _name = self.name
            else:
                Eagle.attr_jar_append(self.name)

            _viz = 0
            for _vv in self.visibles:
                if self.visibles[_vv] == self.visible:
                    _viz += _vv
                    break
            for _ff in self.functions:
                if self.functions[_ff] == self.function:
                    _viz += _ff
                    break
            _rotdir = 0
            for _rr in self.rotates:
                if self.rotates[_rr] == self.rotate:
                    _rotdir += _rr << 4
                    break
            for _ll in self.lengths:
                if self.lengths[_ll] == self.length:
                    _rotdir += _ll
                    break
            for _dd in self.directions:
                if self.directions[_dd] == self.direction:
                    _rotdir += _dd
                    break

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, _viz, 0,
                                   self.encode_real(self.x),
                                   self.encode_real(self.y),
                                   _rotdir, self.swaplevel, 
                                   _name,
                                  )
            return _ret_val

    class Gate(Shape):
        """ A struct that represents a gate
            (no layer is available for gate ; base Shape class
            is used both for uniformity and convertors)
        """
        constant = 0x2d
        template = "=4B2i2BH8s"

        addlevels = {
                     0x00: "must",
                     0x02: None,
                     0x03: "request",
                     0x04: "always",
                    }

        max_embed_len = 8
        no_embed_str = b'\x7f'

        def __init__(self, x, y, name, sindex, addlevel): # pylint: disable=R0913
            """ Just a constructor
            """
            super(Eagle.Gate, self).__init__(-1)
            self.x = x
            self.y = y
            self.name = name
            self.sindex = sindex
            self.addlevel = addlevel
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _addlevel = 0
            for _ll in self.addlevels:
                if self.addlevels[_ll] == self.addlevel:
                    _addlevel = _ll
                    break

            _name = self.no_embed_str + r'\0\0\0' + b'\x09'
            if None == self.name:
                _name = ''
            elif self.max_embed_len >= len(self.name):
                _name = self.name
            else:
                Eagle.attr_jar_append(self.name)

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, 0, 0,
                                   self.encode_real(self.x),
                                   self.encode_real(self.y),
                                   _addlevel, 0, 
                                   self.sindex,
                                   _name,
                                  )
            return _ret_val

    class Text(Shape):
        """ A struct that represents a text
        """
        constant = 0x31
        template = "=4B2iH4B6s"

        max_embed_len = 6
        delimeter = b'!'
        no_embed_str = b'\x7f'

        def __init__(self, value, x, y, size, layer, rotate, font, ratio): # pylint: disable=R0913
            """ Just a constructor
            """
            super(Eagle.Text, self).__init__(layer)
            self.value = str(value)
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

            if None == self.value:
                _value = ''
            elif self.max_embed_len >= len(self.value):
                _value = self.value
            else:
                _value = self.no_embed_str + r'\0\0\0' + b'\x09'
                Eagle.attr_jar_append(self.value)

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

            if None == self.value or self.max_embed_len >= len(self.value):
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

    class Frame(Shape):
        """ A struct that represents a frame
        """
        constant = 0x43
        template = "=4B4i4B"

        bleftmask = 0x08
        btopmask = 0x04
        brightmask = 0x02
        bbottommask = 0x01

        def __init__(self, x1, y1, x2, y2, columns, rows, # pylint: disable=R0913
                    layer, bleft=True, btop=True, bright=True, bbottom=True): 
            """ Just a constructor
            """
            super(Eagle.Frame, self).__init__(layer)
            self.x1 = x1
            self.y1 = y1
            self.x2 = x2
            self.y2 = y2

            self.columns = columns
            self.rows = rows

            self.bleft = bleft
            self.btop = btop
            self.bright = bright
            self.bbottom = bbottom
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _borbot = ( (self.bleftmask if self.bleft else 0) +
                        (self.btopmask if self.btop else 0) +
                        (self.brightmask if self.bright else 0) +
                        (self.bbottommask if self.bbottom else 0) )

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, 0, self.layer,
                                   self.encode_real(self.x1),
                                   self.encode_real(self.y1),
                                   self.encode_real(self.x2),
                                   self.encode_real(self.y2),
                                   self.columns,
                                   self.rows,
                                   _borbot,
                                   0,
                                  )
            return _ret_val

    class AttributeNam(Shape):
        """ A struct that represents a part's NAME attribute
        """
        constant = 0x34
        template = "=4B2i2H4B4s"

        def __init__(self, x, y, size, layer, rotate, font, name="NAME"): # pylint: disable=R0913
            """ Just a constructor
            """
            super(Eagle.AttributeNam, self).__init__(layer)
            self.name = name
            self.x = x
            self.y = y
            self.size = size
            self.font = font
            self.rotate = rotate
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _font = 0
            for _ff in Eagle.AttributeNam.fonts:
                if Eagle.AttributeNam.fonts[_ff] == self.font:
                    _font = _ff
                    break

            _rot = 0
            for _rr in Eagle.AttributeNam.rotates:
                if Eagle.AttributeNam.rotates[_rr] == self.rotate:
                    _rot += _rr
                    break

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, _font, self.layer,
                                   self.encode_real(self.x),
                                   self.encode_real(self.y),
                                   self.encode_real(self.size /
                                       self.size_xscale),
                                   0, 
                                   0, _rot, 0, 0,
                                   ''
                                  )
            return _ret_val

    class AttributeVal(AttributeNam):
        """ A struct that represents a part's VALUE attribute
        """
        constant = 0x35

        def __init__(self, x, y, size, layer, rotate, font, name="VALUE"): # pylint: disable=R0913
            """ Just a constructor
            """
            super(Eagle.AttributeVal, self).__init__(x, y, 
                                        size, layer, rotate, font, name)
            return

    class AttributePrt(AttributeNam):
        """ A struct that represents a part's PART attribute
        """
        constant = 0x3f

        def __init__(self, x, y, size, layer, rotate, font, name="VALUE"): # pylint: disable=R0913
            """ Just a constructor
            """
            super(Eagle.AttributePrt, self).__init__(x, y, 
                                        size, layer, rotate, font, name)
            return

    class PinRef(Shape):
        """ A struct that represents a pinref
            (no layer is available for pinref ; base Shape class
            is used both for uniformity and convertors)
        """
        constant = 0x3d
        template = "=4B3H14s"

        def __init__(self, partno, gateno, pinno):
            """ Just a constructor
            """
            super(Eagle.PinRef, self).__init__(-1)
            self.partno = partno
            self.gateno = gateno
            self.pinno = pinno
            return

        def construct(self):
            """ Prepares a binary block
            """
            _ret_val = None

            _ret_val = struct.pack(self.template,
                                   self.constant, 0, 0, 0,
                                   self.partno,
                                   self.gateno,
                                   self.pinno,
                                   '',
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

            if self.max_embed_len >= len(_str):
                _str2 = _str
            else:
                _str2 = self.no_embed_str + r'\0\0\0' + b'\x09'
                Eagle.attr_jar_append(_str)

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

            _name = self.name + r'\0'

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
    noregdelimeter = r'\0'

    def __init__(self):
        """ Construct a writer object and initialize it.
        """
#        self.shapes = []
#        self.nets = []
#        self.buses = []
        self.header = None
        self.layers = []
        self.settings = []
        self.grid = None
        self.attributeheader = None
        self.attributes = []
        self.libraries = []
        self.shapeheader = None
        self.parts = []
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

    attr_jar = [] # attribute list

    @classmethod
    def attr_jar_append(cls, value):
        """ Puts one more string into the jar
        """
        cls.attr_jar.append(value.encode('ascii', 'replace'))

    def _convert_library(self, design):
        """ Converts library part into a set of Eagle objects
        """

        for _cc in design.components.components:
            _libid = 'default'
            _compname = _cc
            _tech = []
            _attrs = []
            if -1 != _cc.find(':'):
                _libid, _compname = _cc.split(':')

            _lib = None
            _libnid = -1
            for _li, _ll in enumerate(self.libraries):
                if _libid == _ll.name:
                    _lib = _ll
                    _libnid = 1 + _li # numbered from 1
                    break
            else:
                _lib = Eagle.Library(name=_libid)
                _libnid = len(self.libraries) # numbered from 1
                self.libraries.append(_lib)

# checking if symbols / devsets / packages are in the library already
#  (adding them if not)
            _co = design.components.components[_cc]

            if 0 == len(_lib.devsets):
                _lib.devsets.append(Eagle.DeviceSetHeader(name='default'))

            for _di, _dd in enumerate(_lib.devsets[0].shapesets):
                if _compname == _dd.name:
                    _dset = _dd
                    break
            else:
                _prefix = 'xC'
                _desc = 'n/a'
                if 'prefix' in _co.attributes:
                    _prefix = _co.attributes['prefix']
                if 'description' in _co.attributes:
                    _desc = _co.attributes['description']
                _dset = Eagle.DeviceSet(name=_compname, prefix=_prefix, 
                            description=_desc, uservalue=False)

                _lib.devsets[0].shapesets.append(_dset)

            if 0 == len(_lib.symbols):
                _lib.symbols.append(Eagle.SymbolHeader(name='default'))

            for _si, _ss in enumerate(_lib.symbols[0].shapesets):
                if _compname == _ss.name:
                    _symbol = _ss
                    _symnid = 1 + _si # numbered from 1
                    break
            else: # no such symbol yet
                _symbol = Eagle.Symbol(libid=_libnid, name=_compname)
                _symnid = len(_lib.symbols[0].shapesets) # numbered from 1

                for _css in _co.symbols:
                    for _cbb in _css.bodies:

                        for _ci in design.component_instances:
                            if _cc != _ci.library_id:
                                continue
                            for _xaa in _ci.attributes:
                                if 'technology' == _xaa:
                                    _tech.append(_ci.attributes[_xaa])
                                elif _xaa in ('prefix', 'description'):
                                    pass
                                else:
                                    _attrs.append((_xaa, _ci.attributes[_xaa]))
                            for _sa in _ci.symbol_attributes:
                                for _an, _aa in enumerate(_sa.annotations):
                                    _val = 'n/a'
                                    if 0 == _an:
                                        _val = '>NAME'
                                    elif 1 == _an:
                                        _val = '>VALUE'

                                    _rot = self.Shape.rotate2strings(_aa.rotation)

                                    _symbol.shapes.append(Eagle.Text(
                                                value=_val,
                                                x=_aa.x - _sa.x,
                                                y=_aa.y - _sa.y,
                                                size=1.778, layer=95, 
                                                rotate=_rot, font=None,
                                                ratio=10))

                        for _cpp in _cbb.pins:

                            _name = None
                            if None != _cpp.label:
                                _name = _cpp.label.text

                            _visible = None
                            if 'visible' in _cpp.attributes:
                                _visible = _cpp.attributes['visible']

                            _dir = None
                            if 'direction' in _cpp.attributes:
                                _dir = _cpp.attributes['direction']

                            _rot = None

                            _len = 'short'
                            if 'length' in _cpp.attributes:
                                _len = _cpp.attributes['length']
                            
                            _func = None
                            if 'function' in _cpp.attributes:
                                _func = _cpp.attributes['function']
                            
                            _swap = 0
                            if 'swaplevel' in _cpp.attributes:
                                _swap = _cpp.attributes['swaplevel']
                            
                            _symbol.shapes.append(Eagle.Pin(name=_name,
                                    x=_cpp.p2.x, y=_cpp.p2.y, visible=_visible,
                                    direction=_dir, rotate=_rot, length=_len,
                                    function=_func, swaplevel=_swap))
                        for _cff in _cbb.shapes:

                            _layer = 94
                            if 'label' in _cff.attributes:
                                _layer = _cff.attributes['layer']

                            if isinstance(_cff, Line):
                                _style = 'Continuous'
                                if 'style' in _cff.attributes:
                                    _style = _cff.attributes['style']

                                _width = 0.254
                                if 'width' in _cff.attributes:
                                    _width = _cff.attributes['width']

                                _symbol.shapes.append(Eagle.Wire(
                                        x1=_cff.p1.x, y1=_cff.p1.y,
                                        x2=_cff.p2.x, y2=_cff.p2.y,
                                        style=_style, layer=_layer, width=_width))
                            elif isinstance(_cff, Rectangle):
                                _symbol.shapes.append(Eagle.Rectangle(
                                        x1=_cff.x, y1=_cff.y,
                                        x2=(_cff.x + _cff.width), 
                                        y2=(_cff.y - _cff.height),
                                        rotate=None, layer=_layer))
                            elif isinstance(_cff, Arc):
                                _style = 'Continuous'
                                if 'style' in _cff.attributes:
                                    _style = _cff.attributes['style']

                                _width = 0.254
                                if 'width' in _cff.attributes:
                                    _width = _cff.attributes['width']

                                _layer = 91 # usually Nets

                                _dir = ('counterclockwise' 
                                            if _cff.start_angle < _cff.end_angle
                                            else 'clockwise')
                                _symbol.shapes.append(Eagle.Arc( # _cff's angles're in radians
                                        x1=_cff.x + _cff.radius * math.cos(_cff.start_angle), # sign is ok
                                        y1=_cff.y + _cff.radius * math.sin(_cff.start_angle),
                                        x2=_cff.x + _cff.radius * math.cos(_cff.end_angle),
                                        y2=_cff.y + _cff.radius * math.sin(_cff.end_angle),
                                        style=_style, 
                                        layer=_layer, width=_width,
                                        curve=math.degrees(abs(_cff.start_angle - _cff.end_angle)),
                                        cap=None, 
                                        direction=_dir))
                            elif isinstance(_cff, BezierCurve):
#                                raise NotImplementedError("BezierCurve isn't implemented for Eagle yet")
# TODO curve approximation with arcs
                                _style = 'Continuous'
                                if 'style' in _cff.attributes:
                                    _style = _cff.attributes['style']

                                _width = 0.254
                                if 'width' in _cff.attributes:
                                    _width = _cff.attributes['width']

                                _symbol.shapes.append(Eagle.Wire(
                                        x1=_cff.p1.x, y1=_cff.p1.y,
                                        x2=_cff.p2.x, y2=_cff.p2.y,
                                        style=_style, layer=_layer, width=_width))
                            elif isinstance(_cff, Circle):
                                _width = 0.254
                                if 'width' in _cff.attributes:
                                    _width = _cff.attributes['width']

                                _symbol.shapes.append(Eagle.Circle(
                                        x=_cff.x, y=_cff.y,
                                        radius=_cff.radius, 
                                        width=_width, layer=_layer))
                            elif isinstance(_cff, Polygon):
                                _width = 0.254
                                if 'width' in _cff.attributes:
                                    _width = _cff.attributes['width']

                                _style = 'Continuous'
                                if 'style' in _cff.attributes:
                                    _style = _cff.attributes['style']

                                _symbol.shapes.append(Eagle.Polygon(
                                    width=_width, layer=_layer,
                                    numofshapes=len(_cff.points),
                                    shapes=[ # lines from points
                                        Eagle.Wire(
                                            x1=p1.x, y1=p1.y,
                                            x2=p2.x, y2=p2.y,
                                            style=_style, layer=_layer, 
                                            width=_width)
                                        for p1, p2 in zip(_cff.points, 
                                            _cff.points[1:]+[_cff.points[0],])
                                        ]))
                            elif isinstance(_cff, Label):
                                _layer = 95 # usually Names
                                if 'label' in _cff.attributes:
                                    _layer = _cff.attributes['layer']

                                _rot = self.Shape.rotate2strings(_cff.rotation)

                                _symbol.shapes.append(Eagle.Text(
                                        value=_cff.text,
                                        x=_cff.x, y=_cff.y,
                                        size=1.778, font=None, ratio=10,
                                        rotate=_rot, layer=_layer))
                            else:
                                raise ValueError("cannot process " + _cff.__class__.__name__)

                _lib.symbols[0].shapesets.append(_symbol)

                _dset.shapes.append(Eagle.Gate(name='G$1', x=0., y=0., 
                            sindex=_symnid, addlevel=False))
                _dset.connblocks.append(Eagle.ConnectionHeader(name='default', 
                            attributes=_attrs, technologies=_tech,
                            sindex=_symnid))
                
            if 0 == len(_lib.packages):
                _lib.packages.append(Eagle.PackageHeader(name='default'))
            # TODO to load from a library file
        return

    def _convert_shapes1(self, design):
        """ Converts shapes (parts) into a set of Eagle objects
        """
        for _pp in design.component_instances:
            _libid = -1
            _devn = -1
            _libname = 'default'
            _pname = _pp.library_id
            if -1 != _pp.library_id.find(':'):
                _libname, _pname = _pp.library_id.split(':')
                
            for _li, _ll in enumerate(self.libraries):
                if _libname == _ll.name:
                    _libid = _li
                    for _di, _dd in enumerate(_ll.devsets[0].shapesets):
                        if _pname == _dd.name:
                            _devn = _di
                            break
                    break

            self.shapeheader.parts.append(Eagle.Part(
                    name=_pp.instance_id, libid=_libid, devsetndx=_devn,
                    symvar=1, techno=1)) # after OpenJSON all parts are split
        return

    def _convert_shapes2(self, design):
        """ Converts shapes (buses/nets) into a set of Eagle objects
        """
        for _nn in design.nets:
            _web = None
            if 'type' in _nn.attributes:
                if 'bus' == _nn.attributes['type']:
                    _width = 0.762
                    _web = Eagle.Bus(name=_nn.net_id)
                    self.shapeheader.buses.append(_web)
                else:
                    _clrs = []
                    _attrre = re.compile(r'^netclearance(\d+)$')
                    for _aa in _nn.attributes:
                        _attr = _attrre.match(_aa)
                        if None != _attr:
                            _clrs.append((_attr.group(1), _nn.attributes[_aa]))

                    self.netclasses.append(Eagle.NetClass( # duplicates are cleared below
                            num=_nn.attributes['netclass'], 
                            name=_nn.attributes['netname'], 
                            width=_nn.attributes['netwidth'],
                            drill=_nn.attributes['netdrill'],
                            clearances=_clrs,
                        ))
                    _width = 0.1524 # _nn.attributes['netwidth']
                    _web = Eagle.Net(name=_nn.net_id, 
                                nclass=_nn.attributes['netclass'])
                    self.shapeheader.nets.append(_web)
            else:
                _width = 0.1524
                _web = Eagle.Net(name=_nn.net_id, nclass=0)
                self.shapeheader.nets.append(_web)

            _prpts = set() # processed points
            for _pp in _nn.points:
                _pt = _nn.points[_pp]
                for _opp in _pt.connected_points:
                    if not _opp in _prpts: # not yet processed
                        _opt = None
                        try:
                            _opt = _nn.points[_opp]
                        except KeyError: # not from current net
                            for _xxn in design.nets:
                                if _opp in _xxn.points:
                                    _opt = _xxn.points[_opp]
                                    break
                            else:
                                raise ValueError("undefined point ID: %s" % str(_opp))

                        _web.shapes.append(Eagle.Wire(
                                x1=_pt.x, y1=_pt.y,
                                x2=_opt.x,
                                y2=_opt.y,
                                style="Continuous", layer=91, width=_width))

                _prpts.add(_pp)
                letter_pin_numbers = []
                for _rr in _pt.connected_components:
                    _pno = -1
                    for _in, _ii in enumerate(self.shapeheader.parts):
                        if _rr.instance_id == _ii.name:
                            _pno = 1 + _in
                            break
                    try:
                        pin_number = int(_rr.pin_number)
                    except ValueError:
                        if letter_pin_numbers:
                            pin_number = letter_pin_numbers.pop() + 1
                        else: 
                            pin_number = 1
                        letter_pin_numbers.append(pin_number)

                    _web.shapes.append(Eagle.PinRef(
                            partno= _pno, gateno=1, 
                            pinno=pin_number,
                        ))
        return

    def _convert(self, design):
        """ Converts design into a set of Eagle objects
        """
        self._convert_library(design)
        self.shapeheader = Eagle.ShapeHeader()
        self._convert_shapes1(design)
        self._convert_shapes2(design)
        return

    def _validate(self, design):
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

        for _ll in self.layers:
            if 91 == _ll.number:
                break
        else: # default layer set
            _deflayers = ((91, 'Nets', 2),
                          (92, 'Busses', 1),
                          (93, 'Pins', 2),
                          (94, 'Symbols', 4),
                          (95, 'Names', 7),
                          (96, 'Values', 7),
                          (97, 'Info', 7),
                          (98, 'Guide', 6),
                         )
            for _ll in _deflayers:
                self.layers.append(
                        Eagle.Layer(number=_ll[0], name=_ll[1], color=_ll[2], 
                                    fill=1, visible=True, active=True))

        if None == self.attributeheader:
            self.attributeheader = Eagle.AttributeHeader(
                    schematic=Eagle.AttributeHeader.delimeter.join((
                        Eagle.AttributeHeader.defxreflabel,
                        Eagle.AttributeHeader.defxrefpart)))

        if None == self.shapeheader:
            self.shapeheader = Eagle.ShapeHeader()

        if None == self.netclasses:
            self.netclasses = []
        else: # clear duplicates
            _ncsm = {}
            for _nc in self.netclasses:
                _ncsm[_nc.num] = _nc

            self.netclasses = []
            for _nc in sorted(_ncsm):
                self.netclasses.append(_ncsm[_nc])

        if 0 == len(self.netclasses):
            self.netclasses.append(Eagle.NetClass(0, 'default'))

        while 8 > len(self.netclasses):
            self.netclasses.append(Eagle.NetClass(len(self.netclasses)))

# calculate num of blocks
        self._calculatelibs()
        self._calculateshapes()

        self.attributeheader.numofshapes = (self.shapeheader.numofshapes +
                sum(x.numofdevsetblocks + x.numofsymbolblocks + 
                    x.numofpackageblocks for x in self.libraries))
        self.attributeheader.numofattributes = len(self.attributes)

        return

    def _calculatelibs(self):
        """ Refreshes all library (and nested) blocks
        """

        for _ll in self.libraries:

            for _ds in _ll.devsets: # usually a single entry
                _ds.numofshapesets = len(_ds.shapesets)
                _nb = 0
                for _ss in _ds.shapesets:
                    for _cc in _ss.connblocks:
                        _cc.numofshapes = len(_cc.shapes) # conns
                        _nb += 1 + _cc.numofshapes
                    _nb += 1 # connblocks hdr

                    _ss.numofshapes = len(_ss.shapes) # gates
                    _nb += 1 + _ss.numofshapes
                _ds.numofblocks = _nb

            _ll.numofdevsetblocks = 1 + sum(x.numofblocks for x in _ll.devsets)

            for _sh in _ll.symbols: # usually a single entry
                _sh.numofshapesets = len(_sh.shapesets)
                _nb = 0
                for _ss in _sh.shapesets:
                    _ss.numofshapes = len(_ss.shapes)
                    _nb += 1 + _ss.numofshapes
                _sh.numofblocks = _nb
            _ll.numofsymbolblocks = 1 + sum(x.numofblocks for x in _ll.symbols)

            for _ph in _ll.packages: # usually a single entry
                _ph.numofshapesets = len(_ph.shapesets)
                _nb = 0
                for _ss in _ph.shapesets:
                    _ss.numofshapes = len(_ss.shapes)
                    _nb += 1 + _ss.numofshapes
                _ph.numofblocks = _nb
            _ll.numofpackageblocks = 1 + sum(x.numofblocks for x in _ll.packages)

        return

    def _calculateshapes(self):
        """ Refreshes shape header (and nested) blocks
        """
        self.shapeheader.numofshapes = 1 
        for _ss in self.shapeheader.shapes:
            if not isinstance(_ss, Eagle.Polygon):
                self.shapeheader.numofshapes += 1 
            else:
                _ss.numofshapes = len(_ss.shapes)
                self.shapeheader.numofshapes += 1 + _ss.numofshapes

        self.shapeheader.numofpartblocks = 1 + len(self.shapeheader.parts)

        self.shapeheader.numofbusblocks = 1
        for _bb in self.shapeheader.buses:
            _bb.numofshapes = len(_bb.shapes)
            self.shapeheader.numofbusblocks += 1 + _bb.numofshapes

        self.shapeheader.numofnetblocks = 1
        for _nn in self.shapeheader.nets:
            _nn.numofshapes = len(_nn.shapes)
            self.shapeheader.numofnetblocks += 1 + _nn.numofshapes
        return

    def write(self, design, filename):
        """ Save given design as an Eagle format file with a given name
        """

        self._convert(design)
        self._validate(design)

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

            for _ll in self.libraries:
                _of.write(_ll.construct())
                for _ds in _ll.devsets: # usually a single entry
                    _of.write(_ds.construct())
                    for _ss in _ds.shapesets:
                        _of.write(_ss.construct())
                        for _cc in _ss.connblocks:
                            _of.write(_cc.construct())
                            for _hh in _cc.shapes: # connections
                                _of.write(_hh.construct())
                        for _gg in _ss.shapes: # gates, usually a single entry
                            _of.write(_gg.construct())
                for _sh in _ll.symbols: # usually a single entry
                    _of.write(_sh.construct())
                    for _ss in _sh.shapesets:
                        _of.write(_ss.construct())
                        for _pp in _ss.shapes: # pins, lines, texts
                            _of.write(_pp.construct())
                for _ph in _ll.packages: # usually a single entry
                    _of.write(_ph.construct())

            _of.write(self.shapeheader.construct())

            for _ss in self.shapeheader.shapes:
                _of.write(_ss.construct())

            for _pp in self.shapeheader.parts:
                _of.write(_pp.construct())
                for _ss in _pp.shapes:
                    _of.write(_ss.construct())

            for _bb in self.shapeheader.buses:
                _of.write(_bb.construct())
                for _ss in _bb.shapes:
                    _of.write(_ss.construct())

            for _nn in self.shapeheader.nets:
                _of.write(_nn.construct())
                for _ss in _nn.shapes:
                    _of.write(_ss.construct())

            _of.write(Eagle.noregblockconst)

            _dta = self.noregdelimeter.join(self.attr_jar + 
                                        [self.noregdelimeter,])
            _of.write(struct.pack("I", len(_dta))) # length of noreg block
            _of.write(_dta) # noreg block itself

            for _cc in self.netclasses:
                _of.write(_cc.construct())

            _of.write(struct.pack(Eagle.NetClass.template0,
                                  0, Eagle.NetClass.constantend, 0
                                 ))
            return


