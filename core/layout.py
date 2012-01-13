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
        self.type = ''  # Copper or Mask/Silk
        self.traces = []# Lines, Circle parts, etc... connection tracks
        self.vias = []
        self.fills = [] # probably includes pads -- may have to extend
        self.voids = [] # possibly places that must be kept clear -- irrelevant for gerber
        self.components = [] # if used, possibly could include pads
        # self.holes = [] -- should not be relevant - vias probably cover it

# for silk layers, how are symbols defined - eg, 'UART' or '1.' ? Looks like they are traces... Ugh!!
