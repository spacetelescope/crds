"""This module defines a limited abstract model for arbitrary reference file 
formats,  encapsulating the functionality which any new supported format is
required to support.

The original presumption of CRDS was that most files are in .fits format.
Subsequently,  support was added for GEIS files to support WFPC2.   
New formats are a strong possibility for JWST so the intent of this module is
to represent the least common denominator functionality here.
"""
from crds import utils

import pyfits
import geis

# =============================================================================

def get_header(name):
    """Return the complete unconditioned header dictionary of a reference file.
    """
    if geis.is_geis_header(name):
        return geis.get_header(name)
    else:
        return pyfits.getheader(name)
    
def get_conditioned_header(fname, parkeys=[]):
    """Return the complete conditioned header dictionary of a reference file,
    or optionally only the keys listed by `parkeys`.
    """
    header = get_header(fname)
    for key in parkeys or header:
        header[key] = utils.condition_value(header[key])
    return header