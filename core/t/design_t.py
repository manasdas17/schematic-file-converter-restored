#!/usr/bin/python
# encoding: utf-8
from core.design import Design
import unittest


class DesignTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_annotation(self):
        des = Design()
        assert len(des.nets) == 0
