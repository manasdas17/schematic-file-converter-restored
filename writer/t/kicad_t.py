# encoding: utf-8
""" The kicad writer test class """

from writer.kicad import KiCAD
from core.design import Design
from core.components import Pin
from core.net import Net, NetPoint
from core.component_instance import ComponentInstance, SymbolAttribute
from core.shape import Label
from core.annotation import Annotation
from parser.openjson import JSON

import os
import unittest
import tempfile

from cStringIO import StringIO


from parser.t.kicad_t import GOOD_OUTPUT_FILE as TEST_UPV_FILE


class KiCADTests(unittest.TestCase):
    """ The tests of the kicad writer """

    def test_write(self):
        """
        We can write out a complete design file.
        """

        design = JSON().parse(TEST_UPV_FILE)
        writer = KiCAD()
        filedesc, filename = tempfile.mkstemp()
        os.close(filedesc)
        os.remove(filename)
        writer.write(design, filename)
        self.assertTrue(os.path.exists(filename))

    def test_write_header(self):
        """
        The write_header method produces the right string.
        """

        design = Design()
        design.design_attributes.metadata.updated_timestamp = 0
        writer = KiCAD()
        buf = StringIO()
        writer.write_header(buf, design)
        self.assertEqual(buf.getvalue()[:40], 'EESchema Schematic File Version 2  date ')

    def test_write_libs(self):
        """
        The write_libs method produces the right string.
        """

        writer = KiCAD()
        buf = StringIO()
        writer.write_libs(buf, 'test-cache.sch')
        self.assertEqual(buf.getvalue(), 'LIBS:test-cache\n')

    def test_write_eelayer(self):
        """
        The write_eelayer method produces the correct string.
        """

        writer = KiCAD()
        buf = StringIO()
        writer.write_eelayer(buf)
        self.assertEqual(buf.getvalue(), 'EELAYER 25  0\nEELAYER END\n')

    def test_write_annotation(self):
        """
        The write_annotation method produces the correct string.
        """

        writer = KiCAD()
        buf = StringIO()
        ann = Annotation('test', 1, 2, .5, 'true')
        writer.write_annotation(buf, ann)
        self.assertEqual(buf.getvalue(),
                         'Text Label 1 -2 900 60 ~ 0\ntest\n')

    def test_write_instance(self):
        """
        The write_instance method serializes a component instance
        correctly.
        """

        inst = ComponentInstance('id', 'libid', 1)
        inst.add_symbol_attribute(SymbolAttribute(3, 4, 0.5))
        writer = KiCAD()
        buf = StringIO()
        writer.write_instance(buf, inst)
        self.assertEqual(buf.getvalue(), '''\
$Comp
L libid id
U 1 1 00000000
P 3 -4
\t1    3 -4
\t0    1    1    0
$EndComp
''')

    def test_write_net(self):
        """
        The write_net method creates the correct kicad wires from an
        openjson net.
        """

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
            'Wire Wire Line\n\t0 0 0 -1\nWire Wire Line\n\t0 0 1 0\n')

    def test_write_footer(self):
        """
        The write_footer method produces the correct string.
        """

        writer = KiCAD()
        buf = StringIO()
        writer.write_footer(buf)
        self.assertEqual(buf.getvalue(), '$EndSCHEMATC\n')

    def test_get_pin_line(self):
        """
        The get_pin_line returns the correct string for a kicad pin.
        """

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

        pin = Pin('2', (0, 1300), (0, 1500),
                  Label(0, 0, 'name', 'center', 0))
        line = writer.get_pin_line(pin)
        self.assertEqual(
            line, 'X name 2 0 1500 200 D 60 60 %(unit)d %(convert)d B\n')

    def test_write_library_footer(self):
        """
        The write_library_footer produces the correct string.
        """

        writer = KiCAD()
        buf = StringIO()
        writer.write_library_footer(buf)
        self.assertEqual(buf.getvalue(), '#\n#End Library\n')
