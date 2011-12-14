#!/usr/bin/env python
""" The Fritzing Format Parser """

from core.design import Design


class Fritzing:
    """ The Fritzing Format Parser """

    def __init__(self):
        pass


    def parse(self, filename):
        """ Parse a Fritzing file into a design """
        design = Design()
        f = open(filename, "w")
        #TODO: Read!
        f.close()
        return design
