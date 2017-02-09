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

# =============================================================================

import os.path

# =============================================================================

from crds.certify import generic_tpn

# =============================================================================

from . import schema

# =============================================================================

HERE = os.path.dirname(__file__) or "./"

def get_tpninfos(*key):
    """Load the listof TPN info tuples corresponding to `key` from it's .tpn file.

    Key's are typically of the form  ('miri_flat.tpn', refpath) or
    ('miri_flat.ld_tpn', refpath).
    """
    tpn_path = os.path.join(HERE, "tpns", key[0])
    return generic_tpn.get_classic_tpninfos(tpn_path) + schema.get_schema_tpninfos(*key)

# =============================================================================

def main():
    """Place holder function for running this module as cmd line program."""
    print("null tpn processing.")

if __name__ == "__main__":
    main()
