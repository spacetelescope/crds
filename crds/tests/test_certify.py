from __future__ import division # confidence high
from __future__ import with_statement

import os
import warnings

import numpy as np

import crds
from crds import certify, utils, log, certify

from crds.tests import CRDSTestCase
#from pyfits.tests.util import CaptureStdout, catch_warnings

from nose.tools import assert_equal, assert_raises, assert_true, assert_false

class TestHSTTpnInfoClass(CRDSTestCase):

    def setUp(self, *args, **keys):
        super(TestHSTTpnInfoClass, self).setUp(*args, **keys)
        hstlocator = utils.get_locator_module("hst")
        self.tpninfos = hstlocator.get_tpninfos('acs_idc.tpn')
        self.validators = [certify.validator(info) for info in self.tpninfos]
        os.environ['CRDS_SERVER_URL'] = 'https://crds-serverless-mode.stsci.edu'
        os.environ['CRDS_MAPPATH'] = self.hst_mappath
        os.environ['CRDS_PATH'] = "/grp/crds/hst"
        os.environ["CRDS_CONTEXT"] ="hst.pmap"

    def test_character_validator(self):
        assert self.validators[2].check(self.data('acs_new_idc.fits'))

    def test_column_validator(self):
        assert self.validators[-2].check(self.data('acs_new_idc.fits'))

class TestCertifyClasses(CRDSTestCase):

    def setUp(self, *args, **keys):
        super(TestCertifyClasses, self).setUp(*args, **keys)
        self._old_debug = log.set_debug(True)

    def tearDown(self, *args, **keys):
        super(TestCertifyClasses, self).tearDown(*args, **keys)
        log.set_debug(self._old_debug)
        
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

    def test_JsonCertifier_valid(self):
        cert = certify.JsonCertifier(self.data("valid.json"), 
                                     observatory="jwst",context="jwst.pmap")
        cert.certify()
            
    def test_JsonCertifier_invalid(self):
        cert = certify.JsonCertifier(self.data("invalid.json"),
                                     observatory="jwst",context="jwst.pmap")
        assert_raises(certify.InvalidFormatError, cert.certify)
        
    def test_YamlCertifier_valid(self):
        cert = certify.YamlCertifier(self.data("valid.yaml"), 
                                     observatory="jwst",context="jwst.pmap")
        cert.certify()
            
    def test_YamlCertifier_invalid(self):
        cert = certify.YamlCertifier(self.data("invalid.yaml"),
                                     observatory="jwst",context="jwst.pmap")
        assert_raises(certify.InvalidFormatError, cert.certify)
        
    def test_AsdfCertifier_valid(self):
        cert = certify.AsdfCertifier(self.data("valid.asdf"), 
                                     observatory="jwst",context="jwst.pmap")
        cert.certify()
            
    def test_AsdfCertifier_invalid(self):
        cert = certify.YamlCertifier(self.data("invalid.asdf"),
                                     observatory="jwst",context="jwst.pmap")
        assert_raises(certify.InvalidFormatError, cert.certify)
        
    def test_UnknownCertifier_valid(self):
        cert = certify.UnknownCertifier(self.data("valid.text"), 
                                     observatory="jwst",context="jwst.pmap")
        cert.certify()
            
    def test_UnknownCertifier_missing(self):
        cert = certify.UnknownCertifier(self.data("non-existent-file.txt"), 
                                     observatory="jwst",context="jwst.pmap")
        assert_raises(IOError, cert.certify)
        
    def test_FitsCertifier_bad_value(self):
        cert = certify.FitsCertifier(self.data("s7g1700gm_dead_broken.fits"), 
                                     observatory="hst",context="hst.pmap")
        assert_raises(ValueError, cert.certify)

