"""This module defines functions for loading and using CDBS .tpn files.

    *.tpn
    *_ld.tpn
    
These files are all related to checking reference files and CRDS mappings.   This
file is used to support crds.certify using a protocol which maps references and mappings
onto lists of TpnInfo objects which describe parameter constraints.   The protocol
is implemented as an observatory specific "plugin" through the locator.py module.

"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import os.path

from crds.core import rmap, utils
from crds.certify import generic_tpn
from crds.hst import TYPES

# =============================================================================

HERE = os.path.dirname(__file__) or "./"

def _tpn_path(args):
    return os.path.join(HERE, "tpns", args[0])

# =============================================================================
# Plugin-functions for this observatory,  accessed via locator.py

@utils.cached
def get_tpninfos(*args):
    """Load the list of TPN_info tuples corresponding to *args from it's .tpn file.
    Nominally args are (instrument, filekind),  but *args should be supported to 
    handle *key for any key returned by reference_name_to_validator_key.   In particular,
    for some subtypes,  *args will be (tpn_filename,).
    """
    return generic_tpn.load_tpn(_tpn_path(args))

@utils.cached
def get_tpn_text(*args):
    """Return the .tpn text corresponding to *args.
    Nominally args are (instrument, filekind),  but *args should be supported to 
    handle *key for any key returned by reference_name_to_validator_key.   In particular,
    for some subtypes,  *args will be (tpn_filename,).
    """
    with open(_tpn_path(args)) as pfile:
        text = pfile.read()
    return text

def reference_name_to_tpn_text(filename):
    """Given reference `filename`,  return the text of the corresponding .tpn"""
    path = rmap.locate_file(filename, "hst")
    key = TYPES.reference_name_to_tpn_key(path)
    return get_tpn_text(*key)

def reference_name_to_ld_tpn_text(filename):
    """Given reference `filename`,  return the text of the corresponding _ld.tpn"""
    path = rmap.locate_file(filename, "hst")
    key = TYPES.reference_name_to_ld_tpn_key(path)
    return get_tpn_text(*key)

