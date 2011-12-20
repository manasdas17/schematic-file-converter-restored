
import os
import unittest
import tempfile

from core import shape
from core import components 
from writer.geda import GEDA

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
            ['T 0 0 9 10 0 0 0 0 1', 'refdes=U1']
        )
        attribute = self.geda_writer._create_attribute('refdes', 'U1', 0, 0, size=25) 
        self.assertEquals(
            attribute,
            ['T 0 0 9 25 1 0 0 0 1', 'refdes=U1']
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
                'T 100 400 9 10 0 0 0 0 1',
                'pinseq=1',
                'T 100 500 9 10 0 0 0 0 1',
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
                'T 100 0 9 10 1 0 90 0 1',
                'pinlabel=p1',
                'T 100 400 9 10 0 0 0 0 1',
                'pinseq=1',
                'T 100 500 9 10 0 0 0 0 1',
                'pinnumber=E',
                '}'
            ]
        )


    #def test_create_arc(self):
    #    raise NotImplementedError()

    #def test_create_circle(self):
    #    raise NotImplementedError()

    #def test_create_box(self):
    #    raise NotImplementedError()

    #def test_create_line(self):
    #    raise NotImplementedError()

    #def test_create_segment(self):
    #    raise NotImplementedError()

    #def test_create_path(self):
    #    raise NotImplementedError()

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

