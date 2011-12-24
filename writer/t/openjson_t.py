#!/usr/bin/python
# encoding: utf-8
""" The openjson writer test class """

from writer.openjson import JSON
import unittest


class JSONTests(unittest.TestCase):
    """ The tests of the json writer """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_json_writer(self):
        """ Test creating an empty writer. """
        writer = JSON()
        assert writer != None
