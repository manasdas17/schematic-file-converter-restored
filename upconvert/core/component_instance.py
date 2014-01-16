#!/usr/bin/env python2
""" The instance class """

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


from upconvert.utils.stringify import stringify_attributes


class ComponentInstance:
    """ An instance of a component with a specific symbol """

    def __init__(self, instance_id, library_component, library_id, symbol_index, footprint_index=0):
        self.instance_id = instance_id
        self.library_id = library_id
        self.library_component = library_component
        self.symbol_index = symbol_index
        self.symbol_attributes = list()
        self.footprint_index = footprint_index
        self.footprint_attributes = list()
        self.gen_obj_attributes = list()
        self.footprint_pos = None
        self.attributes = dict()


    def add_attribute(self, key, value):
        """ Add attribute to a component """
        self.attributes[key] = value


    def get_attribute(self, key):
        if key in self.attributes:
            return self.attributes[key]

        elif key in self.library_component.attributes:
            return self.library_component.attributes[key]

        else:
            return '??'


    def add_symbol_attribute(self, symbol_attribute):
        """ Add attribute to a components symbol """
        self.symbol_attributes.append(symbol_attribute)


    def add_footprint_attribute(self, footprint_attribute):
        """ Add attribute to a components footprint """
        self.footprint_attributes.append(footprint_attribute)


    def add_gen_obj_attribute(self, gen_obj_attribute):
        """ Add a generated object to the component instance. """
        self.gen_obj_attributes.append(gen_obj_attribute)


    def set_footprint_pos(self, footprint_pos):
        self.footprint_pos = footprint_pos


    def get_instance_id(self):
        """ Return the instance id """
        return self.instance_id


    def scale(self, factor):
        """ Scale the x & y coordinates in the instance. """
        for attr in self.symbol_attributes:
            attr.scale(factor)


    def shift(self, dx, dy):
        """ Shift the x & y coordinates in the instance. """
        for attr in self.symbol_attributes:
            attr.shift(dx, dy)


    def rebase_y_axis(self, height):
        """ Rebase the y coordinate in the instance. """
        for attr in self.symbol_attributes:
            attr.rebase_y_axis(height)


    def json(self):
        """ Return a component as JSON """
        json = {
            "instance_id" : self.instance_id,
            "library_id" : self.library_id,
            "symbol_index" : self.symbol_index,
            "symbol_attributes":[s.json() for s in self.symbol_attributes],
            "footprint_index" : self.footprint_index,
            "footprint_attributes":[s.json() for s in self.footprint_attributes],
            "gen_obj_attributes":[s.json() for s in self.gen_obj_attributes],
            "attributes" : stringify_attributes(self.attributes)
            }
        if self.footprint_pos is not None:
            json["footprint_pos"] = self.footprint_pos.json()
        return json


    def __repr__(self):
        return '''<ComponentInstance('{0}', '{1}', {2}, {3})>'''.format(self.instance_id, self.library_id, self.symbol_index, self.footprint_index)


class SymbolAttribute:
    """ The instance of a single body.  There should be a SymbolAttribute
    for every body in the symbol that ComponentInstance is an instance of.
    """

    def __init__(self, x, y, rotation, flip=False):
        self.x = x
        self.y = y
        self.rotation = rotation
        self.flip = flip
        self.annotations = []


    def add_annotation(self, annotation):
        """ Add annotations to the body """
        self.annotations.append(annotation)


    def scale(self, factor):
        """ Scale the x & y coordinates in the attributes. """
        self.x *= factor
        self.y *= factor
        for anno in self.annotations:
            anno.scale(factor)


    def shift(self, dx, dy):
        """ Shift the x & y coordinates in the attributes. """
        self.x += dx
        self.y += dy
        for anno in self.annotations:
            anno.shift(dx, dy)


    def rebase_y_axis(self, height):
        """ Rebase the y coordinate in the attributes. """
        self.y = height - self.y
        for anno in self.annotations:
            anno.rebase_y_axis(height)


    def json(self):
        """ Return the body as JSON """

        if self.flip:
            flip = "true"
        else:
            flip = "false"

        return {
            "x": int(self.x),
            "y": int(self.y),
            "rotation": self.rotation,
            "flip": flip,
            "annotations": [a.json() for a in self.annotations]
            }


class FootprintAttribute:
    """ The instance of a single body.  There should be a FootprintAttribute
    for every body in the footprint that ComponentInstance is an instance of.
    """

    def __init__(self, x, y, rotation, flip_horizontal, layer):
        self.x = x
        self.y = y
        self.rotation = rotation
        self.flip_horizontal = flip_horizontal
        self.layer = layer


    def scale(self, factor):
        """ Scale the x & y coordinates in the attributes. """
        self.x *= factor
        self.y *= factor


    def shift(self, dx, dy):
        """ Shift the x & y coordinates in the attributes. """
        self.x += dx
        self.y += dy


    def rebase_y_axis(self, height):
        """ Rebase the y coordinate in the attributes. """
        self.y = height - self.y


    def json(self):
        """ Return the body as JSON """

        return {
            "x": int(self.x),
            "y": int(self.y),
            "rotation": self.rotation,
            "flip_horizontal": self.flip_horizontal,
            "layer": self.layer,
            }

    def __repr__(self):
        return '''<FootprintAttribute({0}, {1}, {2}, {3}, '{4}')>'''.format(self.x, self.y, self.rotation, self.flip_horizontal, self.layer)


class GenObjAttribute:
    """ The instance of a single generated object. """

    def __init__(self, x, y, rotation, flip, layer):
        self.x = x
        self.y = y
        self.rotation = rotation
        self.flip = flip
        self.layer = layer
        self.attributes = {}


    def add_attribute(self, key, value):
        self.attributes[key] = value


    def scale(self, factor):
        """ Scale the x & y coordinates in the attributes. """
        self.x *= factor
        self.y *= factor


    def shift(self, dx, dy):
        """ Shift the x & y coordinates in the attributes. """
        self.x += dx
        self.y += dy


    def rebase_y_axis(self, height):
        """ Rebase the y coordinate in the attributes. """
        self.y = height - self.y


    def json(self):
        """ Return the body as JSON """

        return {
            "x": int(self.x),
            "y": int(self.y),
            "rotation": self.rotation,
            "flip": self.flip,
            "layer": self.layer,
            "attributes" : stringify_attributes(self.attributes)
            }

    def __repr__(self):
        return '''<GenObjAttribute({0}, {1}, {2}, {3}, '{4}', {5})>'''.format(self.x, self.y, self.rotation, self.flip, self.layer, self.attributes)


class FootprintPos:
    """ The footprint position. """

    def __init__(self, x, y, rotation, flip, side):
        self.x = x
        self.y = y
        self.rotation = rotation
        self.flip_horizontal = flip
        self.side = side


    def scale(self, factor):
        """ Scale the x & y coordinates in the attributes. """
        self.x *= factor
        self.y *= factor


    def shift(self, dx, dy):
        """ Shift the x & y coordinates in the attributes. """
        self.x += dx
        self.y += dy


    def rebase_y_axis(self, height):
        """ Rebase the y coordinate in the attributes. """
        self.y = height - self.y

    def __repr__(self):
        return '''<FootprintPos(x={0}, y={1}, rotation={2}, flip={3}, side='{4}')>'''.format(self.x, self.y, self.rotation, self.flip_horizontal, self.side)

    def json(self):
        """ Return the body as JSON """

        return {
            "x": int(self.x),
            "y": int(self.y),
            "rotation": self.rotation,
            "flip": self.flip_horizontal,
            "side": self.side
            }

