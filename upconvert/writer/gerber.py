#!/usr/bin/env python2
""" The Gerber RS274-X Format Writer """

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


from sys import stdout
from os import path, mkdir, listdir, makedirs, stat
from shutil import rmtree
from collections import namedtuple
from tarfile import TarFile
from zipfile import ZipFile

from upconvert.core.shape import Circle, Rectangle, Obround, RegularPolygon
from upconvert.core.shape import Polygon, Moire, Thermal
from upconvert.core.shape import Point, Arc
from upconvert.core.layout import Aperture


# exceptions

class Unwritable(ValueError):
    """ Parent class for all gerber writer errors. """
    pass

class MissingLayout(Unwritable):
    """ Design has no layout information. """
    pass

class NoLayersFound(Unwritable):
    """ Layout doesn't have any layers. """
    pass

class UnitsNotSpecified(Unwritable):
    """ Layout doesn't specify units. """
    pass

class ImageContainsNoData(Unwritable):
    """ One of the layers contains an empty image. """
    pass

class NotBatch(ValueError):
    """ The intended output is a single file. """
    pass


# constants

LINE = '{0}\r\n'
FORMAT_SPEC = '%FSLAX{int}{dec}Y{int}{dec}*%'
MACRO = LINE.format('%AM{name}*') + '{primitives}%'
PRIMITIVE = '{mods}*'
APERTURE = '%ADD{code}{type}{mods}*%'
AP_MODS = ',{mods}'
PARAM = '%{name}{val}*%'
SR_MODS = 'X{x}Y{y}I{i}J{j}'
FUNCT = '{type}{code}*'
COORD = 'X{x}Y{y}*'
COORD_EXT = 'X{x}Y{y}I{i}J{j}*'
STEALTH = 'X{x}Y{y}D02*'
FLASH = 'X{x}Y{y}D03*'
MM_UNITS = '%MOMM*%'
EOF = 'M02*'
INTERPOLATION = {'LINEAR': '01',
                 'CLOCKWISE_CIRCULAR': '02',
                 'ANTICLOCKWISE_CIRCULAR': '03'}
SHAPE_TAGS = {'circle': {'int': 1, 'char': 'C'},
              'rectangle': {'int': 22, 'char': 'R'},
              'obround': {'char': 'O'},
              'reg_polygon': {'int': 5, 'char': 'P'},
              'polygon': {'int': 4},
              'moire': {'int': 6},
              'thermal': {'int': 7}}
LAYERS_CFG = 'layers.cfg'
TAR_MODES = {'.tar': 'w',
             '.gz': 'w:gz',
             '.tgz': 'w:gz',
             '.bz2': 'w:bz2'}


# archive class

Batch = namedtuple('Batch', 'archive add_ rootdir')             # pylint: disable=C0103


# writer

class Gerber:
    """ The Gerber Format Writer. """

    def __init__(self):
        self.coord_format = None
        self.images = None
        self.apertures = list()
        self.status = {'x':0,
                       'y':0,
                       'interpolation':None,
                       'aperture':None,
                       'outline_fill':False,
                       'multi_quadrant':False,
                       'units':None,
                       'incremental_coords':None}


    def write(self, design, outfile=None):
        """ Main logic for producing a set of output files. """
        self._check_design(design)
        units = design.layout.units #TODO: handle inline units
        if outfile:
            dir_ = path.dirname(outfile)
            if dir_:
                try:
                    stat(dir_)
                except OSError:
                    makedirs(dir_)
        batch = self._get_archive(outfile)
        try:
            cfg_name = self._config_batch(batch, outfile)
            cfg = open(cfg_name, 'w')
        except NotBatch:
            #TODO: check that there's actually only one layer
            with outfile and open(outfile, 'w') or stdout as f:
                self._gerberize(design.layout.layers[0], units, f)
        else:
            for layer in design.layout.layers:
                member_name = layer.name.lower().replace(' ', '_') + '.ger'
                with open(batch.rootdir and
                          path.join(batch.rootdir, member_name) or
                          path.join(dir_, member_name), 'w') as member:
                    self._gerberize(layer, units, member)
                cfg.write(LINE.format(', '.join([layer.name,
                                                 layer.type,
                                                 member_name])))
        finally:
            if batch:
                cfg.close()
                if batch.archive:
                    batch.add_(batch.rootdir)
                    for member_name in listdir(batch.rootdir):
                        batch.add_(path.join(batch.rootdir, member_name))
                    batch.archive.close()
                    rmtree(batch.rootdir)


    # primary writer support methods

    def _get_archive(self, outfile):
        """ Establish zip or tarfile for batch output. """
        batch = None
        if outfile:
            filename = path.basename(outfile)
            rootdir, ext = path.splitext(filename)
            if ext in TAR_MODES.keys() + ['.zip']:
                if ext == '.zip':
                    archive = ZipFile(outfile, 'w')
                    add_ = archive.write
                else:
                    archive = TarFile.open(outfile, TAR_MODES[ext])
                    add_ = archive.add
                rootdir = filename.split('.')[0]
                batch = Batch(archive, add_, rootdir)
            elif LAYERS_CFG in filename:
                batch = Batch(False, False, False)
        return batch


    def _config_batch(self, batch, outfile):
        """ Establish config file for batch output. """
        if not batch:
            raise NotBatch
        else:
            if batch.rootdir:
                mkdir(batch.rootdir)
                cfg_name = path.join(batch.rootdir, LAYERS_CFG)
            else:
                cfg_name = outfile
        return cfg_name


    def _gerberize(self, layer, units, f):
        """ Logic for producing a single gerber file. """
        self.images = layer.images
        self._define_apertures()

        # write params
        f.write(LINE.format(self._get_format_spec(units)))
        if units != 'inch':
            f.write(LINE.format(MM_UNITS))
        for k in layer.macros:
            f.write(self._get_macro_def(layer.macros[k]))
        for aperture in self.apertures:
            f.write(self._get_ap_def(aperture))

        # select an arbitrary aperture for trace[0] check
        if self.apertures:
            self.status['aperture'] = self.apertures[0]
            f.write(LINE.format(FUNCT.format(type='D',
                                             code=self.apertures[0].code)))

        # build image layers - main data section
        for i in range(len(layer.images)):
            for param in self._get_image_meta(i):
                f.write(param)
            for block in self._gen_paths(layer.images[i]):
                f.write(block)

        # tidy up
        f.write(EOF)


    def _define_apertures(self):
        """ Build the apertures needed to make shapes. """
        for image in self.images:
            for trace in image.traces:
                shape = Circle(0 , 0, trace.width / 2.0)
                self._add_aperture(shape, None)
            for smear in image.smears:
                self._add_aperture(smear.shape, None)
            for shape_instance in image.shape_instances:
                self._add_aperture(shape_instance.shape,
                                   shape_instance.hole)


    def _get_format_spec(self, units, max_size=False, max_precision=False):
        """ Generate FS parameter with sensible precision. """
        if units == 'inch':
            int_, dec_ = (2, 4)
        else:
            int_, dec_ = (3, 3)
        if max_size:
            int_ = 6
        if max_precision:
            dec_ = 6
        self.coord_format = {'int': int_, 'dec': dec_}
        return FORMAT_SPEC.format(int=int_, dec=dec_)


    def _get_macro_def(self, macro):
        """ Convert macro based on core shapes to gerber. """
        prims_def = ''
        for primitive in macro.primitives:
            shape = primitive.shape
            exposure = primitive.is_additive
            rotation = (isinstance(shape, (Moire, Thermal)) and
                        shape.rotation or
                        primitive.rotation)
            rotation = rotation and (2 - rotation) * 180 or 0
            if isinstance(shape, Circle):
                mods = [SHAPE_TAGS['circle']['int'],
                        exposure,
                        shape.radius * 2,
                        shape.x,
                        shape.y]
            elif isinstance(shape, Rectangle):
                mods = [SHAPE_TAGS['rectangle']['int'],
                        exposure,
                        shape.width,
                        shape.height,
                        shape.x,
                        shape.y - shape.height,
                        rotation]
            elif isinstance(shape, Polygon):
                vertices = [(p.x, p.y) for p in shape.points]
                v_args = [vertices[i / 2][i % 2]
                          for i in range(len(vertices) * 2)]
                mods = [SHAPE_TAGS['polygon']['int'],
                        exposure] + v_args + [rotation]
            elif isinstance(shape, RegularPolygon):
                mods = [SHAPE_TAGS['reg_polygon']['int'],
                        exposure,
                        shape.vertices,
                        shape.x,
                        shape.y,
                        shape.outer_diameter,
                        rotation]
            elif isinstance(shape, Moire):
                mods = [SHAPE_TAGS['moire']['int'],
                        shape.x,
                        shape.y,
                        shape.outer_diameter,
                        shape.ring_thickness,
                        shape.gap_thickness,
                        shape.max_rings,
                        shape.hair_thickness,
                        shape.hair_length,
                        rotation]
            elif isinstance(shape, Thermal):
                mods = [SHAPE_TAGS['thermal']['int'],
                        shape.x,
                        shape.y,
                        shape.outer_diameter,
                        shape.inner_diameter,
                        shape.gap_thickness,
                        rotation]
            mods = ','.join(str(m) for m in mods)
            prim_def = PRIMITIVE.format(mods=mods)
            prims_def += LINE.format(prim_def)
        macro_def = MACRO.format(name=macro.name,
                                 primitives=prims_def.strip())
        return LINE.format(macro_def)


    def _get_ap_def(self, aperture):
        """ Convert aperture based on core shapes to gerber. """

        # get type and shape mods
        shape = aperture.shape
        if isinstance(shape, Circle):
            type_ = SHAPE_TAGS['circle']['char']
            mods = [shape.radius * 2]
        elif isinstance(shape, Rectangle):
            type_ = SHAPE_TAGS['rectangle']['char']
            mods = [shape.width,
                    shape.height]
        elif isinstance(shape, Obround):
            type_ = SHAPE_TAGS['obround']['char']
            mods = [shape.width,
                    shape.height]
        elif isinstance(shape, RegularPolygon):
            rot = shape.rotation
            rotation = rot and (2 - rot) * 180 or 0
            type_ = SHAPE_TAGS['reg_polygon']['char']
            mods = [shape.outer_diameter,
                    shape.vertices,
                    rotation]
        elif isinstance(shape, str):
            type_ = shape
            mods = []

        # add hole mods
        hole = aperture.hole
        if isinstance(hole, Circle):
            hole_mods = [hole.radius]
        elif hole:
            hole_mods = [hole.width, hole.height]
        else:
            hole_mods = []
        mods += hole_mods

        # generate param
        mods = 'X'.join(str(m) for m in mods)
        mods_def = (mods and AP_MODS.format(mods=mods) or '')
        ap_def = APERTURE.format(code=aperture.code,
                                 type=type_,
                                 mods=mods_def)
        return LINE.format(ap_def)


    def _get_image_meta(self, i):
        """ Generate layer params for the image layer. """
        image = self.images[i]
        prev_additive = i > 0 and self.images[i - 1].is_additive or True
        if image.name:
            meta = PARAM.format(name='LN',
                                val=image.name)
            yield LINE.format(meta)

        # Image.is_additive can only be set explicitly,
        # so we check the previous image layer.
        if image.is_additive:
            if not prev_additive:
                meta = PARAM.format(name='LP',
                                    val='D')
                yield LINE.format(meta)
        else:
            if prev_additive:
                meta = PARAM.format(name='LP',
                                    val='C')
                yield LINE.format(meta)

        # handle repetition of image layer
        if image.x_repeats > 1 or image.y_repeats > 1:
            val = SR_MODS.format(x=image.x_repeats,
                                 y=image.y_repeats,
                                 i=image.x_step,
                                 j=image.y_step)
            meta = PARAM.format(name='SR',
                                val=val)
            yield LINE.format(meta)


    def _gen_paths(self, image):
        """ Generate functions and coordinates. """
        for trace in image.traces:
            for block in self._gen_trace(trace):
                yield block
        for smear in image.smears:
            for block in self._gen_smear(smear):
                yield block
        for shin in image.shape_instances:
            for block in self._gen_shape_instance(shin):
                yield block
        if image.fills:
            for block in self._gen_fills(image.fills):
                yield block


    # secondary writer support methods

    def _add_aperture(self, shape, hole):
        """ Generate D code and store aperture. """
        next_ap = len(self.apertures) + 10
        aperture = Aperture(next_ap, shape, hole)
        if aperture not in self.apertures:
            self.apertures.append(aperture)


    def _gen_trace(self, trace):
        """ Traces are connected lines and arcs. """
        shape = Circle(0 , 0, trace.width / 2.0)
        select = self._select_aperture(shape, None)
        if select:
            yield LINE.format(select)
        for seg in trace.segments:
            for block in self._draw_seg(seg):
                yield LINE.format(block)


    def _gen_smear(self, smear):
        """ Smears are lines drawn with rect apertures. """
        select = self._select_aperture(smear.shape, None)
        if select:
            yield LINE.format(select)
        for block in self._draw_seg(smear.line):
            yield LINE.format(block)


    def _gen_shape_instance(self, shin):
        """ A snapshot of an aperture or macro. """
        select = self._select_aperture(shin.shape,
                                       shin.hole)
        if select:
            yield LINE.format(select)
        block = self._flash(shin.x, shin.y)
        yield LINE.format(block)


    def _gen_fills(self, fills):
        """ Fills are defined by their line/arc outlines. """
        fill_mode_on = FUNCT.format(type='G', code='36')
        yield LINE.format(fill_mode_on)
        for fill in fills:
            for seg in fill.segments:
                for block in self._draw_seg(seg):
                    yield LINE.format(block)
        fill_mode_off = FUNCT.format(type='G', code='37')
        yield LINE.format(fill_mode_off)


    def _select_aperture(self, shape, hole):
        """ Change the current aperture if necessary. """
        selection = Aperture(None, shape, hole)
        if selection == self.status['aperture']:
            return None
        else:
            index = self.apertures.index(selection)
            self.status['aperture'] = self.apertures[index]
            return FUNCT.format(type='D',
                                code=self.status['aperture'].code)


    def _draw_seg(self, seg):
        """ Define path for a line or arc. """
        init_draw = not self.status['interpolation']
        mq_mode = None
        if isinstance(seg, Arc):
            interpolate = self._interpolate('CLOCKWISE_CIRCULAR')
            start, end = seg.ends()

            # handle clockwise representation of anticlock arcs
            if Point(self.status['x'], self.status['y']) == end:
                interpolate = self._interpolate('ANTICLOCKWISE_CIRCULAR')
                end, start = seg.ends()

            i, j = (seg.x - start.x, seg.y - start.y)

            # further establish interpolation mode
            mq_mode = self._check_mq(seg)
            if not self.status['multi_quadrant']:
                i, j = (abs(i), abs(j))

            move = COORD_EXT.format(x=self._fix(end.x),
                                    y=self._fix(end.y),
                                    i=self._fix(i),
                                    j=self._fix(j))
        else:
            interpolate = self._interpolate('LINEAR')
            start, end = (seg.p1, seg.p2)
            move = COORD.format(x=self._fix(end.x),
                                y=self._fix(end.y))

        # move to the start point of a draw
        stealth_move = self._move_start(start)

        # reset draw mode after stealth move
        if stealth_move or init_draw:
            move = move.replace('*', 'D01*')

        # compile directives for drawing segment
        self.status['x'] = end.x
        self.status['y'] = end.y
        blocks = (mq_mode, interpolate, stealth_move, move)
        return (b for b in blocks if b)


    def _move_start(self, point):
        """ Move the 'photo plotter head' without 'drawing'. """
        loc = Point(self.status['x'], self.status['y'])
        return ((not loc == point) and
                STEALTH.format(x=self._fix(point.x),
                               y=self._fix(point.y)))


    def _flash(self, x, y):
        """ Create a shape instance. """
        return FLASH.format(x=self._fix(x),
                            y=self._fix(y))


    def _interpolate(self, code):
        """ Change the interpolation setting if necessary. """
        if self.status['interpolation'] == code:
            return None
        else:
            self.status['interpolation'] = code
            return FUNCT.format(type='G', code=INTERPOLATION[code])
            

    # general methods

    def _fix(self, ord_):
        """ Convert a float ordinate according to spec. """
        dec = self.coord_format['dec']
        spec = '{{0}}{{1:0<{0}}}'.format(dec)
        padded_ord = spec.format(*str(round(ord_, dec)).split('.'))
        return int(padded_ord) and padded_ord or '0'


    def _check_mq(self, seg):
        """ Set multi_quadrant mode on/off if necessary. """

        # handle arcs that traverse the 3 o'clock boundary
        if seg.end_angle <= seg.start_angle:
            seg.end_angle += 2

        mq_seg = seg.end_angle - seg.start_angle > 0.5
        code = None
        if mq_seg and not self.status['multi_quadrant']:
            self.status['multi_quadrant'] = True
            code = '75'
        elif self.status['multi_quadrant'] and not mq_seg:
            self.status['multi_quadrant'] = False
            code = '74'
        return code and FUNCT.format(type='G', code=code)


    def _check_design(self, design):
        """ Ensure the design contains required information. """

        #TODO: check fills for closure and self-intersection
        if not design.layout:
            raise MissingLayout
        if not design.layout.layers:
            raise NoLayersFound
        if not design.layout.units:
            raise UnitsNotSpecified
        for layer in design.layout.layers:
            for image in layer.images:
                if not (image.traces or
                        image.fills or
                        image.smears or
                        image.shape_instances):
                    raise ImageContainsNoData(image.name)
