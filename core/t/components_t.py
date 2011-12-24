#!/usr/bin/python
# encoding: utf-8
""" The component test class """

from core.components import Components
from core.components import Component
from core.components import Symbol
from core.components import Body
from core.components import Pin
from core.shape import Point
import unittest


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
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_body(self):
        """ Test the creation of a new empty body. """
        bod = Body()
        assert len(bod.shapes) == 0
        assert len(bod.pins) == 0


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
