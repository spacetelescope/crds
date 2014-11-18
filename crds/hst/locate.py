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
import glob

# import crds.pysh as pysh
from crds import (log, rmap, pysh, data_file, config, utils, timestamp)
from crds import CrdsError
from crds.hst import siname, reftypes

HERE = os.path.dirname(__file__) or "./"

# =======================================================================

# REFNAM_TO_PATH is a mapping from { reference_basename : reference_absolute_path }
REFNAME_TO_PATH = {}

def locate_server_reference(ref_filename):
    """Effectively,  search the given  `cdbs` filetree for `ref_filename`
    and return the absolute path.
    
    This translates a name like 'v4q2144qj_bia.fits' into an absolute path
    which most likely depends on instrument.
    
    """
    # return files with paths already unchanged.
    if not os.path.basename(ref_filename) == ref_filename:
        return ref_filename
    if not REFNAME_TO_PATH:
        setup_path_map()
    return REFNAME_TO_PATH[ref_filename]
    
def setup_path_map(rebuild_cache=False):
    """Dump the directory tree `cdbs` into a file and read the results
    into a global map from file basename to absolute path.
    """
    cachepath = HERE + "/cdbs.paths.gz"
    if not os.path.exists(cachepath) or rebuild_cache:
        log.info("Generating CDBS file path cache.")
        pysh.sh("find  /grp/hst/cdbs | gzip -c >cdbs.paths.gz")  # secure.
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

from crds.hst.reftypes import reference_name_to_validator_key, mapping_validator_key
from crds.hst.reftypes import get_row_keys, get_row_keys_by_instrument, get_item
from crds.hst.tpn import get_tpninfos, reference_name_to_tpn_text, reference_name_to_ld_tpn_text
from crds.hst import INSTRUMENTS, FILEKINDS, EXTENSIONS
from crds.hst.substitutions import expand_wildcards

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
        except Exception:
            return properties_inside_mapping(filename)
    elif REF_EXT_RE.search(filename):
        result = get_reference_properties(filename)[2:4]
    else:
        try:
            result = properties_inside_mapping(filename)
        except Exception:
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
        assert len(parts) in [1, 2], "Invalid .pmap filename " + repr(filename)
        instrument, filekind = "", ""
        serial = list_get(parts, 1, "")
    elif ext == ".imap":
        assert len(parts) in [2, 3], "Invalid .imap filename " + repr(filename)
        instrument = parts[1]
        filekind = ""
        serial = list_get(parts, 2, "")
    else:
        assert len(parts) in [3, 4], "Invalid filename " + repr(filename)
        instrument = parts[1]
        filekind = parts[2]
        serial = list_get(parts, 3, "")

    assert observatory == "hst"
    assert instrument in INSTRUMENTS+[""], "Invalid instrument " + \
        repr(instrument) + " in name " + repr(filename)
    assert filekind in FILEKINDS+[""], "Invalid filekind " + \
        repr(filekind) + " in name " + repr(filename)

    # assert re.match("\d*", serial), "Invalid id field " + \
    #     repr(id) + " in name " + repr(filename)
    
# extension may vary for upload temporary files.

    return path, observatory, instrument, filekind, serial, ext

def properties_inside_mapping(filename):
    """Load `filename`s mapping header to discover and 
    return (instrument, filekind).
    """
    loaded = rmap.fetch_mapping(filename)
    if loaded.mapping == "pipeline":
        result = "", ""
    elif loaded.mapping == "instrument":
        result = loaded.instrument, ""
    else:
        result = loaded.instrument, loaded.filekind
    return result

def _get_fields(filename):
    """Break CRDS-style filename down into: path, underscore-separated-parts, extension."""
    path = os.path.dirname(filename)
    name = os.path.basename(filename)
    name, ext = os.path.splitext(name)
    parts = name.split("_")
    return path, parts, ext

def list_get(the_list, index, default):
    """Fetch the `index` item from `the_list`, or return `default` on IndexError.  Like dict.get()."""
    try:
        return the_list[index]
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

def check_naming_consistency(checked_instrument=None, exhaustive_mapping_check=False):
    """Dev function to compare the properties returned by name decomposition
    to the properties determined by file contents and make sure they're the same.
    Also checks rmap membership.
    """
    from crds import certify

    for ref in rmap.list_references("*", observatory="hst", full_path=True):
        with log.error_on_exception("Failed processing:", repr(ref)):

            _path, _observ, instrument, filekind, _serial, _ext = ref_properties_from_cdbs_path(ref)

            if checked_instrument is not None and instrument != checked_instrument:

                continue

            if data_file.is_geis_data(ref):
                if os.path.exists(data_file.get_conjugate(ref)):
                    continue
                else:
                    log.warning("No GEIS header for", repr(ref))

            log.verbose("Processing:", instrument, filekind, ref)
            
            _path2, _observ2, instrument2, filekind2, _serial2, _ext2 = ref_properties_from_header(ref)
            if instrument != instrument2:
                log.error("Inconsistent instruments", repr(instrument), "vs.", repr(instrument2), 
                          "for", repr(ref))
            if filekind != filekind2:
                log.error("Inconsistent filekinds", repr(filekind), "vs.", repr(filekind2), 
                          "for", repr(ref))

            for pmap_name in reversed(sorted(rmap.list_mappings("*.pmap", observatory="hst"))):

                pmap = rmap.get_cached_mapping(pmap_name)

                r = certify.find_governing_rmap(pmap_name, ref)

                if not r:
                    continue

                if r.instrument != instrument:
                    log.error("Rmap instrument", repr(r.instrument), 
                              "inconsistent with name derived instrument", repr(instrument), "for", repr(ref), "in", repr(pmap_name))
                if r.filekind != filekind:
                    log.error("Rmap filekind", repr(r.filekind), 
                              "inconsistent with name derived filekind", repr(filekind), "for", repr(ref), "in", repr(pmap_name))
                if r.instrument != instrument2:
                    log.error("Rmap instrument", repr(r.instrument), 
                              "inconsistent with content derived instrument", repr(instrument2), "for", repr(ref), "in", repr(pmap_name))
                if r.filekind != filekind2:
                    log.error("Rmap filekind", repr(r.filekind), 
                              "inconsistent with content derived filekind", repr(filekind2), "for", repr(ref), "in", repr(pmap_name))
                
                if not exhaustive_mapping_check:
                    break

            else:
                log.error("Orphan reference", repr(ref), "not found under any context.")
            
def get_reference_properties(filename):
    """Figure out FITS (instrument, filekind, serial) based on `filename`."""
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

GEIS_EXT_TO_SUFFIX = {
    "r0" : "msk",     # Static mask
    "r1" : "a2d",     # A-to-D lookup tables
    "r2" : "bas",     # Bias
    "r3" : "drk",     # Preflash
    "r4" : "flt",     # Superpurge
    "r5" : "shd",     # Shutter Shading Reference
    "r6" : "flt",     # Flat field
    "r7" : "w4t",     # wf4tfile
}

def ref_properties_from_cdbs_path(filename):
    """Based on a HST CDBS `filename`,  return 
    
    (path, "hst", instrument, filekind, serial, ext)

    Raise AssertionError if it's not a good filename.
    """
    path, fields, extension = _get_fields(filename)
    # For legacy files,  just use the root filename as the unique id
    serial = os.path.basename(os.path.splitext(filename)[0])
    # First try to figure everything out by decoding filename. fast
    instrument = siname.WhichCDBSInstrument(os.path.basename(filename)).lower()
    if extension == ".fits":
        ext = fields[1]
    else:
        ext = GEIS_EXT_TO_SUFFIX[extension[1:3]]
    try:
        filekind = reftypes.extension_to_filekind(instrument, ext)
    except KeyError:
        assert False, "Couldn't map extension " + repr(ext) + " to filekind."
    return path, "hst", instrument, filekind, serial, extension

INSTRUMENT_FIXERS = {
    "wfii": "wfpc2",
}

TYPE_FIXERS = {
    ("wfpc2","dark") : "drk", 
}


def ref_properties_from_header(filename):
    """Look inside FITS `filename` header to determine:

    (path, "hst", instrument, filekind, serial, ext) 

    """
    # For legacy files,  just use the root filename as the unique id
    path, _parts, ext = _get_fields(filename)
    serial = os.path.basename(os.path.splitext(filename)[0])
    header = data_file.get_header(filename)
    instrument = header["INSTRUME"].lower()
    if instrument in INSTRUMENT_FIXERS:
        instrument = INSTRUMENT_FIXERS[instrument]
    try:
        filetype = header["FILETYPE"].lower()
    except KeyError:
        try:
            filetype = header["CDBSFILE"].lower()
        except KeyError:
            raise CrdsError("File '{}' missing FILETYPE and CDBSFILE,  type not identifiable.".format(os.path.basename(filename)))
    filetype = TYPE_FIXERS.get((instrument, filetype), filetype)
    try:
        filekind = reftypes.filetype_to_filekind(instrument, filetype)
    except KeyError:
        raise CrdsError("Invalid FILETYPE (or CDBSFILE) for '{}' of instrument '{}'." .format(filetype, instrument))
    return path, "hst", instrument, filekind, serial, ext

# ============================================================================

# HST FITS headers have filenames adorned with environment prefixes for each
# instrument.

def get_env_prefix(instrument):
    """Return the environment variable prefix (IRAF prefix) for `instrument`."""
    return siname.add_IRAF_prefix(instrument.upper())

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
        mode = config.get_crds_ref_subdir_mode(observatory="hst")
    else:
        config.check_crds_ref_subdir_mode(mode)
    crds_refpath = config.get_crds_refpath("hst")
    prefix = get_env_prefix(instrument)
    if mode == "legacy":   # Locate cached files at the appropriate CDBS-style  iref$ locations
        try:
            rootdir = os.environ[prefix]
        except KeyError:
            try:
                rootdir = os.environ[prefix[:-1]]
            except KeyError:
                raise KeyError("Reference location not defined for " + repr(instrument) + 
                               ".  Did you configure " + repr(prefix) + "?")
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

def load_all_type_constraints():
    """Make sure that all HST .tpn files are loadable."""
    from crds import certify
    tpns = glob.glob(os.path.join(HERE, "tpns", "*.tpn"))
    for tpn_path in tpns:
        tpn_name = tpn_path.split("/")[-1]  # simply lost all patience with basename and path.split
        log.verbose("Loading", repr(tpn_name))
        certify.validators_by_typekey((tpn_name,), "hst")

# ============================================================================

def handle_undefined_rmap(self, filekind):
    """Customize how HST handles undefined types for an instrument in InstrumentContext.get_rmap(): Raise exception."""
    raise crds.CrdsUnknownReftypeError("Unknown reference type " + repr(str(filekind)))

# ============================================================================

__all__ = [
    "INSTRUMENTS",

    "reference_name_to_validator_key",
    "mapping_validator_key",
    "get_tpninfos",
    "reference_name_to_tpn_text",
    "reference_name_to_ld_tpn_text",
    "load_all_type_constraints",
    "get_item",

    "get_env_prefix",
    "decompose_newstyle_name",
    "locate_dir",
    "get_file_properties",

    "get_row_keys",
    "get_row_keys_by_instrument",
    
    "fits_to_parkeys",
    "reference_keys_to_dataset_keys",
    "expand_wildcards",
    "condition_matching_header",

    "handle_undefined_rmap",
]

for name in __all__:
    assert name in dir()

# ============================================================================

if __name__ == "__main__":
    main()
