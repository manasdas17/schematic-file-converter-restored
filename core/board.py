#!/usr/bin/env python
""" The board class """


class Board:
    """ The physical board as generated from the PCB layout (ie gerbers). """

    def __init__(self):
        self.layers = []


    def generate_netlist(self):
        """ Generate a netlist (connected regions) from the layout. """
        pass


class Layer:
    """ A layer in the physical board. In the final image
    posivite/filled/additive = copper.
    negative/void/subtractive = no-copper. """

    def __init__(self):
        self.type = 'copper' # Copper, mask, silk, or drill
        self.name = ''
        self.manufacturing_details = ''
        self.shapes = []


class Shape:
    """ A shape, wrapped so we can include if its additive or subtractive. """

    def __init__(self):
        self.is_additive = True # additive or subtractive
        self.shape = None
