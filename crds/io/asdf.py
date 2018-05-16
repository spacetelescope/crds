'''
Created on Feb 16, 2017

@author: jmiller
'''
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

# ============================================================================

# import asdf

# ============================================================================

from crds.core import timestamp, utils, log

from .abstract import AbstractFile

# ============================================================================

class AsdfFile(AbstractFile):
    
    format = "ASDF"

    @utils.gc_collected
    def get_raw_header(self, needed_keys=(), **keys):
        """Return the flattened header associated with an ASDF file."""
        import asdf
        with asdf.AsdfFile.open(self.filepath) as handle:
            header = self.to_simple_types(handle.tree)
            with log.warn_on_exception("Failed reading ASDF history"):
                if "history" in handle.tree:
                    histall = []
                    history = handle.tree["history"]
                    if "entries" in history or isinstance(history, list):
                        entries = history["entries"] if "entries" in history else history
                        for hist in entries:
                            histall.append(timestamp.format_date(hist["time"]).split(".")[0] +
                                           " :: " + hist["description"])
                    else:
                        histall = [history.get("description", "Unknown history format.")]
                    header["HISTORY"] = "\n".join(histall)
        return header

