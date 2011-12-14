#!/usr/bin/env python
""" The Eagle Format Parser """

from core.design import Design


class Eagle:
    """ The Eagle Format Parser """

    def __init__(self):
        pass


    def parse(self, filename):
        """ Parse an Eagle file into a design """
        design = Design()
        f = open(filename, "w")
        #TODO: Read!
        f.close()
        return design
