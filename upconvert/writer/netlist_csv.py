#!/usr/bin/env python2
""" The Netlist Format Writer """

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


class Netlist(object):
    """ The Netlist Format Writer """

    def write(self, design, filename):
        """ Write the design to the Netlist format """

        nets = {}
        for n in design.nets:
            endpoints = []
            for p in n.points:
                for c in p.connected_components:
                    endpoints.append('%s.%s' % (c.instance_id, c.pin_number)

            if n.net_id in nets:
                nets[n.net_id]['enpoints'].extend(endpoints)
            else:
                nets[n.net_id] = {'name': n.net_id,
                                  'endpoints': endpoints}

        with open(filename, "w") as f:
            f.write('Name,Connections')
            for n in nets.values():
                if len(n['enpoints']) > 0:
                    f.write('%s:%s' % (n['name'], ','.join(n['endpoints']))
