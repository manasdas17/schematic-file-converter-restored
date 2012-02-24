#!/usr/bin/python
# encoding: utf-8
#pylint: disable=R0904
""" The eagle parser test class """

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

import unittest

from parser.eagle import Eagle

class EagleTests(unittest.TestCase):
    """ The tests of the eagle parser """

    def setUp(self):
        """ Setup the test case. """
        Eagle.attr_jar = [Eagle.Attribute('name_a', 'value_a'),
                            Eagle.Attribute('name_b', 'value_b'),
                            Eagle.Attribute('name_c', 'value_c'),
                         ]
        Eagle.attr_jar_list = Eagle.attr_jar_iter()

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_eagle_parser(self):
        """ Test creating an empty parser. """
        parser = Eagle()
        assert parser != None

    def test_header_parse(self):
        """ Test Header block parsing """
        
        _valid_chunk = b''.join((b"\x10\x00\x0c\x00\x10\x00\x00\x00", 
                                 b"\x05\x0b\x04\x3c\x00\x2e\x00\x00",
                                 b"\x00\x00\x00\x00\x00\x00\x00\x00"))
        _header = Eagle.Header.parse(_valid_chunk)

        self.assertNotEqual(_header, None)

        self.assertEqual(_header.version, "5.11")
        self.assertEqual(_header.numofblocks, 16)
        return

    def test_settings_parse(self):
        """ Test Settings block parsing """

        _valid_chunk = b''.join((b"\x11\x00\x78\x20\x99\xa0\x1a\x47",
                                 b"\xa9\xcd\x10\x02\x00\x78\x20\x99",
                                 b"\xa0\x1a\x47\xa9\xcd\x10\x00\x00"))
        _settings = Eagle.Settings.parse(_valid_chunk)

        self.assertNotEqual(_settings, None)

        self.assertEqual(_settings.copyno, 2)
        return

    def test_grid_parse(self):
        """ Test Grid block parsing """

        _valid_chunk = b''.join((b"\x12\x00\x02\xaa\x0f\x00\x00\x00",
                                 b"\x7f\xc2\xd9\xad\x65\x32\xd9\x3f",
                                 b"\x00\x00\x00\x00\x00\x00\x24\x40"))
        _grid = Eagle.Grid.parse(_valid_chunk)

        self.assertEqual(_grid.distance, 0.1)
        self.assertEqual(_grid.unitdist, "mil")
        self.assertEqual(_grid.unit, "mil")
        self.assertEqual(_grid.style, "dots")
        self.assertEqual(_grid.multiple, 15)
        self.assertEqual(_grid.display, False)
        self.assertEqual(_grid.altdistance, 0.01)
        self.assertEqual(_grid.altunitdist, "mil")
        self.assertEqual(_grid.altunit, "mil")
        return

    def test_layer_parse(self):
        """ Test Layer block parsing """

        _valid_chunk = b''.join((b"\x13\x00\x0f\x5b\x5b\x01\x02\x00",
                                 b"\x00\x00\x00\x00\x00\x00\x00\x4e",
                                 b"\x65\x74\x73\x00\x00\x00\x00\x00"))
        _layer = Eagle.Layer.parse(_valid_chunk)

        self.assertEqual(_layer.number, 91)
        self.assertEqual(_layer.name, "Nets")
        self.assertEqual(_layer.color, 2)
        self.assertEqual(_layer.fill, 1)
        self.assertEqual(_layer.visible, True)
        self.assertEqual(_layer.active, True)
        self.assertEqual(_layer.linkedsign, False)
        self.assertEqual(_layer.linkednumber, 91)
        return

    def test_attributeheader_parse(self):
        """ Test AttributeHeader block parsing """

        _valid_chunk = b''.join((b"\x14\x80\x01\x00\x00\x00\x00\x00",
                                 b"\x02\x00\x00\x00\x00\x00\x00\x00",
                                 b"\x00\x00\x00\x7f\x10\xfa\x0d\x09"))
        _attrheader = Eagle.AttributeHeader.parse(_valid_chunk)

        self.assertEqual(_attrheader.schematic, 'name_a')
        self.assertEqual(_attrheader.numofshapes, 1)
        self.assertEqual(_attrheader.numofattributes, 0) 
# probably no embedded "schematic" is possible
        return

    def test_library_parse(self):
        """ Test Library block parsing """

# embedded name
        _valid_chunk = b''.join((b"\x15\x80\x00\x00\x09\x00\x00\x00",
                                 b"\x16\x00\x00\x00\x24\x00\x00\x00",
                                 b"\x64\x69\x6f\x64\x65\x00\x00\x00"))
        _library = Eagle.Library.parse(_valid_chunk)

        self.assertEqual(_library.name, "diode")
        self.assertEqual(_library.numofdevsetblocks, 9)
        self.assertEqual(_library.numofsymbolblocks, 22)
        self.assertEqual(_library.numofpackageblocks, 36)

# TODO external name
        return

    def test_devicesetheader_parse(self):
        """ Test DeviceSetHeader block parsing """

# embedded name
        _valid_chunk = b''.join((b"\x17\x80\x00\x00\x08\x00\x00\x00",
                                 b"\x02\x00\x00\x00\x00\x00\x00\x00",
                                 b"\x64\x69\x6f\x64\x65\x00\x00\x00"))
        _devicesetheader = Eagle.DeviceSetHeader.parse(_valid_chunk)

        self.assertEqual(_devicesetheader.name, "diode")
        self.assertEqual(_devicesetheader.numofblocks, 8)
        self.assertEqual(_devicesetheader.numofshapesets, 2)

# TODO external name

        return

    def test_symbolheader_parse(self):
        """ Test SymbolHeader block parsing """

# embedded name
        _valid_chunk = b''.join((b"\x18\x80\x00\x00\x15\x00\x00\x00",
                                 b"\x02\x00\x00\x00\x00\x00\x00\x00",
                                 b"\x64\x69\x6f\x64\x65\x00\x00\x00"))
        _symbolheader = Eagle.SymbolHeader.parse(_valid_chunk)

        self.assertEqual(_symbolheader.name, "diode")
        self.assertEqual(_symbolheader.numofblocks, 21)
        self.assertEqual(_symbolheader.numofshapesets, 2)

# TODO external name

        return

    def test_packageheader_parse(self):
        """ Test PackageHeader block parsing """

# embedded name
        _valid_chunk = b''.join((b"\x19\x80\x00\x00\x23\x00\x00\x00",
                                 b"\x02\x00\x00\x00\x00\x00\x00\x00",
                                 b"\x64\x69\x6f\x64\x65\x00\x00\x00"))
        _packageheader = Eagle.PackageHeader.parse(_valid_chunk)

        self.assertEqual(_packageheader.name, "diode")
        self.assertEqual(_packageheader.numofblocks, 35)
        self.assertEqual(_packageheader.numofshapesets, 2)

# TODO external name

        return

    def test_symbol_parse(self):
        """ Test Symbol block parsing """

# embedded name
        _valid_chunk = b''.join((b"\x1d\x00\x0a\x00\xf4\xfe\x62\xff",
                                 b"\x2e\x01\xa8\x00\x00\x00\x00\x00",
                                 b"\x5a\x44\x00\x00\x00\x00\x00\x00"))
        _symbol = Eagle.Symbol.parse(_valid_chunk)

        self.assertEqual(_symbol.name, "ZD")
        self.assertEqual(_symbol.numofshapes, 10)
        self.assertEqual(_symbol.libid, 1)

# TODO external name
        return

    def test_package_parse(self):
        """ Test Package block parsing """

# TODO embedded name

# external name
        _valid_chunk = b''.join((b"\x1e\x00\x0d\x00\x7c\xfe\xb5\xff",
                                 b"\x84\x01\x97\x00\x00\x7f\x34\xe3",
                                 b"\x2a\x09\x7f\x2b\xe3\x2a\x09\x00"))
        _package = Eagle.Package.parse(_valid_chunk)

        self.assertEqual(_package.name, 'name_a')
        self.assertEqual(_package.desc, 'name_b')
        self.assertEqual(_package.numofshapes, 13)

        return

    def test_net_parse(self):
        """ Test Net block parsing """

# embedded name
        _valid_chunk = b''.join((b"\x1f\x80\x05\x00\xff\x7f\xff\x7f",
                                 b"\x00\x80\x00\x80\x01\x00\x00\x00",
                                 b"\x4e\x24\x31\x00\x00\x00\x00\x00"))
        _net = Eagle.Net.parse(_valid_chunk)

        self.assertEqual(_net.name, "N$1")
        self.assertEqual(_net.nclass, 1)
        self.assertEqual(_net.numofshapes, 5)

# TODO external name
        return

    def test_part_parse(self):
        """ Test Part block parsing """

# embedded name
        _valid_chunk = b''.join((b"\x38\x00\x02\x00\x01\x00\x02\x00",
                                 b"\x01\x01\x01\x49\x43\x39\x00\x00",
                                 b"\x44\x53\x33\x36\x36\x38\x00\x00"))
        _part = Eagle.Part.parse(_valid_chunk)

        self.assertEqual(_part.name, "IC9")
        self.assertEqual(_part.libid, 1)
        self.assertEqual(_part.devsetndx, 2)
        self.assertEqual(_part.symvar, 1)
        self.assertEqual(_part.techno, 1)
        self.assertEqual(_part.value, "DS3668")
        self.assertEqual(_part.numofshapes, 2)

# TODO external name
        return

    def test_deviceset_parse(self):
        """ Test DeviceSet block parsing """

# embedded names (2 of 3)
        _valid_chunk = b''.join((b"\x37\x80\x01\x00\x02\x00\x00\x84",
                                 b"\x44\x00\x00\x00\x00\x7f\xdd\x95",
                                 b"\x3c\x09\x31\x4e\x35\x33\x33\x33"))
        _devset = Eagle.DeviceSet.parse(_valid_chunk)

        self.assertEqual(_devset.name, "1N5333")
        self.assertEqual(_devset.prefix, "D")
        self.assertEqual(_devset.description, 'name_a')
        self.assertEqual(_devset.uservalue, False)
        self.assertEqual(_devset.numofshapes, 1)
        self.assertEqual(_devset.numofconnblocks, 2)

# embedded names (2 of 3)
        _valid_chunk = b''.join((b"\x37\x00\x01\x00\x02\x00\x01\x85",
                                 b"\x4A\x50\x00\x00\x00\x00\x00\x00",
                                 b"\x00\x00\x7f\xc1\xd3\xcf\x08\x00"))
        _devset = Eagle.DeviceSet.parse(_valid_chunk)

        self.assertEqual(_devset.name, 'name_b')
        self.assertEqual(_devset.prefix, "JP")
        self.assertEqual(_devset.description, "")
        self.assertEqual(_devset.uservalue, True)
        self.assertEqual(_devset.numofshapes, 1)
        self.assertEqual(_devset.numofconnblocks, 2)

        return

    def test_bus_parse(self):
        """ Test Bus block parsing """

# embedded name
        _valid_chunk = b''.join((b"\x3a\x80\x04\x00\x42\x24\x33\x00",
                                 b"\x00\x00\x00\x00\x00\x00\x00\x00",
                                 b"\x00\x00\x00\x00\x00\x00\x00\x00"))
        _bus = Eagle.Bus.parse(_valid_chunk)

        self.assertEqual(_bus.name, "B$3")
        self.assertEqual(_bus.numofshapes, 4)

# TODO external name
        return

    def test_shapeheader_parse(self):
        """ Test ShapeHeader block parsing """

        _valid_chunk = b''.join((b"\x1a\x00\x03\x00\x33\x01\x05\x0d",
                                 b"\x64\x07\x4b\x10\x04\x00\x00\x00",
                                 b"\x05\x00\x00\x00\x0e\x00\x00\x00"))
        _shapeheader = Eagle.ShapeHeader.parse(_valid_chunk)

        self.assertEqual(_shapeheader.numofshapes, 3)
        self.assertEqual(_shapeheader.numofpartblocks, 4)
        self.assertEqual(_shapeheader.numofbusblocks, 5)
        self.assertEqual(_shapeheader.numofnetblocks, 14)
        return

    def test_segment_parse(self):
        """ Test Segment block parsing """

        _valid_chunk = b''.join((b"\x20\x00\x04\x00\xcd\x05\x9b\x01",
                                 b"\xc8\x13\x0d\x10\x00\x00\x00\x00",
                                 b"\x00\x00\x00\x00\x00\x00\x00\x00"))
        _segment = Eagle.Segment.parse(_valid_chunk)

        self.assertEqual(_segment.numofshapes, 4)
        self.assertEqual(_segment.cumulativenumofshapes, 19)
        return

    def test_connectionheader_parse(self):
        """ Test ConnectionHeader block parsing """

        _valid_chunk = b''.join((b"\x36\x00\x01\x00\x04\x00\x00\x00",
                                 b"\x00\x00\x00\x00\x00\x00\x00\x00",
                                 b"\x00\x00\x00\x27\x27\x00\x00\x00"))
        _connheader = Eagle.ConnectionHeader.parse(_valid_chunk)

        self.assertEqual(_connheader.numofshapes, 1)
        self.assertEqual(_connheader.sindex, 4)
# TODO technology / attributes check, 'name'
        return

    def test_connections_parse(self):
        """ Test Connections block parsing """

        _valid_chunk = b''.join((b"\x3c\x00\x21\x22\x23\x24\x25\x26",
                                 b"\x27\x28\x29\x2a\x2b\x2c\x2d\x2e",
                                 b"\x2f\x30\x00\x00\x00\x00\x00\x00"))
        _connections = Eagle.Connections.parse(_valid_chunk)

        self.assertEqual(_connections.connections, [33, 34, 35, 36, 37, 38, 
                            39, 40, 41, 42, 43, 44, 45, 46, 47, 48])
        return

    def test_instance_parse(self):
        """ Test Instance block parsing """

        _valid_chunk = b''.join((b"\x30\x00\x02\x00\xd0\x54\x21\x00",
                                 b"\x40\x4d\x09\x00\xff\xff\x01\x00",
                                 b"\x00\x04\x01\x00\x00\x00\x00\x00"))
        _instance = Eagle.Instance.parse(_valid_chunk)

        self.assertEqual(_instance.numofshapes, 2)
        self.assertEqual(_instance.x, 218.44)
        self.assertEqual(_instance.y, 60.96)
        self.assertEqual(_instance.smashed, True)
        self.assertEqual(_instance.rotate, "R90")
        return

    def test_wire_parse(self):
        """ Test Wire block parsing """

        _valid_chunk = b''.join((b"\x22\x00\x00\x5b\xd8\x09\x05\x00",
                                 b"\x40\x4d\x09\x00\xd8\x09\x05\x00",
                                 b"\x60\xc0\x07\x00\xfa\x02\x03\x00"))
        _wire = Eagle.Wire.parse(_valid_chunk)

        self.assertEqual(_wire.x1, 33.02)
        self.assertEqual(_wire.y1, 60.96)
        self.assertEqual(_wire.x2, 33.02)
        self.assertEqual(_wire.y2, 50.8)
        self.assertEqual(_wire.style, "DashDot")
        self.assertEqual(_wire.width, 0.1524)
        self.assertEqual(_wire.layer, 91)
        return

    def test_hole_parse(self):
        """ Test Hole block parsing """

        _valid_chunk = b''.join((b"\x28\x00\x00\x00\x00\x00\x00\x00",
                                 b"\x90\xb4\x01\x00\x7e\x40\x00\x00",
                                 b"\x00\x00\x00\x00\x00\x00\x00\x00"))
        _hole = Eagle.Hole.parse(_valid_chunk)

        self.assertEqual(_hole.x, 0.)
        self.assertEqual(_hole.y, 11.176)
        self.assertEqual(_hole.drill, 3.302)
        return

    def test_smd_parse(self):
        """ Test SMD block parsing """

        _valid_chunk = b''.join((b"\x2b\x80\x00\x01\x96\xb5\xff\xff",
                                 b"\x0e\x78\x00\x00\xe6\x0c\xb0\x27",
                                 b"\x00\x00\x00\x31\x34\x00\x00\x00"))
        _smd = Eagle.SMD.parse(_valid_chunk)

        self.assertEqual(_smd.name, "14")
        self.assertEqual(_smd.x, -1.905)
        self.assertEqual(_smd.y, 3.0734)
        self.assertEqual(_smd.dx, 0.6604)
        self.assertEqual(_smd.dy, 2.032)
        self.assertEqual(_smd.layer, 1)
        return

    def test_arc_parse(self):
        """ Test Arc block parsing """

        _valid_chunk = b''.join((b"\x22\x00\x00\x5b\xc0\x80\x0f\xd8",
                                 b"\x48\xd0\x05\x70\xa0\x0d\x11\x11",
                                 b"\x40\x4d\x09\x00\xe8\x0b\x32\x81"))
        _arc = Eagle.Wire.parse(_valid_chunk)

        self.assertEqual(_arc.x1, 101.6)
        self.assertEqual(_arc.y1, 38.1)
        self.assertEqual(_arc.x2, 111.76)
        self.assertEqual(_arc.y2, 60.96)
        self.assertEqual(_arc.width, 0.6096)
        self.assertEqual(_arc.curve, 116.7552) # <---- probably wrong
        self.assertEqual(_arc.cap, "flat")
        self.assertEqual(_arc.direction, "counterclockwise")
        self.assertEqual(_arc.style, "ShortDash")
        self.assertEqual(_arc.layer, 91)
        return

    def test_circle_parse(self):
        """ Test Circle block parsing """

        _valid_chunk = b''.join((b"\x25\x00\x00\x5b\x48\x37\x12\x00",
                                 b"\xb0\x13\x0a\x00\xbd\x65\x01\x00",
                                 b"\xbd\x65\x01\x00\xf4\x05\x00\x00"))
        _circle = Eagle.Circle.parse(_valid_chunk)

        self.assertEqual(_circle.x, 119.38)
        self.assertEqual(_circle.y, 66.04)
        self.assertEqual(_circle.radius, 9.1581)
        self.assertEqual(_circle.width, 0.3048)
        self.assertEqual(_circle.layer, 91)
        return

    def test_rectangle_parse(self):
        """ Test Rectangle block parsing """

        _valid_chunk = b''.join((b"\x26\x80\x00\x5c\x50\x53\x02\x00",
                                 b"\xe8\x76\x0a\x00\x08\xea\x08\x00",
                                 b"\xa0\x0d\x11\x00\x00\x00\x00\x00"))
        _rectangle = Eagle.Rectangle.parse(_valid_chunk)

        self.assertEqual(_rectangle.x1, 15.24)
        self.assertEqual(_rectangle.y1, 68.58)
        self.assertEqual(_rectangle.x2, 58.42)
        self.assertEqual(_rectangle.y2, 111.76)
        self.assertEqual(_rectangle.rotate, None)
        self.assertEqual(_rectangle.layer, 92)
        return

    def test_pad_parse(self):
        """ Test Pad block parsing """

# embedded name
        _valid_chunk = b''.join((b"\x2a\x80\x01\x00\x70\xc6\x00\x00",
                                 b"\x00\x00\x00\x00\xd4\x15\x00\x00",
                                 b"\x00\x00\x00\x41\x00\x00\x00\x00"))
        _pad = Eagle.Pad.parse(_valid_chunk)

        self.assertEqual(_pad.name, "A")
        self.assertEqual(_pad.x, 5.08)
        self.assertEqual(_pad.y, 0.)
        self.assertEqual(_pad.drill, 0.5588)

# TODO external name
        return

    def test_pin_parse(self):
        """ Test Pin block parsing """

# embedded name
        _valid_chunk = b''.join((b"\x2c\x80\x00\x00\x38\x63\x00\x00",
                                 b"\x00\x00\x00\x00\x96\x00\x43\x00",
                                 b"\x00\x00\x00\x00\x00\x00\x00\x00"))
        _pin = Eagle.Pin.parse(_valid_chunk)

        self.assertEqual(_pin.name, "C")
        self.assertEqual(_pin.x, 2.54)
        self.assertEqual(_pin.y, 0.)

# TODO external name
        return

    def test_gate_parse(self):
        """ Test Gate block parsing """

# embedded name
        _valid_chunk = b''.join((b"\x2d\x00\x00\x00\xd0\x1f\xfc\xff",
                                 b"\x38\x63\x00\x00\x03\x00\x02\x00",
                                 b"\x50\x00\x00\x00\x00\x00\x00\x00"))
        _gate = Eagle.Gate.parse(_valid_chunk)

        self.assertEqual(_gate.name, "P")
        self.assertEqual(_gate.x, -25.4)
        self.assertEqual(_gate.y, 2.54)
        self.assertEqual(_gate.sindex, 2)
        self.assertEqual(_gate.addlevel, "request")

# TODO external name
        return

    def test_text_parse(self):
        """ Test Text block parsing """

# embedded text
        _valid_chunk = b''.join((b"\x31\x80\x02\x5b\x80\x9a\x12\x00",
                                 b"\xc0\x19\x03\x00\x02\x7e\x4c\x00",
                                 b"\x00\x08\x74\x65\x78\x74\x21\x00"))
        _text = Eagle.Text.parse(_valid_chunk)

        self.assertEqual(_text.value, "text!")
        self.assertEqual(_text.x, 121.92)
        self.assertEqual(_text.y, 20.32)
        self.assertEqual(_text.size, 6.4516)
        self.assertEqual(_text.rotate, "R180")
        self.assertEqual(_text.font, "fixed")
        self.assertEqual(_text.ratio, 19)
        self.assertEqual(_text.layer, 91)

# extarnal text
        _valid_chunk = b''.join((b"\x31\x80\x02\x5b\x18\xf0\x01\x00",
                                 b"\x18\x57\x0e\x00\x02\x7e\x4c\x00",
                                 b"\x00\x00\x7f\xf8\xcd\x35\x09\x00"))
        _text = Eagle.Text.parse(_valid_chunk)

        self.assertEqual(_text.value, 'name_a')
        self.assertEqual(_text.x, 12.7)
        self.assertEqual(_text.y, 93.98)
        self.assertEqual(_text.size, 6.4516)
        self.assertEqual(_text.rotate, None)
        self.assertEqual(_text.font, "fixed")
        self.assertEqual(_text.ratio, 19)
        self.assertEqual(_text.layer, 91)
        return
 
    def test_label_parse(self):
        """ Test Label block parsing """

        _valid_chunk = b''.join((b"\x33\x00\x02\x5f\xe0\xf3\x0d\x00",
                                 b"\xa0\xa6\x04\x00\xe0\x0f\x0c\x00",
                                 b"\x00\x1c\x01\x00\x00\x00\x00\x00"))
        _label = Eagle.Label.parse(_valid_chunk)

        self.assertEqual(_label.x, 91.44)
        self.assertEqual(_label.y, 30.48)
        self.assertEqual(_label.size, 0.8128)
        self.assertEqual(_label.rotate, "R270")
        self.assertEqual(_label.font, "fixed")
        self.assertEqual(_label.ratio, 3)
        self.assertEqual(_label.onoff, True)
        self.assertEqual(_label.mirrored, True)
        self.assertEqual(_label.layer, 95)
        return
 
    def test_attributenam_parse(self):
        """ Test AttributeNam block parsing """

        _valid_chunk = b''.join((b"\x34\x00\x01\x5f\xd6\xd0\x21\x00",
                                 b"\x14\xe2\x09\x00\xc4\x1d\x20\x00",
                                 b"\x00\x00\x00\x00\x00\x00\x00\x00"))
        _attrnam = Eagle.AttributeNam.parse(_valid_chunk)

        self.assertEqual(_attrnam.x, 221.615)
        self.assertEqual(_attrnam.y, 64.77)
        self.assertEqual(_attrnam.size, 1.524)
        self.assertEqual(_attrnam.layer, 95)
        return
 
    def test_attributeval_parse(self):
        """ Test AttributeVal block parsing """

        _valid_chunk = b''.join((b"\x35\x00\x01\x60\x3a\x9f\x21\x00",
                                 b"\xbe\x8d\x09\x00\xc4\x1d\x20\x00",
                                 b"\x00\x00\x00\x00\x00\x00\x00\x00"))
        _attrval = Eagle.AttributeVal.parse(_valid_chunk)

        self.assertEqual(_attrval.x, 220.345)
        self.assertEqual(_attrval.y, 62.611)
        self.assertEqual(_attrval.size, 1.524)
        self.assertEqual(_attrval.layer, 96)
        return
    
    def test_pinref_parse(self):
        """ Test PinRef block parsing """

        _valid_chunk = b''.join((b"\x3d\x00\x00\x00\x06\x00\x01\x00",
                                 b"\x07\x00\x00\x00\x00\x00\x00\x00",
                                 b"\x00\x00\x00\x00\x00\x00\x00\x00"))
        _pinref = Eagle.PinRef.parse(_valid_chunk)

        self.assertEqual(_pinref.partno, 6)
        self.assertEqual(_pinref.gateno, 1)
        self.assertEqual(_pinref.pinno, 7)
        return

    def test_attribute_parse(self):
        """ Test Attribute block parsing """

# embedded text
        _valid_chunk = b''.join((b"\x42\x80\x2a\x00\x00\x00\x00\x31",
                                 b"\x32\x33\x34\x35\x36\x37\x38\x39",
                                 b"\x30\x21\x71\x77\x21\x72\x74\x00"))
        _attr = Eagle.Attribute.parse(_valid_chunk)

        self.assertEqual(_attr.name, "1234567890")
        self.assertEqual(_attr.value, "qw!rt")

# external text
        _valid_chunk = b''.join((b"\x42\x80\x2a\x00\x00\x00\x00\x7f",
                                 b"\x88\x2b\x18\x09\x00\x00\x00\x00",
                                 b"\x00\x00\x00\x00\x00\x00\x00\x00"))
        _attr = Eagle.Attribute.parse(_valid_chunk)
        self.assertEqual(_attr.name, 'name_a')
        self.assertEqual(_attr.value, None)
        return

