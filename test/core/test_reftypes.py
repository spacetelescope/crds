from pytest import mark
import os
from crds.core import reftypes
from crds import hst, jwst, roman


# ==================================================================================

@mark.hst
@mark.reftypes
@mark.core
def test_reftypes_load_type_spec_spec(default_shared_state):
    SPEC_FILE = os.path.join(os.path.abspath(hst.HERE), "specs", "acs_biasfile.spec")
    spec = reftypes.TypeSpec.from_file(SPEC_FILE)


@mark.hst
@mark.reftypes
@mark.core
def test_reftypes_load_type_spec_rmap(default_shared_state):
    SPEC_FILE = os.path.join(os.path.abspath(hst.HERE), "specs", "cos_xwlkfile.rmap")
    spec = reftypes.TypeSpec.from_file(SPEC_FILE)


@mark.hst
@mark.reftypes
@mark.core
def test_reftypes_hst_load_raw_specs(default_shared_state):
    SPECS = os.path.join(os.path.abspath(hst.HERE), "specs")
    spec = reftypes.load_raw_specs(SPECS)


@mark.hst
@mark.reftypes
@mark.core
def test_reftypes_hst_save_json_specs(default_shared_state, test_temp_dir):
    SPECS = os.path.join(os.path.abspath(hst.HERE), "specs")
    specs = reftypes.load_raw_specs(SPECS)
    f = os.path.join(test_temp_dir, "specfile.json")
    reftypes.save_json_specs(specs, f)
    assert os.path.exists(f)


@mark.jwst
@mark.reftypes
@mark.core
def test_reftypes_jwst_load_raw_specs(default_shared_state):
    SPECS = os.path.join(os.path.abspath(jwst.HERE), "specs")
    spec = reftypes.load_raw_specs(SPECS)


@mark.jwst
@mark.reftypes
@mark.core
def test_reftypes_jwst_save_json_specs(default_shared_state, test_temp_dir):
    SPECS = os.path.join(os.path.abspath(jwst.HERE), "specs")
    specs = reftypes.load_raw_specs(SPECS)
    f = os.path.join(test_temp_dir, "specfile.json")
    reftypes.save_json_specs(specs, f)
    assert os.path.exists(f)


@mark.roman
@mark.reftypes
@mark.core
def test_reftypes_roman_load_raw_specs(default_shared_state):
    SPECS = os.path.join(os.path.abspath(roman.HERE), "specs")
    spec = reftypes.load_raw_specs(SPECS)


@mark.roman
@mark.reftypes
@mark.core
def test_reftypes_roman_save_json_specs(default_shared_state, test_temp_dir):
    SPECS = os.path.join(os.path.abspath(roman.HERE), "specs")
    specs = reftypes.load_raw_specs(SPECS)
    f = os.path.join(test_temp_dir, "specfile.json")
    reftypes.save_json_specs(specs, f)
    assert os.path.exists(f)


@mark.hst
@mark.reftypes
@mark.core
def test_reftypes_hst_reference_name_to_tpn_infos(default_shared_state, hst_data):
    types = reftypes.get_types_object("hst")
    infos = types.reference_name_to_tpninfos(f"{hst_data}/s7g1700gl_dead.fits")
    expected = """('DESCRIP', 'HEADER', 'CHARACTER', 'REQUIRED', values=())
('DETECTOR', 'HEADER', 'CHARACTER', 'REQUIRED', values=('FUV', 'NUV'))
('FILETYPE', 'HEADER', 'CHARACTER', 'REQUIRED', values=('DEADTIME REFERENCE TABLE',))
('INSTRUME', 'HEADER', 'CHARACTER', 'REQUIRED', values=('COS',))
('PEDIGREE', 'HEADER', 'CHARACTER', 'REQUIRED', values=('&PEDIGREE',))
('SEGMENT', 'COLUMN', 'CHARACTER', 'REQUIRED', values=('FUVA', 'FUVB', 'ANY'))
('USEAFTER', 'HEADER', 'CHARACTER', 'REQUIRED', values=('&SYBDATE',))
('VCALCOS', 'HEADER', 'CHARACTER', 'REQUIRED', values=())""".splitlines()
    for i, msg in enumerate(infos):
        assert str(msg) == expected[i]


@mark.jwst
@mark.reftypes
@mark.core
def test_reftypes_jwst_reference_name_to_tpn_infos(default_shared_state, jwst_data):    # doctest: +ELLIPSIS
    types = reftypes.get_types_object("jwst")
    infos = types.reference_name_to_tpninfos(f"{jwst_data}/jwst_miri_flat_slitlessprism.fits")
    expected = """('DETECTOR', 'HEADER', 'CHARACTER', 'OPTIONAL', values=())
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', condition='((array_exists(SCI_ARRAY))and(array_exists(DQ_ARRAY)))', expression='(SCI_ARRAY.SHAPE[-2:]==DQ_ARRAY.SHAPE[-2:])')
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(warn_only(has_type(DQ_ARRAY,'INT')))")
     ('DQ', 'ARRAY_FORMAT', 'EXPRESSION', 'WARN', expression='(is_image(DQ_ARRAY))')
     ('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_column_type(DQ_DEF_ARRAY,'BIT','INT'))")
     ('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_column_type(DQ_DEF_ARRAY,'DESCRIPTION','STRING'))")
     ('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_column_type(DQ_DEF_ARRAY,'NAME','STRING'))")
     ('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_column_type(DQ_DEF_ARRAY,'VALUE','INT'))")
     ('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression="(has_columns(DQ_DEF_ARRAY,['BIT','VALUE','NAME','DESCRIPTION']))")
     ('DQ_DEF', 'ARRAY_FORMAT', 'EXPRESSION', 'OPTIONAL', expression='(is_table(DQ_DEF_ARRAY))')
     ('ERR', 'ARRAY_FORMAT', 'EXPRESSION', 'REQUIRED', expression='(SCI_ARRAY.SHAPE[-2:]==ERR_ARRAY.SHAPE[-2:])')
     ('ERR', 'ARRAY_FORMAT', 'EXPRESSION', 'REQUIRED', expression="(has_type(ERR_ARRAY,'FLOAT'))")
     ('ERR', 'ARRAY_FORMAT', 'EXPRESSION', 'REQUIRED', expression='(is_image(ERR_ARRAY))')
     ('EXP_TYPE', 'HEADER', 'CHARACTER', 'OPTIONAL', values=())
     ('FULLFRAME_XSIZE', 'EXPRESSION', 'EXPRESSION', 'IF_FULL_FRAME', expression='(META_SUBARRAY_XSIZE==1032)')
     ('FULLFRAME_XSTART', 'EXPRESSION', 'EXPRESSION', 'IF_FULL_FRAME', expression='(META_SUBARRAY_XSTART==1)')
     ('FULLFRAME_YSIZE', 'EXPRESSION', 'EXPRESSION', 'IF_FULL_FRAME', expression='(META_SUBARRAY_YSIZE==1024)')
     ('FULLFRAME_YSTART', 'EXPRESSION', 'EXPRESSION', 'IF_FULL_FRAME', expression='(META_SUBARRAY_YSTART==1)')
     ('META.AUTHOR', 'HEADER', 'CHARACTER', 'REQUIRED', values=())
     ('META.DESCRIPTION', 'HEADER', 'CHARACTER', 'REQUIRED', values=())
     ('META.EXPOSURE.READPATT', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('ACQ1', 'ACQ2', 'BRIGHT1', 'BRIGHT2', 'DEEP2', 'DEEP8', 'FAST', 'FASTGRPAVG', 'FASTGRPAVG8', 'FASTGRPAVG16', 'FASTGRPAVG32', 'FASTGRPAVG64', 'FASTR1', 'FASTR100', 'FGS', 'FGS60', 'FGS8370', 'FGS840', 'FGSRAPID', 'FINEGUIDE', 'ID', 'MEDIUM2', 'MEDIUM8', 'NIS', 'NISRAPID', 'NRS', 'NRSIRS2', 'NRSN16R4', 'NRSN32R8', 'NRSN8R2', 'NRSRAPID', 'NRSIRS2RAPID', 'NRSRAPIDD1', 'NRSRAPIDD2', 'NRSRAPIDD6', 'NRSSLOW', 'RAPID', 'SHALLOW2', 'SHALLOW4', 'SLOW', 'SLOWR1', 'TRACK', 'ANY', 'N/A'))
     ('META.EXPOSURE.TYPE', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('MIR_4QPM', 'MIR_CORONCAL', 'MIR_DARK', 'MIR_DARKALL', 'MIR_DARKIMG', 'MIR_DARKMRS', 'MIR_FLATALL', 'MIR_FLATIMAGE', 'MIR_FLAT-IMAGE', 'MIR_FLATIMAGE-EXT', 'MIR_FLATMRS', 'MIR_FLAT-MRS', 'MIR_FLATMRS-EXT', 'MIR_IMAGE', 'MIR_LRS-FIXEDSLIT', 'MIR_LRS-SLITLESS', 'MIR_LYOT', 'MIR_MRS', 'MIR_TACONFIRM', 'MIR_TACQ', 'ANY', 'N/A'))
     ('META.HISTORY', 'HEADER', 'CHARACTER', 'REQUIRED', values=())
     ('META.INSTRUMENT.BAND', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('SHORT', 'MEDIUM', 'LONG', 'SHORT-MEDIUM', 'SHORT-LONG', 'MEDIUM-SHORT', 'MEDIUM-LONG', 'LONG-SHORT', 'LONG-MEDIUM', 'MULTIPLE', 'ANY', 'N/A'))
     ('META.INSTRUMENT.CHANNEL', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('1', '2', '3', '4', '12', '34', '1234', '123', '234', 'ANY', 'N/A'))
     ('META.INSTRUMENT.CORONAGRAPH', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('4QPM', '4QPM_1065', '4QPM_1140', '4QPM_1550', 'LYOT', 'LYOT_2300', 'MASKA210R', 'MASKASWB', 'MASKA335R', 'MASKA430R', 'MASKALWB', 'NONE', 'ANY', 'N/A'))
     ('META.INSTRUMENT.DETECTOR', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('MIRIFULONG', 'MIRIFUSHORT', 'MIRIMAGE', 'ANY', 'N/A'))
     ('META.INSTRUMENT.FILTER', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('CLEAR', 'F070LP', 'F070W', 'F090W', 'F1000W', 'F100LP', 'F1065C', 'F110W', 'F1130W', 'F1140C', 'F115W', 'F1280W', 'F140M', 'F140X', 'F1500W', 'F150W', 'F150W2', 'F1550C', 'F170LP', 'F1800W', 'F182M', 'F187N', 'F200W', 'F2100W', 'F210M', 'F212N', 'F2300C', 'F250M', 'F2550W', 'F2550WR', 'F277W', 'F290LP', 'F300M', 'F322W2', 'F335M', 'F356W', 'F360M', 'F380M', 'F410M', 'F430M', 'F444W', 'F460M', 'F480M', 'F560W', 'F770W', 'FLENS', 'FND', 'GR150C', 'GR150R', 'OPAQUE', 'P750L', 'WLP4', 'MULTIPLE', 'ANY', 'N/A'))
     ('META.INSTRUMENT.GRATING', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('G140M', 'G235M', 'G395M', 'G140H', 'G235H', 'G395H', 'PRISM', 'MIRROR', 'UNKNOWN', 'MULTIPLE', 'N/A', 'ANY'))
     ('META.INSTRUMENT.NAME', 'HEADER', 'CHARACTER', 'REQUIRED', values=('MIRI',))
     ('META.INSTRUMENT.PUPIL', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('CLEAR', 'CLEARP', 'F090W', 'F115W', 'F140M', 'F150W', 'F158M', 'F162M', 'F164N', 'F200W', 'F323N', 'F405N', 'F466N', 'F470N', 'FLAT', 'GDHS0', 'GDHS60', 'GR700XD', 'GRISMC', 'GRISMR', 'GRISMV2', 'GRISMV3', 'MASKBAR', 'MASKIPR', 'MASKRND', 'NRM', 'PINHOLES', 'WLM8', 'WLP8', 'ANY', 'N/A'))
     ('META.MODEL_TYPE', 'HEADER', 'CHARACTER', condition="(warning(not(META_REFTYPE.startswith('pars-'))))", values=())
     ('META.PEDIGREE', 'HEADER', 'CHARACTER', 'REQUIRED', values=('&JWSTPEDIGREE',))
     ('META.REFTYPE', 'HEADER', 'CHARACTER', 'REQUIRED', values=())
     ('META.SUBARRAY.FASTAXIS', 'HEADER', 'INTEGER', 'OPTIONAL', values=('1', '-1', '2', '-2'))
     ('META.SUBARRAY.FASTAXIS', 'HEADER', 'INTEGER', 'REQUIRED', values=())
     ('META.SUBARRAY.NAME', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('BRIGHTSKY', 'MASK1065', 'MASK1140', 'MASK1550', 'MASKLYOT', 'SLITLESSPRISM', 'SUB128', 'SUB256', 'SUB64', 'FULL', 'GENERIC', 'ANY', 'N/A'))
     ('META.SUBARRAY.NAME', 'HEADER', 'CHARACTER', 'REQUIRED', values=())
     ('META.SUBARRAY.SLOWAXIS', 'HEADER', 'INTEGER', 'OPTIONAL', values=('1', '-1', '2', '-2'))
     ('META.SUBARRAY.SLOWAXIS', 'HEADER', 'INTEGER', 'REQUIRED', values=())
     ('META.SUBARRAY.XSIZE', 'HEADER', 'INTEGER', 'OPTIONAL', values=('1:1032',))
     ('META.SUBARRAY.XSIZE', 'HEADER', 'INTEGER', 'REQUIRED', values=())
     ('META.SUBARRAY.XSTART', 'HEADER', 'INTEGER', 'OPTIONAL', values=('1:1032',))
     ('META.SUBARRAY.XSTART', 'HEADER', 'INTEGER', 'REQUIRED', values=())
     ('META.SUBARRAY.YSIZE', 'HEADER', 'INTEGER', 'OPTIONAL', values=('1:1024',))
     ('META.SUBARRAY.YSIZE', 'HEADER', 'INTEGER', 'REQUIRED', values=())
     ('META.SUBARRAY.YSTART', 'HEADER', 'INTEGER', 'OPTIONAL', values=('1:1024',))
     ('META.SUBARRAY.YSTART', 'HEADER', 'INTEGER', 'REQUIRED', values=())
     ('META.TELESCOPE', 'HEADER', 'CHARACTER', 'REQUIRED', values=('JWST',))
     ('META.USEAFTER', 'HEADER', 'CHARACTER', 'REQUIRED', values=('&JWSTDATE',))
     ('MIRIFULONG_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(DETECTOR=='MIRIFULONG')", expression='((FASTAXIS==1)and(SLOWAXIS==2))')
     ('MIRIFUSHORT_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(DETECTOR=='MIRIFUSHORT')", expression='((FASTAXIS==1)and(SLOWAXIS==2))')
     ('MIRIMAGE_AXIS', 'EXPRESSION', 'EXPRESSION', condition="(DETECTOR=='MIRIMAGE')", expression='((FASTAXIS==1)and(SLOWAXIS==2))')
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', 'IF_FULL_FRAME', expression='(SCI_ARRAY.SHAPE[-2:]==(1024,1032))')
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', 'REQUIRED', expression="(has_type(SCI_ARRAY,'FLOAT'))")
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', 'REQUIRED', expression='(is_image(SCI_ARRAY))')
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', 'IF_SUBARRAY', expression='(1<=META_SUBARRAY_XSTART+SCI_ARRAY.SHAPE[-1]-1<=1032)')
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', 'IF_SUBARRAY', expression='(1<=META_SUBARRAY_YSTART+SCI_ARRAY.SHAPE[-2]-1<=1024)')
     ('SCI', 'ARRAY_FORMAT', 'EXPRESSION', 'IF_SUBARRAY', expression='(SCI_ARRAY.SHAPE[-2:]==(META_SUBARRAY_YSIZE,META_SUBARRAY_XSIZE))')
     ('SUBARRAY_INBOUNDS_X', 'EXPRESSION', 'EXPRESSION', 'ANY_SUBARRAY', expression='(1<=META_SUBARRAY_XSTART+META_SUBARRAY_XSIZE-1<=1032)')
     ('SUBARRAY_INBOUNDS_Y', 'EXPRESSION', 'EXPRESSION', 'ANY_SUBARRAY', expression='(1<=META_SUBARRAY_YSTART+META_SUBARRAY_YSIZE-1<=1024)')
     ('SUBARRAY_XSIZE', 'EXPRESSION', 'EXPRESSION', 'IF_SUBARRAY', expression='(1<=META_SUBARRAY_XSIZE<=1032)')
     ('SUBARRAY_XSTART', 'EXPRESSION', 'EXPRESSION', 'IF_SUBARRAY', expression='(1<=META_SUBARRAY_XSTART<=1032)')
     ('SUBARRAY_YSIZE', 'EXPRESSION', 'EXPRESSION', 'IF_SUBARRAY', expression='(1<=META_SUBARRAY_YSIZE<=1024)')
     ('SUBARRAY_YSTART', 'EXPRESSION', 'EXPRESSION', 'IF_SUBARRAY', expression='(1<=META_SUBARRAY_YSTART<=1024)')""".splitlines()
    for i, msg in enumerate(infos):
        assert str(msg) == expected[i].strip()


@mark.roman
@mark.reftypes
@mark.core
def test_reftypes_roman_reference_name_to_tpn_infos(default_shared_state, roman_data):
    types = reftypes.get_types_object("roman")
    infos = types.reference_name_to_tpninfos(f"{roman_data}/roman_wfi_flat.asdf")
    expected = """('ROMAN.META.AUTHOR', 'HEADER', 'CHARACTER', 'REQUIRED', values=())
     ('ROMAN.META.DESCRIPTION', 'HEADER', 'CHARACTER', 'REQUIRED', values=())
     ('ROMAN.META.EXPOSURE.TYPE', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('WFI_IMAGE', 'WFI_GRISM', 'WFI_PRISM', 'WFI_DARK', 'WFI_WSM_ACQ1', 'WFI_WSM_ACQ2', 'WFI_WSM_TRACK', 'WFI_WFSC', 'DEFOCUS_MODERATE', 'DEFOCUS_LARGE', 'WFI_WIM_ACQ', 'WFI_WIM_TRACK', 'WFI_PARALLEL', 'WFI_FLAT_EXTERNAL', 'WFI_FLAT_INTERNAL', 'WFI_RCS'))
     ('ROMAN.META.INSTRUMENT.DETECTOR', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('WFI01', 'WFI02', 'WFI03', 'WFI04', 'WFI05', 'WFI06', 'WFI07', 'WFI08', 'WFI09', 'WFI10', 'WFI11', 'WFI12', 'WFI13', 'WFI14', 'WFI15', 'WFI16', 'WFI17', 'WFI18', 'ANY', 'N/A'))
     ('ROMAN.META.INSTRUMENT.DETECTOR', 'HEADER', 'CHARACTER', 'REQUIRED', values=())
     ('ROMAN.META.INSTRUMENT.NAME', 'HEADER', 'CHARACTER', 'REQUIRED', values=())
     ('ROMAN.META.INSTRUMENT.NAME', 'HEADER', 'CHARACTER', 'REQUIRED', values=('WFI',))
     ('ROMAN.META.INSTRUMENT.OPTICAL_ELEMENT', 'HEADER', 'CHARACTER', 'OPTIONAL', values=('F062', 'F087', 'F106', 'F129', 'F146', 'F158', 'F184', 'F213', 'GRISM', 'PRISM', 'CLEAR', 'DARK', 'N/A', 'ANY', 'UNKNOWN'))
     ('ROMAN.META.INSTRUMENT.OPTICAL_ELEMENT', 'HEADER', 'CHARACTER', 'REQUIRED', values=())
     ('ROMAN.META.ORIGIN', 'HEADER', 'CHARACTER', 'REQUIRED', values=())
     ('ROMAN.META.PEDIGREE', 'HEADER', 'CHARACTER', 'REQUIRED', values=('&JWSTPEDIGREE',))
     ('ROMAN.META.REFTYPE', 'HEADER', 'CHARACTER', 'REQUIRED', values=())
     ('ROMAN.META.TELESCOPE', 'HEADER', 'CHARACTER', 'REQUIRED', values=('ROMAN',))
     ('ROMAN.META.USEAFTER', 'HEADER', 'CHARACTER', 'REQUIRED', values=('&JWSTDATE',))""".splitlines()
    for i, msg in enumerate(infos):
        assert str(msg) == expected[i].strip()


@mark.hst
@mark.reftypes
@mark.core
def test_reftypes_hst_get_filekinds(default_shared_state):
    types = reftypes.get_types_object("hst")
    nicmos_types = types.get_filekinds("nicmos")
    expected_types = ['backtab', 'darkfile', 'flatfile', 'idctab', 'illmfile', 'maskfile', 'nlinfile', 'noisfile', 'pedsbtab', 'phottab', 'pmodfile', 'pmskfile', 'rnlcortb', 'saacntab', 'saadfile', 'tdffile', 'tempfile', 'zprattab']
    assert sorted(nicmos_types) == sorted(expected_types)


@mark.jwst
@mark.reftypes
@mark.core
def test_reftypes_jwst_get_filekinds(default_shared_state):
    types = reftypes.get_types_object("jwst")
    niriss_types = types.get_filekinds("niriss")
    expected_types = ['abvegaoffset', 'all', 'amplifier', 'apcorr', 'area', 'dark', 'distortion', 'drizpars', 'extract1d', 'filteroffset', 'flat', 'gain', 'ipc', 'linearity', 'mask', 'nrm', 'pars-chargemigrationstep', 'pars-darkcurrentstep', 'pars-darkpipeline', 'pars-detector1pipeline', 'pars-image2pipeline', 'pars-jumpstep', 'pars-outlierdetectionstep', 'pars-rampfitstep', 'pars-resamplestep', 'pars-sourcecatalogstep', 'pars-spec2pipeline', 'pars-tweakregstep', 'pars-undersamplecorrectionstep', 'pars-whitelightstep', 'pathloss', 'persat', 'photom', 'readnoise', 'regions', 'saturation', 'speckernel', 'specprofile', 'spectrace', 'specwcs', 'superbias', 'throughput', 'trapdensity', 'trappars', 'wavelengthrange', 'wavemap', 'wcsregions', 'wfssbkg']
    assert sorted(niriss_types) == sorted(expected_types)


@mark.roman
@mark.reftypes
@mark.core
def test_reftypes_roman_get_filekinds(default_shared_state):
    types = reftypes.get_types_object("roman")
    assert {'all', 'flat'}.issubset(types.get_filekinds("wfi")) is True


@mark.hst
@mark.reftypes
@mark.core
def test_reftypes_reference_name_to_tpn_text(default_shared_state, hst_data):
    types = reftypes.get_types_object("hst")
    text = types.reference_name_to_tpn_text(f"{hst_data}/s7g1700gl_dead.fits").splitlines()
    expected = """From TPN: cos_dead.tpn
    ----------------------
    INSTRUME            H        C         R    COS
    FILETYPE            H        C         R    "DEADTIME REFERENCE TABLE"
    DETECTOR            H        C         R    FUV,NUV
    VCALCOS             H        C         R
    USEAFTER            H        C         R    &SYBDATE
    PEDIGREE            H        C         R    &PEDIGREE
    DESCRIP             H        C         R
    SEGMENT             C        C         R    FUVA,FUVB,ANY
    """.splitlines()
    for i, line in enumerate(text):
        assert line.strip() == expected[i].strip()


@mark.hst
@mark.reftypes
@mark.core
def test_reftypes_reference_name_to_ld_tpn_text(default_shared_state, hst_data):
    types = reftypes.get_types_object("hst")
    text = types.reference_name_to_tpn_text(f"{hst_data}/s7g1700gl_dead.fits").splitlines()
    expected = """From TPN: cos_dead.tpn
    ----------------------
    INSTRUME            H        C         R    COS
    FILETYPE            H        C         R    "DEADTIME REFERENCE TABLE"
    DETECTOR            H        C         R    FUV,NUV
    VCALCOS             H        C         R
    USEAFTER            H        C         R    &SYBDATE
    PEDIGREE            H        C         R    &PEDIGREE
    DESCRIP             H        C         R
    SEGMENT             C        C         R    FUVA,FUVB,ANY
    """.splitlines()
    for i, line in enumerate(text):
        assert line.strip() == expected[i].strip()


@mark.hst
@mark.reftypes
@mark.core
def test_reftypes_get_row_keys_by_instrument(default_shared_state):
    types = reftypes.get_types_object("hst")
    cos_keys = types.get_row_keys_by_instrument("cos")
    expected = ['aperture', 'cenwave', 'date', 'fpoffset', 'opt_elem', 'segment']
    assert sorted(cos_keys) == sorted(expected)
