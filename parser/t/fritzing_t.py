#!/usr/bin/python
# encoding: utf-8
from parser.fritzing import Fritzing
import unittest


class FritzingTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_fritzing_parser(self):
        p = Fritzing()
        assert p != None
