"""This module provides functions which determine various observatory
specific policies for JWST:

1. How to convert reference file basenames to fully specified paths.

2. How to manage parameters for reference file Validator objects used
in the certification of reference files.
"""
import os.path
import re
import warnings

from asdf.tags.core import NDArrayType

# =======================================================================

from crds.core import rmap, config, utils, timestamp, log, exceptions
from crds.certify import generic_tpn
from crds import data_file
from crds.io import abstract

# =======================================================================

# These two functions decouple the generic reference file certifier program
# from observatory-unique ways of specifying and caching Validator parameters.

from crds.jwst import TYPES, INSTRUMENTS, FILEKINDS, EXTENSIONS, INSTRUMENT_FIXERS, TYPE_FIXERS

from . import schema

# definitively lists possible exp_types by instrument, or all instruments
from .schema import get_exptypes

get_row_keys_by_instrument = TYPES.get_row_keys_by_instrument
get_item = TYPES.get_item
suffix_to_filekind = TYPES.suffix_to_filekind
filekind_to_suffix = TYPES.filekind_to_suffix
get_all_tpninfos = TYPES.get_all_tpninfos

from crds.jwst.pipeline import header_to_reftypes, header_to_pipelines

# =======================================================================

MODEL = None

def get_datamodels():
    try:
        from jwst import datamodels  # this is fatal.
    except ImportError:
        log.error(
            "CRDS requires installation of the 'jwst' package to operate on JWST files.")
        raise
    global MODEL
    if MODEL is None:
        with log.error_on_exception(
                "Failed constructing basic JWST DataModel"):
            MODEL = datamodels.DataModel()
    return datamodels

# =============================================================================

HERE = os.path.dirname(__file__) or "."

def tpn_path(tpn_file):
    """Return the full filepath of `tpn_file`."""
    return os.path.join(HERE, "tpns", tpn_file)

def get_extra_tpninfos(refpath):
    """Returns TpnInfos (valid value enumerations) derived from the cal code data models schema."""
    return []
    # XXX Disabled during transition period to more specialized reference file schema
    # that will require enhanced schema scraping.
    # return schema.get_schema_tpninfos(refpath)

def project_check(refpath, rmap):
    if not rmap.filekind.startswith("pars-"):
        get_data_model_flat_dict(refpath)

def get_data_model_flat_dict(filepath):
    """Get the header from `filepath` using the jwst data model."""
    datamodels = get_datamodels()
    log.info("Checking JWST datamodels.")
    # with log.error_on_exception("JWST Data Model (jwst.datamodels)"):
    try:
        with datamodels.open(filepath) as d_model:
            flat_dict = d_model.to_flat_dict(include_arrays=False)
            # stdatamodels 0.1.0 has a bug that causes arrays to still
            # be returned:
            flat_dict = {
                k: v for k, v in flat_dict.items()
                if not isinstance(v, NDArrayType)
            }
    except Exception as exc:
        raise exceptions.ValidationError("JWST Data Models:", str(exc).replace("u'","'")) from exc
    return flat_dict

# =======================================================================

def match_context_key(key):
    """Set the case of a context key appropriately for this project, JWST
    always uses upper case.
    """
    return key.upper()

# =======================================================================

REF_EXT_RE = re.compile(r"\.fits|\.r\dh$")

@utils.cached
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

    # Don't include filename in these or it messes up crds.certify unique error tracking.

    assert instrument in INSTRUMENTS+[""], "Invalid instrument " + repr(instrument)
    assert filekind in FILEKINDS+[""], "Invalid filekind " + repr(filekind)

    # The original regular expresssion "\d*\" matches anything in the below assert statement, so it's basically a no-op.
    # The correct way to do it is with fullmatch. However, that generates a bunch of test failures that need
    # to be reconciled before making the change:
    #     ERROR: test_throughput_lookup_generation (crds.tests.test_synphot_lookup_generator.TestSynphotLookupGenerator)
    #     FAIL: Doctest: crds.tests.test_bad_files.dt_bad_references_fast_mode
    #     FAIL: Doctest: crds.tests.test_bad_files.dt_bad_rules_jwst_getreferences_warning
    #     FAIL: Doctest: crds.tests.test_certify.certify_recursive
    #     FAIL: Doctest: crds.tests.test_certify.certify_table_comparison_context
    #     FAIL: Doctest: crds.tests.test_heavy_client.dt_getreferences_ignore_cache
    #     FAIL: Doctest: crds.tests.test_list.dt_list_cached_references
    #     FAIL: Doctest: crds.tests.test_synphot_hst.dt_synphot_core_integration_test
    #
    # XXXX TODO: Change to us fullmatch and resolve all the ensuing test failures.
    assert re.match(r"\d*", serial), "Invalid id field " + repr(id)
    #assert re.fullmatch(r"\d*", serial), "Invalid id field " + repr(id)
    # extension may vary for upload temporary files.

    return path, observatory, instrument, filekind, serial, ext

def properties_inside_mapping(filename):
    """Load `filename`s mapping header to discover and
    return (instrument, filekind).
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

def get_reference_properties(filename):
    """Figure out FITS (instrument, filekind, serial) based on `filename`.
    """
    try:   # Hopefully it's a nice new standard filename, easy
        return decompose_newstyle_name(filename)
    except AssertionError:  # cryptic legacy paths & names, i.e. reality
        pass
    # If not, dig inside the FITS file, slow
    return ref_properties_from_header(filename)

# =======================================================================

FILEKIND_KEYWORDS = ["REFTYPE", "TYPE", "META.REFTYPE",]

def ref_properties_from_header(filename):
    """Look inside FITS `filename` header to determine instrument, filekind.
    """
    # For legacy files,  just use the root filename as the unique id
    path, parts, ext = _get_fields(filename)
    serial = os.path.basename(os.path.splitext(filename)[0])
    header = data_file.get_free_header(filename, (), None, "jwst")
    header["TELESCOP"] = header["TELESCOPE"] = header["META.TELESCOPE"] = "jwst"
    name = os.path.basename(filename)
    try:
        instrument = utils.header_to_instrument(header).lower()
        assert instrument in INSTRUMENTS, "Invalid instrument " + repr(instrument)
    except Exception as exc:
        raise exceptions.CrdsNamingError(
            "Can't identify instrument of", repr(name), ":", str(exc)) from exc
    try:
        filekind = utils.get_any_of(header, FILEKIND_KEYWORDS, "UNDEFINED").lower()
        assert filekind in FILEKINDS, "Invalid file type " + repr(filekind)
    except Exception as exc:
        raise exceptions.CrdsNamingError("Can't identify REFTYPE of", repr(name))
    return path, "jwst", instrument, filekind, serial, ext

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
    """
    header = dict(header)

    # Basic common pattern translations
    translations = {
            "META.EXPOSURE.P_EXPTYPE" : "META.EXPOSURE.TYPE",
            "P_EXP_TY" : "META.EXPOSURE.TYPE",

            "META.INSTRUMENT.P_BAND" : "META.INSTRUMENT.BAND",
            "P_BAND" : "META.INSTRUMENT.BAND",

            "META.INSTRUMENT.P_DETECTOR"  : "META.INSTRUMENT.DETECTOR",
            "P_DETECT"  : "META.INSTRUMENT.DETECTOR",

            "META.INSTRUMENT.P_CHANNEL" : "META.INSTRUMENT.CHANNEL",
            "P_CHANNE" : "META.INSTRUMENT.CHANNEL",

            "META.INSTRUMENT.P_FILTER" : "META.INSTRUMENT.FILTER",
            "P_FILTER"  : "META.INSTRUMENT.FILTER",

            "META.INSTRUMENT.P_PUPIL"  : "META.INSTRUMENT.PUPIL",
            "P_PUPIL" : "META.INSTRUMENT.PUPIL",

            "META.INSTRUMENT.P_MODULE"  : "META.INSTRUMENT.MODULE",
            "P_MODULE" : "META.INSTRUMENT.MODULE",

            "META.SUBARRAY.P_SUBARRAY" : "META.SUBARRAY.NAME",
            "P_SUBARR" : "META.SUBARRAY.NAME",

            "META.INSTRUMENT.P_GRATING" : "META.INSTRUMENT.GRATING",
            "P_GRATIN" : "META.INSTRUMENT.GRATING",

            "META.EXPOSURE.PREADPATT" : "META.EXPOSURE.READPATT",
            "META.EXPOSURE.P_READPATT" : "META.EXPOSURE.READPATT",
            "P_READPA" : "META.EXPOSURE.READPATT",

            # vvvv Speculative,  not currently defined or required by CAL vvvvv
            "META.INSTRUMENT.PCORONAGRAPH" : "META.INSTRUMENT.CORONAGRAPH",
            "P_CORONM" : "META.INSTRUMENT.CORONAGRAPH",
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
                     "can be defined in crds.jwst.locate or rmap header reference_to_dataset field.")
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

    header = abstract.cross_strap_header(header)

    # NOTE:  the hacks below happen after cross-strapping and pattern handling
    # so if the keywords are still undefined they're undefined.  They have to
    # be explicitly defined as UNDEFINED somehow since they're nearly universally
    # used in constraints as condition variables even if they're not used in rmaps.
    # Unlike the targets of constraints,  CRDS is nominally unaware of condition
    # variables so they need to be incidentally defined.  This currently doesn't
    # work out if the rmap doesn't use them.  Condition variables are eval'ed in
    # expressions.

    if "SUBARRAY" not in header:
        header["SUBARRAY"] = header["META.SUBARRAY.NAME"] = "UNDEFINED"

    if "EXP_TYPE" not in header:
        header["EXP_TYPE"] = header["META.EXPOSURE.TYPE"] = "UNDEFINED"

    if "USEAFTER" not in header and "META.USEAFTER" in header:
        header["USEAFTER"] = header["META.USEAFTER"]
    if "USEAFTER" not in header and "META.USEAFTER" in header:
        header["USEAFTER"] = header["META.USEAFTER"]

    # If USEAFTER is defined,  or we're configured to fake it...
    #   don't invent one if its missing and we're not faking it.
    if "USEAFTER" in header or config.ALLOW_BAD_USEAFTER:

        # Identify this as best as possible,
        filename = header.get("FILENAME", None) or rmapping.filename

        reformatted = timestamp.reformat_useafter(filename, header).split()
        header["DATE-OBS"] = header["META.OBSERVATION.DATE"] = reformatted[0]
        header["TIME-OBS"] = header["META.OBSERVATION.TIME"] = reformatted[1]

    log.verbose("reference_to_dataset output header:\n", log.PP(header), verbosity=80)

    return header

# =============================================================================

def condition_matching_header(rmapping, header):
    """Normalize header values for .rmap reference insertion."""
    return dict(header)   # NOOP for JWST,  may have to revisit

# ============================================================================

def fits_to_parkeys(fits_header):
    """Map a FITS header onto rmap parkeys appropriate for JWST."""
    parkeys = {}
    for key, value in fits_header.items():
        key, value = str(key), str(value)
        if not key.lower().startswith("meta."):
            pk = cached_dm_find_fits_keyword(key)
            if not pk:
                pk = key
            else:
                assert len(pk) == 1, "CRDS JWST Data Model ambiguity on " + \
                    repr(key) + " = " + repr(pk)
                pk = pk[0]
        else:
            pk = key
        pk = pk.upper()
        parkeys[pk] = value
    return parkeys

@utils.cached
def cached_dm_find_fits_keyword(key):
    """Return the SSB JWST data model path for the specified non-path keyword,  nominally
    a FITS or json or ASDF bare keyword.
    """
    get_datamodels()
    return MODEL.find_fits_keyword(key.upper(), return_result=True)
# ============================================================================

def get_env_prefix(instrument):
    """Return the environment variable prefix (IRAF prefix) for `instrument`."""
    return "crds://"

# META.REF_FILE.SPECWCS.NAME.FITS_KEYWORD

def filekind_to_keyword(filekind):
    """Return the FITS keyword at which a reference should be recorded.

    >>> filekind_to_keyword("flat")
    'R_FLAT'
    >>> filekind_to_keyword("superbias")
    'R_SUPERB'
    """
    from . import schema
    flat_schema = schema.get_flat_schema()
    filekind = filekind.upper()
    meta_path = "META.REF_FILE.{}.NAME.FITS_KEYWORD".format(filekind)
    try:
        return flat_schema[meta_path]
    except KeyError:
        warn_filekind_once(filekind)
        return filekind

@utils.cached
def warn_filekind_once(filekind):
    log.warning("No apparent JWST cal code data models schema support for", log.srepr(filekind))

def locate_file(refname, mode=None):
    """Given a valid reffilename in CDBS or CRDS format,  return a cache path for the file.
    The aspect of this which is complicated is determining instrument and an instrument
    specific sub-directory for it based on the filename alone,  not the file contents.
    """
    if mode is  None:
        mode = config.get_crds_ref_subdir_mode(observatory="jwst")
    if mode == "instrument":
        instrument = utils.file_to_instrument(refname)
        rootdir = locate_dir(instrument, mode)
    elif mode == "flat":
        rootdir = config.get_crds_refpath("jwst")
    else:
        raise ValueError("Unhandled reference file location mode " + repr(mode))
    return  os.path.join(rootdir, os.path.basename(refname))

def locate_dir(instrument, mode=None):
    """Locate the instrument specific directory for a reference file."""
    if mode is  None:
        mode = config.get_crds_ref_subdir_mode(observatory="jwst")
    else:
        config.check_crds_ref_subdir_mode(mode)
    crds_refpath = config.get_crds_refpath("jwst")
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

# =======================================================================

# When loading headers,  make sure each keyword in a tuple is represented with
# the same value enabling any form to be used.  Case insensitive.

# XXXX the first translation should be the FITS keyword assuming there is one!!

CROSS_STRAPPED_KEYWORDS = {

    # META.REF_FILE.X is now obsolete but retained for backward compatibility.
    # it was replaced by META.X

    # These include non-DM keywords
    "META.INSTRUMENT.NAME" : ["INSTRUME", "INSTRUMENT", "META.INSTRUMENT.TYPE",],
    "META.TELESCOPE" : ["TELESCOP","TELESCOPE","META.TELESCOPE"],
    "META.DESCRIPTION" : ["DESCRIP","DESCRIPTION"],
    "META.REFTYPE" : ["REFTYPE",],

    # These include non-core-DM DM fields
    "META.AUTHOR" : ["AUTHOR",],
    "META.PEDIGREE" : ["PEDIGREE"],
    "META.USEAFTER" : ["USEAFTER"],
    "META.HISTORY" : ["HISTORY"],
    "META.CALIBRATION_SOFTWARE_VERSION" : ["CAL_VER", "CALIBRATION_SOFTWARE_VERSION"],
    "META.OBSERVATION.DATE" : ["DATE-OBS"],
    "META.OBSERVATION.TIME" : ["TIME-OBS"],


    # These should all be stock DM:FITS,  automatic
    # "META.INSTRUMENT.BAND" : ["BAND"],
    # "META.INSTRUMENT.CHANNEL" : ["CHANNEL"],
    # "META.INSTRUMENT.DETECTOR" : ["DETECTOR"],
    # "META.INSTRUMENT.FILTER" : ["FILTER"],
    # "META.INSTRUMENT.PUPIL" : ["PUPIL"],
    # "META.INSTRUMENT.GRATING" : ["GRATING"],

    # "META.SUBARRAY.NAME" : ["SUBARRAY"],
    # "META.SUBARRAY.XSTART" : ["SUBSTRT1"],
    # "META.SUBARRAY.YSTART" : ["SUBSTRT2"],
    # "META.SUBARRAY.XSIZE" : ["SUBSIZE1"],
    # "META.SUBARRAY.YSIZE" : ["SUBSIZE2"],
    # "META.SUBARRAY.FASTAXIS" : ["FASTAXIS"],
    # "META.SUBARRAY.SLOWAXIS" : ["SLOWAXIS"],

    # "META.EXPOSURE.TYPE" : ["EXP_TYPE"],
    # "META.EXPOSURE.READPATT" : ["READPATT"],

    # "META.APERTURE.NAME" : ["APERTURE", "APERNAME"],
}

# ============================================================================

@utils.cached
def get_static_pairs():
    return abstract.equivalence_dict_to_pairs(CROSS_STRAPPED_KEYWORDS)

def get_cross_strapped_pairs(header):
    """Return the list of keyword pairs where each pair describes synonyms for the same
    piece of data.
    """
    return  get_static_pairs() + _get_fits_datamodel_pairs(header)

def _get_fits_datamodel_pairs(header):
    """Return the (FITS, DM) and (DM, FITS) cross strap pairs associated with
    every keyword in `header` as defined by the datamodels interface functions
    defined by the CRDS JWST schema module.
    """
    pairs = []
    from . import schema
    for key in header:
        with log.verbose_warning_on_exception("Failed cross strapping keyword", repr(key)):
            fitskey = schema.dm_to_fits(key) or key
            dmkey = schema.fits_to_dm(key) or key
            pairs.append((fitskey, dmkey))
            pairs.append((dmkey, fitskey))
    log.verbose("Cal code datamodels keyword equivalencies:\n", log.PP(pairs), verbosity=90)
    return pairs


# ============================================================================

# Standard model names
DATA_MODEL_RE_STR = r"(META(\.[A-Z][A-Z0-9_]*)+)"
DATA_MODEL_RE = re.compile(DATA_MODEL_RE_STR)

def add_fits_keywords(log_message):
    """Process log `message` and annotate data model keywords/paths with
    their FITS translations if possible like:

    <data_models_keyword> '[' <fits_keyword> ']'
    """
    try:
        return _add_fits_keywords(log_message)
    except Exception:  # if annotation fails,  just return the original message
        return log_message

def _add_fits_keywords(log_message):
    """Process log `message` and annotate data model keywords/paths with
    their FITS translations if possible like:

    <data_models_keyword> '[' <fits_keyword> ']'
    """
    matches = DATA_MODEL_RE.finditer(log_message)
    if not matches:
        return log_message
    for dm_match in matches:
        model_key = dm_match.group(0)
        fits_key = schema.dm_to_fits(model_key)
        if fits_key is None:
            fits_key = _hack_fits_translation(model_key)
        annotation = " [" + fits_key + "]"
        if annotation not in log_message:
            log_message = log_message.replace(
                model_key, model_key + annotation)
    return log_message

# P_ keyword model names
DATA_MODEL_P_RE_STR = r"META(\.[A-Z][A-Z0-9_]*)*\.(P_[A-Z0-9_]+)"
DATA_MODEL_P_RE = re.compile(DATA_MODEL_P_RE_STR)

def _hack_fits_translation(model_key):
    """Hack FITS translations for data models keyword/paths not covered
    by dm_to_fits(), currently anything outside the core schema.
    """
    if model_key in CROSS_STRAPPED_KEYWORDS:
        fits_key = CROSS_STRAPPED_KEYWORDS[model_key][0]
    elif DATA_MODEL_P_RE.match(model_key):
        match = DATA_MODEL_P_RE.match(model_key)
        fits_key = match.group(2)[:8]
    else:
        fits_key = "FITS unknown"
    return fits_key

log.append_crds_filter(add_fits_keywords)

def disable_fits_annotations():
    log.remove_crds_filter(add_fits_keywords)

# ============================================================================

def test():
    """Run the module doctests."""
    import doctest
    from . import locate
    return doctest.testmod(locate)
