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
class ParamContainsBadData(ParamError): pass
class CoordPrecedesFormatSpec(CoordError): pass
class CoordMalformed(CoordError): pass
class FileNotTerminated(Unparsable): pass
class DataAfterEOF(Unparsable): pass
class UnintelligibleDataBlock(Unparsable): pass

# token classes

Aperture = namedtuple('Aperture', 'id_ code type_ modifiers')
Coord = namedtuple('Coord', 'x y i j')
CoordFmt = namedtuple('CoordFmt', 'int dec')
AxisDef = namedtuple('AxisDef', 'id_ a b')
Funct = namedtuple('Funct', 'type_ code')
Param = namedtuple('Param', 'id_ val')
FormatSpec = namedtuple('FormatSpec', ['id_', 'zero_omission',
                        'incremental_coords', 'n_max', 'g_max',
                        'x', 'y', 'd_max', 'm_max'])

# parser status

Status = namedtuple('Status', 'x y draw aperture')

# parser

class Gerber:
    """ The Gerber Format Parser """

    def __init__(self, filename=None):
        self.filename = filename

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
        layout = Layout()
        data = self._tokenize()
        status = Status(0.0, 0.0, False, None)
        for block in data:
            if isinstance(block, Funct):
                status = self._do_funct(block, status)
            elif isinstance(block, Coord):
                self._go(block, layout, status)
            else:
                self.params[block.id_] = block
        design = Design()
        design.layouts.append(layout)
        return design

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
                                               # -- currently traps aperture macros

        # define constants and counters
        reg_ex = '|'.join('(?P<%s>%s)' % pair for pair in tok_spec)
        tok_re = re.compile(reg_ex, re.MULTILINE)
        directives = all_params[:6]
        img_params = all_params[6:12]
        stored_params = all_params[:13]
        layer_params = all_params[13:]
        ignore = ('SKIP', 'COMMENT', 'DEPRECATED')
        pos = matched = 0
        param_block = data_began = eof = False

        # read the file
        with open(self.filename, 'r') as ger:
            s = ger.read()

        # step through file content, extracting tokens
        mo = tok_re.match(s)
        while pos < len(s):
            if mo is None:
                pos += 1
            else:
                typ = mo.lastgroup
                tok = mo.group(typ)[:-1]

                # store tokens as useful pythonic structures
                try:
                    if typ == 'PARAM_DELIM':
                        param_block = not param_block

                    # handle params
                    elif len(typ) == 2:
                        self._check_pb(param_block, tok)
                        param = self._parse_param(tok)
                        do_yield = (typ in directives and
                                    data_began) or (typ == 'AD' and
                                    self.params.has_key(param.code)) or (
                                    typ not in stored_params)

                        # Though params can change mid-stream,
                        # they are often condensed in a single
                        # block at the top of the file and
                        # thence remain static throughout...
                        # Most of them are going to be cached
                        # in the params dict. We only yield
                        # them into the data generator if their
                        # position in the file is relevant.
                        if do_yield:
                            yield param
                        else:
                            self.params[typ] = param

                    # handle data
                    elif typ not in ignore:
                        self._check_pb(param_block, tok, False)
                        if typ == 'EOF':
                            self._check_eof(s[mo.end():])
                            eof = True
                        else:
                            self._check_typ(typ, tok)
                            data_began = True # TODO: allow FS following funct but preceding coord

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
            tok = FormatSpec('FS', z_omit, inc_coords, n_max, g_max,
                             x, y, d_max, m_max)
        elif name == 'AD':
            code_end = tok[3] in digits and 4 or 3
            code = tok[1:code_end]
            type_, mods = tok[code_end:].split(',')
            tok = Aperture('AD', code, type_, tuple(mods.split('X')))
        elif name == 'LN':
            tok = Param(name, tok)
        elif name in axis_params:
            if name in ('AS', 'IJ'):
                coerce = False
            else:
                coerce = name == 'MI' and 'int' or 'float'
            tok, b = self._pop_val('B', tok, coerce=coerce)
            tok, a = self._pop_val('A', tok, coerce=coerce)
            if name == 'IJ':
                tok = AxisDef(name, self._parse_justify(a), self._parse_justify(b))
            else:
                tok = AxisDef(name, a, b)
        # TODO: handle  IP, IR, layer params KO, LP, SR
        return tok # TODO: MO, IN, PF are naked strings -- maybe not good -- & use a more sensible var

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
