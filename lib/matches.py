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

def find_match_tuples(context, reference):
    ctx = rmap.get_cached_mapping(context)
    return ctx.file_matches(reference)

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

