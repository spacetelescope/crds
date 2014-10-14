"""This module is a command line script which dowloads the references and 
mappings required to support a set of contexts from the CRDS server:

Old references and mappings which are no longer needed can be automatically
removed by specifying --purge-mappingshttps://aeon.stsci.edu/ssb/svn/crds/trunk/crds/hst/tpns or --purge-references:

  % python -m crds.sync --range 1:2 --purge-mappings --purge-references

will remove references or mappings not required by hst_0001.pmap or 
hst_0002.pmap in addition to downloading the required files.

Or explicitly list the files you want cached:

  % python -m crds.sync --files <references or mappings to cache>

To sync best references and rules for specific dataset FITS files:

  % python -m crds.sync --contexts hst_0001.pmap hst_0002.pmap --dataset-files *.fits --fetch-references

To sync best references and rules for specific dataset ids:

  % python -m crds.sync --contexts hst_0001.pmap hst_0002.pmap --dataset-ids J6M915030 --fetch-references

"""
import sys
import os
import os.path
import re
import shutil
import glob

import crds.client.api as api
from crds import (rmap, log, data_file, cmdline, utils, config, heavy_client)
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
            this can be a huge (1T+) network download and should generally only be used by
            institutions,  not individual researchers.
            
    * Removing files:
              
            Files from unspecified contexts can be removed like this::
            
                % python -m crds.sync  --contexts hst_0004.pmap hst_0005.pmap --purge-mappings
    
            this would remove mappings which are *not* in contexts 4 or 5.
        
                % python -m crds.sync  --contexts hst_0004.pmap hst_0005.pmap --purge-references
    
            this would remove reference files which are *not* in 4 or 5.
        
    * References for particular dataset files can be cached like this::
                
         % python -m crds.sync  --contexts hst_0001.pmap hst_0002.pmap --dataset-files  <dataset_files...> e.g. acs_J8D219010.fits
    
      This will fetch all the references required to support the listed datasets for contexts 0001 and 0002.
      This mode does not update dataset file headers.  See also crds.bestrefs for header updates.
              
    * References for particular dataset ids can be cached like this::
                
         % python -m crds.sync  --contexts hst_0001.pmap hst_0002.pmap --dataset-ids  <ids...>  e.g. J6M915030
    
      This will fetch all the references required to support the listed dataset ids for contexts 0001 and 0002.
              
    * Checking the cache::
        
        % python -m crds.sync --contexts hst_0001.pmap --fetch-references --check-sha1sum --repair-files
    
      would first sync the cache downloading all the files in hst_0001.pmap.  Both mappings and references would then
      be checked for correct length, sha1sum, and status.   Any files with bad length or checksum
      would then be deleted and re-downloaded.   This is really intended for an *existing* cache.
      
    * Removing blacklisted or rejected files::
              
        % python -m crds.sync --contexts hst_0001.pmap --fetch-references --check-files --purge-rejected --purge-blacklisted
    
      would first sync the cache downloading all the files in hst_0001.pmap.  Both mappings and references would then
      be checked for correct length.   Files reported as rejected or blacklisted by the server would be removed.
      
    * Reorganizing cache structure::
    
    CRDS now supports two cache structures for organizing references.   The new default cache directory structure
    for reference files includes a sub-directory for each instrument.  To migrate a legacy cache with a flat single
    directory layout to the new structure,  use the --organize=instrument.  To use the flat structure,  use --organize=flat.
        
       % python -m crds.sync --all --organize=instrument --fetch-references --verbose
       
    If CRDS makes note of "junk files" in your cache which are obstructing the process of reorganizing,  you can
    allow CRDS to delete the junk by adding --organize-delete-junk.
    
    The --organize switches are intended to be used only on inactive file caches when calibration software is not 
    running and actively using CRDS.
    """
    
    # ------------------------------------------------------------------------------------------
    
    def add_args(self):    
        super(SyncScript, self).add_args()
        self.add_argument("--files", nargs="*", help="Explicitly list files to be synced.")
        self.add_argument('--dataset-files', metavar='DATASET', type=cmdline.dataset, nargs='*',
                          help='Cache references for the specified datasets FITS files.')
        self.add_argument('--dataset-ids', metavar='DATASET', type=str, nargs='*',
                          help='Cache references for the specified dataset ids.')
        self.add_argument('--fetch-references', action='store_true', dest="fetch_references",
                          help='Cache all the references for the specified contexts.')        
        self.add_argument('--purge-references', action='store_true', dest="purge_references",
                          help='Remove reference files not referred to by contexts from the cache.')
        self.add_argument('--purge-mappings', action='store_true', dest="purge_mappings",
                          help='Remove mapping files not referred to by contexts from the cache.')
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
        self.add_argument('--fetch-sqlite-db', action='store_true', dest='fetch_sqlite_db',
                          help='Download a sqlite3 version of the CRDS file catalog.')
        self.add_argument("--organize", metavar="NEW_SUBDIR_MODE", type=config.check_crds_ref_subdir_mode, 
                          nargs="?", default=None, 
                          help="Migrate cache to specified structure, 'flat' or 'instrument'. WARNING: perform only on idle caches.")
        self.add_argument("--organize-delete-junk", action="store_true",
                          help="When --organize'ing, delete obstructing files or directories CRDS discovers.")

    # ------------------------------------------------------------------------------------------
    
    def main(self):
        """Synchronize files."""
        if self.args.dry_run:
            self.args.readonly_cache = True
        if self.args.repair_files:
            self.args.check_files = True
        if self.args.organize:   # do this before syncing anything under the current mode.
            self.organize_references(self.args.organize)
        self.require_server_connection()
        if self.args.files:
            self.sync_explicit_files()
            verify_file_list = self.args.files
        elif self.args.fetch_sqlite_db:
            self.fetch_sqlite_db()
        elif self.contexts:
            active_mappings = self.get_context_mappings()
            verify_file_list = active_mappings
            if self.args.fetch_references or self.args.purge_references:
                if self.args.dataset_files or self.args.dataset_ids:
                    active_references = self.sync_datasets()
                else:
                    active_references = self.get_context_references()
                active_references = sorted(set(active_references + self.get_conjugates(active_references)))
                if self.args.fetch_references:
                    self.fetch_references(active_references)
                    verify_file_list += active_references
                if self.args.purge_references:
                    self.purge_references(active_references)    
            if self.args.purge_mappings:
                self.purge_mappings()
        else:
            log.error("Define --all, --contexts, --last, --range, --files, or --fetch-sqlite-db to sync.")
            sys.exit(-1)
        if self.args.check_files or self.args.check_sha1sum or self.args.repair_files:
            self.verify_files(verify_file_list)
        heavy_client.update_config_info(self.observatory)
        self.report_stats()
        log.standard_status()

    # ------------------------------------------------------------------------------------------
    
    @property
    def server_info(self):
        """Return the server_info dict from the CRDS server.  Do not call update_config_info() until sync complete."""
        return heavy_client.get_config_info(self.observatory)

    # ------------------------------------------------------------------------------------------

    def purge_mappings(self):
        """Remove all mappings not under pmaps `self.contexts`."""
        # rmap.list_mappings lists all mappings in the *local* cache.
        # in contrast,  client.list_mappings globs available mappings in the server cache.
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
        if self.args.readonly_cache:
            already_have = set(rmap.list_references("*", self.observatory))
            fetched = [ x for x in sorted(set(references)-set(already_have)) if not x.startswith("NOT FOUND") ]
            if fetched:
                log.info("Would fetch references:", repr(fetched))
                with log.info_on_exception("Reference size information not available."):
                    info_map = api.get_file_info_map(self.observatory, fetched, fields=["size"])
                    total_bytes = api.get_total_bytes(info_map)
                    log.info("Would download", len(fetched), "references totaling",  
                             utils.human_format_number(total_bytes).strip(), "bytes.")
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
            if re.match(r"\w+\.r[0-9]h", filename):
                files2.add(filename[:-1] + "d")
        for filename in files:
            with log.error_on_exception("Failed purging", kind, repr(filename)):
                where = rmap.locate_file(filename, self.observatory)
                utils.remove(where, observatory=self.observatory)

    # ------------------------------------------------------------------------------------------
    
    def sync_datasets(self):
        """Sync mappings and references for datasets with respect to `self.contexts`."""
        if not self.contexts:
            log.error("Define --contexts under which references are fetched for --dataset-files or --dataset-ids.""")
            sys.exit(-1)
        active_references = []
        for context in self.contexts:
            if self.args.dataset_ids:
                if len(self.args.dataset_ids) == 1 and self.args.dataset_ids[0].startswith("@"):
                    self.args.dataset_ids = open(self.args.dataset_ids[0][1:]).read().splitlines()
                with log.error_on_exception("Failed to get matching parameters for", self.args.dataset_ids):
                    id_headers = api.get_dataset_headers_by_id(context, self.args.dataset_ids)
            for dataset in self.args.dataset_files or self.args.dataset_ids:
                log.info("Syncing context '%s' dataset '%s'." % (context, dataset))
                with log.error_on_exception("Failed to get matching parameters from", repr(dataset)):
                    if self.args.dataset_files:
                        headers = { dataset : data_file.get_conditioned_header(dataset, observatory=self.observatory) }
                    else:
                        headers = { dataset_id : header for (dataset_id, header) in id_headers.items() if
                                    dataset.upper() in dataset_id }
                    for assc_dataset, header in headers.items():
                        with log.error_on_exception("Failed syncing references for dataset", repr(assc_dataset), 
                                                    "under context", repr(context)):   
                            bestrefs = crds.getrecommendations(header, context=context, observatory=self.observatory, 
                                                               ignore_cache=self.args.ignore_cache)
                            log.verbose("Best references for", repr(assc_dataset), "are", bestrefs)
                            active_references.extend(bestrefs.values())
        active_references = [ ref for ref in active_references if not ref.startswith("NOT FOUND") ]
        log.verbose("Syncing references:", repr(active_references))
        return list(set(active_references))
        
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
            infos = api.get_file_info_map(observatory=self.observatory, files=basenames, 
                                         fields=["size","rejected","blacklisted","state","sha1sum"])
        except Exception, exc:
            log.error("Failed getting file info.  CACHE VERIFICATION FAILED.  Exception: ", repr(str(exc)))
            return
        bytes_so_far = 0
        total_bytes = api.get_total_bytes(infos)
        for nth_file, file in enumerate(files):
            if infos[file] == "NOT FOUND":
                log.error("CRDS has no record of file", repr(file))
            else:
                self.verify_file(file, infos[file], bytes_so_far, total_bytes, nth_file, len(files))
                bytes_so_far += int(infos[file]["size"])
        
    def verify_file(self, file, info, bytes_so_far, total_bytes, nth_file, total_files):
        """Check one `file` against the provided CRDS database `info` dictionary."""
        path = rmap.locate_file(file, observatory=self.observatory)
        base = os.path.basename(file)
        n_bytes = int(info["size"])
        log.verbose(api.file_progress("Verifying", base, path, n_bytes, bytes_so_far, total_bytes, nth_file, total_files),
                    verbosity=10)
        if not os.path.exists(path):
            log.error("File", repr(base), "doesn't exist at", repr(path))
            return
        size = os.stat(path).st_size
        if int(info["size"]) != size:
            self.error_and_repair(path, "File", repr(base), "length mismatch LOCAL size=" + repr(size), 
                                  "CRDS size=" + repr(info["size"]))
        elif self.args.check_sha1sum:
            log.verbose("Computing checksum for", repr(base), "of size", repr(size), verbosity=100)
            sha1sum = utils.checksum(path)
            if info["sha1sum"] == "none":
                log.warning("CRDS doesn't know the checksum for", repr(base))
            elif info["sha1sum"] != sha1sum:
                self.error_and_repair(path, "File", repr(base), "checksum mismatch CRDS=" + repr(info["sha1sum"]), 
                                      "LOCAL=" + repr(sha1sum))
        if info["state"] not in ["archived", "operational"]:
            log.warning("File", repr(base), "has an unusual CRDS file state", repr(info["state"]))
        if info["rejected"] != "false":
            log.warning("File", repr(base), "has been explicitly rejected.")
            if self.args.purge_rejected:
                self.remove_files([path], "files")
            return
        if info["blacklisted"] != "false":
            log.warning("File", repr(base), "has been blacklisted or is dependent on a blacklisted file.")
            if self.args.purge_blacklisted:
                self.remove_files([path], "files")
            return
        return
    
    def error_and_repair(self, file, *args, **keys):
        """Issue an error message and repair `file` if requested by command line args."""
        log.error(*args, **keys)
        if self.args.repair_files:
            if config.writable_cache_or_info("Skipping remove and dump of", repr(file)):
                log.info("Repairing file", repr(file))
                utils.remove(file, observatory=self.observatory)
                self.dump_files(self.default_context, [file]) 
    
    def fetch_sqlite_db(self):
        """Download a SQLite version of the CRDS catalog from the server."""
        path = api.get_sqlite_db(self.observatory)
        log.info("SQLite database file downloaded to:", path)
        
    def organize_references(self, new_mode):
        """Find all references in the CRDS cache and relink them to the paths which are implied by `new_mode`.   
        This is used to reroganize existing file caches into new layouts,  e.g. flat -->  by instrument.
        """
        old_refpaths = rmap.list_references("*", observatory=self.observatory, full_path=True)
        old_mode = config.get_crds_ref_subdir_mode(self.observatory)
        log.info("Reorganizing", len(old_refpaths), "references from", repr(old_mode), "to", repr(new_mode))
        config.set_crds_ref_subdir_mode(new_mode, observatory=self.observatory)
        new_mode = config.get_crds_ref_subdir_mode(self.observatory)  # did it really change.
        for refpath in old_refpaths:
            with log.error_on_exception("Failed relocating:", repr(refpath)):
                desired_loc = rmap.locate_file(os.path.basename(refpath), observatory=self.observatory)
                if desired_loc != refpath:
                    if os.path.exists(desired_loc):
                        if not self.args.organize_delete_junk:
                            log.warning("Link or directory already exists at", repr(desired_loc), "Skipping", repr(refpath))
                            continue
                        utils.remove(desired_loc, observatory=self.observatory)
                    if config.writable_cache_or_info("Skipping file relocation from", repr(refpath), "to", repr(desired_loc)):
                        log.info("Relocating", repr(refpath), "to", repr(desired_loc))
                        shutil.move(refpath, desired_loc)
                else:
                    if old_mode != new_mode:
                        log.warning("Keeping existing cached file", repr(desired_loc), "already in target mode", repr(new_mode))
                    else:
                        log.warning("No change in subdirectory mode", repr(old_mode), "skipping reorganization of", repr(refpath))
        if new_mode == "flat" and old_mode == "instrument":
            log.info("Reorganizing from 'instrument' to 'flat' cache,  removing instrument directories.")
            for instrument in self.locator.INSTRUMENTS:
                self.remove_dir(instrument)

    def remove_dir(self, instrument):
        """Remove an instrument cache directory and any associated legacy link."""
        if config.writable_cache_or_info("Skipping remove instrument", repr(instrument), "directory."):
            crds_refpath = config.get_crds_refpath(self.observatory)
            prefix = self.locator.get_env_prefix(instrument)
            rootdir = os.path.join(crds_refpath, instrument)
            refdir = os.path.join(crds_refpath, prefix[:-1])
            if len(glob.glob(os.path.join(rootdir, "*"))):
                log.info("Residual files in '{}'. Not removing.".format(rootdir))
                return
            if os.path.exists(refdir):   # skip crds://  vs.  oref
                utils.remove(refdir, observatory=self.observatory)
            utils.remove(rootdir, observatory=self.observatory)

# ==============================================================================================================

if __name__ == "__main__":
    SyncScript()()
