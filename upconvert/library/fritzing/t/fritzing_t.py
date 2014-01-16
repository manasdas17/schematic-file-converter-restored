#!/usr/bin/python
# encoding: utf-8
#pylint: disable=R0904
""" The fritzing library test class """

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


from upconvert.library.fritzing import lookup_part

from unittest import TestCase
from os.path import basename, exists


class FritzingTests(TestCase):
    """ The tests of the fritzing library """

    def test_lookup_present(self):
        """ Test looking up a part that is present """

        path = '/some/path/to/fritzing/parts/core/SMD_Diode_REC_DO.fzp'
        version = '0.6.4b.12.16.5683'

        found = lookup_part(path, version)

        self.assertEqual(basename(found), basename(path))
        self.assertTrue(exists(found))

    def test_lookup_missing(self):
        """ Test looking up a part that is missing """

        path = '/some/path/to/fritzing/parts/core/notthere.fzp'
        version = '0.6.4b.12.16.5683'

        found = lookup_part(path, version)

        self.assertEqual(found, None)
