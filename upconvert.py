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
import operator
from argparse import ArgumentParser

import parser.openjson, parser.kicad, parser.geda
import parser.fritzing, parser.gerber
import parser.eagle
import writer.openjson, writer.kicad, writer.geda
import writer.eagle, writer.gerber


# Logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('main')

PARSERS = {
    'openjson': parser.openjson.JSON,
    'kicad': parser.kicad.KiCAD,
    'geda': parser.geda.GEDA,
    'eagle': parser.eagle.Eagle,
    'fritzing': parser.fritzing.Fritzing,
    'gerber': parser.gerber.Gerber,
}

WRITERS = {
    'openjson': writer.openjson.JSON,
    'kicad': writer.kicad.KiCAD,
    'geda': writer.geda.GEDA,
    'eagle': writer.eagle.Eagle,
    'gerber': writer.gerber.Gerber,
}

EXTENSIONS = {
    'openjson': '.upv',
    'kicad': '.sch',
    'geda': '.sch',
    'eagle': '.sch',
    'fritzing': '.fz',
    'gerber': '.grb',
}


def parse(in_file, in_format='openjson', **parser_kwargs):
    """ Parse the given input file using the in_format """

    try:
        if in_format == 'geda':
            p = PARSERS[in_format](**parser_kwargs)
        else:
            p = PARSERS[in_format]()
    except KeyError:
        print "ERROR: Unsupported input type:", in_format
        exit(1)
    return p.parse(in_file)


def write(dsgn, out_file, out_format='openjson', **parser_kwargs):
    """ Write the converted input file to the out_format """

    try:
        if out_format == 'geda':
            w = WRITERS[out_format](**parser_kwargs)
        else:
            w = WRITERS[out_format]()
    except KeyError:
        print "ERROR: Unsupported output type:", out_format
        exit(1)
    return w.write(dsgn, out_file)
    

if __name__ == "__main__":
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

    args = ap.parse_args()
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
        confidence = {}
        for name, parser in PARSERS.iteritems():
            confidence[name] = parser.auto_detect(inputfile)
        ordered = sorted(confidence.iteritems(), key=operator.itemgetter(1), reverse=True)
        if ordered[0][1] >= 0.5:
            inputtype = ordered[0][0]
            log.info('Auto-detected input type: %s', inputtype)
        else:
            log.error('Failed to auto-detect input type for %s. best guess: %s, confidence: %s',
                      inputfile, ordered[0][0], ordered[0][1])
            ap.print_help()
            exit(1)

    # Autoset output file
    if outputfile == None:
        try:
            fileName, fileExtension = os.path.splitext(inputfile)
            outputfile = fileName + EXTENSIONS[outputtype]
            log.info('Auto-set output file: %s', outputfile)
        except:
            log.error('Failed to auto-set output file.')
            ap.print_help()
            exit(1)

    # parse and export the data
    design = parse(inputfile, inputtype, **parser_kwargs)

    # we got a good result
    if design is not None:
        write(design, outputfile, outputtype, **parser_kwargs)

    # parse returned None -> something went wrong
    else:
        print "Output cancelled due to previous errors."
        exit(1)
