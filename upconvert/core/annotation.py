#!/usr/bin/env python2
""" The annotation class """

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


from upconvert.core.shape import Point


class Annotation:
    """ The Annotation class represents all cases of annotations """

    def __init__(self, value, x, y, rotation, visible): # pylint: disable=R0913
        self.value = value
        self.x = x
        self.y = y
        self.rotation = rotation
        self.visible = visible


    def bounds(self):
        """ Return the bounding points of an annotation """
        return [Point(self.x - 10, self.y - 10),
                Point(self.x + 10, self.y + 10)]


    def json(self):
        """ Return an annotation as JSON """
        return {
            "value": self.value, 
            "x": self.x, 
            "y": self.y,
            "rotation": self.rotation, 
            "visible": self.visible
            }
