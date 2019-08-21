import os
from pprint import pprint

# ==================================================================================
import numpy as np

from nose.tools import assert_raises, assert_true

# ==================================================================================

from crds import data_file
from crds.core import utils, log, exceptions
from crds.io import factory, tables

from crds.tests import test_config

# ==================================================================================

def dt_get_fits_type():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> factory.get_filetype("data/valid.fits")
    'fits'
    >>> test_config.cleanup(old_state)
    """

def dt_get_fits_type_opaque():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> factory.get_filetype("data/opaque_fts.tmp")
    'fits'
    >>> test_config.cleanup(old_state)
    """

def dt_get_asdf_type():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> factory.get_filetype("data/valid.asdf")
    'asdf'
    >>> test_config.cleanup(old_state)
    """

def dt_get_asdf_type_opaque():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> factory.get_filetype("data/opaque_asd.tmp")
    'asdf'
    >>> test_config.cleanup(old_state)
    """

def dt_get_geis_type():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> factory.get_filetype("data/e1b09593u.r1h")
    'geis'
    >>> test_config.cleanup(old_state)
    """

def dt_get_geis_type_opaque():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> factory.get_filetype("data/opaque_gs.tmp")
    'geis'
    >>> test_config.cleanup(old_state)
    """

def dt_get_json_type():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> factory.get_filetype("data/valid.json")
    'json'
    >>> test_config.cleanup(old_state)
    """

def dt_get_json_type_opaque():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> factory.get_filetype("data/opaque_jsn.tmp")
    'json'
    >>> test_config.cleanup(old_state)
    """

def dt_get_yaml_type():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> factory.get_filetype("data/valid.yaml")
    'yaml'
    >>> test_config.cleanup(old_state)
    """

def dt_get_yaml_type_opaque():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> factory.get_filetype("data/opaque_yml.tmp")
    'yaml'
    >>> test_config.cleanup(old_state)
    """

def dt_fits_table():
    """
    ----------------------------------------------------------------------------------
    Demo and test the basic API for FITS tables:

    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> FITS_FILE = "data/v8q14451j_idc.fits"
    >>> tables.ntables(FITS_FILE)
    1

    >>> for tab in tables.tables(FITS_FILE):
    ...     print(repr(tab))
    SimpleTable('v8q14451j_idc.fits', 1, colnames=('DETCHIP', 'DIRECTION', 'FILTER1', 'FILTER2', 'XSIZE', 'YSIZE', 'XREF', 'YREF', 'V2REF', 'V3REF', 'SCALE', 'CX10', 'CX11', 'CX20', 'CX21', 'CX22', 'CX30', 'CX31', 'CX32', 'CX33', 'CX40', 'CX41', 'CX42', 'CX43', 'CX44', 'CY10', 'CY11', 'CY20', 'CY21', 'CY22', 'CY30', 'CY31', 'CY32', 'CY33', 'CY40', 'CY41', 'CY42', 'CY43', 'CY44'), nrows=694)

    >>> tab.segment
    1

    >>> tab.rows[0]     # doctest: +ELLIPSIS
    (1, 'FORWARD', 'F475W', 'CLEAR2L', 4096, 2048, ...

    >>> len(tab.rows[0]) == len(tab.colnames)
    True

    >>> tab.colnames[0]
    'DETCHIP'

    >>> tab.columns['DETCHIP'][:1]
    (1,)
    >>> test_config.cleanup(old_state)
    """

def dt_csv_table():
    """
    ----------------------------------------------------------------------------------
    Demo and test the API for non-FITS formats using astropy format guessing:

    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> CSV_FILE = "data/ascii_tab.csv"
    >>> tables.ntables(CSV_FILE)
    1

    >>> for tab in tables.tables(CSV_FILE):
    ...     print(repr(tab))
    SimpleTable('ascii_tab.csv', 1, colnames=('OBSID', 'REDSHIFT', 'X', 'Y', 'OBJECT'), nrows=2)

    >>> tab.segment
    1

    >>> tab.rows[0]    # doctest: +ELLIPSIS
    (3102, 0.32..., 4167, 4085, 'Q1250+568-A')

    >>> tab.colnames[0]
    'OBSID'

    >>> tab.columns['OBSID'][0]
    3102
    >>> test_config.cleanup(old_state)
    """

# ==================================================================================

def dt_asdf_history_no_entries_description():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> header = data_file.get_header("data/niriss_ref_distortion.asdf")
    >>> header["HISTORY"]
    'UNDEFINED'
    >>> test_config.cleanup(old_state)
    """

def dt_asdf_history_no_entries_list():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> header = data_file.get_header("data/jwst_miri_distortion_0022.asdf")
    >>> print(header["HISTORY"])
    2017-06-02 14:29:39 :: DOCUMENT: MIRI-TN-00001-ETH_Iss2-1_Calibrationproduct_MRS_d2c.  New files created from CDP-6 with updated file structure and V2/V3 instead of XAN/YAN
    >>> test_config.cleanup(old_state)
    """

def dt_asdf_history_with_entries():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> header = data_file.get_header("data/jwst_nirspec_ifupost_0004.asdf")
    >>> print(header["HISTORY"])
    2018-04-17 20:18:32 :: New version created from CV3 with updated file structure
    >>> test_config.cleanup(old_state)
    """

def dt_get_array_properties_hdu_name():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> pprint(data_file.get_array_properties("data/x2i1559gl_wcp.fits", "_WCP"))
    {'COLUMN_NAMES': ['OPT_ELEM',
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
     'SHAPE': (4,)}
    >>> test_config.cleanup(old_state)
    """

def dt_get_array_properties_extension_number1():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> pprint(data_file.get_array_properties("data/x2i1559gl_wcp.fits", "EXT1"))
    {'COLUMN_NAMES': ['OPT_ELEM',
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
     'SHAPE': (4,)}
    >>> test_config.cleanup(old_state)
    """

def dt_get_array_properties_extension_number2():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> pprint(data_file.get_array_properties("data/x2i1559gl_wcp.fits", "EXTENSION1"))
    {'COLUMN_NAMES': ['OPT_ELEM',
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
     'SHAPE': (4,)}
    >>> test_config.cleanup(old_state)
    """

def dt_get_array_properties_extension_number1():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> pprint(data_file.get_array_properties("data/x2i1559gl_wcp.fits", "EXT1"))
    {'COLUMN_NAMES': ['OPT_ELEM',
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
     'SHAPE': (4,)}
    >>> test_config.cleanup(old_state)
    """

def dt_get_array_properties_extension_number2():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> pprint(data_file.get_array_properties("data/x2i1559gl_wcp.fits", "EXTENSION1"))
    {'COLUMN_NAMES': ['OPT_ELEM',
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
     'SHAPE': (4,)}
    >>> test_config.cleanup(old_state)
    """


def dt_get_array_properties_extension_number3():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> pprint( data_file.get_array_properties("data/x2i1559gl_wcp.fits", 1))
    {'COLUMN_NAMES': ['OPT_ELEM',
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
     'SHAPE': (4,)}
    >>> test_config.cleanup(old_state)
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> pprint(data_file.get_array_properties("data/x2i1559gl_wcp.fits", "1"))
    {'COLUMN_NAMES': ['OPT_ELEM',
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
     'SHAPE': (4,)}
    >>> test_config.cleanup(old_state)
    """

def dt_get_array_properties_extension_number3():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> pprint( data_file.get_array_properties("data/x2i1559gl_wcp.fits", "_WCP__1"))
    {'COLUMN_NAMES': ['OPT_ELEM',
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
     'SHAPE': (4,)}
    >>> test_config.cleanup(old_state)

    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> pprint(data_file.get_array_properties("data/x2i1559gl_wcp.fits", "1"))
    {'COLUMN_NAMES': ['OPT_ELEM',
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
     'SHAPE': (4,)}
    >>> test_config.cleanup(old_state)
    """

# ==================================================================================

def main():
    """Run module tests,  for now just doctests only."""
    from crds.tests import test_io, tstmod
    return tstmod(test_io)

if __name__ == "__main__":
    print(main())
