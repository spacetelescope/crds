import os

import crds
from conftest import CRDSTestCase
from crds.core import config, rmap
from crds.sync import SyncScript
from crds.core import log

from pytest import mark

@mark.sync
class TestSync(CRDSTestCase):

    script_class = SyncScript

    def test_sync_contexts(self, hst_shared_cache_state):
        cache = hst_shared_cache_state.cache
        self.run_script("crds.sync --contexts hst_cos.imap")
        list_to_check = ['hst_cos.imap',
                         'hst_cos_badttab.rmap',
                         'hst_cos_bpixtab.rmap',
                         'hst_cos_brftab.rmap',
                         'hst_cos_brsttab.rmap',
                         'hst_cos_deadtab.rmap',
                         'hst_cos_disptab.rmap',
                         'hst_cos_flatfile.rmap',
                         'hst_cos_fluxtab.rmap',
                         'hst_cos_geofile.rmap',
                         'hst_cos_gsagtab.rmap',
                         'hst_cos_hvtab.rmap',
                         'hst_cos_lamptab.rmap',
                         'hst_cos_phatab.rmap',
                         'hst_cos_spwcstab.rmap',
                         'hst_cos_tdstab.rmap',
                         'hst_cos_walktab.rmap',
                         'hst_cos_wcptab.rmap',
                         'hst_cos_xtractab.rmap']

        for name in crds.get_cached_mapping("hst_cos.imap").mapping_names():
            assert name in list_to_check
        self.run_script("crds.sync --contexts hst_cos_deadtab.rmap --fetch-references")
        list_to_check = ['s7g1700gl_dead.fits', 's7g1700ql_dead.fits']
        for name in crds.get_cached_mapping("hst_cos_deadtab.rmap").reference_names():
            assert name in list_to_check
            with open(config.locate_file(name, "hst"), "w+") as handle:
                handle.write("foo")
        self.run_script("crds.sync --contexts hst_cos_deadtab.rmap --fetch-references --check-files",
                        2)
        self.run_script("crds.sync --contexts hst_cos_deadtab.rmap --fetch-references --check-files --repair-files",
                        2)
        self.run_script("crds.sync --contexts hst_cos_deadtab.rmap --fetch-references --check-files --repair-files")
        self.run_script(
            "crds.sync --contexts hst_cos_deadtab.rmap --fetch-references --check-files --repair-files --check-sha1sum")
        hst_shared_cache_state.cleanup()

    def test_sync_explicit_files(self, hst_shared_cache_state):
        print(os.path.exists(config.locate_file('hst_cos_deadtab.rmap', 'hst')))
        # Not really sure how either of these lines are supposed to interact, as including neither, one nor both makes
        # no difference.
        # self.assert_crds_not_exists("hst_cos_deadtab.rmap")
        # self.assert_crds_exists("hst_cos_deadtab.rmap")
        self.run_script("crds.sync --files hst_cos_deadtab.rmap --check-files --repair-files --check-sha1sum")
        crds.get_cached_mapping("hst_cos_deadtab.rmap")
        hst_shared_cache_state.cleanup()

    def test_sync_readonly_cache(self, hst_shared_cache_state):
        self.run_script("crds.sync --contexts hst_cos_deadtab.rmap")
        self.run_script("crds.sync --contexts hst_cos_deadtab.rmap --fetch-references --readonly-cache")
        hst_shared_cache_state.cleanup()

    def test_sync_organize_flat(self, hst_shared_cache_state):
        self.assert_crds_not_exists("hst_cos_deadtab.rmap")
        self.assert_crds_not_exists("s7g1700gl_dead.fits")
        self.assert_crds_not_exists("s7g1700ql_dead.fits")
        self.run_script("crds.sync --contexts hst_cos_deadtab.rmap --fetch-references --organize=flat")
        self.assert_crds_exists("hst_cos_deadtab.rmap")
        self.assert_crds_exists("s7g1700gl_dead.fits")
        self.assert_crds_exists("s7g1700ql_dead.fits")
        hst_shared_cache_state.cleanup()

    def test_sync_organize_instr(self, hst_shared_cache_state):
        self.run_script(
            "crds.sync --contexts hst_cos_deadtab.rmap --fetch-references --organize=instrument --organize-delete-junk")
        self.assert_crds_exists("hst_cos_deadtab.rmap")
        self.assert_crds_exists("s7g1700gl_dead.fits")
        self.assert_crds_exists("s7g1700ql_dead.fits")
        self.run_script(
            "crds.sync --contexts hst_cos_deadtab.rmap --fetch-references --organize=flat --organize-delete-junk")
        hst_shared_cache_state.cleanup()

    def test_sync_fetch_sqlite3_db(self, hst_shared_cache_state):
        self.run_script("crds.sync --fetch-sqlite-db")
        hst_shared_cache_state.cleanup()

    def test_sync_dataset_ids(self, hst_shared_cache_state):
        self.run_script("crds.sync --contexts hst.pmap --dataset-ids LA9K03CBQ:LA9K03CBQ --fetch-references")
        hst_shared_cache_state.cleanup()

    @mark.vv
    def test_purge_mappings(self, hst_shared_cache_state):
        self.run_script("crds.sync --contexts hst_cos_deadtab.rmap --fetch-references")
        self.run_script("crds.sync --organize=flat")
        r = crds.get_cached_mapping("hst_cos_deadtab.rmap")
        assert r.reference_names() == ["s7g1700gl_dead.fits", "s7g1700ql_dead.fits"]
        assert rmap.list_references("*", "hst") == ['s7g1700gl_dead.fits', 's7g1700ql_dead.fits',
                                                    'u1t1616ol_lamp.fits', 'u1t1616pl_disp.fits', 'uas19356l_bpix.fits',
                                                    'v2e20129l_flat.fits', 'w3m1716tj_imp.fits', 'w3m17170j_imp.fits',
                                                    'w3m17171j_imp.fits', 'w5g1439sl_1dx.fits', 'x2i1559gl_wcp.fits']
        self.assert_crds_exists("s7g1700gl_dead.fits")
        self.assert_crds_exists("s7g1700ql_dead.fits")
        self.run_script(
            "crds.sync --contexts hst_acs_imphttab.rmap --fetch-references --purge-mappings --purge-references")
        assert rmap.list_references("*", "hst") == ['w3m1716tj_imp.fits', 'w3m17170j_imp.fits',
                                                                          'w3m17171j_imp.fits']
        assert rmap.list_mappings("*", "hst") == ['hst_acs_imphttab.rmap']
        hst_shared_cache_state.cleanup()
