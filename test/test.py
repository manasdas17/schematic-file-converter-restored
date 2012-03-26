#!/usr/bin/python
# encoding: utf-8
#pylint: disable=R0904
""" The regression test class """

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


import unittest
import os
import sys
import re
import logging
import tempfile
from difflib import SequenceMatcher
from upconvert.upconverter import Upconverter


sch_re = re.compile(r'.*\.sch$')
def filter_sch(arg, top, names):
    for name in names:
        if sch_re.match(os.path.join(top, name)):
            arg.append(os.path.join(top, name))


fz_re = re.compile(r'.*\.fz$')
def filter_fz(arg, top, names):
    for name in names:
        if fz_re.match(os.path.join(top, name)):
            arg.append(os.path.join(top, name))


fzz_re = re.compile(r'.*\.fzz$')
def filter_fzz(arg, top, names):
    for name in names:
        if fzz_re.match(os.path.join(top, name)):
            arg.append(os.path.join(top, name))


ger_re = re.compile(r'.*\.ger$')
def filter_ger(arg, top, names):
    for name in names:
        if ger_re.match(os.path.join(top, name)):
            arg.append(os.path.join(top, name))


upv_re = re.compile(r'.*\.upv$')
def filter_upv(arg, top, names):
    for name in names:
        if upv_re.match(os.path.join(top, name)):
            arg.append(os.path.join(top, name))


def file_diff(file1, file2):
    text1 = ''
    with open(file1) as f:
        text1 = f.read()
    text2 = ''
    with open(file2) as f:
        text2 = f.read()
    return SequenceMatcher(None, text1, text2)


def check_output(tmp_path):
    output = None
    with open(tmp_path, 'r') as final:
        output = final.read()
    return output


def test_auto_detect_generator(file_path, format):
    """ Test the autodetection of files. """
    def test(self):
        self.assertEqual(Upconverter.autodetect(file_path), format)
    return test


def test_parse_generator(file_path, format):
    """ Test the parsing of files. """
    def test(self):
        data = Upconverter.parse(file_path, format)
        self.assertTrue(data != None)

        tmp_fd, tmp_path = tempfile.mkstemp()
        os.close(tmp_fd)
        Upconverter.write(data, tmp_path, 'openjson')
        self.assertTrue(check_output(tmp_path) != '')
        os.remove(tmp_path)
    return test


def test_diff_generator(file_path, format):
    """ Test the damage to a file from an in-out. """
    def test(self):
        data = Upconverter.parse(file_path, format)
        self.assertTrue(data != None)

        tmp_fd, tmp_path = tempfile.mkstemp()
        os.close(tmp_fd)
        Upconverter.write(data, tmp_path, format)
        self.assertTrue(check_output(tmp_path) != '')

        self.assertTrue(file_diff(file_path, tmp_path).ratio() > 0.95)
        os.remove(tmp_path)
    return test


def test_write_generator(json_file_path, format):
    """ Test the writing files. """
    def test(self):
        data = Upconverter.parse(json_file_path, 'openjson')
        self.assertTrue(data != None)

        tmp_fd, tmp_path = tempfile.mkstemp()
        os.close(tmp_fd)
        Upconverter.write(data, tmp_path, format)
        self.assertTrue(check_output(tmp_path) != '')
        os.remove(tmp_path)
    return test


if __name__ == "__main__":
    # Hide logging
    logging.getLogger("main").setLevel(logging.ERROR)

    eagle_sch_files = []
    os.path.walk('./test/eagle', filter_sch, eagle_sch_files)

    fritzing_fz_files = []
    os.path.walk('./test/fritzing', filter_fz, fritzing_fz_files)

    fritzing_fzz_files = []
    os.path.walk('./test/fritzing', filter_fzz, fritzing_fzz_files)

    fritzing_sch_files = []
    fritzing_sch_files.extend([str(t) for t in fritzing_fz_files])
    fritzing_sch_files.extend([str(t) for t in fritzing_fzz_files])

    geda_sch_files = []
    os.path.walk('./test/geda', filter_sch, geda_sch_files)

    gerber_ger_files = []
    os.path.walk('./test/gerber', filter_ger, gerber_ger_files)

    kicad_sch_files = []
    os.path.walk('./test/kicad', filter_sch, kicad_sch_files)

    upverter_upv_files = []
    os.path.walk('./test/openjson', filter_upv, upverter_upv_files)

    l = {'eagle': eagle_sch_files,
         'fritzing': fritzing_sch_files,
         'geda': geda_sch_files,
         'gerber': gerber_ger_files,
         'kicad': kicad_sch_files,
         'openjson': upverter_upv_files}

    test_classes = {}
    for format, files in l.iteritems():
        test_class = type('RegressionTest_' + format, (unittest.TestCase,), {})
        test_classes[format] = test_class

        for f in files:
            base = os.path.basename(f)

            test_name = 'test_%s_%s_%s' % (format, base, 'detect')
            test = test_auto_detect_generator(f, format)
            setattr(test_class, test_name, test)

            test_name = 'test_%s_%s_%s' % (format, base, 'parse')
            test = test_parse_generator(f, format)
            setattr(test_class, test_name, test)

            test_name = 'test_%s_%s_%s' % (format, base, 'diff')
            test = test_diff_generator(f, format)
            setattr(test_class, test_name, test)

        for f in upverter_upv_files:
            base = os.path.basename(f)

            test_name = 'test_%s_%s_%s' % (format, base, 'write')
            test = test_write_generator(f, format)
            setattr(test_class, test_name, test)

    for format, c in test_classes.iteritems():
        if len(sys.argv) < 2 or format in sys.argv:
            print format
            s = unittest.TestLoader().loadTestsFromTestCase(c)
            unittest.TextTestRunner().run(s)
