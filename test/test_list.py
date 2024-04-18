from pytest import mark
from crds.list import ListScript
from crds.core import log
import logging
log.THE_LOGGER.logger.propagate=True


@mark.hst
@mark.list
def test_list_hst_mappings(capsys, hst_default_cache_state):
    ListScript("crds.list --mappings --contexts hst.pmap")()
    out, _ = capsys.readouterr()
    out_to_check = """hst.pmap
hst_acs.imap
hst_acs_atodtab.rmap
hst_acs_biasfile.rmap
hst_acs_bpixtab.rmap
hst_acs_ccdtab.rmap
hst_acs_cfltfile.rmap
hst_acs_crrejtab.rmap
hst_acs_d2imfile.rmap
hst_acs_darkfile.rmap
hst_acs_dgeofile.rmap
hst_acs_drkcfile.rmap
hst_acs_flshfile.rmap
hst_acs_idctab.rmap
hst_acs_imphttab.rmap
hst_acs_mdriztab.rmap
hst_acs_mlintab.rmap
hst_acs_npolfile.rmap
hst_acs_oscntab.rmap
hst_acs_pctetab.rmap
hst_acs_pfltfile.rmap
hst_acs_shadfile.rmap
hst_acs_spottab.rmap
hst_cos.imap
hst_cos_badttab.rmap
hst_cos_bpixtab.rmap
hst_cos_brftab.rmap
hst_cos_brsttab.rmap
hst_cos_deadtab.rmap
hst_cos_disptab.rmap
hst_cos_flatfile.rmap
hst_cos_fluxtab.rmap
hst_cos_geofile.rmap
hst_cos_gsagtab.rmap
hst_cos_hvtab.rmap
hst_cos_lamptab.rmap
hst_cos_phatab.rmap
hst_cos_spwcstab.rmap
hst_cos_tdstab.rmap
hst_cos_walktab.rmap
hst_cos_wcptab.rmap
hst_cos_xtractab.rmap
hst_nicmos.imap
hst_nicmos_darkfile.rmap
hst_nicmos_flatfile.rmap
hst_nicmos_idctab.rmap
hst_nicmos_illmfile.rmap
hst_nicmos_maskfile.rmap
hst_nicmos_nlinfile.rmap
hst_nicmos_noisfile.rmap
hst_nicmos_pedsbtab.rmap
hst_nicmos_phottab.rmap
hst_nicmos_pmodfile.rmap
hst_nicmos_pmskfile.rmap
hst_nicmos_rnlcortb.rmap
hst_nicmos_saacntab.rmap
hst_nicmos_saadfile.rmap
hst_nicmos_tdffile.rmap
hst_nicmos_tempfile.rmap
hst_nicmos_zprattab.rmap
hst_stis.imap
hst_stis_apdestab.rmap
hst_stis_apertab.rmap
hst_stis_biasfile.rmap
hst_stis_bpixtab.rmap
hst_stis_ccdtab.rmap
hst_stis_cdstab.rmap
hst_stis_crrejtab.rmap
hst_stis_darkfile.rmap
hst_stis_disptab.rmap
hst_stis_echsctab.rmap
hst_stis_exstab.rmap
hst_stis_gactab.rmap
hst_stis_halotab.rmap
hst_stis_idctab.rmap
hst_stis_inangtab.rmap
hst_stis_lamptab.rmap
hst_stis_lfltfile.rmap
hst_stis_mlintab.rmap
hst_stis_mofftab.rmap
hst_stis_pctab.rmap
hst_stis_pfltfile.rmap
hst_stis_phottab.rmap
hst_stis_riptab.rmap
hst_stis_sdctab.rmap
hst_stis_sptrctab.rmap
hst_stis_srwtab.rmap
hst_stis_tdctab.rmap
hst_stis_tdstab.rmap
hst_stis_teltab.rmap
hst_stis_wcptab.rmap
hst_stis_xtractab.rmap
hst_wfc3.imap
hst_wfc3_atodtab.rmap
hst_wfc3_biasfile.rmap
hst_wfc3_bpixtab.rmap
hst_wfc3_ccdtab.rmap
hst_wfc3_crrejtab.rmap
hst_wfc3_darkfile.rmap
hst_wfc3_flshfile.rmap
hst_wfc3_idctab.rmap
hst_wfc3_imphttab.rmap
hst_wfc3_mdriztab.rmap
hst_wfc3_nlinfile.rmap
hst_wfc3_oscntab.rmap
hst_wfc3_pfltfile.rmap
hst_wfpc2.imap
hst_wfpc2_atodfile.rmap
hst_wfpc2_biasfile.rmap
hst_wfpc2_darkfile.rmap
hst_wfpc2_dgeofile.rmap
hst_wfpc2_flatfile.rmap
hst_wfpc2_idctab.rmap
hst_wfpc2_maskfile.rmap
hst_wfpc2_offtab.rmap
hst_wfpc2_shadfile.rmap
hst_wfpc2_wf4tfile.rmap"""
    assert out_to_check in out


@mark.jwst
@mark.list
def test_list_jwst_mappings(capsys, jwst_shared_cache_state):
    ListScript("crds.list --mappings --contexts jwst.pmap")()
    out, _ = capsys.readouterr()
    out_to_check = """jwst_miri.imap
jwst_miri_flat.rmap
jwst_miri_photom.rmap
jwst_nircam.imap
jwst_nircam_flat.rmap
jwst_nircam_photom.rmap
jwst_nirspec.imap
jwst_nirspec_photom.rmap"""
    assert out_to_check in out


@mark.hst
@mark.list
def test_list_cached_mappings(capsys, hst_default_cache_state):
    # Reducing the large output since otherwise the output is hundreds of lines.
    ListScript("crds.list --cached-mappings --full-path")()
    out, _ = capsys.readouterr()
    expected_files = ['/mappings/hst/hst.pmap', '/mappings/hst/hst_0001.pmap', '/mappings/hst/hst_0002.pmap']
    for f in expected_files:
        assert f in out


@mark.hst
@mark.list
def test_list_references(capsys, hst_default_cache_state):
    # Same as with list_cached_mappings.
    ListScript("crds.list --references --contexts hst.pmap")()
    out, _ = capsys.readouterr()
    checks = ['d6n1328ou.r6h', 'h5s1140lo_pfl.fits', 'i9u1759io_drk.fits', 'w2j2046ej_dkc.fits']
    for check in checks:
        assert check in out


@mark.hst
@mark.list
def test_list_cached_references_hst(capsys, hst_default_cache_state):
   base_path = f'{hst_default_cache_state.cache}/references/hst'
   ListScript("crds.list --cached-references --full-path")()
   out, _ = capsys.readouterr()
   expected_files = ['41g16069m_tmg.fits', 'y951738kl_hv.fits', 'yas2005el_hv.fits']
   for f in expected_files:
       assert f'{base_path}/{f}' in out


@mark.jwst
@mark.list
def test_list_cached_references_jwst(capsys, jwst_default_cache_state):
    base_path = f'{jwst_default_cache_state.cache}/references/jwst'
    ListScript("crds.list --cached-references --full-path")()
    out, _ = capsys.readouterr()
    expected_files = ['jwst_miri_flat_0006.fits', 'jwst_niriss_flat_0000.fits']
    for f in expected_files:
        assert f'{base_path}/{f}' in out


@mark.hst
@mark.list
def test_list_dataset_ids(capsys, hst_default_cache_state):
    ListScript("crds.list --dataset-ids acs --hst")()
    out, _ = capsys.readouterr()
    out_to_check_acs = """J6FY01020:J6FY01EEQ
J6FY01020:J6FY01EJQ
J6FY01020:J6FY01EOQ
J6FY01020:J6FY01ESQ"""
    assert out_to_check_acs in out


@mark.hst
@mark.list
def test_list_dataset_headers(capsys, hst_default_cache_state):
    ListScript("crds.list --dataset-headers U20L0U01T:U20L0U01T --minimize-header --contexts hst.pmap --hst")()
    out, _ = capsys.readouterr()
    out_to_check = """Dataset pars for 'U20L0U01T:U20L0U01T' with respect to 'hst.pmap':
 {'ATODGAIN': '15.0',
 'CRDS_CTX': 'hst.pmap',
 'DATE-OBS': '1993-12-07',
 'FILTER1': '0.0',
 'FILTER2': '0.0',
 'FILTNAM1': 'UNDEFINED',
 'FILTNAM2': 'UNDEFINED',
 'IMAGETYP': 'BIAS',
 'INSTRUME': 'WFPC2',
 'LRFWAVE': '0.0',
 'MODE': 'FULL',
 'SERIALS': 'OFF',
 'SHUTTER': 'A',
 'TIME-OBS': '10:07:16.929999',
 'dataset_id': 'U20L0U01T:U20L0U01T'}"""
    assert out_to_check in out


@mark.hst
@mark.list
def test_list_dataset_headers_json(capsys, hst_default_cache_state):
    ListScript("crds.list --dataset-headers U20L0U01T:U20L0U01T --contexts hst.pmap --json --hst")()
    out, _ = capsys.readouterr()
    out_to_check = """{"U20L0U01T:U20L0U01T": {"ASN_ID_DSN": "U20L0U01T", "ATODFILE": "DBU1405FU.R1H", "ATODGAIN": \
"15.0", "BIASFILE": "E4P16298U.R2H", "DARKFILE": "E1Q14338U.R3H", "DGEOFILE": "SA119437U_DXY.FITS", "EXPSTART": \
"1993-12-07 10:07:16.930000", "FILTER1": "0.0", "FILTER2": "0.0", "FILTNAM1": "UNDEFINED", "FILTNAM2": "UNDEFINED", \
"FLATFILE": "N/A", "IDCTAB": "SAD1946EU_IDC.FITS", "IMAGETYP": "BIAS", "LRFWAVE": "0.0", "MASKFILE": "F8213081U.R0H", \
"MEMBER_NAME_DSN": "U20L0U01T", "MEMBER_TYPE": "UNDEFINED", "MODE": "FULL", "OFFTAB": "S9M1329LU_OFF.FITS", "SERIALS": \
"OFF", "SHADFILE": "E371355EU.R5H", "SHUTTER": "A", "WF4TFILE": "N/A", "INSTRUME": "WFPC2", "DATE-OBS": "1993-12-07", \
"TIME-OBS": "10:07:16.929999"}}"""
    assert out_to_check in out


@mark.hst
@mark.list
def test_list_dataset_headers_bogus(hst_default_cache_state, caplog):
    ListScript("crds.list --dataset-headers BAR:BAR --contexts hst.pmap --hst")()
    with caplog.at_level(logging.ERROR, logger="CRDS"):
        out = caplog.text
    out_to_check = """Failed fetching dataset parameters with repect to 'hst.pmap' for ['BAR:BAR'] : CRDS jsonrpc failure 'get_dataset_headers_by_id' OtherError: Can't determine instrument for dataset 'BAR'"""
    assert out_to_check in out


@mark.hst
@mark.list
def test_list_dataset_headers_id_expansions_only(capsys, hst_default_cache_state):
   ListScript("crds.list --dataset-headers I9ZF01010 --id-expansions-only --contexts hst.pmap --hst")()
   out, _ = capsys.readouterr()
   out_to_check = """I9ZF01010:I9ZF01DZQ
I9ZF01010:I9ZF01E0Q
I9ZF01010:I9ZF01E1Q
I9ZF01010:I9ZF01E3Q"""
   assert out_to_check in out
   

@mark.hst
@mark.list
def test_list_required_parkeys_pmap(capsys, hst_default_cache_state):
    ListScript("crds.list --required-parkeys --contexts hst.pmap --hst")()
    out, _ = capsys.readouterr()
    out_to_check = """--------------------- Parkeys required for 'hst.pmap' ---------------------
acs = ['INSTRUME', 'APERTURE', 'ATODCORR', 'BIASCORR', 'CCDAMP', 'CCDCHIP', 'CCDGAIN', 'CRCORR', 'DARKCORR', 'DATE-OBS', 'DETECTOR', 'DQICORR', 'DRIZCORR', 'FILTER1', 'FILTER2', 'FLASHCUR', 'FLATCORR', 'FLSHCORR', 'FW1OFFST', 'FW2OFFST', 'FWSOFFST', 'GLINCORR', 'LTV1', 'LTV2', 'NUMCOLS', 'NUMROWS', 'OBSTYPE', 'PCTECORR', 'PHOTCORR', 'REFTYPE', 'SHADCORR', 'SHUTRPOS', 'TIME-OBS', 'XCORNER', 'YCORNER']
cos = ['INSTRUME', 'BADTCORR', 'BRSTCORR', 'DATE-OBS', 'DEADCORR', 'DETECTOR', 'EXPTYPE', 'FLATCORR', 'FLUXCORR', 'LIFE_ADJ', 'OBSMODE', 'OBSTYPE', 'OPT_ELEM', 'REFTYPE', 'TDSCORR', 'TIME-OBS', 'WALKCORR']
nicmos = ['INSTRUME', 'CAMERA', 'DATE-OBS', 'FILTER', 'NREAD', 'OBSMODE', 'READOUT', 'REFTYPE', 'SAMP_SEQ', 'TIME-OBS']
stis = ['INSTRUME', 'APERTURE', 'BINAXIS1', 'BINAXIS2', 'CCDAMP', 'CCDGAIN', 'CCDOFFST', 'CENWAVE', 'DATE-OBS', 'DETECTOR', 'OBSTYPE', 'OPT_ELEM', 'REFTYPE', 'TIME-OBS']
wfc3 = ['INSTRUME', 'APERTURE', 'ATODCORR', 'BIASCORR', 'BINAXIS1', 'BINAXIS2', 'CCDAMP', 'CCDGAIN', 'CHINJECT', 'DARKCORR', 'DATE-OBS', 'DETECTOR', 'DQICORR', 'DRIZCORR', 'FILTER', 'FLASHCUR', 'FLATCORR', 'FLSHCORR', 'PHOTCORR', 'REFTYPE', 'SAMP_SEQ', 'SHUTRPOS', 'SUBARRAY', 'SUBTYPE', 'TIME-OBS']
wfpc2 = ['INSTRUME', 'ATODGAIN', 'DATE-OBS', 'FILTER1', 'FILTER2', 'FILTNAM1', 'FILTNAM2', 'IMAGETYP', 'LRFWAVE', 'MODE', 'REFTYPE', 'SERIALS', 'SHUTTER', 'TIME-OBS']"""
    assert out_to_check in out


@mark.hst
@mark.list
def test_list_required_parkeys_imap(capsys, default_shared_state):
    ListScript("crds.list --required-parkeys --contexts hst_acs.imap --hst")()
    out, _ = capsys.readouterr()
    out_to_check = """atodtab: ['DETECTOR', 'DATE-OBS', 'TIME-OBS', 'ATODCORR']
biasfile: ['DETECTOR', 'CCDAMP', 'CCDGAIN', 'APERTURE', 'NUMCOLS', 'NUMROWS', 'LTV1', 'LTV2', 'XCORNER', 'YCORNER', 'CCDCHIP', 'DATE-OBS', 'TIME-OBS', 'BIASCORR', 'XCORNER', 'YCORNER', 'CCDCHIP']
bpixtab: ['DETECTOR', 'DATE-OBS', 'TIME-OBS', 'DQICORR']
ccdtab: ['DETECTOR', 'DATE-OBS', 'TIME-OBS']
cfltfile: ['DETECTOR', 'FILTER1', 'FILTER2', 'OBSTYPE', 'DATE-OBS', 'TIME-OBS']
crrejtab: ['DETECTOR', 'DATE-OBS', 'TIME-OBS', 'CRCORR']
d2imfile: ['DATE-OBS', 'TIME-OBS', 'DRIZCORR']
darkfile: ['DETECTOR', 'CCDAMP', 'CCDGAIN', 'DATE-OBS', 'TIME-OBS', 'DARKCORR']
dgeofile: ['DETECTOR', 'FILTER1', 'FILTER2', 'DATE-OBS', 'TIME-OBS']
drkcfile: ['DETECTOR', 'CCDAMP', 'CCDGAIN', 'DATE-OBS', 'TIME-OBS', 'PCTECORR']
flshfile: ['DETECTOR', 'CCDAMP', 'CCDGAIN', 'FLASHCUR', 'SHUTRPOS', 'DATE-OBS', 'TIME-OBS', 'FLSHCORR']
idctab: ['DETECTOR', 'DATE-OBS', 'TIME-OBS']
imphttab: ['DETECTOR', 'DATE-OBS', 'TIME-OBS', 'PHOTCORR']
mdriztab: ['DETECTOR', 'DATE-OBS', 'TIME-OBS', 'DRIZCORR']
mlintab: ['DETECTOR', 'DATE-OBS', 'TIME-OBS', 'GLINCORR']
npolfile: ['DETECTOR', 'FILTER1', 'FILTER2', 'DATE-OBS', 'TIME-OBS', 'DRIZCORR']
oscntab: ['DETECTOR', 'DATE-OBS', 'TIME-OBS']
pctetab: ['DETECTOR', 'DATE-OBS', 'TIME-OBS', 'PCTECORR']
pfltfile: ['DETECTOR', 'CCDAMP', 'FILTER1', 'FILTER2', 'OBSTYPE', 'FW1OFFST', 'FW2OFFST', 'FWSOFFST', 'DATE-OBS', 'TIME-OBS', 'FLATCORR']
shadfile: ['DETECTOR', 'DATE-OBS', 'TIME-OBS', 'SHADCORR']
spottab: ['DETECTOR', 'OBSTYPE', 'DATE-OBS', 'TIME-OBS']"""
    assert out_to_check in out


@mark.hst
@mark.list
def test_list_required_parkeys_rmap(capsys, default_shared_state):
    ListScript("crds.list --required-parkeys --contexts hst_acs_darkfile.rmap --hst")()
    out, _ = capsys.readouterr()
    out_to_check = """hst_acs_darkfile.rmap: ['DETECTOR', 'CCDAMP', 'CCDGAIN', 'DATE-OBS', 'TIME-OBS', 'DARKCORR']"""
    assert out_to_check in out


@mark.hst
@mark.list
def test_list_resolve_contexts_range(capsys, hst_default_cache_state):
    ListScript("crds.list --resolve-contexts --range 0:5 --hst")()
    out, _ = capsys.readouterr()
    out_to_check = """hst_0001.pmap
hst_0002.pmap
hst_0003.pmap
hst_0004.pmap
hst_0005.pmap"""
    assert out_to_check in out


@mark.hst
@mark.list
def test_list_resolve_contexts_date(capsys, hst_default_cache_state):
    ListScript("crds.list --resolve-contexts --contexts hst-2014-11-11T00:00:00 --hst")()
    out, _ = capsys.readouterr()
    out_to_check = """hst_0297.pmap"""
    assert out_to_check in out


@mark.hst
@mark.list
def test_list_remote_context(capsys, hst_default_cache_state):
    ListScript("crds.list --remote-context hst-ops-pipeline --hst")()
    out, _ = capsys.readouterr()
    assert 'hst_' in out
    assert '.pmap' in out


@mark.hst
@mark.list
def test_list_operational_context(capsys, hst_default_cache_state):
    ListScript("crds.list --operational-context --hst")()
    out, _ = capsys.readouterr()
    assert 'hst_' in out
    assert '.pmap' in out


@mark.hst
@mark.list
def test_list_references_by_context(capsys, hst_default_cache_state):
    ListScript("crds.list --references --contexts hst-cos-deadtab-2014-11-11T00:00:00 --hst")()
    out, _ = capsys.readouterr()
    out_to_check = """s7g1700gl_dead.fits
s7g1700ql_dead.fits"""
    assert out_to_check in out


@mark.hst
@mark.list
def test_list_cat_mappings(capsys, hst_default_cache_state):
    ListScript("crds.list --cat --mappings --contexts hst-cos-deadtab-2014-11-11T00:00:00 --hst")()
    out, _ = capsys.readouterr()
    out_to_check1 = """mappings/hst/hst_cos_deadtab_0250.rmap"""
    out_to_check2 = """header = {
    'derived_from' : 'generated from CDBS database 2014-05-09 23:24:57.840119',
    'filekind' : 'DEADTAB',
    'instrument' : 'COS',
    'mapping' : 'REFERENCE',
    'name' : 'hst_cos_deadtab_0250.rmap',
    'observatory' : 'HST',
    'parkey' : (('DETECTOR',), ('DATE-OBS', 'TIME-OBS')),
    'reffile_format' : 'TABLE',
    'reffile_required' : 'NONE',
    'reffile_switch' : 'DEADCORR',
    'rmap_relevance' : '(DEADCORR != "OMIT")',
    'sha1sum' : 'bde314f1848b67891d6309b30eaa5c95611f86e2',
}
"""
    out_to_check3 = """selector = Match({
    ('FUV',) : UseAfter({
        '1996-10-01 00:00:00' : 's7g1700gl_dead.fits',
    }),
    ('NUV',) : UseAfter({
        '1996-10-01 00:00:00' : 's7g1700ql_dead.fits',
    }),
})"""
    out_to_check4 = """{'activation_date': '2014-05-15 15:31:54',
 'aperture': 'none',
 'blacklisted': 'false',
 'change_level': 'severe',
 'comment': 'none',
 'creator_name': 'todd miller',
 'delivery_date': '2014-05-11 08:14:02',
 'derived_from': 'generated from cdbs database 2014-05-09 23:24:57.840119',
 'description': 'rebaselined hst rmaps as 250-series for opus 2014.2',
 'filekind': 'deadtab',
 'history': 'none',
 'instrument': 'cos',
 'name': 'hst_cos_deadtab_0250.rmap',
 'observatory': 'hst',
 'pedigree': '',
 'reference_file_type': '',
 'rejected': 'false',
 'replaced_by_filename': '',
 'sha1sum': '41cbdf620d41586fbc3de3e26d14d14eb42cc244',
 'size': '711',
 'state': 'operational',
 'type': 'mapping',
 'uploaded_as': 'hst_cos_deadtab_0250.rmap',
 'useafter_date': '2050-01-01 00:00:00'}"""
    assert out_to_check1 in out
    assert out_to_check2 in out
    assert out_to_check3 in out
    assert out_to_check4 in out


@mark.hst
@mark.list
def test_list_status(capsys, hst_default_cache_state):
    ListScript("crds.list --status --hst")()
    out, _ = capsys.readouterr()
    assert "CRDS Summary =" in out
    assert "CRDS Version = " in out
    assert "CRDS_MODE = 'auto'" in out
    assert "CRDS_PATH = " in out
    assert "CRDS_SERVER_URL =" in out
    assert "Effective Context = 'hst_" in out
    assert "Last Synced = " in out
    assert "Python Executable =" in out
    assert "Python Version =" in out
    assert "Readonly Cache = False" in out


@mark.hst
@mark.list
def test_list_config(capsys, hst_default_cache_state):
    ListScript("crds.list --config --hst")()
    out, _ = capsys.readouterr()
    assert "CRDS Environment" in out
    assert "CRDS Client Config" in out
    assert "CRDS Actual Paths" in out
    assert "CRDS Server Info" in out
    assert "Calibration Environment" in out
    assert "Python Environment" in out
