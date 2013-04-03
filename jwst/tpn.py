"""This module defines functions for loading JWST's .tpn files which
describe reference parameters and their values.   The .tpn files are used to
validate headers or tables and list the parameters each filekind must define
in an rmap.
"""
import sys
import os.path
import pprint

from crds import rmap, log, utils, data_file
from crds.certify import TpnInfo

# =============================================================================

HERE = os.path.dirname(__file__) or "./"

# =============================================================================

def _evalfile_with_fail(filename):
    """Evaluate and return a dictionary file,  returning {} if the file
    cannot be found.
    """
    if os.path.exists(filename):
        result = utils.evalfile(filename)
    else:
        result = {}
    return result

# =============================================================================

def _load_tpn_lines(fname):
    """Load the lines of a CDBS .tpn file,  ignoring #-comments, blank lines,
     and joining lines ending in \\.
    """
    lines = []
    append = False
    for line in open(fname):
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


def _tpn_filepath(instrument, filekind):
    """Return the full path for the .tpn file corresponding to `instrument` and 
    `filekind`,  the CRDS name for the header keyword which refers to this 
    reference.
    """
    tpn_filename = "jwst_{}_{}.tpn".format(instrument, filekind)
    path = os.path.join(HERE, "tpns", tpn_filename)
    return path

def get_tpninfos(instrument, filekind):
    """Load the listof TPN info tuples corresponding to `instrument` and 
    `filekind` from it's .tpn file.
    """
    try:
        return _load_tpn(_tpn_filepath(instrument, filekind))
    except IOError:
        log.verbose_warning("no TPN for", instrument, filekind)
        return []

# =============================================================================

def reference_name_to_tpninfos(key):
    """Given a reference cache `key` for a reference's Validator,  return the 
    TpnInfo object which can be used to construct a Validator.
    """
    return get_tpninfos(*key)

# =============================================================================

def main():
    print "null tpn processing."

if __name__ == "__main__":
    main()

