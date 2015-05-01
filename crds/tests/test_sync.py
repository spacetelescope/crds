"""This module contains doctests and unit tests which exercise some of the more
complex features of the basic rmap infrastructure.

"""

from __future__ import division # confidence high
from __future__ import with_statement
from __future__ import print_function

import os
from pprint import pprint as pp

from crds import sync, log, exceptions
from crds.sync import SyncScript
from crds.tests import CRDSTestCase

from nose.tools import assert_raises, assert_true

# ==================================================================================

def test_sync_contexts():
    """
    >>> log.set_test_mode()
    >>> import doctest
    >>> doctest.ELLIPSIS_MARKER = '-etc-'

    >>> SyncScript("sync.py --contexts hst_cos.imap")()  # doctest:+ELLIPSIS
    CRDS  : INFO     0 errors
    CRDS  : INFO     0 warnings
    CRDS  : INFO     0 infos

    >>> SyncScript("sync.py --contexts hst_cos_deadtab.rmap --fetch-references")() # doctest:+ELLIPSIS
    -etc-
    CRDS  : INFO     0 errors
    CRDS  : INFO     0 warnings
    CRDS  : INFO     2 infos
    
    """

# ==================================================================================

class TestSync(CRDSTestCase):

    '''
    def test_get_imap_except(self):
        r = rmap.get_cached_mapping("hst.pmap")
        with self.assertRaises(exceptions.CrdsUnknownInstrumentError):
            r.get_imap("foo")

    def test_get_filekind(self):
        r = rmap.get_cached_mapping("hst.pmap")
        self.assertEqual(r.get_filekinds("data/j8bt05njq_raw.fits"),
                         [ 'PCTETAB', 'CRREJTAB', 'DARKFILE', 'D2IMFILE', 'BPIXTAB', 'ATODTAB', 'BIASFILE',
                           'SPOTTAB', 'MLINTAB', 'DGEOFILE', 'FLSHFILE', 'NPOLFILE', 'OSCNTAB', 'CCDTAB',
                           'SHADFILE', 'IDCTAB', 'IMPHTTAB', 'PFLTFILE', 'DRKCFILE', 'CFLTFILE', 'MDRIZTAB'])

    def test_get_equivalent_mapping(self):
        i = rmap.get_cached_mapping("data/hst_acs_0002.imap")
        self.assertEqual(i.get_equivalent_mapping("hst.pmap"), None)
        self.assertEqual(i.get_equivalent_mapping("data/hst_acs_0001.imap").name, "hst_acs.imap")
        self.assertEqual(i.get_equivalent_mapping("data/hst_acs_biasfile_0002.rmap").name, "hst_acs_biasfile.rmap")


    def test_list_references(self):
        self.assertEqual(rmap.list_references("*.r1h", "hst"), [])
    '''

# ==================================================================================


def tst():
    """Run module tests,  for now just doctests only."""
    import test_sync, doctest
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSync)
    unittest.TextTestRunner().run(suite)
    return doctest.testmod(test_sync)

if __name__ == "__main__":
    print(tst())
