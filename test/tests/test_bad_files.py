import os

import crds
from crds.core import log, utils, config
from crds import client
from crds.bestrefs import BestrefsScript

from crds.tests import test_config

# Contrived headers which will select bad files.

HST_HEADER = {
    'INSTRUME' : 'ACS',
    'REFTYPE' : 'PFLTFILE',
    'DETECTOR': 'SBC',
    'CCDAMP': 'N/A',
    'FILTER1' : 'PR110L',
    'FILTER2' : 'N/A',
    'OBSTYPE': 'SPECTROSCOPIC',
    'FW1OFFST' : 'N/A',
    'FW2OFFST': 'N/A',
    'FWOFFST': 'N/A',
    'DATE-OBS': '1991-01-01',
    'TIME-OBS': '00:00:00'
    }

JWST_HEADER = {
    "meta.instrument.name": "MIRI",
    "meta.observation.date": "2012-07-25T00:00:00",
    "meta.instrument.detector" : "MIRIMAGE",
    "meta.instrument.filter" : "F1000W",
    "meta.subarray.name" : "FULL",
    }

def dt_bad_references_error_cache_config():
    """
    CRDS can designate files as scientifically invalid which is reflected in the catalog
    on a the CRDS server and also recorded in the configuration info and as a bad files list
    which are written down in the "config" directory.

    A key aspect of bad files management is the location and contents of the cache config
    directory.  The current HST cache in trunk/crds/cache has a config area and 4 bad files.

    The default handling when a bad reference file is assigned is to raise an exception:

    >>> old_state = test_config.setup(clear_existing=False)
    >>> config.ALLOW_BAD_RULES.reset()
    >>> config.ALLOW_BAD_REFERENCES.reset()

    >>> crds.getreferences(HST_HEADER, observatory='hst', context='hst_0282.pmap', reftypes=['pfltfile'])
    Traceback (most recent call last):
    ...
    CrdsBadReferenceError: Recommended reference 'l2d0959cj_pfl.fits' of type 'pfltfile' is designated scientifically invalid.
    <BLANKLINE>

    >>> test_config.cleanup(old_state)
    """

def dt_bad_references_warning_cache_config():
    """
    A secondary behaviour is to permit use of bad references with a warning:

    >>> old_state = test_config.setup(clear_existing=False)
    >>> config.ALLOW_BAD_RULES.set("1")
    False
    >>> config.ALLOW_BAD_REFERENCES.set("1")
    False

    >>> crds.getreferences(HST_HEADER, observatory='hst', context='hst_0282.pmap', reftypes=['pfltfile'])    # doctest: +ELLIPSIS
    CRDS - WARNING - Recommended reference 'l2d0959cj_pfl.fits' of type 'pfltfile' is designated scientifically invalid.
    <BLANKLINE>
    {'pfltfile': '.../l2d0959cj_pfl.fits'}

    >>> test_config.cleanup(old_state)
    """

def dt_bad_references_fast_mode():
    """
    When run in 'fast' mode as is done for the calls from crds.bestrefs,  no exception or warning is possible:

    >>> old_state = test_config.setup(clear_existing=False)
    >>> config.ALLOW_BAD_RULES.reset()
    >>> config.ALLOW_BAD_REFERENCES.reset()

    >>> crds.getreferences(HST_HEADER, observatory='hst', context='hst_0282.pmap', reftypes=['pfltfile'], fast=True) # doctest: +ELLIPSIS
    {'pfltfile': '.../references/hst/l2d0959cj_pfl.fits'}

    >>> test_config.cleanup(old_state)
    """


def dt_bad_references_bestrefs_script_error():
    """
    The crds.bestrefs program handles bad files differently because it frequently operates on
    multiple contexts at the same time,  and recommending bad files under the old context is OK.

    >>> old_state = test_config.setup(clear_existing=False)
    >>> config.ALLOW_BAD_RULES.reset()
    >>> config.ALLOW_BAD_REFERENCES.reset()

    By default,  in crds.bestrefs use of a bad reference is an error:

    >>> BestrefsScript("crds.bestrefs --new-context hst_0282.pmap --files data/j8btxxx_raw_bad.fits")()
    CRDS - INFO - No comparison context or source comparison requested.
    CRDS - INFO - No file header updates requested;  dry run.  Use --update-bestrefs to update FITS headers.
    CRDS - INFO - ===> Processing data/j8btxxx_raw_bad.fits
    CRDS - ERROR - instrument='ACS' type='PFLTFILE' data='data/j8btxxx_raw_bad.fits' ::  File 'L2D0959CJ_PFL.FITS' is bad. Use is not recommended,  results may not be scientifically valid.
    CRDS - INFO - 1 errors
    CRDS - INFO - 0 warnings
    CRDS - INFO - 3 infos
    1

    >>> test_config.cleanup(old_state)
    """

def dt_bad_references_bestrefs_script_warning():
    """
    >>> old_state = test_config.setup(clear_existing=False)
    >>> config.ALLOW_BAD_RULES.set("1")
    False
    >>> config.ALLOW_BAD_REFERENCES.set("1")
    False

    >>> BestrefsScript("crds.bestrefs --new-context hst_0282.pmap --files data/j8btxxx_raw_bad.fits --allow-bad-references")() # doctest: +ELLIPSIS
    CRDS - INFO - No comparison context or source comparison requested.
    CRDS - INFO - No file header updates requested;  dry run.  Use --update-bestrefs to update FITS headers.
    CRDS - INFO - ===> Processing data/j8btxxx_raw_bad.fits
    CRDS - WARNING - For data/j8btxxx_raw_bad.fits ACS pfltfile File 'L2D0959CJ_PFL.FITS' is bad. Use is not recommended,  results may not be scientifically valid.
    CRDS - INFO - 0 errors
    CRDS - INFO - 1 warnings
    CRDS - INFO - 3 infos
    0

    >>> test_config.cleanup(old_state)
    """

def dt_bad_references_bestrefs_script_deprecated():
    """
    >>> old_state = test_config.setup(clear_existing=False)
    >>> config.ALLOW_BAD_RULES.reset()
    >>> config.ALLOW_BAD_REFERENCES.reset()

    >>> BestrefsScript("crds.bestrefs --new-context hst_0282.pmap --files data/j8btxxx_raw_bad.fits")() # doctest: +ELLIPSIS
    CRDS - INFO - No comparison context or source comparison requested.
    CRDS - INFO - No file header updates requested;  dry run.  Use --update-bestrefs to update FITS headers.
    CRDS - INFO - ===> Processing data/j8btxxx_raw_bad.fits
    CRDS - ERROR - instrument='ACS' type='PFLTFILE' data='data/j8btxxx_raw_bad.fits' ::  File 'L2D0959CJ_PFL.FITS' is bad. Use is not recommended,  results may not be scientifically valid.
    CRDS - INFO - 1 errors
    CRDS - INFO - 0 warnings
    CRDS - INFO - 3 infos
    1

    >>> test_config.cleanup(old_state)
    """

def dt_bad_rules_jwst_getreferences_error():
    """
    There is also a check for use of bad rules. JWST has a few,  including jwst_0017.pmap by "inheritance"
    since it includes some bad rules.

    Do some setup to switch to a JWST serverless mode.

    >>> old_state = test_config.setup(cache=test_config.CRDS_SHARED_GROUP_CACHE, url="https://jwst-serverless-mode.stsci.edu")
    >>> config.ALLOW_BAD_RULES.reset()
    >>> config.ALLOW_BAD_REFERENCES.reset()

    >>> crds.getreferences(JWST_HEADER, observatory='jwst', context='jwst_0017.pmap', reftypes=["flat"])
    Traceback (most recent call last):
    ...
    CrdsBadRulesError: Final context 'jwst_0017.pmap' is marked as scientifically invalid based on: ['jwst_miri_flat_0003.rmap']
    <BLANKLINE>

    >>> test_config.cleanup(old_state)
    """

def dt_bad_rules_jwst_getreferences_warning():
    """
    Similarly,  the use of bad rules can be permitted:

    >>> old_state = test_config.setup(cache=test_config.CRDS_SHARED_GROUP_CACHE, url="https://jwst-serverless-mode.stsci.edu")
    >>> config.ALLOW_BAD_RULES.set("1")
    False

    >>> refs = crds.getreferences(JWST_HEADER, observatory='jwst', context='jwst_0017.pmap', reftypes=["flat"])   # doctest: +ELLIPSIS
    CRDS - WARNING - Final context 'jwst_0017.pmap' is marked as scientifically invalid based on: ['jwst_miri_flat_0003.rmap']
    <BLANKLINE>

    >>> list(refs.keys()) == ['flat']
    True

    >>> os.path.basename(refs['flat'])
    'jwst_miri_flat_0006.fits'

    >>> test_config.cleanup(old_state)
    """

def dt_bad_rules_jwst_bestrefs_script_error():
    """
    Here try bad rules for a JWST dataset:

    >>> old_state = test_config.setup(cache=test_config.CRDS_SHARED_GROUP_CACHE, url="https://jwst-serverless-mode.stsci.edu")
    >>> config.ALLOW_BAD_RULES.reset()

    >>> crds.getrecommendations(JWST_HEADER, reftypes=["gain"], context="jwst_0017.pmap")    # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    CrdsBadRulesError: Final context 'jwst_0017.pmap' is marked as scientifically invalid based on: ['jwst_miri_flat_0003.rmap']
    <BLANKLINE>

    >>> test_config.cleanup(old_state)
    """

def main():
    """Run module tests,  for now just doctests only."""
    from crds.tests import test_bad_files, tstmod
    return tstmod(test_bad_files)

if __name__ == "__main__":
    print(main())
