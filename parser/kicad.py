""" The KiCAD Format Parser """

# Basic Strategy
# 0) Ignore data except the useful
# 1) Read in all of the segments (and junctions and components)
# 2) Divide all the segments by the junctions
# 3) Calculate the nets from the segments
# 4) Read the part library to figure out pin connectivity [TODO]

from core.design import Design
from core.components import Component, Symbol, Body, Pin
from core.component_instance import ComponentInstance, SymbolAttribute
from core.net import Net, NetPoint
from core import shape

from os.path import exists, splitext


class KiCAD(object):
    """ The KiCAD Format Parser """

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
            element = line.split()[0] # whats next on the list

            if element == "Wire":
                self.parse_wire(f, segments)
            elif element == "Connection": # Store these to apply later
                self.parse_connection(line, junctions)
            elif element == "$Comp": # Component Instance
                circuit.add_component_instance(
                    self.parse_component_instance(f))

            line = f.readline()

        f.close()

        segments = self.divide(segments, junctions)
        circuit.nets = self.calc_nets(segments)

        return circuit


    def parse_wire(self, f, segments):
        """ Parse a Wire segment line """
        # coords on 2nd line
        x1, y1, x2, y2 = [int(i) for i in f.readline().split()]

        if not(x1 == x2 and y1 == y2): # ignore zero-length segments
            segments.add(((x1, y1),(x2, y2)))


    def parse_connection(self, line, junctions):
        """ Parse a Connection line """
        x, y = [int(i) for i in line.split()[2:4]]
        junctions.add((x, y))


    def parse_component_instance(self, f):
        """ Parse a component instance from a $Comp block """
        # name & reference
        prefix, name, reference = f.readline().split()
        assert prefix == 'L'

        # timestamp
        prefix, _ = f.readline().split(None, 1)
        assert prefix == 'U'

        # position
        prefix, compx, compy = f.readline().split()
        assert prefix == 'P'
        compx, compy = int(compx), int(compy)

        # TODO(ajray): ignore all the fields for now, probably
        # could make these annotations

        line = f.readline()
        rotation = 0

        while line.strip() not in ("$EndComp", ''):
            if line.startswith('\t'):
                parts = line.strip().split()
                if len(parts) == 4:
                    key = tuple(int(i) for i in parts)
                    rotation = MATRIX2ROTATION.get(key, 0)
            line = f.readline()

        inst = ComponentInstance(reference, name, 0)
        inst.add_symbol_attribute(SymbolAttribute(compx, compy, rotation))

        return inst

    def parse_library(self, filename, circuit):
        """
        Parse the library file and add the components to the given
        circuit.
        """

        f = open(filename)

        for line in f:
            parts = line.strip().split()
            prefix = parts[0]

            if prefix == 'DEF':
                component = Component(parts[1])
                component.add_attribute('_prefix', parts[2])
                symbol = Symbol()
                component.add_symbol(symbol)
                body = Body()
                symbol.add_body(body)
            elif prefix == 'A': # Arc
                body.add_shape(self.parse_arc(parts))
            elif prefix == 'C': # Circle
                body.add_shape(self.parse_circle(parts))
            elif prefix == 'P': # Polyline
                body.add_shape(self.parse_polyline(parts))
            elif prefix == 'S': # Rectangle
                body.add_shape(self.parse_rectangle(parts))
            elif prefix == 'T': # Text
                body.add_shape(self.parse_text(parts))
            elif prefix == 'X': # Pin
                body.add_pin(self.parse_pin(parts))
            elif prefix == 'ENDDEF':
                circuit.add_component(component.name, component)

        f.close()


    def parse_arc(self, parts):
        """ Parse an A (Arc) line """
        x, y, radius, start, end = [int(i) for i in parts[1:6]]
        # convert tenths of degrees to pi radians
        start = start / 1800.0
        end = end / 1800.0
        return shape.Arc(x, y, start, end, radius)


    def parse_circle(self, parts):
        """ Parse a C (Circle) line """
        x, y, radius = [int(i) for i in parts[1:4]]
        return shape.Circle(x, y, radius)


    def parse_polyline(self, parts):
        """ Parse a P (Polyline) line """
        num_points = int(parts[1])
        poly = shape.Polygon()
        for i in xrange(num_points):
            x, y = int(parts[5 + 2 * i]), int(parts[6 + 2 * i])
            poly.add_point(x, y)
        return poly


    def parse_rectangle(self, parts):
        """ Parse an S (Rectangle) line """
        x, y, x2, y2 = [int(i) for i in parts[1:5]]
        return shape.Rectangle(x, y, x2 - x, y2 - y)


    def parse_text(self, parts):
        """ Parse a T (Text) line """
        angle, x, y = [int(i) for i in parts[1:4]]
        angle = angle / 1800.0
        text = parts[8].replace('~', ' ')
        align = {'C': 'center', 'L': 'left', 'R': 'right'}.get(parts[11])
        return shape.Label(x, y, text, align, angle)


    def parse_pin(self, parts):
        """ Parse an X (Pin) line """
        num, direction = parts[2], parts[6]
        p2x, p2y, pinlen = int(parts[3]), int(parts[4]), int(parts[5])
        if direction == 'U': # up
            p1x = p2x
            p1y = p2y - pinlen
        elif direction == 'D': # down
            p1x = p2x
            p1y = p2y + pinlen
        elif direction == 'L': # left
            p1x = p2x - pinlen
            p1y = p2y
        elif direction == 'R': # right
            p1x = p2x + pinlen
            p1y = p2y
        else:
            raise ValueError('unexpected pin direction', direction)
        # TODO: label?
        return Pin(num, (p1x, p1y), (p2x, p2y))


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


MATRIX2ROTATION = {(1, 0, 0, -1): 0,
                   (0, 1, 1, 0): 0.5,
                   (-1, 0, 0, 1): 1,
                   (0, -1, -1, 0): 1.5}
