#!/usr/bin/python
# encoding: utf-8
#pylint: disable=R0904
""" The layout test class """

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


from upconvert.core.shape import Circle
from upconvert.core.layout import Aperture
import unittest


class ApertureTests(unittest.TestCase):
    """ Tests of core.layout.Aperture """

    def test_eq(self):
        circle1 = Circle(0, 0, 5)
        circle2 = Circle(0, 0, 1)

        self.assertEqual(Aperture('a', circle1, circle1),
                         Aperture('b', circle1, circle1))

        self.assertEqual(Aperture('a', circle1, circle2),
                         Aperture('b', circle1, circle2))

        self.assertEqual(Aperture('a', circle1, None),
                         Aperture('b', circle1, None))

        self.assertNotEqual(Aperture('a', circle1, None),
                            Aperture('b', circle2, None))

        self.assertNotEqual(Aperture('a', circle1, circle1),
                            Aperture('b', circle1, circle2))

        self.assertNotEqual(Aperture('a', circle1, None),
                            Aperture('b', circle1, circle2))

        self.assertNotEqual(Aperture('a', circle1, circle1),
                            Aperture('b', circle1, None))
