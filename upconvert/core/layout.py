#!/usr/bin/env python2
""" The layout class """

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

import copy
import logging
from upconvert.core.shape import Circle, Label, Line, Point, Rectangle

log = logging.getLogger('core.layout')


class Layout:
    """ Represents the design schematic as a PCB Layout. """

    def __init__(self):
        self.layers = list()

    def json(self):
        """ Return the layout as JSON """
        return {
            "layers": [layer.json() for layer in self.layers]
            }


class Layer:
    """ A layer in the layout (ie, a PCB layer). """

    def __init__(self, name='', type_=''):
        self.name = name
        self.type = type_ # copper/mask/silk/drill
        self.images = list()
        self.apertures = dict()
        self.macros = dict()
        self.vias = list()
        self.components = list()


    def json(self):
        """ Return the layer as JSON """
        return {
            "type": self.type,
            "images": [i.json() for i in self.images],
            "apertures": [self.apertures[k].json() for k in self.apertures],
            "macros": [self.macros[m].json() for m in self.macros],
            "vias": [v.json() for v in self.vias],
            "components": [c.json() for c in self.components]
            }


class Image:
    """
    An image layer (not a PCB layer).

    Image layers can be additive or subtractive. Therefore they
    must be applied successively to build up a final image
    representing a single layer of the PCB (ie, a single gerber
    file).

    Image layers will be applied in the order they appear in the
    layer[n].images list of the Layout. Subtractive image layers
    only subtract from previous image layers - not subsequent
    image layers.

    Example
    =======
    For a ground plane that is partly negated to make room for
    traces, define three image layers in the following order:

        1. the ground plane
        2. the area(s) to be negated (as a subtractive image)
        3. the traces to be laid within the negated area(s)
    """

    def __init__(self, name='Untitled Image', is_additive=True):
        self.name = name
        self.is_additive = is_additive
        self.x_repeats = 1
        self.x_step = None
        self.y_repeats = 1
        self.y_step = None
        self.fills = list()
        self.smears = list()
        self.shape_instances = list()


    def not_empty(self):
        """ True if image contains only metadata. """
        return (self.fills or self.smears or self.shape_instances) and True or False


    def add_shape(self, shape, offset, rotation, flip):
        """ Add a shape to the image. (might be added as a smear or fill) """
        # Copy the shape so it can be mutated without affecting other instances
        shapecpy = copy.deepcopy(shape)

        effective_rotation = (rotation + offset.rotation) % 2.0
        if effective_rotation != 0:
            log.debug('rotating %s pi radians', effective_rotation)
            shapecpy.rotate(effective_rotation)
        effective_flip = flip ^ offset.flip
        if effective_flip:
            log.debug('flipping shape %s', flip)
            shapecpy.flip(effective_flip)

        shapecpy.shift(offset.x, offset.y)
        if isinstance(shapecpy, Line):
            # FIXME(shamer): line  doesn't have an explicit width. Gets used for outlines. Defaulted to 0.25mm
            self.smears.append(Smear(shapecpy, Circle(0, 0, 0.25 * 1000000)))

        elif isinstance(shapecpy, Circle):
            self.shape_instances.append(ShapeInstance(Point(shapecpy.x, shapecpy.y), Aperture(None, shapecpy, None)))

        elif isinstance(shapecpy, Rectangle):
            # XXX(shamer): rectangles in gerbers are positioned around their centers
            shapecpy.x += shapecpy.width / 2
            shapecpy.y -= shapecpy.height / 2
            shapecpy.width = abs(shapecpy.width)
            shapecpy.height = abs(shapecpy.height)
            self.shape_instances.append(ShapeInstance(Point(shapecpy.x, shapecpy.y), Aperture(None, shapecpy, None)))

        elif isinstance(shapecpy, Label):
            # TODO(shamer): add as arcs
            pass



    def json(self):
        """ Return the image as JSON """
        return {
            "name": self.name,
            "is_additive": self.is_additive and 'true' or 'false',
            "x_repeats": self.x_repeats,
            "x_step": self.x_step,
            "y_repeats": self.y_repeats,
            "y_step": self.y_step,
            "fills": [f.json() for f in self.fills],
            "smears": [s.json() for s in self.smears],
            "shape_instances": [i.json() for i in self.shape_instances]
            }


class Segment:
    """ A single segment of a trace. """

    def __init__(self, layer, p1, p2, width):
        self.layer = layer
        self.p1 = p1
        self.p2 = p2
        self.width = width

    def __repr__(self):
        return '''<Segment(layer='{0}', p1={1}, p2={2}, width{3})>'''.format(self.layer, self.p1, self.p2, self.width)


class Fill:
    """
    A closed loop of connected segments (lines/arcs).

    The segments define the outline of the fill. They
    must be contiguous, listed in order (ie, each seg
    connects with the previous seg and the next seg)
    and not intersect each other.
    """

    def __init__(self, segments=None):
        self.segments = segments or list()


    def json(self):
        """ Return the trace as JSON """
        return {
            "segments": [s.json() for s in self.segments]
            }


class Smear:
    """ A line drawn by a rectangular aperture. """

    def __init__(self, line, shape):
        self.line = line
        self.shape = shape


    def json(self):
        """ Return the smear as JSON """
        return {
            "line": self.line.json(),
            "shape": self.shape.json()
            }


class ShapeInstance:
    """
    An instance of a shape defined by an aperture.

    Instead of wrapping the aperture itself, we wrap
    its constituent shape and hole defs, because
    gerber does not prohibit an aperture from being
    redefined at some arbitrary point in the file.

    x and y attributes serve as an offset.
    """

    def __init__(self, point, aperture):
        self.x = point.x
        self.y = point.y
        self.shape = aperture.shape
        self.hole = aperture.hole


    def json(self):
        """ Return the shape instance as JSON """
        return {
            "x": self.x,
            "y": self.y,
            "shape": (isinstance(self.shape, str) and
                      self.shape or self.shape.json()),
            "hole": self.hole and self.hole.json()
            }


class Aperture:
    """
    A simple shape, with or without a hole.

    If the shape is not defined by a macro, its class
    must be one of Circle, Rectangle, Obround or
    RegularPolygon.

    If the shape is not defined by a macro, it may have
    a hole. The class of the hole must be either Circle
    or Rectangle. Shape and hole are both centered on
    the origin. Placement is handled by metadata
    connected to the aperture when it used.

    Holes must be fully contained within the shape.

    Holes never rotate, even if the shape is rotatable
    (ie, a RegularPolygon).
    """

    def __init__(self, code, shape, hole):
        self.code = code
        self.shape = shape
        self.hole = hole


    def __eq__(self, other):
        """ Compare 2 apertures. """
        if (isinstance(self.shape, str) or
            isinstance(other.shape, str)):
            equal = self.shape == other.shape
        else:
            equal = (self.shape.__dict__ == other.shape.__dict__ and
                     (self.hole == other.hole or
                      (self.hole and other.hole and
                       self.hole.__dict__ == other.hole.__dict__)))
        return equal


    def json(self):
        """ Return the aperture as JSON """
        return {
            "code": self.code,
            "shape": (isinstance(self.shape, str) and
                      self.shape or self.shape.json()),
            "hole": self.hole and self.hole.json()
            }


class Macro:
    """
    Complex shape built from multiple primitives.

    Primitive shapes are added together in the order they
    appear in the list. Subtractive shapes subtract only
    from prior shapes, not subsequent shapes.

    """
    def __init__(self, name, primitives):
        self.name = name
        self.primitives = primitives


    def json(self):
        """ Return the macro as JSON """
        return {
            "name": self.name,
            "primitives": [prim.json() for prim in self.primitives]
            }


class Primitive:
    """ A shape with rotation and exposure modifiers. """

    def __init__(self, is_additive, rotation, shape):
        self.is_additive = is_additive
        self.rotation = rotation
        self.shape = shape


    def json(self):
        """ Return the primitive as JSON """
        return {
            "is_additive": self.is_additive and 'true' or 'false',
            "rotation": self.rotation,
            "shape": self.shape.json()
            }
