"""This module contains doctests and unit tests which exercise some of the more
complex features of the basic rmap infrastructure.

"""

from __future__ import division # confidence high
from __future__ import with_statement
from __future__ import print_function

import os, os.path
from pprint import pprint as pp

from crds import log, config, uses
from crds.tests import CRDSTestCase

from nose.tools import assert_raises, assert_true

# ==================================================================================

HERE = os.path.dirname(__file__) or "."

def test_uses_finaall_mappings_using_reference():
    """
    >>> old_state = config.get_crds_state(clear_existing=True)
    >>> os.environ["CRDS_MAPPATH"] = HERE + "/../cache/mappings"
    >>> log.set_test_mode()
    
    >>> uses.UsesScript("crds.uses --files v2e20129l_flat.fits")()
    hst.pmap
    hst_0001.pmap
    hst_0002.pmap
    hst_0003.pmap
    hst_0004.pmap
    hst_0005.pmap
    hst_0006.pmap
    hst_cos.imap
    hst_cos_0001.imap
    hst_cos_flatfile.rmap
    hst_cos_flatfile_0002.rmap
    0
    
    >>> config.set_crds_state(old_state)
    """

def test_uses_rmaps():
    """
    >>> old_state = config.get_crds_state(clear_existing=True)
    >>> os.environ["CRDS_MAPPATH"] = HERE + "/../cache/mappings"
    >>> log.set_test_mode()
    
    >>> uses.UsesScript("crds.uses --files hst_cos_flatfile.rmap hst_acs_darkfile.rmap --include-used")()
    hst_cos_flatfile.rmap hst.pmap
    hst_cos_flatfile.rmap hst_0001.pmap
    hst_cos_flatfile.rmap hst_0002.pmap
    hst_cos_flatfile.rmap hst_cos.imap
    hst_acs_darkfile.rmap hst.pmap
    hst_acs_darkfile.rmap hst_0001.pmap
    hst_acs_darkfile.rmap hst_0002.pmap
    hst_acs_darkfile.rmap hst_0003.pmap
    hst_acs_darkfile.rmap hst_0004.pmap
    hst_acs_darkfile.rmap hst_0005.pmap
    hst_acs_darkfile.rmap hst_0006.pmap
    hst_acs_darkfile.rmap hst_0007.pmap
    hst_acs_darkfile.rmap hst_0008.pmap
    hst_acs_darkfile.rmap hst_0009.pmap
    hst_acs_darkfile.rmap hst_0010.pmap
    hst_acs_darkfile.rmap hst_0011.pmap
    hst_acs_darkfile.rmap hst_0012.pmap
    hst_acs_darkfile.rmap hst_0013.pmap
    hst_acs_darkfile.rmap hst_0014.pmap
    hst_acs_darkfile.rmap hst_acs.imap
    hst_acs_darkfile.rmap hst_acs_0001.imap
    0
    
    >>> config.set_crds_state(old_state)
    """
    
def test_uses_imap():
    """
    >>> old_state = config.get_crds_state(clear_existing=True)
    >>> os.environ["CRDS_MAPPATH"] = HERE + "/../cache/mappings"
    >>> log.set_test_mode()
    
    >>> uses.UsesScript("crds.uses --files hst_cos.imap")()
    hst.pmap
    hst_0001.pmap
    hst_0002.pmap
    0

    >>> config.set_crds_state(old_state)
    """

def test_uses_print_datasets():
    """
    >>> old_state = config.get_crds_state(clear_existing=True)
    >>> os.environ["CRDS_MAPPATH"] = HERE + "/../cache/mappings"
    >>> log.set_test_mode()
   
    This test/function is quite slow since it surveys the catalog for recorded uses of the
    specified file.  Too slow for routine unit tests.
    
    >> uses.UsesScript("crds.uses --files n3o1022ij_drk.fits --print-datasets --hst")()
    J8BA0HRPQ:J8BA0HRPQ
    J8BA0IRTQ:J8BA0IRTQ
    J8BA0JRWQ:J8BA0JRWQ
    J8BA0KT4Q:J8BA0KT4Q
    J8BA0LIJQ:J8BA0LIJQ

    >>> config.set_crds_state(old_state)
    """

class TestUses(CRDSTestCase):
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
    '''

# ==================================================================================


def tst():
    """Run module tests,  for now just doctests only."""
    
    import unittest, doctest
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUses)
    unittest.TextTestRunner().run(suite)

    from crds.tests import test_uses
    return doctest.testmod(test_uses)

if __name__ == "__main__":
    print(tst())
