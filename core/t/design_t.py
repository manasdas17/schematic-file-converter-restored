#!/usr/bin/python
# encoding: utf-8
""" The design test class """

from core.design import Design
import unittest


class DesignTests(unittest.TestCase):
    """ The tests of the core module design feature """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_design(self):
        """ Test the creation of a new empty design. """
        des = Design()
        assert len(des.nets) == 0
