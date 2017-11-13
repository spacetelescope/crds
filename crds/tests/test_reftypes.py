from __future__ import division # confidence high
from __future__ import with_statement
from __future__ import print_function
from __future__ import absolute_import

# ==================================================================================

import os
import tempfile

# ==================================================================================
import numpy as np

from nose.tools import assert_raises, assert_true

# ==================================================================================

from crds.core import utils, log, exceptions
from crds.certify import reftypes
from crds import hst, jwst

from crds.tests import test_config

# ==================================================================================


def reftypes_load_type_spec_spec():
    """
    >>> old_state = test_config.setup()
    >>> SPEC_FILE = os.path.join(os.path.abspath(hst.HERE), "specs", "acs_biasfile.spec")
    >>> spec = reftypes.TypeSpec.from_file(SPEC_FILE)
    >>> test_config.cleanup(old_state)
    """

def reftypes_load_type_spec_rmap():
    """
    >>> old_state = test_config.setup()
    >>> SPEC_FILE = os.path.join(os.path.abspath(hst.HERE), "specs", "cos_xwlkfile.rmap")
    >>> spec = reftypes.TypeSpec.from_file(SPEC_FILE)
    >>> test_config.cleanup(old_state)
    """

def reftypes_hst_load_raw_specs():
    """
    >>> old_state = test_config.setup()
    >>> SPECS = os.path.join(os.path.abspath(hst.HERE), "specs")
    >>> spec = reftypes.load_raw_specs(SPECS)
    >>> test_config.cleanup(old_state)
    """
  
def reftypes_hst_save_json_specs():
    """
    >>> old_state = test_config.setup()
    >>> SPECS = os.path.join(os.path.abspath(hst.HERE), "specs")
    >>> specs = reftypes.load_raw_specs(SPECS)
    >>> f = tempfile.NamedTemporaryFile(delete=False)
    >>> f.close()
    >>> reftypes.save_json_specs(specs, f.name)  # doctest: +ELLIPSIS
    CRDS - INFO -  Saved combined type specs to '...'
    >>> test_config.cleanup(old_state)
    """
  
def reftypes_jwst_load_raw_specs():
    """
    >>> old_state = test_config.setup()
    >>> SPECS = os.path.join(os.path.abspath(jwst.HERE), "specs")
    >>> spec = reftypes.load_raw_specs(SPECS)
    >>> test_config.cleanup(old_state)
    """
  
def reftypes_jwst_save_json_specs():
    """
    >>> old_state = test_config.setup()
    >>> SPECS = os.path.join(os.path.abspath(jwst.HERE), "specs")
    >>> specs = reftypes.load_raw_specs(SPECS)
    >>> f = tempfile.NamedTemporaryFile(delete=False)
    >>> f.close()
    >>> reftypes.save_json_specs(specs, f.name) # doctest: +ELLIPSIS
    CRDS - INFO -  Saved combined type specs to '...'
    >>> test_config.cleanup(old_state)
    """
  
def reftypes_hst_reference_name_to_tpn_infos():
    """
    >>> old_state = test_config.setup()
    >>> types = reftypes.get_types_object("hst")
    >>> infos = types.reference_name_to_tpninfos("data/s7g1700gl_dead.fits")
    >>> print(log.PP(infos))
    [('DESCRIP', 'HEADER', 'CHARACTER', 'REQUIRED', values=()),
     ('DETECTOR', 'HEADER', 'CHARACTER', 'REQUIRED', values=('FUV', 'NUV')),
     ('FILETYPE', 'HEADER', 'CHARACTER', 'REQUIRED', values=('DEADTIME REFERENCE TABLE',)),
     ('INSTRUME', 'HEADER', 'CHARACTER', 'REQUIRED', values=('COS',)),
     ('PEDIGREE', 'HEADER', 'CHARACTER', 'REQUIRED', values=('&PEDIGREE',)),
     ('SEGMENT', 'COLUMN', 'CHARACTER', 'REQUIRED', values=('FUVA', 'FUVB', 'ANY')),
     ('USEAFTER', 'HEADER', 'CHARACTER', 'REQUIRED', values=('&SYBDATE',)),
     ('VCALCOS', 'HEADER', 'CHARACTER', 'REQUIRED', values=())]
    >>> test_config.cleanup(old_state)
    """

def reftypes_jwst_reference_name_to_tpn_infos():    # doctest: +ELLIPSIS
    """
    >>> old_state = test_config.setup()
    >>> types = reftypes.get_types_object("jwst")
    >>> infos = types.reference_name_to_tpninfos("data/jwst_miri_flat_slitlessprism.fits")
    >>> print(log.PP(infos))
    [('DETECTOR', 'HEADER', 'CHARACTER', 'OPTIONAL', values=()),
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'ANY_SUBARRAY', expression='(1<=META_SUBARRAY_XSTART+DQ_ARRAY.SHAPE[-1]-1<=1032)'),
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'ANY_SUBARRAY', expression='(1<=META_SUBARRAY_YSTART+DQ_ARRAY.SHAPE[-2]-1<=1024)'),
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'IF_FULL_FRAME', expression='(DQ_ARRAY.SHAPE[-2:]==(1024,1032))'),
    ...
     ('SUBARRAY_INBOUNDS_X', 'EXPRESSION', 'EXPRESSION', 'ANY_SUBARRAY', expression='(1<=META_SUBARRAY_XSTART+META_SUBARRAY_XSIZE-1<=1032)'),
     ('SUBARRAY_INBOUNDS_Y', 'EXPRESSION', 'EXPRESSION', 'ANY_SUBARRAY', expression='(1<=META_SUBARRAY_YSTART+META_SUBARRAY_YSIZE-1<=1024)')]
    >>> len(infos) >= 50
    True
    >>> test_config.cleanup(old_state)
    """

def reftypes_hst_get_filekinds():
    """
    >>> old_state = test_config.setup()
    >>> types = reftypes.get_types_object("hst")
    >>> types.get_filekinds("nicmos")
    ['backtab', 'darkfile', 'flatfile', 'idctab', 'illmfile', 'maskfile', 'nlinfile', 'noisfile', 'pedsbtab', 'phottab', 'pmodfile', 'pmskfile', 'rnlcortb', 'saacntab', 'saadfile', 'tdffile', 'tempfile', 'zprattab']
    >>> test_config.cleanup(old_state)
    """

def reftypes_jwst_get_filekinds():
    """
    >>> old_state = test_config.setup()
    >>> types = reftypes.get_types_object("jwst")
    >>> types.get_filekinds("niriss")
    ['all', 'amplifier', 'area', 'dark', 'distortion', 'drizpars', 'extract1d', 'flat', 'gain', 'ipc', 'linearity', 'mask', 'pathloss', 'persat', 'photom', 'readnoise', 'regions', 'saturation', 'specwcs', 'superbias', 'throughput', 'trapdensity', 'trappars', 'wavelengthrange', 'wcsregions']
    >>> test_config.cleanup(old_state)
    """
    
def reftypes_reference_name_to_tpn_text():
    """
    >>> old_state = test_config.setup()
    >>> types = reftypes.get_types_object("hst")
    >>> print(types.reference_name_to_tpn_text("data/s7g1700gl_dead.fits"))
    [('DESCRIP', 'HEADER', 'CHARACTER', 'REQUIRED', values=()),
     ('DETECTOR', 'HEADER', 'CHARACTER', 'REQUIRED', values=('FUV', 'NUV')),
     ('FILETYPE', 'HEADER', 'CHARACTER', 'REQUIRED', values=('DEADTIME REFERENCE TABLE',)),
     ('INSTRUME', 'HEADER', 'CHARACTER', 'REQUIRED', values=('COS',)),
     ('PEDIGREE', 'HEADER', 'CHARACTER', 'REQUIRED', values=('&PEDIGREE',)),
     ('SEGMENT', 'COLUMN', 'CHARACTER', 'REQUIRED', values=('FUVA', 'FUVB', 'ANY')),
     ('USEAFTER', 'HEADER', 'CHARACTER', 'REQUIRED', values=('&SYBDATE',)),
     ('VCALCOS', 'HEADER', 'CHARACTER', 'REQUIRED', values=())]
    >>> test_config.cleanup(old_state)
    """

def reftypes_reference_name_to_ld_tpn_text():
    """
    >>> old_state = test_config.setup()
    >>> types = reftypes.get_types_object("hst")
    >>> print(types.reference_name_to_tpn_text("data/s7g1700gl_dead.fits"))
    [('DESCRIP', 'HEADER', 'CHARACTER', 'REQUIRED', values=()),
     ('DETECTOR', 'HEADER', 'CHARACTER', 'REQUIRED', values=('FUV', 'NUV')),
     ('FILETYPE', 'HEADER', 'CHARACTER', 'REQUIRED', values=('DEADTIME REFERENCE TABLE',)),
     ('INSTRUME', 'HEADER', 'CHARACTER', 'REQUIRED', values=('COS',)),
     ('PEDIGREE', 'HEADER', 'CHARACTER', 'REQUIRED', values=('&PEDIGREE',)),
     ('SEGMENT', 'COLUMN', 'CHARACTER', 'REQUIRED', values=('FUVA', 'FUVB', 'ANY')),
     ('USEAFTER', 'HEADER', 'CHARACTER', 'REQUIRED', values=('&SYBDATE',)),
     ('VCALCOS', 'HEADER', 'CHARACTER', 'REQUIRED', values=())]
    >>> test_config.cleanup(old_state)
    """
    

def reftypes_get_row_keys_by_instrument():
    """
    >>> old_state = test_config.setup()
    >>> types = reftypes.get_types_object("hst")
    >>> types.get_row_keys_by_instrument("cos")
    ['aperture', 'cenwave', 'date', 'fpoffset', 'opt_elem', 'segment']
    >>> test_config.cleanup(old_state)
    """

# ==================================================================================

class TestReftypes(test_config.CRDSTestCase):

    def setUp(self, *args, **keys):
        super(TestReftypes, self).setUp(*args, **keys)
        self._old_debug = log.set_exception_trap(False)

    def tearDown(self, *args, **keys):
        super(TestReftypes, self).tearDown(*args, **keys)
        log.set_exception_trap(self._old_debug)
        
    # ------------------------------------------------------------------------------
        
    def test_validator_bad_presence(self):
        #         tinfo = certify.TpnInfo('DETECTOR','H','C','Q', ('WFC','HRC','SBC'))
        #         assert_raises(ValueError, certify.validator, tinfo)
        pass
    
# ==================================================================================

def main():
    """Run module tests,  for now just doctests only."""
    import unittest

    suite = unittest.TestLoader().loadTestsFromTestCase(TestReftypes)
    unittest.TextTestRunner().run(suite)

    from crds.tests import test_reftypes, tstmod
    return tstmod(test_reftypes)

if __name__ == "__main__":
    print(main())

