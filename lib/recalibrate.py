"""This module is a command line script which handles comparing the best
reference recommendations for a particular context and dataset to prior bestrefs
recommendations for the dataset.

Prior recommendations can really come in two forms:

1. Recommendations generated relative to a second context.
2. Recommendations extracted from the FITS header.

To make new recommendations more quickly, recalibrate can store information
about prior recommendations in a data store,  including both the recommendations
themselves and as well as critical parameters required to find them.
"""

import sys
import cPickle
import os.path
import pprint

import pyfits

from crds import (log, rmap, utils)
import crds.client.api as api

MISMATCHES = {}

def test_references(fitsname):
    """Compute best references for `fitsname` and compare to the reference
    selections aready recorded in its header.   If there is no comparison value
    in the header,  consider that reference "not applicable" and ignore any
    failures attempting to compute it.
    """
    
    # Just want header for bestrefs,  so conditioning irrelevant + expensive
    header = get_unconditioned_header_union(fitsname)

    refs = rmap.get_best_references("hst.pmap", header)

    mismatches = 0
    for filekind in refs:
        crds, hist = None, None
        try:
            crds = refs[filekind]
            hist = header[filekind.upper()]
            hist = hist.split("$")[-1]
        except:
            pass
        if isinstance(hist, (str, unicode)):
            hist = hist.strip().lower()
        if hist not in [None, "", "n/a","*"]:
            if crds != hist:
                log.warning("Lookup MISMATCH for",  repr(fitsname), repr(filekind), repr(crds), repr(hist))
                if filekind != "mdriztab":  # these are guaranteed to fail for archive files
                    mismatches += 1
                    if filekind not in MISMATCHES:
                        MISMATCHES[filekind] = []
                    MISMATCHES[filekind].append(fitsname)
            else:
                log.verbose("Lookup OK for", repr(filekind), repr(crds))
        else:
            log.verbose("Lookup N/A for", repr(filekind))
    if mismatches > 0:
        sys.exc_clear()
        log.error("Total MISMATCHES for", repr(fitsname), "=", mismatches)
        # log.verbose("\n\n" + str(header))
    else:
        log.info("All lookups for", repr(fitsname), "OK.")

def main():
    files = sys.argv[1:]
    for f in files:
        if f.startswith("@"):
            files.extend([l.strip() for l in open(f[1:])])
            continue
        try:
            test_references(f)
        except Exception, e:
            raise
            log.error("Lookups for", repr(f), "FAILED.")

    log.write("MISMATCHES:")
    log.write(pprint.pformat(MISMATCHES))
    log.standard_status()

# ===================================================================

class Cache(object):
    def __init__(self, filename, compute_value):
        self.filename = filename
        self._compute_value = compute_value
        self._cache = {}
    
    def load(self):
        try:
            self._cache = cPickle.load(self.filename)
        except Exception, e:
            log.verbose("Cache load failed:", str(e))
            self._cache = {}

    def save(self):
        cPickle.dump(self._cache, open(self.filename,"w+"))

    def get(self, key, args):
        if key in self._cache:
            log.verbose("Cache hit:",repr(key))
        else:
            log.verbose("Cache miss:",repr(key))
            self._cache[key] = self._compute_value(args)
        return self._cache[key]
    
def get_recalibrate_info(context, dataset):
    """Fetch best reference parameters and results from `dataset`.
    
    `context` is only used as a helper to determine parkeys and
    filekinds,   not to determine bestref values.  All values
    are extracted from `dataset`s header.
    
    Return  ( {parkey: value, ...},  {filekind: bestref, ...} )
    """
    required_parkeys = context.get_minimum_header(dataset)
    filekinds = context.get_filekinds(dataset)
    parkey_values = utils.get_header_union(dataset, required_parkeys)
    old_bestrefs = utils.get_header_union(dataset, filekinds)
    return (parkey_values, old_bestrefs)
    
HEADER_CACHE = Cache("recalibrate.cache", get_recalibrate_info)

# ============================================================================

def recalibrate(new_context, datasets, options):

    newctx = rmap.get_cached_mapping(new_context)

    for dataset in datasets:
        log.verbose("===> Processing", dataset)

        basename = os.path.basename(dataset)
        
        header, old_bestrefs = HEADER_CACHE.get(basename, (newctx, dataset))

        bestrefs1 = trapped_bestrefs(newctx, header)

        if options.old_context:
            oldctx = rmap.get_cached_mapping(options.old_context)
            bestrefs2 = trapped_bestrefs(olctx, header)
        else:
            bestrefs2 = old_bestrefs
            
        if not bestrefs1 or not bestrefs2:
            continue
        
        compare_bestrefs(bestrefs1, bestrefs2)
        
        if options.update_datasets:
            write_bestrefs(dataset, bestrefs1)
            
def trapped_bestrefs(ctx, header):
    try:
        return ctx.get_best_references(header)
    except Exception, e :
        log.error("Best references FAILED for ", repr(ctx))

def main(args, options):
    parser = optparse.OptionParser(
        "usage: %prog [options] <new_context> <datasets...>")
    parser.add_option("-U", "--update-datasets", dest="update_datasets",
        help="Update dataset headers with new best reference recommendations.", 
        action="store_true")
    parser.add_option("-C", "--cache-headers", dest="cache_headers",
        help="Use and/or remember critical header parameters in a cache file.", 
        action="store_true")
    parser.add_option("-O", "--old-context", dest="old_context",
        help="Compare best refs recommendations from two contexts.", 
        metavar="OLD_CONTEXT", defalut=None)
    options, args = log.handle_standard_options(sys.argv, parser=parser)

    new_context, datasets = args[0], args[1:]
    
    if options.files:
        datasets += [file.strip() for file in open(options.files).readlines()]
    
    if options.use_cache:
        HEADER_CACHE.load()
    
    # do one time startup outside profiler.
    rmap.get_cached_mapping(new_context)  
    if options.context2:
        rmap.get_cached_mapping(options.context2)
        
    log.standard_run("_main(args, options)", options, globals(), globals())

    if options.use_cache:
        HEADER_CACHE.save()

if __name__ == "__main__":
    main()
