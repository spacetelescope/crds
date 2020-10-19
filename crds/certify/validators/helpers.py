"""This module defines helper functions that are used in "expression" validators,
either in a "presence" condition or as the "constraint" condition.   The expressions
themselves appear in .tpn files and are dynamically eval'ed in the context of a reference
header and other globals like these functions.

These functions are used to keep the .tpn expressions comparatively simple since those
are restricted to pigeon-Python that does not allow spaces.  See the JWST .tpn files
(particularly *array*.tpn) for examples of presence or constraint expressions,  grep
those files for these functions.
"""
from crds.core import utils, exceptions

# ----------------------------------------------------------------------------

# Table check expression helper functions

def has_columns(array_info, col_names):
    """Return True IFF CRDS `array_info` object defines `col_names` columns in any order.

    >>> has_columns(utils.Struct(COLUMN_NAMES=["THIS","THAT","ANOTHER"]), ["THAT","ANOTHER","THIS"])
    True
    >>> has_columns(utils.Struct(COLUMN_NAMES=["THIS","THAT","ANOTHER"]), ["THAT","ANOTHER","FOO"])
    False

    >>> has_columns("UNDEFINED",  ["THAT","ANOTHER","FOO"])
    False

    NOTE:  does not disallow extra columns not listed.
    """
    if not array_exists(array_info):
        return False
    for col in col_names:
        if col not in array_info.COLUMN_NAMES:
            return False
    return True

def has_type(array_info, typestr):
    """Return True IFF CRDS `array_info` object has a data array of type `typestr`.

    >>> has_type(utils.Struct({"DATA_TYPE" : "int8"}), "INT")
    True
    >>> has_type(utils.Struct({"DATA_TYPE" : "uint64"}), "INTEGER")
    True
    >>> has_type(utils.Struct({"DATA_TYPE" : "float64"}), "INTEGER")
    False
    >>> has_type(utils.Struct({"DATA_TYPE" : "float32"}), "FLOAT")
    True
    >>> has_type(utils.Struct({"DATA_TYPE" : "float32"}), "INT")
    False
    >>> has_type(utils.Struct({"DATA_TYPE" : "float64"}), "FLOAT")
    True
    >>> has_type(utils.Struct({"DATA_TYPE" : "complex32"}), "COMPLEX")
    True
    >>> has_type(utils.Struct({"DATA_TYPE" : "complex64"}), "COMPLEX")
    True
    >>> has_type(utils.Struct({"DATA_TYPE" : "complex64"}), "FLOAT")
    False
    >>> has_type(utils.Struct({"DATA_TYPE" : "complex64"}), ["FLOAT","INT"])
    False
    >>> has_type(utils.Struct({"DATA_TYPE" : "complex64"}), ["COMPLEX","INT"])
    True
    """
    possible_types = [typestr] if isinstance(typestr, str) else typestr
    for possible_type in possible_types:
        itype = _image_type(possible_type)
        if array_exists(array_info) and itype in array_info.DATA_TYPE:
            return True
    return False

def _image_type(typestr):
    """Return the translation of CRDS fuzzy type name `typestr` into numpy dtype str() prefixes.
    If CRDS has no definition for `typestr`,  return it unchanged.
    """
    return {
        'COMPLEX':'complex',
        'INT' : 'int',
        'INTEGER' : 'int',
        'FLOAT' : 'float',
        'BOOLEAN' : 'bool'
    }.get(typestr, typestr)

def has_column_type(array_info, col_name, typestr):
    """Return True IFF column `col_name` of CRDS `array_info` object has a
    data array of type `typestr`.

    >>> has_column_type(utils.Struct(DATA_TYPE={"WAVELENGTH":">f4"}), "WAVELENGTH", "FLOAT")
    True

    >>> has_column_type(utils.Struct(DATA_TYPE={"WAVELENGTH":">f4"}), "WAVELENGTH", "INTEGER")
    False

    >>> has_column_type("UNDEFINED", "WAVELENGTH", "INTEGER")
    False

    >>> has_column_type(utils.Struct(DATA_TYPE={"WAVELENGTH":">f4"}), "WAVELEN", "INTEGER")
    Traceback (most recent call last):
    ...
    crds.core.exceptions.MissingColumnError: Data type not defined for column 'WAVELEN'

    """
    if not array_exists(array_info):
        return False
    typestrs = _table_type(typestr)
    try:
        for typestr in typestrs:
            if typestr in array_info.DATA_TYPE[col_name.upper()]:
                return True
        return False
    except KeyError:
        pass
    raise exceptions.MissingColumnError("Data type not defined for column", repr(col_name))

def _table_type(typestr):
    """Return the translation of CRDS fuzzy type name `typestr` into numpy dtype str() prefixes.
    If CRDS has no definition for `typestr`,  return it unchanged.
    """
    int_types = [">i","<i","uint","int"]
    float_types = [">f","<f","float","float"]
    complex_types = [">c","<c","complex","complex"]
    string_types = ["|S"]

    def _array_types(types):
        return ["('" + typestr for typestr in types]

    trans = {
        'COMPLEX': complex_types,
        'COMPLEX_ARRAY': _array_types(complex_types),
        'INT' : int_types,
        'INTEGER' : int_types,
        'INT_ARRAY' : _array_types(int_types),
        'INTEGER_ARRAY' : _array_types(int_types),
        'FLOAT' : float_types,
        'FLOAT_ARRAY' : _array_types(float_types),
        'STR' : string_types,
        'STRING' : string_types,
        'STR_ARRAY' : _array_types(string_types),
        'STRING_ARRAY' : _array_types(string_types),
    }.get(typestr, typestr)

    return trans

def is_table(array_info):
    """Return True IFF CRDS `array_info` object corresponds to a table.

    >>> is_table(utils.Struct(KIND="IMAGE"))
    False
    >>> is_table(utils.Struct(KIND="TABLE"))
    True
    """
    return array_exists(array_info) and array_info.KIND=="TABLE"

def is_image(array_info):
    """Return True IFF CRDS `array_info` object corresponds to an image.

    >>> is_image(utils.Struct(KIND="IMAGE"))
    True
    >>> is_image(utils.Struct(KIND="TABLE"))
    False
    """
    return array_exists(array_info) and array_info.KIND=="IMAGE"

def  array_exists(array_info):
    """Return True IFF array_info is not UNDEFINED.

    >>> array_exists("UNDEFINED")
    False
    >>> array_exists(utils.Struct({"KIND":"IMAGE", "SHAPE" : (2048,2048), "TYPE": "float32"}))
    True
    """
    return array_info != "UNDEFINED"

def is_imaging_mode(exp_type):
    """Return True IFF `exp_type` is one of the imaging modes for any instrument.

    >>> is_imaging_mode('MIR_IMAGE')
    True
    >>> is_imaging_mode("NRS_IFU")
    False
    >>> is_imaging_mode('NRS_VERIFY')
    True
    """
    return exp_type in ["NRC_IMAGE", "NRC_TACQ", "NRC_TACONF", "NRC_CORON", "NRC_TSIMAGE",
                        "NRC_FOCUS", "NRC_DARK", "NRC_FLAT", "NRC_LED",

                        "MIR_IMAGE", "MIR_TACQ", "MIR_LYOT", "MIR_4QPM", "MIR_DARK",
                        "MIR_FLATIMAGE", "MIR_CORONCAL",

                        "NRS_CONFIRM", "NRS_DARK", "NRS_FOCUS", "NRS_IMAGE", "NRS_MIMF",
                        "NRS_TACONFIRM", "NRS_TACQ", "NRS_TASLIT", "NRS_VERIFY",

                        "NIS_IMAGE", "NIS_TACQ", "NIS_TACONFIRM", "NIS_AMI",
                        "NIS_FOCUS", "NIS_DARK", "NIS_LAMP",

                        "FGS_IMAGE", "FGS_FOCUS", "FGS_SKYFLAT", "FGS_INTFLAT", "FGS_DARK", "FGS_ID-STACK"]

def is_full_frame(subarray):
    """Return True IFF `subarray` is defined and has a full frame subarray value.

    >>> is_full_frame("UNDEFINED")
    False
    >>> is_full_frame("FULL")
    True
    >>> is_full_frame("GENERIC")
    True
    >>> is_full_frame("N/A")
    True
    >>> is_full_frame("ANY")
    True
    >>> is_full_frame("*")
    True
    >>> is_full_frame("MASK1140")
    False
    >>> is_full_frame("BRIGHTSKY")
    False
    """
    return subarray in ["FULL","GENERIC","N/A","ANY","*"]

def is_subarray(subarray):
    """Return True IFF `subarray` is defined and is not a full frame value.

    >>> is_subarray("UNDEFINED")
    False
    >>> is_subarray("GENERIC")
    False
    >>> is_subarray("N/A")
    False
    >>> is_subarray("ANY")
    False
    >>> is_subarray("*")
    False
    >>> is_subarray("FULL")
    False
    >>> is_subarray("MASK1140")
    True
    >>> is_subarray("BRIGHTSKY")
    True
    """
    return  (subarray != "UNDEFINED") and not is_full_frame(subarray)

def subarray_defined(header):
    """Return True IFF SUBARRAY related keywords are defined.

    >>> header = dict(SUBARRAY="GENERIC",SUBSTRT1="1",SUBSTRT2="1",SUBSIZE1="2048",SUBSIZE2="2048")
    >>> subarray_defined(header)
    True

    >>> header = dict(SUBARRAY="GENERIC",SUBSTRT1="1",SUBSTRT2="1",SUBISIZE2="2048")
    >>> subarray_defined(header)
    False
    """
    for keyword in ["SUBARRAY","SUBSTRT1","SUBSTRT2","SUBSIZE1","SUBSIZE2"]:
        value = header.get(keyword,"UNDEFINED")
        if value == "UNDEFINED":
            return False
    return True

def is_irs2(readpatt):
    """Return True IFF `readpatt` is one of the IRS2 READPATTs.

    >>> is_irs2("NRSIRS2")
    True
    >>> is_irs2("NRSIRS2RAPID")
    True
    >>> is_irs2("NRSN32R8")
    False
    >>> is_irs2("ALLIRS2")
    True
    """
    return 'IRS2' in readpatt

def is_defined(value):
    """Return True IFF `value` is not 'UNDEFINED' or None.

    >>> is_defined("UNDEFINED")
    False

    >>> is_defined(None)
    False

    >>> is_defined("FOO")
    True
    """
    return value not in ["UNDEFINED", None]

# # @utils.traced
# def nir_filter(instrument, reftype, exp_type):
#     """Return True if a SCI, ERR, or DQ array is appropriate for the specified
#     JWST NIR instrument, reftype, and exp_type.   This can be used to filter
#     out NIR SCI,ERR,DQ array definitions for those NIRSPEC modes and types
#     that don't define them.  The logic is too complex to inline.
#
#     >>> nir_filter("NIRSPEC", "SFLAT", "NRS_MSASPEC")
#     True
#     >>> nir_filter("NIRSPEC", "SFLAT", "NRS_IFU")
#     True
#     >>> nir_filter("NIRSPEC", "SFLAT", "NRS_FIXEDSLIT")
#     False
#     >>> nir_filter("NIRSPEC", "SFLAT", "NRS_BRIGHTOBJ")
#     False
#
#     >>> nir_filter("NIRSPEC", "DFLAT", "ANY")
#     True
#
#     >>> nir_filter("NIRSPEC", "FFLAT", "NRS_MSASPEC")
#     True
#     >>> nir_filter("NIRSPEC", "FFLAT", "NRS_IFU")
#     False
#     >>> nir_filter("NIRSPEC", "FFLAT", "NRS_FIXEDSLIT")
#     False
#     >>> nir_filter("NIRSPEC", "FFLAT", "NRS_BRIGTOBJ")
#     False
#
#     """
#     assert instrument != "MIRI",  "nir_filter() .tpn function should only be called for NIR-detector based instruments."
#     if instrument == "NIRSPEC":
#         if reftype == "SFLAT":
#             return exp_type in ["NRS_MSASPEC","NRS_IFU"]
#         elif reftype == "DFLAT":
#             return True
#         elif reftype == "FFLAT":
#             return exp_type in ["NRS_MSASPEC"]
#         elif reftype == "AREA":
#             return is_imaging_mode(exp_type)
#         else:
#             return True
#     else:
#         return True

# ----------------------------------------------------------------------------

# These are presence field helpers that mutate a True value of a presence expression
# into one of the non-boolean presence flags.   This enables combining presence values
# like "O" with presence expressions.   In general,  when an expression is True then
# the presence character of the wrapper helper is returned,  e.g.:
#
# (OPTIONAL(True)) --> "O"
# (OPTIONAL(False)) --> False,  constraint not evaluated.
#
# The enables having constraints which are conditionally optional,  so e.g. a constraint
# on

def optional(flag=True):
    """When this flag is True, an exception should be issued if the related keyword/element is
    defined and the constraint fails.   If the keyword/element is not defined or `flag` is False,
    the constraint should be ignored.   Returns "O" or False

    >>> optional(True)
    'O'
    >>> optional(False)
    False
    """
    return "O" if flag else False

def required(flag=True):
    """When this flag is True,  an exception should be issued if the related keyword/element is
    not defined.     Returns "R" or False.

    >>> required(True)
    'R'
    >>> required(False)
    False
    """
    return "R" if flag else False

def warning(flag=True):
    """Presence condition mutator/wrapper:

    When flag is True,  a warning should be issued if the related keyword/element is
    not defined.     Returns "W" or False.

    >>> warning(True)
    'W'
    >>> warning(False)
    False
    """
    return "W" if flag else False

def warn_only(flag):
    """Expression constraint mutator/wrapper:

    When flag is True,  the wrapped expression was satisifed, so return True
    signaling a passed validator expression.

    If the flag is False, the expression evaluated successfully but was not
    satisified.  Return the value "W" signaling that only a warning should be
    issued rather than an exception or error.

    >>> warn_only(True)
    True

    >>> warn_only(False)
    'W'
    """
    return "W" if not flag else True

def subarray(flag=True):
    """When this flag is True,  the related constraint should be applied if
    is_full_frame(SUBARRAY) is False.     Returns "S" or False.

    >>> subarray(True)
    'S'
    >>> subarray(False)
    False
    """
    return "S" if flag else False

def full_frame(flag=True):
    """When this flag is True,  the related constraint should be applied if
    is_full_frame(SUBARRAY) is True.     Returns "F" or False.

    >>> full_frame(True)
    'F'
    >>> full_frame(False)
    False
    """
    return "F" if flag else False

def all_subarray(flag=True):
    """When `flag` is True,  mark this constraint as applying to all SUBARRAY forms,
    including full frame, as long as SUBARRAY is defined.   Returns "A" or False.

    >>> all_subarray(True)
    'A'
    >>> all_subarray(False)
    False
    """
    return "A" if flag else False

# ----------------------------------------------------------------------------

def ndim(array, dims):
    """Return True IFF CRDS `array` object has number of dimensions `dims`.

    >>> array = utils.Struct({"KIND":"IMAGE", "SHAPE" : (2048,2048), "TYPE": "float32"})

    >>> ndim(array, 2)
    True

    >>> ndim(array, 3)
    False

    """
    return len(array.SHAPE) == dims

# ----------------------------------------------------------------------------

def test():
    import doctest
    from crds.certify import validator_helpers
    return doctest.testmod(validator_helpers)

if __name__ == "__main__":
    print(test())
