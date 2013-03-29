"""This module defines functions for modifying rmaps in various ways,  generally
the transformations required to automate rmap maintenance on the CRDS website.
"""
import sys
import os.path

from crds import (rmap, data_file, timestamp, log, utils, diff, cmdline)
# ============================================================================
    
class NoUseAfterError(ValueError):
    "The specified UseAfter datetime didn't exist in the rmap."

class NoMatchTupleError(ValueError):
    "The specified Match tuple didn't exist in the rmap."

# ============================================================================
    
def set_header_value(old_rmap, new_rmap, key, new_value):
    """Set the value of `key` in `filename` to `new_value` and rewrite the rmap.
    This is potentially lossy since rewriting the rmap may/will lose comments and 
    formatting quirks.
    """
    mapping = rmap.load_mapping(old_rmap)
    mapping.header[key] = new_value
    mapping.write(new_rmap)
    
def update_derivation(new_path, old_basename=None):
    """Set the 'derived_from' and 'name' header fields of `new_path`.  
    This function works for all Mapping classes:  pmap, imap, and rmap.
    """
    new = rmap.fetch_mapping(new_path)
    if old_basename is None:    # assume new is a copy of old, with old's name in header
        derived_from = new.name
    else:
        derived_from = old_basename
    new.header["derived_from"] = str(derived_from)
    new.header["name"] = str(os.path.basename(new_path))
    new.write(new_path)
    return str(derived_from)
    
# ============================================================================

def rmap_insert_references(old_rmap, new_rmap, inserted_references):
    """Given the full path of starting rmap `old_rmap`,  modify it by inserting 
    or replacing all files in `inserted_references` and write out the result to
    `new_rmap`.    If no actions are performed, don't write out `new_rmap`.
    
    Return new ReferenceMapping named `new_rmap`
    """
    new = old = rmap.fetch_mapping(old_rmap, ignore_checksum=True)
    for reference in inserted_references:
        new = _rmap_insert_reference(new, reference)
    new.header["derived_from"] = old.basename
    log.verbose("Writing", repr(new_rmap))
    new.write(new_rmap)
    formatted = new.format()
    for reference in inserted_references:
        reference = os.path.basename(reference)
        assert reference in formatted, \
            "Rules update failure. " + repr(reference) + " does not appear in new rmap." \
            "  May be identical match with other submitted references."
    return new

def rmap_check_modifications(old_rmap, new_rmap, expected=("add",)):
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
    
    returns new ReferenceMapping made from `loaded_rmap` inserting `reffile`.
    """
    log.info("Inserting", repr(os.path.basename(reffile)), "into", repr(loaded_rmap.name))
    header = _get_matching_header(loaded_rmap, reffile)
    new_rmap = loaded_rmap.insert(header, os.path.basename(reffile))
    return new_rmap

def _get_matching_header(loaded_rmap, reffile):
    """Based on `loaded_rmap`,  fetch the abstract header from reffile and use 
    it to define the parkey patterns to which this reffile will apply.   Note 
    that reference files generally apply to a set of parkey values and that the
    parkey patterns returned here can be unexploded or-globs.
    """
    
    # NOTE: required parkeys are in terms of *dataset* headers,  not reference headers.
    parkeys = loaded_rmap.get_required_parkeys()
    
    # Since expansion rules may depend on keys not used in matching,  
    # get entire header  
    header = data_file.get_header(reffile, observatory=loaded_rmap.observatory)

    # log.info("header:", { (key,val) for (key,val) in header.items() if key in parkeys })
    
    # The reference file key and dataset key matched aren't always the same!?!?
    # Specifically ACS BIASFILE NUMCOLS,NUMROWS and NAXIS1,NAXIS2
    # Also DATE-OBS, TIME-OBS  <-->  USEAFTER
    header = loaded_rmap.locate.reference_keys_to_dataset_keys(
        loaded_rmap.instrument, loaded_rmap.filekind, header)
    
    # Reference files specify things like ANY which must be expanded to 
    # glob patterns for matching with the reference file.
    header = loaded_rmap.locate.expand_wildcards(loaded_rmap.instrument, header)
    
    header = { key:utils.condition_value(value) for key, value in header.items() }

    # Add undefined parkeys as "UNDEFINED"
    header = data_file.ensure_keys_defined(header, parkeys)
    
    # Evaluate parkey relevance rules in the context of header to map
    # mode irrelevant parameters to N/A.
    # XXX not clear if/how this works with expanded wildcard or-patterns.
    header = loaded_rmap.map_irrelevant_parkeys_to_na(header)

    # The "extra" parkeys always appear in the rmap with values of "N/A".
    # The dataset value of the parkey is typically used to compute other parkeys
    # for HST corner cases.   It's a little stupid for them to appear in the
    # rmap match tuples,  but the dataset values for those parkeys are indeed 
    # relevant,  and it does provide a hint that magic is going on.  At rmap update
    # time,  these parkeys need to be set to N/A even if they're actually defined.
    for key in loaded_rmap.get_extra_parkeys():
        log.verbose("Mapping extra parkey", repr(key), "from", header[key], "to 'N/A'.")
        header[key] = "N/A"

    return header

# ============================================================================

class RefactorScript(cmdline.Script):
    """Command line script for modifying .rmap files."""

    description = """
    Modifies a reference mapping by adding the specified reference files.
    """
    
    epilog = """    
    """
    
    def add_args(self):
        self.add_argument("command", nargs=1, choices=("insert","set_header"),
            help="Name of refactoring command to perform.")
        self.add_argument('old_rmap', type=cmdline.reference_mapping,
            help="Reference mapping to modify by inserting references.")
        self.add_argument('new_rmap', type=cmdline.reference_mapping,
            help="Name of modified reference mapping output file.")        
        self.add_argument('references', type=cmdline.reference_file, nargs="+",
            help="Reference files to insert into `old_rmap` to produce `new_rmap`.")
        
    def main(self):
        rmap_insert_references(self.args.old_rmap, self.args.new_rmap, self.args.references)


if __name__ == "__main__":
    RefactorScript()()

