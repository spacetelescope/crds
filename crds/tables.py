"""This module defines an abstract API for tables used in CRDS file certification row checks
and bestrefs table effects determinations.  In both cases it basically provides an iterator
over the segments/hdus for a table file and a simple object which gives readonly row acess to
each segment.
"""
import os.path

from astropy.io import fits
from astropy import table

from crds import utils, log

def ntables(filename):
    """Return the number of segments / hdus in `filename`."""
    if filename.endswith(".fits"):
        with fits.open(filename) as hdus:
            return len(hdus) - 1
    else:
        return 1

@utils.cached
def tables(filename):
    """Return [ SimpleTable(filename, segment), ... ] for each table segment in filename.
    
    This function is self-cached.    Clear the cache using clear_cache().
    """
    if filename.endswith(".fits"):
        with fits.open(filename) as hdus:
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
        if filename.endswith(".fits"):
            astropy_table = table.Table.read(filename, hdu=segment)
        else:
            astropy_table = table.Table.read(filename)
        self.rows = tuple(row for row in astropy_table)   # readonly
        self._columns = None  # dynamic,  independent of astropy
        self.colnames = tuple(name for name in astropy_table.columns)
        self.basename = os.path.basename(filename)
        log.verbose("Creating", repr(self), verbosity=60)
        
    @property
    def columns(self):
        """Based on the row tuples,  create columns dict dynamically.  This permits closing astropy Table during __init__.
        
        Retuns { colname : column, ... }
        """
        if self._columns is None:
            self._columns = dict(zip(self.colnames, zip(*self.rows)))
        return self._columns
        
    def __repr__(self):
        return (self.__class__.__name__ + "(" + repr(self.filename) + ", " + repr(self.segment) + ", colnames=" +
                repr(self.colnames) + ", nrows=" + str(len(self.rows)) + ")")
    
    
