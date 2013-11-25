from __future__ import division # confidence high

import os
import shutil
import tempfile

import crds

HERE = os.path.dirname(__file__) or "."

class CRDSTestCase(object):
    def setup(self):
        self.data_dir = os.path.join(HERE, 'data')
        self.temp_dir = tempfile.mkdtemp(prefix='crds-test-')
        self.hst_mappath =  os.path.join(crds.__path__[0],'mappings')

    def teardown(self):
        shutil.rmtree(self.temp_dir)

    def data(self, filename):
        return os.path.join(self.data_dir, filename)

    def temp(self, filename):
        return os.path.join(self.temp_dir, filename)

def test(*args,**kwds):
    from stsci.tools import tester
    tester.test(modname=__name__, *args, **kwds)
