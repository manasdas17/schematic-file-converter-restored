#!/usr/bin/python
# encoding: utf-8
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

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_shape(self):
        shp = Shape()
        assert shp.type == None


class RectangleTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_rectangle(self):
        rect = Rectangle(0, 1, 2, 3)
        assert rect.x == 0
        assert rect.y == 1
        assert rect.width == 2
        assert rect.height == 3


class RoundedRectangleTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_rounded_rectangle(self):
        rrect = RoundedRectangle(0, 1, 2, 3, 4)
        assert rrect.x == 0
        assert rrect.y == 1
        assert rrect.width == 2
        assert rrect.height == 3
        assert rrect.radius == 4


class ArcTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_arc(self):
        arc = Arc(0, 1, 2, 3, 4)
        assert arc.x == 0
        assert arc.y == 1
        assert arc.start_angle == 2
        assert arc.end_angle == 3
        assert arc.radius == 4


class CircleTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_circle(self):
        cir = Circle(0, 1, 2)
        assert cir.x == 0
        assert cir.y == 1
        assert cir.radius == 2


class LabelTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_label(self):
        lbl = Label(0, 1, 'abc', 'left', 2)
        assert lbl.x == 0
        assert lbl.y == 1
        assert lbl.text == 'abc'
        assert lbl.align == 'left'
        assert lbl.rotation == 2


class LineTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_line(self):
        p1 = Point(0, 1)
        p2 = Point(2, 3)
        line = Line(p1, p2)
        assert line.p1.x == p1.x
        assert line.p1.y == p1.y
        assert line.p2.x == p2.x
        assert line.p2.y == p2.y


class PolygonTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_polygon(self):
        poly = Polygon()
        assert len(poly.points) == 0


class BezierCurveTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_bezier_curve(self):
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

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_point(self):
        pnt = Point(0, 1)
        assert pnt.x == 0
        assert pnt.y == 1
