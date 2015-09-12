from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

# ==============================================================================

import os, os.path
import shutil
import tempfile
import unittest

# ==============================================================================

import crds
from crds import log, utils, client, config

# ==============================================================================

HERE = os.path.abspath(os.path.dirname(__file__) or ".")

CRDS_DIR = os.path.abspath(os.path.dirname(crds.__file__))
CRDS_CACHE_TEST = os.environ.get("CRDS_CACHE_TEST", "no-test-cache-defined-see-TESTING")
CRDS_SHARED_GROUP_CACHE = "/grp/crds/cache"
CRDS_FORWARDED_URL = "https://localhost:8001/"
TEST_DATA = os.path.join(HERE, 'data')
TEST_MAPPATH = os.path.join(CRDS_CACHE_TEST, "mappings")
TEST_TEMP_DIR = tempfile.mkdtemp(prefix='crds-test-')

# ==============================================================================

class CRDSTestCase(unittest.TestCase):
    
    clear_existing = False
    server_url = None
    cache = CRDS_SHARED_GROUP_CACHE

    def setUp(self, *args, **keys):
        super(CRDSTestCase, self).setUp(*args, **keys)
        self.data_dir = TEST_DATA
        self.temp_dir = TEST_TEMP_DIR
        if not os.path.exists(self.temp_dir):
            os.mkdir(self.temp_dir)
        self.hst_mappath =  TEST_MAPPATH
        self.old_state = setup(cache=self.cache, url=self.server_url, 
                               clear_existing=self.clear_existing)
        self.old_dir = os.getcwd()
        os.chdir(HERE)

    def tearDown(self, *args, **keys):
        super(CRDSTestCase, self).tearDown(*args, **keys)
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        cleanup(self.old_state)
        os.chdir(self.old_dir)

    def run_script(self, cmd, expected_errs=0):
        """Run SyncScript using command line `cmd` and check for `expected_errs` as return status."""
        errs = self.script_class(cmd)()
        if expected_errs is not None:
            self.assertEqual(errs, expected_errs)

    def assert_crds_exists(self, filename, observatory="hst"):
        self.assertTrue(os.path.exists(config.locate_file(filename, observatory)))

    def assert_crds_not_exists(self, filename, observatory="hst"):
        self.assertFalse(os.path.exists(config.locate_file(filename, observatory)))

    def data(self, filename):
        return os.path.join(self.data_dir, filename)

    def temp(self, filename):
        return os.path.join(self.temp_dir, filename)

# ==============================================================================

def setup(cache=CRDS_SHARED_GROUP_CACHE, url=None, clear_existing=True):
    """Reset the CRDS configuration state to support testing given the supplied parameters."""
    log.set_test_mode()
    old_state = config.get_crds_state()
    if clear_existing:
        config.clear_crds_state()
    if url is not None:
        os.environ["CRDS_SERVER_URL"] = url
        client.set_crds_server(url)
    old_state["OLD_CWD"] = os.getcwd()
    os.chdir(HERE)
    if cache is not None:
        os.environ["CRDS_PATH"] = cache
    utils.clear_function_caches()
    return old_state

def cleanup(old_state):
    """Strictly speaking test cleanup is more than restoring CRDS state."""
    os.chdir(old_state.pop("OLD_CWD"))
    config.set_crds_state(old_state)
    utils.clear_function_caches()

# ==============================================================================

def tstmod(module):
    """Wrap tests.tstmod to configure standard options throughout CRDS tests."""
    import doctest
    # doctest.ELLIPSIS_MARKER = '-etc-'
    return doctest.testmod(module, optionflags=doctest.ELLIPSIS)

