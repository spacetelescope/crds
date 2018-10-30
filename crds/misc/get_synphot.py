#! /usr/bin/env python
#-*-python-*-

"""This script is used to "check out" a version of synphot files corresponding to a CRDS context
with an organization compatible with the classic (Py)Synphot directory structure.
"""

import os
import os.path

# ============================================================================================

from pysynphot import locations

# ============================================================================================

import crds
from crds import pysh, log, utils, cmdline
from crds import sync
from crds.io import tables

# ============================================================================================

class GetSynphotScript(cmdline.Script):
    """Command line script for modifying .rmap files."""

    description = """
This script downloads (Py)Synphot files refered to by <context> 
from the CRDS server to directory <synphot_dir>.
    """
    
    epilog = """    
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
            help="CRDS pipeline mapping defining version of synphot references to fetch.")
        self.add_argument(
            "--delete-crds", action="store_true",
            help="Remove the 'crds' cache subdirectory of <synphot_dir> and links to synphot files.")

    # ---------------------------------------------------------------------------------------
    
    def main(self):

        self.deferred_init()
        self.download_files()
        syn_info = self.load_tables()
        self.cross_link_cdbs_paths(syn_info)
        if self.args.delete_crds:
            os.removedirs(self.crds_cache)
        
        log.standard_status()
        return log.errors()

    # ---------------------------------------------------------------------------------------
    
    def deferred_init(self):
        self.crds_cache = os.path.join(self.args.synphot_dir, "crds")
        os.environ["PYSYN_CDBS"] = self.args.synphot_dir
        os.environ["CRDS_PATH"] = self.crds_cache
        utils.clear_function_cache()
        # Loaded InstrumentMapping
        self.pmap = crds.get_symbolic_mapping(self.args.context)
        self.imap = pmap.get_imap("synphot")
        return None

    # ---------------------------------------------------------------------------------------
    
    def download_files(self):
        with log.warn_on_exception("Failure during CRDS downloads"):
            errors = sync.SyncScript(
                "crds.sync --contexts %s --fetch-references --stats" % (context,))
            if errors:
                log.warning("Errors during CRDS download of SYNPHOT files.")
        return None
    
    # ---------------------------------------------------------------------------------------
    
    def load_tables():
        """Construct the mapping { filename : synphot_file_path, ...} for every file
        referred to by the TMC, TMT as well as the master TMC,TMT,TMG tables themselves.
        """
        syn_info = dict()
        syn_info.update(get_comptab_info("tmt"))
        syn_info.update(get_comptab_info("tmc"))
        syn_info.update(get_mtab_info("tmc"))
        syn_info.update(get_mtab_info("tmt"))
        syn_info.update(get_mtab_info("tmg"))        
        return syn_info

    def get_comptab_info(self, synname):
        """Given synphot component name designator `synname` (e.g. tmc),
        load the corresponding synphot table reference and compute the
        mapping { basename : full_synphot_path, ... } for every synphot
        FILENAME referred to in the table.
        """
        filekind = synname + "tab"
        rmap  = self.imap.get_rmap(filekind)
        references  = rmap.reference_names()
        assert len(references) == 1, \
            "More than one '%s' reference name mentioned in '%s'." % (synname, rmap.name)
        tab_name = references[0]
        tab_path = rmap.locate(tab_name)  # rmap object locate() not module fumction.
        table = tables.tables(tab_path)   # CRDS abstract table object
        fileinfo = {}
        for syn_name in table.columns["FILENAME"]:
            iraf_path, basename = syn_name.split("$")
            name = basename.seplit("[")[0]  # remove parameterization
            simpler_syn_name = syn_name.split("[")[0]
            fileinfo[name] = locations.get_data_filename(simpler_syn_name)
        return fileinfo

    def get_mtab_info(tab):
        """Return the mapping { tab_basename : full_synphot_path } for the synphot
        master TMC,TMG, or TMT table file.
        """
        rmap = self.imap.get_rmap(tab + "tab")
        filename = rmap.reference_names()[0]
        fullpath = os.path.join(self.args.synphot_dir, "mtab")
        return { filename : fullpath }

    # ---------------------------------------------------------------------------------------
    
    def cross_link_cdbs_paths(self, syn_info):
        for reference in syn_info:
            with log.error_on_exception(
                    "Failed linking", repr(crds_filepath), "to", repr(cdbs_filepath)):
                crds_filepath = self.imap.locate_file(reference)
                synphot_refname = syn_info[reference]
                os.link(crds_filepath, cdbs_filepath)
        return None

# ---------------------------------------------------------------------------------------
    
if __name__ == "__main__":
    sys.exit(GetSynphotScript()())
