#!/usr/bin/python
# encoding: utf-8
#pylint: disable=R0904
""" The gerber parser test class """

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

from functools import wraps
from os import path
import unittest

from nose.tools import raises

from upconvert.parser.gerber import Gerber, DelimiterMissing, ParamContainsBadData, \
                            CoordPrecedesFormatSpec, CoordMalformed, \
                            FileNotTerminated, DataAfterEOF, \
                            UnintelligibleDataBlock, QuadrantViolation, \
                            OpenFillBoundary, IncompatibleAperture, Modifier

STRIP_DIRS = path.join('upconvert', 'parser', 't')
BASE_DIR = path.dirname(__file__).split(STRIP_DIRS)[0]
TEST_FILES = path.join('test', 'gerber', 'unittest')
DIR = path.join(BASE_DIR, TEST_FILES)


def use_file(filename):
    """ Return a decorator which will parse a gerber file
    before running the test. """

    def decorator(test_method):
        """ Add params to decorator function. """

        @wraps(test_method)
        def wrapper(self):
            """ Parse file then run test. """
            parser = Gerber(ignore_unknown=False)
            self.design = parser.parse(path.join(DIR, filename))
            test_method(self)

        return wrapper

    return decorator


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

    @use_file('macro1.ger')
    def test_macros(self):
        """ Parse simple macros. """
        macros = self.design.layout.layers[0].macros

        self.assertEqual(len(macros), 10)
        self.assertEqual(set(macros),
                         set(['MOIRE', 'POLYGON', 'POLYGON0', 'LINE2', 'LINE1',
                              'THERMAL', 'VECTOR', 'CIRCLE', 'OUTLINE',
                              'COMPOUND']))

        self.assertEqual(macros['CIRCLE'].primitives[0].shape.type, 'circle')
        self.assertEqual(macros['CIRCLE'].primitives[0].shape.radius, 0.25)

        self.assertEqual(macros['VECTOR'].primitives[0].shape.type, 'rectangle')
        self.assertEqual(macros['VECTOR'].primitives[0].shape.width, 1.25)
        self.assertEqual(macros['VECTOR'].primitives[0].shape.height, 0.05)
        self.assertEqual(macros['VECTOR'].primitives[0].shape.x, 0.0)
        self.assertEqual(macros['VECTOR'].primitives[0].shape.y, 0.025)

        self.assertEqual(macros['LINE1'].primitives[0].shape.type, 'rectangle')
        self.assertEqual(macros['LINE1'].primitives[0].shape.width, 0.3)
        self.assertEqual(macros['LINE1'].primitives[0].shape.height, 0.05)
        self.assertEqual(macros['LINE1'].primitives[0].shape.x, -0.15)
        self.assertEqual(macros['LINE1'].primitives[0].shape.y, 0.025)

        self.assertEqual(macros['LINE2'].primitives[0].shape.type, 'rectangle')
        self.assertEqual(macros['LINE2'].primitives[0].shape.width, 0.8)
        self.assertEqual(macros['LINE2'].primitives[0].shape.height, 0.5)
        self.assertEqual(macros['LINE2'].primitives[0].shape.x, 0.0)
        self.assertEqual(macros['LINE2'].primitives[0].shape.y, 0.5)

        self.assertEqual(macros['OUTLINE'].primitives[0].shape.type, 'polygon')
        self.assertEqual(len(macros['OUTLINE'].primitives[0].shape.points), 4)
        self.assertEqual(macros['OUTLINE'].primitives[0].shape.points[0].x, 0.0)
        self.assertEqual(macros['OUTLINE'].primitives[0].shape.points[0].y, 0.0)
        self.assertEqual(macros['OUTLINE'].primitives[0].shape.points[1].x, 0.0)
        self.assertEqual(macros['OUTLINE'].primitives[0].shape.points[1].y, 0.5)
        self.assertEqual(macros['OUTLINE'].primitives[0].shape.points[2].x, 0.5)
        self.assertEqual(macros['OUTLINE'].primitives[0].shape.points[2].y, 0.5)
        self.assertEqual(macros['OUTLINE'].primitives[0].shape.points[3].x, 0.5)
        self.assertEqual(macros['OUTLINE'].primitives[0].shape.points[3].y, 0.0)

        self.assertEqual(macros['POLYGON'].primitives[0].shape.type, 'regular polygon')
        self.assertEqual(macros['POLYGON'].primitives[0].shape.x, 0.0)
        self.assertEqual(macros['POLYGON'].primitives[0].shape.y, 0.0)
        self.assertEqual(macros['POLYGON'].primitives[0].shape.outer_diameter, 0.5)
        self.assertEqual(macros['POLYGON'].primitives[0].shape.vertices, 3)
        self.assertEqual(macros['POLYGON'].primitives[0].shape.rotation, 0)

        self.assertEqual(macros['POLYGON0'].primitives[0].shape.type, 'regular polygon')
        self.assertEqual(macros['POLYGON0'].primitives[0].shape.x, 0.0)
        self.assertEqual(macros['POLYGON0'].primitives[0].shape.y, 0.0)
        self.assertEqual(macros['POLYGON0'].primitives[0].shape.outer_diameter, 0.5)
        self.assertEqual(macros['POLYGON0'].primitives[0].shape.vertices, 6)
        self.assertEqual(macros['POLYGON0'].primitives[0].shape.rotation, 0)

        self.assertEqual(macros['MOIRE'].primitives[0].shape.type, 'moire')
        self.assertEqual(macros['MOIRE'].primitives[0].shape.x, 0.0)
        self.assertEqual(macros['MOIRE'].primitives[0].shape.y, 0.0)
        self.assertEqual(macros['MOIRE'].primitives[0].shape.outer_diameter, 1.0)
        self.assertEqual(macros['MOIRE'].primitives[0].shape.ring_thickness, 0.1)
        self.assertEqual(macros['MOIRE'].primitives[0].shape.gap_thickness, 0.4)
        self.assertEqual(macros['MOIRE'].primitives[0].shape.max_rings, 2.0)
        self.assertEqual(macros['MOIRE'].primitives[0].shape.hair_thickness, 0.01)
        self.assertEqual(macros['MOIRE'].primitives[0].shape.hair_length, 1.0)
        self.assertEqual(macros['MOIRE'].primitives[0].shape.rotation, 1.777777777777777777)

        self.assertEqual(macros['THERMAL'].primitives[0].shape.type, 'thermal')
        self.assertEqual(macros['THERMAL'].primitives[0].shape.x, 0.0)
        self.assertEqual(macros['THERMAL'].primitives[0].shape.y, 0.0)
        self.assertEqual(macros['THERMAL'].primitives[0].shape.outer_diameter, 1.0)
        self.assertEqual(macros['THERMAL'].primitives[0].shape.inner_diameter, 0.3)
        self.assertEqual(macros['THERMAL'].primitives[0].shape.gap_thickness, 0.01)
        self.assertEqual(macros['THERMAL'].primitives[0].shape.rotation, 2.0722222222222224)

        self.assertEqual(len(macros['COMPOUND'].primitives), 2)
        self.assertEqual(macros['COMPOUND'].primitives[0].shape.type, 'circle')
        self.assertEqual(macros['COMPOUND'].primitives[0].shape.radius, .75)
        self.assertEqual(macros['COMPOUND'].primitives[1].shape.type, 'circle')
        self.assertEqual(macros['COMPOUND'].primitives[1].shape.radius, 2.0)

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

    def test_modifier(self):
        """ The Modifier can evaluate expressions correctly. """
        modif = Modifier('1.2')
        self.assertEqual(modif.evaluate({}), 1.2)
        modif = Modifier('$1')
        self.assertEqual(modif.evaluate({1:3.2}), 3.2)
        modif = Modifier('1+1')
        self.assertEqual(modif.evaluate({}), 2)
        modif = Modifier('3-1.5')
        self.assertEqual(modif.evaluate({}), 1.5)
        modif = Modifier('2.2X3')
        self.assertAlmostEqual(modif.evaluate({}), 6.6, 3)
        modif = Modifier('4.4/2.2')
        self.assertAlmostEqual(modif.evaluate({}), 2, 2)
        modif = Modifier('1+4.4/2.2')
        self.assertAlmostEqual(modif.evaluate({}), 3, 2)
        modif = Modifier('$1+$2')
        self.assertAlmostEqual(modif.evaluate({1:1, 2:2.2}), 3.2, 2)
        modif = Modifier('$3=$1+$2')
        values = {1:1, 2:2}
        self.assertEqual(modif.evaluate(values), 3)
        self.assertEqual(values, {1:1, 2:2, 3:3.0})

    # tests that pass if they raise expected errors

    @raises(DelimiterMissing)
    @use_file('missing-delim.ger')
    def test_missing_delim(self):
        """ Trap param outside of gerber param block. """

    @raises(CoordPrecedesFormatSpec)
    @use_file('coord-precedes-fs.ger')
    def test_coord_preceding_fs(self):
        """ Trap coord preceding gerber format spec. """

    @raises(ParamContainsBadData)
    @use_file('coord-in-param-block.ger')
    def test_data_in_param(self):
        """ Trap coord inside gerber param block. """

    @raises(CoordMalformed)
    @use_file('y-precedes-x.ger')
    def test_y_before_x(self):
        """ Trap coord with 'Y' before 'X' - gerber. """

    @raises(DataAfterEOF)
    @use_file('data-after-eof.ger')
    def test_trailing_data(self):
        """ Trap data following M02* block - gerber. """

    @raises(FileNotTerminated)
    @use_file('not-terminated.ger')
    def test_no_eof(self):
        """ Trap file with no M02* block - gerber. """

    @raises(UnintelligibleDataBlock)
    @use_file('alien.ger')
    def test_alien_data(self):
        """ Trap off-spec data in gerber file. """

    @raises(QuadrantViolation)
    @use_file('sq-violation.ger')
    def test_single_quadrant(self):
        """ Trap long arc in single quadrant mode. """

    @raises(OpenFillBoundary)
    @use_file('open-fill.ger')
    def test_open_fill(self):
        """ Trap unsuccessful outline fill closure. """

    @raises(IncompatibleAperture)
    @use_file('disallowed-smear.ger')
    def test_arc_smear(self):
        """ Trap non-linear smear - gerber. """

