#!/usr/bin/python
# encoding: utf-8
from core.annotation import Annotation
import unittest


class AnnotationTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_new_annotation(self):
        anno = Annotation('abc', 0, 1, 2, False)
        assert anno.value == 'abc'
        assert anno.x == 0
        assert anno.y == 1
        assert anno.rotation == 2
        assert anno.visible == False
