#!/usr/bin/env python2
""" The annotation class """

# upconverty - A universal hardware design file format converter using
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


class Annotation:
    """ The Annotation class represents all cases of annotations """

    def __init__(self, value, x, y, rotation, visible, layer='default', flip_horizontal=False, label=None): # pylint: disable=R0913
        self.value = value
        self.x = x
        self.y = y
        self.flip_horizontal = flip_horizontal
        self.label = label
        self.layer = layer
        self.rotation = rotation
        self.visible = visible


    def bounds(self):
        """ Return the bounding points of an annotation """
        return [Point(self.x - 10, self.y - 10),
                Point(self.x + 10, self.y + 10)]


    def ranges(self):
        """ Return the min - max x range, and the min - max y range of the bounding box """
        minpt, maxpt = self.bounds()
        return [minpt.x, maxpt.x], [minpt.y, maxpt.y]


    def scale(self, factor):
        """ Scale the x & y coordinates in the annotation. """
        self.x *= factor
        self.y *= factor


    def shift(self, dx, dy):
        """ Shift the x & y coordinates in the annotation. """
        self.x += dx
        self.y += dy


    def rebase_y_axis(self, height):
        """ Rebase the y coordinate in the annotation. """
        self.y = height - self.y


    def json(self):
        """ Return an annotation as JSON """
        anno_json =  {
            "value": self.value,
            "x": int(self.x),
            "y": int(self.y),
            "layer": self.layer,
            "flip": self.flip_horizontal,
            "rotation": self.rotation,
            "visible": self.visible
            }
        if self.label is not None:
            anno_json["label"] = self.label.json()
        return anno_json
