#! /usr/bin/env pysh
#-*-python-*-

"""This module is a command line script which lists the reference and/or
mapping files associated with the specified contexts by consulting the CRDS
server.   More generally it's for printing out information on CRDS files.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os.path
import sys

import requests

from crds import cmdline, log, config, utils
from crds.client import api

class CheckArchiveScript(cmdline.Script):
    """Command line script for for checking archive file availability."""

    description =  """Command line script for for checking archive file availability."""
        
    epilog = """    
    """
    
    def add_args(self):
        self.add_argument('--files', nargs='*', dest='files', default=[],
            help='names of files to check for archive availability.')
        super(CheckArchiveScript, self).add_args()

    @property
    def files(self):
        return self.args.files

    @property
    def mapping_url(self):
        return self.server_info["mapping_url"][self.observatory]

    @property
    def reference_url(self):
        return self.server_info["reference_url"][self.observatory]

    def main(self):
        """List files."""
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
        if config.is_mapping(filename):
            return os.path.join(self.mapping_url, filename)
        else:
            return os.path.join(self.reference_url, filename)

    def verify_archive_file(self, filename):
        url = self.archive_url(filename)
        response = requests.head(url)
        if response.status_code in [200,]:
            log.verbose("File", repr(filename), "is available from", repr(url))
        else:
            log.error("File", repr(filename), "failed HTTP HEAD with code =", response.status_code, "from", repr(url))
        
if __name__ == "__main__":
    sys.exit(CheckArchiveScript()())
