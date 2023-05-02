'''
Created on Feb 15, 2017

@author: jmiller
'''
import json

# ============================================================================

from crds.core import exceptions

from .abstract import AbstractFile

# ============================================================================

class JsonFile(AbstractFile):

    format = "JSON"

    def get_raw_header(self, needed_keys=(), **keys):
        """Return the flattened header associated with a JSON file."""
        with open(self.filepath) as pfile:
            try:
                header = json.load(pfile)
            except ValueError as exc:
                raise exceptions.JsonFormatError(
                    "JSON wouldn't load from", repr(self.filepath), ":", str(exc))
            header = self.to_simple_types(header)
        return header
