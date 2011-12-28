#!/usr/bin/env python
""" The design class """

from core.design_attributes import DesignAttributes
from core.components import Components
from core.shape import Point


class Design:
    """ The Design class represents the whole schematic, which is also
    the top level of the output format.  The internal structure of this
    class closely matches the JSON output."""

    def __init__(self):
        self.nets = list()
        self.components = Components()
        self.component_instances = list()
        self.design_attributes = DesignAttributes()
        self.version = dict()
        self.set_version("0.1.0","Upverter converter")


    def bounds(self):
        """ Return the min and max point of a design """
        bounds = [net.bounds() for net in self.nets]
        bounds.extend([anno.bounds() for anno in
                       self.design_attributes.annotations])
        offset_bounds = lambda (p1, p2), (xo, yo): [Point(p1.x + xo, p1.y + yo),
                                                    Point(p2.x + xo, p2.y + yo)]
        for comp in self.component_instances:
            offsets = [(att.x, att.y) for att in comp.symbol_attributes]
            lib_comp = self.components.components[comp.library_id]
            bodybounds = [b.bounds() for b in
                          lib_comp.symbols[comp.symbol_index].bodies]
            # the offsets in symbol_attributes will align and apply to the
            # library components bodies
            bounds.extend([offset_bounds(b, o) for b, o in zip(bodybounds,
                                                               offsets)])
        # flatten out bounds to just a list of Points
        bounds = sum(bounds, [])
        x_values = [pt.x for pt in bounds]
        y_values = [pt.y for pt in bounds]
        # by convention, an empty design will bound just the origin
        if len(x_values) == 0:
            x_values = [0]
            y_values = [0]
        return [Point(min(x_values), min(y_values)),
                Point(max(x_values), max(y_values))]


    def set_version(self, file_version, exporter):
        """ Set the file version and exporter """
        self.version['file_version'] = file_version
        self.version['exporter'] = exporter


    def add_component_instance(self, component_instance):
        """ Add an instance """
        self.component_instances.append(component_instance)


    def add_component(self, library_id, component):
        """ Add a library part """
        self.components.add_component(library_id, component)


    def add_net(self, net):
        """ Add a net """
        self.nets.append(net)


    def set_design_attributes(self, design_attributes):
        """ Add design level attributes """
        self.design_attributes = design_attributes


    def generate_netlist(self):
        """ The netlist as generated from the schematic. """
        pass


    def generate_bom(self):
        """ The bill of materials as generated from the schematic. """
        pass


    def json(self):
        """ Return a design as JSON """
        return {
            "version" : self.version,
            "nets" : [n.json() for n in self.nets],
            "components" : self.components.json(),
            "component_instances" :
                [i.json() for i in self.component_instances],
            "design_attributes" : self.design_attributes.json()
            }


