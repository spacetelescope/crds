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
import yaml

from crds import log, cmdline, config, utils
from crds.client import api

# ===================================================================

@utils.cached
def submission_info(observatory, username):
    return api.get_submission_info(observatory, username)

# ===================================================================

class Submission(object):

    """Base class for file submissions,  carrier object for submission meta-data and filenames."""
    
    def __init__(self, pmap_name, uploaded_files, description, user_name, creator_name="UNKNOWN",
                 change_level="SEVERE", auto_rename=True, compare_old_reference=True,
                 submission_kind=None, observatory=None, pmap_mode=None, instrument=None, **keys):
        
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
        self.submission_key = str(instrument).lower() + "-" + str(datetime.datetime.now()).replace(" ","-")

    @property
    def submission_dir(self):
        return os.path.join(self.submission_info.submission_dir, self.submission_key)

    @property
    def submission_info(self):
        return utils.Struct(get_submission_info(self.observatory, self.username))

    def path(self, *subpaths):
        return os.path.join(self.submission_dir, *subpaths)

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
            locked_instrument = self.locked_instrument,
            status_key = self.status_key,
            observatory = self.observatory,
            submission_kind = self.submission_kind,
            submission_subdir = self.submission_subdir,
            process_name = self.process_name,
            )
    
    def __repr__(self):
        fields = [a + "=" + repr(getattr(self, a)) for a in ["pmap_name", "user_name", "upload_names", "description"]]
        return self.__class__.__name__ + "(" + ", ".join(fields) + ")"

    def create_subdirs(self, base_path):
        utils.create_path(base_path, mode=0770)  # if not exists.
        utils.create_path(os.path.join(base_path, "uploads"), mode=0770)
        utils.create_path(ps.path.join(base_path, "files"), mode=0770)        
        
    def save(self, yaml_path=None):
        """Given file submission parameters and files,  serialize the submission to the CRDS server file system."""
        yaml_path = yaml_path or self.path("submission.yaml")
        utils.ensure_dir_exists(yaml_path, mode=770)
        with open(yaml_path, "w+") as spec_file:
            spec_file.write(yaml.dump(self.params))

    @classmethod
    def load(cls, yaml_path):
        yaml_path = yaml_path or self.path("submission.yaml")
        with open(yaml_path, "r") as spec_file:
            params = yaml.load(spec_file.read())
        return self.__class__(**params)

    def pmap(self):
        return rmap.get_cached_mapping(self.pmap_name)
        
    @property
    def upload_names(self):
        return self.uploaded_files.keys()

    @property
    def obs_locate(self):
        return utils.get_locator_module(self.observatory)

    def destroy(self):
        """Wipe out this submission on the file system.  Failures only."""

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

# ===================================================================

class ReferenceSubmissionScript(cmdline.Script):
    """Command line script file submission script."""

    description = """
"""

    epilog = """
"""

    def __init__(self, *args, **keys):
        super(ReferenceSubmissionScript, self).__init__(*args, **keys)
        self.username = os.getlogin()
        self.submission = None

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
        if self.args.derive_from_context in ["edit", "ops"]:
            self.args.derive_from_context = self.observatory + "-" + self.args.derive_from_context
        # self.trial_certify_files()
        # self.trial_refactor_rules()
        # if log.errors() and not self.args.force_submission:
        #     return log.errors()
        self.submission = self.create_submission()

        with log.fatal_error_on_exception("copying files to server ingest directory."):
            self.copy_files()

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

    def poll_status(self):
        messages = api.jpoll_pull_messages(self.submission_key)
        
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

