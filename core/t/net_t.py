#!/usr/bin/python
# encoding: utf-8
from core.net import Net
from core.net import NetPoint
from core.net import ConnectedComponent
import unittest


class NetTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_net(self):
        net = Net('001')
        assert net.net_id == '001'


class NetPointTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_net_point(self):
        point = NetPoint('001', 0, 1)
        assert point.point_id == '001'


class ConnectedComponentTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_connected_component(self):
        comp = ConnectedComponent('001', '002')
        assert comp.instance_id == '001'
