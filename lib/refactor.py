"""This module defines functions for modifying rmaps in various ways,  generally
the transformations required to automate rmap maintenance on the CRDS website.
"""
import sys
import re
import cStringIO
import os.path

from crds import (rmap, utils, reference_file, timestamp, compat, log)
from crds.timestamp import DATETIME_RE_STR

KEY_RE = r"(\s*')(.*)('\s*:\s*')(.*)('\s*,.*)"

def replace_header_value(filename, key, new_value):
    # print "refactoring", repr(filename), ":", key, "=", repr(new_value)
    newfile = cStringIO.StringIO()
    openfile = open(filename)
    for line in openfile:
        m = re.match(KEY_RE, line)
        if m and m.group(2) == key:
            line = re.sub(KEY_RE, r"\1\2\3%s\5" % new_value, line)
        newfile.write(line)
    openfile.close()
    newfile.seek(0)
    open(filename, "w+").write(newfile.read())
    
# ============================================================================
    
def rmap_insert_reference(old_rmap_contents, reffile):
    """Given the rmap text `old_rmap_contents`,  generate and return the contents
    of a new rmap with `reffile` inserted at all matching parkey 
    locations.  This routine assumes HST standard selector organization,  
    Match -> UseAfter.
    
    returns new_contents, [ old_rmap_match_tuples... ],  useafter_date 
    """
    loaded_rmap = rmap.ReferenceMapping.from_string(old_rmap_contents, ignore_checksum=True)
    parkeys = loaded_rmap.get_required_parkeys()[:-2] # skip DATE-OBS, TIME-OBS
    header = reference_file.get_conditioned_header(reffile)
    
    # Figure out the explicit lookup pattern for reffile.
    ref_match_tuple = tuple([header[key] for key in parkeys])
    
    # log.write("Insert reference match tuple", repr(ref_match_tuple))
    
    useafter_date = timestamp.reformat_date(header["USEAFTER"])

    # Figure out the abstract match tuples header matches against.
    old_rmap_matches = get_tuple_matches(loaded_rmap, header)

    new_contents = old_rmap_contents
    for match_tuple in old_rmap_matches: 
        new_contents = _rmap_delete_useafter(
            new_contents, match_tuple, useafter_date)
        new_contents = _rmap_add_useafter(
            new_contents, match_tuple, useafter_date, os.path.basename(reffile))
    
    return new_contents, old_rmap_matches, useafter_date

def get_tuple_matches(loaded_rmap, header):
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
    for tuples, _useafter_selector in loaded_rmap.selector.winnowing_match(header):
        matches.extend(tuples)
    return matches
    
def get_useafter_date(header):
    return 

def _rmap_add_useafter(old_rmap_contents, match_tuple, useafter_date, useafter_file):
    """Add one new useafter date / file to the `match_tuple` case of
    `old_rmap_contents`,  returning the modified rmap as a string.   If
    `match_tuple` doesn't exist in `old_mapping`,  add `match_tuple` as well.
    """
    # print "adding useafter", old_rmap, new_rmap, match_tuple, useafter_date, useafter_file
    old_rmap_file = cStringIO.StringIO(old_rmap_contents)
    new_mapping_file = cStringIO.StringIO()
    state = "find tuple"
    for line in old_rmap_file:
        if state == "find tuple":
            if "UseAfter" in line:
                #     ('HRC', 'CLEAR1S', 'F435W') : UseAfter({ 
                index = line.index(": UseAfter({")
                tuple_str = line[:index]
                line_tuple = compat.literal_eval(tuple_str.strip())
                if match_tuple == line_tuple:
                    state = "find useafter"
            elif line.strip() == "})":   # end of rmap
                # Never found match,  report an error.
                raise ValueError("Couldn't find match tuple " + repr(match_tuple))
        elif state == "find useafter":
            if line.strip().endswith(".fits',"):
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
    
def rmap_add_useafter(old_rmap, new_rmap, match_tuple, useafter_date, 
                      useafter_file):
    """Add one new useafter date / file to the `match_tuple` case of
    `old_rmap`,  writing the modified rmap out to `new_rmap`.   If
    `match_tuple` doesn't exist in `old_mapping`,  add `match_tuple` as well.
    """
    old_rmap_contents = open(old_rmap).read()
    new_rmap_contents = _rmap_add_useafter(
        old_rmap_contents, match_tuple, usafter_date, useafter_file)
    open(new_rmap, "w+").write(new_mapping_contents)

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
            if "UseAfter" in line:
                #     ('HRC', 'CLEAR1S', 'F435W') : UseAfter({ 
                index = line.index(": UseAfter({")
                tuple_str = line[:index]
                line_tuple = compat.literal_eval(tuple_str.strip())
                if match_tuple == line_tuple:
                    state = "find useafter"
            elif line.strip() == "})":   # end of rmap
                # Never found match,  report an error.
                raise CrdsError("Couldn't find match tuple " + repr(match_tuple))
        elif state == "find useafter":
            if line.strip().endswith(".fits',"):
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
                raise ValueError("Couldn't find useafter " +
                                repr((useafter_date, useafter_file)) +
                                " in match tuple " + repr(match_tuple))
        new_mapping_file.write(line)
    assert state == "copy remainder", "no useafter insertion performed"
    new_mapping_file.seek(0)
    return new_mapping_file.read()

def rmap_delete_useafter(old_rmap, new_rmap, match_tuple, useafter_date, 
                      useafter_file):
    """Add one new useafter date / file to the `match_tuple` case of
    `old_rmap`,  writing the modified rmap out to `new_rmap`.
    """
    old_rmap_contents = open(old_rmap).read()
    new_rmap_contents = _rmap_delete_useafter(
        old_rmap_contents, match_tuple, usafter_date, useafter_file)
    open(new_rmap, "w+").write(new_rmap_contents)

# ===========================================================================

def main():
    if sys.argv[1] == "insert":
        old_rmap = sys.argv[2]
        new_rmap = sys.argv[3]
        inserted_references = sys.argv[4:]
        contents = open(rmap.locate_mapping(old_rmap, "hst")).read()
        for reference in inserted_references:
            log.write("Inserting", repr(reference))
            contents, match_tuples, useafter = \
                rmap_insert_reference(contents, reference)
            for match in match_tuples:
                log.write("Inserted", repr(reference), "at", repr(match), 
                          repr(useafter))
        open(new_rmap, "w+").write(contents)
    else:
        print "usage: python -m crds.refactor insert <old_rmap> <new_rmap> <references...>"

if __name__ == "__main__":
    main()

