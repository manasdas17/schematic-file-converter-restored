#!/usr/bin/env python2
""" A crude image output writer, inspired by ajray's render.py """

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


from PIL import Image as Img, ImageDraw
from math import cos, sin, pi, sqrt, atan
from collections import defaultdict
from upconvert.core.shape import Point


class Image:
    """ encapsulates rendering options and provides the write() method """
    default_style = {'bground': (255, 255, 255),
                     'fground': (  0,   0,   0),
                     'net'    : (  0, 180,   0),
                     'annot'  : (140, 140, 140),
                     'part'   : (  0,   0,   0),
                    }


    def __init__(self, img_format='PNG', style={}, scale=1):
        # Override default style where the user provided some
        self.style = self.default_style
        self.style.update(style)
        self.scale = scale
        self.img_format = img_format


    def write(self, design, filename):
        """ create a worker and have it build and output the image """
        writer = Worker(design, self)
        writer.save(filename)



class Worker:
    """ Does the actual work of converting and saving an image """
    

    def __init__(self, design, options):
        self.design, self.options = design, options
        # Calculate the image size
        minpt, maxpt = self.design.bounds()
        width = int(maxpt.x - minpt.x)
        height = int(maxpt.y - minpt.y)

        # Setup image & design
        self.image = Img.new('RGB', (width * self.options.scale,
                                     height * self.options.scale),
                             self.options.style['bground'])
        self.canvas = ImageDraw.Draw(self.image)

        # Draw & save image
        self.base_xform = Scale(self.options.scale,
                                FixY(height, Shift(-minpt.x, -minpt.y)))
        self.draw_design()


    def save(self, filename):
        """ Save to a file """
        self.image.save(filename, self.options.img_format)


    def draw_design(self):
        """ Render the design into 2 images """
        if len(self.design.traces) > 0:
            self.draw_layout()
        else:
            self.draw_schematic()


    def draw_schematic(self):
        """ Render the schematic into self.img """
        # start off with all the component instances
        for inst in self.design.component_instances:
            comp = self.design.components.components[inst.library_id]
            for body, attr in zip(comp.symbols[inst.symbol_index].bodies,
                                  inst.symbol_attributes):
                # draw the appropriate body, at the position in attr
                pos = Point(attr.x, attr.y)
                self.draw_symbol(body, pos, attr.rotation, attr.flip)
                # draw in any annotations
                for ann in attr.annotations:
                    if ann.visible:
                        pos = self.base_xform.chain(Point(ann.x, ann.y))
                        self.canvas.text((pos.x, pos.y), ann.value,
                                         fill=self.options.style['annot'])

        for shape in self.design.shapes:
            draw_method = getattr(self, 'draw_shape_%s' % shape.type)
            draw_method(shape, self.base_xform, self.options.style['annot'])

        for net in self.design.nets:
            self.draw_net(net)

        for ann in self.design.design_attributes.annotations:
            if ann.visible:
                pos = self.base_xform.chain(Point(ann.x, ann.y))
                self.canvas.text((pos.x, pos.y), ann.value,
                                  fill=self.options.style['annot'])


    def draw_layout(self):
        """ Render the layout into self.img """
        # start off with all the component instances
        for inst in self.design.component_instances:
            comp = self.design.components.components[inst.library_id]
            for body, attr in zip(comp.footprints[inst.footprint_index].bodies,
                                  inst.footprint_attributes):
                # draw the appropriate body, at the position in attr
                pos = Point(attr.x, attr.y)
                self.draw_footprint(body, pos, attr.rotation, attr.flip)
                # draw in any annotations
                for ann in attr.annotations:
                    if ann.visible:
                        pos = self.base_xform.chain(Point(ann.x, ann.y))
                        self.canvas.text((pos.x, pos.y), ann.value,
                                         fill=self.options.style['annot'])

        for trace in self.design.traces:
            self.draw_trace(trace)


    def draw_symbol(self, body, offset, rot, flip):
        """draw a symbol at the location of offset"""
        xform = self.base_xform.copy()
        # flip if necessary, then rotate the symbol, then shift.
        # Want to rotate before it's been moved away from the global origin.
        if flip:
            flipper = FlipY()
        else:
            flipper = XForm()

        locxform = Shift(offset.x, offset.y, Rotate(rot, flipper))
        xform.prefix(locxform)

        for shape in body.shapes:
            draw_method = getattr(self, 'draw_shape_%s' % shape.type)
            draw_method(shape, xform, self.options.style['part'])

        for pin in body.pins:
            self.draw_pin(pin, xform)


    def draw_footprint(self, body, offset, rot, flip):
        """draw a footprint at the location of offset"""
        xform = self.base_xform.copy()
        # flip if necessary, then rotate the footprint, then shift.
        # Want to rotate before it's been moved away from the global origin.
        if flip:
            flipper = FlipY()
        else:
            flipper = XForm()

        locxform = Shift(offset.x, offset.y, Rotate(rot, flipper))
        xform.prefix(locxform)

        for shape in body.shapes:
            draw_method = getattr(self, 'draw_shape_%s' % shape.type)
            draw_method(shape, xform, self.options.style['part'])

        for pad in body.pads:
            self.draw_pad(pad, xform)


    def draw_net(self, net):
        """ draw out a net """
        # need a second dict so that removing nets as they are drawn does
        # not affect the actual design object.
        connects = dict([(pt.point_id, list(pt.connected_points))
                         for pt in net.points.values()])
        for pid, connlist in connects.items():
            pidpt = self.base_xform.chain(net.points[pid])
            for junc in connlist:
                juncpt = self.base_xform.chain(net.points[junc])
                # draw a line to each connected point from this junction
                self.canvas.line([(pidpt.x, pidpt.y),
                                  (juncpt.x, juncpt.y)],
                                 fill=self.options.style['net'])
                # don't need the connected point to draw a line back
                connects[junc].remove(pid)
                # TODO draw the connection to the component pin
                #      (may actually be done)

        for pt in net.points.values():
            if self.dot_at(pt, net):
                drawpt = self.base_xform.chain(pt)
                # arbitrarily, drawing the dot 4x the minimum dimension in the 
                # design + 1 pixel.
                scale = self.options.scale * 2
                # draw the actual solder dot
                self.canvas.ellipse((drawpt.x - scale, drawpt.y - scale,
                                     drawpt.x + scale, drawpt.y + scale),
                                     outline=self.options.style['net'],
                                     fill=self.options.style['net'])

        for ann in net.annotations:
            pos = self.base_xform.chain(Point(ann.x, ann.y))
            self.canvas.text((pos.x, pos.y), ann.value,
                             fill=self.options.style['annot'])


    def draw_trace(self, trace):
        """ draw out a trace """
        pts = [xform.chain(p) for p in (trace.p1, trace.p2)]
        self.canvas.line([(p.x, p.y) for p in pts], fill=colour)


    def dot_at(self, pt, net):
        """ return True if a solder dot is required at pt on net """
        if len(pt.connected_points) + len(pt.connected_components) < 3:
            # definitely not a solder dot, so don't try harder
            return False
        lines = defaultdict(list)
        for pid in pt.connected_points:
            connpt = net.points[pid]
            if pt.x == connpt.x:
                # case of a pt connected to itself falls through the cracks
                # here, as is appropriate. Not sure why it would happen, but if
                # it does it doesn't make any difference as to whether to draw a
                # solder dot or no
                if pt.y != connpt.y:
                    # infinite slope
                    lines[None].append(connpt)
            else:
                slope = float(connpt.y - pt.y) / (connpt.x - pt.x)
                lines[slope].append(connpt)

        spokes = 0
        for slope, pts in lines.items():
            # figure out which axis to compare along
            if slope is None:
                # actually, this means infinite slope
                axis = lambda p: p.y
            else:
                axis = lambda p: p.x

            pts.sort(key=axis)
            if axis(pts[0]) < axis(pt):
                # there is at least one connected point "lower" along this slope
                spokes += 1
            if axis(pts[-1]) > axis(pt):
                # there is at least one connected point "higher" along the slope
                spokes += 1

        return (spokes + len(pt.connected_components)) > 2


    def draw_shape_circle(self, circle, xform, colour):
        """ draw a circle """
        minpt, maxpt = [xform.chain(p) for p in circle.bounds()]
        xs, ys = [minpt.x, maxpt.x], [minpt.y, maxpt.y]
        # draw.ellipse gets confused if x1 > x0 or y1 > y0
        self.canvas.ellipse((min(xs), min(ys), max(xs), max(ys)),
                            outline=colour)


    def draw_shape_line(self, line, xform, colour):
        """ draw a line segment """
        pts = [xform.chain(p) for p in (line.p1, line.p2)]
        self.canvas.line([(p.x, p.y) for p in pts], fill=colour)


    def draw_shape_polygon(self, poly, xform, colour):
        """ draw a multi-segment polygon """
        pts = [xform.chain(p) for p in poly.points]
        self.canvas.polygon([(p.x, p.y) for p in pts], outline=colour)


    def draw_shape_arc(self, arc, xform, colour):
        """ draw an arc segment """
        x, y, r = arc.x, arc.y, arc.radius
        # if the arc segment were extended to draw a full circle, box would
        # enclose that circle
        minpt, maxpt = [xform.chain(Point(px, py)) for (px, py)
                        in [(x - r, y - r), (x + r, y + r)]]
        xs, ys = [minpt.x, maxpt.x], [minpt.y, maxpt.y]
        box = (min(xs), min(ys), max(xs), max(ys))

        center = xform.chain(Point(x, y))

        def pt_to_deg(pt):
            # given a point, give the angle w.r.t. to the xform'd center of the
            # arc (ie. where it will be when drawn)
            # 3 o'clock is angle of 0, angles increase clockwise
            opp, adj = pt.y - center.y, pt.x - center.x
            if adj == 0:
                if opp > 0:
                    return 90
                return 270
            angle = 180 * atan(opp / float(adj)) / pi
            if pt.x < center.x:
                angle += 180
            return int(angle % 360)

        # create a point in the middle of the arc (used to detect that the xform
        # has flipped the arc around. In that case, drawing from start_angle to
        # end_angle will go in the wrong direction, and draw out exactly the
        # wrong part of the circle)
        mid_ang = (arc.start_angle + arc.end_angle) / 2
        if arc.start_angle > arc.end_angle:
            mid_ang = (mid_ang - 1) % 2
        mid_pt = xform.chain(Point(cos((2 - mid_ang) * pi) * arc.radius + x,
                                   sin((2 - mid_ang) * pi) * arc.radius + y))

        start, end = [xform.chain(pt) for pt in arc.ends()]
        if pt_to_deg(start) < pt_to_deg(end):
            if not (pt_to_deg(start) < pt_to_deg(mid_pt) <  pt_to_deg(end)):
                # swap start and end so that the arc traces through the
                # transformed midpoint
                start, end = end, start
        elif (pt_to_deg(end) < pt_to_deg(mid_pt) < pt_to_deg(start)):
            # swap start and end so that the arc traces through the
            # transformed midpoint
            start, end = end, start

        # by using the arc.ends() points, any rotation in xform gets handled
        # properly.
        self.canvas.arc(box, pt_to_deg(start), pt_to_deg(end), fill=colour)


    def draw_shape_rectangle(self, rect, xform, colour):
        """ draw a rectangle """
        # use polygon-style, so it'll handle rotated rectangles
        pts = [Point(p) for p in [(rect.x, rect.y),
                                  (rect.x + rect.width, rect.y),
                                  (rect.x + rect.width, rect.y - rect.height),
                                  (rect.x, rect.y - rect.height)]]
        pts = [xform.chain(p) for p in pts]
        self.canvas.polygon([(p.x, p.y) for p in pts], outline=colour)


    def draw_shape_rounded_rectangle(self, rect, xform, colour):
        """ draw a rectangle, eventually with rounded corners """
        for shape in rect.as_arcs_lines():
            getattr(self, 'draw_shape_%s' % shape.type)(shape, xform, colour)


    def draw_shape_label(self, label, xform, colour):
        """ draw a text label """
        #TODO deal with alignment, rotation
        pos = xform.chain(Point(label.x, label.y))
        self.canvas.text((pos.x, pos.y), label.text, fill=colour)


    def draw_shape_bezier(self, bez, xform, colour):
        """ draw a bezier curve """
        # hasn't really been tested properly, but seems okay
        # calculate maximum path length as straight lines between each point,
        # then double it, and use that to decide t step size
        pts = [xform.chain(p) for p in [bez.point1, bez.control1,
                                        bez.control2, bez.point2]]
        maxpath = sum([sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)
                       for (p1, p2) in zip(pts, pts[1:])]) * 2
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
            self.canvas.point((Bx(i * dt), By(i * dt)), fill=colour)
        # make sure to draw in the endpoint
        self.canvas.point((Bx(1.), By(1.)), fill=colour)


    def draw_pin(self, pin, xform):
        """ draw a component's pin """
        # TODO special pin characteristics (inverted, clock)?
        line = [xform.chain(p) for p in (pin.p1, pin.p2)]
        self.canvas.line([(p.x, p.y) for p in line],
                         fill=self.options.style['part'])



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
        return pt


    def prefix(self, xform):
        """ Put another transformation at the start of this chain. """
        tail = self
        while tail.prev != None:
            tail = tail.prev
        tail.prev = xform


    def copy(self):
        """ A deep copy of the xform chain, from the first XForm to here """
        cprev = None
        if self.prev is not None:
            cprev = self.prev.copy()
        return self._copy(cprev)


    def _copy(self, previous):
        """ A copy of just this transformation, appended to `previous` """
        return XForm(previous)



class Shift(XForm):
    """ Simple shift in cartesian coordinates """
    def __init__(self, dx, dy, prev=None):
        """ A transformation that shifts Points by (dx, dy). """
        XForm.__init__(self, prev)
        self.dx, self.dy = dx, dy


    def convert(self, pt):
        return Point(pt.x + self.dx,
                     pt.y + self.dy)


    def _copy(self, previous):
        return Shift(self.dx, self.dy, previous)



class Rotate(XForm):
    """ Rotation around the origin """
    def __init__(self, theta, prev=None):
        """ A transformation that will rotate a Point theta*pi rads CW. """
        XForm.__init__(self, prev)
        self.theta = theta * -pi


    def convert(self, pt):
        cos_t, sin_t = cos(self.theta), sin(self.theta)
        return Point(int(round(cos_t * pt.x - sin_t * pt.y)),
                     int(round(sin_t * pt.x + cos_t * pt.y)))


    def _copy(self, previous):
        return Rotate(self.theta, previous)



class Scale(XForm):
    """ Linear scaling """
    def __init__(self, scale, prev=None):
        XForm.__init__(self, prev)
        self.scale = scale


    def convert(self, pt):
        return Point(int(pt.x * self.scale), int(pt.y * self.scale))


    def _copy(self, previous):
        return Scale(self.scale, previous)



class FixY(XForm):
    """ Compensate for difference in origin between upverter and PIL """
    def __init__(self, ymax, prev=None):
        """ Will transform Points from bottom-left origin to top-left origin """
        XForm.__init__(self, prev)
        self.ymax = ymax


    def convert(self, pt):
        return Point(pt.x, self.ymax - pt.y)


    def _copy(self, previous):
        return FixY(self.ymax, previous)



class FlipY(XForm):
    """ Flips a point around the y-axis """
    def convert(self, pt):
        return Point(-pt.x, pt.y)


    def _copy(self, previous):
        return FlipY(previous)
