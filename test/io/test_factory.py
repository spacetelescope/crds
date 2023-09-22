from pytest import mark
import os
from pprint import pprint
import numpy as np

from crds import data_file
from crds.core import utils, log, exceptions
from crds.io import factory


def test_get_fits_type(jwst_serverless_state, jwst_data):
    t = factory.get_filetype(f"{jwst_data}/valid.fits")
    jwst_serverless_state.cleanup()
    assert t == 'fits'


def test_get_fits_type_opaque(jwst_serverless_state, jwst_data):
    t = factory.get_filetype(f"{jwst_data}/opaque_fts.tmp")
    jwst_serverless_state.cleanup()
    assert t == 'fits'

def test_get_asdf_type(jwst_serverless_state, jwst_data):
    t = factory.get_filetype(f"{jwst_data}/valid.asdf")
    jwst_serverless_state.cleanup()
    assert t == 'asdf'


def test_get_asdf_type_opaque(jwst_serverless_state, jwst_data):
    t = factory.get_filetype(f"{jwst_data}/opaque_asd.tmp")
    jwst_serverless_state.cleanup()
    assert t == 'asdf'


def test_get_geis_type(jwst_serverless_state, hst_data):
    t = factory.get_filetype(f"{hst_data}/e1b09593u.r1h")
    jwst_serverless_state.cleanup()
    assert t =='geis'


def test_get_geis_type_opaque(jwst_serverless_state, jwst_data):
    t = factory.get_filetype(f"{jwst_data}/opaque_gs.tmp")
    jwst_serverless_state.cleanup()
    assert t =='geis'   


def test_get_json_type(jwst_serverless_state, jwst_data):
    t = factory.get_filetype(f"{jwst_data}/valid.json")
    jwst_serverless_state.cleanup()
    assert t == 'json'


def test_get_json_type_opaque(jwst_serverless_state, jwst_data):
    t = factory.get_filetype(f"{jwst_data}/opaque_jsn.tmp")
    jwst_serverless_state.cleanup()
    assert t == 'json'


def test_get_yaml_type(jwst_serverless_state, jwst_data):
    t = factory.get_filetype(f"{jwst_data}/valid.yaml")
    jwst_serverless_state.cleanup()
    assert t == 'yaml'


def test_get_yaml_type_opaque(jwst_serverless_state, jwst_data):
    t = factory.get_filetype(f"{jwst_data}/opaque_yml.tmp")
    jwst_serverless_state.cleanup()
    assert t == 'yaml'


# ==================================================================================

# Factory module tests by way of crds.data_file (which uses io.factory.file_factory) 

def test_asdf_history_no_entries_description(jwst_serverless_state, jwst_data):
    header = data_file.get_header(f"{jwst_data}/niriss_ref_distortion.asdf")
    jwst_serverless_state.cleanup()
    assert header["HISTORY"] == 'UNDEFINED'


def test_asdf_history_no_entries_list(jwst_serverless_state, jwst_data):
    header = data_file.get_header(f"{jwst_data}/jwst_miri_distortion_0022.asdf")
    jwst_serverless_state.cleanup()
    assert header["HISTORY"] == "2017-06-02 14:29:39 :: DOCUMENT: MIRI-TN-00001-ETH_Iss2-1_Calibrationproduct_MRS_d2c.  New files created from CDP-6 with updated file structure and V2/V3 instead of XAN/YAN"


def test_asdf_history_with_entries(jwst_serverless_state, jwst_data):
    header = data_file.get_header(f"{jwst_data}/jwst_nirspec_ifupost_0004.asdf")
    jwst_serverless_state.cleanup()
    assert header["HISTORY"] == "2018-04-17 20:18:32 :: New version created from CV3 with updated file structure"


def test_get_array_properties_hdu_name(jwst_serverless_state, jwst_data, capsys):
    pprint(data_file.get_array_properties(f"{jwst_data}/x2i1559gl_wcp.fits", "_WCP"))
    out, _ = capsys.readouterr()
    jwst_serverless_state.cleanup()
    expected = """{'COLUMN_NAMES': ['OPT_ELEM',
                      'XC_RANGE',
                      'RESWIDTH',
                      'MAX_TIME_DIFF',
                      'STEPSIZE',
                      'XD_RANGE',
                      'BOX'],
     'DATA': None,
     'DATA_TYPE': {'BOX': '>i4',
                   'MAX_TIME_DIFF': '>f8',
                   'OPT_ELEM': '|S8',
                   'RESWIDTH': '>f8',
                   'STEPSIZE': '>i4',
                   'XC_RANGE': '>i4',
                   'XD_RANGE': '>i4'},
     'EXTENSION': 1,
     'KIND': 'TABLE',
     'NAME': '_WCP',
     'SHAPE': (4,)}"""
    assert expected in out

def test_get_array_properties_extension_number1(jwst_serverless_state, jwst_data, capsys):
    pprint(data_file.get_array_properties(f"{jwst_data}/x2i1559gl_wcp.fits", "EXT1"))
    out, _ = capsys.readouterr()
    jwst_serverless_state.cleanup()
    expected = """{'COLUMN_NAMES': ['OPT_ELEM',
                      'XC_RANGE',
                      'RESWIDTH',
                      'MAX_TIME_DIFF',
                      'STEPSIZE',
                      'XD_RANGE',
                      'BOX'],
     'DATA': None,
     'DATA_TYPE': {'BOX': '>i4',
                   'MAX_TIME_DIFF': '>f8',
                   'OPT_ELEM': '|S8',
                   'RESWIDTH': '>f8',
                   'STEPSIZE': '>i4',
                   'XC_RANGE': '>i4',
                   'XD_RANGE': '>i4'},
     'EXTENSION': 1,
     'KIND': 'TABLE',
     'NAME': '1',
     'SHAPE': (4,)}"""
    assert expected in out

def test_get_array_properties_extension_number2(jwst_serverless_state, jwst_data, capsys):
    pprint(data_file.get_array_properties(f"{jwst_data}/x2i1559gl_wcp.fits", "EXTENSION1"))
    out, _ = capsys.readouterr()
    jwst_serverless_state.cleanup()
    expected = """{'COLUMN_NAMES': ['OPT_ELEM',
                      'XC_RANGE',
                      'RESWIDTH',
                      'MAX_TIME_DIFF',
                      'STEPSIZE',
                      'XD_RANGE',
                      'BOX'],
     'DATA': None,
     'DATA_TYPE': {'BOX': '>i4',
                   'MAX_TIME_DIFF': '>f8',
                   'OPT_ELEM': '|S8',
                   'RESWIDTH': '>f8',
                   'STEPSIZE': '>i4',
                   'XC_RANGE': '>i4',
                   'XD_RANGE': '>i4'},
     'EXTENSION': 1,
     'KIND': 'TABLE',
     'NAME': '1',
     'SHAPE': (4,)}"""
    assert expected in out

def test_get_array_properties_extension_number1(jwst_serverless_state, jwst_data, capsys):
    pprint(data_file.get_array_properties(f"{jwst_data}/x2i1559gl_wcp.fits", "EXT1"))
    out, _ = capsys.readouterr()
    jwst_serverless_state.cleanup()
    expected = """{'COLUMN_NAMES': ['OPT_ELEM',
                      'XC_RANGE',
                      'RESWIDTH',
                      'MAX_TIME_DIFF',
                      'STEPSIZE',
                      'XD_RANGE',
                      'BOX'],
     'DATA': None,
     'DATA_TYPE': {'BOX': '>i4',
                   'MAX_TIME_DIFF': '>f8',
                   'OPT_ELEM': '|S8',
                   'RESWIDTH': '>f8',
                   'STEPSIZE': '>i4',
                   'XC_RANGE': '>i4',
                   'XD_RANGE': '>i4'},
     'EXTENSION': 1,
     'KIND': 'TABLE',
     'NAME': '1',
     'SHAPE': (4,)}"""
    assert expected in out

def test_get_array_properties_extension_number2(jwst_serverless_state, jwst_data, capsys):
    pprint(data_file.get_array_properties(f"{jwst_data}/x2i1559gl_wcp.fits", "EXTENSION1"))
    out, _ = capsys.readouterr()
    jwst_serverless_state.cleanup()
    expected = """{'COLUMN_NAMES': ['OPT_ELEM',
                      'XC_RANGE',
                      'RESWIDTH',
                      'MAX_TIME_DIFF',
                      'STEPSIZE',
                      'XD_RANGE',
                      'BOX'],
     'DATA': None,
     'DATA_TYPE': {'BOX': '>i4',
                   'MAX_TIME_DIFF': '>f8',
                   'OPT_ELEM': '|S8',
                   'RESWIDTH': '>f8',
                   'STEPSIZE': '>i4',
                   'XC_RANGE': '>i4',
                   'XD_RANGE': '>i4'},
     'EXTENSION': 1,
     'KIND': 'TABLE',
     'NAME': '1',
     'SHAPE': (4,)}"""
    assert expected in out


def test_get_array_properties_extension_number3(jwst_serverless_state, jwst_data, capsys):
    pprint(data_file.get_array_properties(f"{jwst_data}/x2i1559gl_wcp.fits", 1))
    out1, _ = capsys.readouterr()
    expected = """{'COLUMN_NAMES': ['OPT_ELEM',
                      'XC_RANGE',
                      'RESWIDTH',
                      'MAX_TIME_DIFF',
                      'STEPSIZE',
                      'XD_RANGE',
                      'BOX'],
     'DATA': None,
     'DATA_TYPE': {'BOX': '>i4',
                   'MAX_TIME_DIFF': '>f8',
                   'OPT_ELEM': '|S8',
                   'RESWIDTH': '>f8',
                   'STEPSIZE': '>i4',
                   'XC_RANGE': '>i4',
                   'XD_RANGE': '>i4'},
     'EXTENSION': 1,
     'KIND': 'TABLE',
     'NAME': '1',
     'SHAPE': (4,)}"""
    pprint(data_file.get_array_properties(f"{jwst_data}/x2i1559gl_wcp.fits", "1"))
    out2, _ = capsys.readouterr()
    jwst_serverless_state.cleanup()
    assert expected in out1
    assert expected in out2

def test_get_array_properties_extension_number4(jwst_serverless_state, jwst_data, capsys):
    pprint(data_file.get_array_properties(f"{jwst_data}/x2i1559gl_wcp.fits", "_WCP__1"))
    out, _ = capsys.readouterr()
    jwst_serverless_state.cleanup()
    expected = """{'COLUMN_NAMES': ['OPT_ELEM',
                      'XC_RANGE',
                      'RESWIDTH',
                      'MAX_TIME_DIFF',
                      'STEPSIZE',
                      'XD_RANGE',
                      'BOX'],
     'DATA': None,
     'DATA_TYPE': {'BOX': '>i4',
                   'MAX_TIME_DIFF': '>f8',
                   'OPT_ELEM': '|S8',
                   'RESWIDTH': '>f8',
                   'STEPSIZE': '>i4',
                   'XC_RANGE': '>i4',
                   'XD_RANGE': '>i4'},
     'EXTENSION': 1,
     'KIND': 'TABLE',
     'NAME': ('_WCP', 1),
     'SHAPE': (4,)}"""
    assert expected in out
 

def test_get_array_properties_extension_number5(jwst_serverless_state, jwst_data, capsys):
    pprint(data_file.get_array_properties(f"{jwst_data}/x2i1559gl_wcp.fits", "1"))
    out, _ = capsys.readouterr()
    jwst_serverless_state.cleanup()
    expected = """{'COLUMN_NAMES': ['OPT_ELEM',
                      'XC_RANGE',
                      'RESWIDTH',
                      'MAX_TIME_DIFF',
                      'STEPSIZE',
                      'XD_RANGE',
                      'BOX'],
     'DATA': None,
     'DATA_TYPE': {'BOX': '>i4',
                   'MAX_TIME_DIFF': '>f8',
                   'OPT_ELEM': '|S8',
                   'RESWIDTH': '>f8',
                   'STEPSIZE': '>i4',
                   'XC_RANGE': '>i4',
                   'XD_RANGE': '>i4'},
     'EXTENSION': 1,
     'KIND': 'TABLE',
     'NAME': '1',
     'SHAPE': (4,)}"""
    assert expected in out
