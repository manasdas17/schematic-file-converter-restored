#!/usr/bin/python
# encoding: utf-8
#pylint: disable=R0904
""" The layout test class """

# upconvert.py - A universal hardware design file format converter using
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


from upconvert.core.shape import Circle
from upconvert.core.layout import Aperture
import unittest


class ApertureTests(unittest.TestCase):
    """ Tests of core.layout.Aperture """

    def test_eq(self):
        c1 = Circle(0, 0, 5)
        c2 = Circle(0, 0, 1)

        self.assertEqual(Aperture('a', c1, c1),
                         Aperture('b', c1, c1))

        self.assertEqual(Aperture('a', c1, c2),
                         Aperture('b', c1, c2))

        self.assertEqual(Aperture('a', c1, None),
                         Aperture('b', c1, None))

        self.assertNotEqual(Aperture('a', c1, None),
                            Aperture('b', c2, None))

        self.assertNotEqual(Aperture('a', c1, c1),
                            Aperture('b', c1, c2))

        self.assertNotEqual(Aperture('a', c1, None),
                            Aperture('b', c1, c2))

        self.assertNotEqual(Aperture('a', c1, c1),
                            Aperture('b', c1, None))
