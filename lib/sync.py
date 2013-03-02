"""This module is a command line script which dowloads the references and 
mappings required to support a set of contexts from the CRDS server:

Old references and mappings which are no longer needed can be automatically
removed by specifying --purge:

  % python -m crds.sync --range 1:2 --purge

will remove references or mappings not required by hst_0001.pmap or 
hst_0002.pmap in addition to downloading the required files.

Or explicitly list the files you want cached:

  % python -m crds.sync <references or mappings to cache>

Synced datasets can be explicitly listed:

  % python -m crds.sync --contexts hst_0001.pmap hst_0002.pmap --datasets *.fits
"""
import sys
import os
import os.path

import crds.client.api as api
from crds import (rmap, log, data_file, cmdline)
import crds

# ============================================================================

def remove_files(observatory, files, kind):
    """Remove the list of `files` basenames which are converted to fully
    specified CRDS paths using the locator module associated with context.
    """
    if not files:
        log.verbose("No " + kind + "s to remove.")
    for filename in files:
        where = rmap.locate_file(filename, observatory)
        log.verbose("Removing", filename, "from", where)
        with log.error_on_exception("File removal failed for", repr(where)):
            os.remove(where)

# ============================================================================

class SyncScript(cmdline.ContextsScript):
    """Command line script for synchronizing local CRDS file cache with CRDS server."""

    description = """
    Synchronize local mapping and reference caches for the given contexts by
    downloading missing files from the CRDS server and/or archive.
    """
    
    epilog = """    
    * Primitive syncing can be done by explicitly listing the files you wish to cache:
    
         % python -m crds.sync  hst_0001.pmap hst_acs_darkfile_0037.fits
    
    * Typically syncing is done with respect to particular CRDS contexts:
    
        Synced contexts can be explicitly listed:
        
          % python -m crds.sync  --contexts hst_0001.pmap hst_0002.pmap
        
        Synced contexts can be specified as a numerical range:
        
          % python -m crds.sync --range 1:2
        
        Synced contexts can be specified as --all contexts:
        
          % python -m crds.sync --all
          
        Files from unspecified contexts can be removed like this:
        
          % python -m crds.sync  --contexts hst_0004.pmap hst_0005.pmap --purge
          this would remove references and mappings for 0,1,2 which are not in 4 or 5.
    
    * Typically reference file retrieval behavior is driven by switches:
    
          Cache all references for the specified contexts like this:
    
          % python -m crds.sync  --contexts hst_0001.pmap hst_0002.pmap  --references   
          
          Cache the best references for the specified datasets like this:
        
          % python -m crds.sync  --contexts hst_0001.pmap hst_0002.pmap  --datasets  <dataset_files...>        
    """
    
    # ------------------------------------------------------------------------------------------
    
    def add_args(self):    
        self.add_argument('--references', action='store_true', dest="get_references",
                          help='Get all the references for the specified contexts.')        
        self.add_argument('--datasets', metavar='DATASET', type=cmdline.dataset, nargs='*',
                          help='List dataset files for which to prefetch references.')
        self.add_argument("files", nargs="*", help="Explicitly list files to be synced.")
        self.add_argument('--purge', action='store_true', dest="purge",
                          help='Remove reference files and mappings not referred to by contexts.')
        self.add_argument('-i', '--ignore-cache', action='store_true', dest="ignore_cache",
                          help="Download sync'ed files even if they're already in the cache.")
        super(SyncScript, self).add_args()

    # ------------------------------------------------------------------------------------------
    
    def main(self):
        """Synchronize files."""
        self.test_server_connection()
        if self.contexts:
            self.sync_context_mappings()
            if self.args.datasets:
                self.sync_datasets()
            elif self.args.get_references:
                self.sync_context_references()
        elif self.args.files:
            self.sync_explicit_files()
        else:
            log.error("Define --contexts and/or --datasets,  or explicitly list particular files to sync.")
            sys.exit(-1)

    # ------------------------------------------------------------------------------------------
    
    def sync_context_mappings(self):
        """Gets all mappings required to support `self.contexts`.  
        if purge:  
            Remove all mappings from the CRDS mapping cache which are not required for `self.contexts`.
        if ignore_cache:
            Re-download all required files.
        """
        if not self.contexts:
            return
        for context in self.contexts:
            log.verbose("Syncing mapping", repr(context))
            api.dump_mappings(context, ignore_cache=self.args.ignore_cache)
        if self.args.purge:
            self.purge_mappings()
            
    def purge_mappings(self):
        """Remove all mappings under pmaps `only_contexts`."""
        pmap = rmap.get_cached_mapping(self.contexts[0])
        purge_maps = set(rmap.list_mappings('*.[pir]map', pmap.observatory))
        keep = self.get_context_mappings()
        remove_files(pmap.observatory, sorted(purge_maps-keep), "mapping")
        
    # ------------------------------------------------------------------------------------------
    
    def sync_context_references(self):
        """Gets all references required to support `only_contexts`.  Removes
        all references from the CRDS reference cache which are not required for
        `only_contexts`.
        """
        if not self.contexts:
            return
        for context in self.contexts:
            log.verbose("Syncing references for", repr(context))
            api.dump_references(context, ignore_cache=self.args.ignore_cache)
        if self.args.purge:
            self.purge_references()
    
    def purge_references(self):
        """Remove all references not references under pmaps `only_contexts`."""
        pmap = rmap.get_cached_mapping(self.contexts[0])
        purge_refs = rmap.list_references("*", pmap.observatory)
        keep = self.get_context_references()
        remove = purge_refs - keep
        remove_files(pmap.observatory, remove, "reference")
    
    # ------------------------------------------------------------------------------------------
    
    def sync_datasets(self):
        """Sync mappings and references for datasets with respect to `contexts`."""
        if not self.contexts:
            log.error("Define --contexts under which references are fetched for --datasets.""")
            sys.exit(-1)
        for context in self.contexts:
            for dataset in self.args.datasets:
                log.info("Syncing context '%s' dataset '%s'." % (context, dataset))
                with log.error_on_exception("Failed to get matching parameters from", repr(dataset)):
                    header = data_file.get_conditioned_header(dataset, observatory=self.observatory)
                    with log.error_on_exception("Failed syncing references for dataset", repr(dataset), 
                                                "under context", repr(context)):   
                        _bestrefs = crds.getreferences(header, context=context, observatory=self.observatory, 
                                                       ignore_cache=self.args.ignore_cache)

    # ------------------------------------------------------------------------------------------
    
    def sync_explicit_files(self):
        """Cache the listed `files`."""
        log.info("Syncing explicitly listed files.")
        mappings = [os.path.basename(mapping) for mapping in self.args.files if rmap.is_mapping(mapping)]
        references = [os.path.basename(ref) for ref in self.args.files if not rmap.is_mapping(ref)]
        if mappings:
            api.dump_mappings(self.default_context, mappings=mappings, ignore_cache=self.args.ignore_cache)
        if references:
            api.dump_references(self.default_context, baserefs=references, ignore_cache=self.args.ignore_cache)

# ==============================================================================================================

if __name__ == "__main__":
    SyncScript()()
