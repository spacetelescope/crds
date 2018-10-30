#! /usr/bin/env python
#-*-python-*-

"""This script is used to "check out" a version of synphot files corresponding to a CRDS context
with an organization compatible with the classic (Py)Synphot directory structure.
"""

import os
import os.path
import sys
import shutil
import warnings

# =============================================================================

# from pysynphot import locations

# =============================================================================

import crds
from crds import pysh, log, utils, cmdline
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
    
    epilog = """get_synphot works by first creating a CRDS cache under the specified
    <synphot_dir> and then hard linking files from that CRDS cache to their classic 
    CDBS directory equivalents.
    """

    def __init__(self, *args, **keys):
        super(GetSynphotScript, self).__init__(*args, **keys)
        self.pmap = None
        self.imap = None
        
    def add_args(self):
        self.add_argument(
            "synphot_dir", type=str, help="Location of synphot directory.")
        self.add_argument(
            'context', type=cmdline.context_spec,
            help="CRDS context (.pmap) or symbolic name defining version of synphot references to fetch.")
        self.add_argument(
            "--wipe-crds", action="store_true",
            help="Remove the 'crds' cache subdirectory of <synphot_dir> after downloading.")
        self.add_argument(
            "--wipe-cdbs", action="store_true",
            help="Remove synphot subdirectories of <synphot_dir> before linking files.")

    # -------------------------------------------------------------------------
    
    def main(self):

        self.deferred_init()
        
        syn_name_map = self.load_tables()

        if self.args.wipe_cdbs:
            self.rmdir("comp")
            self.rmdir("mtab")

        self.cross_link_cdbs_paths(syn_name_map)

        if self.args.wipe_crds:
            self.rmdir("crds")
            
        log.standard_status()    
        return log.errors()

    # -------------------------------------------------------------------------
    
    def deferred_init(self):
        self.crds_cache = os.path.join(self.args.synphot_dir, "crds")
        os.environ["PYSYN_CDBS"] = self.args.synphot_dir
        os.environ["CRDS_PATH"] = self.crds_cache
        utils.clear_function_caches()
        resolved_context = self.resolve_context(self.args.context)
        self.dump_mappings([resolved_context])        
        self.pmap = crds.get_cached_mapping(resolved_context)
        self.imap = self.pmap.get_imap("synphot")
        self.dump_files(resolved_context, self.imap.reference_names())        
        return None
    
    def determine_contexts(self):
        return [self.args.context]

    # -------------------------------------------------------------------------
    
    def load_tables(self):
        """Construct the mapping { filename : synphot_file_path, ...} for every file
        referred to by the TMC, TMT as well as the master TMC,TMT,TMG tables themselves.
        """
        syn_name_map = dict()
        syn_name_map.update(self.get_comptab_info("tmt"))
        syn_name_map.update(self.get_comptab_info("tmc"))
        syn_name_map.update(self.get_mtab_info("tmc"))
        syn_name_map.update(self.get_mtab_info("tmt"))
        syn_name_map.update(self.get_mtab_info("tmg"))        
        return syn_name_map

    def get_comptab_info(self, synname):
        """Given synphot component name designator `synname` (e.g. tmc),
        load the corresponding synphot table reference and compute the
        mapping { basename : full_synphot_path, ... } for every synphot
        FILENAME referred to in the table.
        """
        warnings.filterwarnings("ignore", "Extinction files not found")
        from pysynphot import locations
        
        filekind = synname + "tab"
        rmap  = self.imap.get_rmap(filekind)
        references  = rmap.reference_names()
        assert len(references) == 1, \
            "More than one '%s' reference name mentioned in '%s'." % (synname, rmap.name)
        tab_name = references[0]
        tab_path = rmap.locate_file(tab_name)  # rmap object locate() not module fumction.
        table = tables.tables(tab_path)[0]   # CRDS abstract table object
        fileinfo = {}
        for syn_name in table.columns["FILENAME"]:
            iraf_path, basename = syn_name.split("$")
            name = basename.split("[")[0]  # remove parameterization
            dollar_syn_name = syn_name.split("[")[0]
            cdbsdir = os.path.abspath(locations.irafconvert(dollar_syn_name))
            cdbs_filepath = os.path.join(cdbsdir, name)
            fileinfo[name] = cdbs_filepath
        return fileinfo

    def get_mtab_info(self, tab):
        """Return the mapping { tab_basename : full_synphot_path } for any synphot
        master TMC,TMG, or TMT table file.
        """
        rmap = self.imap.get_rmap(tab + "tab")
        filename = rmap.reference_names()[0]
        fullpath = os.path.abspath(os.path.join(self.args.synphot_dir, "mtab", filename))
        return { filename : fullpath }

    # -------------------------------------------------------------------------
    
    def cross_link_cdbs_paths(self, syn_name_map):
        for reference in syn_name_map:
            with log.error_on_exception(
                    "Failed linking", repr(reference), "to CDBS directory."):
                crds_filepath = os.path.abspath(self.imap.locate_file(reference))
                cdbs_filepath = syn_name_map[reference]
                utils.ensure_dir_exists(cdbs_filepath)
                if not os.path.exists(cdbs_filepath):
                    os.link(crds_filepath, cdbs_filepath)
                    log.info("Linked", cdbs_filepath, "-->", crds_filepath)
        return None

    def rmdir(self, subdir):
        path = os.path.join(self.args.synphot_dir, subdir)
        if os.path.exists(path):
            shutil.rmtree(path)
        
    
# -----------------------------------------------------------------------------
    
if __name__ == "__main__":
    sys.exit(GetSynphotScript()())
