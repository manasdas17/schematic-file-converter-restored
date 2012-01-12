#!/usr/bin/env python
""" The Gerber RS274-X Format Parser """

import re
from string import digits
from collections import namedtuple

from core.design import Design
from core.layout import Layout

# exceptions

class Unparsable(ValueError): pass
class ParamError(Unparsable): pass
class CoordError(Unparsable): pass
class DelimiterMissing(ParamError): pass
class ContainsBadData(ParamError): pass
class PrecedesFormatSpec(CoordError): pass
class Malformed(CoordError): pass
class DataAfterEOF(Unparsable): pass

# token classes

Param = namedtuple('Param', 'id_ val')
Aperture = namedtuple('Aperture', 'code type_ modifiers')
Funct = namedtuple('Funct', 'type_ code')
Coord = namedtuple('Coord', 'x y i j')
CoordFmt = namedtuple('CoordFmt', 'int dec')
FormatSpec = namedtuple('FormatSpec', ['zero_omission', 'incremental_coords',
                                       'n_max', 'g_max', 'x', 'y',
                                       'd_max', 'm_max'])

# parser

class Gerber:
    """ The Gerber Format Parser """

    def __init__(self, filename=None):
        self.filename = filename

        # establish gerber defaults
        self.params = {'AS':{'A':'X',     # axis select
                             'B':'Y'},
                       'FS':None,         # format spec
                       'MI':{'A':0,       # mirror image
                             'B':0},
                       'MO':'IN',         # mode
                       'OF':{'A':0,       # offset
                             'B':0},
                       'SF':{'A':1,       # scale factor
                             'B':1},
                       'IN':'',           # image name
                       'IJ':{'A':('L', 0),# justify
                             'B':('L', 0)},
                       'IO':{'A':0,       # offset
                             'B':0},
                       'IP':True,         # polarity
                       'IR':0,            # rotation
                       'PF':''}           # plot film

    def parse(self):
        """ Parse a Gerber file into a design """
        design = Design()
        data = self._tokenize()
        print 'data...'
        for data_block in data:
            print data_block
        print 'params: %s' % self.params
        return design

    def _tokenize(self):
        tok_spec = [
            ('PARAM_DELIM', r'%'),      # parameter delimiter
            ('AS', r'AS[^\*]*\*'),      # axis select
            ('FS', r'FS[^\*]*\*'),      # format specification
            ('MI', r'MI[^\*]*\*'),      # mirror image (axis)
            ('MO', r'MO[^\*]*\*'),      # mode (inches/mm)
            ('OF', r'OF[^\*]*\*'),      # offset
            ('SF', r'SF[^\*]*\*'),      # scale factor
            ('IJ', r'IJ[^\*]*\*'),      # image justification
            ('IN', r'IN[^\*]*\*'),      # image name
            ('IO', r'IO[^\*]*\*'),      # image offset
            ('IP', r'IP[^\*]*\*'),      # image polarity
            ('IR', r'IR[^\*]*\*'),      # image rotation
            ('PF', r'PF[^\*]*\*'),      # plot film
            ('KO', r'KO[^\*]*\*'),      # layer - knock out
            ('LN', r'LN[^\*]*\*'),      # layer - name
            ('LP', r'LP[^\*]*\*'),      # layer - polarity
            ('SR', r'SR[^\*]*\*'),      # layer - step and repeat
            ('AD', r'AD[^\*]*\*'),      # aperture definition
            ('COMMENT', r'G04[^\*]*\*'),# comment
            ('DEPRECATED', r'G54\*?'),  # historic crud
            ('FUNCT', r'[GD][^\*]*\*'), # function code
            ('COORD', r'[XY][^\*]*\*'), # coordinates
            ('EOF', r'M02\*'),          # end of file
            ('SKIP', r'M0[01]\*|N[^\*]*\*|\s+'), # more historic crud, whitespace
            ('UNKNOWN', r'[^\*]*\*'),   # unintelligble data blocks
                                        # -- currently traps aperture defs and thermal descriptions
        ]
        reg_ex = '|'.join('(?P<%s>%s)' % pair for pair in tok_spec)
        tok_re = re.compile(reg_ex, re.MULTILINE)
        image_params = ('IJ', 'IN', 'IO', 'IP', 'IR', 'PF')
        directives = ('AS', 'FS', 'MI', 'MO', 'OF', 'SF')
        pos = matched = 0
        param_block = data_began = eof = False

        # read the file
        with open(self.filename, 'r') as ger:
            s = ger.read()

        # step through file data and extract tokens
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
                    elif len(typ) == 2: # PARAMS
                        self._check_pb(param_block)
                        if typ in image_params:
                            self.params[tok[:2]] = tok[2:]
                        elif typ in directives:
                            directive = self._parse_dir_param(tok)
                            if data_began:
                                yield directive
                            else:
                                self.params[typ] = directive
                        elif typ == 'AD':
                            aperture = self._parse_ap_def(tok)
                            if self.params.has_key(aperture.code):
                                yield aperture
                            else:
                                self.params[aperture.code] = aperture
                        else:
                            yield Param(tok[:2], tok[2:])
                    elif typ not in ('SKIP', 'UNKNOWN', 'COMMENT', 'DEPRECATED'):
                        self._check_pb(param_block, False)
                        if typ in ('FUNCT', 'COORD'):
                            if 'G' in tok:
                                g_code = tok[1:3] # assumes leading 0 is supplied... maybe flawed
                                tok = tok[3:]
                                yield Funct('G', g_code)
                            if 'D' in tok:
                                tok, d_code = tok.split('D')
                                yield Funct('D', d_code)
                            if tok:
                                data_began = True
                                yield self._parse_coord(tok)
                        elif typ == 'EOF':
                            self._check_eof(s[mo.end():])
                            eof = True
                except Unparsable:
                    raise
                pos = matched = mo.end()
            mo = tok_re.match(s, pos)
        # self._check_eof(eof)

    def _parse_dir_param(self, tok):
        name, tok = (tok[:2], tok[2:])
        if name == 'FS':
            tok, m_max = self._pop_val('M', tok)
            tok, d_max = self._pop_val('D', tok)
            tok, y = self._pop_val('Y', tok, coerce_int=False)
            y = CoordFmt(int(y[0]), int(y[1]))
            tok, x = self._pop_val('X', tok, coerce_int=False)
            x = CoordFmt(int(x[0]), int(x[1]))
            tok, g_max = self._pop_val('G', tok)
            tok, n_max = self._pop_val('N', tok)
            inc_coords = (tok[1] == 'I')
            z_omit = tok[0]
            tok = FormatSpec(z_omit, inc_coords, n_max, g_max,
                             x, y, d_max, m_max)
        return tok

    def _parse_ap_def(self, tok):
        code_end = tok[5] in digits and 6 or 5
        code = tok[3:code_end]
        type_, mods = tok[code_end:].split(',')
        return Aperture(code, type_, tuple(mods.split('X')))

    def _parse_coord(self, tok):
        self._check_fs()
        tok, j = self._pop_val('J', tok, format=True)
        tok, i = self._pop_val('I', tok, format=True)
        tok, y = self._pop_val('Y', tok, format=True)
        tok, x = self._pop_val('X', tok, format=True)
        result = Coord(x, y, i, j)
        if tok:
            raise Malformed('%s remainder=%s' % (result, tok))
        return result

    def _pop_val(self, coord, tok, format=False, coerce_int=True):
        val = None
        if coord in tok:
            tok, num_str = tok.split(coord)
            if num_str:
                if format:
                    if coord in ('X', 'I'):
                        val = self._format_dec(num_str, 4)
                    else:
                        val = self._format_dec(num_str, 5)
                else:
                    val = coerce_int and int(num_str) or num_str
        return (tok, val)

    def _format_dec(self, num_str, xy):
        fs = self.params['FS']
        sign_wid = num_str[0] in ('-', '+') and 1 or 0
        int_wid = sign_wid + fs[xy].int
        wid = int_wid + fs[xy].dec

        # pad to specified width
        if fs.zero_omission == 'L':
            num_str = num_str.zfill(wid)
        elif fs.zero_omission == 'T':
            num_str = num_str.rjust(wid, '0')
        if len(num_str) != wid:
            raise Malformed('num_str: %s wid: %s' % (num_str, wid))

        # insert decimal point
        num_str = '%s.%s' % (num_str[:int_wid], num_str[int_wid:])

        return float(num_str)

    def _check_pb(self, param_block, should_be=True):
        if should_be and not param_block:
            raise DelimiterMissing
        if param_block and not should_be:
            raise ContainsBadData

    def _check_fs(self):
        if not self.params['FS']:
            raise PrecedesFormatSpec

    def _check_eof(self, trailing_fragment):
        if trailing_fragment.strip():
            raise DataAfterEOF(trailing_fragment)
