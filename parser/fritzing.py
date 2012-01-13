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
from core.net import NetPoint

from library.fritzing import lookup_part

from xml.etree.ElementTree import ElementTree

from os.path import basename, dirname, exists, join


class Fritzing(object):
    """ The Fritzing Format Parser """

    def __init__(self):
        self.design = Design()
        self.points = {} # index.connectorid -> NetPoint
        self.component_instances = {} # index -> ComponentInstance
        self.components = {} # idref -> Component


    def parse(self, filename):
        """ Parse a Fritzing file into a design """

        tree = ElementTree(file=filename)

        self.fritzing_version = tree.getroot().get('fritzingVersion', '0')

        for element in tree.findall('instances/instance'):
            self.parse_instance(element)

        for idref, cpt in self.components.iteritems():
            self.design.add_component(idref, cpt)

        for cptinst in self.component_instances.itervalues():
            self.design.add_component_instance(cptinst)

        return self.design


    def parse_instance(self, instance):
        """ Parse a Fritzing instance block """

        if instance.get('moduleIdRef') == 'WireModuleID':
            self.parse_wire(instance)
        else:
            self.parse_component_instance(instance)


    def parse_wire(self, inst):
        """ Parse a Fritzing wire instance into two NetPoints """

        view = inst.find('views/schematicView')

        if view is None:
            return

        index = inst.get('modelIndex')
        geom = view.find('geometry')
        connectors = view.findall('connectors/connector')

        pid1 = index + '.' + connectors[0].get('connectorId')
        self.points[pid1] = NetPoint(pid1, get_x(geom), get_y(geom))

        pid2 = index + '.' + connectors[1].get('connectorId')
        self.points[pid2] = NetPoint(pid2, get_x(geom, 'x2'), get_y(geom, 'y2'))


    def ensure_component(self, inst):
        """ If we have not already done so, create the Component the
        given Fritzing instance is an instance of. Return the Component,
        or None if we cannot load it """

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

        self.components[idref] = ComponentParser(idref, path).component

        return self.components[idref]


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

        if xform is None:
            rotation = 0.0
        else:
            rotation = MATRIX2ROTATION.get(
                tuple(int(xform.get(key, 0))
                      for key in ('m11', 'm12', 'm21', 'm22')), 0.0)

        compinst = ComponentInstance(title, idref, 0)

        compinst.add_symbol_attribute(
            SymbolAttribute(get_x(geom), get_y(geom), rotation))

        self.component_instances[index] = compinst


# map fritzing rotation matrices to pi radians
MATRIX2ROTATION = {(1, 0, 0, 1): 0,
                   (0, 1, -1, 0): 0.5,
                   (-1, 0, 0, -1): 1,
                   (0, -1, 1, 0): 1.5}


class ComponentParser(object):
    """I parse components from Fritzing libraries."""

    def __init__(self, idref, path):
        self.next_pin_number = 0

        tree = ElementTree(file=path)

        self.component = Component(idref)
        self.component.add_attribute('_prefix', tree.find('label').text)

        symbol = Symbol()
        self.component.add_symbol(symbol)

        self.body = Body()
        symbol.add_body(self.body)

        self.terminals = self.parse_terminals(tree)
        self.parse_svg(tree, path)


    def get_next_pin_number(self):
        """ Return the next pin number """

        nextpn = self.next_pin_number
        self.next_pin_number += 1
        return str(nextpn)


    def parse_terminals(self, tree):
        """ Return a dictionary mapping svg id's to connector ids """

        terminals = {}

        for conn in tree.findall('connectors/connector'):
            plug = conn.find('views/schematicView/p')
            if plug is None:
                continue

            cid = plug.get('terminalId')
            if cid is None:
                cid = plug.get('svgId')

            if cid is not None:
                terminals[cid] = conn.get('id')

        return terminals


    def parse_svg(self, tree, fzp_path):
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

        for element in tree.getroot().iter():
            tag = element.tag.rsplit('}', -1)[-1]

            if tag == 'circle':
                shape = self.parse_circle(element)
            elif tag == 'rect':
                shape = self.parse_rect(element)
            elif tag == 'line':
                shape = self.parse_line(element)
            elif tag == 'polygon':
                shape = self.parse_polygon(element)
            elif tag == 'polyline':
                shape = self.parse_polyline(element)
            else:
                shape = None

            if shape is not None:
                self.body.add_shape(shape)
                pin = self.get_pin(shape, element)
                if pin is not None:
                    self.body.add_pin(pin)

        return self.body


    def parse_rect(self, rect):
        """ Parse a rect element """

        x, y = get_x(rect), get_y(rect)
        width, height = get_length(rect, 'width'), get_length(rect, 'height')
        return Rectangle(x, y - height, width, height)


    def parse_line(self, rect):
        """ Parse a line element """

        return Line((get_x(rect, 'x1'), get_y(rect, 'y1')),
                    (get_x(rect, 'x2'), get_y(rect, 'y2')))


    def parse_polygon(self, poly):
        """ Parse a polygon element """

        shape = Polygon()

        for point in poly.get('points', '').split():
            if point:
                x, y = point.split(',')
                shape.add_point(make_x(x), make_y(y))

        if shape.points:
            shape.add_point(shape.points[0].x, shape.points[0].y)

        return shape


    def parse_polyline(self, poly):
        """ Parse a polyline element """

        shape = Polygon()

        for point in poly.get('points', '').split():
            if point:
                x, y = point.split(',')
                shape.add_point(make_x(x), make_y(y))

        return shape


    def parse_circle(self, circle):
        """ Parse a circle element """

        return Circle(get_x(circle, 'cx'),
                      get_y(circle, 'cy'),
                      get_length(circle, 'r'))


    def get_pin(self, shape, element):
        """ Return a Pin for the given shape and element, or None """

        if element.get('id') not in self.terminals:
            return None

        if shape.type == 'rectangle':
            x = shape.x + shape.width / 2
            y = shape.y + shape.height / 2
        elif shape.type == 'circle':
            x, y = shape.x, shape.y
        else:
            return None

        return Pin(self.get_next_pin_number(), (x, y), (x, y))


MULT = 10

def make_x(x):
    """ Make an openjson x coordinate from a fritzing x coordinate """
    return int(float(x) * MULT)

def make_y(y):
    """ Make an openjson y coordinate from a fritzing y coordinate """
    return -int(float(y) * MULT)

make_length = make_x

def get_x(element, name='x', default=0):
    """ Get an openjson x coordinate from a fritzing element """
    return make_x(element.get(name, default))

def get_y(element, name='y', default=0):
    """ Get an openjson y coordinate from a fritzing element """
    return make_y(element.get(name, default))

def get_length(element, name, default=0):
    """ Get an openjson length from a fritzing element """
    return make_length(element.get(name, default))
