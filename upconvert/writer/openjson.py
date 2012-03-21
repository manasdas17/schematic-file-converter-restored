#!/usr/bin/env python2
""" The Open JSON Format Writer """

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
# 0) 1:1 Output of the data model


import json


class JSON:
    """ The JSON Format Writer """

    def write(self, design, filename):
        """ Recursively ask for JSON forms of components for output """
        with open(filename, "w") as f:
            f.write(json.dumps(design.json(), sort_keys=True, indent=4))
