"""This module provides a command line interface for doing CRDS file submissions."""

# ===================================================================

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import os
import os.path
import shutil
import glob
import yaml

from crds import log, cmdline, utils, timestamp, web
from crds.submission import monitor
from crds.client import api
from crds.log import srepr

# ===================================================================

class ReferenceSubmissionScript(cmdline.Script):
    """Command line script file submission script."""

    description = """
This script initiates a CRDS file submission from the command line rather than the
web server.   Once submitted the submission will be processed on the CRDS server,
optionally monitored on a web page, via this script, or as a separate command line
program crds.monitor.
"""

    epilog = """
Typical usage of this script would be something like the following.  Users of
this command line interface must be members of the CRDS operators group
"crdsoper".
"""

    # Override CRDS default behavior of looking in cache for path-less files.
    locate_file = cmdline.Script.locate_file_outside_cache

    def __init__(self, *args, **keys):

        """Initializes a reference file submission script."""

        super(ReferenceSubmissionScript, self).__init__(*args, **keys)

        self.username = None
        self.session = None
        self.submission = None
        self.submission_info = None
        self.pmap_mode = None
        self.pmap_name = None
        self.instruments_filekinds = None
        self.instrument = None

    def create_submission(self):
        """Create a Submission object based on script / command-line parameters."""
        return utils.Struct(
            uploaded_files = { os.path.basename(filepath) : filepath for filepath in self.files },
            description = self.args.description,
            username = self.username,
            creator_name = self.args.creator,
            change_level = self.args.change_level,
            auto_rename = not self.args.dont_auto_rename,
            compare_old_reference = not self.args.dont_compare_old_reference,
            submission_kind = self.args.submission_kind,
            observatory = self.observatory,
            pmap_mode = self.pmap_mode,
            pmap_name = self.pmap_name,
            agent = "command-line-script"
            )

    def add_args(self):
        """Add additional command-line parameters for file submissions not found in baseclass Script."""
        super(ReferenceSubmissionScript, self).add_args()
        self.add_argument("--files", nargs="*", help="Files to submit.  A file preceded with @ is treated as containing the list of files.")
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
        self.add_argument("--username", type=str, default=None, help="CRDS username of file submitter.")
        self.add_argument("--monitor-processing", action="store_true", 
                          help="Monitor CRDS processing for on-going status and final confirmation link.")
        self.add_argument("--submission-kind", type=str, choices=["batch","mapping","references"], default="batch",
                          help="Which form of submission to perform.")

    def finish_parameters(self):
        """Finish up parameter setup which requires parsed command line arguments."""
        self.username = self.args.username or config.USERNAME.get()
        self.submission_info = api.get_submission_info(self.observatory, self.username)
        self.instruments_filekinds = utils.get_instruments_filekinds(self.observatory, self.uploaded_files)
        self.locked_instrument = self.instruments_filekinds.keys()[0] if len(self.instruments_filekinds) == 1 else "none"
        self.session = web.CrdsDjangoConnection(
            locked_instrument=locked_instrument, username=self.username, observatory=self.observatory,
            ingest_destination=self.submission_info.ingest_dir)
        if self.args.derive_from_context in ["edit", "ops"]:
            self.pmap_mode = "pmap_" + self.args.derive_from_context
            self.pmap_name = self.resolve_context(self.observatory + "-" + self.args.derive_from_context)
        else:
            self.pmap_mode = "pmap_text"
            self.pmap_name = self.args.derive_from_context

    def post_batch_submit_references(self):
        self.session.ingest_files(self.uploaded_files)
        self.jpoll_open()
        response = self.session.repost(
            "/batch_submit_references/", 
            pmap_mode = self.pmap_mode,
            pmap_name = self.pmap_name,
            instrument = self.instrument,
            change_level=self.args.change_level,
            creator=self.args.creator,
            description=self.args.description,
            auto_rename=not self.args.dont_auto_rename,
            compare_old_reference=not self.args.dont_compare_old_reference,
            )

    def main(self):
        """Main control flow of submission directory and request manifest creation."""

        self.require_server_connection()
        
        self.finish_parameters()

        self.submission = self.create_submission()

        self.login()

        self.post_batch_submit_references()

# ===================================================================

# ===================================================================

if __name__ == "__main__":
    sys.exit(ReferenceSubmissionScript()())

