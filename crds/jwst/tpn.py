"""This module defines functions for loading JWST's .tpn files which
describe reference parameters and their values.   The .tpn files are used to
validate headers or tables and list the parameters each filekind must define
in an rmap.

See the HST tpn.py and locator.py modules,  as well as crds.certify
and crds.rmap,  for more information.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import sys
import os.path
import pprint

from crds import rmap, log, utils, data_file
from crds.certify import TpnInfo
from . import schema

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

def get_classic_tpninfos(*key):
    """Load the listof TPN info tuples corresponding to `instrument` and 
    `filekind` from it's .tpn file.
    """
    where = os.path.join(HERE, "tpns", key[0])
    try:
        return _load_tpn(where)
    except Exception as exc:
        log.verbose_warning("No TPN file exists for", repr(key[0]), verbosity=70)
        return []

def get_tpninfos(*key):
    """Load the listof TPN info tuples corresponding to `key` from it's .tpn file.

    Key's are typically of the form  ('miri_flat.tpn', refpath) or
    ('miri_flat.ld_tpn', refpath).
    """
    # return schema.get_schema_tpns()  # schema.get_schema_tpninfos(*key)
    # return get_classic_tpninfos(key)
    return get_classic_tpninfos(*key) + schema.get_schema_tpninfos(*key)

# =============================================================================

def main():
    print("null tpn processing.")

if __name__ == "__main__":
    main()

