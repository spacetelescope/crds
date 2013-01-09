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

from crds import (log, rmap, data_file, utils)

# ===================================================================

MISMATCHES = {}

# ===================================================================

class Cache(object):
    """A mapping which is kept in a file."""
    def __init__(self, filename, compute_value):
        """Load/save a mapping from `filename`,  calling `compute_value`
        whenever a key is sought which is not in the cache.
        """
        self.filename = filename
        self._compute_value = compute_value
        self._cache = {}
    
    def load(self):
        """Load the cache from it's file."""
        try:
            self._cache = cPickle.load(open(self.filename))
        except Exception, exc:
            log.verbose("Cache load failed:", str(exc), verbosity=25)
            self._cache = {}

    def save(self):
        """Save the cache to it's file."""
        cPickle.dump(self._cache, open(self.filename,"w+"))

    def get(self, key, args):
        """Get the cache value of `key`, calling the `compute_value`
        function with `args` if `key` is not in the cache.
        """
        if key in self._cache:
            log.verbose("Recalibrate header cache hit:", repr(key), verbosity=45)
        else:
            log.verbose("Recalibrate header cache miss:", repr(key), verbosity=45)
            self._cache[key] = self._compute_value(*args)
        return self._cache[key]
    
def get_bestrefs_info(context, dataset):
    """Fetch best reference parameters and results from `dataset`.
    
    `context` is only used as a helper to determine parkeys and
    filekinds,   not to determine bestref values.  All values
    are extracted from `dataset`s header.
    
    Return  ( {parkey: value, ...},  {filekind: bestref, ...} )
    """
    if isinstance(context, basestring):
        pmap = rmap.get_cached_mapping(context)
    else:
        pmap = context
    parkey_values = pmap.get_minimum_header(dataset)
    filekinds = pmap.get_filekinds(dataset)
    # XXX TODO switch get_fits_header to get_header if JWST meta defined for
    # storing CRDS context and bestrefs in a dataset.   For now hack as FITS
    old_bestrefs = data_file.get_fits_header(dataset, needed_keys=filekinds)
    old_bestrefs = { key.lower(): val.lower() \
                    for (key, val) in old_bestrefs.items()}
    log.verbose("Bestref parameters:", parkey_values)
    log.verbose("Old bestrefs:", old_bestrefs)
    return (parkey_values, old_bestrefs)

HEADER_CACHE = Cache("file_bestrefs.cache", get_bestrefs_info)

# ============================================================================

def file_bestrefs(new_context, datasets, old_context=None, update_datasets=False):
    """Compute best references for `dataset`s with respect to pipeline
    mapping `new_context`.  Either compare `new_context` results to 
    references from an `old_context` or compare to prior results recorded 
    in `dataset`s headers.   Optionally write new best reference
    recommendations to dataset headers.
    """
    for dataset in datasets:
        log.info("===> Processing", dataset, verbosity=25)
        basename = os.path.basename(dataset)
        try:        
            try:
                header, old_bestrefs = HEADER_CACHE.get(basename, (new_context, dataset))
            except Exception, exc:
                raise RuntimeError("Can't get header info for " + repr(dataset) + " " + str(exc))
            try:
                bestrefs1 = new_context.get_best_references(header)
            except Exception, exc:
                raise crds.CrdsError("Bestrefs for " + repr(new_context.name) + " failed: " + str(exc))

            if old_context:
                try:
                    bestrefs2 = old_context.get_best_references(header)
                except Exception, exc:
                    raise crds.CrdsError("Bestrefs for " + repr(old_context.name) + " failed: " + str(exc))
                old_fname = old_context.filename
            else:
                bestrefs2 = old_bestrefs
                old_fname = "<dataset prior results>"
                
            new_fname = os.path.basename(new_context.filename)
            
            compare_bestrefs(new_fname, old_fname, dataset, bestrefs1, bestrefs2)
            
            if update_datasets:
                write_bestrefs(new_fname, dataset, bestrefs1)

        except Exception, exc:
            log.error("Failed processing", repr(dataset), ":", str(exc))
            

def compare_bestrefs(ctx1, ctx2, dataset, bestrefs1, bestrefs2):
    """Compare two sets of best references for `dataset` taken from
    contexts named `ctx1` and `ctx2`.
    """
    mismatches = 0
    
    for filekind in bestrefs1:
        new = remove_irafpath(bestrefs1[filekind])
        if new.upper().startswith("NOT FOUND N/A"):
            log.verbose("Filetype not applicable for ", repr(dataset), repr(filekind))
            continue
        if new.upper().startswith("NOT FOUND"):
            log.error("No new bestref for", repr(dataset), repr(filekind), repr(new))
            continue
        if filekind not in bestrefs2:
            log.warning("No existing bestref for", repr(dataset), repr(filekind),
                        "recommending", repr(new))
            continue
        old = remove_irafpath(bestrefs2[filekind])
        if isinstance(old, (str, unicode)):
            old = str(old).strip().lower()
        if old not in [None, "", "n/a","*"]:
            if new != old:
                log.info("New Reference for",  repr(dataset), repr(filekind), 
                            ":", repr(old), "-->", repr(new))
                if filekind != "mdriztab":  
                    # these are guaranteed to fail for archive files
                    mismatches += 1
                    if filekind not in MISMATCHES:
                        MISMATCHES[filekind] = []
                    MISMATCHES[filekind].append(dataset)
            else:
                log.verbose("Lookup MATCHES for", repr(new), repr(filekind), 
                            "=", repr(old), verbosity=30)
        else:
            log.verbose("Lookup N/A for", repr(new), repr(filekind), 
                        verbosity=30)
    if mismatches > 0:
        sys.exc_clear()
        log.verbose("Total New References for", repr(dataset), "=", mismatches,
                 verbosity=25)
    else:
        log.verbose("All lookups for", repr(dataset), "MATCH.", verbosity=25)

def remove_irafpath(name):
    """jref$n4e12510j_crr.fits  --> n4e12510j_crr.fits"""
    return name.split("$")[-1]

def write_bestrefs(new_pmap_name, dataset, bestrefs):
    """Update the header of `dataset` with best reference recommendations
    `bestrefs` determined by context named `new_pmap`.
    """
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

# =============================================================================

def main():
    """Process command line parameters and run file_bestrefs."""
    import crds
    crds.handle_version()
    parser = optparse.OptionParser(
        "usage: %prog [options] <new_context> <datasets...>")
    parser.add_option("-c", "--cache-headers", dest="use_cache",
        help="Use and/or remember critical header parameters in a cache file.", 
        action="store_true")
    parser.add_option("-f", "--files", dest="files",
        help="Read datasets from FILELIST, one dataset per line.", 
        metavar="FILELIST", default=None)
    parser.add_option("-o", "--old-context", dest="old_context",
        help="Compare best refs recommendations from two contexts.", 
        metavar="OLD_CONTEXT", default=None)
    parser.add_option("-u", "--update-datasets", dest="update_datasets",
        help="Update dataset headers with new best reference recommendations.", 
        action="store_true")
    options, args = log.handle_standard_options(sys.argv, parser=parser)

    if len(args) < 2:
        log.write("usage: file_bestrefs.py <pmap>  <dataset>... [options]")
        sys.exit(-1)

    newctx_fname, datasets = args[1], args[2:]
    
    if options.files:
        datasets += [file_.strip() for file_ in open(options.files).readlines()]
    
    # do one time startup outside profiler.
    newctx = rmap.get_cached_mapping(newctx_fname)
    if options.old_context:
        oldctx = rmap.get_cached_mapping(options.old_context)
    else:
        oldctx = None
        
    if options.use_cache:
        HEADER_CACHE.load()
    
    file_bestrefs(newctx, datasets, oldctx, options.update_datasets)
    
    if options.use_cache:
        HEADER_CACHE.save()

    log.standard_status()

if __name__ == "__main__":
    main()
