#!/usr/bin/python
# encoding: utf-8
#pylint: disable=R0904
""" The annotation test class """

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


from upconvert.core.component_instance import ComponentInstance
from upconvert.core.component_instance import SymbolAttribute
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
        inst = ComponentInstance('001', None, '002', '003')
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
        attr = SymbolAttribute(0, 1, 2, False)
        assert attr.x == 0
        assert attr.y == 1
        assert attr.rotation == 2
        assert len(attr.annotations) == 0
