#!/usr/bin/env python2
""" The package version tool """

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

import os
import subprocess

def version():
    """ Attempt to return the version of the converter """
    try:
        if os.path.exists(".git/"):
            subprocess.call(["git describe --tags > version"])
        with open('version', 'r') as f:
            vrsn = f.read().strip()
    except Exception: #pylint: disable=W0703
        vrsn = '0.8.9'

    return vrsn
