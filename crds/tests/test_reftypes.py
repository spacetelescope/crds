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
     ('FILETYPE', 'HEADER', 'CHARACTER', 'REQUIRED', values=('"DEADTIME_REFERENCE_TABLE"',)),
     ('INSTRUME', 'HEADER', 'CHARACTER', 'REQUIRED', values=('COS',)),
     ('PEDIGREE', 'HEADER', 'CHARACTER', 'REQUIRED', values=('&PEDIGREE',)),
     ('SEGMENT', 'COLUMN', 'CHARACTER', 'REQUIRED', values=('FUVA', 'FUVB', 'ANY')),
     ('USEAFTER', 'HEADER', 'CHARACTER', 'REQUIRED', values=('&SYBDATE',)),
     ('VCALCOS', 'HEADER', 'CHARACTER', 'REQUIRED', values=())]
    >>> test_config.cleanup(old_state)
    """

def reftypes_jwst_reference_name_to_tpn_infos():
    """
    >>> old_state = test_config.setup()
    >>> types = reftypes.get_types_object("jwst")
    >>> infos = types.reference_name_to_tpninfos("data/jwst_miri_flat_slitlessprism.fits")
    >>> print(log.PP(infos))
    [('DETECTOR', 'HEADER', 'CHARACTER', 'OPTIONAL', values=()),
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'ANY_SUBARRAY', expression='(1<=META_SUBARRAY_XSTART+DQ_ARRAY.SHAPE[-1]-1<=1032)'),
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'ANY_SUBARRAY', expression='(1<=META_SUBARRAY_YSTART+DQ_ARRAY.SHAPE[-2]-1<=1024)'),
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'IF_FULL_FRAME', expression='(DQ_ARRAY.SHAPE[-2:]==(1024,1032))'),
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'REQUIRED', expression="(has_type(DQ_ARRAY,'INT'))"),
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'REQUIRED', expression='(is_image(DQ_ARRAY))'),
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'IF_SUBARRAY', expression='(DQ_ARRAY.SHAPE[-2:]==(META_SUBARRAY_YSIZE,META_SUBARRAY_XSIZE))'),
     ('DQ', 'ARRAY_DATA', 'EXPRESSION', 'REQUIRED', expression="(has_type(DQ_ARRAY,'INT'))"),
     ('DQ_DEF', 'ARRAY_DATA', 'EXPRESSION', condition='(DQ_ARRAY.DATA.sum())', expression="(has_column_type(DQ_DEF_ARRAY,'BIT','INT'))"),
     ('DQ_DEF', 'ARRAY_DATA', 'EXPRESSION', condition='(DQ_ARRAY.DATA.sum())', expression="(has_column_type(DQ_DEF_ARRAY,'DESCRIPTION','STRING'))"),
     ('DQ_DEF', 'ARRAY_DATA', 'EXPRESSION', condition='(DQ_ARRAY.DATA.sum())', expression="(has_column_type(DQ_DEF_ARRAY,'NAME','STRING'))"),
     ('DQ_DEF', 'ARRAY_DATA', 'EXPRESSION', condition='(DQ_ARRAY.DATA.sum())', expression="(has_column_type(DQ_DEF_ARRAY,'VALUE','INT'))"),
     ('DQ_DEF', 'ARRAY_DATA', 'EXPRESSION', condition='(DQ_ARRAY.DATA.sum())', expression="(has_columns(DQ_DEF_ARRAY,['BIT','VALUE','NAME','DESCRIPTION']))"),
     ('DQ_DEF', 'ARRAY_DATA', 'EXPRESSION', condition='(DQ_ARRAY.DATA.sum())', expression='(is_table(DQ_DEF_ARRAY))'),
     ('ERR', 'ARRAY_FORMAT', 'EXPRESSION', 'ANY_SUBARRAY', expression='(1<=META_SUBARRAY_XSTART+ERR_ARRAY.SHAPE[-1]-1<=1032)'),
     ('ERR', 'ARRAY_FORMAT', 'EXPRESSION', 'ANY_SUBARRAY', expression='(1<=META_SUBARRAY_YSTART+ERR_ARRAY.SHAPE[-2]-1<=1024)'),
     ('ERR', 'ARRAY_FORMAT', 'EXPRESSION', 'IF_FULL_FRAME', expression='(ERR_ARRAY.SHAPE[-2:]==(1024,1032))'),
     ('ERR', 'ARRAY_FORMAT', 'EXPRESSION', 'REQUIRED', expression="(has_type(ERR_ARRAY,'FLOAT'))"),
     ('ERR', 'ARRAY_FORMAT', 'EXPRESSION', 'REQUIRED', expression='(is_image(ERR_ARRAY))'),
     ('ERR', 'ARRAY_FORMAT', 'EXPRESSION', 'IF_SUBARRAY', expression='(ERR_ARRAY.SHAPE[-2:]==(META_SUBARRAY_YSIZE,META_SUBARRAY_XSIZE))'),
     ('EXP_TYPE', 'HEADER', 'CHARACTER', 'OPTIONAL', values=()),
     ('FULLFRAME_XSIZE', 'EXPRESSION', 'EXPRESSION', 'IF_FULL_FRAME', expression='(META_SUBARRAY_XSIZE==1032)'),
     ('FULLFRAME_XSTART', 'EXPRESSION', 'EXPRESSION', 'IF_FULL_FRAME', expression='(META_SUBARRAY_XSTART==1)'),
     ('FULLFRAME_YSIZE', 'EXPRESSION', 'EXPRESSION', 'IF_FULL_FRAME', expression='(META_SUBARRAY_YSIZE==1024)'),
     ('FULLFRAME_YSTART', 'EXPRESSION', 'EXPRESSION', 'IF_FULL_FRAME', expression='(META_SUBARRAY_YSTART==1)'),
     ('META.EXPOSURE.READPATT', 'HEADER', 'CHARACTER', 'OPTIONAL', values=()),
     ('META.EXPOSURE.TYPE', 'HEADER', 'CHARACTER', 'OPTIONAL', values=()),
     ('META.INSTRUMENT.BAND', 'HEADER', 'CHARACTER', 'OPTIONAL', values=()),
     ('META.INSTRUMENT.CHANNEL', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('1', '2', '3', '4', '12', '34', 'ANY', 'N/A')),
     ('META.INSTRUMENT.DETECTOR', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('MIRIFULONG', 'MIRIFUSHORT', 'MIRIMAGE', 'ANY', 'N/A')),
     ('META.INSTRUMENT.FILTER', 'HEADER', 'CHARACTER', 'OPTIONAL', values=()),
     ('META.INSTRUMENT.NAME', 'HEADER', 'CHARACTER', 'REQUIRED', values=('MIRI',)),
     ('META.REFFILE.AUTHOR', 'HEADER', 'CHARACTER', 'OPTIONAL', values=()),
     ('META.REFFILE.DESCRIPTION', 'HEADER', 'CHARACTER', 'OPTIONAL', values=()),
     ('META.REFFILE.HISTORY', 'HEADER', 'CHARACTER', 'OPTIONAL', values=()),
     ('META.REFFILE.PEDIGREE', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('&PEDIGREE',)),
     ('META.REFFILE.TYPE', 'HEADER', 'CHARACTER', 'REQUIRED', values=()),
     ('META.REFFILE.USEAFTER', 'HEADER', 'CHARACTER', 'REQUIRED', values=('&JWSTDATE',)),
     ('META.SUBARRAY.FASTAXIS', 'HEADER', 'INTEGER', 'OPTIONAL', values=('1', '-1', '2', '-2')),
     ('META.SUBARRAY.FASTAXIS', 'HEADER', 'INTEGER', 'REQUIRED', values=()),
     ('META.SUBARRAY.NAME', 'HEADER', 'CHARACTER', 'OPTIONAL', values=()),
     ('META.SUBARRAY.NAME', 'HEADER', 'CHARACTER', 'REQUIRED', values=()),
     ('META.SUBARRAY.SLOWAXIS', 'HEADER', 'INTEGER', 'OPTIONAL', values=('1', '-1', '2', '-2')),
     ('META.SUBARRAY.SLOWAXIS', 'HEADER', 'INTEGER', 'REQUIRED', values=()),
     ('META.SUBARRAY.XSIZE', 'HEADER', 'INTEGER', 'OPTIONAL', values=('1:1032',)),
     ('META.SUBARRAY.XSIZE', 'HEADER', 'INTEGER', 'REQUIRED', values=()),
     ('META.SUBARRAY.XSTART', 'HEADER', 'INTEGER', 'OPTIONAL', values=('1:1032',)),
     ('META.SUBARRAY.XSTART', 'HEADER', 'INTEGER', 'REQUIRED', values=()),
     ('META.SUBARRAY.YSIZE', 'HEADER', 'INTEGER', 'OPTIONAL', values=('1:1024',)),
     ('META.SUBARRAY.YSIZE', 'HEADER', 'INTEGER', 'REQUIRED', values=()),
     ('META.SUBARRAY.YSTART', 'HEADER', 'INTEGER', 'OPTIONAL', values=('1:1024',)),
     ('META.SUBARRAY.YSTART', 'HEADER', 'INTEGER', 'REQUIRED', values=()),
     ('META.TELESCOPE', 'HEADER', 'CHARACTER', 'REQUIRED', values=('JWST',)),
     ('MIRIFULONG_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(DETECTOR=='MIRIFULONG')", expression='((FASTAXIS==1)and(SLOWAXIS==2))'),
     ('MIRIFUSHORT_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(DETECTOR=='MIRIFUSHORT')", expression='((FASTAXIS==1)and(SLOWAXIS==2))'),
     ('MIRIMAGE_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(DETECTOR=='MIRIMAGE')", expression='((FASTAXIS==1)and(SLOWAXIS==2))'),
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', 'ANY_SUBARRAY', expression='(1<=META_SUBARRAY_XSTART+SCI_ARRAY.SHAPE[-1]-1<=1032)'),
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', 'ANY_SUBARRAY', expression='(1<=META_SUBARRAY_YSTART+SCI_ARRAY.SHAPE[-2]-1<=1024)'),
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', 'IF_FULL_FRAME', expression='(SCI_ARRAY.SHAPE[-2:]==(1024,1032))'),
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', 'REQUIRED', expression="(has_type(SCI_ARRAY,'FLOAT'))"),
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', 'REQUIRED', expression='(is_image(SCI_ARRAY))'),
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', 'IF_SUBARRAY', expression='(SCI_ARRAY.SHAPE[-2:]==(META_SUBARRAY_YSIZE,META_SUBARRAY_XSIZE))'),
     ('SUBARRAY_INBOUNDS_X', 'EXPRESSION', 'EXPRESSION', 'ANY_SUBARRAY', expression='(1<=META_SUBARRAY_XSTART+META_SUBARRAY_XSIZE-1<=1032)'),
     ('SUBARRAY_INBOUNDS_Y', 'EXPRESSION', 'EXPRESSION', 'ANY_SUBARRAY', expression='(1<=META_SUBARRAY_YSTART+META_SUBARRAY_YSIZE-1<=1024)')]
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
    ['all', 'amplifier', 'area', 'dark', 'distortion', 'extract1d', 'flat', 'gain', 'ipc', 'linearity', 'mask', 'pathloss', 'photom', 'readnoise', 'regions', 'saturation', 'specwcs', 'superbias', 'throughput', 'wcsregions']
    >>> test_config.cleanup(old_state)
    """
    
def reftypes_reference_name_to_tpn_text():
    """
    >>> old_state = test_config.setup()
    >>> types = reftypes.get_types_object("hst")
    >>> print(types.reference_name_to_tpn_text("data/s7g1700gl_dead.fits"))
    [('DESCRIP', 'HEADER', 'CHARACTER', 'REQUIRED', values=()),
     ('DETECTOR', 'HEADER', 'CHARACTER', 'REQUIRED', values=('FUV', 'NUV')),
     ('FILETYPE', 'HEADER', 'CHARACTER', 'REQUIRED', values=('"DEADTIME_REFERENCE_TABLE"',)),
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
     ('FILETYPE', 'HEADER', 'CHARACTER', 'REQUIRED', values=('"DEADTIME_REFERENCE_TABLE"',)),
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

