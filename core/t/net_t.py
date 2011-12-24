#!/usr/bin/python
# encoding: utf-8
""" The net test class """

from core.net import Net
from core.net import NetPoint
from core.net import ConnectedComponent
import unittest


class NetTests(unittest.TestCase):
    """ The tests of the core module net feature """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_net(self):
        """ Test the creation of a new empty net. """
        net = Net('001')
        assert net.net_id == '001'


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
