"""This module differences two CRDS reference or mapping files on the local
system.   It supports specification of the files using only the basenames or
a full path.   Currently it operates on mapping, FITS, or text files.
"""
import sys
import os
import optparse

from crds import rmap, log, pysh

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
    map1 = rmap.get_cached_mapping(file1)
    map2 = rmap.get_cached_mapping(file2)
    differences = map1.difference(map2)
    return differences

def diff_action(d):
    """Return 'add', 'replace', or 'delete' based on action represented by
    difference tuple `d`.
    """
    if "replace" in d[-1]:
        return "replace"
    elif "add" in d[-1]:
        return "add"
    elif "delete" in d[-1]:
        return "delete"
    else:
        return "unknown: " + repr(d)

def mapping_difference(observatory, file1, file2, primitive_diffs=False):
    """Print the logical differences between CRDS mappings named `file1` 
    and `file2`.
    """
    differences = mapping_diffs(file1, file2)
    if primitive_diffs:
        for pair in mapping_pairs(differences):
            log.write("="*80)
            log.write(pair)
            text_difference(observatory, pair[0], pair[1])
    for diff in differences:
        diff = rq(diff)
        if primitive_diffs:
            log.write("="*80)
        log.write(diff)
        if primitive_diffs:
            if "replaced" in diff[-1]:
                old, new = diff_replace_old_new(diff)
                difference(observatory, old, new, primitive_diffs=primitive_diffs)

def mapping_pairs(differences):
    pairs = set()
    for diff in differences:
        for pair in diff:
            if len(pair) == 2 and rmap.is_mapping(pair[0]):
                pairs.add(pair)
    return sorted(pairs)
        
def rq(diff):
    """Remove repr str quoting."""
    return diff[:-1] + (diff[-1].replace("'",""),)

def diff_replace_old_new(diff):
    """Return the (old, new) filenames from difference tuple `diff`."""
    _replaced, old, _with, new = diff[-1].split()
    return old, new
    
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

def difference(observatory, file1, file2, primitive_diffs=False):
    """Difference different kinds of CRDS files (mappings, FITS references, etc.)
    named `file1` and `file2` against one another and print out the results 
    on stdout.
    """
    if rmap.is_mapping(file1):
        mapping_difference(observatory, file1, file2, primitive_diffs=primitive_diffs)
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
    difference(observatory, file1, file2, primitive_diffs=options.primitive_diffs)

# ============================================================================

if __name__ == "__main__":
    main()
