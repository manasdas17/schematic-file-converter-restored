# encoding: utf-8
#pylint: disable=R0904
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
from parser.fritzing import Fritzing, ComponentParser, PathParser
from parser.fritzing import make_x, make_y, make_length, get_pin
from parser.fritzing import get_x, get_y, get_length
from unittest import TestCase

from os.path import dirname, join

TEST_DIR = join(dirname(__file__), '..', '..', 'test', 'fritzing')


class FakeElem(dict):
    """ A fake xml element. """

    def __init__(self, tag, **kw):
        self.tag = tag
        super(FakeElem, self).__init__(**kw)


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
        self.assertEqual(shape.x, 15)
        self.assertEqual(shape.y, -1)
        self.assertEqual(shape.width, 0)
        self.assertEqual(shape.height, 0)

        pin = body.pins[0]
        self.assertEqual(pin.pin_number, '0')
        self.assertEqual(pin.p1.x, 15)
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
        self.assertEqual(symbattr.x, 288)
        self.assertEqual(symbattr.y, -159)
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
                """ Return None for the layers """
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
                """ Return None or a fixed element for the p element """
                assert path == 'views/schematicView/p'
                if self.missing:
                    return None
                else:
                    return {'terminalId': 'tid'}

            def get(self, key):
                """ Return 'id' for the 'id' attribute """
                assert key == 'id'
                return 'id'

        class FakeTree(object):
            """A fake tree """

            def findall(self, path):
                """ Return two fake connectors, one missing
                a p element and one not """
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


    def test_parse_circle(self):
        """ We parse svg circles correctly. """

        parser = ComponentParser(None, None)
        elem = FakeElem('circle', cx='72', cy='144', r='216')
        shapes = parser.parse_shapes(elem)
        self.assertEqual(len(shapes), 1)
        self.assertEqual(shapes[0].type, 'circle')
        self.assertEqual(shapes[0].x, 90)
        self.assertEqual(shapes[0].y, -180)
        self.assertEqual(shapes[0].radius, 270)


    def test_parse_rect(self):
        """ We parse svg rectangles correctly. """

        parser = ComponentParser(None, None)
        elem = FakeElem('rect', x='0', y='720',
                        width='72', height='144')
        shapes = parser.parse_shapes(elem)
        self.assertEqual(len(shapes), 1)
        self.assertEqual(shapes[0].type, 'rectangle')
        self.assertEqual(shapes[0].x, 0)
        self.assertEqual(shapes[0].y, -900)
        self.assertEqual(shapes[0].width, 90)
        self.assertEqual(shapes[0].height, 180)


    def test_path_num_re(self):
        """ The path point regex correctly matches numbers in a path. """

        num = '1'
        match = PathParser.num_re.match(num)
        self.assertEqual(match.group(0), num)
        self.assertEqual(match.group(1), '1')

        num = ' 1 '
        match = PathParser.num_re.match(num)
        self.assertEqual(match.group(0), num)
        self.assertEqual(match.group(1), '1')

        num = ' 1.2 '
        match = PathParser.num_re.match(num)
        self.assertEqual(match.group(0), num)
        self.assertEqual(match.group(1), '1.2')

        num = ' 1.2 , '
        match = PathParser.num_re.match(num)
        self.assertEqual(match.group(0), num)
        self.assertEqual(match.group(1), '1.2')

        num = ' 10.22 , '
        match = PathParser.num_re.match(num)
        self.assertEqual(match.group(0), num)
        self.assertEqual(match.group(1), '10.22')

        num = '10.22 , 1'
        match = PathParser.num_re.match(num)
        self.assertEqual(match.group(0), num[:-1])
        self.assertEqual(match.group(1), '10.22')

        num = '10.22 , M'
        match = PathParser.num_re.match(num)
        self.assertEqual(match.group(0), num[:-1])
        self.assertEqual(match.group(1), '10.22')

        num = '-1'
        match = PathParser.num_re.match(num)
        self.assertEqual(match.group(0), num)
        self.assertEqual(match.group(1), '-1')


    def test_parse_nums(self):
        """ Numbers are parsed from svg paths. """

        pp = PathParser(None)

        self.assertEqual(pp.parse_nums(''), ([], ''))
        self.assertEqual(pp.parse_nums('1'), ([1.0], ''))
        self.assertEqual(pp.parse_nums('1.2 3.4'),
                         ([1.2, 3.4], ''))
        self.assertEqual(pp.parse_nums('1.2,3.4  5.6'),
                         ([1.2, 3.4, 5.6], ''))
        self.assertEqual(pp.parse_nums('1.2,3.4  5.6L12'),
                         ([1.2, 3.4, 5.6], 'L12'))
        self.assertEqual(pp.parse_nums('1.2,3.4  5.6 L12'),
                         ([1.2, 3.4, 5.6], 'L12'))


    def test_parse_points(self):
        """ Sequences of points are parsed from svg paths. """

        pp = PathParser(None)

        self.assertEqual(pp.parse_points(''), ([], ''))
        self.assertEqual(pp.parse_points('1 2 3.3 4.4 M'),
                         ([(1, 2), (3.3, 4.4)], 'M'))


    def test_get_path_point(self):
        """ get_path_point returns correct points """

        pp = PathParser(None)

        pp.cur_point = (1, 2)

        self.assertEqual(pp.get_path_point((3, 4), False), (3, 4))
        self.assertEqual(pp.get_path_point((3, 4), True), (4, 6))


    def test_parse_m(self):
        """ moveto segments are parsed correctly """

        pp = PathParser(None)

        rest = pp.parse_m('72 720 144 288 0 0 rest', False)

        self.assertEqual(rest, 'rest')
        self.assertEqual(pp.start_point, (72.0, 720.0))
        self.assertEqual(pp.cur_point, (0, 0))
        self.assertEqual(len(pp.shapes), 2)
        self.assertEqual(pp.shapes[0].type, 'line')
        self.assertEqual(pp.shapes[0].p1.x, 90)
        self.assertEqual(pp.shapes[0].p1.y, -900)
        self.assertEqual(pp.shapes[0].p2.x, 180)
        self.assertEqual(pp.shapes[0].p2.y, -360)
        self.assertEqual(pp.shapes[1].type, 'line')
        self.assertEqual(pp.shapes[1].p1.x, 180)
        self.assertEqual(pp.shapes[1].p1.y, -360)
        self.assertEqual(pp.shapes[1].p2.x, 0)
        self.assertEqual(pp.shapes[1].p2.y, 0)


        pp = PathParser(None)

        rest = pp.parse_m('72 720 144 288 0 0 rest', True)

        self.assertEqual(rest, 'rest')
        self.assertEqual(pp.start_point, (72.0, 720.0))
        self.assertEqual(pp.cur_point, (216.0, 1008.0))
        self.assertEqual(len(pp.shapes), 2)
        self.assertEqual(pp.shapes[0].type, 'line')
        self.assertEqual(pp.shapes[0].p1.x, 90)
        self.assertEqual(pp.shapes[0].p1.y, -900)
        self.assertEqual(pp.shapes[0].p2.x, 270)
        self.assertEqual(pp.shapes[0].p2.y, -1260)
        self.assertEqual(pp.shapes[1].type, 'line')
        self.assertEqual(pp.shapes[1].p1.x, 270)
        self.assertEqual(pp.shapes[1].p1.y, -1260)
        self.assertEqual(pp.shapes[1].p2.x, 270)
        self.assertEqual(pp.shapes[1].p2.y, -1260)


    def test_parse_z(self):
        """ closepath segments are parsed correctly """

        pp = PathParser(None)

        pp.cur_point = (72, 144)
        pp.start_point = (-72, -144)
        rest = pp.parse_z('rest', False)

        self.assertEqual(rest, 'rest')
        self.assertEqual(pp.start_point, (-72, -144))
        self.assertEqual(pp.cur_point, (-72, -144))
        self.assertEqual(len(pp.shapes), 1)
        self.assertEqual(pp.shapes[0].type, 'line')
        self.assertEqual(pp.shapes[0].p1.x, 90)
        self.assertEqual(pp.shapes[0].p1.y, -180)
        self.assertEqual(pp.shapes[0].p2.x, -90)
        self.assertEqual(pp.shapes[0].p2.y, 180)


    def test_parse_l(self):
        """ lineto segments are parsed correctly """

        pp = PathParser(None)

        rest = pp.parse_l('72 720 144 288 0 0 rest', False)

        self.assertEqual(rest, 'rest')
        self.assertEqual(pp.start_point, (0.0, 0.0))
        self.assertEqual(pp.cur_point, (0, 0))
        self.assertEqual(len(pp.shapes), 3)
        self.assertEqual(pp.shapes[0].type, 'line')
        self.assertEqual(pp.shapes[0].p1.x, 0)
        self.assertEqual(pp.shapes[0].p1.y, 0)
        self.assertEqual(pp.shapes[0].p2.x, 90)
        self.assertEqual(pp.shapes[0].p2.y, -900)
        self.assertEqual(pp.shapes[1].type, 'line')
        self.assertEqual(pp.shapes[1].p1.x, 90)
        self.assertEqual(pp.shapes[1].p1.y, -900)
        self.assertEqual(pp.shapes[1].p2.x, 180)
        self.assertEqual(pp.shapes[1].p2.y, -360)
        self.assertEqual(pp.shapes[2].type, 'line')
        self.assertEqual(pp.shapes[2].p1.x, 180)
        self.assertEqual(pp.shapes[2].p1.y, -360)
        self.assertEqual(pp.shapes[2].p2.x, 0)
        self.assertEqual(pp.shapes[2].p2.y, 0)


        pp = PathParser(None)

        rest = pp.parse_l('72 720 144 288 0 0 rest', True)

        self.assertEqual(rest, 'rest')
        self.assertEqual(pp.start_point, (0.0, 0.0))
        self.assertEqual(pp.cur_point, (216.0, 1008.0))
        self.assertEqual(len(pp.shapes), 3)
        self.assertEqual(pp.shapes[0].type, 'line')
        self.assertEqual(pp.shapes[0].p1.x, 0)
        self.assertEqual(pp.shapes[0].p1.y, 0)
        self.assertEqual(pp.shapes[0].p2.x, 90)
        self.assertEqual(pp.shapes[0].p2.y, -900)
        self.assertEqual(pp.shapes[1].type, 'line')
        self.assertEqual(pp.shapes[1].p1.x, 90)
        self.assertEqual(pp.shapes[1].p1.y, -900)
        self.assertEqual(pp.shapes[1].p2.x, 270)
        self.assertEqual(pp.shapes[1].p2.y, -1260)
        self.assertEqual(pp.shapes[2].type, 'line')
        self.assertEqual(pp.shapes[2].p1.x, 270)
        self.assertEqual(pp.shapes[2].p1.y, -1260)
        self.assertEqual(pp.shapes[2].p2.x, 270)
        self.assertEqual(pp.shapes[2].p2.y, -1260)


    def test_parse_h(self):
        """ horizontal lineto segments are parsed correctly """

        pp = PathParser(None)

        rest = pp.parse_h('72 144 288 rest', False)

        self.assertEqual(rest, 'rest')
        self.assertEqual(pp.start_point, (0.0, 0.0))
        self.assertEqual(pp.cur_point, (288, 0))
        self.assertEqual(len(pp.shapes), 3)
        self.assertEqual(pp.shapes[0].type, 'line')
        self.assertEqual(pp.shapes[0].p1.x, 0)
        self.assertEqual(pp.shapes[0].p1.y, 0)
        self.assertEqual(pp.shapes[0].p2.x, 90)
        self.assertEqual(pp.shapes[0].p2.y, 0)
        self.assertEqual(pp.shapes[1].type, 'line')
        self.assertEqual(pp.shapes[1].p1.x, 90)
        self.assertEqual(pp.shapes[1].p1.y, 0)
        self.assertEqual(pp.shapes[1].p2.x, 180)
        self.assertEqual(pp.shapes[1].p2.y, 0)
        self.assertEqual(pp.shapes[2].type, 'line')
        self.assertEqual(pp.shapes[2].p1.x, 180)
        self.assertEqual(pp.shapes[2].p1.y, 0)
        self.assertEqual(pp.shapes[2].p2.x, 360)
        self.assertEqual(pp.shapes[2].p2.y, 0)


        pp = PathParser(None)

        rest = pp.parse_h('72 72 72 rest', True)

        self.assertEqual(rest, 'rest')
        self.assertEqual(pp.start_point, (0.0, 0.0))
        self.assertEqual(pp.cur_point, (216.0, 0.0))
        self.assertEqual(len(pp.shapes), 3)
        self.assertEqual(pp.shapes[0].type, 'line')
        self.assertEqual(pp.shapes[0].p1.x, 0)
        self.assertEqual(pp.shapes[0].p1.y, 0)
        self.assertEqual(pp.shapes[0].p2.x, 90)
        self.assertEqual(pp.shapes[0].p2.y, 0)
        self.assertEqual(pp.shapes[1].type, 'line')
        self.assertEqual(pp.shapes[1].p1.x, 90)
        self.assertEqual(pp.shapes[1].p1.y, 0)
        self.assertEqual(pp.shapes[1].p2.x, 180)
        self.assertEqual(pp.shapes[1].p2.y, 0)
        self.assertEqual(pp.shapes[2].type, 'line')
        self.assertEqual(pp.shapes[2].p1.x, 180)
        self.assertEqual(pp.shapes[2].p1.y, 0)
        self.assertEqual(pp.shapes[2].p2.x, 270)
        self.assertEqual(pp.shapes[2].p2.y, 0)


    def test_parse_v(self):
        """ vertical lineto segments are parsed correctly """

        pp = PathParser(None)

        rest = pp.parse_v('72 144 288 rest', False)

        self.assertEqual(rest, 'rest')
        self.assertEqual(pp.start_point, (0.0, 0.0))
        self.assertEqual(pp.cur_point, (0, 288))
        self.assertEqual(len(pp.shapes), 3)
        self.assertEqual(pp.shapes[0].type, 'line')
        self.assertEqual(pp.shapes[0].p1.x, 0)
        self.assertEqual(pp.shapes[0].p1.y, 0)
        self.assertEqual(pp.shapes[0].p2.x, 0)
        self.assertEqual(pp.shapes[0].p2.y, -90)
        self.assertEqual(pp.shapes[1].type, 'line')
        self.assertEqual(pp.shapes[1].p1.x, 0)
        self.assertEqual(pp.shapes[1].p1.y, -90)
        self.assertEqual(pp.shapes[1].p2.x, 0)
        self.assertEqual(pp.shapes[1].p2.y, -180)
        self.assertEqual(pp.shapes[2].type, 'line')
        self.assertEqual(pp.shapes[2].p1.x, 0)
        self.assertEqual(pp.shapes[2].p1.y, -180)
        self.assertEqual(pp.shapes[2].p2.x, 0)
        self.assertEqual(pp.shapes[2].p2.y, -360)


        pp = PathParser(None)

        rest = pp.parse_v('72 72 72 rest', True)

        self.assertEqual(rest, 'rest')
        self.assertEqual(pp.start_point, (0.0, 0.0))
        self.assertEqual(pp.cur_point, (0.0, 216.0))
        self.assertEqual(len(pp.shapes), 3)
        self.assertEqual(pp.shapes[0].type, 'line')
        self.assertEqual(pp.shapes[0].p1.x, 0)
        self.assertEqual(pp.shapes[0].p1.y, 0)
        self.assertEqual(pp.shapes[0].p2.x, 0)
        self.assertEqual(pp.shapes[0].p2.y, -90)
        self.assertEqual(pp.shapes[1].type, 'line')
        self.assertEqual(pp.shapes[1].p1.x, 0)
        self.assertEqual(pp.shapes[1].p1.y, -90)
        self.assertEqual(pp.shapes[1].p2.x, 0)
        self.assertEqual(pp.shapes[1].p2.y, -180)
        self.assertEqual(pp.shapes[2].type, 'line')
        self.assertEqual(pp.shapes[2].p1.x, 0)
        self.assertEqual(pp.shapes[2].p1.y, -180)
        self.assertEqual(pp.shapes[2].p2.x, 0)
        self.assertEqual(pp.shapes[2].p2.y, -270)


    def test_parse_c(self):
        """ cubic bezier segments are parsed correctly """

        pp = PathParser(None)

        rest = pp.parse_c('6 12 12 6 18 24 -6 -12 -12 -24 -36 -42 rest', False)
        self.assertEqual(rest, 'rest')
        self.assertEqual(pp.start_point, (0.0, 0.0))
        self.assertEqual(pp.cur_point, (-36.0, -42.0))
        self.assertEqual(len(pp.shapes), 2)
        self.assertEqual(pp.shapes[0].type, 'bezier')
        self.assertEqual(pp.shapes[0].p1.x, 0)
        self.assertEqual(pp.shapes[0].p1.y, 0)
        self.assertEqual(pp.shapes[0].control1.x, 8)
        self.assertEqual(pp.shapes[0].control1.y, -15)
        self.assertEqual(pp.shapes[0].control2.x, 15)
        self.assertEqual(pp.shapes[0].control2.y, -8)
        self.assertEqual(pp.shapes[0].p2.x, 23)
        self.assertEqual(pp.shapes[0].p2.y, -30)
        self.assertEqual(pp.shapes[1].type, 'bezier')
        self.assertEqual(pp.shapes[1].p1.x, 23)
        self.assertEqual(pp.shapes[1].p1.y, -30)
        self.assertEqual(pp.shapes[1].control1.x, -8)
        self.assertEqual(pp.shapes[1].control1.y, 15)
        self.assertEqual(pp.shapes[1].control2.x, -15)
        self.assertEqual(pp.shapes[1].control2.y, 30)
        self.assertEqual(pp.shapes[1].p2.x, -45)
        self.assertEqual(pp.shapes[1].p2.y, 53)
