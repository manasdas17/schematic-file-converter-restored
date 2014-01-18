#!/usr/bin/python
# encoding: utf-8
#pylint: disable=R0904
""" The design attribute test class """

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


from upconvert.core.design_attributes import DesignAttributes
from upconvert.core.design_attributes import Metadata
import unittest


class DesignAttributesTests(unittest.TestCase):
    """ The tests of the core module attribute feature """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_attributes(self):
        """ Test the creation of a new empty design. """
        desattrs = DesignAttributes()
        assert len(desattrs.annotations) == 0


class MetadataTests(unittest.TestCase):
    """ The tests of the core module metadata feature """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_metadata(self):
        """ Test the creation of a new empty metatdata container. """
        meta = Metadata()
        assert meta.name == ''
