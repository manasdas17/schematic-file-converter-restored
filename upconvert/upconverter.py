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
#   Active: As of July, 2012
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
import zipfile
from argparse import ArgumentParser
try:
    import simplejson as json
except ImportError:
    import json

from upconvert import version as ver

from upconvert.parser import openjson as openjson_p, kicad as kicad_p, geda as geda_p, \
    eagle as eagle_p, eaglexml as eaglexml_p, fritzing as fritzing_p, gerber as gerber_p, \
    specctra as specctra_p
from upconvert.writer import openjson as openjson_w, kicad as kicad_w, geda as geda_w, \
    eagle as eagle_w, eaglexml as eaglexml_w, gerber as gerber_w, specctra as specctra_w, \
    bom_csv as bom_w, netlist_csv as netlist_w, ncdrill as ncdrill_w


# Try to include image writer support
try:
    from upconvert.writer import image as image_w
    image_parser = image_w.Image # pylint: disable=C0103
except ImportError, err:
    if err.message != 'No module named PIL':
        raise
    image_parser = None # pylint: disable=C0103


# Logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('main')  # pylint: disable=C0103

PARSERS = {
    'openjson': openjson_p.JSON,
    'kicad': kicad_p.KiCAD,
    'geda': geda_p.GEDA,
    'eagle': eagle_p.Eagle,
    'eaglexml': eaglexml_p.EagleXML,
    'fritzing': fritzing_p.Fritzing,
    'gerber': gerber_p.Gerber,
    'specctra': specctra_p.Specctra,
}

WRITERS = {
    'openjson': openjson_w.JSON,
    'kicad': kicad_w.KiCAD,
    'geda': geda_w.GEDA,
    'eagle': eagle_w.Eagle,
    'eaglexml': eaglexml_w.EagleXML,
    'gerber': gerber_w.Gerber,
    'ncdrill': ncdrill_w.NCDrill,
    'specctra': specctra_w.Specctra,
    'image':  image_parser,
    'bom': bom_w.BOM,
    'netlist': netlist_w.Netlist,
}

EXTENSIONS = {
    'openjson': '.upv',
    'kicad': '.sch',
    'geda': '.sch',
    'eagle': '.sch',
    'eaglexml': '.sch',
    'fritzing': '.fz',
    'gerber': '.zip',
    'ncdrill': '.drill',
    'specctra': '.dsn',
    'image': '.png',
    'bom': '.csv',
    'netlist': '.csv',
}


class Upconverter(object):
    """ The bee knees """

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
    def parse(in_filename, in_format='openjson', **parser_kwargs):
        """ Parse the given input file using the in_format """

        log.debug('parsing %s in format %s', in_filename, in_format)
        try:
            if in_format == 'geda':
                par = PARSERS[in_format](**parser_kwargs)
            else:
                par = PARSERS[in_format]()
        except KeyError:
            raise Exception('ERROR: Unsupported input type: %s' % (in_format))

        return par.parse(in_filename)


    @staticmethod
    def write(dsgn, out_file, out_format='openjson', **parser_kwargs):
        """ Write the converted input file to the out_format """

        try:
            if out_format == 'geda':
                wri = WRITERS[out_format](**parser_kwargs)
            else:
                wri = WRITERS[out_format]()
        except KeyError:
            raise Exception('ERROR: Unsupported output type: %s' % (out_format))

        return wri.write(dsgn, out_file)


    @staticmethod
    def file_to_upv(file_content, lib_contents):
        """ convert file_content into upv data pre-jsonification """
        log.info('Starting to convert content into upv')

        tmp_dir = tempfile.mkdtemp()

        tmp_fd, tmp_path = tempfile.mkstemp(dir=tmp_dir)
        os.write(tmp_fd, file_content.read())
        os.close(tmp_fd)

        lib_path_list = []
        for lib_filename, lib_content in lib_contents.iteritems():
            lib_tmp_fd, lib_tmp_path = tempfile.mkstemp(suffix = lib_filename, prefix = lib_filename, dir=tmp_dir)
            os.write(lib_tmp_fd, lib_content.read())
            os.close(lib_tmp_fd)
            lib_path_list.append(lib_tmp_path)

        frmt = Upconverter.autodetect(tmp_path)
        design = Upconverter.parse(tmp_path, frmt)
        os.remove(tmp_path)

        for path in lib_path_list:
            os.remove(path)

        return json.loads(json.dumps(design.json(), sort_keys=True, indent=4))


    @staticmethod
    def json_to_format(upv_json_data, frmt, path):
        """ convert upv_json_data into format as a file @ path """
        log.info('Converting upv data into %s at %s', frmt, path)

        path_w_ext = path + EXTENSIONS[frmt]
        tmp_fd, tmp_path = tempfile.mkstemp()
        os.write(tmp_fd, upv_json_data)
        os.close(tmp_fd)

        design = Upconverter.parse(tmp_path, 'openjson')
        Upconverter.write(design, path_w_ext, frmt)
        os.remove(tmp_path)

        if frmt == 'kicad':
            kicad_zip = zipfile.ZipFile(path + '.zip', mode='w')
            kicad_zip.write(path_w_ext, os.path.basename(path_w_ext))
            kicad_zip.write(path + '-cache.lib', os.path.basename(path + '-cache.lib'))
            kicad_zip.close()
            path_w_ext = path + '.zip'
        elif frmt == 'geda':
            geda_zip = zipfile.ZipFile(path + '.zip', mode='w')
            geda_zip.write(path_w_ext, os.path.basename(path_w_ext))
            symbol_dir = os.path.join(os.path.dirname(path), 'symbols-' + os.path.basename(path_w_ext))
            for symbol_file in os.listdir(symbol_dir):
                geda_zip.write(os.path.join(symbol_dir, symbol_file), symbol_file)
            geda_zip.close()
            path_w_ext = path + '.zip'

        return path_w_ext


def main(): #pylint: disable=R0912,R0915
    """ Also, bees knees """
    argp = ArgumentParser()
    argp.add_argument("-i", "--input", dest="inputfile",
                      help="read INPUT file in", metavar="INPUT")
    argp.add_argument("-f", "--from", dest="inputtype",
                      help="read input file as TYPE", metavar="TYPE")
    argp.add_argument("-o", "--output", dest="outputfile",
                      help="write OUTPUT file out", metavar="OUTPUT")
    argp.add_argument("-t", "--to", dest="outputtype",
                      help="write output file as TYPE", metavar="TYPE",
                      default="openjson")
    argp.add_argument("-s", "--sym-dirs", dest="sym_dirs",
                      help="specify SYMDIRS to search for .sym files (for gEDA only)", 
                      metavar="SYMDIRS", nargs="+")
    argp.add_argument('--unsupported', action='store_true', default=False,
                      help="run with an unsupported python version")
    argp.add_argument('--raise-errors', dest='raise_errors',
                      action='store_true', default=False,
                      help="show tracebacks for parsing and writing errors")
    argp.add_argument('--profile', action='store_true', default=False,
                      help="collect profiling information")
    argp.add_argument('-v', '--version', action='store_true', default=False,
                      help="print version information and quit")
    argp.add_argument('--formats', action='store_true', default=False,
                      help="print supported formats and quit")

    args = argp.parse_args()

    if args.version:
        print "upconverter %s in python %s.%s" % (ver.version(), sys.version_info[0], sys.version_info[1])
        print "Copyright (C) 2007 Upverter, Inc."
        print "This is free software; see the source for copying conditions.  There is NO warranty; not even for",
        print "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE."
        sys.exit(0)

    if args.formats:
        print "upconverter supports the following file formats & encodings"
        print ""
        print "As Input:"
        for frmt in PARSERS:
            print "* %s (%s)" % (frmt, EXTENSIONS[frmt])
        print ""
        print "As Output:"
        for frmt in WRITERS:
            print "* %s (%s)" % (frmt, EXTENSIONS[frmt])
        sys.exit(0)

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
        argp.print_help()
        exit(1)

    # Autodetect input type
    if inputtype == None:
        try:
            inputtype = Upconverter.autodetect(inputfile)
        except Exception: #pylint: disable=W0703
            argp.print_help()
            exit(1)

    # Autoset output file
    if outputfile == None:
        try:
            file_name, file_ext = os.path.splitext(inputfile)  #pylint: disable=W0612
            outputfile = file_name + EXTENSIONS[outputtype]
            log.info('Setting output file & format: %s', outputfile)
        except Exception: #pylint: disable=W0703
            log.error('Failed to set output file & format.')
            argp.print_help()
            exit(1)

    if args.profile:
        import cProfile
        profile = cProfile.Profile()
        profile.enable()

    # parse the data
    try:
        design = Upconverter.parse(inputfile, inputtype, **parser_kwargs) #pylint: disable=W0142
    except Exception: #pylint: disable=W0703
        if args.raise_errors:
            raise
        print "ERROR: Failed to parse", inputtype
        exit(1)

    # we got a good result
    if design is not None:
        try:
            Upconverter.write(design, outputfile, outputtype, **parser_kwargs) #pylint: disable=W0142
        except Exception: #pylint: disable=W0703
            if args.raise_errors:
                raise
            print "ERROR: Failed to write", outputtype
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
