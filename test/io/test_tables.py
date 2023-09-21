from pytest import mark
import os
from pprint import pprint
import numpy as np

from crds import data_file
from crds.core import utils, log, exceptions
from crds.io import factory, tables


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