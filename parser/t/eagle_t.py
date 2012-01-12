#!/usr/bin/python
# encoding: utf-8
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
        pass

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
        return

    def test_attributeheader_parse(self):
        """ Test AttributeHeader block parsing """

        _valid_chunk = b''.join((b"\x14\x80\x01\x00\x00\x00\x00\x00",
                                 b"\x02\x00\x00\x00\x00\x00\x00\x00",
                                 b"\x00\x00\x00\x7f\x10\xfa\x0d\x09"))
        _attrheader = Eagle.AttributeHeader.parse(_valid_chunk)

        self.assertEqual(_attrheader.numofshapes, 1)
        self.assertEqual(_attrheader.numofattributes, 0) 
        return

    def test_shapeheader_parse(self):
        """ Test ShapeHeader block parsing """

        _valid_chunk = b''.join((b"\x1a\x00\x01\x00\x53\x02\x76\x0a",
                                 b"\xeb\x08\x0e\x11\x00\x00\x00\x00",
                                 b"\x00\x00\x00\x00\x00\x00\x00\x00"))
        _shapeheader = Eagle.ShapeHeader.parse(_valid_chunk)

        self.assertEqual(_shapeheader.numofshapes, 1)
        return

    def test_net_parse(self):
        """ Test Net block parsing """

        _valid_chunk = b''.join((b"\x1f\x80\x05\x00\xff\x7f\xff\x7f",
                                 b"\x00\x80\x00\x80\x01\x00\x00\x00",
                                 b"\x4e\x24\x31\x00\x00\x00\x00\x00"))
        _net = Eagle.Net.parse(_valid_chunk)

        self.assertEqual(_net.name, "N$1")
        self.assertEqual(_net.nclass, 1)
        self.assertEqual(_net.numofblocks, 5)
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

    def test_wire_parse(self):
        """ Test Wire block parsing """

        _valid_chunk = b''.join((b"\x22\x00\x00\x5b\xd8\x09\x05\x00",
                                 b"\x40\x4d\x09\x00\xd8\x09\x05\x00",
                                 b"\x60\xc0\x07\x00\xfa\x02\x00\x00"))
        _wire = Eagle.Wire.parse(_valid_chunk)

        self.assertEqual(_wire.x1, 33.02)
        self.assertEqual(_wire.y1, 60.96)
        self.assertEqual(_wire.x2, 33.02)
        self.assertEqual(_wire.y2, 50.8)
        self.assertEqual(_wire.width, 0.1524)
        self.assertEqual(_wire.layer, 91)
        return

    def test_arc_parse(self):
        """ Test Arc block parsing """

        _valid_chunk = b''.join((b"\x22\x00\x00\x5b\xc0\x80\x0f\xd8",
                                 b"\x48\xd0\x05\x70\xa0\x0d\x11\x11",
                                 b"\x40\x4d\x09\x00\xe8\x0b\x30\x81"))
        _arc = Eagle.Wire.parse(_valid_chunk)

        self.assertEqual(_arc.x1, 101.6)
        self.assertEqual(_arc.y1, 38.1)
        self.assertEqual(_arc.x2, 111.76)
        self.assertEqual(_arc.y2, 60.96)
        self.assertEqual(_arc.width, 0.6096)
        self.assertEqual(_arc.curve, 116.7552) # <---- probably wrong
        self.assertEqual(_arc.cap, "flat")
        self.assertEqual(_arc.direction, "counterclockwise")
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

    def test_text_parse_embedded(self):
        """ Test Text block parsing """

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
        return
 
    def test_text_parse_external(self):
        """ Test Text block parsing (value is not in block) """

        _valid_chunk = b''.join((b"\x31\x80\x02\x5b\x18\xf0\x01\x00",
                                 b"\x18\x57\x0e\x00\x02\x7e\x4c\x00",
                                 b"\x00\x00\x7f\xf8\xcd\x35\x09\x00"))
        _text = Eagle.Text.parse(_valid_chunk)

        self.assertEqual(_text.value, None)
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
 
    def test_bus_parse(self):
        """ Test Bus block parsing """

        _valid_chunk = b''.join((b"\x3a\x80\x04\x00\x42\x24\x33\x00",
                                 b"\x00\x00\x00\x00\x00\x00\x00\x00",
                                 b"\x00\x00\x00\x00\x00\x00\x00\x00"))
        _bus = Eagle.Bus.parse(_valid_chunk)

        self.assertEqual(_bus.name, "B$3")
        self.assertEqual(_bus.numofblocks, 4)
        return

    def test_attribute_parse_embedded(self):
        """ Test Attribute block parsing """

        _valid_chunk = b''.join((b"\x42\x80\x2a\x00\x00\x00\x00\x31",
                                 b"\x32\x33\x34\x35\x36\x37\x38\x39",
                                 b"\x30\x21\x71\x77\x21\x72\x74\x00"))
        _attr = Eagle.Attribute.parse(_valid_chunk)

        self.assertEqual(_attr.name, "1234567890")
        self.assertEqual(_attr.value, "qw!rt")
        return

    def test_attribute_parse_external(self):
        """ Test Attribute block parsing (value is not in block) """

        _valid_chunk = b''.join((b"\x42\x80\x2a\x00\x00\x00\x00\x7f",
                                 b"\x88\x2b\x18\x09\x00\x00\x00\x00",
                                 b"\x00\x00\x00\x00\x00\x00\x00\x00"))
        _attr = Eagle.Attribute.parse(_valid_chunk)
        self.assertEqual(_attr.name, None)
        self.assertEqual(_attr.value, None)
        return



