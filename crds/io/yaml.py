'''
Created on Feb 15, 2017

@author: jmiller
'''
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

# ============================================================================

# import yaml

# ============================================================================

from crds.core import exceptions

from .abstract import AbstractFile
# ============================================================================

class YamlFile(AbstractFile):
    
    format = "YAML"

    def get_raw_header(self, needed_keys=()):
        """Return the flattened header associated with a YAML file."""
        import yaml
        with open(self.filepath) as pfile:
            try:
                header = yaml.load(pfile)
            except ValueError as exc:
                raise exceptions.YamlFormatError(
                    "YAML wouldn't load from", repr(self.filepath), ":", str(exc))
            header = self.to_simple_types(header)
        return header

