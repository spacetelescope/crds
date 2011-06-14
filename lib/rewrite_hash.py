import sys

import crds.rmap as rmap

for file_ in sys.argv[1:]:
    print file_
    if file_.endswith((".pmap",".imap")):
        m = rmap.Mapping.from_file(file_, ignore_hash=True)
    elif file_.endswith(".rmap"):
        m = rmap.ReferenceMapping.from_file(file_, ignore_hash=True)
    else:
        raise ValueError("Bad file extension in file " + repr(file_))
    m.write(file_)

