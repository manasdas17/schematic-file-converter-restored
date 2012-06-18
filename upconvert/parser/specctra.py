#!/usr/bin/env python2
""" The Specctra DSN Format Parser """

# Specification of file format can be found here:
# http://tech.groups.yahoo.com/group/kicad-users/files/ file "specctra.pdf"

from upconvert.core.design import Design
from upconvert.core.components import Component, Symbol, Body, Pin
from upconvert.core.component_instance import ComponentInstance, SymbolAttribute
from upconvert.core.net import Net, NetPoint, ConnectedComponent
from upconvert.core.shape import Arc, Circle, Line, Rectangle, Label
from upconvert.core.annotation import Annotation

from collections import defaultdict
from os.path import exists, splitext
from string import whitespace

import dsn

class Specctra(object):
    """ The Specctra DSN Format Parser """
    def __init__(self):
        self.design = None

    @staticmethod
    def auto_detect(filename):
        with open(filename, 'r') as f:
            data = f.read(4096)
        confidence = 0
        if '(pcb ' in data or '(PCB ' in data:
            confidence += 0.75
        return confidence


    def parse(self, filename, library_filename=None):
        self.design = Design()

        with open(filename) as f:
            data = f.read()

        tree = DsnParser().parse(data)

        struct = self.walk(tree)
        self.convert(struct)

        return self.design

    def convert(self, struct):
        x1, y1 = self.to_pixels(struct.structure.boundary.rectangle.vertex1)
        x2, y2 = self.to_pixels(struct.structure.boundary.rectangle.vertex2)
        x0 = abs(min(x1, x2))
        y0 = abs(min(y1, y2))

        for component in struct.placement.component:
            library_id = component.image_id
            for place in component.place:
                # Outside OCB boundary
                if not place.vertex: continue

                inst = ComponentInstance(place.component_id, library_id, 0)
                symbattr = SymbolAttribute(x0 + place.vertex[0], y0 + place.vertex[1], place.rotation)
                inst.add_symbol_attribute(symbattr) 
                self.design.add_component_instance(inst)

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
                        for shape in self.convert_shapes(shapes, self.to_pixels(pin.vertex)):
                            body.add_shape(shape)
                        break
                            
            for outline in image.outline:
                for shape in self.convert_shapes([outline.shape]):
                    body.add_shape(shape)

    def convert_shapes(self, shapes, center = (0, 0)):
        result = []

        for shape in shapes:
            if isinstance(shape, dsn.Path):
                prev = self.to_pixels(shape.vertex[0])
                prev = (prev[0] + center[0], prev[1] + center[1])
                first = prev
                for point in shape.vertex[1:]:
                    point = self.to_pixels(point)
                    point = (point[0] + center[0], point[1] + center[1])
                    result.append(Line(prev, point))
                    prev = point
                result.append(Line(point, first))

            elif isinstance(shape, dsn.Rectangle):
                x1, y1 = self.to_pixels(shape.vertex1)
                x2, y2 = self.to_pixels(shape.vertex2)
                width, height = abs(x1 - x2), abs(y1 - y2)
                x1 = min(x1, x2) + center[0]
                y1 = max(y1, y2) + center[1]

                result.append(Rectangle(x1, y1, width, height))
            elif isinstance(shape, dsn.Circle):
                x, y = self.to_pixels(shape.vertex)
                x += center[0]
                y += center[1]
                result.append(Circle(x, y, self.to_pixels(shape.diameter / 2.0)))
        return result

    def to_pixels(self, vertex):
        #MULT = 90.0 / 1000.0 # mils to 90 dpi
        # (resolution mil 10)
        MULT = 90.0 / 100.0 # mils to 90 dpi
        if isinstance(vertex, tuple):
            return (int(round(float(vertex[0]) * MULT)), int(round(float(vertex[1]) * MULT)))
        return int(round(float(vertex) * MULT))

    def walk(self, elem):
        if isinstance(elem, list) and len(elem) > 0:
            elemx = [self.walk(x) for x in elem]
            func = dsn.all_functions.get(elemx[0], None)
            if func:
                return func(elemx[1:])
            else:
                return elemx
        else:
            return elem

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
                if buf:
                    lst.append(buf)
                    buf = ''

                if ch == '(':
                    lst.append(self._maybe_eval(self._parse_exp()))
                elif ch == ')':
                    return lst
                elif ch == self.string_quote:
                    lst.append(self._parse_string())

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
                return buf
            else:
                buf += ch

        raise SyntaxError('Closing string quote %s not found' % (self.string_quote))
