#!/usr/bin/env python
""" The instance class """

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


class ComponentInstance:
    """ An instance of a component with a specific symbol """

    def __init__(self, instance_id, library_id, symbol_index):
        self.instance_id = instance_id
        self.library_id = library_id
        self.symbol_index = symbol_index
        self.symbol_attributes = list()
        self.attributes = dict()


    def add_attribute(self, key, value):
        """ Add attribute to a component """
        self.attributes[key] = value


    def add_symbol_attribute(self, symbol_attribute):
        """ Add attribute to a components symbol """
        self.symbol_attributes.append(symbol_attribute)


    def get_instance_id(self):
        """ Return the instance id """
        return self.instance_id


    def json(self):
        """ Return a component as JSON """
        return {
            "instance_id" : self.instance_id,
            "library_id" : self.library_id,
            "symbol_index" : self.symbol_index,
            "symbol_attributes":[s.json() for s in self.symbol_attributes],
            "attributes" : self.attributes
            }


class SymbolAttribute:
    """ The instance of a single body.  There should be a SymbolAttribute
    for every body in the symbol that ComponentInstance is an instance of
    """

    def __init__(self, x, y, rotation):
        self.x = x
        self.y = y
        self.rotation = rotation
        self.annotations = []


    def add_annotation(self, annotation):
        """ Add annotations to the body """
        self.annotations.append(annotation)


    def json(self):
        """ Return the body as JSON """
        return {
            "x" : self.x,
            "y": self.y,
            "rotation":self.rotation,
            "annotations" : [a.json() for a in self.annotations]
            }
