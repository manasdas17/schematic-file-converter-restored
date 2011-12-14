#!/usr/bin/python
# encoding: utf-8
from writer.openjson import JSON
import unittest


class JSONTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_json_writer(self):
        w = JSON()
        assert w != None
