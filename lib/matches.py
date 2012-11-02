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
import optparse

from crds import rmap, log, pysh, config

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
        raise ValueError("Must be a .pmap, .imap, or .rmap file: " + repr(filename))
    return filename

def reference(filename):
    """Raise and exception if `filename` does not specify a reference file."""
    if not config.is_reference(filename):
        raise ValueError("Must be a reference (.fits) file: " + repr(filename))
    return filename

# ===================================================================

def find_full_match_paths(context, reffile):
    """Return the list of full match paths for `reference` in `context` as a
    list of tuples of tuples.   Each inner tuple is a (var, value) pair.
    
    Returns [((context_tuples,),(match_tuple,),(useafter_tuple,)), ...]
    """
    ctx = rmap.get_cached_mapping(context)
    return ctx.file_matches(reffile)

def find_full_match_tuples(context, reference):
    """Return a list of the complete match paths of `reference` within `context`.
    
    e.g. [('hst', 'acs', 'dgeofile', 'HRC', 'CLEAR1S', 'F220W', '2002-03-01', '00:00:00')]

    """
    full = []
    for match in find_full_match_paths(context, reference):
        tup = ()
        for part in match:
            tup = tup + tuple([t[1] for t in part])
        full.append(tup)
    return full

def find_match_tuples(context, reffile):
    """Return the list of match tuples for `reference` in `context`.   
    
    Returns [ match_tuple, ...] where match_tuple = (value, ...)
    """
    ctx = rmap.get_cached_mapping(context)
    result = []
    for path in ctx.file_matches(reffile):
        match_tuple = tuple([tup[1] for tup in path[1]])
        result.append(match_tuple)
    return result

def dump_match_tuples(context, references, finder):
    """Print out the match tuples for `references` under `context` as located
    and expressed by `finder()`
    """
    for ref in references:
        if len(references) > 1:
            log.write(ref, ":")
        matches = finder(context, ref)
        if matches:
            for match in matches:        
                log.write(tuple(match))
        else:
            log.write("none")

def main():
    """Process command line parameters in to a context and list of
    reference files.   Print out the match tuples within the context
    which contain the reference files.
    """
    import crds
    crds.handle_version()
    
    parser = optparse.OptionParser("usage: %prog [options] <context> <references...>")
    parser.add_option("-f", "--full", dest="full",
        help="Show the complete match path through the mapping hierarchy.",
        action="store_true")
    options, args = log.handle_standard_options(sys.argv, parser=parser)
    
    if len(args) == 1:
        sys.argv.append("--help")
        parser.parse_args(sys.argv)
        sys.exit(-1)
    
    # Check inputs
    context = mapping(args[1])
    references = args[2:]
    
    for file_ in references:
        reference(file_)

    if options.full:
        dump_match_tuples(context, references, find_full_match_tuples)
    else:   
        # Print match tuples
        dump_match_tuples(context, references, find_match_tuples)

if __name__ == "__main__":
    main()

