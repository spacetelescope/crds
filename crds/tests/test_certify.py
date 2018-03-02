from __future__ import division # confidence high
from __future__ import with_statement
from __future__ import print_function
from __future__ import absolute_import

# ==================================================================================

import os
import doctest

# ==================================================================================
import numpy as np

from nose.tools import assert_raises, assert_true

# ==================================================================================

from crds.core import utils, log, exceptions
from crds import client
from crds import certify
from crds.certify import CertifyScript
from crds.certify import generic_tpn
from crds.certify import validators

from crds.tests import test_config

# ==================================================================================

class TestCertifyScript(CertifyScript):
    """Subclass TestCertifyScript to better support doctesting..."""
    def __call__(self):
        try:
            old_config = test_config.setup()
            return super(TestCertifyScript, self).__call__()
        finally:
            test_config.cleanup(old_config)

# ==================================================================================

def certify_truncated_file():
    """
    >>> doctest.ELLIPSIS_MARKER = '-ignore-'
    >>> TestCertifyScript("crds.certify data/truncated.fits --comparison-context hst.pmap")()  # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/truncated.fits' (1/1) as 'FITS' relative to context 'hst.pmap'
    -ignore-
    CRDS - WARNING -  AstropyUserWarning : astropy.io.fits.file : File may have been truncated: actual file length (7000) is smaller than the expected size (8640)
    -ignore-
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  -ignore- warnings
    CRDS - INFO -  -ignore- infos
    0
    >>> doctest.ELLIPSIS_MARKER = '...'
    """

def certify_bad_checksum():
    """
    >>> doctest.ELLIPSIS_MARKER = '-ignore-'
    >>> TestCertifyScript("crds.certify data/s7g1700gl_dead_bad_xsum.fits --run-fitsverify --comparison-context hst_508.pmap")()  # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/s7g1700gl_dead_bad_xsum.fits' (1/1) as 'FITS' relative to context 'hst_508.pmap'
    CRDS - WARNING -  AstropyUserWarning : astropy.io.fits.hdu.base : Checksum verification failed for HDU ('', 1).
    CRDS - WARNING -  AstropyUserWarning : astropy.io.fits.hdu.base : Datasum verification failed for HDU ('', 1).
    CRDS - INFO -  FITS file 's7g1700gl_dead_bad_xsum.fits' conforms to FITS standards.
    CRDS - WARNING -  AstropyUserWarning : astropy.io.fits.hdu.base : Checksum verification failed for HDU ('', 1).
    CRDS - WARNING -  AstropyUserWarning : astropy.io.fits.hdu.base : Datasum verification failed for HDU ('', 1).
    CRDS - WARNING -  AstropyUserWarning : astropy.io.fits.hdu.base : Checksum verification failed for HDU ('', 1).
    CRDS - WARNING -  AstropyUserWarning : astropy.io.fits.hdu.base : Datasum verification failed for HDU ('', 1).
    CRDS - INFO -  Running fitsverify.
    CRDS - INFO -  >>  
    CRDS - INFO -  >>               fitsverify 4.18 (CFITSIO V3.410)              
    CRDS - INFO -  >>               --------------------------------              
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  
    CRDS - INFO -  >> File: data/s7g1700gl_dead_bad_xsum.fits
    CRDS - INFO -  >> 
    CRDS - INFO -  >> 2 Header-Data Units in this file.
    CRDS - INFO -  >>  
    CRDS - INFO -  >> =================== HDU 1: Primary Array ===================
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  23 header keywords
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  Null data array; NAXIS = 0 
    CRDS - INFO -  >>  
    CRDS - INFO -  >> =================== HDU 2: BINARY Table ====================
    CRDS - INFO -  >>  
    CRDS - ERROR -  >> *** Warning: Data checksum is not consistent with  the DATASUM keyword
    CRDS - ERROR -  >> *** Warning: HDU checksum is not in agreement with CHECKSUM.
    CRDS - ERROR -  >> *** Error:   checking data fill: Data fill area invalid
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  31 header keywords
    CRDS - INFO -  >>  
    CRDS - INFO -  >>    (3 columns x 10 rows)
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  Col# Name (Units)       Format
    CRDS - INFO -  >>    1 SEGMENT              4A        
    CRDS - INFO -  >>    2 OBS_RATE (count /s / D         
    CRDS - INFO -  >>    3 LIVETIME             D         
    CRDS - INFO -  >>  
    CRDS - INFO -  >> ++++++++++++++++++++++ Error Summary  ++++++++++++++++++++++
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  HDU#  Name (version)       Type             Warnings  Errors
    CRDS - INFO -  >>  1                          Primary Array    0         0     
    CRDS - INFO -  >>  2                          Binary Table     2         1     
    CRDS - INFO -  >>  
    CRDS - INFO -  >> **** Verification found 2 warning(s) and 1 error(s). ****
    CRDS - WARNING -  Fitsverify returned a nonzero command line error status.
    CRDS - WARNING -  Fitsverify output contains errors or warnings CRDS categorizes as WARNINGs.
    CRDS - ERROR -  Fitsverify output contains errors or warnings CRDS categorizes as ERRORs.
    CRDS - INFO -  ########################################
    CRDS - INFO -  4 errors
    CRDS - INFO -  8 warnings
    CRDS - INFO -  39 infos
    4
    >>> doctest.ELLIPSIS_MARKER = '...'
    """

def certify_good_checksum():
    """
    >>> TestCertifyScript("crds.certify data/s7g1700gl_dead_good_xsum.fits --run-fitsverify --comparison-context hst_0508.pmap")() # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/s7g1700gl_dead_good_xsum.fits' (1/1) as 'FITS' relative to context 'hst_0508.pmap'
    CRDS - INFO -  FITS file 's7g1700gl_dead_good_xsum.fits' conforms to FITS standards.
    CRDS - INFO -  Running fitsverify.
    CRDS - INFO -  >>  
    CRDS - INFO -  >>               fitsverify ... (CFITSIO ...)              
    CRDS - INFO -  >>               --------------------------------              
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  
    CRDS - INFO -  >> File: data/s7g1700gl_dead_good_xsum.fits
    CRDS - INFO -  >> 
    CRDS - INFO -  >> 2 Header-Data Units in this file.
    CRDS - INFO -  >>  
    CRDS - INFO -  >> =================== HDU 1: Primary Array ===================
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  23 header keywords
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  Null data array; NAXIS = 0 
    CRDS - INFO -  >>  
    CRDS - INFO -  >> =================== HDU 2: BINARY Table ====================
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  31 header keywords
    CRDS - INFO -  >>  
    CRDS - INFO -  >>    (3 columns x 10 rows)
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  Col# Name (Units)       Format
    CRDS - INFO -  >>    1 SEGMENT              4A        
    CRDS - INFO -  >>    2 OBS_RATE (count /s / D         
    CRDS - INFO -  >>    3 LIVETIME             D         
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
    CRDS - INFO -  38 infos
    0
    """

INTERPRET_FITSVERIFY = """
Running fitsverify.
 
              fitsverify 4.18 (CFITSIO V3.370)              
              --------------------------------              
 
 
File: ./s7g1700gl_dead_bad_xsum.fits

2 Header-Data Units in this file.
 
=================== HDU 1: Primary Array ===================
 
23 header keywords

Null data array; NAXIS = 0 
 
=================== HDU 2: BINARY Table ====================
 
*** Warning: Data checksum is not consistent with  the DATASUM keyword
*** Warning: HDU checksum is not in agreement with CHECKSUM.

31 header keywords
 
   (3 columns x 10 rows)

 Col# Name (Units)       Format
   1 SEGMENT              4A        
   2 OBS_RATE (count /s / D         
   3 LIVETIME             D
 
++++++++++++++++++++++ Error Summary  ++++++++++++++++++++++
 
 HDU#  Name (version)       Type             Warnings  Errors
 1                          Primary Array    0         0     
 2                          Binary Table     2         1     
 
Verification found 2 warning(s) and 0 error(s). ****
"""

INTERPRET_FITSVERIFY2 = """
              fitsverify 4.18 (CFITSIO V3.410)              
              --------------------------------              
 
 
File: jwst_nircam_photom_nrcalong.fits

3 Header-Data Units in this file.
 
=================== HDU 1: Primary Array ===================
 
 33 header keywords
 
 Null data array; NAXIS = 0 
 
=================== HDU 2: BINARY Table ====================
 
 27 header keywords
 
 PHOTOM(1)  (8 columns x 41 rows)
 
 Col# Name (Units)       Format
   1 filter               12A       
   2 pupil                12A       
   3 order                E         
   4 photmjsr             E         
   5 uncertainty          I         
   6 nelem                I         
   7 wavelength           3000E     
   8 relresponse          3000E     
 
=================== HDU 3: Image Exten. ====================
 
*** Error:   Unregistered XTENSION value "ASDF    ".
 
 9 header keywords
 
ASDF 8-bit integer pixels,  1 axes (2880), 
 
++++++++++++++++++++++ Error Summary  ++++++++++++++++++++++
 
 HDU#  Name (version)       Type             Warnings  Errors
 1                          Primary Array    0         0     
 2     PHOTOM (1)           Binary Table     0         0     
 3     ASDF                 Image Array      0         1     
 
**** Verification found 0 warning(s) and 1 error(s). ****
"""
    
def certify_interpret_fitsverify():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")

    >>> certify.interpret_fitsverify_output(1, INTERPRET_FITSVERIFY)
    CRDS - INFO -  >> 
    CRDS - INFO -  >> Running fitsverify.
    CRDS - INFO -  >>  
    CRDS - INFO -  >>               fitsverify 4.18 (CFITSIO V3.370)              
    CRDS - INFO -  >>               --------------------------------              
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  
    CRDS - INFO -  >> File: ./s7g1700gl_dead_bad_xsum.fits
    CRDS - INFO -  >> 
    CRDS - INFO -  >> 2 Header-Data Units in this file.
    CRDS - INFO -  >>  
    CRDS - INFO -  >> =================== HDU 1: Primary Array ===================
    CRDS - INFO -  >>  
    CRDS - INFO -  >> 23 header keywords
    CRDS - INFO -  >> 
    CRDS - INFO -  >> Null data array; NAXIS = 0 
    CRDS - INFO -  >>  
    CRDS - INFO -  >> =================== HDU 2: BINARY Table ====================
    CRDS - INFO -  >>  
    CRDS - ERROR -  >> *** Warning: Data checksum is not consistent with  the DATASUM keyword
    CRDS - ERROR -  >> *** Warning: HDU checksum is not in agreement with CHECKSUM.
    CRDS - INFO -  >> 
    CRDS - INFO -  >> 31 header keywords
    CRDS - INFO -  >>  
    CRDS - INFO -  >>    (3 columns x 10 rows)
    CRDS - INFO -  >> 
    CRDS - INFO -  >>  Col# Name (Units)       Format
    CRDS - INFO -  >>    1 SEGMENT              4A        
    CRDS - INFO -  >>    2 OBS_RATE (count /s / D         
    CRDS - INFO -  >>    3 LIVETIME             D
    CRDS - INFO -  >>  
    CRDS - INFO -  >> ++++++++++++++++++++++ Error Summary  ++++++++++++++++++++++
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  HDU#  Name (version)       Type             Warnings  Errors
    CRDS - INFO -  >>  1                          Primary Array    0         0     
    CRDS - INFO -  >>  2                          Binary Table     2         1     
    CRDS - INFO -  >>  
    CRDS - INFO -  >> Verification found 2 warning(s) and 0 error(s). ****
    CRDS - WARNING -  Fitsverify returned a nonzero command line error status.
    CRDS - WARNING -  Fitsverify output contains errors or warnings CRDS categorizes as WARNINGs.
    CRDS - ERROR -  Fitsverify output contains errors or warnings CRDS categorizes as ERRORs.

    >>> certify.interpret_fitsverify_output(1, INTERPRET_FITSVERIFY2)
    CRDS - INFO -  >> 
    CRDS - INFO -  >>               fitsverify 4.18 (CFITSIO V3.410)              
    CRDS - INFO -  >>               --------------------------------              
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  
    CRDS - INFO -  >> File: jwst_nircam_photom_nrcalong.fits
    CRDS - INFO -  >> 
    CRDS - INFO -  >> 3 Header-Data Units in this file.
    CRDS - INFO -  >>  
    CRDS - INFO -  >> =================== HDU 1: Primary Array ===================
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  33 header keywords
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  Null data array; NAXIS = 0 
    CRDS - INFO -  >>  
    CRDS - INFO -  >> =================== HDU 2: BINARY Table ====================
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  27 header keywords
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  PHOTOM(1)  (8 columns x 41 rows)
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  Col# Name (Units)       Format
    CRDS - INFO -  >>    1 filter               12A       
    CRDS - INFO -  >>    2 pupil                12A       
    CRDS - INFO -  >>    3 order                E         
    CRDS - INFO -  >>    4 photmjsr             E         
    CRDS - INFO -  >>    5 uncertainty          I         
    CRDS - INFO -  >>    6 nelem                I         
    CRDS - INFO -  >>    7 wavelength           3000E     
    CRDS - INFO -  >>    8 relresponse          3000E     
    CRDS - INFO -  >>  
    CRDS - INFO -  >> =================== HDU 3: Image Exten. ====================
    CRDS - INFO -  >>  
    CRDS - WARNING -  >> *** Error:   Unregistered XTENSION value "ASDF    ".
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  9 header keywords
    CRDS - INFO -  >>  
    CRDS - INFO -  >> ASDF 8-bit integer pixels,  1 axes (2880), 
    CRDS - INFO -  >>  
    CRDS - INFO -  >> ++++++++++++++++++++++ Error Summary  ++++++++++++++++++++++
    CRDS - INFO -  >>  
    CRDS - INFO -  >>  HDU#  Name (version)       Type             Warnings  Errors
    CRDS - INFO -  >>  1                          Primary Array    0         0     
    CRDS - INFO -  >>  2     PHOTOM (1)           Binary Table     0         0     
    CRDS - INFO -  >>  3     ASDF                 Image Array      0         1     
    CRDS - INFO -  >>  
    CRDS - INFO -  >> **** Verification found 0 warning(s) and 1 error(s). ****
    CRDS - WARNING -  Fitsverify returned a nonzero command line error status.
    CRDS - WARNING -  Fitsverify output contains errors or warnings CRDS categorizes as WARNINGs.

    >>> certify.interpret_fitsverify_output(0, "")

    >>> test_config.cleanup(old_state)
    """

def certify_dump_provenance_fits():
    """
    >>> TestCertifyScript("crds.certify data/s7g1700gl_dead.fits --dump-provenance --comparison-context hst.pmap")()
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying 'data/s7g1700gl_dead.fits' (1/1) as 'FITS' relative to context 'hst.pmap'
    CRDS - INFO - FITS file 's7g1700gl_dead.fits' conforms to FITS standards.
    CRDS - INFO - [0] COMMENT = 'Created by S. Beland and IDT and P. Hodge converted to user coord.' 
    CRDS - INFO - [0] DESCRIP initial version 
    CRDS - INFO - [0] DETECTOR FUV 
    CRDS - INFO - [0] FILETYPE DEADTIME REFERENCE TABLE 
    CRDS - INFO - [0] HISTORY   Modified to account for chamge of coordinates 
    CRDS - INFO - [0] HISTORY fuv_080509_r_dead.fits renamed to s7g1700gl_dead.fits on Jul 16 2008 
    CRDS - INFO - [0] INSTRUME COS 
    CRDS - INFO - [0] PEDIGREE GROUND 16/07/2008 16/07/2010 
    CRDS - INFO - [0] USEAFTER Oct 01 1996 00:00:00 
    CRDS - INFO - [0] VCALCOS 2.0 
    CRDS - INFO - DATE-OBS = '1996-10-01'
    CRDS - INFO - TIME-OBS = '00:00:00'
    CRDS - INFO - ########################################
    CRDS - INFO - 0 errors
    CRDS - INFO - 0 warnings
    CRDS - INFO - 16 infos
    0
    """

def certify_dump_provenance_generic():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> TestCertifyScript("crds.certify data/valid.json --dump-provenance --comparison-context jwst_0034.pmap")()
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/valid.json' (1/1) as 'JSON' relative to context 'jwst_0034.pmap'
    CRDS - WARNING -  Missing suggested keyword 'META.MODEL_TYPE'
    CRDS - INFO -  EXP_TYPE = 'mir_image'
    CRDS - INFO -  META.AUTHOR = 'Todd Miller'
    CRDS - INFO -  META.DESCRIPTION = 'Brief notes on this reference.'
    CRDS - INFO -  META.EXPOSURE.READPATT = 'any'
    CRDS - INFO -  META.EXPOSURE.TYPE = 'mir_image'
    CRDS - INFO -  META.HISTORY = 'How this reference came to be and changed over time.'
    CRDS - INFO -  META.INSTRUMENT.BAND = 'medium'
    CRDS - INFO -  META.INSTRUMENT.CHANNEL = '34'
    CRDS - INFO -  META.INSTRUMENT.DETECTOR = 'mirifulong'
    CRDS - INFO -  META.INSTRUMENT.FILTER = 'UNDEFINED'
    CRDS - INFO -  META.INSTRUMENT.GRATING = 'UNDEFINED'
    CRDS - INFO -  META.INSTRUMENT.NAME = 'miri'
    CRDS - INFO -  META.INSTRUMENT.PUPIL = 'UNDEFINED'
    CRDS - INFO -  META.MODEL_TYPE = 'UNDEFINED'
    CRDS - INFO -  META.PEDIGREE = 'dummy'
    CRDS - INFO -  META.REFTYPE = 'distortion'
    CRDS - INFO -  META.SUBARRAY.FASTAXIS = '1'
    CRDS - INFO -  META.SUBARRAY.NAME = 'MASK1550'
    CRDS - INFO -  META.SUBARRAY.SLOWAXIS = '2'
    CRDS - INFO -  META.SUBARRAY.XSIZE = '1032'
    CRDS - INFO -  META.SUBARRAY.XSTART = '1'
    CRDS - INFO -  META.SUBARRAY.YSIZE = '4'
    CRDS - INFO -  META.SUBARRAY.YSTART = '1020'
    CRDS - INFO -  META.TELESCOPE = 'jwst'
    CRDS - INFO -  META.USEAFTER = '2015-01-25T12:00:00'
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  1 warnings
    CRDS - INFO -  28 infos
    0
    >>> test_config.cleanup(old_state)
    """

def certify_missing_keyword():
    """
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/missing_keyword.fits' (1/1) as 'FITS' relative to context 'hst.pmap'
    CRDS - INFO -  FITS file 'missing_keyword.fits' conforms to FITS standards.
    CRDS - ERROR -  instrument='UNKNOWN' type='UNKNOWN' data='missing_keyword.fits' ::  Checking 'DETECTOR' : Missing required keyword 'DETECTOR'
    CRDS - INFO -  ########################################
    CRDS - INFO -  1 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  4 infos
    1
    """

def certify_recursive():
    """
    >>> TestCertifyScript("crds.certify hst_cos.imap --exist --dont-parse")() # doctest: +ELLIPSIS
    CRDS - INFO -  Certification includes mappings but is not --deep, no --comparison-context is defined.
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos.imap' (1/19) as 'MAPPING' relative to context None
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_badttab.rmap' (2/19) as 'MAPPING' relative to context None
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_bpixtab.rmap' (3/19) as 'MAPPING' relative to context None
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_brftab.rmap' (4/19) as 'MAPPING' relative to context None
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_brsttab.rmap' (5/19) as 'MAPPING' relative to context None
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_deadtab.rmap' (6/19) as 'MAPPING' relative to context None
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_disptab.rmap' (7/19) as 'MAPPING' relative to context None
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_flatfile.rmap' (8/19) as 'MAPPING' relative to context None
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_fluxtab.rmap' (9/19) as 'MAPPING' relative to context None
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_geofile.rmap' (10/19) as 'MAPPING' relative to context None
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_gsagtab.rmap' (11/19) as 'MAPPING' relative to context None
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_hvtab.rmap' (12/19) as 'MAPPING' relative to context None
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_lamptab.rmap' (13/19) as 'MAPPING' relative to context None
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_phatab.rmap' (14/19) as 'MAPPING' relative to context None
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_spwcstab.rmap' (15/19) as 'MAPPING' relative to context None
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_tdstab.rmap' (16/19) as 'MAPPING' relative to context None
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_walktab.rmap' (17/19) as 'MAPPING' relative to context None
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_wcptab.rmap' (18/19) as 'MAPPING' relative to context None
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_xtractab.rmap' (19/19) as 'MAPPING' relative to context None
    CRDS - INFO - ########################################
    CRDS - INFO - 0 errors
    CRDS - INFO - 0 warnings
    CRDS - INFO - 40 infos
    0
    """

def certify_table_comparison_context():
    """
    >>> old_state = test_config.setup()

    >>> TestCertifyScript("crds.certify y951738kl_hv.fits --comparison-context hst_0294.pmap")() # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying '.../references/hst/y951738kl_hv.fits' (1/1) as 'FITS' relative to context 'hst_0294.pmap'
    CRDS - INFO -  Potential table unique row selection parameters are ['DATE']
    CRDS - INFO -  Final combination is intersection with available table columns.
    CRDS - INFO -  FITS file 'y951738kl_hv.fits' conforms to FITS standards.
    CRDS - INFO -  Comparing reference 'y951738kl_hv.fits' against 'yas2005el_hv.fits'
    CRDS - WARNING -  Table mode (('DATE', 56923.5834),) from old reference 'yas2005el_hv.fits[1]' is NOT IN new reference 'y951738kl_hv.fits[1]'
    CRDS - WARNING -  Table mode (('DATE', 56923.625),) from old reference 'yas2005el_hv.fits[1]' is NOT IN new reference 'y951738kl_hv.fits[1]'
    CRDS - WARNING -  Table mode (('DATE', 56964.0),) from old reference 'yas2005el_hv.fits[1]' is NOT IN new reference 'y951738kl_hv.fits[1]'
    CRDS - WARNING -  Table mode (('DATE', 56921.8334),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS - WARNING -  Table mode (('DATE', 56922.0),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS - WARNING -  Table mode (('DATE', 56923.5834),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS - WARNING -  Table mode (('DATE', 56923.625),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS - WARNING -  Table mode (('DATE', 56924.0417),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS - WARNING -  Table mode (('DATE', 56924.2084),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS - WARNING -  Table mode (('DATE', 56924.3125),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS - WARNING -  Table mode (('DATE', 56925.0),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS - WARNING -  Table mode (('DATE', 56959.4584),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS - WARNING -  Table mode (('DATE', 56959.6667),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS - WARNING -  Table mode (('DATE', 56961.8334),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS - WARNING -  Table mode (('DATE', 56962.8334),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  15 warnings
    CRDS - INFO -  7 infos
    0
    >>> test_config.cleanup(old_state)
    """

def certify_table_comparison_reference():
    """
    >>> TestCertifyScript("crds.certify data/y951738kl_hv.fits --comparison-reference data/y9j16159l_hv.fits")()
    CRDS - INFO -  Certifying with --comparison-reference, no default --comparison-context defined.
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/y951738kl_hv.fits' (1/1) as 'FITS' relative to context None and comparison reference 'data/y9j16159l_hv.fits'
    CRDS - INFO -  Potential table unique row selection parameters are ['DATE']
    CRDS - INFO -  Final combination is intersection with available table columns.
    CRDS - INFO -  FITS file 'y951738kl_hv.fits' conforms to FITS standards.
    CRDS - WARNING -  Table mode (('DATE', 56923.5834),) from old reference 'y9j16159l_hv.fits[1]' is NOT IN new reference 'y951738kl_hv.fits[1]'
    CRDS - WARNING -  Table mode (('DATE', 56923.625),) from old reference 'y9j16159l_hv.fits[1]' is NOT IN new reference 'y951738kl_hv.fits[1]'
    CRDS - WARNING -  Duplicate definitions in old reference 'y9j16159l_hv.fits[2]' for mode: (('DATE', 56924.0417),) :
     (129, (('DATE', 56924.0417), ('HVLEVELB', 169)))
    (131, (('DATE', 56924.0417), ('HVLEVELB', 169)))
    CRDS - WARNING -  Duplicate definitions in old reference 'y9j16159l_hv.fits[2]' for mode: (('DATE', 56925.0),) :
     (132, (('DATE', 56925.0), ('HVLEVELB', 175)))
    (134, (('DATE', 56925.0), ('HVLEVELB', 175)))
    CRDS - WARNING -  Table mode (('DATE', 56921.8334),) from old reference 'y9j16159l_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS - WARNING -  Table mode (('DATE', 56922.0),) from old reference 'y9j16159l_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS - WARNING -  Table mode (('DATE', 56923.625),) from old reference 'y9j16159l_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS - WARNING -  Table mode (('DATE', 56924.0417),) from old reference 'y9j16159l_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS - WARNING -  Table mode (('DATE', 56924.3125),) from old reference 'y9j16159l_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS - WARNING -  Table mode (('DATE', 56925.0),) from old reference 'y9j16159l_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  10 warnings
    CRDS - INFO -  7 infos
    0
    """

def certify_comparison_context_none_all_references():
    """
    >>> TestCertifyScript("crds.certify data/y951738kl_hv.fits --comparison-context None")()
    CRDS - INFO -  Comparison context explicitly specified as 'none',  no --comparison-context will be used.
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/y951738kl_hv.fits' (1/1) as 'FITS' relative to context None
    CRDS - INFO -  Potential table unique row selection parameters are ['DATE']
    CRDS - INFO -  Final combination is intersection with available table columns.
    CRDS - INFO -  FITS file 'y951738kl_hv.fits' conforms to FITS standards.
    CRDS - WARNING -  No comparison reference for 'y951738kl_hv.fits' in context None. Skipping tables comparison.
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  1 warnings
    CRDS - INFO -  7 infos
    0
    """

def certify_comparison_context_none_all_mappings():
    """
    >>> TestCertifyScript("crds.certify hst_cos_deadtab.rmap --comparison-context None")() # doctest: +ELLIPSIS
    CRDS - INFO -  Comparison context explicitly specified as 'none',  no --comparison-context will be used.
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_deadtab.rmap' (1/1) as 'MAPPING' relative to context None
    CRDS - INFO - ########################################
    CRDS - INFO - 0 errors
    CRDS - INFO - 0 warnings
    CRDS - INFO - 4 infos
    0
    """

def certify_jwst_valid():
    """
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying 'data/niriss_ref_photom.fits' (1/1) as 'FITS' relative to context None
    CRDS - INFO - FITS file 'niriss_ref_photom.fits' conforms to FITS standards.
    CRDS - WARNING - Non-compliant date format 'Jan 01 2015 00:00:00' for 'META.REFFILE.USEAFTER' should be 'YYYY-MM-DDTHH:MM:SS'
    CRDS - INFO - ########################################
    CRDS - INFO - 0 errors
    CRDS - INFO - 1 warnings
    CRDS - INFO - 4 infos
    0
    """

def certify_jwst_missing_optional_parkey():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> TestCertifyScript("crds.certify data/jwst_miri_ipc_0003.add.fits --comparison-context jwst_0125.pmap")()
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/jwst_miri_ipc_0003.add.fits' (1/1) as 'FITS' relative to context 'jwst_0125.pmap'
    CRDS - INFO -  FITS file 'jwst_miri_ipc_0003.add.fits' conforms to FITS standards.
    CRDS - INFO -  Setting 'META.INSTRUMENT.BAND'=None to value of 'P_BAND'='SHORT | MEDIUM |'
    CRDS - INFO -  Setting 'META.INSTRUMENT.DETECTOR'='MIRIMAGE' to value of 'P_DETECT'='MIRIFUSHORT|MIRIFULONG|'
    CRDS - WARNING -  Missing suggested keyword 'META.MODEL_TYPE'
    CRDS - INFO -  Checking JWST datamodels.
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  1 warnings
    CRDS - INFO -  7 infos
    0
    >>> test_config.cleanup(old_state)
    """
    
def certify_jwst_invalid_asdf():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> doctest.ELLIPSIS_MARKER = '-ignore-'
    >>> TestCertifyScript("crds.certify data/invalid.asdf  --comparison-context jwst.pmap")() # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/invalid.asdf' (1/1) as 'ASDF' relative to context 'jwst.pmap'
    -ignore-
    CRDS - ERROR -  instrument='UNKNOWN' type='UNKNOWN' data='data/invalid.asdf' ::  Validation error : -ignore- not appear -ignore- ASDF -ignore-
    CRDS - INFO -  ########################################
    CRDS - INFO -  -ignore- errors
    CRDS - INFO -  -ignore- warnings
    CRDS - INFO -  3 infos
    1
    >>> test_config.cleanup(old_state)
    >>> doctest.ELLIPSIS_MARKER = '...'
    """

def certify_jwst_invalid_json():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> TestCertifyScript("crds.certify data/invalid.json  --comparison-context jwst.pmap")()   # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/invalid.json' (1/1) as 'JSON' relative to context 'jwst.pmap'
    CRDS - ERROR -  instrument='UNKNOWN' type='UNKNOWN' data='data/invalid.json' ::  Validation error : JSON wouldn't load from 'data/invalid.json' : Expecting ... delimiter: line 5 column 1 (char 77)
    CRDS - INFO -  ########################################
    CRDS - INFO -  1 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  3 infos
    1
    >>> test_config.cleanup(old_state)
    """

def certify_jwst_invalid_yaml():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> TestCertifyScript("crds.certify data/invalid.yaml  --comparison-context jwst_0034.pmap")()
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/invalid.yaml' (1/1) as 'YAML' relative to context 'jwst_0034.pmap'
    CRDS - ERROR -  instrument='UNKNOWN' type='UNKNOWN' data='data/invalid.yaml' ::  Validation error : while scanning a tag
      in "data/invalid.yaml", line 1, column 5
    expected ' ', but found '^'
      in "data/invalid.yaml", line 1, column 21
    CRDS - INFO -  ########################################
    CRDS - INFO -  1 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  3 infos
    1
    >>> test_config.cleanup(old_state)
    """
 
def certify_test_jwst_load_all_type_constraints():
    """
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> generic_tpn.load_all_type_constraints("jwst")
    >>> test_config.cleanup(old_state)
    """

def certify_test_hst_load_all_type_constraints():
    """
    >>> old_state = test_config.setup(url="https://hst-crds-serverless.stsci.edu", observatory="hst")
    >>> generic_tpn.load_all_type_constraints("hst")
    >>> test_config.cleanup(old_state)
    """
    
def certify_validator_bad_presence_condition():
    """
    >>> old_state = test_config.setup(url="https://hst-crds-serverless.stsci.edu", observatory="hst")
    >>> info = certify.TpnInfo('DETECTOR','H','C', '(Q='BAR')', ('WFC','HRC','SBC'))
    Traceback (most recent call last):
    ...
    SyntaxError: invalid syntax
    >>> test_config.cleanup(old_state)
    """
    
def certify_JsonCertify_valid():
    """
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> certify.certify_file("data/valid.json", observatory="jwst",context="jwst_0034.pmap", trap_exceptions=False)
    CRDS - INFO -  Certifying 'data/valid.json' as 'JSON' relative to context 'jwst_0034.pmap'
    CRDS - WARNING -  Missing suggested keyword 'META.MODEL_TYPE'
    >>> test_config.cleanup(old_state)
    """
            
def certify_YamlCertify_valid():
    """
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> certify.certify_file("data/valid.yaml", observatory="jwst",context="jwst_0034.pmap", trap_exceptions=False)
    CRDS - INFO -  Certifying 'data/valid.yaml' as 'YAML' relative to context 'jwst_0034.pmap'
    CRDS - WARNING -  Missing suggested keyword 'META.MODEL_TYPE'
    >>> test_config.cleanup(old_state)
    """
            
def certify_AsdfCertify_valid():
    """
    >>> doctest.ELLIPSIS_MARKER = '-ignore-'
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> certify.certify_file("data/valid.asdf", observatory="jwst",context="jwst_0365.pmap", trap_exceptions=False) # doctest: +ELLIPSIS
    CRDS - INFO -  Certifying 'data/valid.asdf' as 'ASDF' relative to context 'jwst_0365.pmap'
    CRDS - INFO -  Setting 'META.INSTRUMENT.DETECTOR'=None to value of 'META.INSTRUMENT.P_DETECTOR'='NRS1|NRS2|'
    >>> test_config.cleanup(old_state)
    >>> doctest.ELLIPSIS_MARKER = '...'
    """
    
def certify_FitsCertify_opaque_name():
    """
    >>> old_state = test_config.setup(url="https://hst-crds-serverless.stsci.edu", observatory="hst")
    >>> certify.certify_file("data/opaque_fts.tmp", observatory="hst",context="hst.pmap", trap_exceptions=False)
    CRDS - INFO -  Certifying 'data/opaque_fts.tmp' as 'FITS' relative to context 'hst.pmap'
    >>> test_config.cleanup(old_state)
    """
    
def certify_AsdfCertify_opaque_name():
    """
    >>> doctest.ELLIPSIS_MARKER = '-ignore-'
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> certify.certify_file("data/opaque_asd.tmp", observatory="jwst",context="jwst_0365.pmap", trap_exceptions=False) # doctest: +ELLIPSIS
    CRDS - INFO -  Certifying 'data/opaque_asd.tmp' as 'ASDF' relative to context 'jwst_0365.pmap'
    CRDS - INFO -  Setting 'META.INSTRUMENT.DETECTOR'=None to value of 'META.INSTRUMENT.P_DETECTOR'='NRS1|NRS2|'
    >>> test_config.cleanup(old_state)
    >>> doctest.ELLIPSIS_MARKER = '...'
    """

def certify_rmap_compare():
    """
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> certify.certify_file("jwst_miri_distortion_0025.rmap", context="jwst_0357.pmap")
    CRDS - INFO -  Certifying 'jwst_miri_distortion_0025.rmap' as 'MAPPING' relative to context 'jwst_0357.pmap'
    >>> test_config.cleanup(old_state)
    """

def certify_jwst_bad_fits():
    """
    
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> doctest.ELLIPSIS_MARKER = '-ignore-'
    >>> certify.certify_file("data/niriss_ref_photom_bad.fits", observatory="jwst", context=None) # doctest: +ELLIPSIS
    CRDS - INFO -  Certifying 'data/niriss_ref_photom_bad.fits' as 'FITS' relative to context None
    CRDS - INFO -  Potential table unique row selection parameters are ['FILTER', 'PUPIL', 'ORDER']
    CRDS - INFO -  Final combination is intersection with available table columns.
    CRDS - INFO -  FITS file 'niriss_ref_photom_bad.fits' conforms to FITS standards.
    CRDS - ERROR -  In 'niriss_ref_photom_bad.fits' : Missing required array 'PHOTOM'
    CRDS - ERROR -  In 'niriss_ref_photom_bad.fits' : Checking 'META.INSTRUMENT.DETECTOR' : Value 'FOO' is not one of ['ANY', 'N/A', 'NIS']
    CRDS - WARNING -  Missing suggested keyword 'META.MODEL_TYPE'
    CRDS - WARNING -  Non-compliant date format 'Jan 01 2015 00:00:00' for 'META.USEAFTER' should be 'YYYY-MM-DDTHH:MM:SS'
    CRDS - WARNING -  No comparison reference for 'niriss_ref_photom_bad.fits' in context None. Skipping tables comparison.
    CRDS - INFO -  Checking JWST datamodels.
    CRDS - ERROR -  data/niriss_ref_photom_bad.fits Validation error : JWST Data Models: 'FOO' is not one of ['NRCA1', 'NRCA2', 'NRCA3', 'NRCA4', 'NRCALONG', 'NRCB1', 'NRCB2', 'NRCB3', 'NRCB4', 'NRCBLONG', 'NRS1', 'NRS2', 'ANY', 'MIRIMAGE', 'MIRIFULONG', 'MIRIFUSHORT', 'NIS', 'GUIDER1', 'GUIDER2', 'N/A']
    <BLANKLINE>
    Failed validating 'enum' in schema:
        {'$schema': 'http://stsci.edu/schemas/asdf-schema/0.1.0/asdf-schema',
         'description': 'Detector name.',
         'enum': ['NRCA1',
                  'NRCA2',
                  'NRCA3',
                  'NRCA4',
                  'NRCALONG',
                  'NRCB1',
                  'NRCB2',
                  'NRCB3',
                  'NRCB4',
                  'NRCBLONG',
                  'NRS1',
                  'NRS2',
                  'ANY',
                  'MIRIMAGE',
                  'MIRIFULONG',
                  'MIRIFUSHORT',
                  'NIS',
                  'GUIDER1',
                  'GUIDER2',
                  'N/A'],
         'fits_keyword': 'DETECTOR',
         'title': 'Name of detector used to acquire the data',
         'type': 'string'}
    <BLANKLINE>
    On instance:
        'FOO'
    >>> doctest.ELLIPSIS_MARKER = '...'
    >>> test_config.cleanup(old_state)
    """

def certify_duplicate_rmap_case_error():
    """
    >>> old_state = test_config.setup(url="https://hst-crds-serverless.stsci.edu", observatory="hst")
    >>> certify.certify_file("data/hst_cos_tdstab_duplicate.rmap", observatory="hst")
    CRDS - INFO -  Certifying 'data/hst_cos_tdstab_duplicate.rmap' as 'MAPPING' relative to context None
    CRDS - ERROR -  Duplicate entry at selector ('FUV', 'SPECTROSCOPIC') = UseAfter vs. UseAfter
    CRDS - WARNING -  Checksum error : sha1sum mismatch in 'hst_cos_tdstab_duplicate.rmap'
    >>> test_config.cleanup(old_state)
    """

    
def checksum_duplicate_rmap_case_error():
    """
    Verify that the crds rmap checksum update tool does not silently drop duplicate rmap entries
    when updating the checksum and rewriting the file.

    >>> from crds.refactoring import checksum
    >>> old_state = test_config.setup(url="https://hst-crds-serverless.stsci.edu", observatory="hst")
    >>> checksum.add_checksum("data/hst_cos_tdstab_duplicate.rmap")
    CRDS - INFO -  Adding checksum for 'data/hst_cos_tdstab_duplicate.rmap'
    CRDS - ERROR -  Duplicate entry at selector ('FUV', 'SPECTROSCOPIC') = UseAfter vs. UseAfter
    >>> test_config.cleanup(old_state)
    """

def undefined_expr_identifiers():
    """Some TpnInfos include Python expressions either to make them apply conditionally or to
    implement and expression constraint.   validators.expr_identifiers() scans a Tpn header
    expression for the header keywords upon which it depends.   This enables CRDS To short
    circuit checks for which critical keywords are not defined at all.
    
    >>> validators.expr_identifiers("((EXP_TYPE)in(['NRS_MSASPEC','NRS_FIXEDSLIT','NRS_BRIGHTOBJ','NRS_IFU']))")
    ['EXP_TYPE']
    
    >>> validators.expr_identifiers("nir_filter(INSTRUME,REFTYPE,EXP_TYPE)")
    ['INSTRUME', 'REFTYPE', 'EXP_TYPE']
    
    >>> validators.expr_identifiers("(len(SCI_ARRAY.SHAPE)==2)")
    ['SCI_ARRAY']
    """

# ==================================================================================

class TestHSTTpnInfoClass(test_config.CRDSTestCase):

    def setUp(self, *args, **keys):
        super(TestHSTTpnInfoClass, self).setUp(*args, **keys)
        hstlocator = utils.get_locator_module("hst")
        self.tpninfos = hstlocator.get_all_tpninfos("acs","idctab","tpn")
        self.validators = [certify.validator(info) for info in self.tpninfos]
        client.set_crds_server('https://crds-serverless-mode.stsci.edu')
        os.environ['CRDS_MAPPATH'] = self.hst_mappath
        os.environ['CRDS_PATH'] = "/grp/crds/hst"
        os.environ["CRDS_CONTEXT"] ="hst.pmap"

    def test_character_validator(self):
        assert self.validators[2].check(self.data('acs_new_idc.fits'))

    def test_column_validator(self):
        assert self.validators[-2].check(self.data('acs_new_idc.fits'))

# ==================================================================================

class TestCertify(test_config.CRDSTestCase):

    def setUp(self, *args, **keys):
        super(TestCertify, self).setUp(*args, **keys)
        self._old_debug = log.set_exception_trap(False)

    def tearDown(self, *args, **keys):
        super(TestCertify, self).tearDown(*args, **keys)
        log.set_exception_trap(self._old_debug)
        
    # ------------------------------------------------------------------------------
        
    def test_validator_bad_presence(self):
        tinfo = certify.TpnInfo('DETECTOR','H','C','Q', ('WFC','HRC','SBC'))
        assert_raises(ValueError, certify.validator, tinfo)
        
    def test_validator_bad_keytype(self):
        tinfo = certify.TpnInfo('DETECTOR','Q','C','R', ('WFC','HRC','SBC'))
        assert_raises(ValueError, certify.validator, tinfo)

    def test_character_validator_file_good(self):
        tinfo = certify.TpnInfo('DETECTOR','H','C','R', ('WFC','HRC','SBC'))
        cval = certify.validator(tinfo)
        assert_true(isinstance(cval, certify.CharacterValidator))
        cval.check(self.data('acs_new_idc.fits'))

    def test_character_validator_bad(self):
        tinfo = certify.TpnInfo('DETECTOR','H','C','R', ('WFC','HRC','SBC'))
        cval = certify.validator(tinfo)
        assert_true(isinstance(cval, certify.CharacterValidator))
        header = {"DETECTOR" : "WFD" }
        assert_raises(ValueError, cval.check, "foo.fits", header)

    def test_character_validator_missing_required(self):
        tinfo = certify.TpnInfo('DETECTOR','H','C','R', ('WFC','HRC','SBC'))
        cval = certify.validator(tinfo)
        assert_true(isinstance(cval, certify.CharacterValidator))
        header = {"DETECTOR" : "WFD" }
        assert_raises(ValueError, cval.check, "foo.fits", header)

    def test_character_validator_optional_bad(self):
        tinfo = certify.TpnInfo('DETECTOR','H','C','O', ('WFC','HRC','SBC'))
        cval = certify.validator(tinfo)
        assert_true(isinstance(cval, certify.CharacterValidator))
        header = {"DETECTOR" : "WFD" }
        assert_raises(ValueError, cval.check, "foo.fits", header)

    def test_character_validator_optional_missing(self):
        tinfo = certify.TpnInfo('DETECTOR','H','C','O', ('WFC','HRC','SBC'))
        cval = certify.validator(tinfo)
        assert_true(isinstance(cval, certify.CharacterValidator))
        header = {"DETECTR" : "WFC" }
        cval.check("foo.fits", header)

    # ------------------------------------------------------------------------------
        
    def test_logical_validator_good(self):
        tinfo = certify.TpnInfo('ROKIN','H','L','R',())
        cval = certify.validator(tinfo)
        assert_true(isinstance(cval, certify.LogicalValidator))
        header= {"ROKIN": "F"}
        cval.check("foo.fits", header)
        header= {"ROKIN": "T"}
        cval.check("foo.fits", header)

    def test_logical_validator_bad(self):
        tinfo = certify.TpnInfo('ROKIN','H','L','R',())
        cval = certify.validator(tinfo)
        assert_true(isinstance(cval, certify.LogicalValidator))
        header = {"ROKIN" : "True"}
        assert_raises(ValueError, cval.check, "foo.fits", header)
        header = {"ROKIN" : "False"}
        assert_raises(ValueError, cval.check, "foo.fits", header)
        header = {"ROKIN" : "1"}
        assert_raises(ValueError, cval.check, "foo.fits", header)
        header = {"ROKIN" : "0"}
        assert_raises(ValueError, cval.check, "foo.fits", header)

    # ------------------------------------------------------------------------------
        
    def test_integer_validator_bad_format(self):
        info = certify.TpnInfo('READPATT', 'H', 'I', 'R', ('FOO',))
        assert_raises(ValueError, certify.validator, info)
        info = certify.TpnInfo('READPATT', 'H', 'I', 'R', ('1.0','2.0'))
        assert_raises(ValueError, certify.validator, info)

    def test_integer_validator_bad_float(self):
        info = certify.TpnInfo('READPATT', 'H', 'I', 'R', ('1','2'))
        cval = certify.validator(info)
        assert_true(isinstance(cval, certify.IntValidator))
        header = {"READPATT": "1.9"}
        assert_raises(ValueError, cval.check, "foo.fits", header)

    def test_integer_validator_bad_value(self):
        info = certify.TpnInfo('READPATT', 'H', 'I', 'R', ('1','2','3'))
        cval = certify.validator(info)
        assert_true(isinstance(cval, certify.IntValidator))
        header = {"READPATT": "4"}
        assert_raises(ValueError, cval.check, "foo.fits", header)

    def test_integer_validator_good(self):
        info = certify.TpnInfo('READPATT', 'H', 'I', 'R', ('1','2','3'))
        cval = certify.validator(info)
        assert_true(isinstance(cval, certify.IntValidator))
        header = {"READPATT": "2"}
        cval.check("foo.fits", header)

    def test_integer_validator_range_good(self):
        info = certify.TpnInfo('READPATT', 'H', 'I', 'R', ("1:40",))
        cval = certify.validator(info)
        assert_true(isinstance(cval, certify.IntValidator))
        header = {"READPATT": "39"}
        cval.check("foo.fits", header)

    def test_integer_validator_range_bad(self):
        info = certify.TpnInfo('READPATT', 'H', 'I', 'R', ("1:40",))
        cval = certify.validator(info)
        assert_true(isinstance(cval, certify.IntValidator))
        header = {"READPATT": "41"}
        assert_raises(ValueError, cval.check, "foo.fits", header)
 
    def test_integer_validator_range_boundary_good(self):
        info = certify.TpnInfo('READPATT', 'H', 'I', 'R', ("1:40",))
        cval = certify.validator(info)
        assert_true(isinstance(cval, certify.IntValidator))
        header = {"READPATT": "40"}
        cval.check("foo.fits", header)
 
    def test_integer_validator_range_format_bad(self):
        info = certify.TpnInfo('READPATT', 'H', 'I', 'R', ("1:40",))
        cval = certify.validator(info)
        assert_true(isinstance(cval, certify.IntValidator))
        header = {"READPATT": "40.3"}
        assert_raises(ValueError, cval.check, "foo.fits", header)
        info = certify.TpnInfo('READPATT', 'H', 'I', 'R', ("x:40",))
        assert_raises(ValueError, certify.validator, info)
 
    # ------------------------------------------------------------------------------
        
    def test_real_validator_bad_format(self):
        info = certify.TpnInfo('READPATT', 'H', 'R', 'R', ('FOO',))
        assert_raises(ValueError, certify.validator, info)
        info = certify.TpnInfo('READPATT', 'H', 'R', 'R', ('x.0','2.0'))
        assert_raises(ValueError, certify.validator, info)

    def test_real_validator_bad_value(self):
        info = certify.TpnInfo('READPATT', 'H', 'R', 'R', ('1.1','2.2','3.3'))
        cval = certify.validator(info)
        assert_true(isinstance(cval, certify.RealValidator))
        header = {"READPATT": "3.2"}
        assert_raises(ValueError, cval.check, "foo.fits", header)

    def test_real_validator_good(self):
        info = certify.TpnInfo('READPATT', 'H', 'R', 'R', ('1.0','2.1','3.0'))
        cval = certify.validator(info)
        assert_true(isinstance(cval, certify.RealValidator))
        header = {"READPATT": "2.1"}
        cval.check("foo.fits", header)

    def test_real_validator_range_good(self):
        info = certify.TpnInfo('READPATT', 'H', 'R', 'R', ("1.5:40.2",))
        cval = certify.validator(info)
        assert_true(isinstance(cval, certify.RealValidator))
        header = {"READPATT": "40.1"}
        cval.check("foo.fits", header)

    def test_real_validator_range_bad(self):
        info = certify.TpnInfo('READPATT', 'H', 'R', 'R', ("1.5:40.2",))
        cval = certify.validator(info)
        assert_true(isinstance(cval, certify.RealValidator))
        header = {"READPATT": "40.21"}
        assert_raises(ValueError, cval.check, "foo.fits", header)
 
    def test_real_validator_range_boundary_good(self):
        info = certify.TpnInfo('READPATT', 'H', 'R', 'R', ("1.4:40.1",))
        cval = certify.validator(info)
        assert_true(isinstance(cval, certify.RealValidator))
        header = {"READPATT": "40.1"}
        cval.check("foo.fits", header)
 
    def test_real_validator_range_format_bad(self):
        info = certify.TpnInfo('READPATT', 'H', 'R', 'R', ("1.5:40.2",))
        cval = certify.validator(info)
        assert_true(isinstance(cval, certify.RealValidator))
        header = {"READPATT": "40.x"}
        assert_raises(ValueError, cval.check, "foo.fits", header)
        info = certify.TpnInfo('READPATT', 'H', 'R', 'R', ("1.x:40.2",))
        assert_raises(ValueError, certify.validator, info)
 
    def test_real_validator_float_zero(self):
        info = certify.TpnInfo('READPATT', 'H', 'R', 'R', ('1','0.0'))
        cval = certify.validator(info)
        assert_true(isinstance(cval, certify.RealValidator))
        header = {"READPATT": "0.0001"}
        assert_raises(ValueError, cval.check, "foo.fits", header)

    def test_real_validator_float_zero_zero(self):
        info = certify.TpnInfo('READPATT', 'H', 'R', 'R', ('1','0.0'))
        cval = certify.validator(info)
        assert_true(isinstance(cval, certify.RealValidator))
        header = {"READPATT": "0.0003"}
        assert_raises(ValueError, cval.check, "foo.fits", header)

    # ------------------------------------------------------------------------------
        
    def test_double_validator_bad_format(self):
        info = certify.TpnInfo('READPATT', 'H', 'D', 'R', ('FOO',))
        assert_raises(ValueError, certify.validator, info)
        info = certify.TpnInfo('READPATT', 'H', 'D', 'R', ('x.0','2.0'))
        assert_raises(ValueError, certify.validator, info)

    def test_double_validator_bad_value(self):
        info = certify.TpnInfo('READPATT', 'H', 'D', 'R', ('1.1','2.2','3.3'))
        cval = certify.validator(info)
        assert_true(isinstance(cval, certify.DoubleValidator))
        header = {"READPATT": "3.2"}
        assert_raises(ValueError, cval.check, "foo.fits", header)

    def test_double_validator_good(self):
        info = certify.TpnInfo('READPATT', 'H', 'D', 'R', ('1.0','2.1','3.0'))
        cval = certify.validator(info)
        assert_true(isinstance(cval, certify.DoubleValidator))
        header = {"READPATT": "2.1"}
        cval.check("foo.fits", header)

    def test_double_validator_range_good(self):
        info = certify.TpnInfo('READPATT', 'H', 'D', 'R', ("1.5:40.2",))
        cval = certify.validator(info)
        assert_true(isinstance(cval, certify.DoubleValidator))
        header = {"READPATT": "40.1"}
        cval.check("foo.fits", header)

    def test_double_validator_range_bad(self):
        info = certify.TpnInfo('READPATT', 'H', 'D', 'R', ("1.5:40.2",))
        cval = certify.validator(info)
        assert_true(isinstance(cval, certify.DoubleValidator))
        header = {"READPATT": "40.21"}
        assert_raises(ValueError, cval.check, "foo.fits", header)
 
    def test_double_validator_range_boundary_good(self):
        info = certify.TpnInfo('READPATT', 'H', 'D', 'R', ("1.4:40.1",))
        cval = certify.validator(info)
        assert_true(isinstance(cval, certify.DoubleValidator))
        header = {"READPATT": "40.1"}
        cval.check("foo.fits", header)
 
    def test_double_validator_range_format_bad(self):
        info = certify.TpnInfo('READPATT', 'H', 'D', 'R', ("1.5:40.2",))
        cval = certify.validator(info)
        assert_true(isinstance(cval, certify.DoubleValidator))
        header = {"READPATT": "40.x"}
        assert_raises(ValueError, cval.check, "foo.fits", header)
        info = certify.TpnInfo('READPATT', 'H', 'D', 'R', ("1.x:40.2",))
        assert_raises(ValueError, certify.validator, info)
 
    # ------------------------------------------------------------------------------
        
    def test_expression_validator_passes(self):
        tinfo = certify.TpnInfo('DETECTOR','X','X','R', ('((DETECTOR=="FOO")and(SUBARRAY=="BAR"))',))
        cval = certify.validator(tinfo)
        assert_true(isinstance(cval, certify.ExpressionValidator))
        header = { "DETECTOR":"FOO", "SUBARRAY":"BAR" }
        cval.check("foo.fits", header)

    def test_expression_validator_fails(self):
        tinfo = certify.TpnInfo('DETECTOR','X','X','R', ('((DETECTOR=="FOO")and(SUBARRAY=="BAR"))',))
        cval = certify.validator(tinfo)
        assert_true(isinstance(cval, certify.ExpressionValidator))
        header = { "DETECTOR":"FOO", "SUBARRAY":"BA" }
        assert_raises(certify.RequiredConditionError, cval.check, "foo.fits", header)

    def test_expression_validator_bad_format(self):
        # typical subtle expression error, "=" vs. "=="
        tinfo = certify.TpnInfo('DETECTOR','X','X','R', ('((DETECTOR="FOO")and(SUBARRAY=="BAR"))',))
        assert_raises(SyntaxError, certify.validator, tinfo)

    # ------------------------------------------------------------------------------
        
    def test_conditionally_required_bad_format(self):
        # typical subtle expression error, "=" vs. "=="
        tinfo = certify.TpnInfo('DETECTOR','X', 'X', '(SUBARRAY="BAR")', ("FOO","BAR","BAZ"))
        assert_raises(SyntaxError, certify.validator, tinfo)

    def test_conditionally_required_good(self):
        # typical subtle expression error, "=" vs. "=="
        tinfo = certify.TpnInfo('DETECTOR','H', 'C', '(SUBARRAY=="BAR")', ("FOO","BAR","BAZ"))
        cval = certify.validator(tinfo)
        header = { "DETECTOR" : "FOO", "SUBARRAY":"BAR" }
        cval.check("foo.fits", header)

    def test_conditionally_required_bad(self):
        # typical subtle expression error, "=" vs. "=="
        tinfo = certify.TpnInfo('DETECTOR','H', 'C', '(SUBARRAY=="BAR")', ("FOO","BAR","BAZ"))
        checker = certify.validator(tinfo)
        header = { "DETECTOR" : "FRODO", "SUBARRAY":"BAR" }
        assert_raises(ValueError, checker.check, "foo.fits", header)

    def test_conditionally_not_required(self):
        # typical subtle expression error, "=" vs. "=="
        tinfo = certify.TpnInfo('DETECTOR','H', 'C', '(SUBARRAY=="BAR")', ("FOO","BAR","BAZ"))
        checker = certify.validator(tinfo)
        header = { "DETECTOR" : "FRODO", "SUBARRAY":"BAZ" }
        checker.check("foo.fits", header)

    def test_not_conditionally_required(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('DETECTOR','H', 'C', 'R', ("FOO","BAR","BAZ"))
        checker = certify.validator(info)
        assert_true(not checker.conditionally_required)  #
        
    def test_tpn_bad_presence(self):
        try:
            certify.TpnInfo('DETECTOR','H', 'C', 'Q', ("FOO","BAR","BAZ"))
        except ValueError as exc:
            assert_true("presence" in str(exc), "Wrong exception for test_tpn_bad_presence")

    def test_tpn_bad_group_keytype(self):
        info = certify.TpnInfo('DETECTOR','G', 'C', 'R', ("FOO","BAR","BAZ"))
        checker = certify.validator(info)
        warns = log.warnings()
        checker.check("test.fits", {"DETECTOR":"FOO"})
        new_warns = log.warnings()
        assert_true(new_warns - warns >= 1, "No warning issued for unsupported group .tpn constraint type.")
        
    def test_tpn_repr(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('DETECTOR','H', 'C', 'R', ("FOO","BAR","BAZ"))
        repr(certify.Validator(info))
 
    def test_tpn_check_value_method_not_implemented(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('DETECTOR','H', 'C', 'R', ("FOO","BAR","BAZ"))
        checker = certify.Validator(info)
        assert_raises(NotImplementedError, checker.check, "test.fits", header={"DETECTOR":"FOO"})

    def test_tpn_handle_missing(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('DETECTOR','H', 'C', 'W', ("FOO","BAR","BAZ"))
        checker = certify.validator(info)
        assert_true(checker._handle_missing(header={"READPATT":"FOO"}) == "UNDEFINED")
        info = certify.TpnInfo('DETECTOR','H', 'C', 'S', ("FOO","BAR","BAZ"))
        checker = certify.validator(info)
        assert_true(checker._handle_missing(header={"READPATT":"FOO"}) == "UNDEFINED")
        info = certify.TpnInfo('DETECTOR','H', 'C', 'F', ("FOO","BAR","BAZ"))
        checker = certify.validator(info)
        assert_true(checker._handle_missing(header={"READPATT":"FOO"}) == "UNDEFINED")        

    def test_tpn_handle_missing_conditional(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('DETECTOR','H', 'C', '(READPATT=="FOO")', ("FOO","BAR","BAZ"))
        checker = certify.validator(info)
        assert_raises(certify.MissingKeywordError, checker._handle_missing, header={"READPATT":"FOO"})
        assert_true(checker._handle_missing(header={"READPATT":"BAR"}) == "UNDEFINED")
        

    def test_missing_column_validator(self):
        info = certify.TpnInfo('FOO','C', 'C', 'R', ("X","Y","Z"))
        checker = certify.validator(info)
        assert_raises(certify.MissingKeywordError, checker.check, self.data("v8q14451j_idc.fits"), 
                      header={"DETECTOR":"IRRELEVANT"})

    def test_tpn_excluded_keyword(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('DETECTOR','H', 'C', 'E', ())
        checker = certify.validator(info)
        assert_raises(certify.IllegalKeywordError, checker.get_header_value, {"DETECTOR":"SHOULDNT_DEFINE"})

    def test_tpn_not_value(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('SUBARRAY','H', 'C', 'R', ["NOT_GENERIC"])
        checker = certify.validator(info)
        assert_raises(ValueError, checker.check, "test.fits", {"SUBARRAY":"GENERIC"})

    def test_tpn_or_bar_value(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('DETECTOR','H', 'C', 'R', ["THIS","THAT","OTHER"])
        checker = certify.validator(info)
        checker.check("test.fits", {"DETECTOR":"THAT|THIS"})
                
        info = certify.TpnInfo('DETECTOR','H', 'C', 'R', ["THAT","OTHER"])
        checker = certify.validator(info)
        assert_raises(ValueError, checker.check, "test.fits", {"DETECTOR":"THAT|THIS"})

    def test_tpn_esoteric_value(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('DETECTOR','H', 'C', 'R', ["([abc]+)","BETWEEN_300_400","#OTHER#"])
        checker = certify.validator(info)
        checker.check("test.fits", {"DETECTOR":"([abc]+)"})
        assert_raises(ValueError, checker.check, "test.fits", {"DETECTOR": "([def]+)"})
                                    
        info = certify.TpnInfo('DETECTOR','H', 'C', 'R', ["{.*1234}","BETWEEN_300_400","#OTHER#"])
        checker = certify.validator(info)
        checker.check("test.fits", {"DETECTOR":"{.*1234}"})
                                    
        info = certify.TpnInfo('DETECTOR','H', 'C', 'R', ["(THIS)","BETWEEN_300_400","#OTHER#"])
        checker = certify.validator(info)
        checker.check("test.fits", {"DETECTOR":"BETWEEN_300_400"})

        info = certify.TpnInfo('DETECTOR','H', 'C', 'R', ["# >1 and <37 #","BETWEEN_300_400","#OTHER#"])
        checker = certify.validator(info)
        checker.check("test.fits", {"DETECTOR":"# >1 and <37 #"})

        # This demos synatax/check for "NOT FOO" in rmap match tuples
        info = certify.TpnInfo('DETECTOR','H', 'C', 'R', ["NOT_FOO","BETWEEN_300_400","#OTHER#"])
        checker = certify.validator(info)
        checker.check("test.fits", {"DETECTOR":"NOT_FOO"})                           
                                    
    def test_tpn_pedigree_missing(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = certify.validator(info)
        assert_raises(certify.MissingKeywordError, 
            checker.check, "test.fits", {"DETECTOR":"This is a test"})

    def test_tpn_pedigree_dummy(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = certify.validator(info)
        checker.check("test.fits", {"PEDIGREE":"DUMMY"})

    def test_tpn_pedigree_ground(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = certify.validator(info)
        checker.check("test.fits", {"PEDIGREE":"GROUND"})

    def test_tpn_pedigree_simulation(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = certify.validator(info)
        checker.check("test.fits", {"PEDIGREE":"SIMULATION"})

    def test_tpn_pedigree_bad_leading(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = certify.validator(info)
        assert_raises(ValueError, checker.check, "test.fits", {"PEDIGREE":"xDUMMY"})

    def test_tpn_pedigree_bad_trailing(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = certify.validator(info)
        assert_raises(ValueError, checker.check, "test.fits", {"PEDIGREE":"DUMMYxyz"})

    def test_tpn_pedigree_inflight_no_date(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = certify.validator(info)
        checker.check("test.fits", {"PEDIGREE":"INFLIGHT"})

    def test_tpn_pedigree_equal_start_stop(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = certify.validator(info)
        checker.check("test.fits", {"PEDIGREE":"INFLIGHT 02/01/2017 02/01/2017"})

    def test_tpn_pedigree_bad_datetime_order(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = certify.validator(info)
        assert_raises(ValueError, checker.check, "test.fits", {"PEDIGREE":"INFLIGHT 2017-01-02 2017-01-01"})

    def test_tpn_pedigree_good_datetime_slash(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = certify.validator(info)
        checker.check("test.fits", {"PEDIGREE":"INFLIGHT 02/01/2017 03/01/2017"})

    def test_tpn_pedigree_bad_datetime_slash(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = certify.validator(info)
        assert_raises(ValueError, checker.check, "test.fits", {"PEDIGREE":"INFLIGHT 02/25/2017 03/01/2017"})

    def test_tpn_pedigree_good_datetime_dash(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = certify.validator(info)
        checker.check("test.fits", {"PEDIGREE":"INFLIGHT 2017-01-01 2017-01-02"})

    def test_tpn_pedigree_bad_datetime_dash(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = certify.validator(info)
        assert_raises(ValueError, checker.check, "test.fits", {"PEDIGREE":"INFLIGHT 2017-01-01 01-02-2017"})

    def test_tpn_pedigree_good_datetime_dash_dash(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = certify.validator(info)
        checker.check("test.fits", {"PEDIGREE":"INFLIGHT 2017-01-01 - 2017-01-02"})
        
    def test_tpn_pedigree_bad_datetime_format_1(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = certify.validator(info)
        assert_raises(ValueError, checker.check, "test.fits", 
                      {"PEDIGREE":"INFLIGHT 2017-01-01 - 2017-01-02 -"})
        
    def test_tpn_pedigree_bad_datetime_format_2(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = certify.validator(info)
        assert_raises(ValueError, checker.check, 
                      "test.fits", {"PEDIGREE":"INFLIGHT 2017-01-01 - 2017/01/02"})
        
    def test_tpn_pedigree_bad_datetime_format_3(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = certify.validator(info)
        assert_raises(ValueError, checker.check, 
                      "test.fits", {"PEDIGREE":"INFLIGHT 2017-01-01T00:00:00 2017-01-02"})
        
    def test_tpn_pedigree_missing_column(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('PEDIGREE','C', 'C', 'R', ["&PEDIGREE"])
        checker = certify.validator(info)
        assert_raises(certify.MissingKeywordError, checker.check_column, "data/x2i1559gl_wcp.fits")

    def test_tpn_pedigree_ok_column(self):
        # typical subtle expression error, "=" vs. "=="
        info = certify.TpnInfo('PEDIGREE','C', 'C', 'R', ["&PEDIGREE"])
        checker = certify.validator(info)
        checker.check_column("data/16j16005o_apd.fits")
        
# ------------------------------------------------------------------------------
        
    def test_sybdate_validator(self):
        tinfo = certify.TpnInfo('USEAFTER','H','C','R',('&SYBDATE',))
        cval = certify.validator(tinfo)
        assert_true(isinstance(cval,certify.SybdateValidator))
        cval.check(self.data('acs_new_idc.fits'))

    def test_slashdate_validator(self):
        tinfo = certify.TpnInfo('USEAFTER','H','C','R',('&SLASHDATE',))
        checker = certify.validator(tinfo)
        checker.check("test.fits", {"USEAFTER":"25/12/2016"})
        assert_raises(ValueError, checker.check, "test.fits", {"USEAFTER":"2017-12-25"})

    def test_Anydate_validator(self):
        tinfo = certify.TpnInfo('USEAFTER','H','C','R',('&ANYDATE',))
        checker = certify.validator(tinfo)
        checker.check("test.fits", {"USEAFTER":"25/12/2016"})
        checker.check("test.fits", {"USEAFTER":"Mar 21 2001 12:00:00 am"})
        assert_raises(ValueError, checker.check, "test.fits", {"USEAFTER":"2017-01-01T00:00:00.000"})
        assert_raises(ValueError, checker.check, "test.fits", {"USEAFTER":"12-25-2017"})
        assert_raises(ValueError, checker.check, "test.fits", {"USEAFTER":"Mxx 21 2001 01:00:00 PM"})
        assert_raises(ValueError, checker.check, "test.fits", {"USEAFTER":"35/12/20117"})

# ------------------------------------------------------------------------------

    def certify_rmap_missing_parkey(self):
        certify.certify_files([self.data("hst_missing_parkey.rmap")], observatory="hst")
    
    def certify_no_corresponding_rmap(self):
        certify.certify_files([self.data("acs_new_idc.fits")], observatory="hst", context="hst.pmap")  
  
    def certify_missing_provenance(self):
        certify.certify_files([self.data("acs_new_idc.fits")], observatory="hst", context="hst.pmap",
                              dum_provenance=True, provenance=["GAIN"])  
    
# ------------------------------------------------------------------------------
    def test_check_dduplicates(self):
        certify.certify_files([self.data("hst.pmap")], observatory="hst")
        certify.certify_files([self.data("hst_acs.imap")], observatory="hst")
        certify.certify_files([self.data("hst_acs_darkfile.rmap")], observatory="hst")
        
    def test_check_comment(self):
        certify.certify_files([self.data("hst.pmap")], observatory="hst")
        certify.certify_files([self.data("hst_acs.imap")], observatory="hst")
        certify.certify_files([self.data("hst_acs_darkfile_comment.rmap")], observatory="hst")
        
    def test_table_mode_checks_identical(self):
        certify.certify_files([self.data("v8q14451j_idc.fits")], observatory="hst", 
                              context="hst.pmap", compare_old_reference=True)

    def test_table_mode_checks_missing_modes(self):
        certify.certify_files([self.data("v8q1445xx_idc.fits")], observatory="hst", 
                              context="hst.pmap", compare_old_reference=True)
        
    def test_UnknownCertifier_missing(self):
        assert_raises(certify.InvalidFormatError, certify.certify_file, 
            self.data("non-existent-file.txt"), observatory="jwst", context="jwst.pmap", trap_exceptions="test")
        
    def test_FitsCertify_bad_value(self):
        assert_raises(ValueError, certify.certify_file,
            self.data("s7g1700gm_dead_broken.fits"), observatory="hst", context="hst.pmap", trap_exceptions=False)
        
    # ------------------------------------------------------------------------------
        
    # def test_certify_deep_sync(self):
    #     script = certify.CertifyScript(
    #         "crds.certify --deep --comparison-context hst_0317.pmap zbn1927fl_gsag.fits --sync-files")
    #     errors = script()
    #     assert_true(errors == 0)
        
    # def test_certify_sync_comparison_reference(self):
    #     script = certify.CertifyScript(
    #         "crds.certify --comparison-reference zbn1927fl_gsag.fits zbn1927fl_gsag.fits --sync-files")
    #     script()
        
    def test_certify_dont_recurse_mappings(self):
        script = certify.CertifyScript("crds.certify hst_0317.pmap --dont-recurse-mappings")
        errors = script()
        
    def test_certify_kernel_unity_validator_good(self):
        header = {'SCI_ARRAY': utils.Struct({'COLUMN_NAMES': None,
                                'DATA': np.array([[ 0.        ,  0.0276    ,  0.        ],
                                               [ 0.0316    ,  0.88160002,  0.0316    ],
                                               [ 0.        ,  0.0276    ,  0.        ]], dtype='float32'),
                                'DATA_TYPE': 'float32',
                                'EXTENSION': 1,
                                'KIND': 'IMAGE',
                                'SHAPE': (3, 3)})
                }
        info = certify.TpnInfo('SCI','D','X','R',('&KernelUnity',))
        checker = certify.KernelunityValidator(info)
        checker.check("test.fits", header)        

    def test_certify_kernel_unity_validator_bad(self):
        header = {'SCI_ARRAY': utils.Struct({'COLUMN_NAMES': None,
                                'DATA': np.array([[ 0.        ,  0.0276    ,  0.        ],
                                               [ 0.0316    ,  0.88160002 + 1e-6,  0.0316    ],
                                               [ 0.        ,  0.0276    ,  0.        ]], dtype='float32'),
                                'DATA_TYPE': 'float32',
                                'EXTENSION': 1,
                                'KIND': 'IMAGE',
                                'SHAPE': (3, 3)})
                }
        info = certify.TpnInfo('SCI','D','X','R',('&KernelUnity',))
        checker = certify.KernelunityValidator(info)
        assert_raises(exceptions.BadKernelSumError, checker.check, "test.fits", header)        


# ==================================================================================

def main():
    """Run module tests,  for now just doctests only."""
    import unittest

    suite = unittest.TestLoader().loadTestsFromTestCase(TestHSTTpnInfoClass)
    unittest.TextTestRunner().run(suite)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestCertify)
    unittest.TextTestRunner().run(suite)

    from crds.tests import test_certify, tstmod
    return tstmod(test_certify)

if __name__ == "__main__":
    print(main())

