"""This module is a command line script which handles comparing the best
reference recommendations for a particular context and dataset files.

For more details on the several modes of operations and command line parameters browse the source or run:

% crds bestrefs --help
"""
import sys
import os
from collections import namedtuple, OrderedDict

# ===================================================================

import crds
from crds.core import log, config, utils, timestamp, cmdline, heavy_client
from crds import diff, matches
from . import table_effects, headers
from crds.client import api

# ===================================================================

MIN_DATE = "1900-01-01 00:00:00"
MAX_DATE = "9999-01-01 23:59:59"

# ===================================================================

UpdateTuple = namedtuple("UpdateTuple", ["instrument", "filekind", "old_reference", "new_reference"])

# ============================================================================


def reformat_date_or_auto(date):
    """Add 'auto' as an extra valid value for --datasets-since dates.  Auto means figure out dates-since
    based on USEAFTER dates (recorded in rmaps as DATE-OBS TIME-OBS or META.OBSERVATION.DATE).
    """
    if date is None:
        return date
    elif date.lower() == "auto":
        return "auto"
    else:
        return timestamp.reformat_date(date)


class BestrefsScript(cmdline.Script, cmdline.UniqueErrorsMixin):
    """Command line script for determining best references for a sequence of dataset files."""

    description = """
The crds.bestrefs program runs the CRDS library to interpret CRDS reference
file assignment rules with respect to dataset parameters.

crds.bestrefs has several use cases which have different modes for fetching
input parameters, evaluating bestrefs and/or doing comparisons, and producing output.

crds.bestrefs runs in the HST archive pipeline to populate dataset headers FITS
keywords (e.g. DARKFILE) with best reference files.

Other modes of crds.bestrefs are used to support CRDS reprocessing or to test new
versions of CRDS rules.

The crds.bestrefs program is not normally used for JWST and best references
are assigned automatically as a consequence of running the CAL code.

* Determines best references with respect to a context or contexts.
* Optionally updates the headers of file-based data with new recommendations.
* Optionally compares new results to prior results.
* Optionally prints source data names affected by the new context.
    """

    epilog = """
.......................
crds.bestrefs use cases
.......................

  1. File (HST Pipeline) Mode

  The --files switch can be used to specify a list of FITS dataset files to
  process.  This is used in the HST pipeline in conjunction with
  --update-headers to fill in dataset FITS headers with recommended best
  references::

    % crds bestrefs  --update-headers  --files j8bt05njq_raw.fits ...

  The outcome of this command is updating the best references in the FITS
  headers of the specified .fits files.

  Omitting --update-headers can be used to evaluate bestrefs without altering
  the input FITS files::

    % crds bestrefs --print-new-references --files  j8bt05njq_raw.fits ...

  The --new-context switch can be used to choose a context which is not the
  current default::

    % crds bestrefs --new-context hst_0457.pmap --files ...

  2. Reprocessing Mode

  The bestrefs reprocessing mode is used in conjunction with archive databases
  to determine datasets which should be reprocessed as a consequence of the
  delivery of new reference files.

  Reprocessing mode evaluates the same dataset parameters with respect to an
  old context and a new context and recommends reprocessing datasets where some
  reference file assignment changes.

  Bestrefs reprocessing mode is run automatically on the CRDS servers whenever
  new reference files are delivered, after the new CRDS context is selected for
  use by the archive pipeline.  It is run e.g. like this::

    % crds bestrefs --affected-datasets --old-context  hst_0001.pmap --new-context hst_0002.pmap

  --affected-datasets is a "bundle switch" that captures standard options for
  reprocessing.  See *crds bestrefs --help* for more information on individual
  switches.

  Running reprocessing mode requires setting *CRDS_SERVER_URL*.

  3. Context Testing Mode

  CRDS bestrefs and the archive reprocessing parameters can also provide a
  quick way to evaluate a new context and/or residual errors.  It can answer
  the question "what classes of errors still exist for the latest context with
  respect to known parameter sets?"

  Context testing mode can be run like this::

    % crds bestrefs --check-context --new-context jwst-edit

  Context testing also requires setting *CRDS_SERVER_URL* to obtain archived
  dataset parameters.  Note that during JWST pre-I&T the archive database often
  contains parameter sets related to obsolete test cases.

  Undesired test cases can be weeded out like this::

    % crds bestrefs --check-context --new-context jwst-edit --drop-ids JW93135336001_02102_00001.MIRIFUSHORT:JW93135336001_02102_00001.MIRIFUSHORT

...........
New Context
...........

crds.bestrefs always computes best references with respect to a context which
can be explicitly specified with the --new-context parameter.  If --new-context
is not specified, the default operational context is determined by consulting
the CRDS server or looking in the local cache.

...........
Old Context
...........

--old-context can be used to specify a second context for which bestrefs
are dynamically computed; --old-context implies that a bestrefs comparison
will be made with --new-context.  If --old-context is not specified, it
defaults to None.  --old-context is only used for context-to-context
comparisons,  nominally for CRDS repro.

........................
Lookup Parameter Sources
........................

The following methods can be used to define parameter sets for which to compute
best references::

  --files can be used to specify a list of FITS files from which to load
    parameters and optionall update headers.

  --instruments can be used to specify a list of instruments.  Without
    --diffs-only or --datasets-since this choice selects ALL datasets for the
    specified instruments.

  --all-instruments is shorthand for all --instruments supported by the project.
    This parameter can be so memory intensive as to be infeasible.

  --datasets is used to specify a list of dataset IDs as would be found under --instruments.

  --load-pickles can be used to specify a list of .pkl or .json files that define parameter
    sets.  These can most easily be created using --save-pickle.

................
Comparison Modes
................

The --old-context and --compare-source-bestrefs parameters define the best
references comparison mode.  Each names the origin of a set of prior
recommendations and implicitly requests a comparison to the recommendations
from the newly computed bestrefs determined by --new-context.

*--old-context CONTEXT* specifies that the reference results should be
*computed* using the named context.

*--compare-source-bestrefs* directs that prior reference assignments should be
taken from the same *stored source* which provides matching parameters.  These
could be from FITS header keywords (e.g. DARKFILE), from live archive
parameters, or from prior parameter sets that have been stored in CRDS .json or
Python pickle files.

......................
Pickle and .json saves
......................

crds.bestrefs can load parameters and past results from a sequence of .pkl or
.json files using --load-pickles.  These are combined into a single parameter
source in command line order.

crds.bestrefs can save the parameters obtained from various sources into .pkl
or .json formatted save files using --save-pickle.  The single combined result
of multiple pickle or instrument parameter sources is saved.  The file
extension (.json or .pkl) defines the format used.

The preferred .json format defines a singleton { id: parameters}
dictionary on each line as a series of isolated .json objects.  Strictly
speaking only each individual line is .json,  but this localizes any errors.

.json format is preferred over .pkl because it is more transparent and robust
across different versions of Python.

.........
Verbosity
.........

crds.bestrefs has --verbose and --verbosity=N parameters which can increase the
amount of informational and debug output.  Verbosity ranges from 0..100 where 0
means "no debug output" and 100 means "all debug output".  50 is the default
for --verbose.

.........
Bad Files
.........

CRDS files can be designated as scientifically invalid on the CRDS server by
the CRDS team.  Knowledge of bad files is synchronized to remote caches by
crds.bestrefs and crds.sync.  By default, attempting to use bad rules or assign
bad references will generate errors and fail.  crds.bestrefs supports two
command line switches, *---allow-bad-rules* and *---allow-bad-references* to
override the default handling of bad files and enable their use with warnings.
Environment variables **CRDS_ALLOW_BAD_RULES** and
**CRDS_ALLOW_BAD_REFERENCES** can also be set to 1 to establish warnings rather
than errors as the default.
    """

    def __init__(self, *args, **keys):
        cmdline.Script.__init__(self, *args, **keys)

        # Placeholders until complex init is done.
        self.instruments = None
        self.oldctx = None
        self.newctx = None

        if self.args.regression:
            self.args.compare_source_bestrefs = True
            self.args.differences_are_errors = True
            self.args.stats = True
            self.args.dump_unique_errors = True

        if self.args.affected_datasets:
            self.args.diffs_only = True
            if not self.args.datasets_since:
                self.args.datasets_since = "auto"
            self.args.print_update_counts = True
            self.args.print_affected = True
            self.args.dump_unique_errors = True
            self.args.stats = True
            self.args.undefined_differences_matter = True
            self.args.na_differences_matter = True

        if self.args.check_context:
            self.args.dump_unique_errors = True
            self.args.stats = True
            self.args.undefined_differences_matter = True
            self.args.na_differences_matter = True
            if not self.args.all_errors_file:
                self.args.all_errors_file = "all_errors.ids"
            if not self.args.unique_errors_file:
                self.args.unique_errors_file = "unique_errors.ids"

        config.ALLOW_BAD_RULES.set(self.args.allow_bad_rules)
        config.ALLOW_BAD_REFERENCES.set(self.args.allow_bad_references)

        cmdline.UniqueErrorsMixin.__init__(self, *args, **keys)

        self.updates = OrderedDict()  # map of reference updates
        self.kill_list = OrderedDict()

        self.process_filekinds = [typ.lower() for typ in self.args.types ]    # list of filekind str's

        self.skip_filekinds = [typ.lower() for typ in self.args.skip_types]
        self.affected_instruments = None

        # See also complex_init()
        self.new_context = None     # Mapping filename
        self.old_context = None     # Mapping filename

        # headers corresponding to the new context
        self.new_headers = headers.HeaderGenerator(None,None,None)  # Abstract for pylint, replaced later

        # comparison variables
        self.compare_prior = None       # bool
        self.old_headers = headers.HeaderGenerator(None,None,None)  # Abstract for pylint, replaced later
        self.old_bestrefs_name = None   # info str identifying comparison results source,  .pmap filename or text

        self.pickle_headers = None  # any headers loaded from pickle files

        if self.args.remote_bestrefs:
            os.environ["CRDS_MODE"] = "remote"

        self.datasets_since = self.args.datasets_since

        self.active_header = None   # new or old header last processed with bestrefs
    def complex_init(self):
        """Complex init tasks run inside any --pdb environment,  also unfortunately --profile."""

        assert not (self.args.sync_references and self.readonly_cache), "Readonly cache,  cannot fetch references."

        self.new_context, self.old_context = self.setup_contexts()

        # Support 0 to 1 mutually exclusive source modes and/or any number of pickles
        exclusive_source_modes = [self.args.files, self.args.datasets, self.args.instruments,
                                  self.args.diffs_only, self.args.all_instruments]
        source_modes = len(exclusive_source_modes) - exclusive_source_modes.count(None)
        using_pickles = int(bool(self.args.load_pickles))
        assert source_modes <= 1 and (source_modes + using_pickles) >= 1, \
            "Must specify one of: --files, --datasets, --instruments, --all-instruments, --diffs-only and/or --load-pickles."

        if self.args.diffs_only:
            assert self.new_context and self.old_context, \
                "--diffs-only only works for context-to-context bestrefs."
            differ = diff.MappingDifferencer(
                self.observatory, self.old_context, self.new_context,
                include_header_diffs=True, hide_boring_diffs=True)
            self.affected_instruments = differ.get_affected()
            log.info("Mapping differences from", repr(self.old_context),
                     "-->", repr(self.new_context), "affect:\n",
                     log.PP(self.affected_instruments))
            self.instruments = self.affected_instruments.keys()
            if not self.instruments:
                log.info("No instruments were affected.")
                return False
            if (self.args.datasets_since == "auto" and
                    (differ.header_modified() or differ.files_deleted())):
                log.info("Checking all dates due to header changes or file deletions.")
                self.args.datasets_since = MIN_DATE
        elif self.args.instruments:
            self.instruments = self.args.instruments
        elif self.args.all_instruments:
            instruments = list(self.obs_pkg.INSTRUMENTS)
            for instr in ("all","system","synphot"):
                if instr in instruments:
                    instruments.remove(instr)
            self.instruments = instruments
        else:
            self.instruments = []

        if self.args.datasets_since == "auto":
            datasets_since = self.auto_datasets_since()
        else:
            datasets_since = self.args.datasets_since

        # headers corresponding to the new context
        self.new_headers = self.init_headers(self.new_context, datasets_since)

        self.compare_prior, self.old_headers, self.old_bestrefs_name = self.init_comparison(datasets_since)

        if not self.compare_prior:
            log.info("No comparison context or source comparison requested.")

        if self.args.files and not self.args.update_bestrefs:
            log.info("No file header updates requested;  dry run.  Use --update-bestrefs to update FITS headers.")

        return True

    @property
    def only_ids(self):
        return self._normalized(self.args.only_ids) or None

    @property
    def drop_ids(self):
        return self._normalized(self.args.drop_ids)

    def _normalized(self, id_list):
        if id_list:
            return [self.normalize_id(dataset) for dataset in id_list]
        else:
            return []

    def normalize_id(self, dataset):
        """Convert a given `dataset` ID to uppercase.  For the sake of simplicity convert
        simple IDs into unassociated exposure IDs in <exposure>:<exposure> form.  This is a
        convenience for JWST where currently the <product> term is always identical to
        <exposure>.  Where they're different as-in associated exposures for HST,  you must
        specify the drop ID fully to avoid misinterpretation as an unassociated exposure.
        """
        dataset = dataset.upper()
        if ":" not in dataset:
            dataset = dataset + ":" + dataset
        return dataset

    def auto_datasets_since(self):
        """Support --datasets-since="auto" and compute min EXPTIME for all references determined by diffs.

        Returns { instrument: EXPTIME, ... }
        """
        datasets_since = {}
        self.oldctx = crds.get_pickled_mapping(self.old_context)   # reviewed
        self.newctx = crds.get_pickled_mapping(self.new_context)   # reviewed
        for instrument in self.oldctx.selections:
            old_imap = self.oldctx.get_imap(instrument)
            new_imap = self.newctx.get_imap(instrument)
            added_references = diff.get_added_references(old_imap, new_imap)
            deleted_references = diff.get_deleted_references(old_imap, new_imap)
            added_exp_time = deleted_exp_time = MAX_DATE
            if added_references:
                added_exp_time = matches.get_minimum_exptime(new_imap, added_references)
            if deleted_references:
                deleted_exp_time = matches.get_minimum_exptime(old_imap, deleted_references)
            exp_time = min(added_exp_time, deleted_exp_time)
            if exp_time != MAX_DATE:  # if a USEAFTER min found,  remember it.
                datasets_since[instrument] = exp_time
        log.info("Possibly affected --datasets-since dates determined by",
                 repr(self.old_context), "-->", repr(self.new_context), "are:\n", log.PP(datasets_since))
        return datasets_since

    def add_args(self):
        """Add bestrefs script-specific command line parameters."""

        self.add_argument("-n", "--new-context", dest="new_context",
                          help="Compute the updated best references using this context. "
                          "Uses current operational context by default.",
                          default=None, type=cmdline.mapping_spec)

        self.add_argument("-o", "--old-context", dest="old_context",
                          help="Compare bestrefs recommendations from two contexts.",
                          metavar="OLD_CONTEXT", default=None, type=cmdline.mapping_spec)

        self.add_argument("--fetch-old-headers", dest="fetch_old_headers", action="store_true",
                          help="Fetch old headers in accord with old parameter lists.   Slower,  avoid unless required.")

        self.add_argument("-f", "--files", nargs="+", metavar="FILES", default=None,
                          help="Dataset files to compute best references for and optionally update headers.")

        self.add_argument("-d", "--datasets", nargs="+", metavar="IDs", default=None,
                          help="Dataset ids to consult database for matching parameters and old results.")

        self.add_argument("--all-instruments", action="store_true", default=None,
                          help="Compute best references for cataloged datasets for all supported instruments in database.")

        self.add_argument("-i", "--instruments", nargs="+", metavar="INSTRUMENTS", default=None,
                          help="Instruments to compute best references for, all historical datasets in database.")

        self.add_argument("-p", "--load-pickles", nargs="*", default=None,
                          help="Load dataset headers and prior bestrefs from pickle files,  in worst-to-best update order.  Can also load .json files.")

        self.add_argument("-a", "--save-pickle", default=None,
                          help="Write out the combined dataset headers to the specified pickle file.  Can also store .json file.")

        self.add_argument("-t", "--types", nargs="+",  metavar="REFERENCE_TYPES",  default=(),
                          help="Explicitly define the list of reference types to process, --skip-types also still applies.")

        self.add_argument("-k", "--skip-types", nargs="+",  metavar="SKIPPED_REFERENCE_TYPES",  default=(),
                          help="A list of reference types which should not be processed,  defaulting to nothing.")

        self.add_argument("--all-types", action="store_true",
                          help="Evaluate every reference file type regardless of dataset exposure type.")

        self.add_argument("--diffs-only", action="store_true", default=None,
                          help="For context-to-context comparison, choose only instruments and types from context differences.")

        self.add_argument("--datasets-since", default=None, type=reformat_date_or_auto,
                          help="Cut-off date for datasets, none earlier than this.  Use 'auto' to exploit reference USEAFTER.  OFF by default.")

        self.add_argument("-c", "--compare-source-bestrefs", dest="compare_source_bestrefs", action="store_true",
                          help="Compare new bestrefs recommendations to recommendations from data source,  files or database.")

        self.add_argument("--update-pickle", action="store_true",
                          help="Replace source bestrefs with CRDS bestrefs in output pickle.  For setting up regression tests.")

        self.add_argument("--only-ids", nargs="*", default=None, dest="only_ids", metavar="IDS",
                          help="If specified, process only the listed dataset ids.")

        self.add_argument("--drop-ids", nargs="*", default=[], dest="drop_ids", metavar="IDS",
                          help="If specified, skip these dataset ids.")

        self.add_argument("-u", "--update-bestrefs",  dest="update_bestrefs", action="store_true",
                          help="Update sources with new best reference recommendations.")

        self.add_argument("--print-affected", dest="print_affected", action="store_true",
                          help="Print names of products for which the new context would assign new references for some exposure.")

        self.add_argument("--print-affected-details", action="store_true",
                          help="Include instrument and affected types in addition to compound names of affected exposures.")

        self.add_argument("--print-new-references", action="store_true",
                          help="Prints one line per reference file change.  If no comparison requested,  prints all bestrefs.")

        self.add_argument("--print-update-counts", action="store_true",
                          help="Prints dictionary of update counts by instrument and type,  status on updated files.")

        self.add_argument("--print-error-headers", action="store_true",
                          help="For each tracked error,  print out the corresponding dataset header for offline analysis.")

        self.add_argument("-r", "--remote-bestrefs", action="store_true",
                          help="Compute best references on CRDS server,  convenience for env var CRDS_MODE='remote'")

        self.add_argument("-m", "--sync-mappings", default="1", dest="sync_mappings", type=int,
                          help="Fetch the required context mappings to the local cache.  Defaults TRUE.")

        self.add_argument("-s", "--sync-references", default="0", dest="sync_references", type=int,
                          help="Fetch the refefences recommended by new context to the local cache. Defaults FALSE.")

        self.add_argument("--differences-are-errors", action="store_true",
                          help="Treat recommendation differences between new context and original source as errors.")

        self.add_argument("--allow-bad-rules", action="store_true",
                          help="Only warn if a context which is marked 'bad' is used, otherwise error.")

        self.add_argument("--allow-bad-references", action="store_true",
                          help="Only warn if a reference which is marked bad is recommended, otherwise error.")

        self.add_argument("--undefined-differences-matter", action="store_true",
                          help="If not set, a transition from UNDEFINED to anything else is not considered a difference error.")

        self.add_argument("--na-differences-matter", action="store_true",
                          help="If not set,  either CDBS or CRDS recommending N/A is OK to mismatch.")

        self.add_argument("-g", "--regression", action="store_true",
                          help="Abbreviation for --compare-source-bestrefs --differences-are-errors --dump-unique-errors --stats")

        self.add_argument("--check-context", action="store_true",
                          help="Abbreviation for --undefined-differences-matter "
                          "--na-differences-matter --dump-unique-errors --stats")

        self.add_argument("--affected-datasets", action="store_true",
                          help="Abbreviation for --diffs-only --datasets-since=auto --undefined-differences-matter "
                          "--na-differences-matter --print-update-counts --print-affected --dump-unique-errors --stats")

        self.add_argument("-z", "--optimize-tables", action="store_true",
                          help="If set, apply row-based optimizations to screen out inconsequential table updates.")

        self.add_argument("--eliminate-duplicate-cases", action="store_true",
                          help="Categorize unique bestrefs results as errors to determine representative test cases...  Replaces normal error counts with coverage counts and ids.")

        cmdline.UniqueErrorsMixin.add_args(self)

    def setup_contexts(self):
        """Determine and cache the new and comparison .pmap's for this run."""
        if self.args.new_context is None:
            log.verbose("Using default new context", repr(self.default_context),
                        "for computing updated best references.", verbosity=25)
            new_context = self.default_context
        else:
            log.verbose("Using explicit new context", repr(self.args.new_context),
                        "for computing updated best references.", verbosity=25)
            new_context = self.resolve_context(self.args.new_context)
        if self.args.old_context is not None:
            log.verbose("Using explicit old context", repr(self.args.old_context), verbosity=25)
            old_context = self.resolve_context(self.args.old_context)
        else:
            old_context = None
        if self.server_info.effective_mode != "remote":
            if old_context is not None and not os.path.dirname(old_context):
                self.dump_mappings([old_context])
            if not os.path.dirname(new_context):
                self.dump_mappings([new_context])
        return new_context, old_context

    @utils.cached
    def warn_bad_context(self, name, context, instrument):
        """Issue a warning if `context` of named `name` is a known bad file."""
        # Get subset of bad files contained by this context.
        if context is None:
            return
        bad_contained = heavy_client.get_bad_mappings_in_context(self.observatory, context, instrument)
        if bad_contained:
            if not config.ALLOW_BAD_RULES:
                self.log_and_track_error("ALL", "ALL", "ALL", name, "=", repr(context),
                                         "is bad or contains bad rules.  Use is not recommended,  results may not be scientifically valid.")
            else:
                log.warning(name, "=", repr(context),
                            "is bad or contains bad rules.  Use is not recommended,  results may not be scientifically valid.")
            log.verbose(name, "=", repr(context), "contains bad rules", repr(bad_contained))

    def warn_bad_reference(self, dataset, instrument, filekind, reference):
        """Issue a warning if `reference` is a known bad file."""
        if reference.lower() in self.bad_files:
            if not config.ALLOW_BAD_REFERENCES:
                self.log_and_track_error(dataset, instrument, filekind, "File", repr(reference),
                                         "is bad. Use is not recommended,  results may not be scientifically valid.")
            else:
                log.warning("For", dataset, instrument, filekind, "File", repr(reference),
                            "is bad. Use is not recommended,  results may not be scientifically valid.")
            return 1
        else:
            return 0

    def warn_bad_updates(self):
        """Issue warnings for each bad references in the updates map.  This is not inlined in the
        getreferences() core function because it only pertains to *new* bad reference assignments,
        not old ones,  so it is only relevant for an update,  not every assignment.
        """
        log.verbose("Checking updates for bad files.")
        bad_files = 0
        for (dataset, updates) in sorted(self.updates.items()):
            for update in sorted(updates):
                bad_files += self.warn_bad_reference(dataset, update.instrument, update.filekind, update.new_reference)
        log.verbose("Total bad files =", bad_files)

    def locate_file(self, filename):
        """Locate a dataset file leaving the path unchanged. Applies to self.args.files"""
        return filename

    def init_headers(self, context, datasets_since):
        """Create header a header generator for `context`,  interpreting command line parameters."""
        if self.args.files:
            the_headers = headers.FileHeaderGenerator(context, self.files, datasets_since)
            # log.info("Computing bestrefs for dataset files", self.args.files)
        elif self.args.datasets:
            self.require_server_connection()
            the_headers = headers.DatasetHeaderGenerator(context, [dset.upper() for dset in self.args.datasets], datasets_since)
            log.info("Computing bestrefs for datasets", repr(self.args.datasets))
        elif self.instruments:
            self.require_server_connection()
            log.info("Computing bestrefs for db datasets for", repr(list(self.instruments)))
            the_headers = headers.InstrumentHeaderGenerator(
                context, self.instruments, datasets_since, self.args.save_pickle, self.server_info)
        elif self.args.load_pickles:
            the_headers = None
        else:
            log.error("Invalid header source configuration.   "
                      "Specify --files, --datasets, --instruments, --all-instruments, or --load-pickles.")
            self.print_help()
            sys.exit(-1)
        if self.args.load_pickles:
            self.pickle_headers = headers.PickleHeaderGenerator(
                context, self.args.load_pickles, only_ids=self.only_ids, datasets_since=datasets_since)
            if the_headers:   # combine partial correction headers field-by-field
                log.verbose("Augmenting primary parameter sets with pickle overrides.")
                the_headers.update_headers(self.pickle_headers.headers, only_ids=self.only_ids)
            else:   # assume pickles-only sources are all complete snapshots
                log.verbose("Computing bestrefs solely from pickle files:", repr(self.args.load_pickles))
                the_headers = self.pickle_headers
        return the_headers

    def init_comparison(self, datasets_since):
        """Interpret command line parameters to determine comparison mode."""
        assert not (self.args.old_context and self.args.compare_source_bestrefs), \
            "Cannot specify both --old-context and --compare-source-bestrefs."
        compare_prior = \
            self.args.old_context or \
            self.args.compare_source_bestrefs or \
            self.args.print_affected or \
            self.args.print_affected_details
        # self.args.update_bestrefs or \
        if compare_prior:
            if self.args.old_context:
                old_fname = self.args.old_context
                if self.args.fetch_old_headers:
                    log.verbose("Fetching old headers independently allowing them to differ from new headers.")
                    old_headers = self.init_headers(self.old_context, datasets_since)
                else:
                    log.verbose_warning("Assuming parameter names and required types are the same across contexts.")
                    old_headers = self.new_headers
            else:
                old_fname = "recorded bestrefs"
                old_headers = self.new_headers
        else:
            old_headers = old_fname = None
        return compare_prior, old_headers, old_fname

    def main(self):
        """Compute bestrefs for datasets."""
        # Finish __init__() inside --pdb
        if self.complex_init():
            for i, dataset in enumerate(self.new_headers):
                if i != 0 and i % 1000 == 0:
                    log.verbose(self.get_stat("datasets"), "sources processed", verbosity=5)
                self.process(dataset)
            self.post_processing()
        self.report_stats()
        if self.args.eliminate_duplicate_cases:
            log.warning("Running in --eliminate-duplicate-cases mode;  even successful bestrefs are categorized as errors for analysis.")
        log.verbose(self.get_stat("datasets"), "sources processed", verbosity=5)
        log.verbose(len(self.unkilled_updates), "source updates", verbosity=5)
        log.standard_status()
        return log.errors()

    def process(self, dataset):
        """Process best references for `dataset`,  printing dataset output,  collecting stats, trapping exceptions."""
        with log.error_on_exception("Failed processing", repr(dataset)):
            log.verbose("=" * 120)
            if dataset in self.drop_ids:
                log.verbose("Skipping drop-list dataset", repr(dataset))
                return
            elif self.only_ids and dataset not in self.only_ids:
                log.verbose("Skipping", repr(dataset), "not in --only-ids", verbosity=80)
                return
            elif self.args.files:
                log.info("===> Processing", dataset)     # file mode
            else:
                log.verbose("===> Processing", dataset, verbosity=25)   # database or regression modes
            self.increment_stat("datasets", 1)
            self._process(dataset)

    def _process(self, dataset):
        """Core best references,  add to update tuples."""
        self.active_header = new_header = self.new_headers.get_lookup_parameters(dataset)
        instrument = utils.header_to_instrument(new_header)
        self.warn_bad_context("New-context", self.new_context, instrument)
        new_bestrefs = self.get_bestrefs(instrument, dataset, self.new_context, new_header)
        if self.compare_prior:
            self.warn_bad_context("Old-context", self.old_context, instrument)
            if self.args.old_context:
                self.active_header = old_header = self.old_headers.get_lookup_parameters(dataset)
                old_bestrefs = self.get_bestrefs(instrument, dataset, self.old_context, old_header)
            else:
                old_bestrefs = self.old_headers.get_old_bestrefs(dataset)
            updates, kill_list = self._compare_bestrefs(instrument, dataset, old_bestrefs, new_bestrefs)
            if self.args.optimize_tables:
                updates = self.optimize_tables(dataset, updates)
        else:
            updates, kill_list = self._screen_bestrefs(instrument, dataset, new_bestrefs)
        if self.args.update_pickle:  # XX  mutating input bestrefs to support updated pickles
            self.new_headers.update_headers({dataset: new_bestrefs})
        if updates:
            self.updates[dataset] = updates
        if kill_list:
            self.kill_list[dataset] = kill_list

    def get_bestrefs(self, instrument, dataset, context, header):
        """Compute the bestrefs for `dataset` with respect to loaded mapping/context `ctx`."""
        with log.augment_exception("Failed determining reference types for", repr(dataset),
                                   "with respect to", (instrument, context, header)):
            reftypes = self.determine_reftypes(instrument, dataset, context, header)
            if reftypes is None:
                return {}
        with log.augment_exception("Failed computing bestrefs for data", repr(dataset),
                                   "with respect to", repr(context)):
            bestrefs = crds.getrecommendations(
                header, reftypes=reftypes, context=context, observatory=self.observatory, fast=log.get_verbose() < 50)
        return {key.upper(): value for (key, value) in bestrefs.items()}

    def determine_reftypes(self, instrument, dataset, context, header):
        """Based on instrument, context, header as well as command line parameters determine the list
        of reftypes that should be processed.

        Incorporate knowledge from:

        1. --diffs-only   (context-to-context differences determine affected types)
        2. --types        explicit command line specification
        3. Applicable types from project specific locate.header_to_reftypes()
        4. --all-types    override 1-3 above,  check all
        5. --skip-types   explicit command line removal, reduce 1-4 above
        """
        applicable_types = set()
        with log.verbose_warning_on_exception("Failed determining reftypes for", repr(dataset)):
            applicable_types = set(self.locator.header_to_reftypes(header, context))
        if self.affected_instruments:
            types = set(self.affected_instruments[instrument.lower()])
            if applicable_types:
                types &= applicable_types
            if not types:
                return None
        elif self.args.types:
            types = set(self.process_filekinds)
        else:
            types = applicable_types
        if self.args.all_types or not types:  # --all-types trumps --types, --diffs-only
            pmap = crds.get_pickled_mapping(context)
            types = pmap.get_imap(instrument).selections.keys()
        if types and self.args.skip_types:
            types = set(types) - set(self.args.skip_types)
        types = sorted(list(types))
        return types

    @property
    def update_promise(self):
        """Return a string identifying that and update would or will occurr, depending on --update-bestrefs."""
        if self.args.update_bestrefs:
            return ":: Updating."
        else:
            return ":: Would update."

    no_update = ":: No update."

    def verbose_with_prefix(self, dataset, instrument, filekind, *args, **keys):
        """Output a verbose log message with a prefix formated using format_prefix()."""
        if log.should_output(*args, **keys):
            log.verbose(self.format_prefix(dataset, instrument, filekind), *args, **keys)

    def screen_bestrefs(self, instrument, dataset, newrefs):
        """Return only the update tuples of _screen_bestrefs."""
        return self._screen_bestrefs(instrument, dataset, newrefs)[0]

    def _screen_bestrefs(self, instrument, dataset, newrefs):
        """Scan best references dict `newrefs` for atypical results and issue errors and warnings.

        Returns ([UpdateTuple(), ...], [kill list, ...])
        """
        # XX  This is closely related to compare_bestrefs, maintain both!!   See also update_bestrefs()

        log.verbose("-" * 120, verbosity=55)

        updates, kill_list = [], []

        for filekind in sorted(newrefs):

            filekind = filekind.lower()

            if filekind in self.skip_filekinds:
                self.verbose_with_prefix(dataset, instrument, filekind, "Skipping type.", verbosity=55)
                continue

            new_ok, new = self.handle_na_and_not_found("New:", newrefs, dataset, instrument, filekind)
            update = UpdateTuple(instrument, filekind, None, new)
            if new_ok or self.args.update_pickle or self.args.eliminate_duplicate_cases:
                self.verbose_with_prefix(dataset, instrument, filekind,
                    "Bestref FOUND:", repr(new).lower(),  self.update_promise, verbosity=30)
                updates.append(update)
            else:  # ERROR's cannot update
                kill_list.append(update)

        return updates, kill_list

    def compare_bestrefs(self, instrument, dataset, oldrefs, newrefs):
        """Return only the update tuples of _compare_bestrefs()."""
        return self._compare_bestrefs(instrument, dataset, oldrefs, newrefs)[0]

    def _compare_bestrefs(self, instrument, dataset, oldrefs, newrefs):
        """Compare best references dicts `newrefs` and `oldrefs` for `instrument` and `dataset`.

        Returns ([UpdateTuple(), ...], [Kill list...])
        """
        # XX  This is closely related to screen_bestrefs,  maintain both!!    See also update_bestrefs()

        log.verbose("-" * 120, verbosity=55)

        updates, kill_list = [], []

        filekinds = sorted(list(set(list(newrefs.keys()) + list(oldrefs.keys()))))
        for filekind in filekinds:

            filekind = filekind.lower()

            if filekind in self.skip_filekinds:
                self.verbose_with_prefix(dataset, instrument, filekind, "Skipping type.", verbosity=55)
                continue

            _old_ok, old = self.handle_na_and_not_found("Old:", oldrefs, dataset, instrument, filekind)

            new_ok, new = self.handle_na_and_not_found("New:", newrefs, dataset, instrument, filekind)

            update = UpdateTuple(instrument, filekind, old, new)

            if not (new_ok or self.args.update_pickle):   # ERROR's in new cannot update,  except during regression capture
                kill_list.append(update)
                continue

            if new != old:
                if self.args.differences_are_errors:  # regression mode vs. reprocessing
                    #  By default, either CDBS or CRDS scoring a reference as N/A short circuits mismatch errors.
                    if (old != "N/A" and new != "N/A") or self.args.na_differences_matter:
                        self.log_and_track_error(dataset, instrument, filekind,
                            "Comparison difference:", sreprlow(old), "-->", sreprlow(new), self.update_promise)
                elif self.args.print_new_references or log.get_verbose() >= 30 or self.args.files:
                    log.info(self.format_prefix(dataset, instrument, filekind),
                             "New best reference:", sreprlow(old), "-->", sreprlow(new), self.update_promise)
                updates.append(update)
            else:
                self.verbose_with_prefix(dataset, instrument, filekind,
                    "Lookup MATCHES:", sreprlow(old), self.no_update,  verbosity=30)
        return updates, kill_list

    def handle_na_and_not_found(self, name, bestrefs, dataset, instrument, filekind):
        """Fetch the bestref for `filekind` from `bestrefs`, and handle conversions to N/A
        and CRDS NOT FOUND errors.

        `name` is a string identifier for this conversion, Old or New.
        `bestrefs` is a dictionary { filekind : bestref, }

        Return (ref_ok, raw_ref, ref)  where:
            raw_ref is the original name of the reference,  stripped of any iref$ prefix.
            ref is the fully normalized name of the reference, converted to N/A as needed.
            ref_ok is True IFF bestrefs did not fail altogether.
        """
        # UNDEFINED corresponds to "no value in database" or "type not defined in CRDS"
        ref_org = cleanpath(bestrefs.get(filekind.upper(), "UNDEFINED")).strip()
        ref = ref_org.upper()
        ref_ok = True
        if ref.startswith("NOT FOUND N/A"):
            self.verbose_with_prefix(dataset, instrument, filekind, "Bestref is natural N/A.", verbosity=60)
            ref = "N/A"
        elif ref in ("NOT FOUND NO MATCH FOUND.", "UNDEFINED", "NONE", "", "*"):
            if self.args.undefined_differences_matter:  # track these when N/A is being scrutinized, regardless of diff.
                self.log_and_track_error(
                    dataset, instrument, filekind, name,  "No match found:", repr(ref_org))
                ref_ok = False
            else:
                self.verbose_with_prefix(dataset, instrument, filekind,
                    name, "No match found:", repr(ref_org), " => 'N/A'.")
                ref = "N/A"
        elif ref.startswith("NOT FOUND"):
            self.log_and_track_error(
                dataset, instrument, filekind, name, "Bestref FAILED:", ref_org[len("NOT FOUND"):])
            ref_ok = False
        return ref_ok, ref

    def log_and_track_error(self, dataset, *pars, **keys):
        """Track and categorize the specified error,  printing out the dataset header
        if requested on the command line.
        """
        parts = dataset.split(":")
        if parts[0] == parts[-1]:  # no guarantee len() == 2
            dataset = parts[0]
        super(BestrefsScript, self).log_and_track_error(dataset, *pars, **keys)
        if self.args.print_error_headers:
            log.info("Header for", repr(dataset) + ":\n", log.PP(self.active_header))

    def post_processing(self):
        """Given the computed update list, print out results,  update file headers, and fetch missing references."""

        if self.args.save_pickle:
            self.new_headers.save_pickle(self.args.save_pickle, only_ids=self.only_ids)

        self.warn_bad_updates()  # Warn about bad file reference updates only, not failures

        if self.args.print_new_references:
            self.print_new_references()

        if self.args.update_bestrefs:
            log.verbose("Performing best references updates.")
            self.new_headers.handle_updates(self.updates)

        if self.args.sync_references:
            self.sync_references()

        if self.args.print_update_counts:
            self.print_update_stats()  # For affected datasets

        if self.args.print_affected:
            self.print_affected()

        if self.args.print_affected_details:
            self.print_affected_details()

        if self.args.eliminate_duplicate_cases:
            self.eliminate_duplicate_cases()

        self.dump_unique_errors()

    def optimize_tables(self, dataset, updates):
        """Drop table updates for which the reference change doesn't matter based upon examining the
        selected rows.
        """
        for update in sorted(updates):
            new_header = self.new_headers.header(dataset)
            if not table_effects.is_reprocessing_required(dataset, new_header, self.old_context, self.new_context, update):
                updates.remove(update)  # reprocessing not required, ignore update.
                log.verbose("Removing table update for", update.instrument, update.filekind, dataset,
                            "no effective change from reference", repr(update.old_reference),
                            "-->", repr(update.new_reference), verbosity=25)
        return updates

    @property
    def unkilled_updates(self):
        """Return only members of self.updates for which there is no corresponding kill list of failed bestrefs."""
        return { dataset:updates for (dataset, updates) in self.updates.items()
                 if updates and dataset not in self.kill_list }

    def print_affected(self):
        """Print the product id for any product which has new bestrefs for any
        of its component exposures.   All components share a common product id.
        """
        affected_products = { self.dataset_to_product_id(dataset)
                              for dataset in self.unkilled_updates }
        log.info("Affected products =", len(affected_products))
        for product in sorted(affected_products):
            print(product)
        sys.stdout.flush()

    def dataset_to_product_id(self, dataset):
        """CRDS manages products and associations using : separated compound IDs of indeterminate
        complexity.  The only thing guaranteed is that the first colon-section of the dataset ID is the
        product (for possible reprocessing) which is reported whenever any bestref changes for any
        dataset ID beginning with that prefix.
        """
        return dataset.split(":")[0].lower()

    def print_affected_details(self):
        """Print compound ID, instrument, and affected reference types for every exposure with new best references,
        one line per exposure.
        """
        for dataset in sorted(self.updates):
            if self.updates[dataset]:
                types = sorted([update.filekind for update in self.updates[dataset]])
                print("{} {} {}".format(dataset.lower(), self.updates[dataset][0].instrument.lower(), " ".join(types)))
        sys.stdout.flush()

    def print_update_stats(self):
        """Print update counts for each instrument and type."""
        stats = dict()
        for dataset in self.updates:
            for update in self.updates[dataset]:
                if update.instrument not in stats:
                    stats[update.instrument] = dict()
                if update.filekind not in stats[update.instrument]:
                    stats[update.instrument][update.filekind] = 0
                stats[update.instrument][update.filekind] += 1
        log.info("Updated exposure counts:\n", log.PP(stats))

    def print_new_references(self):
        """Print the compound id and update tuple for each exposure with updates."""
        for dataset in sorted(self.updates):
            for update in self.updates[dataset]:
                print(dataset.lower() + " " + " ".join([str(val).lower() for val in update]))
        sys.stdout.flush()

    def eliminate_duplicate_cases(self):
        """Special mode to categorize *single context* bestrefs results, good or
        errors, as unique error strings.
        """
        log.reset()
        self.clear_error_counts()
        for dataset in self.updates:
            updates = self.updates[dataset]
            self.log_and_track_error(
                dataset, "any", "any", "COVERAGE:", self.updates_repr(updates))

    def updates_repr(self, updates):
        """Convert a single dataset's list of update tuples into a string which
        can be used to define unique CRDS results for coverage purposes.
        """
        return str(sorted([tuple(update) for update in updates])).lower()

    def sync_references(self):
        """Locally cache the new references referred to by updates."""
        synced_references = {
            tup.new_reference.lower()
            for dataset in self.updates
            for tup in self.updates[dataset] if tup.new_reference not in ["N/A"]
        }
        api.dump_references(self.new_context, sorted(synced_references), raise_exceptions=self.args.pdb)

# ============================================================================

def sreprlow(s):
    """Squash unicode and return the repr() of string `s` as lower case."""
    return repr(str(s)).lower()

def cleanpath(name):
    """jref$n4e12510j_crr.fits  --> n4e12510j_crr.fits"""
    if "ref$" in name:
        return name.split("$")[-1].strip()
    elif name.startswith("crds://"):
        return name[len("crds://"):]
    else:
        return name

# ============================================================================

def assign_bestrefs(filepaths, context=None, reftypes=(),
                    sync_references=False, verbosity=-1):
    """Assign best references to FITS files specified by `filepaths`
    filling in appropriate reference type keywords.

    Define best references using either .pmap `context` or the default
    CRDS operational context if context=None.

    If `reftypes` is defined, assign bestrefs to only the listed
    reftypes, otherwise assign all reftypes.

    If `sync_references` is True, download any missing reference files
    to the CRDS cache.

    Verbosity defines the level of CRDS log output:

    verbosity=-3    feeling lucky, no output
    verbosity=-2    only errors
    verbosity=-1    only warnings and errors
    verbosity=0     info, warnings, and errors
    verbosity=10    info + minimal progress output
    verbosity=30    info + simplified bestref assignments
    verbosity=50    info + keywords + exact values (standard)
    verbosity=60    info + bestrefs elimination
    ...
    -3 <= verbosity <= 100

    NOTE: While assign_bestrefs() may work for JWST, it is primarily intended
    to expose the behavior of the program used in the HST archive pipeline for
    programmatic use.  Since JWST CAL normally uses an alternate mechanism for
    updating FITS files, using assign_bestrefs() for JWST is less applicable
    and more experimental.

    Returns  count of errors
    """
    old_verbosity = log.set_verbose(verbosity)

    cmd = "crds.bestrefs --update-bestrefs"

    if context:
        cmd += f" --new-context {context}"

    if reftypes:
        types = " ".join(reftypes)
        cmd += f" --types {types}"

    if sync_references:
        cmd += " --sync-references=1"

    files = " ".join(filepaths)
    cmd += f" --files {files}"

    script = BestrefsScript(cmd)

    errors = script()

    log.set_verbose(old_verbosity)

    return errors
