#!/usr/bin/python
# encoding: utf-8
from core.design_attributes import DesignAttributes
from core.design_attributes import Metadata
import unittest


class DesignAttributesTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_design_attributes(self):
        desattrs = DesignAttributes()
        assert len(desattrs.annotations) == 0


class MetadataTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_metadata(self):
        meta = Metadata()
        assert meta.name == ''
