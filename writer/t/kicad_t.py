# encoding: utf-8
from writer.kicad import KiCAD
from core.design import Design
from core.components import Pin
from core.net import Net, NetPoint
from core.component_instance import ComponentInstance, SymbolAttribute
import unittest

from cStringIO import StringIO


class KiCADTests(unittest.TestCase):

    def test_create_new_kicad_writer(self):
        assert KiCAD() is not None

    def test_write_header(self):
        design = Design()
        design.design_attributes.metadata.updated_timestamp = 0
        writer = KiCAD()
        buf = StringIO()
        writer.write_header(buf, design)
        self.assertEqual(buf.getvalue()[:40], 'EESchema Schematic File Version 2  date ')

    def test_write_libs(self):
        writer = KiCAD()
        buf = StringIO()
        writer.write_libs(buf, 'test.sch')
        self.assertEqual(buf.getvalue(), 'LIBS:test-cache\n')

    def test_write_eelayer(self):
        writer = KiCAD()
        buf = StringIO()
        writer.write_eelayer(buf)
        self.assertEqual(buf.getvalue(), 'EELAYER 25  0\nEELAYER END\n')

    def test_write_instance(self):
        inst = ComponentInstance('id', 'libid', 1)
        inst.add_symbol_attribute(SymbolAttribute(3, 4, 0.5))
        writer = KiCAD()
        buf = StringIO()
        writer.write_instance(buf, inst)
        self.assertEqual(buf.getvalue(), '''\
$Comp
L libid id
U 1 1 00000000
P 3 4
\t1    3 4
\t0    1    1    0
$EndComp
''')

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

    def test_get_pin_line(self):
        writer = KiCAD()

        pin = Pin('1', (-300, 100), (-600, 100))
        line = writer.get_pin_line(pin)
        self.assertEqual(
            line, 'X ~ 1 -600 100 300 R 60 60 %(unit)d %(convert)d B\n')

        pin = Pin('1', (300, 100), (600, 100))
        line = writer.get_pin_line(pin)
        self.assertEqual(
            line, 'X ~ 1 600 100 300 L 60 60 %(unit)d %(convert)d B\n')

        pin = Pin('2', (0, -1300), (0, -1500))
        line = writer.get_pin_line(pin)
        self.assertEqual(
            line, 'X ~ 2 0 -1500 200 U 60 60 %(unit)d %(convert)d B\n')

        pin = Pin('2', (0, 1300), (0, 1500))
        line = writer.get_pin_line(pin)
        self.assertEqual(
            line, 'X ~ 2 0 1500 200 D 60 60 %(unit)d %(convert)d B\n')

    def test_write_library_footer(self):
        writer = KiCAD()
        buf = StringIO()
        writer.write_library_footer(buf)
        self.assertEqual(buf.getvalue(), '#\n#End Library\n')
