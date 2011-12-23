#!/usr/bin/env python
""" The Gerber RS274-X Format Parser """

from core.design import Design


class Gerber:
    """ The Gerber Format Parser """

    def __init__(self):
        pass


    def parse(self, filename):
        """ Parse a Gerber file into a design """
        design = Design()
        f = open(filename, "w")
        #TODO: Read!
        f.close()
        return design
