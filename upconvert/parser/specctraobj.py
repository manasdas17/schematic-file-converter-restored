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

# For writing dsn() method always assumes parser configuration:
# (parser
#    (string_quote ")
#    (space_in_quoted_tokens on)
# )

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

def pop_strings(args):
    """ Reads list of strings from args """
    lst = []
    while True:
        arg = pop_string(args)
        if arg is None: break
        lst.append(arg)
    return lst

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

def pop_listtype(args, fname, ptype):
    """ Reads argument of type from args """
    if len(args) > 0 and isinstance(args[0], list):
        if args[0][0] == fname:
            p = ptype()
            p.parse(args.pop(0)[1:])
            return p
    return None

def pop_listtypes(args, fname, ptype):
    """ Reads list of types from args """
    lst = []
    while True:
        arg = pop_listtype(args, fname, ptype)
        if arg is None: break
        lst.append(arg)
    return lst

def assert_empty(obj, args):
    if len(args) > 0:
        print obj, len(args), args
    assert len(args) == 0

class ShapeBase(object):
    """ Base class for all shapes so we can pop a shape from args """
    def parse(self):
        pass

class Shape:
    """ shape """
    function = 'shape'

    def __init__(self):
        self.shape = None

    def parse(self, args):
        assert len(args) >= 0
        self.shape = pop_type(args, ShapeBase)
        #assert_empty(self, args)

    def compose(self):
        return [
            self.function,
            self.shape and self.shape.compose()
        ]

class Ancestor:
    """ ancestor_file_descriptor """
    function = 'ancestor'

    def parse(self, args):
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

    def parse(self, args):
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

    def parse(self, args):
        assert len(args) == 6
        assert args[4] in ('signal', 'back')

        self.pin_reference = args[0]
        self.padstack_id = args[1]
        self.vertex = (int(args[2]), int(args[3]))
        self.signal_back = args[4]
        self.bond_shape_rotation = args[5]

class Boundary:
    """ boundary_descriptor """
    function = 'boundary'

    def __init__(self):
        self.rectangle = None

    def parse(self, args):
        self.rectangle = pop_type(args, Rectangle)

    def compose(self):
        return [self.function, self.rectangle and self.rectangle.compose()]

class Bundle:
    """ bundle_descriptor """
    function = 'bundle'

    class Gap:
        function = 'gap'
        def parse(self, args):
            assert len(args) >= 1
            self.gap = int(args[0])
            self.layer = []
            for arg in args[1:]:
                assert arg[0] == 'layer'
                # FIXME
                self.layer = arg[1:]

    def parse(self, args):
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

    def parse(self, args):
        assert len(args) == 2
        assert args[0] in ('farad', 'mfarad', 'ufarad', 'nfarad', 'pfarad', 'ffarad')

        self.farad = args[0]
        self.value = int(args[1])

class CheckingTrim:
    """ checking_trim_descriptor """
    function = 'checking_trim_by_pin'

    def parse(self, args):
        assert len(args) == 1
        self.checking_trim_by_pin = pop_string(args)
        assert self.checking_trim_by_pin in ('on', 'off')
        assert_empty(self, args)

class Circle(ShapeBase):
    """ circle_descriptor """
    function = 'circle'

    def __init__(self):
        self.layer_id = 'signal'
        self.diameter = None
        self.vertex = (0, 0)

    def parse(self, args):
        super(Circle, self).parse()
        assert len(args) in (2, 4)
        self.layer_id = args[0]
        self.diameter = float(args[1])
        if len(args) == 4:
            self.vertex = (float(args[2]), float(args[3]))
        else:
            self.vertex = (0, 0)

    def compose(self):
        return [
            self.function,
            self.layer_id,
            self.diameter,
            self.vertex[0], self.vertex[1]
        ]

class Polygon(ShapeBase):
    """ polygon_descriptor """
    function = 'polygon'

    def __init__(self):
        self.layer_id = 'signal'
        self.aperture_width = 0
        self.vertex = []

    def parse(self, args):
        super(Polygon, self).parse()
        assert len(args) > 3
        self.layer_id = pop_string(args)
        self.aperture_width = pop_type(args, basestring)
        self.vertex = pop_vertexes(args)
        assert_empty(self, args) 

    def compose(self):
        result = [
            self.function,
            self.layer_id,
            self.aperture_width,
            ]
        for v in self.vertex:
            result.extend(v)
        return result

class Circuit:
    """ circuit_descriptor """
    
    def parse(self, args):
        self.circuit = args

class PlaceControl:
    """ place_control_descriptor """
    function = 'place_control'

    def parse(self, args):
        assert len(args) == 1
        self.flip_style = pop_type(args, FlipStyle)
        assert_empty(self, args)

class FlipStyle:
    """ flip_style_descriptor """
    function = 'flip_style'

    def parse(self, args):
        assert len(args) == 1
        self.first = pop_string(args)
        assert_empty(self, args)

##############################################################

class Placement:
    """ placement_descriptor """    
    function = 'placement'

    def __init__(self):
        self.place_control = None
        self.component = []

    def parse(self, args):
        assert len(args) >= 1
        self.place_control = pop_type(args, PlaceControl)
        self.component = pop_types(args, Component)
        assert_empty(self, args)

    def compose(self):
        return [
            self.function,
            self.place_control and self.place_control.compose(),
        ] + [x.compose() for x in self.component]

class Component:
    """ component_instance """
    function = 'component'

    def __init__(self):
        self.image_id = None
        self.place = None


    def parse(self, args):
        assert len(args) >= 2
        self.image_id = pop_string(args)
        self.place = pop_types(args, Place)
        assert_empty(self, args)

    def compose(self):
        return [
            self.function,
            self.image_id,
            self.place and self.place.compose()
        ]

class Place:
    """ placement_reference """
    function = 'place'

    def __init__(self):
        self.component_id = None
        self.vertex = (None, None)
        self.side = 'front'
        self.rotation = 0
        self.part_number = None

    def parse(self, args):
        assert len(args) >= 1
        self.component_id = pop_string(args)
        self.vertex = pop_vertex(args)
        self.side = pop_string(args)
        self.rotation = int(pop_string(args))
        self.part_number = pop_type(args, PartNumber)
        #  FIXME
        #assert_empty(self, args)

    def compose(self):
        return [
            self.function,
            self.component_id,
            self.vertex[0], self.vertex[1],
            self.side,
            self.rotation,
            self.part_number and self.part_number.compose()
        ]

class PartNumber:
    """ part_number """
    function = 'PN'
    def parse(self, args):
        assert len(args) == 1
        self.part_number = pop_string(args)
        assert_empty(self, args)

class Net:
    """ net_descriptor """
    function = 'net'

    def __init__(self):
        self.net_id = None
        self.pins = []

    def parse(self, args):
        assert len(args) >= 1
        self.net_id = pop_string(args)
        self.no_idea_what = pop_string(args)
        self.pins = pop_type(args, Pins)
        assert_empty(self, args)

    def compose(self):
        return [self.function, self.net_id] + [x.compose() for x in self.pins]

class Network:
    """ network_descriptor """
    function = 'network'

    def __init__(self):
        self.net = []

    def parse(self, args):
        self.net = pop_types(args, Net)
        #assert_empty(self, args)
        # (via ...

    def compose(self):
        return [self.function] + [x.compose() for x in self.net]

class Pins:
    """ pins """
    function = 'pins'

    def __init__(self):
        self.pin_reference = []

    def parse(self, args):
        assert len(args) >= 0
        self.pin_reference = pop_strings(args)
        assert_empty(self, args)

    def compose(self):
        return [self.function] + self.pin_reference

class Library:
    """ library_descriptor """
    function = 'library'

    def __init__(self):
        self.image = []
        self.padstack = []

    def parse(self, args):
        self.image = pop_types(args, Image)
        self.padstack = pop_types(args, Padstack)
        assert_empty(self, args)

    def compose(self):
        return [
            self.function,
        ] + [x.compose() for x in self.image] + [x.compose() for x in self.padstack]

class Padstack:
    """ padstack_descriptor """
    function = 'padstack'

    def __init__(self):
        self.padstack_id = None
        self.shape = []
        self.attach = None
    
    def parse(self, args):
        assert len(args) >= 1
        self.padstack_id = pop_string(args)
        self.shape = pop_types(args, Shape)
        self.attach = pop_type(args, Attach)
#assert_empty(self, args)

    def compose(self):
        return [
            self.function,
            self.padstack_id,
        ] + [x.compose() for x in self.shape] + [
            self.attach and self.attach.compose()
        ]

class Pin:
    """ pin """
    function = 'pin'

    def __init__(self):
        self.padstack_id = None
        self.rotation = None
        self.pin_id = None
        self.vertex = (None, None)

    def parse(self, args):
        assert len(args) >= 1

        self.padstack_id = pop_string(args)
        self.rotation = pop_type(args, Rotate)
        self.pin_id = pop_string(args)
        self.vertex = pop_vertex(args)
        #self.array = pop_type(args, Array)
        #self.property = pop_type(args, Property)

    def compose(self):
        return [
            self.function,
            self.padstack_id,
            self.rotation and self.rotation.compose(),
            self.pin_id,
            self.vertex[0], self.vertex[1],
        ]

class Rotate:
    """ rotate """
    function = 'rotate'

    def __init__(self):
        self.rotation = None

    def parse(self, args):
        assert len(args) == 1
        self.rotation = pop_string(args)
        assert_empty(self, args)

    def compose(self):
        return [
            self.function,
            self.rotation
        ]

class Image:
    """ image_descriptor """
    function = 'image'

    def __init__(self):
        self.image_id = None
        self.side = None
        self.outline = []
        self.pin = []
        self.keepout = []

    def parse(self, args):
        assert len(args) >= 1
        self.image_id = pop_string(args)
        self.side = pop_type(args, Side)
        self.outline = pop_types(args, Outline)
        self.pin = pop_types(args, Pin)
        self.keepout = pop_types(args, Keepout)
        if not self.outline:
            # XXX sometimes outline and pin come in mixed order
            self.outline = pop_types(args, Outline)
        assert_empty(self, args)

    def compose(self):
        return [
            self.function,
            self.image_id,
            self.side and self.side.compose(),
        ] + [x.compose() for x in self.outline] \
          + [x.compose() for x in self.pin] \
          + [x.compose() for x in self.keepout]

class Keepout(object):
    """ Base class for all keepout_descriptors """
    function = 'keepout'

    def __init__(self):
        self.keepout_id = None
        self.shape = None
        self.junk = None

    def parse(self, args):
        assert len(args) >= 1
        self.keepout_id = pop_string(args)
        self.shape = pop_types(args, ShapeBase)
        self.junk = pop_types(args, ClearanceClass)
        assert_empty(self, args)

    def compose(self):
        return [
            self.function,
            self.keepout_id,
            self.shape and self.shape.compose(),
            self.junk and self.junk.composeo()
        ]

class PlaceKeepout(Keepout):
    """ place_keepout """
    function = 'place_keepout'

class ViaKeepout(Keepout):
    """ via_keepout """
    function = 'via_keepout'

class ClearanceClass:
    """ Something undocumented: [['clearance_class', 'default']] """
    function = 'clearance_class'

    def __init__(self):
        self.value = None

    def parse(self, args):
        assert len(args) == 1
        self.value = pop_string(args)
        assert_empty(self, args)

    def compose(self):
        return [
            self.function,
            self.value
        ]

class Side:
    """ side """
    function = 'side'

    def __init__(self):
        self.side = None

    def parse(self, args):
        assert len(args) == 1
        self.side = pop_string(args)
        assert self.side in ('front', 'back', 'both')
        assert_empty(self, args)

    def compose(self):
        return [
            self.function,
            self.side
        ]

class Outline:
    """ outline_descriptor """
    function = 'outline'

    def __init__(self):
        self.shape = None

    def parse(self, args):
        assert len(args) == 1
        self.shape = pop_type(args, ShapeBase)

    def compose(self):
        return [
            self.function,
            self.shape and self.shape.compose()
        ]

class Rectangle(ShapeBase):
    """ rectangle_descriptor """
    function = 'rect'

    def __init__(self):
        super(Rectangle, self).__init__()
        self.layer_id = 'signal'
        self.vertex1 = (None, None)
        self.vertex2 = (None, None)

    def parse(self, args):
        assert len(args) == 5
        self.layer_id = pop_string(args)
        self.vertex1 = pop_vertex(args)
        self.vertex2 = pop_vertex(args)
        assert_empty(self, args)

    def compose(self):
        return [
            self.function,
            self.layer_id,
            self.vertex1[0], self.vertex1[1],
            self.vertex2[0], self.vertex2[1],
        ]

class Path(ShapeBase):
    """ path_descriptor """
    function = 'path'

    def __init__(self):
        super(Path, self).__init__()
        self.layer_id = 'signal'
        self.aperture_width = 0
        self.vertex = []
        self.aperture_type = None

    def parse(self, args):
        assert len(args) >= 2
        self.layer_id = pop_string(args)
        self.aperture_width = pop_string(args)
        self.vertex = pop_vertexes(args)
        self.aperture_type = pop_type(args, ApertureType)
        assert_empty(self, args)

    def compose(self):
        result = [
            self.function,
            self.layer_id,
            self.aperture_width,
            ]
        for v in self.vertex:
            result.extend(v)
        result.append(self.aperture_type)
        return result

class PolylinePath(Path):
    """ Undocumented: seems to be the same as path except start & end are NOT connected """
    function = 'polyline_path'

class ApertureType:
    """ aperture_type """
    function = 'aperture_type'

    def __init__(self):
        self.aperture_type = None

    def parse(self, args):
        assert len(args) == 1
        assert args[0] in ('round', 'square')

        self.aperture_type = args[0]

    def compose(self):
        return [
            self.function,
            self.aperture_type
        ]

class Pcb:
    """ pcb """
    function = 'pcb'

    def __init__(self):
        self.pcb_id = 'dummy'
        self.parser = Parser()
        self.resolution = None
        self.unit = None
        self.structure = None
        self.placement = None
        self.library = None
        self.network = None
        self.wiring = None
 
    def parse(self, args):
        assert len(args) >= 1
        self.pcb_id = pop_string(args)
        self.parser = pop_type(args, Parser)
        self.resolution = pop_type(args, Resolution)
        self.unit = pop_type(args, Unit)
        self.structure = pop_type(args, Structure)
        self.placement = pop_type(args, Placement)
        self.library = pop_type(args, Library)
        self.network = pop_type(args, Network)
        self.wiring = pop_type(args, Wiring)
        assert_empty(self, args)

    def compose(self):
        return [
            self.function,
            self.pcb_id,
            self.parser and self.parser.compose(),
            self.resolution and self.resolution.compose(),
            self.unit and self.unit.compose(),
            self.structure and self.structure.compose(),
            self.placement and self.placement.compose(),
            self.library and self.library.compose(),
            self.network and self.network.compose(),
            self.wiring and self.wiring.compose()
        ]

class PCB(Pcb):
    """ pcb """
    function = 'PCB'

class Parser:
    """ parser_descriptor """
    function = 'parser'

    def __init__(self):
        self.string_quote = StringQuote()
        self.space_in_quoted_tokens = SpaceInQuotedTokens()
        self.host_cad = None
        self.host_version = None

    def parse(self, args):
        self.string_quote = pop_type(args, StringQuote)
        self.space_in_quoted_tokens = pop_type(args, SpaceInQuotedTokens)
        self.host_cad = pop_type(args, HostCad)
        self.host_version = pop_type(args, HostVersion)
        #assert_empty(self, args)
        # (generated_by_freeroute)

    def compose(self):
        return [
            self.function,
            self.string_quote and self.string_quote.compose(),
            self.space_in_quoted_tokens and self.space_in_quoted_tokens.compose(),
            self.host_cad and self.host_cad.compose(),
            self.host_version and self.host_version.compose()
        ]

class StringQuote:
    function = 'string_quote'

    def __init__(self):
        self.value = '"'

    def parse(self, args):
        assert len(args) == 1
        self.value = pop_string(args)
        assert_empty(self, args)

    def compose(self):
        return [self.function, self.value]

class SpaceInQuotedTokens:
    function = 'space_in_quoted_tokens'

    def __init__(self):
        self.value = 'on'

    def parse(self, args):
        assert len(args) == 1
        self.value = pop_string(args)
        assert_empty(self, args)

    def compose(self):
        return [self.function, self.value]

class Structure:
    """ structure_descriptor """
    function = 'structure'

    def __init__(self):
        self.layer = []
        self.boundary = []

    def parse(self, args):
        self.layer = [x for x in args if isinstance(x, Layer)]
        self.boundary = [x for x in args if isinstance(x, Boundary)]

    def compose(self):
        return [
            self.function,
        ] + [x.compose() for x in self.layer] \
          + [x.compose() for x in self.boundary]

class Resolution:
    """ resolution_descriptor """
    function = 'resolution'

    def __init__(self):
        self.dpi = 96.0
        self.unit = None
        self.resolution = 0

    def parse(self, args):
        assert len(args) == 2
        self.unit = pop_string(args)
        assert self.unit in ('inch', 'mil', 'cm', 'mm', 'um')
        self.resolution = int(pop_string(args))
        assert_empty(self, args)

    def compose(self):
        return [
            self.function,
            self.unit,
            self.resolution
        ]

    def to_pixels(self, point):
        if self.unit == 'inch':
            mult = self.dpi / 1.0
        elif self.unit == 'mil':
            mult = self.dpi / 1000.0
        elif self.unit == 'cm':
            mult = self.dpi / 2.54
        elif self.unit == 'mm':
            mult =  self.dpi / 2.54 / 10.0
        elif self.unit == 'um':
            mult =  self.dpi / 2.54 / 1000.0

        mult *= 3
        if isinstance(point, tuple):
            return (int(round(float(point[0]) * mult)), int(round(float(point[1]) * mult)))
        return int(round(float(point) * mult))

    def from_pixels(self, point):
        if self.unit == 'inch':
            mult = 1.0 / self.dpi
        elif self.unit == 'mil':
            mult = 1000.0 / self.dpi
        elif self.unit == 'cm':
            mult = 2.54 / self.dpi
        elif self.unit == 'mm':
            mult =  2.54 / 10.0 / self.dpi
        elif self.unit == 'um':
            mult =  2.54 / 1000.0 / self.dpi

        if isinstance(point, tuple):
            return (float(point[0]) * mult, float(point[1]) * mult)
        return float(point) * mult



class HostCad:
    """ host_cad """
    function = 'host_cad'

    def __init__(self):
        self.value = None

    def parse(self, args):
        assert len(args) == 1
        self.value = pop_string(args)
        assert_empty(self, args)

    def compose(self):
        return [self.function, self.value]

class HostVersion:
    """ host_version """
    function = 'host_version'

    def __init__(self):
        self.value = None

    def parse(self, args):
        assert len(args) == 1
        self.value = pop_string(args)
        assert_empty(self, args)

    def compose(self):
        return [self.function, self.value]

class Absolute:
    """ absolute """
    function = 'absolute'

    def __init__(self):
        self.value = None

    def parse(self, args):
        assert len(args) == 1
        self.value = pop_string(args)
        assert self.value in ('on', 'off')
        assert_empty(self, args)

    def compose(self):
        return [self.function, self.value]

class Unit:
    """ unit """
    function = 'unit'

    def __init__(self):
        self.value = None

    def parse(self, args):
        assert len(args) == 1
        self.value = pop_string(args)
        assert_empty(self, args)

    def compose(self):
        return [self.function, self.value]

class Wiring:
    """ wiring_descriptor """
    function = 'wiring'

    def __init__(self):
        self.wire = []
        self.via = None

    def parse(self, args):
        # Empty seems to be ok
        self.wire = pop_types(args, Wire)
        self.via = pop_listtypes(args, 'via', WireVia)
        self.wire.extend(pop_types(args, Wire))
        assert_empty(self, args)

    def compose(self):
        return [
            self.function,
        ] + [x.compose() for x in self.wire] + [
            self.via and self.via.compose()
        ]

class Wire:
    """ wire_descriptor """
    function = 'wire'

    def __init__(self):
        self.shape = None
        self.net = None
        self.clearance = None
        self.wire_type = None

    def parse(self, args):
        assert len(args) >= 1
        self.shape = pop_type(args, ShapeBase)
        self.net = pop_type(args, Net)
        self.clearance = pop_type(args, ClearanceClass)
        self.wire_type = pop_type(args, Type)
        assert_empty(self, args)

    def compose(self):
        return [
            self.function,
            self.shape and self.shape.compose(),
            self.net and self.net.compose(),
            self.clearance and self.clearance.compose(),
            self.wire_type and self.wire_type.compose()
        ]

class Type:
    """ type for misc places """
    function = 'type'

    def __init__(self):
        self.value = None

    def parse(self, args):
        assert len(args) == 1
        self.value = pop_string(args)
        assert_empty(self, args)

    def compose(self):
        return [self.function, self.value]

class Property:
    function = 'property'

    def __init__(self):
        self.index = None

    def parse(self, args):
        assert len(args) >= 1
        self.index = pop_type(args, Index)
        assert_empty(self, args)

    def compose(self):
        return [
            self.function,
            self.index and self.index.compose()
        ]

class Index:
    function = 'index'

    def __init__(self):
        self.value = None

    def parse(self, args):
        assert len(args) == 1
        self.value = pop_string(args)
        assert_empty(self, args)

    def compose(self):
        return [self.function, self.value]

class Layer:
    function = 'layer'

    def __init__(self):
        self.layer_id = 'signal'
        self.ltype = None
        self.lproperty = None

    def parse(self, args):
        assert len(args) >= 1
        self.layer_id = pop_string(args)
        self.ltype = pop_type(args, Type)
        self.lproperty = pop_type(args, Property)
        assert_empty(self, args)

    def compose(self):
        return [
            self.function,
            self.layer_id,
            self.ltype.compose(),
            self.lproperty and self.lproperty.compose(),
        ]


class WireVia:
    """ wire_via_descriptor """
    #function = 'via'

    def __init__(self):
        self.padstack_id = None
        self.vertex = (None, None)
        self.net = None
        self.via_type = None
        self.clearance = None

    def parse(self, args):
        assert len(args) >= 1
        self.padstack_id = pop_string(args)
        self.vertex = pop_vertex(args)
        self.net = pop_type(args, Net)
        self.via_type = pop_type(args, Type)
        self.clearance = pop_type(args, ClearanceClass)
        assert_empty(self, args)

    def compose(self):
        return [
            'via', 
            self.padstack_id,
            self.vertex[0], self.vertex[1],
            self.net and self.net.compose(),
            self.via_type and self.via_type.compose(),
            self.clearance.compose()
        ]

##############################################################

ALL_FUNCTIONS = dict([(s.function, s) for s in globals().values() if isclass(s) and getattr(s, 'function', None)])

def lookup(funcname):
    """ Return class for given function name """
    return ALL_FUNCTIONS.get(funcname, None)
