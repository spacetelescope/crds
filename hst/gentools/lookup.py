"""This module defines lookup code tailored to the HST rmaps.
"""
import sys
import cPickle
import pprint
import os.path

import pyfits

import crds.log as log
import crds.utils as utils
import crds.hst.gentools.keyval as keyval

# ===================================================================

HEADER_CACHE = {}

def get_unconditioned_header_union(fname):
    """Handle initial or cached fetch of unconditioned header values.
    """
    if fname in HEADER_CACHE:
        log.verbose("Cache hit:",repr(fname))
        return HEADER_CACHE[fname]
    log.verbose("Cache miss:",repr(fname))
    union = HEADER_CACHE[fname] = utils.get_header_union(fname)
    return union

def get_header_union(fname):
    """Return the FITS header of `fname` as a dict,  successively
    adding all extension headers to the dict.   Cache the combined
    header in case this function is called more than once on the
    same FITS file.

    Each keyword value is "conditioned" into a
    canonical form which smoothes over inconsistencies.
    See rmap.condition_value() for details.
    """
    header = get_unconditioned_header_union(fname)
    for key, value in header.items():
        header[key] = keyval.condition_value(value)
    return header

HERE = os.path.dirname(__file__) or "./"

def load_header_cache():
    """Load the global HEADER_CACHE which prevents pyfits header reads for calls
    to get_header_union() when a file as already been visited.
    """
    global HEADER_CACHE
    try:
        HEADER_CACHE = eval(open(HERE + "/header_cache").read())
        # HEADER_CACHE = cPickle.load(open("header_cache"))
    except Exception, e:
        log.info("header_cache failed to load:", str(e))

def save_header_cache():
    """Save the global HEADER_CACHE to store the FITS header unions of any newly visited files.
    """
    open(HERE + "/header_cache", "w+").write(pprint.pformat(HEADER_CACHE))
    # cPickle.dump(HEADER_CACHE, open("header_cache","w+"))


