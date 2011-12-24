#!/usr/bin/python
# encoding: utf-8
""" The eaglexml parser test class """

from parser.eaglexml import EagleXML
import unittest


class EagleXMLTests(unittest.TestCase):
    """ The tests of the eagle-xml parser """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_eaglexml_parser(self):
        """ Test creating an empty parser. """
        parser = EagleXML()
        assert parser != None
