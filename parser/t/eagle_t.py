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

    def test_Header_parse(self):
        """ Test Header block parsing """
        
        _valid_chunk = b''.join((b"\x10\x00\x0c\x00\x10\x00\x00\x00", 
                                 b"\x05\x0b\x04\x3c\x00\x2e\x00\x00",
                                 b"\x00\x00\x00\x00\x00\x00\x00\x00"))
        _header = Eagle.Header.parse(_valid_chunk)

        self.assertNotEqual(_header, None)

        self.assertEqual(_header.version, "5.11")
        self.assertEqual(_header.numofblocks, 16)
        return

    def test_Settings_parse(self):
        """ Test Settings block parsing """

        _valid_chunk = b''.join((b"\x11\x00\x78\x20\x99\xa0\x1a\x47",
                                 b"\xa9\xcd\x10\x02\x00\x78\x20\x99",
                                 b"\xa0\x1a\x47\xa9\xcd\x10\x00\x00"))
        _settings = Eagle.Settings.parse(_valid_chunk)

        self.assertNotEqual(_settings, None)

        self.assertEqual(_settings.copyno, 2)
        return

    def test_Grid_parse(self):
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

    def test_Layer_parse(self):
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

    def test_AttributeHeader_parse(self):
        """ Test AttributeHeader block parsing """

        _valid_chunk = b''.join((b"\x14\x80\x01\x00\x00\x00\x00\x00",
                                 b"\x02\x00\x00\x00\x00\x00\x00\x00",
                                 b"\x00\x00\x00\x7f\x10\xfa\x0d\x09"))
        _attrheader = Eagle.AttributeHeader.parse(_valid_chunk)

        self.assertEqual(_attrheader.numofshapes, 1)
        self.assertEqual(_attrheader.numofattributes, 0) 
        return

    def test_ShapeHeader_parse(self):
        """ Test ShapeHeader block parsing """

        _valid_chunk = b''.join((b"\x1a\x00\x01\x00\x53\x02\x76\x0a",
                                 b"\xeb\x08\x0e\x11\x00\x00\x00\x00",
                                 b"\x00\x00\x00\x00\x00\x00\x00\x00"))
        _shapeheader = Eagle.ShapeHeader.parse(_valid_chunk)

        self.assertEqual(_shapeheader.numofshapes, 1)
        return

    def test_Rectangle_parse(self):
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

