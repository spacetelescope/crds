"""This module defines functions for loading HST's CDBS .tpn files which
describe header parameters and their values.   The .tpn files are used to
validate headers in the original CDBS system and list the parameters each
file kind must define.
"""
import sys
import os
import os.path
import re

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
        
    def __repr__(self):
        return self.__class__.__name__ + "(" + repr(self._info) + ")"

    def check(self, fitsname, keyname, header=None):
        
        if header is None:
            header = pyfits.getheader(fitsname)

        value = self._get_value(fitsname, keyname, header)
        log.verbose("Checking ", repr(fitsname), "keyword", repr(keyname), "=", repr(value))
        if value is None: # missing optional or excluded keyword
            return

        if self._info.keytype == "H":
            self.check_header(value)
        elif self._info.keytype == "C":
            self.check_column(value)
        elif self._info.keytype == "G":
            self.check_group(value)
        else:
            raise ConfigError("Unknown TPN keytype " + repr(self._info.keytype) + " for " + repr(self._info.name))
        
    def check_header(self, value):
        raise NotImplementedError("")
    def check_column(self, value):
        raise NotImplementedError("")
    def check_group(self, value):
        raise NotImplementedError("")

    def _get_value(self, fitsname, keyname, header):
        try:
            value = header[keyname]
        except KeyError:
            if self._info.presence in ["R","P"]:
                raise MissingKeywordError("File " + repr(fitsname) + " is missing required keyword " + repr(keyname))
            else:
                sys.exc_clear()
                return None
        if self._info.presence == "E":
            raise IllegalKeywordError("File " + repr(fitsname) + " should *not define* keyword " + repr(keyname))
        return value
    

class StringValidator(KeywordValidator):
    def __init__(self, info):
        KeywordValidator.__init__(self, info)
        self._values = [s.upper() for s in self._info.values]

    def check_header(self, value):
        value = str(value).upper()
        if " " in value:
            value = '"' + "_".join(value.split()) + '"'
        if self._values != [] and value not in self._values:
            raise ValueError("String value for " + repr(self._info.name) + " of " + repr(value) + " is not one of " + repr(self._values))
        
class FloatValidator(KeywordValidator):
    def __init__(self, info):
        KeywordValidator.__init__(self, info)
        self._floats = [float(x) for x in self._info.values]
        
    def check_header(self, value):
        if float(value) not in self._floats:
            raise ValueError("Float value for " + repr(self._info.name) + " of " + repr(value) + " is not one of " + repr(self._floats))

class IntValidator(KeywordValidator):
    def __init__(self, info):
        KeywordValidator.__init__(self, info)
        self._ints = [int(x) for x in self._info.values]
        
    def check_header(self, value):
        if int(value) not in self._ints:
            raise ValueError("Int value for " + repr(self._info.name) + " of " + repr(value) + " is not one of " + repr(self._ints))

class PedigreeValidator(KeywordValidator):
    def check_header(self, value):
        try:
            pedigree, start, stop = value.split()
        except ValueError:
            log.verbose("Pedigree value for" + repr(self._info.name) + " of " + repr(value) + " does not unpack into (pedigree, start_date, stop_date).")
            pedigree = value
            start = stop = None
        pedigree = pedigree.upper()
        if pedigree not in ["INFLIGHT","GROUND","MODEL","DUMMY"]:
            raise ValueError("Illegal PEDIGREE " + repr(value))
        if start is not None:
            timestamp.Slashdate.get_datetime(start)
        if stop is not None:
            timestamp.Slashdate.get_datetime(stop)
        
class SybdateValidator(KeywordValidator):
    def check_header(self, value):
        timestamp.Sybdate.get_datetime(value)
        
class SlashdateValidator(KeywordValidator):
    def check_header(self, value):
        timestamp.Slashdate.get_datetime(value)

class AnydateValidator(KeywordValidator):
    def check_header(self, value):
        timestamp.Anydate.get_datetime(value)
        
class FilenameValidator(KeywordValidator):
    def check_header(self, value):
        return (value == "(initial)") or not os.path.dirname(value)

def validator(info):
    if info.datatype == "C":
        if len(info.values) == 1 and len(info.values[0]) and info.values[0][0] == "&":
            func = eval(info.values[0][1:].capitalize() + "Validator")
            return func(info)
        else:
            return StringValidator(info)
    elif info.datatype == "R":
        return FloatValidator(info)
    elif info.datatype == "I":
        return IntValidator(info)
    else:
        raise ValueError("Unimplemented datatype " + repr(info.datatype))

