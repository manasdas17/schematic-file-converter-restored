#!/usr/bin/python
# encoding: utf-8
from parser.geda import GEDA
import unittest


class GEDATests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_geda_parser(self):
        p = GEDA()
        assert p != None
