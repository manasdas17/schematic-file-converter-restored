import os
import unittest
import StringIO

from parser.geda import GEDA, GEDAParserError
from parser.openjson import JSON


class TestGEDA(unittest.TestCase):

    def setUp(self):
        self.geda_parser = GEDA()
        ## for easier validation 
        self.geda_parser.SCALE_FACTOR = 10

    def test_constructor(self):
        geda_parser = GEDA()
        self.assertEquals(len(geda_parser.known_symbols), 0)

        geda_parser = GEDA([
            './test/geda/simple_example/symbols',
            '/invalid/dir/gEDA',
        ])

        self.assertEquals(len(geda_parser.known_symbols), 1)
        self.assertEquals(
            geda_parser.known_symbols['opamp.sym'],
            './test/geda/simple_example/symbols/opamp.sym'
        )

        geda_parser = GEDA([
            './test/geda/simple_example/symbols',
            '/usr/share/gEDA/sym',
            '/invalid/dir/gEDA',
        ])

        self.assertGreater(len(geda_parser.known_symbols), 0)
        self.assertTrue('title-B.sym' in geda_parser.known_symbols)

    def test_parse_text(self):
        valid_text = """T 16900 35800 3 10 1 0 0 0 1
Text string!"""

        text_stream = StringIO.StringIO(valid_text)
        typ, params =  self.geda_parser.parse_element(text_stream)
        success, annotation = self.geda_parser.parse_text(text_stream, *params)

        self.assertEquals(success, None)
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
        success, annotation = self.geda_parser.parse_text(text_stream, *params)

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
            (3429, 342),
            (0, 0),
            (-50, -5),
            (-1238, -123),
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

    def test_calculate_nets(self):
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
        design = self.geda_parser.parse_schematic(stream)

        ## check nets from design
        self.assertEquals(len(design.nets), 3)

        self.assertEquals(
            sorted([net.net_id for net in design.nets]),
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



    def test_parse_buses_from_stream(self):
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
        design = self.geda_parser.parse_schematic(stream)

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


    def test_parse_segment(self):
        simple_segment = "N 47300 48500 43500 48500 4"

        self.geda_parser.segments = set()
        self.geda_parser.net_points = dict()
        self.geda_parser.net_names = dict()

        stream = StringIO.StringIO(simple_segment)
        typ, params = self.geda_parser.parse_element(stream)
        self.geda_parser.parse_segment(stream, *params)

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

    def test_parse_path(self):
        simple_example = """H 3 0 0 0 -1 -1 1 -1 -1 -1 -1 -1 5
M 510,240
L 601,200
L 555,295
L 535,265
z"""

        stream = StringIO.StringIO(simple_example)
        typ, params = self.geda_parser.parse_element(stream)
        self.assertEquals(typ, 'H')

        shapes = self.geda_parser.parse_path(stream, *params)
        
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


        curve_example = """H 3 0 0 0 -1 -1 0 2 20 100 -1 -1 6
M 100,100
L 500,100
C 700,100 800,275 800,400
C 800,500 700,700 500,700
L 100,700
z"""
        stream = StringIO.StringIO(curve_example)
        typ, params = self.geda_parser.parse_element(stream)
        self.assertEquals(typ, 'H')

        shapes = self.geda_parser.parse_path(stream, *params)

        self.assertEquals(len(shapes), 5)

        expected_shapes = ['line', 'bezier', 'bezier', 'line', 'line']
        for shape, expected in zip(shapes, expected_shapes):
            self.assertEquals(shape.type, expected)

    def test_segment_from_ripper(self):
        pass
        #samples = [
        #    [46800, 46900, 1, 180, 0, 'busripper-1.sym']
        #    [46800, 46500, 1, 180, 0, 'busripper-1.sym']
        #    [46400, 46700, 1, 270, 1, 'busripper-1.sym']
        #    [47000, 46000, 1, 270, 0, 'busripper-1.sym']
        #    [46500, 45600, 1, 0, 0, 'busripper-1.sym']
        #]
        #expected = [
        #    [
        #]
        #self.geda_parser.segment_from_ripper(


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
            self.assertEquals(pin.label.text, '+')
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

    def test_parse(self):
        self.geda_parser = GEDA([
            '/usr/share/gEDA/sym',
            './test/geda/simple_example/symbols',
        ])

        ## testing EMBEDDED component
        design = self.geda_parser.parse('./test/geda/embedded_component.sch')

        components = design.components.components #test components dictionary
        self.assertEquals(components.keys(), ['EMBEDDEDbattery-1.sym'])

        component = components['EMBEDDEDbattery-1.sym']
        self.assertEquals(component.name, 'EMBEDDEDbattery-1.sym')

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
        self.assertEquals(components.keys(), ['battery-1.sym'])

        component = components['battery-1.sym']
        self.assertEquals(component.name, 'battery-1.sym')

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



    def test_parse_full(self):
        self.geda_parser = GEDA([
            '/usr/share/gEDA/sym',
            './test/geda/simple_example/symbols',
        ])

        design = self.geda_parser.parse('test/geda/simple_example/simple_example.sch')
        
        self.assertEquals(len(design.nets), 2)

        net_names = [net.net_id for net in design.nets]
        self.assertEquals(
            sorted(net_names),
            sorted(['+_1', '-_In+']),
        )

if __name__ == '__main__':
    unittest.main()
