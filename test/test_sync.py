import os
import crds
from conftest import CRDSTestCase
from crds.core import config, rmap
from crds.sync import SyncScript
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
        # no differences.
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
            "crds.sync --contexts hst_cos_deadtab.rmap --fetch-references --organize=instrument --organize-delete-junk",
            4)
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
        list_to_check = ['3241637sm_tmt.fits', '41g16069m_tmg.fits', '43h1240om_tmc.fits', '43h1909cm_tmc.fits',
                         'l2d0959cj_pfl.fits', 'n7p1032ao_apt.fits', 'n9n20182l_flat.fits', 'p7d1548qj_idc.fits',
                         'q5417413o_pct.fits', 'r7p1113nl_geo.fits', 's7g17006l_1dx.fits', 's7g17007l_1dx.fits',
                         's7g1700dl_bpix.fits', 's7g1700fl_burst.fits', 's7g1700gl_dead.fits', 's7g1700il_lamp.fits',
                         's7g1700jl_pha.fits', 's7g1700kl_phot.fits', 's7g1700nl_1dx.fits', 's7g1700ol_1dx.fits',
                         's7g1700pl_bpix.fits', 's7g1700ql_dead.fits', 's7g1700tl_flat.fits', 's7g17010l_lamp.fits',
                         's7g17011l_phot.fits', 's7g17013l_disp.fits', 's7o1739kl_badt.fits', 't2314311l_wcp.fits',
                         't2314312l_tds.fits', 't2314314l_tds.fits', 't2k1224el_disp.fits', 't9b18112l_wcp.fits',
                         't9e1307kl_disp.fits', 't9e1307ll_disp.fits', 't9h1220sl_phot.fits', 'u1t1616ol_lamp.fits',
                         'u1t1616pl_disp.fits', 'u1t1616ql_wcp.fits', 'u6s1320ql_disp.fits', 'u6s1320rl_lamp.fits',
                         'u7d20378l_tds.fits', 'u8k1433ql_phot.fits', 'uai1737ol_spwcs.fits', 'uai1737pl_spwcs.fits',
                         'uai1737ql_spwcs.fits', 'uai1737rl_spwcs.fits', 'uai17385l_spwcs.fits', 'uai17386l_spwcs.fits',
                         'uai17387l_spwcs.fits', 'uas19356l_bpix.fits', 'v2e20129l_flat.fits', 'v3g18194l_disp.fits',
                         'v3g18195l_lamp.fits', 'v3n1816ml_flat.fits', 'v4s17227l_flat.fits', 'w161831hl_walk.fits',
                         'w5g1439sl_1dx.fits', 'w7h1935dl_tds.fits', 'wc318317l_pha.fits', 'x1u1459gl_geo.fits',
                         'x1u1459hl_bpix.fits', 'x1u1459il_brf.fits', 'x1v17413l_lamp.fits', 'x1v17414l_1dx.fits',
                         'x1v17415l_disp.fits', 'x1v17416l_phot.fits', 'x1v17417l_spwcs.fits', 'x2i1559gl_wcp.fits',
                         'x6l1439el_gsag.fits', 'x6l16507l_hv.fits', 'x6q17583l_spwcs.fits', 'x6q17584l_disp.fits',
                         'x6q17585l_lamp.fits', 'x6q17586l_1dx.fits', 'x6q17587l_phot.fits', 'xaf1429el_wcp.fits',
                         'y2r1559to_apt.fits', 'y2r16006o_pct.fits', 'y951738kl_hv.fits', 'yas2005el_hv.fits', ]
        assert rmap.list_references("*", "hst") == list_to_check
        self.assert_crds_exists("s7g1700gl_dead.fits")
        self.assert_crds_exists("s7g1700ql_dead.fits")
        self.run_script(
            "crds.sync --contexts hst_acs_imphttab.rmap --fetch-references --purge-mappings --purge-references")
        assert rmap.list_references("*", "hst") == ['w3m1716tj_imp.fits', 'w3m17170j_imp.fits',
                                                    'w3m17171j_imp.fits']
        assert rmap.list_mappings("*", "hst") == ['hst_acs_imphttab.rmap']
        hst_shared_cache_state.cleanup()
