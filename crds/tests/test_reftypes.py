import os
import tempfile

# ==================================================================================
import numpy as np

from nose.tools import assert_raises, assert_true

# ==================================================================================

from crds.core import utils, log, exceptions
from crds.certify import reftypes
from crds import hst, jwst, roman

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

def reftypes_roman_load_raw_specs():
    """
    >>> old_state = test_config.setup()
    >>> SPECS = os.path.join(os.path.abspath(roman.HERE), "specs")
    >>> spec = reftypes.load_raw_specs(SPECS)
    >>> test_config.cleanup(old_state)
    """

def reftypes_roman_save_json_specs():
    """
    >>> old_state = test_config.setup()
    >>> SPECS = os.path.join(os.path.abspath(roman.HERE), "specs")
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
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', condition='((array_exists(SCI_ARRAY))and(array_exists(DQ_ARRAY)))', expression='(SCI_ARRAY.SHAPE[-2:]==DQ_ARRAY.SHAPE[-2:])'),
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(warn_only(has_type(DQ_ARRAY,'INT')))"),
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'WARN', expression='(is_image(DQ_ARRAY))'),
     ('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_column_type(DQ_DEF_ARRAY,'BIT','INT'))"),
     ('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_column_type(DQ_DEF_ARRAY,'DESCRIPTION','STRING'))"),
     ('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_column_type(DQ_DEF_ARRAY,'NAME','STRING'))"),
     ('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_column_type(DQ_DEF_ARRAY,'VALUE','INT'))"),
     ('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_columns(DQ_DEF_ARRAY,['BIT','VALUE','NAME','DESCRIPTION']))"),
     ('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression='(is_table(DQ_DEF_ARRAY))'),
     ('ERR', 'ARRAY_FORMAT', 'EXPRESSION', 'REQUIRED', expression='(SCI_ARRAY.SHAPE[-2:]==ERR_ARRAY.SHAPE[-2:])'),
     ('ERR', 'ARRAY_FORMAT', 'EXPRESSION', 'REQUIRED', expression="(has_type(ERR_ARRAY,'FLOAT'))"),
     ('ERR', 'ARRAY_FORMAT', 'EXPRESSION', 'REQUIRED', expression='(is_image(ERR_ARRAY))'),
     ('EXP_TYPE', 'HEADER', 'CHARACTER', 'OPTIONAL', values=()),
     ('FULLFRAME_XSIZE', 'EXPRESSION', 'EXPRESSION', 'IF_FULL_FRAME', expression='(META_SUBARRAY_XSIZE==1032)'),
     ('FULLFRAME_XSTART', 'EXPRESSION', 'EXPRESSION', 'IF_FULL_FRAME', expression='(META_SUBARRAY_XSTART==1)'),
     ('FULLFRAME_YSIZE', 'EXPRESSION', 'EXPRESSION', 'IF_FULL_FRAME', expression='(META_SUBARRAY_YSIZE==1024)'),
     ('FULLFRAME_YSTART', 'EXPRESSION', 'EXPRESSION', 'IF_FULL_FRAME', expression='(META_SUBARRAY_YSTART==1)'),
     ('META.AUTHOR', 'HEADER', 'CHARACTER', 'REQUIRED', values=()),
     ('META.DESCRIPTION', 'HEADER', 'CHARACTER', 'REQUIRED', values=()),
     ('META.EXPOSURE.READPATT', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('ACQ1', 'ACQ2', 'BRIGHT1', 'BRIGHT2', 'DEEP2', 'DEEP8', 'FAST', 'FASTGRPAVG', 'FASTGRPAVG8', 'FASTGRPAVG16', 'FASTGRPAVG32', 'FASTGRPAVG64', 'FGS', 'FGS60', 'FGS8370', 'FGS840', 'FGSRAPID', 'FINEGUIDE', 'ID', 'MEDIUM2', 'MEDIUM8', 'NIS', 'NISRAPID', 'NRS', 'NRSIRS2', 'NRSN16R4', 'NRSN32R8', 'NRSN8R2', 'NRSRAPID', 'NRSIRS2RAPID', 'NRSRAPIDD1', 'NRSRAPIDD2', 'NRSRAPIDD6', 'NRSSLOW', 'RAPID', 'SHALLOW2', 'SHALLOW4', 'SLOW', 'TRACK', 'ANY', 'N/A')),
     ('META.EXPOSURE.TYPE', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('MIR_4QPM', 'MIR_CORONCAL', 'MIR_DARK', 'MIR_DARKALL', 'MIR_DARKIMG', 'MIR_DARKMRS', 'MIR_FLATALL', 'MIR_FLATIMAGE', 'MIR_FLAT-IMAGE', 'MIR_FLATIMAGE-EXT', 'MIR_FLATMRS', 'MIR_FLAT-MRS', 'MIR_FLATMRS-EXT', 'MIR_IMAGE', 'MIR_LRS-FIXEDSLIT', 'MIR_LRS-SLITLESS', 'MIR_LYOT', 'MIR_MRS', 'MIR_TACONFIRM', 'MIR_TACQ', 'ANY', 'N/A')),
     ('META.HISTORY', 'HEADER', 'CHARACTER', 'REQUIRED', values=()),
     ('META.INSTRUMENT.BAND', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('SHORT', 'MEDIUM', 'LONG', 'SHORT-MEDIUM', 'SHORT-LONG', 'MEDIUM-SHORT', 'MEDIUM-LONG', 'LONG-SHORT', 'LONG-MEDIUM', 'MULTIPLE', 'ANY', 'N/A')),
     ('META.INSTRUMENT.CHANNEL', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('1', '2', '3', '4', '12', '34', '1234', '123', '234', 'ANY', 'N/A')),
     ('META.INSTRUMENT.CORONAGRAPH', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('4QPM', '4QPM_1065', '4QPM_1140', '4QPM_1550', 'LYOT', 'LYOT_2300', 'MASKA210R', 'MASKASWB', 'MASKA335R', 'MASKA430R', 'MASKALWB', 'NONE', 'ANY', 'N/A')),
     ('META.INSTRUMENT.DETECTOR', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('MIRIFULONG', 'MIRIFUSHORT', 'MIRIMAGE', 'ANY', 'N/A')),
     ('META.INSTRUMENT.FILTER', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('CLEAR', 'F070LP', 'F070W', 'F090W', 'F1000W', 'F100LP', 'F1065C', 'F110W', 'F1130W', 'F1140C', 'F115W', 'F1280W', 'F140M', 'F140X', 'F1500W', 'F150W', 'F150W2', 'F1550C', 'F170LP', 'F1800W', 'F182M', 'F187N', 'F200W', 'F2100W', 'F210M', 'F212N', 'F2300C', 'F250M', 'F2550W', 'F2550WR', 'F277W', 'F290LP', 'F300M', 'F322W2', 'F335M', 'F356W', 'F360M', 'F380M', 'F410M', 'F430M', 'F444W', 'F460M', 'F480M', 'F560W', 'F770W', 'FLENS', 'FND', 'GR150C', 'GR150R', 'OPAQUE', 'P750L', 'WLP4', 'MULTIPLE', 'ANY', 'N/A')),
     ('META.INSTRUMENT.GRATING', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('G140M', 'G235M', 'G395M', 'G140H', 'G235H', 'G395H', 'PRISM', 'MIRROR', 'UNKNOWN', 'MULTIPLE', 'N/A', 'ANY')),
     ('META.INSTRUMENT.NAME', 'HEADER', 'CHARACTER', 'REQUIRED', values=('MIRI',)),
     ('META.INSTRUMENT.PUPIL', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('CLEAR', 'CLEARP', 'F090W', 'F115W', 'F140M', 'F150W', 'F158M', 'F162M', 'F164N', 'F200W', 'F323N', 'F405N', 'F466N', 'F470N', 'FLAT', 'GDHS0', 'GDHS60', 'GR700XD', 'GRISMC', 'GRISMR', 'GRISMV2', 'GRISMV3', 'MASKBAR', 'MASKIPR', 'MASKRND', 'NRM', 'PINHOLES', 'WLM8', 'WLP8', 'ANY', 'N/A')),
     ('META.MODEL_TYPE', 'HEADER', 'CHARACTER', condition="(warning(not(META_REFTYPE.startswith('pars-'))))", values=()),
     ('META.PEDIGREE', 'HEADER', 'CHARACTER', 'REQUIRED', values=('&JWSTPEDIGREE',)),
     ('META.REFTYPE', 'HEADER', 'CHARACTER', 'REQUIRED', values=()),
     ('META.SUBARRAY.FASTAXIS', 'HEADER', 'INTEGER', 'OPTIONAL', values=('1', '-1', '2', '-2')),
     ('META.SUBARRAY.FASTAXIS', 'HEADER', 'INTEGER', 'REQUIRED', values=()),
     ('META.SUBARRAY.NAME', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('BRIGHTSKY', 'MASK1065', 'MASK1140', 'MASK1550', 'MASKLYOT', 'SLITLESSPRISM', 'SUB128', 'SUB256', 'SUB64', 'FULL', 'GENERIC', 'ANY', 'N/A')),
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
     ('META.USEAFTER', 'HEADER', 'CHARACTER', 'REQUIRED', values=('&JWSTDATE',)),
     ('MIRIFULONG_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(DETECTOR=='MIRIFULONG')", expression='((FASTAXIS==1)and(SLOWAXIS==2))'),
     ('MIRIFUSHORT_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(DETECTOR=='MIRIFUSHORT')", expression='((FASTAXIS==1)and(SLOWAXIS==2))'),
     ('MIRIMAGE_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(DETECTOR=='MIRIMAGE')", expression='((FASTAXIS==1)and(SLOWAXIS==2))'),
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', 'IF_FULL_FRAME', expression='(SCI_ARRAY.SHAPE[-2:]==(1024,1032))'),
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', 'REQUIRED', expression="(has_type(SCI_ARRAY,'FLOAT'))"),
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', 'REQUIRED', expression='(is_image(SCI_ARRAY))'),
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', 'IF_SUBARRAY', expression='(1<=META_SUBARRAY_XSTART+SCI_ARRAY.SHAPE[-1]-1<=1032)'),
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', 'IF_SUBARRAY', expression='(1<=META_SUBARRAY_YSTART+SCI_ARRAY.SHAPE[-2]-1<=1024)'),
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', 'IF_SUBARRAY', expression='(SCI_ARRAY.SHAPE[-2:]==(META_SUBARRAY_YSIZE,META_SUBARRAY_XSIZE))'),
     ('SUBARRAY_INBOUNDS_X', 'EXPRESSION', 'EXPRESSION', 'ANY_SUBARRAY', expression='(1<=META_SUBARRAY_XSTART+META_SUBARRAY_XSIZE-1<=1032)'),
     ('SUBARRAY_INBOUNDS_Y', 'EXPRESSION', 'EXPRESSION', 'ANY_SUBARRAY', expression='(1<=META_SUBARRAY_YSTART+META_SUBARRAY_YSIZE-1<=1024)'),
     ('SUBARRAY_XSIZE', 'EXPRESSION', 'EXPRESSION', 'IF_SUBARRAY', expression='(1<=META_SUBARRAY_XSIZE<=1032)'),
     ('SUBARRAY_XSTART', 'EXPRESSION', 'EXPRESSION', 'IF_SUBARRAY', expression='(1<=META_SUBARRAY_XSTART<=1032)'),
     ('SUBARRAY_YSIZE', 'EXPRESSION', 'EXPRESSION', 'IF_SUBARRAY', expression='(1<=META_SUBARRAY_YSIZE<=1024)'),
     ('SUBARRAY_YSTART', 'EXPRESSION', 'EXPRESSION', 'IF_SUBARRAY', expression='(1<=META_SUBARRAY_YSTART<=1024)')]
    >>> test_config.cleanup(old_state)
    """

def reftypes_roman_reference_name_to_tpn_infos():
    """
    >>> old_state = test_config.setup() # doctest: +ELLIPSIS
    >>> types = reftypes.get_types_object("roman")
    >>> infos = types.reference_name_to_tpninfos("roman_wfi_flat.asdf")
    >>> print(log.PP(infos))
    [('META.AUTHOR', 'HEADER', 'CHARACTER', 'REQUIRED', values=()),
     ('META.DESCRIPTION', 'HEADER', 'CHARACTER', 'REQUIRED', values=()),
     ('META.EXPOSURE.TYPE', 'HEADER', 'CHARACTER', 'OPTIONAL', values=(...)),
     ('META.INSTRUMENT.DETECTOR', 'HEADER', 'CHARACTER', 'OPTIONAL', values=(...)),
     ('META.INSTRUMENT.DETECTOR', 'HEADER', 'CHARACTER', 'REQUIRED', values=()),
     ('META.INSTRUMENT.NAME', 'HEADER', 'CHARACTER', 'REQUIRED', values=()),
     ('META.INSTRUMENT.NAME', 'HEADER', 'CHARACTER', 'REQUIRED', values=('WFI',)),
     ('META.INSTRUMENT.OPTICAL_ELEMENT', 'HEADER', 'CHARACTER', 'OPTIONAL', values=(...)),
     ('META.INSTRUMENT.OPTICAL_ELEMENT', 'HEADER', 'CHARACTER', 'REQUIRED', values=()),
     ('META.PEDIGREE', 'HEADER', 'CHARACTER', 'REQUIRED', values=('&JWSTPEDIGREE',)),
     ('META.REFTYPE', 'HEADER', 'CHARACTER', 'REQUIRED', values=()),
     ('META.TELESCOPE', 'HEADER', 'CHARACTER', 'REQUIRED', values=('ROMAN',)),
     ('META.USEAFTER', 'HEADER', 'CHARACTER', 'REQUIRED', values=('&JWSTDATE',))]
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
    ['abvegaoffset', 'all', 'amplifier', 'apcorr', 'area', 'dark', 'distortion', 'drizpars', 'extract1d', 'flat', 'gain', 'ipc', 'linearity', 'mask', 'pars-darkpipeline', 'pars-detector1pipeline', 'pars-image2pipeline', 'pars-outlierdetectionstep', 'pars-sourcecatalogstep', 'pars-spec2pipeline', 'pars-tweakregstep', 'pathloss', 'persat', 'photom', 'readnoise', 'regions', 'saturation', 'specwcs', 'superbias', 'throughput', 'trapdensity', 'trappars', 'wavelengthrange', 'wcsregions', 'wfssbkg']
    >>> test_config.cleanup(old_state)
    """

def reftypes_roman_get_filekinds():
    """
    >>> old_state = test_config.setup()
    >>> types = reftypes.get_types_object("roman")
    >>> {'all', 'flat'}.issubset(types.get_filekinds("wfi"))
    True
    >>> test_config.cleanup(old_state)
    """

def reftypes_reference_name_to_tpn_text():
    """
    >>> old_state = test_config.setup()
    >>> types = reftypes.get_types_object("hst")
    >>> print(types.reference_name_to_tpn_text("data/s7g1700gl_dead.fits"))
    From TPN: cos_dead.tpn
    ----------------------
    INSTRUME            H        C         R    COS
    FILETYPE            H        C         R    "DEADTIME REFERENCE TABLE"
    DETECTOR            H        C         R    FUV,NUV
    VCALCOS             H        C         R
    USEAFTER            H        C         R    &SYBDATE
    PEDIGREE            H        C         R    &PEDIGREE
    DESCRIP             H        C         R
    SEGMENT             C        C         R    FUVA,FUVB,ANY
    <BLANKLINE>

    >>> test_config.cleanup(old_state)
    """

def reftypes_reference_name_to_ld_tpn_text():
    """
    >>> old_state = test_config.setup()
    >>> types = reftypes.get_types_object("hst")
    >>> print(types.reference_name_to_tpn_text("data/s7g1700gl_dead.fits"))
    From TPN: cos_dead.tpn
    ----------------------
    INSTRUME            H        C         R    COS
    FILETYPE            H        C         R    "DEADTIME REFERENCE TABLE"
    DETECTOR            H        C         R    FUV,NUV
    VCALCOS             H        C         R
    USEAFTER            H        C         R    &SYBDATE
    PEDIGREE            H        C         R    &PEDIGREE
    DESCRIP             H        C         R
    SEGMENT             C        C         R    FUVA,FUVB,ANY
    <BLANKLINE>
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
        #         tinfo = certify.generic_tpn.TpnInfo('DETECTOR','H','C','Q', ('WFC','HRC','SBC'))
        #         assert_raises(ValueError, certify.validators.validator, tinfo)
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
