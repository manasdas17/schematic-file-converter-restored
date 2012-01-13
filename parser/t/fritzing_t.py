# encoding: utf-8
""" The fritzing parser test class """

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


from parser.fritzing import Fritzing
from parser.fritzing import make_x, make_y, make_length
from parser.fritzing import get_x, get_y, get_length
from unittest import TestCase

from os.path import dirname, join

TEST_DIR = join(dirname(__file__), '..', '..', 'test', 'fritzing')


class FritzingTests(TestCase):
    """ The tests of the fritzing parser """

    def load_file(self, basename):
        """ Load a fritzing test file with the given basename """
        parser = Fritzing()
        return parser.parse(join(TEST_DIR, basename))

    def test_create_new_fritzing_parser(self):
        """ Test creating an empty parser. """
        parser = Fritzing()
        assert parser != None

    def test_make_x(self):
        """ make_x converts x values correctly """
        self.assertEqual(make_x('17.23'), 172)

    def test_make_y(self):
        """ make_y converts y values correctly """
        self.assertEqual(make_y('17.23'), -172)

    def test_make_length(self):
        """ make_length converts other numeric values correctly """
        self.assertEqual(make_length('17.23'), 172)

    def test_get_x(self):
        """ get_x retrieves x values correctly """
        elem = {'x': '4.42', 'x1': '10.2'}
        self.assertEqual(get_x(elem), 44)
        self.assertEqual(get_x(elem, 'x1'), 102)
        self.assertEqual(get_x(elem, 'x2'), 0)

    def test_get_y(self):
        """ get_y retrieves y values correctly """
        elem = {'y': '4.42', 'y1': '10.2'}
        self.assertEqual(get_y(elem), -44)
        self.assertEqual(get_y(elem, 'y1'), -102)
        self.assertEqual(get_y(elem, 'y2'), 0)

    def test_get_length(self):
        """ get_length retrieves other numeric values correctly """
        elem = {'r': '4.42', 'r1': '10.2'}
        self.assertEqual(get_length(elem, 'r'), 44)
        self.assertEqual(get_length(elem, 'r1'), 102)
        self.assertEqual(get_length(elem, 'r2'), 0)

    def test_components(self):
        """ The parser loads Components correctly """
        design = self.load_file('components.fz')
        self.assertEqual(len(design.components.components), 2)
        cpts = design.components.components
        self.assertEqual(set(cpts),
                         set(['ResistorModuleID',
                              '4a300fed-afa9-4e78-a643-ec209be7e3b8']))
        diode = cpts['4a300fed-afa9-4e78-a643-ec209be7e3b8']
        self.assertEqual(diode.name, '4a300fed-afa9-4e78-a643-ec209be7e3b8')
        self.assertEqual(diode.attributes, {'_prefix': 'D'})
        self.assertEqual(len(diode.symbols), 1)

