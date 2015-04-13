"""This module defines functions for loading JWST's .tpn files which
describe reference parameters and their values.   The .tpn files are used to
validate headers or tables and list the parameters each filekind must define
in an rmap.

See the HST tpn.py and locator.py modules,  as well as crds.certify
and crds.rmap,  for more information.
"""
import sys
import os.path
import pprint

from crds import rmap, log, utils, heavy_client
from crds.certify import TpnInfo

from jwst_lib import models

# ====================================================================================

@utils.cached
def get_tpninfos(*key):
    """Load the list of TPN info tuples corresponding to `instrument` and 
    `filekind` from it's .tpn file.
    """
    tpns = get_tpns()
    parkeys = tpninfos_key_to_parkeys(key)
    return [ info for info in tpns if info.name in parkeys ]

@utils.cached
def get_tpns():
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

'''
    try:
        return _load_tpn(os.path.join(HERE, "tpns", key[0]))
    except IOError:
        log.verbose_warning("no TPN for", key)
        return []
'''

# =============================================================================

# JWST Data Model schema to TPN


def _load_schema():
    """Return the core data model schema."""
    model = models.DataModel()
    return model.schema

def _schema_to_flat(schema):
    """Load the specified data model schema and return a flat dictionary from 
    data model dotted path strings to TpnInfo objects.
    """
    results = {}
    if schema["type"] ==  "object":
        subprops = schema["properties"]
        for prop in subprops:
            sub_tree = _schema_to_flat(subprops[prop])
            if sub_tree is None:
                continue
            if isinstance(sub_tree, dict):
                for subprop, val in sub_tree.items():
                    results[prop + "." + subprop] = val
            else:
                results[prop] = sub_tree
    elif schema["type"] in ["string","number","integer","boolean"]:
        return schema
    elif schema["type"] == "array":
        return None
    elif schema["type"] in ["any", "null"]:
        return None
    else:
        return "unhandled schema type " + repr(schema["type"])
    return results

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
    "string" : "Character",
    "integer" : "Integer",
    "number" : "Double",
    "boolean" : "Logical",
}

def _flat_to_tpns(flat=None):
    """Convert flat representation of DM schema to list of all TpnInfo objects."""
    if flat is None:
        flat = _schema_to_flat(_load_schema())
    tpns = []
    for key, value in flat.iteritems():
        if key.endswith(".type"):
            basekey = str(key[:-len(".type")])
            values = [str(val) for val in flat.get(basekey + ".enum", [])]
            datatype = SCHEMA_TYPE_TO_TPN.get(value, None)
            if type is not None:
                tpn = TpnInfo(name=basekey.upper(), keytype="Header", datatype=datatype, 
                              presence="Required", values=values)
                tpns.append(tpn)
    return sorted(tpns)

def get_dm_to_fits(schema):
    """Return mapping from DM dotted path string to FITS keyword."""
    fits = {}
    flat = _schema_to_flat(schema)
    for key, val in flat.iteritems():
        if key.endswith(".fits_keyword"):
            fits[str(key[:-len(".fits_keyword")])] = str(val)
    return fits

def get_fits_to_dm(schema):
    """Return mapping from FITS keyword to DM dotted path string."""
    return utils.invert_dict(get_dm_to_fits(schema))


# =============================================================================

def main():
    print "null tpn processing."

if __name__ == "__main__":
    main()

