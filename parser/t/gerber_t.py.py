#!/usr/bin/python
# encoding: utf-8
from parser.gerber import Gerber
import unittest


class GerberTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_gerber_parser(self):
        p = Gerber()
        assert p != None
