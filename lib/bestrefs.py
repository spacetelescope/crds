"""This module is a command line script which handles comparing the best
reference recommendations for a particular context and dataset files.

For more details on the several modes of operations and command line parameters browse the source or run:   

% python -m crds.bestrefs --help
"""

from collections import namedtuple

import pyfits

import crds
from crds import (log, rmap, data_file, utils, cmdline, CrdsError)
from crds.client import api

# ===================================================================

UpdateTuple = namedtuple("UpdateTuple", ["instrument", "filekind", "old_reference", "new_reference"])

class UnsupportedUpdateMode(CrdsError):
    """Database modes don't currently support updating best references recommendations on the server."""

# ===================================================================

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
        hdr = self.header(source)
        min_hdr = self.pmap.minimize_header(hdr)
        min_hdr = { key.upper():utils.condition_value(val) for (key, val) in min_hdr.items() }
        log.verbose("Bestref parameters for", repr(source), "with respect to", repr(self.context), "=", min_hdr)
        return min_hdr

    def get_old_bestrefs(self, source):
        """Return the historical best references corresponding to `source`."""
        hdr = self.header(source)
        filekinds = self.pmap.get_filekinds(hdr) #  XXX only includes filekinds in .pmap
        old_bestrefs = { key.lower(): val for (key, val) in hdr.items() if key.upper() in filekinds }
        log.verbose("Old best reference recommendations from", repr(source), "=", repr(old_bestrefs))
        return hdr, old_bestrefs
    
    def handle_updates(self, updates):
        """In general,  reject request to update best references on the source."""
        raise UnsupportedUpdateMode("This dataset access mode doesn't support updates.")

class FileHeaderGenerator(HeaderGenerator):
    """Generates lookup parameters and old bestrefs from dataset files."""
    @utils.cached
    def header(self, filename):
        """Get the best references recommendations recorded in the header of file `dataset`."""
        return data_file.get_header(filename, observatory=self.pmap.observatory)

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
        log.verbose("Dumping dataset parameters from CRDS server for", repr(datasets), verbosity=25)
        self.headers = api.get_dataset_headers_by_id(context, datasets)
        log.verbose("Dumped", len(self.headers), "of", len(datasets), 
                    "dataset parameters from CRDS server.", verbosity=25)
    
class InstrumentHeaderGenerator(HeaderGenerator):
    """Generates lookup parameters and historical best references from a list of instrument names.  Server/DB based."""
    def __init__(self, context, instruments):
        """"Contact the CRDS server and get headers for the list of `instruments` names with respect to `context`."""
        super(InstrumentHeaderGenerator, self).__init__(context, instruments)
        self.instruments = instruments
        sorted_sources = []
        for instrument in instruments:
            log.verbose("Dumping dataset parameters for", repr(instrument), "from CRDS server.", verbosity=25)
            more = api.get_dataset_headers_by_instrument(context, instrument)
            log.verbose("Dumped", len(more), "dataset parameters for", repr(instrument), 
                        "from CRDS server.", verbosity=25)
            self.headers.update(more)
            sorted_sources.extend(sorted(more.keys()))
        self.sources = sorted_sources

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
    
    pyfits.setval(dataset, "CRDS_CTX", value=pmap.basename, ext=0)
    for update in sorted(updates):
        new_ref = update.new_reference.upper()
#        XXX what to do here for failed startswith("NOT FOUND") lookups?
        if new_ref.startswith("NOT FOUND"):
            if "N/A" in new_ref:
                new_ref = "N/A"
        else:
            new_ref = (prefix + new_ref).lower()
        log.verbose("Setting data", repr(dataset), "type", repr(update.filekind), "=", repr(new_ref))
        pyfits.setval(dataset, update.filekind, value=new_ref, ext=0)            

# ============================================================================

class BestrefsScript(cmdline.Script):
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

The options --files, --datasets, --instruments, and --all determine the source of lookup parameters:

1. To find best references for a list of files do something like this:

    % python -m crds.bestrefs --new-context hst.pmap --files j8bt05njq_raw.fits j8bt06o6q_raw.fits j8bt09jcq_raw.fits

the first parameter, hst.pmap,  is the context with respect to which best references are determined.

2. To find best references for a list of catalog dataset ids do something like this:

    % python -m crds.bestrefs --new-context hst.pmap --datasets j8bt05njq j8bt06o6q j8bt09jcq

3. To do mass scale testing for all cataloged datasets for a particular instrument(s) do:

    % python -m crds.bestrefs --new-context hst.pmap --instruments acs

4. To do mass scale testing for all supported instruments for all cataloged datasets do:

    % python -m crds.bestrefs --new-context hst.pmap --all
    
    or to test for differences between two contexts

    % python -m crds.bestrefs --new-context hst_0002.pmap --old-context hst_0001.pmap --all

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

crds.bestrefs has --verbose and --verbosity=N parameters which can increase the amount of informational and debug output.

    """
    
    def __init__(self, *args, **keys):
        super(BestrefsScript, self).__init__(*args, **keys)
        self.updates = {}
        self.parameter_cache = {}
        self.old_bestrefs_cache = {}
    
        self.process_filekinds = [typ.lower() for typ in self.args.types ]
    
        # do one time startup outside profiler.
        self.new_context, self.newctx, self.oldctx = self.setup_contexts()

        self.new_headers = self.init_headers(self.new_context)
        
        self.compare_prior, self.old_headers, self.old_bestrefs_name = self.init_comparison()
            
    def add_args(self):
        """Add bestrefs script-specific command line parameters."""
        
        self.add_argument("-n", "--new-context", dest="new_context", 
            help="Compute the updated best references using this context. "
                 "Uses current operational context by default.",
            default=None, type=cmdline.context_mapping)
        
        self.add_argument("-o", "--old-context", dest="old_context",
            help="Compare bestrefs recommendations from two contexts.", 
            metavar="OLD_CONTEXT", default=None, type=cmdline.context_mapping)
        
        self.add_argument("-c", "--compare-source-bestrefs", dest="compare_source_bestrefs", action="store_true",
            help="Compare new bestrefs recommendations to recommendations from data source,  files or database.")
        
        self.add_argument("-f", "--files", nargs="+", metavar="FILES", default=None,
            help="Dataset files to compute best references for.")
        
        self.add_argument("-d", "--datasets", nargs="+", metavar="IDs", default=None,
            help="Dataset ids to compute best references for.")
        
        self.add_argument("-i", "--instruments", nargs="+", metavar="INSTRUMENTS", default=None,
            help="Instruments to compute best references for, all historical datasets.")
        
        self.add_argument("--all-instruments", action="store_true", default=None,
            help="Compute best references for cataloged datasets for all supported instruments.")
        
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
            help="Compute best references from CRDS server",
            action="store_true")
        
        self.add_argument("-s", "--sync-references", action="store_true",
            help="Fetch the refefences recommended by new context to the local cache.")
    
    def setup_contexts(self):
        """Determine and cache the new and comparison .pmap's for this run."""
        if self.args.new_context is None:
            log.verbose("Using default new context", repr(self.default_context), 
                        "for computing updated best references.", verbosity=25)
            new_context = self.default_context
        else:
            log.verbose("Using explicit new context", repr(self.args.new_context), 
                        "for computing updated best references.", verbosity=25)
            new_context = self.args.new_context
        if self.args.old_context is not None:
            log.verbose("Using explicit old context", repr(self.args.old_context), verbosity=25)
        self.sync_contexts(new_context)
        newctx = rmap.get_cached_mapping(new_context)
        oldctx = rmap.get_cached_mapping(self.args.old_context)  if self.args.old_context else None
        return new_context, newctx, oldctx

    def sync_contexts(self, new_context):
        """Recursively cache the new and comparison mappings."""
        if new_context:
            log.verbose("Syncing context", repr(new_context), verbosity=25)
            api.dump_mappings(new_context)
        if self.args.old_context:
            log.verbose("Syncing context", repr(self.args.old_context), verbosity=25)
            api.dump_mappings(self.args.old_context)

    def locate_file(self, filename):
        """Locate a dataset file leaving the path unchanged. Applies to self.args.files"""
        return filename
    
    def init_headers(self, context):
        """Create header a header generator for `context`,  interpreting command line parameters."""
        source_modes = [self.args.files, self.args.datasets, self.args.instruments, 
                        self.args.all_instruments].count(None)
        assert 4 - source_modes == 1, \
            "Can only specify one of: --files, --datasets, --instruments, --all.  Specified " + repr(source_modes)
        if self.args.files:
            new_headers = FileHeaderGenerator(context, self.args.files)
        elif self.args.datasets:
            self.test_server_connection()
            new_headers = DatasetHeaderGenerator(context, [dset.upper() for dset in self.args.datasets])
        elif self.args.instruments or self.args.all_instruments:
            self.test_server_connection()
            instruments = self.newctx.locate.INSTRUMENTS if self.args.all_instruments else self.args.instruments
            new_headers = InstrumentHeaderGenerator(context, instruments)
        else:
            raise RuntimeError("Invalid header source configuration.   "
                               "Specify --files, --datasets, --instruments, or --all.")
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
                # XXX  old_headers = self.init_headers(self.args.old_context)  # ,  potentially different but slow
                old_fname = self.args.old_context
            else:
                old_fname = "recorded bestrefs"
            old_headers = self.new_headers
        return compare_prior, old_headers, old_fname
    
    def main(self):
        """Compute bestrefs for datasets."""
        
        if not self.compare_prior:
            log.info("No comparison context or source comparison requested.")

        for dataset in self.new_headers:
            # with log.error_on_exception("Failed processing", repr(dataset)):
            log.verbose("===> Processing", dataset, verbosity=25)
            self.updates[dataset] = self.process(dataset)
            
        self.handle_updates()

        log.standard_status()
        return log.errors()

    def process(self, dataset):
        """Process best references for `dataset` and return update tuples.     
        returns (dataset, new_context, new_bestrefs) or 
                (dataset, new_context, new_bestrefs, old_context, old_bestrefs)
        """
        new_header, new_bestrefs = self.get_bestrefs(self.new_headers, dataset)
        instrument = self.newctx.get_instrument(new_header)
        log.verbose("Best references for", repr(instrument), "data", repr(dataset), 
                    "with respect to", repr(self.new_context), "=", repr(new_bestrefs))
        if self.compare_prior:
            if self.args.old_context:
                _old_header, old_bestrefs = self.get_bestrefs(self.old_headers, dataset)
            else:
                _old_header, old_bestrefs = self.old_headers.get_old_bestrefs(dataset)
            updates = self.compare_bestrefs(instrument, dataset, new_bestrefs, old_bestrefs)
        else:
            updates = self.screen_bestrefs(instrument, dataset, new_bestrefs)
        return updates
    
    def get_bestrefs(self, header_gen, dataset):
        """Compute the bestrefs for `dataset` with respect to the `context`."""
        try:
            header = header_gen.get_lookup_parameters(dataset)
        except Exception, exc:
            raise crds.CrdsError("Failed getting lookup parameters for data '{}' with respect to '{}' : {}" .format(
                                dataset, header_gen.context, str(exc)))            
        try:
            bestrefs = header_gen.pmap.get_best_references(header)
        except Exception, exc:
            raise crds.CrdsError("Failed computing bestrefs for data '{}' with respect to '{}' : {}" .format(
                                dataset, header_gen.context, str(exc)))
        return header, bestrefs

    def screen_bestrefs(self, instrument, dataset, bestrefs1):
        """Screen one set of best references for `dataset` taken from context named `ctx1`."""
    
        # XXX  This is closely related to compare_bestrefs, maintain both!!
    
        updates = []
        
        for filekind in (self.process_filekinds or bestrefs1):
            
            new_org = cleanpath(bestrefs1.get(filekind, "UNDEFINED"))
            new = new_org.upper()
            u_filekind = filekind.upper()
            
            if new.startswith("NOT FOUND N/A"):
                log.verbose("Filetype not applicable for data", repr(dataset), "type", repr(u_filekind))
                continue
            if new.startswith("NOT FOUND"):
                log.error("Bestref FAILED for data", repr(dataset), "type", repr(u_filekind), 
                          new_org[len("NOT FOUND"):])
                continue
            
            updates.append(UpdateTuple(instrument, filekind, None, new))

        return updates
    
    def compare_bestrefs(self, instrument, dataset, bestrefs1, bestrefs2):
        """Compare two sets of best references for `dataset` taken from contexts named `ctx1` and `ctx2`."""
    
        # XXX  This is closely related to screen_bestrefs,  maintain both!!
    
        updates = []
        
        for filekind in (self.process_filekinds or bestrefs1):
            
            new_org = cleanpath(bestrefs1.get(filekind, "UNDEFINED"))
            new = new_org.upper()
            u_filekind = filekind.upper()
            
            old = cleanpath(bestrefs2.get(filekind, "UNDEFINED")).strip().upper()
        
            if old in ("N/A", "NONE", "", "*"):
                log.verbose("Old bestref marked as", repr(old), "for data", repr(dataset), "type", repr(u_filekind))
                continue    
            if new.startswith("NOT FOUND N/A"):
                log.verbose("Filetype not applicable for data", repr(dataset), "type", repr(u_filekind))
                continue
            if new.startswith("NOT FOUND"):
                log.error("Bestref FAILED for data", repr(dataset), "type", repr(u_filekind), 
                          new_org[len("NOT FOUND"):])
                continue
            if filekind not in bestrefs2:
                log.warning("No comparison bestref for data", repr(dataset), "type", repr(u_filekind), 
                            "recommending -->", repr(new))
                updates.append(UpdateTuple(instrument, filekind, None, new))
                continue
            
            if new != old:
                if self.args.print_new_references or log.get_verbose():
                    log.info("New Reference for data",  repr(dataset), "type", repr(u_filekind), ":", 
                             repr(old), "-->", repr(new))
                updates.append(UpdateTuple(instrument, filekind, old, new))
            else:
                log.verbose("Lookup MATCHES for data", repr(dataset), "type", repr(u_filekind), "=", 
                            repr(old), verbosity=30)
            
        return updates
    
    def handle_updates(self):
        """Given the computed update list, print out results,  update file headers, and fetch missing references."""
        # (dataset, filekind, old, new)
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
            api.dump_references(self.new_context, references)


# ===================================================================

def cleanpath(name):
    """jref$n4e12510j_crr.fits  --> n4e12510j_crr.fits"""
    return name.split("$")[-1].strip()

# ============================================================================

if __name__ == "__main__":
    BestrefsScript()()
