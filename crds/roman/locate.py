"""This module provides functions which determine various observatory
specific policies/plugins for Roman:

1. How to convert reference file basenames to fully specified paths.

2. How to manage parameters for reference file Validator objects used
in the certification of reference files.

XXXX Roman NOTE: This code was derived from the JWST locate.py module and
contains substantial duplication.  However, because the functions often depend
on project-specific modules, globals, or functions the code is not usable
without some refactoring.  Other plugins may vary simply because
ASDF+datamodels Roman is already different than the FITS+datamodels world of
JWST, e.g. there is no longer a need for FITS <-> datamodels translations and
log annotation, i.e.  AKA keyword cross-strapping.

"""
import os.path
import re
import warnings
from collections import namedtuple

# =======================================================================

from crds.core import rmap, config, utils, timestamp, log, exceptions
from crds.certify import generic_tpn
from crds import data_file
from crds.io import abstract

# =======================================================================

# These two functions decouple the generic reference file certifier program
# from observatory-unique ways of specifying and caching Validator parameters.

from crds.roman import TYPES, INSTRUMENTS, FILEKINDS, EXTENSIONS, INSTRUMENT_FIXERS, TYPE_FIXERS

from . import schema

# definitively lists possible exp_types by instrument, or all instruments
from .schema import get_exptypes    #  XXXX roman

get_row_keys_by_instrument = TYPES.get_row_keys_by_instrument
get_item = TYPES.get_item
suffix_to_filekind = TYPES.suffix_to_filekind
filekind_to_suffix = TYPES.filekind_to_suffix
get_all_tpninfos = TYPES.get_all_tpninfos

HERE = os.path.dirname(__file__) or "."

# =======================================================================

# XXXX roman  TODO needed for scratch JWST repro scheme,  itself incomplete
# from crds.jwst.pipeline import header_to_reftypes, header_to_pipelines

# Stub like HST for now

def header_to_reftypes(header, context="roman-operational"):
    """Based on `header` return the default list of appropriate reference type names.

    >>> ref_types = header_to_reftypes(None)
    >>> print(ref_types)
    []

    """
    return []  # translates to "all types" for instrument defined by header.

def header_to_pipelines(header, context="roman-operational"):
    """Based on `header` return the default list of appropriate reference type names.

    >>> header_to_pipelines(None)
    Traceback (most recent call last):
    ...
    NotImplementedError: Roman has not defined header_to_pipelines().

    """
    raise NotImplementedError("Roman has not defined header_to_pipelines().")

# =======================================================================

MODEL = None

def get_datamodels():
    """Defer datamodels loads until we definitely have a roman usecase.
    Enables light observatory package imports which don't require all
    dependencies when supporting other observatories.

    >>> get_datamodels() # doctest: +ELLIPSIS
    <module 'romancal.datamodels' from .../romancal/datamodels/__init__.py'>

    """
    try:
        from romancal import datamodels
    except ImportError:
        log.error(
            "CRDS requires installation of the 'romancal' package to operate on Roman files.")
        raise
    global MODEL
    if MODEL is None:
        with log.error_on_exception(
                "Failed constructing basic RomanDataModel"):
            MODEL = datamodels.RomanDataModel()
    return datamodels

# =============================================================================

def tpn_path(tpn_file):
    """Return the full filepath of `tpn_file`.

    >>> tpn_path('tpn_file.tpn') # doctest: +ELLIPSIS
    '.../crds/roman/tpns/tpn_file.tpn'

    """
    return os.path.join(HERE, "tpns", tpn_file)

def get_extra_tpninfos(refpath):
    """Returns TpnInfos (valid value enumerations) derived from the cal code data models schema.

    This can be useful to leverage datamodels (core?) schema for rmap checking.

    Datamodels schema historically lack per-instrument granularity so the canonical .tpn scheme
    can catch errors not caught by the schema,  e.g. MIRI values used in a NIRCAM reference
    file because a reference file was cloned and not properly updated.

    These tend to have a superset of acceptable values for any particular instrument,
    particularly since CRDS has historically only loaded the core schema.

    >>> get_extra_tpninfos(None)
    []

    """
    return []   # use this to ignore datamodels schema for CRDS value checking
    # XXXX roman  -- datamodels schema scraping can potentially be enabled once
    # romancal and datamodels are integrated.   This will effectively translate the
    # datamodels schema (core unless work is done) automatically as-if they were
    # being specified in CRDS .tpn files.
    # return schema.get_schema_tpninfos(refpath)

def project_check(refpath):
    """
    >>> get_data_model_flat_dict('crds/tests/data/roman_wfi16_f158_flat_small.asdf')
    {'asdf_library.author': 'Space Telescope Science Institute', 'asdf_library.homepage': 'http://github.com/spacetelescope/asdf', 'asdf_library.name': 'asdf', 'asdf_library.version': '2.7.1', 'history.entries.0.description': 'Creation of dummy flat file for CRDS testing during DMS build 0.0.', 'history.entries.0.time': '2020-11-04T20:01:23', 'history.entries.1.description': 'Update of dummy flat file to test history entries.', 'history.entries.1.time': '2020-11-04T20:02:13', 'history.extensions.0.extension_class': 'astropy.io.misc.asdf.extension.AstropyAsdfExtension', 'history.extensions.0.software.name': 'astropy', 'history.extensions.0.software.version': '4.1', 'history.extensions.1.extension_class': 'asdf.extension.BuiltinExtension', 'history.extensions.1.software.name': 'asdf', 'history.extensions.1.software.version': '2.7.1', 'data': array([[0., 0., 0., 0.],
           [0., 0., 0., 0.],
           [0., 0., 0., 0.],
           [0., 0., 0., 0.]], dtype=float32), 'dq': array([[0, 0, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0]], dtype=uint16), 'err': array([[0., 0., 0., 0.],
           [0., 0., 0., 0.],
           [0., 0., 0., 0.],
           [0., 0., 0., 0.]], dtype=float32), 'meta.author': 'Space Telescope Science Institute', 'meta.date': '2020-12-02T22:56:06.721', 'meta.description': 'Flat reference file.', 'meta.filename': 'roman_wfi16_f158_flat_small.asdf', 'meta.instrument.detector': 'WFI16', 'meta.instrument.name': 'WFI', 'meta.instrument.optical_element': 'F158', 'meta.model_type': 'FlatModel', 'meta.pedigree': 'DUMMY', 'meta.reftype': 'FLAT', 'meta.telescope': 'ROMAN', 'meta.useafter': '2020-01-01T00:00:00.000'}

    """
    return get_data_model_flat_dict(refpath)

def get_data_model_flat_dict(filepath):
    """Get the header from `filepath` using the roman data model.  Data model
    dotted object paths are reduced to capitalized dot-separated FITS-like
    keyword strings and a simple key,value dictionary format vs. nested objects.

    e.g.  meta.instrument.name  -->  "META.INSTRUMENT.NAME'

    Returns   { file_keyword : keyword_value, ... }

    >>> get_data_model_flat_dict('crds/tests/data/roman_wfi16_f158_flat_small.asdf')
    {'asdf_library.author': 'Space Telescope Science Institute', 'asdf_library.homepage': 'http://github.com/spacetelescope/asdf', 'asdf_library.name': 'asdf', 'asdf_library.version': '2.7.1', 'history.entries.0.description': 'Creation of dummy flat file for CRDS testing during DMS build 0.0.', 'history.entries.0.time': '2020-11-04T20:01:23', 'history.entries.1.description': 'Update of dummy flat file to test history entries.', 'history.entries.1.time': '2020-11-04T20:02:13', 'history.extensions.0.extension_class': 'astropy.io.misc.asdf.extension.AstropyAsdfExtension', 'history.extensions.0.software.name': 'astropy', 'history.extensions.0.software.version': '4.1', 'history.extensions.1.extension_class': 'asdf.extension.BuiltinExtension', 'history.extensions.1.software.name': 'asdf', 'history.extensions.1.software.version': '2.7.1', 'data': array([[0., 0., 0., 0.],
           [0., 0., 0., 0.],
           [0., 0., 0., 0.],
           [0., 0., 0., 0.]], dtype=float32), 'dq': array([[0, 0, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0]], dtype=uint16), 'err': array([[0., 0., 0., 0.],
           [0., 0., 0., 0.],
           [0., 0., 0., 0.],
           [0., 0., 0., 0.]], dtype=float32), 'meta.author': 'Space Telescope Science Institute', 'meta.date': '2020-12-02T22:56:06.721', 'meta.description': 'Flat reference file.', 'meta.filename': 'roman_wfi16_f158_flat_small.asdf', 'meta.instrument.detector': 'WFI16', 'meta.instrument.name': 'WFI', 'meta.instrument.optical_element': 'F158', 'meta.model_type': 'FlatModel', 'meta.pedigree': 'DUMMY', 'meta.reftype': 'FLAT', 'meta.telescope': 'ROMAN', 'meta.useafter': '2020-01-01T00:00:00.000'}

    """
    datamodels = get_datamodels()
    log.info("Checking Roman datamodels.")
    try:
        with datamodels.open(filepath) as d_model:
            d_model.validate()
            flat_dict = d_model.to_flat_dict(include_arrays=False)
    except Exception as exc:
        raise exceptions.ValidationError("Roman Data Models:", str(exc).replace("u'","'")) from exc
    return flat_dict

# =======================================================================

def match_context_key(key):
    """Set the case of a context key appropriately for this project, Roman
    always uses upper case.

    >>> match_context_key('aB.$QqZ4nB')
    'AB.$QQZ4NB'

    """
    return key.upper()

# =======================================================================

@utils.cached
def get_file_properties(filename):
    """Figure out (instrument, filekind, serial) based on `filename` which
    should be a mapping or ASDF reference file.

    >>> get_file_properties('crds/tests/data/roman_wfi16_f158_flat_small.asdf')
    ('wfi', 'flat')

    >>> get_file_properties('crds/tests/data/roman_wfi_flat_0004.rmap')
    ('wfi', 'flat')

    >>> get_file_properties('crds/tests/data/roman_0001.pmap')
    ('', '')

    >>> get_file_properties('crds/tests/data/ascii_tab.csv') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    TypeError: string indices must be integers

    """
    if config.is_mapping(filename):
        try:
            return decompose_newstyle_name(filename)[2:4]
        except Exception:
            # NOTE: load_mapping more conservative than fetch_mapping used in properties_from_mapping
            mapping = rmap.load_mapping(filename)
            return mapping.instrument, mapping.filekind
    elif config.is_reference(filename):
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
    >>> decompose_newstyle_name('./roman.pmap')
    ('.', 'roman', '', '', '', '.pmap')

    >>> decompose_newstyle_name('./roman_0001.pmap')
    ('.', 'roman', '', '', '0001', '.pmap')

    >>> decompose_newstyle_name("./roman_wfi_0001.imap")
    ('.', 'roman', 'wfi', '', '0001', '.imap')

    >>> decompose_newstyle_name("./roman_wfi_flat.rmap")
    ('.', 'roman', 'wfi', 'flat', '', '.rmap')

    >>> decompose_newstyle_name("./roman_wfi_flat.asdf")
    ('.', 'roman', 'wfi', 'flat', '', '.asdf')

    >>> decompose_newstyle_name("./hst_acs.imap")
    Traceback (most recent call last):
    ...
    AssertionError: Invalid instrument 'acs'

    >>> decompose_newstyle_name("./roman_wfi_dark_0001.rmap")
    Traceback (most recent call last):
    ...
    AssertionError: Invalid filekind 'dark'

    >>> decompose_newstyle_name("./roman_wfi_flat_abcd.rmap")
    Traceback (most recent call last):
    ...
    AssertionError: Invalid id field <built-in function id>

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

    # Don't include filename in these or it messes up crds.certify unique error tracking.

    assert instrument in INSTRUMENTS+[""], "Invalid instrument " + repr(instrument)
    assert filekind in FILEKINDS+[""], "Invalid filekind " + repr(filekind)
    assert re.fullmatch(r"\d*", serial), "Invalid id field " + repr(id)
    # extension may vary for upload temporary files.

    return path, observatory, instrument, filekind, serial, ext

def properties_inside_mapping(filename):
    """Load `filename`s mapping header to discover and
    return (instrument, filekind).

    >>> properties_inside_mapping('crds/tests/data/roman_0001.pmap')
    ('', '')

    >>> properties_inside_mapping('crds/tests/data/roman_wfi_flat_0004.rmap')
    ('wfi', 'flat')

    >>> properties_inside_mapping('crds/tests/data/roman_wfi_0001.imap')
    ('wfi', '')

    >>> properties_inside_mapping('crds/tests/data/roman_wfi_flat_0004.rmap')
    ('wfi', 'flat')

    """
    map = rmap.fetch_mapping(filename)
    if map.mapping == "pipeline":
        result = "", ""
    elif map.mapping == "instrument":
        result = map.instrument, ""
    else:
        result = map.instrument, map.filekind
    return result

def _get_fields(filename):
    """
    >>> _get_fields("")
    ('', [''], '')

    >>> _get_fields("a/b.c")
    ('a', ['b'], '.c')

    >>> _get_fields("_")
    ('', ['', ''], '')

    >>> _get_fields("__")
    ('', ['', '', ''], '')

    >>> _get_fields("a_b_c")
    ('', ['a', 'b', 'c'], '')

    >>> _get_fields("_a_b_c_")
    ('', ['', 'a', 'b', 'c', ''], '')

    """
    path = os.path.dirname(filename)
    name = os.path.basename(filename)
    name, ext = os.path.splitext(name)
    parts = name.split("_")
    return path, parts, ext

def list_get(l, index, default):
    """
    >>> list_get([], 0, None)

    >>> list_get([], -1, 7)
    7

    >>> list_get(None, 0, None)
    Traceback (most recent call last):
    ...
    TypeError: 'NoneType' object is not subscriptable

    >>> list_get([1], 1, 9)
    9

    >>> list_get([1, 2, 3, 4], 2, 8)
    3

    """
    try:
        return l[index]
    except IndexError:
        return default

def get_reference_properties(filename):
    """Figure out ASDF (instrument, filekind, serial) based on `filename`.

    >>> get_reference_properties('crds/tests/data/roman_0001.pmap')
    ('crds/tests/data', 'roman', '', '', '0001', '.pmap')

    >>> get_reference_properties("./roman_wfi_flat.asdf")
    ('.', 'roman', 'wfi', 'flat', '', '.asdf')

    >>> get_reference_properties('crds/tests/data/s7g1700gl_dead_bad_xsum.fits')
    Traceback (most recent call last):
    ...
    crds.core.exceptions.CrdsNamingError: Can't identify instrument of 's7g1700gl_dead_bad_xsum.fits' : Invalid instrument 'cos'

    """
    try:   # Hopefully it's a nice new standard filename, easy
        return decompose_newstyle_name(filename)
    except AssertionError:  # cryptic legacy paths & names, i.e. reality
        pass
    # If not, dig inside the FITS file, slow
    return ref_properties_from_header(filename)

# =======================================================================

def ref_properties_from_header(filename):
    """Look inside ASDF `filename` header to determine instrument, filekind.

    >>> ref_properties_from_header('crds/tests/data/roman_wfi16_f158_flat_small.asdf')
    ('crds/tests/data', 'roman', 'wfi', 'flat', 'roman_wfi16_f158_flat_small', '.asdf')

    >>> ref_properties_from_header('crds/tests/data/s7g1700gl_dead_bad_xsum.fits')
    Traceback (most recent call last):
    ...
    crds.core.exceptions.CrdsNamingError: Can't identify instrument of 's7g1700gl_dead_bad_xsum.fits' : Invalid instrument 'cos'

    >>> ref_properties_from_header('crds/tests/data/roman_wfi16_f158_badtype_small.asf')
    Traceback (most recent call last):
    ...
    crds.core.exceptions.CrdsNamingError: Can't identify META.REFTYPE of 'roman_wfi16_f158_badtype_small.asf'

    """
    # For legacy files,  just use the root filename as the unique id
    path, parts, ext = _get_fields(filename)
    serial = os.path.basename(os.path.splitext(filename)[0])
    header = data_file.get_free_header(filename, (), None, "roman")
    header["META.TELESCOPE"] = "roman"
    name = os.path.basename(filename)
    try:
        instrument = utils.header_to_instrument(header).lower()
        assert instrument in INSTRUMENTS, "Invalid instrument " + repr(instrument)
    except Exception as exc:
        raise exceptions.CrdsNamingError(
            "Can't identify instrument of", repr(name), ":", str(exc)) from exc
    try:
        filekind = header.get('META.REFTYPE', 'UNDEFINED').lower()
        assert filekind in FILEKINDS, "Invalid file type " + repr(filekind)
    except Exception as exc:
        raise exceptions.CrdsNamingError("Can't identify META.REFTYPE of", repr(name))
    return path, "roman", instrument, filekind, serial, ext

# =============================================================================

def reference_keys_to_dataset_keys(rmapping, header):
    """Given a header dictionary for a reference file, map the header back to keys
    relevant to datasets.  So for ACS biasfile the reference says BINAXIS1 but
    the dataset says NUMCOLS.  This would convert { "BINAXIS1": 1024 } to {
    "NUMCOLS" : 1024 }.

    In general,  rmap parkeys are matched against datset values and are defined
    as dataset header keywords.   For refactoring though,  what's initially
    available are reference file keywords...  which need to be mapped into the
    terms rmaps know:  dataset keywords.

    Another aspect of this translation is handling reference file "pattern"
    keywords which typically define or-barred sets of values rather than
    discrete values, any of which the reference is defined to support:
    e.g. 'DETECTOR1|DETECTOR2' vs. 'DETECTOR1'.  In this case, the reference
    file will define a pattern keyword used to define the match pattern in the
    rmap, while a dataset will define a discrete valued keyword which is
    matched on.  e.g. reference file keyword "META.EXPOSURE.P_EXPTYPE" is
    translated back to dataset keyword "META.EXPOSURE.TYPE".  Reference files
    can specify parameters in either form and the P_ pattern variant is given
    preference if both values are defined.  For CRDS purposes, only the P_
    version is checked and used since it will be used to replace the discrete
    valued keyword in the header which is certified and used to define the rmap
    updates.

    >>> reference_keys_to_dataset_keys( \
    namedtuple('x', ['reference_to_dataset', 'filename'])({}, 'crds/tests/data/roman_wfi16_f158_badtype_small.asf'), \
    {'META.INSTRUMENT.P_HOOLIGAN':'abc'})
    hooligan

    """
    header = dict(header)

    # Basic common pattern translations
    translations = {
            "META.EXPOSURE.P_EXPTYPE" : "META.EXPOSURE.TYPE",

            "META.INSTRUMENT.P_BAND" : "META.INSTRUMENT.BAND",

            "META.INSTRUMENT.P_DETECTOR"  : "META.INSTRUMENT.DETECTOR",

            "META.INSTRUMENT.P_CHANNEL" : "META.INSTRUMENT.CHANNEL",

            "META.INSTRUMENT.P_FILTER" : "META.INSTRUMENT.FILTER",

            "META.INSTRUMENT.P_MODULE"  : "META.INSTRUMENT.MODULE",

            "META.SUBARRAY.P_SUBARRAY" : "META.SUBARRAY.NAME",

            "META.INSTRUMENT.P_GRATING" : "META.INSTRUMENT.GRATING",

            "META.EXPOSURE.PREADPATT" : "META.EXPOSURE.READPATT",
            "META.EXPOSURE.P_READPATT" : "META.EXPOSURE.READPATT",

            # vvvv Speculative,  not currently defined or required by CAL vvvvv
            "META.INSTRUMENT.PCORONAGRAPH" : "META.INSTRUMENT.CORONAGRAPH",
        }

    # Rmap header reference_to_dataset field tranlations,  can override basic!
    try:
        translations.update(rmapping.reference_to_dataset)
    except AttributeError:
        pass

    log.verbose("reference_to_dataset translations:\n", log.PP(translations), verbosity=60)
    log.verbose("reference_to_dataset input header:\n", log.PP(header), verbosity=80)

    for key in header:
        # Match META.X.P_SOMETHING or P_SOMETH
        if (key.split(".")[-1].startswith("P_")) and key not in translations:
            log.warning("CRDS-pattern-like keyword", repr(key),
                        "w/o CRDS translation to corresponding dataset keyword.")
            log.info("Pattern-like keyword", repr(key),
                     "may be misspelled or missing its translation in CRDS.  Pattern will not be used.")
            log.info("The translation for", repr(key),
                     "can be defined in crds.roman.locate or rmap header reference_to_dataset field.")
            log.info("If this is not a pattern keyword, adding a translation to 'not-a-pattern'",
                     "will suppress this warning.")

    # Add replacements for translations *if* the existing untranslated value
    # is poor and the translated value is better defined.   This is to do
    # translations w/o replacing valid/concrete DM values with something
    # like guessed values of "UNDEFINED" or "N/A".
    for rkey in sorted(translations):
        if rkey in header:
            dkey = translations[rkey]
            dval = header.get(translations[rkey], None)
            rval = header[rkey]
            if rval not in [None, "UNDEFINED"] and rval != dval:
                log.info("Setting", repr(dkey), "=", repr(dval),
                         "to value of", repr(rkey), "=", repr(rval))
                header[dkey] = rval

    if "META.SUBARRAY.NAME" not in header:
        header["META.SUBARRAY.NAME"] = "UNDEFINED"

    if "META.EXPOSURE.TYPE" not in header:
        header["META.EXPOSURE.TYPE"] = "UNDEFINED"

    # If USEAFTER is defined,  or we're configured to fake it...
    #   don't invent one if its missing and we're not faking it.
    if "META.USEAFTER" in header or config.ALLOW_BAD_USEAFTER:

        # Identify this as best as possible,
        filename = header.get("META.FILENAME", None) or rmapping.filename

        reformatted = timestamp.reformat_useafter(filename, header).split()
        header["META.OBSERVATION.DATE"] = reformatted[0]
        header["META.OBSERVATION.TIME"] = reformatted[1]

    log.verbose("reference_to_dataset output header:\n", log.PP(header), verbosity=80)

    return header

# =============================================================================

def condition_matching_header(rmapping, header):
    """Normalize header values for .rmap reference insertion."""
    return dict(header)   # NOOP for Roman,  may have to revisit

# ============================================================================

def fits_to_parkeys(fits_header):
    return dict(fits_header)

# ============================================================================

def get_env_prefix(instrument):
    """Return the environment variable prefix (IRAF prefix) for `instrument`."""
    return "crds://"

def filekind_to_keyword(filekind):
    """Return the "keyword" at which a assigned reference should be recorded."""
    raise NotImplementedError("filekind_to_keyword not implemented for Roman")

def locate_file(refname, mode=None):
    """Given a valid reffilename in CDBS or CRDS format,  return a cache path for the file.
    The aspect of this which is complicated is determining instrument and an instrument
    specific sub-directory for it based on the filename alone,  not the file contents.
    """
    if mode is  None:
        mode = config.get_crds_ref_subdir_mode(observatory="roman")
    if mode == "instrument":
        instrument = utils.file_to_instrument(refname)
        rootdir = locate_dir(instrument, mode)
    elif mode == "flat":
        rootdir = config.get_crds_refpath("roman")
    else:
        raise ValueError("Unhandled reference file location mode " + repr(mode))
    return  os.path.join(rootdir, os.path.basename(refname))

def locate_dir(instrument, mode=None):
    """Locate the instrument specific directory for a reference file."""
    if mode is  None:
        mode = config.get_crds_ref_subdir_mode(observatory="roman")
    else:
        config.check_crds_ref_subdir_mode(mode)
    crds_refpath = config.get_crds_refpath("roman")
    if mode == "instrument":   # use simple names inside CRDS cache.
        rootdir = os.path.join(crds_refpath, instrument.lower())
        if not os.path.exists(rootdir):
            if config.writable_cache_or_verbose("Skipping making instrument directory link for", repr(instrument)):
                utils.ensure_dir_exists(rootdir + "/locate_dir.fits")
    elif mode == "flat":    # use original flat cache structure,  all instruments in same directory.
        rootdir = crds_refpath
    else:
        raise ValueError("Unhandled reference file location mode " + repr(mode))
    return rootdir


def get_cross_strapped_pairs(header):
    """Roman does not use FITS files so there is no cross-strapping between datamodels
    notation and FITS keywords.   Returns []
    """
    return []

# ============================================================================

def hijack_warnings(func, *args, **keys):
    """Re-map dependency warnings to CRDS warnings so they're counted and logged
    to web output.   astropy and datamodels are remapped.
    """
    with warnings.catch_warnings():
        # save and replace warnings.showwarning
        old_showwarning, warnings.showwarning = \
            warnings.showwarning, abstract.hijacked_showwarning

        # Always handle astropy warnings
        from astropy.utils.exceptions import AstropyUserWarning
        warnings.simplefilter("always", AstropyUserWarning)

        from stdatamodels.validate import ValidationWarning
        warnings.filterwarnings("always", r".*", ValidationWarning, f".*roman.*")
        if not config.ALLOW_SCHEMA_VIOLATIONS:
            warnings.filterwarnings("error", r".*is not one of.*", ValidationWarning, f".*roman.*")

        try:
            result = func(*args, **keys)
        finally:
            warnings.showwarning = old_showwarning

    return result

# ============================================================================

def test():
    """Run the module doctests."""
    import doctest
    from . import locate
    return doctest.testmod(locate)
