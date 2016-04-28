"""This module is a command line script which handles comparing the best
reference recommendations for a particular context and dataset files.

For more details on the several modes of operations and command line parameters browse the source or run:   

% python -m crds.bestrefs --help
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import sys
import os
from collections import namedtuple, OrderedDict
import json
from crds import python23

try:
    import cPickle as pickle
except ImportError:
    import pickle

import crds
from crds import (log, rmap, data_file, utils, cmdline, heavy_client, diff, timestamp, matches, config)
from crds import table_effects
from crds.client import api
from crds.exceptions import CrdsError, UnsupportedUpdateModeError

# ===================================================================

MIN_DATE = "1900-01-01 00:00:00"
MAX_DATE = "9999-01-01 23:59:59"
    
# ===================================================================

UpdateTuple = namedtuple("UpdateTuple", ["instrument", "filekind", "old_reference", "new_reference"])

# ===================================================================
# There's a problem with using CDBS as a gold standard in getting consistent results between
# DADSOPS DB (fast) and running command line OPUS bestrefs (slow but definitive).   This is kludged
# around here with a two tiered scheme for getting dataset headers:  first load headers from a primary
# source:  files or DADSOPS.  Next update headers from a pickle file computed "elsewhere".   Elsewhere
# is a script that ssh'es to a DMS machine for each dataset and runs OPUS bestrefs,  then eventually
# saves a pickle.
# It is also possible to run solely off of a pickle file(s) (which decouples from the database,  useful for
# both consistency/control and to take a load off the database.)

class HeaderGenerator(object):
    """Generic source for lookup parameters and historical comparison results."""
    def __init__(self, context, sources, datasets_since):
        self.context = context
        self.observatory = utils.file_to_observatory(context)
        self.sources = sources
        self.headers = {}
        self._datasets_since = datasets_since

    def __iter__(self):
        """Return the sources from self with EXPTIME >= self.datasets_since."""
        for source in sorted(self.sources):
            with log.error_on_exception("Failed loading source", repr(source), 
                                        "from", repr(self.__class__.__name__)):
                instrument = utils.header_to_instrument(self.header(source))
                exptime = matches.get_exptime(self.header(source))
                since = self.datasets_since(instrument)
                # since == None when no command line argument given.
                if since is None or exptime >= since:
                    yield source
                else:
                    log.verbose("Dropping source", repr(source), 
                                "with EXPTIME =", repr(exptime),
                                "< --datasets-since =", repr(since))

    def datasets_since(self, instrument):
        """Return the earliest dataset processed cut-off date for `instrument`.
        
        If a universal since-date is in effect,  just return it.
        
        If the since-date varies by instrument, but is not defined for `instrument`, return
        a value equivalent to the end-of-time since it means that no references for `instrument`
        were identified by --datsets-since=auto.
        """
        if isinstance(self._datasets_since, dict):
            return self._datasets_since.get(instrument.lower(),  MIN_DATE)
        else:
            return self._datasets_since

    def header(self, source):
        """Return the full header corresponding to `source`.   If header is a string, raise an exception."""
        header = self._header(source)
        if isinstance(header, str):
            raise CrdsError("Failed to fetch header for " + repr(source) + ": " + repr(header))
        else:
            return dict(header)

    def _header(self, source):
        """Return the full header corresponding to `source`.   Source is a dataset id or filename."""
        return self.headers[source]
    
    def clean_parameters(self, header):
        """Remove extraneous non-bestrefs parameters from header."""
        instrument = utils.header_to_instrument(header)
        # cleaned = { key.upper() : header.get(key, "UNDEFINED")
        #            for key in heavy_client.get_context_parkeys(self.context, instrument) }
        cleaned = header # XXXXX
        cleaned["INSTRUME"] = instrument
        return cleaned
            
    def get_lookup_parameters(self, source):
        """Return the parameters corresponding to `source` used to drive a best references lookup."""
        return self.clean_parameters(self.header(source))

    def get_old_bestrefs(self, source):
        """Return the historical best references corresponding to `source`."""
        return self.clean_parameters(self.header(source))
        # return self.header(source)
    
    def save_pickle(self, outpath, only_ids=None):
        """Write out headers to `outpath` file which can be a Python pickle or .json"""
        if only_ids is None:
            only_hdrs = self.headers
        else:
            only_hdrs = { dataset_id:hdr for (dataset_id, hdr) in self.headers.items() if dataset_id in only_ids }
        log.info("Writing all headers to", repr(outpath))
        if outpath.endswith(".json"):
            with open(outpath, "w+") as pick:
                for dataset, header in sorted(only_hdrs.items()):
                    pick.write(json.dumps({ dataset : header }) + "\n")
        elif outpath.endswith(".pkl"):
            with open(outpath, "wb+") as pick:
                pickle.dump(only_hdrs, pick)
        log.info("Done writing", repr(outpath))
            
    def update_headers(self, headers2, only_ids=None):
        """Incorporate `headers2` updated values into `self.headers`.  Since `headers2` may be incomplete,
        do param-by-param update.   Nominally,  this is to add OPUS bestrefs corrections (definitive) to DADSOPS
        database bestrefs (fast but not definitive).
        """
        if only_ids is None:
            only_ids = headers2.keys()
            
        items = headers2.items()
        for dataset_id, header in items:
            if isinstance(header, python23.string_types):
                log.warning("Skipping bad dataset", dataset_id, ":", headers2[dataset_id])
                del headers2[dataset_id]

        # Munge for consistent case and value formatting regardless of source
        headers2 = { dataset_id : 
                        { key.upper():bestrefs_condition(val) for (key,val) in headers2[dataset_id].items() } 
                        for dataset_id in headers2 if dataset_id in only_ids }
        
        # replace param-by-param,  not id-by-id, since headers2[id] may be partial
        for dataset_id in headers2:
            if dataset_id not in self.headers:
                log.verbose("Adding headers for", repr(dataset_id))
                self.headers[dataset_id] = {}
            else:
                log.verbose("Updating headers for", repr(dataset_id))
            header1, header2 = self.headers[dataset_id], headers2[dataset_id]
            for key in header2:
                if key not in header1 or header1[key] != header2[key]:
                    if key in header1:
                        log.verbose("Updating/correcting", repr(dataset_id), "key", repr(key), 
                                    "from", repr(header1[key]), "to", repr(header2[key]))
                    else:
                        log.verbose("Adding", repr(dataset_id), "key", repr(key), "=", repr(header2[key]))                        
                    header1[key] = header2[key]

    def handle_updates(self, all_updates):
        """Base handle_updates() updates the loaded headers with the computed bestrefs for use 
        with --save-pickle.
        """
        for dataset in sorted(all_updates):
            updates = all_updates[dataset]
            if updates:
                log.verbose("-"*120)
                for update in sorted(updates):
                    new_ref = update.new_reference.upper()
                    if new_ref != "N/A":
                        new_ref = new_ref.lower()
                    self.headers[dataset][update.filekind.upper()] = new_ref

def bestrefs_condition(value):
    """Condition header keyword value to normal form,  converting NOT FOUND N/A to N/A."""
    val = utils.condition_value(value)
    if val == "NOT FOUND N/A":
        val = "N/A"
    return val

# ===================================================================

# FileHeaderGenerator uses a deferred header loading scheme which incrementally reads each header
# from a file as processing is going on via header().   The "pickle correction" scheme works by 
# pre-loading the FileHeaderGenerator with pickled headers...  which prevents the file from ever being
# accessed (except possibly to update the headers).

class FileHeaderGenerator(HeaderGenerator):
    """Generates lookup parameters and old bestrefs from dataset files."""
    def _header(self, filename):
        """Get the best references recommendations recorded in the header of file `dataset`."""
        if filename not in self.headers:
            self.headers[filename] = data_file.get_free_header(filename, observatory=self.observatory)
        return self.headers[filename]

    def handle_updates(self, all_updates):
        """Write best reference updates back to dataset file headers."""
        super(FileHeaderGenerator, self).handle_updates(all_updates)
        for source in sorted(all_updates):
            updates = all_updates[source]
            if updates:
                log.verbose("-"*120)
                update_file_bestrefs(self.context, source, updates)

# ===================================================================

def update_file_bestrefs(context, dataset, updates):
    """Update the header of `dataset` with best reference recommendations
    `bestrefs` determined by context named `pmap`.
    """
    if not updates:
        return

    version_info = heavy_client.version_info()
    instrument = updates[0].instrument
    prefix = utils.instrument_to_locator(instrument).get_env_prefix(instrument)
    with data_file.fits_open(dataset, mode="update", do_not_scale_image_data=True) as hdulist:

        def set_key(keyword, value):
            log.verbose("Setting", repr(dataset), keyword, "=", value)
            hdulist[0].header[keyword] = value

        set_key("CRDS_CTX", context)
        set_key("CRDS_VER", version_info)

        for update in sorted(updates):
            new_ref = update.new_reference.upper()
            if new_ref != "N/A":
                new_ref = (prefix + new_ref).lower()
            set_key(update.filekind.upper(), new_ref)

        for hdu in hdulist:
            hdu.data

# ===================================================================

class DatasetHeaderGenerator(HeaderGenerator):
    """Generates lookup parameters and historical best references from dataset ids.   Server/DB bases"""
    def __init__(self, context, datasets, datasets_since):
        """"Contact the CRDS server and get headers for the list of `datasets` ids with respect to `context`."""
        super(DatasetHeaderGenerator, self).__init__(context, datasets, datasets_since)
        server = api.get_crds_server()
        log.info("Dumping dataset parameters from CRDS server at", repr(server), "for", repr(datasets))
        self.headers = api.get_dataset_headers_by_id(context, datasets)
        log.info("Dumped", len(self.headers), "of", len(datasets), "datasets from CRDS server at", repr(server))

        # every command line id should correspond to 1 or more headers
        for source in self.sources:
            if self.matching_two_part_id(source) not in self.headers.keys():
                log.warning("Dataset", repr(source), "isn't represented by downloaded parameters.")

        # Process according to downloaded 2-part ids,  not command line ids.
        self.sources = sorted(self.headers.keys())

    def matching_two_part_id(self, source):
        """Convert any command line dataset id into it's matching two part id.
        
        matching_two_part_id(<association>)                  -->  <association>  : <first_member>

        matching_two_part_id(<association>:<member>)         -->  <association>  : <member>
        matching_two_part_id(<unassociated>)                 -->  <unassociated> : <unassociated>
        matching_two_part_id(<unassociated>:<unassociated>)  -->  <unassociated> : <unassociated>
        """
        parts = source.split(":")
        assert 1 <= len(parts) <= 2, "Invalid dataset id " + repr(source)
        try:    # when specifying datasets with 1-part id, return first of "associated ids"
                # when specifying datasets with 2-part id,
            if len(parts) == 1:
                return sorted(dataset_id for dataset_id in self.headers if parts[0] in dataset_id)[0]
            else:
                return source
        except:
            return source
    
class InstrumentHeaderGenerator(HeaderGenerator):
    """Generates lookup parameters and historical best references from a list of instrument names.  Server/DB based."""
    def __init__(self, context, instruments, datasets_since, save_pickles, server_info):
        """"Contact the CRDS server and get headers for the list of `instruments` names with respect to `context`."""
        super(InstrumentHeaderGenerator, self).__init__(context, [], datasets_since)
        self.instruments = instruments
        self.sources = self.determine_source_ids()
        self.save_pickles = save_pickles
        try:
            self.segment_size = server_info.max_headers_per_rpc
        except:
            self.segment_size = 5000
            
    def determine_source_ids(self):
        """Return the dataset ids for all instruments."""
        server = api.get_crds_server()
        source_ids = []
        for instrument in self.instruments:
            since_date = self.datasets_since(instrument)
            if since_date:
                log.info("Dumping dataset parameters for", repr(instrument), "from CRDS server at", repr(server),
                         "since", repr(since_date))
            else:
                log.info("Dumping dataset parameters for", repr(instrument), "from CRDS server at", repr(server))
            instr_ids = api.get_dataset_ids(self.context, instrument, self.datasets_since(instrument))
            log.info("Downloaded ", len(instr_ids), "dataset ids for", repr(instrument), "since", repr(since_date)) 
            source_ids.extend(instr_ids)
        return source_ids
    
    def _header(self, source):
        """Return the header associated with dataset id `source`,  fetching the surround segment of
        headers if `source` is not already in the cached set of headers.
        """
        if source not in self.headers:
            self.fetch_source_segment(source)
        return self.headers[source]

    def fetch_source_segment(self, source):
        """Return the segment of dataset ids which surrounds id `source`."""
        try:
            index = self.sources.index(source) // self.segment_size
        except ValueError:
            raise CrdsError("Unknown dataset id " + repr(source))
        lower = index * self.segment_size
        upper = (index +1) * self.segment_size
        segment_ids = self.sources[lower:upper]
        log.verbose("Dumping", len(segment_ids), "datasets from indices", lower, "to", 
                    lower + len(segment_ids), verbosity=20)
        dumped_headers = api.get_dataset_headers_by_id(self.context, segment_ids)
        log.verbose("Dumped", len(dumped_headers), "datasets", verbosity=20)
        if self.save_pickles:  #  keep all headers,  causes memory problems with multiple instruments on ~8G ram.
            self.headers.update(dumped_headers)
        else:  # conserve memory by keeping only the last N headers
            self.headers = dumped_headers

class PickleHeaderGenerator(HeaderGenerator):
    """Generates lookup parameters and historical best references from a list of pickle files (or .json files)
    using successive updates to sets of header dictionaries.  Trailing pickles override leading pickles.
    """
    def __init__(self, context, pickles, datasets_since, only_ids=None):
        """"Contact the CRDS server and get headers for the list of `datasets` ids with respect to `context`."""
        super(PickleHeaderGenerator, self).__init__(context, pickles, datasets_since)
        for pickle in pickles:
            log.info("Loading file", repr(pickle))
            pick_headers = self.load_headers(pickle)
            if not self.headers:
                log.info("Loaded", len(pick_headers), "datasets from file", repr(pickle), 
                         "completely replacing existing headers.")
                self.headers.update(pick_headers)   # replace all of dataset_id
            else:  # OPUS bestrefs don't include original matching parameters,  so full replacement doesn't work.
                log.info("Loaded", len(pick_headers), "datasets from file", repr(pickle), 
                         "augmenting existing headers.")
                self.update_headers(pick_headers, only_ids=only_ids)
        self.sources = only_ids or self.headers.keys()
    
    def load_headers(self, path):
        """Given `path` to a serialization file,  load  {dataset_id : header, ...}.  Supports .pkl and .json"""
        
        if path.endswith(".json"):
            headers = {}
            try:
                with open(path, "r") as pick:
                    for line in pick:
                        headers.update(json.loads(line))
            except ValueError:
                with open(path, "r") as pick:
                    headers = json.load(pick)
        elif path.endswith(".pkl"):
            with open(path, "rb") as pick:
                headers = pickle.load(pick)
        else:
            raise ValueError("Valid serialization formats are .json and .pkl")
        return headers

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
* Determines best references with respect to a context or contexts.   
* Optionally compares new results to prior results.
* Optionally prints source data names affected by the new context.
* Optionally updates the headers of file-based data with new recommendations.
    """
    
    epilog = """
Bestrefs has a number of command line parameters which make it operate in different modes. 

...........
New Context
...........

crds.bestrefs always computes best references with respect to a context which can be explicitly specified with the 
--new-context parameter.    If --new-context is not specified,  the default operational context is determined by 
consulting the CRDS server or looking in the local cache.  

........................
Lookup Parameter Sources
........................

The two primary modes for bestrefs involve the source of reference file matching parameters.   Conceptually 
lookup parameters are always associated with particular datasets and used to identify the references
required to process those datasets.

The options --files, --datasets, --instruments, and --all-instruments determine the source of lookup parameters:

1. To find best references for a list of files do something like this:

    % python -m crds.bestrefs --new-context hst.pmap --files j8bt05njq_raw.fits j8bt06o6q_raw.fits j8bt09jcq_raw.fits

the first parameter, hst.pmap,  is the context with respect to which best references are determined.

2. To find best references for a list of catalog dataset ids do something like this:

    % python -m crds.bestrefs --new-context hst.pmap --datasets j8bt05njq j8bt06o6q j8bt09jcq

3. To do mass scale testing for all cataloged datasets for a particular instrument(s) do:

    % python -m crds.bestrefs --new-context hst.pmap --instruments acs

4. To do mass scale testing for all supported instruments for all cataloged datasets do:

    % python -m crds.bestrefs --new-context hst.pmap --all-instruments
    
    or to test for differences between two contexts

    % python -m crds.bestrefs --new-context hst_0002.pmap --old-context hst_0001.pmap --all-instruments

................
Comparison Modes
................

The --old-context and --compare-source-bestrefs parameters define the best references comparison mode.  Each names
the origin of a set of prior recommendations and implicitly requests a comparison to the recommendations from 
the newly computed bestrefs determined by --new-context.

    Context-to-Context
    ::::::::::::::::::
    
    --old-context can be used to specify a second context for which bestrefs are dynamically computed; --old-context 
    implies that a bestrefs comparison will be made with --new-context.   If --old-context is not specified,  it 
    defaults to None.
    
    Prior Source Recommendations
    ::::::::::::::::::::::::::::
    
    --compare-source-bestrefs requests that the bestrefs from --new-context be compared to the bestrefs which are
    recorded with the lookup parameter data,  either in the file headers of data files,  or in the catalog.   In both
    cases the prior best references are recorded static values,  not dynamically computed bestrefs.
    
............
Output Modes
............

crds.bestrefs supports several output modes for bestrefs and comparison results to standard out.

If --print-affected is specified,  crds.bestrefs will print out the name of any file for which at least one update for
one reference type was recommended.   This is essentially a list of files to be reprocessed with new references.

    % python -m crds.bestrefs --new-context hst.pmap --files j8bt05njq_raw.fits j8bt06o6q_raw.fits j8bt09jcq_raw.fits \\
        --compare-source-bestrefs --print-affected
    j8bt05njq_raw.fits
    j8bt06o6q_raw.fits
    j8bt09jcq_raw.fits
    
............
Update Modes
............

crds.bestrefs initially supports one mode for updating the best reference recommendations recorded in data files:

    % python -m crds.bestrefs --new-context hst.pmap --files j8bt05njq_raw.fits j8bt06o6q_raw.fits j8bt09jcq_raw.fits \\
        --compare-source-bestrefs --update-bestrefs

.........
Verbosity
.........

crds.bestrefs has --verbose and --verbosity=N parameters which can increase the amount of informational 
and debug output.

    """
    
    def __init__(self, *args, **keys):
        cmdline.Script.__init__(self, *args, **keys)

        if self.args.compare_cdbs:
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
        
        config.ALLOW_BAD_RULES.set(self.args.allow_bad_rules)
        config.ALLOW_BAD_REFERENCES.set(self.args.allow_bad_references)

        cmdline.UniqueErrorsMixin.__init__(self, *args, **keys)
            
        self.updates = OrderedDict()  # map of reference updates
        self.failed_updates = OrderedDict()  # map of datasets to failure pseudo-update-tuples
        self.process_filekinds = [typ.lower() for typ in self.args.types ]    # list of filekind str's
        self.skip_filekinds = [typ.lower() for typ in self.args.skip_types]
        self.affected_instruments = None
        
        # See also complex_init()
        self.new_context = None     # Mapping filename
        self.old_context = None     # Mapping filename
        
        # headers corresponding to the new context
        self.new_headers = None     # HeaderGenerator subclass
        
        # comparison variables
        self.compare_prior = None       # bool
        self.old_headers = None         # HeaderGenerator subclass,  comparison context
        self.old_bestrefs_name = None   # info str identifying comparison results source,  .pmap filename or text
        
        self.pickle_headers = None  # any headers loaded from pickle files
        
        if self.args.remote_bestrefs:
            os.environ["CRDS_MODE"] = "remote"
            
        self.datasets_since = self.args.datasets_since

        self.synced_references = set()
    
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
            if (self.args.datasets_since=="auto" and
                (differ.header_modified() or differ.files_deleted())):
                log.info("Checking all dates due to header changes or file deletions.")
                self.args.datasets_since = MIN_DATE
        elif self.args.instruments:
            self.instruments = self.args.instruments
        elif self.args.all_instruments:
            instruments = list(self.obs_pkg.INSTRUMENTS)
            instruments.remove("all")
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
            log.info("No file header updates requested;  dry run.")
        return True

    def auto_datasets_since(self):
        """Support --datasets-since="auto" and compute min EXPTIME for all references determined by diffs.
        
        Returns { instrument: EXPTIME, ... }
        """
        datasets_since = {}
        self.oldctx = rmap.get_cached_mapping(self.old_context)
        self.newctx = rmap.get_cached_mapping(self.new_context)
        for instrument in self.oldctx.selections:
            old_imap = self.oldctx.get_imap(instrument)
            new_imap = self.newctx.get_imap(instrument)
            added_references = diff.get_added_references(old_imap, new_imap)
            deleted_references = diff.get_deleted_references(old_imap, new_imap)
            added_exp_time = deleted_exp_time = MAX_DATE
            if added_references:
                added_exp_time = matches.get_minimum_exptime(new_imap.name, added_references)
            if deleted_references:
                deleted_exp_time = matches.get_minimum_exptime(old_imap.name, deleted_references)
            exp_time = min(added_exp_time, deleted_exp_time)
            if exp_time != MAX_DATE: # if a USEAFTER min found,  remember it.
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
        
        self.add_argument("-c", "--compare-source-bestrefs", dest="compare_source_bestrefs", action="store_true",
            help="Compare new bestrefs recommendations to recommendations from data source,  files or database.")
        
        self.add_argument("-f", "--files", nargs="+", metavar="FILES", default=None,
            help="Dataset files to compute best references for.")
        
        self.add_argument("-d", "--datasets", nargs="+", metavar="IDs", default=None,
            help="Dataset ids to consult database for matching parameters and old results.")
        
        self.add_argument("--all-instruments", action="store_true", default=None,
            help="Compute best references for cataloged datasets for all supported instruments in database.")
        
        self.add_argument("-i", "--instruments", nargs="+", metavar="INSTRUMENTS", default=None,
            help="Instruments to compute best references for, all historical datasets in database.")
        
        self.add_argument("-t", "--types", nargs="+",  metavar="REFERENCE_TYPES",  default=(),
            help="A list of reference types to process,  defaulting to all types.")
        
        self.add_argument("-k", "--skip-types", nargs="+",  metavar="SKIPPED_REFERENCE_TYPES",  default=(),
            help="A list of reference types which should not be processed,  defaulting to nothing.")
        
        self.add_argument("--diffs-only", action="store_true", default=None,
            help="For context-to-context comparison, choose only instruments and types from context differences.")

        self.add_argument("--datasets-since", default=None, type=reformat_date_or_auto,
            help="Cut-off date for datasets, none earlier than this.  Use 'auto' to exploit reference USEAFTER.")
        
        self.add_argument("-p", "--load-pickles", nargs="*", default=None,
            help="Load dataset headers and prior bestrefs from pickle files,  in worst-to-best update order.  Can also load .json files.")
        
        self.add_argument("-a", "--save-pickle", default=None,
            help="Write out the combined dataset headers to the specified pickle file.  Can also store .json file.")
        
        self.add_argument("--update-pickle", action="store_true",
            help="Replace source bestrefs with CRDS bestrefs in output pickle.  For setting up regression tests.")        
        
        self.add_argument("--only-ids", nargs="*", default=None, dest="only_ids", metavar="IDS",
            help="If specified, process only the listed dataset ids.")
        
        self.add_argument("-u", "--update-bestrefs",  dest="update_bestrefs", action="store_true", 
            help="Update sources with new best reference recommendations.")
                    
        self.add_argument("--print-affected", dest="print_affected", action="store_true",
            help="Print names of products for which the new context would assign new references for some exposure.")
    
        self.add_argument("--print-affected-details", action="store_true",
            help="Include instrument and affected types in addition to compound names of affected exposures.")
        
        self.add_argument("--skip-failure-effects", action="store_true",
            help="If bestrefs fail, don't include those dataset ids in the list of affected products.")        
    
        self.add_argument("--print-new-references", action="store_true",
            help="Prints one line per reference file change.  If no comparison requested,  prints all bestrefs.")
    
        self.add_argument("--print-update-counts", action="store_true",
            help="Prints dictionary of update counts by instrument and type,  status on updated files.")
    
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
        
        self.add_argument("-e", "--bad-files-are-errors", action="store_true",
            help="DEPRECATED / default;  Recommendations of known bad/invalid files are errors, not warnings.  Use --allow-bad-... to override.")
        
        self.add_argument("--undefined-differences-matter", action="store_true",
            help="If not set, a transition from UNDEFINED to anything else is not considered a difference error.")
        
        self.add_argument("--na-differences-matter", action="store_true",
            help="If not set,  either CDBS or CRDS recommending N/A is OK to mismatch.")
        
        self.add_argument("--compare-cdbs", action="store_true",
            help="Abbreviation for --compare-source-bestrefs --differences-are-errors --dump-unique-errors --stats")
        
        self.add_argument("--affected-datasets", action="store_true", 
            help="Abbreviation for --diffs-only --datasets-since=auto --undefined-differences-matter --na-differences-matter --print-update-counts --print-affected --dump-unique-errors --stats")
        
        self.add_argument("-z", "--optimize-tables", action="store_true", 
            help="If set, apply row-based optimizations to screen out inconsequential table updates.")
        
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
        self.warn_bad_context("New-context", new_context)
        self.warn_bad_context("Old-context", old_context)
        if self.server_info.effective_mode != "remote":
            if old_context is not None and not os.path.dirname(old_context):
                self.dump_mappings([old_context])
            if not os.path.dirname(new_context):
                self.dump_mappings([new_context])
        return new_context, old_context
    
    def warn_bad_context(self, name, context):
        """Issue a warning if `context` of named `name` is a known bad file."""
        if context is None:
            return
        # Get subset of bad files contained by this context.
        bad_contained = heavy_client.get_bad_mappings_in_context(self.observatory, context)
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
            new_headers = FileHeaderGenerator(context, self.files, datasets_since)
            # log.info("Computing bestrefs for dataset files", self.args.files)
        elif self.args.datasets:
            self.require_server_connection()
            new_headers = DatasetHeaderGenerator(context, [dset.upper() for dset in self.args.datasets], datasets_since)
            log.info("Computing bestrefs for datasets", repr(self.args.datasets))
        elif self.instruments:
            self.require_server_connection()
            log.info("Computing bestrefs for db datasets for", repr(self.instruments))
            if self.args.save_pickle and len(self.instruments) > 1:
                log.warning("--save-pickle with multiple instruments may require > 8G ram.")
            new_headers = InstrumentHeaderGenerator(context, self.instruments, datasets_since, self.args.save_pickle, self.server_info)
        elif self.args.load_pickles:
            # log.info("Computing bestrefs solely from pickle files:", repr(self.args.load_pickles))
            new_headers = {}
        else:
            log.error("Invalid header source configuration.   "
                               "Specify --files, --datasets, --instruments, --all-instruments, or --load-pickles.")
            self.print_help()
            sys.exit(-1)
        if self.args.load_pickles:
            self.pickle_headers = PickleHeaderGenerator(context, self.args.load_pickles, only_ids=self.args.only_ids, 
                                                        datasets_since=datasets_since)
            if new_headers:   # combine partial correction headers field-by-field 
                new_headers.update_headers(self.pickle_headers.headers, only_ids=self.args.only_ids)
            else:   # assume pickles-only sources are all complete snapshots
                new_headers = self.pickle_headers
        return new_headers
        
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
            for dataset in self.new_headers:
                if self.args.only_ids and dataset not in self.args.only_ids:
                    log.verbose("Skipping", repr(dataset), "not in --only-ids", verbosity=80)
                    continue
                updates, failed_updates = self.process(dataset)
                if updates:
                    self.updates[dataset] = updates
                if failed_updates:
                    self.failed_updates[dataset] = failed_updates
            self.post_processing()
        self.report_stats()
        log.verbose(self.get_stat("datasets"), "sources processed", verbosity=30)
        log.verbose(len(self.updates), "source updates", verbosity=30)
        log.standard_status()
        return log.errors()

    def process(self, dataset):
        """Process best references for `dataset`,  printing dataset output,  collecting stats, trapping exceptions."""
        with log.error_on_exception("Failed processing", repr(dataset)):
            log.verbose("="*120)
            if self.args.files:
                log.info("===> Processing", dataset)     # file mode
            else:
                log.verbose("===> Processing", dataset, verbosity=25)   # database or regression modes
            self.increment_stat("datasets", 1)
            return self._process(dataset)
        return None, None

    def _process(self, dataset):
        """Core best references,  add to update tuples."""
        new_header = self.new_headers.get_lookup_parameters(dataset)
        instrument = utils.header_to_instrument(new_header)
        new_bestrefs = self.get_bestrefs(instrument, dataset, self.new_context, new_header)
        if self.compare_prior:
            if self.args.old_context:
                old_header = self.old_headers.get_lookup_parameters(dataset)
                old_bestrefs = self.get_bestrefs(instrument, dataset, self.old_context, old_header)
            else:
                old_bestrefs = self.old_headers.get_old_bestrefs(dataset)
            updates, failed_updates = self.compare_bestrefs(instrument, dataset, new_bestrefs, old_bestrefs)
            if self.args.optimize_tables:
                updates = self.optimize_tables(dataset, updates)
        else:
            updates, failed_updates = self.screen_bestrefs(instrument, dataset, new_bestrefs), []
        if self.args.update_pickle:  # XXXXX mutating input bestrefs to support updated pickles
            self.new_headers.update_headers( { dataset : new_bestrefs })
        return updates, failed_updates
    
    def get_bestrefs(self, instrument, dataset, context, header):
        """Compute the bestrefs for `dataset` with respect to loaded mapping/context `ctx`."""
        with log.augment_exception("Failed computing bestrefs for data", repr(dataset), 
                                    "with respect to", repr(context)):
            types = self.process_filekinds if not self.affected_instruments else self.affected_instruments[instrument.lower()]
            bestrefs = crds.getrecommendations(
                header, reftypes=types, context=context, observatory=self.observatory, fast=log.get_verbose() < 50)
        return { key.upper() : value for (key, value) in bestrefs.items() }
        
    @property
    def update_promise(self):
        """Return a string identifying that and update would or will occurr, depending on --update-bestrefs."""
        if self.args.update_bestrefs:
            return ":: Updating."
        else:
            return ":: Would update."
        
    no_update = ":: No update."
    
    def screen_bestrefs(self, instrument, dataset, newrefs):
        """Scan best references dict `newrefs` for atypical results and issue errors and warnings.

        Returns [UpdateTuple(), ...]
        """
    
        # XXX  This is closely related to compare_bestrefs, maintain both!!   See also update_bestrefs()
    
        log.verbose("-"*120, verbosity=55)

        updates = []
        
        for filekind in sorted(self.process_filekinds or newrefs):

            filekind = filekind.lower()
            
            if filekind in self.skip_filekinds:
                log.verbose(self.format_prefix(dataset, instrument, filekind), 
                            "Skipping type.", verbosity=55)
                continue

            new_ok, _new_org, new = self.handle_na_and_not_found("New:", newrefs, dataset, instrument, filekind, 
                                                       ("NOT FOUND NO MATCH","UNDEFINED"))
            if new_ok:
                log.verbose(self.format_prefix(dataset, instrument, filekind), 
                            "Bestref FOUND:", repr(new).lower(),  self.update_promise, verbosity=30)
                updates.append(UpdateTuple(instrument, filekind, None, new))
            
                self._add_synced_reference(new)

        return updates
    
    def compare_bestrefs(self, instrument, dataset, newrefs, oldrefs):
        """Compare best references dicts `newrefs` and `oldrefs` for `instrument` and `dataset`.
        
        Returns [UpdateTuple(), ...]
        """
    
        # XXX  This is closely related to screen_bestrefs,  maintain both!!    See also update_bestrefs()
    
        log.verbose("-"*120, verbosity=55)

        updates = []
        failed_updates = []
        
        for filekind in sorted(self.process_filekinds or newrefs):

            filekind = filekind.lower()
            
            if filekind in self.skip_filekinds:
                log.verbose(self.format_prefix(dataset, instrument, filekind), 
                            "Skipping type.", verbosity=55)
                continue
            
            old_ok, old_org, old = self.handle_na_and_not_found("Old:", oldrefs, dataset, instrument, filekind, 
                                                        ("NOT FOUND NO MATCH",)) # omit UNDEFINED for useless update check.
            new_ok, new_org, new = self.handle_na_and_not_found("New:", newrefs, dataset, instrument, filekind, 
                                                       ("NOT FOUND NO MATCH","UNDEFINED"))
            if not new_ok or not old_ok:
                failed_updates.append(UpdateTuple(instrument, filekind, old_org, new_org))
                continue
            
            self._add_synced_reference(new)

            if old == "UNDEFINED" and new == "N/A" and not self.args.undefined_differences_matter:
                log.verbose(self.format_prefix(dataset, instrument, filekind),
                            "New best reference: 'UNDEFINED' --> 'N/A',  Special case,  useless reprocessing.", 
                            self.no_update, verbosity=30)
                continue

            if new != old:
                if self.args.differences_are_errors:
                    #  By default, either CDBS or CRDS scoring a reference as N/A short circuits mismatch errors.
                    if (old != "N/A" and new != "N/A") or self.args.na_differences_matter:
                        self.log_and_track_error(dataset, instrument, filekind, 
                            "Comparison difference:", repr(old).lower(), "-->", repr(new).lower(), self.update_promise)
                elif self.args.print_new_references or log.get_verbose() >= 30 or self.args.files:
                    log.info(self.format_prefix(dataset, instrument, filekind), 
                             "New best reference:", repr(old).lower(), "-->", repr(new).lower(), self.update_promise)
                updates.append(UpdateTuple(instrument, filekind, old, new))
            else:
                log.verbose(self.format_prefix(dataset, instrument, filekind), 
                            "Lookup MATCHES:", repr(old).lower(), self.no_update,  verbosity=30)
        
        # Check for missing references in `newrefs`.
        for filekind in oldrefs:
            if new_org == "UNDEFINED" and new_org != old_org and filekind in self.process_filekinds:
                if self.args.differences_are_errors:
                    self.log_and_track_error(dataset, instrument, filekind, 
                        "No new reference recommended. Old reference was", repr(old).lower(), self.no_update, verbosity=30)
                else:
                    log.verbose(self.format_prefix(dataset, instrument, filekind), 
                        "No new reference recommended. Old reference was", repr(old).lower(), self.no_update, verbosity=30)            

        return updates, failed_updates

    def handle_na_and_not_found(self, name, bestrefs, dataset, instrument, filekind, na_conversions):
        """Fetch the bestref for `filekind` from `bestrefs`, and handle conversions to N/A
        and CRDS NOT FOUND errors.
        
        `name` is a string identifier for this conversion, Old or New.
        `bestrefs` is a dictionary { filekind : bestref, }
        na_conversions is a tuple of string prefixes which convert the raw bestref to N/A.
        
        Return (ref_ok, raw_ref, ref)  where:
            raw_ref is the original name of the reference,  stripped of any iref$ prefix.
            ref is the fully normalized name of the reference, converted to N/A as needed.
            ref_ok is True IFF bestrefs did not fail altogether.
        """
        ref_org = cleanpath(bestrefs.get(filekind.upper(), "UNDEFINED")).strip()
        ref = ref_org.upper()
        if ref == "N/A" or ref.startswith("NOT FOUND N/A"):
            log.verbose(self.format_prefix(dataset, instrument, filekind),
                        "Bestref is natural N/A.", verbosity=60)
            ref = "N/A"
        elif ref in ("NONE", "", "*"):
            log.verbose(self.format_prefix(dataset, instrument, filekind),
                        "Mapping", repr(ref), "to N/A.", verbosity=60)
            ref = "N/A"
        ref_ok = True
        if ref.startswith(na_conversions):   
            ref = "N/A"
            if self.args.na_differences_matter:  # track these when N/A is being scrutinized, regardless of diff.
                self.log_and_track_error(dataset, instrument, filekind, 
                                         name,  "No match found => 'N/A'.")
            else:
                log.verbose(self.format_prefix(dataset, instrument, filekind),
                            name, "No match found => 'N/A'.")
        elif ref.startswith("NOT FOUND"):
            self.log_and_track_error(dataset, instrument, filekind, 
                                     name, "Bestref FAILED:", ref_org[len("NOT FOUND"):])
            ref_ok = False
        return ref_ok, ref_org, ref

    def _add_synced_reference(self, ref):
        """Add reference `ref` to the set of synced references if it is not a special value."""
        if ref.upper() not in ["N/A", "UNDEFINED"]:
            self.synced_references.add(ref.lower())

    def post_processing(self):
        """Given the computed update list, print out results,  update file headers, and fetch missing references."""

        if self.args.save_pickle:
            self.new_headers.save_pickle(self.args.save_pickle, only_ids=self.args.only_ids)
        
        self.warn_bad_updates()  # Warn about bad file reference updates only, not failures
 
        if self.args.print_new_references:
            self.print_new_references()
        
        if self.args.update_bestrefs:
            log.verbose("Performing best references updates.")
            self.new_headers.handle_updates(self.updates)

        if self.args.sync_references:
            self.sync_references()

        if not self.args.skip_failure_effects:
            self.updates.update(self.failed_updates)
        
        if self.args.print_update_counts:
            self.print_update_stats()   #  For affected datasets,  add back failed dataset updates
        
        if self.args.print_affected:
            self.print_affected()
        
        if self.args.print_affected_details:
            self.print_affected_details()

        self.dump_unique_errors()
        
    def optimize_tables(self, dataset, updates):
        """Drop table updates for which the reference change doesn't matter based upon examining the
        selected rows.
        """
        for update in sorted(updates):
            new_header = self.new_headers.header(dataset)
            if not table_effects.is_reprocessing_required(dataset, new_header, self.old_context, self.new_context, update):
                updates.remove(update) # reprocessing not required, ignore update.
                log.verbose("Removing table update for", update.instrument, update.filekind, dataset, 
                            "no effective change from reference", repr(update.old_reference),
                            "-->", repr(update.new_reference), verbosity=25)
        return updates

    def print_affected(self):
        """Print the product id for any product which has new bestrefs for any
        of its component exposures.   All components share a common product id.
        """
        affected_products = {self.dataset_to_product_id(dataset) 
                                 for dataset in self.updates 
                                 if self.updates[dataset]}
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
        """Print compound ID, instrument, and affected reference types for every exposure with new best references,
        one line per exposure.
        """
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
                
    def sync_references(self):
        """Locally cache the new references referred to by updates."""
        api.dump_references(self.new_context, sorted(self.synced_references), raise_exceptions=self.args.pdb)

# ===================================================================

def cleanpath(name):
    """jref$n4e12510j_crr.fits  --> n4e12510j_crr.fits"""
    return name.split("$")[-1].strip()

# ============================================================================

def main():
    """Construct and run the bestrefs script,  return 1 if errors occurred, 0 otherwise."""
    errors = BestrefsScript()()
    exit_status = int(errors > 0)  # no errors = 0,  errors = 1
    return exit_status

if __name__ == "__main__":
    sys.exit(main())

