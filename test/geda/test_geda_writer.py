
import os
import unittest
import tempfile

from writer.geda import GEDA

class TestGEDAWriter(unittest.TestCase):

    def setUp(self):
        self.geda_writer = GEDA()

    def test_create_project_files(self):
        geda_filename = '/tmp/test_geda.sch'

        self.geda_writer.create_project_files(geda_filename)

        self.assertEquals(
            self.geda_writer.project_dirs['project'], 
            '/tmp'
        )
        self.assertEquals(
            self.geda_writer.project_dirs['symbol'], 
            '/tmp/symbols'
        )

        self.assertTrue(os.path.exists('/tmp/gafrc'))

        fh = open('/tmp/gafrc', 'r')
        data = ''.join(fh.readlines())
        fh.close()

        self.assertEquals(data, '(component-library "./symbols")') 


         
