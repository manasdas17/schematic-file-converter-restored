#!/usr/bin/python
# encoding: utf-8
""" The gerber parser test class """

from os import path

from parser.gerber import Gerber
import unittest

strip_dirs = path.join('parser', 't')
base_dir = path.dirname(__file__).split(strip_dirs)[0]
test_files = path.join('test', 'gerber')
dir = path.join(base_dir, test_files)

class GerberTests(unittest.TestCase):
    """ The tests of the gerber parser """

    def setUp(self):
        """ Setup the test case. """
        self.design = None

    def tearDown(self):
        """ Teardown the test case. """
        pass


    # decorator for tests that use input files

    def use_file(filename):
        """ Parse a gerber file. """
        def wrap_wrap_tm(test_method):
            def wrap_tm(self):
                parser = Gerber(path.join(dir, filename))
                self.design = parser.parse()
                test_method(self)

            # correctly identify the decorated method
            # (otherwise nose will not run the test)
            wrap_tm.__name__ = test_method.__name__
            wrap_tm.__doc__ = test_method.__doc__
            wrap_tm.__dict__.update(test_method.__dict__)
            wrap_wrap_tm.__name__ = wrap_tm.__name__
            wrap_wrap_tm.__doc__ = wrap_tm.__doc__
            wrap_wrap_tm.__dict__.update(wrap_tm.__dict__)

            return wrap_tm
        return wrap_wrap_tm


    # tests that pass if no errors are raised

    def test_create_new_gerber_parser(self):
        """ Create an empty gerber parser. """
        parser = Gerber()
        assert parser != None

    @use_file('simple.ger')
    def test_simple(self):
        """ Parse a simple, correct gerber file. """
        assert self.design.layouts != None


    # tests that pass if they raise expected errors
