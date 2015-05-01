"""This module contains doctests and unit tests which exercise some of the more
complex features of the basic rmap infrastructure.

"""

from __future__ import division # confidence high
from __future__ import with_statement
from __future__ import print_function

import os, os.path
from pprint import pprint as pp

from crds import rmap, log, exceptions, newcontext, diff, pysh
from crds.tests import CRDSTestCase

from nose.tools import assert_raises, assert_true

# ==================================================================================

def test_new_context():
    """
    >>> log.set_test_mode()

    >>> newcontext.NewContextScript("newcontext.py hst.pmap data/hst_cos_deadtab_9999.rmap data/hst_acs_imphttab_9999.rmap")()
    CRDS  : INFO     Replaced 'hst_cos_deadtab.rmap' with 'data/hst_cos_deadtab_9999.rmap' for 'deadtab' in './hst_cos_0001.imap'
    CRDS  : INFO     Replaced 'hst_acs_imphttab.rmap' with 'data/hst_acs_imphttab_9999.rmap' for 'imphttab' in './hst_acs_0001.imap'
    CRDS  : INFO     Replaced 'hst_cos.imap' with './hst_cos_0001.imap' for 'COS' in './hst_0001.pmap'
    CRDS  : INFO     Replaced 'hst_acs.imap' with './hst_acs_0001.imap' for 'ACS' in './hst_0001.pmap'
    CRDS  : INFO     Adjusting name 'hst_cos_0001.imap' derived_from 'hst_cos.imap' in './hst_cos_0001.imap'
    CRDS  : INFO     Adjusting name 'hst_acs_0001.imap' derived_from 'hst_acs.imap' in './hst_acs_0001.imap'
    CRDS  : INFO     Adjusting name 'hst_0001.pmap' derived_from 'hst.pmap' in './hst_0001.pmap'

    >>> pp([difference[-1] for difference in diff.mapping_diffs("hst.pmap", "./hst_0001.pmap")])
    ["replaced 'hst_acs.imap' with './hst_acs_0001.imap'",
     "replaced 'hst_cos.imap' with './hst_cos_0001.imap'",
     "replaced 'w3m17170j_imp.fits' with 'xb61855jj_imp.fits'",
     "replaced 'hst_acs_imphttab.rmap' with 'data/hst_acs_imphttab_9999.rmap'",
     "replaced 'hst_cos_deadtab.rmap' with 'data/hst_cos_deadtab_9999.rmap'",
     "replaced 's7g1700gl_dead.fits' with 's7g1700gm_dead.fits'"]
    
    >>> _ = pysh.sh("rm *.imap *.pmap")
    """

class TestNewContext(CRDSTestCase):

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
    import test_newcontext, doctest
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNewContext)
    unittest.TextTestRunner().run(suite)
    return doctest.testmod(test_newcontext)

if __name__ == "__main__":
    print(tst())
