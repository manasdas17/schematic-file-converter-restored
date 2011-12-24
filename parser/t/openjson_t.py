#!/usr/bin/python
# encoding: utf-8
""" The openjson parser test class """

from parser.openjson import JSON
import unittest


class JSONTests(unittest.TestCase):
    """ The tests of the json parser """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_json_parser(self):
        """ Test creating an empty parser. """
        parser = JSON()
        assert parser != None
