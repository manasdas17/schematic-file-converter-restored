#!/usr/bin/python
# encoding: utf-8
""" The eagle parser test class """

from parser.eagle import Eagle
import unittest


class EagleTests(unittest.TestCase):
    """ The tests of the eagle parser """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_eagle_parser(self):
        """ Test creating an empty parser. """
        parser = Eagle()
        assert parser != None
