#!/usr/bin/python
# encoding: utf-8
""" The annotation test class """

from core.annotation import Annotation
import unittest


class AnnotationTests(unittest.TestCase):
    """ The tests of the core module annotation feature """

    def setUp(self):
        """ Setup the test case. """
        pass

    def tearDown(self):
        """ Teardown the test case. """
        pass

    def test_create_new_annotation(self):
        """ Test the creation of a new empty annotation. """
        anno = Annotation('abc', 0, 1, 2, False)
        assert anno.value == 'abc'
        assert anno.x == 0
        assert anno.y == 1
        assert anno.rotation == 2
        assert anno.visible != True

    def test_annotation_bounds(self):
        '''Test .bounds()'''
        annot = Annotation('foo', 3, 6, 0, True)
        tl, br = annot.bounds()
        # bounds() will give a square with sides 20 units long, centered on the
        # annotation
        self.assertEqual(tl.x, 3 - 10)
        self.assertEqual(tl.y, 6 - 10)
        self.assertEqual(br.x, 3 + 10)
        self.assertEqual(br.y, 6 + 10)
