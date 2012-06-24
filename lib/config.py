import os

DEFAULT_CRDS_DIR = "./crds"

def get_crds_mappath():
    """get_crds_mappath() returns the base path of the CRDS mapping directory 
    tree where CRDS rules files (mappings) are stored.
    """
    try:
        return os.environ["CRDS_MAPPATH"]
    except KeyError:
        return os.environ.get("CRDS_PATH", DEFAULT_CRDS_DIR) + "/mappings"

def get_crds_refpath():
    """get_crds_refpath returns the base path of the directory tree where CRDS 
    reference files are stored.
    """
    try:
        return os.environ["CRDS_REFPATH"]
    except KeyError:
        return os.environ.get("CRDS_PATH", DEFAULT_CRDS_DIR) + "/references"

