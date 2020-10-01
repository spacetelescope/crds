"""This module defines tests related to bootstrapping Roman and establishing
critical CRDS functions.   It is written to be executed relative to spiked/fake
specs, tpns, and content which are stored in the crds.roman package.
"""
import os
import doctest
from pprint import pprint as pp

# ==================================================================================
import numpy as np

from nose.tools import assert_raises, assert_true, assert_false

# ==================================================================================

import crds
from crds.core import utils, log, exceptions
from crds.tests import test_config

# ==================================================================================

def roman_certify_context():
    """
    >>> old_state = test_config.setup(url="https://roman-crds-serverless.stsci.edu", observatory="roman")

    -------------------------------- XXXXX Roman TODO ------------------------------

    The crds/roman/tpns/* files haven't truly been updated for roman,  more information
    is needed,  typically obtained from the romancal datamodels schema.

    --------------------------------------------------------------------------------

    >>> from crds.certify import CertifyScript

    >>> CertifyScript("crds.certify crds://roman_0001.pmap")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Certification includes mappings but is not --deep, no --comparison-context is defined.
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying '.../roman_0001.pmap' (1/3) as 'MAPPING' relative to context None
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying '.../roman_wfi_0001.imap' (2/3) as 'MAPPING' relative to context None
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying '.../roman_wfi_flat_0001.rmap' (3/3) as 'MAPPING' relative to context None
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  8 infos
    0

    >>> test_config.cleanup(old_state)
    """

def roman_certify_reference():
    """
    >>> old_state = test_config.setup(url="https://roman-crds-serverless.stsci.edu", observatory="roman")

    >>> from crds.certify import CertifyScript

    -------------------------------- XXXXX Roman TODO ---------------------------

    The initial results of this test illuminate 2 things: (1) CRDS' ASDF
    support doesn't currently handle array data so ASDF checks are limited to
    metadata, datamodels, and built-in ASDF checks.  (2) the current CRDS .tpn
    constraint files for WFI FLAT have FITS-based HDU array checks defined.

    Corresponding Roman update questions are: (1) should crds.io.asdf be
    enhanced to support the missing get_array_properties method?  (2) should
    JWST-like array checks be implemented for Roman or are there other more
    decoupled checks upstream such as ASDF or datamodels validation which
    achieve the same ends?

    -----------------------------------------------------------------------------

    >>> CertifyScript("crds.certify crds://roman_wfi_flat_0000.asdf")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Certifying only references,  defaulting --comparison-context to operational context.
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying '.../roman_wfi_flat_0000.asdf' (1/1) as 'ASDF' relative to context 'roman_0001.pmap'
    CRDS - INFO -  Checking Roman datamodels.
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  5 infos
    0

    >>> test_config.cleanup(old_state)

    """

def roman_refactor_insert():
    """
    >>> old_state = test_config.setup(url="https://roman-crds-serverless.stsci.edu", observatory="roman")

    >>> from crds.refactoring.refactor import RefactorScript
    >>> RefactorScript("crds.refactor insert crds://roman_wfi_flat_0001.rmap ./temp.rmap crds://roman_wfi_flat_0000.asdf")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Inserting roman_wfi_flat_0000.asdf into 'roman_wfi_flat_0000.rmap'
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  1 infos
    0

    >>> os.remove("temp.rmap")

    >>> test_config.cleanup(old_state)
    """

def roman_newcontext():
    """
    >>> old_state = test_config.setup(url="https://roman-crds-serverless.stsci.edu", observatory="roman")

    >>> from crds.refactoring.newcontext import NewContextScript

    >>> NewContextScript("crds.newcontext roman_0001.pmap  roman_wfi_flat_0001.rmap")()
    CRDS - INFO -  Replaced 'roman_wfi_flat_0001.rmap' with 'roman_wfi_flat_0001.rmap' for 'FLAT' in 'roman_wfi_0001.imap' producing './roman_wfi_0002.imap'
    CRDS - INFO -  Replaced 'roman_wfi_0001.imap' with './roman_wfi_0002.imap' for 'WFI' in 'roman_0001.pmap' producing './roman_0002.pmap'
    CRDS - INFO -  Adjusting name 'roman_0002.pmap' derived_from 'roman_0001.pmap' in './roman_0002.pmap'
    CRDS - INFO -  Adjusting name 'roman_wfi_0002.imap' derived_from 'roman_wfi_0001.imap' in './roman_wfi_0002.imap'
    0

    >>> os.remove("roman_0002.pmap")
    >>> os.remove("roman_wfi_0002.imap")

    >>> test_config.cleanup(old_state)

    """

def roman_reference_get_header():
    """
    >>> old_state = test_config.setup(url="https://roman-crds-serverless.stsci.edu", observatory="roman")

    >>> from crds import data_file
    >>> from crds import locate_file

    >>> where = locate_file("roman_wfi_flat_0000.asdf", "roman")  # in the cache...
    >>> header = data_file.get_header(where)
    >>> for key in header:
    ...     if key.startswith("META."):
    ...         print(key, "=", header[key])
    META.AUTHOR = Todd Miller / Sosey
    META.DATE = 2017-09-08T12:57:26.928
    META.DESCRIPTION = WFI Flat Frame
    META.EXP_TYPE = WFI_GRISM
    META.EXPOSURE.TYPE = WFI_GRISM
    META.FILENAME = WFI_mod1.asdf
    META.INPUT_UNITS = SUPRESSED_NONSTD_TYPE: 'PrefixUnit'
    META.INSTRUMENT.MODULE = 1
    META.INSTRUMENT.NAME = WFI
    META.INSTRUMENT.FILTER = MULTIPLE
    META.INSTRUMENT.PUPIL = CLEAR
    META.INSTRUMENT.DETECTOR = WFI-1
    META.MODEL_TYPE = WFIGrismModel
    META.OUTPUT_UNITS = SUPRESSED_NONSTD_TYPE: 'PrefixUnit'
    META.PEDIGREE = ground
    META.REFTYPE = flat
    META.TELESCOPE = Roman
    META.TITLE = WFI Flat (ASDF Standard 1.5.0)
    META.USEAFTER = 2014-01-01T00:00:00

    >>> test_config.cleanup(old_state)
    """

HEADER = {
    'META.INSTRUMENT.NAME' : 'WFI',
    'META.INSTRUMENT.DETECTOR' : 'WFI-1',
    'META.INSTRUMENT.FILTER' : 'MULTIPLE',
    'META.INSTRUMENT.PUPIL' : 'CLEAR',
    'META.OBSERVATION.DATE' : '2020-10-08',
    'META.OBSERVATION.TIME' : '14:00:00',
    }

def roman_bestrefs():
    """
    >>> old_state = test_config.setup(url="https://roman-crds-serverless.stsci.edu", observatory="roman")

    >>> crds.getreferences(HEADER, context="roman_0001.pmap", observatory="roman")    # doctest: +ELLIPSIS
    {'flat': '.../roman_wfi_flat_0000.asdf'}

    >>> test_config.cleanup(old_state)
    """

def roman_diffs():
    """
    >>> old_state = test_config.setup(url="https://roman-crds-serverless.stsci.edu", observatory="roman")

    >>> from crds.diff import DiffScript

    >>> DiffScript("crds.diff  -BFQ  crds://roman_0000.pmap   crds://roman_0001.pmap")()
    roman_wfi_flat_0000.rmap roman_wfi_flat_0001.rmap -- WFI-1 MULTIPLE CLEAR -- 2014-01-01 00:00:00 -- added Match rule for roman_wfi_flat_0000.asdf
    roman_wfi_0000.imap roman_wfi_0001.imap -- flat -- replaced roman_wfi_flat_0000.rmap with roman_wfi_flat_0001.rmap
    roman_0000.pmap roman_0001.pmap -- wfi -- replaced roman_wfi_0000.imap with roman_wfi_0001.imap
    roman_0000.pmap roman_0001.pmap -- header replaced 'description' = 'hand edited for roman baseline 2020-10-09.   prototype / fake sample only,  update for roman.' with 'hand edited for roman baseline.'
    1

    >>> test_config.cleanup(old_state)
    """

# ==================================================================================

# class TestRoman(test_config.CRDSTestCase):

#     def setUp(self, *args, **keys):
#         super(TestRoman, self).setUp(*args, **keys)
#         self._old_debug = log.set_exception_trap(False)

#     def tearDown(self, *args, **keys):
#         super(TestRoman, self).tearDown(*args, **keys)
#         log.set_exception_trap(self._old_debug)

#     # ------------------------------------------------------------------------------

#     def test_validator_bad_presence(self):
#         tinfo = generic_tpn.TpnInfo('DETECTOR','H','C','Q', ('WFC','HRC','SBC'))
#         assert_raises(ValueError, validators.validator, tinfo)
#         header = {"READPATT": "40"}
#         cval.check("foo.fits", header)


def main():
    """Run module tests,  for now just doctests only."""
    import unittest

    # suite = unittest.TestLoader().loadTestsFromTestCase(TestRoman)
    # unittest.TextTestRunner().run(suite)

    import test_roman
    from crds.tests import tstmod

    return tstmod(test_roman)

if __name__ == "__main__":
    print(main())
