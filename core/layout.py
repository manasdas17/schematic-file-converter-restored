#!/usr/bin/env python
""" The layout class """


class Layout:
    """ The layout class holds the PCB Layout portion of the design to
    match with the schematics. """

    def __init__(self):
        self.layers = []


class Layer:
    """ A layer in the layout. """

    def __init__(self):
        self.id = ''
        self.type = '' #Copper or Mask/Silk
        self.traces = []
        self.vias = []
        self.fills = []
        self.voids = []
        self.components = []
