#!/usr/bin/python
# encoding: utf-8
from core.components import Components
from core.components import Component
from core.components import Symbol
from core.components import Body
from core.components import Pin
from core.shape import Point
import unittest


class ComponentsTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_components(self):
        lib = Components()
        assert len(lib.components) == 0


class ComponentTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_component(self):
        comp = Component('abc')
        assert comp.name == 'abc'


class SymbolTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_symbol(self):
        symb = Symbol()
        assert len(symb.bodies) == 0


class BodyTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_body(self):
        bod = Body()
        assert len(bod.shapes) == 0
        assert len(bod.pins) == 0


class PinTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_pin(self):
        p1 = Point(0, 1)
        p2 = Point(2, 3)
        pin = Pin(0, p1, p2, 'abc')
        assert pin.label == 'abc'
        assert pin.p1.x == p1.x
        assert pin.p1.y == p1.y
        assert pin.p2.x == p2.x
        assert pin.p2.y == p2.y
        assert pin.pin_number == 0
