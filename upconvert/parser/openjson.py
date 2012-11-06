#!/usr/bin/env python2
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
import logging
from upconvert.core.annotation import Annotation
from upconvert.core.component_instance import ComponentInstance, SymbolAttribute, FootprintAttribute, GenObjAttribute, FootprintPos
from upconvert.core.components import Component, Symbol, SBody, Pin, FBody, Footprint
from upconvert.core.design import Design
from upconvert.core.design_attributes import DesignAttributes, Metadata
from upconvert.core.generated_object import parse_gen_obj_json, Path
from upconvert.core.shape import Rectangle, RoundedRectangle, Arc, Circle, Label, Line, Polygon, BezierCurve, RoundedSegment, Point
from upconvert.core.net import Net, NetPoint, ConnectedComponent
from upconvert.core.layout import Segment, Layer

log = logging.getLogger('parser.openjson')


class JSON(object):
    """ The Open JSON Format Parser
    This is mostly for sanity checks, it reads in the Open JSON format,
    and then outputs it. """

    def __init__(self):
        self.design = Design()


    @staticmethod
    def auto_detect(filename):
        """ Return our confidence that the given file is an openjson file """
        with open(filename, 'r') as f:
            data = f.read()
        confidence = 0
        if 'component_instances' in data:
            confidence += 0.3
        if 'design_attributes' in data:
            confidence += 0.6
        return confidence


    def parse(self, filename):
        """ Parse the openjson file into the core. """
        log.debug('Starting parse of %s', filename)
        with open(filename) as f:
            read = json.loads(f.read())

        self.parse_components(read.get('components'))
        self.parse_component_instances(read.get('component_instances'))
        if read.get('shapes') is not None:
            self.parse_sch_shapes(read.get('shapes'))
        self.parse_design_attributes(read.get('design_attributes'))
        self.parse_nets(read.get('nets'))
        self.parse_version(read.get('version'))

        # layout aspects
        self.parse_layer_options(read.get('layer_options'))
        self.parse_trace_segments(read.get('trace_segments'))
        self.parse_layout_objects(read.get('gen_objs'))
        self.parse_paths(read.get('paths'))

        return self.design


    def parse_version(self, version):
        """ Extract the file version. """
        file_version = version.get('file_version')
        exporter = version.get('exporter')
        self.design.set_version(file_version, exporter)


    def parse_layer_options(self, layer_options_json):
        if layer_options_json is None:
            return None

        for layer_option_json in layer_options_json:
            self.design.layer_options.append(Layer(layer_option_json['name']))


    def parse_trace_segments(self, segments_json):
        if segments_json is None:
            return None

        for segment_json in segments_json:
            p1 = Point(segment_json['p1']['x'], segment_json['p1']['y'])
            p2 = Point(segment_json['p2']['x'], segment_json['p2']['y'])
            segment = Segment(segment_json['layer'], p1, p2, segment_json['width'])
            self.design.trace_segments.append(segment)


    def parse_paths(self, paths_json):
        if paths_json is None:
            return None

        for path_json in paths_json:
            points = [Point(point_json['x'], point_json['y']) for point_json in path_json['points']]
            width = path_json['width']
            is_closed = path_json['is_closed']
            layer = path_json['layer']
            path = Path(layer, points, width, is_closed)
            self.design.paths.append(path)


    def parse_layout_objects(self, gen_objs_json):
        if gen_objs_json is None:
            return None

        for gen_obj_json in gen_objs_json:
            gen_obj = parse_gen_obj_json(gen_obj_json)
            self.design.layout_objects.append(gen_obj)


    def parse_component_instances(self, component_instances):
        """ Extract the component instances. """

        if component_instances is None:
            return None

        for instance in component_instances:
            # Get instance_id, library_id and symbol_index
            instance_id = instance.get('instance_id')
            library_id = instance.get('library_id')
            symbol_index = int(instance.get('symbol_index'))
            # Make the ComponentInstance()
            inst = ComponentInstance(instance_id, self.design.components.components[library_id], library_id, symbol_index)

            # Get the SymbolAttributes
            for symbol_attribute in instance.get('symbol_attributes', []):
                attr = self.parse_symbol_attribute(symbol_attribute)
                inst.add_symbol_attribute(attr)

            # TODO(shamer) footprint_pos, fleb and genobj positions are relative to the footprint_pos
            for footprint_attribute in instance.get('footprint_attributes', []):
                attr = self.parse_footprint_attribute(footprint_attribute)
                inst.add_footprint_attribute(attr)
            for gen_obj_attribute in instance.get('gen_obj_attributes', []):
                attr = self.parse_gen_obj_attribute(gen_obj_attribute)
                inst.add_gen_obj_attribute(attr)

            footprint_json = instance.get('footprint_pos')
            if footprint_json:
                footprint_pos = self.parse_footprint_pos(footprint_json)
            else:
                footprint_pos = None
            inst.set_footprint_pos(footprint_pos)

            # Get the Attributes
            for key, value in instance.get('attributes').items():
                inst.add_attribute(key, value)

            # Add the ComponentInstance
            self.design.add_component_instance(inst)


    def parse_symbol_attribute(self, symbol_attribute):
        """ Extract attributes from a symbol. """
        x = int(symbol_attribute.get('x') or 0)
        y = int(symbol_attribute.get('y') or 0)

        rotation = float(symbol_attribute.get('rotation'))
        try:
            flip = (symbol_attribute.get('flip').lower() == "true")
        except:
            flip = False

        # Make SymbolAttribute
        symbol_attr = SymbolAttribute(x, y, rotation, flip)

        # Add Annotations
        for annotation in symbol_attribute.get('annotations'):
            anno = self.parse_annotation(annotation)
            symbol_attr.add_annotation(anno)

        # Return SymbolAttribute to be added to its ComponentInstance
        return symbol_attr


    def parse_footprint_attribute(self, footprint_attribute):
        """ Extract attributes from a footprint. """
        x = int(footprint_attribute.get('x') or 0)
        y = int(footprint_attribute.get('y') or 0)

        rotation = float(footprint_attribute.get('rotation'))
        try:
            flip = (footprint_attribute.get('flip').lower() == "true")
        except:
            flip = False

        layer = footprint_attribute.get('layer')

        footprint_attr = FootprintAttribute(x, y, rotation, flip, layer)

        return footprint_attr


    def parse_gen_obj_attribute(self, gen_obj_attribute):
        """ Extract attributes from a gen_obj. """
        x = int(gen_obj_attribute.get('x') or 0)
        y = int(gen_obj_attribute.get('y') or 0)

        rotation = float(gen_obj_attribute.get('rotation'))
        try:
            flip = (gen_obj_attribute.get('flip').lower() == "true")
        except:
            flip = False

        layer = gen_obj_attribute.get('layer')

        gen_obj_attr = GenObjAttribute(x, y, rotation, flip, layer)

        for key, value in gen_obj_attribute.get('attributes').items():
            gen_obj_attr.add_attribute(key, value)

        return gen_obj_attr


    def parse_footprint_pos(self, footprint_pos_json):
        """ Extract footprint pos. """
        x = int(footprint_pos_json.get('x') or 0)
        y = int(footprint_pos_json.get('y') or 0)

        rotation = float(footprint_pos_json.get('rotation', 0))
        flip = footprint_pos_json.get('flip')
        side = footprint_pos_json.get('side')

        return FootprintPos(x, y, rotation, flip, side)


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
            for key, value in component.get('attributes', []).items():
                comp.add_attribute(key, value)
            for symbol_json in component.get('symbols', []):
                symbol = self.parse_symbol(symbol_json)
                comp.add_symbol(symbol)
            for footprint_json in component.get('footprints', []):
                footprint = self.parse_footprint(footprint_json)
                comp.add_footprint(footprint)
            self.design.add_component(library_id, comp)


    def parse_sch_shapes(self, shapes):
        """ Extract shapes drawn directly on the schematic. """
        for shape in shapes:
            self.design.add_shape(self.parse_shape(shape))


    def parse_symbol(self, symbol_json):
        """ Extract a symbol. """
        symb = Symbol()
        for body in symbol_json.get('bodies'):
            bdy = self.parse_symbol_body(body)
            symb.add_body(bdy)
        return symb


    def parse_footprint(self, footprint_json):
        """ Extract the bodies for a footprint. """
        footprint = Footprint()
        for body_json in footprint_json.get('bodies'):
            body = self.parse_footprint_body(body_json)
            footprint.add_body(body)
        for gen_obj_json in footprint_json.get('gen_objs'):
            gen_obj = self.parse_gen_obj(gen_obj_json)
            footprint.add_gen_obj(gen_obj)
        return footprint


    def parse_gen_obj(self, gen_obj_json):
        """ Extract the generated object. """
        gen_obj = parse_gen_obj_json(gen_obj_json)
        return gen_obj


    def parse_footprint_body(self, body_json):
        """ Extract a body of a symbol. """
        body = FBody()
        for shape in body_json.get('shapes'):
            parsed_shape = self.parse_shape(shape)
            body.add_shape(parsed_shape)
        body.layer = body_json.get('layer')
        return body


    def parse_symbol_body(self, body):
        """ Extract a body of a symbol. """
        bdy = SBody()
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
        parsed_pin = Pin(pin_number, p1, p2)
        if pin.get('label') is not None:
            parsed_pin.label = self.parse_label(pin.get('label'))
        parsed_pin.styles = pin.get('styles') or {}
        return parsed_pin

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
        font_size = label.get('font_size')
        font_family = label.get('font_family')
        align = label.get('align')
        baseline = label.get('baseline')
        rotation = float(label.get('rotation'))
        parsed_label = Label(x, y, text, font_size, font_family, align, baseline, rotation)
        parsed_label.styles = label.get('styles') or {}
        return parsed_label

    def parse_shape(self, shape):
        """ Extract a shape. """
        # pylint: disable=R0914
        # pylint: disable=R0911

        shape_type = shape.get('type')
        if 'rectangle' == shape_type:
            x = int(shape.get('x'))
            y = int(shape.get('y'))
            height = int(shape.get('height'))
            width = int(shape.get('width'))
            parsed_shape = Rectangle(x, y, width, height)
        elif 'rounded_rectangle' == shape_type:
            x = int(shape.get('x'))
            y = int(shape.get('y'))
            height = int(shape.get('height'))
            width = int(shape.get('width'))
            radius = int(shape.get('radius'))
            parsed_shape = RoundedRectangle(x, y, width, height, radius)
        elif 'arc' == shape_type:
            x = int(shape.get('x'))
            y = int(shape.get('y'))
            start_angle = float(shape.get('start_angle'))
            end_angle = float(shape.get('end_angle'))
            radius = int(shape.get('radius'))
            parsed_shape = Arc(x, y, start_angle, end_angle, radius)
        elif 'circle' == shape_type:
            x = int(shape.get('x'))
            y = int(shape.get('y'))
            radius = int(shape.get('radius'))
            parsed_shape = Circle(x, y, radius)
        elif 'label' == shape_type:
            parsed_shape = self.parse_label(shape)
        elif 'line' == shape_type:
            p1 = self.parse_point(shape.get('p1'))
            p2 = self.parse_point(shape.get('p2'))
            parsed_shape = Line(p1, p2)
        elif 'polygon' == shape_type:
            parsed_shape = Polygon()
            for point in shape.get('points'):
                parsed_shape.add_point(self.parse_point(point))
        elif 'bezier' == shape_type:
            control1 = self.parse_point(shape.get('control1'))
            control2 = self.parse_point(shape.get('control2'))
            p1 = self.parse_point(shape.get('p1'))
            p2 = self.parse_point(shape.get('p2'))
            parsed_shape = BezierCurve(control1, control2, p1, p2)
        elif 'rounded_segment' == shape_type:
            p1 = self.parse_point(shape.get('p1'))
            p2 = self.parse_point(shape.get('p2'))
            width = int(shape.get('width'))
            parsed_shape = RoundedSegment(p1, p2, width)

        parsed_shape.styles = shape.get('styles') or {}
        parsed_shape.attributes = shape.get('attributes') or {}
        return parsed_shape

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

