import asdf
from pytest import mark, xfail
import numpy as np
import logging
from metrics_logger.decorators import metrics_logger
from crds.core import utils, log, exceptions
from crds import data_file, certify
from crds.certify import CertifyScript, generic_tpn, validators, mapping_parser


log.THE_LOGGER.logger.propagate=True

@mark.hst
@mark.certify
def test_certify_truncated_file(default_shared_state, hst_data, caplog):
    argv = f"crds.certify {hst_data}/truncated.fits --comparison-context hst.pmap"
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(argv)()
        out = caplog.text
    expected_out = f"""Certifying '{hst_data}/truncated.fits' (1/1) as 'FITS' relative to context 'hst.pmap'
 AstropyUserWarning : astropy.io.fits.file : File may have been truncated: actual file length (7000) is smaller than the expected size (8640)
 0 errors
 18 warnings"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.hst
@mark.certify
def test_certify_bad_checksum(default_shared_state, hst_data, caplog):
    argv = f"crds.certify {hst_data}/s7g1700gl_dead_bad_xsum.fits --run-fitsverify --comparison-context hst_0508.pmap"
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(argv)()
        out = caplog.text

    expected_out = f"""Certifying
    s7g1700gl_dead_bad_xsum.fits' (1/1) as 'FITS' relative to context 'hst_0508.pmap'
    AstropyUserWarning : astropy.io.fits.hdu.base : Checksum verification failed for HDU ('', 1).
    AstropyUserWarning : astropy.io.fits.hdu.base : Datasum verification failed for HDU ('', 1).
    FITS file 's7g1700gl_dead_bad_xsum.fits' conforms to FITS standards.
    AstropyUserWarning : astropy.io.fits.hdu.base : Checksum verification failed for HDU ('', 1).
    AstropyUserWarning : astropy.io.fits.hdu.base : Datasum verification failed for HDU ('', 1).
    AstropyUserWarning : astropy.io.fits.hdu.base : Checksum verification failed for HDU ('', 1).
    AstropyUserWarning : astropy.io.fits.hdu.base : Datasum verification failed for HDU ('', 1).
    Running fitsverify.
    >> 2 Header-Data Units in this file.
    >>
    >> =================== HDU 1: Primary Array ===================
    >>
    >>  23 header keywords
    >>
    >>  Null data array; NAXIS = 0
    >>
    >> =================== HDU 2: BINARY Table ====================
    >>
    >> RECATEGORIZED *** Warning: Data checksum is not consistent with  the DATASUM keyword
    >> RECATEGORIZED *** Warning: HDU checksum is not in agreement with CHECKSUM.
    >> *** Error:   checking data fill: Data fill area invalid
    >>
    >>  31 header keywords
    >>
    >>    (3 columns x 10 rows)
    >>
    >>  Col# Name (Units)       Format
    >>    1 SEGMENT              4A
    >>    2 OBS_RATE (count /s / D
    >>    3 LIVETIME             D
    >>
    >> ++++++++++++++++++++++ Error Summary  ++++++++++++++++++++++
    >>
    >>  HDU#  Name (version)       Type             Warnings  Errors
    >>  1                          Primary Array    0         0
    >>  2                          Binary Table     2         1
    >>
    >> **** Verification found 2 warning(s) and 1 error(s). ****
    Fitsverify returned a NONZERO COMMAND LINE ERROR STATUS.
    Fitsverify output contains errors or warnings CRDS recategorizes as ERRORs.
    ########################################
    4 errors
    6 warnings"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.hst
@mark.certify
def test_certify_good_checksum(default_shared_state, hst_data, caplog):
    argv = f"crds.certify {hst_data}/s7g1700gl_dead_good_xsum.fits --run-fitsverify --comparison-context hst_0508.pmap"
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(argv)()
        out = caplog.text

    expected_out = """Certifying
    s7g1700gl_dead_good_xsum.fits' (1/1) as 'FITS' relative to context 'hst_0508.pmap'
    FITS file 's7g1700gl_dead_good_xsum.fits' conforms to FITS standards.
    Running fitsverify.
    >> 2 Header-Data Units in this file.
    >>
    >> =================== HDU 1: Primary Array ===================
    >>
    >>  23 header keywords
    >>
    >>  Null data array; NAXIS = 0
    >>
    >> =================== HDU 2: BINARY Table ====================
    >>
    >>  31 header keywords
    >>
    >>    (3 columns x 10 rows)
    >>
    >>  Col# Name (Units)       Format
    >>    1 SEGMENT              4A
    >>    2 OBS_RATE (count /s / D
    >>    3 LIVETIME             D
    >>
    >> ++++++++++++++++++++++ Error Summary  ++++++++++++++++++++++
    >>
    >>  HDU#  Name (version)       Type             Warnings  Errors
    >>  1                          Primary Array    0         0
    >>  2                          Binary Table     0         0
    >>
    >> **** Verification found 0 warning(s) and 0 error(s). ****
    ########################################
    0 errors
    0 warnings"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


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


@mark.jwst
@mark.certify
def test_certify_interpret_fitsverify_1(jwst_serverless_state, caplog):
    with caplog.at_level(logging.INFO, logger="CRDS"):
        certify.certify.interpret_fitsverify_output(1, INTERPRET_FITSVERIFY)
        out = caplog.text

    expected_out = """ >> Running fitsverify.
>>
>>               fitsverify 4.18 (CFITSIO V3.370)
>>               --------------------------------
>>
>>
>> File: ./s7g1700gl_dead_bad_xsum.fits
>>
>> 2 Header-Data Units in this file.
>>
>> =================== HDU 1: Primary Array ===================
>>
>> 23 header keywords
>>
>> Null data array; NAXIS = 0
>>
>> =================== HDU 2: BINARY Table ====================
>>
>> RECATEGORIZED *** Warning: Data checksum is not consistent with  the DATASUM keyword
>> RECATEGORIZED *** Warning: HDU checksum is not in agreement with CHECKSUM.
>>
>> 31 header keywords
>>
>>    (3 columns x 10 rows)
>>
>>  Col# Name (Units)       Format
>>    1 SEGMENT              4A
>>    2 OBS_RATE (count /s / D
>>    3 LIVETIME             D
>>
>> ++++++++++++++++++++++ Error Summary  ++++++++++++++++++++++
>>
>>  HDU#  Name (version)       Type             Warnings  Errors
>>  1                          Primary Array    0         0
>>  2                          Binary Table     2         1
>>
>> Verification found 2 warning(s) and 0 error(s). ****
Fitsverify returned a NONZERO COMMAND LINE ERROR STATUS.
Fitsverify output contains errors or warnings CRDS recategorizes as ERRORs."""
    certify.certify.interpret_fitsverify_output(0, "")
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.jwst
@mark.certify
def test_certify_interpret_fitsverify_2(jwst_serverless_state, caplog):
    with caplog.at_level(logging.INFO, logger="CRDS"):
        certify.certify.interpret_fitsverify_output(1, INTERPRET_FITSVERIFY2)
        out = caplog.text

    expected_out =     """
>>
>>               fitsverify 4.18 (CFITSIO V3.410)
>>               --------------------------------
>>
>>
>> File: jwst_nircam_photom_nrcalong.fits
>>
>> 3 Header-Data Units in this file.
>>
>> =================== HDU 1: Primary Array ===================
>>
>>  33 header keywords
>>
>>  Null data array; NAXIS = 0
>>
>> =================== HDU 2: BINARY Table ====================
>>
>>  27 header keywords
>>
>>  PHOTOM(1)  (8 columns x 41 rows)
>>
>>  Col# Name (Units)       Format
>>    1 filter               12A
>>    2 pupil                12A
>>    3 order                E
>>    4 photmjsr             E
>>    5 uncertainty          I
>>    6 nelem                I
>>    7 wavelength           3000E
>>    8 relresponse          3000E
>>
>> =================== HDU 3: Image Exten. ====================
>>
>> RECATEGORIZED *** Error:   Unregistered XTENSION value "ASDF    ".
>>
>>  9 header keywords
>>
>> ASDF 8-bit integer pixels,  1 axes (2880),
>>
>> ++++++++++++++++++++++ Error Summary  ++++++++++++++++++++++
>>
>>  HDU#  Name (version)       Type             Warnings  Errors
>>  1                          Primary Array    0         0
>>  2     PHOTOM (1)           Binary Table     0         0
>>  3     ASDF                 Image Array      0         1
>>
>> **** Verification found 0 warning(s) and 1 error(s). ****
Fitsverify returned a NONZERO COMMAND LINE ERROR STATUS.
Fitsverify output contains errors or warnings CRDS recategorizes as INFOs."""
    certify.certify.interpret_fitsverify_output(0, "")
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.hst
@mark.certify
def test_certify_dump_provenance_fits(default_shared_state, hst_data, caplog):
    argv = f"crds.certify {hst_data}/s7g1700gl_dead.fits --dump-provenance --comparison-context hst.pmap"
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(argv)()
        out = caplog.text

    expected_out = f"""Certifying '{hst_data}/s7g1700gl_dead.fits' (1/1) as 'FITS' relative to context 'hst.pmap'
FITS file 's7g1700gl_dead.fits' conforms to FITS standards.
[0] COMMENT = 'Created by S. Beland and IDT and P. Hodge converted to user coord.'
[0] DESCRIP initial version
[0] DETECTOR FUV
[0] FILETYPE DEADTIME REFERENCE TABLE
[0] HISTORY   Modified to account for chamge of coordinates
[0] HISTORY fuv_080509_r_dead.fits renamed to s7g1700gl_dead.fits on Jul 16 2008
[0] INSTRUME COS
[0] PEDIGREE GROUND 16/07/2008 16/07/2010
[0] USEAFTER Oct 01 1996 00:00:00
[0] VCALCOS 2.0
DATE-OBS = '1996-10-01'
TIME-OBS = '00:00:00'
########################################
0 errors
0 warnings"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.jwst
@mark.certify
def test_certify_dump_provenance_generic(jwst_serverless_state, jwst_data, caplog):
    argv = f"crds.certify {jwst_data}/valid.json --dump-provenance --comparison-context jwst_0034.pmap"
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(argv)()
        out = caplog.text

    expected_out = f"""Certifying '{jwst_data}/valid.json' (1/1) as 'JSON' relative to context 'jwst_0034.pmap'
EXP_TYPE = 'mir_image'
META.AUTHOR [AUTHOR] = 'Todd Miller'
META.DESCRIPTION [DESCRIP] = 'Brief notes on this reference.'
META.EXPOSURE.READPATT [READPATT] = 'any'
META.EXPOSURE.TYPE [EXP_TYPE] = 'mir_image'
META.HISTORY [HISTORY] = 'How this reference came to be and changed over time.'
META.INSTRUMENT.BAND [BAND] = 'medium'
META.INSTRUMENT.CHANNEL [CHANNEL] = 34
META.INSTRUMENT.CORONAGRAPH [CORONMSK] = 'UNDEFINED'
META.INSTRUMENT.DETECTOR [DETECTOR] = 'mirifulong'
META.INSTRUMENT.FILTER [FILTER] = 'UNDEFINED'
META.INSTRUMENT.GRATING [GRATING] = 'UNDEFINED'
META.INSTRUMENT.NAME [INSTRUME] = 'miri'
META.INSTRUMENT.PUPIL [PUPIL] = 'UNDEFINED'
META.MODEL_TYPE [DATAMODL] = 'DistortionModel'
META.PEDIGREE [PEDIGREE] = 'dummy'
META.REFTYPE [REFTYPE] = 'distortion'
META.SUBARRAY.FASTAXIS [FASTAXIS] = 1
META.SUBARRAY.NAME [SUBARRAY] = 'MASK1550'
META.SUBARRAY.SLOWAXIS [SLOWAXIS] = 2
META.SUBARRAY.XSIZE [SUBSIZE1] = 1032
META.SUBARRAY.XSTART [SUBSTRT1] = 1
META.SUBARRAY.YSIZE [SUBSIZE2] = 4
META.SUBARRAY.YSTART [SUBSTRT2] = 1020
META.TELESCOPE [TELESCOP] = 'jwst'
META.USEAFTER [USEAFTER] = '2015-01-25T12:00:00'
########################################
0 errors
0 warnings"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.hst
@mark.certify
def test_certify_missing_keyword(default_shared_state, hst_data, caplog):
    argv = f"crds.certify {hst_data}/missing_keyword.fits --comparison-context hst.pmap"
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(argv)()
        out = caplog.text

    expected_out = f"""Certifying '{hst_data}/missing_keyword.fits' (1/1) as 'FITS' relative to context 'hst.pmap'
FITS file 'missing_keyword.fits' conforms to FITS standards.
instrument='COS' type='DEADTAB' data='{hst_data}/missing_keyword.fits' ::  Checking 'DETECTOR' : Missing required keyword 'DETECTOR'
########################################
1 errors
0 warnings"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.hst
@mark.certify
def test_certify_recursive(default_shared_state, caplog):
    cache = default_shared_state.cache
    argv = f"crds.certify crds://hst_cos.imap --exist --dont-parse --comparison-context hst.pmap"
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(argv)()
        out = caplog.text

    expected_out = f"""Certifying '{cache}/mappings/hst/hst_cos.imap' (1/19) as 'MAPPING' relative to context 'hst.pmap'
########################################
Certifying '{cache}/mappings/hst/hst_cos_badttab.rmap' (2/19) as 'MAPPING' relative to context 'hst.pmap'
########################################
Certifying '{cache}/mappings/hst/hst_cos_bpixtab.rmap' (3/19) as 'MAPPING' relative to context 'hst.pmap'
########################################
Certifying '{cache}/mappings/hst/hst_cos_brftab.rmap' (4/19) as 'MAPPING' relative to context 'hst.pmap'
########################################
Certifying '{cache}/mappings/hst/hst_cos_brsttab.rmap' (5/19) as 'MAPPING' relative to context 'hst.pmap'
########################################
Certifying '{cache}/mappings/hst/hst_cos_deadtab.rmap' (6/19) as 'MAPPING' relative to context 'hst.pmap'
########################################
Certifying '{cache}/mappings/hst/hst_cos_disptab.rmap' (7/19) as 'MAPPING' relative to context 'hst.pmap'
########################################
Certifying '{cache}/mappings/hst/hst_cos_flatfile.rmap' (8/19) as 'MAPPING' relative to context 'hst.pmap'
########################################
Certifying '{cache}/mappings/hst/hst_cos_fluxtab.rmap' (9/19) as 'MAPPING' relative to context 'hst.pmap'
########################################
Certifying '{cache}/mappings/hst/hst_cos_geofile.rmap' (10/19) as 'MAPPING' relative to context 'hst.pmap'
########################################
Certifying '{cache}/mappings/hst/hst_cos_gsagtab.rmap' (11/19) as 'MAPPING' relative to context 'hst.pmap'
########################################
Certifying '{cache}/mappings/hst/hst_cos_hvtab.rmap' (12/19) as 'MAPPING' relative to context 'hst.pmap'
########################################
Certifying '{cache}/mappings/hst/hst_cos_lamptab.rmap' (13/19) as 'MAPPING' relative to context 'hst.pmap'
########################################
Certifying '{cache}/mappings/hst/hst_cos_phatab.rmap' (14/19) as 'MAPPING' relative to context 'hst.pmap'
########################################
Certifying '{cache}/mappings/hst/hst_cos_spwcstab.rmap' (15/19) as 'MAPPING' relative to context 'hst.pmap'
########################################
Certifying '{cache}/mappings/hst/hst_cos_tdstab.rmap' (16/19) as 'MAPPING' relative to context 'hst.pmap'
########################################
Certifying '{cache}/mappings/hst/hst_cos_walktab.rmap' (17/19) as 'MAPPING' relative to context 'hst.pmap'
########################################
Certifying '{cache}/mappings/hst/hst_cos_wcptab.rmap' (18/19) as 'MAPPING' relative to context 'hst.pmap'
########################################
Certifying '{cache}/mappings/hst/hst_cos_xtractab.rmap' (19/19) as 'MAPPING' relative to context 'hst.pmap'
########################################
0 errors"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.hst
@mark.certify
def test_certify_table_comparison_context(default_shared_state, caplog):
    cache = default_shared_state.cache
    argv = f"crds.certify crds://y951738kl_hv.fits --comparison-context hst_0294.pmap"
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(argv)()
        out = caplog.text

    # Due to the nature of the test file, a numpy.float128 is used. However, this is not
    # supported on many architectures. Mark xfail if this there is no support.
    if """ module 'numpy' has no attribute""" in out:
        xfail('Test requires numpy.float128, which current system does not support.')

    expected_out = f"""Certifying
    y951738kl_hv.fits' (1/1) as 'FITS' relative to context 'hst_0294.pmap'
    FITS file 'y951738kl_hv.fits' conforms to FITS standards.
    Comparing reference 'y951738kl_hv.fits' against 'yas2005el_hv.fits'
    Mode columns defined by spec for old reference 'yas2005el_hv.fits[1]' are: ['DATE']
    All column names for this table old reference 'yas2005el_hv.fits[1]' are: ['DATE', 'HVLEVELA']
    Checking for duplicate modes using intersection ['DATE']
    Mode columns defined by spec for new reference 'y951738kl_hv.fits[1]' are: ['DATE']
    All column names for this table new reference 'y951738kl_hv.fits[1]' are: ['DATE', 'HVLEVELA']
    Checking for duplicate modes using intersection ['DATE']
    Table mode (('DATE', 56923.5834),) from old reference 'yas2005el_hv.fits[1]' is NOT IN new reference 'y951738kl_hv.fits[1]'
    Table mode (('DATE', 56923.625),) from old reference 'yas2005el_hv.fits[1]' is NOT IN new reference 'y951738kl_hv.fits[1]'
    Table mode (('DATE', 56964.0),) from old reference 'yas2005el_hv.fits[1]' is NOT IN new reference 'y951738kl_hv.fits[1]'
    Mode columns defined by spec for old reference 'yas2005el_hv.fits[2]' are: ['DATE']
    All column names for this table old reference 'yas2005el_hv.fits[2]' are: ['DATE', 'HVLEVELB']
    Checking for duplicate modes using intersection ['DATE']
    Mode columns defined by spec for new reference 'y951738kl_hv.fits[2]' are: ['DATE']
    All column names for this table new reference 'y951738kl_hv.fits[2]' are: ['DATE', 'HVLEVELB']
    Checking for duplicate modes using intersection ['DATE']
    Table mode (('DATE', 56921.8334),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    Table mode (('DATE', 56922.0),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    Table mode (('DATE', 56923.5834),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    Table mode (('DATE', 56923.625),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    Table mode (('DATE', 56924.0417),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    Table mode (('DATE', 56924.2084),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    Table mode (('DATE', 56924.3125),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    Table mode (('DATE', 56925.0),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    Table mode (('DATE', 56959.4584),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    Table mode (('DATE', 56959.6667),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    Table mode (('DATE', 56961.8334),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    Table mode (('DATE', 56962.8334),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    0 errors
    15 warnings"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.hst
@mark.certify
def test_certify_table_comparison_reference(default_shared_state, hst_data, caplog):
    argv = f"crds.certify {hst_data}/y951738kl_hv.fits --comparison-reference {hst_data}/y9j16159l_hv.fits --comparison-context hst_0857.pmap"
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(argv)()
        out = caplog.text

    # Due to the nature of the test file, a numpy.float128 is used. However, this is not
    # supported on many architectures. Mark xfail if this there is no support.
    if """ module 'numpy' has no attribute""" in out:
        xfail('Test requires numpy.float128, which current system does not support.')

    expected_out = f"""Certifying
    y951738kl_hv.fits' (1/1) as 'FITS' relative to context 'hst_0857.pmap' and comparison reference
    y9j16159l_hv.fits'
    FITS file 'y951738kl_hv.fits' conforms to FITS standards.
    Mode columns defined by spec for old reference 'y9j16159l_hv.fits[1]' are: ['DATE']
    All column names for this table old reference 'y9j16159l_hv.fits[1]' are: ['DATE', 'HVLEVELA']
    Checking for duplicate modes using intersection ['DATE']
    Mode columns defined by spec for new reference 'y951738kl_hv.fits[1]' are: ['DATE']
    All column names for this table new reference 'y951738kl_hv.fits[1]' are: ['DATE', 'HVLEVELA']
    Checking for duplicate modes using intersection ['DATE']
    Table mode (('DATE', 56923.5834),) from old reference 'y9j16159l_hv.fits[1]' is NOT IN new reference 'y951738kl_hv.fits[1]'
    Table mode (('DATE', 56923.625),) from old reference 'y9j16159l_hv.fits[1]' is NOT IN new reference 'y951738kl_hv.fits[1]'
    Mode columns defined by spec for old reference 'y9j16159l_hv.fits[2]' are: ['DATE']
    All column names for this table old reference 'y9j16159l_hv.fits[2]' are: ['DATE', 'HVLEVELB']
    Checking for duplicate modes using intersection ['DATE']
    Duplicate definitions in old reference 'y9j16159l_hv.fits[2]' for mode: (('DATE', 56924.0417),) :
    (129, (('DATE', 56924.0417), ('HVLEVELB', 169)))
    (131, (('DATE', 56924.0417), ('HVLEVELB', 169)))
    Duplicate definitions in old reference 'y9j16159l_hv.fits[2]' for mode: (('DATE', 56925.0),) :
    (132, (('DATE', 56925.0), ('HVLEVELB', 175)))
    (134, (('DATE', 56925.0), ('HVLEVELB', 175)))
    Mode columns defined by spec for new reference 'y951738kl_hv.fits[2]' are: ['DATE']
    All column names for this table new reference 'y951738kl_hv.fits[2]' are: ['DATE', 'HVLEVELB']
    Checking for duplicate modes using intersection ['DATE']
    Table mode (('DATE', 56921.8334),) from old reference 'y9j16159l_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    Table mode (('DATE', 56922.0),) from old reference 'y9j16159l_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    Table mode (('DATE', 56923.625),) from old reference 'y9j16159l_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    Table mode (('DATE', 56924.0417),) from old reference 'y9j16159l_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    Table mode (('DATE', 56924.3125),) from old reference 'y9j16159l_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    Table mode (('DATE', 56925.0),) from old reference 'y9j16159l_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    0 errors
    10 warnings"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.hst
@mark.certify
def test_certify_duplicate_sha1sum(default_shared_state, hst_data, caplog):
    argv = f"crds.certify {hst_data}/s7g1700gl_dead.fits --check-sha1sums --comparison-context hst_1099.pmap"
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(argv)()
        out = caplog.text

    expected_out = f"""Certifying '{hst_data}/s7g1700gl_dead.fits' (1/1) as 'FITS' relative to context 'hst_1099.pmap'
instrument='COS' type='DEADTAB' data='{hst_data}/s7g1700gl_dead.fits' ::  Duplicate file check : File 's7g1700gl_dead.fits' is identical to existing CRDS file 's7g1700gl_dead.fits'
FITS file 's7g1700gl_dead.fits' conforms to FITS standards.
########################################
1 errors
0 warnings"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.jwst
@mark.certify
def test_certify_jwst_valid(jwst_shared_cache_state, jwst_data, caplog):
    argv = f"crds.certify {jwst_data}/niriss_ref_photom.fits --comparison-context jwst_0125.pmap"
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(argv)()
        out = caplog.text

    # Due to the nature of the test file, a numpy.float128 is used. However, this is not
    # supported on many architectures. Mark xfail if this there is no support.
    if """ module 'numpy' has no attribute""" in out:
        xfail('Test requires numpy.float128, which current system does not support.')

    expected_out = """Certifying
    niriss_ref_photom.fits' (1/1) as 'FITS' relative to context 'jwst_0125.pmap'
    FITS file 'niriss_ref_photom.fits' conforms to FITS standards.
    Missing suggested keyword 'META.MODEL_TYPE [DATAMODL]'
    Non-compliant date format 'Jan 01 2015 00:00:00' for 'META.USEAFTER [USEAFTER]' should be 'YYYY-MM-DDTHH:MM:SS'
    Failed resolving comparison reference for table checks : Failed inserting 'niriss_ref_photom.fits' into rmap: 'jwst_niriss_photom_0006.rmap' with header:
    Mode columns defined by spec for new reference 'niriss_ref_photom.fits[1]' are: ['FILTER', 'PUPIL', 'ORDER']
    All column names for this table new reference 'niriss_ref_photom.fits[1]' are: ['FILTER', 'PUPIL', 'PHOTFLAM', 'NELEM', 'WAVELENGTH', 'RELRESPONSE']
    Checking for duplicate modes using intersection ['FILTER', 'PUPIL']
    No comparison reference for 'niriss_ref_photom.fits' in context 'jwst_0125.pmap'. Skipping tables comparison.
    Checking JWST datamodels.
    NoTypeWarning : stdatamodels.jwst.datamodels.util : model_type not found. Opening
    niriss_ref_photom.fits as a ReferenceFileModel
    0 errors
    5 warnings"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.jwst
@mark.certify
def test_certify_jwst_missing_optional_parkey(jwst_serverless_state, jwst_data, caplog):
    argv = f"crds.certify {jwst_data}/jwst_miri_ipc_0003.add.fits --comparison-context jwst_0125.pmap"
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(argv)()
        out = caplog.text

    expected_out = f"""Certifying '{jwst_data}/jwst_miri_ipc_0003.add.fits' (1/1) as 'FITS' relative to context 'jwst_0125.pmap'
FITS file 'jwst_miri_ipc_0003.add.fits' conforms to FITS standards.
Setting 'META.INSTRUMENT.BAND [BAND]' = None to value of 'P_BAND' = 'SHORT | MEDIUM |'
Setting 'META.INSTRUMENT.DETECTOR [DETECTOR]' = 'MIRIMAGE' to value of 'P_DETECT' = 'MIRIFUSHORT|MIRIFULONG|'
Checking JWST datamodels.
########################################
0 errors"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.jwst
@mark.certify
def test_certify_jwst_invalid_asdf(jwst_serverless_state, jwst_data, caplog):
    argv = f"crds.certify {jwst_data}/invalid.asdf  --comparison-context jwst.pmap"
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(argv)()
        out = caplog.text

    if asdf.__version__ < "3.0.0":
        expected_out = f"""Certifying '{jwst_data}/invalid.asdf' (1/1) as 'ASDF' relative to context 'jwst.pmap'
instrument='UNKNOWN' type='UNKNOWN' data='{jwst_data}/invalid.asdf' ::  Validation error : Input object does not appear to be an ASDF file or a FITS with ASDF extension
########################################
1 errors
0 warnings"""
    else:
        expected_out = f"""Certifying '{jwst_data}/invalid.asdf' (1/1) as 'ASDF' relative to context 'jwst.pmap'
instrument='UNKNOWN' type='UNKNOWN' data='{jwst_data}/invalid.asdf' ::  Validation error : Does not appear to be a ASDF file.
########################################
1 errors
0 warnings"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.jwst
@mark.certify
def test_certify_jwst_invalid_json(jwst_serverless_state, jwst_data, caplog):
    argv = f"crds.certify {jwst_data}/invalid.json  --comparison-context jwst.pmap"
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(argv)()
        out = caplog.text

    expected_out = f"""Certifying '{jwst_data}/invalid.json' (1/1) as 'JSON' relative to context 'jwst.pmap'
instrument='UNKNOWN' type='UNKNOWN' data='{jwst_data}/invalid.json' ::  Validation error : JSON wouldn't load from '{jwst_data}/invalid.json' : Expecting ',' delimiter: line 5 column 1 (char 77)
########################################
1 errors
0 warnings"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.jwst
@mark.certify
def test_certify_jwst_invalid_yaml(jwst_serverless_state, jwst_data, caplog):
    argv = f"crds.certify {jwst_data}/invalid.yaml  --comparison-context jwst_0034.pmap"
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(argv)()
        out = caplog.text

    expected_out = f"""Certifying '{jwst_data}/invalid.yaml' (1/1) as 'YAML' relative to context 'jwst_0034.pmap'
instrument='UNKNOWN' type='UNKNOWN' data='{jwst_data}/invalid.yaml' ::  Validation error : while scanning a tag
  in "{jwst_data}/invalid.yaml", line 1, column 5
expected ' ', but found '^'
  in "{jwst_data}/invalid.yaml", line 1, column 21
########################################
1 errors
0 warnings"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.roman
@mark.certify
def test_certify_roman_load_all_type_constraints(roman_test_cache_state):
    generic_tpn.load_all_type_constraints("roman")


@mark.jwst
@mark.certify
def test_certify_jwst_load_all_type_constraints(jwst_serverless_state):
    generic_tpn.load_all_type_constraints("jwst")


@mark.hst
@mark.certify
def test_certify_hst_load_all_type_constraints(hst_serverless_state):
    generic_tpn.load_all_type_constraints("hst")


@mark.hst
@mark.certify
def test_certify_validator_bad_presence_condition(hst_serverless_state):
    try:
        info = generic_tpn.TpnInfo('DETECTOR','H','C', "(Q='BAR')", ('WFC','HRC','SBC'))
    except SyntaxError:
        assert True

@mark.jwst
@mark.certify
def test_certify_JsonCertify_valid(jwst_serverless_state, jwst_data, caplog):
    with caplog.at_level(logging.INFO, logger="CRDS"):
        certify.certify_file(f"{jwst_data}/valid.json", "jwst_0034.pmap", observatory="jwst")
        out = caplog.text

    expected_out = f"Certifying '{jwst_data}/valid.json' as 'JSON' relative to context 'jwst_0034.pmap'"
    assert expected_out in out


@mark.jwst
@mark.certify
def test_certify_YamlCertify_valid(jwst_serverless_state, jwst_data, caplog):
    with caplog.at_level(logging.INFO, logger="CRDS"):
        certify.certify_file(f"{jwst_data}/valid.yaml", "jwst_0034.pmap", observatory="jwst")
        out = caplog.text

    expected_out = f"Certifying '{jwst_data}/valid.yaml' as 'YAML' relative to context 'jwst_0034.pmap'"
    assert expected_out in out


@mark.jwst
@mark.certify
def test_certify_AsdfCertify_valid(jwst_serverless_state, jwst_data, caplog):
    with caplog.at_level(logging.INFO, logger="CRDS"):
        certify.certify_file(f"{jwst_data}/valid.asdf", "jwst_0365.pmap", observatory="jwst")
        out = caplog.text

    expected_out = f"""Certifying '{jwst_data}/valid.asdf' as 'ASDF' relative to context 'jwst_0365.pmap'
Setting 'META.INSTRUMENT.DETECTOR [DETECTOR]' = None to value of 'META.INSTRUMENT.P_DETECTOR [P_DETECT]' = 'NRS1|NRS2|'
Checking JWST datamodels."""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.roman
@mark.certify
@metrics_logger("DMS4")
def test_certify_roman_valid_asdf(roman_test_cache_state, roman_data, caplog):
    """Required Roman test: confirm that a valid asdf file is recognized as such.
    """
    with caplog.at_level(logging.INFO, logger="CRDS"):
        certify.certify_file(f"{roman_data}/roman_wfi16_f158_flat_small.asdf", "roman_0003.pmap", observatory="roman")
        out = caplog.text
    expected_out = f"Certifying '{roman_data}/roman_wfi16_f158_flat_small.asdf' as 'ASDF' relative to context 'roman_0003.pmap'"
    assert expected_out in out


@mark.roman
@mark.certify
@metrics_logger("DMS4")
def test_certify_roman_invalid_asdf_schema(roman_test_cache_state, roman_data, caplog):
    """Required Roman test: confirm that an asdf file that does not conform to its schema definition
    triggers an error in DataModels.
    """
    fpath = f"{roman_data}/roman_wfi16_f158_flat_invalid_schema.asdf"
    with caplog.at_level(logging.INFO, logger="CRDS"):
        certify.certify_file(fpath, "roman_0003.pmap", observatory="roman")
        out = caplog.text
        assert "Validation error" in out
        assert "This ain't no valid time" in out


@mark.roman
@mark.certify
@metrics_logger("DMS4")
def test_certify_roman_invalid_asdf_tpn(roman_test_cache_state, roman_data, caplog):
    """Required Roman test: confirm that an asdf file that does not conform to its tpn definition
    triggers an error in crds. Note: as the tpn often replicates schema implementation, this also
    triggers an error in Datamodels.
    """
    with caplog.at_level(logging.INFO, logger="CRDS"):
        certify.certify_file(f"{roman_data}/roman_wfi16_f158_flat_invalid_tpn.asdf", "roman_0003.pmap", observatory="roman")
        out = caplog.text
    expected_out = f"""Certifying '{roman_data}/roman_wfi16_f158_flat_invalid_tpn.asdf' as 'ASDF' relative to context 'roman_0003.pmap'
In 'roman_wfi16_f158_flat_invalid_tpn.asdf' : Checking 'ROMAN.META.INSTRUMENT.OPTICAL_ELEMENT [FITS unknown]' : Value 'BAD' is not one of ['ANY',
'CLEAR',
'DARK',
'F062',
'F087',
'F106',
'F129',
'F146',
'F158',
'F184',
'F213',
'GRISM',
'N/A',
'PRISM',
'UNKNOWN']"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.roman
@mark.certify
@metrics_logger("DMS5")
def test_certify_roman_valid_spec_asdf(roman_test_cache_state, roman_data, caplog):
    """Required Roman test: confirm that a valid spectroscopic asdf file is recognized as such."""
    with caplog.at_level(logging.INFO, logger="CRDS"):
        certify.certify_file(f"{roman_data}/roman_wfi16_grism_flat_small.asdf", "roman_0003.pmap", observatory="roman")
        out = caplog.text
    expected_out = f"Certifying '{roman_data}/roman_wfi16_grism_flat_small.asdf' as 'ASDF' relative to context 'roman_0003.pmap'"
    assert expected_out in out


@mark.roman
@mark.certify
@metrics_logger("DMS5")
def test_certify_roman_invalid_spec_asdf_schema(roman_test_cache_state, roman_data, caplog):
    """Required Roman test: confirm that a spectroscopic asdf file that does not conform to its schema
    definition triggers an error in DataModels."""
    fpath = f"{roman_data}/roman_wfi16_grism_flat_invalid_schema.asdf"
    with caplog.at_level(logging.INFO, logger="CRDS"):
        certify.certify_file(fpath, "roman_0003.pmap", observatory="roman")
        out = caplog.text
        assert "Validation error" in out
        assert "yesterday" in out


@mark.roman
@mark.certify
@metrics_logger("DMS5")
def test_certify_roman_invalid_spec_asdf_tpn(roman_test_cache_state, roman_data, caplog):
    """Required Roman test: confirm that a spectroscopic asdf file that does not conform to its tpn
    definition triggers an error in crds. Note: as the tpn often replicates schema implementation,
    this also triggers an error in Datamodels.
    """
    with caplog.at_level(logging.INFO, logger="CRDS"):
        certify.certify_file(f"{roman_data}/roman_wfi16_grism_flat_invalid_tpn.asdf", "roman_0003.pmap", observatory="roman")
        out = caplog.text
        expected_out = f"""Certifying '{roman_data}/roman_wfi16_grism_flat_invalid_tpn.asdf' as 'ASDF' relative to context 'roman_0003.pmap'
In 'roman_wfi16_grism_flat_invalid_tpn.asdf' : Error mapping reference names and values to dataset names and values : Bad USEAFTER time format = 'yesterday'
In 'roman_wfi16_grism_flat_invalid_tpn.asdf' : Checking 'ROMAN.META.USEAFTER [USEAFTER]' : Invalid 'Jwstdate' format 'yesterday' should be '2018-12-22T00:00:00'
In 'roman_wfi16_grism_flat_invalid_tpn.asdf' : Checking ASDF tag validity for '{roman_data}/roman_wfi16_grism_flat_invalid_tpn.asdf' : 'dict' object has no attribute '_tag'"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.jwst
@mark.certify
def test_certify_AsdfCertify_valid_with_astropy_time(jwst_serverless_state, jwst_data, caplog):
    with caplog.at_level(logging.INFO, logger="CRDS"):
        certify.certify_file(f"{jwst_data}/valid_with_astropy_time.asdf", "jwst_0365.pmap", observatory="jwst")
        out = caplog.text

    expected_out = f"""Certifying '{jwst_data}/valid_with_astropy_time.asdf' as 'ASDF' relative to context 'jwst_0365.pmap'
Setting 'META.INSTRUMENT.DETECTOR [DETECTOR]' = None to value of 'META.INSTRUMENT.P_DETECTOR [P_DETECT]' = 'NRS1|NRS2|'
Checking JWST datamodels."""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.hst
@mark.certify
def test_certify_FitsCertify_opaque_name(hst_serverless_state, hst_data, caplog):
    with caplog.at_level(logging.INFO, logger="CRDS"):
        certify.certify_file(f"{hst_data}/opaque_fts.tmp", "hst.pmap", observatory="hst")
        out = caplog.text

    expected_out = f"Certifying '{hst_data}/opaque_fts.tmp' as 'FITS' relative to context 'hst.pmap'"
    assert expected_out in out


@mark.jwst
@mark.certify
def test_certify_AsdfCertify_opaque_name(jwst_serverless_state, jwst_data, caplog):
    """CRDS is able to recognize ASDF files without the .asdf extension, but the cal code is not.
    Leaving this test here in case jwst decides to change its mind someday."""
    with caplog.at_level(logging.INFO, logger="CRDS"):
        certify.certify_file(f"{jwst_data}/opaque_asd.tmp", "jwst_0365.pmap", observatory="jwst")
        out = caplog.text

    expected_out = f"""Certifying '{jwst_data}/opaque_asd.tmp' as 'ASDF' relative to context 'jwst_0365.pmap'
Setting 'META.INSTRUMENT.DETECTOR [DETECTOR]' = None to value of 'META.INSTRUMENT.P_DETECTOR [P_DETECT]' = 'NRS1|NRS2|'
Checking JWST datamodels.
{jwst_data}/opaque_asd.tmp Validation error : JWST Data Models: Unrecognized file type for: {jwst_data}/opaque_asd.tmp"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.jwst
@mark.certify
def test_certify_rmap_compare(jwst_serverless_state, caplog):
    with caplog.at_level(logging.INFO, logger="CRDS"):
        certify.certify_file("jwst_miri_distortion_0025.rmap", "jwst_0357.pmap")
        out = caplog.text

    expected_out = "Certifying 'jwst_miri_distortion_0025.rmap' as 'MAPPING' relative to context 'jwst_0357.pmap'"
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.roman
@mark.certify
@metrics_logger("DMS6")
def test_certify_roman_rmap_compare(roman_test_cache_state, caplog):
    """Required Roman test: confirm that a calibration mapping file properly compares to its context."""
    with caplog.at_level(logging.INFO, logger="CRDS"):
        certify.certify_file("roman_wfi_flat_0004.rmap", "roman_0004.pmap")
        out = caplog.text
        expected_out = """Certifying 'roman_wfi_flat_0004.rmap' as 'MAPPING' relative to context 'roman_0004.pmap'"""
        assert expected_out in out


@mark.jwst
@mark.certify
def test_certify_jwst_bad_fits(jwst_serverless_state, jwst_data, caplog):
    with caplog.at_level(logging.INFO, logger="CRDS"):
        certify.certify_file(f"{jwst_data}/niriss_ref_photom_bad.fits", "jwst_0541.pmap", observatory="jwst")
        out = caplog.text

    # Due to the nature of the test file, a numpy.float128 is used. However, this is not
    # supported on many architectures. Mark xfail if this there is no support.
    if """ module 'numpy' has no attribute""" in out:
        xfail('Test requires numpy.float128, which current system does not support.')

    expected_out = """Certifying
    niriss_ref_photom_bad.fits' as 'FITS' relative to context 'jwst_0541.pmap'
    FITS file 'niriss_ref_photom_bad.fits' conforms to FITS standards.
    In 'niriss_ref_photom_bad.fits' : Checking 'META.INSTRUMENT.DETECTOR [DETECTOR]' : Value 'FOO' is not one of ['ANY', 'N/A', 'NIS']
    Non-compliant date format 'Jan 01 2015 00:00:00' for 'META.USEAFTER [USEAFTER]' should be 'YYYY-MM-DDTHH:MM:SS'
    Failed resolving comparison reference for table checks : Failed inserting 'niriss_ref_photom_bad.fits' into rmap: 'jwst_niriss_photom_0021.rmap' with header:
    Mode columns defined by spec for new reference 'niriss_ref_photom_bad.fits[1]' are: ['FILTER', 'PUPIL', 'ORDER']
    All column names for this table new reference 'niriss_ref_photom_bad.fits[1]' are: ['FILTER', 'PUPIL', 'PHOTFLAM', 'NELEM', 'WAVELENGTH', 'RELRESPONSE']
    Checking for duplicate modes using intersection ['FILTER', 'PUPIL']
    No comparison reference for 'niriss_ref_photom_bad.fits' in context 'jwst_0541.pmap'. Skipping tables comparison.
    Checking JWST datamodels.
    ValidationWarning : stdatamodels.validate : While validating meta.instrument.detector the following error occurred:'FOO' is not one of ['NRCA1', 'NRCA2', 'NRCA3', 'NRCA4', 'NRCALONG', 'NRCB1', 'NRCB2', 'NRCB3', 'NRCB4', 'NRCBLONG', 'NRS1', 'NRS2', 'ANY', 'MIRIMAGE', 'MIRIFULONG', 'MIRIFUSHORT', 'NIS', 'GUIDER1', 'GUIDER2', 'MULTIPLE', 'N/A']Failed validating 'enum' in schema:    OrderedDict([('title', 'Name of detector used to acquire the data'),                 ('type', 'string'),                 ('enum',                  ['NRCA1',                   'NRCA2',                   'NRCA3',                   'NRCA4',                   'NRCALONG',                   'NRCB1',                   'NRCB2',                   'NRCB3',                   'NRCB4',                   'NRCBLONG',                   'NRS1',                   'NRS2',                   'ANY',                   'MIRIMAGE',                   'MIRIFULONG',                   'MIRIFUSHORT',                   'NIS',                   'GUIDER1',                   'GUIDER2',                   'MULTIPLE',                   'N/A']),                 ('description', 'Detector name.'),                 ('fits_keyword', 'DETECTOR')])On instance:    'FOO'
"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.hst
@mark.certify
def test_certify_duplicate_rmap_case_error(hst_serverless_state, hst_data, caplog):
    with caplog.at_level(logging.INFO, logger="CRDS"):
        certify.certify_file(f"{hst_data}/hst_cos_tdstab_duplicate.rmap", "hst.pmap", observatory="hst")
        out = caplog.text

    expected_out = f"""Certifying '{hst_data}/hst_cos_tdstab_duplicate.rmap' as 'MAPPING' relative to context 'hst.pmap'
Duplicate entry at selector ('FUV', 'SPECTROSCOPIC') = UseAfter vs. UseAfter
Checksum error : sha1sum mismatch in 'hst_cos_tdstab_duplicate.rmap'"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.roman
@mark.certify
@metrics_logger("DMS6")
def test_certify_roman_duplicate_rmap_case_error(roman_test_cache_state, roman_data, caplog):
    """Required Roman test: verify that a calibration mapping file containing duplicate match cases 
    fails."""
    with caplog.at_level(logging.INFO, logger="CRDS"):
        certify.certify_file(f"{roman_data}/roman_wfi_flat_0004_duplicate.rmap", "roman_0003.pmap")
        out = caplog.text
        expected_out = f"""Certifying '{roman_data}/roman_wfi_flat_0004_duplicate.rmap' as 'MAPPING' relative to context 'roman_0003.pmap'
Duplicate entry at selector ('WFI01', 'F158') = UseAfter vs. UseAfter
Checksum error : sha1sum mismatch in 'roman_wfi_flat_0004_duplicate.rmap'
{roman_data}/roman_wfi_flat_0004_duplicate.rmap Validation error : Failed to determine 'roman' instrument or reftype for '{roman_data}/roman_wfi_flat_0004_duplicate.rmap' : 'sha1sum mismatch in 'roman_wfi_flat_0004_duplicate.rmap'"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.hst
@mark.certify
def test_checksum_duplicate_rmap_case_error(hst_serverless_state, hst_data, caplog):
    """Verify that the crds rmap checksum update tool does not silently drop duplicate rmap entries
    when updating the checksum and rewriting the file."""
    with caplog.at_level(logging.INFO, logger="CRDS"):
        from crds.refactoring import checksum
        checksum.add_checksum(f"{hst_data}/hst_cos_tdstab_duplicate.rmap")
        out = caplog.text

    expected_out = f"""Adding checksum for '{hst_data}/hst_cos_tdstab_duplicate.rmap'
Duplicate entry at selector ('FUV', 'SPECTROSCOPIC') = UseAfter vs. UseAfter"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.roman
@mark.certify
@metrics_logger("DMS6")
def test_checksum_roman_duplicate_rmap_case_error(roman_serverless_state, roman_data, caplog):
    """Required Roman test: verify that the crds rmap checksum update tool does not silently drop
    duplicate rmap entries when updating the checksum and rewriting the file."""
    with caplog.at_level(logging.INFO, logger="CRDS"):
        from crds.refactoring import checksum
        checksum.add_checksum(f"{roman_data}/roman_wfi_flat_0004_duplicate.rmap")
        out = caplog.text
        expected_out = f"""Adding checksum for '{roman_data}/roman_wfi_flat_0004_duplicate.rmap'
Duplicate entry at selector ('WFI01', 'F158') = UseAfter vs. UseAfter"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.roman
@mark.certify
@metrics_logger("DMS6")
def test_certify_roman_invalid_rmap_tpn(roman_test_cache_state, roman_data, caplog):
    """Required Roman test: verify that a calibration mapping file that violates tpn rules produces an
    error."""
    with caplog.at_level(logging.INFO, logger="CRDS"):
        certify.certify_file(f"{roman_data}/roman_wfi_flat_0004_badtpn.rmap", "roman_0003.pmap", observatory="roman")
        out = caplog.text
        expected_out = f"""Certifying '{roman_data}/roman_wfi_flat_0004_badtpn.rmap' as 'MAPPING' relative to context 'roman_0003.pmap'
Match('ROMAN.META.INSTRUMENT.DETECTOR', 'ROMAN.META.INSTRUMENT.OPTICAL_ELEMENT [FITS unknown]') : ('WFI21', 'F158') :  parameter='ROMAN.META.INSTRUMENT.DETECTOR [DETECTOR]' value='WFI21' is not in ('WFI01', 'WFI02', 'WFI03', 'WFI04', 'WFI05', 'WFI06', 'WFI07', 'WFI08', 'WFI09', 'WFI10', 'WFI11', 'WFI12', 'WFI13', 'WFI14', 'WFI15', 'WFI16', 'WFI17', 'WFI18', '*', 'N/A')
Mapping 'roman_wfi_flat_0004_badtpn.rmap' corresponds to 'roman_wfi_flat_0001.rmap' from context 'roman_0003.pmap' for checking mapping differences.
Checking diffs from 'roman_wfi_flat_0001.rmap' to 'roman_wfi_flat_0004_badtpn.rmap'
Rule change at ('{roman_data}/roman_wfi_flat_0004_badtpn.rmap', ('WFI21', 'F158'), ('2020-01-01 00:00:00',)) added Match rule for 'roman_wfi_flat_0003.asdf'"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.multimission
@mark.certify
def test_undefined_expr_identifiers():
    """Some TpnInfos include Python expressions either to make them apply conditionally or to
    implement and expression constraint.   validators.core.expr_identifiers() scans a Tpn header
    expression for the header keywords upon which it depends.   This enables CRDS To short
    circuit checks for which critical keywords are not defined at all.
    """
    val_1 = validators.core.expr_identifiers("((EXP_TYPE)in(['NRS_MSASPEC','NRS_FIXEDSLIT','NRS_BRIGHTOBJ','NRS_IFU']))")
    assert val_1 == ['EXP_TYPE']
    val_2 = validators.core.expr_identifiers("nir_filter(INSTRUME,REFTYPE,EXP_TYPE)")
    assert val_2 == ['INSTRUME', 'REFTYPE', 'EXP_TYPE']
    val_3 = validators.core.expr_identifiers("(len(SCI_ARRAY.SHAPE)==2)")
    assert val_3 == ['SCI_ARRAY']
    val_4 = validators.core.expr_identifiers("(True)")
    assert val_4 == []


@mark.jwst
@mark.certify
def test_load_nirspec_staturation_tpn_lines(jwst_serverless_state):
    """Print out the outcome of various .tpn directives like "replace" and
    "include" and reuse of generic files."""
    path = generic_tpn.get_tpn_path("nirspec_saturation.tpn","jwst")
    lines = generic_tpn.load_tpn_lines(path)

    expected = [
        'META.SUBARRAY.NAME          H   C   (is_imaging_mode(EXP_TYPE))',
        'SUBARRAY                    H   C   O',
        'META.SUBARRAY.XSTART        H   I   (is_imaging_mode(EXP_TYPE))',
        'META.SUBARRAY.YSTART        H   I   (is_imaging_mode(EXP_TYPE))',
        'META.SUBARRAY.XSIZE         H   I   (is_imaging_mode(EXP_TYPE))',
        'META.SUBARRAY.YSIZE         H   I   (is_imaging_mode(EXP_TYPE))',
        'META.SUBARRAY.FASTAXIS      H   I   (is_imaging_mode(EXP_TYPE))',
        'META.SUBARRAY.SLOWAXIS      H   I   (is_imaging_mode(EXP_TYPE))',
        "FULLFRAME_XSTART            X   X   (full_frame(INSTRUME!='NIRSPEC'))   (META_SUBARRAY_XSTART==1)",
        "FULLFRAME_YSTART            X   X   (full_frame(INSTRUME!='NIRSPEC'))   (META_SUBARRAY_YSTART==1)",
        'DETECTOR                    H   C   O',
        "NRCA1_AXIS                  X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCA1'))    ((FASTAXIS==-1)and(SLOWAXIS==2))",
        "NRCA2_AXIS                  X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCA2'))    ((FASTAXIS==1)and(SLOWAXIS==-2))",
        "NRCA3_AXIS                  X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCA3'))    ((FASTAXIS==-1)and(SLOWAXIS==2))",
        "NRCA4_AXIS                  X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCA4'))    ((FASTAXIS==1)and(SLOWAXIS==-2))",
        "NRCALONG_AXIS               X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCALONG')) ((FASTAXIS==-1)and(SLOWAXIS==2))",
        "NRCB1_AXIS                  X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCB1'))    ((FASTAXIS==1)and(SLOWAXIS==-2))",
        "NRCB2_AXIS                  X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCB2'))    ((FASTAXIS==-1)and(SLOWAXIS==2))",
        "NRCB3_AXIS                  X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCB3'))    ((FASTAXIS==1)and(SLOWAXIS==-2))",
        "NRCB4_AXIS                  X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCB4'))    ((FASTAXIS==-1)and(SLOWAXIS==2))",
        "NRCBLONG_AXIS               X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCBLONG')) ((FASTAXIS==1)and(SLOWAXIS==-2))",
        "MIRIMAGE_AXIS               X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='MIRIMAGE'))    ((FASTAXIS==1)and(SLOWAXIS==2))",
        "MIRIFULONG_AXIS             X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='MIRIFULONG'))  ((FASTAXIS==1)and(SLOWAXIS==2))",
        "MIRIFUSHORT_AXIS            X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='MIRIFUSHORT')) ((FASTAXIS==1)and(SLOWAXIS==2))",
        "NRS1_AXIS                   X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRS1'))    ((FASTAXIS==2)and(SLOWAXIS==1))",
        "NRS2_AXIS                   X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRS2'))    ((FASTAXIS==-2)and(SLOWAXIS==-1))",
        "NIS_AXIS                    X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='NIS'))    ((FASTAXIS==-2)and(SLOWAXIS==-1))",
        "GUIDER1_AXIS                X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='GUIDER1')) ((FASTAXIS==-2)and(SLOWAXIS==-1))",
        "GUIDER2_AXIS                X   X   (is_imaging_mode(EXP_TYPE)and(DETECTOR=='GUIDER2')) ((FASTAXIS==2)and(SLOWAXIS==-1))",
        'SCI       A           X         ((True))                              (array_exists(SCI_ARRAY))',
        'SCI       A           X         ((True))                              (is_image(SCI_ARRAY))',
        "SCI       A           X         ((True))                              (has_type(SCI_ARRAY,['FLOAT','INT']))",
        'SUBARRAY_INBOUNDS_X         X   X   ((True))                           (1<=META_SUBARRAY_XSTART+META_SUBARRAY_XSIZE-1<=2048)',
        'SUBARRAY_INBOUNDS_Y         X   X   ((True))                           (1<=META_SUBARRAY_YSTART+META_SUBARRAY_YSIZE-1<=2048)',
        'SCI       A           X             ((True))                           (SCI_ARRAY.SHAPE[-2:]>=(META_SUBARRAY_YSIZE,META_SUBARRAY_XSIZE))',
        'SCI       A           X         (is_full_frame(SUBARRAY)and(not(is_irs2(READPATT))))   (warn_only(SCI_ARRAY.SHAPE[-2:]in[(2048,2048),(32,2048),(64,2048),(256,2048),(260,2048)]))',
        'SCI       A           X         (is_full_frame(SUBARRAY)and(is_irs2(READPATT)))        (warn_only(SCI_ARRAY.SHAPE[-2:]in[(3200,2048),(32,2048),(64,2048),(256,2048)]))',
        'SCI       A           X         (is_subarray(SUBARRAY)and(not(is_irs2(READPATT))))     (1<=META_SUBARRAY_YSTART+SCI_ARRAY.SHAPE[-2]-1<=2048)',
        'SCI       A           X         (is_subarray(SUBARRAY)and(is_irs2(READPATT)))          (1<=META_SUBARRAY_YSTART+SCI_ARRAY.SHAPE[-2]-1<=3200)',
        'SCI       A           X         (is_subarray(SUBARRAY))                                (1<=META_SUBARRAY_XSTART+SCI_ARRAY.SHAPE[-1]-1<=2048)',
        'DQ   A    X         (optional((True)))                                    (is_image(DQ_ARRAY))',
        "DQ   A    X         (optional((True)))                                    (warn_only(has_type(DQ_ARRAY,'INT')))",
        'DQ   A    X         ((array_exists(SCI_ARRAY))and(array_exists(DQ_ARRAY)))    (DQ_ARRAY.SHAPE[-2:]==SCI_ARRAY.SHAPE[-2:])',
        'DQ_DEF       A           X         O             (is_table(DQ_DEF_ARRAY))',
        "DQ_DEF       A           X         O             (has_columns(DQ_DEF_ARRAY,['BIT','VALUE','NAME','DESCRIPTION']))",
        "DQ_DEF       A           X         O             (has_column_type(DQ_DEF_ARRAY,'BIT','INT'))",
        "DQ_DEF       A           X         O             (has_column_type(DQ_DEF_ARRAY,'VALUE','INT'))",
        "DQ_DEF       A           X         O             (has_column_type(DQ_DEF_ARRAY,'NAME','STRING'))",
        "DQ_DEF       A           X         O             (has_column_type(DQ_DEF_ARRAY,'DESCRIPTION','STRING'))",
        'SCI   A   X    R  (ndim(SCI_ARRAY,2))',
        'DQ    A   X    O  (ndim(DQ_ARRAY,2))',
        'META.EXPOSURE.GAIN_FACTOR     H   R   W  1.0:10.0'
    ]
    for line, exp in zip(lines, expected):
        assert line == exp


@mark.jwst
@mark.certify
def test_load_nirspec_saturation_tpn(jwst_serverless_state):
    """Print out the outcome of various .tpn directives like 'replace' and
    'include' and reuse of generic files as actual .tpn objects.
    """
    path = generic_tpn.get_tpn_path("nirspec_saturation.tpn","jwst")
    loaded = generic_tpn.load_tpn(path)

    expected = """('META.SUBARRAY.NAME', 'HEADER', 'CHARACTER', condition='(is_imaging_mode(EXP_TYPE))', values=())
('SUBARRAY', 'HEADER', 'CHARACTER', 'OPTIONAL', values=())
('META.SUBARRAY.XSTART', 'HEADER', 'INTEGER', condition='(is_imaging_mode(EXP_TYPE))', values=())
('META.SUBARRAY.YSTART', 'HEADER', 'INTEGER', condition='(is_imaging_mode(EXP_TYPE))', values=())
('META.SUBARRAY.XSIZE', 'HEADER', 'INTEGER', condition='(is_imaging_mode(EXP_TYPE))', values=())
('META.SUBARRAY.YSIZE', 'HEADER', 'INTEGER', condition='(is_imaging_mode(EXP_TYPE))', values=())
('META.SUBARRAY.FASTAXIS', 'HEADER', 'INTEGER', condition='(is_imaging_mode(EXP_TYPE))', values=())
('META.SUBARRAY.SLOWAXIS', 'HEADER', 'INTEGER', condition='(is_imaging_mode(EXP_TYPE))', values=())
('FULLFRAME_XSTART', 'EXPRESSION', 'EXPRESSION', condition="(full_frame(INSTRUME!='NIRSPEC'))", expression='(META_SUBARRAY_XSTART==1)')
('FULLFRAME_YSTART', 'EXPRESSION', 'EXPRESSION', condition="(full_frame(INSTRUME!='NIRSPEC'))", expression='(META_SUBARRAY_YSTART==1)')
('DETECTOR', 'HEADER', 'CHARACTER', 'OPTIONAL', values=())
('NRCA1_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCA1'))", expression='((FASTAXIS==-1)and(SLOWAXIS==2))')
('NRCA2_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCA2'))", expression='((FASTAXIS==1)and(SLOWAXIS==-2))')
('NRCA3_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCA3'))", expression='((FASTAXIS==-1)and(SLOWAXIS==2))')
('NRCA4_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCA4'))", expression='((FASTAXIS==1)and(SLOWAXIS==-2))')
('NRCALONG_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCALONG'))", expression='((FASTAXIS==-1)and(SLOWAXIS==2))')
('NRCB1_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCB1'))", expression='((FASTAXIS==1)and(SLOWAXIS==-2))')
('NRCB2_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCB2'))", expression='((FASTAXIS==-1)and(SLOWAXIS==2))')
('NRCB3_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCB3'))", expression='((FASTAXIS==1)and(SLOWAXIS==-2))')
('NRCB4_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCB4'))", expression='((FASTAXIS==-1)and(SLOWAXIS==2))')
('NRCBLONG_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRCBLONG'))", expression='((FASTAXIS==1)and(SLOWAXIS==-2))')
('MIRIMAGE_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='MIRIMAGE'))", expression='((FASTAXIS==1)and(SLOWAXIS==2))')
('MIRIFULONG_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='MIRIFULONG'))", expression='((FASTAXIS==1)and(SLOWAXIS==2))')
('MIRIFUSHORT_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='MIRIFUSHORT'))", expression='((FASTAXIS==1)and(SLOWAXIS==2))')
('NRS1_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRS1'))", expression='((FASTAXIS==2)and(SLOWAXIS==1))')
('NRS2_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NRS2'))", expression='((FASTAXIS==-2)and(SLOWAXIS==-1))')
('NIS_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='NIS'))", expression='((FASTAXIS==-2)and(SLOWAXIS==-1))')
('GUIDER1_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='GUIDER1'))", expression='((FASTAXIS==-2)and(SLOWAXIS==-1))')
('GUIDER2_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(is_imaging_mode(EXP_TYPE)and(DETECTOR=='GUIDER2'))", expression='((FASTAXIS==2)and(SLOWAXIS==-1))')
('SCI', 'ARRAY_FORMAT', 'EXPRESSION', condition='((True))', expression='(array_exists(SCI_ARRAY))')
('SCI', 'ARRAY_FORMAT', 'EXPRESSION', condition='((True))', expression='(is_image(SCI_ARRAY))')
('SCI', 'ARRAY_FORMAT', 'EXPRESSION', condition='((True))', expression="(has_type(SCI_ARRAY,['FLOAT','INT']))")
('SUBARRAY_INBOUNDS_X', 'EXPRESSION', 'EXPRESSION', condition='((True))', expression='(1<=META_SUBARRAY_XSTART+META_SUBARRAY_XSIZE-1<=2048)')
('SUBARRAY_INBOUNDS_Y', 'EXPRESSION', 'EXPRESSION', condition='((True))', expression='(1<=META_SUBARRAY_YSTART+META_SUBARRAY_YSIZE-1<=2048)')
('SCI', 'ARRAY_FORMAT', 'EXPRESSION', condition='((True))', expression='(SCI_ARRAY.SHAPE[-2:]>=(META_SUBARRAY_YSIZE,META_SUBARRAY_XSIZE))')
('SCI', 'ARRAY_FORMAT', 'EXPRESSION', condition='(is_full_frame(SUBARRAY)and(not(is_irs2(READPATT))))', expression='(warn_only(SCI_ARRAY.SHAPE[-2:]in[(2048,2048),(32,2048),(64,2048),(256,2048),(260,2048)]))')
('SCI', 'ARRAY_FORMAT', 'EXPRESSION', condition='(is_full_frame(SUBARRAY)and(is_irs2(READPATT)))', expression='(warn_only(SCI_ARRAY.SHAPE[-2:]in[(3200,2048),(32,2048),(64,2048),(256,2048)]))')
('SCI', 'ARRAY_FORMAT', 'EXPRESSION', condition='(is_subarray(SUBARRAY)and(not(is_irs2(READPATT))))', expression='(1<=META_SUBARRAY_YSTART+SCI_ARRAY.SHAPE[-2]-1<=2048)')
('SCI', 'ARRAY_FORMAT', 'EXPRESSION', condition='(is_subarray(SUBARRAY)and(is_irs2(READPATT)))', expression='(1<=META_SUBARRAY_YSTART+SCI_ARRAY.SHAPE[-2]-1<=3200)')
('SCI', 'ARRAY_FORMAT', 'EXPRESSION', condition='(is_subarray(SUBARRAY))', expression='(1<=META_SUBARRAY_XSTART+SCI_ARRAY.SHAPE[-1]-1<=2048)')
('DQ', 'ARRAY_FORMAT', 'EXPRESSION', condition='(optional((True)))', expression='(is_image(DQ_ARRAY))')
('DQ', 'ARRAY_FORMAT', 'EXPRESSION', condition='(optional((True)))', expression="(warn_only(has_type(DQ_ARRAY,'INT')))")
('DQ', 'ARRAY_FORMAT', 'EXPRESSION', condition='((array_exists(SCI_ARRAY))and(array_exists(DQ_ARRAY)))', expression='(DQ_ARRAY.SHAPE[-2:]==SCI_ARRAY.SHAPE[-2:])')
('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression='(is_table(DQ_DEF_ARRAY))')
('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_columns(DQ_DEF_ARRAY,['BIT','VALUE','NAME','DESCRIPTION']))")
('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_column_type(DQ_DEF_ARRAY,'BIT','INT'))")
('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_column_type(DQ_DEF_ARRAY,'VALUE','INT'))")
('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_column_type(DQ_DEF_ARRAY,'NAME','STRING'))")
('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_column_type(DQ_DEF_ARRAY,'DESCRIPTION','STRING'))")
('SCI', 'ARRAY_FORMAT', 'EXPRESSION', 'REQUIRED', expression='(ndim(SCI_ARRAY,2))')
('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression='(ndim(DQ_ARRAY,2))')
('META.EXPOSURE.GAIN_FACTOR', 'HEADER', 'REAL', 'WARN', values=('1.0:10.0',))""".splitlines()
    for line, exp in zip(loaded, expected):
        assert str(line) == exp


@mark.jwst
@mark.certify
def test_load_miri_mask_tpn_lines(jwst_serverless_state):
    """Print out the outcome of various .tpn directives like 'replace' and
    'include' and reuse of generic files as actual .tpn objects.
    """
    path = generic_tpn.get_tpn_path("miri_mask.tpn","jwst")
    loaded = generic_tpn.load_tpn_lines(path)

    expected = [
        'META.SUBARRAY.NAME          H   C   R',
        'META.SUBARRAY.XSTART        H   I   R',
        'META.SUBARRAY.YSTART        H   I   R',
        'META.SUBARRAY.XSIZE         H   I   R',
        'META.SUBARRAY.YSIZE         H   I   R',
        'META.SUBARRAY.FASTAXIS      H   I   R',
        'META.SUBARRAY.SLOWAXIS      H   I   R',
        'SUBARRAY_INBOUNDS_X         X   X   A  (1<=META_SUBARRAY_XSTART+META_SUBARRAY_XSIZE-1<=1032)',
        'SUBARRAY_INBOUNDS_Y         X   X   A  (1<=META_SUBARRAY_YSTART+META_SUBARRAY_YSIZE-1<=1024)',
        'DETECTOR              H   C   O',
        "MIRIMAGE_AXIS         X   X   (DETECTOR=='MIRIMAGE')    ((FASTAXIS==1)and(SLOWAXIS==2))",
        "MIRIFULONG_AXIS       X   X   (DETECTOR=='MIRIFULONG')  ((FASTAXIS==1)and(SLOWAXIS==2))",
        "MIRIFUSHORT_AXIS      X   X   (DETECTOR=='MIRIFUSHORT') ((FASTAXIS==1)and(SLOWAXIS==2))",
        'FULLFRAME_XSTART     X           X         F             (META_SUBARRAY_XSTART==1)',
        'FULLFRAME_YSTART     X           X         F             (META_SUBARRAY_YSTART==1)',
        'FULLFRAME_XSIZE      X           X         F             (META_SUBARRAY_XSIZE==1032)',
        'FULLFRAME_YSIZE      X           X         F             (META_SUBARRAY_YSIZE==1024)',
        'SUBARRAY_XSTART      X           X         S             (1<=META_SUBARRAY_XSTART<=1032)',
        'SUBARRAY_YSTART      X           X         S             (1<=META_SUBARRAY_YSTART<=1024)',
        'SUBARRAY_XSIZE       X           X         S             (1<=META_SUBARRAY_XSIZE<=1032)',
        'SUBARRAY_YSIZE       X           X         S             (1<=META_SUBARRAY_YSIZE<=1024)',
        'DQ       A           X         R             (is_image(DQ_ARRAY))',
        "DQ       A           X         R             (has_type(DQ_ARRAY,'INT'))",
        'DQ       A           X         F             (DQ_ARRAY.SHAPE[-2:]==(1024,1032))',
        'DQ       A           X         S             (DQ_ARRAY.SHAPE[-2:]==(META_SUBARRAY_YSIZE,META_SUBARRAY_XSIZE))',
        'DQ       A           X         S             (1<=META_SUBARRAY_YSTART+DQ_ARRAY.SHAPE[-2]-1<=1024)',
        'DQ       A           X         S             (1<=META_SUBARRAY_XSTART+DQ_ARRAY.SHAPE[-1]-1<=1032)',
        'DQ       A           X         O   (ndim(DQ_ARRAY,2))',
        'DQ_DEF       A           X         O             (is_table(DQ_DEF_ARRAY))',
        "DQ_DEF       A           X         O             (has_columns(DQ_DEF_ARRAY,['BIT','VALUE','NAME','DESCRIPTION']))",
        "DQ_DEF       A           X         O             (has_column_type(DQ_DEF_ARRAY,'BIT','INT'))",
        "DQ_DEF       A           X         O             (has_column_type(DQ_DEF_ARRAY,'VALUE','INT'))",
        "DQ_DEF       A           X         O             (has_column_type(DQ_DEF_ARRAY,'NAME','STRING'))",
        "DQ_DEF       A           X         O             (has_column_type(DQ_DEF_ARRAY,'DESCRIPTION','STRING'))"
    ]
    for line, exp in zip(loaded, expected):
        assert line == exp


@mark.jwst
@mark.certify
def test_load_miri_mask_tpn(jwst_serverless_state):
    path = generic_tpn.get_tpn_path("miri_mask.tpn","jwst")
    loaded = generic_tpn.load_tpn(path)

    expected = """('META.SUBARRAY.NAME', 'HEADER', 'CHARACTER', 'REQUIRED', values=())
('META.SUBARRAY.XSTART', 'HEADER', 'INTEGER', 'REQUIRED', values=())
('META.SUBARRAY.YSTART', 'HEADER', 'INTEGER', 'REQUIRED', values=())
('META.SUBARRAY.XSIZE', 'HEADER', 'INTEGER', 'REQUIRED', values=())
('META.SUBARRAY.YSIZE', 'HEADER', 'INTEGER', 'REQUIRED', values=())
('META.SUBARRAY.FASTAXIS', 'HEADER', 'INTEGER', 'REQUIRED', values=())
('META.SUBARRAY.SLOWAXIS', 'HEADER', 'INTEGER', 'REQUIRED', values=())
('SUBARRAY_INBOUNDS_X', 'EXPRESSION', 'EXPRESSION', 'ANY_SUBARRAY', expression='(1<=META_SUBARRAY_XSTART+META_SUBARRAY_XSIZE-1<=1032)')
('SUBARRAY_INBOUNDS_Y', 'EXPRESSION', 'EXPRESSION', 'ANY_SUBARRAY', expression='(1<=META_SUBARRAY_YSTART+META_SUBARRAY_YSIZE-1<=1024)')
('DETECTOR', 'HEADER', 'CHARACTER', 'OPTIONAL', values=())
('MIRIMAGE_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(DETECTOR=='MIRIMAGE')", expression='((FASTAXIS==1)and(SLOWAXIS==2))')
('MIRIFULONG_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(DETECTOR=='MIRIFULONG')", expression='((FASTAXIS==1)and(SLOWAXIS==2))')
('MIRIFUSHORT_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(DETECTOR=='MIRIFUSHORT')", expression='((FASTAXIS==1)and(SLOWAXIS==2))')
('FULLFRAME_XSTART', 'EXPRESSION', 'EXPRESSION', 'IF_FULL_FRAME', expression='(META_SUBARRAY_XSTART==1)')
('FULLFRAME_YSTART', 'EXPRESSION', 'EXPRESSION', 'IF_FULL_FRAME', expression='(META_SUBARRAY_YSTART==1)')
('FULLFRAME_XSIZE', 'EXPRESSION', 'EXPRESSION', 'IF_FULL_FRAME', expression='(META_SUBARRAY_XSIZE==1032)')
('FULLFRAME_YSIZE', 'EXPRESSION', 'EXPRESSION', 'IF_FULL_FRAME', expression='(META_SUBARRAY_YSIZE==1024)')
('SUBARRAY_XSTART', 'EXPRESSION', 'EXPRESSION', 'IF_SUBARRAY', expression='(1<=META_SUBARRAY_XSTART<=1032)')
('SUBARRAY_YSTART', 'EXPRESSION', 'EXPRESSION', 'IF_SUBARRAY', expression='(1<=META_SUBARRAY_YSTART<=1024)')
('SUBARRAY_XSIZE', 'EXPRESSION', 'EXPRESSION', 'IF_SUBARRAY', expression='(1<=META_SUBARRAY_XSIZE<=1032)')
('SUBARRAY_YSIZE', 'EXPRESSION', 'EXPRESSION', 'IF_SUBARRAY', expression='(1<=META_SUBARRAY_YSIZE<=1024)')
('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'REQUIRED', expression='(is_image(DQ_ARRAY))')
('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'REQUIRED', expression="(has_type(DQ_ARRAY,'INT'))")
('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'IF_FULL_FRAME', expression='(DQ_ARRAY.SHAPE[-2:]==(1024,1032))')
('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'IF_SUBARRAY', expression='(DQ_ARRAY.SHAPE[-2:]==(META_SUBARRAY_YSIZE,META_SUBARRAY_XSIZE))')
('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'IF_SUBARRAY', expression='(1<=META_SUBARRAY_YSTART+DQ_ARRAY.SHAPE[-2]-1<=1024)')
('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'IF_SUBARRAY', expression='(1<=META_SUBARRAY_XSTART+DQ_ARRAY.SHAPE[-1]-1<=1032)')
('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression='(ndim(DQ_ARRAY,2))')
('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression='(is_table(DQ_DEF_ARRAY))')
('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_columns(DQ_DEF_ARRAY,['BIT','VALUE','NAME','DESCRIPTION']))")
('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_column_type(DQ_DEF_ARRAY,'BIT','INT'))")
('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_column_type(DQ_DEF_ARRAY,'VALUE','INT'))")
('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_column_type(DQ_DEF_ARRAY,'NAME','STRING'))")
('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_column_type(DQ_DEF_ARRAY,'DESCRIPTION','STRING'))")""".splitlines()
    for line, exp in zip(loaded, expected):
        assert str(line) == exp


@mark.hst
@mark.certify
def test_acs_idctab_char_plus_column(default_shared_state, hst_data, caplog):
    argv = f"crds.certify {hst_data}/acs_new_idc.fits --comparison-context hst_0508.pmap"
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(argv)()
        out = caplog.text

    # Due to the nature of the test file, a numpy.float128 is used. However, this is not
    # supported on many architectures. Mark xfail if this there is no support.
    if """ module 'numpy' has no attribute""" in out:
        xfail('Test requires numpy.float128, which current system does not support.')

    expected_out = """Certifying
    acs_new_idc.fits' (1/1) as 'FITS' relative to context 'hst_0508.pmap'
    FITS file 'acs_new_idc.fits' conforms to FITS standards.
    Comparing reference 'acs_new_idc.fits' against 'p7d1548qj_idc.fits'
    Mode columns defined by spec for old reference 'p7d1548qj_idc.fits[1]' are: ['DETCHIP', 'WAVELENGTH', 'DIRECTION', 'FILTER1', 'FILTER2', 'V2REF', 'V3REF']
    All column names for this table old reference 'p7d1548qj_idc.fits[1]' are: ['DETCHIP', 'DIRECTION', 'FILTER1', 'FILTER2', 'XSIZE', 'YSIZE', 'XREF', 'YREF', 'V2REF', 'V3REF', 'SCALE', 'CX10', 'CX11', 'CX20', 'CX21', 'CX22', 'CX30', 'CX31', 'CX32', 'CX33', 'CX40', 'CX41', 'CX42', 'CX43', 'CX44', 'CY10', 'CY11', 'CY20', 'CY21', 'CY22', 'CY30', 'CY31', 'CY32', 'CY33', 'CY40', 'CY41', 'CY42', 'CY43', 'CY44']
    Checking for duplicate modes using intersection ['DETCHIP', 'DIRECTION', 'FILTER1', 'FILTER2', 'V2REF', 'V3REF']
    Duplicate definitions in old reference 'p7d1548qj_idc.fits[1]' for mode: (('DETCHIP', 1), ('DIRECTION', 'FORWARD'), ('FILTER1', 'F550M'), ('FILTER2', 'F220W'), ('V2REF', 207.082), ('V3REF', 471.476)) :
    (29, (('DETCHIP', 1), ('DIRECTION', 'FORWARD'), ('FILTER1', 'F550M'), ('FILTER2', 'F220W'), ('XSIZE', 1024), ('YSIZE', 1024), ('XREF', 512.0), ('YREF', 512.0), ('V2REF', 207.082), ('V3REF', 471.476), ('SCALE', 0.025), ('CX10', -9.479088e-08), ('CX11', 0.028289594), ('CX20', -1.9904244e-08), ('CX21', 2.5261727e-07), ('CX22', -9.322343e-08), ('CX30', -2.4618475e-13), ('CX31', 1.0903676e-11), ('CX32', 5.9885034e-13), ('CX33', 3.2860548e-12), ('CX40', 1.1240284e-15), ('CX41', 3.591716e-15), ('CX42', -4.085765e-14), ('CX43', -5.2304664e-14), ('CX44', 6.967954e-15), ('CY10', 0.02483979), ('CY11', 0.0028646854), ('CY20', 2.8243642e-07), ('CY21', -4.0260268e-08), ('CY22', 3.9303682e-08), ('CY30', 1.2405402e-11), ('CY31', -1.6079407e-11), ('CY32', 8.246831e-12), ('CY33', 1.1388372e-11), ('CY40', -2.7262569e-14), ('CY41', -1.3812129e-14), ('CY42', 2.0695324e-14), ('CY43', -4.071885e-14), ('CY44', 1.0464957e-14)))
    (35, (('DETCHIP', 1), ('DIRECTION', 'FORWARD'), ('FILTER1', 'F550M'), ('FILTER2', 'F220W'), ('XSIZE', 1024), ('YSIZE', 1024), ('XREF', 512.0), ('YREF', 512.0), ('V2REF', 207.082), ('V3REF', 471.476), ('SCALE', 0.025), ('CX10', -9.479088e-08), ('CX11', 0.028289594), ('CX20', -1.9904244e-08), ('CX21', 2.5261727e-07), ('CX22', -9.322343e-08), ('CX30', -2.4618475e-13), ('CX31', 1.0903676e-11), ('CX32', 5.9885034e-13), ('CX33', 3.2860548e-12), ('CX40', 1.1240284e-15), ('CX41', 3.591716e-15), ('CX42', -4.085765e-14), ('CX43', -5.2304664e-14), ('CX44', 6.967954e-15), ('CY10', 0.02483979), ('CY11', 0.0028646854), ('CY20', 2.8243642e-07), ('CY21', -4.0260268e-08), ('CY22', 3.9303682e-08), ('CY30', 1.2405402e-11), ('CY31', -1.6079407e-11), ('CY32', 8.246831e-12), ('CY33', 1.1388372e-11), ('CY40', -2.7262569e-14), ('CY41', -1.3812129e-14), ('CY42', 2.0695324e-14), ('CY43', -4.071885e-14), ('CY44', 1.0464957e-14)))
    Mode columns defined by spec for new reference 'acs_new_idc.fits[1]' are: ['DETCHIP', 'WAVELENGTH', 'DIRECTION', 'FILTER1', 'FILTER2', 'V2REF', 'V3REF']
    All column names for this table new reference 'acs_new_idc.fits[1]' are: ['DETCHIP', 'DIRECTION', 'FILTER1', 'FILTER2']
    Checking for duplicate modes using intersection ['DETCHIP', 'DIRECTION', 'FILTER1', 'FILTER2']
    Change in row format between 'p7d1548qj_idc.fits[1]' and 'acs_new_idc.fits[1]'
    0 errors
    2 warnings"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.hst
@mark.certify
def test_certify_check_rmap_updates(hst_serverless_state, hst_data, caplog):
    """This test verifies trial rmap updates under the control of the CRDS certify program.
    It checks for two primary conditions:

    1. That submitted files with identical matching criteria which would replace one another are errors.
    2. That new files which overlap the matching criteria of existing files without being identical are detected.

    Handling of (2) varies by project,  because for HST it is grudgingly permitted due to its
    existence in CDBS and the need for identical rmap behavior to CDBS.  For JWST,  where
    overlaps are avoidable,  non-identical overlaps are warnings during file submission and fatal errors
    if encountered at runtime. For HST,  warnings are only visible in --verbose mode,  but for JWST they
    are always visible.   Using warnings avoids the automatic cancellation of large file submissions,
    holding open a choice between choosing to cancel or choosing to submit manual rmap fixes instead.
    """
    argv = f"crds.certify {hst_data}/s7g1700gl_dead_overlap.fits {hst_data}/s7g1700gl_dead_dup1.fits {hst_data}/s7g1700gl_dead_dup2.fits --check-rmap-updates --comparison-context hst_0508.pmap --verbose"
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        CertifyScript(argv)()
        out = caplog.text

    expected1 = f"Command: ['crds.certify', '{hst_data}/s7g1700gl_dead_overlap.fits', '{hst_data}/s7g1700gl_dead_dup1.fits', '{hst_data}/s7g1700gl_dead_dup2.fits', '--check-rmap-updates', '--comparison-context', 'hst_0508.pmap', '--verbose']"
    assert expected1 in out
    expected2 = f"Certifying '{hst_data}/s7g1700gl_dead_dup1.fits' (1/3) as 'FITS' relative to context 'hst_0508.pmap'"
    assert expected2 in out

    expected3 = """No unique row parameters, skipping table row checks.
FITS file 's7g1700gl_dead_dup1.fits' conforms to FITS standards.
File='s7g1700gl_dead_dup1.fits' class='Character' keyword='DESCRIP' value='INITIAL VERSION' no .tpn values defined.
File='s7g1700gl_dead_dup1.fits' class='Character' keyword='DETECTOR' value='FUV' is in ['FUV', 'NUV']
File='s7g1700gl_dead_dup1.fits' class='Character' keyword='FILETYPE' value='DEADTIME REFERENCE TABLE' is in ['DEADTIME REFERENCE TABLE']
File='s7g1700gl_dead_dup1.fits' class='Character' keyword='INSTRUME' value='COS' is in ['COS']
File='s7g1700gl_dead_dup1.fits' class='Pedigree' keyword='PEDIGREE' value='GROUND' is in ['INFLIGHT', 'GROUND', 'MODEL', 'DUMMY', 'SIMULATION']
File='s7g1700gl_dead_dup1.fits[0]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_dup1.fits[1]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_dup1.fits[2]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_dup1.fits[3]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_dup1.fits[4]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_dup1.fits[5]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_dup1.fits[6]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_dup1.fits[7]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_dup1.fits[8]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_dup1.fits[9]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_dup1.fits' class='Sybdate' keyword='USEAFTER' value='Oct 01 1996 00:00:00'
File='s7g1700gl_dead_dup1.fits' class='Character' keyword='VCALCOS' value='2.0' no .tpn values defined."""

    expected4 = f"Certifying '{hst_data}/s7g1700gl_dead_dup2.fits' (2/3) as 'FITS' relative to context 'hst_0508.pmap'"
    assert expected4 in out

    expected5 = """No unique row parameters, skipping table row checks.
FITS file 's7g1700gl_dead_dup2.fits' conforms to FITS standards.
File='s7g1700gl_dead_dup2.fits' class='Character' keyword='DESCRIP' value='INITIAL VERSION' no .tpn values defined.
File='s7g1700gl_dead_dup2.fits' class='Character' keyword='DETECTOR' value='FUV' is in ['FUV', 'NUV']
File='s7g1700gl_dead_dup2.fits' class='Character' keyword='FILETYPE' value='DEADTIME REFERENCE TABLE' is in ['DEADTIME REFERENCE TABLE']
File='s7g1700gl_dead_dup2.fits' class='Character' keyword='INSTRUME' value='COS' is in ['COS']
File='s7g1700gl_dead_dup2.fits' class='Pedigree' keyword='PEDIGREE' value='GROUND' is in ['INFLIGHT', 'GROUND', 'MODEL', 'DUMMY', 'SIMULATION']
File='s7g1700gl_dead_dup2.fits[0]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_dup2.fits[1]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_dup2.fits[2]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_dup2.fits[3]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_dup2.fits[4]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_dup2.fits[5]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_dup2.fits[6]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_dup2.fits[7]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_dup2.fits[8]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_dup2.fits[9]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_dup2.fits' class='Sybdate' keyword='USEAFTER' value='Oct 01 1996 00:00:00'
File='s7g1700gl_dead_dup2.fits' class='Character' keyword='VCALCOS' value='2.0' no .tpn values defined.
"""
    expected6 = f"Certifying '{hst_data}/s7g1700gl_dead_overlap.fits' (3/3) as 'FITS' relative to context 'hst_0508.pmap'"
    assert expected6 in out

    expected7 = """No unique row parameters, skipping table row checks.
FITS file 's7g1700gl_dead_overlap.fits' conforms to FITS standards.
File='s7g1700gl_dead_overlap.fits' class='Character' keyword='DESCRIP' value='INITIAL VERSION' no .tpn values defined.
File='s7g1700gl_dead_overlap.fits' class='Character' keyword='DETECTOR' value='FUV|NUV' is an or'ed parameter matching ['FUV', 'NUV']
File='s7g1700gl_dead_overlap.fits' class='Character' keyword='DETECTOR' value='FUV' is in ['FUV', 'NUV']
File='s7g1700gl_dead_overlap.fits' class='Character' keyword='DETECTOR' value='NUV' is in ['FUV', 'NUV']
File='s7g1700gl_dead_overlap.fits' class='Character' keyword='FILETYPE' value='DEADTIME REFERENCE TABLE' is in ['DEADTIME REFERENCE TABLE']
File='s7g1700gl_dead_overlap.fits' class='Character' keyword='INSTRUME' value='COS' is in ['COS']
File='s7g1700gl_dead_overlap.fits' class='Pedigree' keyword='PEDIGREE' value='GROUND' is in ['INFLIGHT', 'GROUND', 'MODEL', 'DUMMY', 'SIMULATION']
File='s7g1700gl_dead_overlap.fits[0]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_overlap.fits[1]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_overlap.fits[2]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_overlap.fits[3]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_overlap.fits[4]' class='Character' keyword='SEGMENT' value='FUVA' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_overlap.fits[5]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_overlap.fits[6]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_overlap.fits[7]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_overlap.fits[8]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_overlap.fits[9]' class='Character' keyword='SEGMENT' value='FUVB' is in ['ANY', 'FUVA', 'FUVB']
File='s7g1700gl_dead_overlap.fits' class='Sybdate' keyword='USEAFTER' value='Oct 01 1996 00:00:00'
File='s7g1700gl_dead_overlap.fits' class='Character' keyword='VCALCOS' value='2.0' no .tpn values defined."""

    expected8 = f"Checking rmap update for ('cos', 'deadtab') inserting files ['{hst_data}/s7g1700gl_dead_dup1.fits', '{hst_data}/s7g1700gl_dead_dup2.fits', '{hst_data}/s7g1700gl_dead_overlap.fits']"
    assert expected8 in out

    expected9 = """Inserting s7g1700gl_dead_dup1.fits into 'hst_cos_deadtab_0250.rmap'
Unexpanded header [('DETECTOR', 'FUV'), ('LIFE_ADJ', 'UNDEFINED'), ('OPT_ELEM', 'UNDEFINED')]
Skipping expansion for unused parkey 'LIFE_ADJ' of '-1.0|1.0'
Skipping expansion for unused parkey 'LIFE_ADJ' of '-1.0|1.0'
Skipping expansion for unused parkey 'OPT_ELEM' of 'G130M|G140L|G160M'
Skipping expansion for unused parkey 'OPT_ELEM' of 'G185M|G225M|G230L|G285M|MIRRORA|MIRRORB'
Expanded header [('DETECTOR', 'FUV'), ('LIFE_ADJ', 'UNDEFINED'), ('OPT_ELEM', 'UNDEFINED')]
Mapping extra parkey 'DEADCORR' from UNDEFINED to 'N/A'.
Validating key 'FUV'
Checking 'DETECTOR' = 'FUV' against ('FUV', 'NUV')
Modify found ('FUV',) augmenting UseAfterSelector(('DATE-OBS', 'TIME-OBS'), nselections=1) with 's7g1700gl_dead_dup1.fits'
Validating key '1996-10-01 00:00:00'
Modify found '1996-10-01 00:00:00' as primitive 's7g1700gl_dead.fits' replacing with 's7g1700gl_dead_dup1.fits'
Inserting s7g1700gl_dead_dup2.fits into 'hst_cos_deadtab_0250.rmap'
Unexpanded header [('DETECTOR', 'FUV'), ('LIFE_ADJ', 'UNDEFINED'), ('OPT_ELEM', 'UNDEFINED')]
Skipping expansion for unused parkey 'LIFE_ADJ' of '-1.0|1.0'
Skipping expansion for unused parkey 'LIFE_ADJ' of '-1.0|1.0'
Skipping expansion for unused parkey 'OPT_ELEM' of 'G130M|G140L|G160M'
Skipping expansion for unused parkey 'OPT_ELEM' of 'G185M|G225M|G230L|G285M|MIRRORA|MIRRORB'
Expanded header [('DETECTOR', 'FUV'), ('LIFE_ADJ', 'UNDEFINED'), ('OPT_ELEM', 'UNDEFINED')]
Mapping extra parkey 'DEADCORR' from UNDEFINED to 'N/A'.
Validating key 'FUV'
Checking 'DETECTOR' = 'FUV' against ('FUV', 'NUV')
Modify found ('FUV',) augmenting UseAfterSelector(('DATE-OBS', 'TIME-OBS'), nselections=1) with 's7g1700gl_dead_dup2.fits'
Validating key '1996-10-01 00:00:00'
Modify found '1996-10-01 00:00:00' as primitive 's7g1700gl_dead_dup1.fits' replacing with 's7g1700gl_dead_dup2.fits'
----------------------------------------
Both 's7g1700gl_dead_dup2.fits' and 's7g1700gl_dead_dup1.fits' identically match case:
    ((('DETECTOR', 'FUV'),), (('DATE-OBS', '1996-10-01'), ('TIME-OBS', '00:00:00')))
Each reference would replace the other in the rmap.
Either reference file matching parameters need correction
or additional matching parameters should be added to the rmap
to enable CRDS to differentiate between the two files.
See the file submission section of the CRDS server user's guide here:
    https://hst-crds.stsci.edu/static/users_guide/index.html
for more explanation.
Inserting s7g1700gl_dead_overlap.fits into 'hst_cos_deadtab_0250.rmap'
Unexpanded header [('DETECTOR', 'FUV|NUV'), ('LIFE_ADJ', 'UNDEFINED'), ('OPT_ELEM', 'UNDEFINED')]
Skipping expansion for unused parkey 'LIFE_ADJ' of '-1.0|1.0'
Skipping expansion for unused parkey 'LIFE_ADJ' of '-1.0|1.0'
Skipping expansion for unused parkey 'OPT_ELEM' of 'G130M|G140L|G160M'
Skipping expansion for unused parkey 'OPT_ELEM' of 'G185M|G225M|G230L|G285M|MIRRORA|MIRRORB'
Expanded header [('DETECTOR', 'FUV|NUV'), ('LIFE_ADJ', 'UNDEFINED'), ('OPT_ELEM', 'UNDEFINED')]
Mapping extra parkey 'DEADCORR' from UNDEFINED to 'N/A'.
Validating key 'FUV|NUV'
Checking 'DETECTOR' = 'FUV' against ('FUV', 'NUV')
Checking 'DETECTOR' = 'NUV' against ('FUV', 'NUV')
Modify couldn't find 'FUV|NUV' adding new selector.
creating nested 'UseAfter' with '1996-10-01 00:00:00' = 's7g1700gl_dead_overlap.fits'
Writing '/tmp/hst_cos_deadtab_0250.rmap'
########################################
Certifying '/tmp/hst_cos_deadtab_0250.rmap' as 'MAPPING' relative to context 'hst_0508.pmap'
Parsing '/tmp/hst_cos_deadtab_0250.rmap'
Validating 'hst_cos_deadtab_0250.rmap' with parameters (('DETECTOR',), ('DATE-OBS', 'TIME-OBS'))
Validating key ('FUV',)
Checking 'DETECTOR' = 'FUV' against ('FUV', 'NUV')"""

    expected10 = """Match case
('FUV',) : UseAfter({
    '1996-10-01 00:00:00' : s7g1700gl_dead_dup2.fits
is an equal weight special case of
('FUV|NUV',) : UseAfter({
    '1996-10-01 00:00:00' : s7g1700gl_dead_overlap.fits 
For some parameter sets, CRDS interprets both matches as equally good.
See the file submission section of the CRDS server user's guide here:
    https://hst-crds.stsci.edu/static/users_guide/index.html
for more explanation.
----------------------------------------
Validating key '1996-10-01 00:00:00'
Validating key ('FUV|NUV',)
Checking 'DETECTOR' = 'FUV' against ('FUV', 'NUV')
Checking 'DETECTOR' = 'NUV' against ('FUV', 'NUV')
Validating key '1996-10-01 00:00:00'
Validating key ('NUV',)
Checking 'DETECTOR' = 'NUV' against ('FUV', 'NUV')
----------------------------------------
Match case
('NUV',) : UseAfter({
    '1996-10-01 00:00:00' : s7g1700ql_dead.fits
is an equal weight special case of
('FUV|NUV',) : UseAfter({
    '1996-10-01 00:00:00' : s7g1700gl_dead_overlap.fits 
For some parameter sets, CRDS interprets both matches as equally good.
See the file submission section of the CRDS server user's guide here:
    https://hst-crds.stsci.edu/static/users_guide/index.html
for more explanation.
    ----------------------------------------
Validating key '1996-10-01 00:00:00'
Mapping '/tmp/hst_cos_deadtab_0250.rmap' did not change relative to context 'hst_0508.pmap'
########################################
1 errors
2 warnings"""

    for msg in expected3.splitlines():
        assert msg.strip() in out
    for msg in expected5.splitlines():
        assert msg.strip() in out
    for msg in expected7.splitlines():
        assert msg.strip() in out
    for msg in expected9.splitlines():
        assert msg.strip() in out
    for msg in expected10.splitlines():
        assert msg.strip() in out


@mark.jwst
@mark.certify
def test_asdf_standard_requirement_fail(jwst_serverless_state, jwst_data, caplog):
    """This test verifies trial rmap updates under the control of the CRDS certify program.
    This test is currently a little vague on output because one of two errors are possible:
    - Failure due to asdf_standard_requirement
    - Failure due to the asdf library not handling the ASDF Standard version at all
    Once the servers have asdf 2.6.0+ installed, we can lock down the output a little more.
    """
    argv = f"crds.certify {jwst_data}/jwst_nircam_specwcs_1_5_0.asdf --comparison-context jwst_0591.pmap"
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(argv)()
        out = caplog.text

    expected_out = f"""Certifying '{jwst_data}/jwst_nircam_specwcs_1_5_0.asdf' (1/1) as 'ASDF' relative to context 'jwst_0591.pmap'
ASDF Standard version 1.5.0 does not fulfill context requirement of asdf_standard<1.5
Checking JWST datamodels.
########################################
1 errors
0 warnings"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.jwst
@mark.certify
def test_asdf_standard_requirement_succeed(jwst_serverless_state, jwst_data, caplog):
    argv = f"crds.certify {jwst_data}/jwst_nircam_specwcs_1_4_0.asdf --comparison-context jwst_0591.pmap"
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(argv)()
        out = caplog.text

    expected_out = f"""Certifying '{jwst_data}/jwst_nircam_specwcs_1_4_0.asdf' (1/1) as 'ASDF' relative to context 'jwst_0591.pmap'
Checking JWST datamodels.
########################################
0 errors
0 warnings"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out


@mark.jwst
@mark.certify
def test_asdf_library_version_fail(jwst_serverless_state, jwst_data, caplog):
    argv = f"crds.certify {jwst_data}/jwst_fgs_distortion_bad_asdf_version.asdf --comparison-context jwst_0591.pmap"
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(argv)()
        out = caplog.text

    if asdf.__version__ < "3.0.0":
        expected_out = f"""Certifying '{jwst_data}/jwst_fgs_distortion_bad_asdf_version.asdf' (1/1) as 'ASDF' relative to context 'jwst_0591.pmap'
Setting 'META.EXPOSURE.TYPE [EXP_TYPE]' = None to value of 'META.EXPOSURE.P_EXPTYPE [P_EXPTYP]' = 'FGS_IMAGE|FGS_FOCUS|FGS_INTFLAT|FGS_SKYFLAT|'
File written with dev version of asdf library: 2.0.0.dev1213
Checking JWST datamodels.
########################################
0 errors
1 warnings"""
    else:
        expected_out = f""" Certifying '{jwst_data}/jwst_fgs_distortion_bad_asdf_version.asdf' (1/1) as 'ASDF' relative to context 'jwst_0591.pmap'
tag:stsci.edu:asdf/core/asdf-1.0.0 is not recognized, converting to raw Python data structure
File written with dev version of asdf library: 2.0.0.dev1213
########################################
0 errors
4 warnings
5 infos"""
    for msg in expected_out.splitlines():
        if msg.strip() not in out:
            breakpoint()
        assert msg.strip() in out


@mark.jwst
@mark.certify
def test_fits_asdf_extension_fail(jwst_serverless_state, jwst_data, caplog):
    argv = f"crds.certify {jwst_data}/jwst_nirspec_ipc_with_asdf_extension.fits --comparison-context jwst_0591.pmap"
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(argv)()
        out = caplog.text

    expected_out = f"""Certifying '{jwst_data}/jwst_nirspec_ipc_with_asdf_extension.fits' (1/1) as 'FITS' relative to context 'jwst_0591.pmap'
instrument='NIRSPEC' type='IPC' data='{jwst_data}/jwst_nirspec_ipc_with_asdf_extension.fits' ::  FITS files must not include an ASDF extension
FITS file 'jwst_nirspec_ipc_with_asdf_extension.fits' conforms to FITS standards.
Checking JWST datamodels.
########################################
1 errors"""
    for msg in expected_out.splitlines():
        assert msg.strip() in out

# ==================================================================================


@mark.jwst
@mark.certify
def test_validator_bad_presence():
    tinfo = generic_tpn.TpnInfo('DETECTOR','H','C','Q', ('WFC','HRC','SBC'))
    try:
        validators.validator(tinfo)
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_validator_bad_keytype():
    tinfo = generic_tpn.TpnInfo('DETECTOR','Q','C','R', ('WFC','HRC','SBC'))
    try:
        validators.validator(tinfo)
    except ValueError:
        assert True


@mark.hst
@mark.certify
def test_character_validator_file_good(hst_data):
    tinfo = generic_tpn.TpnInfo('DETECTOR','H','C','R', ('WFC','HRC','SBC'))
    cval = validators.validator(tinfo)
    assert isinstance(cval, validators.core.CharacterValidator)
    header = {"DETECTOR": "HRC"}
    cval.check(f'{hst_data}/acs_new_idc.fits', header)


@mark.multimission
@mark.certify
def test_character_validator_bad():
    tinfo = generic_tpn.TpnInfo('DETECTOR','H','C','R', ('WFC','HRC','SBC'))
    cval = validators.validator(tinfo)
    assert isinstance(cval, validators.core.CharacterValidator)
    header = {"DETECTOR" : "WFD" }
    try:
        cval.check("foo.fits", header)
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_character_validator_missing_required():
    tinfo = generic_tpn.TpnInfo('DETECTOR','H','C','R', ('WFC','HRC','SBC'))
    cval = validators.validator(tinfo)
    assert isinstance(cval, validators.core.CharacterValidator)
    header = {"DETECTOR" : "WFD" }
    try:
        cval.check("foo.fits", header)
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_character_validator_optional_bad():
    tinfo = generic_tpn.TpnInfo('DETECTOR','H','C','O', ('WFC','HRC','SBC'))
    cval = validators.validator(tinfo)
    assert isinstance(cval, validators.core.CharacterValidator)
    header = {"DETECTOR" : "WFD" }
    try:
        cval.check("foo.fits", header)
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_character_validator_optional_missing():
    tinfo = generic_tpn.TpnInfo('DETECTOR','H','C','O', ('WFC','HRC','SBC'))
    cval = validators.validator(tinfo)
    assert isinstance(cval, validators.core.CharacterValidator)
    header = {"DETECTR" : "WFC" }
    try:
        cval.check("foo.fits", header)
    except ValueError:
        assert True

# ------------------------------------------------------------------------------

@mark.multimission
@mark.certify
def test_logical_validator_good():
    tinfo = generic_tpn.TpnInfo('ROKIN','H','L','R',())
    cval = validators.validator(tinfo)
    assert isinstance(cval, validators.core.LogicalValidator)
    header= {"ROKIN": "F"}
    cval.check("foo.fits", header)
    header= {"ROKIN": "T"}
    cval.check("foo.fits", header)


@mark.multimission
@mark.certify
def test_logical_validator_bad():
    tinfo = generic_tpn.TpnInfo('ROKIN','H','L','R',())
    cval = validators.validator(tinfo)
    assert isinstance(cval, validators.core.LogicalValidator)
    headers = [
        {"ROKIN" : "True"},
        {"ROKIN" : "False"},
        {"ROKIN" : "1"},
        {"ROKIN" : "0"},
    ]
    for header in headers:
        try:
            cval.check("foo.fits", header)
        except ValueError:
            assert True

# ------------------------------------------------------------------------------

@mark.multimission
@mark.certify
def test_integer_validator_bad_format():
    info1 = generic_tpn.TpnInfo('READPATT', 'H', 'I', 'R', ('FOO',))
    info2 = generic_tpn.TpnInfo('READPATT', 'H', 'I', 'R', ('1.0','2.0'))
    for info in [info1, info2]:
        try:
            validators.validator(info)
        except ValueError:
            assert True


@mark.multimission
@mark.certify
def test_integer_validator_bad_float():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'I', 'R', ('1','2'))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.IntValidator)
    header = {"READPATT": "1.9"}
    try:
        cval.check("foo.fits", header)
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_integer_validator_bad_value():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'I', 'R', ('1','2','3'))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.IntValidator)
    header = {"READPATT": "4"}
    try:
        cval.check("foo.fits", header)
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_integer_validator_good():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'I', 'R', ('1','2','3'))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.IntValidator)
    header = {"READPATT": "2"}
    cval.check("foo.fits", header)


@mark.multimission
@mark.certify
def test_integer_validator_range_good():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'I', 'R', ("1:40",))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.IntValidator)
    header = {"READPATT": "39"}
    cval.check("foo.fits", header)


@mark.multimission
@mark.certify
def test_integer_validator_range_bad():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'I', 'R', ("1:40",))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.IntValidator)
    header = {"READPATT": "41"}
    try:
        cval.check("foo.fits", header)
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_integer_validator_range_boundary_good():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'I', 'R', ("1:40",))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.IntValidator)
    header = {"READPATT": "40"}
    cval.check("foo.fits", header)


@mark.multimission
@mark.certify
def test_integer_validator_range_format_bad():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'I', 'R', ("1:40",))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.IntValidator)
    header = {"READPATT": "40.3"}
    try:
        cval.check("foo.fits", header)
    except ValueError:
        assert True
        info = generic_tpn.TpnInfo('READPATT', 'H', 'I', 'R', ("x:40",))
    try:
        validators.validator(info)
    except ValueError:
        assert True

# ------------------------------------------------------------------------------

@mark.multimission
@mark.certify
def test_real_validator_bad_format():
    info1 = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ('FOO',))
    info2 = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ('x.0','2.0'))
    for info in [info1, info2]:
        try:
            validators.validator(info)
        except ValueError:
            assert True


@mark.multimission
@mark.certify
def test_real_validator_bad_value():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ('1.1','2.2','3.3'))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.RealValidator)
    header = {"READPATT": "3.2"}
    try:
        cval.check("foo.fits", header)
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_real_validator_good():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ('1.0','2.1','3.0'))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.RealValidator)
    header = {"READPATT": "2.1"}
    cval.check("foo.fits", header)


@mark.multimission
@mark.certify
def test_real_validator_range_good():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ("1.5:40.2",))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.RealValidator)
    header = {"READPATT": "40.1"}
    cval.check("foo.fits", header)


@mark.multimission
@mark.certify
def test_real_validator_range_bad():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ("1.5:40.2",))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.RealValidator)
    header = {"READPATT": "40.21"}
    try:
        cval.check("foo.fits", header)
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_real_validator_range_boundary_good():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ("1.4:40.1",))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.RealValidator)
    header = {"READPATT": "40.1"}
    cval.check("foo.fits", header)


@mark.multimission
@mark.certify
def test_real_validator_range_format_bad():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ("1.5:40.2",))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.RealValidator)
    header = {"READPATT": "40.x"}
    try:
        cval.check("foo.fits", header)
    except ValueError:
        assert True
        info = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ("1.x:40.2",))
    try:
        validators.validator(info)
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_real_validator_float_zero():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ('1','0.0'))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.RealValidator)
    header = {"READPATT": "0.0001"}
    try:
        cval.check("foo.fits", header)
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_real_validator_float_zero_zero():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ('1','0.0'))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.RealValidator)
    header = {"READPATT": "0.0003"}
    try:
        cval.check("foo.fits", header)
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_real_validator_range_inf_good():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ("5.5:inf",))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.RealValidator)
    header = {"READPATT": "100000.0"}
    cval.check("foo.fits", header)


@mark.multimission
@mark.certify
def test_real_validator_range_inf_bad():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'R', 'R', ("5.5:inf",))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.RealValidator)
    header = {"READPATT": "5.4"}
    try:
        cval.check("foo.fits", header)
    except ValueError:
        assert True

# ------------------------------------------------------------------------------

@mark.multimission
@mark.certify
def test_double_validator_bad_format():
    info1 = generic_tpn.TpnInfo('READPATT', 'H', 'D', 'R', ('FOO',))
    info2 = generic_tpn.TpnInfo('READPATT', 'H', 'D', 'R', ('x.0','2.0'))
    for info in [info1, info2]:
        try:
            validators.validator(info)
        except ValueError:
            assert True


@mark.multimission
@mark.certify
def test_double_validator_bad_value():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'D', 'R', ('1.1','2.2','3.3'))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.DoubleValidator)
    header = {"READPATT": "3.2"}
    try:
        cval.check("foo.fits", header)
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_double_validator_good():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'D', 'R', ('1.0','2.1','3.0'))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.DoubleValidator)
    header = {"READPATT": "2.1"}
    try:
        cval.check("foo.fits", header)
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_double_validator_range_good():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'D', 'R', ("1.5:40.2",))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.DoubleValidator)
    header = {"READPATT": "40.1"}
    try:
        cval.check("foo.fits", header)
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_double_validator_range_bad():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'D', 'R', ("1.5:40.2",))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.DoubleValidator)
    header = {"READPATT": "40.21"}
    try:
        cval.check("foo.fits", header)
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_double_validator_range_boundary_good():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'D', 'R', ("1.4:40.1",))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.DoubleValidator)
    header = {"READPATT": "40.1"}
    cval.check("foo.fits", header)


@mark.multimission
@mark.certify
def test_double_validator_range_format_bad():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'D', 'R', ("1.5:40.2",))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.DoubleValidator)
    header = {"READPATT": "40.x"}
    try:
        cval.check("foo.fits", header)
    except ValueError:
        assert True
        info = generic_tpn.TpnInfo('READPATT', 'H', 'D', 'R', ("1.x:40.2",))
    try:
        validators.validator(info)
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_double_validator_range_inf_good():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'D', 'R', ("5.5:inf",))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.DoubleValidator)
    header = {"READPATT": "100000.0"}
    cval.check("foo.fits", header)


@mark.multimission
@mark.certify
def test_double_validator_range_inf_bad():
    info = generic_tpn.TpnInfo('READPATT', 'H', 'D', 'R', ("5.5:inf",))
    cval = validators.validator(info)
    assert isinstance(cval, validators.core.DoubleValidator)
    header = {"READPATT": "5.4"}
    try:
        cval.check("foo.fits", header)
    except ValueError:
        assert True

# ------------------------------------------------------------------------------

@mark.multimission
@mark.certify
def test_expression_validator_passes():
    tinfo = generic_tpn.TpnInfo('DETECTOR','X','X','R', ('((DETECTOR==\'FOO\')and(SUBARRAY==\'BAR\'))',))
    cval = validators.validator(tinfo)
    assert isinstance(cval, validators.core.ExpressionValidator)
    header = { "DETECTOR":"FOO", "SUBARRAY":"BAR" }
    cval.check("foo.fits", header)


@mark.multimission
@mark.certify
def test_expression_validator_fails():
    tinfo = generic_tpn.TpnInfo('DETECTOR','X','X','R', ('((DETECTOR=="FOO")and(SUBARRAY=="BAR"))',))
    cval = validators.validator(tinfo)
    assert isinstance(cval, validators.core.ExpressionValidator)
    header = { "DETECTOR":"FOO", "SUBARRAY":"BA" }
    try:
        cval.check("foo.fits", header)
    except validators.core.RequiredConditionError:
        assert True


@mark.multimission
@mark.certify
def test_expression_validator_bad_format():
    # typical subtle expression error, "=" vs. "=="
    tinfo = generic_tpn.TpnInfo('DETECTOR','X','X','R', ('((DETECTOR="FOO")and(SUBARRAY=="BAR"))',))
    try:
        validators.validator(tinfo)
    except SyntaxError:
        assert True

# ------------------------------------------------------------------------------

@mark.hst
@mark.certify
def test_column_expression_validator_passes(hst_data):
    tinfo = generic_tpn.TpnInfo('DETCHIP', 'C', 'X', 'R', ('(VALUE%2==1)',))
    cval = validators.validator(tinfo)
    assert isinstance(cval, validators.core.ColumnExpressionValidator)
    cval.check(f'{hst_data}/acs_new_idc.fits', {})


@mark.hst
@mark.certify
def test_column_expression_validator_fails(hst_data):
    tinfo = generic_tpn.TpnInfo('DETCHIP', 'C', 'X', 'R', ('(VALUE%2==0)',))
    cval = validators.validator(tinfo)
    try:
        cval.check(f'{hst_data}/acs_new_idc.fits', {})
    except exceptions.RequiredConditionError:
        assert True

@mark.hst
@mark.certify
def test_column_expression_validator_header_variable(hst_data):
    tinfo = generic_tpn.TpnInfo('DETCHIP', 'C', 'X', 'R', ('(DETECTOR=="FOO")',))
    cval = validators.validator(tinfo)
    header = { "DETECTOR": "FOO" }
    try:
        cval.check(f'{hst_data}/acs_new_idc.fits', header)
    except exceptions.RequiredConditionError:
        assert True

# ------------------------------------------------------------------------------

@mark.hst
@mark.certify
def test_synphot_graph_validator_passes(hst_data):
    tinfo = generic_tpn.TpnInfo('EXT1', 'D', 'X', 'R', ('&SYNPHOT_GRAPH',))
    cval = validators.validator(tinfo)
    assert isinstance(cval, validators.synphot.SynphotGraphValidator)
    val = cval.check(f'{hst_data}/hst_synphot_tmg_connected.fits', {}) 
    assert val is True


@mark.hst
@mark.certify
def test_synphot_graph_validator_fails(hst_data):
    tinfo = generic_tpn.TpnInfo('EXT1', 'D', 'X', 'R', ('&SYNPHOT_GRAPH',))
    cval = validators.validator(tinfo)
    val = cval.check(f'{hst_data}/hst_synphot_tmg_disconnected.fits', {}) 
    assert val is False

# ------------------------------------------------------------------------------

@mark.hst
@mark.certify
def test_synphot_lookup_validator_passes(hst_data):
    tinfo = generic_tpn.TpnInfo('EXT1', 'D', 'X', 'R', ('&SYNPHOT_LOOKUP',))
    cval = validators.validator(tinfo)
    assert isinstance(cval, validators.synphot.SynphotLookupValidator)
    val = cval.check(f'{hst_data}/hst_synphot_tmc_passes.fits', {})
    assert val is True


@mark.hst
@mark.certify
def test_synphot_lookup_validator_fails(hst_data):
    tinfo = generic_tpn.TpnInfo('EXT1', 'D', 'X', 'R', ('&SYNPHOT_LOOKUP',))
    cval = validators.validator(tinfo)
    val  = cval.check(f'{hst_data}/hst_synphot_tmc_bad_filename.fits', {})
    assert val is False

# ------------------------------------------------------------------------------

@mark.hst
@mark.certify
def test_synphot_throughput_validator_passes(hst_data):
    tinfo = generic_tpn.TpnInfo('EXT1', 'D', 'X', 'R', ('&SYNPHOT_THROUGHPUT',))
    cval = validators.validator(tinfo, context="hst_0787.pmap")
    assert isinstance(cval, validators.synphot.SynphotThroughputValidator)
    header = { "COMPNAME": "acs_f555w_hrc"}
    val = cval.check(f'{hst_data}/acs_f555w_hrc_007_syn.fits', header)
    assert val is True


@mark.hst
@mark.certify
def test_synphot_throughput_validator_fails(hst_data):
    tinfo = generic_tpn.TpnInfo('EXT1', 'D', 'X', 'R', ('&SYNPHOT_THROUGHPUT',))
    cval = validators.validator(tinfo, context="hst_0787.pmap")
    header = { "COMPNAME": "acs_f555w_hrc"}
    val = cval.check(f'{hst_data}/acs_f555w_hrc_006_syn.fits', header)
    assert val is False

# ------------------------------------------------------------------------------

@mark.hst
@mark.certify
def test_synphot_thermal_validator_passes(hst_data):
    tinfo = generic_tpn.TpnInfo('EXT1', 'D', 'X', 'R', ('&SYNPHOT_THERMAL',))
    cval = validators.validator(tinfo, context="hst_0787.pmap")
    assert isinstance(cval, validators.synphot.SynphotThermalValidator)
    header = { "COMPNAME": "wfc3_ir_g141_src"}
    val = cval.check(f'{hst_data}/wfc3_ir_g141_src_999_th.fits', header)
    assert val is True


@mark.hst
@mark.certify
def test_synphot_thermal_validator_fails(hst_data):
    tinfo = generic_tpn.TpnInfo('EXT1', 'D', 'X', 'R', ('&SYNPHOT_THERMAL',))
    cval = validators.validator(tinfo, context="hst_0787.pmap")
    header = { "COMPNAME": "wfc3_ir_g141_src"}
    val = cval.check(f'{hst_data}/wfc3_ir_g141_src_003_th.fits', header)
    assert val is False

# ------------------------------------------------------------------------------

@mark.multimission
@mark.certify
def test_conditionally_required_bad_format():
    # typical subtle expression error, "=" vs. "=="
    tinfo = generic_tpn.TpnInfo('DETECTOR','X', 'X', '(SUBARRAY="BAR")', ("FOO","BAR","BAZ"))
    try:
        validators.validator(tinfo)
    except SyntaxError:
        assert True

@mark.multimission
@mark.certify
def test_conditionally_required_good():
    # typical subtle expression error, "=" vs. "=="
    tinfo = generic_tpn.TpnInfo('DETECTOR','H', 'C', '(SUBARRAY=="BAR")', ("FOO","BAR","BAZ"))
    cval = validators.validator(tinfo)
    header = { "DETECTOR" : "FOO", "SUBARRAY":"BAR" }
    cval.check("foo.fits", header)


@mark.multimission
@mark.certify
def test_conditionally_required_bad():
    # typical subtle expression error, "=" vs. "=="
    tinfo = generic_tpn.TpnInfo('DETECTOR','H', 'C', '(SUBARRAY=="BAR")', ("FOO","BAR","BAZ"))
    checker = validators.validator(tinfo)
    header = { "DETECTOR" : "FRODO", "SUBARRAY":"BAR" }
    try:
        checker.check("foo.fits", header)
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_conditionally_not_required():
    # typical subtle expression error, "=" vs. "=="
    tinfo = generic_tpn.TpnInfo('DETECTOR','H', 'C', '(SUBARRAY=="BAR")', ("FOO","BAR","BAZ"))
    checker = validators.validator(tinfo)
    header = { "DETECTOR" : "FRODO", "SUBARRAY":"BAZ" }
    checker.check("foo.fits", header)


@mark.multimission
@mark.certify
def test_not_conditionally_required():
    # typical subtle expression error, "=" vs. "=="
    info = generic_tpn.TpnInfo('DETECTOR','H', 'C', 'R', ("FOO","BAR","BAZ"))
    checker = validators.validator(info)
    assert checker.conditionally_required is False


@mark.multimission
@mark.certify
def test_conditional_warning_true_present():
    info = generic_tpn.TpnInfo('PIXAR_SR', 'H', 'R', "(warning(not(('MRS')in(EXP_TYPE))))", ())
    checker = validators.validator(info)
    assert checker.conditionally_required is True
    header = {"EXP_TYPE":"MIR_LRS-FIXEDSLIT", "PIXAR_SR":"999.0"}
    assert checker.is_applicable(header) == 'W'
    checker.handle_missing(header)


@mark.multimission
@mark.certify
def test_conditional_warning_true_absent():
    info = generic_tpn.TpnInfo('PIXAR_SR', 'H', 'R', "(warning(not(('MRS')in(EXP_TYPE))))", ())
    checker = validators.validator(info)
    assert checker.conditionally_required is True
    header = {"EXP_TYPE":"MIR_LRS-FIXEDSLIT", "PIXAR_SR":"999.0"}
    assert checker.is_applicable(header) == 'W'
    checker.handle_missing(header)


@mark.multimission
@mark.certify
def test_conditional_warning_false_present():
    info = generic_tpn.TpnInfo('PIXAR_SR', 'H', 'R', "(warning(not(('MRS')in(EXP_TYPE))))", ())
    checker = validators.validator(info)
    assert checker.conditionally_required is True
    header = {"EXP_TYPE":"MIR_FLAT-MRS", "PIXAR_SR":"999.0"}
    assert checker.is_applicable(header) is False
    checker.handle_missing(header)


@mark.multimission
@mark.certify
def test_conditional_warning_false_absent():
    info = generic_tpn.TpnInfo('PIXAR_SR', 'H', 'R', "(warning(not(('MRS')in(EXP_TYPE))))", ())
    checker = validators.validator(info)
    assert checker.conditionally_required is True
    header = {"EXP_TYPE":"MIR_FLAT-MRS"}
    assert checker.is_applicable(header) is False
    checker.handle_missing(header)


@mark.multimission
@mark.certify
def test_conditional_optional_true_present():
    info = generic_tpn.TpnInfo('PIXAR_SR', 'H', 'R', "(optional(not(('MRS')in(EXP_TYPE))))", ())
    checker = validators.validator(info)
    assert checker.conditionally_required is True
    header = {"EXP_TYPE":"MIR_LRS-FIXEDSLIT", "PIXAR_SR":"999.0"}
    assert checker.is_applicable(header) == 'O'
    checker.handle_missing(header)


@mark.multimission
@mark.certify
def test_conditional_optional_true_absent():
    info = generic_tpn.TpnInfo('PIXAR_SR', 'H', 'R', "(optional(not(('MRS')in(EXP_TYPE))))", ())
    checker = validators.validator(info)
    assert checker.conditionally_required
    header = {"EXP_TYPE":"MIR_LRS-FIXEDSLIT"}
    assert checker.is_applicable(header) == 'O'
    checker.handle_missing(header)


@mark.multimission
@mark.certify
def test_conditional_optional_false_present():
    info = generic_tpn.TpnInfo('PIXAR_SR', 'H', 'R', "(optional(not(('MRS')in(EXP_TYPE))))", ())
    checker = validators.validator(info)
    assert checker.conditionally_required is True
    header = {"EXP_TYPE":"MIR_FLAT-MRS", "PIXAR_SR":"999.0"}
    assert checker.is_applicable(header) is False
    checker.handle_missing(header)


@mark.multimission
@mark.certify
def test_conditional_optional_false_absent():
    info = generic_tpn.TpnInfo('PIXAR_SR', 'H', 'R', "(optional(not(('MRS')in(EXP_TYPE))))", ())
    checker = validators.validator(info)
    assert checker.conditionally_required
    header = {"EXP_TYPE":"MIR_FLAT-MRS"}
    assert checker.is_applicable(header) is False
    checker.handle_missing(header)


@mark.multimission
@mark.certify
def test_tpn_bad_presence():
    try:
        generic_tpn.TpnInfo('DETECTOR','H', 'C', 'Q', ("FOO","BAR","BAZ"))
    except ValueError as exc:
        assert "presence" in str(exc), "Wrong exception for test_tpn_bad_presence"


@mark.multimission
@mark.certify
def test_tpn_bad_group_keytype():
    info = generic_tpn.TpnInfo('DETECTOR','G', 'C', 'R', ("FOO","BAR","BAZ"))
    checker = validators.validator(info)
    warns = log.warnings()
    checker.check("test.fits", {"DETECTOR":"FOO"})
    new_warns = log.warnings()
    assert new_warns - warns >= 1, "No warning issued for unsupported group .tpn constraint type."


@mark.multimission
@mark.certify
def test_tpn_repr():
    # typical subtle expression error, "=" vs. "=="
    info = generic_tpn.TpnInfo('DETECTOR','H', 'C', 'R', ("FOO","BAR","BAZ"))
    repr(validators.validator(info))


@mark.multimission
@mark.certify
def test_tpn_check_value_method_not_implemented():
    # typical subtle expression error, "=" vs. "=="
    info = generic_tpn.TpnInfo('DETECTOR','H', 'C', 'R', ("FOO","BAR","BAZ"))
    checker = validators.core.Validator(info)
    try:
        checker.check("test.fits", header={"DETECTOR":"FOO"})
    except NotImplementedError:
        assert True


@mark.multimission
@mark.certify
def test_tpn_handle_missing():
    # typical subtle expression error, "=" vs. "=="
    info = generic_tpn.TpnInfo('DETECTOR','H', 'C', 'W', ("FOO","BAR","BAZ"))
    checker = validators.validator(info)
    assert checker.handle_missing(header={"READPATT":"FOO"}) == "UNDEFINED"
    info = generic_tpn.TpnInfo('DETECTOR','H', 'C', 'S', ("FOO","BAR","BAZ"))
    checker = validators.validator(info)
    assert checker.handle_missing(header={"READPATT":"FOO"}) == "UNDEFINED"
    info = generic_tpn.TpnInfo('DETECTOR','H', 'C', 'F', ("FOO","BAR","BAZ"))
    checker = validators.validator(info)
    assert checker.handle_missing(header={"READPATT":"FOO"}) == "UNDEFINED"


@mark.multimission
@mark.certify
def test_tpn_handle_missing_conditional():
    # typical subtle expression error, "=" vs. "=="
    info = generic_tpn.TpnInfo('DETECTOR','H', 'C', "(READPATT=='FOO')", ("FOO","BAR","BAZ"))
    checker = validators.validator(info)
    try:
        checker.handle_missing(header={"READPATT":"FOO"})
    except exceptions.MissingKeywordError:
        assert True
        assert checker.handle_missing(header={"READPATT":"BAR"}) == "UNDEFINED"


@mark.hst
@mark.certify
def test_missing_column_validator(hst_data):
    info = generic_tpn.TpnInfo('FOO','C', 'C', 'R', ("X","Y","Z"))
    checker = validators.validator(info)
    try:
        checker.check(f"{hst_data}/v8q14451j_idc.fits", header={"DETECTOR":"IRRELEVANT"})
    except exceptions.MissingKeywordError:
        assert True


@mark.multimission
@mark.certify
def test_tpn_excluded_keyword():
    # typical subtle expression error, "=" vs. "=="
    info = generic_tpn.TpnInfo('DETECTOR','H', 'C', 'E', ())
    checker = validators.validator(info)
    try:
        checker.check(f"test.fits", {"DETECTOR":"SHOULDNT_DEFINE"})
    except exceptions.IllegalKeywordError:
        assert True


@mark.multimission
@mark.certify
def test_tpn_not_value():
    # typical subtle expression error, "=" vs. "=="
    info = generic_tpn.TpnInfo('SUBARRAY','H', 'C', 'R', ["NOT_GENERIC"])
    checker = validators.validator(info)
    try:
        checker.check("test.fits", {"SUBARRAY":"GENERIC"})
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_tpn_or_bar_value():
    # typical subtle expression error, "=" vs. "=="
    info = generic_tpn.TpnInfo('DETECTOR','H', 'C', 'R', ["THIS","THAT","OTHER"])
    checker = validators.validator(info)
    checker.check("test.fits", {"DETECTOR":"THAT|THIS"})

    info = generic_tpn.TpnInfo('DETECTOR','H', 'C', 'R', ["THAT","OTHER"])
    checker = validators.validator(info)
    try:
        checker.check("test.fits", {"DETECTOR":"THAT|THIS"})
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_tpn_esoteric_value():
    # typical subtle expression error, "=" vs. "=="
    info = generic_tpn.TpnInfo('DETECTOR','H', 'C', 'R', ["([abc]+)","BETWEEN_300_400","#OTHER#"])
    checker = validators.validator(info)
    checker.check("test.fits", {"DETECTOR":"([abc]+)"})
    try:
        checker.check("test.fits", {"DETECTOR": "([def]+)"})
    except ValueError:
        assert True

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


@mark.multimission
@mark.certify
def test_tpn_pedigree_missing():
    info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
    checker = validators.validator(info)
    try:
        checker.check("test.fits", {"DETECTOR":"This is a test"})
    except exceptions.MissingKeywordError:
        assert True


@mark.multimission
@mark.certify
def test_tpn_pedigree_dummy():
    info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
    checker = validators.validator(info)
    checker.check("test.fits", {"PEDIGREE":"DUMMY"})


@mark.multimission
@mark.certify
def test_tpn_pedigree_ground():
    info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
    checker = validators.validator(info)
    checker.check("test.fits", {"PEDIGREE":"GROUND"})


@mark.multimission
@mark.certify
def test_tpn_pedigree_simulation():
    info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
    checker = validators.validator(info)
    checker.check("test.fits", {"PEDIGREE":"SIMULATION"})


@mark.multimission
@mark.certify
def test_tpn_pedigree_bad_leading():
    info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
    checker = validators.validator(info)
    try:
        checker.check("test.fits", {"PEDIGREE":"xDUMMY"})
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_tpn_pedigree_bad_trailing():
    # typical subtle expression error, "=" vs. "=="
    info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
    checker = validators.validator(info)
    try:
        checker.check("test.fits", {"PEDIGREE":"DUMMYxyz"})
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_tpn_pedigree_inflight_no_date():
    info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
    checker = validators.validator(info)
    try:
        checker.check("test.fits", {"PEDIGREE":"INFLIGHT"})
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_tpn_pedigree_equal_start_stop():
    info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
    checker = validators.validator(info)
    checker.check("test.fits", {"PEDIGREE":"INFLIGHT 02/01/2017 02/01/2017"})


@mark.multimission
@mark.certify
def test_tpn_pedigree_bad_datetime_order():
    info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
    checker = validators.validator(info)
    try:
        checker.check("test.fits", {"PEDIGREE":"INFLIGHT 2017-01-02 2017-01-01"})
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_tpn_pedigree_good_datetime_slash():
    info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
    checker = validators.validator(info)
    checker.check("test.fits", {"PEDIGREE":"INFLIGHT 02/01/2017 03/01/2017"})


@mark.multimission
@mark.certify
def test_tpn_pedigree_bad_datetime_slash():
    info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
    checker = validators.validator(info)
    try:
        checker.check("test.fits", {"PEDIGREE":"INFLIGHT 02/25/2017 03/01/2017"})
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_tpn_pedigree_good_datetime_dash():
    info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
    checker = validators.validator(info)
    checker.check("test.fits", {"PEDIGREE":"INFLIGHT 2017-01-01 2017-01-02"})


@mark.multimission
@mark.certify
def test_tpn_pedigree_bad_datetime_dash():
    info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
    checker = validators.validator(info)
    try:
        checker.check("test.fits",  {"PEDIGREE":"INFLIGHT 2017-01-01 01-02-2017"})
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_tpn_pedigree_bad_datetime_dash_dash():
    info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
    checker = validators.validator(info)
    try:
        checker.check("test.fits",  {"PEDIGREE":"INFLIGHT 2017-01-01 - 2017-01-02"})
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_tpn_pedigree_bad_datetime_format_1():
    info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
    checker = validators.validator(info)
    try:
        checker.check("test.fits", {"PEDIGREE":"INFLIGHT 2017-01-01 - 2017-01-02 -"})
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_tpn_pedigree_bad_datetime_format_2():
    info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
    checker = validators.validator(info)
    try:
        checker.check("test.fits", {"PEDIGREE":"INFLIGHT 2017-01-01 - 2017/01/02"})
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_tpn_pedigree_bad_datetime_format_3():
    info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&PEDIGREE"])
    checker = validators.validator(info)
    try:
        checker.check("test.fits",  {"PEDIGREE":"INFLIGHT 2017-01-01T00:00:00 2017-01-02"})
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_tpn_jwstpedigree_dashdate():
    info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&JWSTPEDIGREE"])
    checker = validators.validator(info)
    checker.check("test.fits", {"PEDIGREE":"INFLIGHT 2017-01-01 2017-01-02"})


@mark.multimission
@mark.certify
def test_tpn_jwstpedigree_ground_dates():
    info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&JWSTPEDIGREE"])
    checker = validators.validator(info)
    try:
        checker.check("test.fits",  {"PEDIGREE":"GROUND 2018-01-01 2018-01-25"})
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_tpn_jwstpedigree_nodate_format_3():
    info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&JWSTPEDIGREE"])
    checker = validators.validator(info)
    try:
        checker.check("test.fits",  {"PEDIGREE":"INFLIGHT"})
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_tpn_jwstpedigree_missing_format_3():
    info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&JWSTPEDIGREE"])
    checker = validators.validator(info)
    try:
        checker.check("test.fits",  {})
    except exceptions.MissingKeywordError:
        assert True


@mark.multimission
@mark.certify
def test_tpn_jwstpedigree_no_model_3():
    info = generic_tpn.TpnInfo('PEDIGREE','H', 'C', 'R', ["&JWSTPEDIGREE"])
    checker = validators.validator(info)
    try:
        checker.check("test.fits",  {"PEDIGREE":"MODEL"})
    except ValueError:
        assert True


@mark.hst
@mark.certify
def test_tpn_pedigree_missing_column(hst_data):
    info = generic_tpn.TpnInfo('PEDIGREE','C', 'C', 'R', ["&PEDIGREE"])
    checker = validators.validator(info)
    try:
        checker.check_column(f"{hst_data}/x2i1559gl_wcp.fits", {})
    except exceptions.MissingKeywordError:
        assert True


@mark.hst
@mark.certify
def test_tpn_pedigree_ok_column(hst_data):
    info = generic_tpn.TpnInfo('PEDIGREE','C', 'C', 'R', ["&PEDIGREE"])
    checker = validators.validator(info)
    header = data_file.get_header(f"{hst_data}/16j16005o_apd.fits")
    checker.check_column(f"{hst_data}/16j16005o_apd.fits", header)

# ------------------------------------------------------------------------------

@mark.hst
@mark.certify
def test_sybdate_validator(hst_data):
    tinfo = generic_tpn.TpnInfo('USEAFTER','H','C','R',('&SYBDATE',))
    cval = validators.validator(tinfo)
    assert isinstance(cval,validators.core.SybdateValidator)
    header = data_file.get_header(f"{hst_data}/acs_new_idc.fits")
    cval.check(f'{hst_data}/acs_new_idc.fits', header)


@mark.multimission
@mark.certify
def test_slashdate_validator():
    tinfo = generic_tpn.TpnInfo('USEAFTER','H','C','R',('&SLASHDATE',))
    checker = validators.validator(tinfo)
    checker.check("test.fits", {"USEAFTER":"25/12/2016"})
    try:
        checker.check("test.fits",  {"USEAFTER":"2017-12-25"})
    except ValueError:
        assert True


@mark.multimission
@mark.certify
def test_Anydate_validator():
    tinfo = generic_tpn.TpnInfo('USEAFTER','H','C','R',('&ANYDATE',))
    checker = validators.validator(tinfo)
    checker.check("test.fits", {"USEAFTER":"25/12/2016"})
    checker.check("test.fits", {"USEAFTER":"Mar 21 2001 12:00:00 am"})
    useafters = [
        {"USEAFTER":"2017-01-01T00:00:00.000"},
        {"USEAFTER":"12-25-2017"},
        {"USEAFTER":"Mxx 21 2001 01:00:00 PM"},
        {"USEAFTER":"35/12/20117"},
    ]
    for useafter in useafters:
        try:
            checker.check("test.fits", useafter)
        except ValueError:
            assert True

# ------------------------------------------------------------------------------

@mark.multimission
def certify_files(*args, **keys):
    keys = dict(keys)
    keys["check_rmap"] = True
    return certify.certify_files(*args, **keys)


@mark.hst
@mark.certify
def test_certify_rmap_missing_parkey(hst_data):
    certify_files([f"{hst_data}/hst_missing_parkey.rmap"], "hst.pmap", observatory="hst")


@mark.hst
@mark.certify
def test_certify_no_corresponding_rmap(hst_data):
    certify_files([f"{hst_data}/acs_new_idc.fits"], "hst.pmap", observatory="hst")


@mark.hst
@mark.certify
def test_certify_missing_provenance(hst_data):
    certify_files([f"{hst_data}/acs_new_idc.fits"], "hst.pmap", observatory="hst", dump_provenance=True)

# ------------------------------------------------------------------------------

@mark.hst
@mark.certify
def test_check_ambiguous_match(hst_data):
    try:
        certify.certify_file(f"{hst_data}/hst_acs_darkfile_ewsc.rmap", "hst.pmap", observatory="hst")
    except exceptions.AmbiguousMatchError:
        assert True 


@mark.hst
@mark.certify
def test_check_dduplicates(hst_data):
    certify_files([f"{hst_data}/hst.pmap"], "hst.pmap", observatory="hst")
    certify_files([f"{hst_data}/hst_acs.imap"], "hst.pmap", observatory="hst")
    certify_files([f"{hst_data}/hst_acs_darkfile.rmap"], "hst.pmap", observatory="hst")


@mark.hst
@mark.certify
def test_check_dup_selector_entry(hst_data):
    """Should return:
    CRDS - ERROR -  Duplicate entry at selector Match(('FUV',)) '1996-10-01 00:00:00' = 's7g1700gl_dead_dup2.fits' vs. 's7g1700gl_dead_dup1.fits'
    This is a step within certify that raises other errors, so this approach is to isolate the dup entry error.
    """
    parsing = mapping_parser.parse_mapping(f"{hst_data}/hst_cos_dup.rmap")
    mapping_parser.check_duplicates(parsing)


@mark.hst
@mark.certify
def test_check_comment(hst_data):
    certify_files([f"{hst_data}/hst.pmap"], "hst.pmap", observatory="hst")
    certify_files([f"{hst_data}/hst_acs.imap"], "hst.pmap", observatory="hst")
    certify_files([f"{hst_data}/hst_acs_darkfile_comment.rmap"], "hst.pmap", observatory="hst")


@mark.hst
@mark.certify
def test_table_mode_checks_identical(hst_data):
    certify_files([f"{hst_data}/v8q14451j_idc.fits"], "hst.pmap", observatory="hst",
                            compare_old_reference=True)


@mark.hst
@mark.certify
def test_table_mode_checks_missing_modes(hst_data):
    certify_files([f"{hst_data}/v8q1445xx_idc.fits"], "hst.pmap", observatory="hst",
                            compare_old_reference=True)


@mark.hst
@mark.certify
def test_UnknownCertifier_missing(hst_data):
    # log.set_exception_trap("test")
    try:
        certify.certify_file(f"{hst_data}/non-existent-file.txt", "jwst.pmap", observatory="jwst")
    except FileNotFoundError:
        assert True


@mark.hst
@mark.certify
def test_FitsCertify_bad_value(hst_data):
    try:
        certify.certify_file(f"{hst_data}/s7g1700gm_dead_broken.fits", "hst.pmap", observatory="hst")
    except ValueError:
        assert True

# ------------------------------------------------------------------------------

# def test_certify_deep_sync():
#     script = certify.CertifyScript(
#         "crds.certify --deep --comparison-context hst_0317.pmap zbn1927fl_gsag.fits --sync-files")
#     errors = script()
#     assert_true(errors == 0)

# def test_certify_sync_comparison_reference():
#     script = certify.CertifyScript(
#         "crds.certify --comparison-reference zbn1927fl_gsag.fits zbn1927fl_gsag.fits --sync-files")
#     script()

@mark.hst
@mark.certify
def test_certify_dont_recurse_mappings():
    script = certify.CertifyScript("crds.certify crds://hst_0317.pmap --dont-recurse-mappings")
    errors = script()


@mark.multimission
@mark.certify
def test_certify_kernel_unity_validator_good():
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


@mark.multimission
@mark.certify
def test_certify_kernel_unity_validator_bad():
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
    try:
        checker.check("test.fits", header)
    except exceptions.BadKernelSumError:
        assert True


@mark.jwst
@mark.certify
@mark.or_bars
def test_or_bars_certify_bad_keyword(jwst_serverless_state, jwst_data, caplog):
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(f"crds.certify {jwst_data}/jwst_miri_ipc.bad-keyword.fits --comparison-context jwst_0361.pmap")()
        out = caplog.text

    expected = f"""Certifying '{jwst_data}/jwst_miri_ipc.bad-keyword.fits' (1/1) as 'FITS' relative to context 'jwst_0361.pmap'
FITS file 'jwst_miri_ipc.bad-keyword.fits' conforms to FITS standards.
CRDS-pattern-like keyword 'P_DETEC' w/o CRDS translation to corresponding dataset keyword.
Pattern-like keyword 'P_DETEC' may be misspelled or missing its translation in CRDS.  Pattern will not be used.
The translation for 'P_DETEC' can be defined in crds.jwst.locate or rmap header reference_to_dataset field.
If this is not a pattern keyword, adding a translation to 'not-a-pattern' will suppress this warning.
Checking JWST datamodels.
0 errors""".splitlines()
    for line in expected:
        assert line in out


@mark.jwst
@mark.certify
@mark.or_bars
def test_or_bars_certify_bad_value(jwst_serverless_state, jwst_data, caplog):
    with caplog.at_level(logging.INFO, logger="CRDS"):
        CertifyScript(f"crds.certify {jwst_data}/jwst_miri_ipc.bad-value.fits --comparison-context jwst_0361.pmap")()
        out = caplog.text

    expected = f"""Certifying '{jwst_data}/jwst_miri_ipc.bad-value.fits' (1/1) as 'FITS' relative to context 'jwst_0361.pmap'
FITS file 'jwst_miri_ipc.bad-value.fits' conforms to FITS standards.
Setting 'META.INSTRUMENT.BAND [BAND]' = None to value of 'P_BAND' = 'LONG'
Setting 'META.INSTRUMENT.DETECTOR [DETECTOR]' = 'MIRIMAGE' to value of 'P_DETECT' = 'MIRIFUSHORT|FOO|'
instrument='MIRI' type='IPC' data='{jwst_data}/jwst_miri_ipc.bad-value.fits' ::  Checking 'META.INSTRUMENT.DETECTOR [DETECTOR]' : Value 'FOO' is not one of ['ANY', 'MIRIFULONG', 'MIRIFUSHORT', 'MIRIMAGE', 'N/A']
Checking JWST datamodels.
1 errors""".splitlines()
    for line in expected:
        assert line in out
