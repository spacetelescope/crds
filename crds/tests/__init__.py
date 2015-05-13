from __future__ import division # confidence high
from __future__ import print_function
from __future__ import absolute_import

import os, os.path
import shutil
import tempfile
import unittest

import crds
from crds import utils, config
from crds.client import api

HERE = os.path.abspath(os.path.dirname(__file__) or ".")

CRDS_DIR = os.path.abspath(os.path.dirname(crds.__file__))
CRDS_SOURCE_CACHE = os.path.join(CRDS_DIR,'cache')
CRDS_SHARED_GROUP_CACHE = "/grp/crds/cache"
CRDS_FORWARDED_URL = "https://localhost:8001/"
TEST_DATA = os.path.join(HERE, 'data')
TEST_MAPPATH = os.path.join(CRDS_SOURCE_CACHE, "mappings")
TEST_TEMP_DIR = tempfile.mkdtemp(prefix='crds-test-')

class CRDSTestCase(unittest.TestCase):
    
    server_url = None

    def setUp(self, *args, **keys):
        super(CRDSTestCase, self).setUp(*args, **keys)
        self.data_dir = TEST_DATA
        self.temp_dir = TEST_TEMP_DIR
        if not os.path.exists(self.temp_dir):
            os.mkdir(self.temp_dir)
        self.hst_mappath =  TEST_MAPPATH
        utils.clear_function_caches()
        self.crds_state = config.get_crds_state()
        if self.server_url is not None:
            api.set_crds_server(self.server_url)
        self.old_dir = os.getcwd()
        os.chdir(HERE)

    def tearDown(self, *args, **keys):
        super(CRDSTestCase, self).tearDown(*args, **keys)
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        utils.clear_function_caches()
        config.set_crds_state(self.crds_state)
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
