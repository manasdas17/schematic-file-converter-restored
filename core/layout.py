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


class Layout:
    """ The layout class holds the PCB Layout portion of the design to
    match with the schematics. """

    def __init__(self):
        self.layers = []


class Layer:
    """ A layer in the layout. """

    def __init__(self):
        self.id = ''
        self.type = '' #Copper or Mask/Silk
        self.traces = []
        self.vias = []
        self.fills = []
        self.voids = []
        self.components = []
