"""This module provides functions which determine various observatory
specific policies for TOBS:

1. How to convert reference file basenames to fully specified paths.

2. How to manage parameters for reference file Validator objects used
in the certification of reference files. 

"""
import os.path
import gzip
import re

from crds import (log, rmap, data_file, config)
from . import tpn

HERE = os.path.dirname(__file__) or "./"

# =======================================================================

def test():
    """Run the module doctests."""
    import doctest, locate
    return doctest.testmod(locate)

# =======================================================================

def locate_server_reference(reference):
    """Return the absolute path for the server-side copy of a reference file. Default cache path."""
    return config.locate_file(reference, "tobs")

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

from crds.tobs.tpn import reference_name_to_validator_key, mapping_validator_key, get_tpninfos
from crds.tobs.__init__ import INSTRUMENTS, FILEKINDS, EXTENSIONS

# =======================================================================

REF_EXT_RE = re.compile(r"\.fits|\.r\dh$")

def get_file_properties(filename):
    """Figure out (instrument, filekind, serial) based on `filename` which
    should be a mapping or FITS reference file.

    >> get_file_properties("./hst_acs_biasfile_0001.rmap")
    ('acs', 'biasfile')

    >> get_file_properties("./hst_acs_biasfile_0001.pmap")
    Traceback (most recent call last):
    ...
    AssertionError: Invalid .pmap filename './hst_acs_biasfile_0001.pmap'

    >> get_file_properties("test_data/s7g1700gl_dead.fits")
    """
    if rmap.is_mapping(filename):
        return decompose_newstyle_name(filename)[2:4]
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
    >> decompose_newstyle_name("./hst.pmap")
    ('.', 'hst', '', '', '', '.pmap')

    >> decompose_newstyle_name("./hst_0001.pmap")
    ('.', 'hst', '', '', '0001', '.pmap')

    >> decompose_newstyle_name("./hst_acs.imap")
    ('.', 'hst', 'acs', '', '', '.imap')

    >> decompose_newstyle_name("./hst_acs_0001.imap")
    ('.', 'hst', 'acs', '', '0001', '.imap')

    >> decompose_newstyle_name("./hst_acs_biasfile.rmap")
    ('.', 'hst', 'acs', 'biasfile', '', '.rmap')

    >> decompose_newstyle_name("./hst_acs_biasfile_0001.rmap")
    ('.', 'hst', 'acs', 'biasfile', '0001', '.rmap')

    >> decompose_newstyle_name("./hst_acs_biasfile.fits")
    ('.', 'hst', 'acs', 'biasfile', '', '.fits')

    >> decompose_newstyle_name("./hst_acs_biasfile_0001.fits")
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
    except AssertionError:
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
    return path, "hst", instrument, filekind, serial, ext

def ref_properties_from_header(filename):
    """Look inside FITS `filename` header to determine instrument, filekind.
    """
    # For legacy files,  just use the root filename as the unique id
    path, parts, ext = _get_fields(filename)
    serial = os.path.basename(os.path.splitext(filename)[0])
    header = data_file.get_header(filename)
    instrument = header["INSTRUME"].lower()
    filetype = header["FILETYPE"].lower()
    filekind = tpn.filetype_to_filekind(instrument, filetype)
    return path, "hst", instrument, filekind, serial, ext


def handle_undefined_rmap(self, filekind):
    """Customize how TOBS handles undefined types for an instrument in InstrumentContext.get_rmap(): Raise exception."""
    raise crds.CrdsUnknownReftypeError("Unknown reference type " + repr(str(filekind)))

