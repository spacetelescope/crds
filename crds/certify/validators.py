"""This module defines replacement functionality for the CDBS "certify" program
used to check parameter values in .fits reference files.   It verifies that FITS
files define required parameters and that they have legal values.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

# ============================================================================

import os
import re
import copy

# ============================================================================

from crds.core import log, config, utils, timestamp, selectors
from crds.core.exceptions import MissingKeywordError, IllegalKeywordError
from crds.core.exceptions import TpnDefinitionError, RequiredConditionError
from crds import tables
from crds import data_file

from . import reftypes
from . import generic_tpn
from .generic_tpn import TpnInfo   # generic TpnInfo code

# ============================================================================

class Validator(object):
    """Validator is an Abstract class that applies TpnInfo objects to reference files.  Each
    Validator handles a single constraint defined in a .tpn file.
    """
    def __init__(self, info):
        self.info = info
        self.name = info.name
        self._presence_condition_code = None

        if not (self.info.presence in ["R", "P", "E", "O", "W"] or
                self.conditionally_required):
            raise ValueError("Bad TPN presence field " + repr(self.info.presence))

        if not hasattr(self.__class__, "_values"):
            self._values = self.condition_values(
                [val for val in info.values if not val.upper().startswith("NOT_")])
            self._not_values = self.condition_values(
                [val[4:] for val in info.values if val.upper().startswith("NOT_")])

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

    def check(self, filename, header=None):
        """Pull the value(s) corresponding to this Validator out of it's
        `header` or the contents of the file.   Check them against the
        requirements defined by this Validator.
        """
        if self.info.keytype == "C":
            return self.check_column(filename)
        elif self.info.keytype == "G":
            return self.check_group(filename)

        if header is None:
            header = data_file.get_header(filename)

        if not self.is_applicable(header):
            return True

        if self.info.keytype == "H":
            return self.check_header(filename, header)
        elif self.info.keytype == "X":
            return self.check_header(filename, header)
        else:
            raise ValueError("Unknown TPN keytype " + repr(self.info.keytype) + 
                             " for " + repr(self.name))

    def check_value(self, filename, value):
        """Check a single header or column value against the legal values
        for this Validator.
        """
        if value is None: # missing optional or excluded keyword
            self.verbose(filename, value, "is optional or excluded.")
            return True
        if self.condition is not None:  # verify type regardless of values.
            value = self.condition(value)
        if not (self._values or self._not_values):
            self.verbose(filename, value, "no .tpn values defined.")
            return True
        self._check_value(filename, value)
        # If no exception was raised, consider it validated successfully
        return True

    def _check_value(self, filename, value):
        """_check_value is the core simple value checker."""
        raise NotImplementedError(
            "Validator is an abstract class.  Sub-class and define _check_value().")
    
    def check_header(self, filename, header):
        """Extract the value for this Validator's keyname,  either from `header`
        or from `filename`'s header if header is None.   Check the value.
        """
        value = self._get_header_value(header)
        return self.check_value(filename, value)

    def check_column(self, filename):
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
            self.__handle_missing()
        else:
            self.__handle_excluded(None)
        return True
        
    def check_group(self, _filename):
        """Probably related to pre-FITS HST GEIS files,  not implemented."""
        log.warning("Group keys are not currently supported by CRDS.")

    def _get_header_value(self, header):
        """Pull this Validator's value out of `header` and return it.
        Handle the cases where the value is missing or excluded.
        """
        try:
            value = header[self.name]
            assert value != "UNDEFINED", "Undefined keyword " + repr(self.name)
        except (KeyError, AssertionError):
            return self.__handle_missing()
        return self.__handle_excluded(value)

    def __handle_missing(self):
        """This Validator's key is missing.   Either raise an exception or
        ignore it depending on whether this Validator's key is required.
        """
        if self.info.presence in ["R","P"]:
            raise MissingKeywordError("Missing required keyword " + repr(self.name))
        elif self.info.presence in ["W"]:
            log.warning("Missing suggested keyword " + repr(self.name))
        elif self.info.presence in ["O"]:
            # sys.exc_clear()
            log.verbose("Optional parameter " + repr(self.name) + " is missing.")
            return # missing value is None, so let's be explicit about the return value
        else:
            raise TpnDefinitionError("Unexpected validator 'presence' value:",
                                     log.srepr(self.info.presence))

    def __handle_excluded(self, value):
        """If this Validator's key is excluded,  raise an exception.  Otherwise
        return `value`.
        """
        if self.info.presence == "E":
            raise IllegalKeywordError("*Must not define* keyword " + repr(self.name))
        return value

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
        if has_condition and not self._presence_condition_code:
            self._presence_condition_code = compile(self.info.presence, repr(self.info), "eval")
            return True
        else:
            return False

    def is_applicable(self, header):
        """Return True IFF the conditional presence expression for this validator,  not always
        defined,  returns False indicating that the validator is not applicable to the situation
        defined by `header`.
        """
        if self._presence_condition_code:
            required = eval(self._presence_condition_code, header, header)
            log.verbose("Validator", self.info, "is",
                        "applicable" if required else "not applicable",
                        "based on condition", self.info.presence,
                        verbosity=70)
            return required
        else:
            return True

    def get_required_copy(self):
        """Return a copy of this validator with self.presence overridden to R/required."""
        required = copy.deepcopy(self)
        idict = required.info._asdict()  # returns OrderedDict,  method is public despite _
        idict["presence"] = "R"
        required.info = TpnInfo(*idict.values())
        return required
    
# ----------------------------------------------------------------------------

class KeywordValidator(Validator):
    """Checks that a value is one of the literal TpnInfo values."""

    def _check_value(self, filename, value):
        """Raises ValueError if `value` is not valid."""
        if self._match_value(value):
            if self._values:
                self.verbose(filename, value, "is in", repr(self._values))
        else:
            raise ValueError("Value " + str(log.PP(value)) + " is not one of " +
                             str(log.PP(self._values)))    
        if self._not_match_value(value):
            raise ValueError("Value " + str(log.PP(value)) + " is disallowed.")
    
    def _match_value(self, value):
        """Do a literal match of `value` to the allowed values of this tpninfo."""
        return value in self._values or not self._values
    
    def _not_match_value(self, value):
        """Do a literal match of `value` to the disallowed values of this tpninfo."""
        return value in self._not_values
    
# ----------------------------------------------------------------------------

class RegexValidator(KeywordValidator):
    """Checks that a value matches TpnInfo values treated as regexes."""
    def _match_value(self, value):
        if super(RegexValidator, self)._match_value(value):
            return True
        sval = str(value)
        for pat in self._values:
            if re.match(config.complete_re(pat), sval):
                return True
        return False

# ----------------------------------------------------------------------------

class CharacterValidator(KeywordValidator):
    """Validates values of type Character."""
    def condition(self, value):
        chars = str(value).strip().upper()
        if " " in chars:
            chars = '"' + "_".join(chars.split()) + '"'
        return chars

    def _check_value(self, filename, value):
        if selectors.esoteric_key(value):
            values = [value]
        else:
            values = value.split("|") 
            if len(values) > 1:
                self.verbose(filename, value, "is an or'ed parameter matching", values)
        for val in values:
            super(CharacterValidator, self)._check_value(filename, val)

# ----------------------------------------------------------------------------

class LogicalValidator(KeywordValidator):
    """Validate booleans."""
    _values = ["T","F"]
    _not_values = []

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
            else:
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

    def _check_value(self, filename, value):
        try:
            NumericalValidator._check_value(self, filename, value)
        except ValueError:   # not a range or exact match,  handle fp fuzz
            if self.is_range: # XXX bug: boundary values don't handle fuzz
                raise
            for possible in self._values:
                if possible:
                    err = (value-possible)/possible
                elif value:
                    err = (value-possible)/value
                else:
                    continue
                # print "considering", possible, value, err
                if abs(err) < self.epsilon:
                    self.verbose(filename, value, "is within +-", repr(self.epsilon), 
                                 "of", repr(possible))
                    return
            raise

# ----------------------------------------------------------------------------

class RealValidator(FloatValidator):
    """Validate 32-bit floats."""

# ----------------------------------------------------------------------------

class DoubleValidator(FloatValidator):
    """Validate 64-bit floats."""
    epsilon = 1e-14

# ----------------------------------------------------------------------------

class PedigreeValidator(KeywordValidator):
    """Validates &PREDIGREE fields."""

    _values = ["INFLIGHT", "GROUND", "MODEL", "DUMMY", "SIMULATION"]
    _not_values = []

    def _get_header_value(self, header):
        """Extract the PEDIGREE value from header,  checking any
        start/stop dates.   Return only the PEDIGREE classification.
        Ignore missing start/stop dates.
        """
        value = super(PedigreeValidator, self)._get_header_value(header)
        if value is None:
            return
        try:
            pedigree, start, stop = value.split()
        except ValueError:
            try:
                pedigree, start, _dash, stop = value.split()
            except ValueError:
                pedigree = value
                start = stop = None
        pedigree = pedigree.upper()
        if start is not None:
            timestamp.slashdate_or_dashdate(start)
        if stop is not None:
            timestamp.slashdate_or_dashdate(stop)
        return pedigree

    def _match_value(self, value):
        """Match raw pattern as prefix string only,  no complete_re()."""
        sval = str(value)
        for pat in self._values:
            if re.match(pat, sval):   # intentionally NOT complete_re()
                return True
        return False

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
        try:
            timestamp.Jwstdate.get_datetime(value)
        except Exception:
            raise ValueError(log.format(
                "Invalid JWST date", repr(value), "for", repr(self.name),
                "format should be", repr("YYYY-MM-DDTHH:MM:SS")))
            
'''
        try:
            timestamp.Jwstdate.get_datetime(value)
        except ValueError:
            try:
                timestamp.Anydate.get_datetime(value)
            except ValueError:
                try:
                    timestamp.Jwstdate.get_datetime(value.replace(" ","T"))
                except ValueError:
                    timestamp.Jwstdate.get_datetime(value)                    
            log.warning("Non-compliant date format", repr(value), "for", repr(self.name),
                        "should be", repr("YYYY-MM-DDTHH:MM:SS"),)
'''

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

class FilenameValidator(KeywordValidator):
    """Validates &FILENAME fields."""
    def _check_value(self, filename, value):
        self.verbose(filename, value)
        result = (value == "(initial)") or not os.path.dirname(value)
        return result

# ----------------------------------------------------------------------------

class ExpressionValidator(Validator):
    """Value is an expression on the reference header that must evaluate to True."""

    def __init__(self, info, *args, **keys):
        super(ExpressionValidator, self).__init__(info, *args, **keys)
        self._expr = info.values[0]
        self._expr_code = compile(self._expr, repr(self.info), "eval")

    def _check_value(self, *args, **keys):
        """If this validator is inadvertantly executed... no point in failing.  Design
        intent is to *only* execute check_header().
        """
        return True

    def check_header(self, filename, header):
        """Evalutate the header expression associated with this validator (as its sole value)
        with respect to the given `header`.  Read `header` from `filename` if `header` is None.
        """
        header = data_file.convert_to_eval_header(header)
        log.verbose("Checking", repr(filename), "for condition", repr(self._expr))
        is_true = False
        with log.verbose_warning_on_exception(
            "Failed evaluating condition expression", repr(self._expr)):
            is_true = eval(self._expr_code, header, header)
        if not is_true:
            raise RequiredConditionError(
                "Required condition", repr(self._expr), "failed to evaluate or is not satisfied.")

# ----------------------------------------------------------------------------

def validator(info):
    """Given TpnInfo object `info`, construct and return a Validator for it."""
    if info.datatype == "C":
        if len(info.values) == 1 and len(info.values[0]) and \
            info.values[0][0] == "&":
            # This block handles &-types like &PEDIGREE and &SYBDATE
            # only called on static TPN infos.
            func = eval(info.values[0][1:].capitalize() + "Validator")
            rval = func(info)
        else:
            rval = CharacterValidator(info)
    elif info.datatype == "R":
        rval = RealValidator(info)
    elif info.datatype == "D":
        rval = DoubleValidator(info)
    elif info.datatype == "I":
        rval = IntValidator(info)
    elif info.datatype == "L":
        rval = LogicalValidator(info)
    elif info.datatype == "Z":
        rval = RegexValidator(info)
    elif info.datatype == "X":
        rval = ExpressionValidator(info)
    else:
        raise ValueError("Unimplemented datatype " + repr(info.datatype))
    return rval

# ============================================================================

def get_validators(observatory, refpath):
    """Given `observatory` and a path to a reference file `refpath`,  load the
    corresponding validators that define individual constraints that reference
    should satisfy.
    """
    types = reftypes.get_types_object(observatory)
    locator = utils.get_locator_module(observatory)
    checkers = []
    for key in types.reference_name_to_validator_keys(refpath):
        validators_for_keys = [validator(x) for x in locator.get_tpninfos(*key)]
        checkers.extend(validators_for_keys)
    log.verbose("Validators for", repr(refpath), ":\n", log.PP(checkers), verbosity=60)
    return checkers

