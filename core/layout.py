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
    """ Represents the design schematic as a PCB Layout. """

    def __init__(self):
        self.layers = []


    def generate_netlist(self):
        """ Generate a netlist from the layout. """
        pass


class Layer:
    """ A layer in the layout (ie, a PCB layer). """

    def __init__(self, name=''):
        self.name = name
        self.type = '' # copper/mask/silk/drill
        self.images = []
        self.shapes = {}
        self.macros = {}
        self.vias = []
        self.components = []


    def json(self):
        """ Return the layer as JSON """
        return {
            "type": self.type,
            "images": [i.json() for i in self.images],
            "shapes": [self.shapes[k].json() for k in self.shapes],
            "macros": [self.macros[m].json() for m in self.macros],
            "vias": [v.json() for v in self.vias],
            "components": [c.json() for c in self.components]
            }


class Image:
    """
    An image layer (not a PCB layer).

    Image layers can be additive or subtractive. Therefore they
    must be applied successively to build up a final image
    representing a single layer of the PCB (ie, a single gerber
    file).

    Image layers will be applied in the order they appear in the
    layer[n].images list of the Layout. Subtractive image layers
    only subtract from previous image layers - not subsequent
    image layers.

    Example
    =======
    For a ground plane that is partly negated to make room for
    traces, define three image layers in the following order:

        1. the ground plane
        2. the area(s) to be negated (as a subtractive image)
        3. the traces to be laid within the negated area(s)

    """

    def __init__(self, name='Untitled Image', is_additive=True):
        self.name = name
        self.is_additive = is_additive
        self.x_repeats = 1
        self.x_step = None
        self.y_repeats = 1
        self.y_step = None
        self.traces = []
        self.fills = []
        self.smears = []
        self.shape_instances = []


    def not_empty(self):
        """ True if image contains only metadata. """
        return (self.traces or self.fills or self.smears or
                self.shape_instances) and True or False


    def get_trace(self, width, end_pts):
        """
        Get the list index of a connected trace.

        Params:
            width   - float
            end_pts - tuple of 2 Points (ie, the endpoints of
                      the segment we wish to attach)

        """
        start, end = end_pts
        for tr_index in range(len(self.traces)):
            trace = self.traces[tr_index]
            for seg in trace.segments:
                if trace.width == width:
                    if isinstance(seg, Arc):
                        seg_ends = seg.ends()
                    else:
                        seg_ends = (seg.p1, seg.p2)
                    if start in seg_ends or end in seg_ends:
                        return tr_index
        return None


    def json(self):
        """ Return the image as JSON """
        return {
            "name": self.name,
            "is_additive": self.is_additive and 'true' or 'false',
            "x_repeats": self.x_repeats,
            "x_step": self.x_step,
            "y_repeats": self.y_repeats,
            "y_step": self.y_step,
            "traces": [t.json() for t in self.traces],
            "fills": [[s.json() for s in f] for f in self.fills],
            "shape_instances": [i.json() for i in self.shape_instances]
            }


class Trace:
    """ A collection of connected segments (lines/arcs). """

    def __init__(self, width, segments=None):
        self.width = width
        self.segments = segments or []


    def json(self):
        """ Return the trace as JSON """
        return {
            "width": self.width,
            "segments": [s.json() for s in self.segments]
            }


class Smear:
    """ Line drawn by any shape other than a tiny circle. """

    def __init__(self, line, shape):
        self.line = line
        self.shape = shape


    def json(self):
        """ Return the smear as JSON """
        return {
            "line": self.line.json(),
            "shape": self.shape.json()
            }


class ShapeInstance:
    """
    An instance of a shape or macro.

    If the shape is not defined by a macro, its class
    must be one of Circle, Rectangle, Obround or
    RegularPolygon.

    If the shape is not defined by a macro, it may have
    a hole. The class of the hole must be either Circle
    or Rectangle. The hole is always centered on the
    center of the shape, and never rotates, even if the
    shape itself is rotated.

    x and y attributes can be thought of as an offset.

    """
    def __init__(self, point, shape, hole):
        self.x = point.x
        self.y = point.y
        self.shape = shape
        self.hole = hole


    def json(self):
        """ Return the shape instance as JSON """
        return {
            "x": self.x,
            "y": self.y,
            "shape": (isinstance(self.shape, str) and
                      self.shape or self.shape.json()),
            "hole": self.hole and self.hole.json()
            }


class Macro:
    """
    Complex shape built from multiple primitives.

    Primitive shapes are added together in the order they
    appear in the list. Subtractive shapes subtract only
    from prior shapes, not subsequent shapes.

    """
    def __init__(self, name, primitives):
        self.name = name
        self.primitives = primitives


    def json(self):
        """ Return the macro as JSON """
        return {
            "name": self.name,
            "primitives": [prim.json() for prim in self.primitives]
            }


class Primitive:
    """ A shape with rotation and exposure modifiers. """

    def __init__(self, is_additive, rotation, shape):
        self.is_additive = is_additive
        self.rotation = rotation
        self.shape = shape


    def json(self):
        """ Return the primitive as JSON """
        return {
            "is_additive": self.is_additive and 'true' or 'false',
            "rotation": self.rotation,
            "shape": self.shape.json()
            }
