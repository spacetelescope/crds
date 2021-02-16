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
import datetime
import time
import warnings

# =======================================================================

from crds.core import log, rmap, config, utils, timestamp
from crds import data_file
from crds.core.exceptions import CrdsError, CrdsNamingError
from crds.hst import siname
from crds.io import abstract

# =======================================================================

# This block imports functions and globals defined in other modules to become
# part of the locator interface.

from crds.hst import TYPES, INSTRUMENTS, FILEKINDS, EXTENSIONS, INSTRUMENT_FIXERS, TYPE_FIXERS

get_row_keys_by_instrument = TYPES.get_row_keys_by_instrument
get_item = TYPES.get_item
suffix_to_filekind = TYPES.suffix_to_filekind
filekind_to_suffix = TYPES.filekind_to_suffix
get_all_tpninfos = TYPES.get_all_tpninfos

# =======================================================================
HERE = os.path.dirname(__file__) or "."

def tpn_path(tpn_file):
    return os.path.join(HERE, "tpns", tpn_file)

def get_extra_tpninfos(refpath):
    return []

def project_check(refpath, rmap):
    pass

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

def header_to_reftypes(header, context="hst-operational"):
    """Based on `header` return the default list of appropriate reference type names."""
    return []  # translates to everything.

def header_to_pipelines(header, context="hst-operational"):
    """Based on `header` return the default list of appropriate reference type names."""
    raise NotImplementedError("HST has not defined header_to_pipelines().")

def get_exptypes(instrument=None):
    """Return the list of EXP_TYPE values for instrument,  or for all
    instruments if instrument is not specified.
    """
    raise NotImplementedError("HST has not defined get_exptypes().")


# =======================================================================

def match_context_key(key):
    """Set the case of a context key (instrument or type) appropriately
    for this project, HST used upper case for instruments,  lower case
    for type names.
    """
    if key.lower() in INSTRUMENTS:
        return key.upper()
    elif key.lower() in FILEKINDS:
        return key.lower()
    else:
        return None

# =======================================================================

def reference_keys_to_dataset_keys(rmapping, header):
    """Given a header dictionary for a reference file,  map the header back to
    keys relevant to datasets.
    """
    result = dict(header)

    #  XXXXX TODO   Add/consolidate logic to handle P_ pattern keywords

    # If USEAFTER is defined,  or we're configured to fake it...
    #   don't invent one if its missing and we're not faking it.
    if "USEAFTER" in header or config.ALLOW_BAD_USEAFTER:

        # Identify reference involved as best as possible
        filename = header.get("FILENAME", None) or rmapping.filename

        reformatted = timestamp.reformat_useafter(filename, header).split()
        result["DATE-OBS"] = reformatted[0]
        result["DATE_OBS"] = reformatted[0]
        result["TIME-OBS"] = reformatted[1]
        result["TIME_OBS"] = reformatted[1]

    return result

# =======================================================================

def condition_matching_header(rmapping, header):
    """Condition the matching header values to the normalized form of the .rmap"""
    return utils.condition_header(header)

# =======================================================================

def get_file_properties(filename):
    """Figure out (instrument, filekind) based on `filename` which
    should be a mapping or FITS reference file.

    >>> get_file_properties("./hst_acs_biasfile_0001.rmap")
    ('acs', 'biasfile')

    >> get_file_properties("./hst_acs_biasfile_0001.pmap")
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
    elif config.is_reference(filename):
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
    assert instrument in INSTRUMENTS+[""], "Invalid instrument " + repr(instrument)
    assert filekind in FILEKINDS+[""], "Invalid filekind " + repr(filekind)
    # assert re.fullmatch(r"\d*", serial), "Invalid id field " + repr(id)

    # extension may vary for upload temporary files.

    return path, observatory, instrument, filekind, serial, ext

def properties_inside_mapping(filename):
    """Load `filename`s mapping header to discover and return (instrument, filekind).

    >>> from crds.tests import test_config
    >>> old_config = test_config.setup()

    >>> properties_inside_mapping("hst.pmap")
    ('', '')

    >>> properties_inside_mapping("hst_acs.imap")
    ('acs', '')

    >>> properties_inside_mapping("hst_acs_darkfile.rmap")
    ('acs', 'darkfile')

    >>> test_config.cleanup(old_config)
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

    >> from crds.tests import test_config
    >> old_config = test_config.setup()
    >> check_naming_consistency("acs")
    >> check_naming_consistency("cos")
    >> check_naming_consistency("nicmos")
    >> check_naming_consistency("stis")
    >> check_naming_consistency("wfc3")
    >> check_naming_consistency("wfpc2")
    >> test_config.cleanup(old_config)
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

                r = certify.certify.find_governing_rmap(pmap_name, ref)

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
    # try:
    #     return decompose_synphot_name(filename)
    # except AssertionError:
    #    pass
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
    if instrument == "synphot":
        if filename.endswith("_syn.fits"):
            filekind = "thruput"
        elif filename.endswith("_th.fits"):
            filekind = "thermal"
        elif filename.endswith("_tmt.fits"):
            filekind = "tmttab"
        elif filename.endswith("_tmg.fits"):
            filekind = "tmgtab"
        elif filename.endswith("_tmc.fits"):
            filekind = "tmctab"
        else:
            assert False, "Uknown synphot filetype for: " + repr(filename)
        suffix = filename.split("_")[-1][:-len(".fits")]
    elif extension == ".fits":
        suffix = fields[1]
    else:
        suffix = GEIS_EXT_TO_SUFFIX[extension[1:3]]
    try:
        filekind = TYPES.suffix_to_filekind(instrument, suffix)
    except KeyError:
        assert False, "Couldn't map extension/suffix " + repr(suffix) + " to filekind."
    return path, "hst", instrument, filekind, serial, extension

def instrument_from_refname(filename):
    """Based on `filename` rather than it's contents,  determine the associated
    instrument or raise an exception.

    >>> instrument_from_refname('hst_cos_spottab_0052.fits')
    'cos'

    >>> instrument_from_refname('zas1615jl_spot.fits')
    'cos'

    >>> instrument_from_refname('foobar.fits')
    Traceback (most recent call last):
    ...
    AssertionError: Cannot determine instrument for filename 'foobar.fits'
    """
    try:   # Hopefully it's a nice new standard filename, easy
        return decompose_newstyle_name(filename)[2]
    except AssertionError:  # cryptic legacy paths & names, i.e. reality
        try:
            instrument = siname.WhichCDBSInstrument(os.path.basename(filename)).lower()
            if instrument == "multi":
                instrument = "synphot"
            return instrument
        except Exception:
            assert False, "Cannot determine instrument for filename '{}'".format(filename)

def ref_properties_from_header(filename):
    """Look inside FITS `filename` header to determine:

    (path, "hst", instrument, filekind, serial, ext)
    """
    # For legacy files,  just use the root filename as the unique id
    path, _parts, ext = _get_fields(filename)
    serial = os.path.basename(os.path.splitext(filename)[0])
    header = data_file.get_free_header(filename, (), None, "hst")
    try:
        if "DBTABLE" not in header or header["DBTABLE"] in ["IMPHTTAB"]:
            instrument = header["INSTRUME"].lower()
        else:
            instrument = "synphot"
        instrument = INSTRUMENT_FIXERS.get(instrument, instrument)
    except KeyError as exc:
        raise CrdsNamingError("Can't determine instrument for",
                              repr(os.path.basename(filename)) + ".",
                              "CAL references must define INSTRUME,",
                              "SYNPHOT references define DBTABLE.") from exc
    try:
        filetype = header.get(
            "FILETYPE", header.get(
                "DBTABLE", header.get("CDBSFILE")))
        if filetype is None:
            raise KeyError
        else:
            filetype = filetype.lower()
    except KeyError:
        observatory = header.get(
            "TELESCOP", header.get(
                "TELESCOPE", None))
        if observatory is not None and observatory.upper() != "HST":
            raise CrdsNamingError(
                "CRDS is configured for 'HST' but file",
                repr(os.path.basename(filename)),
                "is for the", repr(observatory),
                "telescope.  Reconfigure CRDS_PATH or CRDS_SEVER_URL.")
        else:
            raise CrdsNamingError(
                "Can't determine HST file type for", repr(os.path.basename(filename)) + ".",
                "Check FILETYPE, CDBSFILE, DBTABLE, TELESCOP, and/or TELESCOPE.")
    filetype = TYPE_FIXERS.get((instrument, filetype), filetype)
    try:
        filekind = TYPES.filetype_to_filekind(instrument, filetype)
    except KeyError:
        raise CrdsNamingError(f"Invalid FILETYPE (or CDBSFILE) of '{filetype}' for instrument '{instrument}'.")
    return path, "hst", instrument, filekind, serial, ext

# ============================================================================

def generate_unique_name(filename, now=None):

    """Given an arbitrarily named filename (which must correctly define it's format, e.g. .fits)
    generate and return a unique enhanced CDBS-style name which incorporates a timestamp,
    and instrument id character, and a filetype suffix.

Character 1   : Year [z=2015, 0=2016, 1= 2017, etc.]
Character 2   : Month [1-9, a-c]
Character 3   : Day [1-9, a-s(28), t(29), u(30), v(31)]
Character 4-5: UT Hour [00 - 23]
Character 6-7: UT Minute [00 - 59]
Character 8   : UT Seconds [0-9, a-t (~2 second intervals)]
Character 9   : Instrument Designation [j=ACS, i=WFC3, o=STIS, l=COS,
u=WFPC2, n=NICMOS, m=SYNPHOT]
    """
    path, _obs, instr, filekind, _serial, ext = get_reference_properties(filename)

    name = generate_unique_name_core(instr, filekind, ext, now)

    return os.path.join(path, name)

def generate_unique_name_core(instr, filekind, extension, now=None):
    """Given an arbitrarily named filename (which must correctly define it's format, e.g. .fits)
    generate and return a unique enhanced CDBS-style name which incorporates a timestamp,
    and instrument id character, and a filetype suffix.

Character 1   : Year [z=2015, 0=2016, 1= 2017, etc.]
Character 2   : Month [1-9, a-c]
Character 3   : Day [1-9, a-s(28), t(29), u(30), v(31)]
Character 4-5: UT Hour [00 - 23]
Character 6-7: UT Minute [00 - 59]
Character 8   : UT Seconds [0-9, a-t (~2 second intervals)]
Character 9   : Instrument Designation [j=ACS, i=WFC3, o=STIS, l=COS,
u=WFPC2, n=NICMOS, m=MULTI, m=SYNPHOT]
    """
    if now is None:   # delay to ensure timestamp is unique.
        time.sleep(2)

    timeid = generate_timestamp(now)

    suffix = "_" + filekind_to_suffix(instr, filekind)
    instr_char = siname.instrument_to_id_char(instr)

    return timeid + instr_char + suffix + extension

def generate_timestamp(now=None):

    """Generate an enhanced CDBS-style uniqname."""

    if now is None:
        now = datetime.datetime.utcnow()

    if now.year < 2016:
        year = chr(now.year - 2015 + ord('z'))
    elif 2016 <= now.year <= 2025:
        year = chr(now.year - 2016 + ord('0'))
    else:
        raise RuntimeError("Unique names are not defined for 2026 and beyond.")

    if 1 <= now.month <= 9:
        month = chr(now.month - 1 + ord('1'))
    elif 10 <= now.month <= 12:
        month = chr(now.month - 10 + ord('a'))

    if 1 <= now.day <= 9:
        day = chr(now.day - 1 + ord('1'))
    elif 10 <= now.day <= 31:
        day = chr(now.day - 10 + ord('a'))

    hour = "%02d" % now.hour
    minute = "%02d" % now.minute

    hsecs = now.second // 2
    if 0 <= hsecs <= 9:
        second = chr(hsecs + ord('0'))
    elif 10 <= hsecs <= 59:
        second = chr(hsecs - 10 + ord('a'))

    return "".join([year, month, day, hour, minute, second])

# ============================================================================

# HST FITS headers have filenames adorned with environment prefixes for each
# instrument.

def get_env_prefix(instrument):
    """Return the environment variable prefix (IRAF prefix) for `instrument`."""
    return siname.add_IRAF_prefix(instrument.upper())

def filekind_to_keyword(filekind):
    """Return the FITS keyword at which a reference should be recorded."""
    return filekind.upper()

def locate_file(refname, mode=None):
    """Given a valid reffilename in CDBS or CRDS format,  return a cache path for the file.
    The aspect of this which is complicated is determining instrument and an instrument
    specific sub-directory for it based on the filename alone,  not the file contents.
    """
    try:
        instrument = instrument_from_refname(refname)
    except Exception:
        instrument = get_reference_properties(refname)[1]
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
    elif mode == "instrument" and instrument != "synphot":   # use simple names inside CRDS cache.
        rootdir = os.path.join(crds_refpath, instrument)
        refdir = os.path.join(crds_refpath, prefix[:-1])
        if not os.path.exists(refdir):
            if config.writable_cache_or_verbose("Skipping making instrument directory link for", repr(instrument)):
                log.verbose("Creating legacy cache link", repr(refdir), "-->", repr(rootdir))
                with log.verbose_warning_on_exception("Failed creating legacy symlink:", refdir, "-->", rootdir):
                    utils.ensure_dir_exists(rootdir + "/locate_dir.fits")
                    os.symlink(rootdir, refdir)
    elif mode == "instrument" and instrument == "synphot":
        rootdir = os.path.join(crds_refpath, instrument)
    elif mode == "flat":    # use original flat cache structure,  all instruments in same directory.
        rootdir = crds_refpath
    else:
        raise ValueError("Unhandled reference file location mode " + repr(mode))
    return rootdir

# ============================================================================

def fits_to_parkeys(header):
    """Map a FITS header onto rmap parkeys appropriate for this observatory."""
    return dict(header)

# =======================================================================

def test():
    """Run the module doctests."""
    import doctest
    from crds.hst import locate
    return doctest.testmod(locate)

# =======================================================================

if __name__ == "__main__":
    print(test())
