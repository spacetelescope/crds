"""This module defines an abstract API for tables used in CRDS file certification row checks
and bestrefs table effects determinations.  In both cases it basically provides a list of
SimpleTable objects,  one per segment/hdu for a table file and a simple object which gives
readonly row acess to each segment.
"""

import os.path

from astropy import table

from crds.core import utils, log
from crds import data_file

_HERE = os.path.dirname(__file__) or "."

def ntables(filename):
    """Return the number of segments / hdus in `filename`."""
    if filename.endswith(".fits"):
        tables = 0
        with data_file.fits_open(filename) as hdus:
            for i,hdu in enumerate(hdus):
                if "TABLEHDU" in hdu.__class__.__name__.upper():
                    tables += 1
        return tables
    else:
        return 1

@utils.cached
def tables(filename):
    """Return [ SimpleTable(filename, segment), ... ] for each table segment in filename.

    This function is self-cached.    Clear the cache using clear_cache().
    """
    if filename.endswith(".fits"):
        tables = []
        with data_file.fits_open(filename) as hdus:
            for i,hdu in enumerate(hdus):
                classname = hdu.__class__.__name__.upper()
                if "TABLEHDU" in classname:
                    tables.append(SimpleTable(filename, i))
                    if classname == "TABLEHDU":
                        log.warning("ASCII Table detected in HDU#", str(i) +
                                    ".  Particularly for HST, verify that it should not be a BIN Table HDU.")
        return tables
    else:
        return [ SimpleTable(filename, segment=1) ]

def clear_cache():
    """Clear the cached values for the tables interface."""
    tables.cache.clear()


class SimpleTable:
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
    import doctest, crds.io.tables
    return doctest.testmod(crds.io.tables)

if __name__ == "__main__":
    print(test())
