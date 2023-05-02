import os, os.path
import shutil
import tempfile
import unittest
import cProfile
import pstats

# ==============================================================================

import crds
from crds.core import log, utils, config

# ==============================================================================

HERE = os.path.abspath(os.path.dirname(__file__) or ".")

CRDS_DIR = os.path.abspath(os.path.dirname(crds.__file__))
CRDS_TESTING_CACHE = os.environ.get("CRDS_TESTING_CACHE", "no-test-cache-defined-see-TESTING")
# CRDS_SHARED_GROUP_CACHE = "/grp/crds/cache"
CRDS_SHARED_GROUP_CACHE=config.get_crds_path()
CRDS_FORWARDED_URL = "https://localhost:8001/"
TEST_DATA = os.path.join(HERE, 'data')
TEST_MAPPATH = os.path.join(CRDS_TESTING_CACHE, "mappings")
TEST_TEMP_DIR = tempfile.mkdtemp(prefix='crds-test-')

# ==============================================================================

class CRDSTestCase(unittest.TestCase):

    clear_existing = False
    server_url = None
    cache = config.get_crds_path()

    def setUp(self, *args, **keys):
        super(CRDSTestCase, self).setUp(*args, **keys)
        self.data_dir = TEST_DATA
        self.temp_dir = TEST_TEMP_DIR
        if not os.path.exists(self.temp_dir):
            os.mkdir(self.temp_dir)
        self.hst_mappath =  TEST_MAPPATH
        self.old_state = setup(cache=self.cache, url=self.server_url,
                               clear_existing=self.clear_existing)
    def tearDown(self, *args, **keys):
        super(CRDSTestCase, self).tearDown(*args, **keys)
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        cleanup(self.old_state)

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

def setup(cache=CRDS_SHARED_GROUP_CACHE, url=None, clear_existing=True, observatory=None):
    """Reset the CRDS configuration state to support testing given the supplied parameters."""
    log.set_test_mode()
    old_state = config.get_crds_state()
    old_state["CRDS_CWD"] = os.getcwd()
    if clear_existing:
        config.clear_crds_state()
    new_state = dict(old_state)
    new_state["CRDS_CWD"] = HERE
    if url is not None:
        new_state["CRDS_SERVER_URL"] = url
    if cache is not None:
        new_state["CRDS_PATH"] = cache
    if observatory is not None:
        new_state["CRDS_OBSERVATORY"] = observatory
    config.set_crds_state(new_state)
    utils.clear_function_caches()
    return old_state

def cleanup(old_state):
    """Strictly speaking test cleanup is more than restoring CRDS state."""
    config.set_crds_state(old_state)
    utils.clear_function_caches()

# ==============================================================================

def run_and_profile(name, case, globs={}, locs={}):
    """Using `name` for a banner and divider,  execute code string `case` in the
    global namespace,  both evaled printing result and under the profiler.
    """
    utils.clear_function_caches()
    log.divider()
    log.divider(name + " example")
    log.divider()
    print(eval(case, globs, locs))
    utils.clear_function_caches()
    log.divider()
    log.divider(name + " profile")
    log.divider()
    cProfile.run(case, "profile.stats")
    stats = pstats.Stats('profile.stats')
    stats.strip_dirs()
    stats.sort_stats('cumulative')
    stats.print_stats(100)
    os.remove('profile.stats')
