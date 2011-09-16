"""This module provides functions which determine various observatory
specific policies for HST:

1. How to convert reference file basenames to fully specified paths.

2. How to convert a reference or mapping basename to a download URL.

3. How to manage parameters for reference file Validator objects used
in the certification of reference files. 

The intentions is that a similar module with different policies could
be implemented for JWST.
"""
import os.path
import gzip
import re

# import crds.pysh as pysh
from crds import (log, rmap, pysh)
import crds.hst.tpn as tpn

HERE = os.path.dirname(__file__) or "./"

# =======================================================================

# CDBS_REFPATH is the location of the master server-side copy of the reference
# file directory tree.
CDBS_REFPATH = "/grp/hst/cdbs"

# REFNAM_TO_PATH is a mapping from { reference_basename : reference_absolute_path }
REFNAME_TO_PATH = {}

def locate_server_reference(ref_filename, cdbs=CDBS_REFPATH):
    """Effectively,  search the given  `cdbs` filetree for `ref_filename`
    and return the absolute path.
    
    This translates a name like 'v4q2144qj_bia.fits' into an absolute path
    which most likely depends on instrument.
    
    """
    global CDBS_REFPATH
    CDBS_REFPATH = cdbs
    if not REFNAME_TO_PATH:
        setup_path_map(cdbs)
    return REFNAME_TO_PATH[ref_filename]
    
def setup_path_map(cdbs=CDBS_REFPATH, rebuild_cache=False):
    """Dump the directory tree `cdbs` into a file and read the results
    into a global map from file basename to absolute path.
    """
    cachepath = HERE + "/cdbs.paths.gz"
    if not os.path.exists(cachepath) or rebuild_cache:
        log.info("Generating CDBS file path cache.")
        pysh.sh("find  ${cdbs} | gzip -c >cdbs.paths.gz")  # , raise_on_error=True) sometimes permission is denied
        log.info("Done.")
    for line in gzip.open(cachepath):
        line = line.strip()
        if not line:
            continue
        dirname, filename = os.path.split(line)
#        if filename in REFNAME_TO_PATH:
#            log.warning("Reference file " + repr(filename) + " found more than once. Using first.")
        REFNAME_TO_PATH[filename] = line        

def main():
    setup_path_map(rebuild_cache=True)

# =======================================================================

# CRDS_REFPATH is the path to the local/client copy of reference files.
def get_crds_refpath():
    return os.environ.get("CRDS_REFPATH", os.path.join(HERE, "references"))

def locate_reference(reference):
    """Return the absolute path for the client-side copy of a reference file.
    """
    sref = locate_server_reference(reference)
    return sref.replace(CDBS_REFPATH, get_crds_refpath())

def reference_url(crds_server_url, reference):
    """Return a file URL which can be used to retrieve the specified `reference`.
    """
    path = locate_server_reference(reference)
    return path.replace(CDBS_REFPATH, crds_server_url)

def reference_exists(reference):
    """Return True iff basename `reference` is known/exists in CRDS.
    """
    try:
        where = locate_server_reference(reference)
    except KeyError:
        return False
    return os.path.exists(where)

# =======================================================================

# CRDS_MAPPATH is the location of the client or sever side mapping directory
# tree,  nominally the package location of crds.<observatory>,  .e.g. crds.hst
def get_crds_mappath():
    return os.environ.get("CRDS_MAPPATH", HERE)

def locate_mapping(mapping):
    """Given basename `mapping`,  return the absolute path of the CRDS
    mapping file.
    """
    if "/" in mapping:
        raise ValueError("Mapping should specify the basename only,  not the path.")
    if mapping.endswith(".pmap"):
        return os.path.join(get_crds_mappath(), mapping)
    elif mapping.endswith(".imap") or mapping.endswith(".rmap"):
        instr = mapping.split("_")[1].split(".")[0]
        return os.path.join(get_crds_mappath(), instr, mapping)
    else:
        raise ValueError("Unknown mapping type for " + repr(mapping))
    
def locate_server_mapping(mapping):
    """Given basename `mapping`,  return the absolute path of the CRDS mapping 
    file on the CRDS server.
    """
    return locate_mapping(mapping)
    
def mapping_exists(mapping):
    """Return True iff the basename `mapping` is known as a mapping to CRDS."""
    try:
        where = locate_server_mapping(mapping)
    except KeyError:
        return False
    return os.path.exists(where)

def mapping_url(crds_server_url, mapping):
    """Return a file URL which can be used to retrieve the specified `mapping`.
    """
    path = locate_mapping(mapping)
    return path.replace(get_crds_mappath(), crds_server_url + "/static/mappings/hst")

# =======================================================================

# These two functions decouple the generic reference file certifier program 
# from observatory-unique ways of specifying and caching Validator parameters.

from .tpn import reference_name_to_validator_key
from .tpn import get_tpninfos

# =======================================================================

def get_file_properties(filename):
    """Figure out (instrument, filekind, serial) based on `filename` which
    should be a mapping or FITS reference file.
    """
    if filename.endswith(".pmap"):
        result = get_pmap_properties(filename)
    elif filename.endswith(".imap"):
        result = get_imap_properties(filename)
    elif filename.endswith(".rmap"):
        result = get_rmap_properties(filename)
    elif filename.endswith(".fits"):
        result = get_reference_properties(filename)
    else:
        raise ValueError("Filename implies neither a mapping nor FITS file.")
    return result

def _get_fields(filename):
    name = os.path.basename(filename)
    name = os.path.splitext(name)[0]
    return name.split("_")

def get_pmap_properties(filename):
    fields = _get_fields(filename)
    if len(fields) == 2:
        observatory, serial = fields
    elif len(fields) == 1:
        observatory, serial = fields + [""]
    else:
        raise ValueError("Invalid .pmap filename " + repr(filename))
    instrument, filekind = "", ""
    return instrument, filekind, serial

def get_imap_properties(filename):
    fields = _get_fields(filename)
    if len(fields) == 3:
        observatory, instrument, serial = fields
    elif len(fields) == 2:
        observatory, instrument, serial = fields + [""]
    else:
        raise ValueError("Invalid .imap filename " + repr(filename))
    filekind = ""
    return instrument, filekind, serial

def get_rmap_properties(filename):
    fields = _get_fields(filename)
    if len(fields) == 4:
        observatory, instrument, filekind, serial = fields
    elif len(fields) == 3:
        observatory, instrument, filekind, serial = fields + [""]
    else:
        raise ValueError("Invalid .imap filename " + repr(filename))
    return instrument, filekind, serial

CDBS_DIRS_TO_INSTR = {
   "/jref/":"acs",
   "/oref/":"stis",
   "/iref/":"wfc3",
   "/lref/":"cos",
}

def get_reference_properties(filename):
    """Figure out FITS (instrument, filekind, serial) based on `filename`."""
    try:   # Hopefully it's a nice new standard filename, easy
        return ref_properties_from_new_path(filename)
    except AssertionError:  # cryptic legacy paths & names, i.e. reality
        pass
    try:   # or maybe a recognizable HST legacy path/filename, fast
        return ref_properties_from_cdbs_path(filename)
    except AssertionError:
        pass
    # If not, dig inside the FITS file, slow
    return ref_properties_from_header(filename)

def ref_properties_from_new_path(filename):
    """Based on a CRDS `filename`,  return (instrument, filekind, serial).
    Raise AssertionError if it's not a good filename.
    """
    fields = _get_fields(filename)
    assert len(fields) == 4, "filename is not in standard format"
    observatory, instrument, filekind, serial = fields
    assert observatory == "hst",  "unknown observatory"
    assert instrument in ["acs","cos","stis","wfc3"], "unknown instrument"
    assert re.match("\d+", serial), "serial number field has non-digits"
    return instrument, filekind, serial

def ref_properties_from_cdbs_path(filename):
    """Based on a HST CDBS `filename`,  return (instrument, filekind, serial). 
    Raise AssertionError if it's not a good filename.
    """
    fields = _get_fields(filename)
    # For legacy files,  just use the root filename as the unique id
    serial = os.path.basename(os.path.splitext(filename)[0])
    # First try to figure everything out by decoding filename. fast
    for idir in CDBS_DIRS_TO_INSTR:
        if idir in filename:
            instrument = CDBS_DIRS_TO_INSTR[idir]
            break
    else:
        assert False, "CDBS instrument directory not found in filepath"
    ext = fields[-1]
    try:
        filekind = tpn.extension_to_filekind(instrument, ext)
    except KeyError:
        assert False, "Couldn't map extension " + repr(ext) + " to filekind."
    return instrument, filekind, serial

def ref_properties_from_header(filename):
    """Look inside FITS `filename` header to determine instrument, filekind.
    """
    import pyfits
    # For legacy files,  just use the root filename as the unique id
    serial = os.path.basename(os.path.splitext(filename)[0])
    location = locate_server_reference(os.path.basename(filename))
    instrument = pyfits.getval(location, "INSTRUME").lower()
    filetype = pyfits.getval(location, "FILETYPE")
    filekind = tpn.filetype_to_filekind(instrument, filetype)
    return instrument, filekind, serial

# ============================================================================

if __name__ == "__main__":
    main()

    