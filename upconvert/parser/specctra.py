#!/usr/bin/env python2

from upconvert.core.design import Design
from upconvert.core.components import Component, Symbol, Body, Pin
from upconvert.core.component_instance import ComponentInstance, SymbolAttribute
from upconvert.core.net import Net, NetPoint, ConnectedComponent
from upconvert.core.shape import Arc, Circle, Line, Rectangle, Label
from upconvert.core.annotation import Annotation

from collections import defaultdict
from os.path import exists, splitext


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
