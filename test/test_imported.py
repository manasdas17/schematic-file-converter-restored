#!/usr/bin/python
# encoding: utf-8
#pylint: disable=R0904
""" Handle imported files """

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

import argparse
import os
import sys
import re
import logging
import tempfile
import traceback
from upconvert.upconverter import Upconverter


def filter_all(arg, top, names):
    for name in names:
        arg.append(os.path.join(top, name))


def main():
    imported_files = []
    os.path.walk('./test/imported', filter_all, imported_files)

    failed_to_autodetect = []
    failed_to_parse = []

    for file_path in imported_files:
        try:
            # test autodetection
            format = Upconverter.autodetect(file_path)
            
            try:
                # test conversion
                data = Upconverter.parse(file_path, format)

            except Exception, e:
                failed_to_parse.append(file_path)
                print traceback.print_exc()
                
        except Exception, e:
            failed_to_autodetect.append(file_path)
            print traceback.print_exc()

    print '\n\n'

    print 'failed to autodetect: %s' % (len(failed_to_autodetect))
    print '--'
    for f in failed_to_autodetect:
        print '%s' % (f)

    print '\n'

    print 'failed to parse:      %s' % (len(failed_to_parse))
    print '--'
    for f in failed_to_parse:
        print '%s' % (f)


if __name__ == "__main__":
    main()
