"""This script updates the checksums of all the mapping files passed in as 
command line parameters:

% python -m crds.checksum  hst.pmap

will rewrite the sha1sum of hst.pmap.   
"""

import sys

from crds import rmap, log

def update_checksum(file_):
    """Rewrite the checksum of a single mapping, in place."""
    mapping = rmap.Mapping.from_file(file_, ignore_checksum=True)
    sha1sum = mapping._get_checksum(open(file_).read())
    result = []
    for line in open(file_):
        if line.strip().startswith("'sha1sum'"):
            line = " "*4 + "'sha1sum' : " + repr(sha1sum) + ",\n"
        result.append(line)
    open(file_, "w+").write("".join(result))

def update_checksums(files):
    """Rewrite the mapping checksums/hashes/sha1sums in all `files`."""
    for file_ in files:
        log.info("Updating checksum for", file_)
        update_checksum(file_)
        
if __name__ == "__main__":
    import crds
    crds.handle_version()
    update_checksums(sys.argv[1:])
