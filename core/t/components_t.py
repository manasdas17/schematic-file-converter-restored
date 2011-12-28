#!/usr/bin/python
# encoding: utf-8
""" The component test class """

from core.components import Components
from core.components import Component
from core.components import Symbol
from core.components import Body
from core.components import Pin
from core.shape import Point, Shape, Label
import unittest


def mkbounds(obj, left, top, right, bot):
    def newbounds():
        return [Point(left, top), Point(right, bot)]
    obj.bounds = newbounds

class ComponentsTests(unittest.TestCase):
    """ The tests of the core module library feature """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_components(self):
        """ Test the creation of a new empty library. """
        lib = Components()
        assert len(lib.components) == 0


class ComponentTests(unittest.TestCase):
    """ The tests of the core module component feature """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_component(self):
        """ Test the creation of a new empty component. """
        comp = Component('abc')
        assert comp.name == 'abc'


class SymbolTests(unittest.TestCase):
    """ The tests of the core module symbol feature """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_symbol(self):
        """ Test the creation of a new empty symbol. """
        symb = Symbol()
        assert len(symb.bodies) == 0


class BodyTests(unittest.TestCase):
    """ The tests of the core module body feature """

    def setUp(self):
        """ Setup the test case. """
        self.bod = Body()

    def tearDown(self):
        """ Teardown the test case. """
        self.bod = Body()

    def test_create_new_body(self):
        """ Test the creation of a new empty body. """
        assert len(self.bod.shapes) == 0
        assert len(self.bod.pins) == 0

    def test_empty_bounds(self):
        '''Test that an empty body only bounds the local origin'''
        tl, br = self.bod.bounds()
        self.assertEqual(tl.x, 0)
        self.assertEqual(tl.y, 0)
        self.assertEqual(br.x, 0)
        self.assertEqual(br.y, 0)

    def test_bounds_pins(self):
        '''Test bounds() with just pins included'''
        pins = [Pin(str(i), Point(0,0), Point(0,0)) for i in range(4)]
        # checking body.bounds(), not the pins, so override their bounds()
        # methods
        for i, pin in enumerate(pins):
            bounds = [3] * 4
            bounds[i] = 2 * i
            mkbounds(pin, *bounds)
            self.bod.add_pin(pin)

        tl, br = self.bod.bounds()
        self.assertEqual(tl.x, 0)
        self.assertEqual(tl.y, 2)
        self.assertEqual(br.x, 4)
        self.assertEqual(br.y, 6)

    def test_bounds_shapes(self):
        '''Test Body.bounds() when the body only consists of shapes'''
        shapes = [Shape() for i in range(4)]
        for i, shape in enumerate(shapes):
            bounds = [3] * 4
            bounds[i] = 2 * i
            mkbounds(shape, *bounds)
            self.bod.add_shape(shape)

        tl, br = self.bod.bounds()
        self.assertEqual(tl.x, 0)
        self.assertEqual(tl.y, 2)
        self.assertEqual(br.x, 4)
        self.assertEqual(br.y, 6)

    def test_bounds_pins_shapes(self):
        '''Test Body.bounds() when some extremes are from pins, others shapes'''
        pt = Point(0,0)
        pin1 = Pin('foo', pt, pt)
        pin2 = Pin('bar', pt, pt)
        sh1 = Shape()
        sh2 = Shape()
        mkbounds(pin1, 3, 2, 3, 3)
        mkbounds(pin2, 3, 3, 5, 3)
        mkbounds(sh1,  3, 3, 3, 4)
        mkbounds(sh2,  1, 3, 3, 3)
        self.bod.add_pin(pin1)
        self.bod.add_pin(pin2)
        self.bod.add_shape(sh1)
        self.bod.add_shape(sh2)

        tl, br = self.bod.bounds()
        self.assertEqual(tl.x, 1)
        self.assertEqual(tl.y, 2)
        self.assertEqual(br.x, 5)
        self.assertEqual(br.y, 4)

class PinTests(unittest.TestCase):
    """ The tests of the core module pin feature """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_pin(self):
        """ Test the creation of a new empty pin. """
        p1 = Point(0, 1)
        p2 = Point(2, 3)
        pin = Pin(0, p1, p2, 'abc')
        assert pin.label == 'abc'
        assert pin.p1.x == p1.x
        assert pin.p1.y == p1.y
        assert pin.p2.x == p2.x
        assert pin.p2.y == p2.y
        assert pin.pin_number == 0

    def test_pin_bounds(self):
        '''Test bounds() for individual pins'''
        pin = Pin(0, Point(2, 5), Point(4, 3))
        tl, br = pin.bounds()
        self.assertEqual(tl.x, 2)
        self.assertEqual(tl.y, 3)
        self.assertEqual(br.x, 4)
        self.assertEqual(br.y, 5)

    def test_pin_label_bounds(self):
        '''Test bounds() for a pin with a label'''
        lab = Label(0, 0, 'foo', 'left', 0)
        mkbounds(lab, 1, 3, 2, 6)
        pin = Pin(0, Point(2, 2), Point(4, 3), lab)
        tl, br = pin.bounds()
        self.assertEqual(tl.x, 1)
        self.assertEqual(tl.y, 2)
        self.assertEqual(br.x, 4)
        self.assertEqual(br.y, 6)
