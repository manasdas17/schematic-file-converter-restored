# encoding: utf-8
#pylint: disable=R0904
""" The eaglexml writer test class """

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


from upconvert.parser.t.eaglexml_t import use_file
from upconvert.writer.eaglexml import EagleXML

import os
import unittest
import tempfile


class EagleXMLTests(unittest.TestCase):
    """ The tests of the eaglexml writer """

    @use_file('E1AA60D5.sch')
    def test_write(self):
        """
        We can write out a complete design file.
        """

        writer = EagleXML()
        filedesc, filename = tempfile.mkstemp()
        os.close(filedesc)
        os.remove(filename)
        writer.write(self.design, filename)
        self.assertTrue(os.path.exists(filename))
        os.remove(filename)
