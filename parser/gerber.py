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
from math import sqrt, sin, cos, acos, pi
from collections import namedtuple

from core.design import Design
from core.layout import Layout, Layer, Image, Macro, Primitive, \
                        Trace, Smear, ShapeInstance
from core.shape import Line, Arc, Point, Circle, Rectangle, Obround, \
                       Polygon, RegularPolygon, Moire, Thermal


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

class QuadrantViolation(CoordError):
    """ Single quadrant arc longer than 0.5 radians/pi. """
    pass

class OpenFillBoundary(CoordError):
    """ Fill boundary ends do not equate. """
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

class IncompatibleAperture(Unparsable):
    """ Attempted to draw non-linear shape with rect. """
    pass


# token classes

MacroDef = namedtuple('MacroDef', 'name primitive_defs')            # pylint: disable=C0103
Coord = namedtuple('Coord', 'x y i j')                              # pylint: disable=C0103
CoordFmt = namedtuple('CoordFmt', 'int dec')                        # pylint: disable=C0103
AxisDef = namedtuple('AxisDef', 'a b')                              # pylint: disable=C0103
Funct = namedtuple('Funct', 'type_ code')                           # pylint: disable=C0103
FormatSpec = namedtuple('FormatSpec', ['zero_omission',             # pylint: disable=C0103
                        'incremental_coords', 'n_max', 'g_max',
                        'x', 'y', 'd_max', 'm_max'])


# constants

DIGITS = '0123456789'
PRIMITIVES = {1:'circle',
              2:'vector',
              20:'vector',
              21:'line',
              22:'rectangle',
              4:'outline',
              5:'polygon',
              6:'moire',
              7:'thermal'}
D_MAP = {1:'ON', 2:'OFF', 3:'FLASH'}
G_MAP = {1:{'interpolation':'LINEAR'},
         2:{'interpolation':'CLOCKWISE_CIRCULAR'},
         3:{'interpolation':'ANTICLOCKWISE_CIRCULAR'},
         36:{'outline_fill':True},
         37:{'outline_fill':False},
         70:{'units':'IN'},
         71:{'units':'MM'},
         74:{'multi_quadrant':False},
         75:{'multi_quadrant':True},
         90:{'incremental':True},
         91:{'incremental':False}}
IMAGE_POLARITIES = {'C': False,
                    'D': True}
AXIS_PARAMS = ('AS', 'MI', 'OF', 'SF', 'IJ', 'IO')
ALL_PARAMS = ('AS', 'FS', 'MI', 'MO', 'OF', 'SF',
              'IJ', 'IN', 'IO', 'IP', 'IR', 'PF', 'AD',
              'KO', 'LN', 'LP', 'SR')
LAYER_PARAMS = ALL_PARAMS[-4:]
TOK_SPEC = (('MACRO', r'%AM[^%]*%'),
            ('PARAM_DELIM', r'%'),
           ) + tuple([(p, r'%s[^\*]*\*' % p) for p in ALL_PARAMS]) + (
            ('COMMENT', r'G04[^\*]*\*'),
            ('DEPRECATED', r'G54\*?'), # historic crud
            ('FUNCT', r'[GD][^\*]*\*'),# function codes
            ('COORD', r'[XY][^\*]*\*'),# coordinates
            ('EOF', r'M02\*'),         # end of file
            ('SKIP', r'M0[01]\*|N[^\*]*\*|\s+'), # historic crud, whitespace
            ('UNKNOWN', r'[^\*]*\*'))  # unintelligble data block
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

    def __init__(self, filename='.'):
        name, ext = filename.rsplit('.', 1)
        layer_name = ext.lower() == 'ger' and name or ext
        self.filename = filename
        self.layer = Layer(layer_name)
        self.img_buff = Image()
        self.fill_buff = []

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
        self.status = {'x':0,
                       'y':0,
                       'draw':'OFF',
                       'interpolation':'LINEAR',
                       'aperture':None,
                       'outline_fill':False,
                       'multi_quadrant':False,
                       'units':None,
                       'incremental_coords':None}


    def parse(self):
        """ Parse tokens from gerber file into a design. """
        for block in self._tokenize():
            if isinstance(block, MacroDef):
                effect = self._build_macro(block)
            elif isinstance(block, Funct):
                effect = self._do_funct(block)
            else:
                effect = self._move(block)
            self.status.update(effect)
        for image in self.layer.images:
            print '-- %s --' % image.name
            print image.json()
        layout = Layout()
        layout.layers.append(self.layer)
        design = Design()
        design.layouts.append(layout)
        return design


    # primary parser support methods

    def _build_macro(self, block):
        """ Build a macro out of component shape defs. """
        primitives = []
        for p_def in block.primitive_defs:
            type_, mods = (p_def[0], [float(i) for i in p_def[1:]])
            is_additive = type_ in ('moire', 'thermal') or int(mods[0])
            rotation = type_ not in ('circle', 'moire',
                                     'thermal') and mods[-1]/180
            shape, rotation = self._gen_shape(type_, mods, rotation)
            primitives.append(Primitive(is_additive, rotation, shape))

        # generate and stow the macro
        self.layer.macros[block.name] = Macro(block.name, primitives)
        return {}


    def _do_funct(self, block):
        """ Set drawing modes, fill terminators. """
        code = int(block.code)
        if block.type_ == 'D':
            if code < 10:
                effect = {'draw':D_MAP[code]}

                # terminate fill mid mode
                if (self.status['outline_fill'] and
                    code == 2 and self.fill_buff):
                    self.img_buff.fills.append(self._check_fill())

            else:
                effect = {'aperture':block.code}
        else:
            effect = G_MAP[code]
            if code == 37:

                # terminate fill if D02 was not specified
                if self.fill_buff:
                    self.img_buff.fills.append(self._check_fill())

        return effect


    def _move(self, block):
        """ Draw a shape, or a segment of a trace or fill. """
        start = tuple([self.status[k] for k in ('x', 'y')])
        end = self._target_pos(block)
        ends = (Point(start), Point(end))
        shapes = self.layer.shapes
        if self.status['draw'] == 'ON':

            # generate segment
            if self.status['interpolation'] == 'LINEAR':
                seg = Line(start, end)
            else:
                ctr_offset = block[2:]
                seg = self._draw_arc(ends, ctr_offset)

            # append segment to fill
            if self.status['outline_fill']:
                self.fill_buff.append(seg)

            else:
                aperture = shapes[self.status['aperture']]
                if isinstance(aperture[0], Rectangle):

                    # construct a smear
                    shape, hole = shapes[self.status['aperture']]
                    self._check_smear(seg, shape)
                    self.img_buff.smears.append(Smear(seg, shape))

                else:
                    wid = aperture[0].radius * 2
                    tr_ind = self.img_buff.get_trace(wid, ends)
                    if tr_ind is None:

                        # construct a trace
                        self.img_buff.traces.append(Trace(wid, [seg]))
                    else:

                        # append segment to existing trace
                        self.img_buff.traces[tr_ind].segments.append(seg)

        elif self.status['draw'] == 'FLASH':
            shape, hole = shapes[self.status['aperture']]
            shape_inst = ShapeInstance(ends[1], shape, hole)
            self.img_buff.shape_instances.append(shape_inst)

        return {'x':end[0], 'y':end[1]}


    # coordinate interpretation

    def _target_pos(self, block):
        """ Interpret coordinates in a data block. """
        coord = {'x':block.x, 'y':block.y}
        for k in coord:
            if self.params['FS'].incremental_coords:
                if coord[k] is None:
                    coord[k] = 0
                coord[k] = self.status[k] + getattr(block, k)
            else:
                if coord[k] is None:
                    coord[k] = self.status[k]
        return (coord['x'], coord['y'])


    # geometry

    def _gen_shape(self, type_, mods, rotation):
        """ Create a primitive shape component for a macro. """
        if type_ == 'circle':
            shape = Circle(x=mods[2],
                           y=mods[3],
                           radius=mods[1]/2)
        elif type_ == 'vector':
            shape, rotation = self._vector_to_rect(mods,
                                                   rotation)
        elif type_ == 'line':
            shape = Rectangle(x=mods[3] - mods[1]/2,
                              y=mods[4] + mods[2]/2,
                              width=mods[1],
                              height=mods[2])
        elif type_ == 'rectangle':
            shape = Rectangle(x=mods[3],
                              y=mods[4] + mods[2],
                              width=mods[1],
                              height=mods[2])
        elif type_ == 'outline':
            points = [Point(mods[i], mods[i + 1])
                      for i in range(2, len(mods[:-1]), 2)]
            shape = Polygon(points)
        elif type_ == 'polygon':
            shape = RegularPolygon(x=mods[2],
                                   y=mods[3],
                                   outer=mods[4],
                                   vertices=mods[1])
        elif type_ == 'moire':
            mods[8] = 2 - mods[8]/180
            shape = Moire(*mods[0:9])
        elif type_ == 'thermal':
            mods[5] = 2 - mods[5]/180
            shape = Thermal(*mods[0:6])
        return (shape, rotation)


    def _vector_to_rect(self, mods, rotation):
        """
        Convert a vector into a Rectangle.

        Strategy
        ========
        If vect is not horizontal:
            - rotate about the origin until horizontal
            - define it as a normal rectangle
            - incorporate rotated angle into explicit rotation

        """
        start, end = (mods[2:4], mods[4:6])
        start_radius = sqrt(start[0]**2 + start[1]**2)
        end_radius = sqrt(end[0]**2 + end[1]**2)

        # Reverse the vector if its endpoint is closer
        # to the origin than its start point (avoids
        # mucking about with signage later).
        if start_radius > end_radius:
            end, start = (mods[2:4], mods[4:6])
            radius = end_radius
        else:
            radius = start_radius

        # Calc the angle of the vector with respect to
        # the x axis.
        x, y = start
        adj = end[0] - x
        opp = end[1] - y
        hyp = sqrt(adj**2 + opp**2)
        theta = acos(adj/hyp)/pi
        if opp > 0:
            theta = 2 - theta

        # Represent vector angle as a delta.
        d_theta = 2 - theta

        # Calc the angle of the start point of the
        # flattened vector.
        theta = acos(x/radius)/pi 
        if y > 0:
            theta = 2 - theta
        theta += d_theta

        # Redefine x and y at center of the rect's left
        # side.
        y = sin((2 - theta) * pi) * radius
        x = cos((2 - theta) * pi) * radius

        # Calc the composite rotation angle.
        rotation = (rotation + theta) % 2

        return (Rectangle(x=x,
                          y=y + mods[1]/2,
                          width=hyp,
                          height=mods[1]),
                rotation)


    def _draw_arc(self, end_pts, center_offset):
        """ Convert arc path into shape. """
        start, end = end_pts
        offset = {'i':center_offset[0], 'j':center_offset[1]}
        for k in offset:
            if offset[k] is None:
                offset[k] = 0
        center, radius = self._get_ctr_and_radius(end_pts, offset)
        start_angle = self._get_angle(center, start)
        end_angle = self._get_angle(center, end)
        self._check_mq(start_angle, end_angle)
        clockwise = 'ANTI' not in self.status['interpolation']
        return Arc(center.x, center.y,
                   clockwise and start_angle or end_angle,
                   clockwise and end_angle or start_angle,
                   radius)


    def _get_ctr_and_radius(self, end_pts, offset):
        """ Apply gerber circular interpolation logic. """
        start, end = end_pts
        radius = sqrt(offset['i']**2 + offset['j']**2)
        center = Point(x=start.x + offset['i'],
                       y=start.y + offset['j'])

        # In single-quadrant mode, gerber requires implicit
        # determination of offset direction, so we find the
        # center through trial and error.
        if not self.status['multi_quadrant']:
            if not snap(center.dist(end), radius):
                center = Point(x=start.x - offset['i'],
                               y=start.y - offset['j'])
                if not snap(center.dist(end), radius):
                    center = Point(x=start.x + offset['i'],
                                   y=start.y - offset['j'])
                    if not snap(center.dist(end), radius):
                        center = Point(x=start.x - offset['i'],
                                       y=start.y + offset['j'])
                        if not snap(center.dist(end), radius):
                            raise ImpossibleGeometry
        return (center, radius)


    def _get_angle(self, arc_center, point):
        """
        Convert 2 points to an angle in radians/pi.

        0 radians = 3 o'clock, in accordance with
        the way arc angles are defined in shape.py

        """
        adj = float(point.x - arc_center.x)
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
                    if typ == 'MACRO':
                        yield self._parse_macro(tok)
                    elif typ == 'PARAM_DELIM':
                        param_block = not param_block

                    # params
                    elif len(typ) == 2:
                        self._check_pb(param_block, tok)
                        self.params.update(self._parse_param(tok))

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
        self.layer.images.append(self.img_buff)


    # tokenizer support - macros

    def _parse_macro(self, tok):
        """ Define a macro, with its component shapes. """
        parts = tok.split('*')
        name = parts[0][3:]
        prims =  [part.strip().split(',') for part in parts[1:-1]] 
        prim_defs = tuple([(PRIMITIVES[int(m[0])],) + tuple(m[1:])
                           for m in prims])
        return MacroDef(name, prim_defs)


    # tokenizer support - params

    def _parse_param(self, tok):
        """ Convert a param specifier into pythonic data. """
        name, tok = (tok[:2], tok[2:])
        if name == 'FS':
            tup = self._extract_fs(tok)
        elif name == 'AD':
            self._extract_ad(tok)
            return {}
        elif name in AXIS_PARAMS:
            tup = self._extract_ap(name, tok)
        elif name in LAYER_PARAMS:
            self._extract_lp(name, tok)
            return {}
        else:
            tup = tok
        return {name:tup}


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
        """ Extract aperture definition into shapes dict. """
        tok = ',' in tok and tok or tok + ','
        code_end = tok[3] in DIGITS and 4 or 3
        code = tok[1:code_end]
        type_, mods = tok[code_end:].split(',')
        if mods:
            mods = [float(m) for m in mods.split('X')]

        # An aperture can use any of the 4 standard types,
        # (with or without a central hole), or a previously
        # defined macro.
        if type_ == 'C':
            shape = Circle(0, 0, mods[0]/2)
            hole_defs = len(mods) > 1 and mods[1:]
        elif type_ == 'R':
            shape = Rectangle(-mods[0]/2, mods[1]/2,
                              mods[0], mods[1])
            hole_defs = len(mods) > 2 and mods[2:]
        elif type_ == 'O':
            shape = Obround(0, 0, mods[0], mods[1])
            hole_defs = len(mods) > 2 and mods[2:]
        elif type_ == 'P':
            if len(mods) < 3:
                mods.append(0)
            shape = RegularPolygon(0, 0, mods[0], mods[1], mods[2])
            hole_defs = len(mods) > 3 and mods[3:]
        else:
            shape = type_
            hole_defs = None
        hole = hole_defs and (len(hole_defs) > 1 and
                              Rectangle(-hole_defs[0]/2,
                                        hole_defs[1]/2,
                                        hole_defs[0],
                                        hole_defs[1]) or
                              Circle(0, 0, hole_defs[0]/2))

        self.layer.shapes.update({code:(shape, hole)})


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


    def _extract_lp(self, name, tok):
        """ Extract "layer param" and reset image layer. """
        if self.img_buff.not_empty():
            self.layer.images.append(self.img_buff)
            self.img_buff = Image('', self.img_buff.is_additive)
            self.status.update({'x':0,
                                'y':0,
                                'draw':'OFF',
                                'interpolation':'LINEAR',
                                'aperture':None,
                                'outline_fill':False,
                                'multi_quadrant':False,
                                'units':None,
                                'incremental_coords':None})
        if name == 'LN':
            self.img_buff.name = tok
        elif name == 'LP':
            self.img_buff.is_additive = IMAGE_POLARITIES[tok]
        elif name == 'SR':
            tok, j = self._pop_val('J', tok, coerce_='float')
            tok, i = self._pop_val('I', tok, coerce_='float')
            tok, y = self._pop_val('Y', tok)
            tok, x = self._pop_val('X', tok)
            self.img_buff.x_repeats = x
            self.img_buff.x_step = i
            self.img_buff.y_repeats = y
            self.img_buff.y_step = j


    def _parse_justify(self, val):
        """ Make a tuple for each axis (special case). """
        if len(val) > 1 or val not in 'LC':
            ab_tup = ('L', float(val.split('L')[-1]))
        else:
            ab_tup = (val, None)
        return ab_tup


    # tokenizer support - funct/coord

    def _parse_data_block(self, tok):
        """ Convert a non-param into pythonic data. """
        if 'G' in tok:
            g_code = tok[1:3]
            tok = tok[3:]
            if int(g_code) in G_MAP:
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


    def _check_fill(self):
        """ Check that a fill is closed. """
        fill = self.fill_buff
        if len(fill) >= 2:
            segs = (fill[0], fill[1], fill[-2], fill[-1])
            ends = [isinstance(s, Arc) and list(s.ends()) or [s.p1, s.p2]
                    for s in segs]
            if len(fill) > 2:

                # If first or last seg is an arc that was defined
                # in anticlockwise mode, we need to reverse it.
                if ends[0][0] in ends[1]:
                    ends[0].reverse()
                if ends[-1][1] in ends[-2]:
                    ends[-1].reverse()

                if not ends[-1][1] == ends[0][0]:
                    raise OpenFillBoundary('%s != %s' %
                                           (ends[-1][1], ends[0][0]))
            else:
                for end in ends[-1]:
                    if end not in end[0]:
                        raise OpenFillBoundary('%s != %s' %
                                               (ends[-1][1], ends[0][0]))
        else:
            start, end = fill[0].ends()
            if not start == end:
                raise OpenFillBoundary('%s != %s' % (start, end))
        self.fill_buff = []
        return fill


    def _check_smear(self, seg, shape):
        """ Enforce linear interpolation constraint. """
        if not isinstance(seg, Line):
            raise IncompatibleAperture('%s cannot draw arc %s'
                                       % (shape, seg))


    def _check_mq(self, start_angle, end_angle):
        """ Enforce single quadrant arc length restriction. """
        if not self.status['multi_quadrant']:
            if abs(end_angle - start_angle) > 0.5:
                raise QuadrantViolation('Arc(%s to %s) > 0.5 rad/pi'
                                        % (start_angle, end_angle))


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
