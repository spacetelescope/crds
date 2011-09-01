"""This script updates the checksums of all the mapping files passed in as 
command line parameters:

% python -m crds.checksum  hst.pmap

will rewrite the sha1sum of hst.pmap.   

This version of crds.checksum fully preserves comments.
"""

import sys

import crds.rmap as rmap

def update_checksum(file_):
    """Rewrite the checksum of a single mapping, in place."""
    if file_.endswith((".pmap",".imap")):
        mapping = rmap.Mapping.from_file(file_, ignore_checksum=True)
    elif file_.endswith(".rmap"):
        mapping = rmap.ReferenceMapping.from_file(file_, ignore_checksum=True)
    else:
        raise ValueError("Bad file extension in file " + repr(file_))
    mapping.rewrite_checksum(file_)

def update_checksums(files):
    """Rewrite the mapping checksums/hashes/sha1sums in all `files`."""
    for file_ in files:
        update_checksum(file_)
        
if __name__ == "__main__":
    update_checksums(sys.argv[1:])
