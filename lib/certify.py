"""This module defines replacement functionality for the CDBS "certify" program
used to check parameter values in .fits reference files.   It verifies that FITS
files define required parameters and that they have legal values.
"""
import sys
import os
import optparse
import re
import sets

import pyfits

from crds import rmap, log, timestamp, utils, data_file
from crds.compat import namedtuple
from crds.rmap import ValidationError
from crds import refmatch

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

class KeywordValidator(object):
    """Validates one field described in a .tpn file,  initialized with
    a TpnInfo object.
    """
    def __init__(self, info):
        self._info = info
        self.name = info.name
        self.names = []
        if self._info.presence not in ["R", "P", "E", "O"]:
            raise ValueError("Bad TPN presence field " +
                             repr(self._info.presence))
        if not hasattr(self.__class__, "_values"):
            self._values = self.condition_values(info)

    def condition(self, value):
        """Condition `value` to standard format for this Validator."""
        return value

    def condition_values(self, info):
        return [self.condition(value) for value in info.values]

    def __repr__(self):
        return self.__class__.__name__ + "(" + repr(self._info) + ")"

    def check(self, filename, header=None, context=None):
        """Pull the value(s) corresponding to this Validator out of it's
        `header` or the contents of the file.   Check them against the
        requirements defined by this Validator.
        """
        if self._info.keytype == "H":
            return self.check_header(filename, header)
        elif self._info.keytype == "C":
            return self.check_column(filename, context=context)
        elif self._info.keytype == "G":
            return self.check_group(filename)
        else:
            raise ValueError(
                "Unknown TPN keytype " + repr(self._info.keytype) + " for " +
                repr(self.name))

    def check_value(self, filename, value):
        """Check a single header or column value against the legal values
        for this Validator.
        """
        log.verbose("Checking ", repr(filename), "keyword",
                    repr(self.name), "=", repr(value))

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
            raise RuntimeError("Can't read column values : " + str(exc))
        check_val = True

        if values is not None: # Only check for non-optional columns
            for i, value in enumerate(values): # compare to TPN default values
                v = self.check_value(filename + "[" + str(i) +"]", value)
                if not v:
                    check_val = False

        if context: # If context has been specified, compare against previous reffile
            current = refmatch.find_current_reffile(filename,context)
            if current: # Only do comparison if current ref file can be found
                log.verbose("Checking values for column", repr(self.name),
                            " against values found in ",current)
                current_values = self._get_column_values(current)

                return _check_column_values(values,current_values)

        # If no context, report results of check_value anyway if not an Exception
        return check_val

    def check_group(self, filename):
        """Probably related to pre-FITS HST GEIS files,  not implemented."""
        assert False, "Group keys were not expected and not implemented."

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
            if hasattr(extn,'_extension') and 'table' in extn._extension.lower()\
                and self.name in extn.data.names:
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
        current_set = sets.Set(current_values)
        new_set = sets.Set(new_values)

        # find values which are uniq to each set/file
        uniq_new = new_set.difference(current_set)
        uniq_current = current_set.difference(new_set)

        # Report on any repeated values
        if len(current_set) != len(current_values):
            # duplicates found, so report which ones
            seen = sets.Set()
            duplicates = []
            for n in new_values:
                if n in seen:
                    duplicates.append(n)
                else:
                    seen.add(n)
            if len(duplicates) > 0:
                log.warning("The following values were duplicated for column "+
                            str(self.name)+": \n"+str(log.PP(duplicates)))
        # report how input values compare to current values, if different
        if len(uniq_new) > 0:
            log.warning("Value(s) for", repr(self.name), "of", log.PP(list(uniq_new)),
                "is/are not one of", log.PP(current_values), sep='\n')
            return True

        if len(uniq_current) > 0:
            log.warning("These values for "+repr(self.name)+
                    " were not present in new input:\n"+
                    str(log.PP(list(uniq_current))))
        # if no differences, return True
        return True

    def __handle_missing(self):
        """This Validator's key is missing.   Either raise an exception or
        ignore it depending on whether this Validator's key is required.
        """
        if self._info.presence in ["R","P"]:
            raise MissingKeywordError(
                "Missing required keyword " + repr(self.name))
        else:
            sys.exc_clear()
            return # missing value is None, so let's be explicit about the return value

    def __handle_excluded(self, value):
        """If this Validator's key is excluded,  raise an exception.  Otherwise
        return `value`.
        """
        if self._info.presence == "E":
            raise IllegalKeywordError(
                "*Must not define* keyword " + repr(self.name))
        return value

class CharacterValidator(KeywordValidator):
    """Validates values of type Character."""
    def condition(self, value):
        chars = str(value).strip().upper()
        if " " in chars:
            chars = '"' + "_".join(chars.split()) + '"'
        return chars

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
        numcols = len(self.names)
        for name in self.names:
            self.name = name
            values = None
            try:
                values = self._get_column_values(filename)
            except Exception, exc:
                raise RuntimeError("Can't read column values from "+filename+": " + str(exc))
            new_values.append(values)
        # convert these values into 'modes' by transposing the separate columns
        # of values into sets of values with one set per row.
        modes = map(tuple, transposed(new_values))

        if context: # If context has been specified, compare against previous reffile
            current = refmatch.find_current_reffile(filename,context)
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
                self._check_column_values(modes,current_modes)

class LogicalValidator(KeywordValidator):
    """Validate booleans."""
    _values = ["T","F"]

class NumericalValidator(KeywordValidator):
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
            if value < min or value > max:
                raise ValueError("Value for " + repr(self.name) + " of " +
                    repr(value) + " is outside acceptable range " +
                    self._info.values[0])
        else:   # First try a simple exact string match check
            KeywordValidator._check_value(self, value)

class IntValidator(NumericalValidator):
    """Validates integer values."""
    condition = int

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

class RealValidator(FloatValidator):
    """Validate 32-bit floats."""

class DoubleValidator(FloatValidator):
    """Validate 64-bit floats."""
    epsilon = 1e-14

class PedigreeValidator(KeywordValidator):
    """Validates &PREDIGREE fields.
    """
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

class SybdateValidator(KeywordValidator):
    """Check &SYBDATE Sybase date fields."""
    def check_value(self, filename, value):
        timestamp.Sybdate.get_datetime(value)

class SlashdateValidator(KeywordValidator):
    """Validates &SLASHDATE fields."""
    def check_value(self, filename, value):
        timestamp.Slashdate.get_datetime(value)

class AnydateValidator(KeywordValidator):
    """Validates &ANYDATE fields."""
    def check_value(self, filename, value):
        timestamp.Anydate.get_datetime(value)

class FilenameValidator(KeywordValidator):
    """Validates &FILENAME fields."""
    def check_value(self, filename, value):
        return (value == "(initial)") or not os.path.dirname(value)

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

VALIDATOR_CACHE = {}
def get_validators(filename):
    """Given a reference file `filename`,  return the observatory specific
    list of Validators used to check that reference file type.
    """
    # Find the observatory's locator module based on the reference file.
    locator = utils.reference_to_locator(filename)

    # Get the cache key for this filetype.
    key = locator.reference_name_to_validator_key(filename)

    if key not in VALIDATOR_CACHE:
        # Get tpninfos in an observatory specific way, a sequence of tuples.
        tpninfos = tuple(locator.get_tpninfos(*key))
        # Make and cache Validators for `filename`s reference file type.
        VALIDATOR_CACHE[key] = [validator(x) for x in tpninfos]

    # Return a list of Validator's for `filename`
    return VALIDATOR_CACHE[key]

# ============================================================================

def certify_reference(fitsname, context=None,
                      dump_provenance=False, trap_exceptions=False):
    """Given reference file path `fitsname`,  fetch the appropriate Validators
    and check `fitsname` against them.
    """
    try:
        validation = validate_file_format(fitsname)
    except Exception:
        if trap_exceptions:
            log.error("FITS file verification failed for "+fitsname)
            return
        else:
            raise IOError
    if validation == NOT_FITS:
        return

    if dump_provenance:
        provenance_keys = ["DESCRIP", "COMMENT", "PEDIGREE", "USEAFTER",
                                  "HISTORY",]
        parkeys = get_rmap_parkeys(fitsname, context)
        dump_multi_key(fitsname, parkeys + provenance_keys)

    header = data_file.get_header(fitsname)

    certify_simple_parameters(fitsname, context, trap_exceptions, header)

    certify_reference_modes(fitsname, context, trap_exceptions, header)

def certify_simple_parameters(fitsname, context, trap_exceptions, header):
    """Check non-column parameters."""
    for checker in get_validators(fitsname):
        if checker._info.keytype != 'C':
            # validate other values independently
            try:
                checker.check(fitsname, header=header) # validate against TPN values
            except Exception, exc:
                if trap_exceptions:
                    log.error("Checking", repr(checker._info.name), "in",
                              repr(fitsname), ":", str(exc))
                else:
                    raise

def certify_reference_modes(fitsname, context, trap_exceptions, header):
    """Check column parameters row-by-row."""
    mode_checker = None # Initialize mode validation
    for checker in get_validators(fitsname):
        # Treat column validations together as a 'mode'
        if checker._info.keytype == 'C':
            checker.check(fitsname, header=header) # validate values against TPN valid values
            if mode_checker is None:
                mode_checker = ModeValidator(checker._info)
            mode_checker.add_column(checker)

    if mode_checker: # Run validation on all collected modes
        try:
            mode_checker.check(fitsname, context=context, header=header)
        except Exception, exc:
            if trap_exceptions:
                log.error("Checking", repr(mode_checker.names), "in",
                          repr(fitsname), ":", str(exc))
            else:
                raise

def dump_multi_key(fitsname, keys):
    """Dump out all header values for `keys` in all extensions of `fitsname`."""
    hdulist = pyfits.open(fitsname)
    for i, hdu in enumerate(hdulist):
        cards = hdu.header.ascardlist()
        for key in keys:
            for card in cards:
                if card.key == key:
                    if interesting_value(card.value):
                        log.info("["+str(i)+"]", key, card.value, card.comment)

def interesting_value(value):
    """Return True IFF `value` isn't uninteresting."""
    if str(value).strip().lower() in ["",
                                 "*** end of mandatory fields ***",
                                 "*** column names ***",
                                 "*** column formats ***"]:
        return False
    return True

def get_rmap_parkeys(refname, context):
    """Determine required parkeys in reference path `refname` according to pipeline
    mapping `context`.
    """
    if context is None:
        return []
    try:
        pmap = rmap.get_cached_mapping(context)
        instrument, filekind = pmap.locate.get_file_properties(refname)
        return pmap.get_imap(instrument).get_rmap(filekind).get_required_parkeys()
    except Exception, exc:
        log.verbose_warning("Failed retrieving required parkeys:", str(exc))
        return []

def validate_file_format(fitsname):
    """ Run PyFITS verify method on file to report any FITS format problems
        with the input file.
    """
    # Not strictly necessary when pyfits.verify gets used...
    #if '.fits' not in fitsname[-5:]:
    #    log.warning('Reference file '+fitsname+' not a FITS file. No validation done.')
    #    return NOT_FITS

    try:
        f = pyfits.open(fitsname)
        f.verify(option='exception') # validates all keywords
        log.info("FITS file "+fitsname+" conforms to FITS standards.")
        f.close()
    except Exception, exc:
        log.error("FITS file "+fitsname+" does not comply with FITS format!")
        log.error(exc)
        raise IOError
    return VALID_FITS

def certify_context(filename, context=None, check_references=None, trap_exceptions=False):
    """Certify `context`.  Unless `shallow` is True,  recursively certify all
    referenced files as well.
    """
    ctx = rmap.get_cached_mapping(filename)
    ctx.validate_mapping(trap_exceptions=trap_exceptions)
    if not check_references: # Accept None or False
        return
    assert check_references in ["exist", "contents"], \
        "invalid check_references parameter " + repr(check_references)
    references = []
    for ref in ctx.reference_names():
        log.info('Validating reference file: '+ref)
        #
        # The location of reference files on disk need to be determined more
        # robustly based on these 2 options
        #
        try:
            where = rmap.locate_file(ref, ctx.observatory)
            if not os.path.exists(where):
                where = ctx.locate.locate_server_reference(ref)
        except:
            where = ref
        if os.path.exists(where):
            references.append(where)
        else:
            if trap_exceptions:
                log.error("Can't find reference file " + repr(where))
            else:
                raise ValidationError("Missing reference file " + repr(ref))

    if check_references == "contents":
        certify_files(references, context=context,
                      check_references=check_references,
                      trap_exceptions=trap_exceptions)

class MissingReferenceError(RuntimeError):
    """A reference file mentioned by a mapping isn't in CRDS yet."""

def certify_files(files, context=None, dump_provenance=False,
                  check_references=None, is_mapping=False, trap_exceptions=True):

    if not isinstance(files,list):
        files = [files]
    n = 0
    for filename in files:
        n += 1
        bname = os.path.basename(filename)
        log.info('#'*40)  # Serves as demarkation for each file's report
        log.info("Certifying", repr(bname)+ ' ('+str(n)+'/'+str(len(files))+')')
        try:
            if is_mapping or rmap.is_mapping(filename):
                certify_context(filename, context=context,
                                check_references=check_references,
                                trap_exceptions=trap_exceptions)
            else:
                certify_reference(filename, context=context,
                                  dump_provenance=dump_provenance,
                                  trap_exceptions=trap_exceptions)
        except Exception, exc:
            if trap_exceptions:
                log.error("Validation error in " + repr(bname) + " : " + str(exc))
            else:
                raise

def transposed(lists):
   if not lists: return []
   return map(lambda *row: list(row), *lists)

def main():
    """Perform checks on each of `files`.   Print status.   If file is a
    context/mapping file,  it is used to define associated reference files which
    are located on the CRDS server.  If file is a .fits file,  it should include
    a relative or absolute filepath.
    """
    import crds
    crds.handle_version()
    parser = optparse.OptionParser("usage: %prog [options] <inpaths...>")
    parser.add_option("-d", "--deep", dest="deep",
        help="Certify reference files referred to by mappings have valid contents.",
        action="store_true")
    parser.add_option("-e", "--exist", dest="exist",
        help="Certify reference files referred to by mappings exist.",
        action="store_true")
    parser.add_option("-m", "--mapping", dest="mapping",
        help="Ignore extensions, the files being certified are mappings.",
        action="store_true")
    parser.add_option("-p", "--dump-provenance", dest="provenance",
        help="Dump provenance keywords.", action="store_true")
    parser.add_option("-t", "--trap-exceptions", dest="trap_exceptions",
        help="Capture exceptions at level: pmap, imap, rmap, selector, debug, none",
        type=str, default="selector")
    parser.add_option("-x", "--context", dest="context",
        help="Pipeline context defining replacement reference.",
        type=str, default=None)

    options, args = log.handle_standard_options(sys.argv, parser=parser)

    if options.deep:
        check_references = "contents"
    elif options.exist:
        check_references = "exist"
    else:
        check_references = None

    if options.trap_exceptions == "none":
        options.trap_exceptions = False

    assert (options.context is None) or rmap.is_mapping(options.context), \
        "Specified --context file " + repr(options.context) + " is not a CRDS mapping."

    log.standard_run("certify_files(args[1:], context=options.context, dump_provenance=options.provenance, check_references=check_references, is_mapping=options.mapping, trap_exceptions=options.trap_exceptions)",
                     options, globals(), locals())
    log.standard_status()
    return log.errors()

# ============================================================================

if __name__ == "__main__":
    main()
