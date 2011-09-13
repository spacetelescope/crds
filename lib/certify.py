"""This module defines replacement functionality for the CDBS "certify" program
used to check parameter values in .fits reference files.   It verifies that FITS
files define required parameters and that they have legal values.
"""
import sys
import os
import optparse

import pyfits 

from crds import rmap, log, timestamp, utils
from crds.compat import namedtuple
    
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
        if self._values != [] and value not in self._values:
            raise ValueError("Value for " + repr(self._info.name) + " of " + 
                             repr(value) + " is not one of " + 
                             repr(self._values))
        
    def check_header(self, filename, header=None):
        """Extract the value for this Validator's keyname,  either from `header`
        or from `filename`'s header if header is None.   Check the value.
        """
        if header is None:
            header = pyfits.getheader(filename)
        value = self._get_header_value(header)
        self.check_value(filename, value)
        
    def check_column(self, filename):
        """Extract a column of values from `filename` and check them all against
        the legal values for this Validator.
        """
        values = self._get_column_values(filename)
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
        # XXX assume tables are in extension #1.
        tbdata = hdu[1].data
        try:
            values = tbdata.field(self._info.name)
        except KeyError:
            return self.__handle_missing()
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

class IntValidator(KeywordValidator):
    """Validates integer values."""
    condition = int

class LogicalValidator(KeywordValidator):
    """Validate booleans."""
    _values = ["T","F"]

class FloatValidator(KeywordValidator):
    """Validates floats of any precision."""
    condition = float
        
class RealValidator(FloatValidator):
    """Validate 32-bit floats."""
    
class DoubleValidator(FloatValidator):
    """Validate 64-bit floats."""
    
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
        tpninfos = tuple(locator.reference_name_to_tpninfos(filename, key))
        # Make and cache Validators for `filename`s reference file type.
        VALIDATOR_CACHE[key] = [validator(x) for x in tpninfos]

    # Return a list of Validator's for `filename`
    return VALIDATOR_CACHE[key]

# ============================================================================

def certify_fits(fitsname):
    """Given reference file path `fitsname`,  fetch the appropriate Validators
    and check `fitsname` against them.
    """
    if OPTIONS.provenance:
        dump_multi_key(fitsname, ["DESCRIP","COMMENT","PEDIGREE","USEAFTER",
                                  "HISTORY",])
    for checker in get_validators(fitsname):
        checker.check(fitsname)

def dump_multi_key(fitsname, keys):
    """Dump out all header values for `keys` in all extensions of `fitsname`."""
    hdulist = pyfits.open(fitsname)
    for i, hdu in enumerate(hdulist):
        cards = hdu.header.ascardlist()
        for key in keys:
            for card in cards:
                if card.key == key:
                    log.write("["+str(i)+"]", key, card.value, card.comment)

def certify_context(context, check_references=False):
    """Certify `context`.  Unless `shallow` is True,  recursively certify all
    referenced files as well.
    Returns the count of errors.
    """
    try:
        ctx = rmap.get_cached_mapping(context)
    except Exception:
        log.error("Couldn't load mapping", repr(context))
        return []
    if not check_references:
        return 0
    return certify(reference_files(ctx))
    
def reference_files(mapping):
    """Returns the list of server reference file paths for `context`."""
    paths = []
    for ref in mapping.reference_names():
        try:
            paths.append(mapping.locate.locate_server_reference(ref))
        except KeyError:
            log.error("Missing reference file", repr(ref))
    return paths

class MissingReferenceError(RuntimeError):
    """A reference file mentioned by a mapping isn't in CRDS yet."""

def certify_mapping(context, check_references=True):
    """Verify that a mapping will load and that all its reference files 
    exist within CRDS.   Otherwise raise an exception.
    """
    ctx = rmap.get_cached_mapping(context)
    if not check_references:
        return
    for ref in ctx.reference_names():
        try:
            ctx.locate.locate_server_reference(ref)
        except KeyError:
            raise MissingReferenceError("Reference file " + repr(ref) + 
                                        " is not known to CRDS." )

def certify(files):
    """Run certify_fits() on a list of FITS `files` logging an error for the 
    first failure in each file,  but continuing.   Returns the count of errors.
    """
    for fname in files:
        log.info("Certifying", repr(os.path.basename(fname)))
        try:
            certify_fits(fname)
        except Exception:
            # raise
            log.error("Validation failed for", repr(fname))
    return log.errors()


def main(files, options):
    """Perform checks on each of `files`.   Print status.   If file is a
    context/mapping file,  it is used to define associated reference files which
    are located on the CRDS server.  If file is a .fits file,  it should include
    a relative or absolute filepath.
    """
    for file_ in files:
        if rmap.is_mapping(file_) or options.mapping:
            certify_context(file_, check_references=(not options.shallow))
        else:
            certify([file_])
    log.standard_status()
    return log.errors()

# ============================================================================

if __name__ == "__main__":
    parser = optparse.OptionParser("usage: %prog [options] <inpaths...>")
    parser.add_option("-s", "--shallow", dest="shallow",
        help="Don't certify referenced files", 
        action="store_true")
    parser.add_option("-m", "--mapping", dest="mapping",
        help="Ignore extensions, the files being certified are mappings.", 
        action="store_true")
    parser.add_option("-P", "--dump-provenance", dest="provenance",
        help="Dump provenance keywords.", action="store_true")
    OPTIONS, ARGS = log.handle_standard_options(sys.argv, parser=parser)
    log.standard_run("main(ARGS[1:], OPTIONS)", OPTIONS, 
                     globals(), globals())

