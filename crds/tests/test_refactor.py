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
    0

    >>> diff.DiffScript("diff.py data/hst_cos_deadtab.rmap ./hst_cos_deadtab_insert.rmap").run()
    (('data/hst_cos_deadtab.rmap', './hst_cos_deadtab_insert.rmap'), ('FUV',), ('1997-10-01', '01:01:01'), 'added terminal s7g1700hl_dead.fits')

    >>> pp(refactor.rmap_check_modifications("data/hst_cos_deadtab.rmap", "./hst_cos_deadtab_insert.rmap", "none", "data/s7g1700hl_dead.fits", expected=("add",)))
    True

    >>> refactor.rmap_check_modifications("data/hst_cos_deadtab.rmap", "./hst_cos_deadtab_insert.rmap", "none", "data/s7g1700hl_dead.fits",
    ...                          expected=("replace",))
    CRDS  : ERROR    Expected one of ('replace',) but got 'add' from change (('data/hst_cos_deadtab.rmap', './hst_cos_deadtab_insert.rmap'), ('FUV',), ('1997-10-01', '01:01:01'), "added terminal 's7g1700hl_dead.fits'")
    False

    >>> _ = os.system("rm ./*.rmap")
    
    """

def test_refactor_set_header():
    """
    >>> RefactorScript("refactor.py set_header data/hst_cos_deadtab.rmap ./hst_cos_deadtab_header.rmap new_key some new value")()  # doctest:+ELLIPSIS
    0

    >>> diff.DiffScript("diff.py data/hst_cos_deadtab.rmap ./hst_cos_deadtab_header.rmap --include-header-diffs --hide-boring-diffs").run()
    (('data/hst_cos_deadtab.rmap', './hst_cos_deadtab_header.rmap'), "header added 'new_key' = 'some new value'")
    
    >>> pp(refactor.rmap_check_modifications("data/hst_cos_deadtab.rmap", "./hst_cos_deadtab_header.rmap", "none", "none", expected=("add_header",)))
    True

    >>> _ = os.system("rm ./*.rmap")
    """

def test_refactor_delete_files():
    """
    >>> RefactorScript("refactor.py delete data/hst_cos_deadtab.rmap hst_cos_deadtab_delete.rmap data/s7g1700gl_dead.fits")()  # doctest:+ELLIPSIS
    CRDS  : INFO     Deleting 'data/s7g1700gl_dead.fits' from 'hst_cos_deadtab.rmap'
    0

    >>> diff.DiffScript("diff.py data/hst_cos_deadtab.rmap ./hst_cos_deadtab_delete.rmap").run()
    (('data/hst_cos_deadtab.rmap', './hst_cos_deadtab_delete.rmap'), ('FUV',), ('1996-10-01', '00:00:00'), 'deleted terminal s7g1700gl_dead.fits')

    >>> refactor.rmap_check_modifications("data/hst_cos_deadtab.rmap", "./hst_cos_deadtab_delete.rmap", "none", "data/s7g1700gl_dead.fits", expected=("delete",))
    True

    >>> RefactorScript("refactor.py delete data/hst_cos_deadtab.rmap hst_cos_deadtab_delete2.rmap data/foobar.fits")()  # doctest:+ELLIPSIS
    CRDS  : INFO     Deleting 'data/foobar.fits' from 'hst_cos_deadtab.rmap'
    CRDS  : ERROR    Refactoring operation FAILED : Terminal 'foobar.fits' could not be found and deleted.
    1

    >>> os.path.exists("./hst_cos_deadtab_delete2.rmap")
    False

    """

# ==================================================================================

class TestRefactor(CRDSTestCase):

    '''
    example unit test code,  not for test_refactor

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
