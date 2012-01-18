#!/usr/bin/python
# encoding: utf-8
""" The gerber parser test class """

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

from os import path
import unittest

from nose.tools import raises

from parser.gerber import Gerber, DelimiterMissing, ParamContainsBadData, \
                            CoordPrecedesFormatSpec, CoordMalformed, \
                            FileNotTerminated, DataAfterEOF, \
                            UnintelligibleDataBlock

STRIP_DIRS = path.join('parser', 't')
BASE_DIR = path.dirname(__file__).split(STRIP_DIRS)[0]
TEST_FILES = path.join('test', 'gerber')
DIR = path.join(BASE_DIR, TEST_FILES)

class GerberTests(unittest.TestCase):
    """ The tests of the gerber parser """

    def setUp(self):
        """ Setup the test case. """
        self.design = None

    def tearDown(self):
        """ Teardown the test case. """
        pass


    # decorator for tests that use input files

    def use_file(filename):                             # pylint: disable=E0213
        """ Parse a gerber file. """
        def wrap_wrap_tm(test_method):
            """ Add params to decorator function. """
            def wrap_tm(self):
                """ Perform meta operations, then method. """
                parser = Gerber(path.join(DIR, filename))
                self.design = parser.parse()
                test_method(self)

            # correctly identify the decorated method
            # (otherwise nose will not run the test)
            wrap_tm.__name__ = test_method.__name__
            wrap_tm.__doc__ = test_method.__doc__
            wrap_tm.__dict__.update(test_method.__dict__)
            wrap_wrap_tm.__name__ = wrap_tm.__name__
            wrap_wrap_tm.__doc__ = wrap_tm.__doc__
            wrap_wrap_tm.__dict__.update(wrap_tm.__dict__)

            return wrap_tm
        return wrap_wrap_tm


    # tests that pass if no errors are raised

    def test_create_new_gerber_parser(self):
        """ Create an empty gerber parser. """
        parser = Gerber()
        assert parser != None

    @use_file('simple.ger')
    def test_simple(self):
        """ Parse a simple, correct gerber file. """
        assert len(self.design.layouts[0].layers[0].traces) == 2

    @use_file('arc_segments.ger')
    def test_arcs(self):
        """ Parse some connected arcs and lines - gerber. """
        assert len(self.design.layouts[0].layers[0].traces) == 2


    # tests that pass if they raise expected errors

    @raises(DelimiterMissing)
    @use_file('missing-delim.ger')
    def test_missing_delim(self):
        """ Trap param outside of gerber param block. """
        pass

    @raises(CoordPrecedesFormatSpec)
    @use_file('coord-precedes-fs.ger')
    def test_coord_preceding_fs(self):
        """ Trap coord preceding gerber format spec. """
        pass

    @raises(ParamContainsBadData)
    @use_file('coord-in-param-block.ger')
    def test_data_in_param(self):
        """ Trap coord inside gerber param block. """
        pass

    @raises(CoordMalformed)
    @use_file('y-precedes-x.ger')
    def test_y_before_x(self):
        """ Trap coord with 'Y' before 'X' - gerber. """
        pass

    @raises(DataAfterEOF)
    @use_file('data-after-eof.ger')
    def test_trailing_data(self):
        """ Trap data following M02* block - gerber. """
        pass

    @raises(FileNotTerminated)
    @use_file('not-terminated.ger')
    def test_no_eof(self):
        """ Trap file with no M02* block - gerber. """
        pass

    @raises(UnintelligibleDataBlock)
    @use_file('alien.ger')
    def test_alien_data(self):
        """ Trap off-spec data in gerber file. """
        pass
