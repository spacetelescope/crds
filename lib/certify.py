"""This module defines replacement functionality for the CDBS "certify" program
used to check parameter values in .fits reference files.   It verifies that FITS
files define required parameters and that they have legal values.
"""
import sys
import os
import re

import pyfits

from crds import rmap, log, timestamp, utils, data_file, diff, cmdline
from crds import client
from crds import mapping_parser
from crds.compat import namedtuple
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

# ----------------------------------------------------------------------------

class KeywordValidator(object):
    """Validates one field described in a .tpn file,  initialized with
    a TpnInfo object.
    """
    def __init__(self, info):
        self.info = info
        self.name = info.name
        self.names = []
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

    def check(self, filename, header=None, context=None):
        """Pull the value(s) corresponding to this Validator out of it's
        `header` or the contents of the file.   Check them against the
        requirements defined by this Validator.
        """
        if self.info.keytype == "H":
            return self.check_header(filename, header)
        elif self.info.keytype == "C":
            return self.check_column(filename, context=context)
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
        """Raises ValueError if `value` is not valid."""
        if value not in self._values:  # and tuple(self._values) != ('*',):
            if isinstance(value, str):
                for pat in self._values:
                    if re.match(pat, value):
                        self.verbose(filename, value, "matches", repr(pat))
                        return
            raise ValueError("Value(s) for " + repr(self.name) + " of " +
                            str(log.PP(value)) + " is not one of " +
                            str(log.PP(self._values)))
        else:
            self.verbose(filename, value, "is in", repr(self._values))

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
        the legal values for this Validator.
        """
        try:
            new_values = self._get_column_values(filename)
            if new_values is None: # Ignore missing optional columns
                return True 
        except Exception, exc:
            log.error("Can't read column values:", str(exc))
            return False

        # new_values must not be None,  check all, waiting to fail later
        bad_vals = False
        for i, value in enumerate(new_values): # compare to TPN values
            try:
                self.check_value(filename + "[" + str(i) +"]", value)
            except ValueError, exc:
                bad_vals = True

        if bad_vals:   # Fail prior to context comparison if values simply bad.
            return False
        
        if not context:  # If no comparison context,  nothing to fail against.
            return True

        # If context has been specified, compare against previous reffile
        old = find_old_reffile(filename, context)
        if old: # Only do comparison if old ref file can be found
            log.verbose("Checking", repr(filename), "values for column", repr(self.name),
                        "against values found in", old)
            old_values = self._get_column_values(old)
            return self._check_column_values(new_values, old_values)
        else:
            return True

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

    def _get_column_values(self, filename):
        """Pull the column of values corresponding to this Validator out of
        `filename` and return it.   Handle missing and excluded cases.
        """
        hdu = pyfits.open(filename)
        
        # make sure table(s) are in extension(s) not the PRIMARY extension
        assert len(hdu) >1, "table file with only primary extension: " + repr(filename)

        # start by finding the extension which contains the requested column
        for extn in hdu:
            if (hasattr(extn,'_extension') and 'table' in extn._extension.lower() and self.name in extn.data.names):
                col_extn = extn
                break
        else:  # If no extension could be found with that column, report as missing
            hdu.close()
            return self.__handle_missing()

        # If it was found, return the values
        tbdata = col_extn.data
        values = tbdata.field(self.name)
        hdu.close()
        return self.__handle_excluded(values)

    def _check_column_values(self, new_values, old_values):
        """ Check column values from new table against values from old table"""
        
        # Use sets to perform comparisons more efficiently
        old_set = set(list(old_values))
        new_set = set(list(new_values))

        # find values which are uniq to each set/file
        uniq_new = new_set.difference(old_set)
        uniq_old = old_set.difference(new_set)

        # report how input values compare to old values, if different
        if len(uniq_new) > 0:
            log.warning("Column value(s) for", repr(self.name), "of", log.PP(list(uniq_new)),
                "are not in:", log.PP(old_values))

        if len(uniq_old) > 0:
            log.warning("Column value(s) for", repr(self.name), "omitted",
                        str(log.PP(list(uniq_old))))

        # if no differences, return True
        return True

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

# ----------------------------------------------------------------------------

class CharacterValidator(KeywordValidator):
    """Validates values of type Character."""
    def condition(self, value):
        chars = str(value).strip().upper()
        if " " in chars:
            chars = '"' + "_".join(chars.split()) + '"'
        return chars

# ----------------------------------------------------------------------------

class ModeValidator(CharacterValidator):
    """ Validates values from multiple columns as a single mode value"""
    
    def add_column(self, column):
        """ Add column validator to be used as basis for mode."""
        log.verbose('Adding column', repr(column.name), 'to ModeValidator')
        self.names.append(column.name)

    def check_column(self, new_file, context=None):
        """Extract a column of values from `new_file` and check them all against
        the legal values for this Validator.
        """
        if context is None: # If context has been specified, compare against previous reffile
            log.verbose("No comparison context,  no mode comparison possible for", repr(new_file))
            return

        new_modes = self.get_modes(new_file)
        
        old_file = find_old_reffile(new_file, context)
        if not old_file: # Only do comparison if old ref file can be found
            log.warning("No comparison reference for", repr(new_file),
                        "in context", repr(context))
        else:
            log.verbose("Checking", repr(new_file), "values for mode", repr(self.names),
                        " against values found in ", repr(old_file))
            old_modes = self.get_modes(old_file)
            # find values which are uniq to each set/file
            self.name = self.names
            self._check_column_values(new_modes, old_modes)
                
    def get_modes(self, filename):
        """Extract the "mode" columns from `filename` and zip them together into a list of mode tuples."""
        columns = []
        for name in self.names:
            self.name = name
            try:
                col_values = self._get_column_values(filename)
            except Exception, exc:
                raise RuntimeError("Can't read column values from " + repr(filename) + ": " + str(exc))
            columns.append(col_values)        
        return zip(*columns)   # zip columns together into "mode" tuples.
    
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
            func = eval(info.values[0][1:].capitalize() + "Validator")
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
    validators = [validator(x) for x in locator.get_tpninfos(*key)]
    log.verbose("Validators for", repr(key), "=", log.PP(validators))
    return validators

# ============================================================================

class Certifier(object):
    """Container class for parameters for a certification run."""
    def __init__(self, filename, context=None, trap_exceptions=False, check_references=False, 
                 compare_old_reference=False, dump_provenance=False,
                 provenance_keys=("DESCRIP", "COMMENT", "PEDIGREE", "USEAFTER","HISTORY",),
                 dont_parse=False, script=None, observatory=None):
        
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
    
        assert self.check_references in [False, None, "exist", "contents"], \
            "invalid check_references parameter " + repr(self.check_references)
    
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

class ReferenceCertifier(Certifier):
    """Support certifying reference files:
    
    1. Check simple keywords against TPN files using the reftype's validators.
    2. Check mode tables against prior reference of context.
    3. Dump out keywords of interest.
    """
    def certify(self):
        """Certify a reference file."""
        if not self.trap("File does not comply with FITS format", self.fits_verify):
            return
        header = data_file.get_header(self.filename)
        self.certify_simple_parameters(header)
        self.certify_reference_modes(header)
        if self.dump_provenance:
            dump_multi_key(self.filename, self.get_rmap_parkeys() + self.provenance_keys, 
                           self.provenance_keys)

    def fits_verify(self):
        """Use pyfits to verify the FITS format of self.filename."""
        if not self.filename.endswith(".fits"):
            log.verbose("Skipping FITS verify for '%s'" % self.filename)
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
            pmap = rmap.fetch_mapping(self.context, ignore_checksum="warn")
            instrument, filekind = pmap.locate.get_file_properties(self.filename)
            return pmap.get_imap(instrument).get_rmap(filekind).get_required_parkeys()
        except Exception, exc:
            log.verbose_warning("Failed retrieving required parkeys:", str(exc))
            return []

    def certify_simple_parameters(self, header):
        """Check non-column parameters."""
        for checker in get_validators(self.filename, self.observatory):
            if checker.info.keytype != 'C':
                self.trap("checking " + repr(checker.info.name),
                          checker.check, self.filename, header=header)
        
    def certify_reference_modes(self, header):
        """Check column parameters row-by-row."""
        mode_checker = None # Initialize mode validation
        for checker in get_validators(self.filename, self.observatory):
            # Treat column validations together as a 'mode'
            if checker.info.keytype == 'C':
                checker.check(self.filename, header=header) # validate values against TPN valid values
                if mode_checker is None:
                    mode_checker = ModeValidator(checker.info)
                mode_checker.add_column(checker)    
        if mode_checker: # Run validation on all collected modes
            context = self.context if self.compare_old_reference else None
            self.trap("checking " + repr(mode_checker.names),
                      mode_checker.check, self.filename, context=context, header=header)

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
    
        derived_from = mapping.get_derived_from()
        if derived_from is not None:
            log.info("Comparing", repr(mapping.name), "against parent", repr(derived_from.name))
            diff.mapping_check_diffs(mapping, derived_from)
        else:
            log.info("No parent for", repr(mapping.name))
            
        # Optionally check nested references,  only for rmaps.
        if not isinstance(mapping, rmap.ReferenceMapping) or not self.check_references: # Accept None or False
            return
        
        references = self.get_existing_reference_paths(mapping)
        
        if self.check_references == "contents":
            certify_files(references, context=self.context, 
                          check_references=self.check_references,
                          trap_exceptions=self.trap_exceptions, 
                          compare_old_reference=self.compare_old_reference)
    
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

# ============================================================================

def find_old_reffile(reffile, pmap):
    """Returns the name of the old reference file(s) that the new reffile would replace,  or None.
    """
    with log.info_on_exception("Failed resolving prior reference for '{}' in '{}'".format(reffile, pmap)):
        return _find_old_reffile(reffile, pmap)
    return None

def _find_old_reffile(reffile, pmap):
    """Returns the name of the old reference file(s) that the new reffile would replace."""
    
    ctx = rmap.fetch_mapping(pmap)
    instrument, filekind = utils.get_file_properties(ctx.observatory, reffile)
    reference_mapping = ctx.get_imap(instrument).get_rmap(filekind)

    # Determine the corresponding reference by attempting to add reffile to the old context.
    new_r = reference_mapping.insert_reference(reffile)
    
    # Examine the differences and treat the replaced file as the prior reference.
    diffs = reference_mapping.difference(new_r)
    match_refname = None
    for diff_tup in diffs:
        if diff.diff_action(diff_tup) == "replace":
            match_refname, dummy = diff.diff_replace_old_new(diff_tup)
            assert dummy == os.path.basename(reffile), "Bad replacement inserting '{}' into '{}'".format(reffile, pmap)
            break   # XXX it may be possible to have more than one corresponding prior reference
    else:
        log.info("No file corresponding to", repr(reffile), "in context", repr(pmap))
        return None
    
    # grab match_file from server and copy it to a local disk, if network
    # connection is available and configured properly
    # Note: this call works in both networked and non-networked modes of operation.
    # Non-networked mode requires access to /grp/crds/[hst|jwst] or a copy of it.
    try:
        match_files = client.dump_references(pmap, baserefs=[match_refname], ignore_cache=False)
        match_file = match_files[match_refname]
        if not os.path.exists(match_file):   # For server-less mode in debug environments w/o Central Store
            raise IOError("Comparison reference " + repr(match_refname) + " is defined but does not exist.")
        log.info("Comparing reference", repr(reffile), "against", repr(match_file))
    except Exception, exc:
        log.warning("Failed to obtain reference comparison file", repr(match_refname), ":", str(exc))
        match_file = None

    return match_file

# ============================================================================

class MissingReferenceError(RuntimeError):
    """A reference file mentioned by a mapping isn't in CRDS yet."""

def certify_files(files, context=None, dump_provenance=False, check_references=False, 
                  is_mapping=False, trap_exceptions=True, compare_old_reference=False,
                  dont_parse=False, skip_banner=False, script=None, observatory=None):
    """Certify the list of `files` relative to .pmap `context`.   Files can be
    references or mappings.
    
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
            log.info("Certifying", repr(filename) + ' (' + str(fnum+1) + '/' + str(len(files)) + ')', 
                     "relative to context", repr(context))
            # log.info("certify_files locals():", log.PP(locals()))
        try:
            if is_mapping or rmap.is_mapping(filename):
                klass = MappingCertifier
            else:
                klass = ReferenceCertifier
            certifier = klass(filename, context=context, check_references=check_references,
                              trap_exceptions=trap_exceptions, 
                              compare_old_reference=compare_old_reference,
                              dump_provenance=dump_provenance,
                              dont_parse=dont_parse, script=script, observatory=observatory)
            certifier.certify()
        except Exception, exc:
            if trap_exceptions:
                log.error("Validation error in " + repr(filename) + " : " + str(exc))
            else:
                raise

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
        self.add_argument("-t", "--trap-exceptions", dest="trap_exceptions", 
            type=str, default="selector",
            help="Capture exceptions at level: pmap, imap, rmap, selector, debug, none")
        self.add_argument("-x", "--comparison-context", dest="context", type=str, default=None,
            help="Pipeline context defining comparison files.")
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
    
        assert (self.args.context is None) or rmap.is_mapping(self.args.context), \
            "Specified --context file " + repr(self.args.context) + " is not a CRDS mapping."
            
        if (not self.args.dont_recurse_mappings):
            all_files = self.mapping_closure(self.files)
        else:
            all_files = set(self.files)
            
        certify_files(sorted(all_files), 
                      context=self.args.context, 
                      dump_provenance=self.args.dump_provenance, 
                      check_references=check_references, 
                      is_mapping=self.args.mapping, 
                      trap_exceptions=self.args.trap_exceptions,
                      dont_parse=self.args.dont_parse,
                      script=self, observatory=self.observatory)
    
        self.dump_unique_errors()
        log.standard_status()
        
        return log.errors()
    
    def mapping_closure(self, files):
        """Traverse the mappings in `files` and return a list of all mappings
        referred to by `files` as well as any references in `files`.
        """
        closure_files = set()
        for file_ in files:
            if rmap.is_mapping(file_):
                mapping = rmap.get_cached_mapping(file_, ignore_checksum="warn")
                more_files = mapping.mapping_names(full_path=True)
            else:
                more_files = [file_]
            closure_files = closure_files.union(more_files)
        return sorted(closure_files)

if __name__ == "__main__":
    CertifyScript()()
