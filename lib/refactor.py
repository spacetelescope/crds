"""This module defines functions for modifying rmaps in various ways,  generally
the transformations required to automate rmap maintenance on the CRDS website.
"""
import sys
import re
import cStringIO
import os.path

from crds import (rmap, data_file, timestamp, compat, log, selectors, checksum)
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
            
    def __str__(self):
        if self.action == "insert":
            parts = [ "At match", self.rmap_match_tuple,
                     "useafter", repr(self.useafter),
                     "INSERT", repr(self.ref_file), 
                     "matching", self.ref_match_tuple,
                      ]
        elif self.action == "replace":
            parts = [ "At match", self.rmap_match_tuple,
                      "useafter", repr(self.useafter),
                      "REPLACE", repr(self.replaced_file),
                      "with", repr(self.ref_file), 
                      "matching", self.ref_match_tuple, 
                      ]
        else:
            raise ValueError("Unknown action " + repr(self.action))    
        return " ".join([str(x) for x in parts])

def _rmap_insert_reference(old_rmap_name, old_rmap_contents, reffile):
    """Given the rmap text `old_rmap_contents`,  generate and return the 
    contents of a new rmap with `reffile` inserted at all matching parkey 
    locations.  This routine assumes HST standard selector organization,  
    Match -> UseAfter.
    
    returns new_contents, [ old_rmap_match_tuples... ],  useafter_date 
    """
    loaded_rmap = rmap.ReferenceMapping.from_string(
        old_rmap_contents, ignore_checksum=True)

    # XXX Hack alert skip DATE-OBS, TIME-OBS
    parkeys = loaded_rmap.get_required_parkeys()[:-2]  
    header = data_file.get_conditioned_header(
        reffile, needed_keys=parkeys + ["USEAFTER"])
    useafter_date = timestamp.reformat_date(header["USEAFTER"])

    # Figure out the explicit lookup pattern for reffile.  Omit USEAFTER
    ref_match_tuple = tuple([header[key] for key in parkeys])
    actions = []
    new_contents = old_rmap_contents
    
    log.verbose("Matching against", ref_match_tuple, repr(useafter_date))
    # Figure out the abstract match tuples header matches against.
    for rmap_tuple in get_match_tuples(loaded_rmap, header, ref_match_tuple):
        log.verbose("Trying", rmap_tuple)
        replaced_filename = None
        try:
            new_contents, replaced_filename = _rmap_delete_useafter(
                new_contents, rmap_tuple, useafter_date)
            kind = "replace"
        except NoUseAfterError:
            kind = "insert"
        except NoMatchTupleError:
            kind = "insert"
        new_contents = _rmap_add_useafter(
            new_contents, rmap_tuple, useafter_date, 
            os.path.basename(reffile))
        actions.append(RefactorAction(old_rmap_name, kind, reffile, 
                                      ref_match_tuple, rmap_tuple, 
                                      useafter_date, replaced_filename,))
    return new_contents, actions, useafter_date

def rmap_insert_references(old_rmap, new_rmap, inserted_references):
    """Given the full path of starting rmap `old_rmap`,  modify it by inserting 
    or replacing all files in `inserted_references` and write out the result to
    `new_rmap`.    If no actions are performed, don't write out `new_rmap`.
    
    Return the list of RefactorAction's performed.
    """
    contents = open(old_rmap).read()
    total_actions = []
    for reference in inserted_references:
        contents, actions, _useafter = \
            _rmap_insert_reference(old_rmap, contents, reference)
        total_actions.extend(actions)
    if total_actions:
        log.verbose("Writing", repr(new_rmap))
        open(new_rmap, "w+").write(contents)
        checksum.update_checksum(new_rmap)
        for action in total_actions:
            log.info(action)            
    else:
        log.warning("No actions in rmap_insert_references().")
    return total_actions

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
        for rmap_tuple in rmap_tuples:
            if selectors.match_superset(ref_match_tuple, rmap_tuple):
                matches.append(rmap_tuple)
    return matches
    
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
            if "UseAfter" in line:
                #     ('HRC', 'CLEAR1S', 'F435W') : UseAfter({ 
                index = line.index(": UseAfter({")
                tuple_str = line[:index]
                line_tuple = compat.literal_eval(tuple_str.strip())
                if match_tuple == line_tuple:
                    state = "find useafter"
            elif line.strip() == "})":   # end of rmap
                # Never found match,  report an error.
                raise ValueError("Couldn't find match tuple " + 
                                 repr(match_tuple))
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
    
def rmap_add_useafter(old_rmap, new_rmap, match_tuple, useafter_date, 
                      useafter_file):
    """Add one new useafter date / file to the `match_tuple` case of
    `old_rmap`,  writing the modified rmap out to `new_rmap`.   If
    `match_tuple` doesn't exist in `old_mapping`,  add `match_tuple` as well.
    """
    old_rmap_contents = open(old_rmap).read()
    new_rmap_contents = _rmap_add_useafter(
        old_rmap_contents, match_tuple, useafter_date, useafter_file)
    open(new_rmap, "w+").write(new_rmap_contents)

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
                raise NoMatchTupleError("Couldn't find match tuple " + 
                                        repr(match_tuple))
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
    old_rmap_contents = open(old_rmap).read()
    new_rmap_contents, _filename = _rmap_delete_useafter(
        old_rmap_contents, match_tuple, useafter_date, useafter_file)
    open(new_rmap, "w+").write(new_rmap_contents)

# ===========================================================================

def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "insert":
        old_rmap = sys.argv[2]
        new_rmap = sys.argv[3]
        inserted_references = sys.argv[4:]
        rmap_insert_references(old_rmap, new_rmap, inserted_references)
    else:
        print "usage: python -m crds.refactor insert " \
                "<old_rmap> <new_rmap> <references...>"
        sys.exit(-1)

if __name__ == "__main__":
    main()

