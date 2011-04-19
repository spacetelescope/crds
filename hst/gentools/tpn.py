"""This module defines functions for loading HST's CDBS .tpn files which
describe header parameters and their values.   The .tpn files are used to
validate headers in the original CDBS system and list the parameters each
file kind must define.
"""
import sys
import os
import collections

import crds.config as config

def load_tpn_lines(fname):
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
            lines[-1] = lines[-1][:-1] + line
        else:
            lines.append(line)
        append = line.endswith("\\")
    return lines


def fix_quoted_whitespace(line):
    i = 0
    while i < len(line):
        c = line[i]
        i += 1
        if c != '"':
            continue
        quote = c
        while i < len(line):
            c = line[i]
            i += 1
            if c == quote:
                break
            if c in " \t":
                line = line[:i-1] + "_" + line[i:]
    return line

tpn_info = collections.namedtuple("tpn_info", "keytype,datatype,presence,values")

def load_tpn(fname):
    """Load a TPN file and return it as a dictionary mapping header
    keywords onto their properties, including acceptable values.
    """
    tpn = {}
    for line in load_tpn_lines(fname):
        line = fix_quoted_whitespace(line)
        items = line.split()
        if len(items) == 4:
            name, keytype, datatype, presence = items
            values = ""
        else:
            name, keytype, datatype, presence, values = items
        values = values.split(",")
        tpn[name] = tpn_info(keytype, datatype, presence, values)
    return tpn


# Correspondence between instrument names and TPN file name <instrument> field.
INSTRUMENT_TO_TPN = {
    "acs" : "acs",
    "cos" : "cos",
    "stis" : "stis",
    "wfc3" : "wfc3",
    "wfpc2" : "wp2",
    "nicmos" : "nic",
}

def tpn_filepath(instrument, extension):
    """Return the full path for the .tpn file corresponding to `instrument` and `extension`."""
    return os.path.join(config.CRDS_ROOT, "hst", "cdbs", "cdbs_tpns",
                        INSTRUMENT_TO_TPN[instrument] + "_" + extension + ".tpn")

def get_tpn(instrument, extension):
    """Load the TPN tuple corresponding to `instrument` and `extension` from it's .tpn file."""
    return load_tpn(tpn_filepath(instrument, extension))


