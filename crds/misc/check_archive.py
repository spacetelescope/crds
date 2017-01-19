"""This module is used to verify the availability of a list of CRDS files
at the archive web server.
"""

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os.path
import sys

import requests

from crds.core import python23, log, config, utils, cmdline
from crds.client import api

class CheckArchiveScript(cmdline.Script):
    """Command line script for for checking archive file availability."""

    description =  """Command line script for for checking archive file availability."""
        
    epilog = """
Checking out the archive with respect to CRDS file availability
and setting up a pipeline cache might have a few stages:

1. Run crds.list to generate a list of files to check, for example for
all contexts, do this:

    % setenv CRDS_SERVER_URL https://jwst-crds.stsci.edu
    % setenv CRDS_PATH $HOME/crds_cache_ops
    % python -m crds.list --all --mappings --references >files.b6

This captures the file list with respect to the CRDS OPS server which
during the development period directly distributes files and is a
complete "reference" copy.

2. Run crds.misc.check_archive to query the archive server with HTTP HEAD for each of the files:

    % setenv CRDS_SERVER_URL https://jwst-crds-b6it.stsci.edu
    % setenv CRDS_PATH $HOME/crds_cache_b6it
    % python -m crds.misc.check_archive --files @files.b6 --dump-good-files --stats > all.b6it.archive

This checks the file list in files.b6 against the CRDS B6 server
database and whatever archive URL that server is configured to use,
nominally the B6 archive server.

crds.misc.check_archive currently checks each file for availability and
correct length with respect to the CRDS catalog.  A status line for
each bad file, or all files, is printed to standard out, in this case
captured to output file all.b6.archive.  e.g. status like:

    jwst_nirspec_superbias_0001.rmap 15a45e1ef114b1d5dc2017fd847830fd3c3eaac6 518 ok
    jwst_nirspec_superbias_0002.rmap 07c94beb372396253dd42c2ff4f2c54ac678d55c 596 ok
    jwst_nirspec_superbias_0003.rmap a031720e6ffeec9d730ec0051a6cea1215e7054f 666 ok

ERROR messages for each problem (missing or length) are printed to stderr

3. Once the archive is looking good,  sync all the CRDS rules to a local cache:
    
    % python -m crds.sync --all --stats --check-sha1sum

which will verify rules download, loadability, and exact contents with respect to 
the CRDS server database.

4. Once all of these trial runs are completed,  the appropriate archive pipeline
is probably ready to run the cron_sync script to initialize their CRDS cache from 
the archive and appropriate CRDS server.
    """

    def __init__(self, *args, **keys):
        super(CheckArchiveScript, self).__init__(*args, **keys)
        self.file_info = {}
        self.missing_files = []
        self.bad_length_files = []

    def add_args(self):
        """Add additional custom parameter for CheckArchiveScript."""
        self.add_argument('--files', nargs='*', dest='files', default=[],
                          help='names of files to check for archive availability.')
        self.add_argument('--dump-good-files', action='store_true',
                          help='dump info on good files as well as those with errors.')
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
        self.file_info = api.get_file_info_map(self.observatory, self.files, fields=["size", "sha1sum"])
        for filename in self.files:
            self.verify_archive_file(filename)
            stats.increment("files")
        self.print_files()
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
            self.check_length(filename, response)
        else:
            log.error("File", repr(filename), "failed HTTP HEAD with code =", response.status_code, "from", repr(url))
            self.missing_files.append(filename)

    def check_length(self, filename, response):
        """Check the content-length reported by HEAD against the CRDS database's file size."""
        archive_size = python23.long(response.headers["content-length"])
        crds_size = python23.long(self.file_info[filename]["size"])
        if archive_size != crds_size:
            log.error("File", repr(filename), "available but length bad.  crds size:", crds_size,
                      "archive size:", archive_size)
            self.bad_length_files.append(filename)
        else:
            log.verbose("File", repr(filename), "lengths agree:", crds_size)

    def print_files(self):
        """Print out info on all missing or bad files."""
        for filename in self.missing_files:
            self.dump_file(filename, "bad_missing")
        for filename in self.bad_length_files:
            self.dump_file(filename, "bad_length")
        if self.args.dump_good_files:
            for filename in self.files:
                if filename not in self.missing_files + self.bad_length_files:
                    self.dump_file(filename, "ok")
            
    def dump_file(self, filename, kind):
        """Dump info about one file annotated with string `kind`."""
        print(filename, self.file_info[filename]["sha1sum"], self.file_info[filename]["size"], kind)
        
if __name__ == "__main__":
    sys.exit(CheckArchiveScript()())