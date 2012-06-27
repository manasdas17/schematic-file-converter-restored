#!/usr/bin/env python2
""" The Specctra DSN Format Parser """

# upconvert.py - A universal hardware design file format converter using
# Format: upverter.com/resources/open-json-format/
# Development: github.com/upverter/schematic-file-converter
#
# Copyright 2011 Upverter, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from upconvert.core.design import Design
from upconvert.core.components import Component, Symbol, Body, Pin
from upconvert.core.component_instance import ComponentInstance, SymbolAttribute
from upconvert.core.net import Net, NetPoint, ConnectedComponent
from upconvert.core.shape import Circle, Line, Rectangle, Label, Polygon, Point
from upconvert.core.annotation import Annotation

from string import whitespace

from upconvert.parser import specctraobj 
import math

class Specctra(object):
    """ The Specctra DSN Format Parser """
    def __init__(self):
        self.design = None
        self.resolution = None
        self.nets = {}
        self.net_points = {}
        self._id = 10

    @staticmethod
    def auto_detect(filename):
        """ Return our confidence that the given file is an specctra schematic """
        with open(filename, 'r') as f:
            data = f.read(4096)
        confidence = 0
        if '(pcb ' in data or '(PCB ' in data:
            confidence += 0.75
        return confidence

    def parse(self, filename, library_filename=None):
        """ Parse a specctra file into a design """

        self.design = Design()

        with open(filename) as f:
            data = f.read()

        tree = DsnParser().parse(data)

        struct = self.walk(tree)
        self.resolution = struct.resolution
        self._convert(struct)

        return self.design

    def _convert(self, struct):
        self._convert_library(struct)
        self._convert_components(struct)
        self._convert_nets(struct)

    def _convert_library(self, struct):
        for image in struct.library.image:
            component = Component(image.image_id)
            self.design.add_component(image.image_id, component)
            sym = Symbol()
            body = Body()
            component.add_symbol(sym)
            sym.add_body(body)
            for pin in image.pin:
                body.add_pin(Pin(pin.pin_id, self.to_pixels(pin.vertex), self.to_pixels(pin.vertex)))
                for padstack in struct.library.padstack:
                    if padstack.padstack_id == pin.padstack_id:
                        shapes = [shape.shape for shape in padstack.shape]
                        for shape in self._convert_shapes(shapes, self.to_pixels(pin.vertex)):
                            body.add_shape(shape)
                        break
                            
            for outline in image.outline:
                for shape in self._convert_shapes([outline.shape]):
                    body.add_shape(shape)

    def _convert_components(self, struct):
        for component in struct.placement.component:
            library_id = component.image_id
            for place in component.place:
                # Outside PCB boundary
                if not place.vertex:
                    continue

                mirror = {90:270, 270:90}
                if place.side == 'back':
                    rotation = place.rotation
                else:
                    rotation = mirror.get(int(place.rotation), place.rotation)
                inst = ComponentInstance(place.component_id, library_id, 0)
                v = self.to_pixels(place.vertex)
                symbattr = SymbolAttribute(v[0], v[1], to_piradians(rotation))
                inst.add_symbol_attribute(symbattr) 
                self.design.add_component_instance(inst)

    def _get_point(self, net_id, point_id, x, y):
        if net_id not in self.nets:
            n = Net(net_id)
            self.design.add_net(n)
            self.nets[n.net_id] = n
        else:
            n = self.nets[net_id]

        key = (x, y)
        if key not in self.net_points:
            if not point_id:
                point_id = str(self._id)
                self._id += 1
            np = NetPoint(net_id + '-' + point_id, x, y)
            n.add_point(np)
            self.net_points[key] = np
        else:
            np = self.net_points[key]

        return np
 
    def _convert_wires(self, struct):
        if struct.wiring:
            for wire in struct.wiring.wire:
                lines = self._convert_shapes([wire.shape])
                for line in lines:
                    try:
                        np1 = self._get_point(wire.net.net_id, None, line.p1.x, line.p1.y)
                        np2 = self._get_point(wire.net.net_id, None, line.p2.x, line.p2.y)

                        np1.add_connected_point(np2.point_id)
                        np2.add_connected_point(np1.point_id)
                    except: pass

    def _convert_nets(self, struct):
        # FIXME polyline_path is not documented and no success with reverse engineering yet
        self._convert_wires(struct)

        if struct.network:
            for net in struct.network.net:
                if net.pins is None:
                    continue

                prev_point = None
                for pin_ref in net.pins.pin_reference:
                    # pin_ref like A1-"-" is valid (parsed to A1--)
                    component_id, pin_id = pin_ref[:pin_ref.index('-')], pin_ref[pin_ref.index('-') + 1:]  
                    point = self.get_component_pin(component_id, pin_id)
                    if point is None:
                        print 'Could not find net %s pin ref %s' % (net.net_id, pin_ref)
                        continue
                    cc = ConnectedComponent(component_id, pin_id)
                    np = self._get_point(net.net_id, pin_ref, point[0], point[1])
                    np.add_connected_component(cc)

                    if prev_point is not None:
                        # XXX if point is already connected assume wiring had routed network, don't do it here
                        if len(prev_point.connected_points) == 0:
                            prev_point.add_connected_point(np.point_id)
                        if len(np.connected_points) == 0:
                            np.add_connected_point(prev_point.point_id)

                    prev_point = np

    def get_component_pin(self, component_id, pin_id):
        for component_instance in self.design.component_instances:
            symbattr = component_instance.symbol_attributes[0]
            if component_instance.instance_id == component_id: 
                component = self.design.components.components[component_instance.library_id]
                for pin in component.symbols[0].bodies[0].pins:
                    if pin.pin_number == pin_id:
                        x, y = rotate((pin.p1.x, pin.p1.y), symbattr.rotation)
                        return (symbattr.x + x, symbattr.y + y)

    def _convert_path(self, aperture, points):
        result = []
        prev = None
        # Path has connected start and end points
        for point in points:
            if prev:
                result.append(Line(prev, point))
            prev = point
        return result

    def _convert_shapes(self, shapes, center = (0, 0)):
        result = []

        def from_center(point):
            return (point[0] + center[0], point[1] + center[1])

        for shape in shapes:
            if isinstance(shape, specctraobj.PolylinePath):
                points = [from_center(self.to_pixels(point)) for point in shape.vertex]
                result.extend(self._convert_path(self.to_pixels(shape.aperture_width), points))
            elif isinstance(shape, specctraobj.Path):
                points = [from_center(self.to_pixels(point)) for point in shape.vertex]
                result.extend(self._convert_path(self.to_pixels(shape.aperture_width), points + points[:1]))

            elif isinstance(shape, specctraobj.PolylinePath):
                points = [from_center(self.to_pixels(point)) for point in shape.vertex]
                prev = None
                for point in points:
                    if prev:
                        result.append(Line(prev, point))
                    prev = point

            elif isinstance(shape, specctraobj.Polygon):
                points = [from_center(self.to_pixels(point)) for point in shape.vertex]
                points = [Point(point[0], point[1]) for point in points]
                result.append(Polygon(points))

            elif isinstance(shape, specctraobj.Rectangle):
                x1, y1 = self.to_pixels(shape.vertex1)
                x2, y2 = self.to_pixels(shape.vertex2)
                width, height = abs(x1 - x2), abs(y1 - y2)
                x1, y1 = from_center((min(x1, x2), max(y1, y2)))

                result.append(Rectangle(x1, y1, width, height))
            elif isinstance(shape, specctraobj.Circle):
                point = from_center(self.to_pixels(shape.vertex))
                result.append(Circle(point[0], point[1], self.to_pixels(shape.diameter / 2.0)))
        return result

    def to_pixels(self, vertex):
        return self.resolution.to_pixels(vertex)

    def walk(self, elem):
        if isinstance(elem, list) and len(elem) > 0:
            elemx = [self.walk(x) for x in elem]
            func = specctraobj.lookup(elemx[0])
            if func:
                f = func()
                f.parse(elemx[1:])
                return f
            else:
#print 'Unhandled element', elemx[0]
                return elemx
        else:
            return elem

def to_piradians(degrees):
    # looks like specctra and upverter rotate in different directions
    return float(degrees) / 180.0

def rotate(point, piradians):
    """ Rotate point around (0, 0) """
    x, y = float(point[0]), float(point[1])
    # Somehow this must rotate in opposite direction than shape, why?
    radians = float(-piradians) * math.pi
    new_x = int(round(x * math.cos(radians) - y * math.sin(radians)))
    new_y = int(round(x * math.sin(radians) + y * math.cos(radians)))
    return (new_x, new_y)

class DsnParser:
    """ Parser for Specctra dialect of lisp """

    # Specctra parser configuration: Disables parentheses as delimiters for text strings.
    string_quote = ''
    # Specctra parser configuration: By default, blank spaces are an absolute delimiter. 
    space_in_quoted_tokens = False

    seperators = whitespace + '()'

    def __init__(self):
        self.pos = 0
        self.length = 0
        self.exp = ''

    def parse(self, exp):
        """ Parses s-expressions and returns them as Python lists """
        self.pos = 0
        self.length = len(exp)
        self.exp = exp
        return self._parse_exp(root=True)[0]

    def _maybe_eval(self, lst):
        """ File format specifies string quoting character:
        this eval configures parser so it can distinguish between
        quote character as atom and quoted string """

        if len(lst) > 1:
            if lst[0] == 'string_quote':
                self.string_quote = lst[1]
            elif lst[0] == 'space_in_quoted_tokens':
                self.space_in_quoted_tokens = lst[1].lower() == 'on'
        return lst

    def _parse_exp(self, root=False):
        """ Parses s-expressions and returns them as Python lists """

        lst = []
        buf = ''

        while self.pos < self.length:
            ch = self.exp[self.pos]
            self.pos += 1

            if ch not in self.seperators and ch != self.string_quote:
                buf += ch
            else:
                if buf and ch != self.string_quote:
                    lst.append(buf)
                    buf = ''

                if ch == '(':
                    lst.append(self._maybe_eval(self._parse_exp()))
                elif ch == ')':
                    return lst
                elif ch == self.string_quote:
                    buf += self._parse_string()

        if not root:
            raise SyntaxError('Closing ) not found')
        return lst

    def _parse_string(self):
        """ Reads string from expression according to current parser configuration """

        buf = ''

        while self.pos < self.length:
            ch = self.exp[self.pos]
            self.pos += 1

            if ch == self.string_quote:
                return buf
            elif ch in whitespace and not self.space_in_quoted_tokens:
                self.pos -= 1
                return buf
            else:
                buf += ch

        raise SyntaxError('Closing string quote %s not found' % (self.string_quote))
