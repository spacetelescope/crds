"""This module tests the synphot pseudo-instrument support for HST."""
from pytest import mark, fixture
import logging
from crds.core import config as crds_config
from crds.core import log, naming, timestamp
from crds.hst import locate as hst_locate
from crds.refactoring import refactor
from crds.certify import CertifyScript
from crds.diff import DiffScript
from crds.core.rmap import get_cached_mapping
from crds.misc.synphot import (
    SynphotCoreIntegrationTest,
    SynphotObsmodeIntegrationTest,
    SynphotLookupGenerator
)

log.THE_LOGGER.logger.propagate = True

NOW = timestamp.parse_date("2018-11-14T00:00:00")

def check_logs(expected, out):
    for line in expected.splitlines():
        assert line.strip() in out

#THERMAL
@mark.hst
@mark.synphot
def test_synphot_naming_thermal(default_shared_state, hst_data):
    # THERMAL
    assert crds_config.is_crds_name("wfc3_ir_f098m_002_th.fits") is False
    assert crds_config.is_cdbs_name("wfc3_ir_f098m_002_th.fits") is True
    assert crds_config.is_reference("wfc3_ir_f098m_002_th.fits") is True
    assert crds_config.is_mapping("wfc3_ir_f098m_002_th.fits") is False
    props = hst_locate.get_file_properties("wfc3_ir_f098m_002_th.fits")
    assert props == ('synphot', 'thermal')
    props = hst_locate.ref_properties_from_cdbs_path(f"{hst_data}/wfc3_ir_f098m_002_th.fits")
    assert props == (f'{hst_data}', 'hst', 'synphot', 'thermal', 'wfc3_ir_f098m_002_th', '.fits')
    props = hst_locate.ref_properties_from_header(f"{hst_data}/wfc3_ir_f098m_002_th.fits")
    assert props == (f'{hst_data}', 'hst', 'synphot', 'thermal', 'wfc3_ir_f098m_002_th', '.fits')
    name = naming.generate_unique_name("wfc3_ir_f098m_002_th.fits", "hst", NOW)
    assert name == '2be00000m_th.fits'


# THRUPUT
@mark.hst
@mark.synphot
def test_synphot_naming_thruput(default_shared_state, hst_data):
    assert crds_config.is_crds_name("wfc3_uvis_f469nf2_003_syn.fits") is False
    assert crds_config.is_cdbs_name("wfc3_uvis_f469nf2_003_syn.fits") is True
    assert crds_config.is_reference("wfc3_uvis_f469nf2_003_syn.fits") is True
    assert crds_config.is_mapping("wfc3_uvis_f469nf2_003_syn.fits") is False
    props = hst_locate.get_file_properties("wfc3_uvis_f469nf2_003_syn.fits")
    assert props == ('synphot', 'thruput')
    props = hst_locate.ref_properties_from_cdbs_path(f"{hst_data}/wfc3_uvis_f469nf2_003_syn.fits")
    assert props == (f'{hst_data}', 'hst', 'synphot', 'thruput', 'wfc3_uvis_f469nf2_003_syn', '.fits')
    props = hst_locate.ref_properties_from_header(f"{hst_data}/wfc3_uvis_f469nf2_003_syn.fits")
    assert props == (f'{hst_data}', 'hst', 'synphot', 'thruput', 'wfc3_uvis_f469nf2_003_syn', '.fits')
    name = naming.generate_unique_name("wfc3_uvis_f469nf2_003_syn.fits", "hst", NOW)
    assert name == '2be00000m_syn.fits'


# TMGTAB
@mark.hst
@mark.synphot
def test_synphot_naming_tmgtab(default_shared_state, hst_data):
    assert crds_config.is_crds_name("2381905mm_tmg.fits") is False
    assert crds_config.is_cdbs_name("2381905mm_tmg.fits") is True
    assert crds_config.is_reference("2381905mm_tmg.fits") is True
    assert crds_config.is_mapping("2381905mm_tmg.fits") is False
    props = hst_locate.get_file_properties("2381905mm_tmg.fits")
    assert props == ('synphot', 'tmgtab')
    props = hst_locate.ref_properties_from_cdbs_path(f"{hst_data}/2381905mm_tmg.fits")
    assert props == (f'{hst_data}', 'hst', 'synphot', 'tmgtab', '2381905mm_tmg', '.fits')
    props = hst_locate.ref_properties_from_header(f"{hst_data}/2381905mm_tmg.fits")
    assert props == (f'{hst_data}', 'hst', 'synphot', 'tmgtab', '2381905mm_tmg', '.fits')
    name = naming.generate_unique_name("2381905mm_tmg.fits", "hst", NOW)
    assert name == '2be00000m_tmg.fits'


# TMCTAB
@mark.hst
@mark.synphot
def test_synphot_naming_tmctab(default_shared_state, hst_data):
    assert crds_config.is_crds_name("43h1909cm_tmc.fits") is False
    assert crds_config.is_cdbs_name("43h1909cm_tmc.fits") is True
    assert crds_config.is_reference("43h1909cm_tmc.fits") is True
    assert crds_config.is_mapping("43h1909cm_tmc.fits") is False
    props = hst_locate.get_file_properties("43h1909cm_tmc.fits")
    assert props == ('synphot', 'tmctab')
    props = hst_locate.ref_properties_from_cdbs_path(f"{hst_data}/43h1909cm_tmc.fits")
    assert props == (f'{hst_data}', 'hst', 'synphot', 'tmctab', '43h1909cm_tmc', '.fits')
    props = hst_locate.ref_properties_from_header(f"{hst_data}/43h1909cm_tmc.fits")
    assert props == (f'{hst_data}', 'hst', 'synphot', 'tmctab', '43h1909cm_tmc', '.fits')
    name = naming.generate_unique_name("43h1909cm_tmc.fits", "hst", NOW)
    assert name == '2be00000m_tmc.fits'


# TMTTAB
@mark.hst
@mark.synphot
def test_synphot_naming_tmttab(default_shared_state, hst_data):
    assert crds_config.is_crds_name("tae17277m_tmt.fits") is False
    assert crds_config.is_cdbs_name("tae17277m_tmt.fits") is True
    assert crds_config.is_reference("tae17277m_tmt.fits") is True
    assert crds_config.is_mapping("tae17277m_tmt.fits") is False
    props = hst_locate.get_file_properties("tae17277m_tmt.fits")
    assert props == ('synphot', 'tmttab')
    props = hst_locate.ref_properties_from_header(f"{hst_data}/tae17277m_tmt.fits")
    assert props == (f'{hst_data}', 'hst', 'synphot', 'tmttab', 'tae17277m_tmt', '.fits')
    props = hst_locate.ref_properties_from_cdbs_path(f"{hst_data}/tae17277m_tmt.fits")
    assert props == (f'{hst_data}', 'hst', 'synphot', 'tmttab', 'tae17277m_tmt', '.fits')
    name = naming.generate_unique_name("tae17277m_tmt.fits", "hst", NOW)
    assert name == '2be00000m_tmt.fits'


# TMC   reference
@mark.hst
@mark.synphot
def test_synphot_certify_refs_tmc(hst_shared_cache_state, hst_data, caplog):
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(f"crds.certify --run-fitsverify {hst_data}/43h1909cm_tmc.fits --comparison-context hst_0772.pmap")()
        out1 = caplog.text
    expected1 = f"""Certifying '{hst_data}/43h1909cm_tmc.fits' (1/1) as 'FITS' relative to context 'hst_0772.pmap'
    FITS file '43h1909cm_tmc.fits' conforms to FITS standards.
    Comparing reference '43h1909cm_tmc.fits' against '43h1240om_tmc.fits'
    Mode columns defined by spec for old reference '43h1240om_tmc.fits[1]' are: ['COMPNAME']
    All column names for this table old reference '43h1240om_tmc.fits[1]' are: ['TIME', 'COMPNAME', 'FILENAME', 'COMMENT']
    Checking for duplicate modes using intersection ['COMPNAME']
    Mode columns defined by spec for new reference '43h1909cm_tmc.fits[1]' are: ['COMPNAME']
    All column names for this table new reference '43h1909cm_tmc.fits[1]' are: ['TIME', 'COMPNAME', 'FILENAME', 'COMMENT']
    Checking for duplicate modes using intersection ['COMPNAME']
    Running fitsverify.
    >> File: {hst_data}/43h1909cm_tmc.fits
    >>
    >> 2 Header-Data Units in this file.
    >>
    >> =================== HDU 1: Primary Array ===================
    >>
    >>  121 header keywords
    >>
    >>  Null data array; NAXIS = 0
    >>
    >> =================== HDU 2: BINARY Table ====================
    >>
    >>  21 header keywords
    >>
    >>    (4 columns x 2713 rows)
    >>
    >>  Col# Name (Units)       Format
    >>    1 TIME                 26A
    >>    2 COMPNAME             18A
    >>    3 FILENAME             56A
    >>    4 COMMENT              68A
    >>
    >> ++++++++++++++++++++++ Error Summary  ++++++++++++++++++++++
    >>
    >>  HDU#  Name (version)       Type             Warnings  Errors
    >>  1                          Primary Array    0         0
    >>  2                          Binary Table     0         0
    >>
    >> **** Verification found 0 warning(s) and 0 error(s). ****
    0 errors"""
    check_logs(expected1, out1)

    caplog.clear()
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(f"crds.certify --run-fitsverify {hst_data}/2381905mm_tmg.fits --comparison-context hst_0691.pmap")()
        out2 = caplog.text

    expected2 = f"""Certifying '{hst_data}/2381905mm_tmg.fits' (1/1) as 'FITS' relative to context 'hst_0691.pmap'
    FITS file '2381905mm_tmg.fits' conforms to FITS standards.
    Mode columns defined by spec for new reference '2381905mm_tmg.fits[1]' are: ['COMPNAME', 'KEYWORD', 'INNODE', 'OUTNODE', 'THCOMPNAME']
    All column names for this table new reference '2381905mm_tmg.fits[1]' are: ['COMPNAME', 'KEYWORD', 'INNODE', 'OUTNODE', 'THCOMPNAME', 'COMMENT']
    Checking for duplicate modes using intersection ['COMPNAME', 'INNODE', 'KEYWORD', 'OUTNODE', 'THCOMPNAME']
    No comparison reference for '2381905mm_tmg.fits' in context 'hst_0691.pmap'. Skipping tables comparison.
    Running fitsverify.
    >> File: {hst_data}/2381905mm_tmg.fits
    >>
    >> 2 Header-Data Units in this file.
    >>
    >> =================== HDU 1: Primary Array ===================
    >>
    >>  192 header keywords
    >>
    >>  Null data array; NAXIS = 0
    >>
    >> =================== HDU 2: BINARY Table ====================
    >>
    >>  103 header keywords
    >>
    >>    (6 columns x 3656 rows)
    >>
    >>  Col# Name (Units)       Format
    >>    1 COMPNAME             18A
    >>    2 KEYWORD              11A
    >>    3 INNODE               J
    >>    4 OUTNODE              J
    >>    5 THCOMPNAME           17A
    >>    6 COMMENT              68A
    >>
    >> ++++++++++++++++++++++ Error Summary  ++++++++++++++++++++++
    >>
    >>  HDU#  Name (version)       Type             Warnings  Errors
    >>  1                          Primary Array    0         0
    >>  2                          Binary Table     0         0
    >>
    >> **** Verification found 0 warning(s) and 0 error(s). ****
    ########################################
    0 errors"""
    check_logs(expected2, out2)


@mark.hst
@mark.synphot
def test_synphot_certify_refs_tmt(hst_shared_cache_state, hst_data, caplog):
    # TMT   reference
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(f"crds.certify  --run-fitsverify {hst_data}/tae17277m_tmt.fits --comparison-context hst_0691.pmap")()
        out = caplog.text
    expected = f"""Certifying '{hst_data}/tae17277m_tmt.fits' (1/1) as 'FITS' relative to context 'hst_0691.pmap'
    FITS file 'tae17277m_tmt.fits' conforms to FITS standards.
    Malformed FILENAME value at index 1 (missing or invalid path prefix)
    Comparing reference 'tae17277m_tmt.fits' against '3241637sm_tmt.fits'
    Mode columns defined by spec for old reference '3241637sm_tmt.fits[1]' are: ['COMPNAME']
    All column names for this table old reference '3241637sm_tmt.fits[1]' are: ['TIME', 'COMPNAME', 'FILENAME', 'COMMENT']
    Checking for duplicate modes using intersection ['COMPNAME']
    Mode columns defined by spec for new reference 'tae17277m_tmt.fits[1]' are: ['COMPNAME']
    All column names for this table new reference 'tae17277m_tmt.fits[1]' are: ['TIME', 'COMPNAME', 'FILENAME', 'COMMENT']
    Checking for duplicate modes using intersection ['COMPNAME']
    Table mode (('COMPNAME', 'dark'),) of new reference 'tae17277m_tmt.fits[1]' is NOT IN old reference '3241637sm_tmt.fits'
    Table mode (('COMPNAME', 'nic1_dn'),) of new reference 'tae17277m_tmt.fits[1]' is NOT IN old reference '3241637sm_tmt.fits'
    Table mode (('COMPNAME', 'nic2_dn'),) of new reference 'tae17277m_tmt.fits[1]' is NOT IN old reference '3241637sm_tmt.fits'
    Table mode (('COMPNAME', 'nic3_dn'),) of new reference 'tae17277m_tmt.fits[1]' is NOT IN old reference '3241637sm_tmt.fits'
    Running fitsverify.
    >> File: {hst_data}/tae17277m_tmt.fits
    >>
    >> 2 Header-Data Units in this file.
    >>
    >> =================== HDU 1: Primary Array ===================
    >>
    >>  32 header keywords
    >>
    >>  Null data array; NAXIS = 0
    >>
    >> =================== HDU 2: BINARY Table ====================
    >>
    >>  54 header keywords
    >>
    >>    (4 columns x 144 rows)
    >>
    >>  Col# Name (Units)       Format
    >>    1 TIME                 27A
    >>    2 COMPNAME             18A
    >>    3 FILENAME             50A
    >>    4 COMMENT              68A
    >>
    >> ++++++++++++++++++++++ Error Summary  ++++++++++++++++++++++
    >>
    >>  HDU#  Name (version)       Type             Warnings  Errors
    >>  1                          Primary Array    0         0
    >>  2                          Binary Table     0         0
    >>
    >> **** Verification found 0 warning(s) and 0 error(s). ****
    1 errors"""
    check_logs(expected, out)


@mark.hst
@mark.synphot
def test_synphot_certify_refs_thermal(hst_shared_cache_state, hst_data, caplog):
    #THERMAL reference
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(f"crds.certify  --run-fitsverify {hst_data}/wfc3_ir_f098m_002_th.fits --comparison-context hst_0691.pmap")()
        out = caplog.text
    expected = f"""Certifying '{hst_data}/wfc3_ir_f098m_002_th.fits' (1/1) as 'FITS' relative to context 'hst_0691.pmap'
    FITS file 'wfc3_ir_f098m_002_th.fits' conforms to FITS standards.
    New filename version (002) must exceed previous version (002)
    Missing suggested keyword 'LITREF'
    Mode columns defined by spec for new reference 'wfc3_ir_f098m_002_th.fits[1]' are: ['WAVELENGTH']
    All column names for this table new reference 'wfc3_ir_f098m_002_th.fits[1]' are: ['WAVELENGTH', 'EMISSIVITY']
    Checking for duplicate modes using intersection ['WAVELENGTH']
    No comparison reference for 'wfc3_ir_f098m_002_th.fits' in context 'hst_0691.pmap'. Skipping tables comparison.
    Running fitsverify.
    >> File: {hst_data}/wfc3_ir_f098m_002_th.fits
    >>
    >> 2 Header-Data Units in this file.
    >>
    >> =================== HDU 1: Primary Array ===================
    >>
    >>  17 header keywords
    >>
    >>  Null data array; NAXIS = 0
    >>
    >> =================== HDU 2: BINARY Table ====================
    >>
    >>  20 header keywords
    >>
    >>    (2 columns x 5863 rows)
    >>
    >>  Col# Name (Units)       Format
    >>    1 WAVELENGTH (ANGSTROM E
    >>    2 EMISSIVITY           E
    >>
    >> ++++++++++++++++++++++ Error Summary  ++++++++++++++++++++++
    >>
    >>  HDU#  Name (version)       Type             Warnings  Errors
    >>  1                          Primary Array    0         0
    >>  2                          Binary Table     0         0
    >>
    >> **** Verification found 0 warning(s) and 0 error(s). ****
    ########################################
    1 errors"""
    check_logs(expected, out)


@mark.hst
@mark.synphot
def test_synphot_certify_refs_thruput(hst_shared_cache_state, hst_data, caplog):
    # THRUPUT reference
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(f"crds.certify  --run-fitsverify {hst_data}/wfc3_uvis_f469nf2_003_syn.fits --comparison-context hst_0691.pmap")()
        out = caplog.text
    
    expected = f"""Certifying '{hst_data}/wfc3_uvis_f469nf2_003_syn.fits' (1/1) as 'FITS' relative to context 'hst_0691.pmap'
    FITS file 'wfc3_uvis_f469nf2_003_syn.fits' conforms to FITS standards.
    New filename version (003) must exceed previous version (003)
    Missing suggested keyword 'LITREF'
    Mode columns defined by spec for new reference 'wfc3_uvis_f469nf2_003_syn.fits[1]' are: ['WAVELENGTH']
    All column names for this table new reference 'wfc3_uvis_f469nf2_003_syn.fits[1]' are: ['WAVELENGTH', 'THROUGHPUT']
    Checking for duplicate modes using intersection ['WAVELENGTH']
    No comparison reference for 'wfc3_uvis_f469nf2_003_syn.fits' in context 'hst_0691.pmap'. Skipping tables comparison.
    Running fitsverify.
    >> File: {hst_data}/wfc3_uvis_f469nf2_003_syn.fits
    >>
    >> 2 Header-Data Units in this file.
    >>
    >> =================== HDU 1: Primary Array ===================
    >>
    >>  24 header keywords
    >>
    >>  Null data array; NAXIS = 0
    >>
    >> =================== HDU 2: BINARY Table ====================
    >>
    >>  17 header keywords
    >>
    >>    (2 columns x 13 rows)
    >>
    >>  Col# Name (Units)       Format
    >>    1 WAVELENGTH (ANGSTROM E
    >>    2 THROUGHPUT (TRANSMIS E
    >>
    >> ++++++++++++++++++++++ Error Summary  ++++++++++++++++++++++
    >>
    >>  HDU#  Name (version)       Type             Warnings  Errors
    >>  1                          Primary Array    0         0
    >>  2                          Binary Table     0         0
    >>
    >> **** Verification found 0 warning(s) and 0 error(s). ****
    ########################################
    1 errors"""
    check_logs(expected, out)


@mark.hst
@mark.synphot
def test_synphot_certify_rmaps_tmc(default_shared_state, hst_data, caplog):
    # TMC   rmap
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(f"crds.certify {hst_data}/synphot_tmctab.rmap --comparison-context hst_0857.pmap")()
        out = caplog.text
       
    expected = f"""Certifying '{hst_data}/synphot_tmctab.rmap' (1/1) as 'MAPPING' relative to context 'hst_0857.pmap'
    Mapping 'synphot_tmctab.rmap' corresponds to 'hst_synphot_tmctab_0021.rmap' from context 'hst_0857.pmap' for checking mapping differences.
    Checking diffs from 'hst_synphot_tmctab_0021.rmap' to 'synphot_tmctab.rmap'
    0 errors"""
    check_logs(expected, out)


@mark.hst
@mark.synphot
def test_synphot_certify_rmaps_tmg(default_shared_state, hst_data, caplog):
    # TMG   rmap
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(f"crds.certify {hst_data}/synphot_tmgtab.rmap --comparison-context hst_0857.pmap")()
        out = caplog.text
    expected = f"""Certifying '{hst_data}/synphot_tmgtab.rmap' (1/1) as 'MAPPING' relative to context 'hst_0857.pmap'
    Mapping 'synphot_tmgtab.rmap' corresponds to 'hst_synphot_tmgtab_0007.rmap' from context 'hst_0857.pmap' for checking mapping differences.
    Checking diffs from 'hst_synphot_tmgtab_0007.rmap' to 'synphot_tmgtab.rmap'
    0 errors"""
    check_logs(expected, out)


@mark.hst
@mark.synphot
def test_synphot_certify_rmaps_tmt(default_shared_state, hst_data, caplog):
    #TMT   rmap
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(f"crds.certify {hst_data}/synphot_tmttab.rmap --comparison-context hst_0857.pmap")()
        out = caplog.text
    expected = f"""Certifying '{hst_data}/synphot_tmttab.rmap' (1/1) as 'MAPPING' relative to context 'hst_0857.pmap'
    Mapping 'synphot_tmttab.rmap' corresponds to 'hst_synphot_tmttab_0001.rmap' from context 'hst_0857.pmap' for checking mapping differences.
    Checking diffs from 'hst_synphot_tmttab_0001.rmap' to 'synphot_tmttab.rmap'
    0 errors"""
    check_logs(expected, out)


@mark.hst
@mark.synphot
def test_synphot_certify_rmaps_thermal(default_shared_state, hst_data, caplog):
    # THERMAL rmap
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(f"crds.certify {hst_data}/synphot_thermal.rmap --comparison-context hst_0857.pmap")()
        out = caplog.text
    expected = f"""Certifying '{hst_data}/synphot_thermal.rmap' (1/1) as 'MAPPING' relative to context 'hst_0857.pmap'
    Mapping 'synphot_thermal.rmap' corresponds to 'hst_synphot_thermal_0002.rmap' from context 'hst_0857.pmap' for checking mapping differences.
    Checking diffs from 'hst_synphot_thermal_0002.rmap' to 'synphot_thermal.rmap'
    0 errors"""
    check_logs(expected, out)


@mark.hst
@mark.synphot
def test_synphot_certify_rmaps_thruput(default_shared_state, hst_data, caplog):
    #THRUPUT rmap
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(f"crds.certify {hst_data}/synphot_thruput.rmap --comparison-context hst_0857.pmap")()
        out = caplog.text
    expected = f"""Certifying '{hst_data}/synphot_thruput.rmap' (1/1) as 'MAPPING' relative to context 'hst_0857.pmap'
    Mapping 'synphot_thruput.rmap' corresponds to 'hst_synphot_thruput_0025.rmap' from context 'hst_0857.pmap' for checking mapping differences.
    Checking diffs from 'hst_synphot_thruput_0025.rmap' to 'synphot_thruput.rmap'
    0 errors"""
    check_logs(expected, out)


@mark.hst
@mark.synphot
def test_synphot_refactor_irrelevant_parkeys(default_shared_state, hst_data, caplog):
    log.set_verbose(55)
    r = get_cached_mapping(f"{hst_data}/synphot_thermal.rmap")
    header = dict(COMPNAME="NIC1_BEND", CREATED="2002-03-06 04:51:00",  DESCRIP="Use NIC2 values")

    # For classic irrelevant parkey matching where values are normalized to N/A and ignored
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        matches = r.map_irrelevant_parkeys_to_na(header)
        out = caplog.text
    assert matches == {
       'COMPNAME': 'NIC1_BEND',
        'CREATED': '2002-03-06 04:51:00',
        'DATE': 'N/A',
        'DESCRIP': 'N/A'
    }
    expected = """Parkey synphot thermal date is relevant: False 'keep_comments'
    Setting irrelevant parkey 'DATE' to N/A
    Parkey synphot thermal descrip is relevant: False 'keep_comments'
    Setting irrelevant parkey 'DESCRIP' to N/A"""
    check_logs(expected, out)


@mark.hst
@mark.synphot
def test_synphot_refactor_comment_keywords(default_shared_state, hst_data, caplog):
    #For rmap updates which add comment keywords to the match tuples for web display
    log.set_verbose(55)
    r = get_cached_mapping(f"{hst_data}/synphot_thermal.rmap")
    header = dict(COMPNAME="NIC1_BEND", CREATED="2002-03-06 04:51:00",  DESCRIP="Use NIC2 values")
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        matches = r.map_irrelevant_parkeys_to_na(header, keep_comments=True)
        out = caplog.text
    assert matches == {
        'COMPNAME': 'NIC1_BEND',
        'CREATED': '2002-03-06 04:51:00',
        'DESCRIP': 'Use NIC2 values'
    }
    expected = """Parkey synphot thermal date is relevant: True 'keep_comments'
    Parkey synphot thermal descrip is relevant: True 'keep_comments'"""
    check_logs(expected, out)


@mark.hst
@mark.synphot
def test_synphot_refactor_tmc(default_shared_state, hst_data, test_temp_dir, caplog, capsys):
    #TMC   rmap
    files =  f"{hst_data}/synphot_tmctab.rmap {test_temp_dir}/synphot_tmctab.test.rmap {hst_data}/43h1909cm_tmc.fits"
    caplog.clear()
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        refactor.RefactorScript(f"crds.refactor insert {files}")()
        out = caplog.text
    expected = """Inserting 43h1909cm_tmc.fits into 'hst_synphot_tmctab_0021.rmap'
    0 errors"""
    check_logs(expected, out)
    ndiffs = DiffScript(f"crds.diff {hst_data}/synphot_tmctab.rmap {test_temp_dir}/synphot_tmctab.test.rmap")()
    sout, _ = capsys.readouterr()
    exp_out = f"""(('{hst_data}/synphot_tmctab.rmap', '{test_temp_dir}/synphot_tmctab.test.rmap'), 'replaced 5182153pm_tmc.fits with 43h1909cm_tmc.fits')"""
    assert ndiffs == 1
    assert exp_out in sout


@mark.hst
@mark.synphot
def test_synphot_refactor_tmg(default_shared_state, hst_data, test_temp_dir, caplog, capsys):
    #TMG   rmap
    files = f"{hst_data}/synphot_tmgtab.rmap {test_temp_dir}/synphot_tmgtab.test.rmap {hst_data}/2381905mm_tmg.fits"
    caplog.clear()
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        refactor.RefactorScript(f"crds.refactor insert {files}")()
        out = caplog.text
    expected = """Inserting 2381905mm_tmg.fits into 'hst_synphot_tmgtab_0007.rmap'
    0 errors"""
    check_logs(expected, out)

    ndiffs = DiffScript(f"crds.diff  {hst_data}/synphot_tmgtab.rmap {test_temp_dir}/synphot_tmgtab.test.rmap")()
    out, _ = capsys.readouterr()
    exp_out = f"(('{hst_data}/synphot_tmgtab.rmap', '{test_temp_dir}/synphot_tmgtab.test.rmap'), 'replaced 4cm1612bm_tmg.fits with 2381905mm_tmg.fits')"
    assert ndiffs == 1
    assert exp_out in out


@mark.hst
@mark.synphot
def test_synphot_refactor_tmt(default_shared_state, hst_data, test_temp_dir, caplog, capsys):
    #TMT   rmap
    files = f"{hst_data}/synphot_tmttab.rmap {test_temp_dir}/synphot_tmttab.test.rmap {hst_data}/tae17277m_tmt.fits"
    caplog.clear()
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        refactor.RefactorScript(f"crds.refactor insert {files}")()
        out = caplog.text
    expected = """Inserting tae17277m_tmt.fits into 'hst_synphot_tmttab_0001.rmap'
    0 errors"""
    check_logs(expected, out)

    ndiffs = DiffScript(f"crds.diff {hst_data}/synphot_tmttab.rmap {test_temp_dir}/synphot_tmttab.test.rmap")()
    sout, _ = capsys.readouterr()
    exp_out = f"(('{hst_data}/synphot_tmttab.rmap', '{test_temp_dir}/synphot_tmttab.test.rmap'), 'replaced 3241637sm_tmt.fits with tae17277m_tmt.fits')"
    assert ndiffs == 1
    assert exp_out in sout


@mark.hst
@mark.synphot
def test_synphot_refactor_thermal(default_shared_state, hst_data, test_temp_dir, caplog, capsys):
    #THERMAL rmap
    files = f"{hst_data}/synphot_thermal.rmap {test_temp_dir}/synphot_thermal.test.rmap {hst_data}/wfc3_ir_f098m_002_th.fits"
    caplog.clear()
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        refactor.RefactorScript(f"crds.refactor insert {files}")()
        out = caplog.text
    expected = """Inserting wfc3_ir_f098m_002_th.fits into 'hst_synphot_thermal_0002.rmap'
    0 errors"""
    check_logs(expected, out)
    ndiffs = DiffScript(f"crds.diff {hst_data}/synphot_thermal.rmap {test_temp_dir}/synphot_thermal.test.rmap")()
    sout, _ = capsys.readouterr()
    assert ndiffs == 1
    print(sout)
    exp_out1 = f"""(('{hst_data}/synphot_thermal.rmap', '{test_temp_dir}/synphot_thermal.test.rmap'), ('WFC3_IR_F098M', '2006-08-15 08:00:00', 'Filter transmission for F098M'), 'deleted Match rule for wfc3_ir_f098m_002_th.fits')"""
    exp_out2 = f"""(('{hst_data}/synphot_thermal.rmap', '{test_temp_dir}/synphot_thermal.test.rmap'), ('WFC3_IR_F098M', '2019-04-02T15:00:35', 'UPDATED TO CONVERT AIR WAVELENGTHS TO VACUUM.'), 'added Match rule for wfc3_ir_f098m_002_th.fits')"""
    assert [exp in str(sout) for exp in [exp_out1, exp_out2]]


@mark.hst
@mark.synphot
def test_synphot_refactor_thruput(default_shared_state, hst_data, test_temp_dir, caplog, capsys):
    #THRUPUT rmap
    files = f"{hst_data}/synphot_thruput.rmap {test_temp_dir}/synphot_thruput.test.rmap {hst_data}/wfc3_uvis_f469nf2_003_syn.fits"
    caplog.clear()
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        refactor.RefactorScript(f"crds.refactor insert {files}")()
        out = caplog.text
    expected = """Inserting wfc3_uvis_f469nf2_003_syn.fits into 'hst_synphot_thruput_0025.rmap'
    0 errors"""
    check_logs(expected, out)
    ndiffs = DiffScript(f"crds.diff {hst_data}/synphot_thruput.rmap {test_temp_dir}/synphot_thruput.test.rmap")()
    sout, _ = capsys.readouterr()
    assert ndiffs == 1
    print(sout)
    exp_out1 = f"""(('{hst_data}/synphot_thruput.rmap', '{test_temp_dir}/synphot_thruput.test.rmap'), ('WFC3_UVIS_F469NF2', '2016-04-20 20:10:00', 'normalization of f469n flat chip 2---------------------------------'), 'deleted Match rule for wfc3_uvis_f469nf2_003_syn.fits')"""
    exp_out2 = f"""(('{hst_data}/synphot_thruput.rmap', '{test_temp_dir}/synphot_thruput.test.rmap'), ('WFC3_UVIS_F469NF2', '2019-04-02T15:00:44', 'NORMALIZATION OF F469N FLAT CHIP 2---------------------------------'), 'added Match rule for wfc3_uvis_f469nf2_003_syn.fits')"""
    assert [exp in str(sout) for exp in [exp_out1, exp_out2]]


@mark.hst
@mark.synphot
def test_synphot_bestrefs_thermal(default_shared_state, hst_data, caplog):
    r = get_cached_mapping(f"{hst_data}/synphot_thermal.rmap")
    with caplog.at_level(logging.INFO, logger="CRDS"):
        brefs = r.get_best_references({'COMPNAME':'NIC1_F110W', 'CREATED':'NO MATCH', 'DESCRIP':'NO MATCH'})
        out = caplog.text
    assert brefs == {'thermal': 'nic1_f110w_002_th.fits'}
    expected = """Failed checking OMIT for 'synphot' 'thermal' with expr 'true' : name 'true' is not defined
    Failed checking OMIT for 'synphot' 'thermal' with expr 'true' : name 'true' is not defined"""
    check_logs(expected, out)


@mark.hst
@mark.synphot
def test_synphot_bestrefs_thruput(default_shared_state, hst_data, caplog):
    r = get_cached_mapping(f"{hst_data}/synphot_thruput.rmap")
    with caplog.at_level(logging.INFO, logger="CRDS"):
        brefs = r.get_best_references({'COMPNAME':'ACS_BLOCK1', 'CREATED':'NO MATCH', 'DESCRIP':'NO MATCH'})
        out = caplog.text
    assert brefs == {'thruput': 'acs_block1_002_syn.fits'}
    expected = """Failed checking OMIT for 'synphot' 'thruput' with expr 'true' : name 'true' is not defined
    Failed checking OMIT for 'synphot' 'thruput' with expr 'true' : name 'true' is not defined"""
    check_logs(expected, out)


@mark.hst
@mark.synphot
def test_synphot_diff(default_shared_state, hst_data, capsys):
    #TMC   reference
    DiffScript(f"crds.diff {hst_data}/43h1240om_tmc.fits {hst_data}/43h1909cm_tmc.fits")()
    out, _ = capsys.readouterr()
    print(out)
    expected = f"""
 a: {hst_data}/43h1240om_tmc.fits
 b: {hst_data}/43h1909cm_tmc.fits
 Maximum number of different data values to be reported: 10
 Relative tolerance: 0.0, Absolute tolerance: 0.0

Primary HDU:

   Headers contain differences:
     Headers have different number of cards:
      a: 116
      b: 120
     Inconsistent duplicates of keyword 'HISTORY':
      Occurs 106 time(s) in a, 110 times in (b)
     Keyword USEAFTER has different values:
        a> Mar 17 2020 08:40:38
         ?              ^  ----
        b> Mar 17 2020 15:09:14
         ?             +++ ^ +

Extension HDU 1:

   Data contains differences:
     Column COMMENT data differs in row 88:
        a> acs/sbc encircled energy table
        b> encircled energy table for ACS/SBC
     Column FILENAME data differs in row 88:
        a> cracscomp$acs_sbc_aper_003_syn.fits[aper#]
         ?                          ^
        b> cracscomp$acs_sbc_aper_004_syn.fits[aper#]
         ?                          ^
     Column TIME data differs in row 88:
        a> Apr 30 2018 11:10:11
        b> Mar 17 2020 15:09:14
     3 different table data element(s) found (0.03% different).

     HDU extension #1 contains no differences"""
    
    assert expected in out


@mark.hst
@mark.synphot
def test_synphot_core_integration_passing(default_shared_state, caplog):
    # Passing tests
    with caplog.at_level(logging.INFO, logger="CRDS"):
        test = SynphotCoreIntegrationTest("hst_0779.pmap")
        result = test.run()
        out = caplog.text
    assert result is True
    expected = """Checking for components present in TMG COMPNAME but missing from TMC COMPNAME
    Checking for components present in TMC COMPNAME but missing from TMG COMPNAME
    Checking for components present in TMG THCOMPNAME but missing from TMT COMPNAME
    Checking for components present in TMT COMPNAME but missing from TMG THCOMPNAME
    Checking for components present in TMG COMPNAME but missing from throughput table COMPNAME
    Checking for components present in throughput table COMPNAME but missing from TMG COMPNAME
    Checking for components present in TMG THCOMPNAME but missing from thermal table COMPNAME
    Checking for components present in thermal table COMPNAME but missing from TMG THCOMPNAME
    Confirming correctly formed TMC filenames
    Confirming correctly formed TMT filenames"""
    check_logs(expected, out)


@mark.hst
@mark.synphot
def test_synphot_core_integration_missing_from_files(default_shared_state, hst_data, caplog):
    """Components present in graph but missing from lookup/component files"""
    with caplog.at_level(logging.INFO, logger="CRDS"):
        test = SynphotCoreIntegrationTest(
            "hst_0779.pmap",
            graph_file=f"{hst_data}/hst_synphot_extra_tmg.fits"
        )
        result = test.run()
        out = caplog.text
    assert result is False
    expected = """Checking for components present in TMG COMPNAME but missing from TMC COMPNAME
    Components present in TMG COMPNAME but missing from TMC COMPNAME: xtra_thruput_comp
    Checking for components present in TMC COMPNAME but missing from TMG COMPNAME
    Checking for components present in TMG THCOMPNAME but missing from TMT COMPNAME
    Components present in TMG THCOMPNAME but missing from TMT COMPNAME: xtra_thermal_comp
    Checking for components present in TMT COMPNAME but missing from TMG THCOMPNAME
    Checking for components present in TMG COMPNAME but missing from throughput table COMPNAME
    Components present in TMG COMPNAME but missing from throughput table COMPNAME: xtra_thruput_comp
    Checking for components present in throughput table COMPNAME but missing from TMG COMPNAME
    Checking for components present in TMG THCOMPNAME but missing from thermal table COMPNAME
    Components present in TMG THCOMPNAME but missing from thermal table COMPNAME: xtra_thermal_comp
    Checking for components present in thermal table COMPNAME but missing from TMG THCOMPNAME
    Confirming correctly formed TMC filenames
    Confirming correctly formed TMT filenames"""
    check_logs(expected, out)


@mark.hst
@mark.synphot
def test_synphot_core_integration_missing_from_graph(default_shared_state, hst_data, caplog):
    """Components missing from graph but present in lookup/component files"""
    with caplog.at_level(logging.INFO, logger="CRDS"):
        test = SynphotCoreIntegrationTest(
            "hst_0779.pmap",
            graph_file=f"{hst_data}/hst_synphot_missing_tmg.fits"
        )
        result = test.run()
        out = caplog.text
    assert result is False
    expected = """Checking for components present in TMG COMPNAME but missing from TMC COMPNAME
    Checking for components present in TMC COMPNAME but missing from TMG COMPNAME
    Components present in TMC COMPNAME but missing from TMG COMPNAME: wfirst_wfi_prism
    Checking for components present in TMG THCOMPNAME but missing from TMT COMPNAME
    Checking for components present in TMT COMPNAME but missing from TMG THCOMPNAME
    Checking for components present in TMG COMPNAME but missing from throughput table COMPNAME
    Checking for components present in throughput table COMPNAME but missing from TMG COMPNAME
    Components present in throughput table COMPNAME but missing from TMG COMPNAME: wfirst_wfi_prism
    Checking for components present in TMG THCOMPNAME but missing from thermal table COMPNAME
    Checking for components present in thermal table COMPNAME but missing from TMG THCOMPNAME
    Confirming correctly formed TMC filenames
    Confirming correctly formed TMT filenames"""
    check_logs(expected, out)


@mark.hst
@mark.synphot
def test_synphot_core_integration_invalid_fname_thruput(default_shared_state, hst_data, caplog):
    """Invalid filename in throughput lookup table"""
    with caplog.at_level(logging.INFO, logger="CRDS"):
        test = SynphotCoreIntegrationTest(
            "hst_0779.pmap",
            throughput_lookup_file=f"{hst_data}/hst_synphot_malformed_filename_tmc.fits"
        )
        result = test.run()
        out = caplog.text
    assert result is False
    expected = """Checking for components present in TMG COMPNAME but missing from TMC COMPNAME
    Checking for components present in TMC COMPNAME but missing from TMG COMPNAME
    Checking for components present in TMG THCOMPNAME but missing from TMT COMPNAME
    Checking for components present in TMT COMPNAME but missing from TMG THCOMPNAME
    Checking for components present in TMG COMPNAME but missing from throughput table COMPNAME
    Checking for components present in throughput table COMPNAME but missing from TMG COMPNAME
    Checking for components present in TMG THCOMPNAME but missing from thermal table COMPNAME
    Checking for components present in thermal table COMPNAME but missing from TMG THCOMPNAME
    Confirming correctly formed TMC filenames
    Malformed TMC filename, expected 'crwfpccomp$wfpc_pol60_003_syn.fits', found 'crwfpccomp$wfpc_foo_003_syn.fits'
    Confirming correctly formed TMT filenames"""
    check_logs(expected, out)
    

@mark.hst
@mark.synphot
def test_synphot_core_integration_invalid_fname_thermal(default_shared_state, hst_data, caplog):
    """Invalid filename in thermal lookup table"""
    with caplog.at_level(logging.INFO, logger="CRDS"):
        test = SynphotCoreIntegrationTest(
            "hst_0779.pmap",
            thermal_lookup_file=f"{hst_data}/hst_synphot_malformed_filename_tmt.fits"
        )
        result = test.run()
        out = caplog.text
    assert result is False
    expected = """Checking for components present in TMG COMPNAME but missing from TMC COMPNAME
    Checking for components present in TMC COMPNAME but missing from TMG COMPNAME
    Checking for components present in TMG THCOMPNAME but missing from TMT COMPNAME
    Checking for components present in TMT COMPNAME but missing from TMG THCOMPNAME
    Checking for components present in TMG COMPNAME but missing from throughput table COMPNAME
    Checking for components present in throughput table COMPNAME but missing from TMG COMPNAME
    Checking for components present in TMG THCOMPNAME but missing from thermal table COMPNAME
    Checking for components present in thermal table COMPNAME but missing from TMG THCOMPNAME
    Confirming correctly formed TMC filenames
    Confirming correctly formed TMT filenames
    Malformed TMT filename, expected 'crwfc3comp$wfc3_ir_f167n_002_th.fits', found 'crwfc3comp$wfc3_ir_foo_002_th.fits'"""
    check_logs(expected, out)


@mark.hst
@mark.synphot
def test_synphot_obsmodes_integration_test(default_shared_state, hst_data, caplog):
    with caplog.at_level(logging.INFO, logger="CRDS"):
        test = SynphotObsmodeIntegrationTest(
            "hst_0779.pmap",
            f"{hst_data}/synphot_root",
            f"{hst_data}/hst_synphot_passing_obs.fits"
        )
        result = test.run()
        out = caplog.text
    assert result is True
    expected = """Creating bandpass objects from 1 observation modes
    Congratulations, all observation modes succeeded!"""
    check_logs(expected, out)


@mark.hst
@mark.synphot
def test_synphot_obsmodes_integration_test_multiproc(default_shared_state, hst_data, caplog):
    """Passing tests in multiprocessing mode"""
    with caplog.at_level(logging.INFO, logger="CRDS"):
        test = SynphotObsmodeIntegrationTest(
            "hst_0779.pmap",
            f"{hst_data}/synphot_root",
            f"{hst_data}/hst_synphot_passing_obs.fits",
            processes=4
        )
        result = test.run()
        out = caplog.text
    assert result is True
    expected = """Creating bandpass objects from 1 observation modes
    Congratulations, all observation modes succeeded!"""
    check_logs(expected, out)


@mark.hst
@mark.synphot
def test_synphot_obsmodes_integration_test_missing_files(default_shared_state, hst_data, caplog):
    """Failure due to missing component files"""
    with caplog.at_level(logging.INFO, logger="CRDS"):
        test = SynphotObsmodeIntegrationTest(
            "hst_0779.pmap",
            f"{hst_data}/synphot_root",
            obsmodes_file=f"{hst_data}/hst_synphot_failing_obs.fits",
        )
        result = test.run()
        out = caplog.text
    assert result is False
    expected = """Creating bandpass objects from 1 observation modes
    Exception from pysynphot with obsmode 'acs,hrc,coron': FileNotFoundError(2, 'No such file or directory')
    1 / 1 observation modes failed"""
    check_logs(expected, out)


@mark.hst
@mark.synphot
def test_synphot_obsmodes_integration_multiproc_fail(default_shared_state, hst_data, caplog):
    """Failure in multiprocessing mode"""
    with caplog.at_level(logging.INFO, logger="CRDS"):
        test = SynphotObsmodeIntegrationTest(
            "hst_0779.pmap",
            f"{hst_data}/synphot_root",
            obsmodes_file=f"{hst_data}/hst_synphot_failing_obs.fits",
            processes=4,
        )
        result = test.run()
        out = caplog.text
    assert result is False
    expected = """Creating bandpass objects from 1 observation modes
    Exception from pysynphot with obsmode 'acs,hrc,coron': FileNotFoundError(2, 'No such file or directory')
    1 / 1 observation modes failed"""
    check_logs(expected, out)


@mark.hst
@mark.synphot
class TestSynphotLookupGenerator:

    generator = SynphotLookupGenerator("hst_0779.pmap")

    @fixture(autouse=True)
    def _get_data(self, hst_data):
        self._dpath = hst_data

    def test_throughput_lookup_generation(self):
        original_hdul = self.generator.generate("tmctab", [])
        original_tmc = original_hdul[-1].data
        original_row = original_tmc[original_tmc["COMPNAME"] == "wfpc_pol60"][0]
        assert original_row["FILENAME"] == "crwfpccomp$wfpc_pol60_003_syn.fits"

        new_hdul = self.generator.generate("tmctab", [f"{self._dpath}/hst_synphot_new_syn.fits"])
        new_tmc = new_hdul[-1].data
        new_row = new_tmc[new_tmc["COMPNAME"] == "wfpc_pol60"][0]
        assert new_row["FILENAME"] == "crwfpccomp$hst_synphot_new_syn.fits"

    def test_thermal_lookup_generation(self):
        original_hdul = self.generator.generate("tmttab", [])
        original_tmt = original_hdul[-1].data
        original_row = original_tmt[original_tmt["COMPNAME"] == "wfc3_ir_f167n"][0]
        assert original_row["FILENAME"] == "crwfc3comp$wfc3_ir_f167n_002_th.fits"

        new_hdul = self.generator.generate("tmttab", [f"{self._dpath}/hst_synphot_new_th.fits"])
        new_tmt = new_hdul[-1].data
        new_row = new_tmt[new_tmt["COMPNAME"] == "wfc3_ir_f167n"][0]
        assert new_row["FILENAME"] == "crwfc3comp$hst_synphot_new_th.fits"
