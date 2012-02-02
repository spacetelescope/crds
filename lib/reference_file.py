"""This module defines a limited abstract model for arbitrary reference file 
formats,  encapsulating the functionality which any new supported format is
required to support.

The original presumption of CRDS was that most files are in .fits format.
Subsequently,  support was added for GEIS files to support WFPC2.   
New formats are a strong possibility for JWST so the intent of this module is
to represent the least common denominator functionality here.
"""
import pyfits
import geis

# =============================================================================

def get_header(name):
    """Return the complete unconditioned header dictionary of a geis or fits file.
    """
    if geis.is_geis_header(name):
        return geis.get_header(name)
    else:
        return pyfits.getheader(name)

