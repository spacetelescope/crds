from __future__ import division # confidence high
from __future__ import with_statement
from __future__ import print_function
from __future__ import absolute_import

# ==================================================================================

import os

# ==================================================================================
import numpy as np

from nose.tools import assert_raises, assert_true

# ==================================================================================

from crds.core import utils, log, exceptions
from crds.io import factory, tables

from crds.tests import test_config

# ==================================================================================

def test_get_fits_type():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> factory.get_filetype("data/valid.fits")
    'fits'
    >>> test_config.cleanup(old_state)
    """

def test_get_fits_type_opaque():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> factory.get_filetype("data/opaque_fts.tmp")
    'fits'
    >>> test_config.cleanup(old_state)
    """

def test_get_asdf_type():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> factory.get_filetype("data/valid.asdf")
    'asdf'
    >>> test_config.cleanup(old_state)
    """

def test_get_asdf_type_opaque():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> factory.get_filetype("data/opaque_asd.tmp")
    'asdf'
    >>> test_config.cleanup(old_state)
    """

def test_get_geis_type():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> factory.get_filetype("data/e1b09593u.r1h")
    'geis'
    >>> test_config.cleanup(old_state)
    """

def test_get_geis_type_opaque():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> factory.get_filetype("data/opaque_gs.tmp")
    'geis'
    >>> test_config.cleanup(old_state)
    """

def test_get_json_type():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> factory.get_filetype("data/valid.json")
    'json'
    >>> test_config.cleanup(old_state)
    """

def test_get_json_type_opaque():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> factory.get_filetype("data/opaque_jsn.tmp")
    'json'
    >>> test_config.cleanup(old_state)
    """

def test_get_yaml_type():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> factory.get_filetype("data/valid.yaml")
    'yaml'
    >>> test_config.cleanup(old_state)
    """

def test_get_yaml_type_opaque():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> factory.get_filetype("data/opaque_yml.tmp")
    'yaml'
    >>> test_config.cleanup(old_state)
    """

def test_fits_table():
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
    
    >>> tab.rows[0]
    (1, 'FORWARD', 'F475W', 'CLEAR2L', 4096, 2048, 2048.0, 1024.0, 260.86691, 198.35629, 0.050000001, 0.0022632401, 0.049226411, 8.8356778e-08, -3.5535871e-07, 4.119137e-07, 2.531863e-12, -2.6421639e-11, -6.091743e-12, -2.302028e-11, 6.8711719e-15, -1.057525e-15, 4.884969e-15, 1.564524e-15, 9.3779168e-16, 0.04858401, 0.0021281759, -4.700963e-07, 2.949148e-07, -1.2576361e-07, -1.890378e-11, -2.340621e-12, -2.209152e-11, 3.51687e-12, -8.4106374e-15, 2.246166e-15, -4.855206e-15, -1.634969e-15, -8.0853678e-16)
    
    >>> tab.colnames[0]
    'DETCHIP'
    
    >>> tab.columns['DETCHIP'][:1]
    (1,)
    >>> test_config.cleanup(old_state)
    """

def test_csv_table():
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
    
    >>> tab.rows[0]
    (3102, 0.32000000000000001, 4167, 4085, 'Q1250+568-A')
    
    >>> tab.colnames[0]
    'OBSID'
    
    >>> tab.columns['OBSID'][0]
    3102
    >>> test_config.cleanup(old_state)
    """    

# ==================================================================================

def main():
    """Run module tests,  for now just doctests only."""
    from crds.tests import test_io, tstmod
    return tstmod(test_io)

if __name__ == "__main__":
    print(main())

