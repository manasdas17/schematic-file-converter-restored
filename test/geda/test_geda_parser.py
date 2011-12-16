import os
import unittest
import StringIO

from parser.geda import GEDA, GEDAParserError
from parser.openjson import JSON

#TEST_INPUT_FILE = join(dirname(__file__), 'test.sch')
#GOOD_OUTPUT_FILE = join(dirname(__file__), 'test.upv')


class TestGEDA(unittest.TestCase):

    def setUp(self):
        self.geda_parser = GEDA()
        ## for easier validation 
        self.geda_parser.SCALE_FACTOR = 10

    def test_constructor(self):
        geda_parser = GEDA()
        self.assertEquals(len(geda_parser.symbol_lookup), 0)

        geda_parser = GEDA([
            './test/geda/simple_example/symbols',
            '/invalid/dir/gEDA',
        ])

        self.assertEquals(len(geda_parser.symbol_lookup), 1)
        self.assertEquals(
            geda_parser.symbol_lookup['opamp.sym'],
            './test/geda/simple_example/symbols/opamp.sym'
        )

        geda_parser = GEDA([
            './test/geda/simple_example/symbols',
            '/usr/share/gEDA/sym',
            '/invalid/dir/gEDA',
        ])

        self.assertGreater(len(geda_parser.symbol_lookup), 0)
        self.assertTrue('title-B.sym' in geda_parser.symbol_lookup)

    def test_parse_text(self):
        valid_text = """T 16900 35800 3 10 1 0 0 0 1
Text string!"""

        text_stream = StringIO.StringIO(valid_text)
        typ, params =  self.geda_parser.parse_element(text_stream)
        annotation = self.geda_parser.parse_text(text_stream, *params)

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
        typ, params =  self.geda_parser.parse_element(text_stream)
        annotation = self.geda_parser.parse_text(text_stream, *params)

        text = """Text string!
And more ...
and more ...
text!"""
        self.assertEquals(annotation.value, text)
        self.assertEquals(annotation.x, 1690)
        self.assertEquals(annotation.y, 3580)
        self.assertEquals(annotation.visible, 'true')
        self.assertEquals(annotation.rotation, 0)

    def test_conv_angle(self):
        angles = [
            (0, 0), 
            (90, 0.5), 
            (180, 1.0), 
            (220, 1.2), 
            (270, 1.5), 
        ]
    
        for angle, expected in angles:
            converted = self.geda_parser.conv_angle(angle)
            self.assertEquals(expected, converted)

    def test_conv_bool(self):
        for test_bool in ['1', 1, True, 'true']:
            self.assertEquals('true', self.geda_parser.conv_bool(test_bool))

        for test_bool in ['0', 0, False, 'false']:
            self.assertEquals('false', self.geda_parser.conv_bool(test_bool))

    def test_conv_mils(self):
        test_mils = [
            (2, 0),
            (100, 10),
            (3429, 340),
            (0, 0),
            (-50, 0),
            (-1238, -120),
        ]

        for mils, expected in test_mils:
            self.assertEquals(
                self.geda_parser.conv_mils(mils),
                expected
            )

    def test_parse_environment(self):
        no_env = "P 100 600 200 600 1 0 0"
        stream = StringIO.StringIO(no_env)
        attributes = self.geda_parser.parse_environment(stream)
        self.assertEquals(attributes, None)
        self.assertEquals(stream.tell(), 0)

        valid_env = """{
W 150 650 5
T 150 650 5 8 1 1 0 6 1
pinnumber=3
T 150 650 5 8 0 1 0 6 1
pinseq=3
T 250 500 9 16 0 1 0 0 1
pinlabel=+=?
T 150 550 5 8 0 1 0 8 1
_sometype=in
}"""
        expected_attributes = {
            'pinnumber': '3',
            'pinseq': '3',
            'pinlabel': '+=?',
            '_sometype': 'in',
        }
        stream = StringIO.StringIO(valid_env)
        attributes = self.geda_parser.parse_environment(stream)

        self.assertEquals(attributes, expected_attributes)

    #def test_parse_embedded_component(self):
    #    raise NotImplementedError()

    #def test_parse_component(self):
    #    raise NotImplementedError()

    def test_calculate_nets(self):
        net_sample = """N 52100 44400 54300 44400 4
N 53200 45100 53200 43500 4
N 55000 44400 56600 44400 4
N 55700 45100 55700 44400 4
N 55700 44400 55700 43500 4"""

        self.geda_parser.segments = set()
        self.geda_parser.net_points = dict()

        stream = StringIO.StringIO(net_sample)
        self.geda_parser.parse_stream(stream)

        self.geda_parser.divide_segments()

        self.assertEquals(len(self.geda_parser.segments), 6)

        nets = self.geda_parser.calculate_nets(self.geda_parser.segments)

        self.assertEquals(len(nets), 3)


    def test_parse_segment(self):
        simple_segment = "N 47300 48500 43500 48500 4"

        self.geda_parser.segments = set()
        self.geda_parser.net_points = dict()

        stream = StringIO.StringIO(simple_segment)
        typ, params = self.geda_parser.parse_element(stream)
        self.geda_parser.parse_segment(stream, *params)

        segment = self.geda_parser.segments.pop()
        self.assertEquals(segment, ((4730, 4850), (4350, 4850)))

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

        stream = StringIO.StringIO(complex_segment)
        typ, params = self.geda_parser.parse_element(stream)
        self.geda_parser.parse_segment(stream, *params)

        expected_points = [(4730, 4850), (4350, 4850)]
        for x, y in expected_points:
            point = self.geda_parser.net_points[(x, y)]
            self.assertEquals(point.point_id, '%da%d' % (x, y))
            self.assertEquals(point.x, x)
            self.assertEquals(point.y, y)

    #def test_parse_bus(self):
    #    raise NotImplementedError()

    #def test_parse_path(self):
    #    raise NotImplementedError()

    def test_parse_arc(self):
        typ, params =  self.geda_parser.parse_element(
            StringIO.StringIO("A 41100 48500 1900 0 90 3 0 0 0 -1 -1")
        )
        arc_obj = self.geda_parser.parse_arc(*params)
        self.assertEquals(arc_obj.type, 'arc')
        self.assertEquals(arc_obj.x, 4110)
        self.assertEquals(arc_obj.y, 4850)
        self.assertEquals(arc_obj.radius, 190)
        self.assertEquals(arc_obj.start_angle, 0.0)
        self.assertEquals(arc_obj.end_angle, 0.5)

        typ, params =  self.geda_parser.parse_element(
            StringIO.StringIO("A 44300 49800 500 30 200 3 0 0 0 -1 -1")
        )
        arc_obj = self.geda_parser.parse_arc(*params)
        self.assertEquals(arc_obj.type, 'arc')
        self.assertEquals(arc_obj.x, 4430)
        self.assertEquals(arc_obj.y, 4980)
        self.assertEquals(arc_obj.radius, 50)
        self.assertEquals(arc_obj.start_angle, 0.2)
        self.assertEquals(arc_obj.end_angle, 1.3)


        typ, params =  self.geda_parser.parse_element(
            StringIO.StringIO("A 45100 48400 700 123 291 3 0 0 0 -1 -1")
        )
        arc_obj = self.geda_parser.parse_arc(*params)
        self.assertEquals(arc_obj.type, 'arc')
        self.assertEquals(arc_obj.x, 4510)
        self.assertEquals(arc_obj.y, 4840)
        self.assertEquals(arc_obj.radius, 70)
        self.assertEquals(arc_obj.start_angle, 0.7)
        self.assertEquals(arc_obj.end_angle, 0.3)

    def test_parse_line(self):
        test_strings = [
            "L 40800 46600 45700 46600 3 0 0 0 -1 -1",
            "L 42300 45900 42900 45500 3 0 0 0 -1 -1",
            "L 44500 45000 44100 45200 3 0 0 0 -1 -1",
        ]

        for line_string in test_strings:
            typ, params =  self.geda_parser.parse_element(
                StringIO.StringIO(line_string)
            )
            line_obj = self.geda_parser.parse_line(*params)
            self.assertEquals(line_obj.type, 'line')
            self.assertEquals(
                line_obj.p1.x, 
                params[0]/self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                line_obj.p1.y, 
                params[1]/self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                line_obj.p2.x, 
                params[2]/self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                line_obj.p2.y, 
                params[3]/self.geda_parser.SCALE_FACTOR
            )

    def test_parse_box(self):
        test_strings = [
            "B 41700 42100 2900 1500 3 0 0 0 -1 -1 0 -1 -1 -1 -1 -1",
            "B 46100 41100 1200 2600 3 0 0 0 -1 -1 0 -1 -1 -1 -1 -1",
        ]

        for rect_string in test_strings:
            typ, params =  self.geda_parser.parse_element(
                StringIO.StringIO(rect_string)
            )
            rect_obj = self.geda_parser.parse_box(*params)
            self.assertEquals(rect_obj.type, 'rectangle')
            self.assertEquals(
                rect_obj.x, 
                (params[0]+params[3])/self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                rect_obj.y, 
                params[1]/self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                rect_obj.width, 
                params[2]/self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                rect_obj.height, 
                params[3]/self.geda_parser.SCALE_FACTOR
            )


    def test_parse_circle(self):
        test_strings = [
            "V 49100 48800 900 3 0 0 0 -1 -1 0 -1 -1 -1 -1 -1",
            "V 51200 49000 400 3 0 0 0 -1 -1 0 -1 -1 -1 -1 -1",
        ]

        for circle_string in test_strings:
            typ, params =  self.geda_parser.parse_element(
                StringIO.StringIO(circle_string)
            )
            circle_obj = self.geda_parser.parse_circle(*params)
            self.assertEquals(circle_obj.type, 'circle')
            self.assertEquals(
                circle_obj.x, 
                params[0]/self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                circle_obj.y, 
                params[1]/self.geda_parser.SCALE_FACTOR
            )
            self.assertEquals(
                circle_obj.radius, 
                params[2]/self.geda_parser.SCALE_FACTOR
            )

    def test_parse_pin(self):
            stream = StringIO.StringIO('P 100 600 200 600 1 0 0\nM')
            typ, params =  self.geda_parser.parse_element(stream)
            self.assertRaises(
                GEDAParserError,
                self.geda_parser.parse_pin,
                stream, 
                *params
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
            typ, params =  self.geda_parser.parse_element(stream)
            pin = self.geda_parser.parse_pin(stream, *params)

            self.assertEquals(pin.pin_number, '3')
            self.assertEquals(pin.label, '+')
            ## null_end
            self.assertEquals(pin.p1.x, 20)
            self.assertEquals(pin.p1.y, 60)
            ## connect_end
            self.assertEquals(pin.p2.x, 10)
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
            typ, params =  self.geda_parser.parse_element(stream)
            pin = self.geda_parser.parse_pin(stream, *params)

            self.assertEquals(pin.pin_number, 'E')
            self.assertEquals(pin.label, None) 
            ## null_end
            self.assertEquals(pin.p1.x, 10)
            self.assertEquals(pin.p1.y, 60)
            ## connect_end
            self.assertEquals(pin.p2.x, 20)
            self.assertEquals(pin.p2.y, 60)

    def test_parse_element(self):
        typ, params = self.geda_parser.parse_element(StringIO.StringIO('{'))
        self.assertEquals(typ, '{')
        self.assertEquals(params, [])

        typ, params = self.geda_parser.parse_element(
            StringIO.StringIO('A 49 34 223')
        )
        self.assertEquals(typ, 'A')
        self.assertEquals(params, [49, 34, 223])
        self.assertEquals(len(params), 3)

        expected_params = [18600, 21500, 1, 0, 0, 'EMBEDDED555-1.sym']
        string = " ".join(['C'] + [str(x) for x in expected_params])
        typ, params = self.geda_parser.parse_element(
            StringIO.StringIO(string)
        )
        self.assertEquals(typ, 'C')
        self.assertEquals(params, expected_params)

    def test_parse_schematic_file(self):
        self.geda_parser = GEDA([
            '/usr/share/gEDA/sym',
            './test/geda/simple_example/symbols',
        ])

        filenames = [
            'test/geda/component.sch',
            #'test/geda/embedded_component.sch',
        ]

        for filename in filenames:
            filename = os.path.join(os.getcwd(),filename)
            self.geda_parser.parse_schematic_file(filename)

            #print self.geda_parser.design.json()

if __name__ == '__main__':
    unittest.main()
