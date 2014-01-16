#!/usr/bin/python
# encoding: utf-8
#pylint: disable=R0904
""" The net test class """

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


from upconvert.core.net import Net
from upconvert.core.net import NetPoint
from upconvert.core.net import ConnectedComponent
import unittest


class NetTests(unittest.TestCase):
    """ The tests of the core module net feature """

    def setUp(self):
        """ Setup the test case. """
        self.net = Net('001')

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_net(self):
        """ Test the creation of a new empty net. """
        assert self.net.net_id == '001'

    def test_bounds_simple(self):
        '''Make sure bounds() uses all the included NetPoints'''
        for (x, y) in ((1, 3), (3, 2), (4, 3), (3, 5)):
            net_pt = NetPoint(str((x, y)), x, y)
            self.net.add_point(net_pt)
            # NetPoints don't actually need to be connected to affect bounds()

        top_left, btm_right = self.net.bounds()
        self.assertEqual(top_left.x, 1)
        self.assertEqual(top_left.y, 2)
        self.assertEqual(btm_right.x, 4)
        self.assertEqual(btm_right.y, 5)


class NetPointTests(unittest.TestCase):
    """ The tests of the core module net point feature """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_net_point(self):
        """ Test the creation of a new empty net point. """
        point = NetPoint('001', 0, 1)
        assert point.point_id == '001'


class ConnectedComponentTests(unittest.TestCase):
    """ The tests of the core module connected component feature """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_component(self):
        """ Test the creation of a new empty connected component. """
        comp = ConnectedComponent('001', '002')
        assert comp.instance_id == '001'
