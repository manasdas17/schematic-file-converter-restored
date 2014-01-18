#!/usr/bin/env python2
""" The Eagle Format Parser """

# upconvert - A universal hardware design file format converter using
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

# Note: It parses a file of an Eagle format of version up to 5.11.
# Default values are used for fields missed in files of previous versions.
#

import struct
import math

from upconvert.core.annotation import Annotation
from upconvert.core.component_instance import ComponentInstance, SymbolAttribute
from upconvert.core.design import Design
from upconvert.core.net import Net, NetPoint, ConnectedComponent
from upconvert.core.components import Component, Symbol, SBody, Pin
from upconvert.core.shape import Point, Line, Label, Arc, Circle, Rectangle, Polygon

#class EagleBinConsts:
#    """ Just a set of constants to be used by both parser and writer
#    """
#    pass# pylint: disable=R0902


EAGLE_SCALE = 1/0.127


class Eagle:
    """ The Eagle Format Parser """

    @staticmethod
    def _do_ojs(value):
        """ Represents a string as required by upconvert core """
        return value.decode('latin-1').encode('utf-8') if None != value else None
# or maybe we need to have a unicode object in openjson?..
#  (in that case all strings in maps have to be created as unicode ones as well)
#        return unicode(value, 'latin-1') if None != value else None

    class Header:
        """ A struct that represents a header """
        constant = 0x10
        template = "=4BI4B3I"

        def __init__(self, version="5.11", numofblocks=0):
            """ Just a constructor
            """
            self.version = version # has to be of x.y (dot-separated) format
            self.numofblocks = numofblocks
            return

        @staticmethod
        def parse(chunk):
            """ Parses header block
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Header.template, chunk)

            _ret_val = Eagle.Header(
                                version=Eagle._do_ojs('%d.%d' % (_dta[5], _dta[6])),
                                numofblocks=_dta[4], # including this one
                                      )
# [13] -- some number / counter ; changed on each 'save as' (even with no changes)
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

        @staticmethod
        def parse(chunk):
            """ Parses ?? settings ?? block
                TODO synchronization could be needed
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Settings.template, chunk)

# [11] -- sequence number of a copy (incremented on each 'save as', even with no changes)
#          (for first "settings" block only; second one contains 0 there)
            _ret_val = Eagle.Settings(seqno=Eagle.Settings.counter,
                                         copyno=_dta[8]
                                        )
            Eagle.Settings.counter += 1
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

        def __init__(self, distance=0.1, unitdist="inch", unit="inch",  # pylint: disable=R0913
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

        @staticmethod
        def parse(chunk):
            """ Parses grid block
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Grid.template, chunk)

            try:
                _unit = Eagle.Grid.units[Eagle.Grid.unitmask & _dta[3]]
            except KeyError: # unknown grid measure units
                _unit = "n/a"

            try:
                _altunit = Eagle.Grid.units[Eagle.Grid.unitmask &
                                               (_dta[3] >> 4)]
            except KeyError: # unknown grid alt measure units
                _altunit = "n/a"

# strage float format here: 8 bytes ; no idea yet
# thus proceeding in 6.0.0 way: default values are used
# (but units are preserved; 6.0.0 uses default set -- with inches)
            _ret_val = Eagle.Grid(
                                     distance=0.1, # <--- here [7:15]
                                     unitdist=_unit,
                                     unit=_unit,
                                     style=Eagle.Grid.look[
                                            Eagle.Grid.lookmask & _dta[2]],
                                     multiple=_dta[4],
                                     display=Eagle.Grid.show[
                                            Eagle.Grid.showmask & _dta[2]],
                                     altdistance=0.01, # <--- here [15:23]
                                     altunitdist=_altunit,
                                     altunit=_altunit
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

        @staticmethod
        def parse(chunk):
            """ Parses single layer block
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Layer.template, chunk)

            _linked = False # a kind of a "twin" layer
# these visible / active signs looks like legacy ones
#  and older format files have other values for this octet
            _visible = False
            _active = False
            if Eagle.Layer.nvisact == Eagle.Layer.visactmask & _dta[2]:
                _visible = False
                _active = True
            elif Eagle.Layer.visact == Eagle.Layer.visactmask & _dta[2]:
                _visible = True
                _active = True
            else:
                pass # unknown layer visibility sign

            if (Eagle.Layer.linkedsignmask ==
                    Eagle.Layer.linkedsignmask & _dta[2]):
                _linked = True

            _name = None
            if Eagle.Layer.no_embed_str != _dta[9][0]:
                _name = Eagle._do_ojs(_dta[9].rstrip(r'\0'))
            else: # from external string block
                _name = Eagle.attr_jar_list.next().name

            _ret_val = Eagle.Layer(number=_dta[3],
                                   name=_name,
                                   color=_dta[6],
                                   fill=_dta[5],
                                   visible=_visible,
                                   active=_active,
                                   linkednumber=_dta[4],
                                   linkedsign=_linked
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

        @staticmethod
        def parse(chunk):
            """ Parses attribute header block
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.AttributeHeader.template, chunk)

            _schematic = None
            if Eagle.AttributeHeader.no_embed_str != _dta[10][0]:
                _schematic = Eagle._do_ojs(_dta[10].rstrip(r'\0'))
            else: # from external string block
                _schematic = Eagle.attr_jar_list.next().name

# number of shapes + header of shapes
# number of attributes, excluding this line
# name can be of length 0 for versions prior to 5.x
#  name==None means a long name stored separately
            _ret_val = Eagle.AttributeHeader(schematic=_schematic,
                                             numofshapes=(-1 + _dta[5]),
                                             numofattributes=_dta[6]
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

        @staticmethod
        def parse(chunk):
            """ Parses library block
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Library.template, chunk)

            _name = None
            if Eagle.Library.no_embed_str != _dta[7][0]:
                _name = Eagle._do_ojs(_dta[7].rstrip(r'\0'))
            else: # from external string block
                _name = Eagle.attr_jar_list.next().name

# three ints are counters, have to recheck
            _ret_val = Eagle.Library(name=_name,
                                     numofdevsetblocks=_dta[4],
                                     numofsymbolblocks=_dta[5],
                                     numofpackageblocks=_dta[6],
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

        @staticmethod
        def parse(chunk):
            """ Parses deviceset block
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.DeviceSetHeader.template, chunk)

            _name = None
            if Eagle.DeviceSetHeader.no_embed_str != _dta[7][0]:
                _name = Eagle._do_ojs(_dta[7].rstrip(r'\0'))
            else: # from external string block
                _name = Eagle.attr_jar_list.next().name

            _ret_val = Eagle.DeviceSetHeader(name=_name,
                                       numofblocks=_dta[4],
                                       numofshapesets=_dta[5],
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

        @staticmethod
        def parse(chunk):
            """ Parses symbolheader block
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.SymbolHeader.template, chunk)

            _name = None
            if Eagle.SymbolHeader.no_embed_str != _dta[7][0]:
                _name = Eagle._do_ojs(_dta[7].rstrip(r'\0'))
            else: # from external string block
                _name = Eagle.attr_jar_list.next().name

            _ret_val = Eagle.SymbolHeader(name=_name,
                                          numofblocks=_dta[4],
                                          numofshapesets=_dta[5],
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

        @staticmethod
        def parse(chunk):
            """ Parses packageheader block
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.PackageHeader.template, chunk)

            _name = None
            if Eagle.PackageHeader.no_embed_str != _dta[7][0]:
                _name = Eagle._do_ojs(_dta[7].rstrip(r'\0'))
            else: # from external string block
                _name = Eagle.attr_jar_list.next().name

            _ret_val = Eagle.PackageHeader(name=_name,
                                           numofblocks=_dta[4],
                                           numofshapesets=_dta[5],
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

        @staticmethod
        def parse(chunk):
            """ Parses symbol block
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Symbol.template, chunk)

            _name = None
            if Eagle.Symbol.no_embed_str != _dta[9][0]:
                _name = Eagle._do_ojs(_dta[9].rstrip(r'\0'))
            else: # from external string block
                _name = Eagle.attr_jar_list.next().name

# number of shapes, excluding this line
            _ret_val = Eagle.Symbol(libid=_dta[5],
                                    name=_name,
                                    numofshapes=_dta[2],
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

        @staticmethod
        def parse(chunk):
            """ Parses package block
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Package.template, chunk)

            _name = None
            if Eagle.Package.no_embed_str != _dta[6][0]:
                _name = Eagle._do_ojs(_dta[6].rstrip(r'\0'))
            else: # from external string block
                _name = Eagle.attr_jar_list.next().name

            _desc = None
            if Eagle.Package.no_embed_str != _dta[7][0]:
                _desc = Eagle._do_ojs(_dta[7].rstrip(r'\0'))
            else: # from external string block
                _desc = Eagle.attr_jar_list.next().name

# number of shapes, excluding this line
            _ret_val = Eagle.Package(name=_name,
                                     desc=_desc,
                                     numofshapes=_dta[2],
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

        @staticmethod
        def parse(chunk):
            """ Parses net
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Net.template, chunk)

            if (Eagle.Net.constantmid1 != _dta[3] or
                    Eagle.Net.constantmid2 != _dta[4]):
                pass # strange mid-constants in net

            _name = None
            if Eagle.Net.no_embed_str != _dta[9][0]:
                _name = Eagle._do_ojs(_dta[9].rstrip(r'\0'))
            else: # from external string block
                _name = Eagle.attr_jar_list.next().name

            _ret_val = Eagle.Net(name=_name,
                                 nclass=_dta[6],
                                 numofshapes=_dta[2],
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

        @staticmethod
        def parse(chunk):
            """ Parses part
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Part.template, chunk)

            _name = None
            if Eagle.Part.no_embed_str != _dta[8][0]:
                _name = Eagle._do_ojs(_dta[8].rstrip(r'\0'))
            else: # from external string block
                _name = Eagle.attr_jar_list.next().name

            _value = None
            if Eagle.Part.no_embed_str != _dta[9][0]:
                _value = Eagle._do_ojs(_dta[9].rstrip(r'\0'))
            else: # from external string block
                _value = Eagle.attr_jar_list.next().name

            _ret_val = Eagle.Part(name=_name,
                                 libid=_dta[3],
                                 devsetndx=_dta[4],
                                 symvar=_dta[5],
                                 techno=_dta[6],
#                                 valpresence =
#                                    True if _dta[7] & Eagle.Part.val_sign_mask
#                                            else False,
                                 value=_value,
                                 numofshapes=_dta[2],
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

        @staticmethod
        def parse(chunk):
            """ Parses deviceset
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.DeviceSet.template, chunk)

            _prefix = None
            if Eagle.DeviceSet.no_embed_str != _dta[6][0]:
                _prefix = Eagle._do_ojs(_dta[6].rstrip(r'\0'))
            else: # from external string block
                _prefix = Eagle.attr_jar_list.next().name

            _desc = None
            if Eagle.DeviceSet.no_embed_str != _dta[7][0]:
                _desc = Eagle._do_ojs(_dta[7].rstrip(r'\0'))
            else: # from external string block
                _desc = Eagle.attr_jar_list.next().name

            _name = None
            if Eagle.DeviceSet.no_embed_str != _dta[8][0]:
                _name = Eagle._do_ojs(_dta[8].rstrip(r'\0'))
            else: # from external string block
                _name = Eagle.attr_jar_list.next().name

# numofshapes excludes connections-related info
# their num is numofconnblocks
            _ret_val = Eagle.DeviceSet(name=_name,
                                       prefix=_prefix,
                                       description=_desc,
#                                 prefpresence =
#                                    False if _dta[4] & Eagle.DeviceSet.nopref_sign_mask
#                                            else True,
                                        uservalue =
                                           True if _dta[4] &
                                                    Eagle.DeviceSet.uservalue_sign_mask
                                                else False,
                                        numofshapes=_dta[2],
                                        numofconnblocks=_dta[3],
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

        @staticmethod
        def parse(chunk):
            """ Parses bus
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Bus.template, chunk)

            _name = None
            if Eagle.Package.no_embed_str != _dta[3][0]:
                _name = Eagle._do_ojs(_dta[3].rstrip(r'\0'))
            else: # from external string block
                _name = Eagle.attr_jar_list.next().name

            _ret_val = Eagle.Bus(name=_name,
                                 numofshapes=_dta[2],
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

        @staticmethod
        def parse(chunk):
            """ Parses shape header block
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.ShapeHeader.template, chunk)

# number of shapes, excluding this header block
            _ret_val = Eagle.ShapeHeader(numofshapes=_dta[2],
                                         numofpartblocks=_dta[5],
                                         numofbusblocks=_dta[6],
                                         numofnetblocks=_dta[7],
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

        @staticmethod
        def parse(chunk):
            """ Parses segment
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Segment.template, chunk)

            _ret_val = Eagle.Segment(numofshapes=_dta[2],
                                     cumulativenumofshapes=_dta[5], # TODO recheck
                                    )
            return _ret_val

    class ConnectionHeader(NamedShapeSet):
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
            super(Eagle.ConnectionHeader, self).__init__(name, numofshapes,
                                                                        shapes)
            self.sindex = sindex

            if None == technologies:
                technologies = []
            self.technologies = technologies

            if None == attributes:
                attributes = []
            self.attributes = attributes
            return

        @staticmethod
        def parse(chunk):
            """ Parses header for 'connections' blocks
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.ConnectionHeader.template, chunk)

            if Eagle.ConnectionHeader.no_embed_str != _dta[4][0]:
                _attrstr = Eagle._do_ojs(_dta[4].rstrip(r'\0'))
            else: # from external string block
                _attrstr = Eagle.attr_jar_list.next().name

            _attrs = []
            _techs = []

            if 0 < len(_attrstr):
                if Eagle.ConnectionHeader.delim_techs == _attrstr[0]:
                    for _tt in _attrstr.split(
                                Eagle.ConnectionHeader.delim_techs)[1:]:
                        _techs.append(Eagle._do_ojs(_tt))
                elif Eagle.ConnectionHeader.delim_names == _attrstr[0]:
                    _attrparts = _attrstr.split(
                                Eagle.ConnectionHeader.delim_namesvals)
                    if 1 < len(_attrparts): # got a correct str
                        for _nn, _vv in zip(
                                (Eagle._do_ojs(x) for x in _attrparts[0].split(
                                        Eagle.ConnectionHeader.delim_names)[1:]),
                                (Eagle._do_ojs(x) for x in _attrparts[1].split(
                                        Eagle.ConnectionHeader.delim_vals)[1:])):
                            _attrs.append((_nn, _vv))

            if Eagle.ConnectionHeader.no_embed_str != _dta[5][0]:
                _name = Eagle._do_ojs(_dta[5].rstrip(r'\0'))
            else: # from external string block
                _name = Eagle.attr_jar_list.next().name
            if Eagle.ConnectionHeader.constantmid_def == _name:
                _name = ''

            _ret_val = Eagle.ConnectionHeader(numofshapes=_dta[2],
                                              sindex=_dta[3],
                                              technologies=_techs,
                                              attributes=_attrs,
                                              name=_name,
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

        @staticmethod
        def parse(chunk):
            """ Parses connection indexes set
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Connections.template, chunk)

            _ret_val = Eagle.Connections(connections=[x for x in _dta[2:]
                                                                if 0 != x],
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
        rotatemask2 = 0x0f # R40 is possible in text...
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
#                   0x10: "MR0",
#                   0x12: "MR45",
#                   0x14: "MR90",
#                   0x16: "MR135",
#                   0x18: "MR180",
#                   0x1a: "MR225",
#                   0x1c: "MR270",
#                   0x1e: "MR315",

#                   0x40: "SR0", #...
                  }

        rotate_r0 = "R0" # used in SR0, MR0 cases

        rotateprefixmask = 0x70
        rotate_prefixes = {
                   0x00: '',
                   0x10: 'M',
                   0x40: 'S',
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
        def decode_real(number, algo=2):
            """ Transforms given binary array to a float
            """
            _ret_val = 0
            if 1 == algo:
                _ret_val = ((number << Eagle.Shape.scale1b) /
                                                Eagle.Shape.scale1a)
            elif 2 == algo:
                _ret_val = number / Eagle.Shape.scale2
            return _ret_val

        @staticmethod
        def rotate2piradians(rotate):
            """ Converts 'rotates' string into pi radians.
                It could be implemented as a map, but a special handling for
                 None as 0. would be needed..
            """
            _ret_val = 0.

            if 'R90' == rotate:
                _ret_val = 0.5
            elif 'R180' == rotate:
                _ret_val = 1.
            elif 'R270' == rotate:
                _ret_val = 1.5
            return _ret_val

        @staticmethod
        def _ext_rotate(rotate_octet):
            """ Constructs extanded rotate mark
            """
            _rotate = (
                    Eagle.Text.rotate_prefixes[
                                Eagle.Text.rotateprefixmask & rotate_octet],
                    Eagle.Text.rotates[Eagle.Text.rotatemask2 & rotate_octet],
                    )
            if None == _rotate[1]: # SR0, MR0, None (R0) cases
                if 0 < len(_rotate[0]): # SR0, MR0
                    _ret_val = _rotate[0] + Eagle.Text.rotate_r0
                else: # None
                    _ret_val = None
            else: # R > 0
                _ret_val = _rotate[0] + _rotate[1]
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

        @staticmethod
        def parse(chunk):
            """ Parses segment
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Polygon.template, chunk)

            _ret_val = Eagle.Polygon(numofshapes=_dta[2],
                                     width=(Eagle.Polygon.width_xscale *
                                             Eagle.Shape.decode_real(
                                                                    _dta[5])),
                                     layer=_dta[9],
                                    )
            return _ret_val

    class Instance(ShapeSet, Shape):
        """ A struct that represents an instance
        """
        constant = 0x30
        template = "=2BH2iH6BI"

        smashed_mask = 0x01 # IC, +PART
        smashed2_mask = 0x02 #??

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

        @staticmethod
        def parse(chunk):
            """ Parses instance
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Instance.template, chunk)

            _ret_val = Eagle.Instance(numofshapes=_dta[2],
                                     x=Eagle.Instance.decode_real(_dta[3]),
                                     y=Eagle.Instance.decode_real(_dta[4]),
                                     smashed=True
                                        if Eagle.Instance.smashed_mask ==
                                            (Eagle.Instance.smashed_mask &
                                                _dta[10]) or
                                            Eagle.Instance.smashed2_mask ==
                                            (Eagle.Instance.smashed2_mask &
                                                _dta[10]) else False,
                                     rotate=Eagle.Instance.rotates[
                                         Eagle.Instance.rotatemask & _dta[9]],
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

        @staticmethod
        def parse(chunk):
            """ Parses rectangle
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Circle.template, chunk)

            _ret_val = Eagle.Circle(
                                      x=Eagle.Shape.decode_real(_dta[4]),
                                      y=Eagle.Shape.decode_real(_dta[5]),
                                      radius=Eagle.Shape.decode_real(_dta[6]), # the same as [7]
                                      layer=_dta[3],
                                      width=(Eagle.Circle.width_xscale *
                                             Eagle.Shape.decode_real(
                                                                    _dta[8]))
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
            self.x1 = x1 # bottom left corner
            self.y1 = y1
            self.x2 = x2 # upper right corner
            self.y2 = y2
            self.rotate = rotate
            return

        @staticmethod
        def parse(chunk):
            """ Parses rectangle
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Rectangle.template, chunk)

            _ret_val = Eagle.Rectangle(
                                      x1=Eagle.Shape.decode_real(_dta[4]),
                                      y1=Eagle.Shape.decode_real(_dta[5]),
                                      x2=Eagle.Shape.decode_real(_dta[6]),
                                      y2=Eagle.Shape.decode_real(_dta[7]),
                                      layer=_dta[3],
                                      rotate=Eagle.Rectangle.rotates[_dta[9]]
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

        wire_sign = 0x00
        arc_preset1 = (0x78, 0x79, ) # -90: q1, q2
        arc_preset2 = (0x7a, 0x7b, ) # +90: q3, q4
        arc_preset3 = (0x7c, 0x7e, ) # -180: q41, q12
        arc_preset4 = (0x7d, 0x7f, ) # +180: q23, q34
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

        @staticmethod
        def parse(chunk):
            """ Parses wire
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Wire.template, chunk)

            if Eagle.Wire.wire_sign == _dta[10]:
                _ret_val = Eagle.Wire(
                                      x1=Eagle.Shape.decode_real(_dta[4]),
                                      y1=Eagle.Shape.decode_real(_dta[5]),
                                      x2=Eagle.Shape.decode_real(_dta[6]),
                                      y2=Eagle.Shape.decode_real(_dta[7]),
                                      style=Eagle.Wire.styles[
                                          Eagle.Wire.stylemask & _dta[9]],
                                      layer=_dta[3],
                                      width=(Eagle.Wire.width_xscale *
                                             Eagle.Shape.decode_real(
                                                                    _dta[8]))
                                         )
            elif _dta[10] in (Eagle.Wire.arc_preset1 + Eagle.Wire.arc_preset2 +
                            Eagle.Wire.arc_preset3 + Eagle.Wire.arc_preset4):
                _ret_val = Eagle.FixedArc.parse(chunk)
            elif Eagle.Wire.arc_sign == _dta[10]: # Arc features "packed" coordinates...
                _ret_val = Eagle.Arc.parse(chunk)
            else:
                raise ValueError("unknown wire sign = x%x" % _dta[10])

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

        @staticmethod
        def parse(chunk):
            """ Parses junction
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Junction.template, chunk)

            _ret_val = Eagle.Junction(x=Eagle.Shape.decode_real(_dta[4]),
                                         y=Eagle.Shape.decode_real(_dta[5]),
                                         layer=_dta[3],
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

        @staticmethod
        def parse(chunk):
            """ Parses junction
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Hole.template, chunk)

            _ret_val = Eagle.Hole(x=Eagle.Shape.decode_real(_dta[4]),
                                  y=Eagle.Shape.decode_real(_dta[5]),
                                  drill=(Eagle.Hole.width_xscale *
                                      Eagle.Shape.decode_real(_dta[6])),
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

        @staticmethod
        def parse(chunk):
            """ Parses junction
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.SMD.template, chunk)

            _name = None
            if Eagle.SMD.no_embed_str != _dta[11][0]:
                _name = Eagle._do_ojs(_dta[11].rstrip(r'\0'))
            else: # from external string block
                _name = Eagle.attr_jar_list.next().name

            _ret_val = Eagle.SMD(name=_name,
                                 x=Eagle.Shape.decode_real(_dta[4]),
                                 y=Eagle.Shape.decode_real(_dta[5]),
                                 dx=(Eagle.Hole.width_xscale *
                                      Eagle.Shape.decode_real(_dta[6])),
                                 dy=(Eagle.Hole.width_xscale *
                                      Eagle.Shape.decode_real(_dta[7])),
                                 layer=_dta[3],
                                )
            return _ret_val

    class FixedArc(Wire):
        """ A struct that represents a fixed angle arc
        """
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
            super(Eagle.FixedArc, self).__init__(x1, y1, x2, y2, style, layer, width)
            self.curve = curve
            self.cap = cap
            self.direction = direction
            return

        @staticmethod
        def parse(chunk):
            """ Parses arc
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.FixedArc.template, chunk)

            _curve = None
            if _dta[10] in Eagle.Wire.arc_preset1:
                _curve = -90.
            elif _dta[10] in Eagle.Wire.arc_preset2:
                _curve = 90.
            elif _dta[10] in Eagle.Wire.arc_preset3:
                _curve = -180.
            elif _dta[10] in Eagle.Wire.arc_preset4:
                _curve = 180.

            _ret_val = Eagle.FixedArc(
                          x1=Eagle.Shape.decode_real(_dta[4]),
                          y1=Eagle.Shape.decode_real(_dta[5]),
                          x2=Eagle.Shape.decode_real(_dta[6]),
                          y2=Eagle.Shape.decode_real(_dta[7]),
                          layer=_dta[3],
                          width=(Eagle.Wire.width_xscale *
                                 Eagle.Shape.decode_real(
                                                        _dta[8])),
                          style=Eagle.Wire.styles[
                              Eagle.Wire.stylemask & _dta[9]],
                          curve=_curve,
                          cap=Eagle.Arc.caps[_dta[9] & Eagle.Arc.capmask],
                          direction=Eagle.Arc.directions[_dta[9] &
                                                Eagle.Arc.directionmask]
                                     )
            return _ret_val


    class Arc(FixedArc):
        """ A struct that represents a free angle arc
        """
        template = "=4B4IH2B" # 3-bytes long coords here..

        @staticmethod
        def parse(chunk):
            """ Parses arc
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Arc.template, chunk)

            # sign propogation by hand
            _x1 = (Eagle.Shape.decode_real(_dta[4] & 0xffffff)
                    if 0 == (0x800000 & _dta[4])
                    else (-1 *
                        Eagle.Shape.decode_real(0x1000000 - (_dta[4] & 0xffffff))))
            _y1 = (Eagle.Shape.decode_real(_dta[5] & 0xffffff)
                    if 0 == (0x800000 & _dta[5])
                    else (-1 *
                        Eagle.Shape.decode_real(0x1000000 - (_dta[5] & 0xffffff))))
            _x2 = (Eagle.Shape.decode_real(_dta[6] & 0xffffff)
                    if 0 == (0x800000 & _dta[6])
                    else (-1 *
                        Eagle.Shape.decode_real(0x1000000 - (_dta[6] & 0xffffff))))
            _y2 = (Eagle.Shape.decode_real(_dta[7] & 0xffffff)
                    if 0 == (0x800000 & _dta[7])
                    else (-1 *
                        Eagle.Shape.decode_real(0x1000000 - (_dta[7] & 0xffffff))))

# _coord is a single (either x or y) coordinate of a circle's center
            _coord = (Eagle.Shape.decode_real(
                      (((_dta[4] & 0xff000000) >> 24) & 0xff) +
                      (((_dta[5] & 0xff000000) >> 16) & 0xff00) +
                      (((_dta[6] & 0xff000000) >> 8) & 0xff0000))
                    if 0 == (0x80000000 & _dta[6])
                    else (-1 *
                      Eagle.Shape.decode_real((0x1000000 - (
                              (((_dta[4] & 0xff000000) >> 24) & 0xff) +
                              (((_dta[5] & 0xff000000) >> 16) & 0xff00) +
                              (((_dta[6] & 0xff000000) >> 8) & 0xff0000))))))

# have to determine which coord is given
            _dx = math.pow(_coord - _y2, 2) - math.pow(_coord - _y1, 2)
            _dy = math.pow(_coord - _x1, 2) - math.pow(_coord - _x2, 2)

            if abs(_x2 - _x1) < abs(_y2 - _y1): # X is given
                _x3 = _coord
                _y3 = (_dy - _y2 * _y2 + _y1 * _y1) / (2 * (_y1 - _y2))
            else: # Y is given
                _x3 = (_dx - _x1 * _x1 + _x2 * _x2) / (2 * (_x2 - _x1))
                _y3 = _coord

            _curve = math.degrees(math.acos((math.pow(_x1 - _x3, 2) + math.pow(_y1 - _y3, 2) +
                                             math.pow(_x2 - _x3, 2) + math.pow(_y2 - _y3, 2) +
                                             - math.pow(_x1 - _x2, 2) - math.pow(_y1 - _y2, 2)) /
                                    (2 * math.sqrt(math.pow(_x1 - _x3, 2) + math.pow(_y1 - _y3, 2)) *
                                         math.sqrt(math.pow(_x2 - _x3, 2) + math.pow(_y2 - _y3, 2)))))
            if not (_dta[9] & Eagle.Arc.directionmask):
                _curve *= -1

            _ret_val = Eagle.Arc( # sign propogation by hand
                          x1=_x1, y1=_y1, x2=_x2, y2=_y2,
                          layer=_dta[3],
                          width=(Eagle.Wire.width_xscale *
                                 Eagle.Shape.decode_real(
                                                        _dta[8])),
                          style=Eagle.Wire.styles[
                              Eagle.Wire.stylemask & _dta[9]],
                          curve=int((_curve + 0.005) * 100) / 100., # rounding
                          cap=Eagle.Arc.caps[_dta[9] & Eagle.Arc.capmask],
                          direction=Eagle.Arc.directions[_dta[9] &
                                                Eagle.Arc.directionmask]
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

        @staticmethod
        def parse(chunk):
            """ Parses pad
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Pad.template, chunk)

            _name = None
            if Eagle.Pad.no_embed_str != _dta[10][0]:
                _name = Eagle._do_ojs(_dta[10].rstrip(r'\0'))
            else: # from external string block
                _name = Eagle.attr_jar_list.next().name

            _ret_val = Eagle.Pad(name=_name,
                                 x=Eagle.Shape.decode_real(_dta[4]),
                                 y=Eagle.Shape.decode_real(_dta[5]),
                                 drill=Eagle.Shape.decode_real(_dta[6]),
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
                   0x30: None, # default
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
            self.name = name
            self.x = x
            self.y = y
            self.visible = visible
            self.direction = direction # signal direction
# rotation codes line direction: R0 means left, R90 - down, R180 - right, R270 - up
            self.rotate = rotate
            self.length = length # not a number
            self.function = function
            self.swaplevel = swaplevel
            return

        @staticmethod
        def parse(chunk):
            """ Parses pin
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Pin.template, chunk)

            _name = None
            if Eagle.Pin.no_embed_str != _dta[8][0]:
                _name = Eagle._do_ojs(_dta[8].rstrip(r'\0'))
            else: # from external string block
                _name = Eagle.attr_jar_list.next().name

            _ret_val = Eagle.Pin(name=_name,
                                 x=Eagle.Shape.decode_real(_dta[4]),
                                 y=Eagle.Shape.decode_real(_dta[5]),
                                 visible=Eagle.Pin.visibles[_dta[2] &
                                                Eagle.Pin.visiblemask],
                                 direction=Eagle.Pin.directions[_dta[6] &
                                                Eagle.Pin.dirmask],
                                 rotate=Eagle.Pin.rotates[
                                              ((Eagle.Pin.rotatemask << 4) &
                                              _dta[6]) >> 4],
                                 length=Eagle.Pin.lengths[_dta[6] &
                                                Eagle.Pin.lengthmask],
                                 function=Eagle.Pin.functions[_dta[2] &
                                                Eagle.Pin.funcmask],
                                 swaplevel=_dta[7],
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
            self.sindex = sindex # symbol index
            self.addlevel = addlevel
            return

        @staticmethod
        def parse(chunk):
            """ Parses junction
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Gate.template, chunk)

            _name = None
            if Eagle.Gate.no_embed_str != _dta[9][0]:
                _name = Eagle._do_ojs(_dta[9].rstrip(r'\0'))
            else: # from external string block
                _name = Eagle.attr_jar_list.next().name

            _ret_val = Eagle.Gate(x=Eagle.Shape.decode_real(_dta[4]),
                                  y=Eagle.Shape.decode_real(_dta[5]),
                                  name=_name,
                                  sindex=_dta[8],
                                  addlevel=Eagle.Gate.addlevels[_dta[6]],
                                 )
            return _ret_val

    class Text(Shape):
        """ A struct that represents a text
        """
        constant = 0x31
        template = "=4B2iH4B6s"

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

        @staticmethod
        def parse(chunk):
            """ Parses text
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Text.template, chunk)

            _value = None
            if Eagle.Text.no_embed_str != _dta[11][0]:
                _value = Eagle._do_ojs(_dta[11].rstrip(r'\0'))
            else: # from external string block
                _value = Eagle.attr_jar_list.next().name

            _ret_val = Eagle.Text(value=_value,
                                     x=Eagle.Shape.decode_real(_dta[4]),
                                     y=Eagle.Shape.decode_real(_dta[5]),
                                     size=Eagle.Text.size_xscale *
                                          Eagle.Shape.decode_real(_dta[6]),
                                     layer=_dta[3],
                                     rotate=Eagle.Text._ext_rotate(_dta[10]),
                                     font=Eagle.Text.fonts[_dta[2]],
                                     ratio=_dta[7] >> Eagle.Text.ratio_sscale,
                                    )
            return _ret_val

        @staticmethod
        def parse2(chunk):
            """ Parses string name
            """
            _ret_val = None

            _parts = chunk.split(Eagle.Text.delimeter)
            if 1 < len(_parts):
                pass # too many extra values for Text

            _ret_val = _parts[0]

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
                Note: 6.0.0's xref is an other name for onoff
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
            return

        @staticmethod
        def parse(chunk):
            """ Parses label
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Label.template, chunk)

            _ret_val = Eagle.Label(x=Eagle.Shape.decode_real(_dta[4]),
                                      y=Eagle.Shape.decode_real(_dta[5]),
                                      size=Eagle.Label.size_xscale *
                                           Eagle.Shape.decode_real(_dta[6]),
                                      layer=_dta[3],
#                                      xref=0,
                                      rotate=Eagle.Label.rotates[
                                              Eagle.Label.rotatemask &
                                              _dta[9]],
                                      ratio=_dta[7] >> Eagle.Text.ratio_sscale,
                                      font=Eagle.Label.fonts[_dta[2]],
                                      onoff=(True if 0 !=
                                             _dta[10] & Eagle.Label.onoffmask
                                             else False),
                                      mirrored=(True if 0 !=
                                                _dta[9] & Eagle.Label.mirroredmask
                                                else False),
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

        @staticmethod
        def parse(chunk):
            """ Parses frame
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.Frame.template, chunk)

            _ret_val = Eagle.Frame(x1=Eagle.Shape.decode_real(_dta[4]),
                                      y1=Eagle.Shape.decode_real(_dta[5]),
                                      x2=Eagle.Shape.decode_real(_dta[6]),
                                      y2=Eagle.Shape.decode_real(_dta[7]),
                                      columns=_dta[8],
                                      rows=_dta[9],
                                      bleft=(0 != Eagle.Frame.bleftmask & _dta[10]),
                                      btop=(0 != Eagle.Frame.btopmask & _dta[10]),
                                      bright=(0 != Eagle.Frame.brightmask & _dta[10]),
                                      bbottom=(0 != Eagle.Frame.bbottommask & _dta[10]),
                                      layer=_dta[3],
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

        @staticmethod
        def parse(chunk):
            """ Parses attribute-name
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.AttributeNam.template, chunk)

            _ret_val = Eagle.AttributeNam(x=Eagle.Shape.decode_real(_dta[4]),
                                          y=Eagle.Shape.decode_real(_dta[5]),
                                          size=Eagle.Shape.size_xscale *
                                               Eagle.Shape.decode_real(_dta[6]),
                                          layer=_dta[3],
                                          rotate=Eagle.AttributeNam.rotates[
                                              Eagle.AttributeNam.rotatemask &
                                              _dta[9]],
                                          font=Eagle.AttributeNam.fonts[_dta[2]],
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

        @staticmethod
        def parse(chunk):
            """ Parses attribute-name
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.AttributeVal.template, chunk)

            _ret_val = Eagle.AttributeVal(x=Eagle.Shape.decode_real(_dta[4]),
                                          y=Eagle.Shape.decode_real(_dta[5]),
                                          size=Eagle.Shape.size_xscale *
                                               Eagle.Shape.decode_real(_dta[6]),
                                          layer=_dta[3],
                                          rotate=Eagle.AttributeVal.rotates[
                                              Eagle.AttributeVal.rotatemask &
                                              _dta[9]],
                                          font=Eagle.AttributeVal.fonts[_dta[2]],
                                         )
            return _ret_val

    class AttributePrt(AttributeNam):
        """ A struct that represents a part's PART attribute
        """
        constant = 0x3f

        def __init__(self, x, y, size, layer, rotate, font, name="PART"): # pylint: disable=R0913
            """ Just a constructor
            """
            super(Eagle.AttributePrt, self).__init__(x, y,
                                        size, layer, rotate, font, name)
            return

        @staticmethod
        def parse(chunk):
            """ Parses attribute-name
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.AttributePrt.template, chunk)

# [7] ?
            _ret_val = Eagle.AttributePrt(x=Eagle.Shape.decode_real(_dta[4]),
                                          y=Eagle.Shape.decode_real(_dta[5]),
                                          size=Eagle.Shape.size_xscale *
                                               Eagle.Shape.decode_real(_dta[6]),
                                          layer=_dta[3],
                                          rotate=Eagle.AttributePrt._ext_rotate(_dta[9]), # no mask: like Text!
                                          font=Eagle.AttributePrt.fonts[_dta[2]],
                                         )
            return _ret_val

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

        @staticmethod
        def parse(chunk):
            """ Parses attribute-name
            """
            _ret_val = None

            _dta = struct.unpack(Eagle.PinRef.template, chunk)

            _ret_val = Eagle.PinRef(partno=_dta[4],
                                    gateno=_dta[5],
                                    pinno=_dta[6],
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

        @staticmethod
        def _parse(string):
            """ Splits string in parts
            """
            (_name, _value) = (None, None)

            _parts = string.split(Eagle.Attribute.delimeter)

            _name = Eagle._do_ojs(_parts[0])
            if 2 > len(_parts):
                pass # strange embedded attribute
            else:
                _value = Eagle.Attribute.delimeter.join(
                                        Eagle._do_ojs(x) for x in _parts[1:])

            return (_name, _value)

        @staticmethod
        def parse(chunk):
            """ Parses block attribute
            """
            _ret_val = None
            (_name, _value) = (None, None)

            _dta = struct.unpack(Eagle.Attribute.template, chunk)

            if Eagle.Attribute.no_embed_str != _dta[4][0]: # embedded attr
                (_name, _value) = Eagle.Attribute._parse(_dta[4].rstrip('\x00'))
            else: # from external string block
# TODO decode [8] [9] [10]
# [11] -- a kind of a marker, 0x09 / 0x08; 4 bytes long int, changed on each save as, even with no changes
#  probably just a random int, no any pattern was discovered
                _name = Eagle.attr_jar_list.next().name

            _ret_val = Eagle.Attribute(name=_name,
                                          value=_value
                                         )
            return _ret_val

        @staticmethod
        def parse2(chunk):
            """ Parses string attribute
            """
            _ret_val = None

            (_name, _value) = Eagle.Attribute._parse(chunk)
            _ret_val = Eagle.Attribute(name=_name,
                                          value=_value
                                         )
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

        @staticmethod
        def parse(chunk):
            """ Parses string attribute
            """
            _ret_val = None
            (_xreflabel, _xrefpart) = (None, None)

            _parts = chunk.split(Eagle.Schematic.delimeter)
            _xreflabel = Eagle._do_ojs(_parts[0])

            if 2 != len(_parts):
                pass # strange schematic string
            else:
                _xrefpart = Eagle._do_ojs(_parts[1])

            _ret_val = Eagle.Schematic(xreflabel=_xreflabel,
                                          xrefpart=_xrefpart
                                         )
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
        def decode_real(number):
            """ Transforms given binary array to a float
            """
            _ret_val = 0
            _ret_val = number / Eagle.NetClass.scale1
            return _ret_val

        @staticmethod
        def parse(leadint, ncconst, chunk):
            """ Parses netclass
            """
            _ret_val = None

            if Eagle.NetClass.constant == ncconst and None != chunk:
                _name = Eagle._do_ojs(chunk.split(r'\0')[0])
                _foff = 1 + len(_name)

# number of clearance intervals (and thus block length) depends on a format version
                _template, _cl_block_len = None, -1
                if 52 == len(chunk[_foff:]):
                    _template = "13I"
                elif 24 == len(chunk[_foff:]):
                    _template = "6I"
                    _cl_block_len = 1
                else:
                    raise ValueError("unexpected netclass block length")

                _dta = struct.unpack(_template, chunk[_foff:])
                if "13I" == _template:
                    _cl_block_len = 1 + _dta[0]

                if (Eagle.NetClass.constantmid == _dta[1] and
                        Eagle.NetClass.constantend == _dta[-1]):
                    if 0 < len(_name): # used netclass
                        _ret_val = Eagle.NetClass(
                                 num=_dta[0],
                                 name=_name,
                                 width=Eagle.NetClass.decode_real(_dta[2]),
                                 drill=Eagle.NetClass.decode_real(_dta[3]),
                                 clearances = [
                                     (_nn,
                                      Eagle.NetClass.decode_real(
                                                                _dta[4 + _nn])
                                     )
                                     for _nn in range(_cl_block_len)
                                     if 0 != _dta[4 + _nn]
                                 ],
                                 leadint=leadint
                                                    )
                    else: # unused netclass
                        _ret_val = Eagle.NetClass(num=_dta[0],
                                                     leadint=leadint)
                else:
                    pass # bad constants or/and data in netclasses
            elif Eagle.NetClass.constantend == ncconst and None == chunk:
                pass # nothing to do: final entry ; never hit though
            else:
                pass # bad constants or/and data in netclasses
            return _ret_val

    blocksize = 24
    noregblockconst = b'\x13\x12\x99\x19'
    noregdelimeter = r'\0'

    def __init__(self):
        """ Basic initilaization
        """
        self.header = None
        self.layers = []
        self.settings = []
        self.grid = None
        self.attributeheader = None
        self.attributes = []
        self.libraries = []
        self.shapeheader = None
#        self.parts = []
        self.texts = []
        self.netclasses = []

        self.noname_counter = self.noname_def_counter
        return


    @staticmethod
    def auto_detect(filename):
        """ Return our confidence that the given file is an eagle schematic """
        with open(filename, 'r') as f:
            data = f.read(4096)
        confidence = 0
        if ('\x10' == data[0x00] and '\x11' == data[0x18] and
                '\x11' == data[0x30] and '\x12' == data[0x48]):
            confidence += 0.9
        return confidence


    def _parse_blocks(self, filehandle, numofblocks): # pylint: disable=R0912
        """ Parse fixed length block part of a file
        """
# to keep parsing position
        _cur_lib = None
        _cur_web = None # consists of one or more shapesets/segments
        _cur_segment = None # consists of one or more shapes
        _prev_segment = None # for polygons only
        _cur_connset = None # consists of one or more shapes (deviceset shows two types)

# loop through 24 byte long blocks
        for _nn in range(numofblocks):
            _dta = filehandle.read(self.blocksize)

#            print"d>",' '.join([x.encode('hex') for x in _dta])

            _type = struct.unpack("24B", _dta)[0]
            if Eagle.Settings.constant == _type:
                self.settings.append(self.Settings.parse(_dta))
            elif Eagle.Grid.constant == _type:
                self.grid = self.Grid.parse(_dta)
            elif Eagle.Layer.constant == _type:
                self.layers.append(self.Layer.parse(_dta))
            elif Eagle.AttributeHeader.constant == _type:
                self.attributeheader = self.AttributeHeader.parse(_dta)
            elif Eagle.Library.constant == _type:
                _cur_lib = self.Library.parse(_dta)
                self.libraries.append(_cur_lib)
            elif Eagle.DeviceSetHeader.constant == _type:
                _cur_web = self.DeviceSetHeader.parse(_dta)
                _cur_lib.devsets.append(_cur_web)
            elif Eagle.SymbolHeader.constant == _type:
                _cur_web = self.SymbolHeader.parse(_dta)
                _cur_lib.symbols.append(_cur_web)
            elif Eagle.PackageHeader.constant == _type:
                _cur_web = self.PackageHeader.parse(_dta)
                _cur_lib.packages.append(_cur_web)
            elif Eagle.Symbol.constant == _type:
                _cur_segment = self.Symbol.parse(_dta)
                _cur_web.shapesets.append(_cur_segment)
                _prev_segment = None
            elif Eagle.Package.constant == _type:
                _cur_segment = self.Package.parse(_dta)
                _cur_web.shapesets.append(_cur_segment)
                _prev_segment = None
            elif Eagle.ShapeHeader.constant == _type:
                self.shapeheader = self.ShapeHeader.parse(_dta)
                _cur_segment = self.shapeheader
            elif Eagle.Bus.constant == _type:
                _cur_web = self.Bus.parse(_dta)
                self.shapeheader.buses.append(_cur_web)
            elif Eagle.Net.constant == _type:
                _cur_web = self.Net.parse(_dta)
                self.shapeheader.nets.append(_cur_web)
            elif Eagle.Segment.constant == _type:
                _cur_segment = self.Segment.parse(_dta)
                _cur_web.shapes.append(_cur_segment)
                _prev_segment = None
            elif Eagle.DeviceSet.constant == _type:
                _cur_segment = self.DeviceSet.parse(_dta)
                _cur_web.shapesets.append(_cur_segment)
                _prev_segment = None
            elif Eagle.ConnectionHeader.constant == _type:
                _cur_connset = self.ConnectionHeader.parse(_dta)
                _cur_segment.connblocks.append(_cur_connset)
                _prev_segment = None
            elif Eagle.Part.constant == _type:
                _cur_web = self.Part.parse(_dta)
                self.shapeheader.parts.append(_cur_web)
            elif Eagle.Polygon.constant == _type:
                if None == _prev_segment: # next polygon in the same segment
                    _prev_segment = _cur_segment
                _cur_segment = self.Polygon.parse(_dta)
                _prev_segment.shapes.append(_cur_segment)
            elif Eagle.Instance.constant == _type:
                _cur_segment = self.Instance.parse(_dta)
                _cur_web.shapes.append(_cur_segment)
                _prev_segment = None
            elif Eagle.Connections.constant == _type:
                _cur_connset.shapes.append(self.Connections.parse(_dta))
            elif Eagle.Gate.constant == _type:
                _cur_segment.shapes.append(self.Gate.parse(_dta))
            elif Eagle.Circle.constant == _type:
                _cur_segment.shapes.append(self.Circle.parse(_dta))
            elif Eagle.Rectangle.constant == _type:
                _cur_segment.shapes.append(self.Rectangle.parse(_dta))
            elif Eagle.Wire.constant == _type:
                _cur_segment.shapes.append(self.Wire.parse(_dta))
            elif Eagle.Hole.constant == _type:
                _cur_segment.shapes.append(self.Hole.parse(_dta))
            elif Eagle.SMD.constant == _type:
                _cur_segment.shapes.append(self.SMD.parse(_dta))
            elif Eagle.PinRef.constant == _type:
                _cur_segment.shapes.append(self.PinRef.parse(_dta))
            elif Eagle.Junction.constant == _type:
                _cur_segment.shapes.append(self.Junction.parse(_dta))
            elif Eagle.Pad.constant == _type:
                _cur_segment.shapes.append(self.Pad.parse(_dta))
            elif Eagle.Pin.constant == _type:
                _cur_segment.shapes.append(self.Pin.parse(_dta))
            elif Eagle.Label.constant == _type:
                _cur_segment.shapes.append(self.Label.parse(_dta))
            elif Eagle.AttributeNam.constant == _type:
                _cur_segment.shapes.append(self.AttributeNam.parse(_dta))
            elif Eagle.AttributeVal.constant == _type:
                _cur_segment.shapes.append(self.AttributeVal.parse(_dta))
            elif Eagle.AttributePrt.constant == _type:
                _cur_segment.shapes.append(self.AttributePrt.parse(_dta))
            elif Eagle.Text.constant == _type:
                _cur_segment.shapes.append(self.Text.parse(_dta))
            elif Eagle.Frame.constant == _type:
                _cur_segment.shapes.append(self.Frame.parse(_dta))
            elif Eagle.Attribute.constant == _type:
                self.attributes.append(self.Attribute.parse(_dta))
            else:
# TODO remove
                print("unknown block tag %s" % hex(_type))

        return

    def _parse_netclasses(self, filehandle):
        """ Parse netclasses part (fixed part + length + data part)
        """

        while True: # netclasses ## 0..7
            (_some_int, _ncconst, _nclen) = struct.unpack(
                    self.NetClass.template0,
                    filehandle.read(struct.calcsize(self.NetClass.template0)))
            _ncdta = None
            if 0 < _nclen:
                _ncdta = filehandle.read(_nclen)
            else:
                break # should leadnum of a final 3I block be saved?..
            self.netclasses.append(self.NetClass.parse(_some_int,
                                                       _ncconst, _ncdta))
        return

    noname_def_counter = 10000
    noname_def_prefix = 'EagleINR/'

    def get_unique_string(self):
        """ Gives a name when it's required; 
            not a random one to get the same schematic on subsequent runs
        """
        _ret_val = '%s%d' % (self.noname_def_prefix, self.noname_counter)
        self.noname_counter += 1
        return _ret_val

    attr_jar = [] # attribute list

    @classmethod
    def attr_jar_iter(cls):
        """ Returns next attribute on each call
        """
        for _aa in cls.attr_jar:
            yield _aa

    def _parse(self, filehandle):
        """ Parse an Eagle file into a set of Eagle objects
        """
# headers (constant block size driven)
        self.header = self.Header.parse(filehandle.read(self.blocksize))

# parsing of external attributes beforehand helps its placing
        filehandle.seek(self.header.numofblocks * self.blocksize)
        filehandle.read(4) # noregblockheader
        _unreg_dta = filehandle.read(struct.unpack("I",
                        filehandle.read(4))[0]).split(self.noregdelimeter)
        filehandle.seek(1 * self.blocksize)
        for _aa in _unreg_dta:
            if 0 < len(_aa):
                Eagle.attr_jar.append(Eagle.Attribute.parse2(_aa))
        Eagle.attr_jar_list = Eagle.attr_jar_iter()

        self._parse_blocks(filehandle, -1 + self.header.numofblocks)

# desc (length driven)
        filehandle.read(4) # noregblockheader
## TODO remove
#        if Eagle.noregblockconst != _noregblockheader:
#            print("bad constant follows headers!")

        # read len in bytes, then read corrsponding number of bytes
        #  -- just to skip since external attributes were parsed earlier
        _unreg_dta = filehandle.read(struct.unpack("I",
                            filehandle.read(4))[0]).split(self.noregdelimeter)

# just to note: the list above ends with two zero bytes

        self._parse_netclasses(filehandle)
        return

    @staticmethod
    def _convert_arc(sarc):
        """ Converts a Eagle's Arc / FixedArc objects into Arc
        """
        _ret_val = None

# calculate radius
        _xm, _ym = (sarc.x1 + sarc.x2) / 2, (sarc.y1 + sarc.y2) / 2
        _dm = math.sqrt(math.pow(sarc.x1 - _xm, 2) +
                math.pow(sarc.y1 -_ym, 2))
        _radius = abs(_dm / math.sin(math.radians(sarc.curve / 2)))

# calculate start and end angles, beginning
        _xu = sarc.x1 if sarc.y1 > sarc.y2 else sarc.x2 # upper point's x
        _am = (math.pi / 2 - math.acos((_xm - _xu) / _dm) + # middle
                0 if True else (math.pi / 2))
        if 0 > _am:
            _am += math.pi

# calculate center
        (_x1, _y1, _x2, _y2) = ((sarc.x1, sarc.y1, sarc.x2, sarc.y2)
                                    if 'counterclockwise' == sarc.direction else
                                    (sarc.x2, sarc.y2, sarc.x1, sarc.y1))
        _mm = _radius * math.cos(math.radians(abs(sarc.curve / 2)))
        _xcc, _ycc = (abs(abs(_y1) - abs(_ym)) * abs(_mm / _dm),
                        abs(abs(_x1) - abs(_xm)) * abs(_mm / _dm)) # x <-> y, for an orthogonal vector

        _xc, _yc = -1., -1.
        if _x1 >= _xm and _y1 <= _ym: # different operations for an each quadrant
            _xc, _yc = _xm - _xcc, _ym - _ycc
        elif _x1 >= _xm and _y1 >= _ym:
            _xc, _yc = _xm + _xcc, _ym - _ycc
        elif _x1 <= _xm and _y1 >= _ym:
            _xc, _yc = _xm + _xcc, _ym + _ycc
        elif _x1 <= _xm and _y1 <= _ym:
            _xc, _yc = _xm - _xcc, _ym + _ycc

# calculate start and end angles, end
        if _x1 <= _xm: # 3rd and 4th quadrants
            _am += math.pi
        _astart = _am - math.radians(abs(sarc.curve / 2))
        _aend = _astart + math.radians(abs(sarc.curve))

        _ret_val = Arc(x=_xc, y=_yc,
                    start_angle=(_astart / math.pi),
                    end_angle=(_aend / math.pi),
                    radius=_radius,
                    )
        return _ret_val

    def _convert(self):
        """ Converts a set of Eagle objects into Design
        """
        design = Design()

# File Version is applied by Design itself

# Component Instances (Array) / Components (Array)
        value_names = []
        for _pp in self.shapeheader.parts:
            _libid = ':'.join((self.libraries[-1 + _pp.libid].name,
                               _pp.value if _pp.value not in value_names else 
                                   self.get_unique_string())) # to avoid same name collisions
            value_names.append(_pp.value)
            _ci = ComponentInstance(instance_id=_pp.name,
                                    library_component=None, # FIXME(shamer): where is the actual library component?
                                    library_id=_libid,
                                    symbol_index=0)    # There appears to only have the possibility
                                                                # 1 symbol per component, so I will
                                                                # hardcode this to 0 while
                                                                # figuring out how to make get the
                                                                # correct component symbol index
                                    #symbol_index=_pp.symvar)    # other candidate is devsetndx:
                                                                #  'devsets' contains all variants
                                                                #  used in this schematic
            _sa = SymbolAttribute(x=_pp.shapes[0].x, # shapes' len is always 1 here
                                  y=_pp.shapes[0].y,
                                  rotation=Eagle.Shape.rotate2piradians(
                                        _pp.shapes[0].rotate),
                                  flip=False
                                 )

            _dd = self.libraries[-1 + _pp.libid].devsets[0].shapesets[-1 + _pp.devsetndx]
            _sym = self.libraries[-1 + _pp.libid].symbols[0].shapesets[
                                                    -1 + _dd.shapes[0].sindex]

            if 0 != len(_dd.connblocks[0].technologies):
                _ci.add_attribute("technology",
                        _dd.connblocks[0].technologies[-1 + _pp.techno])

            _co = None
            if not _libid in design.components.components:
                _co = Component(_sym.name)
                _sy = Symbol()
                _bd = SBody()
                _pc = 1 # Eagle counts from 1

                if 0 != len(_dd.connblocks[0].attributes):
                    for _aa in _dd.connblocks[0].attributes:
                        _co.add_attribute(_aa[0], _aa[1])
                _co.add_attribute("prefix", _dd.prefix)
                _co.add_attribute("description", _dd.description)

            for _ss in _sym.shapes:
                if isinstance(_ss, Eagle.Text):
                    _val = 'undef'
                    if r'>NAME' == _ss.value:
                        _val = _pp.name
                    elif r'>VALUE' == _ss.value:
                        _val = _pp.value
                    _an = Annotation(value=_val, # value from symbol
                                     x=(_ss.x),
                                     y=(_ss.y),
                                     rotation=((
                                         Eagle.Shape.rotate2piradians(
                                                    _pp.shapes[0].rotate) +
                                         Eagle.Shape.rotate2piradians(
                                                    _ss.rotate)) % 2),
                                     visible='true',
                                    )
                    _sa.add_annotation(_an)
                else:
                    if None != _co:
                        if isinstance(_ss, Eagle.Pin):

                            _opx, _lx = _ss.x, _ss.x
                            _opy, _ly = _ss.y, _ss.y
                            _lrot = 0.
                            if None == _ss.rotate: # left
                                _opx += 20/EAGLE_SCALE
                                _lx = (_ss.x + _opx) / 2
                                _ly += 20/EAGLE_SCALE
                            elif "R90" == _ss.rotate: # down
                                _opy += 20/EAGLE_SCALE
                                _lx += 20/EAGLE_SCALE
                                _ly = (_ss.y + _opy) / 2
                                #_lrot = 0.5 or 1.5 if label rotation is required
                            elif "R180" == _ss.rotate: # right
                                _opx -= 20/EAGLE_SCALE
                                _lx = (_ss.x + _opx) / 2
                                _ly += 20/EAGLE_SCALE
                            elif "R270" == _ss.rotate: # up
                                _opy -= 20/EAGLE_SCALE
                                _lx += 20/EAGLE_SCALE
                                _ly = (_ss.y + _opy) / 2
                                #_lrot = 0.5 or 1.5 if label rotation is required

                            _label = Label (x=_lx, y=_ly,
                                            text=_ss.name,
                                            align='center', rotation=_lrot)
                            _pn = Pin(label=_label,
                                      p1=Point(_opx, _opy), # just 10pix in an opposite direction
                                      p2=Point(_ss.x, _ss.y),
                                      pin_number=_pc)

                            _pn.add_attribute('visible', _ss.visible)
                            _pn.add_attribute('direction', _ss.direction) # signal direction
                            _pn.add_attribute('length', _ss.length) # not a number
                            _pn.add_attribute('function', _ss.function)
                            _pn.add_attribute('swaplevel', _ss.swaplevel)

                            _bd.add_pin(_pn)
                            _pc += 1
                        else:
                            _sp = None
                            if isinstance(_ss, Eagle.FixedArc): # including Arc
                                _sp = Eagle._convert_arc(_ss)
                                _sp.add_attribute('style', _ss.style)
                                _sp.add_attribute('width', _ss.width)
                            elif isinstance(_ss, Eagle.Wire):
                                _sp = Line(p1=Point(_ss.x1, _ss.y1),
                                           p2=Point(_ss.x2, _ss.y2))
                                _sp.add_attribute('style', _ss.style)
                                _sp.add_attribute('width', _ss.width)
                            elif isinstance(_ss, Eagle.Circle):
                                _sp = Circle(x=_ss.x, y=_ss.y, 
                                                radius=_ss.radius)
                                _sp.add_attribute('width', _ss.width)
                            elif isinstance(_ss, Eagle.Rectangle):
                                _width = abs(_ss.x2 - _ss.x1)
                                _height = abs(_ss.y2 - _ss.y1)
                                if None == _ss.rotate or "R180" == _ss.rotate: # normal position
                                    _x = _ss.x1
                                    _y = _ss.y1 + _height # bottom left vs upper left
                                elif "R90" == _ss.rotate or "R270" == _ss.rotate: # pi/2 rotation
                                    _width, _height = _height, _width
                                    _x = (_ss.x1 + _ss.x2 - _width) / 2 
                                    _y = (_ss.y1 + _ss.y2 + _height) / 2
                                _sp = Rectangle(x=_x, y=_y, width=_width, height=_height)
                            elif isinstance(_ss, Eagle.Polygon):
# second point for an every Eagle.Wire can be skipped since it'll be the first one
#  for the next Wire
# some Eagle.Wires are actually Eagle.FixedArcs, but processed as Wires, i.e. with no
#  curve
# also it can include Eagle.Text. It's just skipped
                                _pts = [Point(s.x1, s.y1) for s in _ss.shapes
                                        if isinstance(_ss, Eagle.Wire)]
                                _sp = Polygon(points=_pts)
                            elif isinstance(_ss, Eagle.Frame):
                                pass # a kind of a box around a schematic
                            else:
# TODO remove
                                print("unexpected block %s in shapeset" % _ss.__class__.__name__)

                            if None != _sp: # i.e. label (!= text), hole, ..
                                _sp.add_attribute('layer', _ss.layer)
                                _bd.add_shape(_sp)

            _ci.add_symbol_attribute(_sa)
            design.add_component_instance(_ci)
            if None != _co:
                _sy.add_body(_bd)
                _co.add_symbol(_sy)
                design.add_component(_libid, _co)

# Nets (Array)
        for _bb in self.shapeheader.buses + self.shapeheader.nets:
            for _nn, _sg in enumerate(_bb.shapes): # segments, they don't share any common points
                _net = Net('%s-%d' % (_bb.name, _nn))
                if isinstance(_bb, Eagle.Bus):
                    _net.add_attribute(u'type', u'bus')
                else: # Net
                    _net.add_attribute(u'type', u'net')
                    _net.add_attribute(u'netclass', _bb.nclass)

                    _nc = self.netclasses[_bb.nclass] # yes, info will be duplicated
                    _net.add_attribute(u'netname', _nc.name)
                    _net.add_attribute(u'netwidth', _nc.width)
                    _net.add_attribute(u'netdrill', _nc.drill)
                    for _cc in _nc.clearances:
                        _net.add_attribute(u'netclearance' + str(_cc[0]), _cc[1])
                for _ss in _sg.shapes: # wires only for buses, wires + pinrefs + junctions for nets
                    if isinstance(_ss, Eagle.FixedArc): # including Eagle.Arc
                        Eagle._convert_arc(_ss)

# now it's the same as wire, but probably some interpolation is required
                        _p1name = "%s-%s" % (str(_ss.x1), str(_ss.y1))
                        _p2name = "%s-%s" % (str(_ss.x2), str(_ss.y2))

                        if not _p1name in _net.points:
                            _net.add_point(NetPoint(_p1name, _ss.x1, _ss.y1))
                        if not _p2name in _net.points:
                            _net.add_point(NetPoint(_p2name, _ss.x2, _ss.y2))

                        if not _p2name in _net.points[_p1name].connected_points:
                            _net.points[_p1name].add_connected_point(_p2name)
                        if not _p1name in _net.points[_p2name].connected_points:
                            _net.points[_p2name].add_connected_point(_p1name)
                    elif isinstance(_ss, Eagle.Wire):
                        _p1name = "%s-%s" % (str(_ss.x1), str(_ss.y1))
                        _p2name = "%s-%s" % (str(_ss.x2), str(_ss.y2))

                        if not _p1name in _net.points:
                            _net.add_point(NetPoint(_p1name, _ss.x1, _ss.y1))
                        if not _p2name in _net.points:
                            _net.add_point(NetPoint(_p2name, _ss.x2, _ss.y2))

                        if not _p2name in _net.points[_p1name].connected_points:
                            _net.points[_p1name].add_connected_point(_p2name)
                        if not _p1name in _net.points[_p2name].connected_points:
                            _net.points[_p2name].add_connected_point(_p1name)
                    elif isinstance(_ss, Eagle.PinRef):
                        _prt = self.shapeheader.parts[-1 + _ss.partno]
                        _dst = self.libraries[-1 + _prt.libid].devsets[0
                                    ].shapesets[-1 + _prt.devsetndx]
                        _sym = self.libraries[-1 + _prt.libid].symbols[0
                                    ].shapesets[-1 + _dst.shapes[0].sindex]
                        _prno = 1
                        for _yy in _sym.shapes:
                            if isinstance(_yy, Eagle.Pin):
                                if _ss.pinno == _prno:
                                    _pname = "%s-%s" % (str(_prt.shapes[0].x + _yy.x),
                                                str(_prt.shapes[0].y + _yy.y))
                                    if not _pname in _net.points:
                                        _net.add_point(NetPoint(_pname,
                                                        _prt.shapes[0].x + _yy.x,
                                                        _prt.shapes[0].y + _yy.y))
                                    _net.points[_pname].add_connected_component(
                                            ConnectedComponent(_prt.name, _ss.pinno))
                                _prno += 1
                    elif isinstance(_ss, Eagle.Junction):
                        pass # has to be skipped: junction points are implemented as
                             #  connected_points arrays in OJSON
                    elif isinstance(_ss, Eagle.Label):
                        pass # has to be skipped: no use here
                    else:
# TODO remove
                        print("unexpected block %s in bus/net" % _ss.__class__.__name__)
                design.add_net(_net)

# Components (Array) -- above
#        for _ll in self.libraries:
#            for _ss in _ll.symbols[0].shapesets:
#                _co = Component(_ss.name)
#                pass
#                design.add_component(str(_ss.libid) + 'xx', _co)


        return design

    def parse(self, filename):
        """ Parse an Eagle file into a design """
        design = None

        with open(filename, 'rb') as _if:
            self._parse(_if)

        design = self._convert()
        design.scale(EAGLE_SCALE)

        return design


