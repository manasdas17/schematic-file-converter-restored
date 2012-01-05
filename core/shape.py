#!/usr/bin/env python
""" The shape class """


class Shape(object):
    """a Shape with metadata and a list of shape parts
    Iternal representation of the shapes closely matches JSON shapes """

    def __init__(self):
        self.type = None
    
    
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
        x = self.x
        if self.width < 0:
            x += self.width
        y = self.y - self.height
        if self.height < 0:
            y += self.height
        return Point(x, y)
    
    
    def max_point(self):
        """ Return the max point of the shape """
        x = self.x + self.width
        if self.width < 0:
            x -= self.width
        y = self.y
        if self.height < 0:
            y -= self.height
        return Point(x, y)


    @classmethod
    def from_corners(cls, x, y, x2, y2):
        """ (x, y) is the top left corner, (x2, y2) is the bottom right """
        width = x2 - x
        height = y2 - y
        return cls(x, y, width, height)


    def json(self):
        """ Return the rectangle as JSON """
        return {
            "height": self.height,
            "type": self.type,
            "width": self.width,
            "x": self.x,
            "y": self.y,
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
        x = self.x
        if self.width < 0:
            x += self.width
        y = self.y - self.height
        if self.height < 0:
            y += self.height
        return Point(x, y)
    
    
    def max_point(self):
        """ Return the max point of the shape """
        x = self.x + self.width
        if self.width < 0:
            x -= self.width
        y = self.y
        if self.height < 0:
            y -= self.height
        return Point(x, y)


    @classmethod
    def from_corners(cls, x, y, x2, y2, radius): # pylint: disable=R0913
        """ x and y are the top left corner of the rectangle, x2 and y2 are the
        bottom right corner of the rectangle """
        width = x2-x
        height = y2-y
        return cls(x, y, width, height, radius)


    def json(self):
        """ Return the rounded rectangle as JSON """
        return {
            "height": self.height,
            "type": self.type,
            "width": self.width,
            "x": self.x,
            "y": self.y,
            "radius": self.radius,
            }


class Arc(Shape):
    """ arc defined by center point x, y and two angles between which an
    arc is drawn """
    # pylint: disable=W0223

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


    def json(self):
        """ Return the arc as JSON """
        return {
            "start_angle": self.start_angle,
            "end_angle": self.end_angle,
            "type": self.type,
            "radius": self.radius,
            "x": self.x,
            "y": self.y,
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


    def json(self):
        """ Return the circle as JSON """
        return {
            "radius": self.radius,
            "type": self.type,
            "x": self.x,
            "y": self.y,
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


    def json(self):
        """ Return the label as JSON """
        return {
            "type": self.type,
            "align": self.align,
            "rotation": self.rotation,
            "text": self.text,
            "x": self.x,
            "y": self.y,
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


    def json(self):
        """ Return the line as JSON """
        return {
            "type": self.type,
            "p1": self.p1.json(),
            "p2": self.p2.json(),
            }


class Polygon(Shape):
    """ A polygon is just a list of points, drawn as connected in order """

    def __init__(self):
        super(Polygon, self).__init__()
        self.type = "polygon"
        self.points = list()

    
    def bounds(self):
        """ Return the min and max points of the bounding box """
        return [self.min_point(), self.max_point()]


    def min_point(self):
        """ Return the min point of the shape """
        if len(self.points) < 1:
            return None
        x = self.points[0].x
        y = self.points[0].y
        for point in self.points:
            if point.x < x:
                x = point.x
            if point.y < y:
                y = point.y
        return Point(x, y)
    
    
    def max_point(self):
        """ Return the max point of the shape """
        if len(self.points) < 1:
            return None
        x = self.points[0].x
        y = self.points[0].y
        for point in self.points:
            if point.x > x:
                x = point.x
            if point.y > y:
                y = point.y
        return Point(x, y)


    def add_point(self, x, y=None):
        """ Add a point to the polygon """
        self.points.append(Point(x, y))


    def json(self):
        """ Return the polygon as JSON """
        return {
            "type": self.type,
            "points": [point.json() for point in self.points],
            }


class BezierCurve(Shape):
    """ A parametric curved line """
    # pylint: disable=W0223

    def __init__(self, control1, control2, p1, p2):
        super(BezierCurve, self).__init__()
        self.type = "bezier"
        self.control1 = Point(control1)
        self.control2 = Point(control2)
        self.p1 = Point(p1)
        self.p2 = Point(p2)
    
    
    def bounds(self):
        """ Return the min and max points of the bounding box """
        return [self.min_point(), self.max_point()]


    def build(self, control1x, control1y, control2x, control2y, p1x, # pylint: disable=R0913
            p1y, p2x, p2y):
        """ Build the bezier curve """
        self.type = "bezier"
        self.control1 = {"x":control1x, "y":control1y}
        self.control2 = {"x":control2x, "y":control2y}
        self.p1 = {"x":p1x, "y":p1y}
        self.p2 = {"x":p2x, "y":p2y}


    def json(self):
        """ Return the bezier curve as JSON """
        return {
            "type": self.type,
            "control1": self.control1.json(),
            "control2": self.control2.json(),
            "p1": self.p1.json(),
            "p2": self.p2.json(),
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


    def json(self):
        """ Return the point as JSON """
        return {
            "x": self.x,
            "y": self.y
            }
