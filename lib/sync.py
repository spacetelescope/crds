"""This module is a command line script which dowloads the references and 
mappings required to support a set of contexts from the CRDS server:

Old references and mappings which are no longer needed can be automatically
removed by specifying --purge-mappings or --purge-references:

  % python -m crds.sync --range 1:2 --purge-mappings --purge-references

will remove references or mappings not required by hst_0001.pmap or 
hst_0002.pmap in addition to downloading the required files.

Or explicitly list the files you want cached:

  % python -m crds.sync --files <references or mappings to cache>

Synced datasets can be explicitly listed:

  % python -m crds.sync --contexts hst_0001.pmap hst_0002.pmap --datasets *.fits
"""
import sys
import os
import os.path
import re

import crds.client.api as api
from crds import (rmap, log, data_file, cmdline, utils)
import crds

# ============================================================================

# ============================================================================

class SyncScript(cmdline.ContextsScript):
    """Command line script for synchronizing local CRDS file cache with CRDS server."""

    description = """
    Synchronize local mapping and reference caches for the given contexts by
    downloading missing files from the CRDS server and/or archive.
    """
    
    epilog = """    
    * Primitive syncing can be done by explicitly listing the files you wish to cache::
        
                % python -m crds.sync  --files hst_0001.pmap hst_acs_darkfile_0037.fits
    
      this will download only those two files.
        
    * Typically syncing CRDS files is done with respect to particular CRDS contexts:
        
            Synced contexts can be explicitly listed::
            
                % python -m crds.sync  --contexts hst_0001.pmap hst_0002.pmap
              
            this will recursively download all the mappings referred to by .pmaps 0001 and 0002.
            
            Synced contexts can be specified as a numerical range::
            
                % python -m crds.sync --range 1:3
    
            this will also recursively download all the mappings referred to by .pmaps 0001, 002, 0003.
            
            Synced contexts can be specified as --all contexts::
            
                % python -m crds.sync --all
    
            this will recursively download all CRDS mappings for all time.
              
            NOTE:  Fetching references required to support contexts has to be done explicitly::
            
                % python -m crds.sync  --contexts hst_0001.pmap hst_0002.pmap  --fetch-references
     
            will download all the references mentioned by contexts 0001 and 0002.   
            this can be a huge undertaking and should be done with care.
            
    * Removing files:
              
            Files from unspecified contexts can be removed like this::
            
                % python -m crds.sync  --contexts hst_0004.pmap hst_0005.pmap --purge-mappings
    
            this would remove mappings which are *not* in contexts 4 or 5.
        
                % python -m crds.sync  --contexts hst_0004.pmap hst_0005.pmap --purge-references
    
            this would remove reference files which are *not* in 4 or 5.
        
    * References for particular datasets can be cached like this::
                
         % python -m crds.sync  --contexts hst_0001.pmap hst_0002.pmap --datasets  <dataset_files...>
    
      this will fetch all the references required to support the listed datasets for contexts 0001 and 0002.
      this mode does not update dataset file headers.  See also crds.bestrefs for header updates.
              
    * Checking the cache::
        
        % python -m crds.sync --contexts hst_0001.pmap --fetch-references --check-files --check-sha1sum --repair-files
    
      would first sync the cache downloading all the files in hst_0001.pmap.  Both mappings and references would then
      be checked for correct length, sha1sum, and reject and blacklist status.   Any files with bad length or checksum
      would then be deleted and re-downloaded.   This is really intended for an *existing* cache,  where the actual
      sync download process is a null operation which just determines the list of files to check.
      
    * Removing blacklisted or rejected files::
              
        % python -m crds.sync --contexts hst_0001.pmap --fetch-references --check-files --purge-rejected --purge-blacklisted
    
      would first sync the cache downloading all the files in hst_0001.pmap.  Both mappings and references would then
      be checked for correct length, and reject and blacklist status.   Files reported as rejected or blacklisted by 
      the server would be removed.
    """
    
    # ------------------------------------------------------------------------------------------
    
    def add_args(self):    
        super(SyncScript, self).add_args()
        self.add_argument("--files", nargs="*", help="Explicitly list files to be synced.")
        self.add_argument('--datasets', metavar='DATASET', type=cmdline.dataset, nargs='*',
                          help='Cache references for the specified datasets.')
        self.add_argument('--fetch-references', action='store_true', dest="fetch_references",
                          help='Cache all the references for the specified contexts.')        
        self.add_argument('--purge-references', action='store_true', dest="purge_references",
                          help='Remove reference files not referred to by contexts from the cache.')
        self.add_argument('--purge-mappings', action='store_true', dest="purge_mappings",
                          help='Remove mapping files not referred to by contexts from the cache.')
        self.add_argument('-i', '--ignore-cache', action='store_true', dest="ignore_cache",
                          help="Download sync'ed files even if they're already in the cache.")
        self.add_argument('--dry-run', action="store_true",
                          help= "Don't remove purged files, or repair files,  just print out their names.")
        
        self.add_argument('-k', '--check-files', action='store_true', dest='check_files',
                          help='Check cached files against the CRDS database and report anomalies.')
        self.add_argument('-s', '--check-sha1sum', action='store_true', dest='check_sha1sum',
                          help='For --check-files,  also verify file sha1sums.')
        self.add_argument('-r', '--repair-files', action='store_true', dest='repair_files',
                          help='Repair or re-download files noted as bad by --check-files')
        self.add_argument('--purge-rejected', action='store_true', dest='purge_rejected',
                          help='Purge files noted as rejected by --check-files')
        self.add_argument('--purge-blacklisted', action='store_true', dest='purge_blacklisted',
                          help='Purge files (and their mapping anscestors) noted as blacklisted by --check-files')

    # ------------------------------------------------------------------------------------------
    
    def main(self):
        """Synchronize files."""
        self.require_server_connection()
        if self.contexts:
            active_mappings = self.fetch_mappings()
            if self.args.datasets:
                active_references = self.sync_datasets()
            else:
                active_references = self.get_context_references()
            active_references += self.get_conjugates(active_references)
            active_references = sorted(set(active_references))
            if self.args.fetch_references:
                self.fetch_references(active_references)
            if self.args.purge_references:
                self.purge_references(active_references)    
            if self.args.purge_mappings:
                self.purge_mappings()
            verify_file_list = active_mappings + active_references
        elif self.args.files:
            self.sync_explicit_files()
            verify_file_list = self.args.files
        else:
            log.error("Define --contexts, --datasets,  or --files to sync.")
            sys.exit(-1)
        if self.args.check_files:
            self.verify_files(verify_file_list)
        self.report_stats()
        log.standard_status()

    # ------------------------------------------------------------------------------------------
    
    def fetch_mappings(self):
        """Gets all mappings required to support `self.contexts`.  
        if purge:  
            Remove all mappings from the CRDS mapping cache which are not required for `self.contexts`.
        if ignore_cache:
            Re-download all required files.
        """
        if not self.contexts:
            return
        mappings = set()
        for context in self.contexts:
            log.verbose("Syncing mapping", repr(context))
            self.dump_files(context, files=None)  # all mappings for context
            mapping = rmap.fetch_mapping(context)
            mappings = mappings.union(set(mapping.mapping_names()))
        return sorted(mappings)
            
    def purge_mappings(self):
        """Remove all mappings not under pmaps `self.contexts`."""
        purge_maps = set(rmap.list_mappings('*.[pir]map', self.observatory))
        keep = set(self.get_context_mappings())
        self.remove_files(sorted(purge_maps-keep), "mapping")
        
    # ------------------------------------------------------------------------------------------
    
    def fetch_references(self, references):
        """Gets all references required to support `only_contexts`.  Removes
        all references from the CRDS reference cache which are not required for
        `only_contexts`.
        """
        if not self.contexts:
            return
        if self.args.dry_run:
            already_have = set(rmap.list_references("*", self.observatory))
            fetched = [ x for x in sorted(set(references)-set(already_have)) if not x.startswith("NOT FOUND") ]
            log.info("Would fetch references:", repr(fetched))
        else:
            self.dump_files(self.contexts[0], references)

    def purge_references(self, keep=None):
        """Remove all references not references under pmaps `self.contexts`."""
        purge_refs = set(rmap.list_references("*", self.observatory))
        if keep is None:
            keep = set(self.get_context_references())
        else:
            keep = set(keep)
        self.remove_files(sorted(purge_refs - keep), "reference")
    
    def remove_files(self, files, kind):
        """Remove the list of `files` basenames which are converted to fully
        specified CRDS paths using the locator module associated with context.
        """
        if not files:
            log.verbose("No " + kind + "s to remove.")
        files2 = set(files)
        for filename in files:
            if re.match("\w+\.r[0-9]h", filename):
                files2.add(filename[:-1] + "d")
        for filename in files:
            where = rmap.locate_file(filename, self.observatory)
            # instrument, filekind = utils.get_file_properties(self.observatory, where)
            if not self.args.dry_run:
                log.verbose("Removing", filename, "from", where)
                with log.error_on_exception("File removal failed for", repr(where)):
                    os.remove(where)
            else:
                log.info("Without --dry-run would remove", repr(where))

    # ------------------------------------------------------------------------------------------
    
    def sync_datasets(self):
        """Sync mappings and references for datasets with respect to `self.contexts`."""
        if not self.contexts:
            log.error("Define --contexts under which references are fetched for --datasets.""")
            sys.exit(-1)
        active_references = []
        for context in self.contexts:
            for dataset in self.args.datasets:
                log.info("Syncing context '%s' dataset '%s'." % (context, dataset))
                with log.error_on_exception("Failed to get matching parameters from", repr(dataset)):
                    header = data_file.get_conditioned_header(dataset, observatory=self.observatory)
                    with log.error_on_exception("Failed syncing references for dataset", repr(dataset), 
                                                "under context", repr(context)):   
                        bestrefs = crds.getrecommendations(header, context=context, observatory=self.observatory, 
                                                           ignore_cache=self.args.ignore_cache)
                        active_references.extend(bestrefs.values())
        return set(active_references)
        
    # ------------------------------------------------------------------------------------------
    
    def sync_explicit_files(self):
        """Cache `self.args.files`."""
        log.info("Syncing explicitly listed files.")
        self.dump_files(self.default_context, self.args.files)

    # ------------------------------------------------------------------------------------------
    
    def verify_files(self, files):
        """Check `files` against the CRDS server database to ensure integrity and check reject status."""
        basenames = [os.path.basename(file) for file in files]
        try:
            log.verbose("Downloading verification info for", len(basenames), "files.", verbosity=10)
            info = api.get_file_info_map(observatory=self.observatory, files=basenames, 
                                         fields=["size","rejected","blacklisted","state","sha1sum"])
        except Exception, exc:
            log.error("Failed getting file info.  CACHE VERIFICATION FAILED.  Exception: ", repr(str(exc)))
            return
        for file in files:
            if info[file] == "NOT FOUND":
                log.error("CRDS has no record of file", repr(file))
            self.verify_file(file, info[file])
        
    def verify_file(self, file, info):
        """Check one `file` against the provided CRDS database `info` dictionary."""
        path = rmap.locate_file(file, observatory=self.observatory)
        base = os.path.basename(file)
        log.verbose("Verifying", repr(base), "at", repr(path), verbosity=10)
        if not os.path.exists(path):
            log.error("File", repr(base), "doesn't exist at", repr(path))
            return
        size = os.stat(path).st_size
        if int(info["size"]) != size:
            self.error_and_repair(path, "File", repr(base), "length mismatch LOCAL size=" + repr(size), 
                                  "CRDS size=" + repr(info["size"]))
        elif self.args.check_sha1sum:
            log.verbose("Computing checksum for", repr(base), "of size", repr(size))
            sha1sum = utils.checksum(path)
            if info["sha1sum"] == "none":
                log.warning("CRDS doesn't know the checksum for", repr(base))
            elif info["sha1sum"] != sha1sum:
                self.error_and_repair(path, "File", repr(base), "checksum mismatch CRDS=" + repr(info["sha1sum"]), 
                                      "LOCAL=" + repr(sha1sum))
#        elif info["state"] not in ["delivered", "operational"]:
#            self.log_and_purge(path, "File", repr(base), "has a strange server state", repr(info["state"]))
        elif info["rejected"] != "false":
            log.error("File", repr(base), "has been explicitly rejected.")
            if self.args.purge_rejected:
                self.remove_files([path], "files")
            return
        elif info["blacklisted"] != "false":
            log.error("File", repr(base), "has been blacklisted or is dependent on a blacklisted file.")
            if self.args.purge_blacklisted:
                self.remove_files([path], "files")
            return
        return
    
    def dump_files(self, context, files):
        """Download mapping or reference `files1` with respect to `context`,  tracking stats."""
        _localpaths, downloads, bytes = api.dump_files(
            context, files, ignore_cache=self.args.ignore_cache, raise_exceptions=self.args.pdb)
        self.increment_stat("total-files", downloads)
        self.increment_stat("total-bytes", bytes)

    def error_and_repair(self, file, *args, **keys):
        """Issue an error message and repair `file` if requested by command line args."""
        log.error(*args, **keys)
        if self.args.repair_files:
            if not self.args.dry_run:
                log.info("Repairing file", repr(file))
                os.remove(file)
                self.dump_files(self.default_context, [file]) 
            else:
                log.info("Without --dry-run would repair", repr(file))
                
# ==============================================================================================================

if __name__ == "__main__":
    SyncScript()()
