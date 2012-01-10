"""This module is a command line script which synchronizes the local reference and
mapping caches to the CRDS server for a set of contexts.   Sync-ing requires
network access to the CRDS server.

% python -m crds.client.sync  hst_0001.pmap hst_0004.pmap

will update the caches so that the mappings and references required for those
contexts will be locally present.   

WARNING:  All .pmap .imap .rmap and .fits files not referenced from the 
sync'ed contexts will be deleted from CRDS_REFPATH and CRDS_MAPPATH.
"""
import sys
import os
import os.path
import argparse
import re

import crds.client.api as api
from crds import (rmap, pysh, log)

def get_context_mappings(contexts):
    """Return the set of mappings which are pointed to by the mappings
    in `contexts`.
    """
    files = set()
    for context in contexts:
        files = files.union(api.get_mapping_names(context))
    return files

def sync_context_mappings(only_contexts, purge=False):
    """Gets all mappings required to support `only_contexts`.  Removes
    all mappings from the CRDS mapping cache which are not required for
    `only_contexts`.
    """
    if not only_contexts:
        return
    add_context_mappings(only_contexts)
    master_context = only_contexts[0]
    # locator = rmap.get_cached_mapping(master_context).locate
    purge_dir = rmap.get_crds_mappath()
    purge_maps = pysh.lines("find ${purge_dir} -name '*.[pir]map'")
    purge_maps = set([os.path.basename(x.strip()) for x in purge_maps])
    keep = get_context_mappings(only_contexts)
    if purge:
        remove_files(master_context, purge_maps-keep, "mapping")
    
def add_context_mappings(contexts):
    """Gets all the mappings required to support `contexts`."""
    for context in contexts:
        api.dump_mappings(context)

def get_context_references(contexts):
    """Return the set of mappings which are pointed to by the mappings
    in `contexts`.
    """
    files = set()
    for context in contexts:
        files = files.union(api.get_reference_names(context))
    return files

def sync_context_references(only_contexts, purge=False):
    """Gets all mappings required to support `only_contexts`.  Removes
    all mappings from the CRDS mapping cache which are not required for
    `only_contexts`.
    """
    if not only_contexts:
        return
    add_context_references(only_contexts)
    master_context = only_contexts[0]
    # locator = rmap.get_cached_mapping(master_context).locate
    purge_dir = rmap.get_crds_refpath()
    purge_refs = pysh.lines("find ${purge_dir} "
                            "-name '*.fits' ")
                            # "-o -name '*.r*h' "
                            # "-o -name '*.r*d'")
    purge_refs = set([os.path.basename(x.strip()) for x in purge_refs])
    keep = get_context_references(only_contexts)
    if purge:
        remove = purge_refs - keep
        remove_files(master_context, remove, "reference")
    
def add_context_references(contexts):
    """Gets all the mappings required to support `contexts`."""
    for context in contexts:
        api.dump_references(context)
    
def remove_files(context, files, kind):
    """Remove the list of `files` basenames which are converted to fully
    specified CRDS paths using the locator module associated with context.
    """
    if not files:
        log.verbose("No " + kind + "s to remove.")
    # locator = rmap.get_cached_mapping(context).locate
    for file in files:
        where = rmap.locate_file(file)
        log.verbose("removing", file, "from", where)
        try:
            os.remove(where)
        except Exception, exc:
            log.error("exception during file removal")

def mapping(string):
    if api.is_known_mapping(string):
        return string
    else:
        raise ValueError("Parameter " + repr(string) + 
                         " is not a known CRDS mapping.")        
def observatory(string):
    string = string.lower()
    assert string in ["hst","jwst"], "Unknown observatory " + repr(string)
    return string

def nrange(string):
    assert re.match("\d+:\d+", string), \
        "Invalid context range specification " + repr(string)
    rmin, rmax = [int(x) for x in string.split(":")]
    assert 0 <= rmin <= rmax, "Invalid range values"
    return rmin, rmax

def determine_contexts(args):
    """Support explicit specification of contexts, context id range, or all."""
    all_contexts = api.list_mappings(args.observatory, "*.pmap")
    if args.contexts:
       assert not args.range, 'Cannot specify explicit contexts and --range'
       assert not args.all, 'Cannot specify explicit contexts and --all'
       # permit instrument and reference mappings,  not just pipelines:
       all_contexts = api.list_mappings(args.observatory, "*.*map")
       for context in args.contexts:
           assert context in all_contexts, "Unknown context " + repr(context)
       contexts = args.contexts
    elif args.all:
        assert not args.range, "Cannot specify --all and --range"
        contexts = all_contexts
    elif args.range:
        rmin, rmax = args.range
        contexts = []
        for context in all_contexts:
            match = re.match("\w+_(\d+).pmap", context)
            if match:
                id = int(match.group(1))
                if rmin <= id <= rmax:
                    contexts.append(context)
    else:
        raise ValueError("Must explicitly list contexts, a context id --range, or --all.") 
    return contexts

def list_references(contexts):
    refs = set()
    for context in contexts:
        refs = refs.union(api.get_reference_names(context))
    for ref in sorted(list(refs)):
        log.write(ref)

def list_mappings(contexts):
    mappings = set()
    for context in contexts:
        mappings = mappings.union(api.get_mapping_names(context))
    for mapping in sorted(list(mappings)):
        log.write(mapping)

def main():
    log.set_verbose(True)
    parser = argparse.ArgumentParser(
        description='Synchronize local mapping and reference caches to ' + 
                    'the given contexts, removing files not referenced.')
    parser.add_argument(
        'contexts', metavar='CONTEXT', type=mapping, nargs='*',
        help='a list of contexts determining files to sync.')
    parser.add_argument('--purge', action='store_true',
        help='remove reference files and mappings not referred to by contexts')
    parser.add_argument('--list-references', action='store_true',
        dest="list_references",
        help='print names of reference files referred to by contexts')
    parser.add_argument('--list-mappings', action='store_true',
        dest="list_mappings",
        help='print names of mapping files referred to by contexts')
    parser.add_argument('--all', action='store_true',
        help='fetch files for all known contexts.')
    parser.add_argument(
        "--observatory", dest="observatory", metavar="OBSERVATORY", 
        type=observatory, default="hst",
        help='observatory to sync files for,  "hst" or "jwst".')
    parser.add_argument("--range", metavar="MIN:MAX",  type=nrange,
        dest="range", default=None,
        help='fetch files for context ids between <MIN> and <MAX>.')
    args = parser.parse_args()
    
    contexts = determine_contexts(args)
    
    if args.list_references:
        list_references(contexts)
    if args.list_mappings:
        list_mappings(contexts)

    if not args.list_references and not args.list_mappings:
        sync_context_mappings(contexts, args.purge)
        sync_context_references(contexts, args.purge)

if __name__ == "__main__":
    main()

