"""This module is a command line script which synchronizes the local reference and
mapping caches to the CRDS server for a set of contexts.   Sync-ing requires
network access to the CRDS server.

% python -m crds.client.sync  hst_0001.pmap hst_0004.pmap

will update the caches so that the mappings and references required for those
contexts will be locally present.   Other .pmap .imap .rmap and .fits files 
will be deleted from CRDS_REFPATH and CRDS_MAPPATH.
"""
import os
import os.path
import argparse

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

def sync_context_mappings(only_contexts):
    """Gets all mappings required to support `only_contexts`.  Removes
    all mappings from the CRDS mapping cache which are not required for
    `only_contexts`.
    """
    if not only_contexts:
        return
    add_context_mappings(only_contexts)
    master_context = only_contexts[0]
    locator = rmap.get_cached_mapping(master_context).locate
    purge_dir = locator.get_crds_mappath()
    purge_maps = pysh.lines("find ${purge_dir} -name '*map'")
    purge_maps = set([os.path.basename(x.strip()) for x in purge_maps])
    keep = get_context_mappings(only_contexts)
    remove_files(master_context, purge_maps-keep)
    
def remove_files(context, files):
    """Remove the list of `files` basenames which are converted to fully
    specified CRDS paths using the locator module associated with context.
    """
    if not files:
        log.info("No files to remove.")
    locator = rmap.get_cached_mapping(context).locate
    for file in files:
        where = locator.locate_file(file)
        log.info("removing", file, "from", where)
        try:
            os.remove(where)
        except Exception, exc:
            log.error("exception during file removal")

def add_context_mappings(contexts):
    """Gets all the mappings required to support `contexts`."""
    for context in contexts:
        api.dump_mappings(context)

def mapping(string):
    if api.is_known_mapping(string):
        return string
    else:
        raise ValueError("Parameter " + repr(string) + 
                         " is not a known CRDS mapping.")

def main():
    log.set_verbose(True)
    parser = argparse.ArgumentParser(
        description='Synchronize local mapping and reference caches to ' + 
                    'contexts, possibly removing files not referenced.')
    parser.add_argument(
        'contexts', metavar='CONTEXT', type=mapping, nargs='+',
        help='a context determining a set of references and mappings.')
    args = parser.parse_args()
    sync_context_mappings(args.contexts)

if __name__ == "__main__":
    main()

