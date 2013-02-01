"""This module defines functions for modifying rmaps in various ways,  generally
the transformations required to automate rmap maintenance on the CRDS website.
"""
import sys
import re
import cStringIO
import os.path

from crds import (rmap, data_file, timestamp, compat, log, selectors, 
                  checksum, utils, diff)
from crds.timestamp import DATETIME_RE_STR

# ============================================================================
    
class NoUseAfterError(ValueError):
    "The specified UseAfter datetime didn't exist in the rmap."

class NoMatchTupleError(ValueError):
    "The specified UseAfter datetime didn't exist in the rmap."

# ============================================================================
    
def replace_header_value(filename, key, new_value):
    """Replace the value of `key` in `filename` with `new_value`.    This is
    intended to be a "loss-less" operation preserving comments, whitespace,
    etc.,  but currently is not.
    """
    return set_header_value(filename, filename, key, new_value)


def set_header_value(old_rmap, new_rmap, key, new_value):
    """Set the value of `key` in `filename` to `new_value` and rewrite the rmap.
    This is potentially lossy since rewriting the rmap may/will lose comments and 
    formatting quirks.
    """
    map = rmap.load_mapping(old_rmap)
    map.header[key] = new_value
    map.write(new_rmap)
    
def update_derivation(new_path, old_basename=None):
    """Set the 'derived_from' and 'name' header fields of `new_path`.  
    This function works for all Mapping classes:  pmap, imap, and rmap.
    """
    new = rmap.load_mapping(new_path)
    if old_basename is None:    # assume new is a copy of old, with old's name in header
        derived_from = new.name
    else:
        derived_from = old_basename
    new.header["derived_from"] = str(derived_from)
    new.header["name"] = str(os.path.basename(new_path))
    new.write(new_path)
    return str(derived_from)
    
# ============================================================================

def rmap_insert_references(old_rmap, new_rmap, inserted_references, expected=("add","replace")):
    """Given the full path of starting rmap `old_rmap`,  modify it by inserting 
    or replacing all files in `inserted_references` and write out the result to
    `new_rmap`.    If no actions are performed, don't write out `new_rmap`.
    
    Return the list of RefactorAction's performed.
    """
    new = old = rmap.load_mapping(old_rmap, ignore_checksum=True)
    for reference in inserted_references:
        new = _rmap_insert_reference(new, reference)
    new.header["derived_from"] = old.basename
    log.verbose("Writing", repr(new_rmap))
    new.write(new_rmap)
    return new

def rmap_check_modifications(old_rmap, new_rmap, expected=["add"]):
    """Check the differences between `old_rmap` and `new_rmap` and make sure they're
    limited to the types listed in `expected`.
    
    expected should be "add" or "replace".
    
    Returns as_expected,  True IFF all rmap modifications match `expected`.
    """
    diffs = diff.mapping_diffs(old_rmap, new_rmap)
    as_expected = True
    for difference in diffs:
        actual = diff.diff_action(difference)
        if actual in expected:
            pass   # white-list so it will fail when expected is bogus.
        else:
            log.error("Expected one of", repr(expected), "but got", repr(actual),
                      "from change", repr(difference))
            as_expected = False
    return as_expected

def _rmap_insert_reference(loaded_rmap, reffile):
    """Given the rmap text `old_rmap_contents`,  generate and return the 
    contents of a new rmap with `reffile` inserted at all matching parkey 
    locations.  This routine assumes HST standard selector organization,  
    Match -> UseAfter.
    
    returns new_contents, [ old_rmap_match_tuples... ],  useafter_date 
    """
    log.info("Inserting", repr(os.path.basename(reffile)), "into", repr(loaded_rmap.name))
    header = _get_matching_header(loaded_rmap, reffile)
    new_rmap = loaded_rmap.insert(header, os.path.basename(reffile))
    return new_rmap

def _get_matching_header(loaded_rmap, reffile):
    """Based on `loaded_rmap`,  fetch the abstract header from reffile and use 
    it to define the parkey patterns to which this reffile will apply.   Note 
    that reference files generally apply to a set of parkey values and that the
    parkey patterns returned here can be unexploded or-globs.   The header 
    returned actually represents a set of headers corresponding to the discrete 
    values of exploded or-globs.
    
    XXX TODO possibly required:  it may be necessary to fully explode the 
    or-globs and return a list of headers of discrete parameters for matching.
    The current approach depends on an exact match to the or-glob.
    """
    # XXX Hack alert skip DATE-OBS, TIME-OBS
    parkeys = loaded_rmap.get_required_parkeys()[:-2]
    
    # Since expansion rules may depend on keys not used in matching,  
    # get entire header  
    header = data_file.get_header(reffile, observatory=loaded_rmap.observatory)
    
    # The reference file key and dataset key matched aren't always the same!?!?
    # Specifically ACS BIASFILE NUMCOLS,NUMROWS and NAXIS1,NAXIS2
    header = loaded_rmap.locate.reference_keys_to_dataset_keys(
        loaded_rmap.instrument, loaded_rmap.filekind, header)
    
    # Reference files specify things like ANY which must be expanded to 
    # glob patterns for matching with the reference file.
    header = loaded_rmap.locate.expand_wildcards(loaded_rmap.instrument, header)
    
    header = { key:utils.condition_value(value) for key, value in header.items() \
               if key in parkeys + ["USEAFTER"] }
    
    if "USEAFTER" in header and "DATE-OBS" not in header:
        useafter = timestamp.reformat_date(header["USEAFTER"])
        header["DATE-OBS"] = useafter.split()[0]
        header["TIME-OBS"] = useafter.split()[1]
    
    # Add undefined parkeys as "UNDEFINED"
    header = data_file.ensure_keys_defined(header, parkeys + ["DATE-OBS", "TIME-OBS"])
    
    # Evaluate parkey relevance rules in the context of header to map
    # mode irrelevant parameters to N/A.
    # XXX not clear if/how this works with expanded wildcard or-patterns.
    header = loaded_rmap.map_irrelevant_parkeys_to_na(header)
    
    return header

# ============================================================================

def main():
    """Command line refactoring behavior."""
    import crds
    crds.handle_version()
    
    if "--verbose" in sys.argv:
        sys.argv.remove("--verbose")
        log.set_verbose()
    
    if len(sys.argv) >= 5 and sys.argv[1] == "insert":
        old_rmap = sys.argv[2]
        new_rmap = sys.argv[3]
        inserted_references = sys.argv[4:]
        rmap_insert_references(old_rmap, new_rmap, inserted_references)
        # update_derivation(old_rmap, new_rmap)
    elif len(sys.argv) == 6 and sys.argv[1] == "set_header":
        old_rmap = sys.argv[2]
        new_rmap = sys.argv[3]
        key = sys.argv[4]
        value = sys.argv[5]
        set_header_value(old_rmap, new_rmap, key, value)        
    else:
        print "usage: python -m crds.refactor insert <old_rmap> <new_rmap> <references...>"
        print "usage: python -m crds.refactor set_header <old_rmap> <new_rmap> <key> <value>"
        sys.exit(-1)

if __name__ == "__main__":
    main()

