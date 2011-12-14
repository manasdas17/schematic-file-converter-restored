#!/usr/bin/python
# encoding: utf-8
from writer.kicad import KiCAD
import unittest


class KiCADTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_kicad_writer(self):
        w = KiCAD()
        assert w != None
