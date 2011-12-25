#!/usr/bin/python
# encoding: utf-8
""" The design attribute test class """

from core.design_attributes import DesignAttributes
from core.design_attributes import Metadata
import unittest


class DesignAttributesTests(unittest.TestCase):
    """ The tests of the core module attribute feature """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_attributes(self):
        """ Test the creation of a new empty design. """
        desattrs = DesignAttributes()
        assert len(desattrs.annotations) == 0


class MetadataTests(unittest.TestCase):
    """ The tests of the core module metadata feature """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_metadata(self):
        """ Test the creation of a new empty metatdata container. """
        meta = Metadata()
        assert meta.name == ''
