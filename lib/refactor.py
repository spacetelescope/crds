"""This module defines functions for modifying rmaps in various ways,  generally
the transformations required to automate rmap maintenance on the CRDS website.
"""
import re
import cStringIO

from crds import (rmap, utils)

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
    
def rmap_insert_reference(old_rmap, new_rmap, reference_file):
    """Given the rmap at path `old_rmap`,  generate an rmap at `new_rmap` with
    reference file inserted at all matching parkey locations.  This
    routine assumes HST standard selector organization,  Match -> UseAfter.
    """
    ref_match_tuple = get_match_tuple(old_rmap, reference_file)
    old_rmap_matches = get_tuple_matches(old_rmap, ref_match_tuple)
    useafter_date = get_useafter_date(reference_file)
    for match_tuple in old_rmap_matches: 
        rmap_del_useafter(old_rmap, new_rmap1, match_tuple, useafter_date)
        rmap_add_useafter(new_rmap1, new_rmap, match_tuple, useafter_date, 
                          os.path.basename(reference_file))
    
def get_match_tuple(old_rmap, reference_file):
    """Return the relevant parameters from `reference_file` as a tuple
    in the required order to match against the rmap at path `old_rmap`.
    """
    loaded_rmap = rmap.get_cached_mapping(old_rmap)
    parkeys = loaded_rmap.get_required_parkeys()
    header = utils.get_header_union(reference_file, needed_keys=parkeys)
    return tuple([header[key] for key in parkeys])

def get_useafter_date(reference_file):
    return utils.condition_value(pyfits.getval(reference_file, "USEAFTER"))

def get_tuple_matches(old_rmap, match_tuple):
    pass

def rmap_add_useafter(old_rmap, new_rmap, match_tuple, 
                           useafter_date, useafter_file):
    """Add one new useafter date / file to the `match_tuple` case of
    `old_mapping`,  writing the modified rmap out to `new_rmap`.   If
    `match_tuple` doesn't exist in `old_mapping`,  add `match_tuple` as well.
    """
    # print "adding useafter", old_rmap, new_rmap, match_tuple, useafter_date, useafter_file
    new_mapping_file = cStringIO.StringIO()
    state = "find tuple"
    for line in open(old_rmap):
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
    open(new_rmap, "w+").write(new_mapping_file.read())

def rmap_delete_useafter(old_rmap, new_rmap, match_tuple, 
                              useafter_date, useafter_file=None):
    """Add one new useafter date / file to the `match_tuple` case of
    `old_mapping`,  writing the modified rmap out to `new_rmap`.   If
    `match_tuple` doesn't exist in `old_mapping`,  add `match_tuple` as well.
    """
    new_mapping_file = cStringIO.StringIO()
    state = "find tuple"
    for line in open(old_rmap):
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
                raise CrdsError("Couldn't find useafter " +
                                repr((useafter_date, useafter_file)) +
                                " in match tuple " + repr(match_tuple))
        new_mapping_file.write(line)
    assert state == "copy remainder", "no useafter insertion performed"
    new_mapping_file.seek(0)
    open(new_rmap, "w+").write(new_mapping_file.read())

