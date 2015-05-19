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

from crds import rmap, utils
from crds.certify import TpnInfo
from crds.hst import TYPES

# =============================================================================

HERE = os.path.dirname(__file__) or "./"

# =============================================================================
#  HST CDBS .tpn and _ld.tpn reader

def _load_tpn_lines(fname):
    """Load the lines of a CDBS .tpn file,  ignoring #-comments, blank lines,
     and joining lines ending in \\.
    """
    lines = []
    append = False
    with open(fname) as pfile:
        for line in pfile:
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            if append:
                lines[-1] = lines[-1][:-1].strip() + line
            else:
                lines.append(line)
            append = line.endswith("\\")
    return lines


def _fix_quoted_whitespace(line):
    """Replace spaces and tabs which appear inside quotes in `line` with
    underscores,  and return it.
    """
    i = 0
    while i < len(line):
        char = line[i]
        i += 1
        if char != '"':
            continue
        quote = char
        while i < len(line):
            char = line[i]
            i += 1
            if char == quote:
                break
            if char in " \t":
                line = line[:i-1] + "_" + line[i:]
    return line


def _load_tpn(fname):
    """Load a TPN file and return it as a list of TpnInfo objects
    describing keyword requirements including acceptable values.
    """
    tpn = []
    for line in _load_tpn_lines(fname):
        line = _fix_quoted_whitespace(line)
        items = line.split()
        if len(items) == 4:
            name, keytype, datatype, presence = items
            values = []
        else:
            name, keytype, datatype, presence, values = items
            values = values.split(",")
            values = [v.upper() for v in values]
        tpn.append(TpnInfo(name, keytype, datatype, presence, tuple(values)))
    return tpn

# =============================================================================
# Plugin-functions for this observatory,  accessed via locator.py


@utils.cached
def get_tpninfos(*args):
    """Load the list of TPN_info tuples corresponding to *args from it's .tpn file.
    Nominally args are (instrument, filekind),  but *args should be supported to 
    handle *key for any key returned by reference_name_to_validator_key.   In particular,
    for some subtypes,  *args will be (tpn_filename,).
    """
    return _load_tpn(os.path.join(HERE, "tpns", args[0]))

@utils.cached
def get_tpn_text(*args):
    """Return the .tpn text corresponding to *args.
    Nominally args are (instrument, filekind),  but *args should be supported to 
    handle *key for any key returned by reference_name_to_validator_key.   In particular,
    for some subtypes,  *args will be (tpn_filename,).
    """
    with open(os.path.join(HERE, "tpns", args[0])) as pfile:
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

