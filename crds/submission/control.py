"""This module provides a command line script to list, cancel, and/or 
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
This command can be used to list, cancel, and or delete submissions.
"""

    epilog = """
XXXX TBD: under development  XXXXX

The crds.submission control command is a Swiss Army knife which can be used to
list, cancel, or clean up submissions.  It has basically two modes of
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
        self.add_argument("--username", type=str, default=None,
                          help="Operate on submissions with respect to username.   Defaults to login name.")
        self.add_argument("--client", action="store_true",
                          help="Operate the client initiating states which start the submission.")
        self.add_argument("--active", action="store_true",
                          help="Operate on server submission states where CRDS is processing. Server admin only.")
        self.add_argument("--all", action="store_true",
                          help="Operate on all submission states.  WARNING: can delete completed states.  Server admin only.")
        self.add_argument("--cancel", action="store_true",
                          help="Send a process cancellation message to the specified submission key.")
        self.add_argument("--delete", action="store_true",
                          help="Delete submission directories for the specified user or submission key.  Some restrictions.")
        self.add_argument("--list", action="store_true",
                          help="List the existing submission directories for the specified user or submission key.")

    @property
    def username(self):
        """Return the user's login name or the specified command line username."""
        return self.args.username if self.args.username else os.getlogin()

    def main(self):
        """Main processing for submisson control."""

        if self.args.submission_key is None and not self.args.for_user:
            log.fatal_error("You must either specify --submission-key or --for-user.")

        self.require_server_connection()

        if self.args.cancel:
            self.cancel()

        if self.args.list:
            self.list()

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
        if self.args.all:
            paths = submit.all_paths(
                self.observatory, self.username, self.args.submission_key)
        return paths

    def cancel(self):
        """"""
        if not self.args.submission_key:
            log.error("You must specify cancellations exactly by key.")
            return
        try:
            api.jpoll_cancel(self.args.submission_key)
        except exceptions.OwningProcessCancelledError:
            log.info("Cancelled",  repr(self.args.submission_key))
        else:
            log.info("No confirmation of cancellation.")

    def list(self):
        """Print out the names of the submission paths."""
        for path in self.get_submission_paths():
            print(path)

    def delete(self):
        """Delete the submission paths from the file system."""
        for path in self.get_submission_paths():
            shutil.rmtree(path)

# ===================================================================

if __name__ == "__main__":
    sys.exit(ControlSubmissionScript()())

