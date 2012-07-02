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

    def __init__(self):
        self.libcache = {} # name -> library dom object
        self.dscache = {} # (lib, name) -> deviceset dom object


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

        self.add_libraries(eagle.drawing.schematic, design)

        return eagle


    def add_libraries(self, dom, design):
        """ Add the libraries to a dom object. """

        dom.libraries = G.libraries()

        for cpt in design.components.components.itervalues():
            lib = self.ensure_lib_for_cpt(dom.libraries, cpt)
            deviceset = self.ensure_deviceset_for_cpt(lib, cpt)
            self.add_component_to_deviceset(cpt, lib, deviceset)


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

        dsname = cpt.attributes.get('eaglexml_deviceset', 'openjson')

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
