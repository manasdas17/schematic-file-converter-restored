import unittest
import StringIO

from os.path import dirname, join

from parser.geda import GEDA 
from parser.openjson import JSON

#TEST_INPUT_FILE = join(dirname(__file__), 'test.sch')
#GOOD_OUTPUT_FILE = join(dirname(__file__), 'test.upv')


class TestGEDA(unittest.TestCase):

    def setUp(self):
        self.geda_parser = GEDA()

    def test_constructor(self):
        geda_parser = GEDA()
        self.assertEquals(len(geda_parser.symbol_lookup), 0)

        geda_parser = GEDA([
            './test/geda/simple_example/symbols',
            '/invalid/dir/gEDA',
        ])

        self.assertEquals(len(geda_parser.symbol_lookup), 1)
        self.assertEquals(
            geda_parser.symbol_lookup['opamp.sym'],
            './test/geda/simple_example/symbols/opamp.sym'
        )

        geda_parser = GEDA([
            './test/geda/simple_example/symbols',
            '/usr/share/gEDA/sym',
            '/invalid/dir/gEDA',
        ])

        self.assertGreater(len(geda_parser.symbol_lookup), 0)
        self.assertTrue('title-B.sym' in geda_parser.symbol_lookup)

    def test_parse_version(self):
        sample_file = 'v 20040111 2'
        result = self.geda_parser.parse_object(
            StringIO.StringIO(sample_file)
        )

        self.assertEquals(type(result), tuple)

        self.assertEquals(result['version'], '20040111')
        self.assertEquals(result['fileformat_version'], '2')

    def test_parse_line(self):
        pass
        


if __name__ == '__main__':
    unittest.main()
