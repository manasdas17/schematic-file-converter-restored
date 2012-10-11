#!/usr/bin/env python2
""" The Open JSON Format Parser """

# upconvert.py - A universal hardware design file format converter using
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

log = logging.getLogger('core.generated_object')
_parser_types = {}


def parse_gen_obj_json(gen_obj_json):
    try:
        return _parser_types[gen_obj_json['attributes']['type']](gen_obj_json)
    except KeyError:
        raise ValueError('No parser for generated object json')


class GeneratedObject:

    def __init__(self, x, y, layer, rotation, flip, attributes):
        self.x = x
        self.y = y
        self.layer = layer
        self.rotation = rotation
        self.flip = flip
        self.attributes = attributes


class Via(GeneratedObject):
    type_name = 'via'

    @classmethod
    def parse_gen_obj_json(cls, gen_obj_json):
        return Via(int(gen_obj_json['x']),
                   int(gen_obj_json['y']),
                   gen_obj_json['layer'],
                   float(gen_obj_json['rotation']),
                   gen_obj_json['flip'] == 'true', # FIXME(shamer): should this be a bool?
                   gen_obj_json['attributes'])
_parser_types[Via.type_name] = Via.parse_gen_obj_json


class PadStack(GeneratedObject):
    type_name = 'padstack'

    @classmethod
    def parse_gen_obj_json(cls, gen_obj_json):
        return PadStack(int(gen_obj_json['x']),
                        int(gen_obj_json['y']),
                        gen_obj_json['layer'],
                        float(gen_obj_json['rotation']),
                        gen_obj_json['flip'] == 'true', # FIXME(shamer): should this be a bool?
                        gen_obj_json['attributes'])
_parser_types[PadStack.type_name] = PadStack.parse_gen_obj_json


class PlatedThroughHole(GeneratedObject):
    type_name = 'plated through hole'

    @classmethod
    def parse_gen_obj_json(cls, gen_obj_json):
        return PlatedThroughHole(int(gen_obj_json['x']),
                                 int(gen_obj_json['y']),
                                 gen_obj_json['layer'],
                                 float(gen_obj_json['rotation']),
                                 gen_obj_json['flip'] == 'true', # FIXME(shamer): should this be a bool?
                                 gen_obj_json['attributes'])
_parser_types[PlatedThroughHole.type_name] = PlatedThroughHole.parse_gen_obj_json


class CenterCross(GeneratedObject):
    type_name = 'center cross'

    @classmethod
    def parse_gen_obj_json(cls, gen_obj_json):
        return CenterCross(int(gen_obj_json['x']),
                           int(gen_obj_json['y']),
                           gen_obj_json['layer'],
                           float(gen_obj_json['rotation']),
                           gen_obj_json['flip'] == 'true', # FIXME(shamer): should this be a bool?
                           gen_obj_json['attributes'])
_parser_types[CenterCross.type_name] = CenterCross.parse_gen_obj_json
