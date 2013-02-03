"""Higher level mapping based tests for selectors not covered by hst.
"""

import sys
import os
import unittest

from crds import rmap, log

# =============================================================================

class Test_00_Selectors(unittest.TestCase):

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
        
# =============================================================================

class Test_01_Insert(unittest.TestCase):
    """Tests for checking automatic rmap update logic for adding new references."""

    def setUp(self):
        # Note:  load_mapping must deliver a unique copy of the specified rmap
        self.rmap = rmap.load_mapping("tobs_tinstr_tfilekind.rmap")
        self.original = rmap.load_mapping("tobs_tinstr_tfilekind.rmap")
        
    def class_name(self, selector_name):
        return "".join([x.capitalize() for x in selector_name.split("_")])

    def set_classes(self, classes):
        self.rmap.selector._rmap_header["classes"] = classes
        
    def terminal_insert(self, selector_name, param, value):
        """Check the bottom level insert functionality."""
        header = { 
                  "TEST_CASE" : selector_name,
                  "PARAMETER" : param, 
        }
        inner_class = self.class_name(selector_name)
        self.set_classes(("Match", inner_class))
        result = self.rmap.insert(header, value)
        diffs = self.rmap.difference(result)
        log.debug("diffs:", diffs)
        assert len(diffs) == 1, "Fewer/more differences than expected"
        assert diffs[0][0] == ('tobs_tinstr_tfilekind.rmap', 'tobs_tinstr_tfilekind.rmap'), "unexpected file names in diff"
        assert diffs[0][1] == (selector_name,), "unexpected match case in diff"
        assert str(diffs[0][2]) == str(param), "unexpected parameter value in diff"
        assert diffs[0][3] == "added " + repr(value), "diff is not an addition"

    def terminal_replace(self, selector_name, param, value):
        """Check the bottom level replace functionality."""
        header = { 
                  "TEST_CASE" : selector_name,
                  "PARAMETER" : param, 
        }
        inner_class = self.class_name(selector_name)
        self.set_classes(("Match", inner_class))
        result = self.rmap.insert(header, value)
        diffs = self.rmap.difference(result)
        log.debug("diffs:", diffs)
        assert len(diffs) == 1, "Fewer/more differences than expected"
        assert diffs[0][0] == ('tobs_tinstr_tfilekind.rmap', 'tobs_tinstr_tfilekind.rmap'), "unexpected file names in diff"
        assert diffs[0][1] == (selector_name,), "unexpected match case in diff"
        assert str(diffs[0][2]) == str(param), "unexpected parameter value in diff"
        assert "replaced" in diffs[0][3], "diff is not a replacement"
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

# =============================================================================

class RecursiveModify(object):
    """Tests for checking automatic rmap update logic for adding new references."""
    
    result_filename = None
    rmap_str = None
    insert_header = lookup_header = { 
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "DATE-OBS" : "2017-04-20",
          "TIME-OBS" : "00:00:00",
          "SW_VERSION" : "1.2",
          "CLOSETIME" : "2017-05-30 00:01:02",
          "BRACKET_PAR" : "4.4",   # try a number
          "PARAMETER" : "2012-09-09 03:07",
          "GEOM_PAR" : "2.7",  # try a string-formatted number
        }

    def test_0_recursive_modify_rmap(self): # , header, value, classes):
        # Load the test rmap from a string.   The top level selector must exist.
        # This is not a "realistic" test case.   It's a test of the recursive
        # insertion capabilities of all the Selector classes in one go.
        log.debug("-"*60)
        r = rmap.ReferenceMapping.from_string(self.rmap_str, "./test.rmap", ignore_checksum=True)
        log.debug("insert_header:", log.PP(self.insert_header))
        result = r.insert(self.insert_header, "foo.fits")
        result.write(self.result_filename)
        diffs = r.difference(result)
        log.debug("diffs:", diffs)
        assert len(diffs) == 1, "Fewer/more differences than expected: " + repr(diffs)
        log.debug("recursive insert result rmap:")
        log.debug(open(self.result_filename).read())
    
    def test_1_recursive_use_rmap(self):
        r = rmap.load_mapping(self.result_filename)
        result = r.get_best_ref(self.lookup_header)
        log.debug("recursive lookup result:", result)
        assert result == self.expected_lookup_result, "Recursively generated rmap produced wrong result."
    
    def test_9_recursive_tear_down(self):
        os.remove(self.result_filename)
        
class Test_02_DeepRecursiveModify(unittest.TestCase, RecursiveModify):
    result_filename = "./recursive_deep.rmap"
    expected_lookup_result = ("foo.fits", "foo.fits")
    rmap_str = '''
header = {
    'derived_from' : 'Hand written 01-15-2013',
    'filekind' : 'TFILEKIND',
    'instrument' : 'TINSTR',
    'mapping' : 'REFERENCE',
    'name' : 'test.rmap',
    'observatory' : 'TOBS',
    'parkey' : (('MATCH_PAR1','MATCH_PAR2'), ('DATE-OBS','TIME-OBS',), ('SW_VERSION',), ('CLOSETIME',), ('BRACKET_PAR',), ('GEOM_PAR',),),
    'sha1sum' : 'd412b94d1af1a0871fe39d7096e65aea1187c3b7',
    'classes' : ('Match','UseAfter','SelectVersion','ClosestTime','Bracket','GeometricallyNearest')
}

selector = Match({
})
'''

class Test_03_RecursiveUseAfter(unittest.TestCase, RecursiveModify):
    result_filename = "./recursive_useafter.rmap"
    expected_lookup_result = "foo.fits"
    rmap_str = '''
header = {
    'derived_from' : 'Hand written 01-15-2013',
    'filekind' : 'TFILEKIND',
    'instrument' : 'TINSTR',
    'mapping' : 'REFERENCE',
    'name' : 'test.rmap',
    'observatory' : 'TOBS',
    'parkey' : (('DATE-OBS','TIME-OBS',), ('MATCH_PAR1','MATCH_PAR2'),),
    'sha1sum' : 'd412b94d1af1a0871fe39d7096e65aea1187c3b7',
    'classes' : ('UseAfter','Match',)
}

selector = UseAfter({
    '2015-04-01 01:02:03' : Match({
    }),
    '2017-04-20 01:02:03' : Match({    
    }),
    '2018-04-03 01:02:03' : Match({
    }),    
})
'''

class Test_04_RecursiveClosestTime(unittest.TestCase, RecursiveModify):
    result_filename = "./recursive_closest_time.rmap"
    expected_lookup_result = "foo.fits"
    rmap_str = '''
header = {
    'derived_from' : 'Hand written 01-15-2013',
    'filekind' : 'TFILEKIND',
    'instrument' : 'TINSTR',
    'mapping' : 'REFERENCE',
    'name' : 'test.rmap',
    'observatory' : 'TOBS',
    'parkey' : (('CLOSETIME',), ('MATCH_PAR1','MATCH_PAR2'),),
    'sha1sum' : 'd412b94d1af1a0871fe39d7096e65aea1187c3b7',
    'classes' : ('ClosestTime','Match',)
}

selector = ClosestTime({
    '2015-04-01 01:02:03' : Match({
    }),
    '2017-04-20 01:02:03' : Match({    
    }),
    '2018-04-03 01:02:03' : Match({
    }),    
})
'''

class Test_05_RecursiveSelectVersion(unittest.TestCase, RecursiveModify):
    result_filename = "./recursive_select_version.rmap"
    expected_lookup_result = "foo.fits"
    rmap_str = '''
header = {
    'derived_from' : 'Hand written 01-15-2013',
    'filekind' : 'TFILEKIND',
    'instrument' : 'TINSTR',
    'mapping' : 'REFERENCE',
    'name' : 'test.rmap',
    'observatory' : 'TOBS',
    'parkey' : (('SW_VERSION',), ('MATCH_PAR1','MATCH_PAR2'),),
    'sha1sum' : 'd412b94d1af1a0871fe39d7096e65aea1187c3b7',
    'classes' : ('SelectVersion','Match',)
}

selector = SelectVersion({
    '<3.1': Match({
    }),
    '<5' : Match({
    }),
    'default' : Match({    
    }),
})
'''
    insert_header = lookup_header = { 
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "SW_VERSION" : "1.2",
        }
    
class Test_06_RecursiveSelectVersion_MatchingVersion(Test_05_RecursiveSelectVersion):
    insert_header = { 
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "SW_VERSION" : "<3.1",
        }
    lookup_header = { 
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "SW_VERSION" : "3.0",
        }

class Test_07_RecursiveSelectVersion_DefaultVersion(Test_05_RecursiveSelectVersion):
    insert_header = lookup_header = { 
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "SW_VERSION" : "default",
        }

class Test_08_RecursiveGeometricallyNearest(unittest.TestCase, RecursiveModify):
    result_filename = "./recursive_geometrically_nearest.rmap"
    expected_lookup_result = "foo.fits"
    rmap_str = '''
header = {
    'derived_from' : 'Hand written 01-15-2013',
    'filekind' : 'TFILEKIND',
    'instrument' : 'TINSTR',
    'mapping' : 'REFERENCE',
    'name' : 'test.rmap',
    'observatory' : 'TOBS',
    'parkey' : (('GEOM_PAR',), ('MATCH_PAR1','MATCH_PAR2'),),
    'sha1sum' : 'd412b94d1af1a0871fe39d7096e65aea1187c3b7',
    'classes' : ('GeometricallyNearest','Match',)
}

selector = GeometricallyNearest({
    0.1: Match({
        ('MPX', '98.7') : 'bar.fits',
    }),
    2.8 : Match({
    }),
    99.0 : Match({    
    }),
})
'''
    insert_header = lookup_header = { 
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "GEOM_PAR" : "1.2",
        }
class Test_09_RecursiveGeometricallyNearestExact(Test_08_RecursiveGeometricallyNearest):
    insert_header = lookup_header = { 
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "GEOM_PAR" : "0.1",
        }
    
class Test_10_RecursiveBracket(unittest.TestCase, RecursiveModify):
    result_filename = "./recursive_bracket.rmap"
    expected_lookup_result = ("foo.fits", "foo.fits")
    rmap_str = '''
header = {
    'derived_from' : 'Hand written 01-15-2013',
    'filekind' : 'TFILEKIND',
    'instrument' : 'TINSTR',
    'mapping' : 'REFERENCE',
    'name' : 'test.rmap',
    'observatory' : 'TOBS',
    'parkey' : (('BRACKET_PAR',), ('MATCH_PAR1','MATCH_PAR2'),),
    'sha1sum' : 'd412b94d1af1a0871fe39d7096e65aea1187c3b7',
    'classes' : ('Bracket','Match',)
}

selector = Bracket({
    0.1: Match({
        ('MPX', '98.7') : 'bar.fits',
    }),
    2.8 : Match({
        ('MPX', '98.7') : 'bar.fits',
    }),
    99.0 : Match({    
    }),
})
'''
    insert_header = lookup_header = { 
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "BRACKET_PAR" : "0.5",
        }
class Test_11_RecursiveBracketExact(Test_10_RecursiveBracket):
    expected_lookup_result = ("foo.fits", "foo.fits")
    insert_header = lookup_header = { 
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "BRACKET_PAR" : "0.1",
        }

class Test_12_RecursiveBracketExactMidLookup(Test_10_RecursiveBracket):
    expected_lookup_result = ("foo.fits", "bar.fits")
    insert_header = {
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "BRACKET_PAR" : "0.1",
        }
    lookup_header = { 
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "BRACKET_PAR" : "0.5",
        }
    rmap_str = '''
header = {
    'derived_from' : 'Hand written 01-15-2013',
    'filekind' : 'TFILEKIND',
    'instrument' : 'TINSTR',
    'mapping' : 'REFERENCE',
    'name' : 'test.rmap',
    'observatory' : 'TOBS',
    'parkey' : (('BRACKET_PAR',), ('MATCH_PAR1','MATCH_PAR2'),),
    'sha1sum' : 'd412b94d1af1a0871fe39d7096e65aea1187c3b7',
    'classes' : ('Bracket','Match',)
}

selector = Bracket({
    0.1: Match({
        ('MP1', '99.9') : 'bar.fits',
    }),
    2.8 : Match({
        ('MP1', '99.9') : 'bar.fits',
    }),
    99.0 : Match({    
    }),
})
'''
    

        
if __name__ == '__main__':
    unittest.main()

