import numpy as np
from astropy.io import fits

from crds.misc import synphot
from crds.tests import test_config

from nose.tools import assert_true


class TestSynphotLookupGenerator(test_config.CRDSTestCase):
    def test_throughput_lookup_generation(self):
        generator = synphot.SynphotLookupGenerator("hst_0779.pmap")

        original_hdul = generator.generate("tmctab", [])
        original_tmc = original_hdul[-1].data
        original_row = original_tmc[original_tmc["COMPNAME"] == "wfpc_pol60"][0]
        assert_true(original_row["FILENAME"] == "crwfpccomp$wfpc_pol60_003_syn.fits")

        new_hdul = generator.generate("tmctab", ["data/hst_synphot_new_syn.fits"])
        new_tmc = new_hdul[-1].data
        new_row = new_tmc[new_tmc["COMPNAME"] == "wfpc_pol60"][0]
        assert_true(new_row["FILENAME"] == "crwfpccomp$hst_synphot_new_syn.fits")

    def test_thermal_lookup_generation(self):
        generator = synphot.SynphotLookupGenerator("hst_0779.pmap")

        original_hdul = generator.generate("tmttab", [])
        original_tmt = original_hdul[-1].data
        original_row = original_tmt[original_tmt["COMPNAME"] == "wfc3_ir_f167n"][0]
        assert_true(original_row["FILENAME"] == "crwfc3comp$wfc3_ir_f167n_002_th.fits")

        new_hdul = generator.generate("tmttab", ["data/hst_synphot_new_th.fits"])
        new_tmt = new_hdul[-1].data
        new_row = new_tmt[new_tmt["COMPNAME"] == "wfc3_ir_f167n"][0]
        assert_true(new_row["FILENAME"] == "crwfc3comp$hst_synphot_new_th.fits")
