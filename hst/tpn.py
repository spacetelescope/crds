"""This module defines functions for loading HST's CDBS .tpn files which
describe header parameters and their values.   The .tpn files are used to
validate headers in the original CDBS system and list the parameters each
file kind must define.
"""
import sys
import os
import os.path
import re

import pyfits

try:
    from collections import namedtuple
except ImportError:
    from crds.collections2 import namedtuple
    
from crds import config, rmap, log, timestamp

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
    i = 0
    while i < len(line):
        c = line[i]
        i += 1
        if c != '"':
            continue
        quote = c
        while i < len(line):
            c = line[i]
            i += 1
            if c == quote:
                break
            if c in " \t":
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
    """Load the map of TPN_info tuples corresponding to `instrument` and `extension` from it's .tpn file."""
    return load_tpn(tpn_filepath(instrument, extension))

# ===========================================================================================================

class MissingKeywordError(Exception):
    """A required keyword was not defined."""
    
class IllegalKeywordError(Exception):
    """A keyword which should not be defined was present."""

class KeywordValidator(object):
    def __init__(self, info):
        self._info = info
        if self._info.presence not in ["R","P","E","O"]:
            raise ValueError("Bad TPN presence field " + repr(self._info.presence))
        if self.condition is not None:
            self._values = [self.condition(value) for value in info.values]

    def condition(self, value):
        """Condition `value` to standard format for this Validator."""
        return value
            
    def __repr__(self):
        return self.__class__.__name__ + "(" + repr(self._info) + ")"

    def check(self, filename, keyname, header=None):
        if self._info.keytype == "H":
            self.check_header(filename, keyname, header)
        elif self._info.keytype == "C":
            self.check_column(filename, keyname)
        elif self._info.keytype == "G":
            self.check_group(filename, keyname)
        else:
            raise ConfigError("Unknown TPN keytype " + repr(self._info.keytype) + " for " + repr(self._info.name))
        
    def check_value(self, filename, keyname, value):
        log.verbose("Checking ", repr(filename), "keyword", repr(keyname), "=", repr(value))
        if value is None: # missing optional or excluded keyword
            return
        if self.condition is not None:
            value = self.condition(value)
        if self._values != [] and value not in self._values:
            raise ValueError(self._type + " value for " + repr(self._info.name) + " of " + repr(value) + " is not one of " + repr(self._values))
        
    def check_header(self, filename, keyname, header=None):
        if header is None:
            header = pyfits.getheader(filename)
        value = self._get_header_value(filename, keyname, header)
        self.check_value(filename, keyname, value)
        
    def check_column(self, filename, keyname):
        values = self._get_column_values(filename, keyname)
        for i, value in enumerate(values):
            self.check_value(filename, keyname + "[" + str(i) +"]", value)

    def check_group(self, filename, keyname):
        raise NotImplementedError("group checking " + repr(self._info.name))

    def _get_header_value(self, filename, keyname, header):
        try:
            value = header[keyname]
        except KeyError:
            return self.__handle_missing(filename, keyname)
        return self.__handle_excluded(filename, keyname, value)
    
    def _get_column_values(self, filename, keyname):
        f = pyfits.open(filename) 
        tbdata = f[1].data
        try:
            values = tbdata.field(keyname)
        except KeyError:
            return self.__handle_missing(filename, keyname)
        return self.__handle_excluded(filename, keyname, values)
    
    def __handle_missing(self, filename, keyname):
        if self._info.presence in ["R","P"]:
            raise MissingKeywordError("File " + repr(filename) + " is missing required keyword " + repr(keyname))
        else:
            sys.exc_clear()
            return None

    def __handle_excluded(self, filename, keyname, value):
        if self._info.presence == "E":
            raise IllegalKeywordError("File " + repr(filename) + " *must not define* keyword " + repr(keyname))
        return value

    @property
    def _type(self):
        return self.__class__.__name__[:-len("Validator")]

class StringValidator(KeywordValidator):
    def condition(self, value):
        s = str(value).strip().upper()
        if " " in s:
            s = '"' + "_".join(s.split()) + '"'
        return s

class IntValidator(KeywordValidator):
    condition = int

class LogicalValidator(KeywordValidator):
    """Validate booleans."""
    _values = ["T","F"]

class FloatValidator(KeywordValidator):
    condition = float
        
class RealValidator(FloatValidator):
    """Validate 32-bit floats."""
    
class DoubleValidator(FloatValidator):
    """Validate 64-bit floats."""
    
class PedigreeValidator(KeywordValidator):
    _values = ["INFLIGHT","GROUND","MODEL","DUMMY"]
    condition = None
    def check_header(self, filename, keyname, header=None):
        if header is None:
            header = pyfits.getheader(filename)
        value = self._get_header_value(filename, keyname, header)
        try:
            pedigree, start, stop = value.split()
        except ValueError:
            log.verbose("Pedigree value for" + repr(self._info.name) + " of " + repr(value) + " does not unpack into (pedigree, start_date, stop_date).")
            pedigree = value
            start = stop = None
        self.check_value(filename, keyname, pedigree)
        if start is not None:
            timestamp.Slashdate.get_datetime(start)
        if stop is not None:
            timestamp.Slashdate.get_datetime(stop)
        
class SybdateValidator(KeywordValidator):
    condition = None
    def check_value(self, filename, keyname, value):
        timestamp.Sybdate.get_datetime(value)
        
class SlashdateValidator(KeywordValidator):
    condition = None
    def check_value(self, filename, keyname, value):
        timestamp.Slashdate.get_datetime(value)

class AnydateValidator(KeywordValidator):
    condition = None
    def check_value(self, filename, keyname, value):
        timestamp.Anydate.get_datetime(value)
        
class FilenameValidator(KeywordValidator):
    condition = None
    def check_value(self, filename, keyname, value):
        return (value == "(initial)") or not os.path.dirname(value)

def validator(info):
    """Given a TpnInfo object `info`,  construct and return a Validator for it."""
    if info.datatype == "C":
        if len(info.values) == 1 and len(info.values[0]) and info.values[0][0] == "&":
            """This block handles &-types like &PEDIGREE and &SYBDATE"""
            func = eval(info.values[0][1:].capitalize() + "Validator")
            return func(info)
        else:
            return StringValidator(info)
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

