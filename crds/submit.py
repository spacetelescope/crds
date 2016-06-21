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
import socket
import time

from crds import log, config, cmdline, utils, timestamp, web, pysh, exceptions
from crds import monitor
from crds.client import api
from crds.log import srepr

# ===================================================================

class ReferenceSubmissionScript(cmdline.Script):
    """Command line script file submission script."""

    description = """
This script initiates a CRDS file submission from the command line rather than the
web server.   Once submitted the submission will be processed on the CRDS server.
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
        self.connection = None
        self.submission = None
        self.submission_info = None
        self.pmap_mode = None
        self.pmap_name = None
        self.instruments_filekinds = None
        self.instrument = None
        self.base_url = None

    def create_submission(self):
        """Create a Submission object based on script / command-line parameters."""
        return utils.Struct(
            uploaded_files = { os.path.basename(filepath) : filepath for filepath in self.files } if self.args.files else {},
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
                          help="Set of CRDS rules these files will be added to.  Defaults to edit context.")
        self.add_argument("--change-level", type=str, choices=["SEVERE","MODERATE","TRIVIAL"], default="SEVERE", 
                          help="The degree to which the new files are expected to impact science results.")
        self.add_argument("--creator", type=str, 
                          help="Author of this set of references,  most likely not file submitter.  Can be comma separated list of people in quotes.")
        self.add_argument("--description", type=str, default=None,
                          help="Brief description of the purpose of this delivery, mention instrument and type(s).")
        self.add_argument("--dont-auto-rename", action="store_true", 
                          help="Unless specified, CRDS will automatically rename incoming files.")
        self.add_argument("--dont-compare-old-reference", action="store_true",
                          help="Unless specified, CRDS will check the current reference against any reference it replaces, as appropriate and possible.")
        self.add_argument("--username", type=str, default=None, help="CRDS username of file submitter.")
        self.add_argument("--monitor-processing", action="store_true", 
                          help="Monitor CRDS processing for on-going status and final confirmation link.")
        self.add_argument("--wait-for-completion", action="store_true",
                          help="Wait until the server reports that the submission is done before exiting.  Otherwise use e-mail.")
        self.add_argument("--submission-kind", type=str, choices=["batch","mapping","references", "certify", "none"], default="batch",
                          help="Which form of submission to perform.  Defaults to batch.")
        self.add_argument("--wipe", action="store_true", 
                          help="Before performing action,  remove all files from the appropriate CRDS ingest directory.")
        self.add_argument("--logout", action="store_true", 
                          help="Log out of the server,  dropping any lock.")

    # -------------------------------------------------------------------------------------------------
        
    def finish_parameters(self):
        """Finish up parameter setup which requires parsed command line arguments."""
        self.username = self.args.username or config.get_username()
        password = config.get_password()
        self.base_url = config.get_server_url(self.observatory)
        self.submission_info = api.get_submission_info(self.observatory, self.username)
        self.instruments_filekinds = utils.get_instruments_filekinds(self.observatory, self.files) if self.args.files else {}
        self.instrument = list(self.instruments_filekinds.keys())[0] if len(self.instruments_filekinds) == 1 else "none"
        self.connection = web.CrdsDjangoConnection(
            locked_instrument=self.instrument, username=self.username, password=password, base_url=self.base_url)
        if self.args.derive_from_context in ["edit", "ops"]:
            self.pmap_mode = "pmap_" + self.args.derive_from_context
            self.pmap_name = self.resolve_context(self.observatory + "-" + self.args.derive_from_context)
        else:
            self.pmap_mode = "pmap_text"
            self.pmap_name = self.args.derive_from_context
        assert config.is_context(self.pmap_name), "Invalid pmap_name " + repr(self.pmap_name)

    # -------------------------------------------------------------------------------------------------
        
    def ingest_files(self):
        """Copy self.files into the user's ingest directory on the CRDS server."""
        stats = self._start_stats()
        destination = self.submission_info.ingest_dir
        host, path = destination.split(":")
        for name in self.files:
            self.copy_file(name, path, destination)
            stats.increment("bytes", os.stat(name).st_size)
            stats.increment("files", 1)
        log.divider()
        stats.report()
        log.divider(char="=", func=log.info)

    def upload_file(self, name, path, destination):
        self.connection.upload_file('/upload/alt_new/', file=name)
        # self.connection.repost('/upload/alt_new/', file=open(name,"rb"))
        # self.connection.repost('/upload/alt_new/', file = open(name, "rb"))

    def copy_file(self, name, path, destination):
        try:
            log.info("Copying", repr(name))
            if destination.startswith(socket.gethostname()):
                output = pysh.out_err("cp -v ${name} ${path}", raise_on_error=True, trace_commands=log.get_verbose() >= 50)
            else:
                bname = os.path.basename(name)
                output = pysh.out_err("scp -v ${name} ${destination}/${bname}", raise_on_error=True, trace_commands=log.get_verbose() >= 50)
            if output:
                log.verbose(output)
            return output
        except Exception as exc:
            log.fatal_error("File transfer failed for: " + repr(name), "-->", repr(destination))

    def wipe_files(self):
        """Copy self.files into the user's ingest directory on the CRDS server."""
        destination = self.submission_info.ingest_dir
        log.divider(name="wipe files", char="=", func=log.info)
        log.info("Wiping files at", repr(destination))
        host, path = destination.split(":")
        if destination.startswith(socket.gethostname()):
            output = pysh.out_err("rm -vf  ${path}/*")
        else:
            output = pysh.out_err("ssh ${host} rm -vf ${path}/*")
        if output:
            log.verbose(output)

    def _start_stats(self):
        """Helper method to initialize stats keeping for ingest."""
        total_bytes = 0
        for name in self.files:
            total_bytes += os.stat(name).st_size
        stats = utils.TimingStats(output=log.verbose)
        stats.start()
        log.divider(name="ingest files", char="=", func=log.info)
        log.info("Copying", len(self.files), "file(s) totalling", total_bytes, "bytes")
        log.divider()
        return stats

    # -------------------------------------------------------------------------------------------------
        
    def jpoll_open_channel(self):
        """Mimic opening a JPOLL status channel as do pages with real-time status."""
        response = self.connection.get("/jpoll/open_channel")
        return response.json()

    # -------------------------------------------------------------------------------------------------
        
    def certify_files(self):
        """Run the CRDS server Certify Files page on `filepaths`."""
        self.ingest_files()
        self.connection.repost(
            "/certify/", pmap_name=self.pmap_name, pmap_mode=self.pmap_mode,
            compare_old_reference=not self.args.dont_compare_old_reference)
        self.connection.logout()

    # -------------------------------------------------------------------------------------------------
        
    def batch_submit_references(self):
        return self._submission("/batch_submit_references/")
        
    def submit_references(self):
        return self._submission("/submit/reference/")
        
    def submit_mappings(self):
        return self._submission("/submit/mapping/")

    def _submission(self, relative_url):
        assert self.args.description is not None, "You must supply a --description for this function."
        self.ingest_files()
        log.info("Posting web request for", srepr(relative_url))
        completion_args = self.connection.repost_start(
            relative_url,
            pmap_mode = self.pmap_mode,
            pmap_name = self.pmap_name,
            instrument = self.instrument,
            change_level=self.args.change_level,
            creator=self.args.creator,
            description=self.args.description,
            auto_rename=not self.args.dont_auto_rename,
            compare_old_reference=not self.args.dont_compare_old_reference,
            )
        # give POST time to complete send, not response
        time.sleep(5.0)
        return completion_args

    def submission_complete(self, args):
        """Threaded completion function for any submission,  returns web response."""
        return self.connection.repost_complete(args)

    # @web.background
    def monitor(self):
        """Run a background job to monitor the submission on the server and output log info."""
        submission_monitor = monitor.MonitorScript("crds.submission.monitor --submission-key {} --poll {}".format(self.jpoll_key, 3))
        return submission_monitor()

    def monitor_complete(self, monitor_future):
        """Wait for the monitor job to complete and return the result."""
        return self.connection.background_complete(monitor_future)

    # -------------------------------------------------------------------------------------------------
        
    def main(self):
        """Main control flow of submission directory and request manifest creation."""

        self.require_server_connection()
        
        self.finish_parameters()

        if self.args.logout:
            self.connection.login()
            self.connection.logout()
            return

        self.submission = self.create_submission()

        if self.args.wipe:
            self.wipe_files()

        self.connection.login()

        self.jpoll_key = self.jpoll_open_channel()

        if self.args.submission_kind == "batch":
            submit_future = self.batch_submit_references()
        elif self.args.submission_kind == "certify":
            submit_future = self.certify_files()
        elif self.args.submission_kind == "references":
            submit_future = self.submit_references()
        elif self.args.submission_kind == "mappings":
            submit_future = self.submit_mappings()

        if self.args.monitor_processing:
            monitor_future = self.monitor()

        if self.args.monitor_processing:
            self.monitor_complete(monitor_future)

        if self.args.wait_for_completion:
            self.submission_complete(submit_future)

        log.standard_status()
        return log.errors()

# ===================================================================

# ===================================================================

if __name__ == "__main__":
    sys.exit(ReferenceSubmissionScript()())

