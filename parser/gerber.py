#!/usr/bin/env python2
""" The Gerber RS274-X Format Parser """

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

import re
from string import digits
from collections import namedtuple

from core.design import Design
from core.layout import Layout, Layer, Trace
from core.shape import Line

# exceptions

class Unparsable(ValueError): pass
class ParamError(Unparsable): pass
class CoordError(Unparsable): pass
class DelimiterMissing(ParamError): pass
class ParamContainsBadData(ParamError): pass
class CoordPrecedesFormatSpec(CoordError): pass
class CoordMalformed(CoordError): pass
class FileNotTerminated(Unparsable): pass
class DataAfterEOF(Unparsable): pass
class UnintelligibleDataBlock(Unparsable): pass

# token classes

Aperture = namedtuple('Aperture', 'code type_ modifiers')
Coord = namedtuple('Coord', 'x y i j')
CoordFmt = namedtuple('CoordFmt', 'int dec')
AxisDef = namedtuple('AxisDef', 'a b')
Funct = namedtuple('Funct', 'type_ code')
FormatSpec = namedtuple('FormatSpec', ['zero_omission',
                        'incremental_coords', 'n_max', 'g_max',
                        'x', 'y', 'd_max', 'm_max'])

# parser status

Status = namedtuple('Status', 'x y draw aperture')

# parser

class Gerber:
    """ The Gerber Format Parser """

    def __init__(self, filename=None):
        self.filename = filename
        self.layer = Layer()

        # establish gerber defaults
        self.params = {'AS':AxisDef('x', 'y'),# axis select
                       'FS':None,             # format spec
                       'MI':AxisDef(0, 0),    # mirror image
                       'MO':'IN',             # mode: inches/mm
                       'OF':AxisDef(0, 0),    # offset
                       'SF':AxisDef(1, 1),    # scale factor
                       'IJ':AxisDef(('L', 0), # image justify
                                    ('L', 0)),
                       'IO':AxisDef(0, 0),    # image offset
                       'IP':True,             # image polarity
                       'IR':0}                # image rotation

    def parse(self):
        """ Parse tokens from gerber file into a design. """
        status = Status(0.0, 0.0, None, None)
        for block in self._tokenize():
            if isinstance(block, Funct):
                status = self._do_funct(block, status)
            elif isinstance(block, Coord):
                status = self._move(block, status)
            else:
                self.params[block.id_] = block
        layout = Layout()
        layout.layers.append(self.layer)
        print self.layer.json()
        design = Design()
        design.layouts.append(layout)
        return design

    def _do_funct(self, block, status):
        # TODO: write docstrings for private methods
        # TODO: handle G codes
        if block.type_ == 'D':
            if int(block.code) < 10:
                status = status._replace(draw=block.code)
            else:
                status = status._replace(aperture=block.code)
        return status

    def _move(self, block, status):
        x, y = self._target_pos(block, status)
        if status.draw == '01':
            # TODO: handle 'D03'
            # TODO: don't assume circular aperture
            segment = Line(status[:2], (x, y))
            w = self.params[status.aperture].modifiers[0]
            tr_index = self.layer.get_connected_trace(w, status[:2])
            if tr_index is None:
                trace = Trace(w, [segment])
                self.layer.traces.append(trace)
            else:
                self.layer.traces[tr_index].segments.append(segment)
        return status._replace(x=x, y=y)

    def _target_pos(self, block, status):
        coord = {'x':block.x, 'y':block.y}
        for k in coord:
            if self.params['FS'].incremental_coords:
                if coord[k] is None:
                    coord[k] = 0
                coord[k] = getattr(status, k) + getattr(block, k)
            else:
                if coord[k] is None:
                    coord[k] = getattr(status, k)
        return (coord['x'], coord['y'])

    def _tokenize(self):
        """ Split gerber file into pythonic tokens. """
        all_params = ('AS', 'FS', 'MI', 'MO', 'OF', 'SF',
                      'IJ', 'IN', 'IO', 'IP', 'IR', 'PF', 'AD',
                      'KO', 'LN', 'LP', 'SR')
        param_spec = tuple([(p, r'%s[^\*]*\*' % p)
                            for p in all_params])
        tok_spec = (('PARAM_DELIM', r'%'),) + param_spec + (
                    ('COMMENT', r'G04[^\*]*\*'),
                    ('DEPRECATED', r'G54\*?'), # historic crud
                    ('FUNCT', r'[GD][^\*]*\*'),# function codes
                    ('COORD', r'[XY][^\*]*\*'),# coordinates
                    ('EOF', r'M02\*'),         # end of file
                    ('SKIP', r'M0[01]\*|N[^\*]*\*|\s+'), # historic crud, whitespace
                    ('UNKNOWN', r'[^\*]*\*'))  # unintelligble data block
                                               # TODO: handle aperture macros

        # define constants, counters
        reg_ex = '|'.join('(?P<%s>%s)' % pair for pair in tok_spec)
        tok_re = re.compile(reg_ex, re.MULTILINE)
        ignore = ('SKIP', 'COMMENT', 'DEPRECATED')
        pos = matched = 0
        param_block = data_began = eof = False

        # read file
        with open(self.filename, 'r') as ger:
            s = ger.read()

        # step through content, extract tokens
        mo = tok_re.match(s)
        while pos < len(s):
            if mo is None:
                pos += 1
            else:
                typ = mo.lastgroup
                tok = mo.group(typ)[:-1]
                try:
                    if typ == 'PARAM_DELIM':
                        param_block = not param_block

                    # params
                    elif len(typ) == 2:
                        self._check_pb(param_block, tok)
                        self.params.update((self._parse_param(tok),))

                    # data blocks
                    elif typ not in ignore:
                        self._check_pb(param_block, tok, False)
                        if typ == 'EOF':
                            self._check_eof(s[mo.end():])
                            eof = True
                        else:
                            self._check_typ(typ, tok)

                            # explode self-referential data blocks
                            blocks = self._parse_data_block(tok)
                            for block in blocks:
                                yield block

                # tidy up
                except Unparsable:
                    raise
                pos = matched = mo.end()
            mo = tok_re.match(s, pos)
        self._check_eof(eof=eof)

    def _parse_param(self, tok):
        name, tok = (tok[:2], tok[2:])
        axis_params = ('AS', 'MI', 'OF', 'SF', 'IJ', 'IO')
        if name == 'FS':
            tok, m_max = self._pop_val('M', tok)
            tok, d_max = self._pop_val('D', tok)
            tok, y = self._pop_val('Y', tok, coerce=False)
            y = CoordFmt(int(y[0]), int(y[1]))
            tok, x = self._pop_val('X', tok, coerce=False)
            x = CoordFmt(int(x[0]), int(x[1]))
            tok, g_max = self._pop_val('G', tok)
            tok, n_max = self._pop_val('N', tok)
            inc_coords = (tok[1] == 'I')
            z_omit = tok[0]
            tok = FormatSpec(z_omit, inc_coords, n_max, g_max,
                             x, y, d_max, m_max)
        elif name == 'AD':
            code_end = tok[3] in digits and 4 or 3
            name = tok[1:code_end]
            type_, mods = tok[code_end:].split(',')
            tok = Aperture(name, type_, tuple(mods.split('X')))
        elif name in axis_params:
            if name in ('AS', 'IJ'):
                coerce = False
            else:
                coerce = name == 'MI' and 'int' or 'float'
            tok, b = self._pop_val('B', tok, coerce=coerce)
            tok, a = self._pop_val('A', tok, coerce=coerce)
            if name == 'IJ':
                tok = AxisDef(self._parse_justify(a), self._parse_justify(b))
            else:
                tok = AxisDef(a, b)
        # TODO: handle  IP, IR, layer params KO, LN, LP, SR (if they matter)
        # TODO: check file for duplicate image_params -- should use last occurrence for entire file
        return (name, tok)

    def _parse_data_block(self, tok):
        if 'G' in tok:
            g_code = tok[1:3] # TODO: remove assumption that leading 0 is supplied -- not required by spec
            tok = tok[3:]
            yield Funct('G', g_code)
        tok, d_code = self._pop_val('D', tok, coerce=False)
        if d_code:
            yield Funct('D', d_code)
        if tok:
            yield self._parse_coord(tok)

    def _parse_coord(self, tok):
        self._check_fs()
        tok, j = self._pop_val('J', tok, format=True)
        tok, i = self._pop_val('I', tok, format=True)
        tok, y = self._pop_val('Y', tok, format=True)
        tok, x = self._pop_val('X', tok, format=True)
        result = Coord(x, y, i, j)
        if tok:
            raise CoordMalformed('%s remainder=%s' % (result, tok))
        return result

    def _pop_val(self, key, tok, format=False, coerce='int'):
        val = None
        if key in tok:
            tok, num_str = tok.split(key)
            if num_str:
                if format:
                    if key in ('X', 'I'):
                        val = self._format_dec(num_str, 4)
                    else:
                        val = self._format_dec(num_str, 5)
                else:
                    val = coerce and (coerce == 'float' and
                                      float(num_str) or
                                      int(num_str)) or num_str
        return (tok, val)

    def _format_dec(self, num_str, xy):
        fs = self.params['FS']
        sign_wid = num_str[0] in ('-', '+') and 1 or 0
        int_wid = sign_wid + fs[xy].int
        wid = int_wid + fs[xy].dec

        # pad coordinate data to specified width
        if fs.zero_omission == 'L':
            num_str = num_str.zfill(wid)
        elif fs.zero_omission == 'T':
            num_str = num_str.rjust(wid, '0')
        if len(num_str) != wid:
            raise CoordMalformed('num_str: %s wid: %s' % (num_str, wid))

        # insert decimal point
        num_str = '%s.%s' % (num_str[:int_wid], num_str[int_wid:])

        return float(num_str)

    def _parse_justify(self, tok):
        if len(tok) > 1 or tok not in 'LC':
            result = ('L', float(tok.split('L')[-1]))
        else:
            result = (tok, None)
        # TODO: spec for IJ references off-spec examples with , or . delimiters
        return result

    def _check_pb(self, param_block, tok, should_be=True):
        if should_be and not param_block:
            raise DelimiterMissing
        if param_block and not should_be:
            raise ParamContainsBadData(tok)

    def _check_fs(self):
        if not self.params['FS']:
            raise CoordPrecedesFormatSpec

    def _check_eof(self, trailing_fragment=None, eof=False):
        if not (trailing_fragment or eof):
            raise FileNotTerminated
        elif (not eof) and trailing_fragment.strip():
            raise DataAfterEOF(trailing_fragment)

    def _check_typ(self, typ, tok):
        if typ == 'UNKNOWN':
            raise UnintelligibleDataBlock(tok)
