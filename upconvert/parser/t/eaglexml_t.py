#!/usr/bin/python
# encoding: utf-8
#pylint: disable=R0904
""" The eaglexml parser test class """

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

from upconvert.parser.eaglexml import EagleXML

import unittest

from functools import wraps
from os.path import dirname, join

TEST_DIR = join(dirname(__file__), '..', '..', '..', 'test', 'eaglexml')


_cache = {} # filename -> Design

def get_design(filename):
    if filename not in _cache:
        parser = EagleXML()
        _cache[filename] = parser.parse(join(TEST_DIR, filename))
    return _cache[filename]


def use_file(filename):
    """ Return a decorator which will parse a gerber file
    before running the test. """

    def decorator(test_method):
        """ Add params to decorator function. """

        @wraps(test_method)
        def wrapper(self):
            """ Parse file then run test. """
            self.design = get_design(filename)
            test_method(self)

        return wrapper

    return decorator


class EagleXMLTests(unittest.TestCase):
    """ The tests of the eagle-xml parser """

    def test_create_new_eaglexml_parser(self):
        """ Test creating an empty parser. """
        self.assertNotEqual(EagleXML(), None)


    @use_file('E1AA60D5.sch')
    def test_library_components(self):
        """ The right components are created. """
        self.assertTrue('atmel:TINY15L:P' in self.design.components.components)


    @use_file('E1AA60D5.sch')
    def test_component_symbols(self):
        """ The right component symbols are created. """
        self.assertEqual(len(self.get_component('atmel:TINY15L:P').symbols), 1)


    @use_file('E1AA60D5.sch')
    def test_component_body_lines(self):
        """ The right component Lines are created on Body objects. """
        cpt = self.get_component('atmel:TINY15L:P')
        lines = [s for s in cpt.symbols[0].bodies[0].shapes
                 if s.type == 'line']
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0].p1.x, 45)
        self.assertEqual(lines[0].p1.y, -36)
        self.assertEqual(lines[0].p2.x, -45)
        self.assertEqual(lines[0].p2.y, -36)


    @use_file('E1AA60D5.sch')
    def test_component_body_rectangles(self):
        """ The right component Rectangles are created on Body objects. """
        cpt = self.get_component('resistor:CPOL-EU:E2.5-6')
        rects = [s for s in cpt.symbols[0].bodies[0].shapes
                 if s.type == 'rectangle']
        self.assertEqual(len(rects), 1)
        self.assertEqual(rects[0].x, -6)
        self.assertEqual(rects[0].y, -6)
        self.assertEqual(rects[0].width, 12)
        self.assertEqual(rects[0].height, 3)


    @use_file('E1AA60D5.sch')
    def test_component_body_labels(self):
        """ The right component Labels are created on Body objects. """
        cpt = self.get_component('con-berg:PN87520:')
        labels = [s for s in cpt.symbols[0].bodies[0].shapes
                  if s.type == 'label']
        self.assertEqual(len(labels), 1)
        self.assertEqual(labels[0].x, 18)
        self.assertEqual(labels[0].y, -9)
        self.assertEqual(labels[0].text, 'USB')
        self.assertEqual(labels[0].rotation, 1.5)


    @use_file('E1AA60D5.sch')
    def test_component_body_pins(self):
        """ The right component Pins are created on Body objects. """
        cpt = self.get_component('atmel:TINY15L:P')
        pins = cpt.symbols[0].bodies[0].pins
        self.assertEqual(len(pins), 8)
        self.assertEqual(pins[0].p1.x, 45)
        self.assertEqual(pins[0].p1.y, 9)
        self.assertEqual(pins[0].p2.x, 63)
        self.assertEqual(pins[0].p2.y, 9)


    @use_file('E1AA60D5.sch')
    def test_component_instances(self):
        """ The right component instances are created. """
        self.assertEqual(
            set(ci.instance_id for ci in self.design.component_instances),
            set(('Q1', 'X2', 'C2', 'IC1', 'X1', 'R4', 'R1', 'R2', 'R3', 'GND3',
                 'GND2', 'GND1', 'GND7', 'GND6', 'GND5', 'GND4','C1', 'P+2',
                 'P+3', 'P+1', 'P+6', 'P+4','P+5', 'D2', 'D1')))


    @use_file('E1AA60D5.sch')
    def test_component_instance_rotation(self):
        """ Component instance rotation is correct. """
        inst = self.get_instance('GND3')
        self.assertEqual(inst.symbol_attributes[0].rotation, 0)
        inst = self.get_instance('R2')
        self.assertEqual(inst.symbol_attributes[0].rotation, 1.5)


    @use_file('E1AA60D5.sch')
    def test_component_instance_position(self):
        """ Component instance position is correct. """
        inst = self.get_instance('GND3')
        self.assertEqual(inst.symbol_attributes[0].x, 414)
        self.assertEqual(inst.symbol_attributes[0].y, 198)


    @use_file('E1AA60D5.sch')
    def test_nets(self):
        """ The right nets are created. """
        self.assertEqual(set(n.net_id for n in self.design.nets),
                         set(['VCC', 'GND', 'N$1', 'N$2', 'N$3',
                              'N$4', 'N$5', 'N$6', 'N$7']))


    @use_file('E1AA60D5.sch')
    def test_net_points(self):
        """ The right net points are created. """
        net = [n for n in self.design.nets if n.net_id == 'GND'][0]
        self.assertEqual(set(net.points),
                         set(('423a90', '423a81', '414a216', '414a207',
                              '135a225', '432a90', '432a216', '135a216',
                              '144a225')))


    def get_component(self, library_id):
        """ Return the component given its id. """
        return self.design.components.components[library_id]


    def get_instance(self, instance_id):
        """ Return the instance given its id. """
        return [ci for ci in self.design.component_instances
                if ci.instance_id == instance_id][0]
