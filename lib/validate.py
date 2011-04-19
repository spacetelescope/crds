"""This module recursively validates an instrument's context and mapping files.
"""
import sys
import os.path
import log

import rmap

def validate_context(fname):
    log.info("Validating context:", repr(fname))
    try:
        header, data = rmap.load_rmap(fname, "CONTEXT")
    except rmap.RmapError, e:
        log.error()
        return

    filepath = os.path.dirname(fname) or "./"

    for reftype, (ext, mapname) in data.items():
        try:
            validate_mapping_file(filepath +"/" + mapname, reftype)
        except rmap.RmapError, e:
            log.error(repr(reftype))

def validate_mapping_file(fname, reftype=None):
    log.info("Validating mapping file:", repr(fname))
    header, data = rmap.load_rmap(fname, reftype)

def main():
    for fname in sys.argv[1:]:
        validate_context(fname)   # eventually this should probably run off either kind.
    log.standard_status()

if __name__ == "__main__":
    main()

