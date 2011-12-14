#!/usr/bin/python
# encoding: utf-8
from core.component_instance import ComponentInstance
from core.component_instance import SymbolAttribute
import unittest


class ComponentInstanceTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_component_instance(self):
        inst = ComponentInstance('001', '002', '003')
        assert inst.instance_id == '001'
        assert inst.library_id == '002'
        assert inst.symbol_index == '003'
        assert len(inst.symbol_attributes) == 0
        assert len(inst.attributes) == 0


class SymbolAttributeTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_symbol_attribute(self):
        attr = SymbolAttribute(0, 1, 2)
        assert attr.x == 0
        assert attr.y == 1
        assert attr.rotation == 2
        assert len(attr.annotations) == 0
