"""This module defines a limited abstract model for arbitrary reference file 
formats,  encapsulating the functionality which any new supported format is
required to support.

The original presumption of CRDS was that most files are in .fits format.
Subsequently,  support was added for GEIS files to support WFPC2.   
New formats are a strong possibility for JWST so the intent of this module is
to represent the least common denominator functionality here.
"""
from crds import utils, log

import pyfits
import geis

# =============================================================================

def get_conditioned_header(fname, needed_keys=[]):
    """Return the complete conditioned header dictionary of a reference file,
    or optionally only the keys listed by `needed_keys`.
    """
    header = get_header(fname, needed_keys)
    for key in needed_keys or header:
        header[key] = utils.condition_value(header[key])
    return header

def get_header(name, needed_keys=[]):
    """Return the complete unconditioned header dictionary of a reference file.
    """
    if geis.is_geis_header(name):
        return geis.get_header(name)
    else:
        return get_fits_header_union(name, needed_keys)
    
def get_fits_header_union(fname, needed_keys=[]):
    """Get the union of keywords from all header extensions of FITS
    file `fname`.  In the case of collisions, keep the first value
    found as extensions are loaded in numerical order.
    """
    import pyfits
    union = {}
    get_all_keys = not needed_keys
    for hdu in pyfits.open(fname):
        for key in hdu.header:
            if get_all_keys or key in needed_keys:
                newval = hdu.header[key]
                if key not in union:
                    union[key] = newval
                elif union[key] != newval and key in needed_keys:
                    log.warning("Header union collision on", repr(key),
                                repr(union[key]), "precedes",repr(newval))
    for key in needed_keys:
        if key not in union:
            union[key] = "NOT PRESENT"
    return union
