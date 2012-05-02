from PIL import Image, ImageDraw
from math import cos, sin, pi, sqrt
from upconvert.core.shape import Point

class Render:
    """Image output renderer, inspired by ajray's render.py """
    def __init__(self, des, outtype='PNG',
                 bground=(255, 255, 255), fground=(0, 0, 0),
                 scale=1):
        """ des is the design to output. fground applied to all parts. """
        self.des, self.outtype = des, outtype
        self.fg, self.bg, self.scale = fground, bground, scale
        # TODO I think this causes problems if the top left corner is not (0,0)
        minpt, maxpt = self.des.bounds()
        self.img = Image.new('RGB', (int((maxpt.x - minpt.x) * self.scale),
                                     int((maxpt.y - minpt.y) * self.scale)),
                             self.bg)
        self.draw = ImageDraw.Draw(self.img)

    def save(self, filename):
        self.img.save(filename, self.outtype)

    def draw_ckt(self):
        scale = Scale(self.scale)
        for ci in self.des.component_instances:
            c = self.des.components.components[ci.library_id]
            for body, attr in zip(c.symbols[ci.symbol_index].bodies,
                                  ci.symbol_attributes):
                #self.draw_sym(b, (a.x, a.y), a.rotation, a.flipped, self.draw)
                pos = Point(attr.x, attr.y)
                self.draw_sym(body, scale.chain(pos), attr.rotation,
                              False, scale, self.draw)
                for ann in attr.annotations:
                    if ann.visible:
                        pos = scale.chain(Point(ann.x, ann.y))
                        self.draw.text((pos.x, pos.y), ann.value, fill=self.fg)

        #for sh in self.des.shapes:
        #    if sh.type == 'arc':
        #        # special case, it needs a rotation passed, even for 0
        #        self.draw_shape_arc(sh, scale, 0, self.draw)
        #    else:
        #        getattr(self, 'draw_shape_%s' % sh.type)(sh, scale, self.draw)

        for net in self.des.nets:
            # need a second dict so that removing nets as they are drawn does
            # not affect the actual design object.
            connects = dict([(pt.point_id, list(pt.connected_points))
                             for pt in net.points.values()])
            for pid, connlist in connects.items():
                pidpt = scale.chain(net.points[pid])
                for junc in connlist:
                    juncpt = scale.chain(net.points[junc])
                    # draw a line to each connected point
                    self.draw.line([(pidpt.x, pidpt.y),
                                    (juncpt.x, juncpt.y)],
                                    fill=self.fg)
                    # don't need the connected point to draw a line back
                    connects[junc].remove(pid)
                    # TODO draw the connection to the component pin
                    # TODO draw solder dots on net connections
            for ann in net.annotations:
                pos = scale.chain(Point(ann.x, ann.y))
                self.draw.text((pos.x, pos.y), ann.value, fill=self.fg)

        for ann in self.des.design_attributes.annotations:
            if ann.visible:
                pos = scale.chain(Point(ann.x, ann.y))
                self.draw.text((pos.x, pos.y), ann.value, fill=self.fg)
    
    def draw_sym(self, body, offset=Point(0,0), rot=0, flip=False,
                 xform=None, draw=None):
        '''draw a symbol at the location of offset'''
        # create a lambda function that will rotate, then shift an (x,y)
        # pair that we can use it on all the relevent points
        if xform is None:
            xform = XForm()
        xform = Shift(offset.x, offset.y, Rotate(rot, xform))
        if flip:
            xform = FlipY(xform)
        draw = draw or self.draw

        for shape in body.shapes:
            if shape.type == 'arc':
                # special case, to pass along rotation
                self.draw_shape_arc(shape, xform, rot, draw)
            else:
                getattr(self, 'draw_shape_%s' % shape.type)(shape, xform, draw)

        for pin in body.pins:
            self.draw_pin(pin, xform, draw)

    def draw_shape_circle(self, circle, xform, draw):
        minpt, maxpt = [xform.chain(p) for p in circle.bounds()]
        xs, ys = [minpt.x, maxpt.x], [minpt.y, maxpt.y]
        # draw.ellipse gets confused if x1 > x0 or y1 > y0
        draw.ellipse((min(xs), min(ys), max(xs), max(ys)), outline=self.fg)

    def draw_shape_line(self, line, xform, draw):
        pts = [xform.chain(p) for p in (line.p1, line.p2)]
        draw.line([(p.x, p.y) for p in pts], fill=self.fg)

    def draw_shape_polygon(self, poly, xform, draw):
        pts = [xform.chain(p) for p in poly.points]
        draw.polygon([(p.x, p.y) for p in pts], outline=self.fg)

    def draw_shape_arc(self, arc, xform, rot, draw):
        # using arc.bounds would break if arc.bounds() no longer returns bounds
        # of full circle
        x, y, r = arc.x, arc.y, arc.radius
        minpt, maxpt = [xform.chain(Point(px, py)) for (px, py)
                        in [(x - r, y - r), (x + r, y + r)]]

        xs, ys = [minpt.x, maxpt.x], [minpt.y, maxpt.y]
        # draw.arc gets confused if box[0] > box[2] or box[1] > box[3]
        box = (min(xs), min(ys), max(xs), max(ys))

        # 3 o'clock is angle of 0, angles increase clockwise
        (start, end) = [int(180/pi * (theta + rot*(-pi))) for theta in
                        [arc.end_angle, arc.start_angle]]
        draw.arc(box, start, end, fill=self.fg)

    def draw_shape_rectangle(self, rect, xform, draw):
        # use polygon-style, so it'll handle rotated rectangles
        pts = [Point(p) for p in [(rect.x, rect.y),
                                  (rect.x + rect.width, rect.y),
                                  (rect.x + rect.width, rect.y + rect.height),
                                  (rect.x, rect.y + rect.height)]]
        pts = [xform.chain(p) for p in pts]
        draw.polygon([(p.x, p.y) for p in pts], outline=self.fg)

    def draw_shape_rounded_rectangle(self, rect, xform, draw):
        #TODO handle this with lines and arcs
        self.draw_shape_rectangle(rect, xform, draw)

    def draw_shape_label(self, label, xform, draw):
        #TODO deal with alignment, rotation
        pos = xform.chain(Point(label.x, label.y))
        draw.text((pos.x, pos.y), label.text, fill=self.fg)

    def draw_shape_bezier(self, bez, xform, draw):
        # hasn't really been tested properly, but seems okay
        # calculate maximum path length as straight lines between each point,
        # then double it, and use that to decide t step size
        pts = [xform.chain(p) for p in [bez.point1, bez.control1,
                                        bez.control2, bez.point2]]
        maxpath = sum(map(lambda (p1, p2): sqrt((p2.x - p1.x)**2 +
                                                (p2.y - p1.y)**2),
                          zip(pts, pts[1:]))) * 2
        dt = 1. / maxpath
        p0, p1, p2, p3 = pts
        # textbook Bezier interpolation
        Bx = lambda t: int(    (1-t)**3        * p0.x +
                           3 * (1-t)**2 * t    * p1.x +
                           3 * (1-t)    * t**2 * p2.x +
                                          t**3 * p3.x)
        By = lambda t: int(    (1-t)**3        * p0.y +
                           3 * (1-t)**2 * t    * p1.y +
                           3 * (1-t)    * t**2 * p2.y +
                                          t**3 * p3.y)

        for i in xrange(0, int(1./dt)):
            draw.point((Bx(i * dt), By(i * t)), fill=self.fg)
        # make sure to draw in the endpoint
        draw.point((Bx(1.), By(1.)), fill=self.fg)

    def draw_pin(self, pin, xform, draw):
        line = [xform.chain(p) for p in (pin.p1, pin.p2)]
        draw.line([(p.x, p.y) for p in line], fill=self.fg)

class XForm(object):
    """ Transformations operate on a Point, can also be chained. """
    def __init__(self, prev=None):
        """ Create a transformation.
        prev is an optional transformation to append this one to. """
        self.prev = prev

    def chain(self, pt):
        """ Apply all the transformations, one after the other. """
        if self.prev is not None:
            pt = self.prev.chain(pt)
        return self.convert(pt)

    def convert(self, pt):
        """ Apply just this transformation. """
        # default transformation is to do nothing
        return Point(pt)

class Shift(XForm):
    def __init__(self, dx, dy, prev=None):
        """ A transformation that shifts Points by (dx, dy). """
        XForm.__init__(self, prev)
        self.dx, self.dy = dx, dy

    def convert(self, pt):
        return Point(pt.x + self.dx,
                     pt.y + self.dy)

class Rotate(XForm):
    def __init__(self, theta, prev=None):
        """ A transformation that will rotate a Point theta*pi rads CW. """
        XForm.__init__(self, prev)
        self.theta = theta * -pi

    def convert(self, pt):
        cos_t, sin_t = cos(self.theta), sin(self.theta)
        return Point(int(round(cos_t * pt.x - sin_t * pt.y)),
                     int(round(sin_t * pt.x + cos_t * pt.y)))

class FlipY(XForm):
    """ A transformation to flip around the y axis. """
    def convert(self, pt):
        return Point(0 - pt.x, pt.y)

class Scale(XForm):
    def __init__(self, scale, prev=None):
        XForm.__init__(self, prev)
        self.scale = scale

    def convert(self, pt):
        return Point(int(pt.x * self.scale), int(pt.y * self.scale))
