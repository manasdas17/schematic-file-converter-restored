#!/usr/bin/env python2
""" A universal hardware design file format converter using 
Upverter's Open JSON Interchange Format """

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
#
#
# Development:
#   Active: As of Jan, 2012
#   See: github.com/upverter/schematic-file-converter
#
# Authors:
#   Alex Ray ajray@ncsu.edu
#   Upverter support@upverter.com
#
# Contact:
#   Zak Homuth @ Upverter
#   zak@upverter.com
#   415-766-2333
#   24 Phoebe Street, Toronto, On
#
# Format & Documentation:
#   Based on Upverter's Open JSON Interchange Format
#   upverter.com/resources/open-json-format/
#
# Dependencies:
#   Python: 2.6+ (excluding 3.0+)
#   ArgumentParser
# 
#
# Usage example:
#   ./upconvert.py -i test/openjson/simple.upv -o example.upv 


import logging
import os
import sys
import operator
import tempfile
from argparse import ArgumentParser
try:
    import simplejson as json
except ImportError:
    import json

from upconvert.parser import openjson as openjson_p, kicad as kicad_p, geda as geda_p, \
    eagle as eagle_p, eaglexml as eaglexml_p, fritzing as fritzing_p, gerber as gerber_p
from upconvert.writer import openjson as openjson_w, kicad as kicad_w, geda as geda_w, \
    eagle as eagle_w, gerber as gerber_w


# Logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('main')

PARSERS = {
    'openjson': openjson_p.JSON,
    'kicad': kicad_p.KiCAD,
    'geda': geda_p.GEDA,
    'eagle': eagle_p.Eagle,
    'eaglexml': eaglexml_p.EagleXML,
    'fritzing': fritzing_p.Fritzing,
    'gerber': gerber_p.Gerber,
}

WRITERS = {
    'openjson': openjson_w.JSON,
    'kicad': kicad_w.KiCAD,
    'geda': geda_w.GEDA,
    'eagle': eagle_w.Eagle,
    'gerber': gerber_w.Gerber,
}

EXTENSIONS = {
    'openjson': '.upv',
    'kicad': '.sch',
    'geda': '.sch',
    'eagle': '.sch',
    'fritzing': '.fz',
    'gerber': '.grb',
}


class Upconverter(object):

    @staticmethod
    def autodetect(inputfile):
        """ Autodetect the given input files formatting """
        confidence = {}

        for name, parser in PARSERS.iteritems():
            confidence[name] = parser.auto_detect(inputfile)

        ordered = sorted(confidence.iteritems(), key=operator.itemgetter(1), reverse=True)
        if ordered[0][1] < 0.5:
            log.error('Failed to auto-detect input type for %s. best guess: %s, confidence: %s',
                      inputfile, ordered[0][0], ordered[0][1])
            raise Exception('failed to autodetect')

        log.info('Auto-detected input type: %s', ordered[0][0])
        return ordered[0][0]


    @staticmethod
    def parse(in_file, in_format='openjson', **parser_kwargs):
        """ Parse the given input file using the in_format """

        try:
            if in_format == 'geda':
                p = PARSERS[in_format](**parser_kwargs)
            else:
                p = PARSERS[in_format]()
        except KeyError:
            raise Exception('ERROR: Unsupported input type: %s' % (in_format))

        return p.parse(in_file)


    @staticmethod
    def write(dsgn, out_file, out_format='openjson', **parser_kwargs):
        """ Write the converted input file to the out_format """

        try:
            if out_format == 'geda':
                w = WRITERS[out_format](**parser_kwargs)
            else:
                w = WRITERS[out_format]()
        except KeyError:
            raise Exception('ERROR: Unsupported output type: %s' % (out_format))

        return w.write(dsgn, out_file)


    @staticmethod
    def file_to_upv(file_content):
        """ convert file_content into upv data pre-jsonification """
        log.info('Starting to convert content into upv')

        tmp_fd, tmp_path = tempfile.mkstemp()
        os.write(tmp_fd, file_content.read())
        os.close(tmp_fd)

        format = Upconverter.autodetect(tmp_path)
        design = Upconverter.parse(tmp_path, format)
        os.remove(tmp_path)

        return json.loads(json.dumps(design.json(), sort_keys=True, indent=4))


    @staticmethod
    def json_to_format(upv_json_data, format, path):
        """ convert upv_json_data into format as a file @ path """
        log.info('Converting upv data into %s at %s', format, path)

        path_w_ext = path + EXTENSIONS[format]
        tmp_fd, tmp_path = tempfile.mkstemp()
        os.write(tmp_fd, upv_json_data)
        os.close(tmp_fd)

        design = Upconverter.parse(tmp_path, 'openjson')
        Upconverter.write(design, path_w_ext, format)
        os.remove(tmp_path)

        return path_w_ext


def main():
    ap = ArgumentParser()
    ap.add_argument("-i", "--input", dest="inputfile",
                    help="read INPUT file in", metavar="INPUT")
    ap.add_argument("-f", "--from", dest="inputtype",
                    help="read input file as TYPE", metavar="TYPE")
    ap.add_argument("-o", "--output", dest="outputfile",
                    help="write OUTPUT file out", metavar="OUTPUT")
    ap.add_argument("-t", "--to", dest="outputtype",
                    help="write output file as TYPE", metavar="TYPE",
                    default="openjson")
    ap.add_argument("-s", "--sym-dirs", dest="sym_dirs",
                    help="specify SYMDIRS to search for .sym files (for gEDA only)", 
                    metavar="SYMDIRS", nargs="+")
    ap.add_argument('--unsupported', action='store_true', default=False,
                    help="run with an unsupported python version")
    ap.add_argument('--raise-errors', dest='raise_errors',
                    action='store_true', default=False,
                    help="show tracebacks for parsing and writing errors")
    ap.add_argument('--profile', action='store_true', default=False,
                    help="collect profiling information")

    args = ap.parse_args()

    # Fail if strict and wrong python version
    if sys.version_info[0] > 2 or sys.version_info[1] > 6:
        print 'WARNING: RUNNING UNSUPPORTED VERSION OF PYTHON (%s.%s > 2.6)' % (sys.version_info[0],
            sys.version_info[1])
        if not args.unsupported:
            sys.exit(-1)

    inputtype = args.inputtype
    outputtype = args.outputtype
    inputfile = args.inputfile
    outputfile = args.outputfile

    parser_kwargs = {}
    if args.sym_dirs:
        parser_kwargs['symbol_dirs'] = args.sym_dirs

    # Test for input file
    if inputfile == None:
        log.error('No input file provided.')
        ap.print_help()
        exit(1)

    # Autodetect input type
    if inputtype == None:
        try:
            inputtype = Upconverter.autodetect(inputfile)
        except Exception:
            ap.print_help()
            exit(1)

    # Autoset output file
    if outputfile == None:
        try:
            fileName, fileExtension = os.path.splitext(inputfile)
            outputfile = fileName + EXTENSIONS[outputtype]
            log.info('Auto-set output file: %s', outputfile)
        except Exception:
            log.error('Failed to auto-set output file.')
            ap.print_help()
            exit(1)

    if args.profile:
        import cProfile
        profile = cProfile.Profile()
        profile.enable()

    # parse and export the data
    try:
        design = Upconverter.parse(inputfile, inputtype, **parser_kwargs)
    except Exception:
        if args.raise_errors:
            raise
        print "ERROR: Unsupported input type:", inputtype
        exit(1)

    # we got a good result
    if design is not None:
        try:
            Upconverter.write(design, outputfile, outputtype, **parser_kwargs)
        except Exception:
            if args.raise_errors:
                raise
            print "ERROR: Unsupported output type:", outputtype
            exit(1)

    # parse returned None -> something went wrong
    else:
        print "Output cancelled due to previous errors."
        exit(1)

    if args.profile:
        profile.disable()
        profile.print_stats()


if __name__ == "__main__":
    main()
