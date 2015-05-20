from __future__ import division # confidence high
from __future__ import with_statement
from __future__ import print_function
from __future__ import absolute_import

# ==================================================================================

import os

from crds import certify, utils, log, client
from crds.certify import CertifyScript

from crds.tests import CRDSTestCase

from nose.tools import assert_raises, assert_true

# ==================================================================================

def certify_doctests():
    """
    >>> log.set_test_mode()

    >>> CertifyScript("crds.certify data/truncated.fits --comparison-context hst.pmap")()
    CRDS  : WARNING  AstropyUserWarning astropy.io.fits.file (302) File may have been truncated: actual file length (7000) is smaller than the expected size (8640)
    CRDS  : INFO     ########################################
    CRDS  : INFO     Certifying 'data/truncated.fits' (1/1) as 'FITS' relative to context 'hst.pmap'
    CRDS  : INFO     FITS file 'truncated.fits' conforms to FITS standards.
    CRDS  : INFO     ########################################
    CRDS  : INFO     0 errors
    CRDS  : INFO     1 warnings
    CRDS  : INFO     4 infos
    0

    >>> CertifyScript("crds.certify data/s7g1700gl_dead.fits --dump-provenance --comparison-context hst.pmap")()
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
    CRDS  : INFO     ########################################
    CRDS  : INFO     0 errors
    CRDS  : INFO     0 warnings
    CRDS  : INFO     14 infos
    0

    >>> CertifyScript("crds.certify data/missing_keyword.fits --comparison-context hst.pmap")()
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
            self.data("valid.asdf"), observatory="jwst",context="jwst.pmap", trap_exceptions=False)
            
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
        certify.certify_file(self.data("opaque_asd.tmp"), observatory="hst", context="hst.pmap", 
            original_name="valid.asdf", trap_exceptions=False)

# ==================================================================================

def main():
    """Run module tests,  for now just doctests only."""
    import unittest

    suite = unittest.TestLoader().loadTestsFromTestCase(TestHSTTpnInfoClass)
    unittest.TextTestRunner().run(suite)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestCertify)
    unittest.TextTestRunner().run(suite)

    import doctest
    from crds.tests import test_certify
    return doctest.testmod(test_certify)

if __name__ == "__main__":
    print(main())

