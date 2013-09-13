"""This module is a command line script which handles comparing the best
reference recommendations for a particular context and dataset files.

For more details on the several modes of operations and command line parameters browse the source or run:   

% python -m crds.bestrefs --help
"""
import sys
import os
from collections import namedtuple
import cPickle
import gc

import pyfits

import crds
from crds import (log, rmap, data_file, utils, cmdline, CrdsError)
from crds.client import api

# ===================================================================

UpdateTuple = namedtuple("UpdateTuple", ["instrument", "filekind", "old_reference", "new_reference"])

class UnsupportedUpdateMode(CrdsError):
    """Database modes don't currently support updating best references recommendations on the server."""

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
    def __init__(self, context, sources):
        self.context = context
        self.sources = sources
        self.pmap = rmap.get_cached_mapping(context)
        self.headers = {}

    def __iter__(self):
        return iter(self.sources)
    
    def header(self, source):
        """Return the full header corresponding to `source`.   Source is a dataset id or filename."""
        return self.headers[source]
    
    def get_lookup_parameters(self, source):
        """Return the parameters corresponding to `source` used to drive a best references lookup."""
        try:
            hdr = self.header(source)
            min_hdr = self.pmap.minimize_header(hdr)
            min_hdr = { key.upper():utils.condition_value(val) for (key, val) in min_hdr.items() }
            log.verbose("Bestref parameters for", repr(source), "with respect to", 
                        repr(self.context), "=", log.PP(min_hdr))
            return min_hdr
        except Exception, exc:
            raise crds.CrdsError("Failed getting lookup parameters for data '{}' with respect to '{}' : {}" .format(
                                 source, self.context, str(exc)))            

    def get_old_bestrefs(self, source):
        """Return the historical best references corresponding to `source`."""
        hdr = self.header(source)
        filekinds = self.pmap.get_filekinds(hdr) #  XXX only includes filekinds in .pmap
        old_bestrefs = { key.lower(): val for (key, val) in hdr.items() if key.upper() in filekinds }
        log.verbose("Old best reference recommendations from", repr(source), "=", log.PP(old_bestrefs))
        return old_bestrefs
    
    def handle_updates(self, updates):
        """In general,  reject request to update best references on the source."""
        raise UnsupportedUpdateMode("This dataset access mode doesn't support updates.")
    
    def save_pickle(self, pickle):
        """Write out headers to `pickle` file."""
        log.info("Writing all headers to", repr(pickle))
        with open(pickle, "wb+") as pick:
            cPickle.dump(self.headers, pick)
        log.info("Done writing", repr(pickle))
            
    def update_headers(self, headers2):
        """Incorporate `headers2` updated values into `self.headers`.  Since `headers2` may be incomplete,
        do param-by-param update.   Nominally,  this is to add OPUS bestrefs corrections (definitive) to DADSOPS
        database bestrefs (fast but not definitive).
        """
        # Munge for consistent case and value formatting regardless of source
        headers2 = { dataset_id.upper() : 
                        { key.upper():utils.condition_value(val) for (key,val) in headers2[dataset_id].items() } 
                        for dataset_id in headers2 }

        # replace param-by-param,  not id-by-id, since headers2[id] may be partial
        for dataset_id in headers2:
            if dataset_id in self.headers:
                log.verbose("For", repr(dataset_id), "updating", log.PP(self.headers[dataset_id]), 
                            "with corrections", log.PP(headers2[dataset_id]), verbosity=100)
                self.headers[dataset_id].update(headers2[dataset_id])   

# FileHeaderGenerator uses a deferred header loading scheme which incrementally reads each header
# from a file as processing is going on via header().   The "pickle correction" scheme works by 
# pre-loading the FileHeaderGenerator with pickled headers...  which prevents the file from ever being
# accessed (except possibly to update the headers).

class FileHeaderGenerator(HeaderGenerator):
    """Generates lookup parameters and old bestrefs from dataset files."""
    def header(self, filename):
        """Get the best references recommendations recorded in the header of file `dataset`."""
        if filename not in self.headers:
            self.headers[filename] = data_file.get_header(filename, observatory=self.pmap.observatory)
        return self.headers[filename]

    def handle_updates(self, all_updates):
        """Write best reference updates back to dataset file headers."""
        for source in all_updates:
            updates = all_updates[source]
            if updates:
                log.verbose("Updating data", repr(source), "==>", repr(updates), verbosity=25)
                update_file_bestrefs(self.pmap, source, updates)

class DatasetHeaderGenerator(HeaderGenerator):
    """Generates lookup parameters and historical best references from dataset ids.   Server/DB bases"""
    def __init__(self, context, datasets):
        """"Contact the CRDS server and get headers for the list of `datasets` ids with respect to `context`."""
        super(DatasetHeaderGenerator, self).__init__(context, datasets)
        server = api.get_crds_server()
        log.info("Dumping dataset parameters from CRDS server at", repr(server), "for", repr(datasets))
        self.headers = api.get_dataset_headers_by_id(context, datasets)
        log.info("Dumped", len(self.headers), "of", len(datasets), "datasets from CRDS server at", repr(server))
    
class InstrumentHeaderGenerator(HeaderGenerator):
    """Generates lookup parameters and historical best references from a list of instrument names.  Server/DB based."""
    def __init__(self, context, instruments):
        """"Contact the CRDS server and get headers for the list of `instruments` names with respect to `context`."""
        super(InstrumentHeaderGenerator, self).__init__(context, instruments)
        server = api.get_crds_server()
        self.instruments = instruments
        sorted_sources = []
        for instrument in instruments:
            log.info("Dumping dataset parameters for", repr(instrument), "from CRDS server at", repr(server))
            more = api.get_dataset_headers_by_instrument(context, instrument)
            log.info("Dumped", len(more), "datasets for", repr(instrument), "from CRDS server at", repr(server))
            self.headers.update(more)
            sorted_sources.extend(sorted(more.keys()))
        self.sources = sorted_sources

class PickleHeaderGenerator(HeaderGenerator):
    """Generates lookup parameters and historical best references from a list of pickle files
    using successive updates to sets of header dictionaries.  Trailing pickles override leading pickles.
    """
    def __init__(self, context, pickles):
        """"Contact the CRDS server and get headers for the list of `datasets` ids with respect to `context`."""
        super(PickleHeaderGenerator, self).__init__(context, pickles)
        for pickle in pickles:
            log.info("Loading pickle file", repr(pickle))
            with open(pickle, "rb") as pick:
                pick_headers = cPickle.load(pick)
                if not self.headers:
                    log.info("Loaded", len(pick_headers), "datasets from pickle", repr(pickle), 
                             "completely replacing existing pickles.")
                    self.headers.update(pick_headers)   # replace all of dataset_id
                else:  # OPUS bestrefs don't include original matching parameters,  so full replacement doesn't work.
                    log.info("Loaded", len(pick_headers), "datasets from pickle", repr(pickle), 
                             "augmenting existing pickles.")
                    self.update_headers(pick_headers)
        self.sources = self.headers.keys()
    
# ===================================================================

def update_file_bestrefs(pmap, dataset, updates):
    """Update the header of `dataset` with best reference recommendations
    `bestrefs` determined by context named `pmap`.
    """
    pmap = rmap.asmapping(pmap)
    # XXX TODO switch pyfits.setval to data_file.setval if a data model equivalent
    # is defined for CRDS_CTX
    
    # Here we use the dataset file because we know we have the full path, 
    # whereas the reference we'd have to locate.
    instrument = utils.file_to_instrument(dataset)
    prefix = pmap.locate.get_env_prefix(instrument)    
    log.verbose("Setting", repr(dataset), "CRDS_CTX =", repr(pmap.name))
    pyfits.setval(dataset, "CRDS_CTX", value=pmap.basename, ext=0)
    for update in sorted(updates):
        new_ref = update.new_reference.upper()
        if new_ref != "N/A":
            new_ref = (prefix + new_ref).lower()
        log.verbose("Setting", repr(dataset), update.filekind.upper(), "=", repr(new_ref))
        pyfits.setval(dataset, update.filekind, value=new_ref, ext=0)            

# ============================================================================

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
                
        cmdline.UniqueErrorsMixin.__init__(self, *args, **keys)
            
        self.updates = {}                  # map of reference updates
        self.process_filekinds = [typ.lower() for typ in self.args.types ]    # list of filekind str's
        
        # See also complex_init()
        self.new_context = None     # Mapping filename
        self.old_context = None     # Mapping filename
        self.newctx = None          # loaded Mapping
        self.oldctx = None          # loaded Mapping
        
        # headers corresponding to the new context
        self.new_headers = None     # HeaderGenerator subclass
        
        # comparison variables
        self.compare_prior = None       # bool
        self.old_headers = None         # HeaderGenerator subclass,  comparison context
        self.old_bestrefs_name = None   # info str identifying comparison results source,  .pmap filename or text
        
        self.pickle_headers = None  # any headers loaded from pickle files
        
        self.sources_processed = 0     # datasets actually processed,  particulary when restricted by id

        if self.args.remote_bestrefs:
            os.environ["CRDS_MODE"] = "remote"
    
    def complex_init(self):
        """Complex init tasks run inside any --pdb environment,  also unfortunately --profile."""
        
        self.new_context, self.old_context, self.newctx, self.oldctx = self.setup_contexts()
        
        # headers corresponding to the new context
        self.new_headers = self.init_headers(self.new_context)

        self.compare_prior, self.old_headers, self.old_bestrefs_name = self.init_comparison()
                
    def add_args(self):
        """Add bestrefs script-specific command line parameters."""
        
        self.add_argument("-n", "--new-context", dest="new_context", 
            help="Compute the updated best references using this context. "
                 "Uses current operational context by default.",
            default=None, type=cmdline.mapping_spec)
        
        self.add_argument("-o", "--old-context", dest="old_context",
            help="Compare bestrefs recommendations from two contexts.", 
            metavar="OLD_CONTEXT", default=None, type=cmdline.mapping_spec)
        
        self.add_argument("-c", "--compare-source-bestrefs", dest="compare_source_bestrefs", action="store_true",
            help="Compare new bestrefs recommendations to recommendations from data source,  files or database.")
        
        self.add_argument("-f", "--files", nargs="+", metavar="FILES", default=None,
            help="Dataset files to compute best references for.")
        
        self.add_argument("-d", "--datasets", nargs="+", metavar="IDs", default=None,
            help="Dataset ids to consult database for matching parameters and old results.")
        
        self.add_argument("-i", "--instruments", nargs="+", metavar="INSTRUMENTS", default=None,
            help="Instruments to compute best references for, all historical datasets in database.")
        
        self.add_argument("--all-instruments", action="store_true", default=None,
            help="Compute best references for cataloged datasets for all supported instruments in database.")
        
        self.add_argument("-p", "--load-pickles", nargs="*", default=None,
            help="Load dataset headers and prior bestrefs from pickle files,  in worst-to-best update order.")
        
        self.add_argument("-a", "--save-pickle", default=None,
            help="Write out the combined dataset headers to the specified pickle file.")
        
        self.add_argument("--only-ids", nargs="*", default=None, dest="only_ids", metavar="IDS",
            help="If specified, process only the listed dataset ids.")
        
        self.add_argument("-t", "--types", nargs="+",  metavar="REFERENCE_TYPES",  default=(),
            help="A list of reference types to process,  defaulting to all types.")
        
        self.add_argument("-u", "--update-bestrefs",  dest="update_bestrefs",
            help="Update dataset headers with new best reference recommendations.", 
            action="store_true")
        
        self.add_argument("--print-affected",
            help="Print names of data sets for which the new context would assign new references.",
            action="store_true")
    
        self.add_argument("--print-new-references",
            help="Prints messages detailing each reference file change.   If no comparison "
                "was requested,  prints all best references.",
            action="store_true")
    
        self.add_argument("-r", "--remote-bestrefs",
            help="Compute best references on CRDS server,  convenience for env var CRDS_MODE='remote'",
            action="store_true")
        
        self.add_argument("-s", "--sync-references", action="store_true",
            help="Fetch the refefences recommended by new context to the local cache.")
        
        self.add_argument("--differences-are-errors", action="store_true",
            help="Treat recommendation differences between new context and original source as errors.")
        
        self.add_argument("--na-differences-matter", action="store_true",
            help="If not set,  either CDBS or CRDS scoring reference type as N/A is OK to mismatch.")
        
        self.add_argument("--compare-cdbs", action="store_true",
            help="Abbreviation for --compare-source-bestrefs --differences-are-errors --dump-unique-errors --stats")
        
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
        self.sync_context(new_context)
        if self.args.old_context is not None:
            log.verbose("Using explicit old context", repr(self.args.old_context), verbosity=25)
            old_context = self.resolve_context(self.args.old_context)
            self.sync_context(old_context)
        else:
            old_context = None
        newctx = rmap.get_cached_mapping(new_context)
        oldctx = rmap.get_cached_mapping(old_context)  if old_context else None
        return new_context, old_context, newctx, oldctx

    def sync_context(self, context):
        """Recursively cache the new and comparison mappings."""
        if context:
            log.verbose("Syncing context", repr(context), verbosity=25)
            try:
                rmap.get_cached_mapping(context)   # if it loads,  it's cached.
                return
            except IOError:
                try:
                    api.dump_mappings(context)   # otherwise fetch it.
                except Exception, exc:
                    log.error("Failed to download context", repr(context), "from CRDS server", repr(api.get_crds_server()))
                    sys.exit(-1)

    def locate_file(self, filename):
        """Locate a dataset file leaving the path unchanged. Applies to self.args.files"""
        return filename
    
    def init_headers(self, context):
        """Create header a header generator for `context`,  interpreting command line parameters."""
        source_modes = [self.args.files, self.args.datasets, self.args.instruments, 
                        self.args.all_instruments].count(None)
        assert (4 - source_modes <= 1) and (source_modes + int(bool(self.args.load_pickles)) >= 1), \
            "Must specify one and only one of: --files, --datasets, --instruments, --all-instruments, --load-pickles."
        if self.args.files:
            new_headers = FileHeaderGenerator(context, self.args.files)
            # log.info("Computing bestrefs for dataset files", self.args.files)
        elif self.args.datasets:
            self.require_server_connection()
            new_headers = DatasetHeaderGenerator(context, [dset.upper() for dset in self.args.datasets])
            log.info("Computing bestrefs for datasets", repr(self.args.datasets))
        elif self.args.instruments or self.args.all_instruments:
            self.require_server_connection()
            instruments = self.newctx.locate.INSTRUMENTS if self.args.all_instruments else self.args.instruments
            log.info("Computing bestrefs for all cataloged datasets of", repr(instruments))
            new_headers = InstrumentHeaderGenerator(context, instruments)
        elif self.args.load_pickles:
            # log.info("Computing bestrefs solely from pickle files:", repr(self.args.load_pickles))
            new_headers = {}
        else:
            raise RuntimeError("Invalid header source configuration.   "
                               "Specify --files, --datasets, --instruments, --all-instruments, or --load-pickles.")
        if self.args.load_pickles:
            self.pickle_headers = PickleHeaderGenerator(context, self.args.load_pickles)
            if new_headers:   # combine partial correction headers field-by-field 
                new_headers.update_headers(self.pickle_headers.headers)
            else:   # assume pickles-only sources are all complete snapshots
                new_headers = self.pickle_headers
        return new_headers
        
    def init_comparison(self):
        """Interpret command line parameters to determine comparison mode."""
        assert not (self.args.old_context and self.args.compare_source_bestrefs), \
            "Cannot specify both --old-context and --compare-source-bestrefs."
        compare_prior = \
            self.args.old_context or \
            self.args.compare_source_bestrefs or \
            self.args.update_bestrefs or \
            self.args.print_affected 
        old_headers = old_fname = None
        if compare_prior:
            if self.args.old_context:
                # XXXX in old contexts, matching parameters and expected result types might have been different.
                # XXXX for now,  just ensure they're the same,  lesser likelihood of error.
                # old_headers = self.init_headers(self.args.old_context)
                log.verbose_warning("Assuming parameter names and required types are the same across contexts.")
                old_headers = self.new_headers
                old_fname = self.args.old_context
            else:
                old_fname = "recorded bestrefs"
                old_headers = self.new_headers
        return compare_prior, old_headers, old_fname
    
    def main(self):
        """Compute bestrefs for datasets."""
        
        # gc.set_debug(gc.DEBUG_STATS | gc.DEBUG_LEAK)
        
        self.complex_init()   # Finish __init__() inside --pdb
        
        if not self.compare_prior:
            log.info("No comparison context or source comparison requested.")
        if self.args.files and not self.args.update_bestrefs:
            log.info("No file header updates requested;  dry run.")
            
        for i, dataset in enumerate(self.new_headers):
            if i % 5000 == 0:
                gc.collect()
            if self.args.only_ids and dataset not in self.args.only_ids:
                continue
            try:
                if self.args.files:
                    log.info("===> Processing", dataset)
                else:
                    log.verbose("===> Processing", dataset, verbosity=25)
                self.increment_stat("datasets", 1)
                updates = self.process(dataset)
                if updates:
                    self.updates[dataset] = updates
            except Exception, exc:
                if self.args.pdb:
                    raise
                log.error("Failed processing", repr(dataset), ":", str(exc))
                
        self.post_processing()

        self.report_stats()

        log.verbose(self.sources_processed, "sources processed", verbosity=30)
        log.verbose(len(self.updates), "source updates", verbosity=30)
        log.standard_status()
        return log.errors()

    def process(self, dataset):
        """Process best references for `dataset` and return update tuples.     
        returns (dataset, new_context, new_bestrefs) or 
                (dataset, new_context, new_bestrefs, old_context, old_bestrefs)
        """
        self.sources_processed += 1
        new_header = self.new_headers.get_lookup_parameters(dataset)
        instrument = self.newctx.get_instrument(new_header)
        new_bestrefs = self.get_bestrefs(instrument, dataset, self.newctx, new_header)
        if self.compare_prior:
            if self.args.old_context:
                old_header = self.old_headers.get_lookup_parameters(dataset)
                old_bestrefs = self.get_bestrefs(instrument, dataset, self.oldctx, old_header)
            else:
                old_bestrefs = self.old_headers.get_old_bestrefs(dataset)
            updates = self.compare_bestrefs(instrument, dataset, new_bestrefs, old_bestrefs)
        else:
            updates = self.screen_bestrefs(instrument, dataset, new_bestrefs)
        return updates
    
    def get_bestrefs(self, instrument, dataset, ctx, header):
        """Compute the bestrefs for `dataset` with respect to loaded mapping/context `ctx`."""
        try:
            if self.args.remote_bestrefs:
                bestrefs = crds.getrecommendations(header, reftypes=self.process_filekinds, context=ctx.name,
                                                   observatory=self.observatory)
            else:
                bestrefs = ctx.get_best_references(header, include=self.process_filekinds)
        except Exception, exc:
            if self.args.pdb:
                raise
            raise crds.CrdsError("Failed computing bestrefs for data '{}' with respect to '{}' : {}" .format(
                                dataset, ctx.name, str(exc)))
        else:
            log.verbose("Best references for", repr(instrument), "data", repr(dataset), 
                        "with respect to", repr(ctx.name), "=", repr(bestrefs))
            return bestrefs
        
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
    
        updates = []
        
        for filekind in (self.process_filekinds or newrefs):
            
            new_org = cleanpath(newrefs.get(filekind, "UNDEFINED"))
            new = new_org.upper()
            
            if new.startswith("NOT FOUND N/A"):
                log.verbose(self.format_prefix(dataset, instrument, filekind), 
                            "Filetype N/A for dataset.", self.update_promise, verbosity=55)
                new = "N/A"
            elif new.startswith(("NOT FOUND NO MATCH", "UNDEFINED")):
                if self.args.na_differences_matter:  # track these when N/A is being scrutinized, regardless of diff.
                    self.log_and_track_error(dataset, instrument, filekind, 
                        "No CRDS match found => 'N/A'.", self.update_promise)
                else:
                    log.verbose(self.format_prefix(dataset, instrument, filekind),
                        "No CRDS match found => 'N/A'.", self.update_promise)
                new = "N/A"
            elif new.startswith("NOT FOUND"):
                self.log_and_track_error(dataset, instrument, filekind,
                            "Bestref FAILED:", new_org[len("NOT FOUND"):], self.no_update)
                continue
            else:
                log.verbose(self.format_prefix(dataset, instrument, filekind), 
                            "Bestref FOUND:", repr(new_org),  self.update_promise, verbosity=55)
            updates.append(UpdateTuple(instrument, filekind, None, new))

        return updates
    
    def compare_bestrefs(self, instrument, dataset, newrefs, oldrefs):
        """Compare best references dicts `newrefs` and `oldrefs` for `instrument` and `dataset`.
        
        Returns [UpdateTuple(), ...]
        """
    
        # XXX  This is closely related to screen_bestrefs,  maintain both!!    See also update_bestrefs()
    
        updates = []
        
        for filekind in (self.process_filekinds or newrefs):
            
            new_org = cleanpath(newrefs.get(filekind, "UNDEFINED"))
            new = new_org.upper()
            
            old = cleanpath(oldrefs.get(filekind, "UNDEFINED")).strip().upper()
        
            if old in ("N/A", "NONE", "", "*"):
                old = "N/A"
            if new.startswith("NOT FOUND N/A"):
                new = "N/A"
            
            if new.startswith(("NOT FOUND NO MATCH","UNDEFINED")):
                new = "N/A"
                if self.args.na_differences_matter:  # track these when N/A is being scrutinized, regardless of diff.
                    self.log_and_track_error(dataset, instrument, filekind, 
                        "No CRDS match found => 'N/A'.")
                else:
                    log.verbose(self.format_prefix(dataset, instrument, filekind),
                        "No CRDS match found => 'N/A'.")
            elif new.startswith("NOT FOUND"):
                self.log_and_track_error(dataset, instrument, filekind, 
                    "Bestref FAILED:", new_org[len("NOT FOUND"):], self.no_update)
                continue

            if old == "UNDEFINED" and new == "N/A" and not self.args.na_differences_matter:
                log.verbose(self.format_prefix(dataset, instrument, filekind),
                    "New best reference: 'UNDEFINED' --> 'N/A',  Special case,  useless reprocessing.", 
                    self.no_update, verbosity=30)
                continue

            if new != old:
                if self.args.differences_are_errors:
                    #  By default, either CDBS or CRDS scoring a reference as N/A short circuits mismatch errors.
                    if self.args.na_differences_matter or (old != "N/A" and new != "N/A"):
                        self.log_and_track_error(dataset, instrument, filekind, 
                            "Comparison difference:", repr(old), "-->", repr(new), self.update_promise)
                elif self.args.print_new_references or log.get_verbose() or self.args.files:
                    log.info(self.format_prefix(dataset, instrument, filekind), 
                            "New best reference:", repr(old), "-->", repr(new), self.update_promise)
                updates.append(UpdateTuple(instrument, filekind, old, new))
            else:
                log.verbose(self.format_prefix(dataset, instrument, filekind), 
                            "Lookup MATCHES:", repr(old), self.no_update,  verbosity=30)
        
        # Check for missing references in `newrefs`.
        for filekind in oldrefs:
            if filekind not in newrefs and filekind in self.process_filekinds:
                if self.args.differences_are_errors:
                    self.log_and_track_error(dataset, instrument, filekind, 
                        "No new reference recommended. Old reference was", repr(old), self.no_update, verbosity=30)
                else:
                    log.verbose(self.format_prefix(dataset, instrument, filekind), 
                        "No new reference recommended. Old reference was", repr(old), self.no_update, verbosity=30)            

        return updates
    
    def post_processing(self):
        """Given the computed update list, print out results,  update file headers, and fetch missing references."""
        # (dataset, filekind, old, new)
        if self.args.save_pickle:
            self.new_headers.save_pickle(self.args.save_pickle)
        if self.args.print_affected:
            for dataset in self.updates:
                if self.updates[dataset]:
                    print(dataset) 
        if self.args.print_new_references:
            for dataset in self.updates:
                for reftype in self.updates[dataset]:
                    print(dataset.lower() + " " + " ".join([str(val).lower() for val in reftype]))
        if self.args.update_bestrefs:
            log.verbose("Performing best references updates.")
            self.new_headers.handle_updates(self.updates)
        if self.args.sync_references:
            references = [ tup.new_reference.lower() for dataset in self.updates for tup in self.updates[dataset]]
            api.dump_references(self.new_context, references, ignore_cache=self.args.ignore_cache, 
                                raise_exceptions=self.args.pdb)
        self.dump_unique_errors()

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

