'''
Created on Feb 16, 2017

@author: jmiller
'''
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
        with asdf.open(self.filepath) as handle:
            header = self.to_simple_types(handle.tree)
            header["HISTORY"] = self.get_history(handle)
        return header

    def get_history(self, handle):
        """Given and ASDF file object `handle`, return the history collected into a
        single string.
        """
        history = "UNDEFINED"   # or BAD FORMAT
        with log.error_on_exception(
                "Failed reading ASDF history, see ASDF docs on adding history"):
            histall = []
            hist = handle.tree["history"]
            try:
                entries = handle.get_history_entries()
            except Exception:
                log.verbose_warning(
                    "Using inlined CRDS ASDF history entry reading interface.")
                entries = hist["entries"] if "entries" in hist else hist
            for entry in entries:
                time = timestamp.format_date(entry["time"]).split(".")[0]
                description = entry["description"]
                histall.append(time + " :: " + description)
            if histall:
                history = "\n".join(histall)
        return history

    def get_asdf_standard_version(self):
        """
        Return the ASDF Standard version associated with this file as a string,
        or `None` if the file is neither an ASDF file nor contains an embedded
        ASDF file.
        """
        import asdf
        with asdf.open(self.filepath) as handle:
            return str(handle.version)
