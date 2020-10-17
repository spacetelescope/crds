"""This module provides functions which determine various observatory
specific policies/plugins for Roman:

1. How to convert reference file basenames to fully specified paths.

2. How to manage parameters for reference file Validator objects used
in the certification of reference files.

XXXX Roman NOTE: This code was derived from the JWST locate.py module and
contains substantial dupliucation.  However, because the functions often depend
on project-specific modules, globals, or functions the code is not usable
without some refactoring.  Other plugins may vary simply because
ASDF+datamodels Roman is already different than the FITS+datamodels world of
JWST, e.g. there is no longer a need for FITS <-> datamodels translations and
log annotation, i.e.  AKA keyword cross-strapping.

"""
import os.path
import re

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
    """Based on `header` return the default list of appropriate reference type names."""
    return []  # translates to "all types" for instrument defined by header.

def header_to_pipelines(header, context="roman-operational"):
    """Based on `header` return the default list of appropriate reference type names."""
    raise NotImplementedError("Roman has not defined header_to_pipelines().")

# =======================================================================

MODEL = None

def get_datamodels():
    """Defer datamodels loads until we definitely have a roman usecase.
    Enables light observatory package imports which don't require all
    dependencies when supporting other observatories.
    """
    try:
        from jwst import datamodels  # this is fatal.
        # XXXX TODO roman # from roman import datamodels  # this is fatal.
    except ImportError:
        log.error(
            "CRDS requires installation of the 'roman' package to operate on Roman files.")
        raise
    global MODEL
    if MODEL is None:
        with log.error_on_exception(
                "Failed constructing basic Roman DataModel"):
            MODEL = datamodels.DataModel()
    return datamodels

# =============================================================================

def tpn_path(tpn_file):
    """Return the full filepath of `tpn_file`."""
    return os.path.join(HERE, "tpns", tpn_file)

def get_extra_tpninfos(refpath):
    """Returns TpnInfos (valid value enumerations) derived from the cal code data models schema.

    This can be useful to leverage datamodels (core?) schema for rmap checking.

    Datamodels schema historically lack per-instrument granularity so the canonical .tpn scheme
    can catch errors not caught by the schema,  e.g. MIRI values used in a NIRCAM reference
    file because a reference file was cloned and not properly updated.

    These tend to have a superset of acceptable values for any particular instrument,
    particularly since CRDS has historically only loaded the core schema.
    """
    return []   # use this to ignore datamodels schema for CRDS value checking
    # XXXX roman  -- datamodels schema scraping can potentially be enabled once
    # romancal and datamodels are integrated.   This will effectively translate the
    # datamodels schema (core unless work is done) automatically as-if they were
    # being specified in CRDS .tpn files.
    # return schema.get_schema_tpninfos(refpath)

def project_check(refpath):
    return get_data_model_flat_dict(refpath)

def get_data_model_flat_dict(filepath):
    """Get the header from `filepath` using the roman data model.  Data model
    dotted object paths are reduced to capitalized dot-separated FITS-like
    keyword strings and a simple key,value dictionary format vs. nested objects.

    e.g.  meta.instrument.name  -->  "META.INSTRUMENT.NAME'

    Returns   { file_keyword : keyword_value, ... }
    """
    datamodels = get_datamodels()
    log.info("Checking Roman datamodels.")
    try:
        with datamodels.open(filepath) as d_model:
            flat_dict = d_model.to_flat_dict(include_arrays=False)
    except Exception as exc:
        raise exceptions.ValidationError("Roman Data Models:", str(exc).replace("u'","'")) from exc
    return flat_dict

# =======================================================================

def match_context_key(key):
    """Set the case of a context key appropriately for this project, Roman
    always uses upper case.
    """
    return key.upper()

# =======================================================================

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
    assert re.match(r"\d*", serial), "Invalid id field " + repr(id)
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

def ref_properties_from_header(filename):
    """Look inside FITS `filename` header to determine instrument, filekind.
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
    """
    header = dict(header)

    # Basic common pattern translations
    translations = {
            "META.EXPOSURE.P_EXPTYPE" : "META.EXPOSURE.TYPE",

            "META.INSTRUMENT.P_BAND" : "META.INSTRUMENT.BAND",

            "META.INSTRUMENT.P_DETECTOR"  : "META.INSTRUMENT.DETECTOR",

            "META.INSTRUMENT.P_CHANNEL" : "META.INSTRUMENT.CHANNEL",

            "META.INSTRUMENT.P_FILTER" : "META.INSTRUMENT.FILTER",

            "META.INSTRUMENT.P_PUPIL"  : "META.INSTRUMENT.PUPIL",

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

    #  XXXX  roman  no more FITS
    # header = abstract.cross_strap_header(header)

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

# META.REF_FILE.SPECWCS.NAME.FITS_KEYWORD


# XXXX Roman TODO   this is a guess;  define the dotted object path needed to
# set the datamodels field for these.  Then transform it to a "flat form" string.
def filekind_to_keyword(filekind):
    """Return the "keyword" at which a assigned reference should be recorded.

    See also the JWST version of this plugin which translated to R_ FITS keywords.

    >>> filekind_to_keyword("flat")
    'META.REF_FILE.FLAT.NAME'
    """
    return f"META.REF_FILE.{filekind.upper()}.NAME"

@utils.cached
def warn_filekind_once(filekind):
    log.warning("No apparent Roman cal code data models schema support for", log.srepr(filekind))

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

def get_hijack_warning_pars():
    """Parameters used by roman to re-map warnings from package dependencies to
    CRDS so that they are counted and visible in web output.
    """
    from romancal.datamodels.validation import ValidationWarning
    return "roman", ValidationWarning

# ============================================================================

def test():
    """Run the module doctests."""
    import doctest
    from . import locate
    return doctest.testmod(locate)
