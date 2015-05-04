"""This module contains doctests and unit tests which exercise some of the more
complex features of the basic rmap infrastructure.

"""

from __future__ import division # confidence high
from __future__ import with_statement
from __future__ import print_function

import os
from pprint import pprint as pp

from crds import refactor, log, exceptions, diff
from crds.refactor import RefactorScript
from crds.tests import CRDSTestCase

from nose.tools import assert_raises, assert_true

# ==================================================================================

def test_refactor_contexts():
    """
    >>> log.set_test_mode()
    >>> import doctest
    >>> doctest.ELLIPSIS_MARKER = '-etc-'

    >>> RefactorScript("refactor.py insert data/hst_cos_deadtab.rmap hst_cos_deadtab_insert.rmap data/s7g1700hl_dead.fits")()  # doctest:+ELLIPSIS
    CRDS  : INFO     Inserting s7g1700hl_dead.fits into 'hst_cos_deadtab.rmap'

    >>> diff.DiffScript("diff.py data/hst_cos_deadtab.rmap ./hst_cos_deadtab_insert.rmap").run()
    (('data/hst_cos_deadtab.rmap', './hst_cos_deadtab_insert.rmap'), ('FUV',), ('1997-10-01', '01:01:01'), 'added terminal s7g1700hl_dead.fits')

    >>> _ = os.system("rm ./hst_cos_deadtab_insert.rmap")
    
    """

def test_rmap_set_header():
    """
    >>> RefactorScript("refactor.py set_header data/hst_cos_deadtab.rmap ./hst_cos_deadtab_header.rmap new_key some new value")()  # doctest:+ELLIPSIS

    >>> diff.DiffScript("diff.py data/hst_cos_deadtab.rmap ./hst_cos_deadtab_header.rmap --include-header-diffs --hide-boring-diffs").run()
    (('data/hst_cos_deadtab.rmap', './hst_cos_deadtab_header.rmap'), "header added 'new_key' = 'some new value'")
    
    >>> _ = os.system("rm ./hst_cos_deadtab_header.rmap")
    """

# ==================================================================================

class TestRefactor(CRDSTestCase):

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

    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRefactor)
    unittest.TextTestRunner().run(suite)
    
    import test_refactor, doctest
    return doctest.testmod(test_refactor)

if __name__ == "__main__":
    print(tst())
