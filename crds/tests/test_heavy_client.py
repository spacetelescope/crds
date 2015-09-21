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
from crds.tests import CRDSTestCase, test_config

from nose.tools import assert_raises, assert_true

# ==================================================================================

def dt_getreferences_rmap_na():
    """
    >>> old_state = test_config.setup(cache=None, url="https://jwst-crds-dev.stsci.edu")
    >>> os.environ["CRDS_MAPPATH_SINGLE"] = tests.TEST_DATA

    >>> heavy_client.getreferences({"META.INSTRUMENT.NAME":"NIRISS", "META.INSTRUMENT.DETECTOR":"NIS", "META.INSTRUMENT.FILTER":"BOGUS2"},
    ...    observatory="jwst", context="jwst_na_omit.pmap", ignore_cache=False)
    {'flat': 'NOT FOUND n/a'}

    >>> test_config.cleanup(old_state)
    
    >> config.get_crds_state()
    """

def dt_getreferences_rmap_omit():
    """
    >>> old_state = test_config.setup(cache=None, url="https://jwst-crds-dev.stsci.edu")
    >>> os.environ["CRDS_MAPPATH_SINGLE"] = tests.TEST_DATA

    >>> heavy_client.getreferences({"META.INSTRUMENT.NAME":"NIRISS", "META.INSTRUMENT.DETECTOR":"NIS", "META.INSTRUMENT.FILTER":"BOGUS1"},
    ...    observatory="jwst", context="jwst_na_omit.pmap", ignore_cache=False)
    {}

    >>> test_config.cleanup(old_state)
    
    >> config.get_crds_state()
    """

def dt_getreferences_imap_na():
    """
    >>> old_state = test_config.setup(cache=None, url="https://jwst-crds-dev.stsci.edu")
    >>> os.environ["CRDS_MAPPATH_SINGLE"] = tests.TEST_DATA

    >>> heavy_client.getreferences({"META.INSTRUMENT.NAME":"FGS",},
    ...    observatory="jwst", context="jwst_na_omit.pmap", ignore_cache=False)
    {'flat': 'NOT FOUND n/a'}

    >>> test_config.cleanup(old_state)
    """

def dt_getreferences_imap_omit():
    """
    >>> old_state = test_config.setup(cache=None, url="https://jwst-crds-dev.stsci.edu")
    >>> os.environ["CRDS_MAPPATH_SINGLE"] = tests.TEST_DATA

    >>> heavy_client.getreferences({"META.INSTRUMENT.NAME":"MIRI",},
    ...    observatory="jwst", context="jwst_na_omit.pmap", ignore_cache=False)
    {}

    >>> test_config.cleanup(old_state)
    """

# ==================================================================================

# class TestHeavyClient(CRDSTestCase):

    """
    def test_rmap_get_imap_except(self):
        r = rmap.get_cached_mapping("hst.pmap")
        with self.assertRaises(CrdsUnknownInstrumentError):
            r.get_imap("foo")

    def test_rmap_get_filekind(self):
        r = rmap.get_cached_mapping("hst.pmap")
        self.assertEqual(set(r.get_filekinds("data/j8bt05njq_raw.fits")),
                         {'PCTETAB', 'CRREJTAB', 'DARKFILE', 'D2IMFILE', 'BPIXTAB', 'ATODTAB', 'BIASFILE',
                              'SPOTTAB', 'MLINTAB', 'DGEOFILE', 'FLSHFILE', 'NPOLFILE', 'OSCNTAB', 'CCDTAB',
                              'SHADFILE', 'IDCTAB', 'IMPHTTAB', 'PFLTFILE', 'DRKCFILE', 'CFLTFILE', 'MDRIZTAB'})
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

