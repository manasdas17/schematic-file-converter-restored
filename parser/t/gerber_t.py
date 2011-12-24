#!/usr/bin/python
# encoding: utf-8
""" The gerber parser test class """

from parser.gerber import Gerber
import unittest


class GerberTests(unittest.TestCase):
    """ The tests of the gerber parser """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_gerber_parser(self):
        """ Test creating an empty parser. """
        parser = Gerber()
        assert parser != None
