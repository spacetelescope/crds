from __future__ import division # confidence high
from __future__ import with_statement
from __future__ import print_function
from __future__ import absolute_import

# ==================================================================================

import os

from crds import certify, utils, log, client
from crds.certify import CertifyScript

from crds.tests import CRDSTestCase, test_config

from nose.tools import assert_raises, assert_true

# ==================================================================================

class TestCertifyScript(CertifyScript):
    """Subclass TestCertifyScript to better support doctesting..."""
    def __call__(self):
        try:
            old_config = test_config.setup()
            return super(TestCertifyScript, self).__call__()
        finally:
            test_config.cleanup(old_config)

def certify_truncated_file():
    """
    >>> TestCertifyScript("crds.certify data/truncated.fits --comparison-context hst.pmap")()
    CRDS  : WARNING  AstropyUserWarning : astropy.io.fits.file : File may have been truncated: actual file length (7000) is smaller than the expected size (8640)
    CRDS  : WARNING  AstropyUserWarning : astropy.io.fits.file : File may have been truncated: actual file length (7000) is smaller than the expected size (8640)
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying 'data/truncated.fits' (1/1) as 'FITS' relative to context 'hst.pmap'
    CRDS  : WARNING  AstropyUserWarning : astropy.io.fits.file : File may have been truncated: actual file length (7000) is smaller than the expected size (8640)
    CRDS  : INFO     FITS file 'truncated.fits' conforms to FITS standards.
    CRDS  : WARNING  AstropyUserWarning : astropy.io.fits.file : File may have been truncated: actual file length (7000) is smaller than the expected size (8640)
    CRDS  : WARNING  AstropyUserWarning : astropy.io.fits.file : File may have been truncated: actual file length (7000) is smaller than the expected size (8640)
    CRDS  : WARNING  AstropyUserWarning : astropy.io.fits.file : File may have been truncated: actual file length (7000) is smaller than the expected size (8640)
    CRDS  : WARNING  AstropyUserWarning : astropy.io.fits.file : File may have been truncated: actual file length (7000) is smaller than the expected size (8640)
    CRDS  : WARNING  AstropyUserWarning : astropy.io.fits.file : File may have been truncated: actual file length (7000) is smaller than the expected size (8640)
    CRDS  : WARNING  AstropyUserWarning : astropy.io.fits.file : File may have been truncated: actual file length (7000) is smaller than the expected size (8640)
    CRDS  : WARNING  AstropyUserWarning : astropy.io.fits.file : File may have been truncated: actual file length (7000) is smaller than the expected size (8640)
    CRDS  : WARNING  AstropyUserWarning : astropy.io.fits.file : File may have been truncated: actual file length (7000) is smaller than the expected size (8640)
    CRDS  : WARNING  AstropyUserWarning : astropy.io.fits.file : File may have been truncated: actual file length (7000) is smaller than the expected size (8640)
    CRDS  : WARNING  AstropyUserWarning : astropy.io.fits.file : File may have been truncated: actual file length (7000) is smaller than the expected size (8640)
    CRDS  : WARNING  AstropyUserWarning : astropy.io.fits.file : File may have been truncated: actual file length (7000) is smaller than the expected size (8640)
    CRDS  : WARNING  AstropyUserWarning : astropy.io.fits.file : File may have been truncated: actual file length (7000) is smaller than the expected size (8640)
    CRDS  : WARNING  AstropyUserWarning : astropy.io.fits.file : File may have been truncated: actual file length (7000) is smaller than the expected size (8640)
    CRDS  : INFO     ########################################
    CRDS  : INFO     0 errors
    CRDS  : INFO     16 warnings
    CRDS  : INFO     4 infos
    0
    """

def certify_dump_provenance_fits():
    """
    >>> TestCertifyScript("crds.certify data/s7g1700gl_dead.fits --dump-provenance --comparison-context hst.pmap")()
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying 'data/s7g1700gl_dead.fits' (1/1) as 'FITS' relative to context 'hst.pmap'
    CRDS  : INFO     FITS file 's7g1700gl_dead.fits' conforms to FITS standards.
    CRDS  : INFO     [0] COMMENT = 'Created by S. Beland and IDT and P. Hodge converted to user coord.' 
    CRDS  : INFO     [0] DESCRIP initial version 
    CRDS  : INFO     [0] DETECTOR FUV 
    CRDS  : INFO     [0] FILETYPE DEADTIME REFERENCE TABLE 
    CRDS  : INFO     [0] HISTORY   Modified to account for chamge of coordinates 
    CRDS  : INFO     [0] HISTORY fuv_080509_r_dead.fits renamed to s7g1700gl_dead.fits on Jul 16 2008 
    CRDS  : INFO     [0] INSTRUME COS 
    CRDS  : INFO     [0] PEDIGREE GROUND 16/07/2008 16/07/2010 
    CRDS  : INFO     [0] USEAFTER Oct 01 1996 00:00:00 
    CRDS  : INFO     [0] VCALCOS 2.0 
    CRDS  : INFO     DATE-OBS = '1996-10-01'
    CRDS  : INFO     TIME-OBS = '00:00:00'
    CRDS  : INFO     ########################################
    CRDS  : INFO     0 errors
    CRDS  : INFO     0 warnings
    CRDS  : INFO     16 infos
    0
    """

def certify_dump_provenance_generic():
    """
    >>> TestCertifyScript("crds.certify data/valid.json --dump-provenance --comparison-context jwst.pmap")()
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying 'data/valid.json' (1/1) as 'JSON' relative to context 'jwst.pmap'
    CRDS  : INFO     META.EXPOSURE.READPATT = 'any'
    CRDS  : INFO     META.INSTRUMENT.DETECTOR = 'mirifulong'
    CRDS  : INFO     META.INSTRUMENT.NAME = 'MIRI'
    CRDS  : INFO     META.OBSERVATION.DATE = '2015-01-25'
    CRDS  : INFO     META.REFFILE.AUTHOR = 'Todd Miller'
    CRDS  : INFO     META.REFFILE.DESCRIPTION = 'Brief notes on this reference.'
    CRDS  : INFO     META.REFFILE.HISTORY = 'How this reference came to be and changed over time.'
    CRDS  : INFO     META.REFFILE.PEDIGREE = 'dummy'
    CRDS  : INFO     META.REFFILE.USEAFTER = '2015-01-25T12:00:00'
    CRDS  : INFO     META.TELESCOPE = 'jwst'
    CRDS  : INFO     ########################################
    CRDS  : INFO     0 errors
    CRDS  : INFO     0 warnings
    CRDS  : INFO     13 infos
    0
    """

def certify_missing_keyword():
    """
    >>> TestCertifyScript("crds.certify data/missing_keyword.fits --comparison-context hst.pmap")()
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying 'data/missing_keyword.fits' (1/1) as 'FITS' relative to context 'hst.pmap'
    CRDS  : INFO     FITS file 'missing_keyword.fits' conforms to FITS standards.
    CRDS  : ERROR    instrument='COS' type='DEADTAB' data='data/missing_keyword.fits' ::  Checking 'DETECTOR' : Missing required keyword 'DETECTOR'
    CRDS  : INFO     ########################################
    CRDS  : INFO     1 errors
    CRDS  : INFO     0 warnings
    CRDS  : INFO     4 infos
    1
    """

def certify_recursive():
    """
    >>> TestCertifyScript("crds.certify hst_cos.imap --exist --dont-parse")()
    CRDS  : INFO     No comparison context specified or specified as 'none'.  No default context for all mappings or mixed types.
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying '/grp/crds/cache/mappings/hst/hst_cos.imap' (1/19) as 'MAPPING' relative to context None
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying '/grp/crds/cache/mappings/hst/hst_cos_badttab.rmap' (2/19) as 'MAPPING' relative to context None
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying '/grp/crds/cache/mappings/hst/hst_cos_bpixtab.rmap' (3/19) as 'MAPPING' relative to context None
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying '/grp/crds/cache/mappings/hst/hst_cos_brftab.rmap' (4/19) as 'MAPPING' relative to context None
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying '/grp/crds/cache/mappings/hst/hst_cos_brsttab.rmap' (5/19) as 'MAPPING' relative to context None
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying '/grp/crds/cache/mappings/hst/hst_cos_deadtab.rmap' (6/19) as 'MAPPING' relative to context None
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying '/grp/crds/cache/mappings/hst/hst_cos_disptab.rmap' (7/19) as 'MAPPING' relative to context None
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying '/grp/crds/cache/mappings/hst/hst_cos_flatfile.rmap' (8/19) as 'MAPPING' relative to context None
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying '/grp/crds/cache/mappings/hst/hst_cos_fluxtab.rmap' (9/19) as 'MAPPING' relative to context None
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying '/grp/crds/cache/mappings/hst/hst_cos_geofile.rmap' (10/19) as 'MAPPING' relative to context None
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying '/grp/crds/cache/mappings/hst/hst_cos_gsagtab.rmap' (11/19) as 'MAPPING' relative to context None
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying '/grp/crds/cache/mappings/hst/hst_cos_hvtab.rmap' (12/19) as 'MAPPING' relative to context None
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying '/grp/crds/cache/mappings/hst/hst_cos_lamptab.rmap' (13/19) as 'MAPPING' relative to context None
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying '/grp/crds/cache/mappings/hst/hst_cos_phatab.rmap' (14/19) as 'MAPPING' relative to context None
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying '/grp/crds/cache/mappings/hst/hst_cos_spwcstab.rmap' (15/19) as 'MAPPING' relative to context None
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying '/grp/crds/cache/mappings/hst/hst_cos_tdstab.rmap' (16/19) as 'MAPPING' relative to context None
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying '/grp/crds/cache/mappings/hst/hst_cos_walktab.rmap' (17/19) as 'MAPPING' relative to context None
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying '/grp/crds/cache/mappings/hst/hst_cos_wcptab.rmap' (18/19) as 'MAPPING' relative to context None
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying '/grp/crds/cache/mappings/hst/hst_cos_xtractab.rmap' (19/19) as 'MAPPING' relative to context None
    CRDS  : INFO     ########################################
    CRDS  : INFO     0 errors
    CRDS  : INFO     0 warnings
    CRDS  : INFO     40 infos
    0
    """

def certify_table_comparison_context():
    """
    >>> old_state = test_config.setup()

    >>> TestCertifyScript("crds.certify y951738kl_hv.fits --comparison-context hst_0294.pmap")()
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying '/grp/crds/cache/references/hst/y951738kl_hv.fits' (1/1) as 'FITS' relative to context 'hst_0294.pmap'
    CRDS  : INFO     FITS file 'y951738kl_hv.fits' conforms to FITS standards.
    CRDS  : INFO     Table unique row parameters defined as ('DATE',)
    CRDS  : INFO     Comparing reference 'y951738kl_hv.fits' against 'yas2005el_hv.fits'
    CRDS  : WARNING  Table mode (('DATE', 56923.583400000003),) from old reference 'yas2005el_hv.fits[1]' is NOT IN new reference 'y951738kl_hv.fits[1]'
    CRDS  : WARNING  Table mode (('DATE', 56923.625),) from old reference 'yas2005el_hv.fits[1]' is NOT IN new reference 'y951738kl_hv.fits[1]'
    CRDS  : WARNING  Table mode (('DATE', 56964.0),) from old reference 'yas2005el_hv.fits[1]' is NOT IN new reference 'y951738kl_hv.fits[1]'
    CRDS  : WARNING  Table mode (('DATE', 56921.833400000003),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS  : WARNING  Table mode (('DATE', 56922.0),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS  : WARNING  Table mode (('DATE', 56923.583400000003),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS  : WARNING  Table mode (('DATE', 56923.625),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS  : WARNING  Table mode (('DATE', 56924.041700000002),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS  : WARNING  Table mode (('DATE', 56924.208400000003),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS  : WARNING  Table mode (('DATE', 56924.3125),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS  : WARNING  Table mode (('DATE', 56925.0),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS  : WARNING  Table mode (('DATE', 56959.458400000003),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS  : WARNING  Table mode (('DATE', 56959.666700000002),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS  : WARNING  Table mode (('DATE', 56961.833400000003),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS  : WARNING  Table mode (('DATE', 56962.833400000003),) from old reference 'yas2005el_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS  : INFO     ########################################
    CRDS  : INFO     0 errors
    CRDS  : INFO     15 warnings
    CRDS  : INFO     6 infos
    0

    >>> test_config.cleanup(old_state)
    """

def certify_table_comparison_reference():
    """
    >>> TestCertifyScript("crds.certify data/y951738kl_hv.fits --comparison-reference data/y9j16159l_hv.fits")()
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying 'data/y951738kl_hv.fits' (1/1) as 'FITS' relative to context None and comparison reference 'data/y9j16159l_hv.fits'
    CRDS  : INFO     FITS file 'y951738kl_hv.fits' conforms to FITS standards.
    CRDS  : INFO     Table unique row parameters defined as ('DATE',)
    CRDS  : WARNING  Table mode (('DATE', 56923.583400000003),) from old reference 'y9j16159l_hv.fits[1]' is NOT IN new reference 'y951738kl_hv.fits[1]'
    CRDS  : WARNING  Table mode (('DATE', 56923.625),) from old reference 'y9j16159l_hv.fits[1]' is NOT IN new reference 'y951738kl_hv.fits[1]'
    CRDS  : WARNING  Duplicate definitions in old reference 'y9j16159l_hv.fits[2]' for mode: (('DATE', 56924.041700000002),) :
     (129, (('DATE', 56924.041700000002), ('HVLEVELB', 169)))
    (131, (('DATE', 56924.041700000002), ('HVLEVELB', 169)))
    CRDS  : WARNING  Duplicate definitions in old reference 'y9j16159l_hv.fits[2]' for mode: (('DATE', 56925.0),) :
     (132, (('DATE', 56925.0), ('HVLEVELB', 175)))
    (134, (('DATE', 56925.0), ('HVLEVELB', 175)))
    CRDS  : WARNING  Table mode (('DATE', 56921.833400000003),) from old reference 'y9j16159l_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS  : WARNING  Table mode (('DATE', 56922.0),) from old reference 'y9j16159l_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS  : WARNING  Table mode (('DATE', 56923.625),) from old reference 'y9j16159l_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS  : WARNING  Table mode (('DATE', 56924.041700000002),) from old reference 'y9j16159l_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS  : WARNING  Table mode (('DATE', 56924.3125),) from old reference 'y9j16159l_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS  : WARNING  Table mode (('DATE', 56925.0),) from old reference 'y9j16159l_hv.fits[2]' is NOT IN new reference 'y951738kl_hv.fits[2]'
    CRDS  : INFO     ########################################
    CRDS  : INFO     0 errors
    CRDS  : INFO     10 warnings
    CRDS  : INFO     5 infos
    0
    """

def certify_comparison_context_none_all_references():
    """
    >>> TestCertifyScript("crds.certify data/y951738kl_hv.fits --comparison-context None")()
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying 'data/y951738kl_hv.fits' (1/1) as 'FITS' relative to context None
    CRDS  : INFO     FITS file 'y951738kl_hv.fits' conforms to FITS standards.
    CRDS  : INFO     Table unique row parameters defined as ('DATE',)
    CRDS  : WARNING  No comparison reference for 'y951738kl_hv.fits' in context None. Skipping tables comparison.
    CRDS  : INFO     ########################################
    CRDS  : INFO     0 errors
    CRDS  : INFO     1 warnings
    CRDS  : INFO     5 infos
    0
    """

def certify_comparison_context_none_all_mappings():
    """
    >>> TestCertifyScript("crds.certify hst_cos_deadtab.rmap --comparison-context None")()
    CRDS  : INFO     No comparison context specified or specified as 'none'.  No default context for all mappings or mixed types.
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying '/grp/crds/cache/mappings/hst/hst_cos_deadtab.rmap' (1/1) as 'MAPPING' relative to context None
    CRDS  : INFO     ########################################
    CRDS  : INFO     0 errors
    CRDS  : INFO     0 warnings
    CRDS  : INFO     4 infos
    0
    """

def certify_jwst_valid():
    """
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying 'data/niriss_ref_photom.fits' (1/1) as 'FITS' relative to context None
    CRDS  : INFO     FITS file 'niriss_ref_photom.fits' conforms to FITS standards.
    CRDS  : WARNING  Non-compliant date format 'Jan 01 2015 00:00:00' for 'META.REFFILE.USEAFTER' should be 'YYYY-MM-DDTHH:MM:SS'
    CRDS  : INFO     ########################################
    CRDS  : INFO     0 errors
    CRDS  : INFO     1 warnings
    CRDS  : INFO     4 infos
    0
    """

def certify_jwst_invalid():
    """
    >>> TestCertifyScript("crds.certify data/niriss_ref_photom_bad.fits --comparison-context None")()
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying 'data/niriss_ref_photom_bad.fits' (1/1) as 'FITS' relative to context None
    CRDS  : INFO     FITS file 'niriss_ref_photom_bad.fits' conforms to FITS standards.
    CRDS  : ERROR    instrument='UNKNOWN' type='UNKNOWN' data='data/niriss_ref_photom_bad.fits' ::  Validation error : Error loading : JWST Data Model (jwst_lib.models) : 'FOO' is not valid in keyword 'DETECTOR'
    CRDS  : INFO     ########################################
    CRDS  : INFO     1 errors
    CRDS  : INFO     0 warnings
    CRDS  : INFO     4 infos
    1
    """

def certify_jwst_missing_optional_parkey():
    """
    >>> TestCertifyScript("crds.certify data/niriss_ref_photom_missing_parkey.fits --comparison-context jwst_0125.pmap")()
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying 'data/niriss_ref_photom_missing_parkey.fits' (1/1) as 'FITS' relative to context 'jwst_0125.pmap'
    CRDS  : ERROR    instrument='UNKNOWN' type='UNKNOWN' data='data/niriss_ref_photom_missing_parkey.fits' ::  Validation error : Error loading : [Errno 2] No such file or directory: 'data/niriss_ref_photom_missing_parkey.fits'
    CRDS  : INFO     ########################################
    CRDS  : INFO     1 errors
    CRDS  : INFO     0 warnings
    CRDS  : INFO     3 infos
    1
    """

# ==================================================================================

class TestHSTTpnInfoClass(CRDSTestCase):

    def setUp(self, *args, **keys):
        super(TestHSTTpnInfoClass, self).setUp(*args, **keys)
        hstlocator = utils.get_locator_module("hst")
        self.tpninfos = hstlocator.get_tpninfos('acs_idc.tpn')
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

class TestCertify(CRDSTestCase):

    def setUp(self, *args, **keys):
        super(TestCertify, self).setUp(*args, **keys)
        self._old_debug = log.set_exception_trap(False)

    def tearDown(self, *args, **keys):
        super(TestCertify, self).tearDown(*args, **keys)
        log.set_exception_trap(self._old_debug)
        
    def test_character_validator(self):
        """Test the constructor with default argument values."""
        tinfo = certify.TpnInfo('DETECTOR','H','C','R',('WFC','HRC','SBC'))
        cval = certify.validator(tinfo)
        assert_true(isinstance(cval, certify.CharacterValidator))
        cval.check(self.data('acs_new_idc.fits'))

    def test_sybdate_validator(self):
        tinfo = certify.TpnInfo('USEAFTER','H','C','R',('&SYBDATE',))
        cval = certify.validator(tinfo)
        assert_true(isinstance(cval,certify.SybdateValidator))
        cval.check(self.data('acs_new_idc.fits'))

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
        
    def test_loadall_type_constraints_hst(self):
        """Prove the HST constraint files are loadable."""
        from crds.hst import locate
        locate.load_all_type_constraints()

    def test_loadall_type_constraints_jwst(self):
        """Prove the JWST constraint files are loadable."""
        from crds.jwst import locate
        locate.load_all_type_constraints()

    def test_JsonCertify_valid(self):
        certify.certify_file(
            self.data("valid.json"), observatory="jwst",context="jwst.pmap", trap_exceptions=False)
            
    # still raises due to augment_exception but raises with standard InvalidFormatError
    def test_JsonCertify_invalid(self):
        assert_raises(certify.InvalidFormatError, certify.certify_file,  
            self.data("invalid.json"), observatory="jwst", context="jwst.pmap", trap_exceptions="test")
        
    def test_YamlCertify_valid(self):
        certify.certify_file(
            self.data("valid.yaml"), observatory="jwst", context="jwst.pmap", trap_exceptions=False)

    # still raises due to augment_exception but raises with standard InvalidFormatError            
    def test_YamlCertify_invalid(self):
        assert_raises(certify.InvalidFormatError, certify.certify_file,
            self.data("invalid.yaml"), observatory="jwst", context="jwst.pmap", trap_exceptions="test")

    def test_AsdfCertify_valid(self):
        certify.certify_file(
            self.data("valid.asdf"), observatory="jwst",context="jwst_0082.pmap", trap_exceptions=False)
            
    def test_AsdfCertify_invalid(self):
        assert_raises(certify.InvalidFormatError, certify.certify_file,
            self.data("invalid.asdf"), observatory="jwst",context="jwst.pmap", trap_exceptions="test")                  
        
    def test_UnknownCertifier_valid(self):
        certify.certify_file(
            self.data("valid.text"), observatory="jwst",context="jwst.pmap", trap_exceptions=False)
            
    def test_UnknownCertifier_missing(self):
        assert_raises(certify.InvalidFormatError, certify.certify_file, 
            self.data("non-existent-file.txt"), observatory="jwst", context="jwst.pmap", trap_exceptions="test")
        
    def test_FitsCertify_bad_value(self):
        assert_raises(ValueError, certify.certify_file,
            self.data("s7g1700gm_dead_broken.fits"), observatory="hst", context="hst.pmap", trap_exceptions=False)
        
    def test_FitsCertify_opaque_name(self):
        certify.certify_file(
            self.data("opaque_fts.tmp"), observatory="hst", context="hst.pmap",
            original_name="s7g1700gl_dead.fits", trap_exceptions=False)

    def test_AsdfCertify_opaque_name(self):
        certify.certify_file(self.data("opaque_asd.tmp"), observatory="jwst", context="jwst_0082.pmap", 
            original_name="valid.tmp", trap_exceptions=False)

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

