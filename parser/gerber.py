#!/usr/bin/env python
""" The Gerber RS274-X Format Parser """

from collections import namedtuple

from core.design import Design
from core.layout import Layout

# exceptions

class Unparsable(ValueError):
    pass

class ParamError(Unparsable):
    pass

class CoordError(Unparsable):
    pass

class DelimiterMissing(ParamError):
    pass

class ContainsBadData(ParamError):
    pass

class PrecedesFormatSpec(CoordError):
    pass

class Malformed(CoordError):
    pass

class DataAfterEOF(Unparsable):
    pass

# token classes

Funct = namedtuple('Funct', 'type_ code')
Param = namedtuple('Param', 'id_ val')
Coord = namedtuple('Coord', 'x y i j')

# parser

class Gerber:
    """ The Gerber Format Parser """

    def __init__(self, filename=None):
        self.filename = filename
        self.dir_params = {'AS':'AXBY',   # axis select
                           'FS':'',       # format spec
                           'MI':'A0B0',   # mirror image
                           'MO':'IN',     # mode
                           'OF':'A0B0',   # offset
                           'SF':'A1B1'}   # scale factor
        self.img_params = {'IN':'',       # image name
                           'IJ':'AL0BL0', # justification
                           'IO':'A0B0',   # offset
                           'IP':'POS',    # polarity
                           'IR':'0',      # rotation
                           'PF':''}       # plot film

    def parse(self):
        """ Parse a Gerber file into a design """
        design = Design()
        data = self._tokenize()
            for data_block in data:
                print data_block
        return design

    def _tokenize(self):
        tok_spec = [
            ('PARAM_DELIM', r'%'),                                  # parameter delimiter
            ('DIR_PARAM', r'(AS|FS|MI|MO|OF|SF)[^\*]*\*'),          # directive parameter
            ('IMG_PARAM', r'(IJ|IN|IO|IP|IR|PF)[^\*]*\*'),          # image parameter
            ('LYR_PARAM', r'(KO|LN|LP|SR)[^\*]*\*'),                # layer parameter
            ('FUNCT', r'[GD][^\*]*\*'),                             # function code
            ('COORD', r'[XY][^\*]*\*'),                             # coordinates
            ('EOF', 'M02'),                                         # end of file
            ('SKIP', r'G04[^\*]*\*|G54?\*|M0[01]\*|N[^\*]*\*|\s+'), # comments, historic crud, whitespace
            ('UNKNOWN', r'[^\*]*\*'),                               # unintelligble data blocks
                                                                    # -- traps thermal descriptions as well
        ]
        reg_ex = '|'.join('(?P<%s>%s)' % pair for pair in tok_spec)
        tok_re = re.compile(reg_ex, re.MULTILINE)
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
                tok = mo.group(typ)[:-1] # strips *
                try:
                    if typ == 'PARAM_DELIM':
                        param_block = not param_block
                    elif '_PARAM' in typ:
                        self._check_pb(param_block)
                        if typ == 'IMG_PARAM':
                            self.img_params[tok[:2]] = tok[2:]
                        elif typ == 'DIR_PARAM' and not data_began:
                            self.dir_params[tok[:2]] = tok[2:]
                        else:
                            yield Param(tok[:2], tok[2:])
                    elif typ != 'SKIP':
                        self._check_pb(param_block, False)
                        if typ in ('FUNCT', 'COORD'):
                            if 'G' in tok:
                                g_code = tok[1:2]
                                tok = tok[2:]
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

    def _parse_coord(self, tok):
        self._check_fs()
        tok, j = self._extract('J', tok)
        tok, i = self._extract('I', tok)
        tok, y = self._extract('Y', tok)
        tok, x = self._extract('X', tok)
        if tok:
            raise Malformed
        return Coord(x, y, i, j)

    def _extract(coord, tok):
        if coord in tok:
            tok, num_string = tok.split(coord)

            # tidy up according to format spec
            val ### format spec for I,J ????
        return tuple(tok, val)

    def _check_pb(self, param_block, should_be=True):
        if should_be and not param_block:
            raise DelimiterMissing
        if param_block and not should_be:
            raise ContainsBadData

    def _check_fs(self):
        if not self.dir_params['FS']:
            raise PrecedesFormatSpec

    def _check_eof(self, trailing_fragment):
        if trailing_fragment.strip():
            raise DataAfterEOF
