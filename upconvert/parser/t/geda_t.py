#!/usr/bin/python
# encoding: utf-8
#pylint: disable=R0904
""" The geda parser test class """

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

import os
from os.path import dirname, join
from functools import wraps
from unittest import TestCase
import json
import StringIO
from tempfile import mkstemp

import upconvert.core.design
import upconvert.core.shape
from upconvert.core.shape import Point
from upconvert.parser.geda import GEDA, GEDAError, GEDAText

TEST_DIR = join(dirname(__file__), '..', '..', '..', 'test', 'geda')


_cache = {} # filename -> Design

def get_design(filename):
    if filename not in _cache:
        _cache[filename] = GEDA().parse(join(TEST_DIR, filename))
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


class GEDAEmpty(TestCase):
    """ The tests of a blank geda parser """

    def test_create_new_geda_parser(self):
        """ Test creating an empty parser. """
        parser = GEDA()
        assert parser != None


class GEDATextTests(TestCase):

    def test_adding_license_text(self):
        """ Test adding license text to design from GEDAText """
        geda_text = GEDAText('BSD', attribute='use_license')
        parser = GEDA()
        design = upconvert.core.design.Design()
        parser.add_text_to_design(design, geda_text)

        self.assertEquals(
            design.design_attributes.metadata.license,
            'BSD'
        )

    def test_adding_attribute_to_design(self):
        """ Add regular attribute to design from GEDAText """
        geda_text = GEDAText('some text', attribute='test_attr')
        parser = GEDA()
        design = upconvert.core.design.Design()
        parser.add_text_to_design(design, geda_text)

        self.assertEquals(
            design.design_attributes.attributes['test_attr'],
            'some text'
        )

class GEDATestCase(TestCase):

    def setUp(self):
        """
        Set up a new GEDA parser with simplified setting for easier
        testing. The scale factor is 10 and the origin is set to
        (0, 0) for easier calculation of correct/converted values.
        """
        self.geda_parser = GEDA()
        ## for easier validation
        self.geda_parser.SCALE_FACTOR = 10
        self.geda_parser.set_offset(upconvert.core.shape.Point(0, 0))

    def test_parsing_invalid_command(self):
        """ Test parsing a line command into a Line object. """
        invalid_string = "L -400 500 440 560 3 0 0 0 -1 -1",
        stream =  StringIO.StringIO(invalid_string)
        self.assertRaises(
            GEDAError,
            self.geda_parser._parse_command,
            stream
        )


class GEDALineParsingTests(GEDATestCase):

    def test_parsing_lines_from_command(self):
        """ Test parsing a line command into a Line object. """
        test_strings = [
            "L 40800 46600 45700 46600 3 0 0 0 -1 -1",
            "L 42300 45900 42900 45500 3 0 0 0 -1 -1",
            "L -400 500 440 560 3 0 0 0 -1 -1",
        ]

        for line_string in test_strings:
            typ, params =  self.geda_parser._parse_command(
                StringIO.StringIO(line_string)
            )
            self.assertEquals(typ, 'L')
            line_obj = self.geda_parser._parse_L(None, params)
            self.assertEquals(line_obj.type, 'line')
            self.assertEquals(
                line_obj.p1.x,
                params['x1']/self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                line_obj.p1.y,
                params['y1']/self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                line_obj.p2.x,
                params['x2']/self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                line_obj.p2.y,
                params['y2']/self.geda_parser.SCALE_FACTOR
            )

    def test_parsing_mirrored_lines_from_command(self):
        test_strings = [
            "L 40800 46600 45700 46600 3 0 0 0 -1 -1",
            "L 42300 45900 42900 45500 3 0 0 0 -1 -1",
            "L -400 500 440 560 3 0 0 0 -1 -1",
        ]
        for line_string in test_strings:
            typ, params =  self.geda_parser._parse_command(
                StringIO.StringIO(line_string)
            )
            self.assertEquals(typ, 'L')
            params['mirror'] = True
            line_obj = self.geda_parser._parse_L(None, params)
            self.assertEquals(line_obj.type, 'line')
            self.assertEquals(
                line_obj.p1.x,
                0-params['x1']/self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                line_obj.p1.y,
                params['y1']/self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                line_obj.p2.x,
                0-params['x2']/self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                line_obj.p2.y,
                params['y2']/self.geda_parser.SCALE_FACTOR
            )


class GEDATextParsingTest(GEDATestCase):

    def test_parsing_single_line_text_label(self):
        """ Test extracting text commands from input stream. """

        valid_text = """T 16900 35800 3 10 1 0 0 0 1
Text string!"""

        text_stream = StringIO.StringIO(valid_text)
        typ, params =  self.geda_parser._parse_command(text_stream)
        self.assertEquals(typ, 'T')
        geda_text = self.geda_parser._parse_T(text_stream, params)

        self.assertEquals(geda_text.attribute, None)
        self.assertEquals(geda_text.content, "Text string!")

    def test_parsing_multi_line_text_label(self):
        valid_text = """T 16900 35800 3 10 1 0 0 0 4
Text string!
And more ...
and more ...
text!"""
        text_stream = StringIO.StringIO(valid_text)
        typ, params =  self.geda_parser._parse_command(text_stream)
        self.assertEquals(typ, 'T')
        geda_text = self.geda_parser._parse_T(text_stream, params)

        text = """Text string!
And more ...
and more ...
text!"""

        self.assertEquals(geda_text.attribute, None)
        self.assertEquals(geda_text.content, text)


class GEDAEnvironmentParsingTests(GEDATestCase):

    def test_parsing_environment_with_attributes(self):
        """ Tests parsing attribute environments and enclosed attribute
            commands.
        """
        no_env = "P 100 600 200 600 1 0 0"
        stream = StringIO.StringIO(no_env)
        attributes = self.geda_parser._parse_environment(stream)
        self.assertEquals(attributes, None)
        self.assertEquals(stream.tell(), 0)

        valid_env = """{
T 150 650 5 8 1 1 0 6 1
pinnumber=3
T 150 650 5 8 0 1 0 6 1
pinseq=3
T 250 500 9 16 0 1 0 0 1
pinlabel=+=?
T 150 550 5 8 1 1 0 8 1
sometype=in
}"""
        expected_attributes = {
            '_pinnumber': '3',
            '_pinseq': '3',
            '_pinlabel': '+=?',
            'sometype': 'in',
        }
        stream = StringIO.StringIO(valid_env)
        attributes = self.geda_parser._parse_environment(stream)

        self.assertEquals(attributes, expected_attributes)

    def test_parsing_environment_with_invalid_multi_line_attribute(self):
        """ Test parsing environemt with invalid multi-line attribute """
        no_env = "P 100 600 200 600 1 0 0"
        stream = StringIO.StringIO(no_env)
        attributes = self.geda_parser._parse_environment(stream)
        self.assertEquals(attributes, None)
        self.assertEquals(stream.tell(), 0)


class GEDAAngleConversionTests(GEDATestCase):
    """ The tests of the geda parser """
    # pylint: disable=W0212

    def test_conv_angle(self):
        """ Test converting angles from degrees to pi radians. """
        angles = [
            (0, 0),
            (90, 1.5),
            (180, 1.0),
            (220, 0.8),
            (270, 0.5),
            (510, 1.2),
        ]

        for angle, expected in angles:
            converted = self.geda_parser.conv_angle(angle)
            self.assertEquals(expected, converted)


class GEDATests(GEDATestCase):

    def get_all_symbols(self, path):
        symbols = set()
        for dummy, dummy, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith('.sym'):
                    symbols.add(filename.lower())
        return symbols

    def test_constructor(self):
        """
        Test constructor with different parameters to ensure
        that symbols and symbol directories are handled correctly.
        """
        ## get number of symbols in symbols directory
        symbols = self.get_all_symbols('upconvert/library/geda')
        geda_parser = GEDA(['upconvert/library/geda'])
        self.assertEquals(len(geda_parser.known_symbols), len(symbols))

        geda_parser = GEDA([
            './test/geda/simple_example/symbols',
            '/invalid/dir/gEDA',
        ])

        self.assertEquals(len(geda_parser.known_symbols), len(symbols))
        self.assertEquals(
            geda_parser.known_symbols['opamp'],
            './test/geda/simple_example/symbols/opamp.sym'
        )

        geda_parser = GEDA([
            'test/geda/simple_example/symbols',
            '/invalid/dir/gEDA',
        ])

        self.assertTrue('title-b' in geda_parser.known_symbols)

        geda_parser = GEDA()
        self.assertTrue('title-b' in geda_parser.known_symbols)


class GEDATitleParsingTest(GEDATestCase):

    def test_parse_title_frame(self):
        """ Test parsing title frame components """
        title_frames = {
            'title-e': (44000, 34000),
            'title-bordered-e': (44000, 34000),
            'title-bordered-d': (34000, 22000),
            'title-bordered-a': (11000, 8500),
            'title-bordered-c': (22000, 17000),
            'title-bordered-b': (17000, 11000),
            'title-a0': (46800, 33100),
            'title-a1': (33100, 23300),
            'title-a2': (23300, 16500),
            'title-a3': (16500, 11600),
            'title-a4': (11600, 8200),
            'title-a0-2': (46800, 33100),
            'title-a1-2': (33100, 23300),
            'title-a2-2': (23300, 16500),
            'title-a3-2': (16500, 11600),
            'title-a4-2': (11600, 8200),
            'title-d': (34000, 22000),
            'title-b': (17000, 11000),
            'title-c': (22000, 17000),
            'title-a': (11000, 8500),
            'title-bordered-a4': (11600, 8200),
            'title-bordered-a1': (33100, 23300),
            'title-bordered-a0': (46800, 33100),
            'title-bordered-a3': (16500, 11600),
            'title-bordered-a2': (23300, 16500),
            'title-dg-1': (17000, 11000),
            'title-small-square': (7600, 6900),
            'titleblock': (7500, 1800),
            'titleblock1': (11000, 8500),
            'titleblock2': (22000, 17000),
            'titleblock3': (33000, 25500),
            'titleblock4': (44000, 34000),
            'titleblock_a4-1': (17000, 12000),
            'title-b-nameonedge': (26600, 17000),
            'title-b-cibolo': (26600, 17000),
            'title-block': (7500, 1800),
        }

        params = {
            'x': 3200,
            'y': 3109,
        }

        geda_parser = GEDA()
        for name, filename in geda_parser.known_symbols.items():
            if name.startswith('title'):
                params['basename'] = name

                ## reset geda parser
                geda_parser.frame_width = 0
                geda_parser.frame_height = 0

                geda_parser.design = upconvert.core.design.Design()
                geda_parser._parse_title_frame(params)

                self.assertEquals(geda_parser.offset.x, params['x'])
                self.assertEquals(geda_parser.offset.y, params['y'])

                self.assertEquals(
                    geda_parser.frame_width,
                    title_frames[name][0]
                )
                self.assertEquals(
                    geda_parser.frame_height,
                    title_frames[name][1]
                )

        ## check that method does not break when invalid file is passed
        params['basename'] = 'invalid_symbol.sym'

        geda_parser = GEDA()
        geda_parser._parse_title_frame(params)

        self.assertEquals(geda_parser.offset.x, params['x'])
        self.assertEquals(geda_parser.offset.y, params['y'])

        ## check if default is set correctly
        self.assertEquals(geda_parser.frame_width, 46800)
        self.assertEquals(geda_parser.frame_height, 34000)


class GEDABooleanConversionTests(GEDATestCase):

    def test_converting_boolean_values_equal_to_True(self):
        """
        Tests converting various values equal to ``True`` to boolean.
        """
        for test_bool in ['1', 1, True, 'true']:
            self.assertEquals('true', self.geda_parser.conv_bool(test_bool))

    def test_converting_boolean_values_equal_to_False(self):
        """
        Tests converting various values equal to ``False`` to boolean.
        """
        for test_bool in ['0', 0, False, 'false']:
            self.assertEquals('false', self.geda_parser.conv_bool(test_bool))


class GEDAScaleConversionTests(GEDATestCase):

    def test_converting_mils_to_pixel_scale(self):
        """ Test converting MILS to pixels. """
        test_mils = [
            (2, 0),
            (100, 10),
            (3429, 342),
            (0, 0),
            (-50, -5),
            (-1238, -123),
        ]
        self.geda_parser.set_offset(upconvert.core.shape.Point(0, 0))
        for mils, expected in test_mils:
            self.assertEquals(
                self.geda_parser.y_to_px(mils),
                expected
            )
            self.assertEquals(
                self.geda_parser.x_to_px(mils),
                expected
            )


class GEDANetTests(GEDATestCase):

    def test_calculate_nets(self):
        """ Test calculating and creating nets from net segment
            commands.
        """
        net_sample = """N 52100 44400 54300 44400 4
N 54300 44400 54300 46400 4
{
T 54300 44400 5 8 0 1 0 8 1
netname=test
}
N 53200 45100 53200 43500 4
N 55000 44400 56600 44400 4
{
T 55000 44400 5 8 0 1 0 8 1
netname=another name
}
N 55700 45100 55700 44400 4
{
T 55700 45100 5 8 0 1 0 8 1
netname=another name
}
N 55700 44400 55700 43500 4"""
        stream = StringIO.StringIO(net_sample)
        self.geda_parser.parse_schematic(stream)
        design = self.geda_parser.design

        ## check nets from design
        self.assertEquals(len(design.nets), 3)

        self.assertEqual(
            sorted([net.net_id for net in design.nets]),
            sorted(['another name', 'test', '5320a4350'])
        )
        self.assertEqual(
            sorted([net.attributes.get('name', None) for net in design.nets]),
            sorted(['another name', 'test', None])
        )

        sorted_nets = {}
        for net in design.nets:
            sorted_nets[len(net.points)] = net.points

        self.assertEquals(sorted_nets.keys(), [2, 3, 5])

        points_n1 = sorted_nets[2]
        points_n2 = sorted_nets[3]
        points_n3 = sorted_nets[5]

        self.assertEqual(
            sorted(points_n1.keys()),
            sorted(['5320a4510', '5320a4350'])
        )
        self.assertEquals(
            points_n1['5320a4510'].connected_points,
            ['5320a4350']
        )
        self.assertEquals(
            points_n1['5320a4350'].connected_points,
            ['5320a4510']
        )


        self.assertEquals(
            sorted(points_n2.keys()),
            sorted([
                '5210a4440', '5430a4640', '5430a4440'
            ])
        )
        self.assertEquals(
            sorted(points_n2['5210a4440'].connected_points),
            ['5430a4440']
        )
        self.assertEquals(
            sorted(points_n2['5430a4640'].connected_points),
            ['5430a4440']
        )
        self.assertEquals(
            sorted(points_n2['5430a4440'].connected_points),
            ['5210a4440', '5430a4640']
        )

        self.assertEquals(
            sorted(points_n3.keys()),
            sorted([
                '5500a4440', '5660a4440', '5570a4510',
                '5570a4440', '5570a4350'
            ])
        )
        self.assertEquals(
            sorted(points_n3['5500a4440'].connected_points),
            ['5570a4440'],
        )
        self.assertEquals(
            sorted(points_n3['5660a4440'].connected_points),
            ['5570a4440'],
        )
        self.assertEquals(
            sorted(points_n3['5570a4510'].connected_points),
            ['5570a4440'],
        )
        self.assertEquals(
            sorted(points_n3['5570a4440'].connected_points),
            ['5500a4440', '5570a4350', '5570a4510', '5660a4440'],
        )
        self.assertEquals(
            sorted(points_n3['5570a4350'].connected_points),
            ['5570a4440'],
        )

    def test_complex_net_example_with_test_file(self):
        """ Test complex net example with test file. """

        net = """v 20110115 2
C 40000 40000 0 0 0 title-B.sym
N 45300 47000 45400 47000 4
{
T 45300 47000 5 10 1 1 0 0 1
netname=short_test
}
N 44900 46500 45400 46500 4
{
T 44900 46500 5 10 1 1 0 0 1
netname=long test
}
N 48500 48500 48500 46500 4
N 48500 46500 52500 46500 4
N 50400 46500 50400 48500 4
N 50400 48500 52000 48500 4
{
T 50400 48500 5 10 1 1 0 0 1
netname=simple
}
N 51100 48500 51100 49900 4
N 51100 49900 54100 49900 4
N 42000 43000 48500 43000 4
{
T 42000 43000 5 10 1 1 0 0 1
netname=advanced
}
N 48500 43000 48500 45100 4
N 48500 45100 50500 45100 4
N 45300 43000 45300 44400 4
N 45300 44400 42000 44400 4
{
T 45300 44400 5 10 1 1 0 0 1
netname=more_advanced
}
N 48500 44400 50500 44400 4
N 43000 44400 43000 43000 4"""

        net_handle, net_schematic = mkstemp()
        os.write(net_handle, net)

        design = self.geda_parser.parse(net_schematic)

        self.assertEquals(len(design.nets), 4)

        net_names = [net.net_id for net in design.nets]
        self.assertEquals(
            sorted(net_names),
            sorted(['advanced', 'long test', 'short_test', 'simple']),
        )

    @use_file('10M_receiver.sch')
    def test_single_point_nets(self):
        """ Test nets created by overlapping pins."""

        net = [n for n in self.design.nets if n.net_id == '400a1170'][0]
        self.assertEqual(list(net.points), ['400a1170'])
        point = net.points.values()[0]
        self.assertEqual(len(point.connected_components), 2)
        self.assertEqual(set((cc.instance_id, cc.pin_number)
                             for cc in point.connected_components),
                         set([('C153', '1'), ('gnd-1-30', '1')]))


class GEDABusParsingTests(GEDATestCase):

    def test_parsing_buses_from_command(self):
        """ Tests parsing bus commands from stream, extracting
            busripper components and substituting the corresponding
            net segments.
        """
        bus_data = """U 800 0 800 1000 10 -1
N 1000 800 1200 800 4
C 1000 800 1 180 0 busripper-1.sym
{
T 1000 400 5 8 0 0 180 0 1
device=none
}
N 600 400 300 400 4
C 600 400 1 270 0 busripper-1.sym
{
T 1000 400 5 8 0 0 270 0 1
device=none
}"""
        stream = StringIO.StringIO(bus_data)
        self.geda_parser.parse_schematic(stream)
        design = self.geda_parser.design

        ## check nets from design
        self.assertEquals(len(design.nets), 1)

        point_ids = design.nets[0].points.keys()
        expected_points = [
            '80a100', '80a0', '120a80', '100a80', '80a60',
            '30a40', '60a40', '80a20'
        ]

        self.assertEquals(
            sorted(point_ids),
            sorted(expected_points),
        )


class GEDAEmbeddedSectionTests(GEDATestCase):

    def test_skip_embedded_section(self):
        """ Tests skipping an embedded section (enclosed in '[' & ']')."""
        data = """C 1000 800 1 180 0 busripper-1.sym\n"""
        stream = StringIO.StringIO(data)
        self.assertEquals(stream.tell(), 0)

        self.geda_parser.skip_embedded_section(stream)
        self.assertEquals(stream.tell(), 0)

        data += """[
T 1000 400 5 8 0 0 180 0 1
device=none
]\n"""
        stream = StringIO.StringIO(data)
        self.assertEquals(stream.tell(), 0)

        self.geda_parser._parse_command(stream)
        self.geda_parser.skip_embedded_section(stream)
        self.assertEquals(stream.tell(), len(data))


class GEDASegmentParsingTests(GEDATestCase):

    def test_parsing_simple_segment_from_command(self):
        """ Tests parsing a net segment command into NetPoints."""
        simple_segment = "N 47300 48500 43500 48500 4"

        self.geda_parser.segments = set()
        self.geda_parser.net_points = dict()
        self.geda_parser.net_names = dict()

        stream = StringIO.StringIO(simple_segment)
        typ, params = self.geda_parser._parse_command(stream)
        self.assertEquals(typ, 'N')
        self.geda_parser._parse_N(stream, params)

        np_a, np_b = self.geda_parser.segments.pop()
        self.assertEquals(np_a.point_id, '4730a4850')
        self.assertEquals(np_a.x, 4730)
        self.assertEquals(np_a.y, 4850)

        self.assertEquals(np_b.point_id, '4350a4850')
        self.assertEquals(np_b.x, 4350)
        self.assertEquals(np_b.y, 4850)

        expected_points = [(4730, 4850), (4350, 4850)]
        for x, y in expected_points:
            point = self.geda_parser.net_points[(x, y)]
            self.assertEquals(point.point_id, '%da%d' % (x, y))
            self.assertEquals(point.x, x)
            self.assertEquals(point.y, y)

    def test_parsing_complex_segment_from_command(self):
        """ Tests parsing a complex net segment command into NetPoints."""
        complex_segment = """N 47300 48500 43500 48500 4
{
T 43800 48300 5 10 1 1 0 0 1
netname=+_1
}"""
        self.geda_parser.segments = set()
        self.geda_parser.net_points = dict()
        self.geda_parser.net_names = dict()

        stream = StringIO.StringIO(complex_segment)
        typ, params = self.geda_parser._parse_command(stream)
        self.assertEquals(typ, 'N')
        self.geda_parser._parse_N(stream, params)

        expected_points = [(4730, 4850), (4350, 4850)]
        for x, y in expected_points:
            point = self.geda_parser.net_points[(x, y)]
            self.assertEquals(point.point_id, '%da%d' % (x, y))
            self.assertEquals(point.x, x)
            self.assertEquals(point.y, y)


class GEDAArcParsingTests(GEDATestCase):

    def test_parse_arc_of_quarter_circle(self):
        """ Tests parsing an arc command into an Arc object. """
        typ, params =  self.geda_parser._parse_command(
            StringIO.StringIO("A 41100 48500 1900 0 90 3 0 0 0 -1 -1")
        )
        self.assertEquals(typ, 'A')
        arc_obj = self.geda_parser._parse_A(None, params)
        self.assertEquals(arc_obj.type, 'arc')
        self.assertEquals(arc_obj.x, 4110)
        self.assertEquals(arc_obj.y, 4850)
        self.assertEquals(arc_obj.radius, 190)
        self.assertEquals(arc_obj.start_angle, 0.0)
        self.assertEquals(arc_obj.end_angle, 1.5)
        ## mirrored arc
        params['mirror'] = True
        arc_obj = self.geda_parser._parse_A(None, params)
        self.assertEquals(arc_obj.x, -4110)
        self.assertEquals(arc_obj.y, 4850)
        self.assertEquals(arc_obj.radius, 190)
        self.assertEquals(arc_obj.start_angle, 1.5)
        self.assertEquals(arc_obj.end_angle, 1.0)

    def test_parse_arc_with_sweepangle_200(self):
        """ Test parsing arc with sweepangle 200 """
        typ, params =  self.geda_parser._parse_command(
            StringIO.StringIO("A 44300 49800 500 30 200 3 0 0 0 -1 -1")
        )
        self.assertEquals(typ, 'A')
        arc_obj = self.geda_parser._parse_A(None, params)
        self.assertEquals(arc_obj.type, 'arc')
        self.assertEquals(arc_obj.x, 4430)
        self.assertEquals(arc_obj.y, 4980)
        self.assertEquals(arc_obj.radius, 50)
        self.assertEquals(arc_obj.start_angle, 1.8)
        self.assertEquals(arc_obj.end_angle, 0.7)
        ## mirrored arc
        params['mirror'] = True
        arc_obj = self.geda_parser._parse_A(None, params)
        self.assertEquals(arc_obj.type, 'arc')
        self.assertEquals(arc_obj.x, -4430)
        self.assertEquals(arc_obj.y, 4980)
        self.assertEquals(arc_obj.radius, 50)
        self.assertEquals(arc_obj.start_angle, 0.3)
        self.assertEquals(arc_obj.end_angle, 1.2)

    def test_parse_arc_with_sweepangle_291(self):
        """ Test parsing arc with sweepangle 291 """
        typ, params =  self.geda_parser._parse_command(
            StringIO.StringIO("A 45100 48400 700 123 291 3 0 0 0 -1 -1")
        )
        self.assertEquals(typ, 'A')
        arc_obj = self.geda_parser._parse_A(None, params)
        self.assertEquals(arc_obj.type, 'arc')
        self.assertEquals(arc_obj.x, 4510)
        self.assertEquals(arc_obj.y, 4840)
        self.assertEquals(arc_obj.radius, 70)
        self.assertEquals(arc_obj.start_angle, 1.3)
        self.assertEquals(arc_obj.end_angle, 1.7)

    def test_parse_arc_with_sweepangle_larger_full_circle(self):
        """ Test parsing arc larger then full circle """
        typ, params =  self.geda_parser._parse_command(
            StringIO.StringIO("A 45100 48400 700 123 651 3 0 0 0 -1 -1")
        )
        self.assertEquals(typ, 'A')
        arc_obj = self.geda_parser._parse_A(None, params)
        self.assertEquals(arc_obj.type, 'arc')
        self.assertEquals(arc_obj.x, 4510)
        self.assertEquals(arc_obj.y, 4840)
        self.assertEquals(arc_obj.radius, 70)
        self.assertEquals(arc_obj.start_angle, 1.3)
        self.assertEquals(arc_obj.end_angle, 1.7)

    def test_parse_arc_with_large_sweepangle(self):
        """ Test parsing arc with large sweepangle """
        typ, params =  self.geda_parser._parse_command(
            StringIO.StringIO("A 0 0 500 30 200 3 0 0 0 -1 -1")
        )
        self.assertEquals(typ, 'A')
        params['mirror'] = True
        arc_obj = self.geda_parser._parse_A(None, params)
        self.assertEquals(arc_obj.type, 'arc')
        self.assertEquals(arc_obj.x, 0)
        self.assertEquals(arc_obj.y, 0)
        self.assertEquals(arc_obj.radius, 50)
        ## mirrored to 310 (0.3) + 200 = 510 (1.2)
        self.assertEquals(arc_obj.start_angle, 0.3)
        self.assertEquals(arc_obj.end_angle, 1.2)


class GEDABoxParsingTests(GEDATestCase):

    def test_parsing_boxes_from_command(self):
        """ Tests parsing box commands into Rectangle objects. """
        test_strings = [
            "B 41700 42100 2900 1500 3 0 0 0 -1 -1 0 -1 -1 -1 -1 -1",
            "B 46100 41100 1200 2600 3 0 0 0 -1 -1 0 -1 -1 -1 -1 -1",
        ]

        for rect_string in test_strings:
            typ, params =  self.geda_parser._parse_command(
                StringIO.StringIO(rect_string)
            )
            self.assertEquals(typ, 'B')
            rect_obj = self.geda_parser._parse_B(None, params)
            self.assertEquals(rect_obj.type, 'rectangle')
            self.assertEquals(
                rect_obj.x,
                params['x']/self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                rect_obj.y,
                (params['y']+params['height'])/self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                rect_obj.width,
                params['width']/self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                rect_obj.height,
                params['height']/self.geda_parser.SCALE_FACTOR
            )

    def test_parsing_boxes_from_command_with_mirror_flag(self):
        """ Test parsing boxes from command with mirror flag """
        mirror_test_strings = [
            (
                "B 100 300 300 500 3 0 0 0 -1 -1 0 -1 -1 -1 -1 -1",
                {'x': -40, 'y': 80, 'width': 30, 'height': 50},
            ),
            (
                "B -200 400 500 200 3 0 0 0 -1 -1 0 -1 -1 -1 -1 -1",
                {'x': -30, 'y': 60, 'width': 50, 'height': 20},
            )
        ]
        ## check mirrored rectangle
        for rect_string, result_dict in mirror_test_strings:
            typ, params =  self.geda_parser._parse_command(
                StringIO.StringIO(rect_string)
            )
            params['mirror'] = True
            rect_obj = self.geda_parser._parse_B(None, params)
            self.assertEquals(rect_obj.type, 'rectangle')
            self.assertEquals(rect_obj.x, result_dict['x'])
            self.assertEquals(rect_obj.y, result_dict['y'])
            self.assertEquals(rect_obj.width, result_dict['width'])
            self.assertEquals(rect_obj.height, result_dict['height'])


class GEDAPathParsingTests(GEDATestCase):

    def test_parsing_invalid_path(self):
        """ Test parsing a line command into a Line object. """
        invalid_example = """H 3 0 0 0 -1 -1 1 -1 -1 -1 -1 -1 2
M 510,240
X 510,240
z"""
        stream =  StringIO.StringIO(invalid_example)
        typ, params = self.geda_parser._parse_command(stream)
        self.assertRaises(
            GEDAError,
            self.geda_parser._parse_H,
            stream,
            params
        )

    def test_parsing_path_with_first_element_not_M(self):
        """ Test parsing a line command into a Line object. """
        invalid_example = """H 3 0 0 0 -1 -1 1 -1 -1 -1 -1 -1 2
L 510,240
z"""
        stream =  StringIO.StringIO(invalid_example)
        typ, params = self.geda_parser._parse_command(stream)
        self.assertRaises(
            GEDAError,
            self.geda_parser._parse_H,
            stream,
            params
        )

    def test_parse_simple_path_command(self):
        """ Tests parsing path commands into lists of shapes. """
        simple_example = """H 3 0 0 0 -1 -1 1 -1 -1 -1 -1 -1 5
M 510,240
L 601,200
L 555,295
L 535,265
z"""

        stream = StringIO.StringIO(simple_example)
        typ, params = self.geda_parser._parse_command(stream)
        self.assertEquals(typ, 'H')

        shapes = self.geda_parser._parse_H(stream, params)

        expected_results = [
            ['line', (51, 24), (60, 20)],
            ['line', (60, 20), (55, 29)],
            ['line', (55, 29), (53, 26)],
            ['line', (53, 26), (51, 24)],
        ]

        self.assertEquals(len(shapes), 4)

        for shape, expected in zip(shapes, expected_results):
            self.assertEquals(shape.type, expected[0])
            start_x, start_y = expected[1]
            self.assertEquals(shape.p1.x, start_x)
            self.assertEquals(shape.p1.y, start_y)
            end_x, end_y = expected[2]
            self.assertEquals(shape.p2.x, end_x)
            self.assertEquals(shape.p2.y, end_y)

    def test_parse_simple_path_command_with_mirrored_flag(self):
        """ Test parsing simple path command with mirror flag set """
        simple_example = """H 3 0 0 0 -1 -1 1 -1 -1 -1 -1 -1 5
M 510,240
L 601,200
L 555,295
L 535,265
z"""
        stream = StringIO.StringIO(simple_example)
        typ, params = self.geda_parser._parse_command(stream)
        params['mirror'] = True
        shapes = self.geda_parser._parse_H(stream, params)

        expected_results = [
            ['line', (-51, 24), (-60, 20)],
            ['line', (-60, 20), (-55, 29)],
            ['line', (-55, 29), (-53, 26)],
            ['line', (-53, 26), (-51, 24)],
        ]

        self.assertEquals(len(shapes), 4)

        for shape, expected in zip(shapes, expected_results):
            self.assertEquals(shape.type, expected[0])
            start_x, start_y = expected[1]
            self.assertEquals(shape.p1.x, start_x)
            self.assertEquals(shape.p1.y, start_y)
            end_x, end_y = expected[2]
            self.assertEquals(shape.p2.x, end_x)
            self.assertEquals(shape.p2.y, end_y)

    def test_parse_curve_path_command(self):
        """ Test parsing curve path command """
        curve_example = """H 3 0 0 0 -1 -1 0 2 20 100 -1 -1 6
M 100,100
L 500,100
C 700,100 800,275 800,400
C 800,500 700,700 500,700
L 100,700
z"""
        stream = StringIO.StringIO(curve_example)
        typ, params = self.geda_parser._parse_command(stream)
        self.assertEquals(typ, 'H')

        shapes = self.geda_parser._parse_H(stream, params)

        self.assertEquals(len(shapes), 5)

        expected_shapes = ['line', 'bezier', 'bezier', 'line', 'line']
        for shape, expected in zip(shapes, expected_shapes):
            self.assertEquals(shape.type, expected)


class GEDACircleParsingTests(GEDATestCase):

    def test_parse_circles(self):
        """ Tests parsing circle commands into Circle objects. """
        test_strings = [
            "V 49100 48800 900 3 0 0 0 -1 -1 0 -1 -1 -1 -1 -1",
            "V 51200 49000 400 3 0 0 0 -1 -1 0 -1 -1 -1 -1 -1",
        ]

        for circle_string in test_strings:
            typ, params =  self.geda_parser._parse_command(
                StringIO.StringIO(circle_string)
            )
            self.assertEquals(typ, 'V')
            circle_obj = self.geda_parser._parse_V(None, params)
            self.assertEquals(circle_obj.type, 'circle')
            self.assertEquals(
                circle_obj.x,
                params['x']/self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                circle_obj.y,
                params['y']/self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                circle_obj.radius,
                params['radius']/self.geda_parser.SCALE_FACTOR
            )

    def test_parse_circles_with_mirror_flag(self):
        """ Test parsing circles with mirror flag set """
        test_strings = [
            "V 49100 48800 900 3 0 0 0 -1 -1 0 -1 -1 -1 -1 -1",
            "V 51200 49000 400 3 0 0 0 -1 -1 0 -1 -1 -1 -1 -1",
        ]
        for circle_string in test_strings:
            typ, params = self.geda_parser._parse_command(
                StringIO.StringIO(circle_string)
            )
            params['mirror'] = True
            self.assertEquals(typ, 'V')
            circle_obj = self.geda_parser._parse_V(None, params)
            self.assertEquals(circle_obj.type, 'circle')
            self.assertEquals(
                circle_obj.x,
                0-params['x']/self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                circle_obj.y,
                params['y']/self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                circle_obj.radius,
                params['radius']/self.geda_parser.SCALE_FACTOR
            )

class GEDAPinParsingTests(GEDATestCase):

    @staticmethod
    def get_pin_sample():
        """ Get pin command. """
        return """P 100 600 200 600 1 0 0
{
T 150 650 5 8 1 1 0 6 1
pinnumber=3
T 150 650 5 8 0 1 0 6 1
pinseq=3
T 250 500 9 16 0 1 0 0 1
pinlabel=+
T 150 550 5 8 0 1 0 8 1
pintype=in
}"""

    @staticmethod
    def get_reversed_pin():
        """ Get reversed pin command """
        return """P 100 600 200 600 1 0 1
{
T 150 650 5 8 1 1 0 6 1
pinnumber=E
T 150 650 5 8 0 1 0 6 1
pinseq=3
T 150 550 5 8 0 1 0 8 1
pintype=in
}"""

    def test_parse_pin(self):
        """ Tests parsing pin commands into Pin objects. """
        pin_sample = self.get_pin_sample()
        stream = StringIO.StringIO(pin_sample)
        typ, params =  self.geda_parser._parse_command(stream)
        self.assertEquals(typ, 'P')
        pin = self.geda_parser._parse_P(stream, params)

        self.assertEquals(pin.pin_number, '3')
        self.assertEquals(pin.label.text, '+')
        ## null_end
        self.assertEquals(pin.p1.x, 20)
        self.assertEquals(pin.p1.y, 60)
        ## connect_end
        self.assertEquals(pin.p2.x, 10)
        self.assertEquals(pin.p2.y, 60)

    def test_parse_pin_with_mirror_flag(self):
        """ Test parsing a pin command with the mirror flag set."""
        pin_sample = self.get_pin_sample()
        stream = StringIO.StringIO(pin_sample)
        typ, params =  self.geda_parser._parse_command(stream)
        params['mirror'] = True
        pin = self.geda_parser._parse_P(stream, params)

        ## null_end
        self.assertEquals(pin.p1.x, -20)
        self.assertEquals(pin.p1.y, 60)
        ## connect_end
        self.assertEquals(pin.p2.x, -10)
        self.assertEquals(pin.p2.y, 60)

    def test_parse_reversed_pin(self):
        """ Test pin command with reversed order of pin ends. """
        reversed_pin_sample = self.get_reversed_pin()
        stream = StringIO.StringIO(reversed_pin_sample)
        typ, params =  self.geda_parser._parse_command(stream)
        self.assertEquals(typ, 'P')
        pin = self.geda_parser._parse_P(stream, params)

        self.assertEquals(pin.pin_number, 'E')
        self.assertEquals(pin.label, None)
        ## null_end
        self.assertEquals(pin.p1.x, 10)
        self.assertEquals(pin.p1.y, 60)
        ## connect_end
        self.assertEquals(pin.p2.x, 20)
        self.assertEquals(pin.p2.y, 60)

    def test_parse_reversed_pin_with_mirror_flag(self):
        """
        Test parsing pin command with ends in reversed order and
        the mirror flag set.
        """
        reversed_pin_sample = self.get_reversed_pin()
        stream = StringIO.StringIO(reversed_pin_sample)
        typ, params =  self.geda_parser._parse_command(stream)
        params['mirror'] = True
        pin = self.geda_parser._parse_P(stream, params)

        ## null_end
        self.assertEquals(pin.p1.x, -10)
        self.assertEquals(pin.p1.y, 60)
        ## connect_end
        self.assertEquals(pin.p2.x, -20)
        self.assertEquals(pin.p2.y, 60)


class GEDAComponentParsingTests(GEDATestCase):

    def test_parse_command(self):
        """ Test parsing commands from a stream. """
        typ, params = self.geda_parser._parse_command(StringIO.StringIO('{'))
        self.assertEquals(typ, '{')
        self.assertEquals(params, {})

        typ, params = self.geda_parser._parse_command(
            StringIO.StringIO('A 49 34 223 30 90')
        )
        self.assertEquals(typ, 'A')
        self.assertEquals(params, {
            'x': 49,
            'y': 34,
            'radius': 223,
            'startangle': 30,
            'sweepangle': 90,
            'style_color': 3,
            'style_width': 10,
            'style_capstyle': 0,
            'style_dashstyle': 0,
            'style_dashlength': -1,
            'style_dashspace': -1,
        })

        expected_params = {
            'x': 18600,
            'y': 21500,
            'selectable': 1,
            'angle': 0,
            'mirror': 0,
            'basename': 'EMBEDDED555-1',
        }
        string = 'C 18600 21500 1 0 0 EMBEDDED555-1'
        typ, params = self.geda_parser._parse_command(
            StringIO.StringIO(string)
        )
        self.assertEquals(typ, 'C')
        self.assertEquals(params, expected_params)

    def test_parse_component_data(self):
        """ Tests parsing component data from symbol files and embedded
            sections.
        """
        self.geda_parser = GEDA([
            './test/geda/simple_example/symbols',
        ])
        # need to do this to force setup since parse_schematic isn't being run
        self.geda_parser.parse_setup()

        symbol = """v 20110115 2
H 3 0 0 0 -1 -1 1 -1 -1 -1 -1 -1 5
M 510,240
L 601,200
L 555,295
L 535,265
z
H 3 0 0 0 -1 -1 0 2 20 100 -1 -1 6
M 100,100
L 500,100
C 700,100 800,300 800,400
C 800,500 700,700 500,700
L 100,700
z"""
        stream = StringIO.StringIO(symbol)
        component = self.geda_parser.parse_component_data(stream, {
            'basename': 'test.sym',
        })

        self.assertEquals(component.name, 'test')
        self.assertEquals(len(component.symbols), 1)
        self.assertEquals(len(component.symbols[0].bodies), 1)
        self.assertEquals(len(component.symbols[0].bodies[0].shapes), 9)

    def test_parsing_unknown_component(self):
        """ Test parsing unknown component """
        self.geda_parser.design = upconvert.core.design.Design()
        stream = StringIO.StringIO('C 18600 21500 1 0 0 invalid.sym')
        component, instance = self.geda_parser._parse_component(
            stream,
            {'basename': 'invalid',},
        )
        self.assertEquals(component, None)
        self.assertEquals(instance, None)


class GEDATopLevelShapeTests(GEDATestCase):

    def test_adding_top_level_shapes_to_design(self):
        """ Test adding top-level shapes to design """
        with open('/tmp/toplevelshapes.sch', 'w') as toplevel_sch:
            toplevel_sch.write("\n".join([
                "v 20001 2",
                "L 40800 46600 45700 46600 3 0 0 0 -1 -1",
                "L 42300 45900 42900 45500 3 0 0 0 -1 -1",
                GEDAPinParsingTests.get_pin_sample(),
                GEDAPinParsingTests.get_reversed_pin(),
            ]))

        design = self.geda_parser.parse('/tmp/toplevelshapes.sch')

        self.assertEquals(len(design.shapes), 2)
        self.assertEquals(len(design.pins), 2)

        self.assertEqual(
            sorted(['line', 'line']),
            sorted([s.type for s in design.shapes])
        )


class GEDAStyleTests(GEDATestCase):

    def test_attaching_styles_to_shape(self):
        """ Test attaching style to shape """
        params = {
            'x': 49, 'y': 34,
            'radius': 223,
            'startangle': 30,
            'sweepangle': 90,
            'style_capstyle': None,
            'style_color': None,
            'style_dashlength': None,
            'style_dashspace': None,
            'style_dashstyle': None,
            'style_width': None,
        }
        shape_ = upconvert.core.shape.Arc(0, 0, 200, 200, 200)
        self.geda_parser._save_parameters_to_object(shape_, params)
        self.assertEqual(shape_.styles, {
            'style_capstyle': None,
            'style_color': None,
            'style_dashlength': None,
            'style_dashspace': None,
            'style_dashstyle': None,
            'style_width': None,
        })

    def test_attaching_styles_to_invalid_object(self):
        """ Test attaching styles to invalid objects """
        import logging
        logging.basicConfig(level=logging.INFO)
        import StringIO

        stream = StringIO.StringIO()
        logging.root.handlers = []
        logger = logging.getLogger('parser.geda')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler(stream))

        self.geda_parser._save_parameters_to_object(
            object,
            {'style_color': 1, 'style_somethingelse': 1},
        )
        self.assertTrue('without styles dict' in stream.getvalue())


class GEDAFullConversionTests(GEDATestCase):

    def test_parse(self):
        """ Tests parsing valid and invalid schematic files. """
        self.geda_parser = GEDA([
            'test/geda/simple_example/symbols',
        ])

        invalid_sch = open('/tmp/invalid.sch', 'w')
        invalid_sch.write('C 18600 21500 1 0 0 EMBEDDED555-1')
        invalid_sch.close()
        self.assertRaises(
            GEDAError,
            self.geda_parser.parse,
            '/tmp/invalid.sch'
        )

        ## testing EMBEDDED component
        design = self.geda_parser.parse(
            './test/geda/embedded_component.sch'
        )

        components = design.components.components #test components dictionary
        self.assertEquals(components.keys(), ['EMBEDDEDbattery-1'])

        component = components['EMBEDDEDbattery-1']
        self.assertEquals(component.name, 'EMBEDDEDbattery-1')

        keys = ['p1x', 'p1y', 'p2x', 'p2y', 'num', 'seq', 'label', 'type']
        expected_pins = [
            dict(zip(keys, [0, 200, 200, 200, '1', 1, '+', 'pwr'])),
            dict(zip(keys, [700, 200, 500, 200, '2', 2, '-', 'pwr'])),
        ]
        for pin, expected_pin in zip(component.symbols[0].bodies[0].pins,
                                     expected_pins):
            self.assertEquals(pin.label.text, expected_pin['label'])
            ## test reversed pin order due to different handling in direction
            self.assertEquals(
                pin.p1.x,
                expected_pin['p2x'] / self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                pin.p1.y,
                expected_pin['p2y'] / self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                pin.p2.x,
                expected_pin['p1x'] / self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                pin.p2.y,
                expected_pin['p1y'] / self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(pin.pin_number, expected_pin['num'])

        ## testing referenced component
        design = self.geda_parser.parse('test/geda/component.sch')

        components = design.components.components #test components dictionary
        self.assertEquals(components.keys(), ['battery-1'])

        component = components['battery-1']
        self.assertEquals(component.name, 'battery-1')

        keys = ['p1x', 'p1y', 'p2x', 'p2y', 'num', 'seq', 'label', 'type']
        expected_pins = [
            dict(zip(keys, [0, 200, 200, 200, '1', 1, '+', 'pwr'])),
            dict(zip(keys, [700, 200, 500, 200, '2', 2, '-', 'pwr'])),
        ]
        for pin, expected_pin in zip(component.symbols[0].bodies[0].pins,
                                     expected_pins):
            self.assertEquals(pin.label.text, expected_pin['label'])
            ## test reversed pin order due to different handling in direction
            self.assertEquals(
                pin.p1.x,
                expected_pin['p2x'] / self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                pin.p1.y,
                expected_pin['p2y'] / self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                pin.p2.x,
                expected_pin['p1x'] / self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                pin.p2.y,
                expected_pin['p1y'] / self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(pin.pin_number, expected_pin['num'])

    def test_parse_full(self):
        """
        Test parsing a complete schematic file generating OpenJSON.
        """
        self.geda_parser = GEDA([
            './test/geda/simple_example/symbols',
        ])
        design = self.geda_parser.parse(
            'test/geda/simple_example/simple_example.sch'
        )
        self.assertEquals(len(design.nets), 2)

        net_names = [net.net_id for net in design.nets]
        self.assertEquals(
            sorted(net_names),
            sorted(['+_1', '-_In+']),
        )


class GedaLightningProjectTests(TestCase):

    filename = 'test/geda/lightning/lightning.json'

    def setUp(self):
        with open(self.filename) as fh:
            self.reference = json.load(fh)

        self.components = {}
        for comp in self.reference['components']:
            if not comp['filename'].startswith('title'):
                self.components[comp['refdes']] = comp

        self.bom = self.reference['bom']

    def test_something(self):
        self.geda_parser = GEDA(['./test/geda/lightning/symbols',])
        design = self.geda_parser.parse('test/geda/lightning/lightning.sch')

        self.assertEquals(
            len(design.component_instances),
            len(self.components)
        )

        for comp in design.component_instances:
            refcomp = self.components[comp.instance_id]

            self.assertEquals(comp.instance_id, refcomp['refdes'])
            # check that the library ID corresponds to the filename
            # of the symbol but ignoring the suffix that might indicate
            # a mirrored component.
            assert comp.library_id.startswith(
                refcomp['filename'].replace('.sym', '')
            )

        self.assertEquals(len(design.nets), 13)

        net_names = ['net%d' % (idx+1) for idx, ___ in enumerate(design.nets)]
        for net in design.nets:
            net_names.remove(net.net_id)
        self.assertFalse(net_names)

        pin_lookup = {}
        def make_pin_lookup(lst, pins):
            for i in lst:
                pin_lookup[i] = pins

        make_pin_lookup(['A1', 'bat(+3v)', 'lamp(1)', 'lamp(2)', 'bat(0v)'], 1)
        make_pin_lookup(['L1', 'L2', 'C1', 'C2', 'R1', 'R2', 'C3', 'R3',
                         'D1', 'C4', 'R5', 'C5', 'R6', 'C6', 'R7'], 2)
        make_pin_lookup(['Q%d' % idx for idx in range(1, 5)] + ['R4'], 3)

        for inst in design.component_instances:
            comp = design.components.components[inst.library_id]
            body = comp.symbols[inst.symbol_index].bodies[0]
            self.assertEquals(len(body.pins), pin_lookup[inst.instance_id])

        # check for correct amount of netpoints with connections
        # fail early when not the right amount of points connected
        connected_nets = {
            'net1': ['A1', 'L2'],
            'net2': ['L2', 'L1', 'C2', 'C1'],
            'net3': ['L1', 'Q1', 'C1', 'R6', 'C6', 'Q4', 'bat(0v)'],
            'net4': ['Q1', 'R1', 'C2'],
            'net5': ['Q1', 'R1', 'R2', 'C3'],
            'net6': ['R2', 'C6', 'R7', 'bat(+3v)'],
            'net7': ['R4']*2 + ['D1', 'Q3', 'R7', 'lamp(1)'],
            'net8': ['D1', 'Q2', 'C4'],
            'net9': ['R3', 'R4', 'Q2', 'C3'],
            'net10': ['R3', 'C4', 'C5', 'Q3', 'R6', 'Q4'],
            'net11': ['R5', 'C5', 'Q3'],
            'net12': ['Q4', 'lamp(2)'],
            'net13': ['Q2', 'R5'],
        }

        for net in design.nets:
            net_connections = []
            for np in net.points.values():
                net_connections += [c.instance_id for c in np.connected_components]
            self.assertEquals(sorted(connected_nets[net.net_id]), sorted(net_connections))

    def is_connected(self, point, inst):
        for conn_comp in point.connected_components:
            if conn_comp.instance_id == inst.instance_id:
                return True
        return False

    def get_normalised_pins(self, design, inst):
        try:
            inst.library_id
        except AttributeError:
            for i in design.component_instances:
                if i.instance_id == inst:
                    inst = i
                    break

        comp = design.components.components[inst.library_id]

        norm_pins = []
        for pin in comp.symbols[inst.symbol_index].bodies[0].pins:
            inst_origin = inst.symbol_attributes[inst.symbol_index]

            x1, y1 = GEDA.translate_coords(pin.p1.x, pin.p1.y, inst_origin.rotation)
            x2, y2 = GEDA.translate_coords(pin.p2.x, pin.p2.y, inst_origin.rotation)

            norm_pins.append(Point(
                x2 + inst_origin.x,
                y2 + inst_origin.y)
            )
        return norm_pins
