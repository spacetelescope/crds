"""This module differences two CRDS reference or mapping files on the local
system.   It supports specification of the files using only the basenames or
a full path.   Currently it operates on mapping, FITS, or text files.
"""
import sys
import os
import optparse

from crds import rmap, log, pysh

# ============================================================================
        
def mapping_diffs(file1, file2):
    """Return the logical differences between CRDS mappings named `file1` 
    and `file2`.
    """
    assert rmap.is_mapping(file1), \
        "File " + repr(file1) + " is not a CRDS mapping."
    assert rmap.is_mapping(file2), \
        "File " + repr(file2) + " is not a CRDS mapping."
    assert os.path.splitext(file1)[-1] == os.path.splitext(file2)[-1], \
        "Files " + repr(file1) + " and " + repr(file2) + \
        " are not the same kind of CRDS mapping:  .pmap, .imap, .rmap"
    map1 = rmap.load_mapping(file1)
    map2 = rmap.load_mapping(file2)
    differences = map1.difference(map2)
    return differences

def diff_action(d):
    """Return 'add', 'replace', or 'delete' based on action represented by
    difference tuple `d`.   Append "_rule" if the change is a Selector.
    """
    if "replace" in d[-1]:
        result = "replace"
    elif "add" in d[-1]:
        result = "add"
    elif "delete" in d[-1]:
        result = "delete"
    else:
        raise ValueError("Bad difference action: "  + repr(d))
    if "Selector" in d[-1]:
        result += "_rule"
    return result

def mapping_difference(observatory, file1, file2, primitive_diffs=False, check_diffs=False):
    """Print the logical differences between CRDS mappings named `file1` 
    and `file2`.  
    
    IFF primitive_differences,  recursively difference any replaced files found
    in the top level logical differences.
    
    IFF check_diffs, issue warnings about critical differences.   See
    mapping_check_diffs().
    """
    differences = mapping_diffs(file1, file2)
    if primitive_diffs:
        for pair in mapping_pairs(differences):
            log.write("="*80)
            log.write(pair)
            text_difference(observatory, pair[0], pair[1])
    for diff in differences:
        diff = rq_diff(diff)
        if primitive_diffs:
            log.write("="*80)
        log.write(diff)
        if primitive_diffs:
            if "replaced" in diff[-1]:
                old, new = diff_replace_old_new(diff)
                difference(observatory, old, new, primitive_diffs=primitive_diffs)
    if check_diffs:
        mapping_check_diffs(file2, file1)

def mapping_pairs(differences):
    """Return the sorted list of all mapping tuples found in differences."""
    pairs = set()
    for diff in differences:
        for pair in diff:
            if len(pair) == 2 and rmap.is_mapping(pair[0]):
                pairs.add(pair)
    return sorted(pairs)
        
def rq_diff(diff):
    """Remove repr str quoting in `diff` tuple."""
    return diff[:-1] + (diff[-1].replace("'",""),)

def rq(name):
    """Remove string quotes from simple `name` repr."""
    return name.replace("'","").replace('"','')

def diff_replace_old_new(diff):
    """Return the (old, new) filenames from difference tuple `diff`."""
    _replaced, old, _with, new = diff[-1].split()
    return rq(old), rq(new)
    
# ============================================================================

def mapping_check_diffs(mapping, derived_from):
    """Issue warnings for *deletions* in self relative to parent derived_from
    mapping.  Issue warnings for *reversions*,  defined as replacements which
    where the replacement is older than the original,  as defined by the names.   
    
    This is intended to check for missing modes and for inadvertent reversions
    to earlier versions of files.   For speed and simplicity,  file time order
    is currently determined by the names themselves,  not file contents, file
    system,  or database info.
    """
    mapping = rmap.asmapping(mapping)
    derived_from = rmap.asmapping(derived_from)
    log.info("Checking derivation diffs from", repr(derived_from.basename), "to", repr(mapping.basename))
    diffs = derived_from.difference(mapping)
    categorized = sorted([ (diff_action(d), d) for d in diffs ])
    for action, msg in categorized:
        if action == "add":
            log.verbose("In", _diff_tail(msg)[:-1], msg[-1])
        elif "rule" in action:
            log.warning("Rule change at", _diff_tail(msg)[:-1], msg[-1])
        elif action == "replace":
            old_val, new_val = diff_replace_old_new(msg)
            if newer(new_val, old_val):
                log.verbose("In", _diff_tail(msg)[:-1], msg[-1])
            else:
                log.warning("Reversion at", _diff_tail(msg)[:-1], msg[-1])
        elif action == "delete":
            log.warning("Deletion at", _diff_tail(msg)[:-1], msg[-1])
        else:
            raise ValueError("Unexpected difference action:", difference)

def _diff_tail(msg):
    """`msg` is an arbitrary length difference "path",  which could
    be coming from any part of the mapping hierarchy and ending in any kind of 
    selector tree.   The last item is always the change message: add, replace, 
    delete <blah>.  The next to last should always be a selector key of some kind.  
    Back up from there to find the first mapping tuple.
    """
    tail = []
    for part in msg[::-1]:
        if isinstance(part, tuple) and len(part) == 2 and isinstance(part[0], str) and part[0].endswith("map"):
            tail.append(part[1])
            break
        else:
            tail.append(part)
    return tuple(reversed(tail))

def newstyle_name(name):
    """Return True IFF `name` is a CRDS-style name, e.g. hst_acs.imap
    
    >>> newstyle_name("s7g1700gl_dead.fits")
    False
    >>> newstyle_name("hst.pmap")
    True
    >>> newstyle_name("hst_acs_darkfile_0001.fits")
    True
    """
    return name.startswith(("hst", "jwst", "tobs"))

def newer(name1, name2):
    """Determine if `name1` is a more recent file than `name2` accounting for 
    limited differences in naming conventions. Official CDBS and CRDS names are 
    comparable using a simple text comparison,  just not to each other.
    
    >>> newer("s7g1700gl_dead.fits", "hst_cos_deadtab_0001.fits")
    False
    >>> newer("hst_cos_deadtab_0001.fits", "s7g1700gl_dead.fits")
    True
    >>> newer("s7g1700gl_dead.fits", "bbbbb.fits")
    True
    >>> newer("bbbbb.fits", "s7g1700gl_dead.fits")
    False
    >>> newer("hst_cos_deadtab_0001.rmap", "hst_cos_deadtab_0002.rmap")
    False
    >>> newer("hst_cos_deadtab_0002.rmap", "hst_cos_deadtab_0001.rmap")
    True
    """
    n1 = newstyle_name(name1)
    n2 = newstyle_name(name2)
    if n1:
        if n2: # compare CRDS names
            result = name1 > name2
        else:  # CRDS > CDBS
            result = True
    else:
        if n2:  # CDBS < CRDS
            result = False
        else:  # compare CDBS names
            result = name1 > name2
    log.verbose("Comparing filename time order:", repr(name1), ">", repr(name2), "-->", result)
    return result

# ============================================================================
        
def fits_difference(observatory, file1, file2):
    """Run fitsdiff on files named `file1` and `file2`.
    """
    assert file1.endswith(".fits"), \
        "File " + repr(file1) + " is not a FITS file."
    assert file2.endswith(".fits"), \
        "File " + repr(file2) + " is not a FITS file."
    _loc_file1 = rmap.locate_file(file1, observatory)
    _loc_file2 = rmap.locate_file(file2, observatory)
    pysh.sh("fitsdiff ${_loc_file1} ${_loc_file2}")

def text_difference(observatory, file1, file2):
    """Run UNIX diff on two text files named `file1` and `file2`.
    """
    assert os.path.splitext(file1)[-1] == os.path.splitext(file2)[-1], \
        "Files " + repr(file1) + " and " + repr(file2) + " are of different types."
    _loc_file1 = rmap.locate_file(file1, observatory)
    _loc_file2 = rmap.locate_file(file2, observatory)
    pysh.sh("diff -b -c ${_loc_file1} ${_loc_file2}")

def difference(observatory, file1, file2, primitive_diffs=False, check_diffs=False):
    """Difference different kinds of CRDS files (mappings, FITS references, etc.)
    named `file1` and `file2` against one another and print out the results 
    on stdout.
    """
    if rmap.is_mapping(file1):
        mapping_difference(observatory, file1, file2, primitive_diffs=primitive_diffs, check_diffs=check_diffs)
    elif file1.endswith(".fits"):
        fits_difference(observatory, file1, file2)
    else:
        text_difference(observatory, file1, file2)

 
def main():
    import crds
    crds.handle_version()
    
    parser = optparse.OptionParser("""usage: %prog [options] <file1> <file2>
        
        Appropriately difference CRDS mapping or reference files.
        """)
    
    parser.add_option("-J", "--jwst", dest="jwst",
        help="Locate files using JWST naming conventions.", 
        action="store_true")

    parser.add_option("-H", "--hst", dest="hst",
        help="Locate files using HST naming conventions.", 
        action="store_true")
    
    parser.add_option("-P", "--primitive-diffs", dest="primitive_diffs",
        help="Include primitive differences on replaced files.", 
        action="store_true")
    
    parser.add_option("-K", "--dont-check-diffs", dest="dont_check",
        help="Don't issue warnings about new rules or reversions.",
        action="store_true")

    options, args = log.handle_standard_options(sys.argv, parser=parser)
    
    if options.jwst:
        observatory = "jwst"
        assert not options.hst, "Can only specify one of --hst or --jwst"
    elif options.hst:
        observatory = "hst"
        assert not options.jwst, "Can only specify one of --hst or --jwst"
    elif "hst" in args[1]:
        observatory = "hst"
    elif "jwst" in args[1]:
        observatory = "jwst"
    else:
        observatory = "jwst"

    file1, file2 = args[1:]
    difference(observatory, file1, file2, primitive_diffs=options.primitive_diffs, 
               check_diffs=(not options.dont_check))

# ============================================================================

if __name__ == "__main__":
    main()
