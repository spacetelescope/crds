"""This module defines replacement functionality for the CDBS "certify" program
used to check parameter values in .fits reference files.   It verifies that FITS
files define required parameters and that they have legal values.
"""
import sys
import os
import optparse
import re

import pyfits

from crds import rmap, log, timestamp, utils, data_file
from crds.compat import namedtuple
from crds.rmap import ValidationError

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
        if self._info.presence not in ["R", "P", "E", "O"]:
            raise ValueError("Bad TPN presence field " +
                             repr(self._info.presence))
        if self.condition is not None:
            self._values = [self.condition(value) for value in info.values]

    def condition(self, value):
        """Condition `value` to standard format for this Validator."""
        return value

    def __repr__(self):
        return self.__class__.__name__ + "(" + repr(self._info) + ")"

    def check(self, filename, header=None):
        """Pull the value(s) corresponding to this Validator out of it's
        `header` or the contents of the file.   Check them against the
        requirements defined by this Validator.
        """
        if self._info.keytype == "H":
            self.check_header(filename, header)
        elif self._info.keytype == "C":
            self.check_column(filename)
        elif self._info.keytype == "G":
            self.check_group(filename)
        else:
            raise ValueError(
                "Unknown TPN keytype " + repr(self._info.keytype) + " for " +
                repr(self._info.name))

    def check_value(self, filename, value):
        """Check a single header or column value against the legal values
        for this Validator.
        """
        log.verbose("Checking ", repr(filename), "keyword",
                    repr(self._info.name), "=", repr(value))
        if value is None: # missing optional or excluded keyword
            return
        if self.condition is not None:
            value = self.condition(value)
        if not self._values:
            return
        self._check_value(value)

    def _check_value(self, value):
        if value not in self._values and self._values != ('*',):
            if isinstance(value, str):
                for pat in self._values:
                    if re.match(pat, value):
                        return
            raise ValueError("Value for " + repr(self._info.name) + " of " +
                             repr(value) + " is not one of " +
                             repr(self._values))

    def check_header(self, filename, header=None):
        """Extract the value for this Validator's keyname,  either from `header`
        or from `filename`'s header if header is None.   Check the value.
        """
        if header is None:
            header = data_file.get_header(filename)
        value = self._get_header_value(header)
        self.check_value(filename, value)

    def check_column(self, filename):
        """Extract a column of values from `filename` and check them all against
        the legal values for this Validator.
        """
        values = None
        try:
            values = self._get_column_values(filename)
        except Exception, exc:
            raise RuntimeError("Can't read column values : " + str(exc))
        if values is not None: # Only check for non-optional columns
            for i, value in enumerate(values):
                self.check_value(filename + "[" + str(i) +"]", value)

    def check_group(self, filename):
        """Probably related to pre-FITS HST GEIS files,  not implemented."""
        assert False, "Group keys were not expected and not implemented."

    def _get_header_value(self, header):
        """Pull this Validator's value out of `header` and return it.
        Handle the cases where the value is missing or excluded.
        """
        try:
            value = header[self._info.name]
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
                and self._info.name in extn.data.names:
                    col_extn = extn
                    break
        # If no extension could be found with that column, report as missing
        if col_extn is None:
            # close FITS handle
            hdu.close()
            return self.__handle_missing()

        # If it was found, return the values
        tbdata = col_extn.data
        values = tbdata.field(self._info.name)

        # close FITS handle
        hdu.close()
        return self.__handle_excluded(values)

    def __handle_missing(self):
        """This Validator's key is missing.   Either raise an exception or
        ignore it depending on whether this Validator's key is required.
        """
        if self._info.presence in ["R","P"]:
            raise MissingKeywordError(
                "Missing required keyword " + repr(self._info.name))
        else:
            sys.exc_clear()

    def __handle_excluded(self, value):
        """If this Validator's key is excluded,  raise an exception.  Otherwise
        return `value`.
        """
        if self._info.presence == "E":
            raise IllegalKeywordError(
                "*Must not define* keyword " + repr(self._info.name))
        return value

class CharacterValidator(KeywordValidator):
    """Validates values of type Character."""
    def condition(self, value):
        chars = str(value).strip().upper()
        if " " in chars:
            chars = '"' + "_".join(chars.split()) + '"'
        return chars

class LogicalValidator(KeywordValidator):
    """Validate booleans."""
    _values = ["T","F"]

class NumericalValidator(KeywordValidator):
    def __init__(self, info):
        KeywordValidator.__init__(self, info)
        self.is_range = len(info.values) == 1 and ":" in info.values[0]
        if self.is_range:
            smin, smax = info.values[0].split(":")
            self.min, self.max = self.condition(smin), self.condition(smax)

    def _check_value(self, value):
        if self.is_range:
            if value < min or value > max:
                raise ValueError("Value for " + repr(self._info.name) + " of " +
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
    condition = None

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
    condition = None
    def check_value(self, filename, value):
        timestamp.Sybdate.get_datetime(value)

class SlashdateValidator(KeywordValidator):
    """Validates &SLASHDATE fields."""
    condition = None
    def check_value(self, filename, value):
        timestamp.Slashdate.get_datetime(value)

class AnydateValidator(KeywordValidator):
    """Validates &ANYDATE fields."""
    condition = None
    def check_value(self, filename, value):
        timestamp.Anydate.get_datetime(value)

class FilenameValidator(KeywordValidator):
    """Validates &FILENAME fields."""
    condition = None
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

def certify_reference(fitsname, dump_provenance=False, trap_exceptions=False):
    """Given reference file path `fitsname`,  fetch the appropriate Validators
    and check `fitsname` against them.
    """
    if dump_provenance:
        dump_multi_key(fitsname, ["DESCRIP", "COMMENT", "PEDIGREE", "USEAFTER",
                                  "HISTORY",])
    for checker in get_validators(fitsname):
        try:
            checker.check(fitsname)
        except Exception:
            if trap_exceptions:
                log.error("Checking", repr(checker._info.name), "in",
                          repr(fitsname))
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
                    log.write("["+str(i)+"]", key, card.value, card.comment)

def certify_context(context, check_references=None, trap_exceptions=False):
    """Certify `context`.  Unless `shallow` is True,  recursively certify all
    referenced files as well.
    """
    ctx = rmap.get_cached_mapping(context)
    ctx.validate_mapping(trap_exceptions=trap_exceptions)
    if check_references is None:
        return
    assert check_references in ["exist", "contents"], \
        "invalid check_references parameter"
    references = []
    for ref in ctx.reference_names():
        where = rmap.locate_file(ref, ctx.observatory)
        if os.path.exists(where):
            references.append(where)
        else:
            if trap_exceptions:
                log.error("Can't find reference file " + repr(where))
            else:
                raise ValidationError("Missing reference file " + repr(ref))
    if check_references == "contents":
        certify_files(references, check_references=check_references,
                      trap_exceptions=trap_exceptions)

class MissingReferenceError(RuntimeError):
    """A reference file mentioned by a mapping isn't in CRDS yet."""

def certify_files(files, dump_provenance=False, check_references=None,
                  is_mapping=False, trap_exceptions=True):

    if not isinstance(files,list):
        files = [files]

    for filename in files:
        bname = os.path.basename(filename)
        log.info("Certifying", repr(bname))
        try:
            if is_mapping or rmap.is_mapping(filename):
                certify_context(filename, check_references=check_references,
                                trap_exceptions=trap_exceptions)
            else:
                certify_reference(filename, dump_provenance=dump_provenance,
                                  trap_exceptions=trap_exceptions)
        except Exception:
            if trap_exceptions:
                log.error("Validation error in " + repr(bname))
            else:
                raise

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

    options, args = log.handle_standard_options(sys.argv, parser=parser)

    if options.deep:
        check_references = "contents"
    elif options.exist:
        check_references = "exist"
    else:
        check_references = None

    if options.trap_exceptions == "none":
        options.trap_exceptions = False

    log.standard_run("certify_files(args[1:], dump_provenance=options.provenance, check_references=check_references, is_mapping=options.mapping, trap_exceptions=options.trap_exceptions)",
                     options, globals(), locals())
    log.standard_status()
    return log.errors()

# ============================================================================

if __name__ == "__main__":
    main()
