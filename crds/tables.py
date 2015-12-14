"""This module defines an abstract API for tables used in CRDS file certification row checks
and bestrefs table effects determinations.  In both cases it basically provides a list of 
SimpleTable objects,  one per segment/hdu for a table file and a simple object which gives 
readonly row acess to each segment.

----------------------------------------------------------------------------------
Demo and test the basic API for FITS tables:

>>> FITS_FILE = _HERE  + "/tests/data/v8q14451j_idc.fits"
>>> ntables(FITS_FILE)
1

>>> for tab in tables(FITS_FILE):
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


----------------------------------------------------------------------------------
Demo and test the API for non-FITS formats using astropy format guessing:

>>> CSV_FILE = _HERE + "/tests/data/ascii_tab.csv"
>>> ntables(CSV_FILE)
1

>>> for tab in tables(CSV_FILE):
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
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import os.path

from astropy import table

from crds import utils, log, data_file

_HERE = os.path.dirname(__file__) or "."

def ntables(filename):
    """Return the number of segments / hdus in `filename`."""
    if filename.endswith(".fits"):
        with data_file.fits_open(filename) as hdus:
            return len(hdus) - 1
    else:
        return 1

@utils.cached
def tables(filename):
    """Return [ SimpleTable(filename, segment), ... ] for each table segment in filename.
    
    This function is self-cached.    Clear the cache using clear_cache().
    """
    if filename.endswith(".fits"):
        with data_file.fits_open(filename) as hdus:
            return [ SimpleTable(filename, i+1) for i in range(len(hdus)-1) ]
    else:
        return [ SimpleTable(filename, segment=1) ]
    
def clear_cache():
    """Clear the cached values for the tables interface."""
    tables.cache.clear()


class SimpleTable(object):
    """A simple class to encapsulate astropy tables for basic CRDS readonly table row and colname access."""
    def __init__(self, filename, segment=1):
        self.filename = filename
        self.segment = segment
        self.basename = os.path.basename(filename)
        self._columns = None  # dynamic,  independent of astropy
        if filename.endswith(".fits"):
            with data_file.fits_open(filename) as hdus:
                tab = hdus[segment].data
                self.colnames = tuple(name.upper() for name in tab.columns.names)
                self.rows = tuple(tuple(row) for row in tab)   # readonly
        else:
            tab = table.Table.read(filename)
            self.colnames = tuple(name.upper() for name in tab.columns)
            self.rows = tuple(tuple(row) for row in tab)   # readonly
        log.verbose("Creating", repr(self), verbosity=60)
        
    @property
    def columns(self):
        """Based on the row tuples,  create columns dict dynamically.  This permits closing astropy Table during __init__.
        
        Retuns { colname : column, ... }
        """
        if self._columns is None:
            self._columns = dict(list(zip(self.colnames, list(zip(*self.rows)))))
        return self._columns
        
    def __repr__(self):
        return (self.__class__.__name__ + "(" + repr(self.basename) + ", " + repr(self.segment) + ", colnames=" +
                repr(self.colnames) + ", nrows=" + str(len(self.rows)) + ")")
    
    

def test():
    import doctest, crds.tables
    return doctest.testmod(crds.tables)

if __name__ == "__main__":
    print(test())
