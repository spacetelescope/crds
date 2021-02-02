import os
import doctest
from pprint import pprint as pp

# ==================================================================================
import numpy as np

from nose.tools import assert_raises, assert_true, assert_false

# ==================================================================================

from crds.core import utils, log, exceptions
from crds import client
from crds import data_file
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
    >>> TestCertifyScript("crds.certify data/s7g1700gl_dead_bad_xsum.fits --run-fitsverify --comparison-context hst_0508.pmap")()  # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/s7g1700gl_dead_bad_xsum.fits' (1/1) as 'FITS' relative to context 'hst_0508.pmap'
    CRDS - WARNING -  AstropyUserWarning : astropy.io.fits.hdu.base : Checksum verification failed for HDU ('', 1).
    CRDS - WARNING -  AstropyUserWarning : astropy.io.fits.hdu.base : Datasum verification failed for HDU ('', 1).
    CRDS - INFO -  FITS file 's7g1700gl_dead_bad_xsum.fits' conforms to FITS standards.
    CRDS - WARNING -  AstropyUserWarning : astropy.io.fits.hdu.base : Checksum verification failed for HDU ('', 1).
    CRDS - WARNING -  AstropyUserWarning : astropy.io.fits.hdu.base : Datasum verification failed for HDU ('', 1).
    CRDS - WARNING -  AstropyUserWarning : astropy.io.fits.hdu.base : Checksum verification failed for HDU ('', 1).
    CRDS - WARNING -  AstropyUserWarning : astropy.io.fits.hdu.base : Datasum verification failed for HDU ('', 1).
    CRDS - INFO -  Running fitsverify.
    CRDS - INFO -  >>
    CRDS - INFO -  >>               fitsverify -ignore- (CFITSIO -ignore-)
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
    CRDS - ERROR -  >> RECATEGORIZED *** Warning: Data checksum is not consistent with  the DATASUM keyword
    CRDS - ERROR -  >> RECATEGORIZED *** Warning: HDU checksum is not in agreement with CHECKSUM.
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
    CRDS - INFO -  Fitsverify returned a NONZERO COMMAND LINE ERROR STATUS.
    CRDS - ERROR -  Fitsverify output contains errors or warnings CRDS recategorizes as ERRORs.
    CRDS - INFO -  ########################################
    CRDS - INFO -  4 errors
    CRDS - INFO -  6 warnings
    CRDS - INFO -  40 infos
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
    >>> doctest.ELLIPSIS_MARKER = '-ignore-'
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")

    >>> certify.certify.interpret_fitsverify_output(1, INTERPRET_FITSVERIFY)  # doctest: +ELLIPSIS
    CRDS - INFO -  >>
    CRDS - INFO -  >> Running fitsverify.
    CRDS - INFO -  >>
    CRDS - INFO -  >>               fitsverify -ignore- (CFITSIO -ignore-)
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
    CRDS - ERROR -  >> RECATEGORIZED *** Warning: Data checksum is not consistent with  the DATASUM keyword
    CRDS - ERROR -  >> RECATEGORIZED *** Warning: HDU checksum is not in agreement with CHECKSUM.
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
    CRDS - INFO -  Fitsverify returned a NONZERO COMMAND LINE ERROR STATUS.
    CRDS - ERROR -  Fitsverify output contains errors or warnings CRDS recategorizes as ERRORs.

    >>> certify.certify.interpret_fitsverify_output(1, INTERPRET_FITSVERIFY2)  # doctest: +ELLIPSIS
    CRDS - INFO -  >>
    CRDS - INFO -  >>               fitsverify -ignore- (CFITSIO -ignore-)
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
    CRDS - INFO -  >> RECATEGORIZED *** Error:   Unregistered XTENSION value "ASDF    ".
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
    CRDS - INFO -  Fitsverify returned a NONZERO COMMAND LINE ERROR STATUS.
    CRDS - INFO -  Fitsverify output contains errors or warnings CRDS recategorizes as INFOs.

    >>> certify.certify.interpret_fitsverify_output(0, "")

    >>> test_config.cleanup(old_state)
    >>> doctest.ELLIPSIS_MARKER = '...'
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
    CRDS - WARNING -  Missing suggested keyword 'META.MODEL_TYPE [DATAMODL]'
    CRDS - INFO -  EXP_TYPE = 'mir_image'
    CRDS - INFO -  META.AUTHOR [AUTHOR] = 'Todd Miller'
    CRDS - INFO -  META.DESCRIPTION [DESCRIP] = 'Brief notes on this reference.'
    CRDS - INFO -  META.EXPOSURE.READPATT [READPATT] = 'any'
    CRDS - INFO -  META.EXPOSURE.TYPE [EXP_TYPE] = 'mir_image'
    CRDS - INFO -  META.HISTORY [HISTORY] = 'How this reference came to be and changed over time.'
    CRDS - INFO -  META.INSTRUMENT.BAND [BAND] = 'medium'
    CRDS - INFO -  META.INSTRUMENT.CHANNEL [CHANNEL] = 34
    CRDS - INFO -  META.INSTRUMENT.CORONAGRAPH [CORONMSK] = 'UNDEFINED'
    CRDS - INFO -  META.INSTRUMENT.DETECTOR [DETECTOR] = 'mirifulong'
    CRDS - INFO -  META.INSTRUMENT.FILTER [FILTER] = 'UNDEFINED'
    CRDS - INFO -  META.INSTRUMENT.GRATING [GRATING] = 'UNDEFINED'
    CRDS - INFO -  META.INSTRUMENT.NAME [INSTRUME] = 'miri'
    CRDS - INFO -  META.INSTRUMENT.PUPIL [PUPIL] = 'UNDEFINED'
    CRDS - INFO -  META.MODEL_TYPE [DATAMODL] = 'UNDEFINED'
    CRDS - INFO -  META.PEDIGREE [PEDIGREE] = 'dummy'
    CRDS - INFO -  META.REFTYPE [REFTYPE] = 'distortion'
    CRDS - INFO -  META.SUBARRAY.FASTAXIS [FASTAXIS] = 1
    CRDS - INFO -  META.SUBARRAY.NAME [SUBARRAY] = 'MASK1550'
    CRDS - INFO -  META.SUBARRAY.SLOWAXIS [SLOWAXIS] = 2
    CRDS - INFO -  META.SUBARRAY.XSIZE [SUBSIZE1] = 1032
    CRDS - INFO -  META.SUBARRAY.XSTART [SUBSTRT1] = 1
    CRDS - INFO -  META.SUBARRAY.YSIZE [SUBSIZE2] = 4
    CRDS - INFO -  META.SUBARRAY.YSTART [SUBSTRT2] = 1020
    CRDS - INFO -  META.TELESCOPE [TELESCOP] = 'jwst'
    CRDS - INFO -  META.USEAFTER [USEAFTER] = '2015-01-25T12:00:00'
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  1 warnings
    CRDS - INFO -  29 infos
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
    >>> TestCertifyScript("crds.certify crds://hst_cos.imap --exist --dont-parse --comparison-context hst.pmap")() # doctest: +ELLIPSIS
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos.imap' (1/19) as 'MAPPING' relative to context 'hst.pmap'
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_badttab.rmap' (2/19) as 'MAPPING' relative to context 'hst.pmap'
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_bpixtab.rmap' (3/19) as 'MAPPING' relative to context 'hst.pmap'
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_brftab.rmap' (4/19) as 'MAPPING' relative to context 'hst.pmap'
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_brsttab.rmap' (5/19) as 'MAPPING' relative to context 'hst.pmap'
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_deadtab.rmap' (6/19) as 'MAPPING' relative to context 'hst.pmap'
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_disptab.rmap' (7/19) as 'MAPPING' relative to context 'hst.pmap'
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_flatfile.rmap' (8/19) as 'MAPPING' relative to context 'hst.pmap'
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_fluxtab.rmap' (9/19) as 'MAPPING' relative to context 'hst.pmap'
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_geofile.rmap' (10/19) as 'MAPPING' relative to context 'hst.pmap'
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_gsagtab.rmap' (11/19) as 'MAPPING' relative to context 'hst.pmap'
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_hvtab.rmap' (12/19) as 'MAPPING' relative to context 'hst.pmap'
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_lamptab.rmap' (13/19) as 'MAPPING' relative to context 'hst.pmap'
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_phatab.rmap' (14/19) as 'MAPPING' relative to context 'hst.pmap'
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_spwcstab.rmap' (15/19) as 'MAPPING' relative to context 'hst.pmap'
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_tdstab.rmap' (16/19) as 'MAPPING' relative to context 'hst.pmap'
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_walktab.rmap' (17/19) as 'MAPPING' relative to context 'hst.pmap'
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_wcptab.rmap' (18/19) as 'MAPPING' relative to context 'hst.pmap'
    CRDS - INFO - ########################################
    CRDS - INFO - Certifying '.../mappings/hst/hst_cos_xtractab.rmap' (19/19) as 'MAPPING' relative to context 'hst.pmap'
    CRDS - INFO - ########################################
    CRDS - INFO - 0 errors
    CRDS - INFO - 0 warnings
    CRDS - INFO - 39 infos
    0
    """

def certify_table_comparison_context():
    """
    >>> old_state = test_config.setup()

    >>> TestCertifyScript("crds.certify crds://y951738kl_hv.fits --comparison-context hst_0294.pmap")() # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying '.../references/hst/y951738kl_hv.fits' (1/1) as 'FITS' relative to context 'hst_0294.pmap'
    CRDS - INFO -  FITS file 'y951738kl_hv.fits' conforms to FITS standards.
    CRDS - INFO -  Comparing reference 'y951738kl_hv.fits' against 'yas2005el_hv.fits'
    CRDS - INFO -  Mode columns defined by spec for old reference 'yas2005el_hv.fits[1]' are: ['DATE']
    CRDS - INFO -  All column names for this table old reference 'yas2005el_hv.fits[1]' are: ['DATE', 'HVLEVELA']
    CRDS - INFO -  Checking for duplicate modes using intersection ['DATE']
    CRDS - INFO -  Mode columns defined by spec for new reference 'y951738kl_hv.fits[1]' are: ['DATE']
    CRDS - INFO -  All column names for this table new reference 'y951738kl_hv.fits[1]' are: ['DATE', 'HVLEVELA']
    CRDS - INFO -  Checking for duplicate modes using intersection ['DATE']
    CRDS - WARNING -  Table mode (('DATE', 56923.5834),) from old reference 'yas2005el_hv.fits[1]' is NOT IN new reference 'y951738kl_hv.fits[1]'
    CRDS - WARNING -  Table mode (('DATE', 56923.625),) from old reference 'yas2005el_hv.fits[1]' is NOT IN new reference 'y951738kl_hv.fits[1]'
    CRDS - WARNING -  Table mode (('DATE', 56964.0),) from old reference 'yas2005el_hv.fits[1]' is NOT IN new reference 'y951738kl_hv.fits[1]'
    CRDS - INFO -  Mode columns defined by spec for old reference 'yas2005el_hv.fits[2]' are: ['DATE']
    CRDS - INFO -  All column names for this table old reference 'yas2005el_hv.fits[2]' are: ['DATE', 'HVLEVELB']
    CRDS - INFO -  Checking for duplicate modes using intersection ['DATE']
    CRDS - INFO -  Mode columns defined by spec for new reference 'y951738kl_hv.fits[2]' are: ['DATE']
    CRDS - INFO -  All column names for this table new reference 'y951738kl_hv.fits[2]' are: ['DATE', 'HVLEVELB']
    CRDS - INFO -  Checking for duplicate modes using intersection ['DATE']
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
    CRDS - INFO -  17 infos
    0
    >>> test_config.cleanup(old_state)
    """

def certify_table_comparison_reference():
    """
    >>> TestCertifyScript("crds.certify data/y951738kl_hv.fits --comparison-reference data/y9j16159l_hv.fits --comparison-context hst_0857.pmap")() # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/y951738kl_hv.fits' (1/1) as 'FITS' relative to context 'hst_0857.pmap' and comparison reference 'data/y9j16159l_hv.fits'
    CRDS - INFO -  FITS file 'y951738kl_hv.fits' conforms to FITS standards.
    CRDS - INFO -  Mode columns defined by spec for old reference 'y9j16159l_hv.fits[1]' are: ['DATE']
    CRDS - INFO -  All column names for this table old reference 'y9j16159l_hv.fits[1]' are: ['DATE', 'HVLEVELA']
    CRDS - INFO -  Checking for duplicate modes using intersection ['DATE']
    CRDS - INFO -  Mode columns defined by spec for new reference 'y951738kl_hv.fits[1]' are: ['DATE']
    CRDS - INFO -  All column names for this table new reference 'y951738kl_hv.fits[1]' are: ['DATE', 'HVLEVELA']
    CRDS - INFO -  Checking for duplicate modes using intersection ['DATE']
    CRDS - WARNING -  Table mode (('DATE', 56923.5834),) from old reference 'y9j16159l_hv.fits[1]' is NOT IN new reference 'y951738kl_hv.fits[1]'
    CRDS - WARNING -  Table mode (('DATE', 56923.625),) from old reference 'y9j16159l_hv.fits[1]' is NOT IN new reference 'y951738kl_hv.fits[1]'
    CRDS - INFO -  Mode columns defined by spec for old reference 'y9j16159l_hv.fits[2]' are: ['DATE']
    CRDS - INFO -  All column names for this table old reference 'y9j16159l_hv.fits[2]' are: ['DATE', 'HVLEVELB']
    CRDS - INFO -  Checking for duplicate modes using intersection ['DATE']
    CRDS - WARNING -  Duplicate definitions in old reference 'y9j16159l_hv.fits[2]' for mode: (('DATE', 56924.0417),) :
     (129, (('DATE', 56924.0417), ('HVLEVELB', 169)))
    (131, (('DATE', 56924.0417), ('HVLEVELB', 169)))
    CRDS - WARNING -  Duplicate definitions in old reference 'y9j16159l_hv.fits[2]' for mode: (('DATE', 56925.0),) :
     (132, (('DATE', 56925.0), ('HVLEVELB', 175)))
    (134, (('DATE', 56925.0), ('HVLEVELB', 175)))
    CRDS - INFO -  Mode columns defined by spec for new reference 'y951738kl_hv.fits[2]' are: ['DATE']
    CRDS - INFO -  All column names for this table new reference 'y951738kl_hv.fits[2]' are: ['DATE', 'HVLEVELB']
    CRDS - INFO -  Checking for duplicate modes using intersection ['DATE']
    CRDS - WARNING -  Table mode (('DATE', 56921.8334),) from old reference 'y9j16159l_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS - WARNING -  Table mode (('DATE', 56922.0),) from old reference 'y9j16159l_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS - WARNING -  Table mode (('DATE', 56923.625),) from old reference 'y9j16159l_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS - WARNING -  Table mode (('DATE', 56924.0417),) from old reference 'y9j16159l_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS - WARNING -  Table mode (('DATE', 56924.3125),) from old reference 'y9j16159l_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS - WARNING -  Table mode (('DATE', 56925.0),) from old reference 'y9j16159l_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  10 warnings
    CRDS - INFO -  16 infos
    0
    """

def certify_duplicate_sha1sum():
    """
    >>> TestCertifyScript("crds.certify data/s7g1700gl_dead.fits --check-sha1sums")() # doctest: +ELLIPSIS
    CRDS - INFO -  Defaulting --comparison-context to operational context.
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/s7g1700gl_dead.fits' (1/1) as 'FITS' relative to context '...'
    CRDS - ERROR -  instrument='COS' type='DEADTAB' data='data/s7g1700gl_dead.fits' ::  Duplicate file check : File 's7g1700gl_dead.fits' is identical to existing CRDS file 's7g1700gl_dead.fits'
    CRDS - INFO -  FITS file 's7g1700gl_dead.fits' conforms to FITS standards.
    CRDS - INFO -  ########################################
    CRDS - INFO -  1 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  5 infos
    1
    """

def certify_jwst_valid():
    """
    >> TestCertifyScript("crds.certify data/niriss_ref_photom.fits --comparison-context None")() # doctest: +ELLIPSIS
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
    >>> TestCertifyScript("crds.certify data/jwst_miri_ipc_0003.add.fits --comparison-context jwst_0125.pmap")()  # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/jwst_miri_ipc_0003.add.fits' (1/1) as 'FITS' relative to context 'jwst_0125.pmap'
    CRDS - INFO -  FITS file 'jwst_miri_ipc_0003.add.fits' conforms to FITS standards.
    CRDS - INFO -  Setting 'META.INSTRUMENT.BAND [BAND]' = None to value of 'P_BAND' = 'SHORT | MEDIUM |'
    CRDS - INFO -  Setting 'META.INSTRUMENT.DETECTOR [DETECTOR]' = 'MIRIMAGE' to value of 'P_DETECT' = 'MIRIFUSHORT|MIRIFULONG|'
    CRDS - WARNING -  Missing suggested keyword 'META.MODEL_TYPE [DATAMODL]'
    CRDS - INFO -  Checking JWST datamodels.
    CRDS - WARNING -  NoTypeWarning : ...jwst.datamodels.util : model_type not found...
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  2 warnings
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

def certify_test_roman_load_all_type_constraints():
    """
    >>> old_state = test_config.setup(url="https://roman-crds-serverless.stsci.edu", observatory="roman", cache=test_config.CRDS_TESTING_CACHE)
    >>> generic_tpn.load_all_type_constraints("roman")
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
    >>> info = generic_tpn.TpnInfo('DETECTOR','H','C', '(Q='BAR')', ('WFC','HRC','SBC'))
    Traceback (most recent call last):
    ...
    SyntaxError: invalid syntax
    >>> test_config.cleanup(old_state)
    """

def certify_JsonCertify_valid():
    """
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> certify.certify_file("data/valid.json", "jwst_0034.pmap", observatory="jwst")
    CRDS - INFO -  Certifying 'data/valid.json' as 'JSON' relative to context 'jwst_0034.pmap'
    CRDS - WARNING -  Missing suggested keyword 'META.MODEL_TYPE [DATAMODL]'
    >>> test_config.cleanup(old_state)
    """

def certify_YamlCertify_valid():
    """
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> certify.certify_file("data/valid.yaml", "jwst_0034.pmap", observatory="jwst")
    CRDS - INFO -  Certifying 'data/valid.yaml' as 'YAML' relative to context 'jwst_0034.pmap'
    CRDS - WARNING -  Missing suggested keyword 'META.MODEL_TYPE [DATAMODL]'
    >>> test_config.cleanup(old_state)
    """

def certify_AsdfCertify_valid():
    """
    >>> doctest.ELLIPSIS_MARKER = '-ignore-'
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> certify.certify_file("data/valid.asdf", "jwst_0365.pmap", observatory="jwst") # doctest: +ELLIPSIS
    CRDS - INFO -  Certifying 'data/valid.asdf' as 'ASDF' relative to context 'jwst_0365.pmap'
    CRDS - INFO -  Setting 'META.INSTRUMENT.DETECTOR [DETECTOR]' = None to value of 'META.INSTRUMENT.P_DETECTOR [P_DETECT]' = 'NRS1|NRS2|'
    CRDS - INFO -  Checking JWST datamodels.
    >>> test_config.cleanup(old_state)
    >>> doctest.ELLIPSIS_MARKER = '...'
    """

def certify_roman_valid_asdf():
    """
    Required Roman test: confirm that a valid asdf file is recognized as such.
    >>> old_state = test_config.setup(url="https://roman-crds-serverless.stsci.edu", observatory="roman", cache=test_config.CRDS_TESTING_CACHE)
    >>> certify.certify_file("data/roman_wfi16_f158_flat_small.asdf", "roman_0003.pmap", observatory="roman")
    CRDS - INFO -  Certifying 'data/roman_wfi16_f158_flat_small.asdf' as 'ASDF' relative to context 'roman_0003.pmap'
    CRDS - INFO -  Checking Roman datamodels.
    >>> test_config.cleanup(old_state)
    """

def certify_roman_invalid_asdf_schema():
    """
    Required Roman test: confirm that an asdf file that does not conform to its schema definition
    triggers an error in DataModels.
    >>> old_state = test_config.setup(url="https://roman-crds-serverless.stsci.edu", observatory="roman", cache=test_config.CRDS_TESTING_CACHE)
    >>> certify.certify_file("data/roman_wfi16_f158_flat_invalid_schema.asdf", "roman_0003.pmap", observatory="roman") # doctest: +ELLIPSIS
    CRDS - INFO -  Certifying 'data/roman_wfi16_f158_flat_invalid_schema.asdf' as 'ASDF' relative to context 'roman_0003.pmap'
    CRDS - INFO -  Checking Roman datamodels.
    CRDS - ERROR -  data/roman_wfi16_f158_flat_invalid_schema.asdf Validation error : Roman Data Models: sequence item...: expected str instance, Time found
    >>> test_config.cleanup(old_state)
    """

def certify_roman_invalid_asdf_tpn():
    """
    Required Roman test: confirm that an asdf file that does not conform to its tpn definition
    triggers an error in crds. Note: as the tpn often replicates schema implementation, this also
    triggers an error in Datamodels.
    >>> old_state = test_config.setup(url="https://roman-crds-serverless.stsci.edu", observatory="roman", cache=test_config.CRDS_TESTING_CACHE)
    >>> certify.certify_file("data/roman_wfi16_f158_flat_invalid_tpn.asdf", "roman_0003.pmap", observatory="roman") # doctest: +ELLIPSIS
    CRDS - INFO -  Certifying 'data/roman_wfi16_f158_flat_invalid_tpn.asdf' as 'ASDF' relative to context 'roman_0003.pmap'
    CRDS - ERROR -  In 'roman_wfi16_f158_flat_invalid_tpn.asdf' : Checking 'META.INSTRUMENT.OPTICAL_ELEMENT...' : Value 'BAD' is not one of...
    CRDS - INFO -  Checking Roman datamodels.
    CRDS - WARNING -  ValidationWarning : stdatamodels.validate...
    >>> test_config.cleanup(old_state)
    """

def certify_roman_valid_spec_asdf():
    """
    Required Roman test: confirm that a valid spectroscopic asdf file is recognized as such.
    >>> old_state = test_config.setup(url="https://roman-crds-serverless.stsci.edu", observatory="roman", cache=test_config.CRDS_TESTING_CACHE)
    >>> certify.certify_file("data/roman_wfi16_grism_flat_small.asdf", "roman_0003.pmap", observatory="roman")
    CRDS - INFO -  Certifying 'data/roman_wfi16_grism_flat_small.asdf' as 'ASDF' relative to context 'roman_0003.pmap'
    CRDS - INFO -  Checking Roman datamodels.
    >>> test_config.cleanup(old_state)
    """

def certify_roman_invalid_spec_asdf_schema():
    """
    Required Roman test: confirm that a spectroscopic asdf file that does not conform to its schema
    definition triggers an error in DataModels.
    >>> old_state = test_config.setup(url="https://roman-crds-serverless.stsci.edu", observatory="roman", cache=test_config.CRDS_TESTING_CACHE)
    >>> certify.certify_file("data/roman_wfi16_grism_flat_invalid_schema.asdf", "roman_0003.pmap", observatory="roman") # doctest: +ELLIPSIS
    CRDS - INFO -  Certifying 'data/roman_wfi16_grism_flat_invalid_schema.asdf' as 'ASDF' relative to context 'roman_0003.pmap'
    CRDS - INFO -  Checking Roman datamodels.
    CRDS - ERROR -  data/roman_wfi16_grism_flat_invalid_schema.asdf Validation error : Roman Data Models: sequence item...: expected str instance, Time found
    >>> test_config.cleanup(old_state)
    """

def certify_roman_invalid_spec_asdf_tpn():
    """
    Required Roman test: confirm that a spectroscopic asdf file that does not conform to its tpn
    definition triggers an error in crds. Note: as the tpn often replicates schema implementation,
    this also triggers an error in Datamodels.
    >>> old_state = test_config.setup(url="https://roman-crds-serverless.stsci.edu", observatory="roman", cache=test_config.CRDS_TESTING_CACHE)
    >>> certify.certify_file("data/roman_wfi16_grism_flat_invalid_tpn.asdf", "roman_0003.pmap", observatory="roman") # doctest: +ELLIPSIS
    CRDS - INFO -  Certifying 'data/roman_wfi16_grism_flat_invalid_tpn.asdf' as 'ASDF' relative to context 'roman_0003.pmap'
    CRDS - ERROR -  In 'roman_wfi16_grism_flat_invalid_tpn.asdf' : Checking 'META.INSTRUMENT.OPTICAL_ELEMENT...' : Value 'BAD' is not one of...
    CRDS - INFO -  Checking Roman datamodels.
    CRDS - WARNING -  ValidationWarning : stdatamodels.validate...
    >>> test_config.cleanup(old_state)
    """


def certify_AsdfCertify_valid_with_astropy_time():
    """
    >>> doctest.ELLIPSIS_MARKER = '-ignore-'
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> certify.certify_file("data/valid_with_astropy_time.asdf", "jwst_0365.pmap", observatory="jwst") # doctest: +ELLIPSIS
    CRDS - INFO -  Certifying 'data/valid_with_astropy_time.asdf' as 'ASDF' relative to context 'jwst_0365.pmap'
    CRDS - INFO -  Setting 'META.INSTRUMENT.DETECTOR [DETECTOR]' = None to value of 'META.INSTRUMENT.P_DETECTOR [P_DETECT]' = 'NRS1|NRS2|'
    CRDS - INFO -  Checking JWST datamodels.
    >>> test_config.cleanup(old_state)
    >>> doctest.ELLIPSIS_MARKER = '...'
    """

def certify_FitsCertify_opaque_name():
    """
    >>> old_state = test_config.setup(url="https://hst-crds-serverless.stsci.edu", observatory="hst")
    >>> certify.certify_file("data/opaque_fts.tmp", "hst.pmap", observatory="hst")
    CRDS - INFO -  Certifying 'data/opaque_fts.tmp' as 'FITS' relative to context 'hst.pmap'
    >>> test_config.cleanup(old_state)
    """

# CRDS is able to recognize ASDF files without the .asdf extension, but the cal code is not.
# Leaving this test here in case jwst decides to change its mind someday.
def certify_AsdfCertify_opaque_name():
    """
    >>> doctest.ELLIPSIS_MARKER = '-ignore-'
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> certify.certify_file("data/opaque_asd.tmp", "jwst_0365.pmap", observatory="jwst") # doctest: +ELLIPSIS
    CRDS - INFO -  Certifying 'data/opaque_asd.tmp' as 'ASDF' relative to context 'jwst_0365.pmap'
    CRDS - INFO -  Setting 'META.INSTRUMENT.DETECTOR [DETECTOR]' = None to value of 'META.INSTRUMENT.P_DETECTOR [P_DETECT]' = 'NRS1|NRS2|'
    CRDS - INFO -  Checking JWST datamodels.
    CRDS - ERROR -  data/opaque_asd.tmp Validation error : JWST Data Models: Unrecognized file type for: data/opaque_asd.tmp
    >>> test_config.cleanup(old_state)
    >>> doctest.ELLIPSIS_MARKER = '...'
    """

def certify_rmap_compare():
    """
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> certify.certify_file("jwst_miri_distortion_0025.rmap", "jwst_0357.pmap")
    CRDS - INFO -  Certifying 'jwst_miri_distortion_0025.rmap' as 'MAPPING' relative to context 'jwst_0357.pmap'
    >>> test_config.cleanup(old_state)
    """

def certify_roman_rmap_compare():
    """
    Required Roman test: confirm that a calibration mapping file properly compares to its context.
    >>> old_state = test_config.setup(url="https://roman-crds-serverless.stsci.edu", observatory="roman", cache=test_config.CRDS_TESTING_CACHE)
    >>> certify.certify_file("roman_wfi_flat_0004.rmap", "roman_0004.pmap")
    CRDS - INFO -  Certifying 'roman_wfi_flat_0004.rmap' as 'MAPPING' relative to context 'roman_0004.pmap'
    >>> test_config.cleanup(old_state)
    """


def certify_jwst_bad_fits():
    """
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> certify.certify_file("data/niriss_ref_photom_bad.fits", "jwst_0541.pmap", observatory="jwst") # doctest: +ELLIPSIS
    CRDS - INFO -  Certifying 'data/niriss_ref_photom_bad.fits' as 'FITS' relative to context 'jwst_0541.pmap'
    CRDS - INFO -  FITS file 'niriss_ref_photom_bad.fits' conforms to FITS standards.
    CRDS - ERROR -  In 'niriss_ref_photom_bad.fits' : Checking 'META.INSTRUMENT.DETECTOR [DETECTOR]' : Value 'FOO' is not one of ['ANY', 'N/A', 'NIS']
    CRDS - WARNING -  Missing suggested keyword 'META.MODEL_TYPE [DATAMODL]'
    CRDS - WARNING -  Non-compliant date format 'Jan 01 2015 00:00:00' for 'META.USEAFTER [USEAFTER]' should be 'YYYY-MM-DDTHH:MM:SS'
    CRDS - WARNING -  Failed resolving comparison reference for table checks...
    CRDS - INFO -  Mode columns defined by spec for new reference 'niriss_ref_photom_bad.fits[1]' are: ['FILTER', 'PUPIL', 'ORDER']
    CRDS - INFO -  All column names for this table new reference 'niriss_ref_photom_bad.fits[1]' are: ['FILTER', 'PUPIL', 'PHOTFLAM', 'NELEM', 'WAVELENGTH', 'RELRESPONSE']
    CRDS - INFO -  Checking for duplicate modes using intersection ['FILTER', 'PUPIL']
    CRDS - WARNING -  No comparison reference for 'niriss_ref_photom_bad.fits' in context 'jwst_0541.pmap'. Skipping tables comparison.
    CRDS - INFO -  Checking JWST datamodels.
    CRDS - WARNING -  ValidationWarning : ...stdatamodels.validate...
    CRDS - WARNING -  NoTypeWarning : ...jwst.datamodels...
    >>> test_config.cleanup(old_state)
    """

def certify_duplicate_rmap_case_error():
    """
    >>> old_state = test_config.setup(url="https://hst-crds-serverless.stsci.edu", observatory="hst")
    >>> certify.certify_file("data/hst_cos_tdstab_duplicate.rmap", "hst.pmap", observatory="hst")
    CRDS - INFO -  Certifying 'data/hst_cos_tdstab_duplicate.rmap' as 'MAPPING' relative to context 'hst.pmap'
    CRDS - ERROR -  Duplicate entry at selector ('FUV', 'SPECTROSCOPIC') = UseAfter vs. UseAfter
    CRDS - WARNING -  Checksum error : sha1sum mismatch in 'hst_cos_tdstab_duplicate.rmap'
    CRDS - INFO -  Mapping 'hst_cos_tdstab_duplicate.rmap' corresponds to 'hst_cos_tdstab.rmap' from context 'hst.pmap' for checking mapping differences.
    CRDS - INFO -  Checking diffs from 'hst_cos_tdstab.rmap' to 'hst_cos_tdstab_duplicate.rmap'
    >>> test_config.cleanup(old_state)
    """

def certify_roman_duplicate_rmap_case_error():
    """
    Required Roman test: verify that a calibration mapping file containing duplicate match cases
    fails.
    >>> old_state = test_config.setup(url="https://roman-crds-serverless.stsci.edu", observatory="roman", cache=test_config.CRDS_TESTING_CACHE)
    >>> certify.certify_file("data/roman_wfi_flat_0004_duplicate.rmap", "roman_0003.pmap")
    CRDS - INFO -  Certifying 'data/roman_wfi_flat_0004_duplicate.rmap' as 'MAPPING' relative to context 'roman_0003.pmap'
    CRDS - ERROR -  Duplicate entry at selector ('WFI01', 'F158') = UseAfter vs. UseAfter
    CRDS - WARNING -  Checksum error : sha1sum mismatch in 'roman_wfi_flat_0004_duplicate.rmap'
    CRDS - ERROR -  data/roman_wfi_flat_0004_duplicate.rmap Validation error : Failed to determine 'roman' instrument or reftype for 'data/roman_wfi_flat_0004_duplicate.rmap' : 'sha1sum mismatch in 'roman_wfi_flat_0004_duplicate.rmap''
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

def checksum_roman_duplicate_rmap_case_error():
    """
    Required Roman test: verify that the crds rmap checksum update tool does not silently drop
    duplicate rmap entries when updating the checksum and rewriting the file.
    >>> from crds.refactoring import checksum
    >>> old_state = test_config.setup(url="https://roman-crds-serverless.stsci.edu", observatory="roman")
    >>> checksum.add_checksum("data/roman_wfi_flat_0004_duplicate.rmap")
    CRDS - INFO -  Adding checksum for 'data/roman_wfi_flat_0004_duplicate.rmap'
    CRDS - ERROR -  Duplicate entry at selector ('WFI01', 'F158') = UseAfter vs. UseAfter
    >>> test_config.cleanup(old_state)
    """

def certify_roman_invalid_rmap_tpn():
    """
    Required Roman test: verify that a calibration mapping file that violates tpn rules produces an
    error.
    >>> old_state = test_config.setup(url="https://roman-crds-serverless.stsci.edu", observatory="roman", cache=test_config.CRDS_TESTING_CACHE)
    >>> certify.certify_file("data/roman_wfi_flat_0004_badtpn.rmap", "roman_0003.pmap", observatory="roman") # doctest: +ELLIPSIS
    CRDS - INFO -  Certifying 'data/roman_wfi_flat_0004_badtpn.rmap' as 'MAPPING' relative to context 'roman_0003.pmap'
    CRDS - ERROR -  Match('META.INSTRUMENT.DETECTOR', 'META.INSTRUMENT.OPTICAL_ELEMENT...') : ('WFI21', 'F158') :  parameter='META.INSTRUMENT.DETECTOR...' value='WFI21' is not in (...)
    CRDS - INFO -  Mapping 'roman_wfi_flat_0004_badtpn.rmap' corresponds to 'roman_wfi_flat_0001.rmap' from context 'roman_0003.pmap' for checking mapping differences.
    CRDS - INFO -  Checking diffs from 'roman_wfi_flat_0001.rmap' to 'roman_wfi_flat_0004_badtpn.rmap'
    CRDS - WARNING -  Rule change at ('data/roman_wfi_flat_0004_badtpn.rmap', ('WFI21', 'F158'), ('2020-01-01', '00:00:00')) added Match rule for 'roman_wfi_flat_0003.asdf'
    >>> test_config.cleanup(old_state)
    """

def undefined_expr_identifiers():
    """Some TpnInfos include Python expressions either to make them apply conditionally or to
    implement and expression constraint.   validators.core.expr_identifiers() scans a Tpn header
    expression for the header keywords upon which it depends.   This enables CRDS To short
    circuit checks for which critical keywords are not defined at all.

    >>> validators.core.expr_identifiers("((EXP_TYPE)in(['NRS_MSASPEC','NRS_FIXEDSLIT','NRS_BRIGHTOBJ','NRS_IFU']))")
    ['EXP_TYPE']

    >>> validators.core.expr_identifiers("nir_filter(INSTRUME,REFTYPE,EXP_TYPE)")
    ['INSTRUME', 'REFTYPE', 'EXP_TYPE']

    >>> validators.core.expr_identifiers("(len(SCI_ARRAY.SHAPE)==2)")
    ['SCI_ARRAY']

    >>> validators.core.expr_identifiers("(True)")
    []
    """

def load_nirspec_staturation_tpn_lines():
    """Print out the outcome of various .tpn directives like "replace" and
    "include" and reuse of generic files.

    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> path = generic_tpn.get_tpn_path("nirspec_saturation.tpn","jwst")
    >>> lines = generic_tpn.load_tpn_lines(path)   # doctest: +ELLIPSIS
    >>> text = "\\n".join(lines)
    >>> print(text)
    META.SUBARRAY.NAME          H   C   (is_imaging_mode(EXP_TYPE))
    SUBARRAY                    H   C   O
    META.SUBARRAY.XSTART        H   I   (is_imaging_mode(EXP_TYPE))
    META.SUBARRAY.YSTART        H   I   (is_imaging_mode(EXP_TYPE))
    META.SUBARRAY.XSIZE         H   I   (is_imaging_mode(EXP_TYPE))
    META.SUBARRAY.YSIZE         H   I   (is_imaging_mode(EXP_TYPE))
    META.SUBARRAY.FASTAXIS      H   I   (is_imaging_mode(EXP_TYPE))
    META.SUBARRAY.SLOWAXIS      H   I   (is_imaging_mode(EXP_TYPE))
    FULLFRAME_XSTART            X   X   (full_frame(INSTRUME!='NIRSPEC'))   (META_SUBARRAY_XSTART==1)
    FULLFRAME_YSTART            X   X   (full_frame(INSTRUME!='NIRSPEC'))   (META_SUBARRAY_YSTART==1)
    DETECTOR                    H   C   O
    NRCA1_AXIS                  X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCA1'))    ((FASTAXIS==-1)and(SLOWAXIS==2))
    NRCA2_AXIS                  X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCA2'))    ((FASTAXIS==1)and(SLOWAXIS==-2))
    NRCA3_AXIS                  X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCA3'))    ((FASTAXIS==-1)and(SLOWAXIS==2))
    NRCA4_AXIS                  X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCA4'))    ((FASTAXIS==1)and(SLOWAXIS==-2))
    NRCALONG_AXIS               X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCALONG')) ((FASTAXIS==-1)and(SLOWAXIS==2))
    NRCB1_AXIS                  X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCB1'))    ((FASTAXIS==1)and(SLOWAXIS==-2))
    NRCB2_AXIS                  X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCB2'))    ((FASTAXIS==-1)and(SLOWAXIS==2))
    NRCB3_AXIS                  X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCB3'))    ((FASTAXIS==1)and(SLOWAXIS==-2))
    NRCB4_AXIS                  X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCB4'))    ((FASTAXIS==-1)and(SLOWAXIS==2))
    NRCBLONG_AXIS               X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCBLONG')) ((FASTAXIS==1)and(SLOWAXIS==-2))
    MIRIMAGE_AXIS               X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='MIRIMAGE'))    ((FASTAXIS==1)and(SLOWAXIS==2))
    MIRIFULONG_AXIS             X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='MIRIFULONG'))  ((FASTAXIS==1)and(SLOWAXIS==2))
    MIRIFUSHORT_AXIS            X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='MIRIFUSHORT')) ((FASTAXIS==1)and(SLOWAXIS==2))
    NRS1_AXIS                   X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRS1'))    ((FASTAXIS==2)and(SLOWAXIS==1))
    NRS2_AXIS                   X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRS2'))    ((FASTAXIS==-2)and(SLOWAXIS==-1))
    NIS_AXIS                    X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NIS'))    ((FASTAXIS==-2)and(SLOWAXIS==-1))
    GUIDER1_AXIS                X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='GUIDER1')) ((FASTAXIS==-2)and(SLOWAXIS==-1))
    GUIDER2_AXIS                X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='GUIDER2')) ((FASTAXIS==2)and(SLOWAXIS==-1))
    SCI       A           X         ((True))                              (array_exists(SCI_ARRAY))
    SCI       A           X         ((True))                              (is_image(SCI_ARRAY))
    SCI       A           X         ((True))                              (has_type(SCI_ARRAY,['FLOAT','INT']))
    SUBARRAY_INBOUNDS_X         X   X   ((True))                           (1<=META_SUBARRAY_XSTART+META_SUBARRAY_XSIZE-1<=2048)
    SUBARRAY_INBOUNDS_Y         X   X   ((True))                           (1<=META_SUBARRAY_YSTART+META_SUBARRAY_YSIZE-1<=2048)
    SCI       A           X             ((True))                           (SCI_ARRAY.SHAPE[-2:]>=(META_SUBARRAY_YSIZE,META_SUBARRAY_XSIZE))
    SCI       A           X         (is_full_frame(SUBARRAY)and(not(is_irs2(READPATT))))   (warn_only(SCI_ARRAY.SHAPE[-2:]in[(2048,2048),(32,2048),(64,2048),(256,2048)]))
    SCI       A           X         (is_full_frame(SUBARRAY)and(is_irs2(READPATT)))        (warn_only(SCI_ARRAY.SHAPE[-2:]in[(3200,2048),(32,2048),(64,2048),(256,2048)]))
    SCI       A           X         (is_subarray(SUBARRAY)and(not(is_irs2(READPATT))))     (1<=META_SUBARRAY_YSTART+SCI_ARRAY.SHAPE[-2]-1<=2048)
    SCI       A           X         (is_subarray(SUBARRAY)and(is_irs2(READPATT)))          (1<=META_SUBARRAY_YSTART+SCI_ARRAY.SHAPE[-2]-1<=3200)
    SCI       A           X         (is_subarray(SUBARRAY))                                (1<=META_SUBARRAY_XSTART+SCI_ARRAY.SHAPE[-1]-1<=2048)
    DQ   A    X         (optional((True)))                                    (is_image(DQ_ARRAY))
    DQ   A    X         (optional((True)))                                    (warn_only(has_type(DQ_ARRAY,'INT')))
    DQ   A    X         ((array_exists(SCI_ARRAY))and(array_exists(DQ_ARRAY)))    (DQ_ARRAY.SHAPE[-2:]==SCI_ARRAY.SHAPE[-2:])
    DQ_DEF       A           X         O             (is_table(DQ_DEF_ARRAY))
    DQ_DEF       A           X         O             (has_columns(DQ_DEF_ARRAY,['BIT','VALUE','NAME','DESCRIPTION']))
    DQ_DEF       A           X         O             (has_column_type(DQ_DEF_ARRAY,'BIT','INT'))
    DQ_DEF       A           X         O             (has_column_type(DQ_DEF_ARRAY,'VALUE','INT'))
    DQ_DEF       A           X         O             (has_column_type(DQ_DEF_ARRAY,'NAME','STRING'))
    DQ_DEF       A           X         O             (has_column_type(DQ_DEF_ARRAY,'DESCRIPTION','STRING'))
    SCI   A   X    R  (ndim(SCI_ARRAY,2))
    DQ    A   X    O  (ndim(DQ_ARRAY,2))
    META.EXPOSURE.GAIN_FACTOR     H   R   W  1.0:10.0
    >>> test_config.cleanup(old_state)
    """

def load_nirspec_staturation_tpn():
    """Print out the outcome of various .tpn directives like "replace" and
    "include" and reuse of generic files as actual .tpn objects.

    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> path = generic_tpn.get_tpn_path("nirspec_saturation.tpn","jwst")
    >>> pp(generic_tpn.load_tpn(path))
    [('META.SUBARRAY.NAME', 'HEADER', 'CHARACTER', condition='(is_imaging_mode(EXP_TYPE))', values=()),
     ('SUBARRAY', 'HEADER', 'CHARACTER', 'OPTIONAL', values=()),
     ('META.SUBARRAY.XSTART', 'HEADER', 'INTEGER', condition='(is_imaging_mode(EXP_TYPE))', values=()),
     ('META.SUBARRAY.YSTART', 'HEADER', 'INTEGER', condition='(is_imaging_mode(EXP_TYPE))', values=()),
     ('META.SUBARRAY.XSIZE', 'HEADER', 'INTEGER', condition='(is_imaging_mode(EXP_TYPE))', values=()),
     ('META.SUBARRAY.YSIZE', 'HEADER', 'INTEGER', condition='(is_imaging_mode(EXP_TYPE))', values=()),
     ('META.SUBARRAY.FASTAXIS', 'HEADER', 'INTEGER', condition='(is_imaging_mode(EXP_TYPE))', values=()),
     ('META.SUBARRAY.SLOWAXIS', 'HEADER', 'INTEGER', condition='(is_imaging_mode(EXP_TYPE))', values=()),
     ('FULLFRAME_XSTART', 'EXPRESSION', 'EXPRESSION', condition="(full_frame(INSTRUME!='NIRSPEC'))", expression='(META_SUBARRAY_XSTART==1)'),
     ('FULLFRAME_YSTART', 'EXPRESSION', 'EXPRESSION', condition="(full_frame(INSTRUME!='NIRSPEC'))", expression='(META_SUBARRAY_YSTART==1)'),
     ('DETECTOR', 'HEADER', 'CHARACTER', 'OPTIONAL', values=()),
     ('NRCA1_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCA1'))", expression='((FASTAXIS==-1)and(SLOWAXIS==2))'),
     ('NRCA2_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCA2'))", expression='((FASTAXIS==1)and(SLOWAXIS==-2))'),
     ('NRCA3_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCA3'))", expression='((FASTAXIS==-1)and(SLOWAXIS==2))'),
     ('NRCA4_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCA4'))", expression='((FASTAXIS==1)and(SLOWAXIS==-2))'),
     ('NRCALONG_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCALONG'))", expression='((FASTAXIS==-1)and(SLOWAXIS==2))'),
     ('NRCB1_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCB1'))", expression='((FASTAXIS==1)and(SLOWAXIS==-2))'),
     ('NRCB2_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCB2'))", expression='((FASTAXIS==-1)and(SLOWAXIS==2))'),
     ('NRCB3_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCB3'))", expression='((FASTAXIS==1)and(SLOWAXIS==-2))'),
     ('NRCB4_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCB4'))", expression='((FASTAXIS==-1)and(SLOWAXIS==2))'),
     ('NRCBLONG_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCBLONG'))", expression='((FASTAXIS==1)and(SLOWAXIS==-2))'),
     ('MIRIMAGE_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='MIRIMAGE'))", expression='((FASTAXIS==1)and(SLOWAXIS==2))'),
     ('MIRIFULONG_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='MIRIFULONG'))", expression='((FASTAXIS==1)and(SLOWAXIS==2))'),
     ('MIRIFUSHORT_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='MIRIFUSHORT'))", expression='((FASTAXIS==1)and(SLOWAXIS==2))'),
     ('NRS1_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRS1'))", expression='((FASTAXIS==2)and(SLOWAXIS==1))'),
     ('NRS2_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRS2'))", expression='((FASTAXIS==-2)and(SLOWAXIS==-1))'),
     ('NIS_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NIS'))", expression='((FASTAXIS==-2)and(SLOWAXIS==-1))'),
     ('GUIDER1_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='GUIDER1'))", expression='((FASTAXIS==-2)and(SLOWAXIS==-1))'),
     ('GUIDER2_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='GUIDER2'))", expression='((FASTAXIS==2)and(SLOWAXIS==-1))'),
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', condition='((True))', expression='(array_exists(SCI_ARRAY))'),
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', condition='((True))', expression='(is_image(SCI_ARRAY))'),
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', condition='((True))', expression="(has_type(SCI_ARRAY,['FLOAT','INT']))"),
     ('SUBARRAY_INBOUNDS_X', 'EXPRESSION', 'EXPRESSION', condition='((True))', expression='(1<=META_SUBARRAY_XSTART+META_SUBARRAY_XSIZE-1<=2048)'),
     ('SUBARRAY_INBOUNDS_Y', 'EXPRESSION', 'EXPRESSION', condition='((True))', expression='(1<=META_SUBARRAY_YSTART+META_SUBARRAY_YSIZE-1<=2048)'),
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', condition='((True))', expression='(SCI_ARRAY.SHAPE[-2:]>=(META_SUBARRAY_YSIZE,META_SUBARRAY_XSIZE))'),
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', condition='(is_full_frame(SUBARRAY)and(not(is_irs2(READPATT))))', expression='(warn_only(SCI_ARRAY.SHAPE[-2:]in[(2048,2048),(32,2048),(64,2048),(256,2048)]))'),
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', condition='(is_full_frame(SUBARRAY)and(is_irs2(READPATT)))', expression='(warn_only(SCI_ARRAY.SHAPE[-2:]in[(3200,2048),(32,2048),(64,2048),(256,2048)]))'),
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', condition='(is_subarray(SUBARRAY)and(not(is_irs2(READPATT))))', expression='(1<=META_SUBARRAY_YSTART+SCI_ARRAY.SHAPE[-2]-1<=2048)'),
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', condition='(is_subarray(SUBARRAY)and(is_irs2(READPATT)))', expression='(1<=META_SUBARRAY_YSTART+SCI_ARRAY.SHAPE[-2]-1<=3200)'),
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', condition='(is_subarray(SUBARRAY))', expression='(1<=META_SUBARRAY_XSTART+SCI_ARRAY.SHAPE[-1]-1<=2048)'),
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', condition='(optional((True)))', expression='(is_image(DQ_ARRAY))'),
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', condition='(optional((True)))', expression="(warn_only(has_type(DQ_ARRAY,'INT')))"),
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', condition='((array_exists(SCI_ARRAY))and(array_exists(DQ_ARRAY)))', expression='(DQ_ARRAY.SHAPE[-2:]==SCI_ARRAY.SHAPE[-2:])'),
     ('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression='(is_table(DQ_DEF_ARRAY))'),
     ('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_columns(DQ_DEF_ARRAY,['BIT','VALUE','NAME','DESCRIPTION']))"),
     ('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_column_type(DQ_DEF_ARRAY,'BIT','INT'))"),
     ('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_column_type(DQ_DEF_ARRAY,'VALUE','INT'))"),
     ('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_column_type(DQ_DEF_ARRAY,'NAME','STRING'))"),
     ('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_column_type(DQ_DEF_ARRAY,'DESCRIPTION','STRING'))"),
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', 'REQUIRED', expression='(ndim(SCI_ARRAY,2))'),
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression='(ndim(DQ_ARRAY,2))'),
     ('META.EXPOSURE.GAIN_FACTOR', 'HEADER', 'REAL', 'WARN', values=('1.0:10.0',))]
    >>> test_config.cleanup(old_state)
    """

def load_miri_mask_tpn_lines():
    """Print out the outcome of various .tpn directives like "replace" and
    "include" and reuse of generic files.

    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> path = generic_tpn.get_tpn_path("miri_mask.tpn","jwst")
    >>> print("\\n".join(generic_tpn.load_tpn_lines(path)))
    META.SUBARRAY.NAME          H   C   R
    META.SUBARRAY.XSTART        H   I   R
    META.SUBARRAY.YSTART        H   I   R
    META.SUBARRAY.XSIZE         H   I   R
    META.SUBARRAY.YSIZE         H   I   R
    META.SUBARRAY.FASTAXIS      H   I   R
    META.SUBARRAY.SLOWAXIS      H   I   R
    SUBARRAY_INBOUNDS_X         X   X   A  (1<=META_SUBARRAY_XSTART+META_SUBARRAY_XSIZE-1<=1032)
    SUBARRAY_INBOUNDS_Y         X   X   A  (1<=META_SUBARRAY_YSTART+META_SUBARRAY_YSIZE-1<=1024)
    DETECTOR              H   C   O
    MIRIMAGE_AXIS         X   X   (DETECTOR=='MIRIMAGE')    ((FASTAXIS==1)and(SLOWAXIS==2))
    MIRIFULONG_AXIS       X   X   (DETECTOR=='MIRIFULONG')  ((FASTAXIS==1)and(SLOWAXIS==2))
    MIRIFUSHORT_AXIS      X   X   (DETECTOR=='MIRIFUSHORT') ((FASTAXIS==1)and(SLOWAXIS==2))
    FULLFRAME_XSTART     X           X         F             (META_SUBARRAY_XSTART==1)
    FULLFRAME_YSTART     X           X         F             (META_SUBARRAY_YSTART==1)
    FULLFRAME_XSIZE      X           X         F             (META_SUBARRAY_XSIZE==1032)
    FULLFRAME_YSIZE      X           X         F             (META_SUBARRAY_YSIZE==1024)
    SUBARRAY_XSTART      X           X         S             (1<=META_SUBARRAY_XSTART<=1032)
    SUBARRAY_YSTART      X           X         S             (1<=META_SUBARRAY_YSTART<=1024)
    SUBARRAY_XSIZE       X           X         S             (1<=META_SUBARRAY_XSIZE<=1032)
    SUBARRAY_YSIZE       X           X         S             (1<=META_SUBARRAY_YSIZE<=1024)
    DQ       A           X         R             (is_image(DQ_ARRAY))
    DQ       A           X         R             (has_type(DQ_ARRAY,'INT'))
    DQ       A           X         F             (DQ_ARRAY.SHAPE[-2:]==(1024,1032))
    DQ       A           X         S             (DQ_ARRAY.SHAPE[-2:]==(META_SUBARRAY_YSIZE,META_SUBARRAY_XSIZE))
    DQ       A           X         S             (1<=META_SUBARRAY_YSTART+DQ_ARRAY.SHAPE[-2]-1<=1024)
    DQ       A           X         S             (1<=META_SUBARRAY_XSTART+DQ_ARRAY.SHAPE[-1]-1<=1032)
    DQ       A           X         O   (ndim(DQ_ARRAY,2))
    DQ_DEF       A           X         O             (is_table(DQ_DEF_ARRAY))
    DQ_DEF       A           X         O             (has_columns(DQ_DEF_ARRAY,['BIT','VALUE','NAME','DESCRIPTION']))
    DQ_DEF       A           X         O             (has_column_type(DQ_DEF_ARRAY,'BIT','INT'))
    DQ_DEF       A           X         O             (has_column_type(DQ_DEF_ARRAY,'VALUE','INT'))
    DQ_DEF       A           X         O             (has_column_type(DQ_DEF_ARRAY,'NAME','STRING'))
    DQ_DEF       A           X         O             (has_column_type(DQ_DEF_ARRAY,'DESCRIPTION','STRING'))
    >>> test_config.cleanup(old_state)
    """

def load_miri_mask_tpn():
    """
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> path = generic_tpn.get_tpn_path("miri_mask.tpn","jwst")
    >>> pp(generic_tpn.load_tpn(path))
    [('META.SUBARRAY.NAME', 'HEADER', 'CHARACTER', 'REQUIRED', values=()),
     ('META.SUBARRAY.XSTART', 'HEADER', 'INTEGER', 'REQUIRED', values=()),
     ('META.SUBARRAY.YSTART', 'HEADER', 'INTEGER', 'REQUIRED', values=()),
     ('META.SUBARRAY.XSIZE', 'HEADER', 'INTEGER', 'REQUIRED', values=()),
     ('META.SUBARRAY.YSIZE', 'HEADER', 'INTEGER', 'REQUIRED', values=()),
     ('META.SUBARRAY.FASTAXIS', 'HEADER', 'INTEGER', 'REQUIRED', values=()),
     ('META.SUBARRAY.SLOWAXIS', 'HEADER', 'INTEGER', 'REQUIRED', values=()),
     ('SUBARRAY_INBOUNDS_X', 'EXPRESSION', 'EXPRESSION', 'ANY_SUBARRAY', expression='(1<=META_SUBARRAY_XSTART+META_SUBARRAY_XSIZE-1<=1032)'),
     ('SUBARRAY_INBOUNDS_Y', 'EXPRESSION', 'EXPRESSION', 'ANY_SUBARRAY', expression='(1<=META_SUBARRAY_YSTART+META_SUBARRAY_YSIZE-1<=1024)'),
     ('DETECTOR', 'HEADER', 'CHARACTER', 'OPTIONAL', values=()),
     ('MIRIMAGE_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(DETECTOR=='MIRIMAGE')", expression='((FASTAXIS==1)and(SLOWAXIS==2))'),
     ('MIRIFULONG_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(DETECTOR=='MIRIFULONG')", expression='((FASTAXIS==1)and(SLOWAXIS==2))'),
     ('MIRIFUSHORT_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(DETECTOR=='MIRIFUSHORT')", expression='((FASTAXIS==1)and(SLOWAXIS==2))'),
     ('FULLFRAME_XSTART', 'EXPRESSION', 'EXPRESSION', 'IF_FULL_FRAME', expression='(META_SUBARRAY_XSTART==1)'),
     ('FULLFRAME_YSTART', 'EXPRESSION', 'EXPRESSION', 'IF_FULL_FRAME', expression='(META_SUBARRAY_YSTART==1)'),
     ('FULLFRAME_XSIZE', 'EXPRESSION', 'EXPRESSION', 'IF_FULL_FRAME', expression='(META_SUBARRAY_XSIZE==1032)'),
     ('FULLFRAME_YSIZE', 'EXPRESSION', 'EXPRESSION', 'IF_FULL_FRAME', expression='(META_SUBARRAY_YSIZE==1024)'),
     ('SUBARRAY_XSTART', 'EXPRESSION', 'EXPRESSION', 'IF_SUBARRAY', expression='(1<=META_SUBARRAY_XSTART<=1032)'),
     ('SUBARRAY_YSTART', 'EXPRESSION', 'EXPRESSION', 'IF_SUBARRAY', expression='(1<=META_SUBARRAY_YSTART<=1024)'),
     ('SUBARRAY_XSIZE', 'EXPRESSION', 'EXPRESSION', 'IF_SUBARRAY', expression='(1<=META_SUBARRAY_XSIZE<=1032)'),
     ('SUBARRAY_YSIZE', 'EXPRESSION', 'EXPRESSION', 'IF_SUBARRAY', expression='(1<=META_SUBARRAY_YSIZE<=1024)'),
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'REQUIRED', expression='(is_image(DQ_ARRAY))'),
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'REQUIRED', expression="(has_type(DQ_ARRAY,'INT'))"),
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'IF_FULL_FRAME', expression='(DQ_ARRAY.SHAPE[-2:]==(1024,1032))'),
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'IF_SUBARRAY', expression='(DQ_ARRAY.SHAPE[-2:]==(META_SUBARRAY_YSIZE,META_SUBARRAY_XSIZE))'),
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'IF_SUBARRAY', expression='(1<=META_SUBARRAY_YSTART+DQ_ARRAY.SHAPE[-2]-1<=1024)'),
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'IF_SUBARRAY', expression='(1<=META_SUBARRAY_XSTART+DQ_ARRAY.SHAPE[-1]-1<=1032)'),
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression='(ndim(DQ_ARRAY,2))'),
     ('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression='(is_table(DQ_DEF_ARRAY))'),
     ('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_columns(DQ_DEF_ARRAY,['BIT','VALUE','NAME','DESCRIPTION']))"),
     ('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_column_type(DQ_DEF_ARRAY,'BIT','INT'))"),
     ('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_column_type(DQ_DEF_ARRAY,'VALUE','INT'))"),
     ('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_column_type(DQ_DEF_ARRAY,'NAME','STRING'))"),
     ('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_column_type(DQ_DEF_ARRAY,'DESCRIPTION','STRING'))")]
    >>> test_config.cleanup(old_state)
    """

def dt_acs_idctab_char_plus_column():
    """
    >>> TestCertifyScript("crds.certify data/acs_new_idc.fits --comparison-context hst_0508.pmap")()  # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/acs_new_idc.fits' (1/1) as 'FITS' relative to context 'hst_0508.pmap'
    CRDS - INFO -  FITS file 'acs_new_idc.fits' conforms to FITS standards.
    CRDS - INFO -  Comparing reference 'acs_new_idc.fits' against 'p7d1548qj_idc.fits'
    CRDS - INFO -  Mode columns defined by spec for old reference 'p7d1548qj_idc.fits[1]' are: ['DETCHIP', 'WAVELENGTH', 'DIRECTION', 'FILTER1', 'FILTER2', 'V2REF', 'V3REF']
    CRDS - INFO -  All column names for this table old reference 'p7d1548qj_idc.fits[1]' are: ['DETCHIP', 'DIRECTION', 'FILTER1', 'FILTER2', 'XSIZE', 'YSIZE', 'XREF', 'YREF', 'V2REF', 'V3REF', 'SCALE', 'CX10', 'CX11', 'CX20', 'CX21', 'CX22', 'CX30', 'CX31', 'CX32', 'CX33', 'CX40', 'CX41', 'CX42', 'CX43', 'CX44', 'CY10', 'CY11', 'CY20', 'CY21', 'CY22', 'CY30', 'CY31', 'CY32', 'CY33', 'CY40', 'CY41', 'CY42', 'CY43', 'CY44']
    CRDS - INFO -  Checking for duplicate modes using intersection ['DETCHIP', 'DIRECTION', 'FILTER1', 'FILTER2', 'V2REF', 'V3REF']
    CRDS - WARNING -  Duplicate definitions in old reference 'p7d1548qj_idc.fits[1]' for mode: (('DETCHIP', 1), ('DIRECTION', 'FORWARD'), ('FILTER1', 'F550M'), ('FILTER2', 'F220W'), ('V2REF', 207.082), ('V3REF', 471.476)) :
     (29, (('DETCHIP', 1), ('DIRECTION', 'FORWARD'), ('FILTER1', 'F550M'), ('FILTER2', 'F220W'), ...('V2REF', 207.082), ('V3REF', 471.476), ...)))
    (35, (('DETCHIP', 1), ('DIRECTION', 'FORWARD'), ('FILTER1', 'F550M'), ('FILTER2', 'F220W'), ...('V2REF', 207.082), ('V3REF', 471.476), ...)))
    CRDS - INFO -  Mode columns defined by spec for new reference 'acs_new_idc.fits[1]' are: ['DETCHIP', 'WAVELENGTH', 'DIRECTION', 'FILTER1', 'FILTER2', 'V2REF', 'V3REF']
    CRDS - INFO -  All column names for this table new reference 'acs_new_idc.fits[1]' are: ['DETCHIP', 'DIRECTION', 'FILTER1', 'FILTER2']
    CRDS - INFO -  Checking for duplicate modes using intersection ['DETCHIP', 'DIRECTION', 'FILTER1', 'FILTER2']
    CRDS - WARNING -  Change in row format between 'p7d1548qj_idc.fits[1]' and 'acs_new_idc.fits[1]'
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  2 warnings
    CRDS - INFO -  11 infos
    0
    """

def test_certify_check_rmap_updates():
    """
    This test verifies trial rmap updates under the control of the CRDS certify program.

    It checks for two primary conditions:

    1. That submitted files with identical matching criteria which would replace one another are errors.

    2. That new files which overlap the matching criteria of existing files without being identical are detected.

    Handling of (2) varies by project,  because for HST it is grudgingly permitted due to its
    existence in CDBS and the need for identical rmap behavior to CDBS.  For JWST,  where
    overlaps are avoidable,  non-identical overlaps are warnings during file submission and fatal errors
    if encountered at runtime. For HST,  warnings are only visible in --verbose mode,  but for JWST they
    are always visible.   Using warnings avoids the automatic cancellation of large file submissions,
    holding open a choice between choosing to cancel or choosing to submit manual rmap fixes instead.

    >>> old_state = test_config.setup(url="https://hst-crds-serverless.stsci.edu", observatory="hst")
    >>> TestCertifyScript("crds.certify data/s7g1700gl_dead_overlap.fits data/s7g1700gl_dead_dup1.fits data/s7g1700gl_dead_dup2.fits --check-rmap-updates --comparison-context hst_0508.pmap --verbose")()  # doctest: +ELLIPSIS
    CRDS - DEBUG -  Command: ['crds.certify', 'data/s7g1700gl_dead_overlap.fits', 'data/s7g1700gl_dead_dup1.fits', 'data/s7g1700gl_dead_dup2.fits', '--check-rmap-updates', '--comparison-context', 'hst_0508.pmap', '--verbose']
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/s7g1700gl_dead_dup1.fits' (1/3) as 'FITS' relative to context 'hst_0508.pmap'
    CRDS - DEBUG -  No unique row parameters, skipping table row checks.
    CRDS - INFO -  FITS file 's7g1700gl_dead_dup1.fits' conforms to FITS standards.
    CRDS - DEBUG -  File='s7g1700gl_dead_dup1.fits' class='Character' keyword='DESCRIP' value='INITIAL VERSION' no .tpn values defined.
    CRDS - DEBUG -  File='s7g1700gl_dead_dup1.fits' class='Character' keyword='DETECTOR' value='FUV' is in ['FUV', 'NUV']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup1.fits' class='Character' keyword='FILETYPE' value='DEADTIME REFERENCE TABLE' is in ['DEADTIME REFERENCE TABLE']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup1.fits' class='Character' keyword='INSTRUME' value='COS' is in ['COS']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup1.fits' class='Pedigree' keyword='PEDIGREE' value='GROUND' is in ['INFLIGHT', 'GROUND', 'MODEL', 'DUMMY', 'SIMULATION']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup1.fits[0]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup1.fits[1]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup1.fits[2]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup1.fits[3]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup1.fits[4]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup1.fits[5]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup1.fits[6]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup1.fits[7]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup1.fits[8]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup1.fits[9]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup1.fits' class='Sybdate' keyword='USEAFTER' value='Oct 01 1996 00:00:00'
    CRDS - DEBUG -  File='s7g1700gl_dead_dup1.fits' class='Character' keyword='VCALCOS' value='2.0' no .tpn values defined.
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/s7g1700gl_dead_dup2.fits' (2/3) as 'FITS' relative to context 'hst_0508.pmap'
    CRDS - DEBUG -  No unique row parameters, skipping table row checks.
    CRDS - INFO -  FITS file 's7g1700gl_dead_dup2.fits' conforms to FITS standards.
    CRDS - DEBUG -  File='s7g1700gl_dead_dup2.fits' class='Character' keyword='DESCRIP' value='INITIAL VERSION' no .tpn values defined.
    CRDS - DEBUG -  File='s7g1700gl_dead_dup2.fits' class='Character' keyword='DETECTOR' value='FUV' is in ['FUV', 'NUV']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup2.fits' class='Character' keyword='FILETYPE' value='DEADTIME REFERENCE TABLE' is in ['DEADTIME REFERENCE TABLE']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup2.fits' class='Character' keyword='INSTRUME' value='COS' is in ['COS']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup2.fits' class='Pedigree' keyword='PEDIGREE' value='GROUND' is in ['INFLIGHT', 'GROUND', 'MODEL', 'DUMMY', 'SIMULATION']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup2.fits[0]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup2.fits[1]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup2.fits[2]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup2.fits[3]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup2.fits[4]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup2.fits[5]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup2.fits[6]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup2.fits[7]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup2.fits[8]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup2.fits[9]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_dup2.fits' class='Sybdate' keyword='USEAFTER' value='Oct 01 1996 00:00:00'
    CRDS - DEBUG -  File='s7g1700gl_dead_dup2.fits' class='Character' keyword='VCALCOS' value='2.0' no .tpn values defined.
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/s7g1700gl_dead_overlap.fits' (3/3) as 'FITS' relative to context 'hst_0508.pmap'
    CRDS - DEBUG -  No unique row parameters, skipping table row checks.
    CRDS - INFO -  FITS file 's7g1700gl_dead_overlap.fits' conforms to FITS standards.
    CRDS - DEBUG -  File='s7g1700gl_dead_overlap.fits' class='Character' keyword='DESCRIP' value='INITIAL VERSION' no .tpn values defined.
    CRDS - DEBUG -  File='s7g1700gl_dead_overlap.fits' class='Character' keyword='DETECTOR' value='FUV|NUV' is an or'ed parameter matching ['FUV', 'NUV']
    CRDS - DEBUG -  File='s7g1700gl_dead_overlap.fits' class='Character' keyword='DETECTOR' value='FUV' is in ['FUV', 'NUV']
    CRDS - DEBUG -  File='s7g1700gl_dead_overlap.fits' class='Character' keyword='DETECTOR' value='NUV' is in ['FUV', 'NUV']
    CRDS - DEBUG -  File='s7g1700gl_dead_overlap.fits' class='Character' keyword='FILETYPE' value='DEADTIME REFERENCE TABLE' is in ['DEADTIME REFERENCE TABLE']
    CRDS - DEBUG -  File='s7g1700gl_dead_overlap.fits' class='Character' keyword='INSTRUME' value='COS' is in ['COS']
    CRDS - DEBUG -  File='s7g1700gl_dead_overlap.fits' class='Pedigree' keyword='PEDIGREE' value='GROUND' is in ['INFLIGHT', 'GROUND', 'MODEL', 'DUMMY', 'SIMULATION']
    CRDS - DEBUG -  File='s7g1700gl_dead_overlap.fits[0]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_overlap.fits[1]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_overlap.fits[2]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_overlap.fits[3]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_overlap.fits[4]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_overlap.fits[5]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_overlap.fits[6]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_overlap.fits[7]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_overlap.fits[8]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_overlap.fits[9]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
    CRDS - DEBUG -  File='s7g1700gl_dead_overlap.fits' class='Sybdate' keyword='USEAFTER' value='Oct 01 1996 00:00:00'
    CRDS - DEBUG -  File='s7g1700gl_dead_overlap.fits' class='Character' keyword='VCALCOS' value='2.0' no .tpn values defined.
    CRDS - INFO -  ########################################
    CRDS - INFO -  Checking rmap update for ('cos', 'deadtab') inserting files ['data/s7g1700gl_dead_dup1.fits', 'data/s7g1700gl_dead_dup2.fits', 'data/s7g1700gl_dead_overlap.fits']
    CRDS - INFO -  Inserting s7g1700gl_dead_dup1.fits into 'hst_cos_deadtab_0250.rmap'
    CRDS - DEBUG -  Unexpanded header [('DETECTOR', 'FUV'), ('LIFE_ADJ', 'UNDEFINED'), ('OPT_ELEM', 'UNDEFINED')]
    CRDS - DEBUG -  Skipping expansion for unused parkey 'LIFE_ADJ' of '-1.0|1.0'
    CRDS - DEBUG -  Skipping expansion for unused parkey 'LIFE_ADJ' of '-1.0|1.0'
    CRDS - DEBUG -  Skipping expansion for unused parkey 'OPT_ELEM' of 'G130M|G140L|G160M'
    CRDS - DEBUG -  Skipping expansion for unused parkey 'OPT_ELEM' of 'G185M|G225M|G230L|G285M|MIRRORA|MIRRORB'
    CRDS - DEBUG -  Expanded header [('DETECTOR', 'FUV'), ('LIFE_ADJ', 'UNDEFINED'), ('OPT_ELEM', 'UNDEFINED')]
    CRDS - DEBUG -  Mapping extra parkey 'DEADCORR' from UNDEFINED to 'N/A'.
    CRDS - DEBUG -  Validating key 'FUV'
    CRDS - DEBUG -  Checking 'DETECTOR' = 'FUV' against ('FUV', 'NUV')
    CRDS - DEBUG -  Modify found ('FUV',) augmenting UseAfterSelector(('DATE-OBS', 'TIME-OBS'), nselections=1) with 's7g1700gl_dead_dup1.fits'
    CRDS - DEBUG -  Validating key '1996-10-01 00:00:00'
    CRDS - DEBUG -  Modify found '1996-10-01 00:00:00' as primitive 's7g1700gl_dead.fits' replacing with 's7g1700gl_dead_dup1.fits'
    CRDS - INFO -  Inserting s7g1700gl_dead_dup2.fits into 'hst_cos_deadtab_0250.rmap'
    CRDS - DEBUG -  Unexpanded header [('DETECTOR', 'FUV'), ('LIFE_ADJ', 'UNDEFINED'), ('OPT_ELEM', 'UNDEFINED')]
    CRDS - DEBUG -  Skipping expansion for unused parkey 'LIFE_ADJ' of '-1.0|1.0'
    CRDS - DEBUG -  Skipping expansion for unused parkey 'LIFE_ADJ' of '-1.0|1.0'
    CRDS - DEBUG -  Skipping expansion for unused parkey 'OPT_ELEM' of 'G130M|G140L|G160M'
    CRDS - DEBUG -  Skipping expansion for unused parkey 'OPT_ELEM' of 'G185M|G225M|G230L|G285M|MIRRORA|MIRRORB'
    CRDS - DEBUG -  Expanded header [('DETECTOR', 'FUV'), ('LIFE_ADJ', 'UNDEFINED'), ('OPT_ELEM', 'UNDEFINED')]
    CRDS - DEBUG -  Mapping extra parkey 'DEADCORR' from UNDEFINED to 'N/A'.
    CRDS - DEBUG -  Validating key 'FUV'
    CRDS - DEBUG -  Checking 'DETECTOR' = 'FUV' against ('FUV', 'NUV')
    CRDS - DEBUG -  Modify found ('FUV',) augmenting UseAfterSelector(('DATE-OBS', 'TIME-OBS'), nselections=1) with 's7g1700gl_dead_dup2.fits'
    CRDS - DEBUG -  Validating key '1996-10-01 00:00:00'
    CRDS - DEBUG -  Modify found '1996-10-01 00:00:00' as primitive 's7g1700gl_dead_dup1.fits' replacing with 's7g1700gl_dead_dup2.fits'
    CRDS - ERROR -  ----------------------------------------
    Both 's7g1700gl_dead_dup2.fits' and 's7g1700gl_dead_dup1.fits' identically match case:
     ((('DETECTOR', 'FUV'),), (('DATE-OBS', '1996-10-01'), ('TIME-OBS', '00:00:00')))
    Each reference would replace the other in the rmap.
    Either reference file matching parameters need correction
    or additional matching parameters should be added to the rmap
    to enable CRDS to differentiate between the two files.
    See the file submission section of the CRDS server user's guide here:
        https://jwst-crds.stsci.edu/static/users_guide/index.html
    for more explanation.
    CRDS - INFO -  Inserting s7g1700gl_dead_overlap.fits into 'hst_cos_deadtab_0250.rmap'
    CRDS - DEBUG -  Unexpanded header [('DETECTOR', 'FUV|NUV'), ('LIFE_ADJ', 'UNDEFINED'), ('OPT_ELEM', 'UNDEFINED')]
    CRDS - DEBUG -  Skipping expansion for unused parkey 'LIFE_ADJ' of '-1.0|1.0'
    CRDS - DEBUG -  Skipping expansion for unused parkey 'LIFE_ADJ' of '-1.0|1.0'
    CRDS - DEBUG -  Skipping expansion for unused parkey 'OPT_ELEM' of 'G130M|G140L|G160M'
    CRDS - DEBUG -  Skipping expansion for unused parkey 'OPT_ELEM' of 'G185M|G225M|G230L|G285M|MIRRORA|MIRRORB'
    CRDS - DEBUG -  Expanded header [('DETECTOR', 'FUV|NUV'), ('LIFE_ADJ', 'UNDEFINED'), ('OPT_ELEM', 'UNDEFINED')]
    CRDS - DEBUG -  Mapping extra parkey 'DEADCORR' from UNDEFINED to 'N/A'.
    CRDS - DEBUG -  Validating key 'FUV|NUV'
    CRDS - DEBUG -  Checking 'DETECTOR' = 'FUV' against ('FUV', 'NUV')
    CRDS - DEBUG -  Checking 'DETECTOR' = 'NUV' against ('FUV', 'NUV')
    CRDS - DEBUG -  Modify couldn't find 'FUV|NUV' adding new selector.
    CRDS - DEBUG -  creating nested 'UseAfter' with '1996-10-01 00:00:00' = 's7g1700gl_dead_overlap.fits'
    CRDS - DEBUG -  Writing '/tmp/hst_cos_deadtab_0250.rmap'
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying '/tmp/hst_cos_deadtab_0250.rmap' as 'MAPPING' relative to context 'hst_0508.pmap'
    CRDS - DEBUG -  Parsing '/tmp/hst_cos_deadtab_0250.rmap'
    CRDS - DEBUG -  Validating 'hst_cos_deadtab_0250.rmap' with parameters (('DETECTOR',), ('DATE-OBS', 'TIME-OBS'))
    CRDS - DEBUG -  Validating key ('FUV',)
    CRDS - DEBUG -  Checking 'DETECTOR' = 'FUV' against ('FUV', 'NUV')
    CRDS - WARNING -  ----------------------------------------
    Match case
     (('DETECTOR', 'FUV'),)
    is an equal weight special case of
     (('DETECTOR', 'FUV|NUV'),)
    For some parameter sets, CRDS interprets both matches as equally good.
    See the file submission section of the CRDS server user's guide here:
        https://jwst-crds.stsci.edu/static/users_guide/index.html
    for more explanation.
     ----------------------------------------
    CRDS - DEBUG -  Validating key '1996-10-01 00:00:00'
    CRDS - DEBUG -  Validating key ('FUV|NUV',)
    CRDS - DEBUG -  Checking 'DETECTOR' = 'FUV' against ('FUV', 'NUV')
    CRDS - DEBUG -  Checking 'DETECTOR' = 'NUV' against ('FUV', 'NUV')
    CRDS - DEBUG -  Validating key '1996-10-01 00:00:00'
    CRDS - DEBUG -  Validating key ('NUV',)
    CRDS - DEBUG -  Checking 'DETECTOR' = 'NUV' against ('FUV', 'NUV')
    CRDS - WARNING -  ----------------------------------------
    Match case
     (('DETECTOR', 'NUV'),)
    is an equal weight special case of
     (('DETECTOR', 'FUV|NUV'),)
    For some parameter sets, CRDS interprets both matches as equally good.
    See the file submission section of the CRDS server user's guide here:
        https://jwst-crds.stsci.edu/static/users_guide/index.html
    for more explanation.
     ----------------------------------------
    CRDS - DEBUG -  Validating key '1996-10-01 00:00:00'
    CRDS - DEBUG -  Mapping '/tmp/hst_cos_deadtab_0250.rmap' did not change relative to context 'hst_0508.pmap'
    CRDS - INFO -  ########################################
    CRDS - INFO -  1 errors
    CRDS - INFO -  2 warnings
    CRDS - INFO -  17 infos
    1
    >>> test_config.cleanup(old_state)
    """

def test_asdf_standard_requirement_fail():
    """
    This test is currently a little vague on output because one of two errors are possible:
    - Failure due to asdf_standard_requirement
    - Failure due to the asdf library not handling the ASDF Standard version at all
    Once the servers have asdf 2.6.0+ installed, we can lock down the output a little more.

    This test verifies trial rmap updates under the control of the CRDS certify program.
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> TestCertifyScript("crds.certify data/jwst_nircam_specwcs_1_5_0.asdf --comparison-context jwst_0591.pmap")()  # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/jwst_nircam_specwcs_1_5_0.asdf' (1/1) as 'ASDF' relative to context 'jwst_0591.pmap'
    ...
    CRDS - INFO -  ########################################
    CRDS - INFO -  1 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  ... infos
    1
    >>> test_config.cleanup(old_state)
    """

def test_asdf_standard_requirement_succeed():
    """
    >>> old_state = test_config.setup(url="https://jwst-crds-serverless.stsci.edu", observatory="jwst")
    >>> TestCertifyScript("crds.certify data/jwst_nircam_specwcs_1_4_0.asdf --comparison-context jwst_0591.pmap")()  # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/jwst_nircam_specwcs_1_4_0.asdf' (1/1) as 'ASDF' relative to context 'jwst_0591.pmap'
    CRDS - INFO -  Checking JWST datamodels.
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  4 infos
    0
    >>> test_config.cleanup(old_state)
    """

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
        tinfo = generic_tpn.TpnInfo('DETECTOR','H','C','Q', ('WFC','HRC','SBC'))
        assert_raises(ValueError, validators.validator, tinfo)

    def test_validator_bad_keytype(self):
        tinfo = generic_tpn.TpnInfo('DETECTOR','Q','C','R', ('WFC','HRC','SBC'))
        assert_raises(ValueError, validators.validator, tinfo)

    def test_character_validator_file_good(self):
        tinfo = generic_tpn.TpnInfo('DETECTOR','H','C','R', ('WFC','HRC','SBC'))
        cval = validators.validator(tinfo)
        assert_true(isinstance(cval, validators.core.CharacterValidator))
        header = {"DETECTOR": "HRC"}
        cval.check(self.data('acs_new_idc.fits'), header)

    def test_character_validator_bad(self):
        tinfo = generic_tpn.TpnInfo('DETECTOR','H','C','R', ('WFC','HRC','SBC'))
        cval = validators.validator(tinfo)
        assert_true(isinstance(cval, validators.core.CharacterValidator))
        header = {"DETECTOR" : "WFD" }
        assert_raises(ValueError, cval.check, "foo.fits", header)

    def test_character_validator_missing_required(self):
        tinfo = generic_tpn.TpnInfo('DETECTOR','H','C','R', ('WFC','HRC','SBC'))
        cval = validators.validator(tinfo)
        assert_true(isinstance(cval, validators.core.CharacterValidator))
        header = {"DETECTOR" : "WFD" }
        assert_raises(ValueError, cval.check, "foo.fits", header)

    def test_character_validator_optional_bad(self):
        tinfo = generic_tpn.TpnInfo('DETECTOR','H','C','O', ('WFC','HRC','SBC'))
        cval = validators.validator(tinfo)
        assert_true(isinstance(cval, validators.core.CharacterValidator))
        header = {"DETECTOR" : "WFD" }
        assert_raises(ValueError, cval.check, "foo.fits", header)

    def test_character_validator_optional_missing(self):
        tinfo = generic_tpn.TpnInfo('DETECTOR','H','C','O', ('WFC','HRC','SBC'))
        cval = validators.validator(tinfo)
        assert_true(isinstance(cval, validators.core.CharacterValidator))
        header = {"DETECTR" : "WFC" }
        cval.check("foo.fits", header)

    # ------------------------------------------------------------------------------

    def test_logical_validator_good(self):
        tinfo = generic_tpn.TpnInfo('ROKIN','H','L','R',())
        cval = validators.validator(tinfo)
        assert_true(isinstance(cval, validators.core.LogicalValidator))
        header= {"ROKIN": "F"}
        cval.check("foo.fits", header)
        header= {"ROKIN": "T"}
        cval.check("foo.fits", header)

    def test_logical_validator_bad(self):
        tinfo = generic_tpn.TpnInfo('ROKIN','H','L','R',())
        cval = validators.validator(tinfo)
        assert_true(isinstance(cval, validators.core.LogicalValidator))
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
        info = generic_tpn.TpnInfo('READPATT', 'H', 'I', 'R', ('FOO',))
        assert_raises(ValueError, validators.validator, info)
        info = generic_tpn.TpnInfo('READPATT', 'H', 'I', 'R', ('1.0','2.0'))
        assert_raises(ValueError, validators.validator, info)

    def test_integer_validator_bad_float(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'I', 'R', ('1','2'))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.IntValidator))
        header = {"READPATT": "1.9"}
        assert_raises(ValueError, cval.check, "foo.fits", header)

    def test_integer_validator_bad_value(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'I', 'R', ('1','2','3'))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.IntValidator))
        header = {"READPATT": "4"}
        assert_raises(ValueError, cval.check, "foo.fits", header)

    def test_integer_validator_good(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'I', 'R', ('1','2','3'))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.IntValidator))
        header = {"READPATT": "2"}
        cval.check("foo.fits", header)

    def test_integer_validator_range_good(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'I', 'R', ("1:40",))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.IntValidator))
        header = {"READPATT": "39"}
        cval.check("foo.fits", header)

    def test_integer_validator_range_bad(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'I', 'R', ("1:40",))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.IntValidator))
        header = {"READPATT": "41"}
        assert_raises(ValueError, cval.check, "foo.fits", header)

    def test_integer_validator_range_boundary_good(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'I', 'R', ("1:40",))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.IntValidator))
        header = {"READPATT": "40"}
        cval.check("foo.fits", header)

    def test_integer_validator_range_format_bad(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'I', 'R', ("1:40",))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.IntValidator))
        header = {"READPATT": "40.3"}
        assert_raises(ValueError, cval.check, "foo.fits", header)
        info = generic_tpn.TpnInfo('READPATT', 'H', 'I', 'R', ("x:40",))
        assert_raises(ValueError, validators.validator, info)

    # ------------------------------------------------------------------------------

    def test_real_validator_bad_format(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ('FOO',))
        assert_raises(ValueError, validators.validator, info)
        info = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ('x.0','2.0'))
        assert_raises(ValueError, validators.validator, info)

    def test_real_validator_bad_value(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ('1.1','2.2','3.3'))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.RealValidator))
        header = {"READPATT": "3.2"}
        assert_raises(ValueError, cval.check, "foo.fits", header)

    def test_real_validator_good(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ('1.0','2.1','3.0'))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.RealValidator))
        header = {"READPATT": "2.1"}
        cval.check("foo.fits", header)

    def test_real_validator_range_good(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ("1.5:40.2",))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.RealValidator))
        header = {"READPATT": "40.1"}
        cval.check("foo.fits", header)

    def test_real_validator_range_bad(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ("1.5:40.2",))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.RealValidator))
        header = {"READPATT": "40.21"}
        assert_raises(ValueError, cval.check, "foo.fits", header)

    def test_real_validator_range_boundary_good(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ("1.4:40.1",))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.RealValidator))
        header = {"READPATT": "40.1"}
        cval.check("foo.fits", header)

    def test_real_validator_range_format_bad(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ("1.5:40.2",))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.RealValidator))
        header = {"READPATT": "40.x"}
        assert_raises(ValueError, cval.check, "foo.fits", header)
        info = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ("1.x:40.2",))
        assert_raises(ValueError, validators.validator, info)

    def test_real_validator_float_zero(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ('1','0.0'))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.RealValidator))
        header = {"READPATT": "0.0001"}
        assert_raises(ValueError, cval.check, "foo.fits", header)

    def test_real_validator_float_zero_zero(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ('1','0.0'))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.RealValidator))
        header = {"READPATT": "0.0003"}
        assert_raises(ValueError, cval.check, "foo.fits", header)

    def test_real_validator_range_inf_good(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ("5.5:inf",))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.RealValidator))
        header = {"READPATT": "100000.0"}
        cval.check("foo.fits", header)

    def test_real_validator_range_inf_bad(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ("5.5:inf",))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.RealValidator))
        header = {"READPATT": "5.4"}
        assert_raises(ValueError, cval.check, "foo.fits", header)

    # ------------------------------------------------------------------------------

    def test_double_validator_bad_format(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'D', 'R', ('FOO',))
        assert_raises(ValueError, validators.validator, info)
        info = generic_tpn.TpnInfo('READPATT', 'H', 'D', 'R', ('x.0','2.0'))
        assert_raises(ValueError, validators.validator, info)

    def test_double_validator_bad_value(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'D', 'R', ('1.1','2.2','3.3'))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.DoubleValidator))
        header = {"READPATT": "3.2"}
        assert_raises(ValueError, cval.check, "foo.fits", header)

    def test_double_validator_good(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'D', 'R', ('1.0','2.1','3.0'))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.DoubleValidator))
        header = {"READPATT": "2.1"}
        cval.check("foo.fits", header)

    def test_double_validator_range_good(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'D', 'R', ("1.5:40.2",))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.DoubleValidator))
        header = {"READPATT": "40.1"}
        cval.check("foo.fits", header)

    def test_double_validator_range_bad(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'D', 'R', ("1.5:40.2",))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.DoubleValidator))
        header = {"READPATT": "40.21"}
        assert_raises(ValueError, cval.check, "foo.fits", header)

    def test_double_validator_range_boundary_good(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'D', 'R', ("1.4:40.1",))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.DoubleValidator))
        header = {"READPATT": "40.1"}
        cval.check("foo.fits", header)

    def test_double_validator_range_format_bad(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'D', 'R', ("1.5:40.2",))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.DoubleValidator))
        header = {"READPATT": "40.x"}
        assert_raises(ValueError, cval.check, "foo.fits", header)
        info = generic_tpn.TpnInfo('READPATT', 'H', 'D', 'R', ("1.x:40.2",))
        assert_raises(ValueError, validators.validator, info)

    def test_double_validator_range_inf_good(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'D', 'R', ("5.5:inf",))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.DoubleValidator))
        header = {"READPATT": "100000.0"}
        cval.check("foo.fits", header)

    def test_double_validator_range_inf_bad(self):
        info = generic_tpn.TpnInfo('READPATT', 'H', 'D', 'R', ("5.5:inf",))
        cval = validators.validator(info)
        assert_true(isinstance(cval, validators.core.DoubleValidator))
        header = {"READPATT": "5.4"}
        assert_raises(ValueError, cval.check, "foo.fits", header)

    # ------------------------------------------------------------------------------

    def test_expression_validator_passes(self):
        tinfo = generic_tpn.TpnInfo('DETECTOR','X','X','R', ('((DETECTOR==\'FOO\')and(SUBARRAY==\'BAR\'))',))
        cval = validators.validator(tinfo)
        assert_true(isinstance(cval, validators.core.ExpressionValidator))
        header = { "DETECTOR":"FOO", "SUBARRAY":"BAR" }
        cval.check("foo.fits", header)

    def test_expression_validator_fails(self):
        tinfo = generic_tpn.TpnInfo('DETECTOR','X','X','R', ('((DETECTOR=="FOO")and(SUBARRAY=="BAR"))',))
        cval = validators.validator(tinfo)
        assert_true(isinstance(cval, validators.core.ExpressionValidator))
        header = { "DETECTOR":"FOO", "SUBARRAY":"BA" }
        assert_raises(validators.core.RequiredConditionError, cval.check, "foo.fits", header)

    def test_expression_validator_bad_format(self):
        # typical subtle expression error, "=" vs. "=="
        tinfo = generic_tpn.TpnInfo('DETECTOR','X','X','R', ('((DETECTOR="FOO")and(SUBARRAY=="BAR"))',))
        assert_raises(SyntaxError, validators.validator, tinfo)

    # ------------------------------------------------------------------------------

    def test_column_expression_validator_passes(self):
        tinfo = generic_tpn.TpnInfo('DETCHIP', 'C', 'X', 'R', ('(VALUE%2==1)',))
        cval = validators.validator(tinfo)
        assert_true(isinstance(cval, validators.core.ColumnExpressionValidator))
        cval.check(self.data('acs_new_idc.fits'), {})

    def test_column_expression_validator_fails(self):
        tinfo = generic_tpn.TpnInfo('DETCHIP', 'C', 'X', 'R', ('(VALUE%2==0)',))
        cval = validators.validator(tinfo)
        assert_raises(exceptions.RequiredConditionError, cval.check, self.data('acs_new_idc.fits'), {})

    def test_column_expression_validator_header_variable(self):
        tinfo = generic_tpn.TpnInfo('DETCHIP', 'C', 'X', 'R', ('(DETECTOR=="FOO")',))
        cval = validators.validator(tinfo)
        header = { "DETECTOR": "FOO" }
        assert_raises(exceptions.RequiredConditionError, cval.check, self.data('acs_new_idc.fits'), header)

    # ------------------------------------------------------------------------------

    def test_synphot_graph_validator_passes(self):
        tinfo = generic_tpn.TpnInfo('EXT1', 'D', 'X', 'R', ('&SYNPHOT_GRAPH',))
        cval = validators.validator(tinfo)
        assert_true(isinstance(cval, validators.synphot.SynphotGraphValidator))
        assert_true(cval.check(self.data('hst_synphot_tmg_connected.fits'), {}))

    def test_synphot_graph_validator_fails(self):
        tinfo = generic_tpn.TpnInfo('EXT1', 'D', 'X', 'R', ('&SYNPHOT_GRAPH',))
        cval = validators.validator(tinfo)
        assert_false(cval.check(self.data('hst_synphot_tmg_disconnected.fits'), {}))

    # ------------------------------------------------------------------------------

    def test_synphot_lookup_validator_passes(self):
        tinfo = generic_tpn.TpnInfo('EXT1', 'D', 'X', 'R', ('&SYNPHOT_LOOKUP',))
        cval = validators.validator(tinfo)
        assert_true(isinstance(cval, validators.synphot.SynphotLookupValidator))
        assert_true(cval.check(self.data('hst_synphot_tmc_passes.fits'), {}))

    def test_synphot_lookup_validator_fails(self):
        tinfo = generic_tpn.TpnInfo('EXT1', 'D', 'X', 'R', ('&SYNPHOT_LOOKUP',))
        cval = validators.validator(tinfo)
        assert_false(cval.check(self.data('hst_synphot_tmc_bad_filename.fits'), {}))

    # ------------------------------------------------------------------------------

    def test_synphot_throughput_validator_passes(self):
        tinfo = generic_tpn.TpnInfo('EXT1', 'D', 'X', 'R', ('&SYNPHOT_THROUGHPUT',))
        cval = validators.validator(tinfo, context="hst_0787.pmap")
        assert_true(isinstance(cval, validators.synphot.SynphotThroughputValidator))
        header = { "COMPNAME": "acs_f555w_hrc"}
        assert_true(cval.check(self.data('acs_f555w_hrc_007_syn.fits'), header))

    def test_synphot_throughput_validator_fails(self):
        tinfo = generic_tpn.TpnInfo('EXT1', 'D', 'X', 'R', ('&SYNPHOT_THROUGHPUT',))
        cval = validators.validator(tinfo, context="hst_0787.pmap")
        header = { "COMPNAME": "acs_f555w_hrc"}
        assert_false(cval.check(self.data('acs_f555w_hrc_006_syn.fits'), header))

    # ------------------------------------------------------------------------------

    def test_synphot_thermal_validator_passes(self):
        tinfo = generic_tpn.TpnInfo('EXT1', 'D', 'X', 'R', ('&SYNPHOT_THERMAL',))
        cval = validators.validator(tinfo, context="hst_0787.pmap")
        assert_true(isinstance(cval, validators.synphot.SynphotThermalValidator))
        header = { "COMPNAME": "wfc3_ir_g141_src"}
        assert_true(cval.check(self.data('wfc3_ir_g141_src_999_th.fits'), header))

    def test_synphot_thermal_validator_fails(self):
        tinfo = generic_tpn.TpnInfo('EXT1', 'D', 'X', 'R', ('&SYNPHOT_THERMAL',))
        cval = validators.validator(tinfo, context="hst_0787.pmap")
        header = { "COMPNAME": "wfc3_ir_g141_src"}
        assert_false(cval.check(self.data('wfc3_ir_g141_src_003_th.fits'), header))

    # ------------------------------------------------------------------------------

    def test_conditionally_required_bad_format(self):
        # typical subtle expression error, "=" vs. "=="
        tinfo = generic_tpn.TpnInfo('DETECTOR','X', 'X', '(SUBARRAY="BAR")', ("FOO","BAR","BAZ"))
        assert_raises(SyntaxError, validators.validator, tinfo)

    def test_conditionally_required_good(self):
        # typical subtle expression error, "=" vs. "=="
        tinfo = generic_tpn.TpnInfo('DETECTOR','H', 'C', '(SUBARRAY=="BAR")', ("FOO","BAR","BAZ"))
        cval = validators.validator(tinfo)
        header = { "DETECTOR" : "FOO", "SUBARRAY":"BAR" }
        cval.check("foo.fits", header)

    def test_conditionally_required_bad(self):
        # typical subtle expression error, "=" vs. "=="
        tinfo = generic_tpn.TpnInfo('DETECTOR','H', 'C', '(SUBARRAY=="BAR")', ("FOO","BAR","BAZ"))
        checker = validators.validator(tinfo)
        header = { "DETECTOR" : "FRODO", "SUBARRAY":"BAR" }
        assert_raises(ValueError, checker.check, "foo.fits", header)

    def test_conditionally_not_required(self):
        # typical subtle expression error, "=" vs. "=="
        tinfo = generic_tpn.TpnInfo('DETECTOR','H', 'C', '(SUBARRAY=="BAR")', ("FOO","BAR","BAZ"))
        checker = validators.validator(tinfo)
        header = { "DETECTOR" : "FRODO", "SUBARRAY":"BAZ" }
        checker.check("foo.fits", header)

    def test_not_conditionally_required(self):
        # typical subtle expression error, "=" vs. "=="
        info = generic_tpn.TpnInfo('DETECTOR','H', 'C', 'R', ("FOO","BAR","BAZ"))
        checker = validators.validator(info)
        assert_true(not checker.conditionally_required)  #

    def test_conditional_warning_true_present(self):
        info = generic_tpn.TpnInfo('PIXAR_SR', 'H', 'R', "(warning(not(('MRS')in(EXP_TYPE))))", ())
        checker = validators.validator(info)
        assert_true(checker.conditionally_required)
        header = {"EXP_TYPE":"MIR_LRS-FIXEDSLIT", "PIXAR_SR":"999.0"}
        assert_true(checker.is_applicable(header)=='W')  #
        checker.handle_missing(header)

    def test_conditional_warning_true_absent(self):
        info = generic_tpn.TpnInfo('PIXAR_SR', 'H', 'R', "(warning(not(('MRS')in(EXP_TYPE))))", ())
        checker = validators.validator(info)
        assert_true(checker.conditionally_required)
        header = {"EXP_TYPE":"MIR_LRS-FIXEDSLIT", "PIXAR_SR":"999.0"}
        assert_true(checker.is_applicable(header)=='W')  #
        checker.handle_missing(header)

    def test_conditional_warning_false_present(self):
        info = generic_tpn.TpnInfo('PIXAR_SR', 'H', 'R', "(warning(not(('MRS')in(EXP_TYPE))))", ())
        checker = validators.validator(info)
        assert_true(checker.conditionally_required)
        header = {"EXP_TYPE":"MIR_FLAT-MRS", "PIXAR_SR":"999.0"}
        assert_true(checker.is_applicable(header)==False)  #
        checker.handle_missing(header)

    def test_conditional_warning_false_absent(self):
        info = generic_tpn.TpnInfo('PIXAR_SR', 'H', 'R', "(warning(not(('MRS')in(EXP_TYPE))))", ())
        checker = validators.validator(info)
        assert_true(checker.conditionally_required)
        header = {"EXP_TYPE":"MIR_FLAT-MRS"}
        assert_true(checker.is_applicable(header)==False)  #
        checker.handle_missing(header)

    def test_conditional_optional_true_present(self):
        info = generic_tpn.TpnInfo('PIXAR_SR', 'H', 'R', "(optional(not(('MRS')in(EXP_TYPE))))", ())
        checker = validators.validator(info)
        assert_true(checker.conditionally_required)
        header = {"EXP_TYPE":"MIR_LRS-FIXEDSLIT", "PIXAR_SR":"999.0"}
        assert_true(checker.is_applicable(header)=='O')  #
        checker.handle_missing(header)

    def test_conditional_optional_true_absent(self):
        info = generic_tpn.TpnInfo('PIXAR_SR', 'H', 'R', "(optional(not(('MRS')in(EXP_TYPE))))", ())
        checker = validators.validator(info)
        assert_true(checker.conditionally_required)
        header = {"EXP_TYPE":"MIR_LRS-FIXEDSLIT"}
        assert_true(checker.is_applicable(header)=='O')  #
        checker.handle_missing(header)

    def test_conditional_optional_false_present(self):
        info = generic_tpn.TpnInfo('PIXAR_SR', 'H', 'R', "(optional(not(('MRS')in(EXP_TYPE))))", ())
        checker = validators.validator(info)
        assert_true(checker.conditionally_required)
        header = {"EXP_TYPE":"MIR_FLAT-MRS", "PIXAR_SR":"999.0"}
        assert_true(checker.is_applicable(header)==False)  #
        checker.handle_missing(header)

    def test_conditional_optional_false_absent(self):
        info = generic_tpn.TpnInfo('PIXAR_SR', 'H', 'R', "(optional(not(('MRS')in(EXP_TYPE))))", ())
        checker = validators.validator(info)
        assert_true(checker.conditionally_required)
        header = {"EXP_TYPE":"MIR_FLAT-MRS"}
        assert_true(checker.is_applicable(header)==False)  #
        checker.handle_missing(header)

    def test_tpn_bad_presence(self):
        try:
            generic_tpn.TpnInfo('DETECTOR','H', 'C', 'Q', ("FOO","BAR","BAZ"))
        except ValueError as exc:
            assert_true("presence" in str(exc), "Wrong exception for test_tpn_bad_presence")

    def test_tpn_bad_group_keytype(self):
        info = generic_tpn.TpnInfo('DETECTOR','G', 'C', 'R', ("FOO","BAR","BAZ"))
        checker = validators.validator(info)
        warns = log.warnings()
        checker.check("test.fits", {"DETECTOR":"FOO"})
        new_warns = log.warnings()
        assert_true(new_warns - warns >= 1, "No warning issued for unsupported group .tpn constraint type.")

    def test_tpn_repr(self):
        # typical subtle expression error, "=" vs. "=="
        info = generic_tpn.TpnInfo('DETECTOR','H', 'C', 'R', ("FOO","BAR","BAZ"))
        repr(validators.validator(info))

    def test_tpn_check_value_method_not_implemented(self):
        # typical subtle expression error, "=" vs. "=="
        info = generic_tpn.TpnInfo('DETECTOR','H', 'C', 'R', ("FOO","BAR","BAZ"))
        checker = validators.core.Validator(info)
        assert_raises(NotImplementedError, checker.check, "test.fits", header={"DETECTOR":"FOO"})

    def test_tpn_handle_missing(self):
        # typical subtle expression error, "=" vs. "=="
        info = generic_tpn.TpnInfo('DETECTOR','H', 'C', 'W', ("FOO","BAR","BAZ"))
        checker = validators.validator(info)
        assert_true(checker.handle_missing(header={"READPATT":"FOO"}) == "UNDEFINED")
        info = generic_tpn.TpnInfo('DETECTOR','H', 'C', 'S', ("FOO","BAR","BAZ"))
        checker = validators.validator(info)
        assert_true(checker.handle_missing(header={"READPATT":"FOO"}) == "UNDEFINED")
        info = generic_tpn.TpnInfo('DETECTOR','H', 'C', 'F', ("FOO","BAR","BAZ"))
        checker = validators.validator(info)
        assert_true(checker.handle_missing(header={"READPATT":"FOO"}) == "UNDEFINED")

    def test_tpn_handle_missing_conditional(self):
        # typical subtle expression error, "=" vs. "=="
        info = generic_tpn.TpnInfo('DETECTOR','H', 'C', "(READPATT=='FOO')", ("FOO","BAR","BAZ"))
        checker = validators.validator(info)
        assert_raises(exceptions.MissingKeywordError, checker.handle_missing, header={"READPATT":"FOO"})
        assert_true(checker.handle_missing(header={"READPATT":"BAR"}) == "UNDEFINED")


    def test_missing_column_validator(self):
        info = generic_tpn.TpnInfo('FOO','C', 'C', 'R', ("X","Y","Z"))
        checker = validators.validator(info)
        assert_raises(exceptions.MissingKeywordError, checker.check, self.data("v8q14451j_idc.fits"),
                      header={"DETECTOR":"IRRELEVANT"})

    def test_tpn_excluded_keyword(self):
        # typical subtle expression error, "=" vs. "=="
        info = generic_tpn.TpnInfo('DETECTOR','H', 'C', 'E', ())
        checker = validators.validator(info)
        assert_raises(exceptions.IllegalKeywordError, checker.check, "test.fits", {"DETECTOR":"SHOULDNT_DEFINE"})

    def test_tpn_not_value(self):
        # typical subtle expression error, "=" vs. "=="
        info = generic_tpn.TpnInfo('SUBARRAY','H', 'C', 'R', ["NOT_GENERIC"])
        checker = validators.validator(info)
        assert_raises(ValueError, checker.check, "test.fits", {"SUBARRAY":"GENERIC"})

    def test_tpn_or_bar_value(self):
        # typical subtle expression error, "=" vs. "=="
        info = generic_tpn.TpnInfo('DETECTOR','H', 'C', 'R', ["THIS","THAT","OTHER"])
        checker = validators.validator(info)
        checker.check("test.fits", {"DETECTOR":"THAT|THIS"})

        info = generic_tpn.TpnInfo('DETECTOR','H', 'C', 'R', ["THAT","OTHER"])
        checker = validators.validator(info)
        assert_raises(ValueError, checker.check, "test.fits", {"DETECTOR":"THAT|THIS"})

    def test_tpn_esoteric_value(self):
        # typical subtle expression error, "=" vs. "=="
        info = generic_tpn.TpnInfo('DETECTOR','H', 'C', 'R', ["([abc]+)","BETWEEN_300_400","#OTHER#"])
        checker = validators.validator(info)
        checker.check("test.fits", {"DETECTOR":"([abc]+)"})
        assert_raises(ValueError, checker.check, "test.fits", {"DETECTOR": "([def]+)"})

        info = generic_tpn.TpnInfo('DETECTOR','H', 'C', 'R', ["{.*1234}","BETWEEN_300_400","#OTHER#"])
        checker = validators.validator(info)
        checker.check("test.fits", {"DETECTOR":"{.*1234}"})

        info = generic_tpn.TpnInfo('DETECTOR','H', 'C', 'R', ["(THIS)","BETWEEN_300_400","#OTHER#"])
        checker = validators.validator(info)
        checker.check("test.fits", {"DETECTOR":"BETWEEN_300_400"})

        info = generic_tpn.TpnInfo('DETECTOR','H', 'C', 'R', ["# >1 and <37 #","BETWEEN_300_400","#OTHER#"])
        checker = validators.validator(info)
        checker.check("test.fits", {"DETECTOR":"# >1 and <37 #"})

        # This demos synatax/check for "NOT FOO" in rmap match tuples
        info = generic_tpn.TpnInfo('DETECTOR','H', 'C', 'R', ["NOT_FOO","BETWEEN_300_400","#OTHER#"])
        checker = validators.validator(info)
        checker.check("test.fits", {"DETECTOR":"NOT_FOO"})

    def test_tpn_pedigree_missing(self):
        info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = validators.validator(info)
        assert_raises(exceptions.MissingKeywordError,
            checker.check, "test.fits", {"DETECTOR":"This is a test"})

    def test_tpn_pedigree_dummy(self):
        info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = validators.validator(info)
        checker.check("test.fits", {"PEDIGREE":"DUMMY"})

    def test_tpn_pedigree_ground(self):
        info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = validators.validator(info)
        checker.check("test.fits", {"PEDIGREE":"GROUND"})

    def test_tpn_pedigree_simulation(self):
        info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = validators.validator(info)
        checker.check("test.fits", {"PEDIGREE":"SIMULATION"})

    def test_tpn_pedigree_bad_leading(self):
        info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = validators.validator(info)
        assert_raises(ValueError, checker.check, "test.fits", {"PEDIGREE":"xDUMMY"})

    def test_tpn_pedigree_bad_trailing(self):
        # typical subtle expression error, "=" vs. "=="
        info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = validators.validator(info)
        assert_raises(ValueError, checker.check, "test.fits", {"PEDIGREE":"DUMMYxyz"})

    def test_tpn_pedigree_inflight_no_date(self):
        info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = validators.validator(info)
        assert_raises(ValueError, checker.check, "test.fits", {"PEDIGREE":"INFLIGHT"})

    def test_tpn_pedigree_equal_start_stop(self):
        info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = validators.validator(info)
        checker.check("test.fits", {"PEDIGREE":"INFLIGHT 02/01/2017 02/01/2017"})

    def test_tpn_pedigree_bad_datetime_order(self):
        info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = validators.validator(info)
        assert_raises(ValueError, checker.check, "test.fits", {"PEDIGREE":"INFLIGHT 2017-01-02 2017-01-01"})

    def test_tpn_pedigree_good_datetime_slash(self):
        info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = validators.validator(info)
        checker.check("test.fits", {"PEDIGREE":"INFLIGHT 02/01/2017 03/01/2017"})

    def test_tpn_pedigree_bad_datetime_slash(self):
        info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = validators.validator(info)
        assert_raises(ValueError, checker.check, "test.fits", {"PEDIGREE":"INFLIGHT 02/25/2017 03/01/2017"})

    def test_tpn_pedigree_good_datetime_dash(self):
        info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = validators.validator(info)
        checker.check("test.fits", {"PEDIGREE":"INFLIGHT 2017-01-01 2017-01-02"})

    def test_tpn_pedigree_bad_datetime_dash(self):
        info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = validators.validator(info)
        assert_raises(ValueError, checker.check, "test.fits", {"PEDIGREE":"INFLIGHT 2017-01-01 01-02-2017"})

    def test_tpn_pedigree_bad_datetime_dash_dash(self):
        info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = validators.validator(info)
        assert_raises(ValueError, checker.check, "test.fits", {"PEDIGREE":"INFLIGHT 2017-01-01 - 2017-01-02"})

    def test_tpn_pedigree_bad_datetime_format_1(self):
        info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = validators.validator(info)
        assert_raises(ValueError, checker.check, "test.fits",
                      {"PEDIGREE":"INFLIGHT 2017-01-01 - 2017-01-02 -"})

    def test_tpn_pedigree_bad_datetime_format_2(self):
        info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = validators.validator(info)
        assert_raises(ValueError, checker.check,
                      "test.fits", {"PEDIGREE":"INFLIGHT 2017-01-01 - 2017/01/02"})

    def test_tpn_pedigree_bad_datetime_format_3(self):
        info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
        checker = validators.validator(info)
        assert_raises(ValueError, checker.check,
                      "test.fits", {"PEDIGREE":"INFLIGHT 2017-01-01T00:00:00 2017-01-02"})

    def test_tpn_jwstpedigree_dashdate(self):
        info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&JWSTPEDIGREE"])
        checker = validators.validator(info)
        checker.check(
            "test.fits", {"PEDIGREE":"INFLIGHT 2017-01-01 2017-01-02"})

    def test_tpn_jwstpedigree_ground_dates(self):
        info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&JWSTPEDIGREE"])
        checker = validators.validator(info)
        assert_raises(
            ValueError, checker.check, "test.fits",
            {"PEDIGREE":"GROUND 2018-01-01 2018-01-25"})

    def test_tpn_jwstpedigree_nodate_format_3(self):
        info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&JWSTPEDIGREE"])
        checker = validators.validator(info)
        assert_raises(
            ValueError, checker.check, "test.fits", {"PEDIGREE":"INFLIGHT"})

    def test_tpn_jwstpedigree_missing_format_3(self):
        info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&JWSTPEDIGREE"])
        checker = validators.validator(info)
        assert_raises(
            exceptions.MissingKeywordError, checker.check, "test.fits", {})

    def test_tpn_jwstpedigree_no_model_3(self):
        info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&JWSTPEDIGREE"])
        checker = validators.validator(info)
        assert_raises(
            ValueError, checker.check, "test.fits", {"PEDIGREE":"MODEL"})

    def test_tpn_pedigree_missing_column(self):
        info = generic_tpn.TpnInfo('PEDIGREE','C', 'C', 'R', ["&PEDIGREE"])
        checker = validators.validator(info)
        assert_raises(exceptions.MissingKeywordError, checker.check_column, "data/x2i1559gl_wcp.fits", {})

    def test_tpn_pedigree_ok_column(self):
        info = generic_tpn.TpnInfo('PEDIGREE','C', 'C', 'R', ["&PEDIGREE"])
        checker = validators.validator(info)
        header = data_file.get_header(self.data("16j16005o_apd.fits"))
        checker.check_column("data/16j16005o_apd.fits", header)

# ------------------------------------------------------------------------------

    def test_sybdate_validator(self):
        tinfo = generic_tpn.TpnInfo('USEAFTER','H','C','R',('&SYBDATE',))
        cval = validators.validator(tinfo)
        assert_true(isinstance(cval,validators.core.SybdateValidator))
        header = data_file.get_header(self.data("acs_new_idc.fits"))
        cval.check(self.data('acs_new_idc.fits'), header)

    def test_slashdate_validator(self):
        tinfo = generic_tpn.TpnInfo('USEAFTER','H','C','R',('&SLASHDATE',))
        checker = validators.validator(tinfo)
        checker.check("test.fits", {"USEAFTER":"25/12/2016"})
        assert_raises(ValueError, checker.check, "test.fits", {"USEAFTER":"2017-12-25"})

    def test_Anydate_validator(self):
        tinfo = generic_tpn.TpnInfo('USEAFTER','H','C','R',('&ANYDATE',))
        checker = validators.validator(tinfo)
        checker.check("test.fits", {"USEAFTER":"25/12/2016"})
        checker.check("test.fits", {"USEAFTER":"Mar 21 2001 12:00:00 am"})
        assert_raises(ValueError, checker.check, "test.fits", {"USEAFTER":"2017-01-01T00:00:00.000"})
        assert_raises(ValueError, checker.check, "test.fits", {"USEAFTER":"12-25-2017"})
        assert_raises(ValueError, checker.check, "test.fits", {"USEAFTER":"Mxx 21 2001 01:00:00 PM"})
        assert_raises(ValueError, checker.check, "test.fits", {"USEAFTER":"35/12/20117"})

# ------------------------------------------------------------------------------

    def certify_files(self, *args, **keys):
        keys = dict(keys)
        keys["check_rmap"] = True
        return certify.certify_files(*args, **keys)

    def certify_rmap_missing_parkey(self):
        self.certify_files([self.data("hst_missing_parkey.rmap")], "hst.pmap", observatory="hst")

    def certify_no_corresponding_rmap(self):
        self.certify_files([self.data("acs_new_idc.fits")], "hst.pmap", observatory="hst")

    def certify_missing_provenance(self):
        self.certify_files([self.data("acs_new_idc.fits")], "hst.pmap", observatory="hst",
                              dum_provenance=True, provenance=["GAIN"])

# ------------------------------------------------------------------------------
    def test_check_dduplicates(self):
        self.certify_files([self.data("hst.pmap")], "hst.pmap", observatory="hst")
        self.certify_files([self.data("hst_acs.imap")], "hst.pmap", observatory="hst")
        self.certify_files([self.data("hst_acs_darkfile.rmap")], "hst.pmap", observatory="hst")

    def test_check_comment(self):
        self.certify_files([self.data("hst.pmap")], "hst.pmap", observatory="hst")
        self.certify_files([self.data("hst_acs.imap")], "hst.pmap", observatory="hst")
        self.certify_files([self.data("hst_acs_darkfile_comment.rmap")], "hst.pmap", observatory="hst")

    def test_table_mode_checks_identical(self):
        self.certify_files([self.data("v8q14451j_idc.fits")], "hst.pmap", observatory="hst",
                              compare_old_reference=True)

    def test_table_mode_checks_missing_modes(self):
        self.certify_files([self.data("v8q1445xx_idc.fits")], "hst.pmap", observatory="hst",
                              compare_old_reference=True)

    def test_UnknownCertifier_missing(self):
        # log.set_exception_trap("test")
        assert_raises(FileNotFoundError, certify.certify_file,
            self.data("non-existent-file.txt"), "jwst.pmap", observatory="jwst")

    def test_FitsCertify_bad_value(self):
        assert_raises(ValueError, certify.certify_file,
            self.data("s7g1700gm_dead_broken.fits"), "hst.pmap", observatory="hst")

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
        script = certify.CertifyScript("crds.certify crds://hst_0317.pmap --dont-recurse-mappings")
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
        info = generic_tpn.TpnInfo('SCI','D','X','R',('&KernelUnity',))
        checker = validators.core.KernelunityValidator(info)
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
        info = generic_tpn.TpnInfo('SCI','D','X','R',('&KernelUnity',))
        checker = validators.core.KernelunityValidator(info)
        assert_raises(exceptions.BadKernelSumError, checker.check, "test.fits", header)


# ==================================================================================

def main():
    """Run module tests,  for now just doctests only."""
    import unittest

    # suite = unittest.TestLoader().loadTestsFromTestCase(TestHSTTpnInfoClass)
    # unittest.TextTestRunner().run(suite)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestCertify)
    unittest.TextTestRunner().run(suite)

    from crds.tests import test_certify, tstmod
    return tstmod(test_certify)

if __name__ == "__main__":
    print(main())
