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
import freetype
import logging
import re

from upconvert.core.shape import Circle, Label, Line, Point, Rectangle, RoundedRectangle

log = logging.getLogger('core.layout')


class Layout:
    """ Represents the design schematic as a PCB Layout. """

    def __init__(self):
        self.layers = list()


class Layer:
    """ A layer in the gerber (not a layer in the design). """

    def __init__(self, name='', polarity='dark'):
        self.name = name
        self.polarity = polarity
        self.images = list()
        self.apertures = dict()
        self.macros = dict()


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
    attr_re = re.compile(r'{{[^}]*}}')


    def __init__(self, name='Untitled Image', is_additive=True, font_renderer=None):
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
        self.face = font_renderer

    def not_empty(self):
        """ True if image contains only metadata. """
        return (self.fills or self.smears or self.shape_instances or self.complex_instances) and True or False


    def resolve_text(self, text, attr_source):
        ''' Resolve attribute placeholders in a piece of text using an attr_source method. '''
        for attr in self.attr_re.findall(text):
            text = text.replace(attr, attr_source(attr[2:-2]), 1)
        return text


    def add_shape(self, shape, parent, parent_offset, offset):
        """ Add a shape to the image. (might be added as a smear or fill) """
        # Copy the shape so it can be mutated without affecting other instances
        shapecpy = copy.deepcopy(shape)

        # XXX(shamer): a label needs to be rendered before in-place rotations are made so the bounding box for the shape
        # are known
        if isinstance(shapecpy, Label):
            self.face.set_char_size(int(shapecpy.font_size))

            label_contours = []

            x_offset = 0
            y_offset = 0
            label_text = self.resolve_text(shapecpy.text, parent.get_attribute)
            for i, c in enumerate(label_text):
                self.face.load_char(c, flags=freetype.ft_enums.FT_LOAD_NO_BITMAP)
                slot = self.face.glyph
                outline = slot.outline

                glyph_contours = []

                start, end = 0, 0
                # Iterate over each contour separately. Characters like 'g' have multiple contours as they cannot be
                # walked with a contiguous set of arcs. The contours list contains the index of the point that the
                # contour starts on.
                for contour_idx in range(len(outline.contours)):
                    end = outline.contours[contour_idx]
                    points = [Point(t[0], t[1]) for t in outline.points[start:end+1]]
                    tags = outline.tags[start:end+1]
                    # Close the contour by repeating the last point.
                    points.append(copy.deepcopy(points[0]))
                    tags.append(copy.deepcopy(tags[0]))

                    segments = [[points[0], ], ]
                    # Group points into segments. The tag identifies real vs control points.
                    for point_idx in range(1, len(points) ):
                        segments[-1].append(points[point_idx])
                        if tags[point_idx] & (1 << 0) and point_idx < (len(points)-1):
                            segments.append([copy.deepcopy(points[point_idx]),])

                    # take the fist and last points of each segment (the non-control points). To approximate the curves
                    # using straight lines.
                    glyph_contours.append([[segment[0], segment[-1]] for segment in segments])

                    start = end+1

                # update the segments in the glyph with the x_offset
                for contour_segments in glyph_contours:
                    for segments in contour_segments:
                        for point in segments:
                            point.x += x_offset
                            point.y += y_offset
                label_contours.extend(glyph_contours)

                x_offset += slot.advance.x
                # adjust amount to advance with kerning offset
                if i + 1 < len(label_text):
                    next_c = label_text[i + 1]
                    x_offset += self.face.get_kerning(c, next_c).x

            # Update the segments for pre-render shifts, rotates, alignment
            for contour_segments in label_contours:
                for segments in contour_segments:
                    if shapecpy.align == 'center':
                        segments[0].shift(-(x_offset / 2), 0)
                        segments[1].shift(-(x_offset / 2), 0)

                    if shapecpy.rotation:
                        segments[0].rotate(shapecpy.rotation)
                        segments[1].rotate(shapecpy.rotation)

                    if shapecpy.flip_horizontal:
                        segments[0].flip(shapecpy.flip_horizontal)
                        segments[1].flip(shapecpy.flip_horizontal)

                    shapecpy._segments.append(segments)

            # Calculate the bounding fox the label from the segments
            min_point = [2**100, 2**100]
            max_point = [-2**100, -2**100]
            for contour_segments in label_contours:
                for segments in contour_segments:
                    min_point[0] = min(segments[0].x, segments[1].x, min_point[0])
                    max_point[0] = max(segments[0].x, segments[1].x, max_point[0])
                    min_point[1] = min(segments[0].y, segments[1].y, min_point[1])
                    max_point[1] = max(segments[0].y, segments[1].y, max_point[1])
            shapecpy._min_point = Point(min_point[0], min_point[1])
            shapecpy._max_point = Point(max_point[0], max_point[1])


        shapecpy.shift(offset.x, offset.y)
        if parent_offset.rotation != 0:
            shapecpy.rotate(parent_offset.rotation)
        if parent_offset.flip_horizontal:
            shapecpy.flip(parent_offset.flip_horizontal)
        shapecpy.shift(parent_offset.x, parent_offset.y)

        if offset.rotation != 0:
            if parent_offset.flip_horizontal:
                shapecpy.rotate(-offset.rotation, in_place=True)
            else:
                shapecpy.rotate(offset.rotation, in_place=True)
        if offset.flip_horizontal:
            shapecpy.flip(offset.flip_horizontal)

        if isinstance(shapecpy, Line):
            # FIXME(shamer): line  doesn't have an explicit width. Gets used for outlines. Defaulted to 0.15mm
            self.smears.append(Smear(shapecpy, Circle(0, 0, 0.15 * 1000000)))

        elif isinstance(shapecpy, Circle):
            self.shape_instances.append(ShapeInstance(Point(shapecpy.x, shapecpy.y), Aperture(None, shapecpy, None)))

        elif isinstance(shapecpy, Rectangle):
            #shapecpy.x += shapecpy.width
            #shapecpy.y -= shapecpy.height / 2
            shapecpy.width = abs(shapecpy.width)
            shapecpy.height = abs(shapecpy.height)
            if shapecpy.rotation != 0:
                instance_name = 'Rect-W{width}-H{height}-RO{rotation}'.format(height=shapecpy.height,
                                                                              width=shapecpy.width,
                                                                              rotation=shapecpy.rotation)
                # XXX(shamer): additional copy is made so the x, y can be reset for use as a ComplexInstance
                shapecpycpy = copy.deepcopy(shapecpy)
                shapecpycpy.x = 0
                shapecpycpy.y = 0
                shapecpycpy.is_centered = True
                primitives = [Primitive(1, 0.0, shapecpycpy)]
                self.complex_instances.append(ComplexInstance(instance_name, Point(shapecpy.x, shapecpy.y), primitives))
            else:
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

            high_rect = Rectangle(0, 0, abs(inner_width), abs(shapecpy.height), is_centered=True)
            wide_rect = Rectangle(0, 0, abs(shapecpy.width), abs(inner_height), is_centered=True)
            primitives.append(Primitive(1, 0.0, high_rect))
            primitives.append(Primitive(1, 0.0, wide_rect))
            primitives.append(Primitive(1, 0.0, Circle(-half_width, half_height, shapecpy.radius)))
            primitives.append(Primitive(1, 0.0, Circle(half_width, half_height, shapecpy.radius)))
            primitives.append(Primitive(1, 0.0, Circle(half_width, -half_height, shapecpy.radius)))
            primitives.append(Primitive(1, 0.0, Circle(-half_width, -half_height, shapecpy.radius)))

            # rotate the positioning of the rounded corners (the circles)
            for primitive in primitives:
                primitive.shape.rotate(shapecpy.rotation)

            instance_name = 'RR-H{height}-W{width}-R{radius}-RO{rotation}'.format(height=abs(shapecpy.height),
                                                                                  width=abs(shapecpy.width),
                                                                                  radius=radius,
                                                                                  rotation=shapecpy.rotation)
            self.complex_instances.append(ComplexInstance(instance_name,
                                                          Point(shapecpy.x, shapecpy.y),
                                                          primitives))

        elif isinstance(shapecpy, Label):
            # TODO(shamer): cache positions segments for glyphs
            # FIXME((shamer): make baseline shift

            # TODO(shamer) select the correct font based off of the label.font_family

            # Debugging, used to show the anchor point of the label
            #self.shape_instances.append(ShapeInstance(Point(shapecpy.x, shapecpy.y), Aperture(None, Circle(0, 0, 1000000 / 5), None)))

            for segments in shapecpy._segments:
                line = Line(segments[0], segments[1])
                line.shift(shapecpy.x, shapecpy.y)
                self.smears.append(Smear(line, Circle(0, 0, 0.1016 * 1000000))) # 4 Mils


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

    The outline points define the outline of the fill. They
    must be contiguous, listed in order (ie, each point
    connects with the previous point and the next point)
    and not intersect each other.
    """

    def __init__(self, outline_points=None):
        self.outline_points = outline_points or list()


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

    def __init__(self, name, point, primitives):
        self.name = name
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
