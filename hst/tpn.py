"""This module defines functions for loading HST's CDBS .tpn files which
describe reference parameters and their values.   The .tpn files are used to
validate headers or tables in the original CDBS system and list the parameters 
each file kind must define.
"""
import os.path

import pyfits

from crds import rmap, log

from crds.certify import TpnInfo

# =============================================================================

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

EXTENSION_TO_FILEKIND = {}
for instrument in TPN_EXTENSIONS:
    if instrument not in EXTENSION_TO_FILEKIND:
        EXTENSION_TO_FILEKIND[instrument] = {}
    EXTENSION_TO_FILEKIND[instrument] = dict( \
        [(val,key) for (key,val) in TPN_EXTENSIONS[instrument].items()])

def filetype_to_filekind(instrument, filetype):
    """Map the value of a FILETYPE keyword onto it's associated
    keyword name,  i.e.  'dark image' --> 'darkfile'
    """
    instrument = instrument.lower()
    filetype = filetype.lower()
    ext = FILETYPE_TO_EXTENSION[instrument][filetype]
    return EXTENSION_TO_FILEKIND[instrument][ext]

def extension_to_filekind(instrument, extension):
    """Map the value of an instrument and TPN extension onto it's
    associated filekind keyword name,  i.e. drk --> darkfile
    """
    return EXTENSION_TO_FILEKIND[instrument][extension]
    

# =============================================================================

INSTRUMENTS = ["acs", "cos", "stis", "wfc3"]

def get_filetype_map(context):
    """Generate the FILETYPE_TO_EXTENSION map below."""
    pipeline = rmap.get_cached_mapping(context)
    fmap = {}
    for instr in INSTRUMENTS:
        fmap[instr] = {}
    for i, name in enumerate(pipeline.reference_names()):
        ext = name.split("_")[1].split(".")[0].lower()
        hst = rmap.get_cached_mapping("hst.pmap")
        print "Scanning", i, name
        try:
            where = hst.locate.locate_server_reference(name)
        except KeyError:
            log.error("Missing reference file", repr(name))
            continue
        try:
            header = pyfits.getheader(where)
            filetype = header["FILETYPE"].lower()
            instrument = header["INSTRUME"].lower()
        except IOError: 
            log.error("Error getting FILETYPE for", repr(where))
        current = fmap.get(filetype, None)
        if current and current != ext:
            log.error("Multiple extensions for", repr(filetype), 
                      repr(current), repr(ext))
            continue
        if filetype not in fmap[instrument]:
            fmap[instrument][filetype] = ext
            log.info("Setting", repr(instrument), repr(filetype),
                     "to extension", repr(ext))
    return fmap

# FILETYPE_TO_EXT = get_filetype_map("hst.pmap")

FILETYPE_TO_EXTENSION = {
 'acs': {'analog-to-digital': 'a2d',
         'bad pixels': 'bpx',
         'bias': 'bia',
         'ccd parameters': 'ccd',
         'cosmic ray rejection': 'crr',
         'dark': 'drk',
         'distortion coefficients': 'idc',
         'distortion correction': 'dxy',
         'linearity': 'lin',
         'multidrizzle parameters': 'mdz',
         'overscan': 'osc',
         'pixel-to-pixel flat': 'pfl',
         'spot flat': 'cfl',
         'spot position table': 'csp'},
 'cos': {'1-d extraction parameters table': '1dx',
         'bad time intervals table': 'badt',
         'baseline reference frame table': 'brf',
         'burst parameters table': 'burst',
         'data quality initialization table': 'bpix',
         'deadtime reference table': 'dead',
         'dispersion relation reference table': 'disp',
         'flat field reference image': 'flat',
         'geometric distortion reference image': 'geo',
         'photometric sensitivity reference table': 'phot',
         'pulse height parameters reference table': 'pha',
         'template cal lamp spectra table': 'lamp',
         'time dependent sensitivity table': 'tds',
         'wavecal parameters reference table': 'wcp'},
 'stis': {'1-d extraction parameter table': '1dx',
          '1-d spectrum trace table': '1dt',
          '2-d spectrum distortion correction table': 'sdc',
          'aperture description table': 'apd',
          'aperture throughput table': 'apt',
          'bad pixel table': 'bpx',
          'ccd bias image': 'bia',
          'ccd parameters table': 'ccd',
          'cosmic ray rejection table': 'crr',
          'cross-disperser scattering table': 'cds',
          'dark correction table': 'tdc',
          'dark image': 'drk',
          'detector halo table': 'hal',
          'dispersion coefficients table': 'dsp',
          'echelle cross-dispersion scattering table': 'exs',
          'echelle ripple table': 'rip',
          'image distortion correction table': 'idc',
          'incidence angle correction table': 'iac',
          'low-order flatfield image': 'lfl',
          'mama linearity table': 'lin',
          'mama offset correction table': 'moc',
          'photometric correction table': 'pct',
          'pixel-to-pixel flatfield image': 'pfl',
          'scattering reference wavelengths table': 'srw',
          'template cal lamp spectra table': 'lmp',
          'time dependent sensitivity table': 'tds',
          'wavecal parameters table': 'wcp'},
 'wfc3': {'bad pixels': 'bpx',
          'bias': 'bia',
          'ccd parameters': 'ccd',
          'cosmic ray rejection': 'crr',
          'dark': 'drk',
          'distortion coefficients': 'idc',
          'linearity coefficients': 'lin',
          'multidrizzle parameters': 'mdz',
          'overscan': 'osc',
          'pixel-to-pixel flat': 'pfl'}
}

# =============================================================================

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

def load_tpn(fname):
    """Load a TPN file and return it as a list of TpnInfo objects
    describing keyword requirements including acceptable values.
    """
    tpn = []
    for line in load_tpn_lines(fname):
        line = fix_quoted_whitespace(line)
        items = line.split()
        if len(items) == 4:
            name, keytype, datatype, presence = items
            values = []
        else:
            name, keytype, datatype, presence, values = items
            values = values.split(",")
        tpn.append(TpnInfo(name, keytype, datatype, presence, tuple(values)))
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
    CDBS filetype `extension`.
    """
    return os.path.join(HERE, "cdbs", "cdbs_tpns",
            INSTRUMENT_TO_TPN[instrument] + "_" + extension + ".tpn")

def get_tpninfos(instrument, extension):
    """Load the map of TPN_info tuples corresponding to `instrument` and 
    `extension` from it's .tpn file.
    """
    return load_tpn(tpn_filepath(instrument, extension))

# =============================================================================

def reference_name_to_validator_key(fitsname):
    """Given a reference filename `fitsname`,  return a dictionary key
    suitable for caching the reference type's Validator.
    """
    header = pyfits.getheader(fitsname)
    instrument = header["INSTRUME"].lower()
    filetype = header["FILETYPE"].lower()
    extension = FILETYPE_TO_EXTENSION[instrument][filetype]
    return (instrument, extension)

def reference_name_to_tpninfos(fitsname, key):
    """Given a reference filename `fitsname` and the associated cache `key`
    for the reference's Validator,  return the TpnInfo object which can be
    used to construct the Validator.
    """
    if key is None:
        key = reference_name_to_validator_key(fitsname)
    return get_tpninfos(*key)
