import unittest
import StringIO

from os.path import dirname, join

from parser.geda import GEDA 
from parser.openjson import JSON

#TEST_INPUT_FILE = join(dirname(__file__), 'test.sch')
#GOOD_OUTPUT_FILE = join(dirname(__file__), 'test.upv')


class GEDATest(unittest.TestCase):

    def setUp(self):
        self.geda_parser = GEDA()

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
