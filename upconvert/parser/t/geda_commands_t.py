#!/usr/bin/python
# encoding: utf-8
#pylint: disable=R0904
""" The geda parser test class """

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

import os
from unittest import TestCase
import StringIO
from upconvert.parser.geda import GEDA, GEDAError

import upconvert.core.design
import upconvert.core.shape

from upconvert.parser import geda_commands


class GEDACommandTests(TestCase):

    def setUp(self):
        self.command = geda_commands.GEDACommand()
        self.param = geda_commands.GEDAParameter('test')
        self.style_param = geda_commands.GEDAStyleParameter('test')
        self.extra_param = geda_commands.GEDAExtraParameter('test')

        self.command.TYPE = 'X'
        self.command.PARAMETERS = (self.param, self.style_param)
        self.command.EXTRA_PARAMETERS = (self.extra_param,)

    def test_line_command_parameters(self):
        parameter_names = [
            "x1",
            "y1",
            "x2",
            "y2",
            "style_color",
            "style_width",
            "style_capstyle",
            "style_dashstyle",
            "style_dashlength",
            "style_dashspace",
        ]

        line_command = geda_commands.GEDALineCommand()

        self.assertItemsEqual(
            [p.name for p in line_command.PARAMETERS],
            parameter_names
        )

    def test_getting_parameters(self):
        self.assertItemsEqual([
                self.param,
                self.style_param,
                self.extra_param,
            ],
            self.command.parameters()
        )

    def test_getting_style_keywords(self):
        self.assertItemsEqual(
            ['style_test'],
            self.command.get_style_keywords()
        )

    def test_getting_style_keywords_without_parameters(self):
        self.assertItemsEqual(
            [],
            geda_commands.GEDACommand().get_style_keywords()
        )

    def test_updating_default_kwargs_with_empty_dict(self):
        defaults = self.command.update_default_kwargs(**{})
        self.assertItemsEqual(
            ['test', 'style_test', 'extra_test'],
            defaults.keys()
        )

    def test_updating_default_kwargs(self):
        defaults = self.command.update_default_kwargs(**{
            'test': 'test_value',
        })
        self.assertItemsEqual(
            ['test', 'style_test', 'extra_test'],
            defaults.keys()
        )
        self.assertEquals(defaults['test'], 'test_value')
        self.assertEquals(defaults['style_test'], None)
        self.assertEquals(defaults['extra_test'], None)

    def test_generated_command_with_default_parameters(self):
        command = self.command.generate_command(**{})
        self.assertEquals(len(command), 1)
        self.assertEquals(
            command[0], 
            "X None None"
        )

    def test_generated_command_with_set_parameters(self):
        command = self.command.generate_command(**{
            'test': 1,
            'style_test': 5,
            'extra_test': 10
        })
        self.assertEquals(len(command), 1)
        self.assertEquals(
            command[0], 
            "X 1 5"
        )
