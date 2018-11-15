"""This module tests the synphot pseudo-instrument support for HST."""

# ==============================================================
from crds.core import config, naming, timestamp
from crds.hst import locate as hst_locate
from crds import certify
from crds import diff

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

def dt_synphot_certify():
    """
    >>> old_state = test_config.setup()

    TMC   rmap + reference

    >>> certify.CertifyScript("crds.certify  --run-fitsverify data/2b516556m_tmc.fits --comparison-context hst_0672.pmap")()
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/2b516556m_tmc.fits' (1/1) as 'FITS' relative to context 'hst_0672.pmap'
    CRDS - INFO -  FITS file '2b516556m_tmc.fits' conforms to FITS standards.
    CRDS - WARNING -  Checking 'FILENAME' failed: Required CRDS file 'acs_block1_002_syn.fits' does not exist in CRDS cache.
    CRDS - WARNING -  Failed resolving comparison reference for table checks : Unknown instrument 'synphot' for context 'hst_0672.pmap'
    CRDS - INFO -  Mode columns defined by spec for new reference '2b516556m_tmc.fits[1]' are: ['COMPNAME']
    CRDS - INFO -  All column names for this table new reference '2b516556m_tmc.fits[1]' are: ['TIME', 'COMPNAME', 'FILENAME', 'COMMENT']
    CRDS - INFO -  Checking for duplicate modes using intersection ['COMPNAME']
    CRDS - WARNING -  No comparison reference for '2b516556m_tmc.fits' in context 'hst_0672.pmap'. Skipping tables comparison.
    CRDS - INFO -  Running fitsverify.
    CRDS - INFO -  >>  
    CRDS - INFO -  >>               fitsverify 4.18 (CFITSIO V3.440)              
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
    CRDS - INFO -  3 warnings
    CRDS - INFO -  44 infos
    5

    >>> certify.CertifyScript("crds.certify  --run-fitsverify data/2381905mm_tmg.fits --comparison-context hst_0672.pmap")()
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/2381905mm_tmg.fits' (1/1) as 'FITS' relative to context 'hst_0672.pmap'
    CRDS - INFO -  FITS file '2381905mm_tmg.fits' conforms to FITS standards.
    CRDS - WARNING -  Failed resolving comparison reference for table checks : Unknown instrument 'synphot' for context 'hst_0672.pmap'
    CRDS - INFO -  Mode columns defined by spec for new reference '2381905mm_tmg.fits[1]' are: ['COMPNAME', 'KEYWORD', 'INNODE', 'OUTNODE', 'THCOMPNAME']
    CRDS - INFO -  All column names for this table new reference '2381905mm_tmg.fits[1]' are: ['COMPNAME', 'KEYWORD', 'INNODE', 'OUTNODE', 'THCOMPNAME', 'COMMENT']
    CRDS - INFO -  Checking for duplicate modes using intersection ['COMPNAME', 'INNODE', 'KEYWORD', 'OUTNODE', 'THCOMPNAME']
    CRDS - WARNING -  No comparison reference for '2381905mm_tmg.fits' in context 'hst_0672.pmap'. Skipping tables comparison.
    CRDS - INFO -  Running fitsverify.
    CRDS - INFO -  >>  
    CRDS - INFO -  >>               fitsverify 4.18 (CFITSIO V3.440)              
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
    CRDS - INFO -  2 warnings
    CRDS - INFO -  44 infos
    0

    TMT   rmap + reference

    >>> certify.CertifyScript("crds.certify  --run-fitsverify data/tae17277m_tmt.fits --comparison-context hst_0672.pmap")()
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/tae17277m_tmt.fits' (1/1) as 'FITS' relative to context 'hst_0672.pmap'
    CRDS - INFO -  FITS file 'tae17277m_tmt.fits' conforms to FITS standards.
    CRDS - WARNING -  Checking 'FILENAME' failed: Required CRDS file 'nic2_bend_001_th.fits' does not exist in CRDS cache.
    CRDS - WARNING -  Failed resolving comparison reference for table checks : Unknown instrument 'synphot' for context 'hst_0672.pmap'
    CRDS - INFO -  Mode columns defined by spec for new reference 'tae17277m_tmt.fits[1]' are: ['COMPNAME']
    CRDS - INFO -  All column names for this table new reference 'tae17277m_tmt.fits[1]' are: ['TIME', 'COMPNAME', 'FILENAME', 'COMMENT']
    CRDS - INFO -  Checking for duplicate modes using intersection ['COMPNAME']
    CRDS - WARNING -  No comparison reference for 'tae17277m_tmt.fits' in context 'hst_0672.pmap'. Skipping tables comparison.
    CRDS - INFO -  Running fitsverify.
    CRDS - INFO -  >>  
    CRDS - INFO -  >>               fitsverify 4.18 (CFITSIO V3.440)              
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
    CRDS - INFO -  3 warnings
    CRDS - INFO -  42 infos
    0

    THERMAL rmap + reference

    >>> certify.CertifyScript("crds.certify  --run-fitsverify data/wfc3_ir_f098m_002_th.fits --comparison-context hst_0672.pmap")()
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/wfc3_ir_f098m_002_th.fits' (1/1) as 'FITS' relative to context 'hst_0672.pmap'
    CRDS - INFO -  FITS file 'wfc3_ir_f098m_002_th.fits' conforms to FITS standards.
    CRDS - WARNING -  Failed resolving comparison reference for table checks : Unknown instrument 'synphot' for context 'hst_0672.pmap'
    CRDS - INFO -  Mode columns defined by spec for new reference 'wfc3_ir_f098m_002_th.fits[1]' are: ['WAVELENGTH']
    CRDS - INFO -  All column names for this table new reference 'wfc3_ir_f098m_002_th.fits[1]' are: ['WAVELENGTH', 'EMISSIVITY']
    CRDS - INFO -  Checking for duplicate modes using intersection ['WAVELENGTH']
    CRDS - WARNING -  No comparison reference for 'wfc3_ir_f098m_002_th.fits' in context 'hst_0672.pmap'. Skipping tables comparison.
    CRDS - INFO -  Running fitsverify.
    CRDS - INFO -  >>  
    CRDS - INFO -  >>               fitsverify 4.18 (CFITSIO V3.440)              
    CRDS - INFO -  >>               --------------------------------              
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  
    CRDS - INFO -  >> File: data/wfc3_ir_f098m_002_th.fits
    CRDS - INFO -  >> 
    CRDS - INFO -  >> 2 Header-Data Units in this file.
    CRDS - INFO -  >>  
    CRDS - INFO -  >> =================== HDU 1: Primary Array ===================
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  15 header keywords
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
    CRDS - INFO -  2 warnings
    CRDS - INFO -  40 infos
    0

    THRUPUT rmap + reference

    >>> certify.CertifyScript("crds.certify  --run-fitsverify data/wfc3_uvis_f469nf2_003_syn.fits --comparison-context hst_0672.pmap")()
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/wfc3_uvis_f469nf2_003_syn.fits' (1/1) as 'FITS' relative to context 'hst_0672.pmap'
    CRDS - INFO -  FITS file 'wfc3_uvis_f469nf2_003_syn.fits' conforms to FITS standards.
    CRDS - WARNING -  Failed resolving comparison reference for table checks : Unknown instrument 'synphot' for context 'hst_0672.pmap'
    CRDS - INFO -  Mode columns defined by spec for new reference 'wfc3_uvis_f469nf2_003_syn.fits[1]' are: ['WAVELENGTH']
    CRDS - INFO -  All column names for this table new reference 'wfc3_uvis_f469nf2_003_syn.fits[1]' are: ['WAVELENGTH', 'THROUGHPUT']
    CRDS - INFO -  Checking for duplicate modes using intersection ['WAVELENGTH']
    CRDS - WARNING -  No comparison reference for 'wfc3_uvis_f469nf2_003_syn.fits' in context 'hst_0672.pmap'. Skipping tables comparison.
    CRDS - INFO -  Running fitsverify.
    CRDS - INFO -  >>  
    CRDS - INFO -  >>               fitsverify 4.18 (CFITSIO V3.440)              
    CRDS - INFO -  >>               --------------------------------              
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  
    CRDS - INFO -  >> File: data/wfc3_uvis_f469nf2_003_syn.fits
    CRDS - INFO -  >> 
    CRDS - INFO -  >> 2 Header-Data Units in this file.
    CRDS - INFO -  >>  
    CRDS - INFO -  >> =================== HDU 1: Primary Array ===================
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  22 header keywords
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
    CRDS - INFO -  2 warnings
    CRDS - INFO -  40 infos
    0

    >>> test_config.cleanup(old_state)
    """

def dt_synphot_refactor():
    """
    >>> old_state = test_config.setup()

    TMC   rmap
    TMG   rmap
    TMT   rmap
    THERMAL rmap
    THRUPUT rmap
    COMP  rmap

    >>> test_config.cleanup(old_state)
    """

def dt_synphot_bestrefs():
    """
    >>> old_state = test_config.setup()
    >>> test_config.cleanup(old_state)
    """

def dt_synphot_sync():
    """
    >>> old_state = test_config.setup()
    >>> test_config.cleanup(old_state)
    """

def dt_synphot_diff():
    """
    >>> old_state = test_config.setup()

    TMC   rmap + reference
    TMG   rmap + reference
    TMT   rmap + reference
    THERMAL rmap + reference
    THRUPUT rmap + reference

    >>> test_config.cleanup(old_state)
    """

def dt_synphot_diff():
    """
    >>> old_state = test_config.setup()

    TMC   rmap + reference

    >>> diff.DiffScript("crds.diff data/16n1832tm_tmc.fits data/2b516556m_tmc.fits")()   # doctest: +ELLIPSIS
    <BLANKLINE>
     fitsdiff: 3.2.dev23244
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
