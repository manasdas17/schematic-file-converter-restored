#!/usr/bin/python
# encoding: utf-8
#pylint: disable=R0904
""" The shape test class """

# upconvert - A universal hardware design file format converter using
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


from upconvert.core.shape import Shape
from upconvert.core.shape import Rectangle
from upconvert.core.shape import RoundedRectangle
from upconvert.core.shape import Arc
from upconvert.core.shape import Circle
from upconvert.core.shape import Label
from upconvert.core.shape import Line
from upconvert.core.shape import Polygon
from upconvert.core.shape import RegularPolygon
from upconvert.core.shape import Moire
from upconvert.core.shape import Thermal
from upconvert.core.shape import BezierCurve
from upconvert.core.shape import Point
import unittest
from math import sin, cos, pi


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

    def test_create_rect_from_corners(self):
        '''Test for Rectangle.from_corners()'''
        rect = Rectangle.from_corners(0, 1, 2, 4)
        self.assertEqual(rect.x, 0)
        self.assertEqual(rect.y, 1)
        self.assertEqual(rect.width, 2)
        self.assertEqual(rect.height, 3)

    def test_rectangle_min_point(self):
        '''Test Rectangle.min_point()'''
        rect = Rectangle(-2, -3, 8, 5)
        top_left = rect.min_point()
        self.assertEqual(top_left.x, -2)
        self.assertEqual(top_left.y, -3)

    def test_rectangle_max_point(self):
        '''Test Rectangle.max_point()'''
        rect = Rectangle(-2, -3, 8, 5)
        bottom_right = rect.max_point()
        self.assertEqual(bottom_right.x, 6)
        self.assertEqual(bottom_right.y, 2)

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

    def test_create_rnd_frm_corners(self):
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
        top_left = rrect.min_point()
        self.assertEqual(top_left.x, -2)
        self.assertEqual(top_left.y, -3)

    def test_rrectangle_max_point(self):
        '''Test RoundedRectangle.max_point()'''
        rrect = RoundedRectangle(-2, -3, 8, 5, 6)
        bottom_right = rrect.max_point()
        self.assertEqual(bottom_right.x, 6)
        self.assertEqual(bottom_right.y, 2)

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

    def test_min_point_arc_is_circle(self):
        '''min_point() when an arc actually traces out a full circle'''
        arc = Arc(2, 3, 0, 2, 5)
        self.assertEqual(arc.min_point().x, -3)
        self.assertEqual(arc.min_point().y, -2)

    def test_max_point_arc_is_circle(self):
        '''max_point() when an arc actually traces out a full circle'''
        arc = Arc(2, 3, 0, 2, 5)
        self.assertEqual(arc.max_point().x, 7)
        self.assertEqual(arc.max_point().y, 8)

    def test_min_point_arc(self):
        """min_point() of an arc tracing top-left quarter"""
        arc = Arc(2, 3, 1, 1.5, 5)
        self.assertEqual(arc.min_point().x, -3)
        self.assertEqual(arc.min_point().y, -2)

    def test_max_point_arc(self):
        """max_point() of an arc tracing bottom-right quarter"""
        arc = Arc(2, 3, 0, 0.5, 5)
        self.assertEqual(arc.max_point().x, 7)
        self.assertEqual(arc.max_point().y, 8)
        
    def test_min_point_arc_wraparound(self):
        """min_point() of an arc that traces through 0 degrees"""
        arc = Arc(2, 3, 1.75, 0.25, 5)
        self.assertEqual(arc.min_point().x, int(round(cos(1.75 * pi) * 5 + 2)))
        self.assertEqual(arc.min_point().y, int(round(sin(1.75 * pi) * 5 + 3)))

    def test_max_point_arc_wraparound(self):
        """max_point() of an arc that traces through 0 degrees"""
        arc = Arc(2, 3, 1.75, 0.25, 5)
        self.assertEqual(arc.max_point().x, 5 + 2)
        self.assertEqual(arc.max_point().y, int(round(sin(0.25 * pi) * 5 + 3)))

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
        top_left = cir.min_point()
        self.assertEqual(top_left.x, -2)
        self.assertEqual(top_left.y, -1)

    def test_circle_max_point(self):
        '''Test Circle.max_point()'''
        cir = Circle(2, 3, 4)
        bottom_right = cir.max_point()
        self.assertEqual(bottom_right.x, 6)
        self.assertEqual(bottom_right.y, 7)


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
        lbl = Label(0, 1, 'abc', align='left', rotation=2)
        assert lbl.x == 0
        assert lbl.y == 1
        assert lbl.text == 'abc'
        assert lbl.align == 'left'
        assert lbl._rotation == 2

    def test_label_min_point(self):
        '''Test Label.min_point()'''
        #lbl = Label(2, 1, 'foo', 'left', 0)
        # this will fail, until Labels get min/max_point() methods
        #top_left = lbl.min_point()
        # TODO change this to work with however Label.min_point() does
        #self.assertTrue(False)

    def test_label_max_point(self):
        '''Test Label.max_point()'''
        #lbl = Label(2, 1, 'foo', 'left', 0)
        # this will fail, until Labels get min/max_point() methods
        #top_left = lbl.max_point()
        # TODO change this to work with however Label.max_point() does
        #self.assertTrue(False)

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
        line = Line(Point(2, 3), Point(4, 5))
        top_left = line.min_point()
        self.assertEqual(top_left.x, 2)
        self.assertEqual(top_left.y, 3)

        line = Line(Point(2, 3), Point(-1, 4))
        top_left = line.min_point()
        self.assertEqual(top_left.x, -1)
        self.assertEqual(top_left.y, 3)

    def test_line_max_point(self):
        '''Test Line.max_point() in different situations'''
        line = Line(Point(2, 3), Point(4, 5))
        bottom_right = line.max_point()
        self.assertEqual(bottom_right.x, 4)
        self.assertEqual(bottom_right.y, 5)

        line = Line(Point(2, 3), Point(-1, 4))
        bottom_right = line.max_point()
        self.assertEqual(bottom_right.x, 2)
        self.assertEqual(bottom_right.y, 4)

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
        for _xy in [(1, 3), (3, 7), (4, 3), (3, -2)]:
            self.poly.add_point(_xy)
        self.assertEqual(self.poly.min_point().x, 1)
        self.assertEqual(self.poly.min_point().y, -2)

    def test_max_point(self):
        '''Test Polygon.max_point() for complex case'''
        for _xy in [(1, 3), (3, 7), (4, 3), (3, -2)]:
            self.poly.add_point(_xy)
        self.assertEqual(self.poly.max_point().x, 4)
        self.assertEqual(self.poly.max_point().y, 7)


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
        self.curve = BezierCurve((2, 9), (9, 8), (1, 1), (7, 2))

    def tearDown(self):
        """ Teardown the test case. """
        del self.curve

    def test_create_new_bezier_curve(self):
        """ Test the creation of a new empty bezier. """
        control1 = Point(2, 9)
        control2 = Point(9, 8)
        p1 = Point(1, 1)
        p2 = Point(7, 2)
        assert self.curve.control1.x == control1.x
        assert self.curve.control1.y == control1.y
        assert self.curve.control2.x == control2.x
        assert self.curve.control2.y == control2.y
        assert self.curve.p1.x == p1.x
        assert self.curve.p1.y == p1.y
        assert self.curve.p2.x == p2.x
        assert self.curve.p2.y == p2.y


    def interp_bezier(self, points, typ):
        return tuple([int(round(((1 - typ) ** 3) * pts[0]
                                + 3 * ((1 - typ) ** 2) * typ * pts[1]
                                + 3 * (1 - typ) * (typ ** 2) * pts[2]
                                + (typ ** 3) * pts[3]))
                      for pts in ([pt.x for pt in points],
                                  [pt.y for pt in points])])
    

    def bez_recurse(self, pts, lo, hi):
        """Helper method to draw a bezier curve"""
        # kind of important that we don't just copy how it's done in the method
        # to be tested, so do it by recusively bisecting the curve until we hit
        # the necessary resolution
        [plo, phi] = [self.interp_bezier(pts, typ) for typ in (lo, hi)]
        if abs(plo[0] - phi[0]) <= 1 and abs(plo[1] - phi[1]) <= 1:
            return [plo, phi]
        mid = (lo + hi) / 2.
        bot_half = self.bez_recurse(pts, lo, mid)
        top_half = self.bez_recurse(pts, mid, hi)
        if bot_half[-1] == top_half[0]:
            bot_half = bot_half[:-1]
        return bot_half + top_half


    def test_bezier_min_point(self):
        points = self.bez_recurse([self.curve.p1, self.curve.control1,
                                   self.curve.control2, self.curve.p2], 0., 1.)
        x = min([pt[0] for pt in points])
        y = min([pt[1] for pt in points])
        min_pt = self.curve.min_point()
        self.assertEqual(min_pt.x, x)
        self.assertEqual(min_pt.y, y)


    def test_bezier_max_point(self):
        points = self.bez_recurse([self.curve.p1, self.curve.control1,
                                   self.curve.control2, self.curve.p2], 0., 1.)
        x = max([pt[0] for pt in points])
        y = max([pt[1] for pt in points])
        max_pt = self.curve.max_point()
        self.assertEqual(max_pt.x, x)
        self.assertEqual(max_pt.y, y)


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
        self.assertFalse(oldpnt is newpnt)
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
        self.assertEqual(repr(pt), 'Point(x=8, y=7)')
        pt = Point(-3, -4)
        self.assertEqual(repr(pt), 'Point(x=-3, y=-4)')
