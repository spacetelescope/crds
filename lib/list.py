"""This module is a command line script which lists the reference and/or
mapping files associated with the specified contexts by consulting the CRDS
server.

Contexts to list can be specified explicitly:

% python -m crds.list  hst_0001.pmap hst_0002.pmap --references
vb41935ij_bia.fits 
vb41935jj_bia.fits 
vb41935kj_bia.fits 
...

Contexts to list can be specified as a range:

% python -m crds.list --observatory hst --range 1:2 --references
vb41935lj_bia.fits 
vb41935mj_bia.fits 
vb41935nj_bia.fits 
vb41935oj_bia.fits
...

Contexts to list can be specified as --all contexts:

% python -m crds.list --observatory hst --all --mappings
hst.pmap 
hst_0001.pmap 
hst_0002.pmap 
hst_acs.imap 
hst_acs_0001.imap 
hst_acs_0002.imap 
hst_acs_atodtab.rmap 
hst_acs_biasfile.rmap 
hst_acs_bpixtab.rmap 
hst_acs_ccdtab.rmap 
...

"""
import argparse

from crds import log

from crds.sync import (mapping, observatory, nrange, determine_contexts,
                              get_context_references, get_context_mappings)

def list_references(contexts):
    """Consult the server and print the names of all references associated with
    the given contexts.
    """
    for ref in sorted(get_context_references(contexts)):
        log.write(ref)

def list_mappings(contexts):
    """Consult the server and print the names of all CRDS mappings associated 
    with the given contexts.
    """
    for mapfile in sorted(get_context_mappings(contexts)):
        log.write(mapfile)

def main():
    """Parse the command line into contexts and command qualifiers,  then list
    files accordingly.
    """
    import crds
    crds.handle_version()
    log.set_verbose(True)
    parser = argparse.ArgumentParser(
        description='List reference and/or mapping files " + \
            "associated with the specified contexts.')
    parser.add_argument('--references', action='store_true',
        dest="list_references",
        help='print names of reference files referred to by contexts')
    parser.add_argument('--mappings', action='store_true',
        dest="list_mappings",
        help='print names of mapping files referred to by contexts')
    parser.add_argument(
        'contexts', metavar='CONTEXT', type=mapping, nargs='*',
        help='a list of contexts determining files to list.')
    parser.add_argument('--all', action='store_true',
        help='list files for all known contexts.')
    parser.add_argument("--range", metavar="MIN:MAX",  type=nrange,
        dest="range", default=None,
        help='list files for context ids between <MIN> and <MAX>.')
    args = parser.parse_args()
    
    contexts = determine_contexts(args)
    
    if args.list_references:
        list_references(contexts)
    if args.list_mappings:
        list_mappings(contexts)

if __name__ == "__main__":
    main()

