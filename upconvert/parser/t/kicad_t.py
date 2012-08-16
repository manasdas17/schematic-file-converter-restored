# encoding: utf-8
#pylint: disable=R0904
""" The kicad parser test class """

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


from upconvert.parser.kicad import KiCAD, ComponentParser, MULT
from upconvert.writer.openjson import JSON as JSONWriter

import unittest

from functools import wraps
from os.path import dirname, join
from os import devnull

TEST_DIR = join(dirname(__file__), '..', '..', '..', 'test', 'kicad')


_cache = {} # filename -> Design

def get_design(filename):
    if filename not in _cache:
        _cache[filename] = KiCAD().parse(join(TEST_DIR, filename))
    return _cache[filename]


def use_file(filename):
    """ Return a decorator which will parse a kicad file
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


class KiCADTests(unittest.TestCase):
    """ The tests of the kicad parser """

    @use_file('test/test.sch')
    def test_design_attributes(self):
        """ All the design attributes are correct """

        anns = self.design.design_attributes.annotations
        self.assertTrue(len(anns), 1)
        self.assertEqual(anns[0].value, "I'm a net label")


    @use_file('test/test.sch')
    def test_points(self):
        """
        Test that all the points are present and have the right
        positions and connected points and components.
        """

        self.assertEqual(len(self.design.nets[0].points), 3)
        self.assertEqual(set(self.design.nets[0].points),
                         set(['2700a-6450',
                              '2700a-3950',
                              '3250a-3950']))


    @use_file('test/test.sch')
    def test_nets(self):
        """
        Test that all the right nets are present.
        """

        self.assertEqual(len(self.design.nets), 5)
        self.assertEqual(self.design.nets[0].net_id, '2700a-3950')


    @use_file('arduino/Arduino-Ethernet.sch')
    def test_nets_no_dups(self):
        """
        Test that no duplicate nets are present.
        """

        self.assertEqual(len(self.design.nets), 83)
        self.assertEqual(len(self.design.nets),
                         len(set(n.net_id for n in self.design.nets)))


    @use_file('test/test.sch')
    def test_components(self):
        """
        Test that all the right components are present with the
        correct values.
        """

        self.assertEqual(len(self.design.components.components), 5)
        self.assertEqual(set([c.name for c in self.design.components.components.values()]),
                         set(['74LS00',
                             'ATMEGA8-P',
                             'NSL-32',
                             'LP3966',
                             'LAA110']))

        cpt = self.design.components.components['74LS00']

        self.assertEqual(len(cpt.symbols), 2)
        self.assertEqual(len(cpt.symbols[0].bodies), 4)
        self.assertEqual(len(cpt.symbols[0].bodies[0].pins), 5)


    @use_file('test/test.sch')
    def test_component_instances(self):
        """
        Test that the component instances were loaded correctly.
        """

        self.assertEqual(len(self.design.component_instances), 5)

        inst = self.design.component_instances[0]

        self.assertEqual(inst.instance_id, 'U3')
        self.assertEqual(inst.library_id, 'LAA110')
        self.assertEqual(len(inst.symbol_attributes), 1)
        self.assertEqual(inst.symbol_attributes[0].rotation, 1.5)
        self.assertEqual(inst.symbol_attributes[0].x, 1650 * MULT)
        self.assertEqual(inst.symbol_attributes[0].y, -3400 * MULT)


    @use_file('arduino/Arduino-Ethernet.sch')
    def test_connected_components(self):
        """
        The components are connected correctly.
        """

        ccomps = set()
        for net in self.design.nets:
            for point in net.points.itervalues():
                for cc in point.connected_components:
                    ccomps.add((cc.instance_id, cc.pin_number))

        self.assertTrue(('R1', '2') in ccomps)
        self.assertTrue(('P1', '1') in ccomps)
        self.assertTrue(('P1', '2') in ccomps)
        self.assertTrue(('P1', '3') in ccomps)
        self.assertTrue(('P1', '4') in ccomps)
        self.assertTrue(('P1', '5') in ccomps)
        self.assertTrue(('P1', '6') in ccomps)
        self.assertTrue(('D1', '1') in ccomps)
        self.assertTrue(('D1', '2') in ccomps)


    def test_bad_x_line_rotation(self):
        """
        Test that a bad rotation in an X line raises a ValueError.
        """

        parser = ComponentParser('DEF 74LS00 U 0 30 Y Y 4 F N')
        line = 'X GND 7 -200 -200 0 E 40 40 0 0 W N'
        self.assertRaises(ValueError, parser.parse_x_line, line.split())


    @use_file('jtag_schematic.sch')
    def test_annotation_spaces(self):
        """
        Annotations with spaces are handled correctly.
        """

        inst = [i for i in self.design.component_instances
                if i.library_id == 'CONN_4X2'][0]
        self.assertEqual(inst.symbol_attributes[0].annotations[1].value,
                         'MAPLE JTAG')


    @use_file('ps2toserial.sch')
    def test_utf8_annotations(self):
        """
        Annotations with special chars are handled correctly.
        """

        JSONWriter().write(self.design, devnull)


    def test_t_line_no_alignment(self):
        """
        T lines with no alignment are handled correctly.
        """

        parser = ComponentParser('DEF 74LS00 U 0 30 Y Y 4 F N')
        shape = parser.parse_t_line(['T', '0', '150', '-235', '50',
                                     '0', '4', '0', 'Common'])
        self.assertEqual(shape.type, 'label')
        self.assertEqual(shape.text, 'Common')
        self.assertEqual(shape.align, 'left')


    def test_parse_field(self):
        """
        A field description with an embedded quote is parsed correctly.
        """

        line = 'F 0 "Reference Designs ARE PROVIDED "AS IS"" H 1150 11950 120 0000 L B'
        ann = KiCAD().parse_field(0, 0, line)
        self.assertEqual(ann.value, 'Reference Designs ARE PROVIDED "AS IS"')
        self.assertEqual(ann.x, 1150)
        self.assertEqual(ann.y, -11950)
        self.assertEqual(ann.rotation, 0)
