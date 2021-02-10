"""This module tests the synphot pseudo-instrument support for HST."""

# ==============================================================
import crds
from crds.core import config, log, naming, timestamp
from crds.hst import locate as hst_locate
from crds import certify
from crds import diff
from crds.refactoring import refactor

from crds.tests import test_config

# ==============================================================

def dt_synphot_naming():
    """
    >>> old_state = test_config.setup()

    >>> NOW = timestamp.parse_date("2018-11-14T00:00:00")

    THERMAL

    >>> config.is_crds_name("wfc3_ir_f098m_002_th.fits")
    False
    >>> config.is_cdbs_name("wfc3_ir_f098m_002_th.fits")
    True
    >>> config.is_reference("wfc3_ir_f098m_002_th.fits")
    True
    >>> config.is_mapping("wfc3_ir_f098m_002_th.fits")
    False
    >>> hst_locate.get_file_properties("wfc3_ir_f098m_002_th.fits")
    ('synphot', 'thermal')
    >>> hst_locate.ref_properties_from_cdbs_path("data/wfc3_ir_f098m_002_th.fits")
    ('data', 'hst', 'synphot', 'thermal', 'wfc3_ir_f098m_002_th', '.fits')
    >>> hst_locate.ref_properties_from_header("data/wfc3_ir_f098m_002_th.fits")
    ('data', 'hst', 'synphot', 'thermal', 'wfc3_ir_f098m_002_th', '.fits')
    >>> naming.generate_unique_name("wfc3_ir_f098m_002_th.fits", "hst", NOW)
    '2be00000m_th.fits'

    THRUPUT

    >>> config.is_crds_name("wfc3_uvis_f469nf2_003_syn.fits")
    False
    >>> config.is_cdbs_name("wfc3_uvis_f469nf2_003_syn.fits")
    True
    >>> config.is_reference("wfc3_uvis_f469nf2_003_syn.fits")
    True
    >>> config.is_mapping("wfc3_uvis_f469nf2_003_syn.fits")
    False
    >>> hst_locate.get_file_properties("wfc3_uvis_f469nf2_003_syn.fits")
    ('synphot', 'thruput')
    >>> hst_locate.ref_properties_from_cdbs_path("data/wfc3_uvis_f469nf2_003_syn.fits")
    ('data', 'hst', 'synphot', 'thruput', 'wfc3_uvis_f469nf2_003_syn', '.fits')
    >>> hst_locate.ref_properties_from_header("data/wfc3_uvis_f469nf2_003_syn.fits")
    ('data', 'hst', 'synphot', 'thruput', 'wfc3_uvis_f469nf2_003_syn', '.fits')
    >>> naming.generate_unique_name("wfc3_uvis_f469nf2_003_syn.fits", "hst", NOW)
    '2be00000m_syn.fits'

    TMGTAB

    >>> config.is_crds_name("2381905mm_tmg.fits")
    False
    >>> config.is_cdbs_name("2381905mm_tmg.fits")
    True
    >>> config.is_reference("2381905mm_tmg.fits")
    True
    >>> config.is_mapping("2381905mm_tmg.fits")
    False
    >>> hst_locate.get_file_properties("2381905mm_tmg.fits")
    ('synphot', 'tmgtab')
    >>> hst_locate.ref_properties_from_cdbs_path("data/2381905mm_tmg.fits")
    ('data', 'hst', 'synphot', 'tmgtab', '2381905mm_tmg', '.fits')
    >>> hst_locate.ref_properties_from_header("data/2381905mm_tmg.fits")
    ('data', 'hst', 'synphot', 'tmgtab', '2381905mm_tmg', '.fits')
    >>> naming.generate_unique_name("2381905mm_tmg.fits", "hst", NOW)
    '2be00000m_tmg.fits'

    TMCTAB

    >>> config.is_crds_name("43h1909cm_tmc.fits")
    False
    >>> config.is_cdbs_name("43h1909cm_tmc.fits")
    True
    >>> config.is_reference("43h1909cm_tmc.fits")
    True
    >>> config.is_mapping("43h1909cm_tmc.fits")
    False
    >>> hst_locate.get_file_properties("43h1909cm_tmc.fits")
    ('synphot', 'tmctab')
    >>> hst_locate.ref_properties_from_cdbs_path("data/43h1909cm_tmc.fits")
    ('data', 'hst', 'synphot', 'tmctab', '43h1909cm_tmc', '.fits')
    >>> hst_locate.ref_properties_from_header("data/43h1909cm_tmc.fits")
    ('data', 'hst', 'synphot', 'tmctab', '43h1909cm_tmc', '.fits')
    >>> naming.generate_unique_name("43h1909cm_tmc.fits", "hst", NOW)
    '2be00000m_tmc.fits'

    TMTTAB

    >>> config.is_crds_name("tae17277m_tmt.fits")
    False
    >>> config.is_cdbs_name("tae17277m_tmt.fits")
    True
    >>> config.is_reference("tae17277m_tmt.fits")
    True
    >>> config.is_mapping("tae17277m_tmt.fits")
    False
    >>> hst_locate.get_file_properties("tae17277m_tmt.fits")
    ('synphot', 'tmttab')
    >>> hst_locate.ref_properties_from_header("data/tae17277m_tmt.fits")
    ('data', 'hst', 'synphot', 'tmttab', 'tae17277m_tmt', '.fits')
    >>> hst_locate.ref_properties_from_cdbs_path("data/tae17277m_tmt.fits")
    ('data', 'hst', 'synphot', 'tmttab', 'tae17277m_tmt', '.fits')
    >>> naming.generate_unique_name("tae17277m_tmt.fits", "hst", NOW)
    '2be00000m_tmt.fits'

    >>> test_config.cleanup(old_state)
    """

def dt_synphot_certify_refs():
    """
    >>> old_state = test_config.setup()

    TMC   reference

    >>> certify.CertifyScript("crds.certify  --run-fitsverify data/43h1909cm_tmc.fits --comparison-context hst_0772.pmap")() # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/43h1909cm_tmc.fits' (1/1) as 'FITS' relative to context 'hst_0772.pmap'
    CRDS - INFO -  FITS file '43h1909cm_tmc.fits' conforms to FITS standards.
    CRDS - INFO -  Comparing reference '43h1909cm_tmc.fits' against '43h1240om_tmc.fits'
    CRDS - INFO -  Mode columns defined by spec for old reference '43h1240om_tmc.fits[1]' are: ['COMPNAME']
    CRDS - INFO -  All column names for this table old reference '43h1240om_tmc.fits[1]' are: ['TIME', 'COMPNAME', 'FILENAME', 'COMMENT']
    CRDS - INFO -  Checking for duplicate modes using intersection ['COMPNAME']
    CRDS - INFO -  Mode columns defined by spec for new reference '43h1909cm_tmc.fits[1]' are: ['COMPNAME']
    CRDS - INFO -  All column names for this table new reference '43h1909cm_tmc.fits[1]' are: ['TIME', 'COMPNAME', 'FILENAME', 'COMMENT']
    CRDS - INFO -  Checking for duplicate modes using intersection ['COMPNAME']
    CRDS - INFO -  Running fitsverify.
    CRDS - INFO -  >>
    CRDS - INFO -  >>               fitsverify ... (CFITSIO ...)
    CRDS - INFO -  >>               --------------------------------
    CRDS - INFO -  >>
    CRDS - INFO -  >>
    CRDS - INFO -  >> File: data/43h1909cm_tmc.fits
    CRDS - INFO -  >>
    CRDS - INFO -  >> 2 Header-Data Units in this file.
    CRDS - INFO -  >>
    CRDS - INFO -  >> =================== HDU 1: Primary Array ===================
    CRDS - INFO -  >>
    CRDS - INFO -  >>  121 header keywords
    CRDS - INFO -  >>
    CRDS - INFO -  >>  Null data array; NAXIS = 0
    CRDS - INFO -  >>
    CRDS - INFO -  >> =================== HDU 2: BINARY Table ====================
    CRDS - INFO -  >>
    CRDS - INFO -  >>  21 header keywords
    CRDS - INFO -  >>
    CRDS - INFO -  >>    (4 columns x 2713 rows)
    CRDS - INFO -  >>
    CRDS - INFO -  >>  Col# Name (Units)       Format
    CRDS - INFO -  >>    1 TIME                 26A
    CRDS - INFO -  >>    2 COMPNAME             18A
    CRDS - INFO -  >>    3 FILENAME             56A
    CRDS - INFO -  >>    4 COMMENT              68A
    CRDS - INFO -  >>
    CRDS - INFO -  >> ++++++++++++++++++++++ Error Summary  ++++++++++++++++++++++
    CRDS - INFO -  >>
    CRDS - INFO -  >>  HDU#  Name (version)       Type             Warnings  Errors
    CRDS - INFO -  >>  1                          Primary Array    0         0
    CRDS - INFO -  >>  2                          Binary Table     0         0
    CRDS - INFO -  >>
    CRDS - INFO -  >> **** Verification found 0 warning(s) and 0 error(s). ****
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  46 infos
    0

    >>> certify.CertifyScript("crds.certify  --run-fitsverify data/2381905mm_tmg.fits --comparison-context hst_0691.pmap")()   # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/2381905mm_tmg.fits' (1/1) as 'FITS' relative to context 'hst_0691.pmap'
    CRDS - INFO -  FITS file '2381905mm_tmg.fits' conforms to FITS standards.
    CRDS - INFO -  Mode columns defined by spec for new reference '2381905mm_tmg.fits[1]' are: ['COMPNAME', 'KEYWORD', 'INNODE', 'OUTNODE', 'THCOMPNAME']
    CRDS - INFO -  All column names for this table new reference '2381905mm_tmg.fits[1]' are: ['COMPNAME', 'KEYWORD', 'INNODE', 'OUTNODE', 'THCOMPNAME', 'COMMENT']
    CRDS - INFO -  Checking for duplicate modes using intersection ['COMPNAME', 'INNODE', 'KEYWORD', 'OUTNODE', 'THCOMPNAME']
    CRDS - WARNING -  No comparison reference for '2381905mm_tmg.fits' in context 'hst_0691.pmap'. Skipping tables comparison.
    CRDS - INFO -  Running fitsverify.
    CRDS - INFO -  >>
    CRDS - INFO -  >>               fitsverify ... (CFITSIO ...)
    CRDS - INFO -  >>               --------------------------------
    CRDS - INFO -  >>
    CRDS - INFO -  >>
    CRDS - INFO -  >> File: data/2381905mm_tmg.fits
    CRDS - INFO -  >>
    CRDS - INFO -  >> 2 Header-Data Units in this file.
    CRDS - INFO -  >>
    CRDS - INFO -  >> =================== HDU 1: Primary Array ===================
    CRDS - INFO -  >>
    CRDS - INFO -  >>  192 header keywords
    CRDS - INFO -  >>
    CRDS - INFO -  >>  Null data array; NAXIS = 0
    CRDS - INFO -  >>
    CRDS - INFO -  >> =================== HDU 2: BINARY Table ====================
    CRDS - INFO -  >>
    CRDS - INFO -  >>  103 header keywords
    CRDS - INFO -  >>
    CRDS - INFO -  >>    (6 columns x 3656 rows)
    CRDS - INFO -  >>
    CRDS - INFO -  >>  Col# Name (Units)       Format
    CRDS - INFO -  >>    1 COMPNAME             18A
    CRDS - INFO -  >>    2 KEYWORD              11A
    CRDS - INFO -  >>    3 INNODE               J
    CRDS - INFO -  >>    4 OUTNODE              J
    CRDS - INFO -  >>    5 THCOMPNAME           17A
    CRDS - INFO -  >>    6 COMMENT              68A
    CRDS - INFO -  >>
    CRDS - INFO -  >> ++++++++++++++++++++++ Error Summary  ++++++++++++++++++++++
    CRDS - INFO -  >>
    CRDS - INFO -  >>  HDU#  Name (version)       Type             Warnings  Errors
    CRDS - INFO -  >>  1                          Primary Array    0         0
    CRDS - INFO -  >>  2                          Binary Table     0         0
    CRDS - INFO -  >>
    CRDS - INFO -  >> **** Verification found 0 warning(s) and 0 error(s). ****
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  1 warnings
    CRDS - INFO -  44 infos
    0

    TMT   reference

    >>> certify.CertifyScript("crds.certify  --run-fitsverify data/tae17277m_tmt.fits --comparison-context hst_0691.pmap")()   # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/tae17277m_tmt.fits' (1/1) as 'FITS' relative to context 'hst_0691.pmap'
    CRDS - INFO -  FITS file 'tae17277m_tmt.fits' conforms to FITS standards.
    CRDS - ERROR -  Malformed FILENAME value at index 1 (missing or invalid path prefix)
    CRDS - INFO -  Comparing reference 'tae17277m_tmt.fits' against '3241637sm_tmt.fits'
    CRDS - INFO -  Mode columns defined by spec for old reference '3241637sm_tmt.fits[1]' are: ['COMPNAME']
    CRDS - INFO -  All column names for this table old reference '3241637sm_tmt.fits[1]' are: ['TIME', 'COMPNAME', 'FILENAME', 'COMMENT']
    CRDS - INFO -  Checking for duplicate modes using intersection ['COMPNAME']
    CRDS - INFO -  Mode columns defined by spec for new reference 'tae17277m_tmt.fits[1]' are: ['COMPNAME']
    CRDS - INFO -  All column names for this table new reference 'tae17277m_tmt.fits[1]' are: ['TIME', 'COMPNAME', 'FILENAME', 'COMMENT']
    CRDS - INFO -  Checking for duplicate modes using intersection ['COMPNAME']
    CRDS - INFO -  Table mode (('COMPNAME', 'dark'),) of new reference 'tae17277m_tmt.fits[1]' is NOT IN old reference '3241637sm_tmt.fits'
    CRDS - INFO -  Table mode (('COMPNAME', 'nic1_dn'),) of new reference 'tae17277m_tmt.fits[1]' is NOT IN old reference '3241637sm_tmt.fits'
    CRDS - INFO -  Table mode (('COMPNAME', 'nic2_dn'),) of new reference 'tae17277m_tmt.fits[1]' is NOT IN old reference '3241637sm_tmt.fits'
    CRDS - INFO -  Table mode (('COMPNAME', 'nic3_dn'),) of new reference 'tae17277m_tmt.fits[1]' is NOT IN old reference '3241637sm_tmt.fits'
    CRDS - INFO -  Running fitsverify.
    CRDS - INFO -  >>
    CRDS - INFO -  >>               fitsverify ... (CFITSIO ...)
    CRDS - INFO -  >>               --------------------------------
    CRDS - INFO -  >>
    CRDS - INFO -  >>
    CRDS - INFO -  >> File: data/tae17277m_tmt.fits
    CRDS - INFO -  >>
    CRDS - INFO -  >> 2 Header-Data Units in this file.
    CRDS - INFO -  >>
    CRDS - INFO -  >> =================== HDU 1: Primary Array ===================
    CRDS - INFO -  >>
    CRDS - INFO -  >>  32 header keywords
    CRDS - INFO -  >>
    CRDS - INFO -  >>  Null data array; NAXIS = 0
    CRDS - INFO -  >>
    CRDS - INFO -  >> =================== HDU 2: BINARY Table ====================
    CRDS - INFO -  >>
    CRDS - INFO -  >>  54 header keywords
    CRDS - INFO -  >>
    CRDS - INFO -  >>    (4 columns x 144 rows)
    CRDS - INFO -  >>
    CRDS - INFO -  >>  Col# Name (Units)       Format
    CRDS - INFO -  >>    1 TIME                 27A
    CRDS - INFO -  >>    2 COMPNAME             18A
    CRDS - INFO -  >>    3 FILENAME             50A
    CRDS - INFO -  >>    4 COMMENT              68A
    CRDS - INFO -  >>
    CRDS - INFO -  >> ++++++++++++++++++++++ Error Summary  ++++++++++++++++++++++
    CRDS - INFO -  >>
    CRDS - INFO -  >>  HDU#  Name (version)       Type             Warnings  Errors
    CRDS - INFO -  >>  1                          Primary Array    0         0
    CRDS - INFO -  >>  2                          Binary Table     0         0
    CRDS - INFO -  >>
    CRDS - INFO -  >> **** Verification found 0 warning(s) and 0 error(s). ****
    CRDS - INFO -  ########################################
    CRDS - INFO -  1 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  50 infos
    1

    THERMAL reference

    >>> certify.CertifyScript("crds.certify  --run-fitsverify data/wfc3_ir_f098m_002_th.fits --comparison-context hst_0691.pmap")()  # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/wfc3_ir_f098m_002_th.fits' (1/1) as 'FITS' relative to context 'hst_0691.pmap'
    CRDS - INFO -  FITS file 'wfc3_ir_f098m_002_th.fits' conforms to FITS standards.
    CRDS - ERROR -  New filename version (002) must exceed previous version (002)
    CRDS - INFO -  Mode columns defined by spec for new reference 'wfc3_ir_f098m_002_th.fits[1]' are: ['WAVELENGTH']
    CRDS - INFO -  All column names for this table new reference 'wfc3_ir_f098m_002_th.fits[1]' are: ['WAVELENGTH', 'EMISSIVITY']
    CRDS - INFO -  Checking for duplicate modes using intersection ['WAVELENGTH']
    CRDS - WARNING -  No comparison reference for 'wfc3_ir_f098m_002_th.fits' in context 'hst_0691.pmap'. Skipping tables comparison.
    CRDS - INFO -  Running fitsverify.
    CRDS - INFO -  >>
    CRDS - INFO -  >>               fitsverify ... (CFITSIO V...)
    CRDS - INFO -  >>               --------------------------------
    CRDS - INFO -  >>
    CRDS - INFO -  >>
    CRDS - INFO -  >> File: data/wfc3_ir_f098m_002_th.fits
    CRDS - INFO -  >>
    CRDS - INFO -  >> 2 Header-Data Units in this file.
    CRDS - INFO -  >>
    CRDS - INFO -  >> =================== HDU 1: Primary Array ===================
    CRDS - INFO -  >>
    CRDS - INFO -  >>  17 header keywords
    CRDS - INFO -  >>
    CRDS - INFO -  >>  Null data array; NAXIS = 0
    CRDS - INFO -  >>
    CRDS - INFO -  >> =================== HDU 2: BINARY Table ====================
    CRDS - INFO -  >>
    CRDS - INFO -  >>  20 header keywords
    CRDS - INFO -  >>
    CRDS - INFO -  >>    (2 columns x 5863 rows)
    CRDS - INFO -  >>
    CRDS - INFO -  >>  Col# Name (Units)       Format
    CRDS - INFO -  >>    1 WAVELENGTH (ANGSTROM E
    CRDS - INFO -  >>    2 EMISSIVITY           E
    CRDS - INFO -  >>
    CRDS - INFO -  >> ++++++++++++++++++++++ Error Summary  ++++++++++++++++++++++
    CRDS - INFO -  >>
    CRDS - INFO -  >>  HDU#  Name (version)       Type             Warnings  Errors
    CRDS - INFO -  >>  1                          Primary Array    0         0
    CRDS - INFO -  >>  2                          Binary Table     0         0
    CRDS - INFO -  >>
    CRDS - INFO -  >> **** Verification found 0 warning(s) and 0 error(s). ****
    CRDS - INFO -  ########################################
    CRDS - INFO -  1 errors
    CRDS - INFO -  1 warnings
    CRDS - INFO -  40 infos
    1

    THRUPUT reference

    >>> certify.CertifyScript("crds.certify  --run-fitsverify data/wfc3_uvis_f469nf2_003_syn.fits --comparison-context hst_0691.pmap")() # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/wfc3_uvis_f469nf2_003_syn.fits' (1/1) as 'FITS' relative to context 'hst_0691.pmap'
    CRDS - INFO -  FITS file 'wfc3_uvis_f469nf2_003_syn.fits' conforms to FITS standards.
    CRDS - ERROR -  New filename version (003) must exceed previous version (003)
    CRDS - INFO -  Mode columns defined by spec for new reference 'wfc3_uvis_f469nf2_003_syn.fits[1]' are: ['WAVELENGTH']
    CRDS - INFO -  All column names for this table new reference 'wfc3_uvis_f469nf2_003_syn.fits[1]' are: ['WAVELENGTH', 'THROUGHPUT']
    CRDS - INFO -  Checking for duplicate modes using intersection ['WAVELENGTH']
    CRDS - WARNING -  No comparison reference for 'wfc3_uvis_f469nf2_003_syn.fits' in context 'hst_0691.pmap'. Skipping tables comparison.
    CRDS - INFO -  Running fitsverify.
    CRDS - INFO -  >>
    CRDS - INFO -  >>               fitsverify ... (CFITSIO V...)
    CRDS - INFO -  >>               --------------------------------
    CRDS - INFO -  >>
    CRDS - INFO -  >>
    CRDS - INFO -  >> File: data/wfc3_uvis_f469nf2_003_syn.fits
    CRDS - INFO -  >>
    CRDS - INFO -  >> 2 Header-Data Units in this file.
    CRDS - INFO -  >>
    CRDS - INFO -  >> =================== HDU 1: Primary Array ===================
    CRDS - INFO -  >>
    CRDS - INFO -  >>  24 header keywords
    CRDS - INFO -  >>
    CRDS - INFO -  >>  Null data array; NAXIS = 0
    CRDS - INFO -  >>
    CRDS - INFO -  >> =================== HDU 2: BINARY Table ====================
    CRDS - INFO -  >>
    CRDS - INFO -  >>  17 header keywords
    CRDS - INFO -  >>
    CRDS - INFO -  >>    (2 columns x 13 rows)
    CRDS - INFO -  >>
    CRDS - INFO -  >>  Col# Name (Units)       Format
    CRDS - INFO -  >>    1 WAVELENGTH (ANGSTROM E
    CRDS - INFO -  >>    2 THROUGHPUT (TRANSMIS E
    CRDS - INFO -  >>
    CRDS - INFO -  >> ++++++++++++++++++++++ Error Summary  ++++++++++++++++++++++
    CRDS - INFO -  >>
    CRDS - INFO -  >>  HDU#  Name (version)       Type             Warnings  Errors
    CRDS - INFO -  >>  1                          Primary Array    0         0
    CRDS - INFO -  >>  2                          Binary Table     0         0
    CRDS - INFO -  >>
    CRDS - INFO -  >> **** Verification found 0 warning(s) and 0 error(s). ****
    CRDS - INFO -  ########################################
    CRDS - INFO -  1 errors
    CRDS - INFO -  1 warnings
    CRDS - INFO -  40 infos
    1

    >>> test_config.cleanup(old_state)
    """

def dt_synphot_certify_rmaps():
    """
    >>> old_state = test_config.setup()

    TMC   rmap

    >>> certify.CertifyScript("crds.certify data/synphot_tmctab.rmap --comparison-context hst_0857.pmap")() # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/synphot_tmctab.rmap' (1/1) as 'MAPPING' relative to context 'hst_0857.pmap'
    CRDS - INFO -  Mapping 'synphot_tmctab.rmap' corresponds to 'hst_synphot_tmctab_0021.rmap' from context 'hst_0857.pmap' for checking mapping differences.
    CRDS - INFO -  Checking diffs from 'hst_synphot_tmctab_0021.rmap' to 'synphot_tmctab.rmap'
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  5 infos
    0

    TMG   rmap

    >>> certify.CertifyScript("crds.certify data/synphot_tmgtab.rmap --comparison-context hst_0857.pmap")() # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/synphot_tmgtab.rmap' (1/1) as 'MAPPING' relative to context 'hst_0857.pmap'
    CRDS - INFO -  Mapping 'synphot_tmgtab.rmap' corresponds to 'hst_synphot_tmgtab_0007.rmap' from context 'hst_0857.pmap' for checking mapping differences.
    CRDS - INFO -  Checking diffs from 'hst_synphot_tmgtab_0007.rmap' to 'synphot_tmgtab.rmap'
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  5 infos
    0

    TMT   rmap

    >>> certify.CertifyScript("crds.certify data/synphot_tmttab.rmap --comparison-context hst_0857.pmap")() # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/synphot_tmttab.rmap' (1/1) as 'MAPPING' relative to context 'hst_0857.pmap'
    CRDS - INFO -  Mapping 'synphot_tmttab.rmap' corresponds to 'hst_synphot_tmttab_0001.rmap' from context 'hst_0857.pmap' for checking mapping differences.
    CRDS - INFO -  Checking diffs from 'hst_synphot_tmttab_0001.rmap' to 'synphot_tmttab.rmap'
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  5 infos
    0

    THERMAL rmap

    >>> certify.CertifyScript("crds.certify data/synphot_thermal.rmap --comparison-context hst_0857.pmap")() # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/synphot_thermal.rmap' (1/1) as 'MAPPING' relative to context 'hst_0857.pmap'
    CRDS - INFO -  Mapping 'synphot_thermal.rmap' corresponds to 'hst_synphot_thermal_0002.rmap' from context 'hst_0857.pmap' for checking mapping differences.
    CRDS - INFO -  Checking diffs from 'hst_synphot_thermal_0002.rmap' to 'synphot_thermal.rmap'
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  5 infos
    0

    THRUPUT rmap
    >>> certify.CertifyScript("crds.certify data/synphot_thruput.rmap --comparison-context hst_0857.pmap")() # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/synphot_thruput.rmap' (1/1) as 'MAPPING' relative to context 'hst_0857.pmap'
    CRDS - INFO -  Mapping 'synphot_thruput.rmap' corresponds to 'hst_synphot_thruput_0025.rmap' from context 'hst_0857.pmap' for checking mapping differences.
    CRDS - INFO -  Checking diffs from 'hst_synphot_thruput_0025.rmap' to 'synphot_thruput.rmap'
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  5 infos
    0

    >>> test_config.cleanup(old_state)
    """

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
    CRDS - ERROR -  Exception from stsynphot with obsmode 'acs,hrc,coron': FileNotFoundError(2, 'No such file or directory')
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
    CRDS - ERROR -  Exception from stsynphot with obsmode 'acs,hrc,coron': FileNotFoundError(2, 'No such file or directory')
    CRDS - INFO -  1 / 1 observation modes failed
    False

    """

# ==============================================================

def main():
    """Run module tests,  for now just doctests only.

    test_config.setup() and cleanup() are done inline above because bracketing
    the tests here does not get picked up by nose test discovery.  Combining
    tests into one giant docstring works but is hard to analyze and debug when
    things go wrong.
    """
    from crds.tests import test_synphot_hst, tstmod
    return tstmod(test_synphot_hst)

# ==============================================================

if __name__ == "__main__":
    print(main())
