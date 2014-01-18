#!/usr/bin/python
# encoding: utf-8
#pylint: disable=R0904
""" The kicad library test class """

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


from upconvert.library.kicad import lookup_part
from upconvert.core.components import Component

from unittest import TestCase


class KicadTests(TestCase):
    """ The tests of the kicad library """

    def test_lookup_present(self):
        """ Test looking up a part that is present """

        name = 'DS18B20Z'
        libs = ['jensen', '1wire']

        found = lookup_part(name, libs)

        self.assertTrue(isinstance(found, Component))
        self.assertEqual(found.name, name)

    def test_lookup_missing(self):
        """ Test looking up a part that is missing """

        name = 'nosuchpart'
        libs = ['nosuchlib', 'jensen', '1wire']

        found = lookup_part(name, libs)

        self.assertEqual(found, None)
