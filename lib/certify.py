"""This module defines replacement functionality for the CDBS "certify" program
used to check parameter values in .fits reference files.   It verifies that FITS
files define required parameters and that they have legal values.
"""
import sys
import os
import re

import pyfits

from crds import rmap, log, timestamp, utils, data_file, diff, cmdline
from crds import mapping_parser, refmatch
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
        log.verbose("Checking ", repr(filename), "keyword", repr(self.name), "=", repr(value))
        if value is None: # missing optional or excluded keyword
            return True
        if self.condition is not None:
            value = self.condition(value)
        if not self._values:
            return True
        self._check_value(value)
        # If no exception was raised, consider it validated successfully
        return True

    def _check_value(self, value):
        if value not in self._values and self._values != ('*',):
            if isinstance(value, str):
                for pat in self._values:
                    if re.match(pat, value):
                        return
            raise ValueError("Value(s) for " + repr(self.name) + " of " +
                            str(log.PP(value)) + " is not one of " +
                            str(log.PP(self._values)))

    def check_header(self, filename, header=None):
        """Extract the value for this Validator's keyname,  either from `header`
        or from `filename`'s header if header is None.   Check the value.
        """
        if header is None:
            header = data_file.get_header(filename)
        value = self._get_header_value(header)
        return self.check_value(filename, value)

    def check_column(self, filename, context=None):
        """Extract a column of values from `filename` and check them all against
        the legal values for this Validator.
        """
        values = None
        try:
            values = self._get_column_values(filename)
        except Exception, exc:
            log.error("Can't read column values : " + str(exc))
            return
        check_val = True

        if values is not None: # Only check for non-optional columns
            for i, value in enumerate(values): # compare to TPN default values
                valid = self.check_value(filename + "[" + str(i) +"]", value)
                if not valid:
                    check_val = False

        if context: # If context has been specified, compare against previous reffile
            current = refmatch.find_current_reffile(filename, context)
            if current: # Only do comparison if current ref file can be found
                log.verbose("Checking values for column", repr(self.name),
                            " against values found in ",current)
                current_values = self._get_column_values(current)
                return self._check_column_values(values, current_values)

        # If no context, report results of check_value anyway if not an Exception
        return check_val

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
        col_extn = None
        for extn in hdu:
            if (hasattr(extn,'_extension') and 'table' in extn._extension.lower() and self.name in extn.data.names):
                col_extn = extn
                break
        # If no extension could be found with that column, report as missing
        if col_extn is None:
            # close FITS handle
            hdu.close()
            return self.__handle_missing()

        # If it was found, return the values
        tbdata = col_extn.data
        values = tbdata.field(self.name)

        # close FITS handle
        hdu.close()
        return self.__handle_excluded(values)

    def _check_column_values(self, new_values, current_values):
        """ Check column values from new table against values from current table"""
        # Use sets to perform comparisons more efficiently
        current_set = set(current_values)
        new_set = set(new_values)

        # find values which are uniq to each set/file
        uniq_new = new_set.difference(current_set)
        uniq_current = current_set.difference(new_set)

        # report how input values compare to current values, if different
        if len(uniq_new) > 0:
            log.warning("Value(s) for", repr(self.name), "of", log.PP(list(uniq_new)),
                "is/are not one of", log.PP(current_values), sep='\n')
            return True

        if len(uniq_current) > 0:
            log.warning("These values for "+repr(self.name)+ " were not present in new input:\n"+
                        str(log.PP(list(uniq_current))))
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
        log.verbose('Adding column '+column.name+' to ModeValidator')
        self.names.append(column.name)

    def check_column(self, filename, context=None):
        """Extract a column of values from `filename` and check them all against
        the legal values for this Validator.
        """
        #
        # TODO: Expand to concatenate all columns values
        #
        new_values = []
        for name in self.names:
            self.name = name
            values = None
            try:
                values = self._get_column_values(filename)
            except Exception, exc:
                raise RuntimeError("Can't read column values from " + filename + ": " + str(exc))
            new_values.append(values)

        # convert these values into 'modes' by transposing the separate columns
        # of values into sets of values with one set per row.
        modes = map(tuple, transposed(new_values))

        if context: # If context has been specified, compare against previous reffile
            current = refmatch.find_current_reffile(filename, context)
            if not current: # Only do comparison if current ref file can be found
                log.warning("No comparison reference for", repr(filename),
                            "in context", repr(context))
            else:
                log.verbose("Checking values for mode", repr(self.names),
                            " against values found in ",current)

                current_values = []
                for name in self.names:
                    self.name = name
                    current_values.append(self._get_column_values(current))
                current_modes = map(tuple, transposed(current_values))
                # find values which are uniq to each set/file
                self.name = self.names
                self._check_column_values(modes, current_modes)

def transposed(lists):
    if not lists: 
        return []
    return map(lambda *row: list(row), *lists)

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
            values = None
        else:
            values = KeywordValidator.condition_values(self, info)
        return values

    def _check_value(self, value):
        if self.is_range:
            if value < self.min or value > self.max:
                raise ValueError("Value for " + repr(self.name) + " of " +
                    repr(value) + " is outside acceptable range " +
                    self.info.values[0])
        else:   # First try a simple exact string match check
            KeywordValidator._check_value(self, value)

# ----------------------------------------------------------------------------

class IntValidator(NumericalValidator):
    """Validates integer values."""
    condition = int

# ----------------------------------------------------------------------------

class FloatValidator(NumericalValidator):
    """Validates floats of any precision."""
    condition = float
    epsilon = 1e-7

    def _check_value(self, value):
        try:
            NumericalValidator._check_value(self, value)
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
        timestamp.Sybdate.get_datetime(value)

# ----------------------------------------------------------------------------

class SlashdateValidator(KeywordValidator):
    """Validates &SLASHDATE fields."""
    def check_value(self, filename, value):
        timestamp.Slashdate.get_datetime(value)

# ----------------------------------------------------------------------------

class AnydateValidator(KeywordValidator):
    """Validates &ANYDATE fields."""
    def check_value(self, filename, value):
        timestamp.Anydate.get_datetime(value)

# ----------------------------------------------------------------------------

class FilenameValidator(KeywordValidator):
    """Validates &FILENAME fields."""
    def check_value(self, filename, value):
        return (value == "(initial)") or not os.path.dirname(value)

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

def get_validators(filename):
    """Given a reference file `filename`,  return the observatory specific
    list of Validators used to check that reference file type.
    """
    # Find the observatory's locator module based on the reference file.
    locator = utils.reference_to_locator(filename)
    # Get the cache key for this filetype.
    key = locator.reference_name_to_validator_key(filename)
    return validators_by_typekey(locator, key)

@utils.cached
def validators_by_typekey(locator, key):
    """Load and return the list of validators associated with reference type 
    validator `key`.
    """
    tpninfos = tuple(locator.get_tpninfos(*key))
    # Make and cache Validators for `filename`s reference file type.
    return [validator(x) for x in tpninfos]
        
# ============================================================================

class Certifier(object):
    """Container class for parameters for a certification run."""
    def __init__(self, filename, context=None, trap_exceptions=False, check_references=False, 
                 compare_old_reference=False, dump_provenance=False,
                 provenance_keys=("DESCRIP", "COMMENT", "PEDIGREE", "USEAFTER","HISTORY",),
                 dont_parse=False):
        self.filename = filename
        self.context = context
        self.trap_exceptions = trap_exceptions
        self.check_references = check_references
        self.compare_old_reference = compare_old_reference
        self.dump_provenance = dump_provenance
        self.provenance_keys = list(provenance_keys)
        self.dont_parse = dont_parse     # mapping only
        
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
            msg = "In " + repr(self.filename) + " : " + message + " : " + str(exc)
            if self.trap_exceptions:
                log.error(msg)
                return None
            else:
                log.error(msg)
                raise
                # raise ValidationError(msg)
            
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
            pmap = rmap.get_cached_mapping(self.context, ignore_checksum="warn")
            instrument, filekind = pmap.locate.get_file_properties(self.filename)
            return pmap.get_imap(instrument).get_rmap(filekind).get_required_parkeys()
        except Exception, exc:
            log.verbose_warning("Failed retrieving required parkeys:", str(exc))
            return []

    def certify_simple_parameters(self, header):
        """Check non-column parameters."""
        for checker in get_validators(self.filename):
            if checker.info.keytype != 'C':
                self.trap("checking " + repr(checker.info.name),
                          checker.check, self.filename, header=header)
        
    def certify_reference_modes(self, header):
        """Check column parameters row-by-row."""
        mode_checker = None # Initialize mode validation
        for checker in get_validators(self.filename):
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
            diff.mapping_check_diffs(mapping, derived_from)
            
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

class MissingReferenceError(RuntimeError):
    """A reference file mentioned by a mapping isn't in CRDS yet."""

def certify_files(files, context=None, dump_provenance=False, check_references=False, 
                  is_mapping=False, trap_exceptions=True, compare_old_reference=False,
                  dont_parse=False, skip_banner=False):
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
    """

    if not isinstance(files, list):
        files = [files]

    for fnum, filename in enumerate(files):
        if not skip_banner:
            log.info('#' * 40)  # Serves as demarkation for each file's report
            log.info("Certifying", repr(filename) + ' (' + str(fnum+1) + '/' + str(len(files)) + ')', 
                     "relative to context", repr(context))
        try:
            if is_mapping or rmap.is_mapping(filename):
                klass = MappingCertifier
            else:
                klass = ReferenceCertifier
            certifier = klass(filename, context=context, check_references=check_references,
                              trap_exceptions=trap_exceptions, 
                              compare_old_reference=compare_old_reference,
                              dump_provenance=dump_provenance,
                              dont_parse=dont_parse)
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

class CertifyScript(cmdline.Script):
    """Command line script for for checking CRDS mapping and reference files.
    
    Perform checks on each of `files`.   Print status.   If file is a context /
    mapping file,  it is used to define associated reference files which are
    located on the CRDS server.  If file is a .fits file,  it should include a
    relative or absolute filepath.
    """

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
                      dont_parse=self.args.dont_parse)
    
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
