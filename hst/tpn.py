"""This module defines functions for loading HST's CDBS .tpn files which
describe header parameters and their values.   The .tpn files are used to
validate headers in the original CDBS system and list the parameters each
file kind must define.
"""
import sys
import os
import os.path

import pyfits

try:
    from collections import namedtuple
except ImportError:
    from crds.collections2 import namedtuple
    
from crds import rmap, log, timestamp

def get_tpn_map(pipeline_context_name):
    """
    Return the map of 3 character tpn extensions used by CDBS:  
        
    { instrument : { reftype : extension } }
    """
    context = rmap.get_cached_mapping(pipeline_context_name)
    tpns = {}
    for instrument, instr_sel in context.selections.items():
        tpns[instrument] = {}
        for reftype, reftype_sel in instr_sel.selections.items():
            current = tpns.get(reftype, None)
            if current and reftype_sel.extension != current:
                log.error("Conflicting extensions for reftype", 
                          repr(current), "and", repr(reftype_sel.extension))
            tpns[instrument][reftype] = reftype_sel.extension
    return tpns

TPN_EXTENSIONS = {                 
 'acs': {'atodtab': 'a2d',
         'biasfile': 'bia',
         'bpixtab': 'bpx',
         'ccdtab': 'ccd',
         'cfltfile': 'cfl',
         'crrejtab': 'crr',
         'darkfile': 'drk',
         'dgeofile': 'dxy',
         'idctab': 'idc',
         'mdriztab': 'mdz',
         'mlintab': 'lin',
         'oscntab': 'osc',
         'pfltfile': 'pfl',
         'spottab': 'csp'},
 'cos': {'badttab': 'badt',
         'bpixtab': 'bpix',
         'brftab': 'brf',
         'brsttab': 'burst',
         'deadtab': 'dead',
         'disptab': 'disp',
         'flatfile': 'flat',
         'geofile': 'geo',
         'lamptab': 'lamp',
         'phatab': 'pha',
         'phottab': 'phot',
         'tdstab': 'tds',
         'wcptab': 'wcp',
         'xtractab': '1dx'},
 'stis': {'apdstab': 'apd',
          'apertab': 'apt',
          'biasfile': 'bia',
          'bpixtab': 'bpx',
          'ccdtab': 'ccd',
          'cdstab': 'cds',
          'crrejtab': 'crr',
          'darkfile': 'drk',
          'disptab': 'dsp',
          'echsctab': 'ech',
          'exstab': 'exs',
          'halotab': 'hal',
          'idctab': 'idc',
          'inangtab': 'iac',
          'lamptab': 'lmp',
          'lfltfile': 'lfl',
          'mlintab': 'lin',
          'mofftab': 'moc',
          'pctab': 'pct',
          'pfltfile': 'pfl',
          'phottab': 'pht',
          'riptab': 'rip',
          'sdctab': 'sdc',
          'sptrctab': '1dt',
          'srwtab': 'srw',
          'tdctab': 'tdc',
          'tdstab': 'tds',
          'wcptab': 'wcp',
          'xtractab': '1dx'},
 'wfc3': {'biasfile': 'bia',
          'bpixtab': 'bpx',
          'ccdtab': 'ccd',
          'crrejtab': 'crr',
          'darkfile': 'drk',
          'idctab': 'idc',
          'mdriztab': 'mdz',
          'nlinfile': 'lin',
          'oscntab': 'osc',
          'pfltfile': 'pfl'}
 }

def load_tpn_lines(fname):
    """Load the lines of a CDBS .tpn file,  ignoring #-comments, blank lines,
     and joining lines ending in \\.
    """
    lines = []
    append = False
    for line in open(fname):
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        if append:
            lines[-1] = lines[-1][:-1] + line
        else:
            lines.append(line)
        append = line.endswith("\\")
    return lines


def fix_quoted_whitespace(line):
    """Replace spaces and tabs which appear inside quotes in `line` with
    underscores,  and return it.
    """
    i = 0
    while i < len(line):
        char = line[i]
        i += 1
        if char != '"':
            continue
        quote = char
        while i < len(line):
            char = line[i]
            i += 1
            if char == quote:
                break
            if char in " \t":
                line = line[:i-1] + "_" + line[i:]
    return line

TpnInfo = namedtuple("TpnInfo", "name,keytype,datatype,presence,values")

def load_tpn(fname):
    """Load a TPN file and return it as a dictionary mapping header
    keywords onto their properties, including acceptable values.
    """
    tpn = {}
    for line in load_tpn_lines(fname):
        line = fix_quoted_whitespace(line)
        items = line.split()
        if len(items) == 4:
            name, keytype, datatype, presence = items
            values = []
        else:
            name, keytype, datatype, presence, values = items
            values = values.split(",")
        tpn[name] = validator(TpnInfo(name, keytype, datatype, presence, values))
    return tpn


# Correspondence between instrument names and TPN file name <instrument> field.
INSTRUMENT_TO_TPN = {
    "acs" : "acs",
    "cos" : "cos",
    "stis" : "stis",
    "wfc3" : "wfc3",
    "wfpc2" : "wp2",
    "nicmos" : "nic",
}

HERE = os.path.dirname(__file__) or "./"

def tpn_filepath(instrument, extension):
    """Return the full path for the .tpn file corresponding to `instrument` and 
    CDBS filetype `extension`."""
    return os.path.join(HERE, "cdbs", "cdbs_tpns",
            INSTRUMENT_TO_TPN[instrument] + "_" + extension + ".tpn")

def get_tpn(instrument, extension):
    """Load the map of TPN_info tuples corresponding to `instrument` and 
    `extension` from it's .tpn file.
    """
    return load_tpn(tpn_filepath(instrument, extension))

# ===========================================================================================================

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
        assert False,  "Group keys were not expected and not implemented."

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

