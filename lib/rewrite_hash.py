"""This script updates the checksums of all the mapping files passed in as 
command line parameters:

% python -m crds.rewrite_hash  hst.pmap

will rewrite the sha1sum of hst.pmap.   

NOTE: Since the module loads mappings using Mapping.from_file() and then
rewrites them,  it silently drops mapping comments,  and hence should be used
with discretion.
"""

import sys

import crds.rmap as rmap

def main(files):
    """Rewrite the mapping checksums/hashes/sha1sums in all `files`."""
    for file_ in files:
        print file_
        if file_.endswith((".pmap",".imap")):
            mapping = rmap.Mapping.from_file(file_, ignore_hash=True)
        elif file_.endswith(".rmap"):
            mapping = rmap.ReferenceMapping.from_file(file_, ignore_hash=True)
        else:
            raise ValueError("Bad file extension in file " + repr(file_))
        mapping.write(file_)

if __name__ == "__main__":
    main(sys.argv[1:])
