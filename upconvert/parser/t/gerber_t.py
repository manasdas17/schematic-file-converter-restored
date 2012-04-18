#!/usr/bin/python
# encoding: utf-8
#pylint: disable=R0904
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

from upconvert.parser.gerber import Gerber, DelimiterMissing, ParamContainsBadData, \
                            CoordPrecedesFormatSpec, CoordMalformed, \
                            FileNotTerminated, DataAfterEOF, \
                            UnintelligibleDataBlock, QuadrantViolation, \
                            OpenFillBoundary, IncompatibleAperture

STRIP_DIRS = path.join('upconvert', 'parser', 't')
BASE_DIR = path.dirname(__file__).split(STRIP_DIRS)[0]
TEST_FILES = path.join('test', 'gerber', 'unittest')
DIR = path.join(BASE_DIR, TEST_FILES)


# decorator for tests that use input files

def use_file(filename):
    """ Parse a gerber file. """
    def wrap_wrap_tm(test_method):
        """ Add params to decorator function. """
        def wrap_tm(self):
            """ Perform meta operations, then method. """
            parser = Gerber(ignore_unknown=False)
            self.design = parser.parse(path.join(DIR, filename))
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


class GerberTests(unittest.TestCase):
    """ The tests of the gerber parser """

    def setUp(self):
        """ Setup the test case. """
        self.design = None

    # tests that pass if no errors are raised

    def test_create_new_gerber_parser(self):
        """ Create an empty gerber parser. """
        parser = Gerber()
        assert parser != None

    @use_file('simple.ger')
    def test_simple(self):
        """ Parse a simple, correct gerber file. """
        image = self.design.layout.layers[0].images[0]
        assert len(image.traces) == 2

    @use_file('arc_segments.ger')
    def test_arcs(self):
        """ Parse some connected arcs and lines - gerber. """
        image = self.design.layout.layers[0].images[0]
        assert len(image.traces) == 2

    @use_file('fills.ger')
    def test_outline_fills(self):
        """ Parse outline fills - gerber. """
        image = self.design.layout.layers[0].images[0]
        assert len(image.fills) == 2

    @use_file('smear.ger')
    def test_smear(self):
        """ Parse a smear - gerber. """
        image = self.design.layout.layers[0].images[0]
        assert len(image.smears) == 1

    @use_file('complex.ger')
    def test_complex(self):
        """ Parse aperture macros - gerber. """
        image = self.design.layout.layers[0].images[2]
        assert len(image.shape_instances) == 3

    @use_file('simple.zip')
    def test_zip_batch(self):
        """ Parse a batch of gerber files in a zip file. """
        assert self.design.layout.layers[0].name == 'top'

    @use_file('simple.bz2')
    def test_bz_batch(self):
        """ Parse a batch of gerber files in a bz2 tarball. """
        assert self.design.layout.layers[0].name == 'top'

    @use_file('simple.tgz')
    def test_gz_batch(self):
        """ Parse a batch of gerber files in a gz tarball. """
        assert self.design.layout.layers[0].name == 'top'


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

    @raises(QuadrantViolation)
    @use_file('sq-violation.ger')
    def test_single_quadrant(self):
        """ Trap long arc in single quadrant mode. """
        pass

    @raises(OpenFillBoundary)
    @use_file('open-fill.ger')
    def test_open_fill(self):
        """ Trap unsuccessful outline fill closure. """
        pass

    @raises(IncompatibleAperture)
    @use_file('disallowed-smear.ger')
    def test_arc_smear(self):
        """ Trap non-linear smear - gerber. """
        pass
