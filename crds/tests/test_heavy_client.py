"""This module contains doctests and unit tests which exercise some of the more
complex features of the basic rmap infrastructure.
"""

from __future__ import division # confidence high
from __future__ import with_statement
from __future__ import print_function

import os
import json
from pprint import pprint as pp

from crds import rmap, log, config, tests, heavy_client
from crds.exceptions import *
from crds.tests import test_config
from crds.client import api

from nose.tools import assert_raises, assert_true

# ==================================================================================

def dt_getreferences_rmap_na():
    """
    >>> old_state = test_config.setup(cache=None, url="https://jwst-crds-dev.stsci.edu")
    >>> os.environ["CRDS_MAPPATH_SINGLE"] = test_config.TEST_DATA

    >>> heavy_client.getreferences({"META.INSTRUMENT.NAME":"NIRISS", "META.INSTRUMENT.DETECTOR":"NIS", "META.INSTRUMENT.FILTER":"BOGUS2"},
    ...    observatory="jwst", context="jwst_na_omit.pmap", ignore_cache=False)
    {'flat': 'NOT FOUND n/a'}

    >>> test_config.cleanup(old_state)
    
    >> config.get_crds_state()
    """

def dt_getreferences_rmap_omit():
    """
    >>> old_state = test_config.setup(cache=None, url="https://jwst-crds-dev.stsci.edu")
    >>> os.environ["CRDS_MAPPATH_SINGLE"] = test_config.TEST_DATA

    >>> heavy_client.getreferences({"META.INSTRUMENT.NAME":"NIRISS", "META.INSTRUMENT.DETECTOR":"NIS", "META.INSTRUMENT.FILTER":"BOGUS1"},
    ...    observatory="jwst", context="jwst_na_omit.pmap", ignore_cache=False)
    {}

    >>> test_config.cleanup(old_state)
    
    >> config.get_crds_state()
    """

def dt_getreferences_imap_na():
    """
    >>> old_state = test_config.setup(cache=None, url="https://jwst-crds-dev.stsci.edu")
    >>> os.environ["CRDS_MAPPATH_SINGLE"] = test_config.TEST_DATA

    >>> heavy_client.getreferences({"META.INSTRUMENT.NAME":"FGS",},
    ...    observatory="jwst", context="jwst_na_omit.pmap", ignore_cache=False)
    {'flat': 'NOT FOUND n/a'}

    >>> test_config.cleanup(old_state)
    """

def dt_getreferences_imap_omit():
    """
    >>> old_state = test_config.setup(cache=None, url="https://jwst-crds-dev.stsci.edu")
    >>> os.environ["CRDS_MAPPATH_SINGLE"] = test_config.TEST_DATA

    >>> heavy_client.getreferences({"META.INSTRUMENT.NAME":"MIRI",},
    ...    observatory="jwst", context="jwst_na_omit.pmap", ignore_cache=False)
    {}

    >>> test_config.cleanup(old_state)
    """

def dt_cache_references_multiple_bad_files():
    """

    Define bestrefs with multiple errors which should all be reported
    prior to raising an exception.

    >>> old_state = test_config.setup()

    >>> bestrefs = {
    ...    "flat": "NOT FOUND something went wrong for flat.",
    ...    "dark": "NOT FOUND something else went wrong for dark.",
    ... }

    To work effectively for JWST reference file coverage improvement,
    CRDS needs to report ALL bad references in a given Step or
    prefetch, not just raise an exception on the first bad reference
    found.

    >>> api.cache_references("jwst.pmap", bestrefs)
    Traceback (most recent call last):
    ...
    CrdsLookupError: Error determining best reference for 'flat'  =   something went wrong for flat.

    >>> test_config.cleanup(old_state)
    
    """

# ==================================================================================

# class TestHeavyClient(test_config.CRDSTestCase):

    """
    def test_rmap_get_imap_except(self):
        r = rmap.get_cached_mapping("hst.pmap")
        with self.assertRaises(CrdsUnknownInstrumentError):
            r.get_imap("foo")
    """

# ==================================================================================

def tst():
    """Run module tests,  for now just doctests only."""
    # import unittest
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestHeavyClient)
    # unittest.TextTestRunner().run(suite)

    from crds.tests import test_heavy_client, tstmod
    return tstmod(test_heavy_client)

if __name__ == "__main__":
    print(tst())

