# encoding: utf-8
from writer.kicad import KiCAD
from core.components import Pin
from core.net import Net, NetPoint
import unittest

from cStringIO import StringIO


class KiCADTests(unittest.TestCase):

    def test_create_new_kicad_writer(self):
        assert KiCAD() is not None

    def test_write_net(self):
        net = Net('')
        p1 = NetPoint('p1', 0, 0)
        p2 = NetPoint('p2', 1, 0)
        p3 = NetPoint('p3', 0, 1)

        net.add_point(p1)
        net.add_point(p2)
        net.add_point(p3)

        net.conn_point(p1, p2)
        net.conn_point(p1, p3)

        writer = KiCAD()
        buf = StringIO()
        writer.write_net(buf, net)
        self.assertEqual(
            buf.getvalue(),
            'Wire Wire Line\n\t0 0 0 1\nWire Wire Line\n\t0 0 1 0\n')

    def test_write_footer(self):
        writer = KiCAD()
        buf = StringIO()
        writer.write_footer(buf)
        self.assertEqual(buf.getvalue(), '$EndSCHEMATC\n')

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

    def test_write_library_footer(self):
        writer = KiCAD()
        buf = StringIO()
        writer.write_library_footer(buf)
        self.assertEqual(buf.getvalue(), '#\n#End Library\n')
