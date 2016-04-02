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

from crds import log, cmdline, utils, timestamp, monitor
from crds.client import api

# ===================================================================

SUBMISSION_DEFS = [
    ("creating",   0770),  # This submission code is still encoding the submission in user-space
    ("submitted",  0770),  # This submission is ready for pick-up by the background processor
    ("processing", 0740),  # The background processor is running
    ("confirming", 0740),  # The background processor has completed and the results are ready for review
    ("failed",     0740),  # CRDS detected a fatal error in the submission content forcing cancellation
    ("confirmed",  0740),  # The user has confirmed the submission
    ("aborted",    0740),  # The user killed the submission early with an RPC.
    ("cancelled",  0740),  # The user rejected the submission upon review
    ("crashed",    0740),  # An untrapped exception occurred
    ]

STATE_MODE_MAP = dict(SUBMISSION_DEFS)

CLIENT_STATES = { 
    "creating", 
    "submitted" 
    }

ACTIVE_STATES = {
    "processing",
    "confirming",
    }

INACTIVE_STATES = {
    "confirmed",
    "failed",
    "aborted",
    "cancelled",
    "crashed"
    }

SUBMISSION_STATES = CLIENT_STATES | ACTIVE_STATES | INACTIVE_STATES
assert SUBMISSION_STATES == set(STATE_MODE_MAP.keys())

def check_state(state):
    """Raise an exception if `state` is not a known valid state."""
    assert state in STATE_MODE_MAP, "Submission state " + repr(state) + "is not a vaild state."
        
# ===================================================================

@utils.cached
def get_submission_info(observatory, username):
    """Return parameter information from the server required to perform
    command line file submissions.
    """
    return api.get_submission_info(observatory, username)

# ===================================================================

def new_submission_name(user_name, instrument):
    """Return a new unique name for a submission based on `user` and `instrument`."""
    # Designed to sort by instrument and date.
    return "-".join([instrument, timestamp.now("T"), user_name])

def instrument_name(submission_name):
    """Return the instrument name associated with this submission."""        
    return submission_name.split("-")[0]

# ===================================================================

class Submission(object):

    """Base class for file submissions,  carrier object for submission meta-data and filenames."""
    
    def __init__(self, pmap_name, uploaded_files, description, user_name, creator_name="UNKNOWN",
                 change_level="SEVERE", auto_rename=True, compare_old_reference=True,
                 submission_kind=None, observatory=None, pmap_mode=None, instruments_filekinds=None, 
                 submission_key=None, **keys):

        """Initialize a submission object in memory."""

        self.pmap_name = str(pmap_name)
        self.pmap_mode = str(pmap_mode)
        self.uploaded_files = uploaded_files
        self.description = str(description)
        self.user_name = str(user_name)
        self.creator_name = str(creator_name)
        self.change_level = str(change_level).upper()
        self.auto_rename = bool(auto_rename)
        self.compare_old_reference = bool(compare_old_reference)
        self.submission_kind = submission_kind
        self.observatory = observatory
        self.instruments_filekinds = instruments_filekinds
        instrument = str(instruments_filekinds.keys()[0])
        self.submission_key = submission_key or new_submission_name(self.user_name, instrument)
        self._keys = keys

    def state_path(self, state, *subdirs):
        """Return the path of the top level directory for `state` which has links
        for all submissions in `state`.

        Returns: ".../submissions/<state>"

        This enables submissions to migrate through top level state directories during
        the course of processing.
        """
        return os.path.join(self.submission_info.submission_subdir, state, *subdirs)

    def path(self, *subdirs):
        """Create a path in the submission tree where subdirs[0] describes the
        state of the submission (and contains many submissions) and subdirs[1:]
        further describe this individual submission and it's subdirectories.
        
        Returns: ".../submissions/<state>/<submission_key>/<submission_subpath...>"
        """
        state, submission_subpath = subdirs[0], subdirs[1:]
        return os.path.join(self.state_path(state), self.submission_key, *submission_subpath)

    @property
    def submission_info(self):
        """A Struct of parameters defined by the server needed to create file system
        artifacts.   Filepaths vary by server.
        """
        return get_submission_info(self.observatory, self.user_name)

    def transition(self, from_state, to_state):
        """Transition this submission from one state to the next, with states nominally:

        1. Corresponding to a root directory into which the submission dir tree is hard-linked.

        2. Being roughly:  creating, submitted, processing, failed, cancelled,
                           confirming, confirmed

        cancelled can be either a process cancellation or a confirmation cancellation.
        """
        check_state(from_state)
        check_state(to_state)
        os.link(self.path(from_state), self.path(to_state))
        os.unlink(self.path(from_state))

    @property
    def params(self):
        """Return a dictionary of the parameters for this submission suitable for serialization."""
        return dict(
            pmap_name = self.pmap_name,
            pmap_mode = self.pmap_mode,
            uploaded_files = self.uploaded_files, 
            description = self.description, 
            user_name = self.user_name, 
            creator_name = self.creator_name,
            change_level = self.change_level,
            auto_rename = self.auto_rename,
            compare_old_reference = self.compare_old_reference,
            observatory = self.observatory,
            submission_kind = self.submission_kind,
            submission_key = self.submission_key,
            instruments_filekinds = self.instruments_filekinds
            )
    
    def __repr__(self):
        """Return the string representation of a Submission object."""
        fields = [a + "=" + repr(getattr(self, a)) for a in ["pmap_name", "user_name", "upload_names", "description"]]
        return self.__class__.__name__ + "(" + ", ".join(fields) + ")"

    def create_subdirs(self):
        """Create subdirectories associated with this submission."""
        utils.create_path(self.path("creating", "files"), mode=0770)

    def save(self, yaml_path):
        """Given file submission parameters and files,  serialize the submission to the CRDS server file system."""
        utils.ensure_dir_exists(yaml_path, mode=770)
        with open(yaml_path, "w+") as spec_file:
            spec_file.write(self.yaml)
        return yaml_path

    @property
    def yaml(self):
        """Return the yaml representation of this Submission object (a string)."""
        return yaml.dump(self.params)

    @classmethod
    def load(cls, yaml_path):
        """Clasd method:  Load a submission object from the given `yaml_path`."""
        with open(yaml_path, "r") as spec_file:
            params = yaml.load(spec_file.read())
        return cls(**params)

    @property
    def upload_names(self):
        """Return the list of uploaded file names associated with this submission."""
        return self.uploaded_files.keys()

    @property
    def obs_locate(self):
        """Return the observatory locator module associted with this submission."""
        return utils.get_locator_module(self.observatory)

    def destroy(self):
        """Wipe out this submission on the file system."""
        for state in STATE_MODE_MAP:
            shutil.rmtree(self.path(state))

    def delete_files(self):
        """Delete the submitted files but retain the other portions of the submission."""
        shutil.rmtree(self.path("uploaded_files"))

    def ensure_unique_uploaded_names(self):
        """Make sure there are no duplicate names in the submitted file list."""
        # This is a sensible check for files originating on the command line.
        uploaded_as, paths = zip(*self.uploaded_files)
        pathmap = dict(*zip(paths, uploaded_as))
        for name in uploaded_as:
            assert uploaded_as.count(name) == 1, "File '%s' appears more than once." % name
        for path in paths:
            assert paths.count(path) == 1, "File path for '%s' appears more than once." %  pathmap[path]

    def ordered_files(self):
        """Organize uploaded file tuples in dependency order,  starting with references and ending with .pmaps."""
        rmaps, imaps, pmaps, other = [], [], [], []
        for original_name, uploaded_path in self.uploaded_files.items():
            if original_name.endswith(".rmap"):
                rmaps.append((original_name, uploaded_path))
            elif original_name.endswith(".imap"):
                imaps.append((original_name, uploaded_path))
            elif original_name.endswith(".pmap"):
                pmaps.append((original_name, uploaded_path))
            else:
                other.append((original_name, uploaded_path))
        return sorted(other) + sorted(rmaps) + sorted(imaps) + sorted(pmaps)

    def unique_for_instrument(self):
        """Return True IFF there is no other submission actively processing for
        the same instrument or instrument "none".
        """
        submsn_instr = instrument_name(self.submission_key)
        for state in ACTIVE_STATES:
            server_submissions = [
                os.path.basename(sub) 
                for sub in glob.glob(self.state_path(state, "*"))
                ]
            for active_name in server_submissions:
                active_instr = instrument_name(active_name)
                if submsn_instr in [active_instr] or "none" in active_instr:
                    return False
        return True

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
        self.user_name = None
        self.submission = None

    def create_submission(self):
        """Create a Submission object based on script / command-line parameters."""
        submission = Submission(
            pmap_name = self.resolve_context(self.args.derive_from_context),
            uploaded_files = { os.path.basename(filepath) : filepath for filepath in self.files },
            description = self.args.description,
            user_name = self.user_name,
            creator_name = self.args.creator,
            change_level = self.args.change_level,
            auto_rename = not self.args.dont_auto_rename,
            compare_old_reference = not self.args.dont_compare_old_reference,
            submission_kind = "batch",
            observatory = self.observatory,
            pmap_mode = "pmap_text",
            instruments_filekinds = self.instruments_filekinds
            )
        return submission

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
        # self.add_argument("--password", type=str, default=None, help="CRDS password of file submitter.")

    def finish_parameters(self):
        """Finish up parameter setup which requires parsed command line arguments."""
        if self.args.derive_from_context in ["edit", "ops"]:
            self.args.derive_from_context = self.observatory + "-" + self.args.derive_from_context
        self.user_name = self.args.username or os.getlogin()
        self.instruments_filekinds = self.get_instruments_and_filekinds()

    def main(self):
        """Main control flow of submission directory and request manifest creation."""

        self.finish_parameters()
        
        # self.trial_certify_files()
        # self.trial_refactor_rules()
        # if log.errors() and not self.args.force_submission:
        #     return log.errors()
        
        with self.fatal("While creating submission request"):
            self.submission = self.create_submission()
            self.submission.save(self.submission.path("creating", "submission.yaml"))
            return log.errors()

        with self.fatal("While coping submitted files"):
            self._copy_files()

        with self.fatal("Submitting request"):
            self.submission.transition("creating", "submitted")

        with self.fatal("While processing"):
            confirm_link = self._monitor_processing()

        log.info("File submission ready for confirmation at:", log.srepr(confirm_link))
        log.standard_status()

        return log.errors()

    def fatal(self, *params):
        """Return a fatal error context manager with message based on `params`."""
        return log.fatal_error_on_exception(*params)

    @property
    def ingest_dir(self):
        """Return the ingest directory associated with this submission,  nominally
        only a function of server, observatory, and user and outside the scope of
        the submissions file tree.
        """
        return self.submission.submission_info.ingest_dir

    def _copy_files(self):
        """Copy uploaded files into the server ingest directory."""
        for filepath in self.files:
            if filepath.startswith(self.ingest_dir):
                log.info("File", repr(filepath), "is already in your ingest directory.  Skipping copy.")
                continue
            else:
                destpath = os.path.join(self.ingest_dir, os.path.basename(filepath))
                log.info("Copying", repr(filepath), "to", repr(destpath))
                utils.ensure_dir_exists(destpath)
                shutil.copyfile(filepath, destpath)
            os.link(filepath, self.submission.path("creating","uploads", os.path.basename(filepath)))

    def _monitor_processing(self):
        """Loop polling the CRDS server for status on this submission and produce console
        log output for important events.
        """
        script = monitor.MonitorScript(
            "crds.monitor --process-key " +  self.submission.submission_key + 
            " --verbose" if log.get_verbose() else "",
            reset_log=False
            )
        return script()

# ===================================================================

# ===================================================================

if __name__ == "__main__":
    sys.exit(ReferenceSubmissionScript()())

