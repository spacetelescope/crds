"""This module defines an abstract API for tables used in CRDS file certification row checks
and bestrefs table effects determinations.  In both cases it basically provides an iterator
over the segments/hdus for a table file and a simple object which gives readonly row acess to
each segment.
"""
import os.path

from astropy.io import fits
from astropy import table

def ntables(filename):
    """Return the number of segments / hdus in `filename`."""
    if filename.endswith(".fits"):
        return len(fits.open("filename","r")) - 1
    else:
        return 1

def tables(filename):
    """Iterate over all the sections/extensions of filename returning an astropy Table for each."""
    if filename.endswith(".fits"):
        for i in range(len(fits.open(filename, "r"))):
            yield SimpleTable(filename, i+1)
    else:
        yield SimpleTable(filename)


class SimpleTable(object):
    """A simple class to encapsulate astropy tables for basic CRDS readonly table access."""
    def __init__(self, filename, segment=1):
        self.filename = filename
        self.segment = segment
        if filename.endswith(".fits"):
            astropy_table = table.Table.read(filename, hdu=segment)
        else:
            astropy_table = table.Table.read(filename)
        self.rows = [tuple(row) for row in astropy_table]
        self.cols = [col for col in astropy_table.columns]
        self.colnames = tuple(astropy_table.columns)
        self.basefile = os.path.basename(filename)
        
    def __repr__(self):
        return self.__class__.__name__ + "(" + repr(self.filename) + ", " + repr(self.segment) + ")"
    
    