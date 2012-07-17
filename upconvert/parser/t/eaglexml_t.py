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
        _cache[filename] = EagleXML().parse(join(TEST_DIR, filename))
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

    def setUp(self):
        self.parser = EagleXML()


    def test_create_new_eaglexml_parser(self):
        """ Test creating an empty parser. """
        self.assertNotEqual(self.parser, None)


    def test_make_length(self):
        """ Lengths are converted correctly. """
        parser = EagleXML()
        self.assertEqual(parser.make_length("0"), 0)
        self.assertEqual(parser.make_length("254"), int(900 * 2.0))


    @use_file('E1AA60D5.sch')
    def test_library_components(self):
        """ A deviceset should have a matching component. """
        self.assertTrue('atmel:TINY15L:logical'
                        in self.design.components.components)


    @use_file('E1AA60D5.sch')
    def test_component_symbols(self):
        """ A logical component should have 1 symbol. """
        self.assertEqual(
            len(self.get_component('atmel:TINY15L:logical').symbols), 1)


    @use_file('D9CD1423.sch')
    def test_component_bodies(self):
        """ A deviceset with 2 gates should have 2 bodies. """
        cpt = self.get_component('Discrete:010-DUAL-N-MOSFET*:logical')
        self.assertEqual(len(cpt.symbols[0].bodies), 2)


    @use_file('E1AA60D5.sch')
    def test_component_body_lines(self):
        """ The right component Lines are created on Body objects. """
        cpt = self.get_component('atmel:TINY15L:logical')
        lines = [s for s in cpt.symbols[0].bodies[0].shapes
                 if s.type == 'line']
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0].p1.x, self.make_length("12.7"))
        self.assertEqual(lines[0].p1.y, self.make_length("-10.16"))
        self.assertEqual(lines[0].p2.x, self.make_length("-12.7"))
        self.assertEqual(lines[0].p2.y, self.make_length("-10.16"))


    @use_file('E1AA60D5.sch')
    def test_component_body_rectangles(self):
        """ The right component Rectangles are created on Body objects. """
        cpt = self.get_component('resistor:CPOL-EU:logical')
        rects = [s for s in cpt.symbols[0].bodies[0].shapes
                 if s.type == 'rectangle']
        self.assertEqual(len(rects), 1)
        self.assertEqual(rects[0].x, self.make_length("-1.651"))
        self.assertEqual(rects[0].y, self.make_length("-1.651"))
        self.assertEqual(rects[0].width,
                         self.make_length("1.651") - self.make_length("-1.651"))
        self.assertEqual(rects[0].height,
                         self.make_length("-1.651") - self.make_length("-2.54"))


    @use_file('450B679C.sch')
    def test_component_body_polygons(self):
        """ The right component Rectangles are created on Body objects. """

        cpt = self.get_component('adafruit:LED:logical')
        polys = [s for s in cpt.symbols[0].bodies[0].shapes
                 if s.type == 'polygon']
        self.assertEqual(len(polys), 2)
        self.assertEqual(len(polys[0].points), 3)
        self.assertEqual(polys[0].points[0].x, self.make_length("-3.429"))
        self.assertEqual(polys[0].points[0].y, self.make_length("-2.159"))


    @use_file('D9CD1423.sch')
    def test_component_body_circles(self):
        """ The right component Circles are created on Body objects. """

        cpt = self.get_component('CONNECTER:HEADER_1X10:logical')
        circs = [s for s in cpt.symbols[0].bodies[0].shapes
                 if s.type == 'circle']
        self.assertEqual(len(circs), 9)
        self.assertEqual(circs[0].x, self.make_length("0"))
        self.assertEqual(circs[0].y, self.make_length("8.89"))
        self.assertEqual(circs[0].radius, self.make_length("1.016"))
        self.assertEqual(circs[0].attributes['eaglexml_width'], "0.254")


    @use_file('E1AA60D5.sch')
    def test_component_body_labels(self):
        """ The right component Labels are created on Body objects. """
        cpt = self.get_component('con-berg:PN87520:logical')
        labels = [s for s in cpt.symbols[0].bodies[0].shapes
                  if s.type == 'label']
        self.assertEqual(len(labels), 1)
        self.assertEqual(labels[0].x, self.make_length("5.08"))
        self.assertEqual(labels[0].y, self.make_length("-2.54"))
        self.assertEqual(labels[0].text, 'USB')
        self.assertEqual(labels[0].rotation, 1.5)


    @use_file('E1AA60D5.sch')
    def test_component_body_pins(self):
        """ The right component Pins are created on Body objects. """
        cpt = self.get_component('atmel:TINY15L:logical')
        pins = cpt.symbols[0].bodies[0].pins
        self.assertEqual(len(pins), 8)
        self.assertEqual(pins[0].p1.x, 90)
        self.assertEqual(pins[0].p1.y, 18)
        self.assertEqual(pins[0].p2.x, self.make_length("17.78"))
        self.assertEqual(pins[0].p2.y, self.make_length("2.54"))
        self.assertEqual(pins[0].label.text, '(ADC3)PB4')
        self.assertEqual(pins[0].label.x, 0)
        self.assertEqual(pins[0].label.y, 18)
        self.assertEqual(pins[0].label.rotation, 0.0)

        cpt = self.get_component('diode:ZENER-DIODE:logical')
        pins = cpt.symbols[0].bodies[0].pins
        self.assertEqual(pins[0].label, None)


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
        self.assertEqual(len(inst.symbol_attributes), 1)
        self.assertEqual(inst.symbol_attributes[0].x, self.make_length("116.84"))
        self.assertEqual(inst.symbol_attributes[0].y, self.make_length("55.88"))


    @use_file('E1AA60D5.sch')
    def test_component_instance_value(self):
        """ Component instance value is correct. """
        inst = self.get_instance('R2')
        self.assertEqual(inst.attributes['value'], '68')


    @use_file('E1AA60D5.sch')
    def test_component_instance_annotations(self):
        """ Component instance annotations are correct. """
        inst = self.get_instance('R2')
        anns = inst.symbol_attributes[0].annotations
        self.assertEqual(len(anns), 2)
        self.assertEqual(anns[0].value, 'R2')
        self.assertEqual(anns[0].x, -27)
        self.assertEqual(anns[0].y, 11)
        self.assertEqual(anns[1].value, '68')
        self.assertEqual(anns[1].x, -27)
        self.assertEqual(anns[1].y, -23)


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
        self.assertEqual(len(net.points), 13)
        self.assertTrue(self.make_point_name("40.64", "63.5") in net.points)


    @use_file('E1AA60D5.sch')
    def test_net_points_connected(self):
        """ The right net points are connected. """
        net = [n for n in self.design.nets if n.net_id == 'N$7'][0]
        pt = net.points[self.make_point_name("83.82", "68.58")]
        self.assertEqual(sorted(pt.connected_points),
                         [self.make_point_name("76.2", "68.58"),
                          self.make_point_name("83.82", "48.26")])


    @use_file('E1AA60D5.sch')
    def test_net_points_connected_components(self):
        """ The right net points are connected to the right components. """
        net = [n for n in self.design.nets if n.net_id == 'N$7'][0]
        pt = net.points[self.make_point_name("76.2", "68.58")]
        self.assertEqual(len(pt.connected_components), 1)
        self.assertEqual(pt.connected_components[0].instance_id, 'IC1')
        self.assertEqual(pt.connected_components[0].pin_number, '(ADC1)PB2')


    @use_file('D9CD1423.sch')
    def test_smashed_annotations(self):
        """ The right annotations are created for smashed components. """
        inst = self.get_instance('U1')
        symattr = inst.symbol_attributes[0]
        self.assertEqual(len(symattr.annotations), 2)
        self.assertEqual(symattr.annotations[0].value, 'U1')
        self.assertEqual(symattr.annotations[0].x, self.parser.make_length("22.86"))
        self.assertEqual(symattr.annotations[0].y, self.parser.make_length("52.07"))
        self.assertEqual(symattr.annotations[0].rotation, 0.0)
        self.assertEqual(symattr.annotations[1].value, 'ATMEGA328AU')
        self.assertEqual(symattr.annotations[1].x, self.parser.make_length("22.86"))
        self.assertEqual(symattr.annotations[1].y, self.parser.make_length("43.18"))
        self.assertEqual(symattr.annotations[1].rotation, 0.0)


    def get_component(self, library_id):
        """ Return the component given its id. """
        return self.design.components.components[library_id]


    def get_instance(self, instance_id):
        """ Return the instance given its id. """
        return [ci for ci in self.design.component_instances
                if ci.instance_id == instance_id][0]


    def make_length(self, length):
        """ Return a length from the parser. """
        return self.parser.make_length(length)


    def make_point_name(self, x, y):
        """ Return a point name given an eaglexml point. """
        return '%sa%s' % (self.make_length(x), self.make_length(y))
