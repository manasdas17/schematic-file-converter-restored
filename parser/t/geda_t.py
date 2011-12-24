#!/usr/bin/python
# encoding: utf-8
""" The geda parser test class """

from parser.geda import GEDA
import unittest


class GEDATests(unittest.TestCase):
    """ The tests of the geda parser """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_geda_parser(self):
        """ Test creating an empty parser. """
        parser = GEDA()
        assert parser != None
