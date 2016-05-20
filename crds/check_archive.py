"""This module is used to verify the availability of a list of CRDS files
at the archive web server.
"""

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os.path
import sys

import requests

from crds import cmdline, log, config, utils

class CheckArchiveScript(cmdline.Script):
    """Command line script for for checking archive file availability."""

    description =  """Command line script for for checking archive file availability."""
        
    epilog = """    
    """

    def __init__(self, *args, **keys):
        super(CheckArchiveScript, self).__init__(*args, **keys)
        self.missing_files = []
    
    def add_args(self):
        """Add additional custom parameter for CheckArchiveScript."""
        self.add_argument('--files', nargs='*', dest='files', default=[],
                          help='names of files to check for archive availability.')
        super(CheckArchiveScript, self).add_args()

    @property
    def files(self):
        """Return the filename basenames specified by --files parameters or @-file."""
        return [ os.path.basename(x) for x in self.get_files(self.args.files) ]

    @property
    def mapping_url(self):
        """Return the base archive URL associated with mappings."""
        return self.server_info["mapping_url"][self.observatory]

    @property
    def reference_url(self):
        """Return the base archive URL associated with references."""
        return self.server_info["reference_url"][self.observatory]

    def main(self):
        """Check files for availability from the archive."""
        self.require_server_connection()
        log.info("Mapping URL:", repr(self.mapping_url))
        log.info("Reference URL:", repr(self.reference_url))
        stats = utils.TimingStats()
        for filename in self.files:
            self.verify_archive_file(filename)
            stats.increment("files")
        stats.report_stat("files")
        log.standard_status()

    def archive_url(self, filename):
        """Return the URL used to fetch `filename` from the archive."""
        if config.is_mapping(filename):
            return os.path.join(self.mapping_url, filename)
        else:
            return os.path.join(self.reference_url, filename)

    def verify_archive_file(self, filename):
        """Verify the likely presence of `filename` on the archive web server.  Issue an ERROR if absent."""
        url = self.archive_url(filename)
        response = requests.head(url)
        if response.status_code in [200,]:
            log.verbose("File", repr(filename), "is available from", repr(url))
        else:
            log.error("File", repr(filename), "failed HTTP HEAD with code =", response.status_code, "from", repr(url))
            self.missing_files.append(filename)
            print(filename)
        
if __name__ == "__main__":
    sys.exit(CheckArchiveScript()())
