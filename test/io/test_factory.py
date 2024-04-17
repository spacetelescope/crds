from pytest import mark
from crds import data_file
from crds.io import factory

ARRAY_PROPS = {'SHAPE': (4,),
 'KIND': 'TABLE',
 'DATA_TYPE': {'OPT_ELEM': '|S8',
  'XC_RANGE': '>i4',
  'RESWIDTH': '>f8',
  'MAX_TIME_DIFF': '>f8',
  'STEPSIZE': '>i4',
  'XD_RANGE': '>i4',
  'BOX': '>i4'},
 'COLUMN_NAMES': ['OPT_ELEM',
  'XC_RANGE',
  'RESWIDTH',
  'MAX_TIME_DIFF',
  'STEPSIZE',
  'XD_RANGE',
  'BOX'],
 'NAME': '1',
 'EXTENSION': 1,
 'DATA': None}


@mark.jwst
@mark.io
@mark.factory
def test_get_fits_type(jwst_serverless_state, jwst_data):
    t = factory.get_filetype(f"{jwst_data}/valid.fits")
    assert t == 'fits'


@mark.hst
@mark.io
@mark.factory
def test_get_fits_type_opaque(hst_serverless_state, hst_data):
    t = factory.get_filetype(f"{hst_data}/opaque_fts.tmp")
    assert t == 'fits'


@mark.jwst
@mark.io
@mark.factory
def test_get_asdf_type(jwst_serverless_state, jwst_data):
    t = factory.get_filetype(f"{jwst_data}/valid.asdf")
    assert t == 'asdf'


@mark.jwst
@mark.io
@mark.factory
def test_get_asdf_type_opaque(jwst_serverless_state, jwst_data):
    t = factory.get_filetype(f"{jwst_data}/opaque_asd.tmp")
    assert t == 'asdf'


@mark.jwst
@mark.io
@mark.factory
def test_get_geis_type(jwst_serverless_state, hst_data):
    t = factory.get_filetype(f"{hst_data}/e1b09593u.r1h")
    assert t =='geis'


@mark.jwst
@mark.io
@mark.factory
def test_get_geis_type_opaque(jwst_serverless_state, jwst_data):
    t = factory.get_filetype(f"{jwst_data}/opaque_gs.tmp")
    assert t =='geis'   


@mark.jwst
@mark.io
@mark.factory
def test_get_json_type(jwst_serverless_state, jwst_data):
    t = factory.get_filetype(f"{jwst_data}/valid.json")
    assert t == 'json'


@mark.jwst
@mark.io
@mark.factory
def test_get_json_type_opaque(jwst_serverless_state, jwst_data):
    t = factory.get_filetype(f"{jwst_data}/opaque_jsn.tmp")
    assert t == 'json'


@mark.jwst
@mark.io
@mark.factory
def test_get_yaml_type(jwst_serverless_state, jwst_data):
    t = factory.get_filetype(f"{jwst_data}/valid.yaml")
    assert t == 'yaml'


@mark.jwst
@mark.io
@mark.factory
def test_get_yaml_type_opaque(jwst_serverless_state, jwst_data):
    t = factory.get_filetype(f"{jwst_data}/opaque_yml.tmp")
    assert t == 'yaml'


# ==================================================================================

# Factory module tests by way of crds.data_file (which uses io.factory.file_factory) 

@mark.jwst
@mark.io
@mark.factory
def test_asdf_history_no_entries_description(jwst_serverless_state, jwst_data):
    header = data_file.get_header(f"{jwst_data}/niriss_ref_distortion.asdf")
    assert header["HISTORY"] == 'UNDEFINED'


@mark.jwst
@mark.io
@mark.factory
def test_asdf_history_no_entries_list(jwst_serverless_state, jwst_data):
    header = data_file.get_header(f"{jwst_data}/jwst_miri_distortion_0022.asdf")
    assert header["HISTORY"] == "2017-06-02 14:29:39 :: DOCUMENT: MIRI-TN-00001-ETH_Iss2-1_Calibrationproduct_MRS_d2c.  New files created from CDP-6 with updated file structure and V2/V3 instead of XAN/YAN"


@mark.jwst
@mark.io
@mark.factory
def test_asdf_history_with_entries(jwst_serverless_state, jwst_data):
    header = data_file.get_header(f"{jwst_data}/jwst_nirspec_ifupost_0004.asdf")
    assert header["HISTORY"] == "2018-04-17 20:18:32 :: New version created from CV3 with updated file structure"


@mark.hst
@mark.io
@mark.factory
def test_get_array_properties_hdu_name(hst_serverless_state, hst_data):
    props = data_file.get_array_properties(f"{hst_data}/x2i1559gl_wcp.fits", "_WCP")
    for k, v in props.items():
        if k != "NAME":
            assert ARRAY_PROPS[k] == v
        else:
            assert v == '_WCP'


@mark.hst
@mark.io
@mark.factory
def test_get_array_properties_extension_number1(hst_serverless_state, hst_data):
    props = data_file.get_array_properties(f"{hst_data}/x2i1559gl_wcp.fits", "EXT1")
    for k, v in props.items():
        if k != "NAME":
            assert ARRAY_PROPS[k] == v
        else:
            assert v == '1'

@mark.hst
@mark.io
@mark.factory
def test_get_array_properties_extension_number2(hst_serverless_state, hst_data):
    props = data_file.get_array_properties(f"{hst_data}/x2i1559gl_wcp.fits", "EXTENSION1")
    for k, v in props.items():
        if k != "NAME":
            assert ARRAY_PROPS[k] == v
        else:
            assert v == '1'


@mark.hst
@mark.io
@mark.factory
def test_get_array_properties_extension_number1(hst_serverless_state, hst_data):
    props = data_file.get_array_properties(f"{hst_data}/x2i1559gl_wcp.fits", "EXT1")
    for k, v in props.items():
        if k != "NAME":
            assert ARRAY_PROPS[k] == v
        else:
            assert v == '1'


@mark.hst
@mark.io
@mark.factory
def test_get_array_properties_extension_number2(hst_serverless_state, hst_data):
    props = data_file.get_array_properties(f"{hst_data}/x2i1559gl_wcp.fits", "EXTENSION1")
    for k, v in props.items():
        if k != "NAME":
            assert ARRAY_PROPS[k] == v
        else:
            assert v == '1'


@mark.hst
@mark.io
@mark.factory
def test_get_array_properties_extension_number3(hst_serverless_state, hst_data):
    props1 = data_file.get_array_properties(f"{hst_data}/x2i1559gl_wcp.fits", 1)
    props2 = data_file.get_array_properties(f"{hst_data}/x2i1559gl_wcp.fits", "1")
    for props in [props1, props2]:
        for k, v in props.items():
            if k != "NAME":
                assert ARRAY_PROPS[k] == v
            else:
                assert v == '1'
    

@mark.hst
@mark.io
@mark.factory
def test_get_array_properties_extension_number4(hst_serverless_state, hst_data):
    props1 = data_file.get_array_properties(f"{hst_data}/x2i1559gl_wcp.fits", "_WCP__1")
    props2 = data_file.get_array_properties(f"{hst_data}/x2i1559gl_wcp.fits", "1")
    names = [('_WCP', 1), '1']
    for i, props in enumerate([props1, props2]):
        for k, v in props.items():
            if k != "NAME":
                assert ARRAY_PROPS[k] == v
            else:
                assert v == names[i]
