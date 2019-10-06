"""This module is a command line script which dowloads the references and
mappings required to support a set of contexts from the CRDS server:

Old references and mappings which are no longer needed can be automatically
removed by specifying --purge-mappings or --purge-references::

  % crds sync --range 1:2 --purge-mappings --purge-references

will remove references or mappings not required by hst_0001.pmap or
hst_0002.pmap in addition to downloading the required files.

Or explicitly list the files you want cached:

  % crds sync --files <references or mappings to cache>

To sync best references and rules for specific dataset FITS files:

  % crds sync --contexts hst_0001.pmap hst_0002.pmap --dataset-files *.fits --fetch-references

To sync best references and rules for specific dataset ids:

  % crds sync --contexts hst_0001.pmap hst_0002.pmap --dataset-ids J6M915030 --fetch-references

"""
import sys
import os
import os.path
import re
import shutil
import glob

# ============================================================================

import crds
from crds.core import log, config, utils, rmap, heavy_client, cmdline, crds_cache_locking
from crds import data_file
from crds.core.log import srepr
from crds.client import api

# ============================================================================

# ============================================================================

class SyncScript(cmdline.ContextsScript):
    """Command line script for synchronizing local CRDS file cache with CRDS server."""

    description = """
    Synchronize local mapping and reference caches for the given contexts by
    downloading missing files from the CRDS server and/or archive.
    """

    epilog = """
    * Dry-Running Cache Changes

       Since CRDS cache operations can involve significant network downloads,  as a general note,
       crds.sync can be run with *---readonly-cache ---verbose* switches to better determine what
       the effects of any command should be.   This can be used to gauge download sizes or list
       files before deleting them.

    * Syncing Specific Files

        Downloading an explicit list of files can be done by like this::

        % crds sync  --files hst_0001.pmap hst_acs_darkfile_0037.fits

        this will download only those two files into the appropriate locations
        in your CRDS cache.

        An output directory outside the CRDS cache can also be specified like
        this::

        % crds sync --output-dir . --files hst_0001.pmap hst_acs_darkfile_0037.fits

        which will fetch the same files but put them in the current working
        directory "." instead of at their implicit locations in the CRDS cache.

    * Syncing Rules

        Typically syncing CRDS files is done with respect to particular CRDS contexts:

        Synced contexts can be explicitly listed::

            % crds sync  --contexts hst_0001.pmap hst_0002.pmap

        this will recursively download all the mappings referred to by .pmaps 0001 and 0002.

        Synced contexts can be specified as a numerical range::

            % crds sync --range 1:3

        this will also recursively download all the mappings referred to by .pmaps 0001, 002, 0003.

        Synced contexts can be specified as --all contexts::

            % crds sync --all

        this will recursively download all CRDS mappings for all time.

    * Syncing References By Context

        Because complete reference downloads can be enormous,  you must explicitly specify when
        you wish to fetch the references which are enumerated in particular CRDS rules::

            % crds sync  --contexts hst_0001.pmap hst_0002.pmap  --fetch-references

        will download all the references mentioned by contexts 0001 and 0002.

        This can be a huge (1T+) network download and should generally only be
        used by institutions,  not individual researchers.

        **NOTE:** the contexts synced can be for particular instruments or types rather than
        the entire pipeline,  e.g. hst_cos_0002.imap or hst_cos_proftab_0001.rmap

    * Removing Unused Files

        CRDS rules from **unspecified** contexts can be removed like this::

            % crds sync  --contexts hst_0004.pmap hst_0005.pmap --purge-mappings

        while this would remove references which are *not* in contexts 4 or 5::

            % crds sync  --contexts hst_0004.pmap hst_0005.pmap --purge-references

        Again, both of these commands remove cached files which are not specified or implied.

    * References for Dataset Files

        References required by particular dataset files can be cached like this::

            % crds sync  --contexts hst_0001.pmap hst_0002.pmap --dataset-files  <dataset_files...> e.g. acs_J8D219010.fits

        This will fetch all the references required to support the listed datasets for contexts 0001 and 0002.

        This mode does not update dataset file headers.  See also crds.bestrefs for similar functionality with header updates.

    * References for Dataset Ids

        References for particular dataset ids can be cached like this::

            % crds sync  --contexts hst_0001.pmap hst_0002.pmap --dataset-ids  <ids...>  e.g. J6M915030

        This will fetch all the references required to support the listed dataset ids for contexts 0001 and 0002.

    * Checking and Repairing Large Caches

        Large Institutional caches can be checked and/or repaired like this::

            % crds sync --contexts hst_0001.pmap --fetch-references --check-sha1sum --repair-files

        will download all the files in hst_0001.pmap not already present.

        Both mappings and references would then be checked for correct length, sha1sum, and status.

        Any files with bad length or checksum would then be deleted and re-downloaded.   This is really intended
        for a large *existing* cache.

        File checksum verification is optional because it is time consuming.  Verifying the contents of the current
        HST shared cache requires 8-10 hours.   In contrast, doing simple length, existence, and status checks
        takes 5-10 minutes,  sufficient for a quick check but not foolproof.

    * Checking Smaller Caches,  Identifying Foreign Files

        The simplest approach for "repairing" a small cache is to delete it and resync::

           % rm -rf $CRDS_PATH
           % crds sync  -- ...  # repeat whatever syncs you did to cache files of interest

        A more complicated but also more precise approach to check all rules and references in your local CRDS cache::

           % crds sync --check-files --files `crds list --all --cached-mappings --cached-references`

        This approach works by using the crds.list command to dump the file names of all files in the CRDS cache
        and then using the crds.sync command to check exactly those files.

        Since --cached-mappings and --cached-references will only print the name of rules or references in the cache,
        not all files from CRDS,  the second approach can also be used to detect files which are not from CRDS.

        For smaller caches *--check-sha1sum* is likekly to be less of a performance/runtime issue and should be used
        to detect files which have changed in contents but not in length,  particularly CRDS mapping files.

    * Removing blacklisted or rejected files

        crds.sync can be used to remove the files from specific contexts which have been marked as "bad".

          % crds sync --contexts hst_0001.pmap --fetch-references --check-files --purge-rejected --purge-blacklisted

        would first sync the cache downloading all the files in hst_0001.pmap.  Both mappings and references would then
        be checked for correct length.   Files reported as rejected or blacklisted by the server would be removed.

    * Reorganizing cache structure

        CRDS now supports two cache structures for organizing references: flat and instrument.  *flat* places all references
        for a telescope in a single directory,  e.g. references/hst.   *instrument* segregates references into subdirectories
        which name instruments or legacy environment variables,  e.g. acs or jref.

        Newly created caches will default to the *instrument* organization.  To migrate a legacy cache with a flat single
        directory layout to the new structure,  sync with --organize=instrument::

           % crds sync --organize=instrument --verbose

        To migrate to the flat structure,  use --organize=flat::

           % crds sync --organize=flat --verbose

        While reorganizing, if CRDS makes note of "junk files" in your cache which are
        obstructing the process of reorganizing, you can allow CRDS to delete the junk
        by adding --organize-delete-junk.

        The --organize switches are intended to be used only on inactive file caches
        when calibration software is not running and actively using CRDS.
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
        self.add_argument("--verify-context-change", action="store_true",
                          help="Make it an error if the context does not update to something new.")
        self.add_argument("--push-context", metavar="KEY", type=str,
                          help="Push the name of the final cached context to the server for the pipeline identified by KEY.")
        self.add_argument("--clear-pickles", action="store_true",
                          help="Remove all context pickles from the CRDS cache. Can precede --save-pickles.")
        self.add_argument("--save-pickles", action="store_true",
                          help="Save pre-compiled versions of the sync'ed contexts in the CRDS cache.  Keep pre-existing pickles.")
        self.add_argument("--output-dir", type=str, default=None,
                          help="Directory to output sync'ed files, for simple syncs,  particularly --files.   Implies 'flat' cache.")
        self.add_argument("--clear-locks", action="store_true",
                          help="Remove CRDS cache file lock(s).")
        self.add_argument("--force-config-update", action="store_true",
                          help="Even if sync errors occur, attempt to update the CRDS configuration, including the default context.")

    # ------------------------------------------------------------------------------------------

    def main(self):
        """Synchronize files."""

        # clear any mutliprocessing locks associated with the CRDS cache.
        if self.args.clear_locks:
            crds_cache_locking.clear_cache_locks()
            return log.errors()

        self.handle_misc_switches()   # simple side effects only

        # if explicitly requested,  or the cache is suspect or being ignored,  clear
        # cached context pickles.
        if self.args.clear_pickles or self.args.ignore_cache or self.args.repair_files:
            self.clear_pickles()

        # utility to change cache structure, e.g. add instrument subdirs.
        # do this before syncing anything under the current mode.
        if self.args.organize:
            self.organize_references(self.args.organize)

        # fetching and verifying files both require a server connection.
        self.require_server_connection()

        # primary sync'ing occurs here,  both mappings and references as well as odd-ball
        # server sqlite3 database download.
        verify_file_list = self.file_transfers()

        # verification is relative to sync'ed files,  and can include file replacement if
        # defects are found.
        if (self.args.check_files or self.args.check_sha1sum or self.args.repair_files or
            self.args.purge_blacklisted or self.args.purge_rejected):
            self.verify_files(verify_file_list)

        # context pickles should only be (re)generated after mappings are fully sync'ed and verified
        if self.args.save_pickles:
            self.pickle_contexts(self.contexts)

        # update CRDS cache config area,  including stored version of operational context.
        # implement pipeline support functions of context update verify and echo
        # If --output-dir was specified,  do not update cache config.
        if self.args.output_dir:
            log.verbose_warning("Used --output-dir,  skipping cache server_config update including default context and bad files.")
            if config.writable_cache_or_verbose("skipping removal of ref_cache_subdir_mode file."):
                os.remove(config.get_crds_ref_subdir_file(self.observatory))
        else:
            self.update_context()

        self.report_stats()
        log.standard_status()
        return log.errors()
    # ------------------------------------------------------------------------------------------

    def handle_misc_switches(self):
        """Handle command line switches with simple side-effects that should precede
        other sync operations.
        """
        if self.args.dry_run:
            config.set_cache_readonly(True)

        if self.args.repair_files:
            self.args.check_files = True

        if self.args.output_dir:
            os.environ["CRDS_MAPPATH_SINGLE"] = self.args.output_dir
            os.environ["CRDS_REFPATH_SINGLE"] = self.args.output_dir
            os.environ["CRDS_CFGPATH_SINGLE"] = self.args.output_dir
            os.environ["CRDS_PICKLEPATH_SINGLE"] = self.args.output_dir
            self.args.organize = "flat"

        if self.readonly_cache:
            log.info("Syncing READONLY cache,  only checking functions are enabled.")
            log.info("All cached updates, context changes, and file downloads are inhibited.")

    def file_transfers(self):
        """Top level control for the primary function of downloading files specified as:

        --files ...      (explicit list of CRDS mappings or references)
        --contexts ...   (many varieties of mapping specifier including --all, --range, etc.)
        --fetch-sqlite-db ...  (Server catalog download as sqlite3 database file.

        Returns list of downloaded/cached files for later verification if requested.
        """
        if self.args.files:
            self.sync_explicit_files()
            verify_file_list = self.files
        elif self.args.fetch_sqlite_db:
            self.fetch_sqlite_db()
            verify_file_list = []
        elif self.contexts:
            verify_file_list = self.interpret_contexts()
        else:
            log.error("Define --all, --contexts, --last, --range, --files, or --fetch-sqlite-db to sync.")
            sys.exit(-1)
        return verify_file_list

    def interpret_contexts(self):
        """Sync the mapping files associated with any context specifiers like
        --all, --contexts,  etc...

        If --fetch-references or --purge-references are specified, also fetch and/or
        purge references with respect to the specified contexts.
        """
        active_mappings = self.get_context_mappings()
        verify_file_list = active_mappings
        if self.args.fetch_references or self.args.purge_references:
            active_references = self.get_synced_references()
            if self.args.purge_rejected or self.args.purge_blacklisted:
                references = active_references - self.bad_files
            else:
                references = active_references
            if self.args.fetch_references:
                self.fetch_files(self.contexts[0], references)
                verify_file_list += active_references
            if self.args.purge_references:
                self.purge_references(active_references)
        if self.args.purge_mappings:
            self.purge_mappings()
        return verify_file_list

    def get_synced_references(self):
        """Return the list of reference names associated with the specified dataset
        files, dataset ids, or contexts, including any associated GEIS data
        file names.
        """
        if self.args.dataset_files or self.args.dataset_ids:
            active_references = self.sync_datasets()
        else:
            active_references = self.get_context_references()
        # Handle GEIS paired data files
        active_references = set(active_references + self.get_conjugates(active_references))
        return active_references

    def update_context(self):
        """Update the CRDS operational context in the cache.  Handle pipeline-specific
        targeted features of (a) verifying a context switch as actually recorded in
        the local CRDS cache and (b) echoing/pushing the pipeline context back up to the
        CRDS server for tracking using an id/authorization key.

        If errors occurred during the sync and --force_config_update is not set,
        """
        if not log.errors() or self.args.force_config_update:
            if self.args.verify_context_change:
                old_context = heavy_client.load_server_info(self.observatory).operational_context
            heavy_client.update_config_info(self.observatory)
            if self.args.verify_context_change:
                self.verify_context_change(old_context)
            if self.args.push_context:
                self.push_context()
        else:
            log.warning("Errors occurred during sync,  skipping CRDS cache config and context update.")

    def clear_pickles(self):
        """Remove all pickles."""
        log.info("Removing all context pickles.  Use --save-pickles to recreate for specified contexts.")
        for path in rmap.list_pickles("*.pmap", self.observatory, full_path=True):
            if os.path.exists(path):
                utils.remove(path, self.observatory)

    def pickle_contexts(self, contexts):
        """Save pickled versions of `contexts` in the CRDS cache.

        By default this will by-pass existing pickles if they successfully load.
        """
        for context in contexts:
            with log.error_on_exception("Failed pickling", repr(context)):
                crds.get_pickled_mapping.uncached(context, use_pickles=True, save_pickles=True)  # reviewed

    # ------------------------------------------------------------------------------------------

    @property
    def server_info(self):
        """Return the server_info dict from the CRDS server.  Do not call update_config_info() until sync complete."""
        return heavy_client.get_config_info(self.observatory)

    def verify_context_change(self, old_context):
        """Verify that the starting and post-sync contexts are different,  or issue an error."""
        new_context = heavy_client.load_server_info(self.observatory).operational_context
        if old_context == new_context:
            log.error("Expected operational context switch but starting and post-sync contexts are both", repr(old_context))
        else:
            log.info("Operational context updated from", repr(old_context), "to",  repr(new_context))

    def push_context(self):
        """Push the final context recorded in the local cache to the CRDS server so it can be displayed
        as the operational state of a pipeline.
        """
        info = heavy_client.load_server_info(self.observatory)
        with log.error_on_exception("Failed pushing cached operational context name to CRDS server"):
            api.push_remote_context(self.observatory, "operational", self.args.push_context, info.operational_context)
            log.info("Pushed cached operational context name", repr(info.operational_context), "to CRDS server")

    # ------------------------------------------------------------------------------------------

    def purge_mappings(self):
        """Remove all mappings not under pmaps `self.contexts`."""
        # rmap.list_mappings lists all mappings in the *local* cache.
        # in contrast,  client.list_mappings globs available mappings in the server cache.
        purge_maps = set(rmap.list_mappings('*.[pir]map', self.observatory))
        keep = set(self.get_context_mappings())
        self.remove_files(sorted(purge_maps-keep), "mapping")

    # ------------------------------------------------------------------------------------------

    def fetch_files(self, context, files):
        """Downloads `files` as needed relative to `context` nominally used to identify
        the observatory to the server.  If the CRDS cache is currently configured as READONLY,
        prints an estimate about which files will download and the total size.  The estimate
        does not (currently) include the nested mappings associated with the closure of `files`,
        but the dominant costs of downloads are reference files.
        """
        files = set([os.path.basename(_file) for _file in files])
        if config.get_cache_readonly():
            log.info("READONLY CACHE estimating required downloads.")
            if not self.args.ignore_cache:
                already_have = (set(rmap.list_references("*", self.observatory)) |
                                set(rmap.list_mappings("*", self.observatory)))
            else:
                already_have = set()
            fetched = [ x for x in sorted(files - already_have) if not x.startswith("NOT FOUND") ]
            for _file in files:
                if _file in already_have:
                    log.verbose("File", repr(_file), "is already in the CRDS cache.", verbosity=55)
                else:
                    log.verbose("File", repr(_file), "would be downloaded.", verbosity=55)
            if fetched:
                with log.info_on_exception("File size information not available."):
                    info_map = api.get_file_info_map(self.observatory, fetched, fields=["size"])
                    total_bytes = api.get_total_bytes(info_map)
                    log.info("READONLY CACHE would download", len(fetched), "files totalling",
                             utils.human_format_number(total_bytes).strip(), "bytes.")
            else:
                log.info("READONLY CACHE no reference downloads expected.")
        else:
            self.dump_files(context, files, self.args.ignore_cache)

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
                where = config.locate_file(filename, self.observatory)
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
                    with open(self.args.dataset_ids[0][1:]) as pfile:
                        self.args.dataset_ids = pfile.read().splitlines()
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
        """Cache `self.files`."""
        log.info("Syncing explicitly listed files.")
        self.fetch_files(self.default_context, self.files)

    # ------------------------------------------------------------------------------------------

    def verify_files(self, files):
        """Check `files` against the CRDS server database to ensure integrity and check reject status."""
        basenames = [os.path.basename(file) for file in files]
        try:
            log.verbose("Downloading verification info for", len(basenames), "files.", verbosity=10)
            infos = api.get_file_info_map(observatory=self.observatory, files=basenames,
                                         fields=["size","rejected","blacklisted","state","sha1sum"])
        except Exception as exc:
            log.error("Failed getting file info.  CACHE VERIFICATION FAILED.  Exception: ", repr(str(exc)))
            return
        bytes_so_far = 0
        total_bytes = api.get_total_bytes(infos)
        for nth_file, file in enumerate(files):
            bfile = os.path.basename(file)
            if infos[bfile] == "NOT FOUND":
                log.error("CRDS has no record of file", repr(bfile))
            else:
                self.verify_file(file, infos[bfile], bytes_so_far, total_bytes, nth_file, len(files))
                bytes_so_far += int(infos[bfile]["size"])

    def verify_file(self, file, info, bytes_so_far, total_bytes, nth_file, total_files):
        """Check one `file` against the provided CRDS database `info` dictionary."""
        path = config.locate_file(file, observatory=self.observatory)
        base = os.path.basename(file)
        n_bytes = int(info["size"])

        # Only output verification info for slow sha1sum checks by default
        log.verbose(
            api.file_progress(
                "Verifying", base, path, n_bytes, bytes_so_far, total_bytes, nth_file, total_files),
            verbosity=10 if self.args.check_sha1sum else 60)

        if not os.path.exists(path):
            if base not in self.bad_files:
                log.error("File", repr(base), "doesn't exist at", repr(path))
            return

        # Checks which force repairs should do if/else to avoid repeat repair
        size = os.stat(path).st_size
        if int(info["size"]) != size:
            self.error_and_repair(path, "File", repr(base), "length mismatch LOCAL size=" + srepr(size),
                                  "CRDS size=" + srepr(info["size"]))
        elif self.args.check_sha1sum or config.is_mapping(base):
            log.verbose("Computing checksum for", repr(base), "of size", repr(size), verbosity=60)
            sha1sum = utils.checksum(path)
            if info["sha1sum"] == "none":
                log.warning("CRDS doesn't know the checksum for", repr(base))
            elif info["sha1sum"] != sha1sum:
                self.error_and_repair(path, "File", repr(base), "checksum mismatch CRDS=" + repr(info["sha1sum"]),
                                      "LOCAL=" + repr(sha1sum))

        if info["state"] not in ["archived", "operational"]:
            log.warning("File", repr(base), "has an unusual CRDS file state", repr(info["state"]))

        if info["rejected"] != "false":
            log.verbose_warning("File", repr(base), "has been explicitly rejected.", verbosity=60)
            if self.args.purge_rejected:
                self.remove_files([path], "file")
            return

        if info["blacklisted"] != "false":
            log.verbose_warning("File", repr(base), "has been blacklisted or is dependent on a blacklisted file.",
                                verbosity=60)
            if self.args.purge_blacklisted:
                self.remove_files([path], "file")
            return
        return

    def error_and_repair(self, file, *args, **keys):
        """Issue an error message and repair `file` if requested by command line args."""
        log.error(*args, **keys)
        if self.args.repair_files:
            if config.writable_cache_or_info("Skipping remove and re-download of", repr(file)):
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
                desired_loc = config.locate_file(os.path.basename(refpath), observatory=self.observatory)
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
                        log.verbose_warning("Keeping existing cached file", repr(desired_loc), "already in target mode", repr(new_mode))
                    else:
                        log.verbose_warning("No change in subdirectory mode", repr(old_mode), "skipping reorganization of", repr(refpath))
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
    sys.exit(SyncScript()())
