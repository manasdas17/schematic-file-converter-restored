#!/usr/bin/env python2
""" The Fritzing Format Parser """

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

from upconvert.core.design import Design
from upconvert.core.components import Component, Symbol, Body, Pin
from upconvert.core.component_instance import ComponentInstance, SymbolAttribute
from upconvert.core.shape import Circle, Line, Polygon, Rectangle, BezierCurve
from upconvert.core.net import Net, NetPoint, ConnectedComponent

from upconvert.library.fritzing import lookup_part

from xml.etree.ElementTree import ElementTree

from os.path import basename, dirname, exists, join

import re, zipfile


class Fritzing(object):
    """ The Fritzing Format Parser

    Connection points in a fritzing file are identified by a 'module
    index' which references a component instance or a wire, and a
    'connector id' which references a specific pin. Together the
    (index, connid) tuple uniquely identifies a connection point.
    """

    def __init__(self):
        self.design = Design()

        # This maps fritzing connector keys to (x, y) coordinates
        self.points = {} # (index, connid) -> (x, y)

        # This maps fritzing component indices to ComponentInstances
        self.component_instances = {} # index -> ComponentInstance

        # Map connector keys to the list of connector keys they
        # are connected to.
        self.connects = {} # (index, connid) -> [(index, connid)]

        self.components = {} # idref -> ComponentParser

        self.fritzing_version = None
        self.fzz_zipfile = None # The ZipFile if we are parsing an fzz


    @staticmethod
    def auto_detect(filename):
        """ Return our confidence that the given file is an fritzing file """
        with open(filename, 'r') as f:
            data = f.read(4096)
        confidence = 0
        if 'fritzingVersion' in data:
            confidence += 0.9
        return confidence


    def parse(self, filename):
        """ Parse a Fritzing file into a design """

        tree = self.make_tree(filename)

        self.fritzing_version = tree.getroot().get('fritzingVersion', '0')

        for element in tree.findall('instances/instance'):
            self.parse_instance(element)

        for idref, cpt_parser in self.components.iteritems():
            self.design.add_component(idref, cpt_parser.component)

        for cptinst in self.component_instances.itervalues():
            self.design.add_component_instance(cptinst)

        for net in self.build_nets():
            self.design.add_net(net)

        return self.design


    def make_tree(self, filename):
        """
        Return an ElementTree for the given file name.
        """

        if filename.endswith('.fzz'):
            self.fzz_zipfile = zipfile.ZipFile(filename)
            fz_file = self.fzz_zipfile.open(basename(filename[:-1]))
        else:
            fz_file = filename

        return ElementTree(file=fz_file)

    def parse_instance(self, instance):
        """ Parse a Fritzing instance block """

        if instance.get('moduleIdRef') == 'WireModuleID':
            self.parse_wire(instance)
        else:
            self.parse_component_instance(instance)


    def parse_wire(self, inst):
        """ Parse a Fritzing wire instance """

        view = inst.find('views/schematicView')

        if view is None:
            return

        index = inst.get('modelIndex')
        geom = view.find('geometry')

        origin_x, origin_y = get_x(geom), get_y(geom)

        conn_keys = []

        for connect in view.findall('connectors/connector/connects/connect'):
            if connect.get('layer') == 'breadboardbreadboard':
                return

        for i, connector in enumerate(view.findall('connectors/connector'), 1):
            cid = connector.get('connectorId')
            self.points[index, cid] = (origin_x + get_x(geom, 'x%d' % i),
                                       origin_y + get_y(geom, 'y%d' % i))

            conn_keys.append((index, cid))

            self.connects[index, cid] = \
                [(c.get('modelIndex'), c.get('connectorId'))
                 for c in connector.findall('connects/connect')]

        # connect wire ends to each other
        if len(conn_keys) >= 2:
            self.connects[conn_keys[0]].append(conn_keys[1])
            self.connects[conn_keys[1]].append(conn_keys[0])


    def ensure_component(self, inst):
        """ If we have not already done so, create the Component the
        given Fritzing instance is an instance of. Return the
        Component, or None if we cannot load it"""

        idref = inst.get('moduleIdRef')

        if idref in self.components:
            return self.components[idref]

        fzp_path = inst.get('path')
        if not fzp_path:
            return None

        if exists(fzp_path):
            fzp_file = fzp_path
        else:
            fzp_file = self.lookup_fzz_file(fzp_path, 'part')

        if not fzp_file:
            fzp_file = lookup_part(fzp_path, self.fritzing_version)
            if fzp_file is not None:
                fzp_path = fzp_file

        if not fzp_file:
            return None

        parser = ComponentParser(idref)
        parser.parse_fzp(fzp_file)

        if parser.image is not None:
            svg_file = self.lookup_fzz_file(parser.image, 'svg.schematic')

            if svg_file is None:
                fzp_dir = dirname(fzp_path)
                parts_dir = dirname(fzp_dir)
                svg_path = join(parts_dir, 'svg', basename(fzp_dir),
                                parser.image)

                if exists(svg_path):
                    svg_file = svg_path

            if svg_file is not None:
                parser.parse_svg(svg_file)

        self.components[idref] = parser

        return parser


    def lookup_fzz_file(self, path, prefix):
        """ Find a file in our fzz archive, if any """

        if not self.fzz_zipfile:
            return None

        fzz_name = prefix + '.' + basename(path)

        try:
            self.fzz_zipfile.getinfo(fzz_name)
        except KeyError:
            return None
        else:
            return self.fzz_zipfile.open(fzz_name)


    def parse_component_instance(self, inst):
        """ Parse a Fritzing non-wire instance into a ComponentInstance """

        view = inst.find('views/schematicView')

        if view is None:
            return

        if view.get('layer') == 'breadboardbreadboard':
            return

        cpt = self.ensure_component(inst)

        if cpt is None:
            return

        index = inst.get('modelIndex')
        idref = inst.get('moduleIdRef')
        title = inst.find('title').text
        geom = view.find('geometry')
        xform = geom.find('transform')

        x, y = float(geom.get('x', 0)), float(geom.get('y', 0))

        if xform is None:
            rotation = 0.0
        else:
            matrix = tuple(int(float(xform.get(key, 0)))
                           for key in ('m11', 'm12', 'm21', 'm22'))
            x, y = rotate_component(cpt, matrix, x, y)
            rotation = MATRIX2ROTATION.get(matrix, 0.0)

        compinst = ComponentInstance(title, idref, 0)

        compinst.add_symbol_attribute(
            SymbolAttribute(make_x(x), make_y(y), rotation))

        self.component_instances[index] = compinst


    def build_nets(self):
        """ Build the nets from the connects, points, and instances """

        todo = set(self.connects) # set([(index, cid)])
        points = {} # (x, y) -> NetPoint
        nets = []

        def get_point(point):
            """ Return a new or existing NetPoint for an (x,y) point """
            if point not in points:
                points[point] = NetPoint('%da%d' % point, point[0], point[1])
            return points[point]

        def update_net(net, main_key):
            """ Update a net with a new set of connects """

            todo.discard(main_key)

            main_point = get_point(self.points[main_key])
            net.add_point(main_point)

            remaining = []

            for conn_key in self.connects[main_key]:
                if conn_key in todo:
                    remaining.append(conn_key)

                if conn_key in self.points:
                    connect(net, main_point, get_point(self.points[conn_key]))
                elif conn_key[0] in self.component_instances:
                    inst = self.component_instances[conn_key[0]]
                    cpt_parser = self.components[inst.library_id]
                    cpt_parser.connect_point(conn_key[1], inst, main_point)

            return remaining

        while todo:
            net = Net(str(len(nets)))
            nets.append(net)
            remaining = [todo.pop()]

            while remaining:
                remaining.extend(update_net(net, remaining.pop(0)))

        return nets


def connect(net, p1, p2):
    """ Connect two points in a net """

    if p1 is p2:
        return

    net.add_point(p1)
    net.add_point(p2)

    if p2.point_id not in p1.connected_points:
        p1.connected_points.append(p2.point_id)
    if p1.point_id not in p2.connected_points:
        p2.connected_points.append(p1.point_id)


# map fritzing rotation matrices to pi radians
MATRIX2ROTATION = {(1, 0, 0, 1): 0,
                   (0, 1, -1, 0): 0.5,
                   (-1, 0, 0, -1): 1,
                   (0, -1, 1, 0): 1.5}


class ComponentParser(object):
    """I parse components from Fritzing libraries."""

    # The svg files in fritzing libraries are specified in pixels that
    # are 72dpi. The schematics are in 90dpi.
    svg_mult = 90.0 / 72.0

    def __init__(self, idref):
        self.component = Component(idref)
        self.next_pin_number = 0
        self.cid2termid = {} # connid -> termid
        self.termid2pin = {} # termid -> Pin
        self.terminals = set()
        self.width = 0.0
        self.height = 0.0


    def parse_fzp(self, fzp_file):
        """ Parse the Fritzing component file """

        tree = ElementTree(file=fzp_file)

        try:
            prefix = tree.find('label').text
        except AttributeError:
            pass
        else:
            self.component.add_attribute('_prefix', prefix)

        symbol = Symbol()
        self.component.add_symbol(symbol)

        self.body = Body()
        symbol.add_body(self.body)

        self.cid2termid.update(self.parse_terminals(tree))
        self.terminals.update(self.cid2termid.values())

        layers = tree.find('views/schematicView/layers')
        if layers is None:
            self.image = None
        else:
            self.image = layers.get('image')


    def connect_point(self, cid, inst, point):
        """ Given a connector id, instance id, and a NetPoint,
        add the appropriate ConnectedComponent to the point """

        termid = self.cid2termid.get(cid)
        pin = self.termid2pin.get(termid)

        if pin is not None:
            ccpt = ConnectedComponent(inst.instance_id, pin.pin_number)
            point.add_connected_component(ccpt)


    def get_next_pin_number(self):
        """ Return the next pin number """

        nextpn = self.next_pin_number
        self.next_pin_number += 1
        return str(nextpn)


    def parse_terminals(self, tree):
        """ Return a dictionary mapping connector id's to terminal id's """

        cid2termid = {}

        for conn in tree.findall('connectors/connector'):
            plug = conn.find('views/schematicView/p')
            if plug is None:
                continue

            termid = plug.get('terminalId')
            if termid is None:
                termid = plug.get('svgId')

            if termid is not None:
                cid2termid[conn.get('id')] = termid

        return cid2termid


    def parse_svg(self, svg_file):
        """ Parse the shapes and pins from an svg file """

        tree = ElementTree(file=svg_file)
        viewbox = tree.getroot().get('viewBox')

        if viewbox != None:
            self.width, self.height = [float(v) for v in viewbox.split()[-2:]]
            self.width *= self.svg_mult
            self.height *= self.svg_mult

        _iter = tree.getroot().getiterator()
        for element in _iter:
            for shape in self.parse_shapes(element):
                self.body.add_shape(shape)
                if element.get('id') in self.terminals:
                    pin = get_pin(shape)
                    if pin is not None:
                        pin.pin_number = self.get_next_pin_number()
                        self.termid2pin[element.get('id')] = pin
                        self.body.add_pin(pin)


    def parse_shapes(self, element):
        """ Parse a list of shapes from an svg element """

        tag = element.tag.rsplit('}', -1)[-1]

        if tag == 'circle':
            return self.parse_circle(element)
        elif tag == 'rect':
            return self.parse_rect(element)
        elif tag == 'line':
            return self.parse_line(element)
        elif tag == 'path':
            return self.parse_path(element)
        elif tag == 'polygon':
            return self.parse_polygon(element)
        elif tag == 'polyline':
            return self.parse_polyline(element)
        else:
            return []

    def parse_rect(self, rect):
        """ Parse a rect element """

        x, y = (get_x(rect, mult=self.svg_mult),
                get_y(rect, mult=self.svg_mult))
        width, height = (get_length(rect, 'width', self.svg_mult),
                         get_length(rect, 'height', self.svg_mult))
        return [Rectangle(x, y, width, height)]


    def parse_line(self, rect):
        """ Parse a line element """

        return [Line((get_x(rect, 'x1', self.svg_mult),
                      get_y(rect, 'y1', self.svg_mult)),
                     (get_x(rect, 'x2', self.svg_mult),
                      get_y(rect, 'y2', self.svg_mult)))]


    def parse_path(self, path):
        """ Parse a path element """

        return PathParser(path).parse()


    def parse_polygon(self, poly):
        """ Parse a polygon element """

        shape = Polygon()

        for point in poly.get('points', '').split():
            if point:
                x, y = point.split(',')
                shape.add_point(make_x(x, self.svg_mult),
                                make_y(y, self.svg_mult))

        if shape.points:
            shape.add_point(shape.points[0].x, shape.points[0].y)

        return [shape]


    def parse_polyline(self, poly):
        """ Parse a polyline element """

        shapes = []
        last_point = None

        for point in poly.get('points', '').split():
            if point:
                x, y = point.split(',')
                point = (make_x(x, self.svg_mult), make_y(y, self.svg_mult))
                if last_point is not None:
                    shapes.append(Line(last_point, point))
                last_point = point

        return shapes


    def parse_circle(self, circle):
        """ Parse a circle element """

        return [Circle(get_x(circle, 'cx', self.svg_mult),
                       get_y(circle, 'cy', self.svg_mult),
                       get_length(circle, 'r', self.svg_mult))]


def get_pin(shape):
    """ Return a Pin for the given shape, or None """

    if shape.type == 'rectangle':
        x = shape.x + shape.width / 2
        y = shape.y + shape.height / 2
    elif shape.type == 'circle':
        x, y = shape.x, shape.y
    else:
        return None

    return Pin('', (x, y), (x, y))


def rotate_component(cpt, matrix, x, y):
    """ Given a ComponentParser, a rotation matrix, and x/y points
    referencing the upper left edge of the Fritzing component (in
    Fritzing space), return a new pair of x/y points referencing the
    component after it is rotated about its center. Fritzing rotations
    are applied to the center of the component bounding boxes."""

    # upper left corner when origin is at center
    x1, y1 = -cpt.width / 2, -cpt.height / 2

    # rotate upper left corner
    x2, y2 = (matrix[0] * x1 + matrix[2] * y1,
              matrix[1] * x1 + matrix[3] * y1)

    # translate original coordinate
    return (x + (x2 - x1), y + (y2 - y1))


class PathParser(object):
    """ A parser for svg path elements. """

    num_re = re.compile(r'\s*(-?\d+(?:\.\d+)?)\s*,?\s*')

    svg_mult = ComponentParser.svg_mult

    def __init__(self, path):
        self.path = path
        self.shapes = []
        self.cur_point = (0, 0) # (x, y) of current point
        self.start_point = (0, 0) # (x, y) of start of current subpath
        self.prev_cmd = '' # previous path command letter
        self.prev_ctl = None # previous control point

    def parse(self):
        """ Parse the path element and return a list of shapes. """

        data = self.path.get('d', '').strip()

        while data:
            cmd = data[0].lower()
            is_relative = data[0] == cmd
            handler = getattr(self, 'parse_' + cmd, None)
            if handler is None:
                break
            else:
                data = handler(data[1:], is_relative)
                self.prev_cmd = cmd

        def is_empty_line(shape):
            """ Return True if the shape is an empty line """
            return shape.type == 'line' and shape.p1 == shape.p2

        return [s for s in self.shapes if not is_empty_line(s)]

    def parse_nums(self, data):
        """ Parse a series of numbers in an svg path. Return the
        list of numbers and the remaining portion of the path. """

        nums = []

        while data:
            match = self.num_re.match(data)

            if match is None:
                break
            else:
                nums.append(float(match.group(1)))
                data = data[len(match.group(0)):]

        return nums, data

    def parse_points(self, data):
        """ Parse a series of points in an svg path. Return the
        list of points and the remaining portion of the path """

        nums, data = self.parse_nums(data)

        return zip(nums[::2], nums[1::2]), data

    def get_path_point(self, base_point, is_relative):
        """ Return a path point given a base point and whether we
        are in relative path mode. """

        if is_relative:
            return (base_point[0] + self.cur_point[0],
                    base_point[1] + self.cur_point[1])
        else:
            return base_point

    def parse_m(self, data, is_relative):
        """ Parse an M or m (moveto) segment. """

        points, data = self.parse_points(data)

        for i, point in enumerate(points):
            point = self.get_path_point(point, is_relative)
            if i == 0:
                self.start_point = self.cur_point = point
            else: # subsequent moves are lineto's
                self.shapes.append(
                    Line(make_point(self.cur_point, self.svg_mult),
                         make_point(point, self.svg_mult)))
                self.cur_point = point

        return data


    def parse_z(self, data, is_relative):
        """ Parse a Z or z (closepath) segment. """

        self.shapes.append(
            Line(make_point(self.cur_point, self.svg_mult),
                 make_point(self.start_point, self.svg_mult)))
        self.cur_point = self.start_point

        return data


    def parse_l(self, data, is_relative):
        """ Parse an L or l (lineto) segment. """

        points, data = self.parse_points(data)

        for point in points:
            point = self.get_path_point(point, is_relative)
            self.shapes.append(
                Line(make_point(self.cur_point, self.svg_mult),
                     make_point(point, self.svg_mult)))
            self.cur_point = point

        return data


    def parse_h(self, data, is_relative):
        """ Parse an H or h (horizontal line) segment. """

        nums, data = self.parse_nums(data)

        for num in nums:
            point = (num, 0 if is_relative else self.cur_point[1])
            point = self.get_path_point(point, is_relative)
            self.shapes.append(
                Line(make_point(self.cur_point, self.svg_mult),
                     make_point(point, self.svg_mult)))
            self.cur_point = point

        return data


    def parse_v(self, data, is_relative):
        """ Parse a V or v (vertical line) segment. """

        nums, data = self.parse_nums(data)

        for num in nums:
            point = (0 if is_relative else self.cur_point[0], num)
            point = self.get_path_point(point, is_relative)
            self.shapes.append(
                Line(make_point(self.cur_point, self.svg_mult),
                     make_point(point, self.svg_mult)))
            self.cur_point = point

        return data


    def parse_c(self, data, is_relative):
        """ Parse a C or c (cubic bezier) segment. """

        points, data = self.parse_points(data)

        while points:
            start = self.cur_point

            (ctl1, ctl2, end), points = points[:3], points[3:]

            self.cur_point = ctl1 = self.get_path_point(ctl1, is_relative)
            self.cur_point = ctl2 = self.get_path_point(ctl2, is_relative)
            self.cur_point = end = self.get_path_point(end, is_relative)

            self.prev_ctl = ctl2

            self.shapes.append(
                BezierCurve(make_point(ctl1, self.svg_mult),
                            make_point(ctl2, self.svg_mult),
                            make_point(start, self.svg_mult),
                            make_point(end, self.svg_mult)))

        return data


    def parse_s(self, data, is_relative):
        """ Parse an S or s (cubic shorthand bezier) segment. """

        points, data = self.parse_points(data)

        while points:
            start = self.cur_point

            (ctl2, end), points = points[:2], points[2:]

            self.cur_point = ctl2 = self.get_path_point(ctl2, is_relative)
            self.cur_point = end = self.get_path_point(end, is_relative)

            if self.prev_cmd not in 'cs' or not self.prev_ctl:
                ctl1 = start
            else:
                ctl1 = (start[0] - (self.prev_ctl[0] - start[0]),
                        start[1] - (self.prev_ctl[1] - start[1]))

            self.prev_ctl = ctl2

            self.shapes.append(
                BezierCurve(make_point(ctl1, self.svg_mult),
                            make_point(ctl2, self.svg_mult),
                            make_point(start, self.svg_mult),
                            make_point(end, self.svg_mult)))

        return data


    def parse_q(self, data, is_relative):
        """ Parse a Q or q (quadratic bezier) segment. """

        points, data = self.parse_points(data)

        while points:
            start = self.cur_point

            (ctl, end), points = points[:2], points[2:]

            self.cur_point = ctl = self.get_path_point(ctl, is_relative)
            self.cur_point = end = self.get_path_point(end, is_relative)

            self.prev_ctl = ctl

            ctl1 = (start[0] + (2.0 / 3.0 * (ctl[0] - start[0])),
                    start[1] + (2.0 / 3.0 * (ctl[1] - start[1])))

            ctl2 = (end[0] + (2.0 / 3.0 * (ctl[0] - end[0])),
                    end[1] + (2.0 / 3.0 * (ctl[1] - end[1])))

            self.shapes.append(
                BezierCurve(make_point(ctl1, self.svg_mult),
                            make_point(ctl2, self.svg_mult),
                            make_point(start, self.svg_mult),
                            make_point(end, self.svg_mult)))

        return data


    def parse_t(self, data, is_relative):
        """ Parse a T or t (quadratic shorthand bezier) segment. """

        points, data = self.parse_points(data)

        while points:
            start = self.cur_point

            end, points = points[0], points[1:]

            self.cur_point = end = self.get_path_point(end, is_relative)

            if self.prev_cmd not in 'qt' or not self.prev_ctl:
                ctl = start
            else:
                ctl = (start[0] - (self.prev_ctl[0] - start[0]),
                       start[1] - (self.prev_ctl[1] - start[1]))

            self.prev_ctl = ctl

            ctl1 = (start[0] + (2.0 / 3.0 * (ctl[0] - start[0])),
                    start[1] + (2.0 / 3.0 * (ctl[1] - start[1])))

            ctl2 = (end[0] + (2.0 / 3.0 * (ctl[0] - end[0])),
                    end[1] + (2.0 / 3.0 * (ctl[1] - end[1])))

            self.shapes.append(
                BezierCurve(make_point(ctl1, self.svg_mult),
                            make_point(ctl2, self.svg_mult),
                            make_point(start, self.svg_mult),
                            make_point(end, self.svg_mult)))

        return data


def make_x(x, mult=1.0):
    """ Make an openjson x coordinate from a fritzing x coordinate """
    return int(round(float(x) * mult))

def make_y(y, mult=1.0):
    """ Make an openjson y coordinate from a fritzing y coordinate """
    return -int(round(float(y) * mult))

def make_length(value, mult=1.0):
    """ Make a length measurement from a fritzing measurement """
    return int(round(float(value) * mult))

def make_point(point, mult=1.0):
    """ Make a point from a fritzing point """
    return (make_x(point[0], mult=mult), make_y(point[1], mult=mult))

def get_x(element, name='x', mult=1.0):
    """ Get an openjson x coordinate from a fritzing element """
    return make_x(element.get(name, 0), mult)

def get_y(element, name='y', mult=1.0):
    """ Get an openjson y coordinate from a fritzing element """
    return make_y(element.get(name, 0), mult)

def get_length(element, name, mult=1.0):
    """ Get an openjson length from a fritzing element """
    return make_length(element.get(name, 0), mult)
