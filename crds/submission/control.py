"""This module provides a command line script to list, abort, and/or 
delete submissions by user or submission key.
"""

# ===================================================================

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import os
import shutil

from crds import cmdline, log, exceptions
from crds.client import api
from . import submit

# ===================================================================

class ControlSubmissionScript(cmdline.Script):
    """Command line script to control submissions."""

    description = """
This command can be used to list, abort, and or delete submissions.
"""

    epilog = """
XXXX TBD: under development  XXXXX

The crds.submission control command is a Swiss Army knife which can be used to
list, abort, or clean up submissions.  It has basically two modes of
operation:

1. It can operate with respect to a specific submission name.   These come from
command line submission output, automatic e-mails, or web-pages.

2. It can operate with respect to a user and act on all their submissions.

Only some submission states can be cleaned up file submitters.   Some states can
only be cleared by a server admin.
"""

    def add_args(self):
        """Add class-specifc command line parameters."""
        super(ControlSubmissionScript, self).add_args()
        self.add_argument("--submission-key", type=cmdline.process_key, default=None,
                          help="Name for a specific submission.")
        self.add_argument("--for-user", action="store_true",
                          help="Operate on all submissions for username.")
        self.add_argument("--any-user", action="store_true",
                          help="Operate on submissions for any/all users.")
        self.add_argument("--client", action="store_true",
                          help="Operate the client initiating states which start the submission.")
        self.add_argument("--active", action="store_true",
                          help="Operate on server submission states where CRDS is processing. Server admin only.")
        self.add_argument("--all-states", action="store_true",
                          help="Operate on all submission states.  WARNING: can delete completed states.  Server admin only.")
        self.add_argument("--abort", action="store_true",
                          help="Send a process cancellation message to the specified submission key.")
        self.add_argument("--delete", action="store_true",
                          help="Delete submission directories for the specified user or submission key.  Some restrictions.")
        self.add_argument("--list", action="store_true",
                          help="List the existing submission directories for the specified user or submission key.")
        self.add_argument("--cat", action="store_true",
                          help="Print out the .yaml manifests associated with the specified submissions.")

    @property
    def username(self):
        """Return the user's login name or the specified command line username."""
        return self.args.username if self.args.username else os.getlogin()

    def main(self):
        """Main processing for submisson control."""

        if not (self.args.submission_key or self.args.for_user or self.args.any_user):
            log.fatal_error("You must either specify --submission-key or --for-user or --any-user.")

        if self.args.any_user:
            self.args.username = "*"

        self.require_server_connection()

        if self.args.abort:
            self.abort()

        if self.args.list:
            self.list()

        if self.args.cat:
            self.cat()

        if self.args.delete:
            self.delete()

    def get_submission_paths(self):
        """Return the submission paths defined by the command line parameters
        and existing submissions.
        """
        paths = []
        if self.args.client:
            paths += submit.client_paths(
                self.observatory, self.username, self.args.submission_key)
        if self.args.active:
            paths += submit.active_paths(
                self.observatory, self.username, self.args.submission_key)
        if self.args.all_states:
            paths = submit.all_paths(
                self.observatory, self.username, self.args.submission_key)
        return paths

    def abort(self):
        """Send a request to the submission processor to abort the submission
        specified by explicit key.
        """
        if not self.args.submission_key:
            log.error("You must specify cancellations exactly by key.")
            return
        try:
            api.jpoll_abort(self.args.submission_key)
        except exceptions.OwningProcessAbortedError:
            log.info("Aborted",  repr(self.args.submission_key))
        else:
            log.info("No confirmation of process abort.")

    def list(self):
        """Print out the names of the submission paths."""
        for path in self.get_submission_paths():
            print(path)

    def cat(self):
        """Dump out the yaml manifests associated with each submission path."""
        for path in self.get_submission_paths():
            print("="*15, path, "="*15)
            manifest = os.path.join(path, "submission.yaml")
            with log.error_on_exception("Failed dumping manifest", repr(manifest)):
                print(open(manifest).read())
        
    def delete(self):
        """Delete the submission paths from the file system."""
        for path in self.get_submission_paths():
            shutil.rmtree(path)

# ===================================================================

if __name__ == "__main__":
    sys.exit(ControlSubmissionScript()())

