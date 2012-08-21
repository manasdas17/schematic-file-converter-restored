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

import argparse
import unittest
import os
import sys
import re
import logging
import subprocess
import tempfile

from upconvert.upconverter import Upconverter
from upconvert.utils.verify_json import verify_json

from os.path import splitext


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
    if os.path.basename(top) == 'unittest':
        return
    for name in names:
        if ger_re.match(os.path.join(top, name)):
            arg.append(os.path.join(top, name))


upv_re = re.compile(r'.*\.upv$')
def filter_upv(arg, top, names):
    for name in names:
        if upv_re.match(os.path.join(top, name)):
            arg.append(os.path.join(top, name))

dsn_re = re.compile(r'.*\.dsn$')
def filter_dsn(arg, top, names):
    for name in names:
        if dsn_re.match(os.path.join(top, name)):
            arg.append(os.path.join(top, name))

def get_file_diff_ratio(file1, file2):
    """ Return the ratio of differences to the total
    number of lines in file1 and file2. """
    with open(file1) as f:
        num_lines1 = sum(1 for _ in f)
    with open(file2) as f:
        num_lines2 = sum(1 for _ in f)

    p = subprocess.Popen(('diff', '--speed-large-files', file1, file2),
                         stdout=subprocess.PIPE)

    num_diffs = sum(1 for line in p.stdout if line and line[0] in '<>')

    p.wait()

    return float(num_diffs) / (num_lines1 + num_lines2)


def get_file_contents(tmp_path):
    with open(tmp_path, 'r') as final:
        return final.read()


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

        verify_json(data.json())

        tmp_fd, tmp_path = tempfile.mkstemp()
        os.close(tmp_fd)
        Upconverter.write(data, tmp_path, 'openjson')
        self.assertTrue(get_file_contents(tmp_path) != '')
        os.remove(tmp_path)
    return test


max_diff_ratios = {
    'geda': 0.30,
    'kicad': 0.049,
    'openjson': 0.0
    }

def test_diff_generator(file_path, format):
    """ Parse the file, write to both openjson and to the given
    format. Then parse the new file in the same format and write that
    to openjson. Test the differences between the two openjson files
    and fail if they differ by more than 5 percent.

    This tests that the parser and writer together preserve as much
    information as the parser by itself.

    Given a file F in format X, written as F.X, do the following
    conversions:

      F.X --> F1.upv --> F2.X --> F3.upv

    Then compare F1 and F3 using the 'diff' program and compute the
    ratio of the number of differences to the total number of lines in
    both files. Assert the ratio is below a given threshold.
    """
    def test(self):
        try:
            data = Upconverter.parse(file_path, format)
            self.assertNotEqual(data, None)

            tmp_fd, json_path_1 = tempfile.mkstemp(prefix='test.1.', suffix='.upv')
            os.close(tmp_fd)
            Upconverter.write(data, json_path_1, 'openjson')
            self.assertNotEqual(get_file_contents(json_path_1), '')

            tmp_fd, tmp_path = tempfile.mkstemp(suffix='.' + format)
            os.close(tmp_fd)
            Upconverter.write(data, tmp_path, format)
            self.assertNotEqual(get_file_contents(tmp_path), '')

            data = Upconverter.parse(tmp_path, format)
            self.assertNotEqual(data, None)

            tmp_fd, json_path_2 = tempfile.mkstemp(prefix='test.2.', suffix='.upv')
            os.close(tmp_fd)
            Upconverter.write(data, json_path_2, 'openjson')
            self.assertNotEqual(get_file_contents(json_path_2), '')

            ratio = get_file_diff_ratio(json_path_1, json_path_2)

            self.assertTrue(ratio <= max_diff_ratios[format],
                            (file_path, tmp_path, json_path_1, json_path_2, ratio))
        finally:
            # need to remove each file if a failure occured.
            # tries handle variables that have not yet been instantiated.
            try:
                os.remove(json_path_1)
            except:
                pass
            try:
                os.remove(json_path_2)
            except:
                pass
            try:
                os.remove(splitext(tmp_path)[0] + '-cache.lib')
            except:
                pass
            try:
                os.remove(tmp_path)
            except:
                pass
        
    return test


def test_write_generator(json_file_path, format):
    """ Test the writing files. """
    def test(self):
        data = Upconverter.parse(json_file_path, 'openjson')
        self.assertTrue(data != None)

        tmp_fd, tmp_path = tempfile.mkstemp()
        os.close(tmp_fd)
        Upconverter.write(data, tmp_path, format)
        self.assertTrue(get_file_contents(tmp_path) != '')
        os.remove(tmp_path)
    return test


def main():
    desc = 'Run the upconverter regression tests'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--fail-fast', action='store_true', default=False)
    parser.add_argument('--unsupported', action='store_true', default=False)
    parser.add_argument('--test-type', dest='test_types', action='append')
    parser.add_argument('file_types', metavar='input-type', nargs='*')

    args = parser.parse_args()

    if not args.test_types:
        args.test_types = ['parse', 'write', 'autodetect', 'diff']

    if 'all' in args.file_types:
        args.file_types = None

    # Fail if strict and wrong python version
    if sys.version_info[0] > 2 or sys.version_info[1] > 6:
        print 'WARNING: RUNNING UNSUPPORTED VERSION OF PYTHON (%s.%s > 2.6)' % (sys.version_info[0],
            sys.version_info[1])
        if not args.unsupported:
            sys.exit(-1)

    # Hide logging
    logging.getLogger("main").setLevel(logging.ERROR)
    logging.getLogger("parser.geda").setLevel(logging.ERROR)

    eagle_sch_files = []
    os.path.walk('./test/eagle', filter_sch, eagle_sch_files)

    eaglexml_sch_files = []
    os.path.walk('./test/eaglexml', filter_sch, eaglexml_sch_files)

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

    specctra_dsn_files = []
    os.path.walk('./test/specctra', filter_dsn, specctra_dsn_files)

    l = {'eagle': eagle_sch_files,
         'eaglexml': eaglexml_sch_files,
         'fritzing': fritzing_sch_files,
         'geda': geda_sch_files,
         'gerber': gerber_ger_files,
         'kicad': kicad_sch_files,
         'openjson': upverter_upv_files,
         'specctra': specctra_dsn_files,
        #'image': image_files,
    }

    test_classes = {}

    for format, files in l.iteritems():
        test_class = type('RegressionTest_' + format, (unittest.TestCase,), {})
        test_classes[format] = test_class

        for f in files:
            base = os.path.basename(f)

            if 'autodetect' in args.test_types:
                test_name = 'test_%s_%s_%s' % (format, base, 'detect')
                test = test_auto_detect_generator(f, format)
                setattr(test_class, test_name, test)

            if 'parse' in args.test_types:
                test_name = 'test_%s_%s_%s' % (format, base, 'parse')
                test = test_parse_generator(f, format)
                setattr(test_class, test_name, test)

            if 'diff' in args.test_types and format in max_diff_ratios:
                test_name = 'test_%s_%s_%s' % (format, base, 'diff')
                test = test_diff_generator(f, format)
                setattr(test_class, test_name, test)

        for f in upverter_upv_files:
            base = os.path.basename(f)

            if 'write' in args.test_types \
                    and format not in ('eaglexml', 'fritzing', 'gerber'):
                test_name = 'test_%s_%s_%s' % (format, base, 'write')
                test = test_write_generator(f, format)
                setattr(test_class, test_name, test)

    for format, c in test_classes.iteritems():
        if not args.file_types or format in args.file_types:
            print '=============================\n\n\nTesting: %s >>>' % format
            s = unittest.TestLoader().loadTestsFromTestCase(c)
            if args.fail_fast:
                unittest.TextTestRunner(failfast=args.fail_fast).run(s)
            else:
                unittest.TextTestRunner().run(s)


if __name__ == "__main__":
    main()
