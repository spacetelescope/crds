"""This module is a command line script which lists the match tuples associated
with a reference file.

% python -m crds.matches  hst_0001.pmap u451251ej_bpx.fits
(('observatory', 'hst'), ('INSTRUME', 'acs'), ('filekind', 'bpixtab'), ('DETECTOR', 'SBC'), ('DATE-OBS', '1993-01-01'), ('TIME-OBS', '00:00:00')) 


The core function find_match_tuples() returns a list of "match paths",  lists of
parkey value assignment tuples:

>>> find_match_tuples("hst.pmap", "u451251ej_bpx.fits")
[((('observatory', 'hst'), ('INSTRUME', 'acs'), ('filekind', 'bpixtab')), (('DETECTOR', 'SBC'),), (('DATE-OBS', '1993-01-01'), ('TIME-OBS', '00:00:00')))]

observatory and filekind are really pseudo-parkeys because they are not
directly present in dataset file headers,  whereas the other parkeys all 
appear as header values.

"""
import sys
import argparse

from crds import rmap, log

# ===================================================================

def test():
    """Run any doctests."""
    import doctest, crds.matches
    return doctest.testmod(crds.matches)

# ===================================================================

# For use with argparse.

def mapping(filename):
    """Raise an exception if `filename` does not specify a mapping file."""
    if not rmap.is_mapping(filename):
        raise ValueError("Must be a .pmap, .imap, or .rmap file.")
    return filename

def reference(filename):
    """Raise and exception if `filename` does not specify a reference file."""
    if not filename.endswith(".fits"):
        raise ValueError("Must be a reference (.fits) file.")
    return filename

# ===================================================================

def find_full_match_paths(context, reference):
    """Return the list of full match paths for `reference` in `context` as a
    list of tuples of tuples.   Each inner tuple is a (var, value) pair.
    
    Returns [((context_tuples,),(match_tuple,),(useafter_tuple,)), ...]
    """
    ctx = rmap.get_cached_mapping(context)
    return ctx.file_matches(reference)

def find_match_tuples(context, reference):
    """Return the list of match tuples for `reference` in `context`.   
    
    Returns [ match_tuple, ...] where match_tuple = ((var, value), ...)
    """
    ctx = rmap.get_cached_mapping(context)
    result = []
    for path in ctx.file_matches(reference):
        match_tuple = tuple([tup[1] for tup in path[1]])
        result.append(match_tuple)
    return result

def main():
    # Check inputs
    context = mapping(sys.argv[1])
    for file in sys.argv[2:]:
        reference(file)
        
    # Print match tuples
    for file in sys.argv[2:]:
        ref = reference(file)
        if len(sys.argv) > 3:
            log.write(ref, ":")
        for match in find_match_tuples(context, ref) or ["none"]:
            log.write(tuple(match))
        log.write()

if __name__ == "__main__":
    main()

