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

from core.design import Design
from core.components import Component, Symbol, Body, Pin
from core.component_instance import ComponentInstance, SymbolAttribute
from core.shape import Circle, Line, Polygon, Rectangle
from core.net import Net, NetPoint, ConnectedComponent

from library.fritzing import lookup_part

from xml.etree.ElementTree import ElementTree

from os.path import basename, dirname, exists, join


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


    def parse(self, filename):
        """ Parse a Fritzing file into a design """

        tree = ElementTree(file=filename)

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
        self.connects[conn_keys[0]].append(conn_keys[1])
        self.connects[conn_keys[1]].append(conn_keys[0])


    def ensure_component(self, inst):
        """ If we have not already done so, create the Component the
        given Fritzing instance is an instance of. Return the
        Component, or None if we cannot load it"""

        idref = inst.get('moduleIdRef')

        if idref in self.components:
            return self.components[idref]

        path = inst.get('path')
        if not path:
            return None

        if not exists(path):
            path = lookup_part(path, self.fritzing_version)

        if not path or not exists(path):
            return None

        parser = ComponentParser(idref, path)
        self.components[idref] = parser
        parser.parse()
        return parser


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
            matrix = tuple(int(xform.get(key, 0))
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

    def __init__(self, idref, path):
        self.component = Component(idref)
        self.next_pin_number = 0
        self.cid2termid = {} # connid -> termid
        self.termid2pin = {} # termid -> Pin
        self.terminals = set()
        self.path = path
        self.width = 0.0
        self.height = 0.0

    def parse(self):
        """ Parse the Fritzing component """

        tree = ElementTree(file=self.path)

        self.component.add_attribute('_prefix', tree.find('label').text)

        symbol = Symbol()
        self.component.add_symbol(symbol)

        body = Body()
        symbol.add_body(body)

        self.cid2termid.update(self.parse_terminals(tree))
        self.terminals.update(self.cid2termid.values())

        self.parse_svg(body, tree, self.path)

        return self.component


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


    def parse_svg(self, body, tree, fzp_path):
        """ Parse the shapes and pins from an svg file """

        layers = tree.find('views/schematicView/layers')
        if layers is None:
            return

        image = layers.get('image')
        if image is None:
            return

        fzp_dir = dirname(fzp_path)
        parts_dir = dirname(fzp_dir)
        svg_path = join(parts_dir, 'svg', basename(fzp_dir), image)

        if not exists(svg_path):
            return

        tree = ElementTree(file=svg_path)

        viewbox = tree.getroot().get('viewBox')
        self.width, self.height = [float(v) for v in viewbox.split()[-2:]]

        for element in tree.getroot().iter():
            for shape in self.parse_shapes(element):
                body.add_shape(shape)
                if element.get('id') in self.terminals:
                    pin = get_pin(shape)
                    if pin is not None:
                        pin.pin_number = self.get_next_pin_number()
                        self.termid2pin[element.get('id')] = pin
                        body.add_pin(pin)


    def parse_shapes(self, element):
        """ Parse a list of shapes from an svg element """

        tag = element.tag.rsplit('}', -1)[-1]

        if tag == 'circle':
            return self.parse_circle(element)
        elif tag == 'rect':
            return self.parse_rect(element)
        elif tag == 'line':
            return self.parse_line(element)
        elif tag == 'polygon':
            return self.parse_polygon(element)
        elif tag == 'polyline':
            return self.parse_polyline(element)
        else:
            return []

    def parse_rect(self, rect):
        """ Parse a rect element """

        x, y = get_x(rect), get_y(rect)
        width, height = get_length(rect, 'width'), get_length(rect, 'height')
        return [Rectangle(x, y, width, height)]


    def parse_line(self, rect):
        """ Parse a line element """

        return [Line((get_x(rect, 'x1'), get_y(rect, 'y1')),
                     (get_x(rect, 'x2'), get_y(rect, 'y2')))]


    def parse_polygon(self, poly):
        """ Parse a polygon element """

        shape = Polygon()

        for point in poly.get('points', '').split():
            if point:
                x, y = point.split(',')
                shape.add_point(make_x(x), make_y(y))

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
                point = (make_x(x), make_y(y))
                if last_point is not None:
                    shapes.append(Line(last_point, point))
                last_point = point

        return shapes


    def parse_circle(self, circle):
        """ Parse a circle element """

        return [Circle(get_x(circle, 'cx'),
                       get_y(circle, 'cy'),
                       get_length(circle, 'r'))]


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


def make_x(x):
    """ Make an openjson x coordinate from a fritzing x coordinate """
    return int(round(float(x)))

def make_y(y):
    """ Make an openjson y coordinate from a fritzing y coordinate """
    return -int(round(float(y)))

def make_length(value):
    """ Make a length measurement from a fritzing measurement """
    return int(round(float(value)))

def get_x(element, name='x', default=0):
    """ Get an openjson x coordinate from a fritzing element """
    return make_x(element.get(name, default))

def get_y(element, name='y', default=0):
    """ Get an openjson y coordinate from a fritzing element """
    return make_y(element.get(name, default))

def get_length(element, name, default=0):
    """ Get an openjson length from a fritzing element """
    return make_length(element.get(name, default))
