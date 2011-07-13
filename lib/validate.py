"""This module recursively validates an instrument's context and mapping files.
"""
import sys
import os.path
import log

import crds.rmap as rmap

def validate_context(fname):
    log.info("Validating context:", repr(fname))
    
    mapping = rmap.get_cached_mapping(fname)
    
    for reference in mapping.reference_names():
        try:
            where = mapping.locate.locate_reference(reference)
        except KeyError, e:
            sys.exc_clear()
            log.error("Unknown reference file", str(e))
        else:
            log.info("OK reference", repr(where))
        # if not os.path.exists(where):
        #     log.error("Missing reference file", repr(where))


def main():
    for fname in sys.argv[1:]:
        validate_context(fname)   # eventually this should probably run off either kind.
    log.standard_status()

if __name__ == "__main__":
    main()

