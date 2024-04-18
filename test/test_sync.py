from pytest import mark, fixture
import os
import crds
from crds.core import config, rmap
from crds.sync import SyncScript


EXPECTED_MAPPINGS = [
    'hst_cos.imap',
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
    'hst_cos_xtractab.rmap'
]


@mark.hst
@mark.sync
class TestSync:

    script_class = SyncScript
    obs = "hst"
    _rmap = "hst_cos_deadtab.rmap"
    ref1 = "s7g1700gl_dead.fits"
    ref2 = "s7g1700ql_dead.fits"
    sync_rmap = f"crds.sync --contexts {_rmap}"

    @fixture(autouse=True)
    def _get_config(self, hst_temp_cache_state):
        self._config = hst_temp_cache_state
        os.environ["CRDS_REF_SUBDIR_MODE"] = "flat"

    def run_script(self, cmd, expected_errs=0):
        """Run SyncScript using command line `cmd` and check for `expected_errs` as return status."""
        errs = self.script_class(cmd)()
        if expected_errs is not None:
            assert errs == expected_errs
    
    def crds_exists(self, filename):
        return os.path.exists(config.locate_file(filename, self.obs))

    def clear_tmp_cache(self, filename):
        if self.crds_exists(filename):
            fpath = config.locate_file(filename, self.obs)
            os.remove(fpath)

    def test_sync_contexts(self):
        self.run_script("crds.sync --contexts hst_cos.imap")
        mapping_names = crds.get_cached_mapping("hst_cos.imap").mapping_names()
        for name in mapping_names:
            assert name in EXPECTED_MAPPINGS
            assert self.crds_exists(name)
        self.run_script(f"{self.sync_rmap} --fetch-references")
        reference_names = crds.get_cached_mapping(self._rmap).reference_names()
        for name in reference_names:
            assert self.crds_exists(name)
            assert name in [self.ref1, self.ref2]
            with open(config.locate_file(name, "hst"), "w+") as handle:
                handle.write("foo")
        self.run_script(f"{self.sync_rmap} --fetch-references --check-files", expected_errs=2)
        self.run_script(f"{self.sync_rmap} --fetch-references --check-files --repair-files", expected_errs=2)
        self.run_script(f"{self.sync_rmap} --fetch-references --check-files --repair-files")
        self.run_script(f"{self.sync_rmap} --fetch-references --check-files --repair-files --check-sha1sum")

    def test_sync_explicit_files(self):
        self.clear_tmp_cache(self._rmap)
        assert self.crds_exists(self._rmap) is False
        self.run_script(f"crds.sync --files {self._rmap} --check-files --repair-files --check-sha1sum")
        crds.get_cached_mapping(self._rmap)

    def test_sync_readonly_cache(self):
        self.run_script(self.sync_rmap)
        self.run_script(f"{self.sync_rmap} --fetch-references --readonly-cache")

    def test_sync_organize_flat(self):
        for fname in [self._rmap, self.ref1, self.ref2]:
            self.clear_tmp_cache(fname)
        assert self.crds_exists(self._rmap) is False
        assert self.crds_exists(self.ref1) is False
        assert self.crds_exists(self.ref2) is False
        self.run_script(f"{self.sync_rmap} --fetch-references --organize=flat")
        assert self.crds_exists(self._rmap) is True
        assert self.crds_exists(self.ref1) is True
        assert self.crds_exists(self.ref2) is True

    def test_sync_organize_instr(self):
        self.run_script(
            f"{self.sync_rmap} --fetch-references --organize=instrument --organize-delete-junk"
        )
        assert self.crds_exists(self._rmap) is True
        assert self.crds_exists(self.ref1) is True
        assert self.crds_exists(self.ref2) is True
        self.run_script(
            f"{self.sync_rmap} --fetch-references --organize=flat --organize-delete-junk"
        )

    def test_purge_mappings(self):
        self.run_script(f"{self.sync_rmap} --fetch-references")
        self.run_script("crds.sync --organize=flat")
        refnames = crds.get_cached_mapping(self._rmap).reference_names() 
        assert refnames == [self.ref1, self.ref2]
        assert rmap.list_references("*", "hst") == [self.ref1, self.ref2]
        for ref in [self.ref1, self.ref2]:
            assert self.crds_exists(ref) is True
        self.run_script(
            "crds.sync --contexts hst_acs_imphttab.rmap --fetch-references --purge-mappings --purge-references"
        )
        assert rmap.list_references("*", "hst") == [
            'w3m1716tj_imp.fits', 
            'w3m17170j_imp.fits',
            'w3m17171j_imp.fits'
        ]
        assert rmap.list_mappings("*", "hst") == ['hst_acs_imphttab.rmap']

    def test_sync_fetch_sqlite3_db(self):
        self.run_script("crds.sync --fetch-sqlite-db")

    def test_sync_dataset_ids(self):
        self.run_script("crds.sync --contexts hst.pmap --dataset-ids LA9K03CBQ:LA9K03CBQ --fetch-references")
