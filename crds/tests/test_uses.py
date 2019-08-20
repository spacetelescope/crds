"""This module contains doctests and unit tests which exercise the crds.uses
module that identifies mappings that reference a file.

XXX IMPORTANT:  crds.uses tests are extremely time consuming, DISABLED
"""
import os, os.path
from pprint import pprint as pp

from crds.core import log, config
from crds import uses
from crds import tests
from crds.tests import test_config

from nose.tools import assert_raises, assert_true

# ==================================================================================

HERE = os.path.dirname(__file__) or "."

def dt_disabled_uses_finaall_mappings_using_reference():
    """
    >>> old_state = test_config.setup()

    >> uses.UsesScript("crds.uses --files v2e20129l_flat.fits")()
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

    >>> test_config.cleanup(old_state)
    """

def dt_disabled_uses_rmaps():
    """
    >>> old_state = test_config.setup()

    >> uses.UsesScript("crds.uses --files hst_cos_flatfile.rmap hst_acs_darkfile.rmap --include-used")()
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

    >>> test_config.cleanup(old_state)
    """

def dt_disabled_uses_imap():
    """
    >>> old_state = test_config.setup()

    >> uses.UsesScript("crds.uses --files hst_cos.imap")()
    hst.pmap
    hst_0001.pmap
    hst_0002.pmap
    0

    >>> test_config.cleanup(old_state)
    """

class TestUses(test_config.CRDSTestCase):
    '''
    def test_get_imap_except(self):
        r = rmap.get_cached_mapping("hst.pmap")
        with self.assertRaises(exceptions.CrdsUnknownInstrumentError):
            r.get_imap("foo")
    '''

# ==================================================================================


def tst():
    """Run module tests,  for now just doctests only."""

    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUses)
    unittest.TextTestRunner().run(suite)

    from crds.tests import test_uses, tstmod
    return tstmod(test_uses)

if __name__ == "__main__":
    print(tst())
