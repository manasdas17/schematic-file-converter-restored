#!/usr/bin/env python
""" The board class """

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


class Board:
    """ The physical board as generated from the PCB layout (ie gerbers). """

    def __init__(self):
        self.layers = []


    def generate_netlist(self):
        """ Generate a netlist (connected regions) from the layout. """
        pass


class Layer:
    """ A layer in the physical board. In the final image
    posivite/filled/additive = copper.
    negative/void/subtractive = no-copper. """

    def __init__(self):
        self.type = 'copper' # Copper, mask, silk, or drill
        self.name = ''
        self.manufacturing_details = ''
        self.shapes = []


class Shape:
    """ A shape, wrapped so we can include if its additive or subtractive. """

    def __init__(self):
        self.is_additive = True # additive or subtractive
        self.shape = None
