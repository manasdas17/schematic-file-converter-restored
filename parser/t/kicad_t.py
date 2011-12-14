#!/usr/bin/python
# encoding: utf-8
from parser.kicad import KiCAD
import unittest


class KiCADTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_kicad_parser(self):
        p = KiCAD()
        assert p != None
