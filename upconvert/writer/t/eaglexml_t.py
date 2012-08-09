# encoding: utf-8
#pylint: disable=R0904
""" The eaglexml writer test class """

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


from upconvert.parser.t.eaglexml_t import get_design
from upconvert.writer.eaglexml import EagleXML

from functools import wraps

import os
import unittest
import tempfile

EAGLE_SCALE = 10.0/9.0

_cache = {} # filename -> DOM

def get_dom(filename):
    if filename not in _cache:
        design = get_design(filename)
        _cache[filename] = EagleXML().make_dom(design)
    return _cache[filename]


def use_file(filename):
    """ Return a decorator which will parse a gerber file
    before running the test. """

    def decorator(test_method):
        """ Add params to decorator function. """

        @wraps(test_method)
        def wrapper(self):
            """ Parse file then run test. """
            self.design = get_design(filename)
            self.dom = get_dom(filename)
            test_method(self)

        return wrapper

    return decorator


class EagleXMLTests(unittest.TestCase):
    """ The tests of the eaglexml writer """

    @use_file('E1AA60D5.sch')
    def test_write(self):
        """
        We can write out a complete design file.
        """

        writer = EagleXML()
        filedesc, filename = tempfile.mkstemp()
        os.close(filedesc)
        os.remove(filename)
        writer.write(self.design, filename)
        self.assertTrue(os.path.exists(filename))
        os.remove(filename)


    @use_file('E1AA60D5.sch')
    def test_libraries(self):
        """
        The correct libraries are generated.
        """

        libnames = [lib.name for lib
                    in self.dom.drawing.schematic.libraries.library]
        self.assertTrue('atmel' in libnames, libnames)


    @use_file('E1AA60D5.sch')
    def test_layers(self):
        """
        The correct layers are generated.
        """

        layers = [layer.name for layer in self.dom.drawing.layers.layer]
        self.assertTrue('Nets' in layers, layers)


    @use_file('E1AA60D5.sch')
    def test_devicesets(self):
        """
        The correct devicesets are generated.
        """

        lib = self.get_library('atmel')
        dsnames = [ds.name for ds in lib.devicesets.deviceset]
        self.assertTrue('TINY15L' in dsnames, dsnames)


    @use_file('E1AA60D5.sch')
    def test_parts(self):
        """
        The correct parts are generated.
        """

        parts = self.dom.drawing.schematic.parts
        names = [p.name for p in parts.part]
        self.assertTrue('R1' in names, names)


    @use_file('E1AA60D5.sch')
    def test_instances(self):
        """
        The correct instances are generated.
        """

        instances = self.dom.drawing.schematic.sheets.sheet[0].instances.instance
        names = [i.part for i in instances]
        self.assertTrue('IC1' in names, names)


    @use_file('E1AA60D5.sch')
    def test_attributes(self):
        """
        The correct instances are generated.
        """

        instances = self.dom.drawing.schematic.sheets.sheet[0].instances.instance
        instance = [i for i in instances if i.part == 'IC1'][0]
        self.assertTrue(len(instance.attribute), 2)
        self.assertTrue(set(a.value for a in instance.attribute),
                        set(['IC1', 'TINY25']))


    @use_file('E1AA60D5.sch')
    def test_symbols(self):
        """
        The correct symbols are generated.
        """

        lib = self.get_library('transistor-pnp')
        self.assertEqual(len(lib.symbols.symbol), 1)
        self.assertEqual(lib.symbols.symbol[0].name, 'PNP')


    @use_file('E1AA60D5.sch')
    def test_symbol_wires(self):
        """
        The correct symbol wires are generated.
        """

        lib = self.get_library('transistor-pnp')
        sym = lib.symbols.symbol[0]
        self.assertEqual(len(sym.wire), 11)
        wire = sym.wire[0]
        self.assertEqual(round(wire.x1 / EAGLE_SCALE, 3), 2.117)
        self.assertEqual(round(wire.y1 / EAGLE_SCALE, 3), 1.693)
        self.assertEqual(round(wire.x2 / EAGLE_SCALE, 2), 1.55)
        self.assertEqual(round(wire.y2 / EAGLE_SCALE, 2), 2.54)


    @use_file('E1AA60D5.sch')
    def test_symbol_rectangles(self):
        """
        The correct symbol rectangles are generated.
        """

        lib = self.get_library('transistor-pnp')
        sym = lib.symbols.symbol[0]
        self.assertEqual(len(sym.rectangle), 1)
        rect = sym.rectangle[0]
        self.assertEqual(round(rect.x1 / EAGLE_SCALE, 2), -0.28)
        self.assertEqual(round(rect.y1 / EAGLE_SCALE, 2), -2.54)
        self.assertEqual(round(rect.x2 / EAGLE_SCALE, 2), 0.56)
        self.assertEqual(round(rect.y2 / EAGLE_SCALE, 2), 2.54)


    @use_file('450B679C.sch')
    def test_symbol_polygons(self):
        """
        The correct symbol polygons are generated.
        """

        lib = self.get_library('adafruit')
        sym = lib.symbols.symbol[0]
        self.assertEqual(sym.name, 'LED')
        self.assertEqual(len(sym.polygon), 2)
        poly = sym.polygon[0]
        self.assertEqual(len(poly.vertex), 3)
        self.assertEqual(round(poly.vertex[0].x / EAGLE_SCALE, 3), -3.387)
        self.assertEqual(round(poly.vertex[0].y / EAGLE_SCALE, 3), -2.117)


    @use_file('D9CD1423.sch')
    def test_symbol_circles(self):
        """
        The correct symbol circles are generated.
        """

        lib = self.get_library('CONNECTER')
        sym = lib.symbols.symbol[0]
        self.assertEqual(sym.name, 'HEADER_1X10')
        self.assertEqual(len(sym.circle), 9)
        self.assertEqual(round(sym.circle[0].x / EAGLE_SCALE, 2), 0)
        self.assertEqual(round(sym.circle[0].y / EAGLE_SCALE, 2), 8.89)
        self.assertEqual(round(sym.circle[0].radius / EAGLE_SCALE, 3), 0.988)
        self.assertEqual(sym.circle[0].width, '0.254')


    @use_file('E1AA60D5.sch')
    def test_symbol_pins(self):
        """
        The correct symbol pins are generated.
        """

        lib = self.get_library('transistor-pnp')
        sym = lib.symbols.symbol[0]
        self.assertEqual(len(sym.pin), 3)
        pin = sym.pin[0]
        self.assertEqual(pin.name, "B")
        self.assertEqual(round(pin.x / EAGLE_SCALE, 2), -2.54)
        self.assertEqual(round(pin.y / EAGLE_SCALE, 2), 0)
        self.assertEqual(pin.length, "short")
        self.assertEqual(pin.rot, None)
        pin = sym.pin[1]
        self.assertEqual(pin.name, "E")
        self.assertEqual(round(pin.x / EAGLE_SCALE, 2), 2.54)
        self.assertEqual(round(pin.y / EAGLE_SCALE, 2), 5.08)
        self.assertEqual(pin.length, "short")
        self.assertEqual(pin.rot, "R270")
        pin = sym.pin[2]
        self.assertEqual(pin.name, "C")
        self.assertEqual(round(pin.x / EAGLE_SCALE, 2), 2.54)
        self.assertEqual(round(pin.y / EAGLE_SCALE, 2), -5.08)
        self.assertEqual(pin.length, "short")
        self.assertEqual(pin.rot, "R90")


    @use_file('E1AA60D5.sch')
    def test_nets(self):
        """
        The correct nets are generated.
        """

        nets = self.dom.drawing.schematic.sheets.sheet[0].nets
        names = [n.name for n in nets.net]
        self.assertTrue('GND' in names, names)


    @use_file('E1AA60D5.sch')
    def test_segments(self):
        """
        The correct segments are generated.
        """

        nets = self.dom.drawing.schematic.sheets.sheet[0].nets
        gnd = [n for n in nets.net if n.name == 'GND'][0]
        self.assertEqual(len(gnd.segment), 7)


    @use_file('E1AA60D5.sch')
    def test_segment_wires(self):
        """
        The correct wires in segments are generated.
        """

        nets = self.dom.drawing.schematic.sheets.sheet[0].nets
        net = [n for n in nets.net if n.name == 'N$7'][0]
        self.assertEqual(len(net.segment), 1)
        seg = net.segment[0]
        self.assertEqual(len(seg.wire), 2)
        self.assertEqual(round(seg.wire[0].x1 / EAGLE_SCALE, 1), 76.2)
        self.assertEqual(round(seg.wire[0].y1 / EAGLE_SCALE, 2), 68.58)
        self.assertEqual(round(seg.wire[0].x2 / EAGLE_SCALE, 2), 83.82)
        self.assertEqual(round(seg.wire[0].y2 / EAGLE_SCALE, 2), 68.58)
        self.assertEqual(round(seg.wire[1].x1 / EAGLE_SCALE, 2), 83.82)
        self.assertEqual(round(seg.wire[1].y1 / EAGLE_SCALE, 2), 48.26)
        self.assertEqual(round(seg.wire[1].x2 / EAGLE_SCALE, 2), 83.82)
        self.assertEqual(round(seg.wire[1].y2 / EAGLE_SCALE, 2), 68.58)


    @use_file('E1AA60D5.sch')
    def test_segment_pinrefs(self):
        """
        The correct pinrefs in segments are generated.
        """

        nets = self.dom.drawing.schematic.sheets.sheet[0].nets
        net = [n for n in nets.net if n.name == 'N$7'][0]
        self.assertEqual(len(net.segment), 1)
        seg = net.segment[0]
        self.assertEqual(len(seg.pinref), 2)
        self.assertEqual(seg.pinref[0].part, 'IC1')
        self.assertEqual(seg.pinref[0].gate, 'G$1')
        self.assertEqual(seg.pinref[0].pin, '(ADC1)PB2')
        self.assertEqual(seg.pinref[1].part, 'R3')
        self.assertEqual(seg.pinref[1].gate, 'G$1')
        self.assertEqual(seg.pinref[1].pin, '2')


    def get_library(self, name):
        """ Return the named library from the dom. """

        return [lib for lib
                in self.dom.drawing.schematic.libraries.library
                if lib.name == name][0]
