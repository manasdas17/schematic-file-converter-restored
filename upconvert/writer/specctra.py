#!/usr/bin/env python2

""" The Specctra DSN Format Writer """

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

from upconvert.parser import specctraobj 
import math

class Specctra(object):

    def __init__(self):
        self.resolution = None
        self.padstack_sequence = 1
        self.max_x = 0
        self.max_y = 0
        self.min_x = 0
        self.min_y = 0
        self.max_offset = 0
        self.pin_padstacks = {}
        self.pcb = self._make_pcb()

    def write(self, design, filename, library_filename=None):
        self._convert(design)

        with open(filename, "w") as f:
            f.write(self._to_string(self.pcb.compose()))

    def _make_layer(self, name, index):
        layer = specctraobj.Layer()
        layer.layer_id = name 
        layer.ltype = specctraobj.Type()
        layer.ltype.value = 'signal'
        layer.lproperty = specctraobj.Property()
        layer.lproperty.index = specctraobj.Index()
        layer.lproperty.index.value = index
        return layer

    def _make_pcb(self):
        pcb = specctraobj.Pcb()
        pcb.library = specctraobj.Library()
        pcb.placement = specctraobj.Placement()
        pcb.network = specctraobj.Network()
        pcb.wiring = specctraobj.Wiring()
        pcb.parser.host_cad = specctraobj.HostCad()
        pcb.parser.host_cad.value = 'Upverter'
        pcb.parser.host_version = specctraobj.HostVersion()
        pcb.parser.host_version.value = 'Upverter x.y.z'

        pcb.resolution = specctraobj.Resolution()
        pcb.resolution.unit = 'mil'
        pcb.resolution.resolution = 10
        self.resolution = pcb.resolution

        pcb.unit = specctraobj.Unit()
        pcb.unit.value = 'mil'
        return pcb
 
    def _convert(self, design):

        for library_id, cpt in design.components.components.items():
            self._convert_component(library_id, cpt)

        for inst in design.component_instances:
            cpt_inst = self._convert_component_instance(inst)
            self.pcb.placement.component.append(cpt_inst)

        for net in design.nets:
            self._convert_net(net)

        self.pcb.structure = self._make_structure()

    def _convert_component_instance(self, inst):
        component = specctraobj.Component()
        component.image_id = inst.library_id + '-' + str(inst.symbol_index)
        component.place = specctraobj.Place()
        component.place.component_id = inst.instance_id
        symbattr = inst.symbol_attributes[0]
        mirror = {0.5:1.5, 1.5:0.5}
        component.place.rotation = int(mirror.get(symbattr.rotation,  symbattr.rotation) * 180)
        component.place.vertex = self._from_pixels_abs((symbattr.x, symbattr.y))
        return component

    def _make_structure(self):
        structure = specctraobj.Structure()
        boundary = specctraobj.Boundary()
        boundary.rectangle = specctraobj.Rectangle()
        boundary.rectangle.layer_id = 'pcb'
        boundary.rectangle.vertex1 = (self.min_x - self.max_offset, self.min_y - self.max_offset)
        boundary.rectangle.vertex2 = (self.max_x + self.max_offset, self.max_y + self.max_offset)
        structure.boundary.append(boundary)

        structure.layer.append(self._make_layer('Front', 0))
        structure.layer.append(self._make_layer('Back', 1))
        return structure

    def _from_pixels_abs(self, point):
        """ Converts absolute position and updates min/max values for boundary calculation """
        point = self.resolution.from_pixels(point)
        self.max_x = max(self.max_x, point[0])
        self.max_y = max(self.max_y, point[1])
        self.min_x = min(self.min_x, point[0])
        self.min_y = min(self.min_y, point[1])
        return point

    def _from_pixels(self, point):
        """ Converts relative position and updates max value for boundary calculation """
        point = self.resolution.from_pixels(point)
        try:
            self.max_offset = max(self.max_offset, max(abs(point[0]), abs(point[1])))
        except:
            self.max_offset = max(self.max_offset, abs(point))
        return point

    def _convert_net(self, net):
        pcbnet = specctraobj.Net()
        pcbnet.net_id = net.net_id
        pcbnet.pins.append(specctraobj.Pins())

        wire = specctraobj.Wire()
        wire.net = specctraobj.Net() 
        wire.net.net_id = net.net_id

        paths = set()
        for point in net.points.values():
            for cpt in point.connected_components:
                pcbnet.pins[-1].pin_reference.append(cpt.instance_id + '-' + cpt.pin_number)

            for point2_id in point.connected_points:
                point2 = net.points.get(point2_id)
                if point2 is not None:
                    path = [(point.x, point.y), (point2.x, point2.y)]
                    path.sort() # canonical order
                    paths.add(tuple(path))

        # Keep unique pins only
        pcbnet.pins[-1].pin_reference = dict.fromkeys(pcbnet.pins[-1].pin_reference).keys()
        self.pcb.network.net.append(pcbnet)

        for path in paths:
            wire = specctraobj.Wire()
            wire.net = specctraobj.Net() 
            wire.net.net_id = net.net_id
            wire.shape = specctraobj.Path()
            wire.shape.layer_id = 'Back'

            point1, point2 = path
            wire.shape.vertex.append(self._from_pixels_abs(point1))
            wire.shape.vertex.append(self._from_pixels_abs(point2))
            self.pcb.wiring.wire.append(wire)


    def _convert_component(self, library_id, cpt):
        for symbol in cpt.symbols:
            for idx, body in enumerate(symbol.bodies):
                image = specctraobj.Image()
                image.image_id = library_id + '-' + str(idx)
                for shape in body.shapes:
                    for pcbshape in self._convert_shape(shape):
                        outline = specctraobj.Outline()
                        outline.shape = pcbshape
                        image.outline.append(outline)

                for pin in body.pins:
                    image.pin.append(self._convert_pin(pin))
        self.pcb.library.image.append(image)

    def _get_arc_qarcs(self, arc):
        """ Specctra does not have arcs so convert them to qarcs """
        
        min_angle = min(arc.start_angle, arc.end_angle)
        max_angle = max(arc.start_angle, arc.end_angle)

        def make_point(angle):
            opp = math.sin(angle * math.pi) * arc.radius
            adj = math.cos(angle * math.pi) * arc.radius
            return (arc.x + adj, arc.y - opp)
 
        points = []
        for angle in (0.5, 1.0, 1.5, 2.0):
            if max_angle < angle:
                points.append((make_point(max_angle), make_point(min_angle)))
                break
            elif min_angle < angle:
                points.append((make_point(angle), make_point(min_angle)))
                min_angle = angle
                if min_angle == max_angle:
                    break

        return points

    def _get_arc_points(self, arc):
        """ Specctra does not have arcs so convert them to lines
        """
        
        min_angle = min(arc.start_angle, arc.end_angle)
        max_angle = max(arc.start_angle, arc.end_angle)
        step = 0.2
        count = int((max_angle - min_angle) / step)

        angle = min_angle
        angles = []
        for i in xrange(count):
            angles.append(angle)
            angle += step
        angles.append(max_angle)

        def make_point(angle):
            opp = math.sin(angle * math.pi) * arc.radius
            adj = math.cos(angle * math.pi) * arc.radius
            return (arc.x - adj, arc.y + opp)
 
        points = []
        for angle in angles:
            points.append(make_point(angle))
        return points

    def _convert_shape(self, shape):
        if shape.type == 'circle':
            circle = specctraobj.Circle()
            circle.diameter = self._from_pixels(float(shape.radius) * 2.0)
            circle.vertex = self._from_pixels((shape.x, shape.y))
            return [circle]
        elif shape.type == 'line':
            path = specctraobj.Path()
            path.vertex.append(self._from_pixels((shape.p1.x, shape.p1.y)))
            path.vertex.append(self._from_pixels((shape.p2.x, shape.p2.y)))
            return [path]
        elif shape.type == 'polygon':
            polygon = specctraobj.Polygon()
            for point in shape.points:
                polygon.vertex.append(self._from_pixels((point.x, point.y)))
            return [polygon]
        elif shape.type == 'arc':
            # Can't get freerouting.net to show qarc, replace it with multiple paths
            '''
            points = self._get_arc_qarcs(shape)
            center = self._from_pixels((shape.x, shape.y))

            result = []
            for start, end in points:
                qarc = specctraobj.QArc()
                qarc.vertex1 = self._from_pixels(start)
                qarc.vertex2 = self._from_pixels(end)
                qarc.vertex3 = center
                result.append(qarc)
            return result
            '''
            points = [self._from_pixels(point) for point in self._get_arc_points(shape)]

            prev = points[0]
            result = []
            for point in points[1:]:
                path = specctraobj.Path()
                path.vertex.append(prev)
                path.vertex.append(point)
                result.append(path)
                prev = point
            return result
            
        elif shape.type == 'rectangle':
            rect = specctraobj.Rectangle()
            rect.vertex1 = self._from_pixels((shape.x, shape.y))
            rect.vertex2 = self._from_pixels((shape.x + shape.width, shape.y - shape.height))
            return [rect]
        else:
            print 'Unsupported shape', shape.type
            return []

    def _convert_pin(self, pin):
        point = self._from_pixels((pin.p1.x - pin.p2.x, pin.p1.y - pin.p2.y))
        if point in self.pin_padstacks:
            padstack_id = self.pin_padstacks[point]
        else:
            self.padstack_sequence += 1
            padstack_id = str(self.padstack_sequence)
            self.pin_padstacks[point] = padstack_id

            shape = specctraobj.Path()
            shape.layer_id = 'Front'
            shape.vertex.append((0, 0))
            point = self._from_pixels((pin.p1.x - pin.p2.x, pin.p1.y - pin.p2.y))
            shape.vertex.append(point)

            padstack = specctraobj.Padstack()
            padstack.padstack_id = padstack_id
            padstack.shape.append(specctraobj.Shape())
            padstack.shape[-1].shape = shape
            self.pcb.library.padstack.append(padstack)

        p = specctraobj.Pin()
        p.pin_id = pin.pin_number
        p.vertex = self._from_pixels_abs((pin.p2.x, pin.p2.y))
        p.padstack_id = padstack_id

        return p
 
    def _to_string(self, lst, indent=''):
        result = []
        for elem in lst:
            if isinstance(elem, list):
                if len(elem) > 0:
                    result.append('\n')
                    result.append(self._to_string(elem, indent + '  '))
            elif isinstance(elem, float):
                result.append('%.6f' % elem)
            elif isinstance(elem, basestring):
                for char in '() ':
                    if char in elem:
                        result.append('"%s"' % elem)
                        break
                else:
                    result.append(str(elem))
            elif elem is not None:
                result.append(str(elem))
        return indent + '(' + ' '.join(result) + ')\n' + indent 


