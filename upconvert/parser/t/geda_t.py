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
import unittest
import StringIO
from upconvert.parser.geda import GEDA, GEDAError
import upconvert.core.shape


class GEDAEmpty(unittest.TestCase):
    """ The tests of a blank geda parser """

    def test_create_new_geda_parser(self):
        """ Test creating an empty parser. """
        parser = GEDA()
        assert parser != None


class GEDATests(unittest.TestCase):
    """ The tests of the geda parser """
    # pylint: disable=W0212

    def setUp(self):
        """ setup gEDA parser instance with offset (0,0) for easier 
            comparsion.
        """
        self.geda_parser = GEDA()
        ## for easier validation 
        self.geda_parser.SCALE_FACTOR = 10
        self.geda_parser.set_offset(upconvert.core.shape.Point(0, 0))

    def test_constructor(self):
        """ Test constructor with different parameters to ensure
            that symbols and symbol directories are handled correctly.
        """
        ## get number of symbols in symbols directory
        symbols = set() 
        for dummy, dummy, filenames in os.walk('upconvert/library/geda'):
            for filename in filenames:
                if filename.endswith('.sym'):
                    symbols.add(filename)

        geda_parser = GEDA()
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

        self.assertTrue('title-B' in geda_parser.known_symbols)

        geda_parser = GEDA()
        self.assertTrue('title-B' in geda_parser.known_symbols)

    def test__parse_title_frame(self):
        title_frames = {
            'title-E': (44000, 34000),
            'title-bordered-E': (44000, 34000),
            'title-bordered-D': (34000, 22000),
            'title-bordered-A': (11000, 8500),
            'title-bordered-C': (22000, 17000),
            'title-bordered-B': (17000, 11000),
            'title-A0': (46800, 33100),
            'title-A1': (33100, 23300),
            'title-A2': (23300, 16500),
            'title-A3': (16500, 11600),
            'title-A4': (11600, 8200),
            'title-A0-2': (46800, 33100),
            'title-A1-2': (33100, 23300),
            'title-A2-2': (23300, 16500),
            'title-A3-2': (16500, 11600),
            'title-A4-2': (11600, 8200),
            'title-D': (34000, 22000),
            'title-B': (17000, 11000),
            'title-C': (22000, 17000),
            'title-A': (11000, 8500),
            'title-bordered-A4': (11600, 8200),
            'title-bordered-A1': (33100, 23300),
            'title-bordered-A0': (46800, 33100),
            'title-bordered-A3': (16500, 11600),
            'title-bordered-A2': (23300, 16500),
            'title-dg-1': (17000, 11000),
            'title-small-square': (7600, 6900),
            'titleblock': (7500, 1800),
            'titleblock1': (11000, 8500),
            'titleblock2': (22000, 17000),
            'titleblock3': (33000, 25500),
            'titleblock4': (44000, 34000),
            'title-B-nameOnEdge': (26600, 17000),
            'title-B-cibolo': (26600, 17000),
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

                print name

                ## reset geda parser 
                geda_parser.frame_width = 0
                geda_parser.frame_height = 0

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

    def test__parse_text(self):
        """ Test extracting text commands from input stream. """

        valid_text = """T 16900 35800 3 10 1 0 0 0 1
Text string!"""

        text_stream = StringIO.StringIO(valid_text)
        typ, params =  self.geda_parser._parse_command(text_stream)
        self.assertEquals(typ, 'T')
        key, value = self.geda_parser._parse_text(text_stream, params)

        self.assertEquals(key, None)

        annotation = self.geda_parser._create_annotation(value, params)

        self.assertEquals(annotation.value, "Text string!")
        self.assertEquals(annotation.x, 1690)
        self.assertEquals(annotation.y, 3580)
        self.assertEquals(annotation.visible, 'true')
        self.assertEquals(annotation.rotation, 0)

        
        valid_text = """T 16900 35800 3 10 1 0 0 0 4
Text string!
And more ...
and more ...
text!"""
        text_stream = StringIO.StringIO(valid_text)
        typ, params =  self.geda_parser._parse_command(text_stream)
        self.assertEquals(typ, 'T')
        key, value = self.geda_parser._parse_text(text_stream, params)

        text = """Text string!
And more ...
and more ...
text!"""

        self.assertEquals(key, None)

        annotation = self.geda_parser._create_annotation(value, params)

        self.assertEquals(annotation.value, text)
        self.assertEquals(annotation.x, 1690)
        self.assertEquals(annotation.y, 3580)
        self.assertEquals(annotation.visible, 'true')
        self.assertEquals(annotation.rotation, 0)

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

    def test_conv_bool(self):
        """ Tests converting various values to boolean. """
        for test_bool in ['1', 1, True, 'true']:
            self.assertEquals('true', self.geda_parser.conv_bool(test_bool))

        for test_bool in ['0', 0, False, 'false']:
            self.assertEquals('false', self.geda_parser.conv_bool(test_bool))

    def test_conv_mils(self):
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

    def test__parse_environment(self):
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

        self.assertEquals(
            sorted([net.net_id for net in design.nets]),
            sorted(['another name', 'test', ''])
        )
        self.assertEquals(
            sorted([net.attributes['_name'] for net in design.nets]),
            sorted(['another name', 'test', ''])
        )

        sorted_nets = {}
        for net in design.nets:
            sorted_nets[len(net.points)] = net.points

        self.assertEquals(sorted_nets.keys(), [2, 3, 5])

        points_n1 = sorted_nets[2]
        points_n2 = sorted_nets[3]
        points_n3 = sorted_nets[5]

        self.assertEquals(
            sorted(points_n1.keys()), 
            sorted([
                '5320a4510', '5320a4350'
            ])
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

        #run more complex test with nets sample file
        net_schematic = 'test/geda/nets.sch'
        design = self.geda_parser.parse(net_schematic)

        self.assertEquals(len(design.nets), 4)

        net_names = [net.net_id for net in design.nets]
        self.assertEquals(
            sorted(net_names),
            sorted(['advanced', 'long test', 'short_test', 'simple']),
        )



    def test__parse_buses_from_stream(self):
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

    def test__parse_segment(self):
        """ Tests parsing a net segment command into NetPoints."""
        simple_segment = "N 47300 48500 43500 48500 4"

        self.geda_parser.segments = set()
        self.geda_parser.net_points = dict()
        self.geda_parser.net_names = dict()

        stream = StringIO.StringIO(simple_segment)
        typ, params = self.geda_parser._parse_command(stream)
        self.assertEquals(typ, 'N')
        self.geda_parser._parse_segment(stream, params)

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
        self.geda_parser._parse_segment(stream, params)

        expected_points = [(4730, 4850), (4350, 4850)]
        for x, y in expected_points:
            point = self.geda_parser.net_points[(x, y)]
            self.assertEquals(point.point_id, '%da%d' % (x, y))
            self.assertEquals(point.x, x)
            self.assertEquals(point.y, y)

    def test__parse_arc(self):
        """ Tests parsing an arc command into an Arc object. """
        typ, params =  self.geda_parser._parse_command(
            StringIO.StringIO("A 41100 48500 1900 0 90 3 0 0 0 -1 -1")
        )
        self.assertEquals(typ, 'A')
        arc_obj = self.geda_parser._parse_arc(params)
        self.assertEquals(arc_obj.type, 'arc')
        self.assertEquals(arc_obj.x, 4110)
        self.assertEquals(arc_obj.y, 4850)
        self.assertEquals(arc_obj.radius, 190)
        self.assertEquals(arc_obj.start_angle, 0.0)
        self.assertEquals(arc_obj.end_angle, 1.5)
        ## mirrored arc
        arc_obj = self.geda_parser._parse_arc(params, mirrored=True)
        self.assertEquals(arc_obj.x, -4110)
        self.assertEquals(arc_obj.y, 4850)
        self.assertEquals(arc_obj.radius, 190)
        self.assertEquals(arc_obj.start_angle, 1.5)
        self.assertEquals(arc_obj.end_angle, 1.0)

        typ, params =  self.geda_parser._parse_command(
            StringIO.StringIO("A 44300 49800 500 30 200 3 0 0 0 -1 -1")
        )
        self.assertEquals(typ, 'A')
        arc_obj = self.geda_parser._parse_arc(params)
        self.assertEquals(arc_obj.type, 'arc')
        self.assertEquals(arc_obj.x, 4430)
        self.assertEquals(arc_obj.y, 4980)
        self.assertEquals(arc_obj.radius, 50)
        self.assertEquals(arc_obj.start_angle, 1.8)
        self.assertEquals(arc_obj.end_angle, 0.7)
        ## mirrored arc
        arc_obj = self.geda_parser._parse_arc(params, mirrored=True)
        self.assertEquals(arc_obj.type, 'arc')
        self.assertEquals(arc_obj.x, -4430)
        self.assertEquals(arc_obj.y, 4980)
        self.assertEquals(arc_obj.radius, 50)
        self.assertEquals(arc_obj.start_angle, 0.3)
        self.assertEquals(arc_obj.end_angle, 1.2)

        typ, params =  self.geda_parser._parse_command(
            StringIO.StringIO("A 45100 48400 700 123 291 3 0 0 0 -1 -1")
        )
        self.assertEquals(typ, 'A')
        arc_obj = self.geda_parser._parse_arc(params)
        self.assertEquals(arc_obj.type, 'arc')
        self.assertEquals(arc_obj.x, 4510)
        self.assertEquals(arc_obj.y, 4840)
        self.assertEquals(arc_obj.radius, 70)
        self.assertEquals(arc_obj.start_angle, 1.3)
        self.assertEquals(arc_obj.end_angle, 1.7)

        typ, params =  self.geda_parser._parse_command(
            StringIO.StringIO("A 45100 48400 700 123 651 3 0 0 0 -1 -1")
        )
        self.assertEquals(typ, 'A')
        arc_obj = self.geda_parser._parse_arc(params)
        self.assertEquals(arc_obj.type, 'arc')
        self.assertEquals(arc_obj.x, 4510)
        self.assertEquals(arc_obj.y, 4840)
        self.assertEquals(arc_obj.radius, 70)
        self.assertEquals(arc_obj.start_angle, 1.3)
        self.assertEquals(arc_obj.end_angle, 1.7)

        typ, params =  self.geda_parser._parse_command(
            StringIO.StringIO("A 0 0 500 30 200 3 0 0 0 -1 -1")
        )
        self.assertEquals(typ, 'A')
        arc_obj = self.geda_parser._parse_arc(params, mirrored=True)
        self.assertEquals(arc_obj.type, 'arc')
        self.assertEquals(arc_obj.x, 0)
        self.assertEquals(arc_obj.y, 0)
        self.assertEquals(arc_obj.radius, 50)
        ## mirrored to 310 (0.3) + 200 = 510 (1.2)
        self.assertEquals(arc_obj.start_angle, 0.3)
        self.assertEquals(arc_obj.end_angle, 1.2)

    def test__parse_line(self):
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
            line_obj = self.geda_parser._parse_line(params)
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

        for line_string in test_strings:
            typ, params =  self.geda_parser._parse_command(
                StringIO.StringIO(line_string)
            )
            self.assertEquals(typ, 'L')
            line_obj = self.geda_parser._parse_line(params, mirrored=True)
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

    def test__parse_box(self):
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
            rect_obj = self.geda_parser._parse_box(params)
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
            rect_obj = self.geda_parser._parse_box(params, mirrored=True)
            self.assertEquals(rect_obj.type, 'rectangle')
            self.assertEquals(rect_obj.x, result_dict['x'])
            self.assertEquals(rect_obj.y, result_dict['y'])
            self.assertEquals(rect_obj.width, result_dict['width'])
            self.assertEquals(rect_obj.height, result_dict['height'])

    def test__parse_path(self):
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

        shapes = self.geda_parser._parse_path(stream, params)
        
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

        ##NOTE: parse mirrored path
        stream = StringIO.StringIO(simple_example)
        typ, params = self.geda_parser._parse_command(stream)
        shapes = self.geda_parser._parse_path(stream, params, mirrored=True)
        
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

        shapes = self.geda_parser._parse_path(stream, params)

        self.assertEquals(len(shapes), 5)

        expected_shapes = ['line', 'bezier', 'bezier', 'line', 'line']
        for shape, expected in zip(shapes, expected_shapes):
            self.assertEquals(shape.type, expected)

    def test__parse_circle(self):
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
            circle_obj = self.geda_parser._parse_circle(params)
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

        ##mirrored circles
        for circle_string in test_strings:
            typ, params =  self.geda_parser._parse_command(
                StringIO.StringIO(circle_string)
            )
            self.assertEquals(typ, 'V')
            circle_obj = self.geda_parser._parse_circle(params, mirrored=True)
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

    def test__parse_pin(self):
        """ Tests parsing pin commands into Pin objects. """
        stream = StringIO.StringIO('P 100 600 200 600 1 0 0\n')
        typ, params =  self.geda_parser._parse_command(stream)
        self.assertEquals(typ, 'P')
        self.assertRaises(
            GEDAError,
            self.geda_parser._parse_pin,
            stream, 
            params
        )

        pin_sample = """P 100 600 200 600 1 0 0
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
        stream = StringIO.StringIO(pin_sample)
        typ, params =  self.geda_parser._parse_command(stream)
        self.assertEquals(typ, 'P')
        pin = self.geda_parser._parse_pin(stream, params)

        self.assertEquals(pin.pin_number, '3')
        self.assertEquals(pin.label.text, '+')
        ## null_end
        self.assertEquals(pin.p1.x, 20)
        self.assertEquals(pin.p1.y, 60)
        ## connect_end
        self.assertEquals(pin.p2.x, 10)
        self.assertEquals(pin.p2.y, 60)

        ##NOTE: test mirrored pin
        stream = StringIO.StringIO(pin_sample)
        typ, params =  self.geda_parser._parse_command(stream)
        pin = self.geda_parser._parse_pin(stream, params, mirrored=True)

        ## null_end
        self.assertEquals(pin.p1.x, -20)
        self.assertEquals(pin.p1.y, 60)
        ## connect_end
        self.assertEquals(pin.p2.x, -10)
        self.assertEquals(pin.p2.y, 60)

        reversed_pin_sample = """P 100 600 200 600 1 0 1
{
T 150 650 5 8 1 1 0 6 1
pinnumber=E
T 150 650 5 8 0 1 0 6 1
pinseq=3
T 150 550 5 8 0 1 0 8 1
pintype=in
}"""
        stream = StringIO.StringIO(reversed_pin_sample)
        typ, params =  self.geda_parser._parse_command(stream)
        self.assertEquals(typ, 'P')
        pin = self.geda_parser._parse_pin(stream, params)

        self.assertEquals(pin.pin_number, 'E')
        self.assertEquals(pin.label, None) 
        ## null_end
        self.assertEquals(pin.p1.x, 10)
        self.assertEquals(pin.p1.y, 60)
        ## connect_end
        self.assertEquals(pin.p2.x, 20)
        self.assertEquals(pin.p2.y, 60)

        ##NOTE: test mirrored pin
        stream = StringIO.StringIO(reversed_pin_sample)
        typ, params =  self.geda_parser._parse_command(stream)
        pin = self.geda_parser._parse_pin(stream, params, mirrored=True)

        ## null_end
        self.assertEquals(pin.p1.x, -10)
        self.assertEquals(pin.p1.y, 60)
        ## connect_end
        self.assertEquals(pin.p2.x, -20)
        self.assertEquals(pin.p2.y, 60)

    def test__parse_command(self):
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
        })
        self.assertEquals(len(params), 5)

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
        design = self.geda_parser.parse('./test/geda/embedded_component.sch')

        components = design.components.components #test components dictionary
        self.assertEquals(components.keys(), ['EMBEDDEDbattery-1'])

        component = components['EMBEDDEDbattery-1']
        self.assertEquals(component.name, 'EMBEDDEDbattery-1')

        keys = ['p1x', 'p1y', 'p2x', 'p2y', 'num', 'seq', 'label', 'type']
        expected_pins = [
            dict(zip(keys, [0, 200, 200, 200, '1', 1, '+', 'pwr'])),
            dict(zip(keys, [700, 200, 500, 200, '2', 2, '-', 'pwr'])),
        ]
        for pin, expected_pin in zip(component.symbols[0].bodies[0].pins, expected_pins):
            self.assertEquals(pin.label.text, expected_pin['label'])
            ## test reversed pin order due to different handling in direction
            self.assertEquals(pin.p1.x, expected_pin['p2x'] / self.geda_parser.SCALE_FACTOR)
            self.assertEquals(pin.p1.y, expected_pin['p2y'] / self.geda_parser.SCALE_FACTOR)
            self.assertEquals(pin.p2.x, expected_pin['p1x'] / self.geda_parser.SCALE_FACTOR)
            self.assertEquals(pin.p2.y, expected_pin['p1y'] / self.geda_parser.SCALE_FACTOR)
            
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
        for pin, expected_pin in zip(component.symbols[0].bodies[0].pins, expected_pins):
            self.assertEquals(pin.label.text, expected_pin['label'])
            ## test reversed pin order due to different handling in direction
            self.assertEquals(pin.p1.x, expected_pin['p2x'] / self.geda_parser.SCALE_FACTOR)
            self.assertEquals(pin.p1.y, expected_pin['p2y'] / self.geda_parser.SCALE_FACTOR)
            self.assertEquals(pin.p2.x, expected_pin['p1x'] / self.geda_parser.SCALE_FACTOR)
            self.assertEquals(pin.p2.y, expected_pin['p1y'] / self.geda_parser.SCALE_FACTOR)
            
            self.assertEquals(pin.pin_number, expected_pin['num'])

    def test_parse_component_data(self):
        """ Tests parsing component data from symbol files and embedded 
            sections.
        """ 
        self.geda_parser = GEDA([
            './test/geda/simple_example/symbols',
        ])
        
        fpath = open('test/geda/path.sch')
        component = self.geda_parser.parse_component_data(fpath, {
            'basename': 'test.sym',
        })
        fpath.close()

        self.assertEquals(component.name, 'test')
        self.assertEquals(len(component.symbols), 1)
        self.assertEquals(len(component.symbols[0].bodies), 1)
        self.assertEquals(len(component.symbols[0].bodies[0].shapes), 9)

    def test_parse_full(self):
        """ Test parsing a complete schematic file generating OpenJSON. """
        self.geda_parser = GEDA([
            './test/geda/simple_example/symbols',
        ])

        design = self.geda_parser.parse('test/geda/simple_example/simple_example.sch')
        
        self.assertEquals(len(design.nets), 2)

        net_names = [net.net_id for net in design.nets]
        self.assertEquals(
            sorted(net_names),
            sorted(['+_1', '-_In+']),
        )
