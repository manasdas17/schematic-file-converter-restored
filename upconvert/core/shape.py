#!/usr/bin/env python2
""" The shape class """

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


from math import sqrt, pi, sin, cos, asin, acos


def stringify_attributes(attributes):
    attrs = {}
    for n, v in attributes.iteritems():
        attrs[n] = str(v)
    return attrs


class Shape(object):
    """a Shape with metadata and a list of shape parts
    Internal representation of the shapes closely matches JSON shapes """

    def __init__(self):
        self.type = None
        self.attributes = dict()
        self.styles = dict()


    def add_attribute(self, key, value):
        """ Add attribute to a shape """
        self.attributes[key] = value


    def bounds(self):
        """ Return the min and max points of the bounding box """
        raise NotImplementedError("Not implemented")


    def min_point(self):
        """ Return the min point of the shape """
        raise NotImplementedError("Not implemented")


    def max_point(self):
        """ Return the max point of the shape """
        raise NotImplementedError("Not implemented")


class Rectangle(Shape):
    """ A rectangle, defined by x, y of top left corner and width, height"""

    def __init__(self, x, y, width, height):
        super(Rectangle, self).__init__()
        self.type = "rectangle"
        self.x = x
        self.y = y
        self.width = width
        self.height = height


    def bounds(self):
        """ Return the min and max points of the bounding box """
        return [self.min_point(), self.max_point()]


    def min_point(self):
        """ Return the min point of the shape """
        return Point(min(self.x, self.x + self.width),
                     min(self.y, self.y + self.height))


    def max_point(self):
        """ Return the max point of the shape """
        return Point(max(self.x, self.x + self.width),
                     max(self.y, self.y + self.height))


    @classmethod
    def from_corners(cls, x, y, x2, y2):
        """ (x, y) is the top left corner, (x2, y2) is the bottom right """
        width = x2 - x
        height = y2 - y
        return cls(x, y, width, height)


    def scale(self, factor):
        """ Scale the x & y coordinates in the rectangle. """
        self.x *= factor
        self.y *= factor
        self.width *= factor
        self.height *= factor


    def json(self):
        """ Return the rectangle as JSON """
        return {
            "height": self.height,
            "type": self.type,
            "width": self.width,
            "x": self.x,
            "y": self.y,
            #"attributes": stringify_attributes(self.attributes),
            "styles": self.styles,
            }


class RoundedRectangle(Shape):
    """ A rectangle with rounded corners, defined by x, y of top left corner
    and width, height and corner radius"""

    def __init__(self, x, y, width, height, radius): # pylint: disable=R0913
        super(RoundedRectangle, self).__init__()
        self.type = "rounded_rectangle"
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.radius = radius


    def bounds(self):
        """ Return the min and max points of the bounding box """
        return [self.min_point(), self.max_point()]


    def min_point(self):
        """ Return the min point of the shape """
        return Point(min(self.x, self.x + self.width),
                     min(self.y, self.y + self.height))


    def max_point(self):
        """ Return the max point of the shape """
        return Point(max(self.x, self.x + self.width),
                     max(self.y, self.y + self.height))


    @classmethod
    def from_corners(cls, x, y, x2, y2, radius): # pylint: disable=R0913
        """ x and y are the top left corner of the rectangle, x2 and y2 are the
        bottom right corner of the rectangle """
        width = x2-x
        height = y2-y
        return cls(x, y, width, height, radius)


    def scale(self, factor):
        """ Scale the x & y coordinates in the rounded rectangle. """
        self.x *= factor
        self.y *= factor
        self.width *= factor
        self.height *= factor
        self.radius *= factor


    def json(self):
        """ Return the rounded rectangle as JSON """
        return {
            "height": self.height,
            "type": self.type,
            "width": self.width,
            "x": self.x,
            "y": self.y,
            "radius": self.radius,
            #"attributes": stringify_attributes(self.attributes),
            "styles": self.styles,
            }


class Arc(Shape):
    """ arc defined by center point x, y and two angles between which an
    arc is drawn """

    def __init__(self, x, y, start_angle, end_angle, radius): # pylint: disable=R0913
        super(Arc, self).__init__()
        self.type = "arc"
        self.x = x
        self.y = y
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.radius = radius


    def bounds(self):
        """ Return the min and max points of the bounding box """
        return [self.min_point(), self.max_point()]


    def _contains_angle(self, theta):
        """Return True iff tracing the arc passes through theta"""
        if abs(self.start_angle - self.end_angle) >= 2:
            # ha ha I'm actually a circle!
            return True
        # normalize angles to the interval [0, 2)
        start = self.start_angle % 2.0
        end = self.end_angle % 2.0
        theta = theta % 2.0

        if start == end:
            # arc is really a dot, I suppose?
            return theta == start
        elif start < end:
            return start <= theta and theta <= end
        else:
            # arc spans [start, 2.0), wraps around, and also spans [0, end]
            return start <= theta or theta <= end


    def min_point(self):
        """ Return the min point of the shape """
        start, end = (self.start_angle % 2.0) * pi, (self.end_angle % 2.0) * pi
        if self._contains_angle(1.5):
            # the top of the circle is included
            y = self.y - self.radius
        else:
            y = self.y + min([sin(start), sin(end)]) * self.radius
        if self._contains_angle(1):
            x = self.x - self.radius
        else:
            x = self.x + min([cos(start), cos(end)]) * self.radius
        return Point(int(round(x)), int(round(y)))


    def max_point(self):
        """ Return the max point of the shape """
        # assuming angle is in radians/pi, such that an angle of 1.0 is 180
        # degrees, assuming 0 is 3 o'clock, and angles increase clockwise.
        # normalize angles to the interval [0, 2)
        start, end = (self.start_angle % 2.0) * pi, (self.end_angle % 2.0) * pi
        if self._contains_angle(0.5):
            # the bottom of the circle is included
            y = self.y + self.radius
        else:
            y = self.y + max([sin(start), sin(end)]) * self.radius
        if self._contains_angle(0):
            x = self.x + self.radius
        else:
            x = self.x + max([cos(start), cos(end)]) * self.radius
        return Point(int(round(x)), int(round(y)))


    def ends(self):
        """ Calculate arc endpoints. """
        points = {}
        for ord_ in ('start', 'end'):
            opp = sin(getattr(self, ord_ + '_angle') * pi) * self.radius
            adj = cos(getattr(self, ord_ + '_angle') * pi) * self.radius
            points[ord_] = Point(self.x + adj, self.y - opp)
        return (points['start'], points['end'])


    def scale(self, factor):
        """ Scale the x & y coordinates in the arc. """
        self.x *= factor
        self.y *= factor
        self.radius *= factor


    def json(self):
        """ Return the arc as JSON """
        return {
            "start_angle": self.start_angle,
            "end_angle": self.end_angle,
            "type": self.type,
            "radius": self.radius,
            "x": self.x,
            "y": self.y,
            #"attributes": stringify_attributes(self.attributes),
            "styles": self.styles,
            }


class Circle(Shape):
    """ circle defined by center point x, y and radius """

    def __init__(self, x, y, radius):
        super(Circle, self).__init__()
        self.type = "circle"
        self.x = x
        self.y = y
        self.radius = abs(radius)


    def bounds(self):
        """ Return the min and max points of the bounding box """
        return [self.min_point(), self.max_point()]


    def min_point(self):
        """ Return the min point of the shape """
        x = self.x - self.radius
        y = self.y - self.radius
        return Point(x, y)


    def max_point(self):
        """ Return the max point of the shape """
        x = self.x + self.radius
        y = self.y + self.radius
        return Point(x, y)


    def scale(self, factor):
        """ Scale the x & y coordinates in the circle. """
        self.x *= factor
        self.y *= factor
        self.radius *= factor


    def json(self):
        """ Return the circle as JSON """
        return {
            "radius": self.radius,
            "type": self.type,
            "x": self.x,
            "y": self.y,
            #"attributes": stringify_attributes(self.attributes),
            "styles": self.styles,
            }


class Label(Shape):
    """ Text label with x, y location, alignment, rotation and text.
    Alignment can be 'left','right', or 'center'. """
    # pylint: disable=W0223

    def __init__(self, x, y, text, align, rotation): # pylint: disable=R0913
        super(Label, self).__init__()
        self.type = "label"
        self.x = x
        self.y = y
        self.text = text
        self.rotation = rotation # TODO verify correct value
        # Parse , TODO maybe clean this up some, dont need to accept
        #   all of these inputs, converting to lowercase would be enough
        if align in ["left", "Left"]:
            self.align = "left"
        elif align in ["right", "Right"]:
            self.align = "right"
        elif align in ["center", "Center", "centered", "Centered", "middle"]:
            self.align = "center"
        else:
            raise ValueError("Label requires the align to be either " +
                    "\"left\", \"right\", or \"center\" ")


    def bounds(self):
        """ Return the min and max points of the bounding box """
        return [self.min_point(), self.max_point()]


    def scale(self, factor):
        """ Scale the x & y coordinates in the label. """
        self.x *= factor
        self.y *= factor


    def json(self):
        """ Return the label as JSON """
        return {
            "type": self.type,
            "align": self.align,
            "rotation": self.rotation,
            "text": self.text,
            "x": self.x,
            "y": self.y,
            #"attributes": stringify_attributes(self.attributes),
            "styles": self.styles,
            }


class Line(Shape):
    """ line segment from point1 to point2 """

    def __init__(self, p1, p2):
        super(Line, self).__init__()
        self.type = "line"
        self.p1 = Point(p1)
        self.p2 = Point(p2)


    def bounds(self):
        """ Return the min and max points of the bounding box """
        return [self.min_point(), self.max_point()]


    def min_point(self):
        """ Return the min point of the shape """
        x = self.p1.x
        if self.p2.x < x:
            x = self.p2.x
        y = self.p1.y
        if self.p2.y < y:
            y = self.p2.y
        return Point(x, y)


    def max_point(self):
        """ Return the max point of the shape """
        x = self.p1.x
        if self.p2.x > x:
            x = self.p2.x
        y = self.p1.y
        if self.p2.y > y:
            y = self.p2.y
        return Point(x, y)


    def scale(self, factor):
        """ Scale the x & y coordinates in the line. """
        self.p1.scale(factor)
        self.p2.scale(factor)


    def json(self):
        """ Return the line as JSON """
        return {
            "type": self.type,
            "p1": self.p1.json(),
            "p2": self.p2.json(),
            #"attributes": stringify_attributes(self.attributes),
            "styles": self.styles,
            }


class Polygon(Shape):
    """ A polygon is just a list of points, drawn as connected in order """

    def __init__(self, points=None):
        super(Polygon, self).__init__()
        self.type = "polygon"
        self.points = points or list()


    def bounds(self):
        """ Return the min and max points of the bounding box """
        return [self.min_point(), self.max_point()]


    def min_point(self):
        """ Return the min point of the shape """
        if len(self.points) < 1:
            # by convention
            x, y = 0, 0
        else:
            x = min([pt.x for pt in self.points])
            y = min([pt.y for pt in self.points])
        return Point(x, y)


    def max_point(self):
        """ Return the max point of the shape """
        if len(self.points) < 1:
            # by convention
            x, y = 0, 0
        else:
            x = max([pt.x for pt in self.points])
            y = max([pt.y for pt in self.points])
        return Point(x, y)


    def add_point(self, x, y=None):
        """ Add a point to the polygon """
        self.points.append(Point(x, y))


    def scale(self, factor):
        """ Scale the x & y coordinates in the polygon. """
        for p in self.points:
            p.scale(factor)


    def json(self):
        """ Return the polygon as JSON """
        return {
            "type": self.type,
            "points": [point.json() for point in self.points],
            #"attributes": stringify_attributes(self.attributes),
            "styles": self.styles,
            }


class BezierCurve(Shape):
    """ A parametric curved line """

    def __init__(self, control1, control2, p1, p2):
        super(BezierCurve, self).__init__()
        self.type = "bezier"
        self.control1 = Point(control1)
        self.control2 = Point(control2)
        self.p1 = Point(p1)
        self.p2 = Point(p2)
        self._memo_cache = {'min_point': {}, 'max_point': {}}


    def _line(self):
        """ Convert the curve into a set of points. """
        segments = [(self.p1, self.control1),
                    (self.control1, self.control2),
                    (self.control2, self.p1)]
        # calculate maximum path length as straight lines between each point,
        # (think the curve itself can be no longer than that) then double it so
        # as not to skip points, and use that to decide t step size. Quite
        # possible too many points will result.
        maxpath = sum([sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2) for
                       p1, p2 in segments]) * 2
        # textbook Bezier interpolation
        bzx = lambda t: int(round((1-t) * (1-t) * (1-t) * self.p1.x +
                                 3 * (1-t) * (1-t) * t * self.control1.x +
                                 3 * (1-t) * t * t * self.control2.x +
                                 t * t * t * self.p2.x))
        bzy = lambda t: int(round((1-t) * (1-t) * (1-t) * self.p1.y +
                                 3 * (1-t) * (1-t) * t * self.control1.y +
                                 3 * (1-t) * t * t * self.control2.y +
                                 t * t * t * self.p2.y))
        points = [Point(bzx(t), bzy(t)) for t in [float(s)/maxpath for s in
                                                range(int(maxpath) + 1)]]
        return points


    def bounds(self):
        """ Return the min and max points of the bounding box """
        return [self.min_point(), self.max_point()]


    def min_point(self):
        """ Return the min point of the shape """
        # key the memoization cache on the actual (x,y) co-ords of our points
        cache_key = tuple([(p.x, p.y) for p in [self.p1, self.control1,
                                                self.control2, self.p2]])
        if cache_key not in self._memo_cache['min_point']:
            pts = self._line()
            x_pts = [pt.x for pt in pts]
            y_pts = [pt.y for pt in pts]
            self._memo_cache['min_point'][cache_key] = (min(x_pts), min(y_pts))
        # create a new Point each time, in case the caller modifies them
        return Point(self._memo_cache['min_point'][cache_key])


    def max_point(self):
        """ Return the max point of the shape """
        cache_key = tuple([(p.x, p.y) for p in [self.p1, self.control1,
                                                self.control2, self.p2]])
        if cache_key not in self._memo_cache['max_point']:
            pts = self._line()
            x_pts = [pt.x for pt in pts]
            y_pts = [pt.y for pt in pts]
            self._memo_cache['max_point'][cache_key] = (max(x_pts), max(y_pts))
        return Point(self._memo_cache['max_point'][cache_key])


    def build(self, control1x, control1y, control2x, control2y, p1x, # pylint: disable=R0913
            p1y, p2x, p2y):
        """ Build the bezier curve """
        self.type = "bezier"
        self.control1 = {"x":control1x, "y":control1y}
        self.control2 = {"x":control2x, "y":control2y}
        self.p1 = {"x":p1x, "y":p1y}
        self.p2 = {"x":p2x, "y":p2y}


    def scale(self, factor):
        """ Scale the x & y coordinates in the curve. """
        self.control1.scale(factor)
        self.control2.scale(factor)
        self.p1.scale(factor)
        self.p2.scale(factor)


    def json(self):
        """ Return the bezier curve as JSON """
        return {
            "type": self.type,
            "control1": self.control1.json(),
            "control2": self.control2.json(),
            "p1": self.p1.json(),
            "p2": self.p2.json(),
            #"attributes": stringify_attributes(self.attributes),
            "styles": self.styles,
            }


class Moire(Shape):
    """
    A target of concentric rings with crosshairs.

    Without rotation, the crosshairs are aligned to
    the axes. Rotation is in radians / pi, clockwise
    positive.

    """
    def __init__(self, x, y, outer, ring_thickness, gap, max_rings, # pylint: disable=R0913
                 hair_thickness, hair_length, rotation):
        super(Moire, self).__init__()
        self.type = "moire"
        self.x = x
        self.y = y
        self.outer_diameter = outer
        self.ring_thickness = ring_thickness
        self.gap_thickness = gap
        self.max_rings = max_rings
        self.hair_thickness = hair_thickness
        self.hair_length = hair_length
        self.rotation = rotation


    def bounds(self):
        """ Return the min and max points of the bounding box """
        return [self.min_point(), self.max_point()]


    def min_point(self):
        """ Return the min point of the shape """
        x = self.x - self._half_box()
        y = self.y - self._half_box()
        return Point(x, y)


    def max_point(self):
        """ Return the max point of the shape """
        x = self.x + self._half_box()
        y = self.y + self._half_box()
        return Point(x, y)


    def _half_box(self):
        """ Return half the width of the bounding square. """
        rad = self.outer_diameter / 2.0
        opp = abs(sin(self.rotation * pi) * rad)
        adj = abs(cos(self.rotation * pi) * rad)
        return max(opp, adj, rad)


    def scale(self, factor):
        """ Scale the x & y coordinates in the moire. """
        self.x *= factor
        self.y *= factor


    def json(self):
        """ Return the moire as JSON """
        return {
            "x": self.x,
            "y": self.y,
            "outer_diameter": self.outer_diameter,
            "ring_thickness": self.ring_thickness,
            "gap_thickness": self.gap_thickness,
            "max_rings": self.max_rings,
            "hair_thickness": self.hair_thickness,
            "hair_length": self.hair_length,
            "rotation": self.rotation,
            #"attributes": stringify_attributes(self.attributes),
            "styles": self.styles,
            }


class Thermal(Shape):
    """
    A ring with 4 gaps, each separated by 0.5 rad/pi.

    Without rotation, the gaps are at the cardinal points.
    Rotation is in rad/pi, clockwise positive.

    """
    def __init__(self, x, y, outer, inner, gap, rotation=0): # pylint: disable=R0913
        super(Thermal, self).__init__()
        self.type = "thermal"
        self.x = x
        self.y = y
        self.outer_diameter = outer
        self.inner_diameter = inner
        self.gap_thickness = gap
        self.rotation = rotation


    def bounds(self):
        """ Return the min and max points of the bounding box """
        return [self.min_point(), self.max_point()]


    def min_point(self):
        """ Return the min point of the shape """
        x = self.x - self._half_box()
        y = self.y - self._half_box()
        return Point(x, y)


    def max_point(self):
        """ Return the max point of the shape """
        x = self.x + self._half_box()
        y = self.y + self._half_box()
        return Point(x, y)


    def _half_box(self):
        """ Return half the width of the bounding box. """
        hyp = self.outer_diameter / 2.0
        opp = self.gap_thickness / 2.0
        norm_theta = asin(opp / hyp) / pi
        rot = self.rotation % 0.5
        if rot < norm_theta:
            hwid = cos((norm_theta - rot) * pi) * hyp
        elif (0.5 - rot) < norm_theta:
            hwid = cos((norm_theta - (0.5 - rot)) * pi) * hyp
        else:
            hwid = hyp
        return hwid


    def scale(self, factor):
        """ Scale the x & y coordinates in the thermal. """
        self.x *= factor
        self.y *= factor


    def json(self):
        """ Return the thermal as JSON """
        return {
            "x": self.x,
            "y": self.y,
            "outer_diameter": self.outer_diameter,
            "inner_diameter": self.inner_diameter,
            "gap_thickness": self.gap_thickness,
            "rotation": self.rotation,
            #"attributes": stringify_attributes(self.attributes),
            "styles": self.styles,
            }


class RegularPolygon(Shape):
    """
    A polygon with sides of equal length.

    Without rotation, the first vertex is at 3 o'clock.
    Rotation is in rad/pi, clockwise positive.

    """
    def __init__(self, x, y, outer, vertices, rotation=0): # pylint: disable=R0913
        super(RegularPolygon, self).__init__()
        self.type = "regular polygon"
        self.x = x
        self.y = y
        self.outer_diameter = outer
        self.vertices = vertices
        self.rotation = rotation


    def bounds(self):
        """ Return the min and max points of the bounding box """
        return [self.min_point(), self.max_point()]


    def min_point(self):
        """ Return the min point of the shape """
        x = self.x + self._max_dist(1)
        y = self.y + self._max_dist(0.5)
        return Point(x, y)


    def max_point(self):
        """ Return the max point of the shape """
        x = self.x + self._max_dist(0)
        y = self.y + self._max_dist(1.5)
        return Point(x, y)


    def _max_dist(self, axis_rads):
        """ Return max reach of the shape along an axis. """
        v_rads = 2.0 / self.vertices
        if self.vertices % 2 == 0:
            hyp = self.outer_diameter / 2.0
        else:
            hyp = self.outer_diameter - acos(v_rads / 2.0)
        start_angle = (axis_rads + self.rotation) % v_rads
        this_v = abs(cos(start_angle * pi) * hyp)
        next_v = abs(cos((start_angle - v_rads) * pi) * hyp)
        return max(this_v, next_v)


    def scale(self, factor):
        """ Scale the x & y coordinates in the polygon. """
        self.x *= factor
        self.y *= factor
        for v in self.vertices:
            v.scale(factor)


    def json(self):
        """ Return the regular polygon as JSON """
        return {
            "x": self.x,
            "y": self.y,
            "outer_diameter": self.outer_diameter,
            "vertices": self.vertices,
            "rotation": self.rotation,
            #"attributes": stringify_attributes(self.attributes),
            "styles": self.styles,
            }


class Point:
    """ Simple x, y coordinate. Different from the 'Point' in Nets """

    def __init__(self, x, y=None):
        if y is not None:
            self.x = x
            self.y = y
        # Do a copy of a Point if passed
        elif isinstance(x, Point):
            self.x = x.x
            self.y = x.y
        # Allow for instantiation from a tuple
        else:
            self.x, self.y = x


    def __repr__(self):
        return 'Point(%d, %d)' % (self.x, self.y)


    def __eq__(self, other):
        """
        Compare with another point. eg: p1 == p2

        Points are considered equal if they are equal when
        rounded to maximum gerber precision (ie, 6 decimal
        places).

        """
        snap = True
        precision = 6
        if snap:
            equal = (isinstance(other, Point) and
                     round(self.x, precision) == round(other.x, precision) and
                     round(self.y, precision) == round(other.y, precision))
        else:
            equal = self.__dict__ == other.__dict__
        return equal


    def dist(self, other):
        """ Calculate the distance to another point. """
        delta_x = self.x - other.x
        delta_y = self.y - other.y
        return sqrt(delta_x**2 + delta_y**2)


    def scale(self, factor):
        """ Scale the x & y coordinates in the point. """
        self.x *= factor
        self.y *= factor


    def json(self):
        """ Return the point as JSON """
        return {
            "x": self.x,
            "y": self.y,
            }


class Obround(Shape):
    """ An oval, defined by x, y at center and width, height"""

    def __init__(self, x, y, width, height):
        super(Obround, self).__init__()
        self.type = "obround"
        self.x = x
        self.y = y
        self.width = width
        self.height = height


    def bounds(self):
        """ Return the min and max points of the bounding box """
        return [self.min_point(), self.max_point()]


    def min_point(self):
        """ Return the min point of the shape """
        x = self.x - self.width / 2.0
        y = self.y - self.height / 2.0
        return Point(x, y)


    def max_point(self):
        """ Return the max point of the shape """
        x = self.x + self.width / 2.0
        y = self.y + self.height / 2.0
        return Point(x, y)


    def scale(self, factor):
        """ Scale the x & y coordinates in the oval. """
        self.x *= factor
        self.y *= factor
        self.width *= factor
        self.height *= factor


    def json(self):
        """ Return the oval as JSON """
        return {
            "height": self.height,
            "type": self.type,
            "width": self.width,
            "x": self.x,
            "y": self.y,
            #"attributes": stringify_attributes(self.attributes),
            "styles": self.styles,
            }

