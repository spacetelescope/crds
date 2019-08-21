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

    >>> config.is_crds_name("2b516556m_tmc.fits")
    False
    >>> config.is_cdbs_name("2b516556m_tmc.fits")
    True
    >>> config.is_reference("2b516556m_tmc.fits")
    True
    >>> config.is_mapping("2b516556m_tmc.fits")
    False
    >>> hst_locate.get_file_properties("2b516556m_tmc.fits")
    ('synphot', 'tmctab')
    >>> hst_locate.ref_properties_from_cdbs_path("data/2b516556m_tmc.fits")
    ('data', 'hst', 'synphot', 'tmctab', '2b516556m_tmc', '.fits')
    >>> hst_locate.ref_properties_from_header("data/2b516556m_tmc.fits")
    ('data', 'hst', 'synphot', 'tmctab', '2b516556m_tmc', '.fits')
    >>> naming.generate_unique_name("2b516556m_tmc.fits", "hst", NOW)
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

    >>> certify.CertifyScript("crds.certify  --run-fitsverify data/2b516556m_tmc.fits --comparison-context hst_0691.pmap")() # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/2b516556m_tmc.fits' (1/1) as 'FITS' relative to context 'hst_0691.pmap'
    CRDS - INFO -  FITS file '2b516556m_tmc.fits' conforms to FITS standards.
    CRDS - WARNING -  Checking 'FILENAME' failed: Required CRDS file 'acs_block1_002_syn.fits' does not exist in CRDS cache.
    CRDS - INFO -  Mode columns defined by spec for new reference '2b516556m_tmc.fits[1]' are: ['COMPNAME']
    CRDS - INFO -  All column names for this table new reference '2b516556m_tmc.fits[1]' are: ['TIME', 'COMPNAME', 'FILENAME', 'COMMENT']
    CRDS - INFO -  Checking for duplicate modes using intersection ['COMPNAME']
    CRDS - WARNING -  No comparison reference for '2b516556m_tmc.fits' in context 'hst_0691.pmap'. Skipping tables comparison.
    CRDS - INFO -  Running fitsverify.
    CRDS - INFO -  >>
    CRDS - INFO -  >>               fitsverify ... (CFITSIO ...)
    CRDS - INFO -  >>               --------------------------------
    CRDS - INFO -  >>
    CRDS - INFO -  >>
    CRDS - INFO -  >> File: data/2b516556m_tmc.fits
    CRDS - INFO -  >>
    CRDS - INFO -  >> 2 Header-Data Units in this file.
    CRDS - INFO -  >>
    CRDS - INFO -  >> =================== HDU 1: Primary Array ===================
    CRDS - INFO -  >>
    CRDS - INFO -  >>  81 header keywords
    CRDS - INFO -  >>
    CRDS - INFO -  >>  Null data array; NAXIS = 0
    CRDS - INFO -  >>
    CRDS - INFO -  >> =================== HDU 2: BINARY Table ====================
    CRDS - INFO -  >>
    CRDS - ERROR -  >> *** Error:   Keyword #11, TDISP1: invalid format "26A".
    CRDS - ERROR -  >> *** Error:   Keyword #14, TDISP2: invalid format "18A".
    CRDS - ERROR -  >> *** Error:   Keyword #17, TDISP3: invalid format "56A".
    CRDS - ERROR -  >> *** Error:   Keyword #20, TDISP4: invalid format "68A".
    CRDS - INFO -  >>
    CRDS - INFO -  >>  21 header keywords
    CRDS - INFO -  >>
    CRDS - INFO -  >>    (4 columns x 3012 rows)
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
    CRDS - INFO -  >>  2                          Binary Table     0         4
    CRDS - INFO -  >>
    CRDS - INFO -  >> **** Verification found 0 warning(s) and 4 error(s). ****
    CRDS - INFO -  Fitsverify returned a NONZERO COMMAND LINE ERROR STATUS.
    CRDS - ERROR -  Fitsverify output contains errors or warnings CRDS recategorizes as ERRORs.
    CRDS - INFO -  ########################################
    CRDS - INFO -  5 errors
    CRDS - INFO -  2 warnings
    CRDS - INFO -  44 infos
    5

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
    CRDS - WARNING -  Checking 'FILENAME' failed: Required CRDS file 'nic2_bend_001_th.fits' does not exist in CRDS cache.
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
    CRDS - INFO -  >>               fitsverify ... (CFITSIO V...)
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
    CRDS - INFO -  0 errors
    CRDS - INFO -  1 warnings
    CRDS - INFO -  50 infos
    0

    THERMAL reference

    >>> certify.CertifyScript("crds.certify  --run-fitsverify data/wfc3_ir_f098m_002_th.fits --comparison-context hst_0691.pmap")()  # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/wfc3_ir_f098m_002_th.fits' (1/1) as 'FITS' relative to context 'hst_0691.pmap'
    CRDS - INFO -  FITS file 'wfc3_ir_f098m_002_th.fits' conforms to FITS standards.
    CRDS - INFO -  Mode columns defined by spec for new reference 'wfc3_ir_f098m_002_th.fits[1]' are: ['WAVELENGTH']
    CRDS - INFO -  All column names for this table new reference 'wfc3_ir_f098m_002_th.fits[1]' are: ['WAVELENGTH', 'EMISSIVITY']
    CRDS - INFO -  Checking for duplicate modes using intersection ['WAVELENGTH']
    CRDS - WARNING -  No comparison reference for 'wfc3_ir_f098m_002_th.fits' in context 'hst_0691.pmap'. Skipping tables comparison.
    CRDS - INFO -  Running fitsverify.
    CRDS - INFO -  >>
    CRDS - INFO -  >>               fitsverify ... (CFITSIO ...)
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
    CRDS - INFO -  0 errors
    CRDS - INFO -  1 warnings
    CRDS - INFO -  40 infos
    0

    THRUPUT reference

    >>> certify.CertifyScript("crds.certify  --run-fitsverify data/wfc3_uvis_f469nf2_003_syn.fits --comparison-context hst_0691.pmap")() # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/wfc3_uvis_f469nf2_003_syn.fits' (1/1) as 'FITS' relative to context 'hst_0691.pmap'
    CRDS - INFO -  FITS file 'wfc3_uvis_f469nf2_003_syn.fits' conforms to FITS standards.
    CRDS - INFO -  Mode columns defined by spec for new reference 'wfc3_uvis_f469nf2_003_syn.fits[1]' are: ['WAVELENGTH']
    CRDS - INFO -  All column names for this table new reference 'wfc3_uvis_f469nf2_003_syn.fits[1]' are: ['WAVELENGTH', 'THROUGHPUT']
    CRDS - INFO -  Checking for duplicate modes using intersection ['WAVELENGTH']
    CRDS - WARNING -  No comparison reference for 'wfc3_uvis_f469nf2_003_syn.fits' in context 'hst_0691.pmap'. Skipping tables comparison.
    CRDS - INFO -  Running fitsverify.
    CRDS - INFO -  >>
    CRDS - INFO -  >>               fitsverify ... (CFITSIO ...)
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
    CRDS - INFO -  0 errors
    CRDS - INFO -  1 warnings
    CRDS - INFO -  40 infos
    0

    >>> test_config.cleanup(old_state)
    """

def dt_synphot_certify_rmaps():
    """
    >>> old_state = test_config.setup()

    TMC   rmap

    >>> certify.CertifyScript("crds.certify  data/synphot_tmctab.rmap")() # doctest: +ELLIPSIS
    CRDS - INFO -  Certification includes mappings but is not --deep, no --comparison-context is defined.
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/synphot_tmctab.rmap' (1/1) as 'MAPPING' relative to context None
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  4 infos
    0

    TMG   rmap

    >>> certify.CertifyScript("crds.certify  data/synphot_tmgtab.rmap")() # doctest: +ELLIPSIS
    CRDS - INFO -  Certification includes mappings but is not --deep, no --comparison-context is defined.
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/synphot_tmgtab.rmap' (1/1) as 'MAPPING' relative to context None
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  4 infos
    0

    TMT   rmap

    >>> certify.CertifyScript("crds.certify  data/synphot_tmttab.rmap")() # doctest: +ELLIPSIS
    CRDS - INFO -  Certification includes mappings but is not --deep, no --comparison-context is defined.
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/synphot_tmttab.rmap' (1/1) as 'MAPPING' relative to context None
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  4 infos
    0

    THERMAL rmap

    >>> certify.CertifyScript("crds.certify  data/synphot_thermal.rmap")() # doctest: +ELLIPSIS
    CRDS - INFO -  Certification includes mappings but is not --deep, no --comparison-context is defined.
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/synphot_thermal.rmap' (1/1) as 'MAPPING' relative to context None
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  4 infos
    0

    THRUPUT rmap
    >>> certify.CertifyScript("crds.certify  data/synphot_thruput.rmap")() # doctest: +ELLIPSIS
    CRDS - INFO -  Certification includes mappings but is not --deep, no --comparison-context is defined.
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/synphot_thruput.rmap' (1/1) as 'MAPPING' relative to context None
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  4 infos
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
    CRDS - DEBUG -  Parkey synphot thermal created is relevant: False 'keep_comments'
    CRDS - DEBUG -  Setting irrelevant parkey 'CREATED' to N/A
    CRDS - DEBUG -  Parkey synphot thermal descrip is relevant: False 'keep_comments'
    CRDS - DEBUG -  Setting irrelevant parkey 'DESCRIP' to N/A
    {'COMPNAME': 'NIC1_BEND', 'CREATED': 'N/A', 'DESCRIP': 'N/A'}

    For rmap updates which add comment keywords to the match tuples for web display

    >>> print(log.PP(r.map_irrelevant_parkeys_to_na(header, keep_comments=True)))
    CRDS - DEBUG -  Parkey synphot thermal created is relevant: True 'keep_comments'
    CRDS - DEBUG -  Parkey synphot thermal descrip is relevant: True 'keep_comments'
    {'COMPNAME': 'NIC1_BEND',
     'CREATED': '2002-03-06 04:51:00',
     'DESCRIP': 'Use NIC2 values'}

    >>> _ = log.set_verbose(v)

    TMC   rmap

    >>> refactor.RefactorScript("crds.refactor insert data/synphot_tmctab.rmap /tmp/synphot_tmctab.test.rmap data/2b516556m_tmc.fits")()
    CRDS - INFO -  Inserting 2b516556m_tmc.fits into 'synphot_tmctab.rmap'
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  1 infos
    0

    >>> diff.DiffScript("crds.diff  data/synphot_tmctab.rmap /tmp/synphot_tmctab.test.rmap")()
    (('data/synphot_tmctab.rmap', '/tmp/synphot_tmctab.test.rmap'), 'added Match rule for 2b516556m_tmc.fits')
    1

    TMG   rmap

    >>> refactor.RefactorScript("crds.refactor insert data/synphot_tmgtab.rmap /tmp/synphot_tmgtab.test.rmap data/2381905mm_tmg.fits")()
    CRDS - INFO -  Inserting 2381905mm_tmg.fits into 'hst_synphot_tmg.rmap'
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  1 infos
    0

    >>> diff.DiffScript("crds.diff  data/synphot_tmgtab.rmap /tmp/synphot_tmgtab.test.rmap")()
    (('data/synphot_tmgtab.rmap', '/tmp/synphot_tmgtab.test.rmap'), 'added Match rule for 2381905mm_tmg.fits')
    1

    TMT   rmap

    >>> refactor.RefactorScript("crds.refactor insert data/synphot_tmttab.rmap /tmp/synphot_tmttab.test.rmap data/tae17277m_tmt.fits")()
    CRDS - INFO -  Inserting tae17277m_tmt.fits into 'synphot_tmt.rmap'
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  1 infos
    0

    >>> diff.DiffScript("crds.diff  data/synphot_tmttab.rmap /tmp/synphot_tmttab.test.rmap")()
    (('data/synphot_tmttab.rmap', '/tmp/synphot_tmttab.test.rmap'), 'added Match rule for tae17277m_tmt.fits')
    1

    THERMAL rmap

    >>> refactor.RefactorScript("crds.refactor insert data/synphot_thermal.rmap /tmp/synphot_thermal.test.rmap data/wfc3_ir_f098m_002_th.fits")()
    CRDS - INFO -  Inserting wfc3_ir_f098m_002_th.fits into 'hst_synphot_thermal.rmap'
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  1 infos
    0

    >>> diff.DiffScript("crds.diff  data/synphot_thermal.rmap /tmp/synphot_thermal.test.rmap")()
    (('data/synphot_thermal.rmap', '/tmp/synphot_thermal.test.rmap'), ('WFC3_IR_F098M', '2019-08-15 08:00:00', 'Filter transmission for F098M XXX YYY ZZZ'), 'deleted Match rule for wfc3_ir_f098m_001_th.fits')
    (('data/synphot_thermal.rmap', '/tmp/synphot_thermal.test.rmap'), ('WFC3_IR_F098M', 'NOV 16 2018', 'UPDATED TO CONVERT AIR WAVELENGTHS TO VACUUM.'), 'added Match rule for wfc3_ir_f098m_002_th.fits')
    1

    THRUPUT rmap

    >>> refactor.RefactorScript("crds.refactor insert data/synphot_thruput.rmap /tmp/synphot_thruput.test.rmap data/wfc3_uvis_f469nf2_003_syn.fits")()
    CRDS - INFO -  Inserting wfc3_uvis_f469nf2_003_syn.fits into 'hst_synphot_thruput.rmap'
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  1 infos
    0

    >>> diff.DiffScript("crds.diff  data/synphot_thruput.rmap /tmp/synphot_thruput.test.rmap")()
    (('data/synphot_thruput.rmap', '/tmp/synphot_thruput.test.rmap'), ('WFC3_UVIS_F469NF2', 'NOV 16 2018', 'NORMALIZATION OF F469N FLAT CHIP 2---------------------------------'), 'added Match rule for wfc3_uvis_f469nf2_003_syn.fits')
    1

    >>> test_config.cleanup(old_state)
    """

def dt_synphot_bestrefs():
    """
    >>> old_state = test_config.setup()

    >>> r = crds.get_cached_mapping("data/synphot_thermal.rmap")
    >>> r.get_best_references({'COMPNAME':'NIC1_F110W', 'CREATED':'NO MATCH', 'DESCRIP':'NO MATCH'})
    {'thermal': 'nic1_f110w_002_th.fits'}

    >>> r = crds.get_cached_mapping("data/synphot_thruput.rmap")
    >>> r.get_best_references({'COMPNAME':'ACS_BLOCK1', 'CREATED':'NO MATCH', 'DESCRIP':'NO MATCH'})
    {'thruput': 'acs_block1_002_syn.fits'}

    >>> test_config.cleanup(old_state)
    """


def dt_synphot_diff():
    """
    >>> old_state = test_config.setup()

    TMC   reference

    >>> diff.DiffScript("crds.diff data/16n1832tm_tmc.fits data/2b516556m_tmc.fits")()   # doctest: +ELLIPSIS
    <BLANKLINE>
     fitsdiff: ...
     a: data/16n1832tm_tmc.fits
     b: data/2b516556m_tmc.fits
     Maximum number of different data values to be reported: 10
     Relative tolerance: 0.0, Absolute tolerance: 0.0
    <BLANKLINE>
    Primary HDU:
    <BLANKLINE>
       Headers contain differences:
         Headers have different number of cards:
          a: 48
          b: 80
         Inconsistent duplicates of keyword 'HISTORY':
          Occurs 38 time(s) in a, 70 times in (b)
         Keyword COMMENT  has different values:
            a> = Reference file created by WFC3
             ? --                          ^^ ^
            b> Reference file created by ReDCaT Team
             ?                           ^^^ ^^^^^^^
    ...
    <BLANKLINE>
    Extension HDU 1:
    <BLANKLINE>
       Headers contain differences:
         Keyword NAXIS2   has different values:
            a> 3008
            b> 3012
    <BLANKLINE>
       Data contains differences:
         Table rows differ:
          a: 3008
          b: 3012
         No further data comparison performed.
    <BLANKLINE>
     Row differences for HDU extension #1
    <BLANKLINE>
        Summary:
            a rows 92-94 differ from b rows 92-94
            a rows 107-107 differ from b rows 107-107
            a rows 109-113 differ from b rows 109-113
            a rows 177-194 differ from b rows 177-194
            a rows 197-208 differ from b rows 197-212
            a rows 210-307 differ from b rows 214-311
            a rows 2298-2299 differ from b rows 2302-2303
            a rows 2301-2302 differ from b rows 2305-2306
            a rows 2304-2333 differ from b rows 2308-2337
    <BLANKLINE>
        Row difference, unified diff format:
            --- Table A
    <BLANKLINE>
            +++ Table B
    <BLANKLINE>
            @@ -90,9 +90,9 @@
    ...

    >>> test_config.cleanup(old_state)
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
