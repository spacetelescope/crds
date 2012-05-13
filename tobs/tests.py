"""Higher level mapping based tests.
"""

from crds import rmap

import unittest

class TestSelectors(unittest.TestCase):

    def setUp(self):
        self.rmap = rmap.get_cached_mapping("tobs_tinstr_tfilekind.rmap")

    def _selector_testcase(self, case, parameter, result):
        header = {
            "TEST_CASE":"SELECT_VERSION",
            "PARAMETER": parameter,
            }
        bestref = self.rmap.get_best_ref(header)
        self.assertEqual(bestref, result)
    
    def test_select_version1(self): 
        self._selector_testcase('SELECT_VERSION', '4.5', 'cref_flatfield_73.fits')
    def test_select_version2(self): 
        self._selector_testcase('SELECT_VERSION', '5', 'cref_flatfield_123.fits')
    def test_select_version3(self): 
        self._selector_testcase('SELECT_VERSION', '6', 'cref_flatfield_123.fits')
    def test_select_version4(self): 
        self._selector_testcase('SELECT_VERSION', '2.0', 'cref_flatfield_65.fits')

if __name__ == '__main__':
    unittest.main()

