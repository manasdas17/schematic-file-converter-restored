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
from upconvert.parser.eaglexml.generated_g import wire

import unittest

from functools import wraps
from os.path import dirname, join

TEST_DIR = join(dirname(__file__), '..', '..', '..', 'test', 'eaglexml')
EAGLE_SCALE = 10.0/9.0

_cache = {} # filename -> Design

def get_design(filename):
    if filename not in _cache:
        _cache[filename] = EagleXML().parse(join(TEST_DIR, filename))
    return _cache[filename]


def use_file(filename):
    """ Return a decorator which will parse an eaglexml file
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
        self.assertTrue('atmel:TINY15L:P'
                        in self.design.components.components)


    @use_file('E1AA60D5.sch')
    def test_component_symbols(self):
        """ A component should have 1 symbol. """
        self.assertEqual(
            len(self.get_component('atmel:TINY15L:P').symbols), 1)


    @use_file('D9CD1423.sch')
    def test_component_bodies(self):
        """ A deviceset with 2 gates should have 2 bodies. """
        cpt = self.get_component('Discrete:010-DUAL-N-MOSFET*:_1206-8')
        self.assertEqual(len(cpt.symbols[0].bodies), 2)


    @use_file('E1AA60D5.sch')
    def test_component_body_lines(self):
        """ The right component Lines are created on SBody objects. """
        cpt = self.get_component('atmel:TINY15L:P')
        lines = [s for s in cpt.symbols[0].bodies[0].shapes
                 if s.type == 'line']
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0].p1.x / EAGLE_SCALE, self.make_length("12.7"))
        self.assertEqual(lines[0].p1.y / EAGLE_SCALE, self.make_length("-10.16"))
        self.assertEqual(lines[0].p2.x / EAGLE_SCALE, self.make_length("-12.7"))
        self.assertEqual(lines[0].p2.y / EAGLE_SCALE, self.make_length("-10.16"))


    @use_file('E1AA60D5.sch')
    def test_component_body_rectangles(self):
        """ The right component Rectangles are created on SBody objects. """
        cpt = self.get_component('resistor:CPOL-EU:E2.5-6')
        rects = [s for s in cpt.symbols[0].bodies[0].shapes
                 if s.type == 'rectangle']
        self.assertEqual(len(rects), 1)
        self.assertEqual(rects[0].x / EAGLE_SCALE, self.make_length("-1.651"))
        self.assertEqual(rects[0].y / EAGLE_SCALE, self.make_length("-1.651"))
        self.assertEqual(rects[0].width / EAGLE_SCALE,
                         self.make_length("1.651") - self.make_length("-1.651"))
        self.assertEqual(rects[0].height / EAGLE_SCALE,
                         self.make_length("-1.651") - self.make_length("-2.54"))


    @use_file('S12G_Micro_20EVB_RevA.sch')
    def test_component_body_rectangles_rot(self):
        """ The right rotations are applied to Rectangles on SBody objects. """

        cpt = self.get_component('myLibrary:L:0805')
        rect = [s for s in cpt.symbols[0].bodies[0].shapes
                if s.type == 'rectangle'][0]
        self.assertEqual(rect.x / EAGLE_SCALE, self.make_length("-3.556"))
        self.assertEqual(rect.y / EAGLE_SCALE, self.make_length("1.016"))
        self.assertEqual(rect.width / EAGLE_SCALE,
                         self.make_length("3.556") - self.make_length("-3.556"))
        self.assertEqual(rect.height / EAGLE_SCALE,
                         self.make_length("1.016") - self.make_length("-1.016"))


    @use_file('450B679C.sch')
    def test_component_body_polygons(self):
        """ The right component Rectangles are created on SBody objects. """

        cpt = self.get_component('adafruit:LED:5MM')
        polys = [s for s in cpt.symbols[0].bodies[0].shapes
                 if s.type == 'polygon']
        self.assertEqual(len(polys), 2)
        self.assertEqual(len(polys[0].points), 3)
        self.assertEqual(polys[0].points[0].x / EAGLE_SCALE, self.make_length("-3.429"))
        self.assertEqual(polys[0].points[0].y / EAGLE_SCALE, self.make_length("-2.159"))


    @use_file('D9CD1423.sch')
    def test_component_body_circles(self):
        """ The right component Circles are created on SBody objects. """

        cpt = self.get_component('CONNECTER:HEADER_1X10:DD')
        circs = [s for s in cpt.symbols[0].bodies[0].shapes
                 if s.type == 'circle']
        self.assertEqual(len(circs), 9)
        self.assertEqual(circs[0].x, self.make_length("0"))
        self.assertEqual(circs[0].y / EAGLE_SCALE, self.make_length("8.89"))
        self.assertEqual(circs[0].radius / EAGLE_SCALE, self.make_length("1.016"))
        self.assertEqual(circs[0].attributes['eaglexml_width'], "0.254")


    @use_file('E1AA60D5.sch')
    def test_component_body_labels(self):
        """ The right component Labels are created on SBody objects. """
        cpt = self.get_component('con-berg:PN87520:')
        labels = [s for s in cpt.symbols[0].bodies[0].shapes
                  if s.type == 'label']
        self.assertEqual(len(labels), 1)
        self.assertEqual(labels[0].x / EAGLE_SCALE, self.make_length("5.08"))
        self.assertEqual(labels[0].y / EAGLE_SCALE, self.make_length("-2.54"))
        self.assertEqual(labels[0].text, 'USB')
        self.assertEqual(labels[0]._rotation, 1.5)


    @use_file('msp430_f249_ctk.sch')
    def test_component_body_labels_mirrored(self):
        """ The right component Labels are created on SBody objects. """
        cpt = self.get_component('TI_MSP430_v16:F24[X/10]---PM64:')
        labels = [s for s in cpt.symbols[0].bodies[0].shapes
                  if s.type == 'label' and s.text == 'P4.6/TB6']
        self.assertEqual(len(labels), 1)
        self.assertEqual(labels[0].x / EAGLE_SCALE, self.make_length("36.83"))
        self.assertEqual(labels[0].y / EAGLE_SCALE, self.make_length("0.0"))
        self.assertEqual(labels[0]._rotation, 0.0)
        self.assertEqual(labels[0].align, 'right')


    @use_file('E1AA60D5.sch')
    def test_component_body_pins(self):
        """ The right component Pins are created on SBody objects. """
        cpt = self.get_component('atmel:TINY15L:P')
        pins = cpt.symbols[0].bodies[0].pins
        self.assertEqual(len(pins), 8)
        self.assertEqual(pins[0].p1.x / EAGLE_SCALE, 90)
        self.assertEqual(pins[0].p1.y / EAGLE_SCALE, 18)
        self.assertEqual(pins[0].p2.x / EAGLE_SCALE, self.make_length("17.78"))
        self.assertEqual(pins[0].p2.y / EAGLE_SCALE, self.make_length("2.54"))
        self.assertEqual(pins[0].label.text, '(ADC3)PB4')
        self.assertEqual(pins[0].label.x / EAGLE_SCALE, 85.0)
        self.assertEqual(pins[0].label.y / EAGLE_SCALE, 15.0)
        self.assertEqual(pins[0].label._rotation, 0.0)
        self.assertEqual([p.pin_number for p in pins],
                         ['2', '3', '1', '7', '6', '5', '8', '4'])
        self.assertEqual([p.label.text for p in pins],
                         ['(ADC3)PB4', '(ADC2)PB3', '(ADC0)PB5',
                          '(ADC1)PB2', '(OCP)PB1', '(AREF)PB0',
                          'VCC', 'GND'])
        cpt = self.get_component('diode:ZENER-DIODE:DO35Z10')
        pins = cpt.symbols[0].bodies[0].pins
        self.assertEqual(pins[0].label, None)
        self.assertEqual([p.pin_number for p in pins], ['A', 'C'])


    @use_file('Shock Controller.sch')
    def test_component_body_pin_duplicate_names(self):
        """ Duplicate pin names on different gates are de-duplicated
        with pin numbers. """

        cpt = self.get_component('con-molex:22-?-04:27-2041')
        pin_numbers = [p.pin_number for b in cpt.symbols[0].bodies for p in b.pins]
        self.assertEqual(pin_numbers, ['1', '2', '3', '4'])


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
    def test_component_instance_refdes(self):
        """ Component instance refdes is correct. """
        inst = self.get_instance('GND3')
        self.assertEqual(inst.get_attribute('refdes'), 'GND3')


    @use_file('E1AA60D5.sch')
    def test_component_instance_position(self):
        """ Component instance position is correct. """
        inst = self.get_instance('GND3')
        self.assertEqual(len(inst.symbol_attributes), 1)
        self.assertEqual(inst.symbol_attributes[0].x / EAGLE_SCALE, self.make_length("116.84"))
        self.assertEqual(inst.symbol_attributes[0].y / EAGLE_SCALE, self.make_length("55.88"))


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
        self.assertEqual(anns[0].x / EAGLE_SCALE, -27)
        self.assertEqual(anns[0].y / EAGLE_SCALE, 11)
        self.assertEqual(anns[1].value, '68')
        self.assertEqual(anns[1].x / EAGLE_SCALE, -27)
        self.assertEqual(anns[1].y / EAGLE_SCALE, -23)


    @use_file('WiFi.sch')
    def test_component_instance_annotations_case_insensitive(self):
        """ Component instance annotations are correct. """
        inst = self.get_instance('U$1')
        anns = inst.symbol_attributes[0].annotations
        self.assertEqual(len(anns), 1)
        self.assertEqual(anns[0].value, 'U$1')


    @use_file('pcb_switch_switch.sch')
    def test_component_instance_annotations_multi_gates(self):
        """ Component instance annotations with multiple gates are correct. """
        inst = self.get_instance('X1')
        values = []
        for attr in inst.symbol_attributes:
            for ann in attr.annotations:
                values.append(ann.value)
        self.assertEqual(set(values), set(['SW', 'X1-1', 'X1-2']))


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


    @use_file('S12G_Micro_20EVB_RevA.sch')
    def test_net_points_connected_rot(self):
        """ The right net points are connected for a rotated part. """
        net = [n for n in self.design.nets if n.net_id == 'GND'][0]
        pt = net.points[self.make_point_name("0", "15.24")]
        self.assertEqual(sorted(pt.connected_points),
                         [self.make_point_name("0", "7.62")])


    @use_file('S12G_Micro_20EVB_RevA.sch')
    def test_net_points_connected_flip_rot(self):
        """ The right net points are connected for a flipped and rotated part. """
        net = [n for n in self.design.nets if n.net_id == 'PT1'][0]
        pt = net.points[self.make_point_name("162.56", "33.02")]
        self.assertEqual(sorted(pt.connected_points),
                         [self.make_point_name("162.56", "30.48")])


    @use_file('E1AA60D5.sch')
    def test_net_points_connected_components(self):
        """ The right net points are connected to the right components. """
        net = [n for n in self.design.nets if n.net_id == 'N$7'][0]
        pt = net.points[self.make_point_name("76.2", "68.58")]
        self.assertEqual(len(pt.connected_components), 1)
        self.assertEqual(pt.connected_components[0].instance_id, 'IC1')
        self.assertEqual(pt.connected_components[0].pin_number, '7')


    @use_file('D9CD1423.sch')
    def test_smashed_annotations(self):
        """ The right annotations are created for smashed components. """
        inst = self.get_instance('U1')
        symattr = inst.symbol_attributes[0]
        self.assertEqual(len(symattr.annotations), 2)
        self.assertEqual(symattr.annotations[0].value, 'U1')
        self.assertEqual(symattr.annotations[0].x / EAGLE_SCALE, self.parser.make_length("22.86"))
        self.assertEqual(symattr.annotations[0].y / EAGLE_SCALE, self.parser.make_length("52.07"))
        self.assertEqual(symattr.annotations[0].rotation, 0.0)
        self.assertEqual(symattr.annotations[1].value, 'ATMEGA328AU')
        self.assertEqual(symattr.annotations[1].x / EAGLE_SCALE, self.parser.make_length("22.86"))
        self.assertEqual(symattr.annotations[1].y / EAGLE_SCALE, self.parser.make_length("43.18"))
        self.assertEqual(symattr.annotations[1].rotation, 0.0)


    @use_file('msp430_f249_ctk.sch')
    def test_smashed_annotations_offset(self):
        """ The right annotations are created for smashed components. """
        inst = self.get_instance('SV3')
        symattr = inst.symbol_attributes[0]
        self.assertEqual(len(symattr.annotations), 2)
        self.assertEqual(symattr.annotations[0].value, '14 PIN JTAG')
        self.assertEqual(symattr.annotations[0].x / EAGLE_SCALE,
                         self.parser.make_length("110.49") - self.parser.make_length('118.11'))
        self.assertEqual(symattr.annotations[0].y / EAGLE_SCALE,
                         self.parser.make_length("127") - self.parser.make_length('139.7'))
        self.assertEqual(symattr.annotations[0].rotation, 0.0)
        self.assertEqual(symattr.annotations[1].value, 'SV3')
        self.assertEqual(symattr.annotations[1].x / EAGLE_SCALE,
                         self.parser.make_length("114.3") - self.parser.make_length('118.11'))
        self.assertEqual(symattr.annotations[1].y / EAGLE_SCALE,
                         self.parser.make_length("150.622") - self.parser.make_length('139.7'))
        self.assertEqual(symattr.annotations[1].rotation, 0.0)


    def test_arc_shape(self):
        """ Arc shapes are generated correctly. """
        parser = EagleXML()

        w = wire(x1='25.4', y1='0', x2='-25.4', y2='0', curve='180')
        s = parser.make_shape_for_wire(w)
        self.assertEqual(s.x, 0)
        self.assertEqual(s.y, 0)
        self.assertEqual(s.start_angle, 0.0)
        self.assertEqual(s.end_angle, 1.0)
        self.assertEqual(s.radius, parser.make_length('25.4'))

        w = wire(x1='-25.4', y1='0', x2='25.4', y2='0', curve='180')
        s = parser.make_shape_for_wire(w)
        self.assertEqual(s.x, 0)
        self.assertEqual(s.y, 0)
        self.assertEqual(s.start_angle, 1.0)
        self.assertEqual(s.end_angle, 0.0)
        self.assertEqual(s.radius, parser.make_length('25.4'))

        w = wire(x1='25.4', y1='0', x2='-25.4', y2='0', curve='90')
        s = parser.make_shape_for_wire(w)
        self.assertEqual(s.x, 0)
        self.assertEqual(s.y, self.make_length('-25.4'))
        self.assertEqual(s.start_angle, 0.25)
        self.assertEqual(s.end_angle, 0.75)
        self.assertEqual(s.radius, parser.make_length('35.915'))

        w = wire(x1='25.4', y1='0', x2='-25.4', y2='0', curve='-90')
        s = parser.make_shape_for_wire(w)
        self.assertEqual(s.x, 0)
        self.assertEqual(s.y, self.make_length('25.4'))
        self.assertEqual(s.start_angle, 1.25)
        self.assertEqual(s.end_angle, 1.75)
        self.assertEqual(s.radius, parser.make_length('35.915'))

        w = wire(x1='0', y1='25.4', x2='0', y2='-25.4', curve='90')
        s = parser.make_shape_for_wire(w)
        self.assertEqual(s.x, self.make_length('25.4'))
        self.assertEqual(s.y, 0)
        self.assertEqual(s.start_angle, 0.75)
        self.assertEqual(s.end_angle, 1.25)
        self.assertEqual(s.radius, parser.make_length('35.915'))

        w = wire(x1='0', y1='25.4', x2='0', y2='-25.4', curve='-180')
        s = parser.make_shape_for_wire(w)
        self.assertEqual(s.x, 0)
        self.assertEqual(s.y, 0)
        self.assertEqual(s.start_angle, 1.5)
        self.assertEqual(s.end_angle, 0.5)
        self.assertEqual(s.radius, parser.make_length('25.4'))

        w = wire(x1='25.4', y1='0', x2='-25.4', y2='0', curve='270')
        s = parser.make_shape_for_wire(w)
        self.assertEqual(s.x, 0)
        self.assertEqual(s.y, self.make_length('25.4'))
        self.assertEqual(s.start_angle, 1.75)
        self.assertEqual(s.end_angle, 1.25)
        self.assertEqual(s.radius, parser.make_length('35.915'))

        w = wire(x1='25.4', y1='0', x2='-25.4', y2='0', curve='-270')
        s = parser.make_shape_for_wire(w)
        self.assertEqual(s.x, 0)
        self.assertEqual(s.y, self.make_length('-25.4'))
        self.assertEqual(s.start_angle, 0.75)
        self.assertEqual(s.end_angle, 0.25)
        self.assertEqual(s.radius, parser.make_length('35.915'))


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
