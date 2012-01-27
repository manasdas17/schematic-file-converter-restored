#!/usr/bin/python
# encoding: utf-8
#pylint: disable=R0904
""" The shape test class """

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


from core.shape import Shape
from core.shape import Rectangle
from core.shape import RoundedRectangle
from core.shape import Arc
from core.shape import Circle
from core.shape import Label
from core.shape import Line
from core.shape import Polygon
from core.shape import RegularPolygon
from core.shape import Moire
from core.shape import Thermal
from core.shape import BezierCurve
from core.shape import Point
import unittest


class ShapeTests(unittest.TestCase):
    """ The tests of the core module shape feature """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_shape(self):
        """ Test the creation of a new empty shape. """
        shp = Shape()
        assert shp.type == None


class RectangleTests(unittest.TestCase):
    """ The tests of the core module rectangle shape """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_rectangle(self):
        """ Test the creation of a new empty rectangle. """
        rect = Rectangle(0, 1, 2, 3)
        assert rect.x == 0
        assert rect.y == 1
        assert rect.width == 2
        assert rect.height == 3


class RoundedRectangleTests(unittest.TestCase):
    """ The tests of the core module rounded rectangle shape """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_rounded(self):
        """ Test the creation of a new empty rounded rectangle. """
        rrect = RoundedRectangle(0, 1, 2, 3, 4)
        assert rrect.x == 0
        assert rrect.y == 1
        assert rrect.width == 2
        assert rrect.height == 3
        assert rrect.radius == 4


class ArcTests(unittest.TestCase):
    """ The tests of the core module arc shape """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_arc(self):
        """ Test the creation of a new empty arc. """
        arc = Arc(0, 1, 2, 3, 4)
        assert arc.x == 0
        assert arc.y == 1
        assert arc.start_angle == 2
        assert arc.end_angle == 3
        assert arc.radius == 4


class CircleTests(unittest.TestCase):
    """ The tests of the core module circle shape """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_circle(self):
        """ Test the creation of a new empty circle. """
        cir = Circle(0, 1, 2)
        assert cir.x == 0
        assert cir.y == 1
        assert cir.radius == 2


class LabelTests(unittest.TestCase):
    """ The tests of the core module label shape """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_label(self):
        """ Test the creation of a new empty label. """
        lbl = Label(0, 1, 'abc', 'left', 2)
        assert lbl.x == 0
        assert lbl.y == 1
        assert lbl.text == 'abc'
        assert lbl.align == 'left'
        assert lbl.rotation == 2


class LineTests(unittest.TestCase):
    """ The tests of the core module line shape """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_line(self):
        """ Test the creation of a new empty line. """
        p1 = Point(0, 1)
        p2 = Point(2, 3)
        line = Line(p1, p2)
        assert line.p1.x == p1.x
        assert line.p1.y == p1.y
        assert line.p2.x == p2.x
        assert line.p2.y == p2.y


class PolygonTests(unittest.TestCase):
    """ The tests of the core module polygon shape """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_polygon(self):
        """ Test the creation of a new empty polygon. """
        poly = Polygon()
        assert len(poly.points) == 0


class RegularPolygonTests(unittest.TestCase):
    """ The tests of the core module regular polygon shape. """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_regular_polygon(self):
        """ Test creating a new regular polygon. """
        rpoly = RegularPolygon(x=0,
                               y=0,
                               outer=5,
                               vertices=5)
        assert rpoly.x == 0
        assert rpoly.y == 0
        assert rpoly.outer_diameter == 5
        assert rpoly.vertices == 5
        assert rpoly.rotation == 0


class MoireTests(unittest.TestCase):
    """ The tests of the core module moire shape. """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_moire(self):
        """ Test the creation of a new Moire. """
        moire = Moire(x=0,
                      y=0,
                      outer=6,
                      ring_thickness=1.5,
                      gap=1,
                      max_rings=2,
                      hair_thickness=0.2,
                      hair_length=6,
                      rotation=0)
        assert moire.x == 0
        assert moire.y == 0
        assert moire.outer_diameter == 6
        assert moire.ring_thickness == 1.5
        assert moire.gap_thickness == 1
        assert moire.max_rings == 2
        assert moire.hair_thickness == 0.2
        assert moire.hair_length == 6
        assert moire.rotation == 0


class ThermalTests(unittest.TestCase):
    """ The tests of the core module thermal shape. """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_thermal(self):
        """ Test the creation of a new thermal. """
        thermal = Thermal(x=0,
                          y=0,
                          outer=5,
                          inner=3,
                          gap=2)
        assert thermal.x == 0
        assert thermal.y == 0
        assert thermal.outer_diameter == 5
        assert thermal.inner_diameter == 3
        assert thermal.gap_thickness == 2
        assert thermal.rotation == 0


class BezierCurveTests(unittest.TestCase):
    """ The tests of the core module bezier shape """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_bezier_curve(self):
        """ Test the creation of a new empty bezier. """
        control1 = Point(0, 1)
        control2 = Point(2, 3)
        p1 = Point(4, 5)
        p2 = Point(6, 7)
        curve = BezierCurve(control1, control2, p1, p2)
        assert curve.control1.x == control1.x
        assert curve.control1.y == control1.y
        assert curve.control2.x == control2.x
        assert curve.control2.y == control2.y
        assert curve.p1.x == p1.x
        assert curve.p1.y == p1.y
        assert curve.p2.x == p2.x
        assert curve.p2.y == p2.y


class PointTests(unittest.TestCase):
    """ The tests of the core module point feature. """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_point(self):
        """ Test the creation of a new empty point. """
        pnt = Point(0, 1)
        assert pnt.x == 0
        assert pnt.y == 1

    def test_create_point_from_tuple(self):
        '''Test Point constructor using a tuple as only argument'''
        pnt = Point((2, 3))
        self.assertEqual(pnt.x, 2)
        self.assertEqual(pnt.y, 3)

    def test_create_point_from_point(self):
        '''Test Point constructor when cloning another point'''
        oldpnt = Point(2, 3)
        newpnt = Point(oldpnt)
        self.assertIsNot(oldpnt, newpnt)
        self.assertEqual(oldpnt.x, newpnt.x)
        self.assertEqual(oldpnt.y, newpnt.y)
        oldpnt.x = 4
        oldpnt.y = 5
        self.assertEqual(newpnt.x, 2)
        self.assertEqual(newpnt.y, 3)

    def test_point_equality(self):
        '''pt1 == pt2 iff (pt1.x == pt2.x and pt1.y == pt2.y)'''
        pta = Point(2, 3)
        ptb = Point(2, 3)
        ptc = Point(2, 4)
        ptd = Point(4, 3)
        pte = Point(4, 5)
        self.assertEqual(pta, ptb)
        for pt in (ptc, ptd, pte):
            self.assertNotEqual(pta, pt)

    def test_point_repr(self):
        '''repr(Point) --> Point($x, $y)'''
        pt = Point(8, 7)
        self.assertEqual(repr(pt), 'Point(8, 7)')
        pt = Point(-3, -4)
        self.assertEqual(repr(pt), 'Point(-3, -4)')
