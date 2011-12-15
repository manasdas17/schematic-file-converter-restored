import unittest
import StringIO

from parser.geda import GEDA, GEDAParserError
from parser.openjson import JSON

#TEST_INPUT_FILE = join(dirname(__file__), 'test.sch')
#GOOD_OUTPUT_FILE = join(dirname(__file__), 'test.upv')


class TestGEDA(unittest.TestCase):

    def setUp(self):
        self.geda_parser = GEDA()

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
        params = text_stream.readline().split(' ')[1:]
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
        params = text_stream.readline().split(' ')[1:]
        annotation = self.geda_parser.convert_text(text_stream, *params)

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
        raise NotImplementedError()

    def test_parse_embedded_component(self):
        raise NotImplementedError()

    def test_parse_component(self):
        raise NotImplementedError()

    def test_parse_segement(self):
        raise NotImplementedError()

    def test_parse_bus(self):
        raise NotImplementedError()

    def test_parse_path(self):
        raise NotImplementedError()

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
        raise NotImplementedError()

    def test_parse_box(self):
        raise NotImplementedError()

    def test_parse_circle(self):
        raise NotImplementedError()

    def test_parse_pin(self):
        raise NotImplementedError()

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

if __name__ == '__main__':
    unittest.main()
