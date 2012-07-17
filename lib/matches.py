"""This module is a command line script which lists the match tuples associated
with a reference file.

% python -m crds.matches  hst_0001.pmap u451251ej_bpx.fits
(('observatory', 'hst'), ('instrument', 'acs'), ('filekind', 'bpixtab'), ('DETECTOR', 'SBC'), ('DATE-OBS', '1993-01-01'), ('TIME-OBS', '00:00:00')) 


The core function find_full_match_paths() returns a list of 
"match paths",  lists of parkey value assignment tuples:

>>> find_full_match_paths("hst.pmap", "u451251ej_bpx.fits")
[((('observatory', 'hst'), ('instrument', 'acs'), ('filekind', 'bpixtab')), (('DETECTOR', 'SBC'),), (('DATE-OBS', '1993-01-01'), ('TIME-OBS', '00:00:00')))]

A related function finds only the "match tuples",  the value portion of a match
expression for HST:

>>> find_match_tuples("hst.pmap", "u451251ej_bpx.fits")
[('SBC',)]

observatory and filekind are really pseudo-parkeys because they are not
directly present in dataset file headers,  whereas the other parkeys all 
appear as header values.

"""
import sys

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
    # if not filename.endswith(".fits"):
    #     raise ValueError("Must be a reference (.fits) file.")
    return filename

# ===================================================================

def find_full_match_paths(context, reffile):
    """Return the list of full match paths for `reference` in `context` as a
    list of tuples of tuples.   Each inner tuple is a (var, value) pair.
    
    Returns [((context_tuples,),(match_tuple,),(useafter_tuple,)), ...]
    """
    ctx = rmap.get_cached_mapping(context)
    return ctx.file_matches(reffile)

def find_match_tuples(context, reffile):
    """Return the list of match tuples for `reference` in `context`.   
    
    Returns [ match_tuple, ...] where match_tuple = ((var, value), ...)
    """
    ctx = rmap.get_cached_mapping(context)
    result = []
    for path in ctx.file_matches(reffile):
        match_tuple = tuple([tup[1] for tup in path[1]])
        result.append(match_tuple)
    return result

def main():
    """Process command line parameters in to a context and list of
    reference files.   Print out the match tuples within the context
    which contain the reference files.
    """
    import crds
    crds.handle_version()
    
    # Check inputs
    context = mapping(sys.argv[1])
    for file_ in sys.argv[2:]:
        reference(file_)
        
    # Print match tuples
    for file_ in sys.argv[2:]:
        ref = reference(file_)
        if len(sys.argv) > 3:
            log.write(ref, ":")
        for match in find_match_tuples(context, ref) or ["none"]:
            log.write(tuple(match))
        log.write()

if __name__ == "__main__":
    main()

