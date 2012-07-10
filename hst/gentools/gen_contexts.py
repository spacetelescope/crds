import sys
import pprint
import os.path

from crds import (rmap, log, timestamp)
from crds.compat import OrderedDict

import crds.hst.parkeys as parkeys

def generate_imap(instr, filekinds):
    now = str(timestamp.now())
    name = "hst_" + instr + ".imap"
    header = OrderedDict([
      ("name", name),
      ("derived_from", "generated " + now),
      ("mapping", "INSTRUMENT"),
      ("observatory" , "HST"),
      ("instrument", instr.upper()),
      ('parkey', ('REFTYPE',)),
      # ("description", ("Initially generated on " + now)),
    ])

    imap = "../mappings/hst/hst_"  + instr + ".imap"
    log.write("writing", imap)

    selector = {}
    for keyword in filekinds:
        eventually_generated_rmap = "hst_" + instr + "_" + keyword + ".rmap"
        if os.path.exists("../mappings/hst/" + eventually_generated_rmap):
            selector[keyword] = eventually_generated_rmap
        else:
            log.warning("Skipping non-existent", eventually_generated_rmap)

    imap = rmap.Mapping(imap, header, selector)
    imap.write()

def main():
    for instr in parkeys.get_instruments():
        generate_imap(instr, parkeys.get_filekinds(instr))
    log.standard_status()

if __name__ == "__main__":
    main()
