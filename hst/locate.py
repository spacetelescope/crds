"""This provides functions which determine and manage the location of reference files.
"""
import os.path
import crds.pysh as pysh
import crds.log as log

HERE = os.path.dirname(__file__) or "./"

# =======================================================================

CDBS = None
REFNAME_TO_PATH = {}

def locate_server_reference(ref_filename, cdbs="/grp/hst/cdbs"):
    """Effectively,  search the given  `cdbs` filetree for `ref_filename`
    and return the absolute path.
    """
    global CDBS
    CDBS = cdbs
    if not REFNAME_TO_PATH.keys():
        setup_path_map(cdbs)
    return REFNAME_TO_PATH[ref_filename]
    
def setup_path_map(cdbs="/grp/hst/cdbs", rebuild_cache=False):
    """Dump the directory tree `cdbs` into a file and read the results
    into a global map from file basename to absolute path.
    """
    cachepath = HERE + "/cdbs.paths"
    if not os.path.exists(cachepath) or rebuild_cache:
        log.info("Generating CDBS file path cache.")
        pysh.sh("find  ${cdbs} >${cachepath}", raise_on_error=True)
        log.info("Done.")
    for line in open(cachepath):
        line = line.strip()
        if not line:
            continue
        dirname, filename = os.path.split(line)
#        if filename in REFNAME_TO_PATH:
#            log.warning("Reference file " + repr(filename) + " found more than once. Using first.")
        REFNAME_TO_PATH[filename] = line        

# =======================================================================

CRDS_REFPATH = os.environ.get("CRDS_REFPATH", os.path.join(HERE, "references"))

def locate_reference(reference):
    """Return the absolute path for the client-side copy of a reference file.
    """
    sref = locate_server_reference(reference)
    return sref.replace(CDBS, CRDS_REFPATH)

def reference_url(crds_server_url, reference):
    """Return a file URL which can be used to retrieve the specified `reference`.
    """
    path = locate_server_reference(reference)
    return path.replace(CDBS, crds_server_url + "/static/references/hst")

# =======================================================================

CRDS_MAPPATH = os.environ.get("CRDS_MAPPATH", HERE)

def locate_mapping(mapping):
    """Given basename `mapping`,  return the absolute path of the CRDS
    mapping file.
    """
    if "/" in mapping:
        raise ValueError("Mapping should specify the basename only,  not the path.")
    if mapping.endswith(".pmap"):
        return os.path.join(CRDS_MAPPATH, mapping)
    elif mapping.endswith(".imap") or mapping.endswith(".rmap"):
        instr = mapping.split("_")[1].split(".")[0]
        return os.path.join(CRDS_MAPPATH, instr, mapping)
    else:
        raise ValueError("Unknown mapping type for " + repr(mapping))
    
def mapping_url(crds_server_url, mapping):
    """Return a file URL which can be used to retrieve the specified `mapping`.
    """
    path = locate_mapping(mapping)
    return path.replace(CRDS_MAPPATH, crds_server_url + "/static/mappings/hst")

