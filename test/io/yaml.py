'''
Created on Feb 15, 2017

@author: jmiller
'''
# import yaml

# ============================================================================

from crds.core import exceptions

from .abstract import AbstractFile
# ============================================================================

class YamlFile(AbstractFile):

    format = "YAML"

    def get_raw_header(self, needed_keys=(), **keys):
        """Return the flattened header associated with a YAML file."""
        import yaml
        with open(self.filepath) as pfile:
            try:
                header = yaml.safe_load(pfile)
            except ValueError as exc:
                raise exceptions.YamlFormatError(
                    "YAML wouldn't load from", repr(self.filepath), ":", str(exc))
            header = self.to_simple_types(header)
        return header
