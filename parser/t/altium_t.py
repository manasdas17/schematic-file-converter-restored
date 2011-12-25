#!/usr/bin/python
# encoding: utf-8
""" The altium parser test class """

from parser.altium import Altium
import unittest


class AltiumTests(unittest.TestCase):
    """ The tests of the altium parser """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_altium_parser(self):
        """ Test creating an empty parser. """
        parser = Altium()
        assert parser != None
