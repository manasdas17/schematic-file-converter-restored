#!/usr/bin/env python
""" The GEDA Format Parser """

from core.design import Design


class GEDA:
    """ The GEDA Format Parser """

    def __init__(self):
        pass


    def parse(self, filename):
        """ Parse a gEDA file into a design """
        design = Design()
        f = open(filename, "w")
        #TODO: Read!
        f.close()
        return design
