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


import upconvert.parser.eaglexml.generated as G


class EagleXML(object):
    """ The Eagle XML Format Writer """

    SCALE = 0.5
    MULT =  25.4 / 90 # 90dpi to mm

    def __init__(self):
        # map library names to eaglexml library dom objects
        self.libcache = {}

        # map (lib, name) to deviceset dom objects where lib
        # is a library dom object and name is a deviceset name
        self.dscache = {} # (lib, name) -> deviceset dom object

        # map openjson Body objects to eaglexml gate dom objects
        self.body2gate = {}

        # map openjson components ids to eaglexml libraries
        self.cpt2lib = {} # component id -> library

        # map openjson components ids to eaglexml devicesets
        self.cpt2deviceset = {} # component id -> deviceset

        # map (component id, device name) to eaglexml devices
        self.cptdname2dev = {} # (component id, device name) -> device


    def write(self, design, filename):
        """ Write the design to the Eagle XML format """

        eagle = self.make_dom(design)

        with open(filename, 'wb') as outfile:
            outfile.write('<?xml version="1.0" encoding="utf-8"?>\n')
            outfile.write('<!DOCTYPE eagle SYSTEM "eagle.dtd">\n')
            eagle.export(outfile, 0, namespace_='')


    def make_dom(self, design):
        """ Return the DOM tree for a design. """

        eagle = G.eagle()
        eagle.drawing = G.drawing()
        eagle.drawing.schematic = G.schematic()
        eagle.drawing.schematic.libraries = G.libraries()
        eagle.drawing.schematic.parts = G.parts()
        eagle.drawing.schematic.sheets = G.sheets()
        eagle.drawing.schematic.sheets.sheet.append(G.sheet())

        sheet = eagle.drawing.schematic.sheets.sheet[0]
        sheet.instances = G.instances()
        sheet.nets = G.nets()

        self.add_libraries(eagle.drawing.schematic.libraries, design)
        self.add_parts(eagle.drawing.schematic.parts, design)
        self.add_instances(sheet.instances, design)
        self.add_nets(sheet.nets, design)

        return eagle


    def add_libraries(self, dom, design):
        """ Add the libraries to a dom object. """

        for cpt in design.components.components.itervalues():
            lib = self.ensure_lib_for_cpt(dom, cpt)
            deviceset = self.ensure_deviceset_for_cpt(lib, cpt)
            self.add_component_to_deviceset(cpt, lib, deviceset)


    def add_parts(self, dom, design):
        """ Add the parts to a dom object. """

        for ci in design.component_instances:
            dom.part.append(self.make_part(ci))


    def add_instances(self, dom, design):
        """ Add the instances to a dom object. """

        for ci in design.component_instances:
            for symattr in ci.symbol_attributes:
                dom.instance.append(self.make_instance(ci, symattr))


    def add_nets(self, dom, design):
        """ Add the nets to a dom object. """


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


    def add_component_to_deviceset(self, cpt, lib, deviceset):
        """ Add the openjson component to the eagle library and deviceset objects. """

        if cpt.attributes.get('eaglexml_type', 'logical') == 'physical':
            self.add_physical_component_to_deviceset(cpt, lib, deviceset)
        else:
            self.add_logical_component_to_deviceset(cpt, lib, deviceset)

        self.cpt2lib[cpt.name] = lib
        self.cpt2deviceset[cpt.name] = deviceset


    def add_logical_component_to_deviceset(self, cpt, lib, deviceset):
        """ Add the openjson component to the eagle library and deviceset objects
        as a logical device with gates. """

        symbol_names = set() # set of names used for eaglexml symbols
        gate_names = set() # set of names used for eaglemxl gates

        for symindex, symbol in enumerate(cpt.symbols):
            for bodyindex, body in enumerate(symbol.bodies):
                index = (symindex * len(symbol.bodies)) + bodyindex
                symname = cpt.attributes.get('eaglexml_symbol_%d' % index,
                                             'symbol_%d' % index)
                if symname not in symbol_names:
                    lib.symbols.symbol.append(
                        self.make_eagle_symbol_for_openjson_body(symname, body))
                    symbol_names.add(symname)

                gatename = cpt.attributes.get('eaglexml_gate_%d' % bodyindex,
                                              'G$%d' % symindex)
                if gatename not in gate_names:
                    deviceset.gates.gate.append(
                        G.gate(name=gatename, symbol=symname, x="0", y="0"))
                    gate_names.add(gatename)

                self.body2gate[body] = gatename


    def make_eagle_symbol_for_openjson_body(self, name, body):
        """ Make an eaglexml symbol from an opensjon body. """

        symbol = G.symbol(name=name)

        for shape in body.shapes:
            if shape.type == 'line':
                wire = G.wire(x1=self.make_length(shape.p1.x),
                              y1=self.make_length(shape.p1.y),
                              x2=self.make_length(shape.p2.x),
                              y2=self.make_length(shape.p2.y))
                symbol.wire.append(wire)
            elif shape.type == 'rectangle':
                rect = G.rectangle(x1=self.make_length(shape.x),
                                   y1=self.make_length(shape.y)
                                   - self.make_length(shape.height),
                                   x2=self.make_length(shape.x)
                                   + self.make_length(shape.width),
                                   y2=self.make_length(shape.y))
                symbol.rectangle.append(rect)

        return symbol


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


    def make_instance(self, cpt_inst, symattr):
        """ Make an eaglexml part for an openjson component instance
        and symbol attribute. """

        inst = G.instance()
        return inst


    def ensure_device_for_component_instance(self, cpt_inst):
        name = cpt_inst.attributes.get('eaglexml_device', '')

        if (cpt_inst.library_id, name) in self.cptdname2dev:
            return self.cptdname2dev[cpt_inst.library_id, name]

        device = G.device(name=name)

        self.cptdname2dev[cpt_inst.library_id, name] = device
        self.cpt2deviceset[cpt_inst.library_id].devices.device.append(device)

        return device


    def make_length(self, value):
        """ Make an eagle length measurement from an openjson length. """

        return round(float(value) * self.MULT * self.SCALE, 3)
