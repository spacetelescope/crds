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

from crds import log, cmdline, utils, timestamp
from crds.submission import monitor
from crds.client import api
from crds.log import srepr

# ===================================================================

SUBMISSION_DEFS = [
    ("creating",   0o770),  # This submission code is still encoding the submission in user-space
    ("submitted",  0o770),  # This submission is ready for pick-up by the background processor
    ("ingesting",  0o750),  # The background processor is creating a CRDS owned copy of the submission
    ("processing", 0o750),  # The background processor is processing the submission
    ("confirming", 0o750),  # The background processor has completed and the results are ready for review
    ("failed",     0o750),  # CRDS detected a fatal error in the submission content forcing cancellation
    ("confirmed",  0o750),  # The user has confirmed the submission
    ("aborted",    0o750),  # The user killed the submission early with an RPC.
    ("cancelled",  0o750),  # The user rejected the submission upon review
    ("crashed",    0o750),  # An untrapped exception occurred
    ]

STATE_MODE_MAP = dict(SUBMISSION_DEFS)

CLIENT_STATES = { 
    "creating", 
    "submitted" 
    }

ACTIVE_STATES = {
    "ingesting",
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

SERVER_STATES = ACTIVE_STATES | INACTIVE_STATES

SUBMISSION_STATES = CLIENT_STATES | ACTIVE_STATES | INACTIVE_STATES
assert SUBMISSION_STATES == set(STATE_MODE_MAP.keys())

# ===================================================================

def check_state(state):
    """Raise an exception if `state` is not a known valid state."""
    assert state in SUBMISSION_STATES, "Submission state " + srepr(state) + "is not a vaild state."
    return state

# ===================================================================

@utils.cached
def get_submission_info(observatory, username):
    """Return parameter information from the server required to perform
    command line file submissions.
    """
    return api.get_submission_info(observatory, username)

# ===================================================================

def submission_state_paths(observatory, username, submission_key, state):
    """Return all the paths associated with the given `state` and parameters.
    If the submission key is None then all submissions for that user are
    returned,  otherwise only the
    """
    subdir = get_submission_info(observatory, username).submission_dir
    if submission_key is None:
        pattern = os.path.join(subdir, state, "*-" + username)
        return glob.glob(pattern)
    else:
        path = os.path.join(subdir, state, submission_key)
        return [path] if os.path.exists(path) else []

def submission_paths(observatory, username, submission_key, states):
    """Return all submission paths associated with the specified 
    parameters and `states`.
    """
    paths = []
    for state in states:
        paths.extend(submission_state_paths(observatory, username, submission_key, state))
    return paths

def active_paths(observatory, username, submission_key):
    """Return associated with active states and the specified `username` and/or
    `submission_key`.
    """
    return submission_paths(observatory, username, submission_key, ACTIVE_STATES)

def inactive_paths(observatory, username, submission_key):
    """Return associated with active states and the specified `username` and/or
    `submission_key`.
    """
    return submission_paths(observatory, username, submission_key, INACTIVE_STATES)

def client_paths(observatory, username, submission_key):
    """Return associated with client states and the specified `username` and/or
    `submission_key`.
    """
    return submission_paths(observatory, username, submission_key, CLIENT_STATES)

def all_paths(observatory, username, submission_key):
    """Return all submission paths related to the specified parameters.  If
    submission_key is None then all submissions for the given username are
    returned.
    """
    return (client_paths(observatory, username, submission_key) +
            active_paths(observatory, username, submission_key) +
            inactive_paths(observatory, username, submission_key))

def split_path(path):
    """
    >>> split_path("/somewhere/on/the/disk/submitted/miri-2015-12-25T00:00:00.000000-homer")
    ('submitted', 'miri', '2015-12-25T00:00:00.000000', 'homer')
    """
    state = os.path.basename(os.path.basename(path))
    subname = os.path.basename(path)
    instrument, year, month, day_time, user = subname.split("-")
    return utils.Struct(
        state=state, instrument=instrument, 
        datetime="-".join([year, month, day_time]), user=user)

# ===================================================================

def new_submission_name(user_name, instrument):
    """Return a new unique name for a submission based on `user` and `instrument`."""
    # Designed to sort by instrument and date.
    return "-".join([instrument, timestamp.now("T"), user_name])

# ===================================================================

class Submission(object):

    """Base class for file submissions,  carrier object for submission meta-data and filenames."""
    
    def __init__(self, pmap_name, uploaded_files, description, user_name, creator_name="UNKNOWN",
                 change_level="SEVERE", auto_rename=True, compare_old_reference=True,
                 submission_kind=None, observatory=None, pmap_mode=None, instruments_filekinds=None, 
                 submission_key=None, agent=None, submission_state=None, related_files=None, **keys):

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
        search_files = uploaded_files.values() if uploaded_files else related_files
        self.instruments_filekinds = (instruments_filekinds or utils.get_instruments_filekinds(observatory, search_files))
        instrument = str(self.instruments_filekinds.keys()[0]) if len(self.instruments_filekinds) == 1 else "multiple"
        self.submission_key = submission_key or new_submission_name(self.user_name, instrument)
        self.submission_state = submission_state or "creating"
        self.agent = agent
        self.related_files = related_files or []
        self.keys = keys

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
            submission_kind = self.submission_kind,
            observatory = self.observatory,
            instruments_filekinds = self.instruments_filekinds,
            submission_key = self.submission_key,
            agent = self.agent,
            submission_state = self.submission_state,
            related_files = self.related_files,
            keys = self.keys,
            )
    
    def state_path(self, state, *subdirs):
        """Return the path of the top level directory for `state` which has links
        for all submissions in `state`.

        Returns: ".../submissions/<state>"

        This enables submissions to migrate through top level state directories during
        the course of processing.
        """
        return os.path.join(self.submission_info.submission_dir, state, *subdirs)

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

    @property
    def monitor_url(self):
        """Return the server URL which can be used to monitor this submission via a web page."""
        return self.submission_info.monitor_url + self.submission_key + "/"

    @property
    def confirm_url(self):
        """Return the server URL which can be used to confirm/cancel this submission via a web page."""
        return self.submission_info.confirm_url + self.submission_key + "/"

    def push_status(self, *args):
        """Issue a status message, intended to be overridden/augmented for web status."""
        log.info(*args)
        
    def transition(self, to_state, copy=None):
        """Transition this submission from one state to the next, with states nominally:

        1. Corresponding to a root directory into which the submission dir tree is hard-linked.

        2. Being roughly:  creating, submitted, processing, failed, cancelled,
        confirming, confirmed

        cancelled can be either a process cancellation or a confirmation cancellation.
        """
        from_state = self.submission_state
        from_path = self.path(check_state(from_state))
        to_path = self.path(check_state(to_state))
        self.push_status("Transitioning", srepr(self.submission_key), "from", srepr(from_state), "to", srepr(to_state))
        if copy is None and from_state in CLIENT_STATES and to_state in SERVER_STATES:
            self.push_status("Copying", srepr(from_path), "to", srepr(to_path), "to change ownership.")
            utils.copytree(from_path, to_path, fnc_file=self.push_status)
            shutil.rmtree(from_path)
        else:
            self.push_status("Moving", srepr(from_path), "to", srepr(to_path))
            shutil.move(self.path(from_state), self.path(to_state))
        self.submission_state = to_state
        self.save(self.path(to_state, "submission.yaml"))

    def __repr__(self):
        """Return the string representation of a Submission object."""
        fields = [a + "=" + srepr(getattr(self, a)) for a in ["pmap_name", "user_name", "upload_names", "description"]]
        return self.__class__.__name__ + "(" + ", ".join(fields) + ")"

    def create_subdirs(self):
        """Create subdirectories associated with this submission."""
        utils.create_path(self.path("creating", "uploaded_files"), mode=0o770)
        utils.create_path(self.path("creating", "generated_files"), mode=0o770)
        utils.create_path(self.path("creating", "renamed_files"), mode=0o770)
        utils.create_path(self.path("submitted"), mode=0o770)

    def save(self, yaml_path=None, added_params={}):
        """Given file submission parameters and files,  serialize the submission to the CRDS server file system."""
        self.create_subdirs()
        if yaml_path is None:
            yaml_path = self.path("creating", "submission.yaml")
        utils.ensure_dir_exists(yaml_path, mode=0o770)
        pars = self.params
        pars.update(added_params)
        text = yaml.dump(pars)
        with open(yaml_path, "w+") as spec_file:
            spec_file.write(text)
        return yaml_path

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

    '''
    Untested... 

    def destroy(self):
        """Wipe out this submission on the file system."""
        for state in SUBMISSION_STATES:
            self.rmtree_no_fail(self.path(state))

    def delete_files(self):
        """Delete the submitted files but retain the other portions of the submission."""
        for state in SUBMISSION_STATES:
            self.rmtree_no_fail(state, "uploaded_files")
            self.rmtree_no_fail(state, "renamed_files")
            self.rmtree_no_fail(state, "generated_files")

    def rmtree_no_fail(self, *subtree):
        """Remove the specified `subtree` of this submission directory, ignore if non-existent."""
        with log.verbose_warning_on_exception("Failed removing", repr(subtree)):
            shutil.rmtree(self.path(*subtree))
    '''

    def ensure_unique_uploaded_names(self):
        """Make sure there are no duplicate names in the submitted file list."""
        # This is a sensible check for files originating on the command line.
        uploaded_as, paths = zip(*self.uploaded_files)
        pathmap = dict(*zip(paths, uploaded_as))
        for name in uploaded_as:
            assert uploaded_as.count(name) == 1, "File '%s' appears more than once." % name
        for path in paths:
            assert paths.count(path) == 1, "File path for '%s' appears more than once." %  pathmap[path]
            assert os.path.exists(path), "File path for '%s' is not visible." % pathmap[path]

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
        submsn_instr = self.instrument_name(self.submission_key)
        for state in ACTIVE_STATES:
            server_submissions = [
                os.path.basename(sub) 
                for sub in glob.glob(self.state_path(state, "*"))
                ]
            for active_name in server_submissions:
                active_instr = self.instrument_name(active_name)
                if submsn_instr in [active_instr] or "none" in active_instr:
                    return False
        return True

    def instrument_name(self, submission_name):
        """Return the instrument name associated with this submission."""
        instr = split_path(submission_name).instrument
        assert instr.lower() in self.obs_locate.INSTRUMENTS, "Invalid instrument name."
        return instr

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
            pmap_name = self.args.derive_from_context,  # defer symbolic resolution to post-confirmation
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
            agent = "command-line-script"
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
        self.add_argument("--monitor-processing", action="store_true", 
                          help="Monitor CRDS processing for on-going status and final confirmation link.")
        # self.add_argument("--password", type=str, default=None, help="CRDS password of file submitter.")

    def finish_parameters(self):
        """Finish up parameter setup which requires parsed command line arguments."""
        if self.args.derive_from_context in ["edit", "ops"]:
            self.args.derive_from_context = self.observatory + "-" + self.args.derive_from_context
        self.user_name = self.args.username or os.getlogin()

    def main(self):
        """Main control flow of submission directory and request manifest creation."""

        self.require_server_connection()
        
        self.finish_parameters()

        # self.trial_certify_files()
        # self.trial_refactor_rules()
        # if log.errors() and not self.args.force_submission:
        #     return log.errors()
        
        with self.fatal("While creating submission request"):
            self.submission = self.create_submission()
            self.submission.save()
            self.submission.transition("submitted")

        log.info("Submitted request:", srepr(self.submission.submission_key))
        log.info("The submission can be monitored at:", self.submission.monitor_url)

        if self.args.monitor_processing:
            self.monitor_processing()
            log.info("The submission can be confirmed or cancelled at:", self.submission.confirm_url)

        log.standard_status()

        return self.submission.submission_key

    def fatal(self, *params):
        """Return an exception context manager with message based on `params`.

        Add any clean up required.
        """
        return log.augment_exception(*params)

    @property
    def ingest_dir(self):
        """Return the ingest directory associated with this submission,  nominally
        only a function of server, observatory, and user and outside the scope of
        the submissions file tree.
        """
        return self.submission.submission_info.ingest_dir
    
    def monitor_processing(self):
        """Loop polling the CRDS server for status on this submission and produce console
        log output for important events.
        """
        with self.fatal("While monitoring processing"):
            command_line = ("crds.monitor --submission-key " +  self.submission.submission_key + 
                            (" --verbose" if log.get_verbose() else ""))
            script = monitor.MonitorScript(argv=command_line, reset_log=False)
            return script()
        

# ===================================================================

# ===================================================================

if __name__ == "__main__":
    sys.exit(ReferenceSubmissionScript()())

