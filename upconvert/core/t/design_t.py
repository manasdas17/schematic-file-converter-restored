#!/usr/bin/python
# encoding: utf-8
#pylint: disable=R0904
""" The design test class """

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


from upconvert.core.design import Design
from upconvert.core.net import Net
from upconvert.core.shape import Point
from upconvert.core.annotation import Annotation
from upconvert.core.components import Component, Symbol, SBody
from upconvert.core.component_instance import ComponentInstance, SymbolAttribute
import unittest


def mkbounds(obj, left, top, right, bot):
    """ Helper function for testing bounds. """
    def newbounds():
        """ Function that gets returned"""
        return [Point(left, top), Point(right, bot)]
    obj.bounds = newbounds


class DesignTests(unittest.TestCase):
    """ The tests of the core module design feature """

    def setUp(self):
        """ Setup the test case. """
        self.des = Design()

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_design(self):
        """ Test the creation of a new empty design. """
        self.assertEqual(len(self.des.nets), 0)

    def test_empty_bounds(self):
        '''bounds() on an empty design is to include just the origin'''
        for point in self.des.bounds():
            self.assertEqual(point.x, 0)
            self.assertEqual(point.y, 0)

    def test_bounds_nets(self):
        '''Test bounds() with just the design's nets'''
        leftnet = Net('foo1')
        topnet = Net('foo2')
        rightnet = Net('foo3')
        botnet = Net('foo4')
        # limits minx=2, miny=1, maxx=7, maxy=9
        mkbounds(leftnet, 2, 3, 3, 3)
        mkbounds(topnet, 3, 1, 3, 3)
        mkbounds(rightnet, 3, 3, 7, 3)
        mkbounds(botnet, 3, 3, 3, 9)
        self.des.add_net(topnet)
        self.des.add_net(rightnet)
        self.des.add_net(leftnet)
        self.des.add_net(botnet)

        top_left, btm_right = self.des.bounds()
        self.assertEqual(top_left.x, 2)
        self.assertEqual(top_left.y, 1)
        self.assertEqual(btm_right.x, 7)
        self.assertEqual(btm_right.y, 9)

    def test_bounds_annots(self):
        '''Test bounds() with just Annotations added as design attributes'''
        left = Annotation('foo1', 3, 3, 0, True)
        top = Annotation('foo2', 3, 3, 0, True)
        right = Annotation('foo3', 3, 3, 0, True)
        bot = Annotation('foo4', 3, 3, 0, True)
        mkbounds(left, 2, 3, 3, 3)
        mkbounds(top, 3, 2, 3, 3)
        mkbounds(right, 3, 3, 5, 3)
        mkbounds(bot, 3, 3, 3, 6)
        for anno in (left, right, bot, top):
            self.des.design_attributes.add_annotation(anno)

        top_left, btm_right = self.des.bounds()
        self.assertEqual(top_left.x, 2)
        self.assertEqual(top_left.y, 2)
        self.assertEqual(btm_right.x, 5)
        self.assertEqual(btm_right.y, 6)

    def test_bounds_parts(self):
        '''test bounds() with just components in the design'''
        libcomp = Component('bar')
        libcomp.add_symbol(Symbol())
        libcomp.symbols[0].add_body(SBody())
        mkbounds(libcomp.symbols[0].bodies[0], 0, 0, 10, 10)
        self.des.add_component('foo', libcomp)
        for (x, y) in ((1, 3), (3, 2), (5, 3), (3, 7)):
            compinst = ComponentInstance(str((x, y)), libcomp, 'foo', 0)
            compinst.add_symbol_attribute(SymbolAttribute(x, y, 0, False))
            self.des.add_component_instance(compinst)

        top_left, btm_right = self.des.bounds()
        self.assertEqual(top_left.x, 1)
        self.assertEqual(top_left.y, 2)
        self.assertEqual(btm_right.x, 15)
        self.assertEqual(btm_right.y, 17)

    def test_bounds_neg_coords(self):
        '''Test bounds() when the schematic is all negative coordinates'''
        net = Net('foo')
        mkbounds(net, -1, -2, -3, -4)
        self.des.add_net(net)

        top_left, btm_right = self.des.bounds()
        self.assertEqual(top_left.x, -3)
        self.assertEqual(top_left.y, -4)
        self.assertEqual(btm_right.x, -1)
        self.assertEqual(btm_right.y, -2)

    def test_bounds_all_elts(self):
        '''bounds() with all the elements competing'''
        net = Net('foo')
        mkbounds(net, 3, 3, -1, -2)
        self.des.add_net(net)

        annot = Annotation('foo', 3, 3, 0, True)
        mkbounds(annot, 3, 3, 3, 5)
        self.des.design_attributes.add_annotation(annot)

        libcomp = Component('bar')
        libcomp.add_symbol(Symbol())
        libcomp.symbols[0].add_body(SBody())
        mkbounds(libcomp.symbols[0].bodies[0], 0, 0, 3, 3)
        self.des.add_component('foo', libcomp)

        compinst = ComponentInstance('bar', libcomp, 'foo', 0)
        compinst.add_symbol_attribute(SymbolAttribute(3, 0, 0, False))
        self.des.add_component_instance(compinst)

        top_left, btm_right = self.des.bounds()
        self.assertEqual(top_left.x, -1)
        self.assertEqual(top_left.y, -2)
        self.assertEqual(btm_right.x, 6)
        self.assertEqual(btm_right.y, 5)
