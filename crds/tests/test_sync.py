"""This module contains doctests and unit tests which exercise some of the more
complex features of the basic rmap infrastructure.

"""

from __future__ import division # confidence high
from __future__ import with_statement
from __future__ import print_function

import os
from pprint import pprint as pp

import crds
from crds import sync, log, exceptions, config
from crds.sync import SyncScript
from crds.tests import CRDSTestCase

from nose.tools import assert_raises, assert_true

# ==================================================================================

class TestSync(CRDSTestCase):

    def setUp(self):
        super(TestSync, self).setUp()
        config.clear_crds_state()
        os.environ["CRDS_PATH"] = self.temp_dir
        os.environ["CRDS_REF_SUBDIR_MODE"] = "flat"
        log.set_test_mode()

    def test_sync_contexts(self):
        SyncScript("sync.py --contexts hst_cos.imap")()
        i = crds.get_cached_mapping("hst_cos.imap")
        for name in i.mapping_names():
            assert os.path.exists(config.locate_mapping(name))

        SyncScript("sync.py --contexts hst_cos_deadtab.rmap --fetch-references")()
        r = crds.get_cached_mapping("hst_cos_deadtab.rmap")
        for name in r.reference_names():
            fname = config.locate_file(name, "hst")
            assert os.path.exists(fname)
            with open(fname, "w+") as handle:
                handle.write("foo")

        errs = SyncScript("sync.py --contexts hst_cos_deadtab.rmap --fetch-references --check-files")()
        self.assertEqual(errs, 2)

        errs = SyncScript("sync.py --contexts hst_cos_deadtab.rmap --fetch-references --check-files --repair-files")()
        self.assertEqual(errs, 2)

        errs = SyncScript("sync.py --contexts hst_cos_deadtab.rmap --fetch-references --check-files --repair-files")()
        self.assertEqual(errs, 0)

        errs = SyncScript("sync.py --contexts hst_cos_deadtab.rmap --fetch-references --check-files --repair-files --check-sha1sum")()
        self.assertEqual(errs, 0)
    
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
