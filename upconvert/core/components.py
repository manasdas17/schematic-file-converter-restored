#!/usr/bin/env python2
""" The component class """

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


class Components:
    """ Container class for individual 'Component's.
    Only used for add_component and json() (export) """

    def __init__(self):
        self.components = dict()


    def add_component(self, library_id, component):
        """ Add a component to the library """
        self.components[library_id] = component


    def scale(self, factor):
        """ Scale the x & y coordinates in the library. """
        for component in self.components.values():
            component.scale(factor)


    def shift(self, dx, dy):
        """ Shift the x & y coordinates in the library. """
        for component in self.components.values():
            component.shift(dx, dy)


    def rebase_y_axis(self, height):
        """ Rebase the y coordinate in the library. """
        for component in self.components.values():
            component.rebase_y_axis(height)


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
    The 'components' of a design is basically its library of available
    parts.  The actual placed parts on the design are 'Instances' of
    components, and reference their respective component via a unique
    library_id.
    """

    def __init__(self, name):
        self.name = name
        self.attributes = dict()
        self.symbols = list()
        self.footprints = list()


    def add_attribute(self, key, value):
        """ Add an attribute to a component """
        self.attributes[key] = value


    def add_symbol(self, symbol):
        """ Add a symbol to a component """
        self.symbols.append(symbol)


    def add_footprint(self, footprint):
        """ Add a footprint to a component """
        self.footprints.append(footprint)


    def scale(self, factor):
        """ Scale the x & y coordinates in the component. """
        for symbol in self.symbols:
            symbol.scale(factor)


    def shift(self, dx, dy):
        """ Shift the x & y coordinates in the component. """
        for symbol in self.symbols:
            symbol.shift(dx, dy)


    def rebase_y_axis(self, height):
        """ Rebase the y coordinate in the component. """
        for symbol in self.symbols:
            symbol.rebase_y_axis(height)


    def json(self):
        """ Return a component as JSON """
        return {
            "symbols": [s.json() for s in self.symbols],
            "footprints": [s.json() for s in self.footprints],
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


    def scale(self, factor):
        """ Scale the x & y coordinates in the symbol. """
        for body in self.bodies:
            body.scale(factor)


    def shift(self, dx, dy):
        """ Shift the x & y coordinates in the symbol. """
        for body in self.bodies:
            body.shift(dx, dy)


    def rebase_y_axis(self, height):
        """ Rebase the y coordinate in the symbol. """
        for body in self.bodies:
            body.rebase_y_axis(height)


    def json(self):
        """ Return a symbol as JSON """
        return {"bodies":[b.json() for b in self.bodies]}


class Footprint:
    """ This is the physical representation of a Component.
    A Component can have many Footprints, and each Footprint can have
    multiple Bodies """

    def __init__(self):
        self.bodies = list()
        self.gen_objs = list()


    def add_body(self, body):
        """ Add a body to a footprint """
        self.bodies.append(body)


    def add_gen_obj(self, gen_obj):
        """ Add a generated object to a footprint """
        self.gen_objs.append(gen_obj)


    def scale(self, factor):
        """ Scale the x & y coordinates in the footprint. """
        for body in self.bodies:
            body.scale(factor)
        for gen_obj in self.gen_objs:
            gen_obj.scale(factor)


    def shift(self, dx, dy):
        """ Shift the x & y coordinates in the footprint. """
        for body in self.bodies:
            body.shift(dx, dy)
        for gen_obj in self.gen_objs:
            gen_obj.shift(dx, dy)


    def rebase_y_axis(self, height):
        """ Rebase the y coordinate in the footprint. """
        for body in self.bodies:
            body.rebase_y_axis(height)
        for gen_obj in self.gen_objs:
            gen_obj.rebase_y_axis(height)


    def json(self):
        """ Return a footprint as JSON """
        return {"bodies":[b.json() for b in self.bodies],
                "gen_objs": [go.json() for go in self.gen_objs]}


class SBody:
    """ A body of a Symbol of a Component """

    def __init__(self):
        self.shapes = list()
        self.pins = list()


    def bounds(self):
        """ Return the min and max points of the bounding box around a body """
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


    def scale(self, factor):
        """ Scale the x & y coordinates in the symbol. """
        for shape in self.shapes:
            shape.scale(factor)
        for pin in self.pins:
            pin.scale(factor)


    def shift(self, dx, dy):
        """ Shift the x & y coordinates in the symbol. """
        for shape in self.shapes:
            shape.shift(dx, dy)
        for pin in self.pins:
            pin.shift(dx, dy)


    def rebase_y_axis(self, height):
        """ Rebase the y coordinate in the symbol. """
        for shape in self.shapes:
            shape.rebase_y_axis(height)
        for pin in self.pins:
            pin.rebase_y_axis(height)


    def json(self):
        """ Return a symbol as JSON """
        return {
            "shapes":[s.json() for s in self.shapes],
            "pins"  :[p.json() for p in self.pins]
            }


class FBody:
    """ A body of a footprint of a Component """

    def __init__(self):
        self.shapes = list()
        self.layer = None
        self.rotation = 0
        self.flip_horizontal = False


    def bounds(self):
        """ Return the min and max points of the bounding box around a body """
        points = sum([s.bounds() for s in self.shapes], [])
        x_values = [pt.x for pt in points]
        y_values = [pt.y for pt in points]
        if len(x_values) == 0:
            # Empty body includes just the origin
            x_values = [0]
            y_values = [0]
        return [Point(min(x_values), min(y_values)),
                Point(max(x_values), max(y_values))]


    def add_shape(self, shape):
        """ Add a shape to a footprint """
        self.shapes.append(shape)


    def scale(self, factor):
        """ Scale the x & y coordinates in the footprint. """
        for shape in self.shapes:
            shape.scale(factor)


    def shift(self, dx, dy):
        """ Shift the x & y coordinates in the footprint. """
        for shape in self.shapes:
            shape.shift(dx, dy)


    def rebase_y_axis(self, height):
        """ Rebase the y coordinate in the footprint. """
        for shape in self.shapes:
            shape.rebase_y_axis(height)


    def json(self):
        """ Return a footprint as JSON """
        return {
            "shapes":[s.json() for s in self.shapes],
            "rotation": self.rotation,
            "flip": self.flip_horizontal,
            "layer": self.layer
            }


    def rotate(self, rotation):
        self.rotation = (self.rotation + rotation) % 2
        for shape in self.shapes:
            shape.rotate(rotation)


class Pin:
    """ Pins are the parts of SBodies (/symbols/components) that connect
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


    def scale(self, factor):
        """ Scale the x & y coordinates in the pin. """
        if self.label is not None:
            self.label.scale(factor)
        self.p1.scale(factor)
        self.p2.scale(factor)


    def shift(self, dx, dy):
        """ Shift the x & y coordinates in the pin. """
        if self.label is not None:
            self.label.shift(dx, dy)
        self.p1.shift(dx, dy)
        self.p2.shift(dx, dy)


    def rebase_y_axis(self, height):
        """ Rebase the y coordinate in the pin. """
        if self.label is not None:
            self.label.rebase_y_axis(height)
        self.p1.rebase_y_axis(height)
        self.p2.rebase_y_axis(height)


    def json(self):
        """ Return a pin as JSON """
        ret = {
            "pin_number": self.pin_number,
            "p1": self.p1.json(),
            "p2": self.p2.json(),
            "attributes": stringify_attributes(self.attributes),
            "styles": self.styles,
            }
        if self.label is not None:
            ret["label"] = self.label.json()
        return ret


class Pad:
    """ Pads are the parts of FBodies (/footprints/components) that connect
    to traces. Basically a set of shapes.
    """

    def __init__(self, pin_number, p, shapes, label=None):
        self.label = label # is a Label
        self.p = Point(p)
        self.pin_number = pin_number
        self.shapes = shapes
        self.attributes = dict()
        self.styles = dict()


    def add_attribute(self, key, value):
        """ Add attribute to a pin """
        self.attributes[key] = value


    def bounds(self):
        """ Return the min and max points of a pin """
        pass


    def scale(self, factor):
        """ Scale the x & y coordinates in the pin. """
        pass


    def shift(self, dx, dy):
        """ Shift the x & y coordinates in the pin. """
        pass


    def rebase_y_axis(self, height):
        """ Rebase the y coordinate in the pin. """
        pass


    def json(self):
        """ Return a pin as JSON """
        ret = {
            "pin_number": self.pin_number,
            "p": self.p.json(),
            "shapes": [s.json() for s in self.shapes],
            "attributes": stringify_attributes(self.attributes),
            "styles": self.styles,
            }
        if self.label is not None:
            ret["label"] = self.label.json()
        return ret
