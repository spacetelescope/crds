"""This module defines functions for loading Roman's data model schema files which
describe reference parameters and their values.  The schema files are used to
validate reference and rmap parameters to screen out illegal values.

The primary functions provided by this module are:

1. Scraping the romancal data model schema for keyword value enumerations

See the locator.py module, as well as crds.certify, crds.rmap, and crds.selectors
for more information.
"""
import re

# ====================================================================================

# from romancal import datamodels   # deferred
# from . import locate  # deferred

import crds
from crds.core import log, utils, heavy_client, config
from crds.core.generic_tpn import TpnInfo

# ====================================================================================

def get_exptypes(instrument=None):
    """Using an arbitrary reference from an instrument that matches using EXP_TYPE, return
    the set of all EXP_TYPE values defined in the Roman schema.
    """
    raise NotImplementedError("get_exptypes is not yet implemented for Roman")

def get_schema_tpninfos(refpath):
    """Load the list of TPN info tuples corresponding to `instrument` and
    `filekind` from it's .tpn file.
    """
    with log.warn_on_exception("Failed loading schema constraints for", repr(refpath)):
        schema_name = reference_to_schema_name(refpath)
        tpns = get_schema_tpns(schema_name)
        parkeys = refpath_to_parkeys(refpath)
        return [ info for info in tpns if info.name in parkeys ]
    return []

def reference_to_schema_name(reference_name):
    """This function will eventually identify the schema associated with `reference_name`
    unless replaced by similar functionality in the models package.

    Returns None meaning "default/core schema"
    """
    return None

@utils.cached
def get_schema_tpns(schema_name=None):
    """Load all the TpnInfos in the core schema."""
    flat = _schema_to_flat(_load_schema(schema_name))
    all_tpns = _flat_to_tpns(flat)
    return all_tpns

@utils.cached
def get_flat_schema(schema_name=None):
    """Flatten the specified data model schema, defaulting to the core schema,
    useful for retrieving FITS keywords or valid value lists.
    """
    return _schema_to_flat(_load_schema(schema_name))

@utils.cached
def refpath_to_parkeys(refpath):
    """Given a key for a TpnInfo's list, return the associated required parkeys."""
    from . import locate
    keys = []
    with log.verbose_warning_on_exception("Can't determine parkeys for", repr(refpath)):
        context  = heavy_client.get_context_name("roman")
        p = crds.get_pickled_mapping(context)   # reviewed
        instrument, filekind = locate.get_file_properties(refpath)
        keys = p.get_imap(instrument).get_rmap(filekind).get_required_parkeys()
    return sorted(keys)

# =============================================================================

# Roman Data Model schema to TPN


def _load_schema(schema_name=None):
    """Return the core data model schema."""
    from . import locate
    datamodels = locate.get_datamodels()
    model = datamodels.RomanDataModel(schema=schema_name)
    return model.schema

def _schema_to_flat(schema):
    """Load the specified data model schema and return a flat dictionary from
    data model dotted path strings to TpnInfo objects.
    """
    flat = _x_schema_to_flat(schema)
    if flat is None:
        return None
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
    for feature in ["oneOf","allOf","$ref"]:
        if feature in schema:
            log.verbose_warning("Schema item has unhandled feature {}.", verbosity=80)
            return None

    if "anyOf" in schema and "type" in schema["anyOf"]:
        schema_type = schema["anyOf"]["type"]
    else:
        schema_type = schema.get("type", "null")

    if schema_type ==  "object":
        subprops = schema["properties"]
        for prop in subprops:
            with log.augment_exception("In schema property", repr(prop)):
                sub_tree = _schema_to_flat(subprops[prop])
                if sub_tree is None:
                    continue
                if isinstance(sub_tree, dict):
                    for subprop, val in list(sub_tree.items()):
                        results[prop + "." + subprop] = val
                else:
                    results[prop] = sub_tree
    elif schema_type in BASIC_TYPES:
        return schema
    elif schema_type in OPTIONAL_TYPES:
        return schema
    elif schema_type == "array":
        return None
    elif schema_type in ["any", "null"]:
        return None
    else:
        log.verbose_warning("Schema item has unhandled type", repr(schema_type), verbosity=80)
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
    "STRING" : ("C", "O"),
    "INTEGER" : ("I", "O"),
    "NUMBER" : ("D", "O"),
    "BOOLEAN" : ("L", "O"),

    ("STRING", "NULL") : ("C", "O"),
    ("INTEGER", "NULL") : ("I", "O"),
    ("NUMBER", "NULL") : ("D", "O"),
    ("BOOLEAN", "NULL") : ("L", "O"),
}

def _flat_to_tpns(flat=None, schema_name=None):
    """Convert flat representation of DM schema to list of all TpnInfo objects."""
    if flat is None:
        flat = _schema_to_flat(_load_schema(schema_name))
    tpns = []
    for key, value in flat.items():
        if key.endswith(".TYPE"):
            basekey = str(key[:-len(".TYPE")])
            legal_values = [str(val) for val in flat.get(basekey + ".ENUM", [])]
            if legal_values:
                legal_values += ["ANY", "N/A"]
            legal_values = tuple(sorted(set(legal_values)))
            if isinstance(value, list):
                value = tuple(value)
            datatype = SCHEMA_TYPE_TO_TPN.get(value, None)
            if datatype is not None:
                tpn = TpnInfo(name=basekey.upper(), keytype="H", datatype=datatype[0],
                              presence=datatype[1], values=legal_values)
                log.verbose("Adding tpn constraint from DM schema:", repr(tpn), verbosity=65)
                tpns.append(tpn)
            else:
                log.warning("No TPN form for", repr(key), repr(value))
    return sorted(tpns)

# =============================================================================

def main():
    print("null tpn processing.")

if __name__ == "__main__":
    main()
