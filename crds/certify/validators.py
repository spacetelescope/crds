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

import numpy as np

# ============================================================================

from crds.core import log, utils, timestamp, selectors
from crds.core.exceptions import MissingKeywordError, IllegalKeywordError
from crds.core.exceptions import TpnDefinitionError, RequiredConditionError
from crds.core.exceptions import BadKernelSumError
from crds.io import tables
from crds import data_file

from . import generic_tpn
from .generic_tpn import TpnInfo   # generic TpnInfo code
from .validator_helpers import *

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

class Validator(object):
    """Validator is an Abstract class that applies TpnInfo objects to reference files.  Each
    Validator handles a single constraint defined in a .tpn file.
    """
    def __init__(self, info):
        self.info = info
        self.name = info.name
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

    def check(self, filename, header=None):
        """Pull the value(s) corresponding to this Validator out of it's
        `header` or the contents of the file.   Check them against the
        requirements defined by this Validator.
        """
        if header is None:
            header = data_file.get_header(filename)

        if not self.is_applicable(header):
            return True
        
        if self.info.keytype == "C":
            return self.check_column(filename)
        elif self.info.keytype == "G":
            return self.check_group(filename)
        elif self.info.keytype in ["H","X","A","D"]:
            return self.check_header(filename, header)
        else:
            raise ValueError("Unknown TPN keytype " + repr(self.info.keytype) + 
                             " for " + repr(self.name))

    def check_header(self, filename, header):
        """Extract the value for this Validator's keyname,  either from `header`
        or from `filename`'s header if header is None.   Check the value.
        """
        value = self.get_header_value(header)
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
            self._handle_missing()
        return True
        
    def check_group(self, _filename):
        """Probably related to pre-FITS HST GEIS files,  not implemented."""
        log.warning("Group keys are not currently supported by CRDS.")

    def get_header_value(self, header):
        """Pull this Validator's value out of `header` and return it.
        Handle the cases where the value is missing or excluded.
        """
        value = header.get(self.complex_name, "UNDEFINED")
        if value in [None, "UNDEFINED"]:
            return self._handle_missing(header)
        elif self.info.presence == "E":
            raise IllegalKeywordError("*Must not define* keyword " + repr(self.name))
        return value
    
    def _handle_missing(self, header=None):
        """This Validator's key is missing.   Either raise an exception or
        ignore it depending on whether this Validator's key is required.
        """
        if self.info.presence in ["R","P"]:
            raise MissingKeywordError("Missing required keyword " + repr(self.name))
        elif self.info.presence in ["W"]:
            log.warning("Missing suggested keyword " + repr(self.name))
            return "UNDEFINED"
        elif self.info.presence in ["O"]:
            log.verbose("Optional parameter " + repr(self.name) + " is missing.", verbosity=70)
            return "UNDEFINED"
        elif self.info.presence in ["S","F","A"]:
            log.verbose("Conditional SUBARRAY parameter is not defined.")
            return "UNDEFINED"
        elif self.conditionally_required:
            if header and self.is_applicable(header):
                raise MissingKeywordError("Missing keyword", repr(self.name), 
                                           "required by condition", self.info.presence)
            else:
                return "UNDEFINED"
        else:
            raise TpnDefinitionError("Unexpected validator 'presence' value:",
                                     repr(self.info.presence))

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
        """Return True IFF the conditional presence expression for this validator,  not always
        defined,  returns False indicating that the validator is not applicable to the situation
        defined by `header`.
        """
        SUBARRAY = header.get('SUBARRAY','UNDEFINED')
        if self._presence_condition_code:
            try:
                required = eval(self._presence_condition_code, header, dict(globals()))
                log.verbose("Validator", self.info, "is",
                            "applicable." if required else "not applicable.", verbosity=70)
            except Exception as exc:
                log.warning("Failed checking applicability of", repr(self.info),"skipping check : ", str(exc))
                required = False
            return required
        if self.info.presence == "F": # IF_FULL_FRAME
            return is_full_frame(SUBARRAY)
        elif self.info.presence == "S": # IF_SUBARRAY        
            return is_subarray(SUBARRAY)
        elif self.info.presence == "A":
            return subarray_defined(header)
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
                    err = value
                else:
                    err = 0
                if abs(err) < self.epsilon and log.get_verbose():
                     self.verbose(filename, value, "is within +-", repr(self.epsilon), 
                                  "of", repr(possible))
                     return
            raise ValueError("Float", repr(value), "is not within +-", repr(self.epsilon), 
                            "of any of", repr(self._values))
 
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

    def _check_value(self, filename, value):
        """Check `value` as a PEDIGREE."""
        values = value.split()
        if len(values) not in [1, 3, 4]:
            raise ValueError("Invalid PEDIGREE format: " + repr(value))
        try:
            pedigree, start, stop = values
        except ValueError:
            try:
                pedigree, start, _dash, stop = values
            except ValueError:
                pedigree = value
                start = stop = None
        pedigree = pedigree.upper()
        if start is not None and stop is not None:
            if "T" in start+stop:  # can't appear in either string
                raise ValueError("Invalid PEDIGREE format: " + repr(value))
            start_dt = timestamp.slashdate_or_dashdate(start)
            stop_dt = timestamp.slashdate_or_dashdate(stop)
            if not (start_dt <= stop_dt):
                raise ValueError("PEDIGREE date order invalid: " + repr(start) + " > " + repr(stop))
        # else:
        #     if pedigree == "INFLIGHT":
        #         raise ValueError("INFLIGHT PEDIGREE must supply start and end dates, e.g. INFLIGHT 2017-01-01 2017-01-15")
        return super(PedigreeValidator, self)._check_value(filename, pedigree)

#     def _match_value(self, value):
#         """Match raw pattern as prefix string only,  no complete_re()."""
#         sval = str(value)
#         for pat in self._values:
#             if re.match(pat, sval):   # intentionally NOT complete_re()
#                 return True
#         return False

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
        with respect to the given `header`.  Read `header` from `filename` if `header` is None.
        """
        # super(ExpressionValidator, self).check_header(filename, header)
        header = data_file.convert_to_eval_header(header)
        if self.info.keytype in ["A","D"] and header.get(self.complex_name, "UNDEFINED") == "UNDEFINED":
            log.verbose_warning("Array", repr(self.name),
                "is undefined.  Skipping check", str(self._expr))
            return
        log.verbose("File=" + repr(os.path.basename(filename)), "Checking",
                    repr(self.name), "condition", str(self._expr))
        try:
            satisfied = eval(self._expr_code, header, dict(globals()))
        except Exception as exc:
            raise RequiredConditionError("Failed checking condition", repr(self._expr), ":", str(exc))
        if not satisfied:
            raise RequiredConditionError("Condition", str(self._expr), "is not satisfied.")
        return satisfied
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
                    images_data[0].shape, "for individual sums of 1+-1e-6.")
        for (i, image) in enumerate(images_data):
            if abs(image.sum()-1.0) > 1.0e-6:
                raise BadKernelSumError("Kernel sum", image.sum(),
                    "is not 1+-1e-6 for kernel #" + str(i), ":", repr(image))    

# ----------------------------------------------------------------------------

def validator(info):
    """Given TpnInfo object `info`, construct and return a Validator for it."""
    if len(info.values) == 1 and len(info.values[0]) and \
        info.values[0][0] == "&":
        # This block handles &-types like &PEDIGREE and &SYBDATE
        # only called on static TPN infos.
        class_name = info.values[0][1:].capitalize() + "Validator"
        rval = eval(class_name)(info)
    elif info.datatype == "C":
        rval = CharacterValidator(info)
    elif info.datatype == "R":
        rval = RealValidator(info)
    elif info.datatype == "D":
        rval = DoubleValidator(info)
    elif info.datatype == "I":
        rval = IntValidator(info)
    elif info.datatype == "L":
        rval = LogicalValidator(info)
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
    tpns = get_reffile_tpninfos(observatory, refpath)
    checkers = [validator(x) for x in tpns]
    log.verbose("Validators for", repr(refpath), "("+str(len(checkers))+"):\n", log.PP(checkers), verbosity=65)
    return checkers

def get_reffile_tpninfos(observatory, refpath):
    """Load just the TpnInfo objects for `observatory` and the given `refpath`.
    This entails both "class" TpnInfo's from CDBS as well as TpnInfo objects
    derived from the JWST data models.
    """
    locator = utils.get_locator_module(observatory)
    instrument, filekind = locator.get_file_properties(refpath)
    tpns = list(locator.get_all_tpninfos(instrument, filekind, "tpn"))
    tpns.extend(locator.get_extra_tpninfos(refpath))
    return tpns

