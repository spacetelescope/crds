"""This script updates the checksums of all the mapping files passed in as 
command line parameters:

% python -m crds.checksum  hst.pmap

will rewrite the sha1sum of hst.pmap.   
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys

from crds import rmap, log

def update_checksum(file_):
    """Rewrite the checksum of a single mapping, in place."""
    mapping = rmap.Mapping.from_file(file_, ignore_checksum=True)
    mapping.write()

def update_checksums(files):
    """Rewrite the mapping checksums/hashes/sha1sums in all `files`."""
    for file_ in files:
        log.info("Updating checksum for", file_)
        with log.error_on_exception("Failed updating checksum for", repr(file_)):
            update_checksum(file_)
        
if __name__ == "__main__":
    import crds
    crds.handle_version()
    update_checksums(sys.argv[1:])
    log.standard_status()
