""" The fritzing partlib test class """

from partlib.fritzing import lookup_part

from unittest import TestCase
from os.path import basename, exists


class FritzingTests(TestCase):
    """ The tests of the fritzing partlib """

    def test_lookup_present(self):
        """ Test looking up a part that is present """

        path = '/some/path/to/fritzing/parts/core/SMD_Diode_REC_DO.fzp'
        version = '0.6.4b.12.16.5683'

        found = lookup_part(path, version)

        self.assertEqual(basename(found), basename(path))
        self.assertTrue(exists(found))

    def test_lookup_missing(self):
        """ Test looking up a part that is missing """

        path = '/some/path/to/fritzing/parts/core/notthere.fzp'
        version = '0.6.4b.12.16.5683'

        found = lookup_part(path, version)

        self.assertEqual(found, None)
