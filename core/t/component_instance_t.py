#!/usr/bin/python
# encoding: utf-8
""" The annotation test class """

from core.component_instance import ComponentInstance
from core.component_instance import SymbolAttribute
import unittest


class ComponentInstanceTests(unittest.TestCase):
    """ The tests of the core module instance feature """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_instance(self):
        """ Test the creation of a new empty instance. """
        inst = ComponentInstance('001', '002', '003')
        assert inst.instance_id == '001'
        assert inst.library_id == '002'
        assert inst.symbol_index == '003'
        assert len(inst.symbol_attributes) == 0
        assert len(inst.attributes) == 0


class SymbolAttributeTests(unittest.TestCase):
    """ The tests of the core module symbol feature """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_attribute(self):
        """ Test the creation of a new empty symbol. """
        attr = SymbolAttribute(0, 1, 2)
        assert attr.x == 0
        assert attr.y == 1
        assert attr.rotation == 2
        assert len(attr.annotations) == 0
