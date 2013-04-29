"""This module is a command line script which handles comparing the best
reference recommendations for a particular context and dataset files.

Dataset parameters/headers required to compute best refs can come in two
forms:

1. Dataset file headers
2. Cache file

Prior recommendations can really come in three forms:

1. Generated from a second context.
2. Dataset file headers
3. Cache file

To make new recommendations more quickly, file_bestrefs can store information
about prior recommendations in a cache file,  including both the recommendations
themselves and as well as critical parameters required to find them.

To support one possible use case of CRDS,  file_bestrefs can write new best
reference recommendations into the dataset file headers.
"""

import sys
import cPickle
import os.path
import pprint
import optparse

import pyfits

import crds
from crds import (log, rmap, data_file, utils, cmdline)
from crds.client import api

# ===================================================================

class HeaderGenerator(object):
    def __init__(self, context, sources):
        self.context = context
        self.sources = sources
        self.pmap = rmap.get_cached_mapping(context)
        self.headers = {}

    def __iter__(self):
        return iter(self.sources)
    
    def header(self, source):
        return self.headers[source]
    
    def get_lookup_parameters(self, source):
        hdr = self.header(source)
        min_hdr = self.pmap.minimize_header(hdr)
        min_hdr = { key.upper():utils.condition_value(val) for (key,val) in min_hdr.items() }
        log.verbose("Bestref parameters for", repr(source), "with respect to", repr(self.context), "=", min_hdr)
        return min_hdr

    def get_old_bestrefs(self, source):
        hdr = self.header(source)
        filekinds = self.pmap.get_filekinds(hdr) #  XXX only includes filekinds in .pmap
        old_bestrefs = { key.lower(): val for (key, val) in hdr.items() if key.upper() in filekinds }
        log.verbose("Old best reference recommendations from", repr(source), "=", repr(old_bestrefs))
        return old_bestrefs

class FileHeaderGenerator(HeaderGenerator):
    @utils.cached
    def header(self, filename):
        """Get the best references recommendations recorded in the header of file `dataset`."""
        return data_file.get_header(filename, observatory=self.pmap.observatory)

class DatasetHeaderGenerator(HeaderGenerator):
    def __init__(self, context, datasets):
        super(DatasetHeaderGenerator, self).__init__(context, datasets)
        log.verbose("Dumping datasets from CRDS server for", repr(datasets), verbosity=25)
        self.headers = api.get_dataset_headers_by_id(context, datasets)
        log.verbose("Dumped", len(self.headers), "of", len(datasets), "datasets from CRDS server.", verbosity=25)
    
class InstrumentHeaderGenerator(HeaderGenerator):
    def __init__(self, context, instruments):
        super(InstrumentHeaderGenerator, self).__init__(context, instruments)
        self.instruments = instruments
        sorted_sources = []
        for instrument in instruments:
            log.verbose("Dumping datasets for", repr(instrument), "from CRDS server.", verbosity=25)
            more = api.get_dataset_headers_by_instrument(context, instrument)
            log.verbose("Dumped", len(more), "datasets for", repr(instrument), "from CRDS server.", verbosity=25)
            self.headers.update(more)
            sorted_sources.extend(sorted(more.keys()))
        self.sources = sorted_sources

# ===================================================================

def update_file_bestrefs(pmap, dataset, bestrefs):
    """Update the header of `dataset` with best reference recommendations
    `bestrefs` determined by context named `pmap`.
    """
    pmap = rmap.asmapping(pmap)
    # XXX TODO switch pyfits.setval to data_file.setval if a data model equivalent
    # is defined for CRDS_CTX
    
    # Here we use the dataset file because we know we have the full path, 
    # whereas the reference we'd have to locate.
    instrument = utils.file_to_instrument(dataset)
    pmap = rmap.get_cached_mapping(new_pmap_name)
    prefix = pmap.locate.get_env_prefix(instrument)
    
    pyfits.setval(dataset, "CRDS_CTX", value=new_pmap_name, ext=0)
    for key, value in bestrefs.items():
#        XXX what to do here for failed startswith("NOT FOUND") lookups?
        if value.upper().startswith("NOT FOUND"):
            if "N/A" in value.upper():
                value = "N/A"
        else:
            value = prefix + value
        pyfits.setval(dataset, key, value=value, ext=0)            

def update_db_bestrefs(self, pmap, dataset_id):
    """Get the best references recommendations stored in the database for `dataset_id`."""
    raise NotImplementedError("Database best reference updates aren't implemented yet.")

# ============================================================================

class BestrefsScript(cmdline.Script):
    """Command line script for determining best references for a sequence of dataset files."""

    description = """
Determines best references with respect to a context.
    """
    
    epilog = ""
    
    def __init__(self, *args, **keys):
        super(BestrefsScript, self).__init__(*args, **keys)
        self.updates = []
        self.parameter_cache = {}
        self.old_bestrefs_cache = {}
    
        self.process_filekinds = [typ.lower() for typ in self.args.types ]
    
        # do one time startup outside profiler.
        self.newctx = rmap.get_cached_mapping(self.args.new_context)
        self.oldctx = None if self.args.old_context is None else rmap.get_cached_mapping(self.args.old_context)
        self.new_headers = self.init_headers(self.args.new_context)
        self.compare_prior, self.old_headers, self.old_bestrefs_name = self.init_comparison()

    def add_args(self):
        """Add bestrefs script-specific command line parameters."""
        self.add_argument("new_context", type=cmdline.context_mapping,
            help="New CRDS context/rules (.pmap or .imap) used to determine best references.")
        
        self.add_argument("-o", "--old-context", dest="old_context",
            help="Compare best refs recommendations from two contexts.", 
            metavar="OLD_CONTEXT", default=None, type=cmdline.context_mapping)
        
        self.add_argument("-c", "--compare-cdbs", dest="compare_cdbs", action="store_true",
            help="Compare best refs recommendations from two contexts.")
        
        self.add_argument("-f", "--files", nargs="+", metavar="FILES", default=None,
            help="Dataset files to compute best references for.")
        
        self.add_argument("-d", "--datasets", nargs="+", metavar="IDs", default=None,
            help="Dataset ids to compute best references for.")
        
        self.add_argument("-i", "--instruments", nargs="+", metavar="INSTRUMENTS", default=None,
            help="Instruments to compute best references for, all historical datasets.")
        
        self.add_argument("-t", "--types", nargs="+",  metavar="REFERENCE_TYPES",  default=(),
            help="A list of reference types to process,  defaulting to all types.")
        
        self.add_argument("-u", "--update-datasets", dest="update_datasets",
            help="Update dataset headers with new best reference recommendations.", 
            action="store_true")
        
        self.add_argument("-a", "--print-affected", dest="print_affected",
            help="Print names of data sets for which the new context would assign new references.",
            action="store_true")
    
        self.add_argument("-n", "--print-new-references", dest="print_new_references",
            help="Prints info messages detailing each reference file change.",
            action="store_true")
    
        self.add_argument("-b", "--print-best-references", dest="print_best_references",
            help="Prints info messages describing all recommended references.",
            action="store_true")
    
    def locate_file(self, filename):
        """Locate a dataset file leaving the path unchanged. Applies to self.args.files"""
        return filename

    def init_headers(self, context):
        assert [self.args.files, self.args.datasets, self.args.instruments].count(None) == 2, \
            "Can only specify one of: --files, --datasets, --instruments"
        if self.args.files:
            new_headers = FileHeaderGenerator(context, self.args.files)
        elif self.args.datasets:
            self.test_server_connection()
            new_headers = DatasetHeaderGenerator(context, [dset.upper() for dset in self.args.datasets])
        elif self.args.instruments:
            self.test_server_connection()
            new_headers = InstrumentHeaderGenerator(context, self.args.instruments)
        else:
            raise RuntimeError("Invalid header source configuration.   Specify --files, --datasets, or --instruments.")
        return new_headers
    
    def init_comparison(self):
        assert not (self.args.old_context and self.compare_cdbs), \
            "Cannot specify both --old-context and --compare-cdbs."
        compare_prior = self.args.old_context or self.args.compare_cdbs
        old_headers = old_fname = None
        if compare_prior:
            if self.args.old_context:
                # XXX  old_headers = self.init_headers(self.args.old_context)  # ,  potentially different but slow
                old_fname = self.args.old_context
            else:
                old_fname = "SAVED BESTREFS"
            old_headers = self.new_headers
        return compare_prior, old_headers, old_fname
    
    def main(self):
        """Compute bestrefs for datasets."""
        
        for dataset in self.new_headers:
            # with log.error_on_exception("Failed processing", repr(dataset)):
            log.verbose("===> Processing", dataset, verbosity=25)
            updates = self.process(dataset)            
            self.updates.extend(updates)
            
        self.handle_updates()

        log.standard_status()
        return log.errors()

    def process(self, dataset):
        """Process best references for `dataset` and return update tuples.     
        returns (dataset, new_context, new_bestrefs) or 
                (dataset, new_context, new_bestrefs, old_context, old_bestrefs)
        """
        new_bestrefs = self.get_bestrefs(self.new_headers, dataset)
        if self.args.print_best_references or log.get_verbose():
            log.info("Best references for", repr(dataset), "with respect to", repr(self.args.new_context), 
                     "=", repr(new_bestrefs))
        if self.compare_prior:
            if self.args.old_context:
                old_bestrefs = self.get_bestrefs(self.old_headers, dataset)
            else:
                old_bestrefs = self.old_headers.get_old_bestrefs(dataset)
            updates = self.compare_bestrefs(dataset, self.args.new_context, self.old_bestrefs_name, new_bestrefs, old_bestrefs)
        else:
            updates = [(dataset, filekind, None, new) for (filekind, new) in sorted(new_bestrefs.items())]
        return updates
    
    def get_bestrefs(self, header_gen, dataset):
        """Compute the bestrefs for `dataset` with respect to the `context`."""
        try:
            header = header_gen.get_lookup_parameters(dataset)
            bestrefs = header_gen.pmap.get_best_references(header)
            return bestrefs
        except Exception, exc:
            raise crds.CrdsError("Failed computing bestrefs for '{}' with respect to '{}' : {}" .format(dataset, header_gen.context, str(exc)))

    def compare_bestrefs(self, dataset, ctx1, ctx2, bestrefs1, bestrefs2):
        """Compare two sets of best references for `dataset` taken from contexts named `ctx1` and `ctx2`."""
    
        updates = []
        
        errors = 0
        for filekind in (self.process_filekinds or bestrefs1):
            
            new_org = cleanpath(bestrefs1.get(filekind, "UNDEFINED"))
            new = new_org.upper()
            u_filekind = filekind.upper()
            
            old = cleanpath(bestrefs2.get(filekind, "UNDEFINED")).strip().upper()
        
            if old.startswith(("N/A","NONE","","*")):
                log.verbose("Old bestref marked as", repr(old), "for", repr(dataset), repr(u_filekind))
                continue    
            if new.startswith("NOT FOUND N/A"):
                log.verbose("Filetype not applicable for ", repr(dataset), repr(u_filekind))
                continue
            if new.startswith("NOT FOUND"):
                errors += 1
                log.error("Bestref FAILED for", repr(dataset), repr(u_filekind), new_org[len("NOT FOUND"):])
                continue
            if filekind not in bestrefs2:
                log.warning("No comparison bestref for", repr(dataset), repr(u_filekind), "recommending -->", repr(new))
                updates.append((dataset, filekind, None, new))
                continue
            
            if old not in ["", "N/A","*"]:
                if new != old:
                    if self.args.print_new_references or log.get_verbose():
                        log.info("New Reference for",  repr(dataset), repr(u_filekind), ":", repr(old), "-->", repr(new))
                    updates.append((dataset, filekind, old, new))
                else:
                    log.verbose("Lookup MATCHES for", repr(dataset), repr(u_filekind), "=", repr(old), verbosity=30)
            else:
                log.verbose("Lookup N/A for", repr(dataset), repr(u_filekind), repr(old), verbosity=30)
            
        return updates
    
    def handle_updates(self):
        # (dataset, filekind, old, new)
        if self.args.print_affected:
            self.print_affected()
            
    def print_affected(self):
        seen = set()
        for dataset, filekind, old, new in self.updates:
            if dataset not in seen:
                print(dataset)
                seen.add(dataset)

# ===================================================================

def cleanpath(name):
    """jref$n4e12510j_crr.fits  --> n4e12510j_crr.fits"""
    return name.split("$")[-1].strip()

# ============================================================================

if __name__ == "__main__":
    BestrefsScript()()
