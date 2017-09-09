"""This module contains doctests and unit tests which exercise the module that
builds on the crds.client web api and enhances it with fully developed cache
semantics.  crds.client is largely decoupled from the core CRDS modules and
focuses on JSONRPC calls and file downloads.   The heavy_client extends those
primitive functions to provide higher level APIs that are dependent on the 
core library to implement.
"""

from __future__ import division # confidence high
from __future__ import with_statement
from __future__ import print_function
from __future__ import absolute_import

import os
import json
from pprint import pprint as pp

from crds.core import rmap, log, config, heavy_client
from crds.core.exceptions import *
from crds import tests
from crds.tests import test_config
from crds.client import api

from nose.tools import assert_raises, assert_true

# ==================================================================================

def dt_getreferences_rmap_na():
    """ 
    >>> old_state = test_config.setup(cache=None, url="https://jwst-crds.stsci.edu")
    >>> os.environ["CRDS_MAPPATH_SINGLE"] = test_config.TEST_DATA

    >>> heavy_client.getreferences({"META.INSTRUMENT.NAME":"NIRISS", "META.INSTRUMENT.DETECTOR":"NIS",
    ...                             "META.INSTRUMENT.FILTER":"BOGUS2", "META.EXPOSURE.TYPE":"NIS_IMAGE"},
    ...    observatory="jwst", context="jwst_na_omit.pmap", ignore_cache=False, reftypes=["flat"])
    {'flat': 'NOT FOUND n/a'}

    >>> test_config.cleanup(old_state)
    
    >> config.get_crds_state()
    """

def dt_getreferences_rmap_omit():
    """
    >>> old_state = test_config.setup(cache=None, url="https://jwst-crds.stsci.edu")
    >>> os.environ["CRDS_MAPPATH_SINGLE"] = test_config.TEST_DATA

    >>> heavy_client.getreferences({"META.INSTRUMENT.NAME":"NIRISS", "META.INSTRUMENT.DETECTOR":"NIS", "META.INSTRUMENT.FILTER":"BOGUS1", "META.EXPOSURE.TYPE":"NIS_IMAGE"},
    ...    observatory="jwst", context="jwst_na_omit.pmap", ignore_cache=False, reftypes=["flat"])
    {}

    >>> test_config.cleanup(old_state)
    
    >> config.get_crds_state()
    """

def dt_getreferences_imap_na():
    """
    >>> old_state = test_config.setup(cache=None, url="https://jwst-crds.stsci.edu")
    >>> os.environ["CRDS_MAPPATH_SINGLE"] = test_config.TEST_DATA

    >>> heavy_client.getreferences({"META.INSTRUMENT.NAME":"FGS", "META.EXPOSURE.TYPE":"FGS_IMAGE"},
    ...    observatory="jwst", context="jwst_na_omit.pmap", ignore_cache=False, reftypes=["flat"])
    {'flat': 'NOT FOUND n/a'}

    >>> test_config.cleanup(old_state)
    """

def dt_getreferences_imap_omit():
    """
    >>> old_state = test_config.setup(cache=None, url="https://jwst-crds.stsci.edu")
    >>> os.environ["CRDS_MAPPATH_SINGLE"] = test_config.TEST_DATA

    >>> heavy_client.getreferences({"META.INSTRUMENT.NAME":"MIRI", "META.EXPOSURE.TYPE":"MIR_IMAGE"},
    ...    observatory="jwst", context="jwst_na_omit.pmap", ignore_cache=False, reftypes=["flat"])
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

def dt_get_context_name_literal():
    """
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> heavy_client.get_context_name("jwst", "jwst_0341.pmap")
    'jwst_0341.pmap'
    >>> test_config.cleanup(old_state)
    """

def dt_get_context_name_crds_context():
    """
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> os.environ["CRDS_CONTEXT"] = "jwst_0399.pmap"
    >>> heavy_client.get_context_name("jwst")
    'jwst_0399.pmap'
    >>> del os.environ["CRDS_CONTEXT"]
    >>> test_config.cleanup(old_state)
    """

def dt_get_context_name_symbolic():
    """
    >>> old_state = test_config.setup()
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> heavy_client.get_context_name("jwst", "jwst-operational")  # doctest: +ELLIPSIS
    'jwst_...pmap'
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

