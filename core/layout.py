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

from core.shape import Arc

class Layout:
    """ The layout class holds the PCB Layout portion of the design to
    match with the schematics. """

    def __init__(self):
        self.layers = []


class Layer:
    """ A layer in the layout. """

    def __init__(self):
        self.id = ''
        self.type = ''   # Copper or Mask/Silk
        self.traces = [] # Trace = connected shapes that are of a width
        self.vias = []
        self.fills = []  # probably includes pads -- may have to extend
        self.voids = []
        self.components = [] # if used, possibly could include pads


    def get_trace(self, width, start_pt, end_pt):
        """ Is coord connected to any of the layer's traces? """
        #TODO: interpolate and take widths into account
        for tr_index in range(len(self.traces)):
            trace = self.traces[tr_index]
            for segment in trace.segments:
                if trace.width == width:
                    if isinstance(segment, Arc):
                        seg_ends = segment.ends()
                    else:
                        seg_ends = (segment.p1, segment.p2)
                    if start_pt in seg_ends or end_pt in seg_ends:
                        return tr_index
        return None


    def json(self):
        """ Return the layer as JSON """
        return {
            "type": self.type,
            "traces": [t.json() for t in self.traces],
            "vias": [v.json() for v in self.vias],
            "fills": [f.json() for f in self.fills],
            "voids": [v.json() for v in self.voids]
            }


class Trace:
    """ A collection of connected segments such as lines and arcs. """

    def __init__(self, width=0.01, segments=None, tool_shape='circle'):
        self.type = 'trace'
        self.width = width
        self.tool_shape = tool_shape
        self.segments = segments or []


    def json(self):
        """ Return the trace as JSON """
        return {
            "type": self.type,
            "width": self.width,
            "tool_shape": self.tool_shape,
            "segments": [s.json() for s in self.segments]
            }
