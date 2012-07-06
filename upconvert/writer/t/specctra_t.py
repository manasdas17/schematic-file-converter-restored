# encoding: utf-8
#pylint: disable=R0904
""" The specctra writer test class """

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


from upconvert.writer.specctra import Specctra
from upconvert.core.design import Design
from upconvert.core.components import Pin
from upconvert.core.net import Net, NetPoint
from upconvert.core.component_instance import ComponentInstance, SymbolAttribute
from upconvert.core.shape import Label, Rectangle, Polygon, Arc, BezierCurve, Circle
from upconvert.core.annotation import Annotation
from upconvert.parser.openjson import JSON

import sys
import unittest
import math

def to_string(writer, obj):
    if isinstance(obj, list):
        buf = writer._to_string([o.compose() for o in obj]).replace('\n', '')
    else:
        buf = writer._to_string(obj.compose()).replace('\n', '')
    return ' '.join(buf.split())

class SpecctraTests(unittest.TestCase):
    """ The tests of the specctra writer """


    def test_write_instance(self):
        """ Convert component instance """
        inst = ComponentInstance('id', 'libid', 1)
        inst.add_symbol_attribute(SymbolAttribute(3, 4, 0.5, False))
        writer = Specctra()
        obj = writer._convert_component_instance(inst)
        self.assertEqual(
                to_string(writer, obj),
                '(component libid-1 (place id 31.250000 41.666667 front 270) )')

    def test_circle(self):
        """ Convert circle shape """

        circle = Circle(10, 20, 10)
        writer = Specctra()
        obj = writer._convert_shape(circle)
        self.assertEqual(
                to_string(writer, obj),
                '( (circle signal 208.333333 104.166667 208.333333) )')

    def test_rectangle(self):
        """ Convert rectangle shape """

        rect = Rectangle(10, 20, 5, 10)
        writer = Specctra()
        obj = writer._convert_shape(rect)
        self.assertEqual(
                to_string(writer, obj),
                '( (rect signal 104.166667 208.333333 156.250000 104.166667) )')

    def test_polygon(self):
        """ Convert polygon shape """

        poly = Polygon()
        poly.add_point(0, 0)
        poly.add_point(0, 10)
        poly.add_point(10, 10)
        poly.add_point(10, 0)
        writer = Specctra()
        obj = writer._convert_shape(poly)
        self.assertEqual(
                to_string(writer, obj), 
                '( (polygon signal 10.416667 0.000000 0.000000 0.000000 104.166667 104.166667 104.166667 104.166667 0.000000) )')

    def test_arc(self):
        """ Convert arc to lines shape """

        arc = Arc(0, 0, -0.5, 0.5, 1)
        writer = Specctra()
        obj = writer._convert_shape(arc)
        self.assertEqual(
                to_string(writer, obj), 
                '( (path signal 10.416667 -0.000000 -10.416667 -6.122763 -8.427260)' +
                    ' (path signal 10.416667 -6.122763 -8.427260 -9.906839 -3.218927)' +
                    ' (path signal 10.416667 -9.906839 -3.218927 -9.906839 3.218927)' +
                    ' (path signal 10.416667 -9.906839 3.218927 -6.122763 8.427260)' +
                    ' (path signal 10.416667 -6.122763 8.427260 -0.000000 10.416667) )')

    def test_bezier_curve(self):
        """ Convert bezier to lines shape """

        bezier = BezierCurve((0, 0), (1, 1), (2, 2), (3, 3))
        writer = Specctra()
        obj = writer._convert_shape(bezier)
        self.assertEqual(
                to_string(writer, obj),
                '( (path signal 10.416667 20.833333 20.833333 20.833333 20.833333)' +
                ' (path signal 10.416667 20.833333 20.833333 10.416667 10.416667)' +
                ' (path signal 10.416667 10.416667 10.416667 10.416667 10.416667)' +
                ' (path signal 10.416667 10.416667 10.416667 10.416667 10.416667)' +
                ' (path signal 10.416667 10.416667 10.416667 10.416667 10.416667)' +
                ' (path signal 10.416667 10.416667 10.416667 10.416667 10.416667)' +
                ' (path signal 10.416667 10.416667 10.416667 10.416667 10.416667)' +
                ' (path signal 10.416667 10.416667 10.416667 20.833333 20.833333)' +
                ' (path signal 10.416667 20.833333 20.833333 20.833333 20.833333)' +
                ' (path signal 10.416667 20.833333 20.833333 20.833333 20.833333)' +
                ' (path signal 10.416667 20.833333 20.833333 31.250000 31.250000) )')

if __name__ == '__main__':
    unittest.main()
