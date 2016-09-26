from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os
import json
import shutil

from crds.bestrefs import BestrefsScript
from crds.tests import test_config

BESTREFS = {
        "FLATFILE": 'x5v1944hl_flat.fits',
        "BADTTAB" : "NOT FOUND n/a",
        "BRFTAB" : "UNDEFINED",
        "TRACETAB" : "NOT FOUND some other error",
        }

def dt_bestrefs_na_undefined_single_ctx_defaults():
    """
    >>> old_state = test_config.setup()
    
    Instantiate a BestrefsScript with default settings and dummy parameters,  simulating pipeline bestrefs defaults:

    >>> script = BestrefsScript(argv="crds.bestrefs --load-pickles data/bestrefs.special.json --new-context hst_0315.pmap")
    >>> script.complex_init()
    CRDS - INFO - Loading file 'data/bestrefs.special.json'
    CRDS - INFO - Loaded 1 datasets from file 'data/bestrefs.special.json' completely replacing existing headers.
    CRDS - INFO - No comparison context or source comparison requested.
    True

    Skip ahead past bestrefs (faked) into special values results evaluation.

    First a postitive result:  OK,  lowercase-original-result,  uppercase-final-result-for-update
    
    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "FLATFILE",
    ... ("NOT FOUND NO MATCH","UNDEFINED"))
    (True, 'x5v1944hl_flat.fits', 'X5V1944HL_FLAT.FITS')
    
    Second a formal N/A result:  OK,  bestrefs string,  final update value

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "BADTTAB",
    ... ("NOT FOUND NO MATCH","UNDEFINED"))
    (True, 'NOT FOUND n/a', 'N/A')

    An explicit response of UNDEFINED,  by default converted to N/A for update,  considered OK
    
    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "BRFTAB",
    ... ("NOT FOUND NO MATCH","UNDEFINED"))
    (True, 'UNDEFINED', 'N/A')
    
    An implicit response of UNDEFINED, i.e. OMIT, also coverted to N/A for update

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "XTRACTAB",
    ... ("NOT FOUND NO MATCH","UNDEFINED"))
    (True, 'UNDEFINED', 'N/A')

    An explicit error response from CRDS,  not OK

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "TRACETAB",
    ... ("NOT FOUND NO MATCH","UNDEFINED"))
    CRDS - ERROR - instrument='COS' type='TRACETAB' data='LA9K03C3Q:LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    (False, 'NOT FOUND some other error', 'NOT FOUND SOME OTHER ERROR')
    
    >>> test_config.cleanup(old_state)
    
    """

def dt_bestrefs_na_undefined_single_ctx_undefined_matters():
    """
    >>> old_state = test_config.setup()
    
    Instantiate a BestrefsScript with default settings and dummy parameters,  simulating pipeline bestrefs defaults:

    >>> script = BestrefsScript(argv="crds.bestrefs --load-pickles data/bestrefs.special.json --undefined-differences-matter --new-context hst_0315.pmap")
    >>> script.complex_init()
    CRDS - INFO - Loading file 'data/bestrefs.special.json'
    CRDS - INFO - Loaded 1 datasets from file 'data/bestrefs.special.json' completely replacing existing headers.
    CRDS - INFO - No comparison context or source comparison requested.
    True

    Skip ahead past bestrefs (faked) into special values results evaluation.

    First a postitive result:  OK,  lowercase-original-result,  uppercase-final-result-for-update
    
    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "FLATFILE",
    ... ("NOT FOUND NO MATCH","UNDEFINED"))
    (True, 'x5v1944hl_flat.fits', 'X5V1944HL_FLAT.FITS')
    
    Second a formal N/A result:  OK,  bestrefs string,  final update value

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "BADTTAB",
    ... ("NOT FOUND NO MATCH","UNDEFINED"))
    (True, 'NOT FOUND n/a', 'N/A')

    An explicit response of UNDEFINED,  by default converted to N/A for update,  considered OK
    
    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "BRFTAB",
    ... ("NOT FOUND NO MATCH","UNDEFINED"))
    (True, 'UNDEFINED', 'N/A')
    
    An implicit response of UNDEFINED, i.e. OMIT, also coverted to N/A for update

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "XTRACTAB",
    ... ("NOT FOUND NO MATCH","UNDEFINED"))
    (True, 'UNDEFINED', 'N/A')

    An explicit error response from CRDS,  not OK

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "TRACETAB",
    ... ("NOT FOUND NO MATCH","UNDEFINED"))
    CRDS - ERROR - instrument='COS' type='TRACETAB' data='LA9K03C3Q:LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    (False, 'NOT FOUND some other error', 'NOT FOUND SOME OTHER ERROR')
    
    >>> test_config.cleanup(old_state)
    
    """

def dt_bestrefs_na_undefined_single_ctx_na_matters():
    """
    >>> old_state = test_config.setup()
    
    Instantiate a BestrefsScript with default settings and dummy parameters,  simulating pipeline bestrefs defaults:

    >>> script = BestrefsScript(argv="crds.bestrefs --load-pickles data/bestrefs.special.json --na-differences-matter --new-context hst_0315.pmap")
    >>> script.complex_init()
    CRDS - INFO - Loading file 'data/bestrefs.special.json'
    CRDS - INFO - Loaded 1 datasets from file 'data/bestrefs.special.json' completely replacing existing headers.
    CRDS - INFO - No comparison context or source comparison requested.
    True

    Skip ahead past bestrefs (faked) into special values results evaluation.

    First a postitive result:  OK,  lowercase-original-result,  uppercase-final-result-for-update
    
    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "FLATFILE",
    ... ("NOT FOUND NO MATCH","UNDEFINED"))
    (True, 'x5v1944hl_flat.fits', 'X5V1944HL_FLAT.FITS')
    
    Second a formal N/A result:  OK,  bestrefs string,  final update value

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "BADTTAB",
    ... ("NOT FOUND NO MATCH","UNDEFINED"))
    (True, 'NOT FOUND n/a', 'N/A')

    An explicit response of UNDEFINED,  by default converted to N/A for update,  considered OK
    
    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "BRFTAB",
    ... ("NOT FOUND NO MATCH","UNDEFINED"))
    CRDS - ERROR - instrument='COS' type='BRFTAB' data='LA9K03C3Q:LA9K03C3Q' ::  New: No match found => 'N/A'.
    (True, 'UNDEFINED', 'N/A')
    
    An implicit response of UNDEFINED, i.e. OMIT, also coverted to N/A for update

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "XTRACTAB",
    ... ("NOT FOUND NO MATCH","UNDEFINED"))
    CRDS - ERROR - instrument='COS' type='XTRACTAB' data='LA9K03C3Q:LA9K03C3Q' ::  New: No match found => 'N/A'.
    (True, 'UNDEFINED', 'N/A')

    An explicit error response from CRDS,  not OK

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "TRACETAB",
    ... ("NOT FOUND NO MATCH","UNDEFINED"))
    CRDS - ERROR - instrument='COS' type='TRACETAB' data='LA9K03C3Q:LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    (False, 'NOT FOUND some other error', 'NOT FOUND SOME OTHER ERROR')
    
    >>> test_config.cleanup(old_state)
    
    """

class TestBestrefs(test_config.CRDSTestCase):
    
    script_class = BestrefsScript
    # server_url = "https://hst-crds-dev.stsci.edu"
    cache = test_config.CRDS_TESTING_CACHE

    '''
    def test_bestrefs_affected_datasets(self):
        self.run_script("crds.bestrefs --affected-datasets --old-context hst_0314.pmap --new-context hst_0315.pmap --datasets-since 2015-01-01",
                        expected_errs=0)
        
    def test_bestrefs_from_pickle(self):
        self.run_script("crds.bestrefs --new-context hst_0315.pmap --load-pickle data/test_cos.pkl --stats --print-affected-details",
                        expected_errs=0)
        
    def test_bestrefs_to_pickle(self):
        self.run_script("crds.bestrefs --datasets LA9K03C3Q:LA9K03C3Q LA9K03C5Q:LA9K03C5Q LA9K03C7Q:LA9K03C7Q "
                        "--new-context hst_0315.pmap --save-pickle test_cos.pkl --stats",
                        expected_errs=0)
        os.remove("test_cos.pkl")
        
    def test_bestrefs_from_json(self):
        self.run_script("crds.bestrefs --new-context hst_0315.pmap --load-pickle data/test_cos.json --stats",
                        expected_errs=1)

    def test_bestrefs_to_json(self):
        self.run_script("crds.bestrefs --instrument cos --new-context hst_0315.pmap --save-pickle test_cos.json --datasets-since 2015-01-01 --stats",
                        expected_errs=None)
        os.remove("test_cos.json")

    def test_bestrefs_at_file(self):
        self.run_script("crds.bestrefs --files @data/bestrefs_file_list  --new-context hst_0315.pmap --stats",
                        expected_errs=0)
        
    def test_bestrefs_remote(self):
        self.run_script("crds.bestrefs --files @data/bestrefs_file_list  --new-context hst_0315.pmap --remote --stats",
                        expected_errs=0)
        
    def test_bestrefs_new_references(self):
        self.run_script("crds.bestrefs --files @data/bestrefs_file_list  --new-context hst_0315.pmap --print-new-references --stats",
                        expected_errs=0)

    def test_bestrefs_default_new_context(self):
        self.run_script("crds.bestrefs --files @data/bestrefs_file_list  --stats",
                        expected_errs=0)

    def test_bestrefs_update_file_headers(self):
        shutil.copy("data/j8bt06o6q_raw.fits", "j8bt06o6q_raw.fits")
        self.run_script("crds.bestrefs --files ./j8bt06o6q_raw.fits --new-context hst_0315.pmap --update-bestrefs",
                       expected_errs=0)
        os.remove("j8bt06o6q_raw.fits")

    def test_bestrefs_update_bestrefs(self):
        # """update_bestrefs modifies dataset file headers"""
        shutil.copy("data/j8bt06o6q_raw.fits", "j8bt06o6q_raw.fits")
        self.run_script("crds.bestrefs --files ./j8bt06o6q_raw.fits --new-context hst_0315.pmap --update-bestrefs",
                       expected_errs=0)
        os.remove("j8bt06o6q_raw.fits")

    def test_bestrefs_bad_sources(self):
        with self.assertRaises(AssertionError):
            self.run_script("crds.bestrefs --all-instruments --instrument cos --new-context hst_0315.pmap",
                            expected_errs=1)

    def test_bestrefs_update_headers(self):
        # """update_headers updates original headers from a pickle saving a new pickle withn orginal + overrides."""
        self.run_script("crds.bestrefs --new-context hst_0315.pmap --datasets LCE31SW6Q:LCE31SW6Q --load-pickle data/test_cos_update.json "
                        " --save-pickle ./test_cos_combined.json --update-bestrefs --update-pickle", expected_errs=1)
        with open("./test_cos_combined.json") as pfile:
            header = json.load(pfile)
        header = header["LCE31SW6Q:LCE31SW6Q"]
        badttab = header["BADTTAB"]
        assert badttab == "N/A"
        gsagtab = header["GSAGTAB"]
        assert gsagtab == "X6L1439EL_GSAG.FITS"
        flatfile = header["FLATFILE"] 
        assert flatfile == "N/A"
        os.remove("./test_cos_combined.json")

    '''

# ==================================================================================

def main():
    """Run module tests,  for now just doctests only."""
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBestrefs)
    unittest.TextTestRunner().run(suite)

    from crds.tests import test_special, tstmod
    return tstmod(test_special)

if __name__ == "__main__":
    print(main())

