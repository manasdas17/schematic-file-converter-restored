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
        if '(pcb' in data:
            confidence += 0.75
        return confidence


    def parse(self, filename, library_filename=None):
        self.design = Design()

        with open(filename) as f:
            data = f.read()

        tree = DsnParser().parse(data)

        struct = self.walk(tree)
        print struct
        self.convert(struct)

        return self.design

    def convert(self, struct):
        for component in struct.placement.component:
            library_id = component.image_id
            for place in component.place:
                # Outside OCB boundary
                if not place.vertex: continue

                inst = ComponentInstance(place.component_id, library_id, 0)
                v = self.convert_vertex(struct, place.vertex)
                symbattr = SymbolAttribute(v[0], v[1], place.rotation)
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
                body.add_pin(Pin(pin.pin_id, self.convert_vertex(struct, pin.vertex), self.convert_vertex(struct, pin.vertex)))

    def convert_vertex(self, struct, vertex):
        v1 = struct.structure.boundary.rectangle.vertex1
        v2 = struct.structure.boundary.rectangle.vertex2
        x0 = min(v1[0], v2[0])
        y0 = min(v1[1], v2[1])
        return (vertex[0] + x0 * -1, vertex[1] + y0 * -1)
        

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
