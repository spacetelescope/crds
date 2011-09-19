"""This module is a command line script which synchronizes the local reference and
mapping caches to the CRDS server for a set of contexts.   Sync-ing requires
network access to the CRDS server.

% python -m crds.client.sync  hst_0001.pmap hst_0004.pmap

will update the caches so that the mappings and references required for those
contexts will be locally present.   Other .pmap .imap .rmap and .fits files 
will be deleted from CRDS_REFPATH and CRDS_MAPPATH.
"""
import argparse

import crds.client.api as api

def get_context_mappings(contexts):
    """Return the set of mappings which are pointed to by the mappings
    in `contexts`.
    """
    files = set()
    for context in contexts:
        files = files.union(api.get_mapping_names(context))
    return files

def add_context_mappings(contexts):
    """Gets all the mappings required to support `contexts`."""
    for context in contexts:
        api.dump_mappings(context)

def remove_context_mappings(remove_contexts,  keep_contexts=[]):
    """Removes all the mappings listed by `remove_contexts` which
    are not also listed in `keep_contexts.`
    """
    if not remove_contexts:
        return
    keep = get_context_mappings(keep_contexts)
    remove = get_context_mappings(remove_contexts)
    remove_files(remove_contexts[0], remove-keep)
    
def sync_context_mappings(only_contexts):
    """Gets all mappings required to support `only_contexts`.  Removes
    all mappings from the CRDS mapping cache which are not required for
    `only_contexts`.
    """
    if not only_contexts:
        return
    master_context = only_contexts[0]
    locator = rmap.get_cached_mapping(master_context).locate
    purge_dir = locator.get_crds_mappath()
    purge_maps = pysh.lines("find ${purge_dir} -name '*map'")
    purge_maps = set([x.strip() for x in purge_maps])
    keep = get_context_mappings(only_contexts)
    remove_files(master_context, purge_maps-keep)
    add_context_mappings(contexts)
    
def remove_files(context, files):
    """Remove the list of `files` basenames which are converted to fully
    specified CRDS paths using the locator module associated with context.
    """
    locator = rmap.get_cached_mapping(context).locate
    for file in files:
        where = locator.locate_file(file)
        log.verbose("removing", file, "from", where)
        try:
            pass
            # os.remove(where)
        except Exception, exc:
            log.error("exception during file removal")
            
def main():
    parser = argparse.ArgumentParser(
        description='Synchronize local mapping and reference caches to ' + 
                    'contexts, possibly removing or adding referenced files.')
    parser.add_argument(
        'contexts', metavar='C', type=str, nargs='+',
        help='a context determining a set of references and mappings.')
    parser.add_argument(
        '--add', dest='add_countexts', action='store_const',
        const=True, default=False,
        help='Add the files required for the specified contexts.')
    parser.add_argument(
        '--remove', dest='remove_contexts', action='store_const',
        const=True, default=False,
        help='Remove the files required for the specified contexts.')

args = parser.parse_args()
print args.accumulate(args.integers)
