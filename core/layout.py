#!/usr/bin/env python2
""" The layout class """

# upconvert.py - A universal hardware design file format converter using
# Format:       upverter.com/resources/open-json-format/
# Development:  github.com/upverter/schematic-file-converter
#
# Copyright 2011 Upverter, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from shape import Line

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
        self.traces = []# Trace = connected FatLines, FatArcs, etc
        self.vias = []
        self.fills = [] # probably includes pads -- may have to extend
        self.voids = [] # possibly places that must be kept clear -- irrelevant for gerber
        self.components = [] # if used, possibly could include pads

    def json(self):
        """ Return the layer as JSON """
        return {
            "type": self.type,
            "traces": [t.json() for t in self.traces],
            "vias": [v.json() for v in self.vias],
            "fills": [f.json() for f in self.fills],
            "voids": [v.json() for v in self.voids]
            }


class FatLine(Line):
    """ finite width line segment from point1 to point2 """

    def __init__(self, p1, p2, wid):
        super(FatLine, self).__init__(p1, p2)
        self.type = "fatline"
        self.wid = wid

    def json(self):
        """ Return the fatline as JSON """
        return {
            "type": self.type,
            "p1": self.p1.json(),
            "p2": self.p2.json(),
            "wid": self.wid
            }
