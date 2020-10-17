import os
import re
import copy
import abc

# ============================================================================

import numpy as np

# ============================================================================

from crds.core import log, utils, timestamp, selectors, config
from crds.core.exceptions import MissingKeywordError, IllegalKeywordError
from crds.core.exceptions import TpnDefinitionError, RequiredConditionError
from crds.core.exceptions import BadKernelSumError, BadKernelCenterPixelTooSmall
from crds.core import generic_tpn
from crds.core.generic_tpn import TpnInfo # generic TpnInfo code
from crds.io import tables
from crds import data_file

from . import helpers as validator_helpers

# ============================================================================

def array_name(rootname):
    """Given the `rootname` for an array,  return the name of the array used
    in Validator expressions.

    >>> array_name('SCI')
    'SCI_ARRAY'
    >>> array_name(1)
    'ARRAY_1'
    >>> array_name('1')
    'ARRAY_1'

    """
    if isinstance(rootname,int) or re.match(r"\d+", rootname):
        return "ARRAY_" + str(rootname)
    elif isinstance(rootname, str):
        return rootname.upper() + "_ARRAY"
    else:
        raise TypeError("Invalid array rootname type for: " + repr(rootname))

# ============================================================================

class Validator:
    """Validator is an Abstract class that applies TpnInfo objects to reference files.  Each
    Validator handles a single constraint defined in a .tpn file.
    """
    def __init__(self, info, context=None):
        self.info = info
        self.name = info.name
        self.context = context
        self._presence_condition_code = None

        if self.info.datatype not in generic_tpn.TpnInfo.datatypes:
            raise ValueError("Bad TPN datatype field " + repr(self.info.presence))

        if not (self.info.presence in generic_tpn.TpnInfo.presences or
                self.conditionally_required):
            raise ValueError("Bad TPN presence field " + repr(self.info.presence))

        if not (self.info.keytype in generic_tpn.TpnInfo.keytypes):
            raise ValueError("Bad TPN keytype " + repr(self.info.keytype))

        if not hasattr(self.__class__, "_values"):
            self._values = self.condition_values(info.values)

    @property
    def _eval_namespace(self):
        """Namespace in which various validator expressions and conditions are evaluated."""
        space = dict(globals())
        space.update(validator_helpers.__dict__)
        return space

    @property
    def complex_name(self):
        """If this is an array validator,  return name of array as it appears in expressions,
        otherwise return self.name.
        """
        if self.info.keytype in ["A","D"]:
            return array_name(self.name)
        else:
            return self.name

    def verbose(self, filename, value, *args, **keys):
        """Prefix log.verbose() with standard info about this Validator.
        Unique message is in *args, **keys
        """
        return log.verbose("File=" + repr(os.path.basename(filename)),
                           "class=" + repr(self.__class__.__name__[:-len("Validator")]),
                           "keyword=" + repr(self.name),
                           "value=" + repr(value),
                           *args, **keys)

    def condition(self, value):
        """Condition `value` to standard format for this Validator."""
        return value

    def condition_values(self, values):
        """Return the Validator-specific conditioned version of all the values in `info`."""
        return sorted([self.condition(value) for value in values])

    def __repr__(self):
        """Represent Validator instance as a string."""
        return self.__class__.__name__ + repr(self.info)

    def check(self, filename, header):
        """Pull the value(s) corresponding to this Validator out of it's
        `header` or the contents of the file.   Check them against the
        requirements defined by this Validator.
        """
        if not self.is_applicable(header):
            return True

        if self.info.keytype == "C":
            return self.check_column(filename, header)
        elif self.info.keytype == "G":
            return self.check_group(filename, header)
        elif self.info.keytype in ["H","X","A","D"]:
            return self.check_header(filename, header)
        else:
            raise ValueError("Unknown TPN keytype " + repr(self.info.keytype) +
                             " for " + repr(self.name))

    def check_header(self, filename, header):
        """Extract the value for this Validator's keyname,  either from `header`
        or from `filename`'s header if header is None.   Check the value.
        """
        value = header.get(self.complex_name, "UNDEFINED")
        if value in [None, "UNDEFINED"]:
            return self.handle_missing(header)
        elif self.info.presence == "E":
            raise IllegalKeywordError("*Must not define* keyword " + repr(self.name))
        return self.check_value(filename, value)

    def check_value(self, filename, value):
        """Check a single header or column value against the legal values
        for this Validator.
        """
        if value in [None, "UNDEFINED"]: # missing optional or excluded keyword
            return True
        value = self.condition(value)
        if not self._values and log.get_verbose():
            self.verbose(filename, value, "no .tpn values defined.")
            return True
        self._check_value(filename, value)
        # If no exception was raised, consider it validated successfully
        return True

    def _check_value(self, filename, value):
        """_check_value is the core simple value checker."""
        raise NotImplementedError(
            "Validator is an abstract class.  Sub-class and define _check_value().")

    def check_column(self, filename, header):
        """Extract a column of new_values from `filename` and check them all against
        the legal values for this Validator.   This checks a single column,  not a row/mode.
        """
        column_seen = False
        for tab in tables.tables(filename):
            if self.name in tab.colnames:
                column_seen = True
                # new_values must not be None,  check all, waiting to fail later
                for i, value in enumerate(tab.columns[self.name]): # compare to TPN values
                    self.check_value(filename + "[" + str(i) +"]", value)
        if not column_seen:
            self.handle_missing(header)
        return True

    def check_group(self, _filename, _header):
        """Probably related to pre-FITS HST GEIS files,  not implemented."""
        log.warning("Group keys are not currently supported by CRDS.")

    def handle_missing(self, header):
        """This Validator's key is missing.   Either raise an exception or
        ignore it depending on whether this Validator's key is required.
        """
        presence = self.info.presence
        if self.conditionally_required:
            if header:
                presence = self.is_applicable(header)
                if not presence:
                    log.verbose("Conditional constraint on", repr(self.name),
                                "is not required by", repr(self.info.presence), verbosity=70)
                    return "UNDEFINED"
            else:
                log.verbose("No header supplied to evaluate conditional constraint",
                            repr(self.name), "based on", repr(self.info.presence),
                            "  Skipping.")
                return "UNDEFINED"
        if presence in ["R","P",True]:
            raise MissingKeywordError("Missing required", self._keytype_descr, repr(self.name))
        elif presence in ["W"]:
            log.warning("Missing suggested", self._keytype_descr, repr(self.name))
        elif presence in ["O"]:
            log.verbose("Optional", self._keytype_descr, repr(self.name), " is missing.", verbosity=70)
        elif presence in ["S","F","A"]:
            log.verbose("Conditional SUBARRAY parameter is not defined.")
        else:
            raise TpnDefinitionError("Unexpected validator 'presence' value:",
                                     repr(self.info.presence))
        return "UNDEFINED"

    @property
    def _keytype_descr(self):
        descr = self.info._repr_keytype()[1:-1]
        return {
            "HEADER" : "keyword",
            "COLUMN" : "table column",
            "GROUP" : "group",
            "ARRAY_FORMAT" : "array",
            "ARRAY_DATA" : "array",
            "EXPRESSION" : "expression",
            }.get(descr, descr.lower())

    @property
    def optional(self):
        """Return True IFF this parameter is optional."""
        return self.info.presence in ["O","W"]

    @property
    def conditionally_required(self):
        """Return True IFF this validator has a header expression defining when it is valid
        instead of the classic single character values.   If it has an expression, make sure
        it compiles now.
        """
        has_condition = generic_tpn.is_expression(self.info.presence)
        if has_condition:
            if not self._presence_condition_code:
                self._presence_condition_code = compile(self.info.presence, repr(self.info), "eval")
            return True
        else:
            return False

    def is_applicable(self, header):
        """Return True IFF this Validator is applicable based upon header and the
        presence field of the TpnInfo.   The presence field can contain an expression
        which is evaluated in the context of `header`.

        There are variations of "True" which can be returned.  Some checks are
        designated optional (O), warning (W), or as only applying to FULL (F)
        frame or true SUBARRAY (S) cases.  These cases return the presence
        character which as a non-zero length string also evaluates to True but
        carries extra information,  particularly "optional" or "warning".
        """
        SUBARRAY = header.get('SUBARRAY','UNDEFINED')
        if self._presence_condition_code:
            try:
                presence = eval(self._presence_condition_code, header, self._eval_namespace)
                log.verbose("Validator", self.info, "is",
                            "applicable." if presence else "not applicable.", verbosity=70)
                if not presence:
                    return False
            except Exception as exc:
                log.warning("Failed checking applicability of", repr(self.info),"skipping check : ", str(exc))
                return False
        else:
            presence = self.info.presence
        if presence in ["O","W"]:
            return presence
#            return header.get(self.name, False) != "UNDEFINED"
        elif presence == "F": # IF_FULL_FRAME
            return validator_helpers.is_full_frame(SUBARRAY)
        elif presence == "S": # IF_SUBARRAY
            return validator_helpers.is_subarray(SUBARRAY)
        elif presence == "A":
            return validator_helpers.subarray_defined(header)
        else:
            return True

    def get_required_copy(self):
        """Return a copy of this validator with self.info.presence overridden to R/required."""
        required = copy.deepcopy(self)
        idict = required.info._asdict()  # returns OrderedDict,  method is public despite _
        idict["presence"] = "R"
        required.info = TpnInfo(*idict.values())
        return required

# ----------------------------------------------------------------------------

class KeywordValidator(Validator):
    """Checks that a value is one of the literal TpnInfo values."""

    def condition(self, value):
        """Condition `value` to standard format for this Validator, squashing
        Python-2.7 unicode.
        """
        return str(value)

    def _check_value(self, filename, value):
        """Raises ValueError if `value` is not valid."""
        if self._match_value(value):
            if self._values and log.get_verbose():
                self.verbose(filename, value, "is in", repr(self._values))
        else:
            raise ValueError("Value " + str(log.PP(value)) + " is not one of " +
                             str(log.PP(self._values)))

    def _match_value(self, value):
        """Do a literal match of `value` to the allowed values of this tpninfo."""
        return value in self._values or not self._values

# ----------------------------------------------------------------------------

class CharacterValidator(KeywordValidator):
    """Validates values of type Character."""
    def condition(self, value):
        """Condition a header values by stripping, converting to all uppercase, and replacing
        space with underscore.
        """
        chars = str(value).strip().upper()
#         if " " in chars:
#             chars = '"' + chars + '"'
        return chars

    def _check_value(self, filename, value):
        """Support rmap validation by handling esoteric values and or-groups."""
        values = selectors.glob_list(value)
        if len(values) > 1:
            self.verbose(filename, value, "is an or'ed parameter matching", values)
        for val in values:
            super(CharacterValidator, self)._check_value(filename, val)

# ----------------------------------------------------------------------------

class LogicalValidator(KeywordValidator):
    """Validate booleans."""

    _values = ["T","F"]

# ----------------------------------------------------------------------------

class NumericalValidator(KeywordValidator):
    """Check the value of a numerical keyword,  supporting range checking."""

    def __init__(self, info, *args, **keys):
        self.is_range = (len(info.values) == 1) and (":" in info.values[0])
        if self.is_range:
            smin, smax = info.values[0].split(":")
            self.min, self.max = self.condition(smin), self.condition(smax)
        else:
            self.min = self.max = None
        super(NumericalValidator, self).__init__(info, *args, **keys)

    def condition_values(self, values):
        if self.is_range:
            assert self.min != '*' and self.max != '*', \
                               "TPN error, range min/max conditioned to '*'"
            values = [self.min, self.max]
        else:
            values = KeywordValidator.condition_values(self, values)
        return values

    def _check_value(self, filename, value):
        if self.is_range:
            if value < self.min or value > self.max:
                raise ValueError("Value for " + repr(self.name) + " of " +
                                 repr(value) + " is outside acceptable range " +
                                 self.info.values[0])
            elif log.get_verbose():
                self.verbose(filename, value, "is in range", self.info.values[0])
        else:   # First try a simple exact string match check
            KeywordValidator._check_value(self, filename, value)

# ----------------------------------------------------------------------------

class IntValidator(NumericalValidator):
    """Validates integer values."""
    condition = int

# ----------------------------------------------------------------------------

class FloatValidator(NumericalValidator):
    """Validates floats of any precision."""

    epsilon = 1e-7

    condition = float

    type_name = "Float"

    def _check_value(self, filename, value):
        try:
            NumericalValidator._check_value(self, filename, value)
        except ValueError as exc:   # not a range or exact match,  handle fp fuzz
            if self.is_range: # XXX bug: boundary values don't handle fuzz
                raise
            for possible in self._values:
                if np.allclose(value, possible, self.epsilon):
                    self.verbose(filename, value, "is within +-",
                                 repr(self.epsilon), "of", repr(possible))
                    return
            msg = " ".join([self.type_name, repr(value), "is not within +-",
                            repr(self.epsilon), "of any of", repr(self._values)])
            raise ValueError(msg) from exc

# ----------------------------------------------------------------------------

class RealValidator(FloatValidator):
    """Validate 32-bit floats."""

    type_name = "Real"

# ----------------------------------------------------------------------------

class DoubleValidator(FloatValidator):
    """Validate 64-bit floats."""

    epsilon = 1e-14

    type_name = "Double"

# ----------------------------------------------------------------------------

class PedigreeBaseValidator(KeywordValidator):
    """Validates abstract &PEDIGREE values."""

    # Abstract atrributes to customize acceptable values and date requirements
    _values = []   # All valid pedigree kinds, e.g. INFLIGHT or GROUND,  no dates
    _values_w_date = []  # Formats similar to INFLIGHT <start> <stop> accepted for these
    _values_wo_date = [] # Formats similar to GROUND are accepted for these
    _dated_format = ""  # Abstract description of preferred date format.

    def _check_value(self, filename, value):
        """Check `value` as a PEDIGREE."""
        pedigree = self._check_pedigree_start_stop(filename, value)
        return super(PedigreeBaseValidator, self)._check_value(filename, pedigree)

    @abc.abstractmethod
    def validate_date(self, date):
        """Subclasses must define validate_date().

        validate_date() parses `date` str for valid format for one date.

        raises ValueError for invalid formats.

        returns datetime for valid formats.
        """

    @property
    def should_be(self):
        """Generate a combined single value + INFLIGHT format recommendation str."""
        return "One of " + repr(self._values_wo_date) + " or " + repr(self._dated_format)

    def _inflight_exc(self, clarification=""):
        """Raise a ValueError() for an INFLIGHT PEDIGREE showing the expected
        format augmented by additional `clarification` str.
        """
        return ValueError(
            "INFLIGHT format should be " + repr(self._dated_format) +
            " : " + clarification)

    def _check_pedigree_start_stop(self, filename, value):
        """Check the start + stop dates for INFLIGHT PEDIGREE values,  and
        return the PEDIGREE "kind" for all values.
        """
        with log.augment_exception("Invalid value:", repr(value)):

            values = value.split()
            if len(values) == 0:
                raise ValueError("Missing value.")
            else:
                pedigree = values[0].upper()
            if len(values) == 1:
                if pedigree not in self._values_wo_date:
                    raise ValueError("Value " + repr(pedigree) +
                                     " cannot be used as a simple value.")
                else:
                    return pedigree
            elif len(values) == 3:
                if pedigree not in self._values_w_date:
                    raise ValueError(
                        "Value " + repr(pedigree) +
                        " cannot be specified with <start> and <stop> dates.")
            else:
                raise ValueError(
                    "Invalid format for PEDIGREE: ", repr(value))

            start, stop = values[1:]

            # timecan't appear in either string
            for char in start+stop:
                if char in ["T"," ",":"]:
                    raise self._inflight_exc(
                        "Time should not appear in INFLIGHT dates.")

            try:
                start_dt = self.validate_date(start)
                stop_dt = self.validate_date(stop)
            except Exception as exc:
                raise self._inflight_exc(str(exc)) from exc

            if not (start_dt <= stop_dt):
                raise self._inflight_exc("Start date > stop date")

            return pedigree

# These class names are "magic" and correspond to
# PEDIGREE and JWSTPEDIGREE Tpn checks
class PedigreeValidator(PedigreeBaseValidator):
    """Validates (HST) &PEDIGREE fields."""

    _values = ["INFLIGHT", "GROUND", "MODEL", "DUMMY", "SIMULATION"]
    _values_w_date = ["INFLIGHT", "GROUND", "MODEL", "DUMMY", "SIMULATION"]
    _values_wo_date = ["GROUND", "MODEL", "DUMMY", "SIMULATION"]
    _dated_format = "INFLIGHT DD/MM/YYYY DD/MM/YYYY"

    def validate_date(self, date):
        """"e.g. '25/02/1996' --> datetime()"""
        try:
            return timestamp.get_dash_date(date)   # YYYY-MM-DD
        except Exception:
            return timestamp.get_slash_date(date)  # DD/MM/YYYY

class JwstpedigreeValidator(PedigreeBaseValidator):
    """Validates &JWSTPEDIGREE fields."""

    _values = ["INFLIGHT", "GROUND", "DUMMY", "SIMULATION"]
    _values_wo_date = ["GROUND", "DUMMY", "SIMULATION"]
    _values_w_date = ["INFLIGHT"]
    _dated_format = "INFLIGHT YYYY-MM-DD YYYY-MM-DD"

    def validate_date(self, date):
        """e.g.  '2018-01-30' --> datetime"""
        return timestamp.get_dash_date(date)

# ----------------------------------------------------------------------------

class SybdateValidator(KeywordValidator):
    """Check &SYBDATE Sybase date fields."""
    def _check_value(self, filename, value):
        self.verbose(filename, value)
        timestamp.Sybdate.get_datetime(value)

# ----------------------------------------------------------------------------

class JwstdateValidator(KeywordValidator):
    """Check &JWSTDATE date fields."""
    def _check_value(self, filename, value):
        self.verbose(filename, value)
#         try:
#             timestamp.Jwstdate.get_datetime(value)
#         except Exception:
#             raise ValueError(log.format(
#                 "Invalid JWST date", repr(value), "for", repr(self.name),
#                 "format should be", repr("YYYY-MM-DDTHH:MM:SS")))
        try:
            timestamp.Jwstdate.get_datetime(value)
        except ValueError:
            try:
                timestamp.Anydate.get_datetime(value)
            except ValueError:
                try:
                    timestamp.Jwstdate.get_datetime(value.replace(" ","T"))
                except ValueError:
                    timestamp.Jwstdate.get_datetime(value)   # re-execute to replace exception raised
            log.warning("Non-compliant date format", repr(value), "for", repr(self.name),
                        "should be", repr("YYYY-MM-DDTHH:MM:SS"),)

# ----------------------------------------------------------------------------

class SlashdateValidator(KeywordValidator):
    """Validates &SLASHDATE fields."""
    def _check_value(self, filename, value):
        self.verbose(filename, value)
        timestamp.Slashdate.get_datetime(value)

# ----------------------------------------------------------------------------

class AnydateValidator(KeywordValidator):
    """Validates &ANYDATE fields."""
    def _check_value(self, filename, value):
        self.verbose(filename, value)
        timestamp.Anydate.get_datetime(value)

# ----------------------------------------------------------------------------

class ExpressionValidator(Validator):
    """Value is an expression on the reference header that must evaluate to True."""

    def __init__(self, info, *args, **keys):
        super(ExpressionValidator, self).__init__(info, *args, **keys)
        self._expr = info.values[0]
        self._expr_code = compile(self._expr, repr(self.info), "eval")

    def _check_value(self, *args, **keys):
        return True

    def check_header(self, filename, header):
        """Evalutate the header expression associated with this validator (as its sole value)
        with respect to the given `header`.

        Note that array-based checkers are not automatically loaded during a classic header
        fetch and expressions can involve operations on multiple keywords or arrays.
        """
        log.verbose("File=" + repr(os.path.basename(filename)), "Checking",
                    repr(self.name), "condition", str(self._expr))
        for keyword in expr_identifiers(self._expr):
            if header.get(keyword, "UNDEFINED") == "UNDEFINED":
                log.verbose_warning("Keyword or Array", repr(keyword),
                                    "is 'UNDEFINED'. Skipping ", repr(self._expr))
                return True   # fake satisfied
        try:
            satisfied = eval(self._expr_code, header, self._eval_namespace)
        except Exception as exc:
            raise RequiredConditionError("Failed checking constraint", repr(self._expr), ":", str(exc))
        if not satisfied:
            raise RequiredConditionError("Constraint", str(self._expr), "is not satisfied.")
        elif satisfied == "W":  # from warn_only() helper
            log.warning("Constraint", str(self._expr), "is not satisfied.")
            satisfied = True
        return satisfied

def expr_identifiers(expr):
    """Scan `expr` for identifiers,  assume helper functions are in mixed or lowercase.

    Returns [ identifier_in_expr, ...]

    >>> expr_identifiers("((EXP_TYPE)in(['NRS_MSASPEC','NRS_FIXEDSLIT','NRS_BRIGHTOBJ','NRS_IFU']))")
    ['EXP_TYPE']

    >>> expr_identifiers("(len(SCI_ARRAY.SHAPE)==2)")
    ['SCI_ARRAY']

    >>> expr_identifiers("_")
    []

    >>> expr_identifiers("200121")
    []

    >>> expr_identifiers("(not(META_SUBARRAY_NAME)in(['GENERIC','N/A']))")
    ['META_SUBARRAY_NAME']
    """
    # First match identifiers including quoted strings and dotted attribute paths.
    candidates = [ key.group(0) for key in re.finditer(r"['\"\.A-Z0-9_a-z]+", expr)]
    # Next reject strings with quotes in them,  or lower case or mixed case
    no_quotes = [key for key in candidates if re.match(r"^[A-Z0-9_\.]+$", key)]
    no_dots = [key.split(".")[0] for key in no_quotes]
    no_numbers = [key for key in no_dots if not re.match(r"\d+", key)]
    no_underscores = [key for key in no_numbers if key != "_"]
    return no_underscores

# ----------------------------------------------------------------------------

class ColumnExpressionValidator(Validator):
    """Value is an expression on the column value that must evaluate to True."""

    def __init__(self, info, *args, **keys):
        super(ColumnExpressionValidator, self).__init__(info, *args, **keys)
        self._expr = info.values[0]
        self._expr_code = compile(self._expr, repr(self.info), "eval")

    def check_value(self, filename, value):
        if value in [None, "UNDEFINED"]: # missing optional or excluded keyword
            return True
        value = self.condition(value)

        try:
            satisfied = eval(self._expr_code, {"VALUE": value}, self._eval_namespace)
        except Exception as exc:
            raise RequiredConditionError("Failed checking constraint", repr(self._expr), ":", str(exc))

        if not satisfied:
            raise RequiredConditionError("Constraint", str(self._expr), "is not satisfied.")
        elif satisfied == "W":  # from warn_only() helper
            log.warning("Constraint", str(self._expr), "is not satisfied.")
            satisfied = True

        return satisfied

    def check_header(self, filename, header):
        return True

# ---------------------------------------------------------------------------

class KernelunityValidator(Validator):
    """Ensure that every image in the specified array as a sum() near 1.0"""
    def _check_value(self, *args, **keys):
        return True

    def check_header(self, filename, header):
        """Evalutate the header expression associated with this validator (as its sole value)
        with respect to the given `header`.  Read `header` from `filename` if `header` is None.
        """
        # super(KernelunityValidator, self).check_header(filename, header)
        array_name = self.complex_name
        all_data = header[array_name].DATA.transpose()
        images = int(np.product(all_data.shape[:-2]))
        images_shape = (images,) + all_data.shape[-2:]
        images_data = np.reshape(all_data, images_shape)
        log.verbose("File=" + repr(os.path.basename(filename)),
                   "Checking", len(images_data), repr(array_name), "kernel(s) of size",
                    images_data[0].shape, "for individual sums of 1+-1e-6.   Center pixels >= 1.")

        center_0 = images_data.shape[-2]//2
        center_1 = images_data.shape[-1]//2
        center_pixels = images_data[..., center_0, center_1]
        if not np.all(center_pixels >= 1.0):
            log.warning("Possible bad IPC Kernel:  One or more kernel center pixel value(s) too small, should be >= 1.0")
            # raise BadKernelCenterPixelTooSmall(
            #    "One or more kernel center pixel value(s) too small,  should be >= 1.0")

        for (i, image) in enumerate(images_data):
            if abs(image.sum()-1.0) > 1.0e-6:
                raise BadKernelSumError("Kernel sum", image.sum(),
                    "is not 1+-1e-6 for kernel #" + str(i), ":", repr(image))

# ----------------------------------------------------------------------------

class IsomorphicfitsverValidator(Validator):
    """Ensure that every image in a (HDU, ver*) stack has the same shape
    and type as (HDU,1).   Subclass to set expected maximum HDU ver.
    """

    max_ver = None

    def _check_value(self, *args, **keys):
        return True

    def check_header(self, filename, header):
        """Evalutate the header expression associated with this validator (as its sole value)
        with respect to the given `header`.  Read `header` from `filename` if `header` is None.
        """
        array_name = self.complex_name
        max_ver = 0
        with data_file.fits_open(filename) as hdus:
            first = dict()
            for hdu in hdus:
                if hdu.name != self.name:
                    continue
                self.verbose(filename, "ver=" + str(hdu.ver),
                             "Array has shape=" + str(hdu.data.shape),
                             "and dtype=" + repr(str(hdu.data.dtype)) + ".")
                if hdu.name not in first:
                    first[hdu.name] = (hdu.data.shape, hdu.data.dtype)
                else:
                    expected = first[hdu.name][0]
                    got = hdu.data.shape
                    assert expected == got, \
                        "Shape mismtatch for " + repr((hdu.name, hdu.ver)) + \
                        "relative to" + repr((self.name,1)) + ". Expected " + \
                        str(expected) + " but got " + str(got) + "."
                    expected = first[hdu.name][1]
                    got = hdu.data.dtype
                    assert expected == got, \
                        "Data type mismtatch for " + \
                        repr((hdu.name,hdu.ver)) + \
                        " relative to " + repr((self.name,1)) + \
                        ". Expected " + str(expected) + \
                        " but got " + str(got) + "."
                max_ver = hdu.ver
            if self.max_ver is not None:
                assert self.max_ver == max_ver, \
                    "Bad maximum HDU ver for " + repr(self.name) + \
                    ". Expected " +  str(self.max_ver) + \
                    ", got " + str(max_ver) + "."

class Isomorphicfitsver4Validator(IsomorphicfitsverValidator):
    max_ver = 4

class Isomorphicfitsver2Validator(IsomorphicfitsverValidator):
    max_ver = 2

class Isomorphicfitsver1Validator(IsomorphicfitsverValidator):
    max_ver = 1

# ----------------------------------------------------------------------------

class FileexistsValidator(Validator):
    """"""
    def _check_value(self, filename, value):
        """Verify that the file named `value` defined somewhere in certified
        file `filename` actually exists in CRDS.   This is useful for e.g.
        checking that a SYNPHOT TMC or TMT filename column value actually
        exists in CRDS.
        """
        observatory = utils.file_to_observatory(self.condition(filename))
        checked_path = config.locate_file(value, observatory)
        log.verbose("Checking file", repr(value), "for existence in CRDS cache.")
        if not os.path.exists(checked_path):
            raise ValueError("Required CRDS file " + repr(value) + " does not exist in CRDS cache.")

    def condition(self, value):
        crds_name = value
        if "$" in value: # remove IRAF-style path prefix from SYNPHOT TMC and TMT filename column values
            crds_name = crds_name.split("$")[-1]
        if "[" in value: # split off HDU index trailer,  or SYNPHOT parameterization trailer
            crds_name = crds_name.split("[")[0]
        log.verbose("Conditioned filepath", repr(value), "to", repr(crds_name))
        return crds_name
