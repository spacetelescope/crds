"""This module provides functions which determine various observatory
specific policies for TOBS:

1. How to convert reference file basenames to fully specified paths.

2. How to manage parameters for reference file Validator objects used
in the certification of reference files.

"""
import os.path
import re

from crds.core import log, rmap, config, utils, timestamp
from crds import data_file
from crds.io import abstract

HERE = os.path.dirname(__file__) or "./"

# =======================================================================

# These two functions decouple the generic reference file certifier program
# from observatory-unique ways of specifying and caching Validator parameters.

from crds.tobs import TYPES, INSTRUMENTS, FILEKINDS, EXTENSIONS, INSTRUMENT_FIXERS, TYPE_FIXERS

get_row_keys_by_instrument = TYPES.get_row_keys_by_instrument
get_item = TYPES.get_item
suffix_to_filekind = TYPES.suffix_to_filekind
filekind_to_suffix = TYPES.filekind_to_suffix
get_all_tpninfos = TYPES.get_all_tpninfos

# =============================================================================
# Plugin-functions for this observatory,  accessed via locator.py

HERE = os.path.dirname(__file__) or "."

def tpn_path(tpn_file):
    return os.path.join(HERE, "tpns", tpn_file)

def get_extra_tpninfos(refpath):
    return []

def project_check(refpath):
    pass

def get_exptypes(instrument=None):
    """Return the list of EXP_TYPE values for instrument,  or for all
    instruments if instrument is not specified.
    """
    raise NotImplementedError("TOBS has not defined get_exptypes().")

# =======================================================================

# When loading headers,  make sure each keyword in a tuple is represented with
# the same value enabling any form to be used.
CROSS_STRAPPED_KEYWORDS = {
       # "META.INSTRUMENT.NAME" : ["INSTRUME", "INSTRUMENT", "META.INSTRUMENT.TYPE",],
    }

@utils.cached
def get_static_pairs():
    return abstract.equivalence_dict_to_pairs(CROSS_STRAPPED_KEYWORDS)

def get_cross_strapped_pairs(header):
    """Return the list of keyword pairs where each pair describes synonyms for the same
    piece of data.
    """
    return  get_static_pairs()

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
    if config.is_mapping(filename):
        return decompose_newstyle_name(filename)[2:4]
    elif REF_EXT_RE.search(filename):
        result = get_reference_properties(filename)[2:4]
    else:
        try:
            result = properties_inside_mapping(filename)
        except Exception as exc:
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
    assert re.fullmatch(r"\d*", serial), "Invalid id field " + \
        repr(id) + " in name " + repr(filename)
    # extension may vary for upload temporary files.

    return path, observatory, instrument, filekind, serial, ext

def properties_inside_mapping(filename):
    """Load `filename`s mapping header to discover and
    return (instrument, filekind).
    """
    mapping = rmap.fetch_mapping(filename)
    if mapping.filekind == "PIPELINE":
        result = "", ""
    elif mapping.filekind == "INSTRUMENT":
        result = mapping.instrument, ""
    else:
        result = mapping.instrument, mapping.filekind
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
    # If not, dig inside the FITS file, slow
    return ref_properties_from_header(filename)

def ref_properties_from_header(filename):
    """Look inside FITS `filename` header to determine instrument, filekind.
    """
    # For legacy files,  just use the root filename as the unique id
    path, _parts, ext = _get_fields(filename)
    serial = os.path.basename(os.path.splitext(filename)[0])
    header = data_file.get_header(filename)
    instrument = header["INSTRUME"].lower()
    filetype = header["FILETYPE"].lower()
    filekind = TYPES.filetype_to_filekind(instrument, filetype)
    return path, "tobs", instrument, filekind, serial, ext



# =======================================================================

def header_to_reftypes(header, context):
    """Based on `header` return the default list of appropriate reference type names."""
    return [] # translates to all types.

# =======================================================================

def reference_keys_to_dataset_keys(rmapping, header):
    """Given a header dictionary for a reference file,  map the header back to
    keys relevant to datasets.
    """
    result = dict(header)
    if "USEAFTER" in header:  # and "DATE-OBS" not in header:
        reformatted = timestamp.reformat_date(header["USEAFTER"]).split()
        result["DATE-OBS"] = reformatted[0]
        result["TIME-OBS"] = reformatted[1]
    return result

# =======================================================================

def condition_matching_header(rmapping, header):
    """Condition the matching header values to the normalized form of the .rmap"""
    return utils.condition_header(header)

# =======================================================================

def get_env_prefix(instrument):
    """Return the environment variable prefix (IRAF prefix) for `instrument`."""
    return "crds://"

def filekind_to_keyword(filekind):
    """Return the FITS keyword at which a reference should be recorded."""
    return filekind.upper()

def locate_file(refname, mode=None):
    """Given a valid reffilename in CDBS or CRDS format,  return a cache path for the file.
    The aspect of this which is complicated is determining instrument and an instrument
    specific sub-directory for it based on the filename alone,  not the file contents.
    """
    _path,  _observatory, instrument, _filekind, _serial, _ext = get_reference_properties(refname)
    rootdir = locate_dir(instrument, mode)
    return  os.path.join(rootdir, os.path.basename(refname))

def locate_dir(instrument, mode=None):
    """Locate the instrument specific directory for a reference file."""
    if mode is  None:
        mode = config.get_crds_ref_subdir_mode(observatory="tobs")
    else:
        config.check_crds_ref_subdir_mode(mode)
    crds_refpath = config.get_crds_refpath("tobs")
    prefix = get_env_prefix(instrument)
    if mode == "legacy":   # Locate cached files at the appropriate CDBS-style  iref$ locations
        try:
            rootdir = os.environ[prefix]
        except KeyError:
            try:
                rootdir = os.environ[prefix[:-1]]
            except KeyError as exc:
                raise KeyError(
                    "Reference location not defined for", repr(instrument),
                    ".  Did you configure", repr(prefix) + "?") from exc
    elif mode == "instrument":   # use simple names inside CRDS cache.
        rootdir = os.path.join(crds_refpath, instrument)
        refdir = os.path.join(crds_refpath, prefix[:-1])
        if not os.path.exists(refdir):
            if config.writable_cache_or_verbose("Skipping making instrument directory link for", repr(instrument)):
                log.verbose("Creating legacy cache link", repr(refdir), "-->", repr(rootdir))
                utils.ensure_dir_exists(rootdir + "/locate_dir.fits")
                os.symlink(rootdir, refdir)
    elif mode == "flat":    # use original flat cache structure,  all instruments in same directory.
        rootdir = crds_refpath
    else:
        raise ValueError("Unhandled reference file location mode " + repr(mode))
    return rootdir

# ============================================================================

def fits_to_parkeys(header):
    """Map a FITS header onto rmap parkeys appropriate for this observatory."""
    return dict(header)

# ============================================================================

def hijack_warnings(func, *args, **keys):
    """Re-map dependency warnings to CRDS warnings so they're counted and logged
    to web output.
    """
    with warnings.catch_warnings():
        # save and replace warnings.showwarning
        old_showwarning, warnings.showwarning = \
            warnings.showwarning, abstract.hijacked_showwarning

        # Always handle astropy warnings
        from astropy.utils.exceptions import AstropyUserWarning
        warnings.simplefilter("always", AstropyUserWarning)

        try:
            result = func(*args, **keys)
        finally:
            warnings.showwarning = old_showwarning

    return result

# =======================================================================

def test():
    """Run the module doctest_config."""
    import doctest
    from . import locate
    return doctest.testmod(locate)
