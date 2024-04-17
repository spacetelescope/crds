from pytest import mark
from crds.io import tables


@mark.hst
@mark.io
@mark.tables
def test_fits_table(hst_serverless_state, hst_data):
    """
    ----------------------------------------------------------------------------------
    Demo and test the basic API for FITS tables:
    """
    FITS_FILE = f"{hst_data}/v8q14451j_idc.fits"
    assert tables.ntables(FITS_FILE) == 1
    tab = tables.tables(FITS_FILE)[0]
    assert tab.segment == 1
    assert tab.rows[0][:6] == (1, 'FORWARD', 'F475W', 'CLEAR2L', 4096, 2048)
    assert len(tab.rows[0]) == len(tab.colnames)
    assert tab.colnames[0] == 'DETCHIP'
    assert tab.columns['DETCHIP'][:1] == (1,)
    expected = """SimpleTable('v8q14451j_idc.fits', 1, colnames=('DETCHIP', 'DIRECTION', 'FILTER1', 'FILTER2', 'XSIZE', 'YSIZE', 'XREF', 'YREF', 'V2REF', 'V3REF', 'SCALE', 'CX10', 'CX11', 'CX20', 'CX21', 'CX22', 'CX30', 'CX31', 'CX32', 'CX33', 'CX40', 'CX41', 'CX42', 'CX43', 'CX44', 'CY10', 'CY11', 'CY20', 'CY21', 'CY22', 'CY30', 'CY31', 'CY32', 'CY33', 'CY40', 'CY41', 'CY42', 'CY43', 'CY44'), nrows=694)"""
    assert str(tab) == expected


@mark.hst
@mark.io
@mark.tables
def test_csv_table(hst_serverless_state, hst_data):
    """
    ----------------------------------------------------------------------------------
    Demo and test the API for non-FITS formats using astropy format guessing:
    """
    CSV_FILE = f"{hst_data}/ascii_tab.csv"
    assert tables.ntables(CSV_FILE) == 1
    tab = tables.tables(CSV_FILE)[0]
    assert tab.segment == 1
    assert tab.rows[0] == (3102, 0.32, 4167, 4085, 'Q1250+568-A')
    assert tab.colnames[0] == 'OBSID'
    assert tab.columns['OBSID'][0] == 3102
    expected = "SimpleTable('ascii_tab.csv', 1, colnames=('OBSID', 'REDSHIFT', 'X', 'Y', 'OBJECT'), nrows=2)"
    assert str(tab) == expected
