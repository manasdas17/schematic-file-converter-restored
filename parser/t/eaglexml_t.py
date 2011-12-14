#!/usr/bin/python
# encoding: utf-8
from parser.eaglexml import EagleXML
import unittest


class EagleXMLTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_eaglexml_parser(self):
        p = EagleXML()
        assert p != None
