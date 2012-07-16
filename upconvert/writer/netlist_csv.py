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
        for net in design.nets:
            endpoints = []
            for point in net.points.values():
                for connect in point.connected_components:
                    endpoints.append('%s.%s' % (connect.instance_id, connect.pin_number))

            if net.net_id in nets:
                nets[net.net_id]['endpoints'].extend(endpoints)
            else:
                nets[net.net_id] = {'name': net.net_id,
                                  'endpoints': endpoints}

        with open(filename, "w") as f:
            f.write('Name,Connections\n')
            for net in nets.values():
                if len(net['endpoints']) > 0:
                    f.write('%s:%s\n' % (net['name'], ','.join(net['endpoints'])))
