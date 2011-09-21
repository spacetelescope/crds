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
    header = lookup.get_unconditioned_header_union(fitsname)

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

def load_header_cache():
    """Load the global HEADER_CACHE which prevents pyfits header reads for calls
    to get_header_union() when a file as already been visited.
    """
    global HEADER_CACHE
    try:
        HEADER_CACHE = eval(open(HERE + "/header_cache").read())
        # HEADER_CACHE = cPickle.load(open("header_cache"))
    except Exception, e:
        log.info("header_cache failed to load:", str(e))

def save_header_cache():
    """Save the global HEADER_CACHE to store the FITS header unions of any newly visited files.
    """
    open(HERE + "/header_cache", "w+").write(pprint.pformat(HEADER_CACHE))
    # cPickle.dump(HEADER_CACHE, open("header_cache","w+"))

if __name__ == "__main__":
    lookup.load_header_cache()
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
        lookup.save_header_cache()

