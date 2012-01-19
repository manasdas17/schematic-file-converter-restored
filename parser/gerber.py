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
from math import sqrt, acos, pi
from collections import namedtuple

from core.design import Design
from core.layout import Layout, Layer, Trace
from core.shape import Line, Arc, Point

# exceptions

class Unparsable(ValueError):
    """ Superclass for all parser errors. """
    pass

class ParamError(Unparsable):
    """ Superclass for parameter errors. """
    pass

class CoordError(Unparsable):
    """ Superclass for coordinate errors. """
    pass

class DelimiterMissing(ParamError):
    """ Missing paramater block delimiter (%). """
    pass

class ParamContainsBadData(ParamError):
    """ Non-paramater found within param block. """
    pass

class CoordPrecedesFormatSpec(CoordError):
    """ Coordinate data prior to format specification. """
    pass

class CoordMalformed(CoordError):
    """ Coordinate block doesn't conform to spec. """
    pass

class FileNotTerminated(Unparsable):
    """ M02* was not encountered. """
    pass

class DataAfterEOF(Unparsable):
    """ M02* was not the last thing in the file. """
    pass

class UnintelligibleDataBlock(Unparsable):
    """ Data block did not conform to any known pattern. """
    pass

class ImpossibleGeometry(Unparsable):
    """ Arc radius, center and endpoints don't gel. """
    pass

# token classes

Aperture = namedtuple('Aperture', 'code type_ modifiers')           # pylint: disable=C0103
Coord = namedtuple('Coord', 'x y i j')                              # pylint: disable=C0103
CoordFmt = namedtuple('CoordFmt', 'int dec')                        # pylint: disable=C0103
AxisDef = namedtuple('AxisDef', 'a b')                              # pylint: disable=C0103
Funct = namedtuple('Funct', 'type_ code')                           # pylint: disable=C0103
FormatSpec = namedtuple('FormatSpec', ['zero_omission',             # pylint: disable=C0103
                        'incremental_coords', 'n_max', 'g_max',
                        'x', 'y', 'd_max', 'm_max'])

# parser status

Status = namedtuple('Status', ['x', 'y', 'draw', 'interpolation',   # pylint: disable=C0103
                               'aperture', 'outline_fill', 'multi_quadrant',
                               'units', 'incremental_coords'])

# constants

DIGITS = '0123456789'
D_MAP = {1:'ON', 2:'OFF', 3:'FLASH'}
G_MAP = {1:'LINEAR', 2:'CLOCKWISE_CIRCULAR', 3:'ANTICLOCKWISE_CIRCULAR',
         36:True, 37:False,
         70:'IN', 71:'MM',
         74:True, 75:False,
         90:True, 91:False}
AXIS_PARAMS = ('AS', 'MI', 'OF', 'SF', 'IJ', 'IO')
ALL_PARAMS = ('AS', 'FS', 'MI', 'MO', 'OF', 'SF',
              'IJ', 'IN', 'IO', 'IP', 'IR', 'PF', 'AD',
              'KO', 'LN', 'LP', 'SR')
TOK_SPEC = (('PARAM_DELIM', r'%'),
           ) + tuple([(p, r'%s[^\*]*\*' % p) for p in ALL_PARAMS]) + (
            ('COMMENT', r'G04[^\*]*\*'),
            ('DEPRECATED', r'G54\*?'), # historic crud
            ('FUNCT', r'[GD][^\*]*\*'),# function codes
            ('COORD', r'[XY][^\*]*\*'),# coordinates
            ('EOF', r'M02\*'),         # end of file
            ('SKIP', r'M0[01]\*|N[^\*]*\*|\s+'), # historic crud, whitespace
            ('UNKNOWN', r'[^\*]*\*'))  # unintelligble data block
                                       #TODO: handle aperture macros
IGNORE = ('SKIP', 'COMMENT', 'DEPRECATED')
REG_EX = '|'.join('(?P<%s>%s)' % pair for pair in TOK_SPEC)
TOK_RE = re.compile(REG_EX, re.MULTILINE)


# module global funct

def snap(float_1, float_2):
    """ Compare floats at max gerber precision (6dp). """
    return round(float_1, 6) == round(float_2, 6)


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
        status = Status(x=0, y=0, draw='OFF', interpolation='LINEAR',
                        aperture=None, outline_fill=False, multi_quadrant=False,
                        units=None, incremental_coords=None)
        for block in self._tokenize():
            if isinstance(block, Funct):
                status = self._do_funct(block, status)
            else:
                status = self._move(block, status)
        layout = Layout()
        layout.layers.append(self.layer)
        design = Design()
        design.layouts.append(layout)
        return design


    # primary parser support methods

    def _do_funct(self, block, status):
        """ Set drawing modes. """
        code = int(block.code)
        if block.type_ == 'D':
            if code < 10:
                status = status._replace(draw=D_MAP[code])          # pylint: disable=W0212
            else:
                status = status._replace(aperture=block.code)       # pylint: disable=W0212
        else:
            if code in range(1, 4):
                status = status._replace(interpolation=G_MAP[code]) # pylint: disable=W0212
            elif code in range(36, 38):
                status = status._replace(outline_fill=G_MAP[code])  # pylint: disable=W0212
            elif code in range(70, 72):
                status = status._replace(units=G_MAP[code])         # pylint: disable=W0212
            elif code in range(90, 92):
                status = status._replace(incremental=G_MAP[code])   # pylint: disable=W0212
        return status


    def _move(self, block, status):
        """ Draw a segment of a shape or trace. """
        x, y = self._target_pos(block, status)
        if status.draw == 'ON':
            #TODO: handle non-circular apertures
            if status.interpolation == 'LINEAR':
                segment = Line(status[:2], (x, y))
            else:
                clockwise = 'ANTI' not in status.interpolation
                segment = self._draw_arc(start_pt=Point(status[:2]),
                                         end_pt=Point(x, y),
                                         center_offset=block[2:],
                                         clockwise=clockwise)
            wid = self.params[status.aperture].modifiers[0]
            tr_index = self.layer.get_connected_trace(wid, status[:2], (x, y))
            if tr_index is None:

                # begin a new trace
                trace = Trace(wid, [segment])
                self.layer.traces.append(trace)
            else:

                # add segment to existing trace
                self.layer.traces[tr_index].segments.append(segment)

        elif status.draw == 'FLASH':
            pass #TODO: add some kind of shape to the layer

        return status._replace(x=x, y=y)                            # pylint: disable=W0212


    # coordinate interpretation

    def _target_pos(self, block, status):
        """ Interpret coordinates in a data block. """
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


    # circular paths

    def _draw_arc(self, start_pt, end_pt, center_offset, clockwise):
        """ Convert arc path into shape. """
        offset = {'i':center_offset[0], 'j':center_offset[1]}
        for k in offset:
            if offset[k] is None:
                offset[k] = 0
        center, radius = self._get_center_and_radius(start_pt, end_pt, offset)
        start_angle = self._get_angle(center, start_pt)
        end_angle = self._get_angle(center, end_pt)
        return Arc(center.x, center.y,
                   clockwise and start_angle or end_angle,
                   clockwise and end_angle or start_angle,
                   radius)


    def _get_center_and_radius(self, start_pt, end_pt, offset):
        """ Apply gerber circular interpolation logic. """
        radius = sqrt(offset['i']**2 + offset['j']**2)
        center = Point(x=start_pt.x + offset['i'],
                       y=start_pt.y + offset['j'])

        # In single-quadrant mode, gerber requires implicit
        # determination of offset direction, so we find the
        # center through trial and error.
        if not snap(center.dist(end_pt), radius):
            center = Point(x=start_pt.x - offset['i'],
                           y=start_pt.y - offset['j'])
            if not snap(center.dist(end_pt), radius):
                center = Point(x=start_pt.x + offset['i'],
                               y=start_pt.y - offset['j'])
                if not snap(center.dist(end_pt), radius):
                    center = Point(x=start_pt.x - offset['i'],
                                   y=start_pt.y + offset['j'])
                    if not snap(center.dist(end_pt), radius):
                        raise ImpossibleGeometry
        return (center, radius)


    def _get_angle(self, arc_center, point):
        """
        Convert 2 points to an angle in radians/pi.

        0 radians = 3 o'clock, in accordance with
        the way arc angles are defined in shape.py

        """
        adj = point.x - arc_center.x
        opp = point.y - arc_center.y
        hyp = arc_center.dist(point)
        angle = acos(adj/hyp)/pi
        if opp > 0:
            angle = 2 - angle
        return angle


    # tokenizer

    def _tokenize(self):
        """ Split gerber file into pythonic tokens. """
        param_block = eof = False
        pos = 0
        with open(self.filename, 'r') as ger:
            content = ger.read()
        match = TOK_RE.match(content)
        while pos < len(content):
            if match is None:
                pos += 1
            else:
                typ = match.lastgroup
                tok = match.group(typ)[:-1]
                try:
                    if typ == 'PARAM_DELIM':
                        param_block = not param_block

                    # params
                    elif len(typ) == 2:
                        self._check_pb(param_block, tok)
                        self.params.update((self._parse_param(tok),))

                    # data blocks
                    elif typ not in IGNORE:
                        self._check_pb(param_block, tok, False)
                        if typ == 'EOF':
                            self._check_eof(content[match.end():])
                            eof = True
                        else:
                            self._check_typ(typ, tok)

                            # explode self-referential data blocks
                            blocks = self._parse_data_block(tok)
                            for block in blocks:
                                yield block

                except Unparsable:
                    raise
                pos = match.end()
            match = TOK_RE.match(content, pos)
        self._check_eof(eof=eof)


    # tokenizer support methods - parameters

    def _parse_param(self, tok):
        """ Convert a param specifier into pythonic data. """
        name, tok = (tok[:2], tok[2:])
        if name == 'FS':
            tup = self._extract_fs(tok)
        elif name == 'AD':
            tup = self._extract_ad(tok)
            name = tup.code
        elif name in AXIS_PARAMS:
            tup = self._extract_ap(name, tok)
        else:
            #TODO: handle  IP, IR, layer params KO, LN, LP, SR
            #TODO: check file for duplicate image_params
            #      (should use last occurrence for entire file)
            tup = tok
        return (name, tup)


    def _extract_fs(self, tok):
        """ Extract format spec param parts into tuple. """
        tok, m_max = self._pop_val('M', tok)
        tok, d_max = self._pop_val('D', tok)
        tok, y = self._pop_val('Y', tok, coerce_=False)
        y = CoordFmt(int(y[0]), int(y[1]))
        tok, x = self._pop_val('X', tok, coerce_=False)
        x = CoordFmt(int(x[0]), int(x[1]))
        tok, g_max = self._pop_val('G', tok)
        tok, n_max = self._pop_val('N', tok)
        inc_coords = (tok[1] == 'I')
        z_omit = tok[0]
        return FormatSpec(z_omit, inc_coords, n_max, g_max,
                          x, y, d_max, m_max)


    def _extract_ad(self, tok):
        """ Extract aperture definition into tuple. """
        code_end = tok[3] in DIGITS and 4 or 3
        name = tok[1:code_end]
        type_, mods = tok[code_end:].split(',')
        return Aperture(name, type_, tuple(mods.split('X')))


    def _extract_ap(self, name, tok):
        """ Extract axis-defining param into tuple. """
        if name in ('AS', 'IJ'):
            coerce_ = False
        else:
            coerce_ = name == 'MI' and 'int' or 'float'
        tok, b_val = self._pop_val('B', tok, coerce_=coerce_)
        tok, a_val = self._pop_val('A', tok, coerce_=coerce_)
        if name == 'IJ':
            tup = AxisDef(self._parse_justify(a_val),
                          self._parse_justify(b_val))
        else:
            tup = AxisDef(a_val, b_val)
        return tup


    def _parse_justify(self, val):
        """ Make a tuple for each axis (special case). """
        if len(val) > 1 or val not in 'LC':
            ab_tup = ('L', float(val.split('L')[-1]))
        else:
            ab_tup = (val, None)
        #TODO: spec for IJ references off-spec examples
        #      with , or . delimiters
        return ab_tup


    # tokenizer support methods - functions and coordinates

    def _parse_data_block(self, tok):
        """ Convert a non-param into pythonic data. """
        if 'G' in tok:
            g_code = tok[1:3]
            tok = tok[3:]
            #TODO: remove assumption that leading 0 is
            #      supplied -- not required by spec
            yield Funct('G', g_code)
        tok, d_code = self._pop_val('D', tok, coerce_=False)
        if d_code:
            yield Funct('D', d_code)
        if tok:
            yield self._parse_coord(tok)


    def _parse_coord(self, tok):
        """ Convert a coordinate set into pythonic data. """
        self._check_fs()
        tok, j = self._pop_val('J', tok, format_=True)
        tok, i = self._pop_val('I', tok, format_=True)
        tok, y = self._pop_val('Y', tok, format_=True)
        tok, x = self._pop_val('X', tok, format_=True)
        result = Coord(x, y, i, j)
        if tok:
            raise CoordMalformed('%s remainder=%s' % (result, tok))
        return result


    def _format_dec(self, num_str, axis):
        """
        Interpret a coordinate value using format spec.

        Params: num_str (the string representation of a number
                         portended by format spec)
                axis (X or Y - not to be confused with A/B)

        Returns: float

        """
        f_spec = self.params['FS']
        sign_wid = num_str[0] in ('-', '+') and 1 or 0
        int_wid = sign_wid + f_spec[axis].int
        wid = int_wid + f_spec[axis].dec

        # pad coordinate to specified width
        if f_spec.zero_omission == 'L':
            num_str = num_str.zfill(wid)
        elif f_spec.zero_omission == 'T':
            num_str = num_str.rjust(wid, '0')
        if len(num_str) != wid:
            raise CoordMalformed('num_str: %s wid: %s' % (num_str, wid))

        # insert decimal point
        num_str = '%s.%s' % (num_str[:int_wid], num_str[int_wid:])

        return float(num_str)


    # general support methods

    def _pop_val(self, key, tok, format_=False, coerce_='int'):
        """ Pop a labelled value from the end of a token. """
        val = None
        if key in tok:
            tok, num_str = tok.split(key)
            if num_str:
                if format_:
                    if key in ('X', 'I'):
                        val = self._format_dec(num_str, 4)
                    else:
                        val = self._format_dec(num_str, 5)
                else:
                    val = coerce_ and (coerce_ == 'float' and
                                      float(num_str) or
                                      int(num_str)) or num_str
        return (tok, val)


    def _check_pb(self, param_block, tok, should_be=True):
        """ Ensure we are parsing an appropriate block. """
        if should_be and not param_block:
            raise DelimiterMissing
        if param_block and not should_be:
            raise ParamContainsBadData(tok)


    def _check_fs(self):
        """ Ensure coordinate is able to be interpreted. """
        if not self.params['FS']:
            raise CoordPrecedesFormatSpec


    def _check_eof(self, trailing_fragment=None, eof=False):
        """ Ensure file is terminated correctly. """
        if not (trailing_fragment or eof):
            raise FileNotTerminated
        elif (not eof) and trailing_fragment.strip():
            raise DataAfterEOF(trailing_fragment)


    def _check_typ(self, typ, tok):
        """ Ensure data block is understood by the parser. """
        if typ == 'UNKNOWN':
            raise UnintelligibleDataBlock(tok)
