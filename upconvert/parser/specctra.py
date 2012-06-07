#!/usr/bin/env python2

# Specification of file format can be found here:
# http://tech.groups.yahoo.com/group/kicad-users/files/  file "specctra.pdf"

from upconvert.core.design import Design
from upconvert.core.components import Component, Symbol, Body, Pin
from upconvert.core.component_instance import ComponentInstance, SymbolAttribute
from upconvert.core.net import Net, NetPoint, ConnectedComponent
from upconvert.core.shape import Arc, Circle, Line, Rectangle, Label
from upconvert.core.annotation import Annotation

from collections import defaultdict
from os.path import exists, splitext
from string import whitespace

class Specctra(object):

    @staticmethod
    def auto_detect(filename):
        with open(filename, 'r') as f:
            data = f.read(4096)
        confidence = 0
        if '(DSN' in data.upper():
            confidence += 0.75
        return confidence


    def parse(self, filename, library_filename=None):
        design = Design()
        return design


class DsnParser:
    # Specctra parser configuration: Disables parentheses as delimiters for text strings.
    string_quote = ''
    # Specctra parser configuration: By default, blank spaces are an absolute delimiter. 
    space_in_quoted_tokens = False

    seperators = whitespace + '()'

    def parse(self, exp):
        self.i = 0
        self.length = len(exp)
        self.exp = exp
        return self._parse_exp(root=True)[0]

    def _maybe_eval(self, l):
        """ File format specifies string quoting character:
        this eval configures parser so it can distinguish between
        quote character as atom and quoted string """

        if len(l) > 1:
            if l[0].lower() == 'string_quote':
                self.string_quote = l[1]
            elif l[0].lower() == 'space_in_quoted_tokens':
                self.space_in_quoted_tokens = l[1].lower() == 'on'
        return l

    def _parse_exp(self, root=False):
        """ Parses s-expressions and returns them as Python lists """

        l = []
        s = ''

        while self.i < self.length:
            c = self.exp[self.i]
            self.i += 1

            if c not in self.seperators and c != self.string_quote:
                s += c
            else:
                if s:
                    l.append(s)
                    s = ''

                if c == '(':
                    l.append(self._maybe_eval(self._parse_exp()))
                elif c == ')':
                    return l
                elif c == self.string_quote:
                    l.append(self._parse_string())

        if not root:
            raise SyntaxError('Closing ) not found')
        return l

    def _parse_string(self):
        """ Reads string from expression according to current parser configuration """

        s = ''

        while self.i < self.length:
            c = self.exp[self.i]
            self.i += 1

            if c == self.string_quote:
                return s
            elif c in whitespace and not self.space_in_quoted_tokens:
                return s
            else:
                s += c

        raise SyntaxError('Closing string quote %s not found' % (self.string_quote))
