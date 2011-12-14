#!/usr/bin/python
# encoding: utf-8
from parser.eagle import Eagle
import unittest


class EagleTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_eagle_parser(self):
        p = Eagle()
        assert p != None
