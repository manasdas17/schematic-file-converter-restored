#!/usr/bin/env python2
""" Generated objects """

# upconvert - A universal hardware design file format converter using
# Format:       upverter.com/resources/open-json-format/
# Development:  github.com/upverter/schematic-file-converter
#
# Copyright 2012 Upverter, Inc.
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

import logging

from upconvert.core.shape import Circle, Point, Rectangle, RoundedRectangle
from upconvert.core.components import FBody
from upconvert.core.component_instance import FootprintAttribute

log = logging.getLogger('core.generated_object')
_parser_types = {}


def parse_gen_obj_json(gen_obj_json):
    obj_type = gen_obj_json['attributes']['type']
    if obj_type not in _parser_types:
        raise ValueError('No parser for generated object json')
    return _parser_types[obj_type](gen_obj_json)


class GeneratedObject(object):

    def __init__(self, x, y, layer, rotation, flip, attributes):
        self.x = x
        self.y = y
        self.layer = layer
        self.rotation = rotation
        self.flip = flip
        self.attributes = attributes

    def get_attr(self, name, default, instance_attributes):
        return self.attributes.get(name, instance_attributes.get(name, default))

    def get_float_attr(self, name, default, instance_attributes):
        return float(self.get_attr(name, default, instance_attributes))

    def get_int_attr(self, name, default, instance_attributes):
        return int(self.get_attr(name, default, instance_attributes))

    def json(self):
        return {'x': self.x,
                'y': self.y,
                'layer': self.layer,
                'rotation': self.rotation,
                'flip': self.flip,
                'attributes': self.attributes}




class PadStack(GeneratedObject):
    type_name = 'padstack'

    @classmethod
    def parse_gen_obj_json(cls, gen_obj_json):
        return PadStack(int(gen_obj_json['x']),
                        int(gen_obj_json['y']),
                        gen_obj_json['layer'],
                        float(gen_obj_json['rotation']),
                        gen_obj_json['flip'],
                        gen_obj_json['attributes'])


    def bodies(self, offset, instance_attributes):
        bodies = []

        attached_layers = self.get_attr('attached_layers', '', instance_attributes).split(',')
        width = self.get_int_attr('width', 0, instance_attributes)
        height = self.get_int_attr('height', 0, instance_attributes)
        radius = self.get_int_attr('radius', 0, instance_attributes)
        shape_type = self.get_attr('shape', '', instance_attributes)

        pos = Point(self.x, self.y)

        for layer_name in attached_layers:
            layer_name = layer_name
            pad = FBody()
            # invert top/bottom if the footprint is on the bottom of the board
            if offset.side == 'bottom':
                rev_sides = {'top': 'bottom', 'bottom': 'top'}
                layer_name = ' '.join([rev_sides.get(piece, piece) for piece in layer_name.split(' ')])

            if shape_type == 'rectangle':
                pad.add_shape(Rectangle((width / 2), -(height / 2), width, height))
            elif shape_type == 'rounded rectangle':
                pad.add_shape(RoundedRectangle((width / 2), -(height / 2), width, height, radius))
            elif shape_type == 'circle':
                pad.add_shape(Circle(0, 0, radius))
            else:
                raise ValueError('unexpected shape type for padstack')

            pad.rotate(self.rotation)
            pad.shift(pos.x, pos.y)
            bodies.append((FootprintAttribute(0, 0, 0, False, layer_name), pad))

        return bodies


    def __repr__(self):
        return '''<Padstack({0}, {1}, '{2}', {3}, {4}, {5})>'''.format(self.x, self.y, self.layer, self.rotation, self.flip, self.attributes)
_parser_types[PadStack.type_name] = PadStack.parse_gen_obj_json



class PlatedThroughHole(GeneratedObject):
    type_name = 'plated through hole'

    @classmethod
    def parse_gen_obj_json(cls, gen_obj_json):
        return PlatedThroughHole(int(gen_obj_json['x']),
                                 int(gen_obj_json['y']),
                                 gen_obj_json['layer'],
                                 float(gen_obj_json['rotation']),
                                 gen_obj_json['flip'],
                                 gen_obj_json['attributes'])

    def bodies(self, offset, instance_attributes):
        """ Generated the bodies for the Via with instance attribute overrides. Returns placment attribute and body
            pairs.

        """
        attached_layers = self.get_attr('attached_layers', '', instance_attributes).split(',')
        internal_diameter = self.get_float_attr('internal_diameter', 0, instance_attributes)
        plating_shape = self.get_attr('plating_shape', '', instance_attributes)

        # Local vars for use in closures to generate shapes
        # XXX(shamer): The assignment of width and lenght are reversed from the javascript. Not sure why this is.
        plating_width = self.get_float_attr('plating_length', 0, instance_attributes)
        plating_height = self.get_float_attr('plating_width', 0, instance_attributes)
        plating_radius = self.get_float_attr('plating_radius', 0, instance_attributes)
        plating_diameter = self.get_float_attr('plating_diameter', 0, instance_attributes)

        solder_mask_expansion = self.get_float_attr('solder_mask_expansion', 0, instance_attributes)
        #thermal_inner_diameter = self.get_float_attr('thermal_inner_diameter', 0, instance_attributes)
        #thermal_spoke_width = self.get_float_attr('thermal_spoke_width', 0, instance_attributes)
        #antipad_diameter = self.get_float_attr('antipad_diameter', 0, instance_attributes)

        # placment attribute + body pairs making up the generated object
        bodies = []

        pad_pos = Point(self.x, self.y)
        sme_pos = Point(self.x, self.y)

        # Debugging marker for displaying the placment position for generated objects.
        #marker = FBody()
        #marker.add_shape(Circle(pad_pos.x, pad_pos.y, 1000000))
        #bodies.append((FootprintAttribute(0, 0, 0, False, 'top silkscreen'), marker))

        if plating_shape == 'square':
            solder_mask_width = (solder_mask_expansion * 2) + plating_diameter

            create_shape = lambda : Rectangle(pad_pos.x, pad_pos.y, plating_diameter, plating_diameter)
            create_solder_mask_expansion = lambda : Rectangle(sme_pos.x, sme_pos.y, solder_mask_width, solder_mask_width)

        elif plating_shape == 'circle':
            create_shape = lambda : Circle(pad_pos.x, pad_pos.y, plating_diameter / 2)

            solder_mask_radius = solder_mask_expansion + (plating_diameter / 2)
            create_solder_mask_expansion = lambda : Circle(sme_pos.x, sme_pos.y, solder_mask_radius)

        elif plating_shape == 'rectangle':
            solder_mask_width = (solder_mask_expansion * 2) + plating_width
            solder_mask_height = (solder_mask_expansion * 2) + plating_height

            create_shape = lambda : Rectangle(pad_pos.x, pad_pos.y, plating_width, plating_height)
            create_solder_mask_expansion = lambda : Rectangle(sme_pos.x, sme_pos.y, solder_mask_width, solder_mask_height)

        elif plating_shape == 'rounded rectangle':
            solder_mask_width = (solder_mask_expansion * 2) + plating_width
            solder_mask_height = (solder_mask_expansion * 2) + plating_height

            create_shape = lambda : RoundedRectangle(pad_pos.x, pad_pos.y, plating_width, plating_height, plating_radius)
            create_solder_mask_expansion = lambda : RoundedRectangle(sme_pos.x, sme_pos.y, solder_mask_width, solder_mask_height, plating_radius)

        else:
            raise ValueError('unexpected shape for plated through hole "{0}"'.format(plating_shape))

        # cirle of radius 'solder_mask_expansion' + ('plating_diameter' / 2) in the top and bottom silkscreen layers
        solder_mask_radius = solder_mask_expansion + (plating_diameter / 2)
        top_solder_mask = FBody()
        top_solder_mask.add_shape(create_solder_mask_expansion())
        bodies.append((FootprintAttribute(0, 0, 0, False, 'top solder mask'), top_solder_mask))

        bottom_solder_mask = FBody()
        bottom_solder_mask.add_shape(create_solder_mask_expansion())
        bodies.append((FootprintAttribute(0, 0, 0, False, 'bottom solder mask'), bottom_solder_mask))

        # circle of diameter 'internal_diameter' on the hole layer
        hole = FBody()
        hole.add_shape(Circle(pad_pos.x, pad_pos.y, internal_diameter / 2))
        bodies.append((FootprintAttribute(0, 0, 0, False, 'hole'), hole))

        # circles of diameter 'plating_diameter' on each connection layer
        for layer_name in attached_layers:
            connected_layer = FBody()
            if layer_name == 'top copper' or layer_name == 'bottom copper':
                connected_layer.add_shape(create_shape())
            else:
                connected_layer.add_shape(Circle(pad_pos.x, pad_pos.y, plating_diameter / 2))
            bodies.append((FootprintAttribute(0, 0, 0, False, layer_name), connected_layer))

        return bodies

    def __repr__(self):
        return '''<PlatedThroughHole({0}, {1}, '{2}', {3}, {4}, {5})>'''.format(self.x, self.y, self.layer, self.rotation, self.flip, self.attributes)
_parser_types[PlatedThroughHole.type_name] = PlatedThroughHole.parse_gen_obj_json


class Via(GeneratedObject):
    type_name = 'via'

    @classmethod
    def parse_gen_obj_json(cls, gen_obj_json):
        return Via(int(gen_obj_json['x']),
                   int(gen_obj_json['y']),
                   gen_obj_json['layer'],
                   float(gen_obj_json['rotation']),
                   gen_obj_json['flip'],
                   gen_obj_json['attributes'])

    def bodies(self, offset, instance_attributes):
        """ Generated the bodies for the Via with instance attribute overrides. Returns placment attribute and body
            pairs.

        """
        pos = Point(self.x, self.y)

        attached_layers = self.get_attr('attached_layers', '', instance_attributes).split(',')
        solder_mask_expansion = self.get_int_attr('solder_mask_expansion', 0, instance_attributes)
        plating_diameter = self.get_int_attr('plating_diameter', 0, instance_attributes)
        internal_diameter = self.get_int_attr('internal_diameter', 0, instance_attributes)
        solder_mask_radius = solder_mask_expansion + (plating_diameter / 2)

        # placment attribute + body pairs making up the generated object
        bodies = []

        top_solder_mask = FBody()
        top_solder_mask.add_shape(Circle(pos.x, pos.y, solder_mask_radius))
        bodies.append((FootprintAttribute(0, 0, 0, False, 'top solder mask'), top_solder_mask))

        bottom_solder_mask = FBody()
        bottom_solder_mask.add_shape(Circle(pos.x, pos.y, solder_mask_radius))
        bodies.append((FootprintAttribute(0, 0, 0, False, 'bottom solder mask'), bottom_solder_mask))

        # circle of diameter 'internal_diameter' on the hole layer
        hole = FBody()
        hole.add_shape(Circle(pos.x, pos.y, internal_diameter / 2))
        bodies.append((FootprintAttribute(0, 0, 0, False, 'hole'), hole))

        # circles of diameter 'plating_diameter' on each connection layer
        for layer_name in attached_layers:
            connected_layer = FBody()
            connected_layer.add_shape(Circle(pos.x, pos.y, plating_diameter / 2))
            bodies.append((FootprintAttribute(0, 0, 0, False, layer_name), connected_layer))

        return bodies

    def __repr__(self):
        return '''<Via({0}, {1}, '{2}', {3}, {4}, {5})>'''.format(self.x, self.y, self.layer, self.rotation, self.flip, self.attributes)
_parser_types[Via.type_name] = Via.parse_gen_obj_json



class CenterCross(GeneratedObject):
    type_name = 'center cross'

    @classmethod
    def parse_gen_obj_json(cls, gen_obj_json):
        return CenterCross(int(gen_obj_json['x']),
                           int(gen_obj_json['y']),
                           gen_obj_json['layer'],
                           float(gen_obj_json['rotation']),
                           gen_obj_json['flip'],
                           gen_obj_json['attributes'])


    def bodies(self, offset, instance_attributes):
        return []
_parser_types[CenterCross.type_name] = CenterCross.parse_gen_obj_json



class Path(object):
    """ A path formed from connected points. """

    def __init__(self, layer, points, width, is_closed):
        self.layer = layer
        self.points = points
        self.width = width
        self.is_closed = is_closed


    def min_point(self):
        """ Return the min point of the shape """
        if len(self.points) < 1:
            # by convention
            x, y = 0, 0
        else:
            x = min([pt.x for pt in self.points])
            y = min([pt.y for pt in self.points])
        return Point(x, y)


    def max_point(self):
        """ Return the max point of the shape """
        if len(self.points) < 1:
            # by convention
            x, y = 0, 0
        else:
            x = max([pt.x for pt in self.points])
            y = max([pt.y for pt in self.points])
        return Point(x, y)


    def move(self, x, y):
        """ Move the polygon to an explicit position. """
        dx = x - self.point[0].x
        dy = y - self.point[0].y

        for point in self.points:
            point.x -= dx
            point.y -= dy


    def add_point(self, x, y=None):
        """ Add a point to the polygon """
        self.points.append(Point(x, y))


    def scale(self, factor):
        """ Scale the x & y coordinates in the polygon. """
        for point in self.points:
            point.scale(factor)


    def shift(self, dx, dy):
        """ Shift the x & y coordinates in the polygon. """
        for point in self.points:
            point.shift(dx, dy)


    def rebase_y_axis(self, height):
        """ Rebase the y coordinate in the polygon. """
        for point in self.points:
            point.rebase_y_axis(height)


    def json(self):
        """ Return the polygon as JSON """
        return {
            "points": [point.json() for point in self.points],
            "layer": self.layer,
            "width": self.width,
            "is_closed": self.is_closed,
            }



class Pour(object):
    """ A pour formed from connected points with additive and subtractive shapes. """

    def __init__(self, layer, points, subtractive_shapes, readded_shapes):
        self.layer = layer
        self.points = points
        self.subtractive_shapes = subtractive_shapes
        self.readded_shapes = readded_shapes


    def min_point(self):
        """ Return the min point of the shape """
        if len(self.points) < 1:
            # by convention
            x, y = 0, 0
        else:
            x = min([pt.x for pt in self.points])
            y = min([pt.y for pt in self.points])
        return Point(x, y)


    def max_point(self):
        """ Return the max point of the shape """
        if len(self.points) < 1:
            # by convention
            x, y = 0, 0
        else:
            x = max([pt.x for pt in self.points])
            y = max([pt.y for pt in self.points])
        return Point(x, y)


    def move(self, x, y):
        """ Move the polygon to an explicit position. """
        dx = x - self.point[0].x
        dy = y - self.point[0].y

        for point in self.points:
            point.x -= dx
            point.y -= dy


    def add_point(self, x, y=None):
        """ Add a point to the polygon """
        self.points.append(Point(x, y))


    def scale(self, factor):
        """ Scale the x & y coordinates in the pour. """
        for point in self.points:
            point.scale(factor)


    def shift(self, dx, dy):
        """ Shift the x & y coordinates in the pour. """
        for point in self.points:
            point.shift(dx, dy)


    def rebase_y_axis(self, height):
        """ Rebase the y coordinate in the pour. """
        for point in self.points:
            point.rebase_y_axis(height)


    def json(self):
        """ Return the polygon as JSON """
        return {
            "points": [point.json() for point in self.points],
            "layer": self.layer,
            "subtractive_shapes": [subtractive_shape.json() for subtractive_shape in self.subtractive_shapes],
            "readded_shapes": [readded_shape.json() for readded_shape in self.readded_shapes],
            }


