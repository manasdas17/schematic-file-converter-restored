#!/usr/bin/env python
#
# Basic Strategy
# 0) ...


class GEDA:
    """ The gEDA Format Writer """

    def __init__(self):
        pass


    def write(self, design, filename):
        """ Write the design to the gEDA format """
        f = open(filename, "w")
        # Write!
        f.close()
        return
