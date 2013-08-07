from __future__ import division # confidence high
from __future__ import with_statement

import os
import warnings

import numpy as np

import crds
from crds import certify, utils

from crds.tests import CRDSTestCase
#from pyfits.tests.util import CaptureStdout, catch_warnings

from nose.tools import assert_equal, assert_raises, assert_true, assert_false

class TestHSTTpninfoClass(CRDSTestCase):
    def setup(self):
        CRDSTestCase.setup(self)
        hstlocator = utils.get_locator_module("hst")
        self.tpninfos = hstlocator.get_tpninfos('acs_idc.tpn')
        self.validators = [certify.validator(info) for info in self.tpninfos]
        os.environ['CRDS_SERVER_URL'] = 'http://not-a-crds-server.stsci.edu'
        os.environ['CRDS_MAPPATH'] = self.hst_mappath
        os.environ['CRDS_PATH'] = "/grp/crds/hst"
        os.environ["CRDS_CONTEXT"] ="hst.pmap"

    def test_character_validator(self):
        assert self.validators[2].check(self.data('acs_new_idc.fits'))

    def test_column_validator(self):
        assert self.validators[-2].check(self.data('acs_new_idc.fits'))

    def test_mode_validator(self):
        """ Test that all modes in ref file match those from previously checked
            in reference file
        """
        mode_checker = None # Initialize mode validation
        for checker in self.validators:
            # Treat column validations together as a 'mode'
            if checker.info.keytype == 'C':
                checker.check(self.data('acs_new_idc.fits')) # validate values against TPN valid values
                if mode_checker is None:
                    mode_checker = certify.ModeValidator(checker.info)
                mode_checker.add_column(checker)
        mode_checker.check(self.data('acs_new_idc.fits'),context='hst.pmap')

class TestValidatorClasses(CRDSTestCase):
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
        from crds import certify
        certify.certify_files([self.data("hst.pmap")], trap_exceptions=False, observatory="hst")
        certify.certify_files([self.data("hst_acs.imap")], observatory="hst")
        certify.certify_files([self.data("hst_acs_darkfile.rmap")], observatory="hst")

def test():
    import doctest
    from . import test_certify
    return doctest.testmod(test_certify)

