"""This module contains doctests and unit tests which exercise the module that
builds on the crds.client web api and enhances it with fully developed cache
semantics.  crds.client is largely decoupled from the core CRDS modules and
focuses on JSONRPC calls and file downloads.   The heavy_client extends those
primitive functions to provide higher level APIs that are dependent on the
core library to implement.
"""
import os
import json
from pprint import pprint as pp
import doctest


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

def dt_getreferences_ignore_cache():
    """
    >>> old_state = test_config.setup(url="https://jwst-crds.stsci.edu")
    >>> header = { "META.INSTRUMENT.NAME":"MIRI", "META.EXPOSURE.TYPE":"MIR_IMAGE",
    ...            "META.OBSERVATION.DATE":"2018-05-25", "META.OBSERVATION.TIME":"00:00:00" }
    >>> heavy_client.getreferences(header,
    ...   observatory="jwst", context="jwst_miri.imap", ignore_cache=True, reftypes=["flat"])   # doctest: +ELLIPSIS
    CRDS - INFO -  Fetching  .../crds-cache-default-test/mappings/jwst/jwst_miri_photom.rmap      399 bytes  (1 / 3 files) (0 / 1.2 K bytes)
    CRDS - INFO -  Fetching  .../crds-cache-default-test/mappings/jwst/jwst_miri_flat.rmap      427 bytes  (2 / 3 files) (399 / 1.2 K bytes)
    CRDS - INFO -  Fetching  .../crds-cache-default-test/mappings/jwst/jwst_miri.imap      358 bytes  (3 / 3 files) (826 / 1.2 K bytes)
    CRDS - INFO -  Fetching  .../crds-cache-default-test/references/jwst/jwst_miri_flat_0001.fits   42.0 M bytes  (1 / 1 files) (0 / 42.0 M bytes)
    {'flat': '.../crds-cache-default-test/references/jwst/jwst_miri_flat_0001.fits'}
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
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> heavy_client.get_context_name("jwst", "jwst-operational")  # doctest: +ELLIPSIS
    'jwst_...pmap'
    >>> heavy_client.get_context_name("jwst", "jwst-edit")  # doctest: +ELLIPSIS
    'jwst_...pmap'
    >>> heavy_client.get_context_name("jwst", "jwst-versions")  # doctest: +ELLIPSIS
    'jwst_...pmap'
    >>> test_config.cleanup(old_state)
    """

def dt_translate_date_based_context():
    """
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> heavy_client.translate_date_based_context("foo-edit", observatory=None)
    Traceback (most recent call last):
    ...
    crds.core.exceptions.CrdsError: Cannot determine observatory to translate mapping 'foo-edit'
    >>> heavy_client.translate_date_based_context("jwst-2018-01-01T00:00:00")
    Traceback (most recent call last):
    ...
    crds.core.exceptions.CrdsError: Specified CRDS context by date 'jwst-2018-01-01T00:00:00' and CRDS server is not reachable.
    >>> test_config.cleanup(old_state)

    >>> old_state = test_config.setup(url="https://jwst-crds.stsci.edu", observatory="jwst")
    >>> heavy_client.translate_date_based_context("jwst-foo-2018-01-01T00:00:00")
    Traceback (most recent call last):
    ...
    crds.core.exceptions.ServiceError: CRDS jsonrpc failure 'get_context_by_date' InvalidDateBasedContext: Bad instrument 'foo' in CRDS date based context specification.
    >>> test_config.cleanup(old_state)
    """
def dt_get_bad_mappings_in_context_no_instrument():
    """
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> heavy_client.get_bad_mappings_in_context("jwst", "jwst_0016.pmap")
    ['jwst_miri_flat_0002.rmap']
    >>> test_config.cleanup(old_state)
    """

def dt_pickled_mappings(mapping):
    """
    >>> old_state = test_config.setup()

    >>> pickle_file = config.locate_pickle("jwst_0016.pmap","jwst")
    >>> pickle_file   # doctest: +ELLIPSIS
    '.../pickles/jwst/jwst_0016.pmap.pkl'

    >>> _ = heavy_client.get_pickled_mapping("jwst_0016.pmap", cached=True, use_pickles=True, save_pickles=True)  # doctest: +ELLIPSIS
    CRDS - INFO -  Saved pickled context '.../crds-cache-default-test/pickles/jwst/jwst_0016.pmap.pkl'
    >>> assert os.path.exists(pickle_file)

    >>> _ = heavy_client.get_pickled_mapping("jwst_0016.pmap", cached=True, use_pickles=True, save_pickles=False)  # doctest: +ELLIPSIS
     CRDS - INFO -  Loaded pickled context 'jwst_0016.pmap'

    >>> _ = heavy_client.get_pickled_mapping("jwst_0016.pmap", cached=False, use_pickles=False, save_pickles=False)  # doctest: +ELLIPSIS

    >>> _ = heavy_client.get_pickled_mapping("jwst_0016.pmap", cached=False, use_pickles=True, save_pickles=False)  # doctest: +ELLIPSIS
     CRDS - INFO -  Loaded pickled context 'jwst_0016.pmap'

    >>> heavy_client.load_pickled_mapping("jwst_0016.pmap")
    CRDS - INFO -  Loaded pickled context 'jwst_0016.pmap'
    PipelineContext('jwst_0016.pmap')

    >>> _ = log.set_verbose()
    >>> os.chmod(pickle_file, 0o444)
    >>> heavy_client.remove_pickled_mapping("jwst_0016.pmap")  # doctest: +ELLIPSIS
    CRDS - DEBUG -  Pickle file '.../crds-cache-default-test/pickles/jwst/jwst_0016.pmap.pkl' is not writable,  skipping pickle remove.

    >>> os.chmod(pickle_file, 0o666)
    >>> heavy_client.remove_pickled_mapping("jwst_0016.pmap")  # doctest: +ELLIPSIS
    CRDS - INFO -  Removed pickle for context '.../pickles/jwst/jwst_0016.pmap.pkl'
    >>> assert not os.path.exists(pickle_file)

    >>> heavy_client.remove_pickled_mapping("somewhere/foo.pmap")  # doctest: +ELLIPSIS
    CRDS - DEBUG -  Pickle file 'somewhere/foo.pmap' is not writable,  skipping pickle remove.

    >>> test_config.cleanup(old_state)
    """

def dt_check_parameters():
    """
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")

    >>> header = { "NAME" : "VALID_VALUE",  "NAME1" : 1.0, "META.VALID.NAME3" : 1,   "NAME4" : True}
    >>> heavy_client.check_parameters(header)
    {'NAME': 'VALID_VALUE', 'NAME1': 1.0, 'META.VALID.NAME3': 1, 'NAME4': True}

    >>> header = { (1,2,3) : "something for invalid key" }
    >>> heavy_client.check_parameters(header)
    Traceback (most recent call last):
    ...
    AssertionError: Non-string key (1, 2, 3) in parameters.

    >>> header = { "META.BAD.VALUE" : object() }
    >>> heavy_client.check_parameters(header)
    {}

    >>> test_config.cleanup(old_state)
    """

def dt_check_context():
    """
    >>> heavy_client.check_context(None)
    """

def dt_get_context_parkeys():
    """
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> heavy_client.get_context_parkeys("jwst.pmap","miri")
    ['META.INSTRUMENT.TYPE', 'META.INSTRUMENT.LAMP_STATE', 'META.OBSERVATION.DATE', 'META.VISIT.TSOVISIT', 'REFTYPE']
    >>> heavy_client.get_context_parkeys("jwst_miri.imap","miri")
    ['META.INSTRUMENT.LAMP_STATE', 'META.OBSERVATION.DATE', 'META.VISIT.TSOVISIT', 'REFTYPE']
    >>> heavy_client.get_context_parkeys("jwst_miri_flat.rmap","miri")
    ['META.OBSERVATION.DATE', 'META.VISIT.TSOVISIT', 'META.INSTRUMENT.LAMP_STATE']
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
