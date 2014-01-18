#!/usr/bin/env python2
""" The trace class """

# upconvert - A universal hardware design file format converter using
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


from upconvert.core.shape import Point
from upconvert.utils.stringify import stringify_attributes


class Trace:
    """ a Trace with metadata and a pair of points """

    def __init__(self, trace_id):
        self.trace_id = trace_id
        self.p1 = None
        self.p2 = None
        self.attributes = dict()
        self.annotations = list()


    def bounds(self):
        """ Return the min and max points of the bounding box """
        pass


    def add_annotation(self, annotation):
        """ Add an annotation """
        self.annotations.append(annotation)


    def add_attribute(self, key, value):
        """ Add an attribute """
        self.attributes[key] = value


    def scale(self, factor):
        """ Scale the x & y coordinates in the trace. """
        self.p1.scale(factor)
        self.p2.scale(factor)
        for anno in self.annotations:
            anno.scale(factor)


    def shift(self, dx, dy):
        """ Shift the x & y coordinates in the trace. """
        self.p1.shift(factor)
        self.p2.shift(factor)
        for anno in self.annotations:
            anno.shift(dx, dy)


    def rebase_y_axis(self, height):
        """ Rebase the y coordinate in the trace. """
        self.p1.rebase_y_axis(factor)
        self.p2.rebase_y_axis(factor)
        for anno in self.annotations:
            anno.rebase_y_axis(height)


    def json(self):
        """ Return a trace as JSON """
        return {
            "trace_id": self.trace_id,
            "p1": self.p1.json(),
            "p2": self.p2.json(),
            "attributes": stringify_attributes(self.attributes),
            "annotations": [ann.json() for ann in self.annotations]
            }
