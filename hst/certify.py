"""This module defines replacement functionality for the CDBS "certify" program which
is used to check parameter values in .fits reference files and .lod files.  certify.py
loads expressions of legal values from CDBS .tpn files and applies them to reference
files to look for discrepancies.
"""
import crds.hst.tpn as tpn

def rmap_to_tpn(rmap):
    return tpn.get_tpn(rmap.instrument, rmap.extension)

