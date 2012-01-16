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


from core.shape import Circle, Rectangle, Shape
from parser.fritzing import Fritzing, ComponentParser
from parser.fritzing import make_x, make_y, make_length, get_pin
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
        self.assertEqual(make_x('17.23'), 17)


    def test_make_y(self):
        """ make_y converts y values correctly """
        self.assertEqual(make_y('17.23'), -17)


    def test_make_length(self):
        """ make_length converts other numeric values correctly """
        self.assertEqual(make_length('17.23'), 17)


    def test_get_x(self):
        """ get_x retrieves x values correctly """
        elem = {'x': '4.62', 'x1': '10.2'}
        self.assertEqual(get_x(elem), 5)
        self.assertEqual(get_x(elem, 'x1'), 10)
        self.assertEqual(get_x(elem, 'x2'), 0)


    def test_get_y(self):
        """ get_y retrieves y values correctly """
        elem = {'y': '4.62', 'y1': '10.2'}
        self.assertEqual(get_y(elem), -5)
        self.assertEqual(get_y(elem, 'y1'), -10)
        self.assertEqual(get_y(elem, 'y2'), 0)


    def test_get_length(self):
        """ get_length retrieves other numeric values correctly """
        elem = {'r': '4.62', 'r1': '10.2'}
        self.assertEqual(get_length(elem, 'r'), 5)
        self.assertEqual(get_length(elem, 'r1'), 10)
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

        symb = diode.symbols[0]
        self.assertEqual(len(symb.bodies), 1)

        body = symb.bodies[0]
        self.assertEqual(len(body.shapes), 8)
        self.assertEqual(len(body.pins), 2)

        shape = body.shapes[0]
        self.assertEqual(shape.type, 'rectangle')
        self.assertEqual(shape.x, 12)
        self.assertEqual(shape.y, -1)
        self.assertEqual(shape.width, 0)
        self.assertEqual(shape.height, 0)

        pin = body.pins[0]
        self.assertEqual(pin.pin_number, '0')
        self.assertEqual(pin.p1.x, 12)
        self.assertEqual(pin.p1.y, -1)
        self.assertEqual(pin.p2.x, pin.p1.x)
        self.assertEqual(pin.p2.y, pin.p1.y)


    def test_component_instances(self):
        """ The parser loads ComponentInstances correctly """

        design = self.load_file('components.fz')
        self.assertEqual(len(design.component_instances), 2)
        self.assertEqual(
            set([i.instance_id for i in design.component_instances]),
            set(['D1', 'R1']))

        inst = [i for i in design.component_instances
                if i.instance_id == 'D1'][0]
        self.assertEqual(inst.library_id, "4a300fed-afa9-4e78-a643-ec209be7e3b8")
        self.assertEqual(inst.symbol_index, 0)
        self.assertEqual(len(inst.symbol_attributes), 1)

        symbattr = inst.symbol_attributes[0]
        self.assertEqual(symbattr.x, 293)
        self.assertEqual(symbattr.y, -147)
        self.assertEqual(symbattr.rotation, 1.5)


    def test_get_pin(self):
        """ The get_pin function returns the correct Pins """

        shape = Rectangle(0, 0, 4, 8)
        pin = get_pin(shape)
        self.assertEqual(pin.p1.x, 2)
        self.assertEqual(pin.p1.y, 4)
        self.assertEqual(pin.p2.x, pin.p1.x)
        self.assertEqual(pin.p2.y, pin.p1.y)

        shape = Circle(0, 0, 4)
        pin = get_pin(shape)
        self.assertEqual(pin.p1.x, 0)
        self.assertEqual(pin.p1.y, 0)
        self.assertEqual(pin.p2.x, pin.p1.x)
        self.assertEqual(pin.p2.y, pin.p1.y)

        self.assertEqual(get_pin(Shape()), None)


    def test_missing_layers(self):
        """The component parser handles a missing schematic layer """

        parser = ComponentParser(None, None)

        class FakeTree(object):
            """A fake tree """

            def find(self, path):
                assert path == 'views/schematicView/layers'
                return None

        parser.parse_svg(None, FakeTree(), None)


    def test_missing_p(self):
        """The component parser handles a connector missing a p element """

        parser = ComponentParser(None, None)

        class FakeConn(object):
            """A fake connector"""

            def __init__(self, missing):
                self.missing = missing

            def find(self, path):
                assert path == 'views/schematicView/p'
                if self.missing:
                    return None
                else:
                    return {'terminalId': 'tid'}

            def get(self, key):
                assert key == 'id'
                return 'id'

        class FakeTree(object):
            """A fake tree """

            def findall(self, path):
                assert path == 'connectors/connector'
                return [FakeConn(missing=True), FakeConn(missing=False)]

        terminals = parser.parse_terminals(FakeTree())

        self.assertEqual(terminals, {'id':'tid'})


    def test_nets(self):
        """ The parser loads Nets correctly """

        design = self.load_file('nets.fz')
        self.assertEqual(len(design.nets), 2)
        self.assertEqual(set(len(net.points) for net in design.nets),
                         set([8, 5]))

        net = [n for n in design.nets if len(n.points) == 5][0]

        p1 = net.points['143a33']
        self.assertEqual(p1.connected_points, ['143a44'])
        self.assertEqual(len(p1.connected_components), 1)
        self.assertEqual(p1.connected_components[0].instance_id, 'L1')
        self.assertEqual(p1.connected_components[0].pin_number, '1')
