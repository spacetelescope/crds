"""This module provides a command line interface for doing CRDS file submissions.

It supports reference file submissions only.
"""

# ===================================================================

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import os
import os.path
import shutil

from crds import log, cmdline, config, utils
from crds.client import api

# ===================================================================

INGEST_PATHS = {
    "https://jwst-crds.stsci.edu" : "/ifs/crds/jwst/ops/server_files/ingest",
    "https://jwst-crds-b6it.stsci.edu" : "/ifs/crds/jwst/b6it/server_files/ingest",
    "https://hst-crds.stsci.edu" : "/ifs/crds/hst/ops/server_files/ingest",
}

# ===================================================================

class ReferenceSubmissionScript(cmdline.Script):
    """Command line script file submission script."""

    description = """
"""

    epilog = """
"""
    
    def add_args(self):
        super(ReferenceSubmissionScript, self).add_args()
        self.add_argument("--files", nargs="+", help="Files to submit.  A file preceded with @ is treated as containing the list of files.")
        self.add_argument("--derive-from-context", type=cmdline.context_spec, default="edit",
                          help="Set of CRDS rules these files will be added to.")
        self.add_argument("--change-level", type=str, choices=["SEVERE","MODERATE","TRIVIAL"], default="SEVERE", 
                          help="The degree to which the new files are expected to impact science results.")
        self.add_argument("--creator", type=str, 
                          help="Author of this set of references,  most likely not file submitter.")
        self.add_argument("--description", type=str,
                          help="Brief description of the purpose of this delivery, mention instrument and type(s).")
        self.add_argument("--dont-auto-rename", action="store_true", 
                          help="Unless specified, CRDS will automatically rename incoming files.")
        self.add_argument("--dont-compare-old-reference", action="store_true",
                          help="Unless specified, CRDS will check the current reference against any reference it replaces, as appropriate and possible.")
        # self.add_argument("--username", type=str, default=None, help="CRDS username of file submitter.")
        # self.add_argument("--password", type=str, default=None, help="CRDS password of file submitter.")

        # self.add_argument("--dry-run", type=bool, action="store_true",
        #                   help="")

    def main(self):
        """
        Process command line parameters in to a context and list of
        reference files.   Print out the match tuples within the context
        which contain the reference files.
        """
        self.username = os.getlogin()
        if self.args.derive_from_context in ["edit", "ops"]:
            self.args.derive_from_context = self.observatory + "-" + self.args.derive_from_context
        # self.trial_certify_files()
        # self.trial_refactor_rules()
        # if log.errors() and not self.args.force_submission:
        #     return log.errors()
        with log.fatal_error_on_exception("copying files to server ingest directory."):
            self.copy_files()
        # with log.fatal_error_on_exception("writing submission manifest file."):
        #     self.write_yaml_manifest()
        with log.fatal_error_on_exception("submitting files"):
            handle = self.submit_files()
        with log.fatal_error_on_exception("monitoring submission processing."):
            confirm_link = self.monitor_processing(handle)
        log.info("File submission ready for confirmation at:", log.srepr(confirm_link))
        return log.errors()

    locate_file = cmdline.Script.locate_file_outside_cache

    def check_delivery(self):
        ifmapping = self.get_instruments_and_filekinds(self.files)
        assert len(ifmapping) == 1, \
            "Only submit files for one instrument not: " + repr(ifmapping.keys())

    @property
    def ingest_dir(self):
        # ingest_path = api.get_ingest_directory(self.username)
        ingest_path = INGEST_PATHS[config.get_server_url(self.observatory)[:-1]]
        return os.path.join(ingest_path, self.username)
        
    def copy_files(self):
        for filepath in self.files:
            if filepath.startswith(self.ingest_dir):
                log.info("File", repr(filepath), "is already in your ingest directory.  Skipping copy.")
                continue
            else:
                destpath = os.path.join(self.ingest_dir, os.path.basename(filepath))
                log.info("Copying", repr(filepath), "to", repr(destpath))
                utils.ensure_dir_exists(destpath)
                shutil.copyfile(filepath, destpath)

    def submit_files(self):
        values = {
            "description": self.args.description,
            "creator" : self.args.creator,
            "change_level": self.args.change_level.upper(),
            "auto_rename" : not self.args.dont_auto_rename,
            "compare_old_reference" : not self.args.dont_compare_old_reference
            }
        return None

    def monitor_processing(self, handle):
        pass

# ===================================================================

if __name__ == "__main__":
    sys.exit(ReferenceSubmissionScript()())

