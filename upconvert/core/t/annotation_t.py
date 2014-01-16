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


from upconvert.core.annotation import Annotation
import unittest


class AnnotationTests(unittest.TestCase):
    """ The tests of the core module annotation feature """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_annotation(self):
        """ Test the creation of a new empty annotation. """
        anno = Annotation('abc', 0, 1, 2, False)
        assert anno.value == 'abc'
        assert anno.x == 0
        assert anno.y == 1
        assert anno.rotation == 2
        assert anno.visible != True

    def test_annotation_bounds(self):
        '''Test .bounds()'''
        annot = Annotation('foo', 3, 6, 0, True)
        top_left, bottom_right = annot.bounds()
        # bounds() will give a square with sides 20 units long, centered on the
        # annotation
        self.assertEqual(top_left.x, 3 - 10)
        self.assertEqual(top_left.y, 6 - 10)
        self.assertEqual(bottom_right.x, 3 + 10)
        self.assertEqual(bottom_right.y, 6 + 10)
