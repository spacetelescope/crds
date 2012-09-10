"""This module is a command line script which dowloads the references and 
mappings required to support a set of contexts from the CRDS server:

Synced contexts can be explicitly listed:

  % python -m crds.client.sync  --contexts hst_0001.pmap hst_0002.pmap

Synced datasets can be explicitly listed:

  % python -m crds.client.sync --datasets  *.fits

Synced contexts can be specified as a range:

  % python -m crds.client.sync --range 1:2

Synced contexts can be specified as --all contexts:

  % python -m crds.client.sync --all

XXX TODO
Or explicitly list the files you want cached:

  % python -m crds.client.sync <references or mappings to cache>

Old references and mappings which are no longer needed can be automatically
removed by specifying --purge:

  % python -m crds.client.sync --range 1:2 --purge

will remove references or mappings not required by hst_0001.pmap or 
hst_0002.pmap in addition to downloading the required files.
"""
import sys
import os
import os.path
import argparse
import re

import crds.client.api as api
from crds import (rmap, pysh, log, data_file)

def get_context_mappings(contexts):
    """Return the set of mappings which are pointed to by the mappings
    in `contexts`.
    """
    files = set()
    for context in contexts:
        pmap = rmap.get_cached_mapping(context)
        files = files.union(pmap.mapping_names())
    return files

def sync_context_mappings(only_contexts, purge=False):
    """Gets all mappings required to support `only_contexts`.  Removes
    all mappings from the CRDS mapping cache which are not required for
    `only_contexts`.
    """
    if not only_contexts:
        return
    for context in only_contexts:
        api.dump_mappings(context)
    pmap = rmap.get_cached_mapping(only_contexts[0])
    purge_maps = rmap.list_mappings('*.[pir]map', pmap.observatory)
    keep = get_context_mappings(only_contexts)
    if purge:
        remove_files(pmap.observatory, purge_maps-keep, "mapping")
    
def get_context_references(contexts):
    """Return the set of mappings which are pointed to by the mappings
    in `contexts`.
    """
    files = set()
    for context in contexts:
        files = files.union(api.get_reference_names(context))
    return files

def sync_context_references(only_contexts, purge=False):
    """Gets all references required to support `only_contexts`.  Removes
    all references from the CRDS reference cache which are not required for
    `only_contexts`.
    """
    if not only_contexts:
        return
    for context in only_contexts:
        api.dump_references(context)
    pmap = rmap.get_cached_mapping(only_contexts[0])
    purge_refs = rmap.list_references("*", pmap.observatory)
    keep = get_context_references(only_contexts)
    if purge:
        remove = purge_refs - keep
        remove_files(pmap.observatory, remove, "reference")
    
def remove_files(observatory, files, kind):
    """Remove the list of `files` basenames which are converted to fully
    specified CRDS paths using the locator module associated with context.
    """
    if not files:
        log.verbose("No " + kind + "s to remove.")
    for file in files:
        where = rmap.locate_file(file, observatory)
        log.verbose("Removing", file, "from", where)
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

def dataset(string):
    if data_file.is_dataset(string):
        return string
    else:
        raise ValueError("Parameter " + repr(string) + 
                         " does not appear to be a dataset filename.")

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
    all_contexts = api.list_mappings(glob_pattern="*.pmap")
    if args.contexts:
       assert not args.range, 'Cannot specify explicit contexts and --range'
       assert not args.all, 'Cannot specify explicit contexts and --all'
       # permit instrument and reference mappings,  not just pipelines:
       all_contexts = api.list_mappings(glob_pattern="*.*map")
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
        raise ValueError("Must explicitly list contexts, " +
                         "a context id --range, or --all.") 
    return contexts

def main():
    import crds
    crds.handle_version()
    log.set_verbose(True)
    parser = argparse.ArgumentParser(
        description='Synchronize local mapping and reference caches to ' + 
                    'the given contexts, removing files not referenced.')
    parser.add_argument(
        '--contexts', metavar='CONTEXT', type=mapping, nargs='*',
        help='a list of contexts to sync.')
    parser.add_argument('--mappings-only', action='store_true', 
        dest="mappings_only",
        help='just get the mapping files, not the references')
    parser.add_argument(
        '--datasets', metavar='DATASET', type=dataset, nargs='*',
        help='a list of datasets for which to prefetch references.')
    parser.add_argument('--all', action='store_true',
        help='fetch files for all known contexts.')
    parser.add_argument("--range", metavar="MIN:MAX",  type=nrange,
        dest="range", default=None,
        help='fetch files for context ids between <MIN> and <MAX>.')
    parser.add_argument('--purge', action='store_true', dest="purge",
        help='remove reference files and mappings not referred to by contexts')
    args = parser.parse_args()
    
    contexts = determine_contexts(args)
    if contexts:
        sync_context_mappings(contexts, args.purge)
    if not args.mappings_only:
        sync_context_references(contexts, args.purge)


if __name__ == "__main__":
    main()

