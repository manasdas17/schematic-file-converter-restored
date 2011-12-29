#!/usr/bin/python
# encoding: utf-8
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

    def test_create_rectangle_from_corners(self):
        '''Test for Rectangle.from_corners()'''
        rect = Rectangle.from_corners(0, 1, 2, 4)
        self.assertEqual(rect.x, 0)
        self.assertEqual(rect.y, 1)
        self.assertEqual(rect.width, 2)
        self.assertEqual(rect.height, 3)

    def test_rectangle_min_point(self):
        '''Test Rectangle.min_point()'''
        rect = Rectangle(-2, -3, 8, 5)
        tl = rect.min_point()
        self.assertEqual(tl.x, -2)
        self.assertEqual(tl.y, -3)

    def test_rectangle_max_point(self):
        '''Test Rectangle.max_point()'''
        rect = Rectangle(-2, -3, 8, 5)
        br = rect.max_point()
        self.assertEqual(br.x, 6)
        self.assertEqual(br.y, 2)

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

    def test_create_rounded_from_corners(self):
        '''Test for RoundedRectangle.from_corners()'''
        rrect = RoundedRectangle.from_corners(0, 1, 2, 4, 5)
        self.assertEqual(rrect.x, 0)
        self.assertEqual(rrect.y, 1)
        self.assertEqual(rrect.width, 2)
        self.assertEqual(rrect.height, 3)
        self.assertEqual(rrect.radius, 5)

    def test_rrectangle_min_point(self):
        '''Test RoundedRectangle.min_point()'''
        rrect = RoundedRectangle(-2, -3, 8, 5, 6)
        tl = rrect.min_point()
        self.assertEqual(tl.x, -2)
        self.assertEqual(tl.y, -3)

    def test_rrectangle_max_point(self):
        '''Test RoundedRectangle.max_point()'''
        rrect = RoundedRectangle(-2, -3, 8, 5, 6)
        br = rrect.max_point()
        self.assertEqual(br.x, 6)
        self.assertEqual(br.y, 2)

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

    def test_min_point_arc_is_really_a_circle(self):
        '''min_point() when an arc actually traces out a full circle'''
        arc = Arc(2, 3, 0, 2, 5)
        self.assertEqual(arc.min_point().x, -3)
        self.assertEqual(arc.min_point().y, -2)

    def test_max_point_arc_is_really_a_circle(self):
        '''max_point() when an arc actually traces out a full circle'''
        arc = Arc(2, 3, 0, 2, 5)
        self.assertEqual(arc.max_point().x, 7)
        self.assertEqual(arc.max_point().y, 8)

    def test_min_point_arc(self):
        arc = Arc(2, 3, 0, 1.5, 5)
        self.assertEqual(arc.min_point().x, -3)
        self.assertEqual(arc.min_point().y, -2)

    def test_max_point_arc(self):
        arc = Arc(2, 3, 0, 1.5, 5)
        self.assertEqual(arc.max_point().x, 7)
        self.assertEqual(arc.max_point().y, 8)
        
    def test_min_point_arc_wraparound(self):
        arc = Arc(2, 3, 1.75, 0.25, 5)
        self.assertEqual(arc.min_point().x, 6)
        self.assertEqual(arc.min_point().y, 5)

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

    def test_circle_min_point(self):
        '''Test Circle.min_point()'''
        cir = Circle(2, 3, 4)
        tl = cir.min_point()
        self.assertEqual(tl.x, -2)
        self.assertEqual(tl.y, -1)

    def test_circle_max_point(self):
        '''Test Circle.max_point()'''
        cir = Circle(2, 3, 4)
        br = cir.max_point()
        self.assertEqual(br.x, 6)
        self.assertEqual(br.y, 7)


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

    def test_label_min_point(self):
        '''Test Label.min_point()'''
        lbl = Label(2, 1, 'foo', 'left', 0)
        # this will fail, until Labels get min/max_point() methods
        tl = lbl.min_point()
        # TODO change this to work with however Label.min_point() does
        self.assertTrue(False)

    def test_label_max_point(self):
        '''Test Label.max_point()'''
        lbl = Label(2, 1, 'foo', 'left', 0)
        # this will fail, until Labels get min/max_point() methods
        tl = lbl.max_point()
        # TODO change this to work with however Label.max_point() does
        self.assertTrue(False)

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

    def test_line_min_point(self):
        '''Test Line.min_point() in different situations'''
        line = Line(Point(2,3), Point(4,5))
        tl = line.min_point()
        self.assertEqual(tl.x, 2)
        self.assertEqual(tl.y, 3)

        line = Line(Point(2,3), Point(-1,4))
        tl = line.min_point()
        self.assertEqual(tl.x, -1)
        self.assertEqual(tl.y, 3)

    def test_line_max_point(self):
        '''Test Line.max_point() in different situations'''
        line = Line(Point(2,3), Point(4,5))
        br = line.max_point()
        self.assertEqual(br.x, 4)
        self.assertEqual(br.y, 5)

        line = Line(Point(2, 3), Point(-1,4))
        br = line.max_point()
        self.assertEqual(br.x, 2)
        self.assertEqual(br.y, 4)

class PolygonTests(unittest.TestCase):
    """ The tests of the core module polygon shape """

    def setUp(self):
        """ Setup the test case. """
        self.poly = Polygon()

    def tearDown(self):
        """ Teardown the test case. """
        del self.poly

    def test_create_new_polygon(self):
        """ Test the creation of a new empty polygon. """
        assert len(self.poly.points) == 0

    def test_empty_min_point(self):
        '''Test Polygon.min_point() for a Polygon with no points at all'''
        self.assertEqual(self.poly.min_point().x, 0)
        self.assertEqual(self.poly.min_point().y, 0)

    def test_empty_max_point(self):
        '''Test Polygon.max_point() for a Polygon with no points at all'''
        self.assertEqual(self.poly.max_point().x, 0)
        self.assertEqual(self.poly.max_point().y, 0)

    def test_min_point(self):
        '''Test Polygon.min_point() for complex case'''
        for xy in [(1,3), (3,7), (4,3), (3,-2)]:
            self.poly.add_point(xy)
        self.assertEqual(self.poly.min_point().x, 1)
        self.assertEqual(self.poly.min_point().y, -2)

    def test_max_point(self):
        '''Test Polygon.max_point() for complex case'''
        for xy in [(1,3), (3,7), (4,3), (3,-2)]:
            self.poly.add_point(xy)
        self.assertEqual(self.poly.max_point().x, 4)
        self.assertEqual(self.poly.max_point().y, 7)


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
