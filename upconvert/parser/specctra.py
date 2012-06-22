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
        self.px_mult = None

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
        self._set_mult(struct.resolution)
        self._convert(struct)

        return self.design

    def _set_mult(self, res):
        """ Set multiplier for converting file units to internal units """
        dpi = 96.0 # * 2.0
        if res.unit == 'inch':
            self.px_mult = dpi / 1.0
        elif res.unit == 'mil':
            self.px_mult = dpi / 1000.0
        elif res.unit == 'cm':
            self.px_mult = dpi / 2.54
        elif res.unit == 'mm':
            self.px_mult =  dpi / 2.54 / 10.0
        elif res.unit == 'um':
            self.px_mult =  dpi / 2.54 / 1000.0

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
        x1, y1 = self.to_pixels(struct.structure.boundary.rectangle.vertex1)
        x2, y2 = self.to_pixels(struct.structure.boundary.rectangle.vertex2)
        x0 = abs(min(x1, x2))
        y0 = abs(min(y1, y2))

        for component in struct.placement.component:
            library_id = component.image_id
            for place in component.place:
                # Outside OCB boundary
                if not place.vertex:
                    continue

                inst = ComponentInstance(place.component_id, library_id, 0)
                v = self.to_pixels(place.vertex)
                symbattr = SymbolAttribute(x0 + v[0], y0 + v[1], to_piradians(place.rotation))
                inst.add_symbol_attribute(symbattr) 
                self.design.add_component_instance(inst)
 
    def _convert_nets(self, struct):
        for net in struct.network.net:
            n = Net(net.net_id)
            if net.pins is not None:
                pin_reference = net.pins.pin_reference
                
                prev_point = None
                for pin_ref in pin_reference:
                    # pin_ref like A1-"-" is valid (parsed to A1--)
                    component_id, pin_id = pin_ref[:pin_ref.index('-')], pin_ref[pin_ref.index('-') + 1:]  
                    point = self.get_component_pin(component_id, pin_id)
                    if point is None:
                        print 'Could not find net %s pin ref %s' % (n.net_id, pin_ref)
                        continue
                    cc = ConnectedComponent(component_id, pin_id)
                    np = NetPoint('%s-%s' % (n.net_id, pin_ref), point[0], point[1])
                    np.add_connected_component(cc)
                    n.add_point(np)

                    if prev_point is not None:
                        prev_point.add_connected_point(np.point_id)
                        np.add_connected_point(prev_point.point_id)
                    prev_point = np

            self.design.add_net(n)

    def get_component_pin(self, component_id, pin_id):
        for component_instance in self.design.component_instances:
            symbattr = component_instance.symbol_attributes[0]
            if component_instance.instance_id == component_id: 
                component = self.design.components.components[component_instance.library_id]
                for pin in component.symbols[0].bodies[0].pins:
                    if pin.pin_number == pin_id:
                        x, y = rotate((pin.p1.x, pin.p1.y), symbattr.rotation)
                        return (symbattr.x + x, symbattr.y + y)

    def _convert_shapes(self, shapes, center = (0, 0)):
        result = []

        def from_center(point):
            return (point[0] + center[0], point[1] + center[1])

        for shape in shapes:
            if isinstance(shape, specctraobj.Path):
                prev = from_center(self.to_pixels(shape.vertex[0]))
                first = prev
                for point in shape.vertex[1:]:
                    point = from_center(self.to_pixels(point))
                    result.append(Line(prev, point))
                    prev = point
                result.append(Line(point, first))

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
        if isinstance(vertex, tuple):
            return (int(round(float(vertex[0]) * self.px_mult)), int(round(float(vertex[1]) * self.px_mult)))
        return int(round(float(vertex) * self.px_mult))

    def walk(self, elem):
        if isinstance(elem, list) and len(elem) > 0:
            elemx = [self.walk(x) for x in elem]
            func = specctraobj.lookup(elemx[0])
            if func:
                return func(elemx[1:])
            else:
                return elemx
        else:
            return elem

def to_piradians(degrees):
    # looks like specctra and upverter rotate in different directions
    return float(-degrees) / 180.0

def rotate(point, piradians):
    """ Rotate point around (0, 0) """
    x, y = float(point[0]), float(point[1])
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
