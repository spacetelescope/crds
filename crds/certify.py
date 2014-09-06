"""This module defines replacement functionality for the CDBS "certify" program
used to check parameter values in .fits reference files.   It verifies that FITS
files define required parameters and that they have legal values.
"""
import sys
import os
import re
import json
from collections import defaultdict, namedtuple

from astropy.io import fits as pyfits
import numpy as np

from crds import rmap, log, timestamp, utils, data_file, diff, cmdline, config
from crds import client
from crds import mapping_parser
from crds.rmap import ValidationError

NOT_FITS = -1
VALID_FITS = 1

# ============================================================================

#
# Only the first character of the field is stored, i.e. Header == H
#
# name = field identifier
# keytype = (Header|Group|Column)
# datatype = (Integer|Real|Logical|Double|Character)
# presence = (Optional|Required)
# values = [...]
#
TpnInfo = namedtuple("TpnInfo", "name,keytype,datatype,presence,values")

# ============================================================================

class MissingKeywordError(Exception):
    """A required keyword was not defined."""

class IllegalKeywordError(Exception):
    """A keyword which should not be defined was present."""

class InvalidFormatError(Exception):
    """The given file was not loadable."""

# ----------------------------------------------------------------------------
class Validator(object):
    """Validator is an Abstract class which applies TpnInfo objects to reference files.
    """
    def __init__(self, info):
        self.info = info
        self.name = info.name
        if self.info.presence not in ["R", "P", "E", "O"]:
            raise ValueError("Bad TPN presence field " + repr(self.info.presence))
        if not hasattr(self.__class__, "_values"):
            self._values = self.condition_values(info)

    def verbose(self, filename, value, *args, **keys):
        """Prefix log.verbose() with standard info about this Validator.  Unique message is in *args, **keys"""
        return log.verbose("File=" + repr(filename), 
                           "Class=" + repr(self.__class__.__name__[:-len("Validator")]), 
                           "keyword=" + repr(self.name), 
                           "value =" + repr(value), 
                           *args, **keys)

    def condition(self, value):
        """Condition `value` to standard format for this Validator."""
        return value

    def condition_values(self, info):
        return [self.condition(value) for value in info.values]

    def __repr__(self):
        return self.__class__.__name__ + "(" + repr(self.info) + ")"

    def check(self, filename, header=None):
        """Pull the value(s) corresponding to this Validator out of it's
        `header` or the contents of the file.   Check them against the
        requirements defined by this Validator.
        """
        if self.info.keytype == "H":
            return self.check_header(filename, header)
        elif self.info.keytype == "C":
            return self.check_column(filename)
        elif self.info.keytype == "G":
            return self.check_group(filename)
        else:
            raise ValueError("Unknown TPN keytype " + repr(self.info.keytype) + " for " + repr(self.name))

    def check_value(self, filename, value):
        """Check a single header or column value against the legal values
        for this Validator.
        """
        if value is None: # missing optional or excluded keyword
            self.verbose(filename, value, "is optional or excluded.")
            return True
        if self.condition is not None:
            value = self.condition(value)
        if not self._values:
            self.verbose(filename, value, "no .tpn values defined.")
            return True
        self._check_value(filename, value)
        # If no exception was raised, consider it validated successfully
        return True
    
    def _check_value(self, filename, value):
        raise NotImplementedError("Validator is an abstract class.  Sub-class and define _check_value().")
    
    def check_header(self, filename, header=None):
        """Extract the value for this Validator's keyname,  either from `header`
        or from `filename`'s header if header is None.   Check the value.
        """
        if header is None:
            header = data_file.get_header(filename)
        value = self._get_header_value(header)
        return self.check_value(filename, value)

    def check_column(self, filename, context=None):
        """Extract a column of new_values from `filename` and check them all against
        the legal values for this Validator.   This checks a single column,  not a row/mode.
        """
        try:
            new_values = self.get_column_values(filename)
            if new_values is None: # Ignore missing optional columns
                return True 
        except Exception, exc:
            log.error("Can't read column values:", str(exc))
            return False

        # new_values must not be None,  check all, waiting to fail later
        ok = True
        for i, value in enumerate(new_values): # compare to TPN values
            try:
                self.check_value(filename + "[" + str(i) +"]", value)
            except ValueError, exc:
                ok = False 
        return ok
        
    def check_group(self, _filename):
        """Probably related to pre-FITS HST GEIS files,  not implemented."""
        assert False, "Group keys are not currently supported by CRDS."

    def _get_header_value(self, header):
        """Pull this Validator's value out of `header` and return it.
        Handle the cases where the value is missing or excluded.
        """
        try:
            value = header[self.name]
        except KeyError:
            return self.__handle_missing()
        return self.__handle_excluded(value)

    def get_column_values(self, filename):
        """Pull the column of values corresponding to this Validator out of
        `filename` and return it.   Handle missing and excluded cases.
        """
        hdu = pyfits.open(filename)
        
        # make sure table(s) are in extension(s) not the PRIMARY extension
        assert len(hdu) > 1, "table file with only primary extension: " + repr(filename)

        # start by finding the extension which contains the requested column
        for extn in hdu:
            if (hasattr(extn,'_extension') and 'table' in extn._extension.lower() and self.name in extn.data.names):
                col_extn = extn
                break
        else:  # If no extension could be found with that column, report as missing
            hdu.close()
            return self.__handle_missing()

        # If it was found, return the values
        values = col_extn.data.field(self.name)
        hdu.close()
        return self.__handle_excluded(values)

    def __handle_missing(self):
        """This Validator's key is missing.   Either raise an exception or
        ignore it depending on whether this Validator's key is required.
        """
        if self.info.presence in ["R","P"]:
            raise MissingKeywordError("Missing required keyword " + repr(self.name))
        else:
            sys.exc_clear()
            return # missing value is None, so let's be explicit about the return value

    def __handle_excluded(self, value):
        """If this Validator's key is excluded,  raise an exception.  Otherwise
        return `value`.
        """
        if self.info.presence == "E":
            raise IllegalKeywordError("*Must not define* keyword " + repr(self.name))
        return value


class KeywordValidator(Validator):
    """Checks that a value is one of the literal TpnInfo values."""

    def _check_value(self, filename, value):
        """Raises ValueError if `value` is not valid."""
        if value not in self._values:  # and tuple(self._values) != ('*',):
            if isinstance(value, str):
                for pat in self._values:
                    if re.match(pat, value):
                        self.verbose(filename, value, "matches", repr(pat))
                        return
            raise ValueError("Value for " + repr(self.name) + " of " +
                            str(log.PP(value)) + " is not one of " +
                            str(log.PP(self._values)))
        else:
            self.verbose(filename, value, "is in", repr(self._values))

# ----------------------------------------------------------------------------

class CharacterValidator(KeywordValidator):
    """Validates values of type Character."""
    def condition(self, value):
        chars = str(value).strip().upper()
        if " " in chars:
            chars = '"' + "_".join(chars.split()) + '"'
        return chars

# ----------------------------------------------------------------------------

class LogicalValidator(KeywordValidator):
    """Validate booleans."""
    _values = ["T","F"]

# ----------------------------------------------------------------------------

class NumericalValidator(KeywordValidator):
    """Check the value of a numerical keyword,  supporting range checking."""
    def condition_values(self, info):
        self.is_range = len(info.values) == 1 and ":" in info.values[0]
        if self.is_range:
            smin, smax = info.values[0].split(":")
            self.min, self.max = self.condition(smin), self.condition(smax)
            assert self.min != '*' and self.max != '*', "TPN error, range min/max conditioned to '*'"
            values = None
        else:
            values = KeywordValidator.condition_values(self, info)
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
                    self.verbose(filename, value, "is within +-", repr(self.epsilon), "of", repr(possible))
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
    _values = ["INFLIGHT", "GROUND", "MODEL", "DUMMY"]

    def _get_header_value(self, header):
        """Extract the PEDIGREE value from header,  checking any
        start/stop dates.   Return only the PEDIGREE classification.
        Ignore missing start/stop dates.
        """
        value = KeywordValidator._get_header_value(self, header)
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
            timestamp.Slashdate.get_datetime(start)
        if stop is not None:
            timestamp.Slashdate.get_datetime(stop)
        return pedigree

# ----------------------------------------------------------------------------

class SybdateValidator(KeywordValidator):
    """Check &SYBDATE Sybase date fields."""
    def check_value(self, filename, value):
        self.verbose(filename, value)
        timestamp.Sybdate.get_datetime(value)

# ----------------------------------------------------------------------------

class SlashdateValidator(KeywordValidator):
    """Validates &SLASHDATE fields."""
    def check_value(self, filename, value):
        self.verbose(filename, value)
        timestamp.Slashdate.get_datetime(value)

# ----------------------------------------------------------------------------

class AnydateValidator(KeywordValidator):
    """Validates &ANYDATE fields."""
    def check_value(self, filename, value):
        self.verbose(filename, value)
        timestamp.Anydate.get_datetime(value)

# ----------------------------------------------------------------------------

class FilenameValidator(KeywordValidator):
    """Validates &FILENAME fields."""
    def check_value(self, filename, value):
        self.verbose(filename, value)
        result = (value == "(initial)") or not os.path.dirname(value)
        return result

# ----------------------------------------------------------------------------

def validator(info):
    """Given TpnInfo object `info`, construct and return a Validator for it."""
    if info.datatype == "C":
        if len(info.values) == 1 and len(info.values[0]) and \
            info.values[0][0] == "&":
            # This block handles &-types like &PEDIGREE and &SYBDATE
            func = eval(info.values[0][1:].capitalize() + "Validator")  # only called on static TPN infos.
            return func(info)
        else:
            return CharacterValidator(info)
    elif info.datatype == "R":
        return RealValidator(info)
    elif info.datatype == "D":
        return DoubleValidator(info)
    elif info.datatype == "I":
        return IntValidator(info)
    elif info.datatype == "L":
        return LogicalValidator(info)
    else:
        raise ValueError("Unimplemented datatype " + repr(info.datatype))

# ============================================================================

def get_validators(filename, observatory):
    """Given a reference file `filename`,  return the observatory specific
    list of Validators used to check that reference file type.
    """
    locator = utils.get_locator_module(observatory)
    # Get the cache key for this filetype.
    key = locator.reference_name_to_validator_key(filename)
    return validators_by_typekey(key, observatory)

@utils.cached
def validators_by_typekey(key, observatory):
    """Load and return the list of validators associated with reference type 
    validator `key`.   Factored out because it is cached on parameters.
    """
    locator = utils.get_locator_module(observatory)
    # Make and cache Validators for `filename`s reference file type.
    try:
        validators = [validator(x) for x in locator.get_tpninfos(*key)]
        log.verbose("Validators for", repr(key), "=", log.PP(validators))
    except Exception, exc:
        raise RuntimeError("FAILED loading type contraints for " + repr(key) + " with " + repr(exc))
    return validators

# ============================================================================

class Certifier(object):
    """Container class for parameters for a certification run."""
    def __init__(self, filename, context=None, trap_exceptions=False, check_references=False, 
                 compare_old_reference=False, dump_provenance=False,
                 provenance_keys=("DESCRIP", "COMMENT", "PEDIGREE", "USEAFTER","HISTORY",),
                 dont_parse=False, script=None, observatory=None, comparison_reference=None):
        
        self.filename = filename
        self.context = context
        self.trap_exceptions = trap_exceptions
        self.check_references = check_references
        self.compare_old_reference = compare_old_reference
        self.dump_provenance = dump_provenance
        self.provenance_keys = list(provenance_keys)
        self.dont_parse = dont_parse     # mapping only
        self.script = script
        self.observatory = observatory
        self.comparison_reference = comparison_reference
    
        assert self.check_references in [False, None, "exist", "contents"], \
            "invalid check_references parameter " + repr(self.check_references)
        assert not comparison_reference or context, \
            "specifying a comparison reference also requires a comparison context."
    
    @property
    def basename(self):
        return os.path.basename(self.filename)

    def trap(self, message, function, *args, **keys):
        """Execute function(*args, **keys) and log.error(message) on any exception 
        if self.trap_exception is True,  otherwise re-raise the exception as a
        CrdsError.
        """
        try:
            return function(*args, **keys)
        except Exception, exc:
            msg = message + " : " + str(exc)
            if self.trap_exceptions:
                self.log_error(msg)
                return None
            else:
                self.log_error(msg)
                raise
                # raise ValidationError(msg)

    def log_error(self, msg):
        """Output a log error on behalf of `msg`,  tracking it for uniqueness if run inside a script."""
        if self.script:
            try:
                instrument, filekind = utils.get_file_properties(self.script.observatory, self.filename)
            except Exception:
                instrument = filekind = "unknown"
            self.script.log_and_track_error(self.filename, instrument, filekind, msg)
        else:
            log.error("In", repr(self.filename), ":", msg)
            
    def certify(self):
        """Certify `self.filename`,  either reporting using log.error() or raising
        ValidationError exceptions.
        """
        raise NotImplementedError("Certify is an abstract class.")
# ============================================================================

class FitsCertifier(Certifier):
    """Support certifying reference files:
    
    1. Check simple keywords against TPN files using the reftype's validators.
    2. Check mode tables against prior reference of comparison_context.
    3. Dump out keywords of interest.
    """
    def __init__(self, *args, **keys):
        super(FitsCertifier, self).__init__(*args, **keys)
        self.simple_validators = get_validators(self.filename, self.observatory)
        self.all_column_names = [ val.name for val in self.simple_validators if val.info.keytype == 'C' ]
        self.basefile = os.path.basename(self.filename)
        self.mode_columns = self.get_mode_column_names()

    def certify(self):
        """Certify a FITS reference file."""
        if not self.trap("File does not comply with FITS format", self.fits_verify):
            return
        self.certify_simple_parameters()
        if self.mode_columns:
            self.certify_reference_modes()
        if self.dump_provenance:
            dump_multi_key(self.filename, self.get_rmap_parkeys() + self.provenance_keys, 
                           self.provenance_keys)

    def fits_verify(self):
        """Use pyfits to verify the FITS format of self.filename."""
        if not self.filename.endswith(".fits"):
            log.verbose("Skipping FITS verify for '%s'" % self.basefile)
            return
        fits = pyfits.open(self.filename)
        fits.verify(option='exception') # validates all keywords
        fits.close()
        log.info("FITS file", repr(self.basename), " conforms to FITS standards.")
        return True

    def get_rmap_parkeys(self):
        """Determine required parkeys in reference path `refname` according to pipeline
        mapping `context`.
        """
        if self.context is None:
            return []
        try:
            pmap = rmap.get_cached_mapping(self.context, ignore_checksum="warn")
            instrument, filekind = pmap.locate.get_file_properties(self.filename)
            return pmap.get_imap(instrument).get_rmap(filekind).get_required_parkeys()
        except Exception, exc:
            log.verbose_warning("Failed retrieving required parkeys:", str(exc))
            return []

    def certify_simple_parameters(self):
        """Check simple parameter values,  column and non-column."""
        header = data_file.get_header(self.filename)
        for checker in self.simple_validators:
            self.trap("checking " + repr(checker.info.name), checker.check, self.filename, header)

    def get_mode_column_names(self):
        """Return any column names of `self` defined to be mode columns by the corresponding rmap in `self.context`.
        
        Only tables whose rmaps define row_keys will have mode checking performed.
        """
        if not self.context:
            log.info("Table mode checking requires a comparison context.   Skipping.")
            return []
        mode_columns = []
        with log.error_on_exception("Error finding governing rmap for", repr(self.basefile), 
                                    "under", repr(self.context)):
            g_rmap = find_governing_rmap(self.context, self.filename)
            try:
                if g_rmap.reffile_format != "table":
                    log.info("Rmap reffile_format is not 'TABLE',  skipping table mode checks.")
                    return []
            except:
                log.warning("Rmap reffile_format NOT DEFINED,  assuming it's a table.")
            try:   # get_row_keys should return [] to suppress mode checks,  otherwise mode columns.
                mode_columns = g_rmap.locate.get_row_keys(g_rmap)
                log.info("Table unique-row-keys defined as", repr(mode_columns))
            except:
                log.warning("Table unique-row-keys for", repr(g_rmap.basename), "for", repr(self.filename), "NOT DEFINED. Skipping table mode checks.")
        return mode_columns
            
    def certify_reference_modes(self):
        """Check column parameters row-by-row, using mode groups."""
        if self.comparison_reference:
            old_reference = self.comparison_reference
        else:
            old_reference = self.find_old_reference(self.context, self.filename)
            if old_reference is None or old_reference == self.basefile:
                # Load table modes anyway,  looking for duplicate modes.
                _new_modes, _new_all_cols = table_mode_dictionary(
                    "new reference", self.filename, self.mode_columns)
                log.warning("No comparison reference for", repr(self.basefile), 
                            "in context", repr(self.context) + ". Skipping table comparison.")
                return
        n_old_hdus = len(pyfits.open(old_reference))
        n_new_hdus = len(pyfits.open(self.filename))
        if n_old_hdus != n_new_hdus:
            log.warning("Differing HDU counts in", repr(old_reference), "and", repr(self.basefile), ":",
                        n_old_hdus, "vs.", n_new_hdus)

        for i in range(1, min(n_new_hdus, n_old_hdus)):
            self.trap("checking table modes", self.check_table_modes, old_reference, ext=i)
    
    def find_old_reference(self, context, reffile):
        """Returns the name of the old reference file(s) that the new reffile would replace in `context`,  or None.
        """
        return self.trap("Resolving prior reference for '{}' in '{}'".format(reffile, context), 
                         self._find_old_reference, context, reffile) 
    
    def _find_old_reference(self, context, reffile):
        """Returns the name of the old reference file(s) that the new reffile would replace."""
        
        reference_mapping = find_governing_rmap(context, reffile)
        
        refname = os.path.basename(reffile)
        if refname in reference_mapping.reference_names():
            return refname
    
        # Determine the corresponding reference by attempting to add reffile to the old context.
        new_r = reference_mapping.insert_reference(reffile)
        
        # Examine the differences and treat the replaced file as the prior reference.
        diffs = reference_mapping.difference(new_r)
        match_refname = None
        for diff_tup in diffs:
            if diff.diff_action(diff_tup) == "replace":
                match_refname, dummy = diff.diff_replace_old_new(diff_tup)
                assert dummy == refname, "Bad replacement inserting '{}' into '{}'".format(reffile, reference_mapping.name)
                break   # XXX it may be possible to have more than one corresponding prior reference
        else:
            log.info("No file corresponding to", repr(reffile), "in context", repr(reference_mapping.name))
            return None
        
        # grab match_file from server and copy it to a local disk, if network
        # connection is available and configured properly
        # Note: this call works in both networked and non-networked modes of operation.
        # Non-networked mode requires access to /grp/crds/[hst|jwst] or a copy of it.
        try:
            match_files = client.dump_references(reference_mapping.name, baserefs=[match_refname], ignore_cache=False)
            match_file = match_files[match_refname]
            if not os.path.exists(match_file):   # For server-less mode in debug environments w/o Central Store
                raise IOError("Comparison reference " + repr(match_refname) + " is defined but does not exist.")
            log.info("Comparing reference", repr(refname), "against", repr(os.path.basename(match_file)))
        except Exception, exc:
            log.warning("Failed to obtain reference comparison file", repr(match_refname), ":", str(exc))
            match_file = None
    
        return match_file
    
    def check_table_modes(self, old_reference, ext):
        """Check the table modes of extension `ext` of `old_reference` versus self.filename"""
        ext_suffix = "[" + str(ext) + "]"
        new_reference_ex = self.basefile + ext_suffix
        old_reference_ex = old_reference + ext_suffix
        log.verbose("Checking table modes of '{}' against comparison reference '{}'".format(
                new_reference_ex, old_reference_ex))
        old_modes, old_all_cols = table_mode_dictionary(
            "old reference", old_reference, self.mode_columns, ext=ext)
        if not old_modes:
            log.info("No modes defined in comparison reference", repr(old_reference_ex), 
                     "for keys", repr(self.mode_columns))
            return
        new_modes, new_all_cols = table_mode_dictionary(
            "new reference", self.filename, self.mode_columns, ext=ext)
        if not new_modes:
            log.info("No modes defined in new reference", repr(new_reference_ex), "for keys", 
                     repr(self.mode_columns))
            return
        old_sample = old_modes.values()[0]
        new_sample = new_modes.values()[0]
        if len(old_sample) != len(new_sample) or old_all_cols != new_all_cols:
            log.warning("Change in row format betwween", repr(old_reference_ex), "and", repr(new_reference_ex))
            log.verbose("Old sample:", repr(old_sample))
            log.verbose("New sample:", repr(new_sample))
            return
        for mode in sorted(old_modes):
            if mode not in new_modes:
                log.warning("Table mode", mode, "from old reference", repr(old_reference_ex),
                            "is NOT IN new reference", repr(new_reference_ex))
                log.verbose("Old:", repr(old_modes[mode]), verbosity=60)
                continue
            # modes[mode][0] is row_no,  modes[mode][1] is row value
            diff = self.compare_row_values(mode, old_modes[mode][1], new_modes[mode][1])
            if not diff:
                log.verbose("Mode", mode, "of", repr(new_reference_ex), 
                            "has same values as", repr(old_reference_ex),  verbosity=60)
            else:
                log.verbose("Mode change", mode, "between", repr(old_reference_ex), "and", 
                            repr(new_reference_ex))
                log.verbose("Old:", repr(old_modes[mode]), verbosity=60)
                log.verbose("New:", repr(new_modes[mode]), verbosity=60)
        for mode in sorted(new_modes):
            if mode not in old_modes:
                log.info("Table mode", mode, "of new reference", repr(new_reference_ex),
                         "is NOT IN old reference", repr(old_reference))
                log.verbose("New:", repr(new_modes[mode]), verbosity=60)
                
    def compare_row_values(self, mode, old_row, new_row):
        """Compare key value tuple list `old_row` to `new_row` for key value tuple list `mode`.
        Handle array value comparisons.   
        
        Return 0 if old_row == new_row,  non-0 otherwise.
        """
        different = 0
        for field_no, (old_key, old_value) in enumerate(old_row):
            new_key, new_value = new_row[field_no]
            if old_key != new_key:
                log.warning("Column key mismatch at mode", mode, "old_key", repr(old_key), 
                            "new_key", new_key)
                different += 1
            old_value = handle_nan(old_value)
            new_value = handle_nan(new_value)
            if np.any(old_value != new_value):
                different += 1
        return different

def dump_multi_key(fitsname, keys, warn_keys):
    """Dump out all header values for `keys` in all extensions of `fitsname`."""
    hdulist = pyfits.open(fitsname)
    unseen = set(keys)
    for i, hdu in enumerate(hdulist):
        for key in keys:
            for card in hdu.header.cards:
                if card.keyword == key:
                    if interesting_value(card.value):
                        log.info("["+str(i)+"]", key, card.value, card.comment)
                        if key in unseen:
                            unseen.remove(key)
    for key in unseen:
        if key in warn_keys:
            log.warning("Missing keyword '%s'."  % key)

def interesting_value(value):
    """Return True IFF `value` isn't uninteresting."""
    if str(value).strip().lower() in ["",
                                 "*** end of mandatory fields ***",
                                 "*** column names ***",
                                 "*** column formats ***"]:
        return False
    return True

class JsonCertifier(Certifier):
    """Certifier for a .json file,  currently basic parsing only."""
    
    def certify(self):
        """Certify a .json file."""
        self.trap("File does not parse as valid JSON", self.load)
        
    def load(self):
        """Load and parse the .json in self.filename"""
        import json
        with open(self.filename) as handle:
            contents = handle.read()
        try:
            return json.loads(contents)
        except Exception as exc:
            raise InvalidFormatError(str(exc))

class YamlCertifier(Certifier):
    """Certifier for a .yaml file,  currently basic parsing only."""
    
    def certify(self):
        """Certify a .yaml file."""
        self.trap("File does not parse as valid YAML", self.load)
        
    def load(self):
        """Load and parse the .yaml in self.filename"""
        try:
            import yaml
        except Exception:
            log.warning("Cannot import yaml (PyYAML) for", repr(self.basename), "no YAML checking possible.")
            return
        with open(self.filename) as handle:
            contents = handle.read()
        try:
            return yaml.load(contents)
        except Exception as exc:
            raise InvalidFormatError(str(exc))

class TextCertifier(Certifier):
    """Certifier for a text file,  currently a pass through with a warning."""
    
    def certify(self):
        """Certify a .text file."""
        self.trap("File does not parse as valid text", self.load)
        
    def load(self):
        """Load and parse the .json in self.filename"""
        log.warning("No certification checks for text file", repr(self.basename))
        with open(self.filename) as handle:
            contents = handle.read()
        return contents

class UnknownCertifier(Certifier):
    """Certifier for unknown type,  currently a pass through with a warning."""
    
    def certify(self):
        """Certify an unknown format file."""
        self.trap("File does not load", self.load)
        
    def load(self):
        """Load file of unknown type."""
        log.warning("No certification checks for unknown file type of", repr(self.basename))
        with open(self.filename) as handle:
            contents = handle.read()
        return contents
    
# ============================================================================
class MappingCertifier(Certifier):
    """Parameter container for certifying a mapping file,  and possibly it's references."""

    def certify(self):
        """Certify mapping `self.filename` relative to `self.context`."""
        if not self.dont_parse:
            parsing = mapping_parser.parse_mapping(self.filename)
            mapping_parser.check_duplicates(parsing)

        mapping = rmap.fetch_mapping(self.filename, ignore_checksum="warn")
        mapping.validate_mapping(trap_exceptions=self.trap_exceptions)
    
        # derived_from = mapping.get_derived_from()
        derived_from = find_old_mapping(self.context, self.filename)
        if derived_from is not None:
            if derived_from.name == self.filename:
                log.verbose("Mapping", repr(self.filename), "did not change relative to context", repr(self.context))
            else:
                diff.mapping_check_diffs(mapping, derived_from)
        else:
            if self.context is not None:
                log.info("No predecessor for", repr(mapping.name), "relative to context", repr(self.context))
            
        # Optionally check nested references,  only for rmaps.
        if not isinstance(mapping, rmap.ReferenceMapping) or not self.check_references: # Accept None or False
            return
        
        references = self.get_existing_reference_paths(mapping)
        
        if self.check_references == "contents":
            certify_files(references, context=self.context, 
                          check_references=self.check_references,
                          trap_exceptions=self.trap_exceptions, 
                          compare_old_reference=self.compare_old_reference,
                          observatory=self.observatory)
    
    def get_existing_reference_paths(self, mapping):
        """Return the paths of the references referred to by mapping.  Omit
        paths for which the reference does not exist.
        """
        references = []
        for ref in mapping.reference_names():
            path = self.trap("Can't locate reference file.", 
                             get_existing_path, ref, mapping.observatory)
            if path:
                log.verbose("Reference", repr(ref), "exists at", repr(path))
                references.append(path)
        return references
    
def get_existing_path(reference, observatory):
    """Return the path of `reference` located relative to `mapping`."""
    path = rmap.locate_file(reference, observatory)
    if not os.path.exists(path):
        raise ValidationError("Path " + repr(path) + " does not exist.")
    return path

def mapping_closure(files):
    """Traverse the mappings in `files` and return a list of all mappings
    referred to by `files` as well as any references in `files`.
    """
    closure_files = set()
    for file_ in files:
        if rmap.is_mapping(file_):
            mapping = rmap.get_cached_mapping(file_, ignore_checksum="warn")
            more_files = set([rmap.locate_mapping(name) for name in mapping.mapping_names()])
            more_files = (more_files - set([rmap.locate_mapping(mapping.basename)])) | set([file_])
        else:
            more_files = set([file_])
        closure_files = closure_files.union(more_files)
    return sorted(closure_files)

# ============================================================================

def find_old_mapping(comparison_context, new_mapping):
    """Find the mapping in pmap `comparison_context` corresponding to `new_mapping`,  if there is one.
    This call will cache `comparison_context` so it should only be called on "official" mappings,  not
    trial mappings.
    """
    if comparison_context:
        comparison_mapping = rmap.get_cached_mapping(comparison_context)
        return comparison_mapping.get_equivalent_mapping(new_mapping)
    else:
        return None

def find_governing_rmap(context, reference):
    """Given mapping `context`,  return the loaded rmap which governs `reference`.   Typically this will
    be the rmap which contains the predecessor to `reference`,  not `reference` itself.
    """
    mapping = rmap.asmapping(context, cached=True)
    instrument, filekind = mapping.locate.get_file_properties(reference)
    if mapping.name.endswith(".pmap"):
        governing_rmap = mapping.get_imap(instrument).get_rmap(filekind)
    elif mapping.name.endswith(".imap"):
        governing_rmap = mapping.get_rmap(filekind)
    elif mapping.name.endswith(".rmap"):
        governing_rmap = mapping
    else:
        raise ValueError("Invalid comparison context " + repr(context))
    g_instrument, g_filekind = mapping.locate.get_file_properties(governing_rmap.name)
    assert instrument == g_instrument, "Comparison context inconsistent with reference file."
    assert filekind == g_filekind, "Comparison context inconsistent with reference type."
    log.verbose("Reference '{}' corresponds to rmap '{}' in context '{}'".format(
                reference, governing_rmap.name, mapping.name))
    return governing_rmap

# ============================================================================

def find_old_reference(context, reffile):
    """Returns the name of the old reference file(s) that the new reffile would replace in `context`,  or None.
    """
    with log.info_on_exception("Failed resolving prior reference for '{}' in '{}'".format(reffile, context)):
        return _find_old_reference(context, reffile)
    return None

def _find_old_reference(context, reffile):
    """Returns the name of the old reference file(s) that the new reffile would replace."""
    
    reference_mapping = find_governing_rmap(context, reffile)
    
    refname = os.path.basename(reffile)
    if refname in reference_mapping.reference_names():
        return refname

    # Determine the corresponding reference by attempting to add reffile to the old context.
    new_r = reference_mapping.insert_reference(reffile)
    
    # Examine the differences and treat the replaced file as the prior reference.
    diffs = reference_mapping.difference(new_r)
    match_refname = None
    for diff_tup in diffs:
        if diff.diff_action(diff_tup) == "replace":
            match_refname, dummy = diff.diff_replace_old_new(diff_tup)
            assert dummy == refname, "Bad replacement inserting '{}' into '{}'".format(reffile, reference_mapping.name)
            break   # XXX it may be possible to have more than one corresponding prior reference
    else:
        log.info("No file corresponding to", repr(reffile), "in context", repr(reference_mapping.name))
        return None
    
    # grab match_file from server and copy it to a local disk, if network
    # connection is available and configured properly
    # Note: this call works in both networked and non-networked modes of operation.
    # Non-networked mode requires access to /grp/crds/[hst|jwst] or a copy of it.
    try:
        match_files = client.dump_references(reference_mapping.name, baserefs=[match_refname], ignore_cache=False)
        match_file = match_files[match_refname]
        if not os.path.exists(match_file):   # For server-less mode in debug environments w/o Central Store
            raise IOError("Comparison reference " + repr(match_refname) + " is defined but does not exist.")
        log.info("Comparing reference", repr(refname), "against", repr(os.path.basename(match_file)))
    except Exception, exc:
        log.warning("Failed to obtain reference comparison file", repr(match_refname), ":", str(exc))
        match_file = None

    return match_file

def table_mode_dictionary(generic_name, filename, mode_keys, ext=1):
    """Returns ({ (mode_val,...) : (row_no, (entire_row_values, ...)) },  [col_name, ...] ) 
    for FITS data table `filename` at extension `ext` where column names `mode_keys` define the 
    columns to select for mode values.
    """
    table = pyfits.getdata(filename, ext=ext)
    all_cols = [name.upper() for name in table.names]
    basename = repr(os.path.basename(filename) + "[{}]".format(ext))
    log.verbose("Mode columns for", generic_name, basename, "are:", repr(mode_keys))
    log.verbose("All column names for", generic_name, basename, "are:", repr(all_cols))
    modes = defaultdict(list)
    for i, row in enumerate(table):
        new_row = tuple(zip(all_cols, (handle_nan(v) for v in row)))
        rowdict = dict(new_row)
        # Table row keys can vary by extension.  Have CRDS support a simple model of using
        # whichever mode_keys are present in a given row.
        mode = tuple((key, rowdict[key]) for key in mode_keys if key in rowdict)
        if not mode:
            log.info("Empty actual mode in", generic_name, basename, "with candidate mode columns", mode_keys)
            return {}, []
        modes[mode].append((i, new_row))
    for mode in sorted(modes.keys()):
        if len(modes[mode]) > 1:
            log.warning("Duplicate definitions in", generic_name, basename, "for mode:", mode, ":\n", 
                        "\n".join([repr(new_row) for row in modes[mode]]))
    # modes[mode][0] is first instance of multiply defined mode.
    return { mode:modes[mode][0] for mode in modes }, all_cols

def handle_nan(var):
    """Map nan values to 'nan' so that 'nan' == 'nan'."""
    if isinstance(var, (np.float32, np.float64, np.float128)) and np.isnan(var):
        return 'nan'
    elif isinstance(var, np.ndarray) and var.shape == () and np.any(np.isnan(var)):
        return 'nan'
    else:
        return var

# ============================================================================

class MissingReferenceError(RuntimeError):
    """A reference file mentioned by a mapping isn't in CRDS yet."""

def certify_files(files, context=None, dump_provenance=False, check_references=False, 
                  is_mapping=False, trap_exceptions=True, compare_old_reference=False,
                  dont_parse=False, skip_banner=False, script=None, observatory=None,
                  comparison_reference=None):
    """Certify the list of `files` relative to .pmap `context`.   Files can be
    references or mappings.   This function primarily provides an interface for web code.
    
    files:                  list of file paths to certify.
    context:                .pmap name to certify relative to
    dump_provenance:        for references,  log provenance keywords and rmap parkey values.
    check_references:       False, "exists", "contents"
    is_mapping:             bool  (assume mapping regardless of filename)
    trap_exceptions:        bool   if True, issue log.error() messages, else raise.
    compare_old_reference:  bool,  if True,  attempt table mode checking.
    dont_parse:       bool,  if True,  don't run parser to scan mappings for duplicate keys.
    script:   command line Script instance
    """

    if not isinstance(files, list):
        files = [files]
        
    assert observatory is not None, "Undefined observatory in certify_files."
        
    for fnum, filename in enumerate(files):
        if not skip_banner:
            log.info('#' * 40)  # Serves as demarkation for each file's report

            klasses = {
                "mapping" : MappingCertifier,
                "fits" : FitsCertifier,
                "json" : JsonCertifier,
                "yaml" : YamlCertifier,
                "text" : TextCertifier,
                "unknown" : UnknownCertifier,
            }
            filetype = config.filetype(filename)
            
            klass = klasses.get(filetype, UnknownCertifier)
            certifier_name = klass.__name__[:-len("Certifier")].lower()
            
        if comparison_reference:
            log.info("Certifying", repr(filename) + ' (' + str(fnum+1) + '/' + str(len(files)) + ')', 
                     "as", repr(certifier_name), "relative to context", repr(context), 
                     "and comparison reference", repr(comparison_reference))
        else:
            log.info("Certifying", repr(filename) + ' (' + str(fnum+1) + '/' + str(len(files)) + ')', 
                     "as", repr(certifier_name), "relative to context", repr(context))
        try:
            certifier = klass(filename, context=context, check_references=check_references,
                              trap_exceptions=trap_exceptions, 
                              compare_old_reference=compare_old_reference,
                              dump_provenance=dump_provenance,
                              dont_parse=dont_parse, script=script, observatory=observatory,
                              comparison_reference=comparison_reference)
            
            certifier.certify()
        except Exception, exc:
            if trap_exceptions:
                log.error("Validation error in " + repr(filename) + " : " + str(exc))
            else:
                raise

    log.info('#' * 40)  # Serves as demarkation for each file's report

def test():
    """Run doctests in this module.  See also certify unittests."""
    import doctest
    from crds import certify
    return doctest.testmod(certify)

# ============================================================================

class CertifyScript(cmdline.Script, cmdline.UniqueErrorsMixin):
    """Command line script for checking CRDS mapping and reference files.
    
    Perform checks on each of `files`.   Print status.   If file is a context /
    mapping file,  it is used to define associated reference files which are
    located on the CRDS server.  If file is a .fits file,  it should include a
    relative or absolute filepath.
    """
    
    def __init__(self, *args, **keys):
        cmdline.Script.__init__(self, *args, **keys)
        cmdline.UniqueErrorsMixin.__init__(self, *args, **keys)

    description = """
Checks a CRDS reference or mapping file.
    """
    
    epilog = ""
    
    def add_args(self):
        self.add_argument("files", nargs="+")
        self.add_argument("-d", "--deep", dest="deep", action="store_true",
            help="Certify reference files referred to by mappings have valid contents.")
        self.add_argument("-r", "--dont-recurse-mappings", dest="dont_recurse_mappings", action="store_true",
            help="Do not load and validate mappings recursively,  checking only directly specified files.")
        self.add_argument("-a", "--dont-parse", dest="dont_parse", action="store_true",
            help="Skip slow mapping parse based checks,  including mapping duplicate entry checking.")
        self.add_argument("-e", "--exist", dest="exist", action="store_true",
            help="Certify reference files referred to by mappings exist.")
        self.add_argument("-m", "--mapping", dest="mapping", action="store_true",
            help="Ignore extensions, the files being certified are mappings.")
        self.add_argument("-p", "--dump-provenance", dest="dump_provenance", action="store_true",
            help="Dump provenance keywords.")
        self.add_argument("-t", "--trap-exceptions", dest="trap_exceptions", type=str, default="selector",
            help="Capture exceptions at level: pmap, imap, rmap, selector, debug, none")
        self.add_argument("-x", "--comparison-context", dest="comparison_context", type=str, default=None,
            help="Pipeline context defining comparison files.")
        self.add_argument("-y", "--comparison-reference", dest="comparison_reference", type=str, default=None,
            help="Comparison reference for table certification.")
        
        cmdline.UniqueErrorsMixin.add_args(self)

    def main(self):
        if self.args.deep:
            check_references = "contents"
        elif self.args.exist:
            check_references = "exist"
        else:
            check_references = None

        if self.args.trap_exceptions == "none":
            self.args.trap_exceptions = False
    
        assert (self.args.comparison_context is None) or rmap.is_mapping(self.args.comparison_context), \
            "Specified --context file " + repr(self.args.comparison_context) + " is not a CRDS mapping."
        assert (self.args.comparison_reference is None) or not rmap.is_mapping(self.args.comparison_reference), \
            "Specified --comparison-reference file " + repr(self.args.comparison_reference) + " is not a reference."
        if self.args.comparison_reference:
            assert len(self.files) == 1 and not rmap.is_mapping(self.files[0]), \
                "Only one reference can be certified if --comparison-reference is specified."
            
        if (not self.args.dont_recurse_mappings):
            all_files = mapping_closure(self.files)
        else:
            all_files = set(self.files)
            
        certify_files(sorted(all_files), 
                      context=self.args.comparison_context,
                      comparison_reference=self.args.comparison_reference,
                      compare_old_reference=self.args.comparison_context or self.args.comparison_reference,
                      dump_provenance=self.args.dump_provenance, 
                      check_references=check_references, 
                      is_mapping=self.args.mapping, 
                      trap_exceptions=self.args.trap_exceptions,
                      dont_parse=self.args.dont_parse,
                      script=self, observatory=self.observatory)
    
        self.dump_unique_errors()
        self.report_stats()
        log.standard_status()
        
        return log.errors()

if __name__ == "__main__":
    CertifyScript()()
