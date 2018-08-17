"""This module provides a command line interface for doing CRDS file submissions."""
import sys
import os
import os.path
import socket
import time

from crds.core import log, config, utils, pysh, cmdline
from crds.core.log import srepr
from . import web, background, monitor
from crds.client import api

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
        self.jpoll_key = None

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
        self.add_argument("--submission-kind", type=str, choices=["batch","certify","none"], default="batch", # mapping, reference
                          help="Which form of submission to perform.  Defaults to batch.")
        self.add_argument("--wipe-existing-files", action="store_true", 
                          help="Before performing action,  remove all files from the appropriate CRDS ingest directory.")
        self.add_argument("--keep-existing-files", action="store_true", 
                          help="Don't recopy files already in the server ingest directory that have the correct length.")
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
        assert not (self.args.keep_existing_files and self.args.wipe_existing_files), \
            "--keep-existing-files and --wipe-existing-files are mutually exclusive."

    # -------------------------------------------------------------------------------------------------

    def ingest_files(self):
        """Copy self.files into the user's ingest directory on the CRDS server."""
        stats = self._start_stats()
        destination = self.submission_info.ingest_dir
        host, path = destination.split(":")
        self.ensure_ingest_exists(host, path)
        total_size = utils.total_size(self.files)

        ingest_info = self.get_ingested_files()

        self.scan_for_nonsubmitted_ingests(ingest_info)

        remaining_files = self.keep_existing_files(ingest_info, self.files) \
            if self.args.keep_existing_files else self.files

        for i, filename in enumerate(remaining_files):
            file_size = utils.file_size(filename)
            log.info("Copy started", repr(filename), "[", i+1, "/", len(self.files), " files ]",
                     "[", utils.human_format_number(file_size), 
                     "/", utils.human_format_number(total_size), " bytes ]")
            self.copy_file(filename, path, destination)
            stats.increment("bytes", file_size)
            stats.increment("files", 1)
            stats.log_status("files", "Copy complete", len(self.files))
            stats.log_status("bytes", "Copy complete", total_size)

        log.divider(func=log.verbose)
        stats.report()
        log.divider(char="=")

    def ensure_ingest_exists(self, host, path):
        """Ensure the destination directory for submitted files on the CRDS server exist, or create it."""
        self.possibly_remote_command(host, "mkdir -p " + path)
        self.possibly_remote_command(host, "chmod 770 " + path)
            
    def possibly_remote_command(self, host, cmd, verbosity=65):
        """If `host` is the localhost,  excecute `cmd` in subshell.  Otherwise execute `cmd` by ssh."""
        if host.startswith(socket.gethostname()):
            output = pysh.out_err(cmd, trace_commands=log.get_verbose() >= verbosity)
        else:
            output = pysh.out_err("ssh   ${host}    ${cmd}", trace_commands=log.get_verbose() >= verbosity)
        if output:
            log.verbose(output, verbosity=verbosity)
   
    #def upload_file(self, name, path, destination):
    #    self.connection.upload_file('/upload/alt_new/', file=name)
    #    # self.connection.repost('/upload/alt_new/', file=open(name,"rb"))
    #    # self.connection.repost('/upload/alt_new/', file = open(name, "rb"))

    def scan_for_nonsubmitted_ingests(self, ingest_info):
        """Check for junk in the submitter's ingest directory,  left over files not
        in the current submission and fail if found.
        """
        submitted_basenames = [ os.path.basename(filepath) for filepath in self.files ]
        for ingested in ingest_info.keys():
            if ingested not in submitted_basenames:
                log.fatal_error(
                    "Non-submitted file", log.srepr(ingested), 
                    "is already in the CRDS server's ingest directory.  Delete it (--wipe-existing-files?) or submit it.")

    def keep_existing_files(self, ingest_info, files):
        """Keep files which have already been copied and have the correct server side
        length.  This can save *hours* of copy time for repeat submissions.
        """
        for filename in files[:]:
            local_size = utils.file_size(filename)
            basename = os.path.basename(filename)
            try:
                existing_size = int(ingest_info[basename]["size"])
            except:
                log.info("File", repr(filename), 
                         "does not exist in ingest directory and will be copied to CRDS server.")
                continue
            if local_size == existing_size:
                log.info("File", repr(filename), 
                         "has already been copied and has correct length on CRDS server", 
                         utils.human_format_number(existing_size))
                files.remove(filename)
            else:
                log.info("File", repr(filename), 
                         "exists but has incorrect size and must be recopied.  Deleting old ingest.")
                self.connection.get(ingest_info[basename]["delete_url"])
        return files

    def get_ingested_files(self):
        """Return the server-side JSON info on the files already in the submitter's ingest directory."""
        log.info("Determining existing files.")
        result = self.connection.get('/upload/list/').json()
        log.verbose("JSON info on existing ingested files:\n", log.PP(result))
        if "files" in result and isinstance(result["files"], list):
            return { info["name"] : info for info in result["files"] }
        else:
            return { info["name"] : info for info in result }

    def copy_file(self, name, path, destination):
        """Perform a cp-based or scp-based copy of file `name`,  either to `path` or
        a host location based on `destination` and `name`,  depending on whether or not 
        the submitter's submission directory is visible from the host running this script.
        """
        try:
            verbose = "-v" if log.get_verbose() >= 65 else ""
            if destination.startswith(socket.gethostname()):
                output = pysh.out_err("cp ${verbose} ${name} ${path}", raise_on_error=True, trace_commands=log.get_verbose() >= 65)
            else:
                bname = os.path.basename(name)
                output = pysh.out_err("scp ${verbose} ${name} ${destination}/${bname}", raise_on_error=True, trace_commands=log.get_verbose() >= 65)
            if output:
                log.verbose(output)
            return output
        except Exception as exc:
            log.fatal_error("File transfer failed for: " + repr(name), "-->", repr(destination))
            
    def wipe_files(self):
        """Copy self.files into the user's ingest directory on the CRDS server."""
        destination = self.submission_info.ingest_dir
        log.divider(name="wipe files", char="=")
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
        total_bytes = utils.total_size(self.files)
        stats = utils.TimingStats(output=log.verbose)
        stats.start()
        log.divider(name="ingest files", char="=")
        log.info("Copying", len(self.files), "file(s) totalling", utils.human_format_number(total_bytes), "bytes")
        log.divider(func=log.verbose)
        return stats

    # -------------------------------------------------------------------------------------------------
        
    def jpoll_open_channel(self):
        """Mimic opening a JPOLL status channel as do pages with real-time status."""
        log.info("Preparing server logging.")
        response = self.connection.get("/jpoll/open_channel")
        return response.json()

    # -------------------------------------------------------------------------------------------------

    def certify_files(self):
        """Run the CRDS server Certify Files page on `filepaths`."""
        self.ingest_files()
        t = self.connection.repost_start(
            "/certify/", pmap_name=self.pmap_name, pmap_mode=self.pmap_mode,
            compare_old_reference=not self.args.dont_compare_old_reference)
        time.sleep(10)
        return t
    
    # -------------------------------------------------------------------------------------------------
        
    def batch_submit_references(self):
        """Do a web re-post to the batch submit references web page."""
        return self._submission("/batch_submit_references/")
        
    def submit_references(self):
        """Do a web re-post to the submit references web page."""
        return self._submission("/submit/reference/")
        
    def submit_mappings(self):
        """Do a web re-post to the submit mappings web page."""
        return self._submission("/submit/mapping/")

    def _submission(self, relative_url):
        """Do a generic submission re-post to the specified relative_url."""
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
        time.sleep(10)
        return completion_args

    def submission_complete(self, args):
        """Threaded completion function for any submission,  returns web response."""
        return self.connection.repost_complete(args)

    @background.background
    def monitor(self):
        """Run a background job to monitor the submission on the server and output log info."""
        extra_params = ""
        if "--log-time" in sys.argv:
            extra_params = "--log-time"
        submission_monitor = monitor.MonitorScript("crds.monitor --key {} --poll {} {}".format(
            self.jpoll_key, 3, extra_params), reset_log=False)
        return submission_monitor()

    def monitor_complete(self, monitor_future):
        """Wait for the monitor job to complete and return the result."""
        return background.background_complete(monitor_future)

    # -------------------------------------------------------------------------------------------------

    def login(self):
        """Log in to the CRDS server using server user credentials."""
        log.info("Logging in aquiring lock.")
        self.connection.fail_if_existing_lock()
        self.connection.login()

    def logout(self):
        """Log out of the CRDS server,  releasing any lock held by this user."""
        log.info("Logging out releasing lock.")
        self.connection.login()
        self.connection.logout()
        
    def main(self):
        """Main control flow of submission directory and request manifest creation."""

        log.divider("setting up", char="=")

        self.require_server_connection()
        
        self.finish_parameters()

        if self.args.logout:
            return self.logout()

        self.submission = self.create_submission()

        self.login()

        if self.args.wipe_existing_files:
            self.wipe_files()

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

        if self.args.wait_for_completion:
            self.submission_complete(submit_future)

        if self.args.monitor_processing:
            self.monitor_complete(monitor_future)

        log.standard_status()
        return log.errors()

# ===================================================================

# ===================================================================

