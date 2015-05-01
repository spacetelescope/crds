from __future__ import division # confidence high

import os
import shutil
import tempfile
import unittest

import crds
from crds import utils, config

HERE = os.path.dirname(__file__) or "."

class CRDSTestCase(unittest.TestCase):
    def setUp(self, *args, **keys):
        super(CRDSTestCase, self).setUp(*args, **keys)
        self.data_dir = os.path.join(HERE, 'data')
        self.temp_dir = tempfile.mkdtemp(prefix='crds-test-')
        self.hst_mappath =  os.path.join(crds.__path__[0],'cache','mappings')
        utils.clear_function_caches()
        self.crds_state = config.get_crds_state()

    def tearDown(self, *args, **keys):
        super(CRDSTestCase, self).tearDown(*args, **keys)
        shutil.rmtree(self.temp_dir)
        utils.clear_function_caches()
        config.set_crds_state(self.crds_state)

    def data(self, filename):
        return os.path.join(self.data_dir, filename)

    def temp(self, filename):
        return os.path.join(self.temp_dir, filename)

