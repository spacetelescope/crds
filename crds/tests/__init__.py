from __future__ import division # confidence high

import os
import shutil
import tempfile
import unittest

import crds
from crds import utils, config
from crds.client import api

HERE = os.path.dirname(__file__) or "."

class CRDSTestCase(unittest.TestCase):
    
    server_url = None

    def setUp(self, *args, **keys):
        super(CRDSTestCase, self).setUp(*args, **keys)
        self.data_dir = os.path.join(HERE, 'data')
        self.temp_dir = tempfile.mkdtemp(prefix='crds-test-')
        self.hst_mappath =  os.path.join(crds.__path__[0],'cache','mappings')
        utils.clear_function_caches()
        self.crds_state = config.get_crds_state()
        if self.server_url is not None:
            api.set_crds_server(self.server_url)

    def tearDown(self, *args, **keys):
        super(CRDSTestCase, self).tearDown(*args, **keys)
        shutil.rmtree(self.temp_dir)
        utils.clear_function_caches()
        config.set_crds_state(self.crds_state)

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

