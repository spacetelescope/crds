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
from crds import (log, rmap, pysh, data_file, config, utils)
from crds.hst import (tpn, siname)

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
    # return files with paths already unchanged.
    if not os.path.basename(ref_filename) == ref_filename:
        return ref_filename
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
        if filename in REFNAME_TO_PATH:
            if "linux" in dirname:
                log.verbose_warning("Reference file " + repr(filename) + " found more than once.  Overriding with Linux version.")
                REFNAME_TO_PATH[filename] = line
            else:
                log.verbose_warning("Reference file " + repr(filename) + " found more than once.  Keeping original version since 'linux' not in new path.")
        else:
            REFNAME_TO_PATH[filename] = line

def main():
    """Regenerate the CDBS path cache."""
    # log.set_verbose()
    setup_path_map(rebuild_cache=True)

def test():
    """Run the module doctests."""
    import doctest
    from crds.hst import locate
    return doctest.testmod(locate)

# =======================================================================

def reference_exists(reference):
    """Return True iff basename `reference` is known/exists in CRDS.
    """
    try:
        where = locate_server_reference(reference)
    except KeyError:
        return False
    return os.path.exists(where)

# =======================================================================

# These two functions decouple the generic reference file certifier program 
# from observatory-unique ways of specifying and caching Validator parameters.

from crds.hst.tpn import reference_name_to_validator_key, mapping_validator_key, get_tpninfos
from crds.hst import INSTRUMENTS, FILEKINDS, EXTENSIONS
from crds.hst.substitutions import expand_wildcards
from crds.hst.parkeys import reference_keys_to_dataset_keys

# =======================================================================

REF_EXT_RE = re.compile(r"\.fits|\.r\dh$")

def get_file_properties(filename):
    """Figure out (instrument, filekind) based on `filename` which
    should be a mapping or FITS reference file.

    >>> get_file_properties("./hst_acs_biasfile_0001.rmap")
    ('acs', 'biasfile')

    >>> get_file_properties("./hst_acs_biasfile_0001.pmap")
    Traceback (most recent call last):
    ...
    IOError: [Errno 2] No such file or directory: './hst_acs_biasfile_0001.pmap'

    >> get_file_properties("test_data/s7g1700gl_dead.fits")
    """
    if data_file.is_geis_data(filename):
        # determine GEIS data file properties from corresponding header file.
        filename = filename[:-1] + "h"
    if config.is_mapping(filename):
        try:
            return decompose_newstyle_name(filename)[2:4]
        except Exception, exc:
            return properties_inside_mapping(filename)
    elif REF_EXT_RE.search(filename):
        result = get_reference_properties(filename)[2:4]
    else:
        try:
            result = properties_inside_mapping(filename)
        except Exception, exc:
            result = get_reference_properties(filename)[2:4]
    assert result[0] in INSTRUMENTS+[""], "Bad instrument " + \
        repr(result[0]) + " in filename " + repr(filename)
    assert result[1] in FILEKINDS+[""], "Bad filekind " + \
        repr(result[1]) + " in filename " + repr(filename)
    return result

def decompose_newstyle_name(filename):
    """
    >>> decompose_newstyle_name("./hst.pmap")
    ('.', 'hst', '', '', '', '.pmap')

    >>> decompose_newstyle_name("./hst_0001.pmap")
    ('.', 'hst', '', '', '0001', '.pmap')

    >>> decompose_newstyle_name("./hst_acs.imap")
    ('.', 'hst', 'acs', '', '', '.imap')

    >>> decompose_newstyle_name("./hst_acs_0001.imap")
    ('.', 'hst', 'acs', '', '0001', '.imap')

    >>> decompose_newstyle_name("./hst_acs_biasfile.rmap")
    ('.', 'hst', 'acs', 'biasfile', '', '.rmap')

    >>> decompose_newstyle_name("./hst_acs_biasfile_0001.rmap")
    ('.', 'hst', 'acs', 'biasfile', '0001', '.rmap')

    >>> decompose_newstyle_name("./hst_acs_biasfile.fits")
    ('.', 'hst', 'acs', 'biasfile', '', '.fits')

    >>> decompose_newstyle_name("./hst_acs_biasfile_0001.fits")
    ('.', 'hst', 'acs', 'biasfile', '0001', '.fits')
    """
    path, parts, ext = _get_fields(filename)
    observatory = parts[0]
    serial = list_get(parts, 3, "")

    if ext == ".pmap":
        assert len(parts) in [1,2], "Invalid .pmap filename " + repr(filename)
        instrument, filekind = "", ""
        serial = list_get(parts, 1, "")
    elif ext == ".imap":
        assert len(parts) in [2,3], "Invalid .imap filename " + repr(filename)
        instrument = parts[1]
        filekind = ""
        serial = list_get(parts, 2, "")
    else:
        assert len(parts) in [3,4], "Invalid filename " + repr(filename)
        instrument = parts[1]
        filekind = parts[2]
        serial = list_get(parts, 3, "")

    assert observatory == "hst"
    assert instrument in INSTRUMENTS+[""], "Invalid instrument " + \
        repr(instrument) + " in name " + repr(filename)
    assert filekind in FILEKINDS+[""], "Invalid filekind " + \
        repr(filekind) + " in name " + repr(filename)
    assert re.match("\d*", serial), "Invalid id field " + \
        repr(id) + " in name " + repr(filename)
    # extension may vary for upload temporary files.

    return path, observatory, instrument, filekind, serial, ext

def properties_inside_mapping(filename):
    """Load `filename`s mapping header to discover and 
    return (instrument, filekind).
    """
    map = rmap.fetch_mapping(filename)
    if map.filekind == "PIPELINE":
        result = "", ""
    elif map.filekind == "INSTRUMENT":
        result = map.instrument, ""
    else:
        result = map.instrument, map.filekind
    return result

def _get_fields(filename):
    path = os.path.dirname(filename)
    name = os.path.basename(filename)
    name, ext = os.path.splitext(name)
    parts = name.split("_")
    return path, parts, ext

def list_get(l, index, default):
    try:
        return l[index]
    except IndexError:
        return default

CDBS_DIRS_TO_INSTR = {
   "/jref/":"acs",
   "/oref/":"stis",
   "/iref/":"wfc3",
   "/lref/":"cos",
   "/nref/":"nicmos",
   
   "/upsf/":"wfpc2",
   "/uref/":"wfpc2",
   "/uref_linux/":"wfpc2",
   
   "/yref/" : "fos",
   "/zref/" : "hrs",
   
}

def get_reference_properties(filename):
    """Figure out FITS (instrument, filekind, serial) based on `filename`.
    """
    try:   # Hopefully it's a nice new standard filename, easy
        return decompose_newstyle_name(filename)
    except AssertionError:  # cryptic legacy paths & names, i.e. reality
        pass
    try:   # or maybe a recognizable HST legacy path/filename, fast
        return ref_properties_from_cdbs_path(filename)
    except Exception:
        pass
    # If not, dig inside the FITS file, slow
    return ref_properties_from_header(filename)

def ref_properties_from_cdbs_path(filename):
    """Based on a HST CDBS `filename`,  return (instrument, filekind, serial). 
    Raise AssertionError if it's not a good filename.
    """
    path, fields, ext = _get_fields(filename)
    # For legacy files,  just use the root filename as the unique id
    serial = os.path.basename(os.path.splitext(filename)[0])
    # First try to figure everything out by decoding filename. fast
    instrument = siname.WhichCDBSInstrument(os.path.basename(filename)).lower()
    ext = fields[-1]
    try:
        filekind = tpn.extension_to_filekind(instrument, ext)
    except KeyError:
        assert False, "Couldn't map extension " + repr(ext) + " to filekind."
    return path, "hst", instrument, filekind, serial, ext

INSTRUMENT_FIXERS = {
    "wfii": "wfpc2",
}

def ref_properties_from_header(filename):
    """Look inside FITS `filename` header to determine instrument, filekind.
    """
    # For legacy files,  just use the root filename as the unique id
    path, parts, ext = _get_fields(filename)
    serial = os.path.basename(os.path.splitext(filename)[0])
    header = data_file.get_header(filename)
    instrument = header["INSTRUME"].lower()
    if instrument in INSTRUMENT_FIXERS:
        instrument = INSTRUMENT_FIXERS[instrument]
    filetype = header["FILETYPE"].lower()
    filekind = tpn.filetype_to_filekind(instrument, filetype)
    return path, "hst", instrument, filekind, serial, ext

# ============================================================================

# HST FITS headers have filenames adorned with environment prefixes for each
# instrument.

def get_env_prefix(instrument):
    """Return the environment variable prefix (IRAF prefix) for `instrument`."""
    return siname.add_IRAF_prefix(instrument.upper())

# ============================================================================

def fits_to_parkeys(header):
    """Map a FITS header onto rmap parkeys appropriate for this observatory."""
    return dict(header)

# ============================================================================

if __name__ == "__main__":
    main()
