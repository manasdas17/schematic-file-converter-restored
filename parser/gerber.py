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
from math import sqrt, asin, pi
from collections import namedtuple

from core.design import Design
from core.layout import Layout, Layer, Trace
from core.shape import Line, Arc, Point

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

Status = namedtuple('Status', ['x', 'y', 'draw', 'interpolation',
                               'aperture', 'outline_fill', 'multi_quadrant',
                               'units', 'incremental_coords'])

# constants
d_map = {1:'ON', 2:'OFF', 3:'FLASH'}
g_map = {1:'LINEAR', 2:'CLOCKWISE_CIRCULAR', 3:'ANTICLOCKWISE_CIRCULAR',
         36:True, 37:False,
         70:'IN', 71:'MM',
         74:True, 75:False,
         90:True, 91:False}

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
        print self.layer.json()
        layout = Layout()
        layout.layers.append(self.layer)
        design = Design()
        design.layouts.append(layout)
        return design

    def _do_funct(self, block, status):
        """ Set drawing modes. """
        code = int(block.code)
        if block.type_ == 'D':
            if code < 10:
                status = status._replace(draw=d_map[code])
            else:
                status = status._replace(aperture=block.code)
        else:
            if code in range(1, 4):
                status = status._replace(interpolation=g_map[code])
            elif code in range(36, 38):
                status = status._replace(outline_fill=g_map[code])
            elif code in range(70, 72):
                status = status._replace(units=g_map[code])
            elif code in range(90, 92):
                status = status._replace(incremental=g_map[code])
        return status

    def _move(self, block, status):
        """ Draw a segment of a shape or trace. """
        x, y = self._target_pos(block, status)
        if status.draw == 'ON':
            #TODO: handle non-circular apertures
            if status.interpolation == 'LINEAR':
                segment = Line(status[:2], (x, y))
            else:
                clockwise = 'CLOCKWISE' in status.interpolation
                segment = self._draw_arc(start_pt=Point(status[:2]),
                                         end_pt=Point(x, y),
                                         center_offset=block[2:],
                                         clockwise=clockwise)
            w = self.params[status.aperture].modifiers[0]
            tr_index = self.layer.get_connected_trace(w, status[:2], (x,y))
            if tr_index is None:

                # begin a new trace
                trace = Trace(w, [segment])
                self.layer.traces.append(trace)
            else:

                # add segment to existing trace
                self.layer.traces[tr_index].segments.append(segment)

        elif status.draw == 'FLASH':
            pass #TODO: add some kind of shape to the layer

        return status._replace(x=x, y=y)

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

    def _draw_arc(self, start_pt, end_pt, center_offset, clockwise):
        """ Convert arc path into shape. """
        if clockwise:
            start, end = (start_pt, end_pt)
        else:
            start, end = (end_pt, start_pt)
        offset = {'i':center_offset[0], 'j':center_offset[1]}
        for k in offset:
            if offset[k] is None:
                offset[k] = 0
        center, radius = self._get_center_and_radius(start, end, offset)
        start_angle = self._get_angle(center, start)
        end_angle = self._get_angle(center, end)
        return Arc(center.x, center.y, start_angle, end_angle, radius)

    def _get_center_and_radius(self, start_pt, end_pt, offset):
        """ Apply gerber circular interpolation logic. """
        radius = sqrt(offset['i']**2 + offset['j']**2)
        center = Point(x=start_pt.x + offset['i'],
                       y=start_pt.y + offset['j'])

        # In single-quadrant mode, gerber requires implicit
        # determination of offset direction, so we find the
        # center through trial and error.
        if not self._almost_equals(center.dist(end_pt), radius):
            center = Point(x=start_pt.x - offset['i'],
                           y=start_pt.y - offset['j'])
            if not self._almost_equals(center.dist(end_pt), radius):
                center = Point(x=start_pt.x + offset['i'],
                               y=start_pt.y - offset['j'])
                if not self._almost_equals(center.dist(end_pt), radius):
                    center = Point(x=start_pt.x - offset['i'],
                                   y=start_pt.y + offset['j'])
                    if not self._almost_equals(center.dist(end_pt), radius):
                        raise ImpossibleGeometry
        return (center, radius)

    def _get_angle(self, arc_center, point):
        """
        Convert 2 points to an angle in radians/pi.

        Quadrants are counter-cartesian, in accordance with
        the way arc angles are defined in shape.py

        """
        opp = arc_center.y - point.y
        adj = arc_center.x - point.x
        hyp = arc_center.dist(point)
        angle = asin(opp/hyp)/pi
        if adj > 0: # Q2 and Q3
            angle = 1 - angle
        elif opp < 0 and adj < 0: # Q4
            angle += 2
        return angle

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
                                               #TODO: handle aperture macros

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
        """ Convert a param specifier into pythonic data. """
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
        #TODO: handle  IP, IR, layer params KO, LN, LP, SR (if they matter)
        #TODO: check file for duplicate image_params -- should use last occurrence for entire file
        return (name, tok)

    def _parse_data_block(self, tok):
        """ Convert a non-param into pythonic data. """
        if 'G' in tok:
            g_code = tok[1:3] #TODO: remove assumption that leading 0 is supplied -- not required by spec
            tok = tok[3:]
            yield Funct('G', g_code)
        tok, d_code = self._pop_val('D', tok, coerce=False)
        if d_code:
            yield Funct('D', d_code)
        if tok:
            yield self._parse_coord(tok)

    def _parse_coord(self, tok):
        """ Convert a coordinate set into pythonic data. """
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
        """ Pop a labelled value from the end of a token. """
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
        """ Interpret a coordinate value using format spec. """
        fs = self.params['FS']
        sign_wid = num_str[0] in ('-', '+') and 1 or 0
        int_wid = sign_wid + fs[xy].int
        wid = int_wid + fs[xy].dec

        # pad coordinate to specified width
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
        """ Unlike other axis defs, return a tuple. """
        if len(tok) > 1 or tok not in 'LC':
            result = ('L', float(tok.split('L')[-1]))
        else:
            result = (tok, None)
        #TODO: spec for IJ references off-spec examples with , or . delimiters
        return result

    def _almost_equals(self, f1, f2):
        """ Check floats for equality (with 0.1% margin). """
        margin = abs(0.001 * f2)
        print margin, f1, f2
        return (f2 - margin) <= f1 <= (f2 + margin)

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
