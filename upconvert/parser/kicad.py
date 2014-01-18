#!/usr/bin/env python2
""" The KiCAD Format Parser """

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


# Basic Strategy
# 0) Ignore data except the useful
# 1) Read in all of the segments (and junctions and components)
# 2) Divide all the segments by the junctions
# 3) Calculate the nets from the segments
# 4) Read the part library to figure out components and pin connectivity
#
# Note: in a KiCAD schematic, the y coordinates increase downwards. In
# OpenJSON, y coordinates increase upwards, so we negate them. In the
# KiCAD library file (where components are stored) y coordinates
# increase upwards as in OpenJSON and no transformation is needed.
# KiCAD units are mils (1/1000th of an inch)

from upconvert.core.design import Design
from upconvert.core.components import Component, Symbol, SBody, Pin
from upconvert.core.component_instance import ComponentInstance, SymbolAttribute
from upconvert.core.net import Net, NetPoint, ConnectedComponent
from upconvert.core.shape import Arc, Circle, Line, Rectangle, Label
from upconvert.core.annotation import Annotation

from upconvert.library.kicad import lookup_part

from os.path import split
from os import listdir

MULT = 2.0 / 10.0 # mils to 90 dpi


class KiCAD(object):
    """ The KiCAD Format Parser """

    library = None

    @staticmethod
    def auto_detect(filename):
        """ Return our confidence that the given file is an kicad schematic """
        with open(filename, 'r') as f:
            data = f.read(4096)
        confidence = 0
        if 'EESchema Schematic' in data:
            confidence += 0.75
        return confidence


    def parse(self, filename, library_filename=None):
        """ Parse a kicad file into a design """

        design = Design()
        segments = set() # each wire segment
        junctions = set() # wire junction point (connects all wires under it)

        self.instance_names = []

        self.library = KiCADLibrary()

        if library_filename is None:
            directory, _ = split(filename)
            for dir_file in listdir(directory):
                if dir_file.endswith('.lib'):
                    self.library.parse(directory + '/' + dir_file)

        for cpt in self.library.components:
            design.add_component(cpt.name, cpt)

        with open(filename) as f:
            libs = []
            line = f.readline().strip()

            # parse the library references
            while line and line != "$EndDescr":
                if line.startswith('LIBS:'):
                    libs.extend(line.split(':', 1)[1].split(','))
                line = f.readline().strip()

            # Now parse wires and components, ignore connections, we get
            # connectivity from wire segments

            line = f.readline()

            while line:
                prefix = line.split()[0]

                if line.startswith('Wire Wire Line'):
                    self.parse_wire(f, segments)
                elif prefix == "Connection": # Store these to apply later
                    self.parse_connection(line, junctions)
                elif prefix == "Text":
                    design.design_attributes.add_annotation(
                        self.parse_text(f, line))
                elif prefix == "$Comp": # Component Instance
                    inst, comp = self.parse_component_instance(f)
                    design.add_component_instance(inst)
                    if comp is not None:
                        design.add_component(comp.name, comp)
                    self.ensure_component(design, inst.library_id, libs)

                line = f.readline()

        segments = self.divide(segments, junctions)
        design.nets = self.calc_nets(design, segments)

        design.scale(MULT)

        return design


    def ensure_component(self, design, name, libs):
        """
        Add a component to the design, it if is not already present.
        """

        if self.library is not None \
                and self.library.lookup_part(name) is not None:
            return

        cpt = lookup_part(name, libs)

        if cpt is None:
            return

        if cpt.name not in design.components.components:
            design.components.add_component(cpt.name, cpt)


    def parse_wire(self, f, segments):
        """ Parse a Wire segment line """
        x1, y1, x2, y2 = [int(i) for i in f.readline().split()]

        if not(x1 == x2 and y1 == y2): # ignore zero-length segments
            segments.add(((x1, -y1), (x2, -y2)))


    def parse_connection(self, line, junctions):
        """ Parse a Connection line """
        x, y = [int(i) for i in line.split()[2:4]]
        junctions.add((x, -y))


    def parse_text(self, f, line):
        """ Parse a Text line """
        parts = line.split()
        x, y, rotation = int(parts[2]), int(parts[3]), int(parts[4])
        rotation = rotation / 2.0
        value = f.readline().decode('utf-8', 'replace').strip()
        return Annotation(value, x, -y, rotation, 'true')


    def parse_field(self, compx, compy, line):
        """ Parse a field (F) line in a component block """
        parts = line.rsplit('"', 1)
        value = parts[0].split('"', 1)[1].decode('utf-8', 'replace')
        parts = parts[1].strip().split()

        return Annotation(value,
                          int(parts[1]) - compx,
                          -(int(parts[2]) - compy),
                          0 if parts[0] == 'H' else 1, 'true')


    def parse_component_instance(self, f):
        """ Parse a component instance from a $Comp block """
        # pylint: disable=R0914

        # name & reference
        prefix, name, reference = f.readline().split()
        assert prefix == 'L'

        ref_count_idx = 1
        while reference in self.instance_names:
            ref_count_idx += 1
            reference = reference + '-' + str(ref_count_idx)

        self.instance_names.append(reference)

        comp = None
        if self.library is not None:
            library_part = self.library.lookup_part(name)
            if library_part is not None:
                name = library_part.name

        # unit & convert
        prefix, unit, convert, ar_path = f.readline().split(None, 3)
        unit, convert = int(unit), int(convert)
        assert prefix == 'U'

        # position
        prefix, compx, compy = f.readline().split()
        assert prefix == 'P'
        compx, compy = int(compx), int(compy)

        line = f.readline()
        rotation = 0
        flip = False
        annotations = []

        while line.strip() not in ("$EndComp", ''):
            if line.startswith('F '):
                annotations.append(self.parse_field(compx, compy, line))
            elif line.startswith('\t'):
                parts = line.strip().split()
                if len(parts) == 4:
                    rotation, flip = MATRIX2ROTATIONFLIP.get(
                        tuple(int(i) for i in parts), (0, False))
            elif line.startswith('AR Path'):
                if '?' in reference:
                    path_line = line.strip().split()
                    ar_path_check = path_line[1].strip('"')[7:] #removes Path="/
                    if ar_path.strip() == ar_path_check:
                        reference = path_line[2].strip('"')[5:] #removes Ref="

            line = f.readline()

        inst = ComponentInstance(reference, library_part, name.upper(), convert - 1)
        symbattr = SymbolAttribute(compx, -compy, rotation, flip)
        for ann in annotations:
            symbattr.add_annotation(ann)
        inst.add_symbol_attribute(symbattr)

        return inst, comp


    def intersect(self, segment, ptc):
        """ Does point c intersect the segment """
        pta, ptb = segment
        ptax, ptay, ptbx, ptby, ptcx, ptcy = pta + ptb + ptc
        if ptax == ptbx == ptcx: # Vertical
            if min(ptay, ptby) < ptcy < max(ptay, ptby): # between a and b
                return True
        elif ptay == ptby == ptcy: # Horizontal
            if min(ptax, ptbx) < ptcx < max(ptax, ptbx): # between a and b
                return True
        elif (ptcx-ptax)*(ptby-ptay)==(ptbx-ptax)*(ptcy-ptay): # Diagonal
            if min(ptax, ptbx) < ptcx < max(ptax, ptbx): # between a and b
                return True
        return False


    def divide(self, segments, junctions):
        """ Divide segments by junctions """
        for ptc in junctions:
            toremove = set()
            toadd = set()
            for seg in segments:
                if self.intersect(seg, ptc):
                    pta, ptb = seg
                    toremove.add((pta, ptb))
                    toadd.add((pta, ptc))
                    toadd.add((ptc, ptb))
            segments -= toremove
            segments |= toadd
        return segments


    def calc_nets(self, design, segments):
        """ Return a set of Nets from segments """

        coord2point = {} # (x, y) -> NetPoint

        def get_point(coord):
            """ Return a new or existing NetPoint for an (x,y) point """
            coord = (int(coord[0]), int(coord[1]))
            if coord not in coord2point:
                coord2point[coord] = NetPoint('%da%d' % coord, coord[0], coord[1])
            return coord2point[coord]

        # use this to track connected pins not yet added to a net
        self.make_pin_points(design, get_point)

        # set of points connected to pins
        pin_points = set(coord2point.itervalues())

        # turn the (x, y) points into unique NetPoint objects
        segments = set((get_point(p1), get_point(p2)) for p1, p2 in segments)
        nets = []

        # Iterate over the segments, removing segments when added to a net
        while segments:
            seg = segments.pop() # pick a point
            newnet = Net('')
            map(pin_points.discard, seg) # mark points as used
            newnet.connect(seg)
            found = True

            while found:
                found = set()

                for seg in segments: # iterate over segments
                    if newnet.connected(seg): # segment touching the net
                        map(pin_points.discard, seg) # mark points as used
                        newnet.connect(seg) # add the segment
                        found.add(seg)

                for seg in found:
                    segments.remove(seg)

            nets.append(newnet)

        # add single-point nets for overlapping pins that are not
        # already in other nets
        for point in pin_points:
            if len(point.connected_components) > 1:
                net = Net('')
                net.add_point(point)
                nets.append(net)

        for net in nets:
            net.net_id = min(net.points)

        nets.sort(key=lambda net : net.net_id)

        return nets


    def make_pin_points(self, design, point_factory):
        """ Construct a set of NetPoints connected to pins. """

        for inst in design.component_instances:
            if inst.library_id in design.components.components:
                cpt = design.components.components[inst.library_id]
                for symba, body in zip(inst.symbol_attributes,
                                       cpt.symbols[inst.symbol_index].bodies):
                    for pin in body.pins:
                        point = point_factory(self.get_pin_coord(pin, symba))
                        point.add_connected_component(
                            ConnectedComponent(inst.instance_id, pin.pin_number))


    def get_pin_coord(self, pin, symba):
        """ Return the x, y coordinate of a pin on a symbol attribute """

        x, y = pin.p2.x, pin.p2.y

        matrix = ROTFLIP2MATRIX.get((symba.rotation, symba.flip), ROTFLIP2MATRIX[(0, False)])

        x, y = (matrix[0] * x + matrix[1] * y,
                matrix[2] * x + matrix[3] * y)

        return symba.x + x, symba.y - y


# map kicad rotation matrices to pi radians
#TODO: add flip
MATRIX2ROTATIONFLIP = {(1, 0, 0, -1): (0, False),
                   (0, 1, 1, 0): (0.5, False),
                   (-1, 0, 0, 1): (1, False),
                   (0, -1, -1, 0): (1.5, False),
                   (0, 1, -1, 0): (0.5, True),
                   (0, -1, 1, 0): (1.5, True),
                   (1, 0, 0, 1): (1, True),
                   (-1, 0, 0, -1): (0, True)}

# map openjson rotations to rotation matrices
ROTFLIP2MATRIX = dict((v, k) for k, v in MATRIX2ROTATIONFLIP.iteritems())


class KiCADLibrary(object):
    """
    I represent a library of kicad parts.
    """

    def __init__(self):
        self.components = []
        self.name2cpt = {}

    def lookup_part(self, name):
        """
        Return a kicad component by name, or None if not found.
        """

        return self.name2cpt.get(name.upper())

    def __getitem__(self, name):
        return self.lookup_part(name)

    def __contains__(self, name):
        return self.lookup_part(name) != None

    def parse(self, filename):
        """
        Parse the library file, and update the KiCADLibrary.
        """

        new_components = []

        with open(filename) as f:
            for line in f:
                if line.startswith('DEF '):
                    new_components.append(ComponentParser(line).parse(f))

        for new_component in new_components:
            new_component.name = new_component.name.upper()
            if new_component.name not in self.name2cpt:
                self.name2cpt[new_component.name] = new_component
                self.components.append(new_component)
                if 'kicad_alias' in new_component.attributes:
                    for name in new_component.attributes['kicad_alias'].split():
                        self.name2cpt[name.upper()] = new_component


class ComponentParser(object):
    """I parse components from KiCAD libraries."""

    # the column positions of the unit and convert fields
    unit_cols = dict(A=6, C=4, P=2, S=5, T=6, X=9)
    convert_cols = dict((k, v+1) for k, v in unit_cols.items())

    def __init__(self, line):
        parts = line.split()
        name = parts[1]
        if name.startswith('~'):
            name = name[1:]
        self.component = Component(name)
        self.component.add_attribute('_prefix', parts[2])
        self.num_units = max(int(parts[7]), 1)


    def build_symbols(self, has_convert):
        """ Build all Symbols and Bodies for this component. The
        has_convert argument should be True if there are DeMorgan
        convert bodies. """

        for _ in range(2 if has_convert else 1):
            symbol = Symbol()
            for _ in range(self.num_units):
                symbol.add_body(SBody())
            self.component.add_symbol(symbol)


    def iter_bodies(self, unit, convert, has_convert):
        """ Return an iterator over all the bodies implied by the
        given unit and convert options. A unit of 0 means all units
        for the given convert. A convert of 0 means both converts for
        the given unit. If both are 0 it applies to all bodies."""

        if convert == 0 and has_convert:
            symbol_indices = [0, 1] # both regular and convert
        elif convert in (0, 1):
            symbol_indices = [0] # just regular
        else:
            symbol_indices = [1] # just convert

        if unit == 0:
            body_indices = range(self.num_units) # all bodies
        else:
            body_indices = [unit-1] # one body

        for symbol_index in symbol_indices:
            for body_index in body_indices:
                try:
                    yield self.component.symbols[symbol_index].bodies[body_index]
                except IndexError:
                    pass

    def parse(self, f):
        """ Parse a DEF block and return the Component """

        draw_lines = [] # (unit, convert, prefix, parts)

        for line in f:
            parts = line.split()
            prefix = parts[0]

            if prefix in ('A', 'C', 'P', 'S', 'T', 'X'):
                draw_lines.append((int(parts[self.unit_cols[prefix]]),
                                           int(parts[self.convert_cols[prefix]]),
                                           prefix, parts))
            elif prefix == 'ALIAS':
                self.component.add_attribute('kicad_alias', ' '.join(parts[1:]))
            elif prefix == 'ENDDEF':
                break

        has_convert = any(convert == 2 for _, convert, _, _ in draw_lines)

        self.build_symbols(has_convert)

        for unit, convert, prefix, parts in draw_lines:
            method = getattr(self, 'parse_%s_line' % (prefix.lower(),))

            for body in self.iter_bodies(unit, convert, has_convert):
                obj = method(parts)

                if prefix == 'X':
                    body.add_pin(obj)
                else:
                    if isinstance(obj, (list, tuple)):
                        for o in obj:
                            body.add_shape(o)
                    else:
                        body.add_shape(obj)

        for symbol in self.component.symbols:
            for body in symbol.bodies:
                body.pins.sort(key=lambda pin : pin.pin_number)

        return self.component


    def parse_a_line(self, parts):
        """ Parse an A (Arc) line """
        x, y, radius, start, end = [int(i) for i in parts[1:6]]
        # convert tenths of degrees to pi radians
        start = start / 1800.0
        end = end / 1800.0
        return Arc(x, y, end, start, radius)


    def parse_c_line(self, parts):
        """ Parse a C (Circle) line """
        x, y, radius = [int(i) for i in parts[1:4]]
        return Circle(x, y, radius)


    def parse_p_line(self, parts):
        """ Parse a P (Polyline) line """
        num_points = int(parts[1])
        lines = []
        last_point = None
        for i in xrange(num_points):
            point = int(parts[5 + 2 * i]), int(parts[6 + 2 * i])
            if last_point is not None:
                lines.append(Line(last_point, point))
            last_point = point
        return lines


    def parse_s_line(self, parts):
        """ Parse an S (Rectangle) line """
        x, y, x2, y2 = [int(i) for i in parts[1:5]]
        return Rectangle(x, y, x2 - x, y - y2)


    def parse_t_line(self, parts):
        """ Parse a T (Text) line """
        angle, x, y = [int(i) for i in parts[1:4]]
        angle = angle / 1800.0
        text = parts[8].replace('~', ' ')

        if len(parts) >= 12:
            align = {'C': 'center', 'L': 'left', 'R': 'right'}.get(parts[11])
        else:
            align = 'left'

        return Label(x, y, text, align=align, rotation=angle)


    def parse_x_line(self, parts):
        """ Parse an X (Pin) line """
        name, num, direction = parts[1], parts[2], parts[6]
        p2x, p2y, pinlen = int(parts[3]), int(parts[4]), int(parts[5])

        if direction == 'U': # up
            p1x = p2x
            p1y = p2y + pinlen
            label_x = p2x - 20
            label_y = p2y + int(pinlen / 2)
            label_rotation = 1.5
        elif direction == 'D': # down
            p1x = p2x
            p1y = p2y - pinlen
            label_x = p2x - 20
            label_y = p2y - int(pinlen / 2)
            label_rotation = 1.5
        elif direction == 'L': # left
            p1x = p2x - pinlen
            p1y = p2y
            label_x = p2x - int(pinlen / 2)
            label_y = p2y + 20
            label_rotation = 0
        elif direction == 'R': # right
            p1x = p2x + pinlen
            p1y = p2y
            label_x = p2x + int(pinlen / 2)
            label_y = p2y + 20
            label_rotation = 0
        else:
            raise ValueError('unexpected pin direction', direction)

        if name == '~':
            label = None
        else:
            label = Label(label_x, label_y,
                          name, align='center', rotation=label_rotation)

        return Pin(num, (p1x, p1y), (p2x, p2y), label)
