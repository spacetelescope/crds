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

def dt_refactor_add_files():
    """
    >>> log.set_test_mode()

    >>> RefactorScript("refactor.py insert data/hst_cos_deadtab.rmap hst_cos_deadtab_insert.rmap data/s7g1700hl_dead.fits")()  # doctest: +ELLIPSIS
    CRDS  : INFO     Inserting s7g1700hl_dead.fits into 'hst_cos_deadtab.rmap'
    0

    >>> diff.DiffScript("diff.py data/hst_cos_deadtab.rmap ./hst_cos_deadtab_insert.rmap").run()
    (('data/hst_cos_deadtab.rmap', './hst_cos_deadtab_insert.rmap'), ('FUV',), ('1997-10-01', '01:01:01'), 'added terminal s7g1700hl_dead.fits')
    1
    
    >>> pp(refactor.rmap_check_modifications("data/hst_cos_deadtab.rmap", "./hst_cos_deadtab_insert.rmap", "none", "data/s7g1700hl_dead.fits", expected=("add",)))
    True

    >>> refactor.rmap_check_modifications("data/hst_cos_deadtab.rmap", "./hst_cos_deadtab_insert.rmap", "data/s7g1700gl_dead.fits", "data/s7g1700hl_dead.fits",
    ...                          expected=("replace",))
    CRDS  : ERROR    Expected one of ('replace',) but got 'add' from change (('data/hst_cos_deadtab.rmap', './hst_cos_deadtab_insert.rmap'), ('FUV',), ('1997-10-01', '01:01:01'), "added terminal 's7g1700hl_dead.fits'")
    False

    >>> _ = os.system("rm ./*.rmap")
    
    """

def dt_refactor_delete_files():
    """ 
    >>> log.set_test_mode()

    >>> RefactorScript("refactor.py delete data/hst_cos_deadtab.rmap hst_cos_deadtab_delete.rmap data/s7g1700gl_dead.fits")()  # doctest: +ELLIPSIS
    CRDS  : INFO     Deleting 'data/s7g1700gl_dead.fits' from 'hst_cos_deadtab.rmap'
    0

    >>> diff.DiffScript("diff.py data/hst_cos_deadtab.rmap ./hst_cos_deadtab_delete.rmap").run()
    (('data/hst_cos_deadtab.rmap', './hst_cos_deadtab_delete.rmap'), ('FUV',), ('1996-10-01', '00:00:00'), 'deleted Match rule for s7g1700gl_dead.fits')
    1

    >>> refactor.rmap_check_modifications("data/hst_cos_deadtab.rmap", "./hst_cos_deadtab_delete.rmap", "none", "data/s7g1700gl_dead.fits", expected=("delete_rule",))
    True

    >>> RefactorScript("refactor.py delete data/hst_cos_deadtab.rmap hst_cos_deadtab_delete2.rmap data/foobar.fits")()  # doctest: +ELLIPSIS
    CRDS  : INFO     Deleting 'data/foobar.fits' from 'hst_cos_deadtab.rmap'
    CRDS  : ERROR    Refactoring operation FAILED : Terminal 'foobar.fits' could not be found and deleted.
    1

    >>> os.path.exists("./hst_cos_deadtab_delete2.rmap")
    False

    """

def dt_refactor_add_header():
    """
    >>> log.set_test_mode()

    >>> RefactorScript("refactor.py set_header data/hst_cos_deadtab.rmap ./hst_cos_deadtab_add_header.rmap new_key some new value")()  # doctest: +ELLIPSIS
    0

    >>> diff.DiffScript("diff.py data/hst_cos_deadtab.rmap ./hst_cos_deadtab_add_header.rmap --include-header-diffs --hide-boring-diffs").run()
    (('data/hst_cos_deadtab.rmap', './hst_cos_deadtab_add_header.rmap'), "header added 'new_key' = 'some new value'")
    1

    >>> pp(refactor.rmap_check_modifications("data/hst_cos_deadtab.rmap", "./hst_cos_deadtab_add_header.rmap", "none", "none", expected=("add_header",)))
    True

    >>> _ = os.system("rm ./*.rmap")
    """

def dt_refactor_replace_header():
    """
    >>> log.set_test_mode()

    >>> RefactorScript("refactor.py set_header data/hst_cos_deadtab.rmap ./hst_cos_deadtab_replace_header.rmap reffile_format something new")()  # doctest: +ELLIPSIS
    0

    >>> diff.DiffScript("diff.py data/hst_cos_deadtab.rmap ./hst_cos_deadtab_replace_header.rmap --include-header-diffs --hide-boring-diffs").run()
    (('data/hst_cos_deadtab.rmap', './hst_cos_deadtab_replace_header.rmap'), "header replaced 'reffile_format' = 'table' with 'something new'")
    1
    
    >>> pp(refactor.rmap_check_modifications("data/hst_cos_deadtab.rmap", "./hst_cos_deadtab_replace_header.rmap", "none", "none", expected=("replace_header",)))
    True

    >>> _ = os.system("rm ./*.rmap")
    """

def dt_refactor_del_header():
    """
    >>> log.set_test_mode()

    >>> RefactorScript("refactor.py del_header data/hst_cos_deadtab.rmap ./hst_cos_deadtab_del_header.rmap reffile_format")()  # doctest: +ELLIPSIS
    0

    >>> diff.DiffScript("diff.py data/hst_cos_deadtab.rmap ./hst_cos_deadtab_del_header.rmap --include-header-diffs --hide-boring-diffs").run()
    (('data/hst_cos_deadtab.rmap', './hst_cos_deadtab_del_header.rmap'), "deleted header 'reffile_format' = 'table'")
    1

    >>> pp(refactor.rmap_check_modifications("data/hst_cos_deadtab.rmap", "./hst_cos_deadtab_del_header.rmap", "none", "none", expected=("del_header",)))
    True

    >>> _ = os.system("rm ./*.rmap")
    """

def dt_refactor_bad_modify_count():
    """ 
    >>> log.set_test_mode()

    >>> refactor.rmap_check_modifications("data/hst_cos_deadtab.rmap", "data/hst_cos_deadtab_9998.rmap", 
    ...                                   "data/s7g1700gl_dead.fits", "data/s7g1700hl_dead.fits", expected=("add",))
    CRDS  : ERROR    Expected one of ('add',) but got 'replace' from change (('data/hst_cos_deadtab.rmap', 'data/hst_cos_deadtab_9998.rmap'), ('FUV',), ('1996-10-01', '00:00:00'), "replaced 's7g1700gl_dead.fits' with 's7g1700hl_dead.fits'")
    CRDS  : ERROR    Expected one of ('add',) but got 'replace' from change (('data/hst_cos_deadtab.rmap', 'data/hst_cos_deadtab_9998.rmap'), ('NUV',), ('1996-10-01', '00:00:00'), "replaced 's7g1700ql_dead.fits' with 's7g1700hl_dead.fits'")
    False

    >>> refactor.rmap_check_modifications("data/hst_cos_deadtab.rmap", "data/hst_cos_deadtab_9998.rmap", 
    ...                                   "data/s7g1700gl_dead.fits", "data/s7g1700hl_dead.fits", expected=("replace",))
    CRDS  : ERROR    Replacement COUNT DIFFERENCE replacing 'data/s7g1700gl_dead.fits' with 'data/s7g1700hl_dead.fits' in 'data/hst_cos_deadtab.rmap' 1 vs. 2
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
    
    from crds.tests import test_refactor, tstmod
    return tstmod(test_refactor)

if __name__ == "__main__":
    print(tst())
