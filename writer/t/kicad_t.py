# encoding: utf-8
from writer.kicad import KiCAD
from core.components import Pin
import unittest

from cStringIO import StringIO


class KiCADTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_kicad_writer(self):
        assert KiCAD() is not None

    def test_write_pin(self):
        writer = KiCAD()

        buf = StringIO()
        pin = Pin('1', (-300, 100), (-600, 100))
        writer.write_pin(buf, pin)
        self.assertEqual(buf.getvalue(), 'X ~ 1 -600 100 300 R 60 60 1 1 B\n')

        buf = StringIO()
        pin = Pin('1', (300, 100), (600, 100))
        writer.write_pin(buf, pin)
        self.assertEqual(buf.getvalue(), 'X ~ 1 600 100 300 L 60 60 1 1 B\n')

        buf = StringIO()
        pin = Pin('2', (0, -1300), (0, -1500))
        writer.write_pin(buf, pin)
        self.assertEqual(buf.getvalue(), 'X ~ 2 0 -1500 200 U 60 60 1 1 B\n')

        buf = StringIO()
        pin = Pin('2', (0, 1300), (0, 1500))
        writer.write_pin(buf, pin)
        self.assertEqual(buf.getvalue(), 'X ~ 2 0 1500 200 D 60 60 1 1 B\n')
