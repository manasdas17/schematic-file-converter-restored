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
from upconvert.core.shape import Circle, Label, Line, Point, Rectangle, RoundedRectangle

log = logging.getLogger('core.layout')


class Layout:
    """ Represents the design schematic as a PCB Layout. """

    def __init__(self):
        self.layers = list()


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
        self.complex_instances = list()

    def not_empty(self):
        """ True if image contains only metadata. """
        return (self.fills or self.smears or self.shape_instances or self.complex_instances) and True or False


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
            self.smears.append(Smear(shapecpy, Circle(0, 0, 0.15 * 1000000)))

        elif isinstance(shapecpy, Circle):
            self.shape_instances.append(ShapeInstance(Point(shapecpy.x, shapecpy.y), Aperture(None, shapecpy, None)))

        elif isinstance(shapecpy, Rectangle):
            # XXX(shamer): rectangles in gerbers are positioned around their centers
            shapecpy.x += shapecpy.width / 2
            shapecpy.y -= shapecpy.height / 2
            shapecpy.width = abs(shapecpy.width)
            shapecpy.height = abs(shapecpy.height)
            self.shape_instances.append(ShapeInstance(Point(shapecpy.x, shapecpy.y), Aperture(None, shapecpy, None)))

        elif isinstance(shapecpy, RoundedRectangle):
            # Rounded rectangle is added as a macro with two rectangles to fill out the body and four circles to make up
            # the corners. `roundrect` is assumed to already be centered.
            primitives = []
            radius = abs(shapecpy.radius)
            inner_height = abs(shapecpy.height) - (radius * 2)
            inner_width = abs(shapecpy.width) - (radius * 2)
            half_width = inner_width / 2.0
            half_height = inner_height / 2.0

            primitives.append(Primitive(1, 0.0, Rectangle(0, 0, abs(inner_width), abs(shapecpy.height))))
            primitives.append(Primitive(1, 0.0, Rectangle(0, 0, abs(shapecpy.width), abs(inner_height))))
            primitives.append(Primitive(1, 0.0, Circle(-half_width, half_height, shapecpy.radius)))
            primitives.append(Primitive(1, 0.0, Circle(half_width, half_height, shapecpy.radius)))
            primitives.append(Primitive(1, 0.0, Circle(half_width, -half_height, shapecpy.radius)))
            primitives.append(Primitive(1, 0.0, Circle(-half_width, -half_height, shapecpy.radius)))

            self.complex_instances.append(ComplexInstance(Point(shapecpy.x + (shapecpy.width / 2), shapecpy.y - (shapecpy.height / 2)), primitives))

        elif isinstance(shapecpy, Label):
            # TODO(shamer): add as arcs
            pass



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


class Smear:
    """ A line drawn by a rectangular aperture. """

    def __init__(self, line, shape):
        self.line = line
        self.shape = shape


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


class ComplexInstance:
    """
    A complex instance of a collection of primitive shapes.

    """

    def __init__(self, point, primitives):
        self.x = point.x
        self.y = point.y
        self.primitives = primitives


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

        #XXX(shamer): aperture doesn't include the offset/placement of the shape
        shapecpy = copy.deepcopy(shape)
        shapecpy.x = 0
        shapecpy.y = 0

        self.shape = shapecpy
        self.hole = hole


    def __eq__(self, other):
        """ Compare 2 apertures. """
        if not isinstance(other, Aperture):
            return False

        same_shape = self.shape.__dict__ == other.shape.__dict__
        same_hole = (self.hole == other.hole or
                     (self.hole and other.hole and
                      self.hole.__dict__ == other.hole.__dict__))
        return same_shape and same_hole


    def __repr__(self):
        return '<Aperture(code={0}, shape={1}, hole={2})>'.format(self.code, self.shape, self.hole)


class Macro:
    """
    Complex shape built from multiple primitives.

    Primitive shapes are added together in the order they
    appear in the list. Subtractive shapes subtract only
    from prior shapes, not subsequent shapes.

    """
    # TODO(shamer): How can parameters get stored?
    def __init__(self, name, primitives):
        self.name = name
        self.primitives = primitives

    def __eq__(self, other):
        return self.primitives == other.primitives



class MacroAperture:
    """ An aperture utilizing a macro with specific parameters. """

    def __init__(self, code, name, params=None):
        self.code = code
        self.name = name
        self.params = params


    def __eq__(self, other):
        if not isinstance(other, MacroAperture):
            return False

        return (self.name == other.name and self.params == other.params)


class Primitive:
    """ A shape with rotation and exposure modifiers. """

    def __init__(self, is_additive, rotation, shape):
        self.is_additive = is_additive
        self.rotation = rotation
        self.shape = shape

    def __eq__(self, other):
        return (self.is_additive == other.is_additive and
                self.rotation == other.rotation and
                self.shape == other.shape)
