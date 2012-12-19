"""This module is a command line script which dowloads the references and 
mappings required to support a set of contexts from the CRDS server:

Old references and mappings which are no longer needed can be automatically
removed by specifying --purge:

  % python -m crds.sync --range 1:2 --purge

will remove references or mappings not required by hst_0001.pmap or 
hst_0002.pmap in addition to downloading the required files.

XXX TODO
Or explicitly list the files you want cached:

  % python -m crds.sync <references or mappings to cache>

Synced datasets can be explicitly listed:

  % python -m crds.sync --contexts hst_0001.pmap hst_0002.pmap --datasets *.fits

"""
import sys
import os
import os.path
import argparse
import re

from argparse import RawTextHelpFormatter

import crds.client.api as api
from crds import (rmap, log, data_file)
import crds

# ============================================================================

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
        log.verbose("Syncing mapping", repr(context))
        api.dump_mappings(context)
    if purge:
        purge_mappings(only_contexts)
        
def purge_mappings(only_contexts):
    """Remove all mappings not references under pmaps `only_contexts."""
    pmap = rmap.get_cached_mapping(only_contexts[0])
    purge_maps = rmap.list_mappings('*.[pir]map', pmap.observatory)
    keep = get_context_mappings(only_contexts)
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
        log.verbose("Syncing references for", repr(context))
        api.dump_references(context)
    if purge:
        purge_references(only_contexts)

def purge_references(only_contexts):
    """Remove all references not references under pmaps `only_contexts`."""
    pmap = rmap.get_cached_mapping(only_contexts[0])
    purge_refs = rmap.list_references("*", pmap.observatory)
    keep = get_context_references(only_contexts)
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

# ============================================================================

def sync_datasets(contexts, datasets):
    """Sync mappings and references for datasets with respect to `contexts`."""
    for context in contexts:
        observatory = data_file.get_observatory(context)
        for dataset in datasets:
            try:
                header = data_file.get_conditioned_header(dataset, observatory=observatory)
            except Exception, exc:
                log.error("Failed to get matching parameters from", repr(dataset))
                continue
            try:
                bestrefs = crds.getreferences(header, context=context, observatory=observatory)
            except Exception, exc:
                log.error("Failed to sync references for dataset", repr(dataset), 
                          "under context", repr(context), ":", str(exc))

# ============================================================================

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
        contexts = []
    return contexts

def sync_explicit_files(files):
    """Cache the listed `files`."""
    log.info("Syncing explicitly listed files.")
    mappings, references = [], []
    for file in files:
        file = os.path.basename(file)
        if rmap.is_mapping(file):
            mappings.append(file)
        else:
            references.append(file)
    context = api.get_default_context()
    if mappings:
        api.dump_mappings(context, mappings=mappings)
    if references:
        api.dump_references(context, references=references)


def main():
    import crds
    crds.handle_version()
    
    try:
        info = api.get_server_info()
    except Exception:
        log.error("Failed connecting to CRDS server at", repr(api.get_crds_server()))
        sys.exit(-1)

    parser = argparse.ArgumentParser(
        formatter_class = RawTextHelpFormatter,
        description = \
"""Synchronize local mapping and reference caches for the given contexts by
downloading missing files from the CRDS server and/or archive.

* Primitive syncing can be done by explicitly listing the files you wish to cache:

     % python -m crds.sync  hst_0001.pmap hst_acs_darkfile_0037.fits

* Typically syncing is done with respect to particular CRDS contexts:

    Synced contexts can be explicitly listed:
    
      % python -m crds.sync  --contexts hst_0001.pmap hst_0002.pmap
    
    Synced contexts can be specified as a numerical range:
    
      % python -m crds.sync --range 1:2
    
    Synced contexts can be specified as --all contexts:
    
      % python -m crds.sync --all

* Typically reference file retrieval behavior is driven by switches:

      Cache all references for the specified contexts like this:

      % python -m crds.sync  --contexts hst_0001.pmap hst_0002.pmap  --references   
      
      Cache the best references for the specified datasets like this:
    
      % python -m crds.sync  --contexts hst_0001.pmap hst_0002.pmap  --datasets  <dataset_files...>        
""")
    
    parser.add_argument('--contexts', metavar='CONTEXT', type=mapping, nargs='*',
        help='A list of contexts to sync.  dependent mappings are loaded recursively.')
    parser.add_argument('--references', action='store_true', dest="get_context_references",
                        help='get all the references for the specified contexts.')
    parser.add_argument('--datasets', metavar='DATASET', type=dataset, nargs='*',
        help='a list of datasets for which to prefetch references.')
    parser.add_argument('--all', action='store_true',
        help='Operate with respect to all known contexts.')
    parser.add_argument("--range", metavar="MIN:MAX",  type=nrange, dest="range", default=None,
        help='Fetch files for pipeline context ids between <MIN> and <MAX>.')
    parser.add_argument('--purge', action='store_true', dest="purge",
        help='Remove reference files and mappings not referred to by contexts.')
    parser.add_argument('--verbose', action='store_true', dest="verbose",
        help='Enable nominal debug output.')
    parser.add_argument("files", nargs="*", help="Synced files can be explicitly listed.")
    args = parser.parse_args()
    
    if args.verbose:
        log.set_verbose()
    
    contexts = determine_contexts(args)
    if contexts:
        sync_context_mappings(contexts, args.purge)
        if args.datasets:
            sync_datasets(contexts, args.datasets)
        elif args.get_context_references:
            sync_context_references(contexts, args.purge)
    elif args.files:
        sync_explicit_files(args.files)

if __name__ == "__main__":
    main()

