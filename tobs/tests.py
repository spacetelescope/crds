"""Higher level mapping based tests for selectors not covered by hst.
"""

import sys
import unittest

from crds import rmap, log

class TestSelectors(unittest.TestCase):

    def setUp(self):
        self.rmap = rmap.get_cached_mapping("tobs_tinstr_tfilekind.rmap")
    
    def _selector_testcase(self, case, parameter, result):
        header = {
            "TEST_CASE": case,
            "PARAMETER": parameter,
        }
        bestref = self.rmap.get_best_ref(header)
        self.assertEqual(bestref, result)
        
    def test_use_after_bad_datetime(self):
        with self.assertRaises(rmap.ValidationError):
            self._selector_testcase('USE_AFTER', '4.5', 'cref_flatfield_73.fits')

    def test_use_after_no_time(self):
        self._selector_testcase('USE_AFTER', '2005-12-20', 'o9f15549j_bia.fits')

    def test_use_after_nominal(self):
        self._selector_testcase('USE_AFTER', '2005-12-20', 'o9f15549j_bia.fits')

    def test_use_after_missing_parameter(self):
        header = { "TEST_CASE": "USE_AFTER" }  # no PARAMETER
        with self.assertRaisesRegexp(
            rmap.ValidationError, 
            "UseAfter required lookup parameter 'PARAMETER' is undefined."):
            bestref = self.rmap.get_best_ref(header)

    def test_select_version1(self): 
        self._selector_testcase('SELECT_VERSION', '4.5', 'cref_flatfield_73.fits')
    def test_select_version2(self): 
        self._selector_testcase('SELECT_VERSION', '5', 'cref_flatfield_123.fits')
    def test_select_version3(self): 
        self._selector_testcase('SELECT_VERSION', '6', 'cref_flatfield_123.fits')
    def test_select_version4(self): 
        self._selector_testcase('SELECT_VERSION', '2.0', 'cref_flatfield_65.fits')
        
    def test_closest_time1(self):
        self._selector_testcase('CLOSEST_TIME', '2016-05-05', 'cref_flatfield_123.fits')
    def test_closest_time2(self):
        self._selector_testcase('CLOSEST_TIME', '2016-04-24', 'cref_flatfield_123.fits')
    def test_closest_time3(self):
        self._selector_testcase('CLOSEST_TIME', '2018-02-02', 'cref_flatfield_222.fits')
    def test_closest_time4(self):
        self._selector_testcase('CLOSEST_TIME', '2019-03-01', 'cref_flatfield_123.fits')
    def test_closest_time5(self):
        self._selector_testcase('CLOSEST_TIME', '2016-04-15', 'cref_flatfield_123.fits')
    def test_closest_time6(self):
        self._selector_testcase('CLOSEST_TIME', '2016-04-16', 'cref_flatfield_123.fits')

    def test_bracket1(self):
        self._selector_testcase('BRACKET', '1.25',     
            ('cref_flatfield_120.fits', 'cref_flatfield_124.fits'))
    def test_bracket2(self):
        self._selector_testcase('BRACKET', '1.2',     
            ('cref_flatfield_120.fits', 'cref_flatfield_120.fits'))
    def test_bracket3(self):
        self._selector_testcase('BRACKET', '1.5',     
            ('cref_flatfield_124.fits', 'cref_flatfield_124.fits'))
    def test_bracket4(self):
        self._selector_testcase('BRACKET', '5.0',     
            ('cref_flatfield_137.fits', 'cref_flatfield_137.fits'))
    def test_bracket5(self):
        self._selector_testcase('BRACKET', '1.0',
            ('cref_flatfield_120.fits', 'cref_flatfield_120.fits'))
    def test_bracket6(self):
        self._selector_testcase('BRACKET', '6.0',
            ('cref_flatfield_137.fits', 'cref_flatfield_137.fits'))

    def test_geometrically_nearest1(self):
        self._selector_testcase("GEOMETRICALLY_NEAREST", '1.0', 'cref_flatfield_120.fits')
    def test_geometrically_nearest2(self):
        self._selector_testcase("GEOMETRICALLY_NEAREST", '1.2', 'cref_flatfield_120.fits')
    def test_geometrically_nearest3(self):
        self._selector_testcase("GEOMETRICALLY_NEAREST", '1.25', 'cref_flatfield_120.fits')
    def test_geometrically_nearest4(self):
        self._selector_testcase("GEOMETRICALLY_NEAREST", '1.4', 'cref_flatfield_124.fits')
    def test_geometrically_nearest5(self):
        self._selector_testcase("GEOMETRICALLY_NEAREST", '3.25', 'cref_flatfield_124.fits')
    def test_geometrically_nearest6(self):
        self._selector_testcase("GEOMETRICALLY_NEAREST", '3.26', 'cref_flatfield_137.fits')
    def test_geometrically_nearest7(self):
        self._selector_testcase("GEOMETRICALLY_NEAREST", '5.0', 'cref_flatfield_137.fits')
    def test_geometrically_nearest8(self):
        self._selector_testcase("GEOMETRICALLY_NEAREST", '5.1', 'cref_flatfield_137.fits')
        
class TestInsert(unittest.TestCase):

    def setUp(self):
        self.rmap = rmap.load_mapping("tobs_tinstr_tfilekind.rmap")
        self.original = rmap.load_mapping("tobs_tinstr_tfilekind.rmap")
        
    def terminal_insert(self, selector_name, param, value):
        """Check the bottom level insert functionality."""
        header = { 
                  "TEST_CASE" : selector_name,
                  "PARAMETER" : param, 
        }
        result = self.rmap.insert(header, value)
        diffs = self.rmap.difference(result)
        log.debug(diffs)
        assert diffs[0][0] == ('tobs_tinstr_tfilekind.rmap', 'tobs_tinstr_tfilekind.rmap')
        assert diffs[0][1] == (selector_name,)
        assert str(diffs[0][2]) == str(param),  diffs
        assert diffs[0][3] == "added " + repr(value)

    def terminal_replace(self, selector_name, param, value):
        """Check the bottom level replace functionality."""
        header = { 
                  "TEST_CASE" : selector_name,
                  "PARAMETER" : param, 
        }
        result = self.rmap.insert(header, value)
        diffs = self.rmap.difference(result)
        log.debug(diffs)
        assert diffs[0][0] == ('tobs_tinstr_tfilekind.rmap', 'tobs_tinstr_tfilekind.rmap')
        assert diffs[0][1] == (selector_name,)
        assert str(diffs[0][2]) == str(param), diffs
        assert "replaced" in diffs[0][3]
        assert diffs[0][3].endswith(repr(value))

    def test_useafter_insert_before(self):
        self.terminal_insert("USE_AFTER", '2003-09-25 01:28:00', 'foo.fits')

    def test_useafter_replace_before(self):
        self.terminal_replace("USE_AFTER", '2003-09-26 01:28:00', 'foo.fits')
            
    def test_useafter_insert_mid(self):
        self.terminal_insert("USE_AFTER", '2004-06-18 04:36:01', 'foo.fits')
            
    def test_useafter_replace_mid(self):
        self.terminal_replace("USE_AFTER", '2004-06-18 04:36:00', 'foo.fits')
            
    def test_useafter_insert_after(self):
        self.terminal_insert("USE_AFTER", '2004-07-14 16:52:01', 'foo.fits')

    def test_useafter_replace_after(self):
        self.terminal_replace("USE_AFTER", '2004-07-14 16:52:00', 'foo.fits')

    """
           '<3.1':    'cref_flatfield_65.fits',
           '<5':      'cref_flatfield_73.fits',
           'default': 'cref_flatfield_123.fits',
    """
    def test_select_version_insert_before(self):
        self.terminal_insert("SELECT_VERSION", '<3.0', 'foo.fits')

    def test_select_version_insert_mid(self):
        self.terminal_insert("SELECT_VERSION", '<4', 'foo.fits')

    # There's *nothing* after default,  so no insert possible.
    #    def test_select_version_insert_after(self):
    #        self.terminal_insert("SELECT_VERSION", 'default', 'foo.fits')

    def test_select_version_replace_before(self):
        self.terminal_replace("SELECT_VERSION", '<3.1', 'foo.fits')

    def test_select_version_replace_mid(self):
        self.terminal_replace("SELECT_VERSION", '<5', 'foo.fits')

    def test_select_version_replace_after(self):
        self.terminal_replace("SELECT_VERSION", 'default', 'foo.fits')

    """
            '2017-04-24': "cref_flatfield_123.fits",
            '2018-02-01':  "cref_flatfield_222.fits",
            '2019-04-15': "cref_flatfield_123.fits",
    """
    def test_closest_time_insert_before(self):
         self.terminal_insert("CLOSEST_TIME", '2017-04-20 00:00:00', 'foo.fits')
    def test_closest_time_insert_mid(self):
         self.terminal_insert("CLOSEST_TIME", '2018-01-20 00:57', 'foo.fits')
    def test_closest_time_insert_after(self):
         self.terminal_insert("CLOSEST_TIME", '2020-04-20 00:00:00', 'foo.fits')
    
    def test_closest_time_replace_before(self):
         self.terminal_replace("CLOSEST_TIME", '2017-04-24', 'foo.fits')
    def test_closest_time_replace_mid(self):
         self.terminal_replace("CLOSEST_TIME", '2018-02-01', 'foo.fits')
    def test_closest_time_replace_after(self):
         self.terminal_replace("CLOSEST_TIME", '2019-04-15', 'foo.fits')
    
    """
            1.2: "cref_flatfield_120.fits",
            1.5: "cref_flatfield_124.fits",
            5.0: "cref_flatfield_137.fits",
    """
    def test_bracket_insert_before(self):
         self.terminal_insert("BRACKET", 1.0, 'foo.fits')
    def test_bracket_insert_mid(self):
         self.terminal_insert("BRACKET", 1.3, 'foo.fits')
    def test_bracket_insert_after(self):
         self.terminal_insert("BRACKET", 5.1, 'foo.fits')

    def test_bracket_replace_before(self):
         self.terminal_replace("BRACKET", 1.2, 'foo.fits')
    def test_bracket_replace_mid(self):
         self.terminal_replace("BRACKET", 1.5, 'foo.fits')
    def test_bracket_replace_after(self):
         self.terminal_replace("BRACKET", 5.0, 'foo.fits')

    """
            1.2 : "cref_flatfield_120.fits",
            1.5 : "cref_flatfield_124.fits",
            5.0 : "cref_flatfield_137.fits",
    """
    def test_geometrically_nearest_insert_before(self):
         self.terminal_insert("GEOMETRICALLY_NEAREST", 1.0, 'foo.fits')
    def test_geometrically_nearest_insert_mid(self):
         self.terminal_insert("GEOMETRICALLY_NEAREST", 1.3, 'foo.fits')
    def test_geometrically_nearest_insert_after(self):
         self.terminal_insert("GEOMETRICALLY_NEAREST", 5.1, 'foo.fits')

    def test_geometrically_nearest_replace_before(self):
         self.terminal_replace("GEOMETRICALLY_NEAREST", 1.2, 'foo.fits')
    def test_geometrically_nearest_replace_mid(self):
         self.terminal_replace("GEOMETRICALLY_NEAREST", 1.5, 'foo.fits')
    def test_geometrically_nearest_replace_after(self):
         self.terminal_replace("GEOMETRICALLY_NEAREST", 5.0, 'foo.fits')

    def test_recursive_insert(self): # , header, value, classes):
        """Check recursively adding a lookup path,  including new selectors."""
        header = { 
                  "TEST_CASE" : "INSERT",
                  "PARAMETER" : "2012-09-09 03:07", 
        }
        result = self.rmap.insert(header, "foo.fits")
        diffs = self.rmap.difference(result)
#        print diffs
#        print self.rmap.selector.format()
    
if __name__ == '__main__':
    unittest.main()

