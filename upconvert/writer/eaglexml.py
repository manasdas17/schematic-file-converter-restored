#!/usr/bin/env python2
""" The Eagle XML Format Writer """

# upconvert.py - A universal hardware design file format converter using
# Format:       upverter.com/resources/open-json-format/
# Development:  github.com/upverter/schematic-file-converter
#
# Copyright 2012 Upverter, Inc.
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

# TODO: handle layers

import upconvert.parser.eaglexml.generated_g as G

default_layers = {
    "net": G.layer(number="91", name="Nets", color="2", fill="1", visible="yes", active="yes"),
    "bus": G.layer(number="92", name="Busses", color="1", fill="1", visible="yes", active="yes"),
    "pin": G.layer(number="93", name="Pins", color="2", fill="1", visible="no", active="yes"),
    "symbol": G.layer(number="94", name="Symbols", color="4", fill="1", visible="yes", active="yes"),
    "name": G.layer(number="95", name="Names", color="7", fill="1", visible="yes", active="yes"),
    "value": G.layer(number="96", name="Values", color="7", fill="1", visible="yes", active="yes"),
    "info": G.layer(number="97", name="Info", color="7", fill="1", visible="yes", active="yes"),
    "guide": G.layer(number="98", name="Guide", color="6", fill="1", visible="yes", active="yes"),
    }

EAGLE_SCALE = 10.0/9.0

class EagleXML(object):
    """ The Eagle XML Format Writer """

    SCALE = 0.5
    MULT =  25.4 / 90 # 90dpi to mm

    def __init__(self):
        # map library names to eaglexml library dom objects
        self.libcache = {}

        # map string layer numbers to eaglexml layer objects.
        self.layercache = {}

        # map (lib, name) to deviceset dom objects where lib
        # is a library dom object and name is a deviceset name
        self.dscache = {} # (lib, name) -> deviceset dom object

        # map openjson Body objects to eaglexml gate names
        self.body2gate = {}

        # map openjson components ids to eaglexml libraries
        self.cpt2lib = {} # component id -> library

        # map openjson components ids to eaglexml devicesets
        self.cpt2deviceset = {} # component id -> deviceset

        # map (component id, device name) to eaglexml devices
        self.cptdname2dev = {} # (component id, device name) -> device

        # map (component id, pin name) to eaglexml gate names
        self.cptpin2gate = {} # (component id, pin name) -> gate name

        # map (instance id to component id)
        self.inst2cpt = {}

        # map a (library id, pin number) to the pin name
        self.pinnum2name = {}

    def write(self, design, filename):
        """ Write the design to the Eagle XML format """

        design.scale(1 / EAGLE_SCALE)

        eagle = self.make_dom(design)

        with open(filename, 'wb') as outfile:
            outfile.write('<?xml version="1.0" encoding="utf-8"?>\n')
            outfile.write('<!DOCTYPE eagle SYSTEM "eagle.dtd">\n')
            eagle.export(outfile, 0, namespace_='')


    def make_dom(self, design):
        """ Return the DOM tree for a design. """

        self.design = design

        for ci in design.component_instances:
            self.inst2cpt[ci.instance_id] = ci.library_id

        eagle = G.eagle()
        eagle.drawing = G.drawing()
        eagle.drawing.layers = G.layers()
        eagle.drawing.schematic = G.schematic()
        eagle.drawing.schematic.libraries = G.libraries()
        eagle.drawing.schematic.parts = G.parts()
        eagle.drawing.schematic.sheets = G.sheets()
        eagle.drawing.schematic.sheets.sheet.append(G.sheet())

        sheet = eagle.drawing.schematic.sheets.sheet[0]
        sheet.instances = G.instances()
        sheet.nets = G.nets()

        self.layers = eagle.drawing.layers

        self.add_libraries(eagle.drawing.schematic.libraries, design)
        self.add_parts(eagle.drawing.schematic.parts, design)
        self.add_instances(sheet.instances, design)
        self.add_nets(sheet.nets, design)
        self.add_default_layers()

        return eagle


    def add_libraries(self, dom, design):
        """ Add the libraries to a dom object. """

        for cpt_name, cpt in design.components.components.iteritems():
            lib = self.ensure_lib_for_cpt(dom, cpt)
            deviceset = self.ensure_deviceset_for_cpt(lib, cpt)
            self.add_component_to_deviceset(cpt_name, cpt, lib, deviceset)


    def add_parts(self, dom, design):
        """ Add the parts to a dom object. """

        for ci in design.component_instances:
            dom.part.append(self.make_part(ci))


    def add_instances(self, dom, design):
        """ Add the instances to a dom object. """

        for ci in design.component_instances:
            for bodyindex, symattr in enumerate(ci.symbol_attributes):
                dom.instance.append(self.make_instance(ci, symattr, bodyindex))


    def add_nets(self, dom, design):
        """ Add the nets to a dom object. """

        for net in design.nets:
            dom.net.append(self.make_net(net))


    def ensure_lib_for_cpt(self, libraries, cpt):
        """ Ensure there is an eaglexml library for the given openjson
        component. Return the new or existing library. """

        libname = cpt.attributes.get('eaglexml_library', 'openjson')

        if libname in self.libcache:
            return self.libcache[libname]

        lib = G.library(libname)
        lib.packages = G.packages()
        lib.symbols = G.symbols()
        lib.devicesets = G.devicesets()

        libraries.library.append(lib)
        self.libcache[libname] = lib

        return lib


    def ensure_deviceset_for_cpt(self, lib, cpt):
        """Ensure there is an eaglexml deviceset for the given
        openjson component. """

        dsname = cpt.attributes.get('eaglexml_deviceset', cpt.name)

        if (lib, dsname) in self.dscache:
            return self.dscache[lib, dsname]

        deviceset = G.deviceset(name=dsname)
        deviceset.gates = G.gates()
        deviceset.devices = G.devices()

        lib.devicesets.deviceset.append(deviceset)
        self.dscache[lib, dsname] = deviceset

        return deviceset


    def add_component_to_deviceset(self, cpt_name, cpt, lib, deviceset):
        """ Add the openjson component to the eagle library and deviceset objects. """

        if cpt.attributes.get('eaglexml_type', 'logical') == 'physical':
            self.add_physical_component_to_deviceset(cpt, lib, deviceset)
        else:
            self.add_logical_component_to_deviceset(cpt_name, cpt, lib, deviceset)

        self.cpt2lib[cpt_name] = lib
        self.cpt2deviceset[cpt_name] = deviceset


    def add_logical_component_to_deviceset(self, cpt_name, cpt, lib, deviceset):
        """ Add the openjson component to the eagle library and deviceset objects
        as a logical device with gates. """

        symbol_names = set() # set of names used for eaglexml symbols
        gate_names = set() # set of names used for eaglemxl gates

        for symindex, symbol in enumerate(cpt.symbols):
            for bodyindex, body in enumerate(symbol.bodies):
                index = (symindex * len(symbol.bodies)) + bodyindex
                symname = cpt.attributes.get('eaglexml_symbol_%d' % index,
                                             'symbol_%d' % len(lib.symbols.symbol))
                if symname not in symbol_names:
                    lib.symbols.symbol.append(
                        self.make_eagle_symbol_for_openjson_body(symname, body))
                    symbol_names.add(symname)

                gatename = cpt.attributes.get('eaglexml_gate_%d' % bodyindex,
                                              'G$%d' % bodyindex)
                if gatename not in gate_names:
                    deviceset.gates.gate.append(
                        G.gate(name=gatename, symbol=symname, x="0", y="0"))
                    gate_names.add(gatename)

                self.body2gate[body] = gatename

                for pin in body.pins:
                    if pin.label is not None:
                        pin_name = pin.label.text
                    else:
                        pin_name = pin.pin_number
                    self.pinnum2name[(cpt_name, pin.pin_number)] = pin_name
                    self.cptpin2gate[cpt_name, pin.pin_number] = gatename


    def make_eagle_symbol_for_openjson_body(self, name, body):
        """ Make an eaglexml symbol from an opensjon body. """

        symbol = G.symbol(name=name)

        layer = self.ensure_layer(body, 'symbol')

        for shape in body.shapes:
            if shape.type == 'line':
                symbol.wire.append(
                    G.wire(x1=self.make_length(shape.p1.x),
                           y1=self.make_length(shape.p1.y),
                           x2=self.make_length(shape.p2.x),
                           y2=self.make_length(shape.p2.y),
                           layer=layer.number))
            elif shape.type == 'rectangle':
                symbol.rectangle.append(
                    G.rectangle(x1=self.make_length(shape.x),
                                y1=self.make_length(shape.y)
                                - self.make_length(shape.height),
                                x2=self.make_length(shape.x)
                                + self.make_length(shape.width),
                                y2=self.make_length(shape.y),
                                layer=layer.number))
            elif shape.type == 'polygon':
                symbol.polygon.append(self.make_polygon(shape))
                symbol.polygon[-1].layer = layer.number
            elif shape.type == 'circle':
                symbol.circle.append(self.make_circle(shape))
                symbol.circle[-1].layer = layer.number

        for pin in body.pins:
            if pin.label is not None:
                pin_name = pin.label.text
            else:
                pin_name = pin.pin_number
            symbol.pin.append(
                G.pin(name=pin_name,
                      x=self.make_length(pin.p2.x),
                      y=self.make_length(pin.p2.y),
                      length=self.get_pin_length(pin),
                      direction=pin.attributes.get('eaglexml_direction'),
                      visible=pin.attributes.get('eaglexml_visible'),
                      rot=self.get_pin_rotation(pin)))

        return symbol


    def make_polygon(self, ipoly):
        """ Make an eagle polygon from an opensjon polygon. """

        poly = G.polygon()

        for point in ipoly.points:
            poly.vertex.append(G.vertex(x=self.make_length(point.x),
                                        y=self.make_length(point.y)))

        return poly


    def make_circle(self, shape):
        """ Make an eagle circle from an opensjon circle. """

        circ = G.circle(x=self.make_length(shape.x),
                        y=self.make_length(shape.y),
                        radius=self.make_length(shape.radius))

        if 'eaglexml_width' in shape.attributes:
            circ.width = shape.attributes['eaglexml_width']
        else:
            circ.width = "0.254"

        return circ


    def get_pin_length(self, pin):
        """ Return the eaglexml length for an openjson pin. """

        length = (((pin.p2.x - pin.p1.x) ** 2)
                  + ((pin.p2.y - pin.p1.y) ** 2)) ** .5
        length = self.make_length(length)
        if length == 0:
            return 'point'
        elif length <= 2.90:
            return 'short'
        elif length <= 5.70:
            return 'middle'
        else:
            return 'long'


    def get_pin_rotation(self, pin):
        """ Return the eaglexml rotation for an openjson pin. """

        if pin.p2.x == pin.p1.x:
            if pin.p2.y == pin.p1.y:
                return None # point
            elif pin.p2.y < pin.p1.y:
                return 'R90'
            else:
                return 'R270'
        elif pin.p2.x < pin.p1.x:
            return None
        else:
            return 'R180'


    def add_physical_component_to_deviceset(self, cpt, lib, deviceset):
        """ Add the openjson component to the eagle library and deviceset objects
        as a physical device with a package. """


    def make_part(self, cpt_inst):
        """ Make an eaglexml part for an openjson component instance. """

        part = G.part()
        part.name = cpt_inst.instance_id
        part.library = self.cpt2lib[cpt_inst.library_id].name
        part.deviceset = self.cpt2deviceset[cpt_inst.library_id].name
        part.device = self.ensure_device_for_component_instance(cpt_inst).name

        return part


    def make_instance(self, cpt_inst, symattr, bodyindex):
        """ Make an eaglexml part for an openjson component instance
        and symbol attribute. """

        cpt = self.design.components.components[cpt_inst.library_id]
        symbol = cpt.symbols[cpt_inst.symbol_index]
        body = symbol.bodies[bodyindex]

        inst = G.instance()
        inst.part = cpt_inst.instance_id
        inst.gate = self.body2gate[body]
        inst.x = self.make_length(symattr.x)
        inst.y = self.make_length(symattr.y)
        inst.rot = self.make_angle(symattr.rotation)

        layer = self.ensure_layer(body, 'symbol')

        for ann in symattr.annotations:
            inst.attribute.append(
                G.attribute(name=ann.value,
                            value=ann.value,
                            layer=layer.number,
                            size="1.27",
                            x=self.make_length(ann.x + symattr.x),
                            y=self.make_length(ann.y + symattr.y),
                            rot=self.make_angle(ann.rotation),
                            display='value' if ann.visible else 'off'))

        return inst


    def ensure_device_for_component_instance(self, cpt_inst):
        """ Return an eagle device for an openjson component instance,
        creating a new one if necessary. """

        name = cpt_inst.attributes.get('eaglexml_device', '')

        if (cpt_inst.library_id, name) in self.cptdname2dev:
            return self.cptdname2dev[cpt_inst.library_id, name]

        device = G.device(name=name)

        self.cptdname2dev[cpt_inst.library_id, name] = device
        self.cpt2deviceset[cpt_inst.library_id].devices.device.append(device)

        return device


    def make_net(self, openjson_net):
        """ Make a new eagle net from an openjson net. """

        # connected components. maps point ids to sets of points in
        # the net which are connected visually. These become eagle
        # segments in the net.
        conncomps = {} # point id -> set([point id])

        for point in openjson_net.points.itervalues():
            point_ids = set(point.connected_points)
            point_ids.add(point.point_id)
            for point_id in point_ids:
                if point_id in conncomps:
                    conncomp = conncomps[point_id]
                    conncomp.update(point_ids)
                    break
            else:
                conncomp = point_ids

            for point_id in point_ids:
                conncomps[point_id] = conncomp

        net = G.net(name=openjson_net.net_id)
        done = set() # objects ids of point sets

        for pointset in conncomps.itervalues():
            if id(pointset) not in done:
                done.add(id(pointset))
                net.segment.append(self.make_segment(openjson_net, pointset))

        return net


    def make_segment(self, openjson_net, pointset):
        wires = set() # ((x1, y1), (x2, y2))

        for point_id in pointset:
            p1 = openjson_net.points[point_id]
            x1 = self.make_length(p1.x)
            y1 = self.make_length(p1.y)

            for point_id in p1.connected_points:
                p2 = openjson_net.points[point_id]
                x2 = self.make_length(p2.x)
                y2 = self.make_length(p2.y)
                wires.add(tuple(sorted([(x1, y1), (x2, y2)])))

        seg = G.segment()

        layer = self.ensure_layer(openjson_net, "net")

        for (x1, y1), (x2, y2) in sorted(wires):
            wire = G.wire(x1=x1, y1=y1, x2=x2, y2=y2, layer=layer.number)
            seg.wire.append(wire)

        for point_id in pointset:
            for cc in openjson_net.points[point_id].connected_components:
                cid = self.inst2cpt[cc.instance_id]
                gate = self.cptpin2gate[cid, cc.pin_number]
                pin_name = self.pinnum2name[(cid, cc.pin_number)]
                pinref = G.pinref(part=cc.instance_id, gate=gate, pin=pin_name)
                seg.pinref.append(pinref)

        seg.pinref.sort(key=lambda p : (p.part, p.gate, p.pin))

        return seg


    def ensure_layer(self, openjson_obj, eagle_context):
        """
        Return the eaglexml layer for the given openjson object (Pin, Shape, etc.)
        given an eaglexml context string (pin, symbol, etc.). If the layer does
        not exists, create it and add it to the design.
        """

        layernum = None

        if hasattr(openjson_obj, 'attributes') \
                and 'eaglexml_layer' in openjson_obj.attributes:
            layernum = openjson_obj.attributes['eaglexml_layer']

            if layernum in self.layercache:
                return self.layercache[layernum]

        layer = default_layers[eagle_context]

        if layernum is None or layernum == layer.number:
            pass
        else:
            layer = G.layer(number=layernum, name=layernum,
                            color="1", fill="1", visible="yes", active="yes")

        if layer.number in self.layercache:
            return self.layercache[layer.number]
        else:
            self.layercache[layer.number] = layer
            self.layers.layer.append(layer)
            return layer


    def add_default_layers(self):
        """
        Add default layers to the design if they have not been added already.
        """

        for layer in default_layers.itervalues():
            if layer.number not in self.layercache:
                self.layercache[layer.number] = layer
                self.layers.layer.append(layer)

        self.layers.layer.sort(key=lambda layer : int(layer.number))


    def make_length(self, value):
        """ Make an eagle length measurement from an openjson length. """

        return round(float(value) * self.MULT * self.SCALE, 3)


    def make_angle(self, value):
        """ Make an eaglexml angle measurement from an openjson angle. """

        return 'R%d' % (value * 180,)
