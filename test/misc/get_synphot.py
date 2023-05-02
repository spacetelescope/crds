#! /usr/bin/env python
#-*-python-*-

"""This script is used to "check out" a version of synphot files corresponding
to a CRDS context with an organization compatible with the classic (Py)Synphot
directory structure.  This largely isolates CRDS from the CDBS/IRAF-style
synphot directory structure and keeps rmaps in a simple form which does not
include IRAF-style env vars as part of filenames.
"""

import os
import os.path
import sys
import shutil
import warnings

# =============================================================================

# from pysynphot import locations

SYNPHOT_IGNORE = [
    "Extinction files not found",
    "No graph or component tables found",
    "No thermal tables found"
    ]

# =============================================================================

import crds
from crds.core import pysh, log, utils, cmdline, config
from crds import sync
from crds import client
from crds.io import tables

# =============================================================================

class GetSynphotScript(cmdline.Script):
    """Command line script for modifying .rmap files."""

    description = """
This script downloads (Py)Synphot files refered to by <context>
from the CRDS server to directory <synphot_dir>.
    """

    epilog = """
get_synphot works by first creating a CRDS cache under the specified
<synphot_dir> and then hard linking files from that CRDS cache to their
classic CDBS directory equivalents in comp and mtab subdirectories.

With --keep-crds get_synphot will retain the CRDS cache structure used to
perform the initial download of files under <synphot_dir>/crds. This makes
additional calls to get_synphot incremental updates instead of full downloads.
The <synphot_dir>/crds directory exists in addition to the mtab and comp
directories.

Example get_synophot runs:

1. Basic run

  $ crds get_synphot  my_pysyn_dir  hst-edit

  Overwrites my_pysyn_dir in the current working directory, storing the (py)synphot
  reference files associated with with the latest file deliveries to HST.   This
  will force a full download and will remove existing synphot subdirectories and
  files whether they come from CRDS or not.

2. Get specific version of synphot files (hyothetical context hst_0999.pmap)

  $ crds get_synphot  my_pysyn_dir  hst_0999.pmap

3. Get synphot files,  keeping working copy of CRDS cache

  $ crds get_synphot  my_pysyn_dir  hst-edit --keep-crds

  This keeps a copy of the working CRDS cache under <my_pysyn_dir>/crds.  These files
  refer to the same storage as the normal synphot paths and do not require extra space.
  --keep-crds is largely used to minimize repeat downloads.

4. Get synphot files,  keeping old versions and user added synphot files

  $ crds get_synphot  my_pysyn_dir  hst-edit --keep-synphot

  This retains the existing synphot comp and mtab directories my_pysyn_dir.
"""
    def __init__(self, *args, **keys):
        super(GetSynphotScript, self).__init__(*args, **keys)
        self.pmap = None
        self.imap = None

    def add_args(self):
        """Add command line parameters specific to this script."""
        self.add_argument(
            "synphot_dir", type=str, help="Location of synphot directory.")
        self.add_argument(
            'context', type=cmdline.context_spec,
            help="CRDS context (.pmap) defining version of synphot references to fetch.")
        self.add_argument(
            "--keep-crds", action="store_true",
            help="Don't remove the 'crds' cache subdirectory of <synphot_dir> after downloading.")
        self.add_argument(
            "--keep-synphot", action="store_true",
            help="Don't remove <synphot_dir> subdirectories before linking requested files.")

    def determine_contexts(self):
        """Use the command line `context` parameter to help define things like
        observatory and default CRDS_SERVER_URL.
        """
        return [self.args.context]

    # -------------------------------------------------------------------------

    def main(self):
        """Perform the high level sequence of tasks needed to download and
        organize a version of pysynphot files under the specified directory.
        """
        self.deferred_init()

        # Blow away CRDS cache prior to syncing
        if not self.args.keep_crds:
            self.rmdir("crds")

        self.crds_download()

        syn_name_map = self.pysyn_cdbs_from_syn_tables()

        # Blow away comp and mtab to remove old versions of links
        if not self.args.keep_synphot:
            self.rmdir("comp")
            self.rmdir("mtab")

        self.cross_link_cdbs_paths(syn_name_map)

        # Blow away CRDS cache leaving only synphot organization.
        # in the final product.
        if not self.args.keep_crds:
            self.rmdir("crds")

        log.standard_status()
        return log.errors()

    # -------------------------------------------------------------------------

    def deferred_init(self):
        """Initialize CRDS and PySYNPHOT after module import and basic script
        object construction.
        """
        self.crds_cache = os.path.abspath(os.path.join(
            self.args.synphot_dir, "crds"))
        config.override_crds_paths(self.crds_cache)
        os.environ["PYSYN_CDBS"] = self.args.synphot_dir
        utils.clear_function_caches()

    def crds_download(self):
        """Populates the <synphot_dir>/crds file cache with all synphot files
        implied by self.args.context.   This creates an ordinary CRDS cache
        within <synphot_dir> which both sources the synphot files needed now
        and can optimize future downloads if desired.
        """
        resolved_context = self.resolve_context(self.args.context)
        self.dump_mappings([resolved_context])
        self.pmap = crds.get_cached_mapping(resolved_context)
        self.imap = self.pmap.get_imap("synphot")
        self.dump_files(resolved_context, self.imap.reference_names())

    # -------------------------------------------------------------------------

    def pysyn_cdbs_from_syn_tables(self):
        """Construct the mapping from synphot file basename to classic CDBS path for
        every file defined by the TMC and TMT tables.  Also include mtab paths
        for the master TMC,TMT,TMG tables themselves.

        This bridges the gap between basenames recorded by CRDS and synphot
        paths which are defined with environment variables encoded in the table
        filenames.

        Reads table files ending with _tmt.fits and _tmc.fits

        Returns   { syn_basename : full_pysn_path, ... }
        """
        syn_name_map = dict()
        syn_name_map.update(self.get_comptab_info("tmt"))
        syn_name_map.update(self.get_comptab_info("tmc"))
        syn_name_map.update(self.get_mtab_info("tmc"))
        syn_name_map.update(self.get_mtab_info("tmt"))
        syn_name_map.update(self.get_mtab_info("tmg"))
        return syn_name_map

    def get_comptab_info(self, synname):
        """Dump the FILENAME column of the component table implied by `synname`
        (e.g. "tmc" --> something_tmc.fits) and use pysynphot to interpret the
        embedded iraf$-style path env var into a normal filepath.  This is used
        to locate files within appropriate sub-directories of
        <synphot_dir>/comp.

        Return the mapping from a component file basename as defined in the CRDS
        rmap to the absolute path in a CDBS-style synphot file repo being created.

        Returns  { component_basename : abs_pysyn_path, ...}
        """
        for msg in SYNPHOT_IGNORE:
            warnings.filterwarnings("ignore",msg)
        from pysynphot import locations

        filekind = synname + "tab"
        rmap  = self.imap.get_rmap(filekind)

        references  = rmap.reference_names()
        assert len(references) == 1, \
            "More than one '%s' reference name mentioned in '%s'." % \
            (synname, rmap.name)
        tab_name = references[0]

        # rmap object locate() not module function.
        tab_path = rmap.locate_file(tab_name)

        # CRDS abstract table object nominally from HDU 1
        table = tables.tables(tab_path)[0]

        fileinfo = {}
        for syn_name in table.columns["FILENAME"]:

            iraf_path, basename = syn_name.split("$")
            name = basename.split("[")[0]  # remove parameterization

            dollar_syn_name = syn_name.split("[")[0]

            # Use pysynphot to interpret iraf_path
            cdbs_filepath = os.path.abspath(
                locations.irafconvert(dollar_syn_name))

            fileinfo[name] = cdbs_filepath

        return fileinfo

    def get_mtab_info(self, tab):
        """Return the mapping from basename to the full pysyn CDBS-style absolute
        filepath for any master TMC,TMG, or TMT table file referred to under
        the spoecified context.  There can be only one of each kind of file.

        tab       string      nominally one of "tmc","tmt","tmg"

        Returns   { table_basename(tab) : pysyn_mtab_filepath }
        """
        rmap = self.imap.get_rmap(tab + "tab")
        references = rmap.reference_names()
        assert len(references) == 1, "More than one " + repr(tab.upper()) + " file."
        filename = references[0]
        fullpath = os.path.abspath(os.path.join(
            self.args.synphot_dir, "mtab", filename))
        return { filename : fullpath }

    # -------------------------------------------------------------------------

    def cross_link_cdbs_paths(self, syn_name_map):
        """Hard link files from the downloaded CRDS cache structure to the
        classic CDBS-style directory locations specified by `syn_name_map`.

        On OS-X and Linux this creates files which are referenced from two
        different paths on the file system.   Deleting one path or the other
        leaves behind a normal file referenced from only one location.

        syn_name_map    dict     { syn_basename : pysyn_filepath, ... }

        returns   None
        """
        for reference in syn_name_map:
            with log.error_on_exception(
                    "Failed linking", repr(reference), "to CDBS directory."):
                crds_filepath = os.path.abspath(self.imap.locate_file(reference))
                cdbs_filepath = syn_name_map[reference]
                utils.ensure_dir_exists(cdbs_filepath)
                if not os.path.exists(cdbs_filepath):
                    os.link(crds_filepath, cdbs_filepath)
                    log.verbose("Linked", cdbs_filepath, "-->", crds_filepath)
                else:
                    log.verbose("Skipped existing", cdbs_filepath)

    def rmdir(self, subdir):
        """If it exists, remove `subdir` of the <synphot_dir> specified.

        subdir    string    subdirectory of <synphot_dir> to remove.
        """
        path = os.path.join(self.args.synphot_dir, subdir)
        log.verbose("rmdir: ", repr(path))
        with log.verbose_warning_on_exception("Failed removing", repr(path)):
            shutil.rmtree(path)

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(GetSynphotScript()())
