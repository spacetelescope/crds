"""This module defines functions for loading JWST's data model schema files which
describe reference parameters and their values.   The schema files are used to 
validate reference and rmap parameters to screen out illegal values.   In particular
the resulting TpnInfo objects describe rmap constraints which are not enforced at
load time by the JWST data model since rmaps are not loaded by the data model.

See the tpn.py and locator.py modules,  as well as crds.certify and crds.rmap,
and crds.selectors for more information.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import os.path
import pprint

# from jwst_lib import models   # deferred

from crds import rmap, log, utils, heavy_client
from crds.certify import TpnInfo

# ====================================================================================

@utils.cached
def get_schema_tpninfos(*key):
    """Load the list of TPN info tuples corresponding to `instrument` and 
    `filekind` from it's .tpn file.
    """
    with log.warn_on_exception("Failed loading schema constraints for", repr(key)):
        tpns = get_schema_tpns()
        parkeys = tpninfos_key_to_parkeys(key)
        return [ info for info in tpns if info.name in parkeys ]
    return []

@utils.cached
def get_schema_tpns():
    """Load all the TpnInfos in the core schema."""
    flat = _schema_to_flat(_load_schema())
    all_tpns = _flat_to_tpns(flat)
    return all_tpns

@utils.cached
def tpninfos_key_to_parkeys(key):
    """Given a key for a TpnInfo's list, return the associated required parkeys."""
    _mode, context  = heavy_client.get_processing_mode("jwst")
    p = rmap.get_cached_mapping(context)
    instrument, filekind = key[0].split(".")[0].split("_")[:2]
    keys = p.get_imap(instrument).get_rmap(filekind).get_required_parkeys()
    keys.append("META.INSTRUMENT.NAME")
    return sorted(keys)

# =============================================================================

# JWST Data Model schema to TPN


def _load_schema():
    """Return the core data model schema."""
    from jwst_lib import models
    model = models.DataModel()
    return model.schema

def _schema_to_flat(schema):
    """Load the specified data model schema and return a flat dictionary from 
    data model dotted path strings to TpnInfo objects.
    """
    flat = _x_schema_to_flat(schema)
    uppercase = {}
    for key, val in flat.items():
        if isinstance(val, list):
            val = [ str(item).upper() for item in val ]
        else:
            val = str(val).upper()
        uppercase[str(key).upper()] = val
    return uppercase

def _x_schema_to_flat(schema):
    """Recursively flatten `schema` without addressing case issues."""
    results = {}
    if schema["type"] ==  "object":
        subprops = schema["properties"]
        for prop in subprops:
            with log.augment_exception("In", repr(prop)):
                sub_tree = _schema_to_flat(subprops[prop])
                if sub_tree is None:
                    continue
                if isinstance(sub_tree, dict):
                    for subprop, val in list(sub_tree.items()):
                        results[prop + "." + subprop] = val
                else:
                    results[prop] = sub_tree
    elif schema["type"] in BASIC_TYPES:
        return schema
    elif schema["type"] in OPTIONAL_TYPES:
        return schema
    elif schema["type"] == "array":
        return None
    elif schema["type"] in ["any", "null"]:
        return None
    else:
        log.verbose_warning("Schema item has unhandled type", repr(schema["type"]), verbosity=80)
    return results

def type_or_null(names):
    """Return the list of types `names` + the name-or-null list for every type in `names`."""
    return [[name, 'null'] for name in names]

BASIC_TYPES = ["string","number","integer","boolean"]
OPTIONAL_TYPES = type_or_null(BASIC_TYPES)

#
# Only the first character of the field is stored, i.e. Header == H                                                       
#
# name = field identifier                                                                                                 
# keytype = (Header|Group|Column)                                                                                         
# datatype = (Integer|Real|Logical|Double|Character)                                                                      
# presence = (Optional|Required)                                                                                          
# values = [...]                                                                                                          
#
# TpnInfo = namedtuple("TpnInfo", "name,keytype,datatype,presence,values")
#

SCHEMA_TYPE_TO_TPN = {
    "STRING" : ("C", "R"),
    "INTEGER" : ("I", "R"),
    "NUMBER" : ("D", "R"),
    "BOOLEAN" : ("L", "R"),
    
    ("STRING", "NULL") : ("C", "O"),
    ("INTEGER", "NULL") : ("I", "O"),
    ("NUMBER", "NULL") : ("D", "O"),
    ("BOOLEAN", "NULL") : ("L", "O"),
}

def _flat_to_tpns(flat=None):
    """Convert flat representation of DM schema to list of all TpnInfo objects."""
    if flat is None:
        flat = _schema_to_flat(_load_schema())
    tpns = []
    for key, value in flat.items():
        if key.endswith(".TYPE"):
            basekey = str(key[:-len(".TYPE")])
            legal_values = [str(val) for val in flat.get(basekey + ".ENUM", [])]
            if isinstance(value, list):
                value = tuple(value)
            datatype = SCHEMA_TYPE_TO_TPN.get(value, None)
            if datatype is not None:
                tpn = TpnInfo(name=basekey.upper(), keytype="H", datatype=datatype[0], 
                              presence=datatype[1], values=legal_values)
                tpns.append(tpn)
            else:
                log.warning("No TPN form for", repr(key), repr(value))
    return sorted(tpns)

def _get_dm_to_fits(schema=None):
    """Return mapping from DM dotted path string to FITS keyword."""
    if schema is None:
        schema = _load_schema()
    fits = {}
    flat = _schema_to_flat(schema)
    for key, val in flat.items():
        if key.endswith(".fits_keyword"):
            fits[str(key[:-len(".fits_keyword")])] = str(val)
    return fits

def _get_fits_to_dm(schema=None):
    """Return mapping from FITS keyword to DM dotted path string."""
    return utils.invert_dict(_get_dm_to_fits(schema))

DM_TO_FITS = _get_dm_to_fits()
FITS_TO_DM = _get_fits_to_dm()

def dm_to_fits(key):
    """Return the FITS keyword for DM `key` or None."""
    return DM_TO_FITS.get(key, None)

def fits_to_dm(key):
    """Return the DM keyword for FITS `key` or None."""
    return FITS_TO_DM.get(key, None)

# =============================================================================

def main():
    print("null tpn processing.")

if __name__ == "__main__":
    main()

