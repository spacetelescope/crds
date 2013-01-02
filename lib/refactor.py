"""This module defines functions for modifying rmaps in various ways,  generally
the transformations required to automate rmap maintenance on the CRDS website.
"""
import sys
import re
import cStringIO
import os.path

from crds import (rmap, data_file, timestamp, compat, log, selectors, checksum, utils)
from crds.timestamp import DATETIME_RE_STR

# ============================================================================
    
KEY_RE = r"(\s*')(.*)('\s*:\s*')(.*)('\s*,.*)"

# ============================================================================
    
class NoUseAfterError(ValueError):
    "The specified UseAfter datetime didn't exist in the rmap."

class NoMatchTupleError(ValueError):
    "The specified UseAfter datetime didn't exist in the rmap."

# ============================================================================
    
def replace_header_value(filename, key, new_value):
    """Set the value of `key` in `filename` to `new_value`."""
    # print "refactoring", repr(filename), ":", key, "=", repr(new_value)
    newfile = cStringIO.StringIO()
 
    with open(filename) as openfile:
        for line in openfile:
            m = re.match(KEY_RE, line)
            if m and m.group(2) == key:
                line = re.sub(KEY_RE, r"\1\2\3%s\5" % new_value, line)
            newfile.write(line)
    newfile.seek(0)
    
    with open(filename, "w+") as outputfile:
        outputfile.write(newfile.read())
    
# ============================================================================

class RefactorAction(object):
    """Records and formats info regarding a refactoring operation."""
    def __init__(self, rmap_name, action, ref_file, ref_match_tuple, 
                 rmap_match_tuple, useafter, replaced_file):
        self.rmap_name = str(os.path.basename(rmap_name))
        self.action = action
        self.ref_file = str(os.path.basename(ref_file))
        self.ref_match_tuple = ref_match_tuple
        self.rmap_match_tuple = rmap_match_tuple
        self.useafter = useafter
        if replaced_file:
            self.replaced_file = str(os.path.basename(replaced_file))
        else:
            self.replaced_file = "N/A"
            
    def close_enough(self, tup1, tup2):
        if len(tup1) != len(tup2):
            return False
        for i in range(len(tup2)):
            if tup1[i] == "N/A":
                continue
            if tup1[i] != tup2[i]:
                return False
        return True
            
    def __str__(self):
        exact = self.close_enough(self.rmap_match_tuple, self.ref_match_tuple)
        if exact:
            intro = "At exact match"
            trailer = ""
        else:
            intro = "At match"
            trailer = "matching " + str(self.ref_match_tuple)  
        if self.action == "insert":
            parts = [ intro, self.rmap_match_tuple,
                     "useafter", repr(self.useafter),
                     "INSERT", repr(self.ref_file), 
                     trailer
                      ]
        elif self.action == "replace":
            parts = [ intro, self.rmap_match_tuple,
                      "useafter", repr(self.useafter),
                      "REPLACE", repr(self.replaced_file),
                      "with", repr(self.ref_file), 
                      trailer
                      ]
        else:
            raise ValueError("Unknown action " + repr(self.action))    
        return " ".join([str(x) for x in parts])
    
def __repr__(self):
#    (self, rmap_name, action, ref_file, ref_match_tuple, 
#                 rmap_match_tuple, useafter, replaced_file):
    attrs = ["rmap_name", "action", "ref_file", "ref_match_tuple", 
             "rmap_match_tuple", "useafter", "replaced_file"]
    return self.__class__.__name__ + "(%s, %s, %s, %s, %s, %s, %s)" % \
        tuple([ repr(getattr(self, attr)) for attr in attrs ])

def _rmap_insert_reference(loaded_rmap, reffile):
    """Given the rmap text `old_rmap_contents`,  generate and return the 
    contents of a new rmap with `reffile` inserted at all matching parkey 
    locations.  This routine assumes HST standard selector organization,  
    Match -> UseAfter.
    
    returns new_contents, [ old_rmap_match_tuples... ],  useafter_date 
    """
    log.verbose("Inserting",repr(reffile),"into",repr(loaded_rmap))
    header, parkeys = _get_matching_header(loaded_rmap, reffile)
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
    
    return header, parkeys

def rmap_insert_references(old_rmap, new_rmap, inserted_references):
    """Given the full path of starting rmap `old_rmap`,  modify it by inserting 
    or replacing all files in `inserted_references` and write out the result to
    `new_rmap`.    If no actions are performed, don't write out `new_rmap`.
    
    Return the list of RefactorAction's performed.
    """
    new = rmap.load_mapping(old_rmap, ignore_checksum=True)
    for reference in inserted_references:
        new = _rmap_insert_reference(new, reference)
    log.verbose("Writing", repr(new_rmap))
    new.write(new_rmap)
    checksum.update_checksum(new_rmap)

def get_match_tuples(loaded_rmap, header, ref_match_tuple):
    """Given a ReferenceMapping `loaded_rmap` and a `header` dictionary,
    perform a winnowing match and return a list of match tuples corresponding
    to all possible matches of `loaded_rmap` against `header`.
    
    The match algorithm yields possible matches in best to worst order.   
    Further,  each rank of match may contain multiple tuples if ambiguous 
    matches are supported by merging.   Since a merged "ambiguous" match 
    actually corresponds to one choice resulting from multiple match cases,  
    each match returns a list of match tuples.   If ambiguous matches are 
    never supported,  len(match tuples) == 1.
    """
    matches = []
    for rmap_tuples, _useafter_selector in loaded_rmap.selector.winnowing_match(
                                        header, raise_ambiguous=False):
        # rmap_tuples are all equally weighted matches to header requiring
        # dynamic merger if there's more than one.
        for rmap_tuple in rmap_tuples:
            # Any time ref_match_tuple matches,  rmap_tuple matches.
            if selectors.match_superset(ref_match_tuple, rmap_tuple):
                matches.append(_normalize_match_tuple(rmap_tuple))
            else:
                log.verbose("Removing non-superset match", ref_match_tuple, "of", rmap_tuple)
    matches = _remove_special_cases(matches)
    return matches

def _remove_special_cases(matches):
    """It only makes sense to add the most general cases of the possible
    matches,  removing all proper special cases.   Note that all overlapping
    matches are not necessarily special cases,  only those with a true 
    subset/superset relationship.
    
    For instance,  ("A|B",) overlaps ("B|C",),  but is not a special case, so
    a refactoring of that rmap would affect both tuples.   On the other hand,
    ("A",) overlaps ("A|B",) and there is no case where the former will match
    and the latter will not... hence it only makes sense to change the latter.
    """
    matches2 = set(matches)
    for m1 in matches2:
        for m2 in matches2:
            if m1 != m2 and selectors.match_superset(m1, m2) and \
                    not selectors.different_match_weight(m1, m2) and m2 in matches:
                log.verbose("Match",repr(m1),"is a superset of", repr(m2))
                matches.remove(m2)
    return list(set(matches))
    
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
                    modification = "Inserted useafter into existing match case."
            elif line.strip() == "}),":
                # Never found < useafter before next Match tuple
                new_mapping_file.write("\t'%s' : '%s',\n" % \
                                           (useafter_date, useafter_file))
                state = "copy remainder"
                modification = "Appended useafter to existing match case."
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

# ===========================================================================

def main():
    import crds
    crds.handle_version()
    log.set_verbose(60)
    if len(sys.argv) >= 2 and sys.argv[1] == "insert":
        old_rmap = sys.argv[2]
        new_rmap = sys.argv[3]
        inserted_references = sys.argv[4:]
        rmap_insert_references(old_rmap, new_rmap, inserted_references)
    else:
        print "usage: python -m crds.refactor insert <old_rmap> <new_rmap> <references...>"
        sys.exit(-1)

if __name__ == "__main__":
    main()

