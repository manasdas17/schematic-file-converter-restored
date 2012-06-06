#!/usr/bin/env python2
""" The component class """

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


def stringify_attributes(attributes):
    attrs = {}
    for n, v in attributes:
        attrs[n] = str(v)
    return attrs


class Components:
    """ Container class for individual 'Component's.
    Only used for add_component and json() (export) """

    def __init__(self):
        self.components = dict()


    def add_component(self, library_id, component):
        """ Add a component to the library """
        self.components[library_id] = component


    def json(self):
        """ Copy to a new dictionary to return """
        ret = dict()
        for library_id, component in self.components.items():
            ret[library_id] = component.json()
        return ret


class Component:
    """ The Component class represents a single kind of part (component).
    It can have multiple graphical representations (Symbols), each with
    multiple sections (Bodies).
    The 'components' of a design is basically it's library of available
    parts.  The actual placed parts on the design are 'Instances' of
    components, and reference their respective component via a unique
    library_id.
    """

    def __init__(self, name):
        self.name = name
        self.attributes = dict()
        self.symbols = list()


    def add_attribute(self, key, value):
        """ Add an attribute to a component """
        self.attributes[key] = value


    def add_symbol(self, symbol):
        """ Add a symbol to a component """
        self.symbols.append(symbol)


    def json(self):
        """ Return a component as JSON """
        return {
            "symbols": [s.json() for s in self.symbols],
            "attributes": stringify_attributes(self.attributes),
            "name": self.name
            }


class Symbol:
    """ This is a graphical representation of a Component.
    A Component can have many Symbols, and each Symbol can have
    multiple Bodies """

    def __init__(self):
        self.bodies = list()


    def add_body(self, body):
        """ Add a body to a symbol """
        self.bodies.append(body)


    def json(self):
        """ Return a symbol as JSON """
        return {"bodies":[b.json() for b in self.bodies]}


class Body:
    """ A body of a Symbol of a Component """

    def __init__(self):
        self.shapes = list()
        self.pins = list()


    def bounds(self):
        """ Return the in and max points of the bounding box around a body """
        points = sum([s.bounds() for s in self.shapes + self.pins], [])
        x_values = [pt.x for pt in points]
        y_values = [pt.y for pt in points]
        if len(x_values) == 0:
            # Empty body includes just the origin
            x_values = [0]
            y_values = [0]
        return [Point(min(x_values), min(y_values)),
                Point(max(x_values), max(y_values))]


    def add_pin(self, pin):
        """ Add a pin to a symbol """
        self.pins.append(pin)


    def add_shape(self, shape):
        """ Add a shape to a symbol """
        self.shapes.append(shape)


    def json(self):
        """ Return a symbol as JSON """
        return {
            "shapes":[s.json() for s in self.shapes],
            "pins"  :[p.json() for p in self.pins]
            }


class Pin:
    """ Pins are the parts of Bodies (/symbols/components) that connect
    to nets. Basically a line segment, with a null end and a connect end
    """

    def __init__(self, pin_number, p1, p2, label=None):
        self.label = label # is a Label
        self.p1 = Point(p1) # null end
        self.p2 = Point(p2) # connect end
        self.pin_number = pin_number
        self.attributes = dict()
        self.styles = dict()


    def add_attribute(self, key, value):
        """ Add attribute to a pin """
        self.attributes[key] = value


    def bounds(self):
        """ Return the min and max points of a pin """
        x_values = [self.p1.x, self.p2.x]
        y_values = [self.p1.y, self.p2.y]
        if self.label is not None:
            x_values.extend([pt.x for pt in self.label.bounds()])
            y_values.extend([pt.y for pt in self.label.bounds()])
        return [Point(min(x_values), min(y_values)),
                Point(max(x_values), max(y_values))]


    def json(self):
        """ Return a pin as JSON """
        ret = {
            "pin_number":self.pin_number,
            "p1":self.p1.json(),
            "p2":self.p2.json(),
            "attributes" : stringify_attributes(self.attributes),
            "styles": self.styles,
            }
        if self.label is not None:
            ret["label"] = self.label.json()
        return ret
