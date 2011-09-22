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
import cProfile
import pprint

import pyfits

import crds.hst.gentools.lookup as lookup
import crds.log as log
import crds.rmap as rmap
import crds.client.api as api

import sys
import cPickle
import pprint
import os.path

import pyfits

import crds.log as log
import crds.utils as utils

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
        log.verbose("===> Processing", f)
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

"""This module defines lookup code tailored to the HST rmaps.
"""
import sys
import cPickle
import pprint
import os.path

import pyfits

import crds.log as log
import crds.utils as utils

# ===================================================================

HEADER_CACHE = {}

def get_unconditioned_header_union(fpath):
    """Handle initial or cached fetch of unconditioned header values.
    """
    fname = os.path.basename(fpath)
    if fname in HEADER_CACHE:
        log.verbose("Cache hit:",repr(fname))
        return HEADER_CACHE[fname]
    log.verbose("Cache miss:",repr(fname))
    union = HEADER_CACHE[fname] = utils.get_header_union(fpath)
    return union

def get_header_union(fname):
    """Return the FITS header of `fname` as a dict,  successively
    adding all extension headers to the dict.   Cache the combined
    header in case this function is called more than once on the
    same FITS file.

    Each keyword value is "conditioned" into a
    canonical form which smoothes over inconsistencies.
    See rmap.condition_value() for details.
    """
    header = get_unconditioned_header_union(fname)
    for key, value in header.items():
        header[key] = utils.condition_value(value)
    return header

HERE = os.path.dirname(__file__) or "./"

def load_cache():
    """Load the global HEADER_CACHE which prevents pyfits header reads for calls
    to get_header_union() when a file as already been visited.
    """
    global HEADER_CACHE
    try:
        # HEADER_CACHE = eval(open(HERE + "/recalibrate.cache").read())
        HEADER_CACHE = cPickle.load(open(HERE + "/recalibrate.cache"))
    except Exception, e:
        log.info("cache failed to load:", str(e))

def save_cache():
    """Save the global HEADER_CACHE to store the FITS header unions of any newly
     visited files.
    """
    # open(HERE + "/recalibrate.cache", "w+").write(pprint.pformat(HEADER_CACHE))
    cPickle.dump(HEADER_CACHE, open(HERE + "/recalibrate.cache","w+"))

if __name__ == "__main__":
    lookup.load_cache()
    rmap.get_cached_mapping("hst.pmap")   # pre-cache the bestref stuff
    if "--profile" in sys.argv:
        sys.argv.remove("--profile")
        cProfile.run("main()")
    else:
        if "--verbose" in sys.argv:
            sys.argv.remove("--verbose")
            log.set_verbose(True)
        main()
    if SAVE:
        lookup.save_cache()

def _main(args, options):
    context1, datasets = args[0], args[1:]
    
    ctx1 = rmap.get_cached_mapping(context1)
    if options.context2:
        ctx2 = rmap.get_cached_mapping(options.context2)

    for dataset in datasets:

        if options.cache_headers:
            header = get_required_header(options, dataset)

        bestrefs1 = ctx1.get_best_references(header)
        if options.context2:
            bestrefs2 = ctx2.get_best_references(header)
        else:
            bestrefs2 = utils.get_header_union(dataset, bestrefs1.keys())

def main(args, options):
    parser = optparse.OptionParser(
        "usage: %prog [options] <context1> <datasets...>")
    parser.add_option("-W", "--write-datasets", dest="write_bestrefs",
        help="Update dataset headers with new best reference recommendations.", 
        action="store_true")
    parser.add_option("-U", "--update-bestrefs", dest="write_bestrefs",
        help="Update dataset headers with new best reference recommendations.", 
        action="store_true")
    parser.add_option("-C", "--cache-headers", dest="cache_headers",
        help="Use and/or remember critical header parameters in a cache file.", 
        action="store_true")
    parser.add_option("-2", "--context2", dest="context2",
        help="Compare best refs recommendations from two contexts.", 
        metavar="CONTEXT2", defalut=None)
    options, args = log.handle_standard_options(sys.argv, parser=parser)

    if options.use_cache:
        load_cache()
    
    # get through one time startup outside profiler.
    rmap.get_cached_mapping(context1)  
    if options.context2:
        rmap.get_cached_mapping(options.context2)
        
    log.standard_run("_main(args, options)", options, globals(), globals())

    if options.use_cache:
        save_cache()

if __name__ == "__main__":
    main()
