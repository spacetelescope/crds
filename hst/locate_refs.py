"""This provides functions which determine and manage the location of reference files.
"""
import os.path
import crds.pysh as pysh
import crds.log as log

# =======================================================================

REFNAME_TO_PATH = {}

def locate_file(ref_filename, cdbs="/grp/hst/cdbs"):
    """Effectively,  search the given  `cdbs` filetree for `ref_filename`
    and return the absolute path.

    This is implemented by dumping the tree into cache file 'cdbs.paths'
    and then grepping `ref_filename` using a subprocess.   The cache takes
    a while to compute so it is not routinely regenerated;  if the current
    cache is deleted,  this routine will create a new one.
    """
    if not REFNAME_TO_PATH.keys():
        setup_path_map(cdbs)
    return REFNAME_TO_PATH[ref_filename]
    
def setup_path_map(cdbs="/grp/hst/cdbs"):
    """Dump the directory tree `cdbs` into a file and read the results
    into a global map from file basename to absolute path.
    """
    if not os.path.exists("cdbs.paths"):
        log.info("Generating CDBS file path cache.")
        pysh.sh("find  ${cdbs} >cdbs.paths", raise_on_error=True)
        log.info("Done.")
    for line in open("cdbs.paths"):
        line = line.strip()
        if not line:
            continue
        dirname, filename = os.path.split(line)
#        if filename in REFNAME_TO_PATH:
#            log.warning("Reference file " + repr(filename) + " found more than once. Using first.")
        REFNAME_TO_PATH[filename] = line

