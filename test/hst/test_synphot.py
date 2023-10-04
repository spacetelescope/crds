"""This module tests the synphot pseudo-instrument support for HST."""
from pytest import mark
import logging
from crds.core import config as crds_config
from crds.core import log, naming, timestamp
from crds.hst import locate as hst_locate
from crds.refactoring import refactor
from crds.certify import CertifyScript


log.THE_LOGGER.logger.propagate = True

@mark.synphot
def test_synphot_naming(default_shared_state, hst_data):
    NOW = timestamp.parse_date("2018-11-14T00:00:00")

    # THERMAL
    assert crds_config.is_crds_name("wfc3_ir_f098m_002_th.fits") is False
    assert crds_config.is_cdbs_name("wfc3_ir_f098m_002_th.fits") is True
    assert crds_config.is_reference("wfc3_ir_f098m_002_th.fits") is True
    assert crds_config.is_mapping("wfc3_ir_f098m_002_th.fits") is False
    props = hst_locate.get_file_properties("wfc3_ir_f098m_002_th.fits")
    assert props == ('synphot', 'thermal')
    props = hst_locate.ref_properties_from_cdbs_path(f"{hst_data}/wfc3_ir_f098m_002_th.fits")
    assert props == ('data', 'hst', 'synphot', 'thermal', 'wfc3_ir_f098m_002_th', '.fits')
    props = hst_locate.ref_properties_from_header(f"{hst_data}/wfc3_ir_f098m_002_th.fits")
    assert props == ('data', 'hst', 'synphot', 'thermal', 'wfc3_ir_f098m_002_th', '.fits')
    name = naming.generate_unique_name("wfc3_ir_f098m_002_th.fits", "hst", NOW)
    assert name == '2be00000m_th.fits'

    # THRUPUT

    assert crds_config.is_crds_name("wfc3_uvis_f469nf2_003_syn.fits") is False
    assert crds_config.is_cdbs_name("wfc3_uvis_f469nf2_003_syn.fits") is True
    assert crds_config.is_reference("wfc3_uvis_f469nf2_003_syn.fits") is True
    assert crds_config.is_mapping("wfc3_uvis_f469nf2_003_syn.fits") is False
    props = hst_locate.get_file_properties("wfc3_uvis_f469nf2_003_syn.fits")
    assert props == ('synphot', 'thruput')
    props = hst_locate.ref_properties_from_cdbs_path(f"{hst_data}/wfc3_uvis_f469nf2_003_syn.fits")
    assert props == ('data', 'hst', 'synphot', 'thruput', 'wfc3_uvis_f469nf2_003_syn', '.fits')
    props = hst_locate.ref_properties_from_header(f"{hst_data}/wfc3_uvis_f469nf2_003_syn.fits")
    assert props == ('data', 'hst', 'synphot', 'thruput', 'wfc3_uvis_f469nf2_003_syn', '.fits')
    name = naming.generate_unique_name("wfc3_uvis_f469nf2_003_syn.fits", "hst", NOW)
    assert name == '2be00000m_syn.fits'

    # TMGTAB

    assert crds_config.is_crds_name("2381905mm_tmg.fits") is False
    assert crds_config.is_cdbs_name("2381905mm_tmg.fits") is True
    assert crds_config.is_reference("2381905mm_tmg.fits") is True
    assert crds_config.is_mapping("2381905mm_tmg.fits") is False
    props = hst_locate.get_file_properties("2381905mm_tmg.fits")
    assert props == ('synphot', 'tmgtab')
    props = hst_locate.ref_properties_from_cdbs_path(f"{hst_data}/2381905mm_tmg.fits")
    assert props == ('data', 'hst', 'synphot', 'tmgtab', '2381905mm_tmg', '.fits')
    props = hst_locate.ref_properties_from_header(f"{hst_data}/2381905mm_tmg.fits")
    assert props == ('data', 'hst', 'synphot', 'tmgtab', '2381905mm_tmg', '.fits')
    name = naming.generate_unique_name("2381905mm_tmg.fits", "hst", NOW)
    assert name == '2be00000m_tmg.fits'

    # TMCTAB

    assert crds_config.is_crds_name("43h1909cm_tmc.fits") is False
    assert crds_config.is_cdbs_name("43h1909cm_tmc.fits") is True
    assert crds_config.is_reference("43h1909cm_tmc.fits") is True
    assert crds_config.is_mapping("43h1909cm_tmc.fits") is False
    props = hst_locate.get_file_properties("43h1909cm_tmc.fits")
    assert props == ('synphot', 'tmctab')
    props = hst_locate.ref_properties_from_cdbs_path("data/43h1909cm_tmc.fits")
    assert props == ('data', 'hst', 'synphot', 'tmctab', '43h1909cm_tmc', '.fits')
    props = hst_locate.ref_properties_from_header("data/43h1909cm_tmc.fits")
    assert props == ('data', 'hst', 'synphot', 'tmctab', '43h1909cm_tmc', '.fits')
    name = naming.generate_unique_name("43h1909cm_tmc.fits", "hst", NOW)
    assert name == '2be00000m_tmc.fits'

    # TMTTAB

    assert crds_config.is_crds_name("tae17277m_tmt.fits") is False
    assert crds_config.is_cdbs_name("tae17277m_tmt.fits") is True
    assert crds_config.is_reference("tae17277m_tmt.fits") is True
    assert crds_config.is_mapping("tae17277m_tmt.fits") is False
    props = hst_locate.get_file_properties("tae17277m_tmt.fits")
    assert props == ('synphot', 'tmttab')
    props = hst_locate.ref_properties_from_header("data/tae17277m_tmt.fits")
    assert props == ('data', 'hst', 'synphot', 'tmttab', 'tae17277m_tmt', '.fits')
    props = hst_locate.ref_properties_from_cdbs_path("data/tae17277m_tmt.fits")
    assert props == ('data', 'hst', 'synphot', 'tmttab', 'tae17277m_tmt', '.fits')
    name = naming.generate_unique_name("tae17277m_tmt.fits", "hst", NOW)
    assert name == '2be00000m_tmt.fits'


@mark.synphot
def test_synphot_certify_refs(default_shared_state, hst_data, caplog):
    # TMC   reference
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(f"crds.certify  --run-fitsverify {hst_data}/43h1909cm_tmc.fits --comparison-context hst_0772.pmap")()
        out = caplog.text
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
    0 errors""".splitlines()
    for msg in expected1:
        assert msg.strip() in out

    caplog.clear()
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(f"crds.certify  --run-fitsverify {hst_data}/2381905mm_tmg.fits --comparison-context hst_0691.pmap")()
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
    0 errors""".splitlines()
    for msg in expected2:
        assert msg.strip() in out2


    # TMT   reference
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript("crds.certify  --run-fitsverify data/tae17277m_tmt.fits --comparison-context hst_0691.pmap")()
        out3 = caplog.text
    expected3 = f"""Certifying '{hst_data}/tae17277m_tmt.fits' (1/1) as 'FITS' relative to context 'hst_0691.pmap'
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
    1 errors""".splitlines()
    for msg in expected3:
        assert msg.strip() in out3

    #THERMAL reference
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(f"crds.certify  --run-fitsverify {hst_data}/wfc3_ir_f098m_002_th.fits --comparison-context hst_0691.pmap")()
        out4 = caplog.text
    expected4 = f"""Certifying '{hst_data}/wfc3_ir_f098m_002_th.fits' (1/1) as 'FITS' relative to context 'hst_0691.pmap'
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
    1 errors""".splitlines()
    for msg in expected4:
        assert msg.strip() in out4

    # THRUPUT reference
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(f"crds.certify  --run-fitsverify {hst_data}/wfc3_uvis_f469nf2_003_syn.fits --comparison-context hst_0691.pmap")()
        out5 = caplog.text
    
    expected5 = f"""Certifying '{hst_data}/wfc3_uvis_f469nf2_003_syn.fits' (1/1) as 'FITS' relative to context 'hst_0691.pmap'
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
    1 errors""".splitlines()
    for msg in expected5:
        assert msg.strip() in out5


@mark.synphot
def test_synphot_certify_rmaps(default_shared_state, hst_data, caplog):
    # TMC   rmap
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(f"crds.certify {hst_data}/synphot_tmctab.rmap --comparison-context hst_0857.pmap")()
        out = caplog.text
       
    expected = f"""Certifying '{hst_data}/synphot_tmctab.rmap' (1/1) as 'MAPPING' relative to context 'hst_0857.pmap'
    Mapping 'synphot_tmctab.rmap' corresponds to 'hst_synphot_tmctab_0021.rmap' from context 'hst_0857.pmap' for checking mapping differences.
    Checking diffs from 'hst_synphot_tmctab_0021.rmap' to 'synphot_tmctab.rmap'
    0 errors""".splitlines()
    for msg in expected:
        assert msg.strip() in out

    # TMG   rmap
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript("crds.certify data/synphot_tmgtab.rmap --comparison-context hst_0857.pmap")()
        out2 = caplog.text
    expected2 = f"""Certifying '{hst_data}/synphot_tmgtab.rmap' (1/1) as 'MAPPING' relative to context 'hst_0857.pmap'
    Mapping 'synphot_tmgtab.rmap' corresponds to 'hst_synphot_tmgtab_0007.rmap' from context 'hst_0857.pmap' for checking mapping differences.
    Checking diffs from 'hst_synphot_tmgtab_0007.rmap' to 'synphot_tmgtab.rmap'
    0 errors""".splitlines()
    for msg in expected2:
        assert msg.strip() in out2

    #TMT   rmap
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(f"crds.certify {hst_data}/synphot_tmttab.rmap --comparison-context hst_0857.pmap")()
        out3 = caplog.text
    expected3 = f"""Certifying '{hst_data}/synphot_tmttab.rmap' (1/1) as 'MAPPING' relative to context 'hst_0857.pmap'
    Mapping 'synphot_tmttab.rmap' corresponds to 'hst_synphot_tmttab_0001.rmap' from context 'hst_0857.pmap' for checking mapping differences.
    Checking diffs from 'hst_synphot_tmttab_0001.rmap' to 'synphot_tmttab.rmap'
    0 errors""".splitlines()
    for msg in expected3:
        assert msg.strip() in out3

    # THERMAL rmap
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(f"crds.certify {hst_data}/synphot_thermal.rmap --comparison-context hst_0857.pmap")()
        out4 = caplog.text
    expected4 = f"""Certifying '{hst_data}/synphot_thermal.rmap' (1/1) as 'MAPPING' relative to context 'hst_0857.pmap'
    Mapping 'synphot_thermal.rmap' corresponds to 'hst_synphot_thermal_0002.rmap' from context 'hst_0857.pmap' for checking mapping differences.
    Checking diffs from 'hst_synphot_thermal_0002.rmap' to 'synphot_thermal.rmap'
    0 errors""".splitlines()
    for msg in expected4:
        assert msg.strip() in out4

    #THRUPUT rmap
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(f"crds.certify {hst_data}/synphot_thruput.rmap --comparison-context hst_0857.pmap")()
        out5 = caplog.text
    expected5 = f"""Certifying '{hst_data}/synphot_thruput.rmap' (1/1) as 'MAPPING' relative to context 'hst_0857.pmap'
    Mapping 'synphot_thruput.rmap' corresponds to 'hst_synphot_thruput_0025.rmap' from context 'hst_0857.pmap' for checking mapping differences.
    Checking diffs from 'hst_synphot_thruput_0025.rmap' to 'synphot_thruput.rmap'
    0 errors""".splitlines()
    for msg in expected5:
        assert msg.strip() in out5


def dt_synphot_refactor():
    """
    >>> old_state = test_config.setup()

    >>> r = crds.get_cached_mapping("data/synphot_thermal.rmap")
    >>> header = dict(COMPNAME="NIC1_BEND", CREATED="2002-03-06 04:51:00",  DESCRIP="Use NIC2 values")

    >>> v = log.set_verbose(55)

    For classic irrelevant parkey matching where values are normalized to N/A and ignored

    >>> print(log.PP(r.map_irrelevant_parkeys_to_na(header)))
    CRDS - DEBUG -  Parkey synphot thermal date is relevant: False 'keep_comments'
    CRDS - DEBUG -  Setting irrelevant parkey 'DATE' to N/A
    CRDS - DEBUG -  Parkey synphot thermal descrip is relevant: False 'keep_comments'
    CRDS - DEBUG -  Setting irrelevant parkey 'DESCRIP' to N/A
    {'COMPNAME': 'NIC1_BEND',
     'CREATED': '2002-03-06 04:51:00',
     'DATE': 'N/A',
     'DESCRIP': 'N/A'}

    For rmap updates which add comment keywords to the match tuples for web display

    >>> print(log.PP(r.map_irrelevant_parkeys_to_na(header, keep_comments=True)))
    CRDS - DEBUG -  Parkey synphot thermal date is relevant: True 'keep_comments'
    CRDS - DEBUG -  Parkey synphot thermal descrip is relevant: True 'keep_comments'
    {'COMPNAME': 'NIC1_BEND',
     'CREATED': '2002-03-06 04:51:00',
     'DESCRIP': 'Use NIC2 values'}

    >>> _ = log.set_verbose(v)

    TMC   rmap

    >>> refactor.RefactorScript("crds.refactor insert data/synphot_tmctab.rmap /tmp/synphot_tmctab.test.rmap data/43h1909cm_tmc.fits")()
    CRDS - INFO -  Inserting 43h1909cm_tmc.fits into 'hst_synphot_tmctab_0021.rmap'
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  1 infos
    0

    >>> diff.DiffScript("crds.diff  data/synphot_tmctab.rmap /tmp/synphot_tmctab.test.rmap")()
    (('data/synphot_tmctab.rmap', '/tmp/synphot_tmctab.test.rmap'), 'replaced 5182153pm_tmc.fits with 43h1909cm_tmc.fits')
    1

    TMG   rmap

    >>> refactor.RefactorScript("crds.refactor insert data/synphot_tmgtab.rmap /tmp/synphot_tmgtab.test.rmap data/2381905mm_tmg.fits")()
    CRDS - INFO -  Inserting 2381905mm_tmg.fits into 'hst_synphot_tmgtab_0007.rmap'
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  1 infos
    0

    >>> diff.DiffScript("crds.diff  data/synphot_tmgtab.rmap /tmp/synphot_tmgtab.test.rmap")()
    (('data/synphot_tmgtab.rmap', '/tmp/synphot_tmgtab.test.rmap'), 'replaced 4cm1612bm_tmg.fits with 2381905mm_tmg.fits')
    1

    TMT   rmap

    >>> refactor.RefactorScript("crds.refactor insert data/synphot_tmttab.rmap /tmp/synphot_tmttab.test.rmap data/tae17277m_tmt.fits")()
    CRDS - INFO -  Inserting tae17277m_tmt.fits into 'hst_synphot_tmttab_0001.rmap'
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  1 infos
    0

    >>> diff.DiffScript("crds.diff  data/synphot_tmttab.rmap /tmp/synphot_tmttab.test.rmap")()
    (('data/synphot_tmttab.rmap', '/tmp/synphot_tmttab.test.rmap'), 'replaced 3241637sm_tmt.fits with tae17277m_tmt.fits')
    1

    THERMAL rmap

    >>> refactor.RefactorScript("crds.refactor insert data/synphot_thermal.rmap /tmp/synphot_thermal.test.rmap data/wfc3_ir_f098m_002_th.fits")()
    CRDS - INFO -  Inserting wfc3_ir_f098m_002_th.fits into 'hst_synphot_thermal_0002.rmap'
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  1 infos
    0

    >>> diff.DiffScript("crds.diff  data/synphot_thermal.rmap /tmp/synphot_thermal.test.rmap")()
    (('data/synphot_thermal.rmap', '/tmp/synphot_thermal.test.rmap'), ('WFC3_IR_F098M', '2006-08-15 08:00:00', 'Filter transmission for F098M'), 'deleted Match rule for wfc3_ir_f098m_002_th.fits')
    (('data/synphot_thermal.rmap', '/tmp/synphot_thermal.test.rmap'), ('WFC3_IR_F098M', '2019-04-02T15:00:35', 'UPDATED TO CONVERT AIR WAVELENGTHS TO VACUUM.'), 'added Match rule for wfc3_ir_f098m_002_th.fits')
    1

    THRUPUT rmap

    >>> refactor.RefactorScript("crds.refactor insert data/synphot_thruput.rmap /tmp/synphot_thruput.test.rmap data/wfc3_uvis_f469nf2_003_syn.fits")()
    CRDS - INFO -  Inserting wfc3_uvis_f469nf2_003_syn.fits into 'hst_synphot_thruput_0025.rmap'
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  1 infos
    0

    >>> diff.DiffScript("crds.diff  data/synphot_thruput.rmap /tmp/synphot_thruput.test.rmap")()
    (('data/synphot_thruput.rmap', '/tmp/synphot_thruput.test.rmap'), ('WFC3_UVIS_F469NF2', '2016-04-20 20:10:00', 'normalization of f469n flat chip 2---------------------------------'), 'deleted Match rule for wfc3_uvis_f469nf2_003_syn.fits')
    (('data/synphot_thruput.rmap', '/tmp/synphot_thruput.test.rmap'), ('WFC3_UVIS_F469NF2', '2019-04-02T15:00:44', 'NORMALIZATION OF F469N FLAT CHIP 2---------------------------------'), 'added Match rule for wfc3_uvis_f469nf2_003_syn.fits')
    1

    >>> test_config.cleanup(old_state)
    """

def dt_synphot_bestrefs():
    """
    >>> old_state = test_config.setup()

    >>> r = crds.get_cached_mapping("data/synphot_thermal.rmap")
    >>> r.get_best_references({'COMPNAME':'NIC1_F110W', 'CREATED':'NO MATCH', 'DESCRIP':'NO MATCH'})
    CRDS - WARNING -  Failed checking OMIT for 'synphot' 'thermal' with expr 'true' : name 'true' is not defined
    CRDS - WARNING -  Failed checking OMIT for 'synphot' 'thermal' with expr 'true' : name 'true' is not defined
    {'thermal': 'nic1_f110w_002_th.fits'}

    >>> r = crds.get_cached_mapping("data/synphot_thruput.rmap")
    >>> r.get_best_references({'COMPNAME':'ACS_BLOCK1', 'CREATED':'NO MATCH', 'DESCRIP':'NO MATCH'})
    CRDS - WARNING -  Failed checking OMIT for 'synphot' 'thruput' with expr 'true' : name 'true' is not defined
    CRDS - WARNING -  Failed checking OMIT for 'synphot' 'thruput' with expr 'true' : name 'true' is not defined
    {'thruput': 'acs_block1_002_syn.fits'}

    >>> test_config.cleanup(old_state)
    """


def dt_synphot_diff():
    """
    >>> old_state = test_config.setup()

    TMC   reference

    >>> diff.DiffScript("crds.diff data/43h1240om_tmc.fits data/43h1909cm_tmc.fits")()   # doctest: +ELLIPSIS
    <BLANKLINE>
     fitsdiff: ...
     a: data/43h1240om_tmc.fits
     b: data/43h1909cm_tmc.fits
     Maximum number of different data values to be reported: 10
     Relative tolerance: 0.0, Absolute tolerance: 0.0
    <BLANKLINE>
    Primary HDU:
    <BLANKLINE>
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
    <BLANKLINE>
    Extension HDU 1:
    <BLANKLINE>
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
    <BLANKLINE>
         HDU extension #1 contains no differences
    ...

    >>> test_config.cleanup(old_state)
    """

def dt_synphot_core_integration_test():
    """
    >>> old_state = test_config.setup()
    >>> from crds.misc.synphot import SynphotCoreIntegrationTest

    Passing tests

    >>> test = SynphotCoreIntegrationTest("hst_0779.pmap")
    >>> test.run()
    CRDS - INFO -  Checking for components present in TMG COMPNAME but missing from TMC COMPNAME
    CRDS - INFO -  Checking for components present in TMC COMPNAME but missing from TMG COMPNAME
    CRDS - INFO -  Checking for components present in TMG THCOMPNAME but missing from TMT COMPNAME
    CRDS - INFO -  Checking for components present in TMT COMPNAME but missing from TMG THCOMPNAME
    CRDS - INFO -  Checking for components present in TMG COMPNAME but missing from throughput table COMPNAME
    CRDS - INFO -  Checking for components present in throughput table COMPNAME but missing from TMG COMPNAME
    CRDS - INFO -  Checking for components present in TMG THCOMPNAME but missing from thermal table COMPNAME
    CRDS - INFO -  Checking for components present in thermal table COMPNAME but missing from TMG THCOMPNAME
    CRDS - INFO -  Confirming correctly formed TMC filenames
    CRDS - INFO -  Confirming correctly formed TMT filenames
    True

    Components present in graph but missing from lookup/component files

    >>> test = SynphotCoreIntegrationTest("hst_0779.pmap", graph_file="data/hst_synphot_extra_tmg.fits")
    >>> test.run()
    CRDS - INFO -  Checking for components present in TMG COMPNAME but missing from TMC COMPNAME
    CRDS - ERROR -  Components present in TMG COMPNAME but missing from TMC COMPNAME: xtra_thruput_comp
    CRDS - INFO -  Checking for components present in TMC COMPNAME but missing from TMG COMPNAME
    CRDS - INFO -  Checking for components present in TMG THCOMPNAME but missing from TMT COMPNAME
    CRDS - ERROR -  Components present in TMG THCOMPNAME but missing from TMT COMPNAME: xtra_thermal_comp
    CRDS - INFO -  Checking for components present in TMT COMPNAME but missing from TMG THCOMPNAME
    CRDS - INFO -  Checking for components present in TMG COMPNAME but missing from throughput table COMPNAME
    CRDS - ERROR -  Components present in TMG COMPNAME but missing from throughput table COMPNAME: xtra_thruput_comp
    CRDS - INFO -  Checking for components present in throughput table COMPNAME but missing from TMG COMPNAME
    CRDS - INFO -  Checking for components present in TMG THCOMPNAME but missing from thermal table COMPNAME
    CRDS - ERROR -  Components present in TMG THCOMPNAME but missing from thermal table COMPNAME: xtra_thermal_comp
    CRDS - INFO -  Checking for components present in thermal table COMPNAME but missing from TMG THCOMPNAME
    CRDS - INFO -  Confirming correctly formed TMC filenames
    CRDS - INFO -  Confirming correctly formed TMT filenames
    False

    Components missing from graph but present in lookup/component files

    >>> test = SynphotCoreIntegrationTest("hst_0779.pmap", graph_file="data/hst_synphot_missing_tmg.fits")
    >>> test.run()
    CRDS - INFO -  Checking for components present in TMG COMPNAME but missing from TMC COMPNAME
    CRDS - INFO -  Checking for components present in TMC COMPNAME but missing from TMG COMPNAME
    CRDS - ERROR -  Components present in TMC COMPNAME but missing from TMG COMPNAME: wfirst_wfi_prism
    CRDS - INFO -  Checking for components present in TMG THCOMPNAME but missing from TMT COMPNAME
    CRDS - INFO -  Checking for components present in TMT COMPNAME but missing from TMG THCOMPNAME
    CRDS - INFO -  Checking for components present in TMG COMPNAME but missing from throughput table COMPNAME
    CRDS - INFO -  Checking for components present in throughput table COMPNAME but missing from TMG COMPNAME
    CRDS - ERROR -  Components present in throughput table COMPNAME but missing from TMG COMPNAME: wfirst_wfi_prism
    CRDS - INFO -  Checking for components present in TMG THCOMPNAME but missing from thermal table COMPNAME
    CRDS - INFO -  Checking for components present in thermal table COMPNAME but missing from TMG THCOMPNAME
    CRDS - INFO -  Confirming correctly formed TMC filenames
    CRDS - INFO -  Confirming correctly formed TMT filenames
    False

    Invalid filename in throughput lookup table

    >>> test = SynphotCoreIntegrationTest("hst_0779.pmap", throughput_lookup_file="data/hst_synphot_malformed_filename_tmc.fits")
    >>> test.run()
    CRDS - INFO -  Checking for components present in TMG COMPNAME but missing from TMC COMPNAME
    CRDS - INFO -  Checking for components present in TMC COMPNAME but missing from TMG COMPNAME
    CRDS - INFO -  Checking for components present in TMG THCOMPNAME but missing from TMT COMPNAME
    CRDS - INFO -  Checking for components present in TMT COMPNAME but missing from TMG THCOMPNAME
    CRDS - INFO -  Checking for components present in TMG COMPNAME but missing from throughput table COMPNAME
    CRDS - INFO -  Checking for components present in throughput table COMPNAME but missing from TMG COMPNAME
    CRDS - INFO -  Checking for components present in TMG THCOMPNAME but missing from thermal table COMPNAME
    CRDS - INFO -  Checking for components present in thermal table COMPNAME but missing from TMG THCOMPNAME
    CRDS - INFO -  Confirming correctly formed TMC filenames
    CRDS - ERROR -  Malformed TMC filename, expected 'crwfpccomp$wfpc_pol60_003_syn.fits', found 'crwfpccomp$wfpc_foo_003_syn.fits'
    CRDS - INFO -  Confirming correctly formed TMT filenames
    False

    Invalid filename in thermal lookup table

    >>> test = SynphotCoreIntegrationTest("hst_0779.pmap", thermal_lookup_file="data/hst_synphot_malformed_filename_tmt.fits")
    >>> test.run()
    CRDS - INFO -  Checking for components present in TMG COMPNAME but missing from TMC COMPNAME
    CRDS - INFO -  Checking for components present in TMC COMPNAME but missing from TMG COMPNAME
    CRDS - INFO -  Checking for components present in TMG THCOMPNAME but missing from TMT COMPNAME
    CRDS - INFO -  Checking for components present in TMT COMPNAME but missing from TMG THCOMPNAME
    CRDS - INFO -  Checking for components present in TMG COMPNAME but missing from throughput table COMPNAME
    CRDS - INFO -  Checking for components present in throughput table COMPNAME but missing from TMG COMPNAME
    CRDS - INFO -  Checking for components present in TMG THCOMPNAME but missing from thermal table COMPNAME
    CRDS - INFO -  Checking for components present in thermal table COMPNAME but missing from TMG THCOMPNAME
    CRDS - INFO -  Confirming correctly formed TMC filenames
    CRDS - INFO -  Confirming correctly formed TMT filenames
    CRDS - ERROR -  Malformed TMT filename, expected 'crwfc3comp$wfc3_ir_f167n_002_th.fits', found 'crwfc3comp$wfc3_ir_foo_002_th.fits'
    False
    """

def dt_synphot_obsmodes_integration_test():
    """
    >>> old_state = test_config.setup()
    >>> from crds.misc.synphot import SynphotObsmodeIntegrationTest

    Passing tests

    >>> test = SynphotObsmodeIntegrationTest(
    ... "hst_0779.pmap",
    ... "data/synphot_root",
    ... "data/hst_synphot_passing_obs.fits"
    ... )
    >>> test.run()
    CRDS - INFO -  Creating bandpass objects from 1 observation modes
    CRDS - INFO -  Congratulations, all observation modes succeeded!
    True

    Passing tests in multiprocessing mode

    >>> test = SynphotObsmodeIntegrationTest(
    ... "hst_0779.pmap",
    ... "data/synphot_root",
    ... "data/hst_synphot_passing_obs.fits",
    ... processes=4
    ... )
    >>> test.run()
    CRDS - INFO -  Creating bandpass objects from 1 observation modes
    CRDS - INFO -  Congratulations, all observation modes succeeded!
    True

    Failure due to missing component files

    >>> test = SynphotObsmodeIntegrationTest(
    ... "hst_0779.pmap",
    ... "data/synphot_root",
    ... obsmodes_file="data/hst_synphot_failing_obs.fits"
    ... )
    >>> test.run()
    CRDS - INFO -  Creating bandpass objects from 1 observation modes
    CRDS - ERROR -  Exception from stsynphot with obsmode 'acs,hrc,coron': UnboundLocalError("local variable 'fs' referenced before assignment")
    CRDS - ERROR -  Exception from pysynphot with obsmode 'acs,hrc,coron': FileNotFoundError(2, 'No such file or directory')
    CRDS - INFO -  1 / 1 observation modes failed
    False

    Failure in multiprocessing mode

    >>> test = SynphotObsmodeIntegrationTest(
    ... "hst_0779.pmap",
    ... "data/synphot_root",
    ... obsmodes_file="data/hst_synphot_failing_obs.fits",
    ... processes=4
    ... )
    >>> test.run()
    CRDS - INFO -  Creating bandpass objects from 1 observation modes
    CRDS - ERROR -  Exception from stsynphot with obsmode 'acs,hrc,coron': UnboundLocalError("local variable 'fs' referenced before assignment")
    CRDS - ERROR -  Exception from pysynphot with obsmode 'acs,hrc,coron': FileNotFoundError(2, 'No such file or directory')
    CRDS - INFO -  1 / 1 observation modes failed
    False

    """