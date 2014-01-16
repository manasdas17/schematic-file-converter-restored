#!/usr/bin/env python2
""" The BOM Format Writer """

# upconvert - A universal hardware design file format converter using
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


class BOM(object):
    """ The BOM Format Writer """

    def write(self, design, filename):
        """ Write the design to the BOM format """

        bom = {}
        for c in design.component_instances:
            refdes = c.instance_id
            if 'refdes' in c.attributes:
                refdes = c.attributes['refdes']

            if c.library_id in bom:
                bom[c.library_id]['refs'].append(refdes)

            else:
                library_part = design.components.components[c.library_id]
                name = ''
                if '_manufacturer' in library_part.attributes:
                    name += library_part.attributes['_manufacturer'] + ' '
                if '_part_number' in library_part.attributes:
                    name += library_part.attributes['_part_number']
                bom[c.library_id] = {'part': c.library_id,
                                     'name': name,
                                     'refs': [refdes]}

        with open(filename, "w") as f:
            f.write('Part,Name,Reference,Qty\n')
            for c in bom.values():
                if len(c['refs']) > 0 and c['part'] != '0000000000000001':
                    f.write('%s,"%s","%s",%s\n' % (c['part'], c['name'], ','.join(c['refs']), len(c['refs'])))
