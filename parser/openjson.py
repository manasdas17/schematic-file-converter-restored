#!/usr/bin/env python
""" The Open JSON Format Parser """

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
# 0) 1:1 Input of the data model

import json
from core.annotation import Annotation
from core.component_instance import ComponentInstance, SymbolAttribute
from core.components import Component, Symbol, Body, Pin
from core.design import Design
from core.design_attributes import DesignAttributes, Metadata
from core.shape import Rectangle, RoundedRectangle, Arc, Circle, Label, Line, Polygon, BezierCurve, Point
from core.net import Net, NetPoint, ConnectedComponent


class JSON:
    """ The Open JSON Format Parser
    This is mostly for sanity checks, it reads in the Open JSON format,
    and then outputs it. """

    def __init__(self):
        self.design = Design()


    def parse(self, filename):
        """ Parse the openjson file into the core. """
        f = open(filename)
        read = json.loads(f.read())
        f.close()

        self.parse_component_instances(read.get('component_instances'))
        self.parse_components(read.get('components'))
        self.parse_design_attributes(read.get('design_attributes'))
        self.parse_nets(read.get('nets'))
        self.parse_version(read.get('version'))

        return self.design


    def parse_version(self, version):
        """ Extract the file version. """
        file_version = version.get('file_version')
        exporter = version.get('exporter')
        self.design.set_version(file_version, exporter)


    def parse_component_instances(self, component_instances):
        """ Extract the component instances. """
        for instance in component_instances:
            # Get instance_id, library_id and symbol_index
            instance_id = instance.get('instance_id')
            library_id = instance.get('library_id')
            symbol_index = int(instance.get('symbol_index'))
            # Make the ComponentInstance()
            inst = ComponentInstance(instance_id, library_id, symbol_index)

            # Get the SymbolAttributes
            for symbol_attribute in instance.get('symbol_attributes'):
                attr = self.parse_symbol_attribute(symbol_attribute)
                inst.add_symbol_attribute(attr)

            # Get the Attributes
            for key, value in instance.get('attributes').items():
                inst.add_attribute(key, value)

            # Add the ComponentInstance
            self.design.add_component_instance(inst)


    def parse_symbol_attribute(self, symbol_attribute):
        """ Extract attributes from a symbol. """
        x = int(symbol_attribute.get('x'))
        y = int(symbol_attribute.get('y'))
        rotation = float(symbol_attribute.get('rotation'))

        # Make SymbolAttribute
        symbol_attr = SymbolAttribute(x, y, rotation)

        # Add Annotations
        for annotation in symbol_attribute.get('annotations'):
            anno = self.parse_annotation(annotation)
            symbol_attr.add_annotation(anno)

        # Return SymbolAttribute to be added to it's ComponentInstance
        return symbol_attr


    def parse_annotation(self, annotation):
        """ Extract an annotation. """
        value = annotation.get('value')
        x = int(annotation.get('x'))
        y = int(annotation.get('y'))
        rotation = float(annotation.get('rotation'))
        visible = annotation.get('visible')
        if visible is not None and visible.lower() == 'false':
            visible = 'false'
        else:
            visible = 'true'
        return Annotation(value, x, y, rotation, visible)


    def parse_components(self, components):
        """ Extract a component library. """
        for library_id, component in components.items():
            name = component.get('name')
            comp = Component(name)
            # Get attributes
            for key, value in component.get('attributes').items():
                comp.add_attribute(key, value)
            for symbol in component.get('symbols'):
                symb = self.parse_symbol(symbol)
                comp.add_symbol(symb)
            self.design.add_component(library_id, comp)


    def parse_symbol(self, symbol):
        """ Extract a symbol. """
        symb = Symbol()
        for body in symbol.get('bodies'):
            bdy = self.parse_body(body)
            symb.add_body(bdy)
        return symb


    def parse_body(self, body):
        """ Extract a body of a symbol. """
        bdy = Body()
        for pin in body.get('pins'):
            parsed_pin = self.parse_pin(pin)
            bdy.add_pin(parsed_pin)
        for shape in body.get('shapes'):
            parsed_shape = self.parse_shape(shape)
            bdy.add_shape(parsed_shape)
        return bdy


    def parse_pin(self, pin):
        """ Extract a pin of a body. """
        pin_number = pin.get('pin_number')
        p1 = self.parse_point(pin.get('p1'))
        p2 = self.parse_point(pin.get('p2'))
        if pin.get('label') is not None:
            pin_label = self.parse_label(pin.get('label'))
            return Pin(pin_number, p1, p2, pin_label)
        return Pin(pin_number, p1, p2)


    def parse_point(self, point):
        """ Extract a point. """
        x = int(point.get('x'))
        y = int(point.get('y'))
        return Point(x, y)

    def parse_label(self, label):
        """ Extract a label. """
        x = int(label.get('x'))
        y = int(label.get('y'))
        text = label.get('text')
        align = label.get('align')
        rotation = float(label.get('rotation'))
        return Label(x, y, text, align, rotation)

    def parse_shape(self, shape):
        """ Extract a shape. """
        # pylint: disable=R0914
        # pylint: disable=R0911

        typ = shape.get('type')
        if 'rectangle' == typ:
            x = int(shape.get('x'))
            y = int(shape.get('y'))
            height = int(shape.get('height'))
            width = int(shape.get('width'))
            return Rectangle(x, y, width, height)
        elif 'rounded_rectangle' == typ:
            x = int(shape.get('x'))
            y = int(shape.get('y'))
            height = int(shape.get('height'))
            width = int(shape.get('width'))
            radius = int(shape.get('radius'))
            return RoundedRectangle(x, y, width, height, radius)
        elif 'arc' == typ:
            x = int(shape.get('x'))
            y = int(shape.get('y'))
            start_angle = float(shape.get('start_angle'))
            end_angle = float(shape.get('end_angle'))
            radius = int(shape.get('radius'))
            return Arc(x, y, start_angle, end_angle, radius)
        elif 'circle' == typ:
            x = int(shape.get('x'))
            y = int(shape.get('y'))
            radius = int(shape.get('radius'))
            return Circle(x, y, radius)
        elif 'label' == typ:
            x = int(shape.get('x'))
            y = int(shape.get('y'))
            rotation = float(shape.get('rotation'))
            text = shape.get('text')
            align = shape.get('align')
            return Label(x, y, text, align, rotation)
        elif 'line' == typ:
            p1 = self.parse_point(shape.get('p1'))
            p2 = self.parse_point(shape.get('p2'))
            return Line(p1, p2)
        elif 'polygon' == typ:
            poly = Polygon()
            for point in shape.get('points'):
                poly.add_point(self.parse_point(point))
            return poly
        elif 'bezier' == typ:
            control1 = self.parse_point(shape.get('control1'))
            control2 = self.parse_point(shape.get('control2'))
            p1 = self.parse_point(shape.get('p1'))
            p2 = self.parse_point(shape.get('p2'))
            return BezierCurve(control1, control2, p1, p2)


    def parse_design_attributes(self, design_attributes):
        """ Extract design attributes. """
        attrs = DesignAttributes()
        # Get the Annotations
        for annotation in design_attributes.get('annotations'):
            anno = self.parse_annotation(annotation)
            attrs.add_annotation(anno)

        # Get the Attributes
        for key, value in design_attributes.get('attributes').items():
            attrs.add_attribute(key, value)

        # Get the Metadata
        meta = self.parse_metadata(design_attributes.get('metadata'))
        attrs.set_metadata(meta)
        self.design.set_design_attributes(attrs)


    def parse_metadata(self, metadata):
        """ Extract design meta-data. """
        meta = Metadata()
        meta.set_name(metadata.get('name'))
        meta.set_license(metadata.get('license'))
        meta.set_owner(metadata.get('owner'))
        meta.set_updated_timestamp(metadata.get('updated_timestamp'))
        meta.set_design_id(metadata.get('design_id'))
        meta.set_description(metadata.get('description'))
        meta.set_slug(metadata.get('slug'))
        for attached_url in metadata.get('attached_urls'):
            meta.add_attached_url(attached_url)
        return meta


    def parse_nets(self, nets):
        """ Extract nets. """
        for net in nets:
            net_id = net.get('net_id')
            ret_net = Net(net_id)
            # Add Annotations
            for annotation in net.get('annotations'):
                anno = self.parse_annotation(annotation)
                ret_net.add_annotation(anno)
            # Get the Attributes
            for key, value in net.get('attributes').items():
                ret_net.add_attribute(key, value)
            # Get the Points
            for net_point in net.get('points'):
                npnt = self.parse_net_point(net_point)
                ret_net.add_point(npnt)
            self.design.add_net(ret_net)


    def parse_net_point(self, net_point):
        """ Extract a net point. """
        point_id = net_point.get('point_id')
        x = int(net_point.get('x'))
        y = int(net_point.get('y'))
        npnt = NetPoint(point_id, x, y)
        # Get the connected points
        for point in net_point.get('connected_points'):
            npnt.add_connected_point(point)
        # Get the ConnectedComponents
        for connectedcomponent in net_point.get('connected_components'):
            conn_comp = self.parse_connected_component(connectedcomponent)
            npnt.add_connected_component(conn_comp)
        return npnt


    def parse_connected_component(self, connectedcomponent):
        """ Extract a connected component. """
        instance_id = connectedcomponent.get('instance_id')
        pin_number = connectedcomponent.get('pin_number')
        return ConnectedComponent(instance_id, pin_number)
