#!/usr/bin/env python2
""" Specctra DSN objects """

# upconvert.py - A universal hardware design file format converter using
# Format: upverter.com/resources/open-json-format/
# Development: github.com/upverter/schematic-file-converter
#
# Copyright 2011 Upverter, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Specification of file format can be found here:
# http://tech.groups.yahoo.com/group/kicad-users/files/ file "specctra.pdf"

from inspect import isclass

def pop_type(args, ptype):
    """ Reads argument of type from args """
    if len(args) > 0 and isinstance(args[0], ptype):
        return args.pop(0)
    return None

def pop_types(args, ptype):
    """ Reads list of types from args """
    lst = []
    while True:
        arg = pop_type(args, ptype)
        if arg is None: break
        lst.append(arg)
    return lst

def pop_string(args):
    """ Reads string from args """
    return pop_type(args, basestring)

def pop_vertex(args):
    """ Reads vertex (2 ints) from args """
    x, y = pop_string(args), pop_string(args)
    if x is None or y is None:
        return None
    return (float(x), float(y))

def pop_vertexes(args):
    """ Reads array of vertexes from args """
    lst = []
    while True:
        arg = pop_vertex(args)
        if arg is None: break
        lst.append(arg)
    return lst

class ShapeBase(object):
    """ Base class for all shapes so we can pop a shape from args """
    def __init__(self):
        pass

class Shape:
    """ shape """
    function = 'shape'

    def __init__(self, args):
        assert len(args) >= 0
        self.shape = pop_type(args, ShapeBase)
        #assert len(args) == 0

class Ancestor:
    """ ancestor_file_descriptor """
    function = 'ancestor'

    def __init__(self, args):
        assert len(args) in (2, 3)
        assert args[1][0] == 'created_time'

        self.file_path_name = args[0]
        self.created_time = args[1][1]

        if len(args) == 3:
            assert args[2][0] == 'comment'
            self.comment = args[2][1]
        else:
            self.comment = None

class Attach:
    """ attach_descriptor """
    function = 'attach'

    def __init__(self, args):
        assert len(args) in (1, 2)
        assert args[0] in ('off', 'on')

        self.attach = args[0]
        if len(args) == 2:
            assert args[1][0] == 'use_via'
            self.use_via = args[1][1]
        else:
            self.use_via = None

class Bond:
    """ bond_shape_descriptor """
    function = 'bond'

    def __init__(self, args):
        assert len(args) == 6
        assert args[4] in ('front', 'back')

        self.pin_reference = args[0]
        self.padstack_id = args[1]
        self.vertex = (int(args[2]), int(args[3]))
        self.front_back = args[4]
        self.bond_shape_rotation = args[5]

class Boundary:
    """ boundary_descriptor """
    function = 'boundary'

    def __init__(self, args):
        self.rectangle = pop_type(args, Rectangle)

class Bundle:
    """ bundle_descriptor """
    function = 'bundle'

    class Gap:
        function = 'gap'
        def __init__(self, args):
            assert len(args) >= 1
            self.gap = int(args[0])
            self.layer = []
            for arg in args[1:]:
                assert arg[0] == 'layer'
                # FIXME
                self.layer = arg[1:]

    def __init__(self, args):
        assert len(args) >= 2
        assert args[1][0] == 'nets'

        self.bundle_id = args[0]
        self.nets = args[1][1:]
        self.gap = []
        for arg in args[2:]:
            assert arg[0] == 'gap'
            self.gap.append(Bundle.Gap(arg[1:]))

class CapacitanceResolution:
    """ capacitance_resolution_descriptor """
    function = 'capacitance_resolution'

    def __init__(self, args):
        assert len(args) == 2
        assert args[0] in ('farad', 'mfarad', 'ufarad', 'nfarad', 'pfarad', 'ffarad')

        self.farad = args[0]
        self.value = int(args[1])

class CheckingTrim:
    """ checking_trim_descriptor """
    function = 'checking_trim_by_pin'

    def __init__(self, args):
        assert len(args) == 1
        self.checking_trim_by_pin = pop_string(args)
        assert self.checking_trim_by_pin in ('on', 'off')
        assert len(args) == 0

class Circle(ShapeBase):
    """ circle_descriptor """
    function = 'circle'

    def __init__(self, args):
        super(Circle, self).__init__()
        assert len(args) in (2, 4)
        self.layer_id = args[0]
        self.diameter = float(args[1])
        if len(args) == 4:
            self.vertex = (float(args[2]), float(args[3]))
        else:
            self.vertex = (0, 0)

class Polygon(ShapeBase):
    """ polygon_descriptor """
    function = 'polygon'

    def __init__(self, args):
        super(Polygon, self).__init__()
        assert len(args) > 3
        self.layer_id = pop_string(args)
        self.aperture_width = pop_type(args, basestring)
        self.vertex = pop_vertexes(args)
        assert len(args) == 0 

class Circuit:
    """ circuit_descriptor """
    
    def __init__(self, args):
        self.circuit = args

class PlaceControl:
    """ place_control_descriptor """
    function = 'place_control'

    def __init__(self, args):
        assert len(args) == 1
        self.flip_style = pop_type(args, FlipStyle)
        assert len(args) == 0

class FlipStyle:
    """ flip_style_descriptor """
    function = 'flip_style'

    def __init__(self, args):
        assert len(args) == 1
        self.first = pop_string(args)
        assert len(args) == 0

##############################################################

class Placement:
    """ placement_descriptor """    
    function = 'placement'

    def __init__(self, args):
        assert len(args) >= 1
        self.place_control = pop_type(args, PlaceControl)
        self.component = pop_types(args, Component)
        assert len(args) == 0

class Component:
    """ component_instance """
    function = 'component'

    def __init__(self, args):
        assert len(args) >= 2
        self.image_id = pop_string(args)
        self.place = pop_types(args, Place)
        assert len(args) == 0

class Place:
    """ placement_reference """
    function = 'place'

    def __init__(self, args):
        assert len(args) >= 1
        self.component_id = pop_string(args)
        self.vertex = pop_vertex(args)
        self.side = pop_string(args)
        self.rotation = int(pop_string(args))
        self.part_number = pop_type(args, PartNumber)
        #  FIXME
        #assert len(args) == 0

class PartNumber:
    """ part_number """
    function = 'PN'
    def __init__(self, args):
        assert len(args) == 1
        self.part_number = pop_string(args)
        assert len(args) == 0

class Net:
    """ net_descriptor """
    function = 'net'

    def __init__(self, args):
        assert len(args) >= 1
        self.net_id = pop_string(args)
        self.no_idea_what = pop_string(args)
        self.pins = pop_type(args, Pins)
        assert len(args) == 0

class Network:
    """ network_descriptor """
    function = 'network'

    def __init__(self, args):
        assert len(args) > 0
        self.net = pop_types(args, Net)
        #assert len(args) == 0

class Pins:
    """ pins """
    function = 'pins'

    def __init__(self, args):
        assert len(args) >= 0
        self.pin_reference = args[:]

class Library:
    """ library_descriptor """
    function = 'library'

    def __init__(self, args):
        self.image = pop_types(args, Image)
        self.padstack = pop_types(args, Padstack)
        assert len(args) == 0


class Padstack:
    """ padstack_descriptor """
    function = 'padstack'
    
    def __init__(self, args):
        assert len(args) >= 1
        self.padstack_id = pop_string(args)
        self.shape = pop_types(args, Shape)
        self.attach = pop_type(args, Attach)
#assert len(args) == 0

class Pin:
    """ pin """
    function = 'pin'

    def __init__(self, args):
        assert len(args) >= 1

        self.padstack_id = pop_string(args)
        self.rotation = pop_type(args, Rotate)
        self.pin_id = pop_string(args)
        self.vertex = pop_vertex(args)
        #self.array = pop_type(args, Array)
        #self.property = pop_type(args, Property)

class Rotate:
    """ rotate """
    function = 'rotate'

    def __init__(self, args):
        assert len(args) == 1
        self.rotation = pop_string(args)
        assert len(args) == 0

class Image:
    """ image_descriptor """
    function = 'image'

    def __init__(self, args):
        assert len(args) >= 1
        self.image_id = pop_string(args)
        self.side = pop_type(args, Side)
        self.outline = pop_types(args, Outline)
        self.pin = pop_types(args, Pin)
        #assert len(args) == 0

class Side:
    """ side """
    function = 'side'

    def __init__(self, args):
        assert len(args) == 1
        assert args[0] in ('front', 'back', 'both')

        self.side = pop_type(args, basestring)

class Outline:
    """ outline_descriptor """
    function = 'outline'

    def __init__(self, args):
        assert len(args) == 1
        self.shape = args[0]

class Rectangle(ShapeBase):
    """ rectangle_descriptor """
    function = 'rect'

    def __init__(self, args):
        super(Rectangle, self).__init__()
        assert len(args) == 5
        self.layer_id = pop_string(args)
        self.vertex1 = pop_vertex(args)
        self.vertex2 = pop_vertex(args)
        assert len(args) == 0

class Path(ShapeBase):
    """ path_descriptor """
    function = 'path'

    def __init__(self, args):
        super(Path, self).__init__()
        assert len(args) >= 2

        self.layer_id = pop_type(args, basestring)
        self.aperture_width = pop_type(args, basestring)
        self.vertex = []

        while True:
            x, y = pop_type(args, basestring), pop_type(args, basestring)
            if x is None: break
            self.vertex.append((float(x), float(y)))
        
        self.aperture_type = pop_type(args, ApertureType)
        assert len(args) == 0

class ApertureType:
    """ aperture_type """
    function = 'aperture_type'

    def __init__(self, args):
        assert len(args) == 1
        assert args[0] in ('round', 'square')

        self.aperture_type = args[0]

class Pcb:
    """ pcb """
    function = 'pcb'

    def __init__(self, args):
        assert len(args) >= 1
        self.pcb_id = pop_string(args)
        #self.placement = pop_type(args, Placement)
        self.parser = pop_type(args, Parser)
        self.resolution = pop_type(args, Resolution)
        self.structure = [x for x in args if isinstance(x, Structure)][0]
        self.placement = [x for x in args if isinstance(x, Placement)][0]
        self.library = [x for x in args if isinstance(x, Library)][0]
        self.network = [x for x in args if isinstance(x, Network)][0]

class PCB(Pcb):
    """ pcb """
    function = 'PCB'

class Parser:
    """ parser_descriptor """
    function = 'parser'

    def __init__(self, args):
        pass

class Structure:
    """ structure_descriptor """
    function = 'structure'

    def __init__(self, args):
        self.boundary = [x for x in args if isinstance(x, Boundary)][0]

class Resolution:
    """ resolution_descriptor """
    function = 'resolution'

    def __init__(self, args):
        assert len(args) == 2
        self.unit = pop_string(args)
        assert self.unit in ('inch', 'mil', 'cm', 'mm', 'um')
        self.resolution = int(pop_string(args))
        assert len(args) == 0

##############################################################

ALL_FUNCTIONS = dict([(s.function, s) for s in globals().values() if isclass(s) and getattr(s, 'function', None)])

def lookup(funcname):
    """ Return class for given function name """
    return ALL_FUNCTIONS.get(funcname, None)
