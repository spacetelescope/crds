"""This modules consolidates different kinds of information related to each
instrument and reference type under one data structure. Most of the information
contained here was reverse engineered from CDBS in a piecemeal fashion,  then
consolidated into the single common data structure to support future maintenance
and the addition of new types.
"""

import sys
import os.path
import pprint

from crds import rmap, log, utils, data_file
from crds.certify import TpnInfo

# =============================================================================

HERE = (os.path.dirname(__file__) + "/") or "./"

# =============================================================================
#  Global table loads used at operational runtime:

def _evalfile_with_fail(filename):
    """Evaluate and return a dictionary file,  returning {} if the file
    cannot be found.
    """
    if os.path.exists(filename):
        result = utils.evalfile(filename)
    else:
        log.warning("Couldn't load CRDS config file", repr(filename))
        result = {}
    return result

def _invert_instr_dict(map):
    """Invert a set of nested dictionaries of the form {instr: {key: val}}
    to create a dict of the form {instr: {val: key}}.
    """
    inverted = {}
    for instr in map:
        inverted[instr] = utils.invert_dict(map[instr])
    return inverted

def consolidate():
    """One time generation function to consolidate piecemeal spec files."""
    from crds.hst import tpn, INSTRUMENTS, FILEKINDS
    rowkeys = _evalfile_with_fail("./row_keys.dat")
    tpn_cat = _evalfile_with_fail("./crds_tpn_catalog.dat")
    ld_tpn_cat = _evalfile_with_fail("./crds_ld_tpn_catalog.dat")
    parkeys = _evalfile_with_fail("./parkeys.dat")
    consolidated = {}
    for instr in tpn.FILEKIND_TO_SUFFIX:
        if instr not in consolidated:
            consolidated[instr] = {}
        for filekind in tpn.FILEKIND_TO_SUFFIX[instr]:
            if filekind in ["comptab", "graphtab"]:  # unsupported synphot types
                continue
            if instr == "wfc3" and filekind == "dgeofile":  # unimplemented type
                continue
            if instr =="cos" and filekind in ["proftab", "tracetab", "twozxtab"]:  # first types added manually
                continue
            if filekind not in consolidated[instr]:
                consolidated[instr][filekind] = {}
            suffix = assign_field(consolidated, instr, filekind, "suffix", lambda: tpn.FILEKIND_TO_SUFFIX[instr][filekind])
            assign_field(consolidated, instr, filekind, "filetype", lambda: tpn.SUFFIX_TO_FILETYPE[instr][suffix])
            if instr == "stis" and filekind in ["lfltfile", "pfltfile"]:
                assign_field(consolidated, instr, filekind, "tpn", lambda: tpn_cat[instr][filekind][0][1][0])
                assign_field(consolidated, instr, filekind, "format", lambda: tpn_cat[instr][filekind][0][1][2])
                assign_field(consolidated, instr, filekind, "file_ext", lambda: tpn_cat[instr][filekind][0][1][3])
            else:
                assign_field(consolidated, instr, filekind, "tpn", lambda: tpn_cat[instr][filekind][0])
                assign_field(consolidated, instr, filekind, "format", lambda: tpn_cat[instr][filekind][2])
                assign_field(consolidated, instr, filekind, "file_ext", lambda: tpn_cat[instr][filekind][3])
            assign_field(consolidated, instr, filekind, "ld_tpn", lambda: ld_tpn_cat[instr][filekind][0])
            if consolidated[instr][filekind]["format"] == "table":  # only tables have rowkeys
                assign_field(consolidated, instr, filekind, "unique_rowkeys", lambda: rowkeys[instr][filekind])
            else:
                assign_field(consolidated, instr, filekind, "unique_rowkeys", lambda: None)
            assign_field(consolidated, instr, filekind, "reffile_required", lambda: parkeys[instr][filekind]["reffile_required"])
            assign_field(consolidated, instr, filekind, "reffile_switch", lambda: parkeys[instr][filekind]["reffile_switch"])
            assign_field(consolidated, instr, filekind, "parkeys", lambda: tuple(parkey.upper() for parkey in parkeys[instr][filekind]["parkeys"]))
            assign_field(consolidated, instr, filekind, "rmap_relevance", lambda: parkeys[instr][filekind]["rmap_relevance"])
            assign_field(consolidated, instr, filekind, "parkey_relevance", lambda: parkeys[instr][filekind]["parkey_relevance"])
            assign_field(consolidated, instr, filekind, "extra_keys", lambda: parkeys[instr][filekind]["not_in_db"])
    assign_field(consolidated, "stis", "lfltfile", "tpn", lambda: [("OBSTYPE == 'IMAGING'", "stis_ilflt.tpn"),
                                                                   ("OBSTYPE == 'SPECTROSCOPIC", "stis_slflt.tpn")])
    assign_field(consolidated, "stis", "pfltfile", "tpn", lambda: [("OBSTYPE == 'IMAGING'", "stis_ipflt.tpn"),
                                                                   ("OBSTYPE == 'SPECTROSCOPIC", "stis_spflt.tpn")])
                
    open("./reftypes.dat", "wb").write(str(log.PP(consolidated)))


def assign_field(consolidated, instr, filekind, field, valuef):
    try:
        value = consolidated[instr][filekind][field] = valuef()
    except Exception, exc:
        log.warning("Skipping", instr, filekind, field, ":", exc)
        value = consolidated[instr][filekind][field] = None
    return value

# =============================================================================

