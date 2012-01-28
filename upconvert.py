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


import parser.openjson, parser.kicad, parser.geda
import parser.fritzing
import parser.eagle
import writer.openjson, writer.kicad, writer.geda
import writer.eagle

from argparse import ArgumentParser

PARSERS = {
    'openjson': parser.openjson.JSON,
    'kicad': parser.kicad.KiCAD,
    'geda': parser.geda.GEDA,
    'eagle': parser.eagle.Eagle,
    'fritzing': parser.fritzing.Fritzing,
}

WRITERS = {
    'openjson': writer.openjson.JSON,
    'kicad': writer.kicad.KiCAD,
    'geda': writer.geda.GEDA,
    'eagle': writer.eagle.Eagle,
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
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", dest="inputfile",
            help="read INPUT file in", metavar="INPUT")
    parser.add_argument("-f", "--from", dest="inputtype",
            help="read input file as TYPE", metavar="TYPE",
            default="openjson")
    parser.add_argument("-o", "--output", dest="outputfile",
            help="write OUTPUT file out", metavar="OUTPUT")
    parser.add_argument("-s", "--sym-dirs", dest="sym_dirs",
            help="specify SYMDIRS to search for .sym files (for gEDA only)", 
            metavar="SYMDIRS", nargs="+")
    parser.add_argument("-t", "--to", dest="outputtype",
            help="write output file as TYPE", metavar="TYPE",
            default="openjson")

    args = parser.parse_args()
    inputtype = args.inputtype
    outputtype = args.outputtype
    inputfile = args.inputfile
    outputfile = args.outputfile

    parser_kwargs = {}
    if args.sym_dirs:
        parser_kwargs['symbol_dirs'] = args.sym_dirs

    if None == inputfile:
        print_help()
        exit(1)

    # parse and export the data
    design = parse(inputfile, inputtype, **parser_kwargs)
    if design is not None: # we got a good result
        write(design, outputfile, outputtype, **parser_kwargs)
    else: # parse returned None -> something went wrong
        print "Output cancelled due to previous errors."
        exit(1)
