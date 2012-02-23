#!/usr/bin/env python2
""" The KiCAD Format Parser """

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

from core.design import Design
from core.components import Component, Symbol, Body, Pin
from core.component_instance import ComponentInstance, SymbolAttribute
from core.net import Net, NetPoint, ConnectedComponent
from core.shape import Arc, Circle, Polygon, Rectangle, Label
from core.annotation import Annotation

from collections import defaultdict
from os.path import exists, splitext


class KiCAD(object):
    """ The KiCAD Format Parser """

    @staticmethod
    def auto_detect(filename):
        """ Return our confidence that the given file is an kicad schematic """
        f = open(filename, 'r')
        data = f.readline()
        f.close()
        confidence = 0
        if 'EESchema Schematic' in data:
            confidence += 0.75
        return confidence


    def parse(self, filename, library_filename=None):
        """ Parse a kicad file into a design """

        # Rough'n'dirty parsing, assume nothing useful comes before
        # the description
        circuit = Design()
        segments = set() # each wire segment
        junctions = set() # wire junction point (connects all wires under it)

        if library_filename is None:
            library_filename = splitext(filename)[0] + '-cache.lib'
            if exists(library_filename):
                self.parse_library(library_filename, circuit)

        f = open(filename)

        # Read until the end of the description
        while f.readline().strip() != "$EndDescr":
            pass

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
                circuit.design_attributes.add_annotation(
                    self.parse_text(f, line))
            elif prefix == "$Comp": # Component Instance
                circuit.add_component_instance(self.parse_component_instance(f))

            line = f.readline()

        f.close()

        segments = self.divide(segments, junctions)
        circuit.nets = self.calc_nets(segments)
        self.calc_connected_components(circuit)

        return circuit


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
        rotation = rotation / 1800.0
        value = f.readline().decode('utf-8', errors='replace').strip()
        return Annotation(value, make_length(x), -make_length(y),
                          rotation, 'true')

    def parse_component_instance(self, f):
        """ Parse a component instance from a $Comp block """
        # pylint: disable=R0914

        # name & reference
        prefix, name, reference = f.readline().split()
        assert prefix == 'L'

        # unit & convert
        prefix, unit, convert, _ = f.readline().split(None, 3)
        unit, convert = int(unit), int(convert)
        assert prefix == 'U'

        # position
        prefix, compx, compy = f.readline().split()
        assert prefix == 'P'
        compx, compy = int(compx), int(compy)

        line = f.readline()
        rotation = 0
        annotations = []

        while line.strip() not in ("$EndComp", ''):
            if line.startswith('F '):
                parts = line.split('"', 2)
                value = parts[1].decode('utf-8', errors='replace')
                parts = parts[2].strip().split()
                annotations.append(
                    Annotation(value, make_length(parts[1]),
                               -make_length(parts[2]),
                               0 if parts[0] == 'H' else 1, 'true'))
            elif line.startswith('\t'):
                parts = line.strip().split()
                if len(parts) == 4:
                    rotation = MATRIX2ROTATION.get(
                        tuple(int(i) for i in parts), 0)
            line = f.readline()

        inst = ComponentInstance(reference, name, convert - 1)
        symbattr = SymbolAttribute(make_length(compx), -make_length(compy),
                                   rotation)
        for ann in annotations:
            symbattr.add_annotation(ann)
        inst.add_symbol_attribute(symbattr)

        return inst

    def parse_library(self, filename, circuit):
        """
        Parse the library file and add the components to the given
        circuit.
        """

        f = open(filename)

        for line in f:
            if line.startswith('DEF '):
                cpt = ComponentParser(line).parse(f)
                circuit.add_component(cpt.name, cpt)

        f.close()


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


    def calc_nets(self, segments):
        """ Return a set of Nets from segments """

        points = {} # (x, y) -> NetPoint

        def get_point(point):
            """ Return a new or existing NetPoint for an (x,y) point """
            point = (make_length(point[0]), make_length(point[1]))
            if point not in points:
                points[point] = NetPoint('%da%d' % point, point[0], point[1])
            return points[point]

        # turn the (x, y) points into unique NetPoint objects
        segments = set((get_point(p1), get_point(p2)) for p1, p2 in segments)
        nets = []

        # Iterate over the segments, removing segments when added to a net
        while segments:
            seg = segments.pop() # pick a point
            newnet = Net('')
            newnet.connect(seg)
            found = True

            while found:
                found = set()

                for seg in segments: # iterate over segments
                    if newnet.connected(seg): # segment touching the net
                        newnet.connect(seg) # add the segment
                        found.add(seg)

                for seg in found:
                    segments.remove(seg)

            nets.append(newnet)

        return nets


    def calc_connected_components(self, circuit):
        """ Add all the connected components to the nets """

        pins = defaultdict(set) # (x, y) -> set([(instance_id, pin_number)])

        for inst in circuit.component_instances:
            if inst.library_id in circuit.components.components:
                cpt = circuit.components.components[inst.library_id]
                for symba, body in zip(inst.symbol_attributes,
                                       cpt.symbols[inst.symbol_index].bodies):
                    for pin in body.pins:
                        pins[symba.x + pin.p2.x, symba.y - pin.p2.y].add(
                            (inst.instance_id, pin.pin_number))

        for net in circuit.nets:
            for point in net.points.values():
                for instance_id, pin_number in pins.get((point.x, point.y), ()):
                    conncpt = ConnectedComponent(instance_id, pin_number)
                    point.add_connected_component(conncpt)


# map kicad rotation matrices to pi radians
MATRIX2ROTATION = {(1, 0, 0, -1): 0,
                   (0, 1, 1, 0): 0.5,
                   (-1, 0, 0, 1): 1,
                   (0, -1, -1, 0): 1.5}


class ComponentParser(object):
    """I parse components from KiCAD libraries."""

    # the column positions of the unit and convert fields
    unit_cols = dict(A=6, C=4, P=2, S=5, T=6, X=9)
    convert_cols = dict((k, v+1) for k, v in unit_cols.items())

    def __init__(self, line):
        parts = line.split()
        self.component = Component(parts[1])
        self.component.add_attribute('_prefix', parts[2])
        self.num_units = int(parts[7])


    def build_symbols(self, has_convert):
        """ Build all Symbols and Bodies for this component. The
        has_convert argument should be True if there are DeMorgan
        convert bodies. """

        for _ in range(2 if has_convert else 1):
            symbol = Symbol()
            for _ in range(self.num_units):
                symbol.add_body(Body())
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
                yield self.component.symbols[symbol_index].bodies[body_index]


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
                    body.add_shape(obj)

        return self.component


    def parse_a_line(self, parts):
        """ Parse an A (Arc) line """
        x, y, radius, start, end = [int(i) for i in parts[1:6]]
        # convert tenths of degrees to pi radians
        start = start / 1800.0
        end = end / 1800.0
        return Arc(make_length(x), make_length(y),
                   start, end, make_length(radius))


    def parse_c_line(self, parts):
        """ Parse a C (Circle) line """
        x, y, radius = [int(i) for i in parts[1:4]]
        return Circle(make_length(x), make_length(y), make_length(radius))


    def parse_p_line(self, parts):
        """ Parse a P (Polyline) line """
        num_points = int(parts[1])
        poly = Polygon()
        for i in xrange(num_points):
            x, y = int(parts[5 + 2 * i]), int(parts[6 + 2 * i])
            poly.add_point(make_length(x), make_length(y))
        return poly


    def parse_s_line(self, parts):
        """ Parse an S (Rectangle) line """
        x, y, x2, y2 = [int(i) for i in parts[1:5]]
        return Rectangle(make_length(x), make_length(y),
                         make_length(x2 - x), make_length(y2 - y))


    def parse_t_line(self, parts):
        """ Parse a T (Text) line """
        angle, x, y = [int(i) for i in parts[1:4]]
        angle = angle / 1800.0
        text = parts[8].replace('~', ' ')
        align = {'C': 'center', 'L': 'left', 'R': 'right'}.get(parts[11])
        return Label(make_length(x), make_length(y), text, align, angle)


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
            label = Label(make_length(label_x), make_length(label_y),
                          name, 'center', label_rotation)

        return Pin(num,
                   (make_length(p1x), make_length(p1y)),
                   (make_length(p2x), make_length(p2y)), label)


MULT = 90.0 / 1000.0 # mils to 90 dpi

def make_length(value):
    """ Make a length measurement from a kicad measurement """
    return int(round(float(value) * MULT))
