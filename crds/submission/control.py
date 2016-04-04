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

from crds import cmdline, log
from crds.client import api
from . import submit

# ===================================================================

class ControlSubmissionScript(cmdline.Script):
    """Command line script to control submissions."""

    description = """
This command can be used to list, cancel, and or delete submissions.
"""

    epilog = """
"""

    def add_args(self):
        """Add class-specifc command line parameters."""
        super(ControlSubmissionScript, self).add_args()
        self.add_argument("--submission-key", type=cmdline.process_key, default=None,
                          help="Key used to connect to remote process status stream.")
        self.add_argument("--for-user", action="store_true",
                          help="When set, operate on all submissions for username.  Omit --submission-key.")
        self.add_argument("--username", type=str, default=None,
                          help="Override login user name with the specified user name.")
        self.add_argument("--active", action="store_true",
                          help="Operate on active submission directories.")
        self.add_argument("--all", action="store_true",
                          help="Operate on all submission directories for the specified submission key.")
        self.add_argument("--cancel", action="store_true",
                          help="Send a process cancellation message to the specified submission key.")
        self.add_argument("--delete", action="store_true",
                          help="Delete submission directories for the specified user or submission key.")
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
            api.jpoll_cancel(self.args.submission_key)

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

