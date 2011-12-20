
import os
import unittest
import tempfile

from core import net 
from core import shape
from core import components 
from writer.geda import GEDA, GEDAWriterError

class TestGEDA(unittest.TestCase):

    def setUp(self):
        self.geda_writer = GEDA()

    def test_create_project_files(self):
        geda_filename = '/tmp/test_geda.sch'

        self.geda_writer.create_project_files(geda_filename)

        self.assertEquals(
            self.geda_writer.project_dirs['project'], 
            '/tmp'
        )
        self.assertEquals(
            self.geda_writer.project_dirs['symbol'], 
            '/tmp/symbols'
        )
        self.assertTrue(os.path.exists('/tmp/gafrc'))
        
        fh = open('/tmp/gafrc', 'r')
        data = ''.join(fh.readlines())
        fh.close()
        self.assertEquals(data, '(component-library "./symbols")') 

    def test_create_component(self):
        component = self.geda_writer._create_component(0, 0, 'test-1.sym')
        self.assertEquals(
            component,
            'C 0 0 0 0 0 test-1.sym'
        )

    def test_create_attribute(self):
        attribute = self.geda_writer._create_attribute('_refdes', 'U1', 0, 0) 
        self.assertEquals(
            attribute,
            ['T 0 0 5 10 0 0 0 0 1', 'refdes=U1']
        )
        attribute = self.geda_writer._create_attribute('refdes', 'U1', 0, 0, size=25) 
        self.assertEquals(
            attribute,
            ['T 0 0 5 25 1 0 0 0 1', 'refdes=U1']
        )

    def test_create_text(self):
        text = self.geda_writer._create_text('some text', 0, 0)
        self.assertEquals(len(text), 2)
        self.assertEquals(
            text,
            ['T 0 0 9 10 1 0 0 0 1', 'some text']
        )

        text = self.geda_writer._create_text(
            "some text\nmulti line\ntext", 
            0, 0, size=25, visibility=0, alignment=8,
        )
        self.assertEquals(len(text), 4)
        self.assertEquals(
            text,
            ['T 0 0 9 25 0 0 0 8 3', "some text", "multi line", "text"]
        )

    def test_create_pin(self):
        pin = components.Pin('E', (0, 0), (0, 30))
        command = self.geda_writer._create_pin(1, pin) 

        self.assertEquals(
            command,
            [
                'P 0 300 0 0 1 0 0', 
                '{',
                'T 100 400 5 10 0 0 0 0 1',
                'pinseq=1',
                'T 100 500 5 10 0 0 0 0 1',
                'pinnumber=E',
                '}'
            ]
        )

        label = shape.Label(10, 0, 'p1', 'left', 0.5)

        pin = components.Pin('E', (0, 0), (0, 30), label=label)
        command = self.geda_writer._create_pin(1, pin) 

        self.assertEquals(
            command,
            [
                'P 0 300 0 0 1 0 0', 
                '{',
                'T 100 0 5 10 1 0 90 0 1',
                'pinlabel=p1',
                'T 100 400 5 10 0 0 0 0 1',
                'pinseq=1',
                'T 100 500 5 10 0 0 0 0 1',
                'pinnumber=E',
                '}'
            ]
        )


    def test_create_arc(self):
        arc = shape.Arc(0, 0, 0.0, 0.7, 30)
        command = self.geda_writer._create_arc(arc)
        
        self.assertEquals(
            command,
            ['A 0 0 300 0 125 3 0 0 0 -1 -1'] 
        )

        arc = shape.Arc(200, 400, 1.0, 0.5, 10)
        command = self.geda_writer._create_arc(arc)
        
        self.assertEquals(
            command,
            ['A 2000 4000 100 180 270 3 0 0 0 -1 -1'] 
        )

        arc = shape.Arc(200, 400, 0.2, 0.1, 10)
        command = self.geda_writer._create_arc(arc)
        
        self.assertEquals(
            command,
            ['A 2000 4000 100 36 342 3 0 0 0 -1 -1'] 
        )

    def test_create_circle(self):
        circle = shape.Circle(0, 0, 300)
        command = self.geda_writer._create_circle(circle)

        self.assertEquals(
            command,
            ['V 0 0 3000 3 0 0 0 -1 -1 0 -1 -1 -1 -1 -1']
        )

        circle = shape.Circle(10, 30, 10)
        command = self.geda_writer._create_circle(circle)

        self.assertEquals(
            command,
            ['V 100 300 100 3 0 0 0 -1 -1 0 -1 -1 -1 -1 -1']
        )

    def test_create_box(self):
        rect = shape.Rectangle(0, 0, 40, 50)
        command = self.geda_writer._create_box(rect)

        self.assertEquals(
            command,
            ['B -500 0 400 500 3 0 0 0 -1 -1 0 -1 -1 -1 -1 -1']
        )

        rect = shape.Rectangle(100, 50, 150, 30)
        command = self.geda_writer._create_box(rect)

        self.assertEquals(
            command,
            ['B 700 500 1500 300 3 0 0 0 -1 -1 0 -1 -1 -1 -1 -1']
        )

        rect = shape.RoundedRectangle(0, 0, 40, 50, 0.5)
        command = self.geda_writer._create_box(rect)

        self.assertEquals(
            command,
            ['B -500 0 400 500 3 0 0 0 -1 -1 0 -1 -1 -1 -1 -1']
        )

        rect = shape.RoundedRectangle(100, 50, 150, 30, 0.1)
        command = self.geda_writer._create_box(rect)

        self.assertEquals(
            command,
            ['B 700 500 1500 300 3 0 0 0 -1 -1 0 -1 -1 -1 -1 -1']
        )

    def test_create_line(self):
        line = shape.Line((0, 0), (0, 50))
        command = self.geda_writer._create_line(line)
        self.assertEquals(
            command,
            ['L 0 0 0 500 3 0 0 0 -1 -1']
        )

        line = shape.Line((20, 40), (-20, 40))
        command = self.geda_writer._create_line(line)
        self.assertEquals(
            command,
            ['L 200 400 -200 400 3 0 0 0 -1 -1']
        )

        line = shape.Line((20, 40), (-30, 50))
        command = self.geda_writer._create_line(line)
        self.assertEquals(
            command,
            ['L 200 400 -300 500 3 0 0 0 -1 -1']
        )

    def test_create_segment(self):
        np1 = net.NetPoint('0a0', 0, 0)
        np2 = net.NetPoint('0a10', 0, 10)
        self.assertEquals(
            self.geda_writer._create_segment(np1, np2),
            ['N 0 0 0 100 4']
        )
        np1 = net.NetPoint('100a40', 100, 40)
        np2 = net.NetPoint('50a40', 50, 40)
        attrs = {'netname': 'test_net'}
        self.assertEquals(
            self.geda_writer._create_segment(np1, np2, attributes=attrs),
            [
                'N 1000 400 500 400 4',
                '{',
                'T 1100 500 5 10 1 0 0 0 1',
                'netname=test_net',
                '}',
            ]
        )

    def test_create_path(self):
        self.assertRaises(
            GEDAWriterError,
            self.geda_writer._create_path,
            components.Symbol()
        )

        self.assertRaises(
            GEDAWriterError,
            self.geda_writer._create_path,
            components.Body().add_shape(shape.Circle(0, 0, 20))
        )

        polygon = shape.Polygon()
        polygon.add_point((0, 0))
        polygon.add_point((100, 200))
        polygon.add_point((150, 200))
        polygon.add_point((200, 100))

        self.assertEquals(
            self.geda_writer._create_path(polygon),
            [
                'H 3 0 0 0 -1 -1 1 -1 -1 -1 -1 -1 5',
                'M 0,0',
                'L 1000,2000',
                'L 1500,2000',
                'L 2000,1000',
                'z'
            ]
        )
    
        curve = shape.BezierCurve((9, -10), (11, -10), (3, -12), (17, -12))

        self.assertEquals(
            self.geda_writer._create_path(curve),
            [
                'H 3 0 0 0 -1 -1 1 -1 -1 -1 -1 -1 2',
                'M 30,-120',
                'C 90,-100 110,-100 170,-120',
            ]
        )

        shapes = [
            shape.Line((10, 10), (50, 10)),
            shape.BezierCurve((70, 10), (80, 30), (50, 10), (80, 40)),
            shape.BezierCurve((80, 50), (70, 70), (80, 40), (50, 70)),
            shape.Line((50, 70), (10, 70)),
        ]
        
        body = components.Body()
        body.shapes = shapes

        self.assertEquals(
            self.geda_writer._create_path(body),
            [
                'H 3 0 0 0 -1 -1 1 -1 -1 -1 -1 -1 5',
                'M 100,100',
                'L 500,100',
                'C 700,100 800,300 800,400',
                'C 800,500 700,700 500,700',
                'L 100,700',
            ]
        )

        body.add_shape(shape.Line((10, 70), (10, 10)))

        self.assertEquals(
            self.geda_writer._create_path(body),
            [
                'H 3 0 0 0 -1 -1 1 -1 -1 -1 -1 -1 6',
                'M 100,100',
                'L 500,100',
                'C 700,100 800,300 800,400',
                'C 800,500 700,700 500,700',
                'L 100,700',
                'z',
            ]
        )

    def test_is_valid_path(self):
        shapes = [
            shape.Line((10, 10), (50, 10)), #L 500,100
            shape.BezierCurve((70, 10), (80, 30), (50, 10), (80, 40)), #C 700,100 800,300 800,400
            shape.BezierCurve((80, 50), (70, 70), (80, 40), (50, 70)), #C 800,500 700,700 500,700
            shape.Line((50, 70), (10, 70)), #L 100,700
        ]
        
        body = components.Body()
        body.shapes = shapes
        self.assertTrue(self.geda_writer.is_valid_path(body))

        body.add_shape(shape.Line((10, 70), (10, 10)))
        self.assertTrue(self.geda_writer.is_valid_path(body))

        shapes = [
            shape.Line((10, 10), (50, 10)), #L 500,100
            shape.BezierCurve((70, 10), (80, 30), (50, 10), (80, 40)), #C 700,100 800,300 800,400
            shape.Line((50, 70), (10, 70)), #L 100,700
        ]
        body.shapes = shapes
        self.assertFalse(self.geda_writer.is_valid_path(body))

        body.add_shape(shape.Circle(0, 0, 10))
        self.assertFalse(self.geda_writer.is_valid_path(body))

    def test_conv_angle(self):
        angle_samples = [
            # angle, steps, expected result
            (0.0, 1, 0),
            (0.0, 10.0, 0),
            (0.5, 90, 90),
            (0.7,  1, 125), 
            (0.7,  90, 90), 
            (1.8,  1, 324), 
            (1.5,  1, 270), 
            (1.5,  90, 270),
        ]

        for angle, steps, expected in angle_samples:
            self.assertEquals(
                self.geda_writer.conv_angle(angle, steps), 
                expected
            )

