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
    
def update_derivation(old_path, new_path):
    """Set the 'derived_from' and 'name' header fields of `new_path` based on both."""
    old = rmap.load_mapping(old_path)
    new = rmap.load_mapping(new_path)
    new.header["derived_from"] = old.name
    new.header["name"] = os.path.basename(new_path)
    new.write(new_path)
    
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
    new.header["derived_from"] = old.derived_from
    log.verbose("Writing", repr(new_rmap))
    new.write(new_rmap)
    checksum.update_checksum(new_rmap)

def rmap_check_modifications(old_rmap, new_rmap, expected="add"):
    """Check the differences between `old_rmap` and `new_rmap` and make sure they're
    limited to the types listed in `expected`.
    
    expected should be "add" or "replace".
    
    Returns as_expected,  True IFF all rmap modifications match `expected`.
    """
    diffs = diff.mapping_diffs(old_rmap, new_rmap)
    as_expected = True
    for difference in diffs:
        actual = diff.diff_action(difference)
        if actual == expected:
            pass   # white-list so it will fail when expected is bogus.
        else:
            log.error("Expected", repr(expected), "but got", repr(actual),
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
    log.info("Inserting", repr(reffile), "into", repr(loaded_rmap.name))
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
    header = data_file.get_header(reffile)
    
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

def rmap_add_useafter(old_rmap, new_rmap, match_tuple, useafter_date, 
                      useafter_file):
    """Add one new useafter date / file to the `match_tuple` case of
    `old_rmap`,  writing the modified rmap out to `new_rmap`.   If
    `match_tuple` doesn't exist in `old_mapping`,  add `match_tuple` as well.
    """
    with open(old_rmap) as old_file:
        old_rmap_contents = old_file.read()
    new_rmap_contents = _rmap_add_useafter(
        old_rmap_contents, match_tuple, useafter_date, useafter_file)
    with open(new_rmap, "w+") as new_file:
        new_file.write(new_rmap_contents)

def _rmap_add_useafter(old_rmap_contents, match_tuple, useafter_date, 
                       useafter_file):
    """Add one new useafter date / file to the `match_tuple` case of
    `old_rmap_contents`,  returning the modified rmap as a string.   If
    `match_tuple` doesn't exist in `old_mapping`,  add `match_tuple` as well.
    """
    # print "adding useafter", old_rmap, new_rmap, match_tuple, useafter_date, 
    # useafter_file
    old_rmap_file = cStringIO.StringIO(old_rmap_contents)
    new_mapping_file = cStringIO.StringIO()
    state = "find tuple"
    for line in old_rmap_file:
        if state == "find tuple":
            state = _find_match(line, match_tuple) or state
        elif state == "find useafter":
            if re.match(".*: '.*',", line.strip()):
                # Handle a standard useafter clause
                # '2002-03-01 00:00:00' : 'oai16328j_cfl.fits', 
                line_date = re.search(DATETIME_RE_STR, line)
                if useafter_date < line_date.group(1):
                    # Found useafter insertion point inside existing match case
                    new_mapping_file.write("\t'%s' : '%s',\n" % \
                        (useafter_date, useafter_file))
                    state = "copy remainder"
                    # modification = "Inserted useafter into existing match case."
            elif line.strip() == "}),":
                # Never found < useafter before next Match tuple
                new_mapping_file.write("\t'%s' : '%s',\n" % \
                                           (useafter_date, useafter_file))
                state = "copy remainder"
                # modification = "Appended useafter to existing match case."
        new_mapping_file.write(line)
    assert state == "copy remainder", "no useafter insertion performed"
    new_mapping_file.seek(0)
    return new_mapping_file.read()
    
def _find_match(line, match_tuple):
    if "UseAfter" in line:
        #     ('HRC', 'CLEAR1S', 'F435W') : UseAfter({ 
        index = line.index(": UseAfter({")
        tuple_str = line[:index]
        line_tuple = compat.literal_eval(tuple_str.strip())
        norm_line_tuple = _normalize_match_tuple(line_tuple)
        # log.write("comparing match tuples", repr(match_tuple), repr(norm_line_tuple))
        if match_tuple == norm_line_tuple:
            return "find useafter"
        elif line.strip() == "})":   # end of rmap
            # Never found match,  report an error.
            raise ValueError("Couldn't find match tuple " + repr(match_tuple))
    return None

def _normalize_match_tuple(tup):
    return selectors.MatchSelector.condition_key(tup)
    # return tuple([str(item).strip() for item in tup])
    
def rmap_delete_useafter(old_rmap, new_rmap, match_tuple, useafter_date, 
                      useafter_file):
    """Delete one new useafter date / file of the `match_tuple` case of
    `old_rmap`,  writing the modified rmap out to `new_rmap`.   The case
    is expected to be present in the rmap or an exception is raised.
    """
    with open(old_rmap) as old_file:
        old_rmap_contents = old_file.read()
    new_rmap_contents, _filename = _rmap_delete_useafter(
        old_rmap_contents, match_tuple, useafter_date, useafter_file)
    with open(new_rmap, "w+") as new_file:
        new_file.write(new_rmap_contents)

def _rmap_delete_useafter(old_rmap_contents, match_tuple, useafter_date, 
                          useafter_file=None):
    """Remove useafter date / file from the `match_tuple` case of
    `old_rmap_contents`,  returning the contents of the new rmap.   If
    `match_tuple` doesn't exist in `old_mapping`,  add `match_tuple` as well.
    """
    old_rmap_file = cStringIO.StringIO(old_rmap_contents)
    new_mapping_file = cStringIO.StringIO()
    state = "find tuple"
    for line in old_rmap_file:
        if state == "find tuple":
            state = _find_match(line, match_tuple) or state
        elif state == "find useafter":
            if re.match(".*: '.*',", line.strip()):
                # Handle a standard useafter clause
                # '2002-03-01 00:00:00' : 'oai16328j_cfl.fits', 
                line_date = re.search(DATETIME_RE_STR, line)
                if useafter_date == line_date.group(1):
                    filename = re.search("'.*' : '(.*)'", line).group(1)
                    if not useafter_file or filename == useafter_file:
                        # Found useafter delete point.
                        state = "copy remainder"
                        continue
            elif line.strip() == "}),":
                raise NoUseAfterError("Couldn't find useafter " +
                                repr((useafter_date, useafter_file)) +
                                " in match tuple " + repr(match_tuple))
        new_mapping_file.write(line)
    assert state == "copy remainder", "no useafter insertion performed"
    new_mapping_file.seek(0)
    return new_mapping_file.read(), filename

# ===========================================================================

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

