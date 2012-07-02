# encoding: utf-8
#pylint: disable=R0904
""" The kicad writer test class """

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


from upconvert.writer.kicad import KiCAD
from upconvert.core.design import Design
from upconvert.core.components import Pin
from upconvert.core.net import Net, NetPoint
from upconvert.core.component_instance import ComponentInstance, SymbolAttribute
from upconvert.core.shape import Label, Rectangle, Polygon, Arc, BezierCurve
from upconvert.core.annotation import Annotation
from upconvert.parser.openjson import JSON

import os
import unittest
import tempfile

from cStringIO import StringIO


from upconvert.parser.t.kicad_t import GOOD_OUTPUT_FILE as TEST_UPV_FILE


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
        os.remove(filename)

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
                         'Text Label 11 -22 900 60 ~ 0\ntest\n')

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
P 33 -44
\t1    33 -44
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
            'Wire Wire Line\n\t0 0 0 -11\nWire Wire Line\n\t0 0 11 0\n')

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
            line, 'X ~ 1 -6667 1111 3333 R 60 60 %(unit)d %(convert)d B\n')

        pin = Pin('1', (300, 100), (600, 100))
        line = writer.get_pin_line(pin)
        self.assertEqual(
            line, 'X ~ 1 6667 1111 3333 L 60 60 %(unit)d %(convert)d B\n')

        pin = Pin('2', (0, -1300), (0, -1500))
        line = writer.get_pin_line(pin)
        self.assertEqual(
            line, 'X ~ 2 0 -16667 2222 U 60 60 %(unit)d %(convert)d B\n')

        pin = Pin('2', (0, 1300), (0, 1500))
        line = writer.get_pin_line(pin)
        self.assertEqual(
            line, 'X ~ 2 0 16667 2222 D 60 60 %(unit)d %(convert)d B\n')

        pin = Pin('2', (0, 1300), (0, 1500),
                  Label(0, 0, 'name', 'center', 0))
        line = writer.get_pin_line(pin)
        self.assertEqual(
            line, 'X name 2 0 16667 2222 D 60 60 %(unit)d %(convert)d B\n')

    def test_write_library_footer(self):
        """
        The write_library_footer produces the correct string.
        """

        writer = KiCAD()
        buf = StringIO()
        writer.write_library_footer(buf)
        self.assertEqual(buf.getvalue(), '#\n#End Library\n')


    def test_rectangle(self):
        """
        Rectangles are output correctly.
        """

        writer = KiCAD()
        rect = Rectangle(10, 20, 5, 10)
        line = writer.get_shape_line(rect)
        self.assertEqual(line, 'S 111 222 167 111 %(unit)d %(convert)d 0 N\n')


    def test_polygon(self):
        """
        Polygons are output correctly.
        """

        writer = KiCAD()
        poly = Polygon()
        poly.add_point(0, 0)
        poly.add_point(0, 10)
        poly.add_point(10, 10)
        poly.add_point(10, 0)
        line = writer.get_shape_line(poly)
        self.assertEqual(line, 'P 5 %(unit)d %(convert)d 0 0 0 0 111 111 111 111 0 0 0 N\n')


    def test_arc(self):
        """
        Arcs are output correctly.
        """

        writer = KiCAD()
        arc = Arc(0, 0, -0.5, 0.5, 1)
        line = writer.get_shape_line(arc)
        self.assertEqual(line, 'A 0 0 11 900 -900 %(unit)d %(convert)d 0 N\n')


    def test_bezier_curve(self):
        """
        BezierCurves are output correctly.
        """

        writer = KiCAD()
        bezier = BezierCurve((0, 0), (1, 1), (2, 2), (3, 3))
        line = writer.get_shape_line(bezier)
        self.assertEqual(line, 'P 2 %(unit)d %(convert)d 0 22 22 33 33 N\n')
