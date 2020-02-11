import os
import json
import shutil
import datetime

from crds import bestrefs
from crds.bestrefs import BestrefsScript
from crds import assign_bestrefs
from crds.tests import test_config

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

    % crds bestrefs --new-context hst.pmap --files j8bt05njq_raw.fits j8bt06o6q_raw.fits j8bt09jcq_raw.fits

the first parameter, hst.pmap,  is the context with respect to which best references are determined.

2. To find best references for a list of catalog dataset ids do something like this:

    % crds bestrefs --new-context hst.pmap --datasets j8bt05njq j8bt06o6q j8bt09jcq

3. To do mass scale testing for all cataloged datasets for a particular instrument(s) do:

    % crds bestrefs --new-context hst.pmap --instruments acs

4. To do mass scale testing for all supported instruments for all cataloged datasets do:

    % crds bestrefs --new-context hst.pmap --all

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

    % crds bestrefs --new-context hst.pmap --files j8bt05njq_raw.fits j8bt06o6q_raw.fits j8bt09jcq_raw.fits --compare-source-bestrefs --print-affected
    j8bt05njq_raw.fits
    j8bt06o6q_raw.fits
    j8bt09jcq_raw.fits
"""

def dt_bestrefs_3_files():
    """
    Compute simple bestrefs for 3 files:

    >>> old_state = test_config.setup()

    >>> BestrefsScript(argv="bestrefs.py --new-context hst.pmap --files data/j8bt05njq_raw.fits data/j8bt06o6q_raw.fits data/j8bt09jcq_raw.fits")()
    CRDS - INFO - No comparison context or source comparison requested.
    CRDS - INFO - No file header updates requested;  dry run.  Use --update-bestrefs to update FITS headers.
    CRDS - INFO - ===> Processing data/j8bt05njq_raw.fits
    CRDS - INFO - ===> Processing data/j8bt06o6q_raw.fits
    CRDS - INFO - ===> Processing data/j8bt09jcq_raw.fits
    CRDS - INFO - 0 errors
    CRDS - INFO - 0 warnings
    CRDS - INFO - 5 infos
    0

    >>> test_config.cleanup(old_state)
    """

def dt_bestrefs_compare_source_files():
    """
    Compute and print files with at least one reference change:

    >>> old_state = test_config.setup()

    >>> BestrefsScript(argv="bestrefs.py --new-context hst.pmap --files data/j8bt05njq_raw.fits data/j8bt06o6q_raw.fits data/j8bt09jcq_raw.fits --print-affected --compare-source-bestrefs")()
    CRDS - INFO -  No file header updates requested;  dry run.  Use --update-bestrefs to update FITS headers.
    CRDS - INFO -  ===> Processing data/j8bt05njq_raw.fits
    CRDS - INFO -  instrument='ACS' type='ATODTAB' data='data/j8bt05njq_raw.fits' ::  New best reference: 'kcb1734ij_a2d.fits' --> 'n/a' :: Would update.
    CRDS - INFO -  instrument='ACS' type='CRREJTAB' data='data/j8bt05njq_raw.fits' ::  New best reference: 'n4e12510j_crr.fits' --> 'n/a' :: Would update.
    CRDS - INFO -  instrument='ACS' type='IMPHTTAB' data='data/j8bt05njq_raw.fits' ::  New best reference: 'n/a' --> 'w3m1716tj_imp.fits' :: Would update.
    CRDS - INFO -  instrument='ACS' type='NPOLFILE' data='data/j8bt05njq_raw.fits' ::  New best reference: 'n/a' --> 'v9718263j_npl.fits' :: Would update.
    CRDS - INFO -  instrument='ACS' type='SHADFILE' data='data/j8bt05njq_raw.fits' ::  New best reference: 'kcb1734pj_shd.fits' --> 'n/a' :: Would update.
    CRDS - INFO -  ===> Processing data/j8bt06o6q_raw.fits
    CRDS - INFO -  instrument='ACS' type='ATODTAB' data='data/j8bt06o6q_raw.fits' ::  New best reference: 'kcb1734ij_a2d.fits' --> 'n/a' :: Would update.
    CRDS - INFO -  instrument='ACS' type='CRREJTAB' data='data/j8bt06o6q_raw.fits' ::  New best reference: 'n4e12510j_crr.fits' --> 'n/a' :: Would update.
    CRDS - INFO -  instrument='ACS' type='IMPHTTAB' data='data/j8bt06o6q_raw.fits' ::  New best reference: 'n/a' --> 'w3m1716tj_imp.fits' :: Would update.
    CRDS - INFO -  instrument='ACS' type='NPOLFILE' data='data/j8bt06o6q_raw.fits' ::  New best reference: 'n/a' --> 'v9718264j_npl.fits' :: Would update.
    CRDS - INFO -  instrument='ACS' type='SHADFILE' data='data/j8bt06o6q_raw.fits' ::  New best reference: 'kcb1734pj_shd.fits' --> 'n/a' :: Would update.
    CRDS - INFO -  ===> Processing data/j8bt09jcq_raw.fits
    CRDS - INFO -  instrument='ACS' type='ATODTAB' data='data/j8bt09jcq_raw.fits' ::  New best reference: 'kcb1734ij_a2d.fits' --> 'n/a' :: Would update.
    CRDS - INFO -  instrument='ACS' type='IMPHTTAB' data='data/j8bt09jcq_raw.fits' ::  New best reference: 'n/a' --> 'w3m1716tj_imp.fits' :: Would update.
    CRDS - INFO -  instrument='ACS' type='NPOLFILE' data='data/j8bt09jcq_raw.fits' ::  New best reference: 'n/a' --> 'v9718260j_npl.fits' :: Would update.
    CRDS - INFO -  instrument='ACS' type='SHADFILE' data='data/j8bt09jcq_raw.fits' ::  New best reference: 'kcb1734pj_shd.fits' --> 'n/a' :: Would update.
    CRDS - INFO -  Affected products = 3
    data/j8bt05njq_raw.fits
    data/j8bt06o6q_raw.fits
    data/j8bt09jcq_raw.fits
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  19 infos
    0

    >>> test_config.cleanup(old_state)
    """

def dt_bestrefs_3_files_default_context_from_server():
    """
    Compute simple bestrefs for 3 files using the default context from the server:

    >>> old_state = test_config.setup()

    >>> BestrefsScript(argv="bestrefs.py --new-context=hst.pmap --files data/j8bt05njq_raw.fits data/j8bt06o6q_raw.fits data/j8bt09jcq_raw.fits")()
    CRDS - INFO - No comparison context or source comparison requested.
    CRDS - INFO - No file header updates requested;  dry run.  Use --update-bestrefs to update FITS headers.
    CRDS - INFO - ===> Processing data/j8bt05njq_raw.fits
    CRDS - INFO - ===> Processing data/j8bt06o6q_raw.fits
    CRDS - INFO - ===> Processing data/j8bt09jcq_raw.fits
    CRDS - INFO - 0 errors
    CRDS - INFO - 0 warnings
    CRDS - INFO - 5 infos
    0

    >>> test_config.cleanup(old_state)
    """

def dt_bestrefs_broken_dataset_file():
    """
    Same + one broken file to test shell error status

    >>> old_state = test_config.setup()

    >>> BestrefsScript(argv="bestrefs.py --new-context hst.pmap --files data/j8bt05njq_raw.fits data/j8bt05njq_raw_broke.fits data/j8bt06o6q_raw.fits data/j8bt09jcq_raw.fits")()
    CRDS - INFO - No comparison context or source comparison requested.
    CRDS - INFO - No file header updates requested;  dry run.  Use --update-bestrefs to update FITS headers.
    CRDS - INFO - ===> Processing data/j8bt05njq_raw.fits
    CRDS - INFO - ===> Processing data/j8bt05njq_raw_broke.fits
    CRDS - ERROR - instrument='ACS' type='BIASFILE' data='data/j8bt05njq_raw_broke.fits' ::  New: Bestref FAILED:   parameter='CCDAMP' value='FOOBAR' is not in ['A', 'ABCD', 'AC', 'AD', 'B', 'BC', 'BD', 'C', 'D']
    CRDS - INFO - ===> Processing data/j8bt06o6q_raw.fits
    CRDS - INFO - ===> Processing data/j8bt09jcq_raw.fits
    CRDS - INFO - 1 errors
    CRDS - INFO - 0 warnings
    CRDS - INFO - 6 infos
    1

    >>> test_config.cleanup(old_state)
    """

def dt_bestrefs_broken_cache_and_server():
    """


    >>> old_state = test_config.setup(cache="/nowhere", url="https://server-is-out-of-town")

    >> BestrefsScript(argv="bestrefs.py --new-context hst.pmap --files data/j8bt05njq_raw.fits")()
    CRDS - ERROR - (FATAL) CRDS server connection and cache load FAILED.  Cannot continue.  See https://hst-crds.stsci.edu or https://jwst-crds.stsci.edu for more information on configuring CRDS.
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
    CRDS - INFO - Dumping dataset parameters from CRDS server at '...' for ['LB6M01030']
    CRDS - INFO - Dumped 1 of 1 datasets from CRDS server at '...'
    CRDS - INFO - Computing bestrefs for datasets ['LB6M01030']
    CRDS - INFO - No comparison context or source comparison requested.
    CRDS - INFO - 0 errors
    CRDS - INFO - 0 warnings
    CRDS - INFO - 4 infos
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
    CRDS - INFO - No file header updates requested;  dry run.  Use --update-bestrefs to update FITS headers.
    CRDS - INFO - ===> Processing data/j8bt05njq_raw.fits
    CRDS - INFO - ===> Processing data/j8bt06o6q_raw.fits
    CRDS - INFO - ===> Processing data/j8bt09jcq_raw.fits
    CRDS - INFO - 0 errors
    CRDS - INFO - 0 warnings
    CRDS - INFO - 4 infos
    0

    >>> test_config.cleanup(old_state)
    """

def dt_bestrefs_all_instruments_hst():
    """
    Compute comparison bestrefs between two contexts:

    >>> old_state = test_config.setup()
    >>> script = BestrefsScript(argv="bestrefs.py --new-context data/hst_0001.pmap  --old-context hst.pmap --all-instruments") # doctest: +ELLIPSIS
    >>> script.complex_init()
    CRDS - INFO -  Computing bestrefs for db datasets for ['acs', 'cos', 'nicmos', 'stis', 'wfc3', 'wfpc2']
    CRDS - INFO -  Dumping dataset parameters for 'acs' from CRDS server at '...'
    CRDS - INFO -  Downloaded  ... dataset ids for 'acs' since None
    CRDS - INFO -  Dumping dataset parameters for 'cos' from CRDS server at '...'
    CRDS - INFO -  Downloaded  ... dataset ids for 'cos' since None
    CRDS - INFO -  Dumping dataset parameters for 'nicmos' from CRDS server at '...'
    CRDS - INFO -  Downloaded  ... dataset ids for 'nicmos' since None
    CRDS - INFO -  Dumping dataset parameters for 'stis' from CRDS server at '...'
    CRDS - INFO -  Downloaded  ... dataset ids for 'stis' since None
    CRDS - INFO -  Dumping dataset parameters for 'wfc3' from CRDS server at '...'
    CRDS - INFO -  Downloaded  ... dataset ids for 'wfc3' since None
    CRDS - INFO -  Dumping dataset parameters for 'wfpc2' from CRDS server at '...'
    CRDS - INFO -  Downloaded  ... dataset ids for 'wfpc2' since None
    True
    >>> test_config.cleanup(old_state)
    """

def dt_bestrefs_datasets_since_auto_hst():
    """
    Compute comparison bestrefs between two contexts:

    >>> old_state = test_config.setup()
    >>> script = BestrefsScript(argv="bestrefs.py --old-context hst.pmap --new-context data/hst_0001.pmap --diffs-only --datasets-since=auto") # doctest: +ELLIPSIS
    >>> script.complex_init()
    CRDS - INFO -  Mapping differences from 'hst.pmap' --> 'data/hst_0001.pmap' affect:
     {'acs': ['biasfile']}
    CRDS - INFO -  Possibly affected --datasets-since dates determined by 'hst.pmap' --> 'data/hst_0001.pmap' are:
     {'acs': '1992-01-02 00:00:00'}
    CRDS - INFO -  Computing bestrefs for db datasets for ['acs']
    CRDS - INFO -  Dumping dataset parameters for 'acs' from CRDS server at '...' since '1992-01-02 00:00:00'
    CRDS - INFO -  Downloaded  ... dataset ids for 'acs' since '1992-01-02 00:00:00'
    True
    >>> test_config.cleanup(old_state)
    """

def dt_bestrefs_dataset_drop_ids():
    """
    >>> old_state = test_config.setup()
    >>> script = BestrefsScript(argv="bestrefs.py --new-context data/hst_0001.pmap  --old-context hst.pmap --load-pickle data/test_cos.json --drop-ids LCE31SW6Q:LCE31SW6Q")
    >>> script.complex_init()
    CRDS - INFO -  Loading file 'data/test_cos.json'
    CRDS - INFO -  Loaded 1 datasets from file 'data/test_cos.json' completely replacing existing headers.
    True
    >>> test_config.cleanup(old_state)
    """

def dt_bestrefs_dataset_only_ids():
    """
    >>> old_state = test_config.setup()
    >>> script = BestrefsScript(argv="bestrefs.py --new-context data/hst_0001.pmap  --old-context hst.pmap --load-pickle data/test_cos.json --only-ids LPPPPPP6Q:LCE31SW6Q")
    >>> script.complex_init()
    CRDS - INFO -  Loading file 'data/test_cos.json'
    CRDS - INFO -  Loaded 1 datasets from file 'data/test_cos.json' completely replacing existing headers.
    True
    >>> test_config.cleanup(old_state)
    """

def dt_bestrefs_compare_source_canary():
    """
    >>> old_state = test_config.setup()
    >>> BestrefsScript("crds.bestrefs --new-context hst_0551.pmap --compare-source --load-pickles data/canary.json --differences-are-errors")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Loading file 'data/canary.json'
    CRDS - INFO -  Loaded 1 datasets from file 'data/canary.json' completely replacing existing headers.
    CRDS - ERROR -  instrument='COS' type='BPIXTAB' data='LA7803FIQ' ::  Comparison difference: 'bar.fits' --> 'yae1249sl_bpix.fits' :: Would update.
    CRDS - ERROR -  instrument='COS' type='XWLKFILE' data='LA7803FIQ' ::  Comparison difference: 'foo.fits' --> '14o2013ql_xwalk.fits' :: Would update.
    CRDS - INFO -  2 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  2 infos
    2
    >>> test_config.cleanup(old_state)
    """

def dt_bestrefs_multiple_updates_with_error():
    """
    >>> old_state = test_config.setup()
    >>> BestrefsScript("crds.bestrefs --old-context hst_0628.pmap --new-context hst_0633.pmap --print-affected --load-pickle data/bestrefs_new_error.json --verbosity=30")() # doctest: +ELLIPSIS
    CRDS - DEBUG -  Command: ['crds.bestrefs', '--old-context', 'hst_0628.pmap', '--new-context', 'hst_0633.pmap', '--print-affected', '--load-pickle', 'data/bestrefs_new_error.json', '--verbosity=30']
    CRDS - DEBUG -  Using explicit new context 'hst_0633.pmap' for computing updated best references.
    CRDS - DEBUG -  Using explicit old context 'hst_0628.pmap'
    CRDS - INFO -  Loading file 'data/bestrefs_new_error.json'
    CRDS - INFO -  Loaded 1 datasets from file 'data/bestrefs_new_error.json' completely replacing existing headers.
    CRDS - DEBUG -  ===> Processing JA9553M3Q:JA9553M3Q
    CRDS - DEBUG -  instrument='ACS' type='ATODTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
    CRDS - ERROR -  instrument='ACS' type='BIASFILE' data='JA9553M3Q' ::  New: Bestref FAILED:   parameter='CCDGAIN' value='1.4' is not in ['1.0', '2.0', '4.0', '8.0']
    CRDS - DEBUG -  instrument='ACS' type='BPIXTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 't3n1116nj_bpx.fits' :: No update.
    CRDS - DEBUG -  instrument='ACS' type='CCDTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'uc82140bj_ccd.fits' :: No update.
    CRDS - DEBUG -  instrument='ACS' type='CFLTFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
    CRDS - DEBUG -  instrument='ACS' type='CRREJTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
    CRDS - DEBUG -  instrument='ACS' type='D2IMFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
    CRDS - INFO -  instrument='ACS' type='DARKFILE' data='JA9553M3Q:JA9553M3Q' ::  New best reference: '1ag2019jj_drk.fits' --> '25815071j_drk.fits' :: Would update.
    CRDS - DEBUG -  instrument='ACS' type='DGEOFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'qbu16423j_dxy.fits' :: No update.
    CRDS - INFO -  instrument='ACS' type='DRKCFILE' data='JA9553M3Q:JA9553M3Q' ::  New best reference: '1ag20119j_dkc.fits' --> '2581508ij_dkc.fits' :: Would update.
    CRDS - DEBUG -  instrument='ACS' type='FLSHFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
    CRDS - DEBUG -  instrument='ACS' type='IDCTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: '0461802dj_idc.fits' :: No update.
    CRDS - DEBUG -  instrument='ACS' type='IMPHTTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
    CRDS - DEBUG -  instrument='ACS' type='MDRIZTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
    CRDS - DEBUG -  instrument='ACS' type='MLINTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
    CRDS - DEBUG -  instrument='ACS' type='NPOLFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
    CRDS - DEBUG -  instrument='ACS' type='OSCNTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: '17717071j_osc.fits' :: No update.
    CRDS - DEBUG -  instrument='ACS' type='PCTETAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: '19i16323j_cte.fits' :: No update.
    CRDS - DEBUG -  instrument='ACS' type='PFLTFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
    CRDS - DEBUG -  instrument='ACS' type='SHADFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
    CRDS - DEBUG -  instrument='ACS' type='SNKCFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
    CRDS - DEBUG -  instrument='ACS' type='SPOTTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
    CRDS - INFO -  Affected products = 0
    CRDS - DEBUG -  1 sources processed
    CRDS - DEBUG -  0 source updates
    CRDS - INFO -  1 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  5 infos
    1
    >>> test_config.cleanup(old_state)
    """

def dt_test_cleanpath():
    """
    Removes prefixes added to reference files prior to writing into FITS headers.

    HST IRAF-style env path prefix

    >>> bestrefs.cleanpath("jref$foo.fits")
    'foo.fits'

    JWST URI-style prefix

    >>> bestrefs.cleanpath('crds://foo.fits')
    'foo.fits'

    >>> bestrefs.cleanpath('foo.fits')
    'foo.fits'

    >>> bestrefs.cleanpath('something/foo.fits')
    'something/foo.fits'
    """

def dt_test_hst_tobs_header_to_reftypes():
    """
    >>> from crds.hst.locate import header_to_reftypes
    >>> header_to_reftypes({}, "hst.pmap")
    []
    >>> from crds.tobs.locate import header_to_reftypes
    >>> header_to_reftypes({}, "tobs.pmap")
    []
    """

def dt_test_jwst_header_to_reftypes():
    """
    >>> from crds.jwst.locate import header_to_reftypes

    >>> header_to_reftypes({"EXP_TYPE":"MIR_DARK", "CAL_VER": "0.7.0"}, "jwst_0301.pmap")
    ['ipc', 'linearity', 'mask', 'refpix', 'rscd', 'saturation', 'superbias']

    >>> header_to_reftypes({"EXP_TYPE":"NIR_IMAGE", "CAL_VER": "0.7.0"}, "jwst_0301.pmap")
    []

    # Traceback (most recent call last):
    # ...
    # RuntimeError: Unhandled EXP_TYPE 'NIR_IMAGE'

    >>> header_to_reftypes({"EXP_TYPE":"MIR_IMAGE", "CAL_VER": "0.7.0"}, "jwst_0301.pmap")
    ['area', 'camera', 'collimator', 'dark', 'disperser', 'distortion', 'filteroffset', 'fore', 'fpa', 'gain', 'ifufore', 'ifupost', 'ifuslicer', 'ipc', 'linearity', 'mask', 'msa', 'ote', 'photom', 'readnoise', 'refpix', 'regions', 'rscd', 'saturation', 'specwcs', 'superbias', 'v2v3', 'wavelengthrange']
    """

class TestBestrefs(test_config.CRDSTestCase):

    script_class = BestrefsScript
    # server_url = "https://hst-crds-dev.stsci.edu"
    cache = test_config.CRDS_TESTING_CACHE

    def get_10_days_ago(self):
        now = datetime.datetime.now()
        now -= datetime.timedelta(days=10)
        return now.isoformat().split("T")[0]

    def test_bestrefs_affected_datasets(self):
        self.run_script(f"crds.bestrefs --affected-datasets --old-context hst_0543.pmap --new-context hst_0544.pmap "
                        f"--datasets-since {self.get_10_days_ago()}",
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
        self.run_script(f"crds.bestrefs --instrument cos --new-context hst_0315.pmap --save-pickle test_cos.json "
                        f"--datasets-since {self.get_10_days_ago()}", expected_errs=None)
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
        self.assertEqual(badttab, "N/A")
        gsagtab = header["GSAGTAB"]
        self.assertEqual(gsagtab, "X6L1439EL_GSAG.FITS")
        flatfile = header["FLATFILE"]
        self.assertEqual(flatfile, "N/A")
        os.remove("./test_cos_combined.json")

    def test_assign_bestrefs(self):
        test_copy = "cos_N8XTZCAWQ_updated.fits"
        shutil.copy("data/cos_N8XTZCAWQ.fits", test_copy)

        errors = assign_bestrefs([test_copy], context="hst_0500.pmap")
        self.assertEqual(errors, 0)

        os.remove(test_copy)


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
