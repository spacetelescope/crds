from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os
import json
import shutil

from crds.bestrefs import BestrefsScript
from crds.tests import CRDSTestCase, test_config, CRDS_CACHE_TEST

"""
Bestrefs has a number of command line parameters which make it operate in different modes. 

-----------
NEW CONTEXT
-----------

crds.bestrefs always computes best references with respect to a context which can be explicitly specified with the 
--new-context parameter.    If no --new-context is specified,  the default operational context is determined by 
consulting the CRDS server or looking in the local cache as a fallback.  

------------------------
LOOKUP PARAMETER SOURCES
------------------------

The two primary modes for bestrefs involve the source of reference file matching parameters.   Conceptually 
lookup parameters are always associated with particular datasets and used to identify the references
required to process those datasets.

The options --files, --datasets, --instruments, and --all determine the source of lookup parameters:

1. To find best references for a list of files do something like this:

    % python -m crds.bestrefs --new-context hst.pmap --files j8bt05njq_raw.fits j8bt06o6q_raw.fits j8bt09jcq_raw.fits

the first parameter, hst.pmap,  is the context with respect to which best references are determined.

2. To find best references for a list of catalog dataset ids do something like this:

    % python -m crds.bestrefs --new-context hst.pmap --datasets j8bt05njq j8bt06o6q j8bt09jcq

3. To do mass scale testing for all cataloged datasets for a particular instrument(s) do:

    % python -m crds.bestrefs --new-context hst.pmap --instruments acs

4. To do mass scale testing for all supported instruments for all cataloged datasets do:

    % python -m crds.bestrefs --new-context hst.pmap --all

----------------
COMPARISON MODES
----------------

The --old-context and --compare-source-bestrefs parameters define the best references comparison mode.  Each names
the origin of a set of prior recommendations and implicitly requests a comparison to the recommendations from 
the newly computed bestrefs determined by --new-context.

CONTEXT-TO-CONTEXT
..................

--old-context can be used to specify a second context for which bestrefs are dynamically computed; --old-context implies 
that a bestrefs comparison will be made with --new-context.   

PRIOR SOURCE RECOMMENDATIONS
............................

--compare-source-bestrefs requests that the bestrefs from --new-context be compared to the bestrefs which are
recorded with the lookup parameter data,  either in the file headers of data files,  or in the catalog.   In both
cases the prior best references are recorded static values,  not dynamically computed bestrefs.

------------
UPDATE MODES
------------

Currently there is only one update mode.   When --files are specified as the input source,  --update-bestrefs can 
also be specified to update the input data file headers with new bestrefs recommendations.   In this case the data
files are used as both the source of matching parameters and as the destination for best reference recommendations.

------------
OUTPUT MODES
------------

crds.bestrefs supports several output modes for bestrefs and comparison results.

If --print-affected is specified,  crds.bestrefs will print out the name of any file (or dataset id) for which at least one update for
one reference type was recommended.   This is essentially a list of files to be reprocessed with new references.

    % python -m crds.bestrefs --new-context hst.pmap --files j8bt05njq_raw.fits j8bt06o6q_raw.fits j8bt09jcq_raw.fits --compare-source-bestrefs --print-affected
    j8bt05njq_raw.fits
    j8bt06o6q_raw.fits
    j8bt09jcq_raw.fits
"""

def dt_bestrefs_3_files():
    """
    Compute simple bestrefs for 3 files:

    >>> old_state = test_config.setup()
    
    >>> BestrefsScript(argv="bestrefs.py --new-context hst.pmap --files data/j8bt05njq_raw.fits data/j8bt06o6q_raw.fits data/j8bt09jcq_raw.fits")()
    CRDS  : INFO     No comparison context or source comparison requested.
    CRDS  : INFO     No file header updates requested;  dry run.
    CRDS  : INFO     ===> Processing data/j8bt05njq_raw.fits
    CRDS  : INFO     ===> Processing data/j8bt06o6q_raw.fits
    CRDS  : INFO     ===> Processing data/j8bt09jcq_raw.fits
    CRDS  : INFO     0 errors
    CRDS  : INFO     0 warnings
    CRDS  : INFO     5 infos
    0
    
    >>> test_config.cleanup(old_state)
    """

def dt_bestrefs_compare_source_files():
    """
    Compute and print files with at least one reference change:

    >>> old_state = test_config.setup()
    
    >>> BestrefsScript(argv="bestrefs.py --new-context hst.pmap --files data/j8bt05njq_raw.fits data/j8bt06o6q_raw.fits data/j8bt09jcq_raw.fits --print-affected --compare-source-bestrefs")()
    CRDS  : INFO     No file header updates requested;  dry run.
    CRDS  : INFO     ===> Processing data/j8bt05njq_raw.fits
    CRDS  : INFO     instrument='ACS' type='ATODTAB' data='data/j8bt05njq_raw.fits' ::  New best reference: 'kcb1734ij_a2d.fits' --> 'n/a' :: Would update.
    CRDS  : INFO     instrument='ACS' type='CRREJTAB' data='data/j8bt05njq_raw.fits' ::  New best reference: 'n4e12510j_crr.fits' --> 'n/a' :: Would update.
    CRDS  : INFO     instrument='ACS' type='IMPHTTAB' data='data/j8bt05njq_raw.fits' ::  New best reference: 'undefined' --> 'w3m1716tj_imp.fits' :: Would update.
    CRDS  : INFO     instrument='ACS' type='NPOLFILE' data='data/j8bt05njq_raw.fits' ::  New best reference: 'undefined' --> 'v9718263j_npl.fits' :: Would update.
    CRDS  : INFO     instrument='ACS' type='SHADFILE' data='data/j8bt05njq_raw.fits' ::  New best reference: 'kcb1734pj_shd.fits' --> 'n/a' :: Would update.
    CRDS  : INFO     ===> Processing data/j8bt06o6q_raw.fits
    CRDS  : INFO     instrument='ACS' type='ATODTAB' data='data/j8bt06o6q_raw.fits' ::  New best reference: 'kcb1734ij_a2d.fits' --> 'n/a' :: Would update.
    CRDS  : INFO     instrument='ACS' type='CRREJTAB' data='data/j8bt06o6q_raw.fits' ::  New best reference: 'n4e12510j_crr.fits' --> 'n/a' :: Would update.
    CRDS  : INFO     instrument='ACS' type='IMPHTTAB' data='data/j8bt06o6q_raw.fits' ::  New best reference: 'undefined' --> 'w3m1716tj_imp.fits' :: Would update.
    CRDS  : INFO     instrument='ACS' type='NPOLFILE' data='data/j8bt06o6q_raw.fits' ::  New best reference: 'undefined' --> 'v9718264j_npl.fits' :: Would update.
    CRDS  : INFO     instrument='ACS' type='SHADFILE' data='data/j8bt06o6q_raw.fits' ::  New best reference: 'kcb1734pj_shd.fits' --> 'n/a' :: Would update.
    CRDS  : INFO     ===> Processing data/j8bt09jcq_raw.fits
    CRDS  : INFO     instrument='ACS' type='ATODTAB' data='data/j8bt09jcq_raw.fits' ::  New best reference: 'kcb1734ij_a2d.fits' --> 'n/a' :: Would update.
    CRDS  : INFO     instrument='ACS' type='IMPHTTAB' data='data/j8bt09jcq_raw.fits' ::  New best reference: 'undefined' --> 'w3m1716tj_imp.fits' :: Would update.
    CRDS  : INFO     instrument='ACS' type='NPOLFILE' data='data/j8bt09jcq_raw.fits' ::  New best reference: 'undefined' --> 'v9718260j_npl.fits' :: Would update.
    CRDS  : INFO     instrument='ACS' type='SHADFILE' data='data/j8bt09jcq_raw.fits' ::  New best reference: 'kcb1734pj_shd.fits' --> 'n/a' :: Would update.
    CRDS  : INFO     Affected products = 3
    data/j8bt05njq_raw.fits
    data/j8bt06o6q_raw.fits
    data/j8bt09jcq_raw.fits
    CRDS  : INFO     0 errors
    CRDS  : INFO     0 warnings
    CRDS  : INFO     19 infos
    0

    >>> test_config.cleanup(old_state)
    """

def dt_bestrefs_3_files_default_context_from_server():
    """
    Compute simple bestrefs for 3 files using the default context from the server:

    >>> old_state = test_config.setup()
    
    >>> BestrefsScript(argv="bestrefs.py --new-context=hst.pmap --files data/j8bt05njq_raw.fits data/j8bt06o6q_raw.fits data/j8bt09jcq_raw.fits")()
    CRDS  : INFO     No comparison context or source comparison requested.
    CRDS  : INFO     No file header updates requested;  dry run.
    CRDS  : INFO     ===> Processing data/j8bt05njq_raw.fits
    CRDS  : INFO     ===> Processing data/j8bt06o6q_raw.fits
    CRDS  : INFO     ===> Processing data/j8bt09jcq_raw.fits
    CRDS  : INFO     0 errors
    CRDS  : INFO     0 warnings
    CRDS  : INFO     5 infos
    0

    >>> test_config.cleanup(old_state)
    """

def dt_bestrefs_broken_dataset_file():
    """
    Same + one broken file to test shell error status

    >>> old_state = test_config.setup()
    
    >>> BestrefsScript(argv="bestrefs.py --new-context hst.pmap --files data/j8bt05njq_raw.fits data/j8bt05njq_raw_broke.fits data/j8bt06o6q_raw.fits data/j8bt09jcq_raw.fits")()
    CRDS  : INFO     No comparison context or source comparison requested.
    CRDS  : INFO     No file header updates requested;  dry run.
    CRDS  : INFO     ===> Processing data/j8bt05njq_raw.fits
    CRDS  : INFO     ===> Processing data/j8bt05njq_raw_broke.fits
    CRDS  : ERROR    instrument='ACS' type='BIASFILE' data='data/j8bt05njq_raw_broke.fits' ::  New: Bestref FAILED:   parameter='CCDAMP' value='FOOBAR' is not in ['A', 'ABCD', 'AC', 'AD', 'B', 'BC', 'BD', 'C', 'D']
    CRDS  : INFO     ===> Processing data/j8bt06o6q_raw.fits
    CRDS  : INFO     ===> Processing data/j8bt09jcq_raw.fits
    CRDS  : INFO     1 errors
    CRDS  : INFO     0 warnings
    CRDS  : INFO     6 infos
    1

    >>> test_config.cleanup(old_state)
    """

def dt_bestrefs_broken_cache_and_server():
    """
    

    >>> old_state = test_config.setup(cache="/nowhere", url="https://server-is-out-of-town")
    
    >> BestrefsScript(argv="bestrefs.py --new-context hst.pmap --files data/j8bt05njq_raw.fits")()
    CRDS  : ERROR    (FATAL) CRDS server connection and cache load FAILED.  Cannot continue.  See https://hst-crds.stsci.edu or https://jwst-crds.stsci.edu for more information on configuring CRDS.
    Traceback (most recent call last):
    ...
    SystemExit: 1

>>> test_config.cleanup(old_state)
    """

def dt_bestrefs_catalog_dataset():
    """
    Compute simple bestrefs for 1 catalog datasets using hst.pmap:

    >>> old_state = test_config.setup()
    
    >>> BestrefsScript(argv="bestrefs.py --new-context hst.pmap  --datasets LB6M01030")() # doctest: +ELLIPSIS
    CRDS  : INFO     Dumping dataset parameters from CRDS server at '...' for ['LB6M01030']
    CRDS  : INFO     Dumped 1 of 1 datasets from CRDS server at '...'
    CRDS  : INFO     Computing bestrefs for datasets ['LB6M01030']
    CRDS  : INFO     No comparison context or source comparison requested.
    CRDS  : INFO     0 errors
    CRDS  : INFO     0 warnings
    CRDS  : INFO     4 infos
    0

    >>> test_config.cleanup(old_state)

    MAINTENANCE NOTE:  the preceding test is currently an expected error case pending the delivery of a modified
    WFC3 FLSHFILE rmap located at crds/hst/prototypes/wfc3/hst_wfc3_flshfile_0251.rmap.  Once the modified rmap 
    is delivered to operations,  the above new-context should be changed to the new OPS context.  After that point,
    all mirrors of OPS to DEV should work without the exected errors due to FLASHCUR=='UNDEFINED'.   The only changes
    in the modified rmap should be header changes,  nominally the rmap_relevance expression;  additional changes
    may reflect new flshfile submissions which happened after the prototype rmap was created.
    """
    
def dt_bestrefs_context_to_context():
    """
    Compute comparison bestrefs between two contexts:
    
    >>> old_state = test_config.setup()
    
    >>> BestrefsScript(argv="bestrefs.py --new-context data/hst_0001.pmap  --old-context hst.pmap --files data/j8bt05njq_raw.fits data/j8bt06o6q_raw.fits data/j8bt09jcq_raw.fits")()
    CRDS  : INFO     No file header updates requested;  dry run.
    CRDS  : INFO     ===> Processing data/j8bt05njq_raw.fits
    CRDS  : INFO     ===> Processing data/j8bt06o6q_raw.fits
    CRDS  : INFO     ===> Processing data/j8bt09jcq_raw.fits
    CRDS  : INFO     0 errors
    CRDS  : INFO     0 warnings
    CRDS  : INFO     4 infos
    0
    
    >>> test_config.cleanup(old_state)
    """

class TestBestrefs(CRDSTestCase):
    
    script_class = BestrefsScript
    server_url = "https://hst-crds-dev.stsci.edu"
    cache = CRDS_CACHE_TEST

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

# ==================================================================================

def main():
    """Run module tests,  for now just doctests only."""
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBestrefs)
    unittest.TextTestRunner().run(suite)

    from crds.tests import test_bestrefs, tstmod
    return tstmod(test_bestrefs)

if __name__ == "__main__":
    print(main())

