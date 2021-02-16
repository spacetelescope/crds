'''
This module defines the generic functions and abstract class used to manage
file access in CRDS.
'''
import functools
import warnings
import re

# ================================================================================================

import datetime
from astropy.time import Time

# ================================================================================================

# from astropy.utils.exceptions import AstropyUserWarning    # deferred

# ================================================================================================

from crds.core import exceptions, config, log, utils, timestamp

# ================================================================================================

DUPLICATES_OK = ["COMMENT", "HISTORY", "NAXIS","EXTNAME","EXTVER"]
APPEND_KEYS = ["COMMENT", "HISTORY"]

# ===========================================================================

# The point of hijack_warnings is to remap warnings from other packages to CRDS
# so that they are counted and logged and visible in web output.
# NOTE:  hijack_warnings needs to be nestable
# XXX: hijack_warnings is non-reentrant and FAILS with THREADS

def hijack_warnings(func):
    """Decorator that redirects warning messages to CRDS warnings."""
    @functools.wraps(func)
    def wrapper(*args, **keys):
        """Reassign warnings to CRDS warnings prior to executing `func`,  restore
        warnings state afterwards and return result of `func`.
        """
        # warnings.resetwarnings()
        from astropy.utils.exceptions import AstropyUserWarning
        with warnings.catch_warnings():
            old_showwarning = warnings.showwarning
            warnings.showwarning = hijacked_showwarning
            warnings.simplefilter("always", AstropyUserWarning)
            try:
                from stdatamodels.validate import ValidationWarning
            except:
                log.verbose_warning(
                    "stdatamodels ValidationWarning import failed.  "
                    "Not a problem for HST.",
                    verbosity=70)
            else:
                warnings.filterwarnings("always", r".*", ValidationWarning, r".*jwst.*")
                if not config.ALLOW_SCHEMA_VIOLATIONS:
                    warnings.filterwarnings("error", r".*is not one of.*", ValidationWarning, r".*jwst.*")
            try:
                result = func(*args, **keys)
            finally:
                warnings.showwarning = old_showwarning
        return result
    return wrapper

def hijacked_showwarning(message, category, filename, lineno, *args, **keys):
    """Map the warnings.showwarning plugin function parameters onto log.warning."""
    try:
        scat = str(category).split(".")[-1].split("'")[0]
    except Exception:
        scat = category
    try:
        sfile = str(filename).split(".egg")[-1].split("site-packages")[-1].replace("/",".").replace(".py", "")
        while sfile.startswith(("/",".")):
            sfile = sfile[1:]
    except Exception:
        sfile = filename
    message = str(message).replace("\n","")
    log.warning(scat, ":", sfile, ":", message)

# ----------------------------------------------------------------------------------------------
#
# Cross-strapping is used to support different synonyms for the same keyword:
#
#   FITS
#   JWST data model dotted path
#   Ad hoc names appearing in un-modeled reference files
#
# It's complicated because of inconsistent support for data model nomenclature both
# within and between projects;  it's currently a JWST-only concept but is implemented
# in a pluggable way.
#
# For "un-modeled" references or if the decision is made to drop datamodels use, each
# observatories locator module can define CROSS_STRAPPED_KEYWORDS.  See an example, jwst.
#
# For projects supporting the datamodels,  the schema is used to define the correspondence
# between data model dotted paths and the keyword of the underlying file format.
#
def cross_strap_header(header):
    """Set up keyword equivalencies in a copy of `header`.  Ensure both FITS
    and datamodel dotted path variants are defined for each keyword.
    Also add variations defined by observatory locator module
    CROSS_STRAPPED_KEYWORDS.
    """
    crossed = dict(header)
    try:
        locator = utils.header_to_locator(header)
    except Exception:
        log.verbose_warning(
            "Cannot identify observatory from header. Skipping keyword aliasing")
        return crossed
    equivalency_pairs = locator.get_cross_strapped_pairs(header)
    for pair in equivalency_pairs:
        _cross_strap_pair(crossed, pair)
    return crossed

def equivalence_dict_to_pairs(equivalent_keywords_dict):
    """Convert a dictionary mapping master keywords to equivalents to
    a list of keyword pairs that should be cross-strapped.
    """
    pairs = []
    log.verbose("Explicitly cross_strapped_keywords:",
                log.PP(equivalent_keywords_dict), verbosity=90)
    for master, slaves in equivalent_keywords_dict.items():
        for slave in slaves:
            if master != slave:
                pairs.append((master, slave))
                pairs.append((slave, master))
    return pairs


def _cross_strap_pair(header, keyword_pair):
    """Mutate `header` using (master, slave) `keyword_pair` so that slave
    duplicates master's value under slave's name IFF master is defined
    in header and slave is not.
    """
    master_key, slave_key = keyword_pair
    master_val = header.get(master_key, "UNDEFINED")
    slave_val =  header.get(slave_key, "UNDEFINED")
    if slave_val == "UNDEFINED" and master_val != "UNDEFINED":
        header[slave_key] = master_val

# ----------------------------------------------------------------------------------------------

def convert_to_eval_header(header):
    """To support using file headers in eval expressions,  two changes need to be made:

    1. JWST data model keywords, dotted paths, need to be translated to underscored paths.
    This makes them valid identifiers instead of non-existent nested objects when evaled.

    2. Numerial values that CRDS has conditioned into strings need to be converted back to
    numerical values so they can be used in arithmetic expressions.
    """
    header = _destringize_numbers(header)
    header = _convert_dotted_paths(header)
    return header

def _destringize_numbers(header):
    """Convert string values in `header` that work as numbers back into
    ints and floats.
    """
    with_numbers = {}
    for key, val in header.items():
        try:
            val = int(val)
        except:
            try:
                val = float(val)
            except:
                pass
        with_numbers[key] = val
    return with_numbers

def _convert_dotted_paths(header):
    """Convert header dotted-path keys into valid Python identifiers
    (for eval()) by using underscores instead of periods and add to
    existing contents of `header`.
    """
    cleaned = dict(header)
    for key, val in header.items():
        clean = re.sub(r"([A-Za-z][A-Za-z0-9_]*)\.", r"\1_", key)
        cleaned[clean] = val
    return cleaned

# ----------------------------------------------------------------------------------------------

def ensure_keys_defined(header, needed_keys=(), define_as="UNDEFINED"):
    """Define any keywords from `needed_keys` which are missing in `header`,  or defined as 'UNDEFINED',
    as `default`.

    Normally this defines missing keys as UNDEFINED.

    It can be used to redefine UNDEFINED as something else,  like N/A.
    """
    header = dict(header)
    for key in needed_keys:
        if key not in header or header[key] in ["UNDEFINED", None]:
            header[key] = define_as
    return header

# ================================================================================================

class AbstractFile:

    format = "ABSTRACT"

    def __init__(self, filepath, original_name=None, observatory=None):
        """Create an AbstractFile.

        Required for use:

        filepath          working path for this file

        Retained for debug:

        original_name     abstract,  possibly more readable name to infer type and observatory w/o io
        observatory       observatory this file belongs to
        """
        # This __init__ should be kept fast
        self.filepath = filepath
        self.original_name = original_name
        self.observatory = observatory
        self.array_formats = {}

    def _unsupported_file_op_error(self, method):
        return exceptions.UnsupportedFileOpError(
            "Method", repr(method), "is not supported for file format", repr(self.format))

    def add_checksum(self):
        """Add checksum to`self.filepath`."""
        raise self._unsupported_file_op_error("add_checksum")

    def remove_checksum(self):
        """Remove checksum from`self.filepath`."""
        raise self._unsupported_file_op_error("remove_checksum")

    def verify_checksum(self):
        """Verify checksum in `self.filepath`."""
        raise self._unsupported_file_op_error("verify_checksum")

    def get_format(self):
        """Return a string describing the structure of file at `filepath`,  intended
        for file overview describing generic array structure.
        """
        raise self._unsupported_file_op_error("get_format")

    def get_array_properties(self, array_name, keytype="A"):
        """Return a basic properties dictionary for array named `array_name`."""
        raise self._unsupported_file_op_error("get_array_properties")

    def get_array(self, array_name):
        """Return the array object corresponding to array selected by `array_id_info`."""
        raise self._unsupported_file_op_error("get_array")

    # ----------------------------------------------------------------------------------------------

    def getval(self, key, **keys):
        """Return a single metadata value from `key` of file at `filepath`."""
        return self.get_header((key,), **keys)[key]

    def setval(self, key, value):
        """Set the value of a single metadata key,  nominally in the 'primary header'."""
        raise self._unsupported_file_op_error("setval")

    # ----------------------------------------------------------------------------------------------

    def get_header(self, needed_keys, **keys):
        """Return dictionary of metadata for this file,  e.g. FITS primary header
         dictionary featuring keywords `needed_keys`.
         """
        raw_header = self.get_raw_header(needed_keys, **keys)
        reduced_header = self._reduce_header(raw_header, needed_keys)
        crossed_header = cross_strap_header(reduced_header)
        crossed_header["FILE_FORMAT"] = \
            self.__class__.__name__[:-len("File")].upper()
        return crossed_header

    def get_raw_header(self, needed_keys, **keys):
        """Return the metadata dictionary associated with this file,  nominally a dict
        describing the FITS header, ASDF tree, or JSON or YAML contents.
        """
        raise self._unsupported_file_op_error("get_raw_header")
    # ----------------------------------------------------------------------------------------------

    def _reduce_header(self, old_header, needed_keys=()):
        """Limit `header` to `needed_keys`,  converting all keys to upper case
        and making note of any significant duplicates, and adding any missing
        `needed_keys` as UNDEFINED.

        To detect duplicates,  use an item list for `old_header`,  not a dict.
        """
        needed_keys = tuple(key.upper() for key in needed_keys)
        header = {}
        if isinstance(old_header, dict):
            old_header = old_header.items()
        for (key, value) in old_header:
            key = str(key).upper()
            value = str(value)
            if (not needed_keys) or key in needed_keys:
                if key in header and header[key] != value:
                    if key not in DUPLICATES_OK:
                        log.verbose_warning("Duplicate key", repr(key), "in", repr(self.filepath),
                                            "using", repr(header[key]), "not", repr(value), verbosity=70)
                        continue
                    elif key in APPEND_KEYS:
                        header[key] += "\n" + value
                else:
                    header[key] = value
        return ensure_keys_defined(header, needed_keys)

    # ----------------------------------------------------------------------------------------------

    def to_simple_types(self, tree):
        """Convert a tree structure to a flat dictionary of simple types with dotted path tree keys."""
        result = dict()
        for key in tree:
            if not isinstance(key, str):  # skip non-string keys
                continue
            value = tree[key]
            if isinstance(value, (type(tree), dict)):
                nested = self.to_simple_types(value)
                for nested_key, nested_value in nested.items():
                    result[str(key.upper() + "." + nested_key)] = nested_value
            else:
                result[str(key.upper())] = self._simple_type(value)
        return result

    def _simple_type(self, value):
        """Convert ASDF values to simple strings, where applicable,  exempting potentially large values."""
        if isinstance(value, (str, int, float, complex)):
            rval = str(value)
        elif isinstance(value, (list, tuple)):
            rval = tuple(self._simple_type(val) for val in value)
        elif isinstance(value, (datetime.datetime, Time)):
            rval = timestamp.reformat_date(value).replace(" ", "T")
        else:
            rval = "SUPRESSED_NONSTD_TYPE: " + repr(str(value.__class__.__name__))
        return rval

    def get_asdf_standard_version(self):
        """
        Return the ASDF Standard version associated with this file as a string,
        or `None` if the file is neither an ASDF file nor contains an embedded
        ASDF file.
        """
        return None
