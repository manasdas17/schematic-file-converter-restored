#!/usr/bin/python
# encoding: utf-8
from parser.altium import Altium
import unittest


class AltiumTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_altium_parser(self):
        p = Altium()
        assert p != None
