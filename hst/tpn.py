"""This module defines functions for loading HST's CDBS .tpn files which
describe reference parameters and their values.   The .tpn files are used to
validate headers or tables in the original CDBS system and list the parameters 
each file kind must define.
"""
import sys
import os.path
import pprint

import pyfits

from crds import rmap, log, utils
from crds.certify import TpnInfo

# =============================================================================

def update_tpn_data(pipeline_context):
    """Update the data files which relate reftypes, filekinds, and tpn
    extensions,  all somewhat redundant ways of saying the same thing,
    but the way HST is.
    """
    log.info("Computing TPN extension map")
    tpn_extensions = get_tpn_map(pipeline_context)
    open("tpn_extensions.dat", "w+").write(pprint.pformat(tpn_extensions))
    log.info("Computing TPN filetype map")    
    tpn_filetypes = get_filetype_map(pipeline_context)
    open("tpn_filetypes.dat", "w+").write(pprint.pformat(tpn_filetypes))
    log.standard_status()
    
# =============================================================================

HERE = os.path.dirname(__file__) or "./"

def get_tpn_map(pipeline_context):
    """
    Return the map of 3 character tpn extensions used by CDBS:  
        
    { instrument : { filekind : extension } }
    """
    context = rmap.get_cached_mapping(pipeline_context)
    tpns = {}
    for instrument, instr_sel in context.selections.items():
        tpns[instrument] = {}
        for filekind, filekind_sel in instr_sel.selections.items():
            current = tpns.get(filekind, None)
            if current and filekind_sel.extension != current:
                log.error("Conflicting extensions for filekind", 
                          repr(current), "and", repr(filekind_sel.extension))
            tpns[instrument][filekind] = instr_sel.extensions[filekind]
    return tpns

# .e.g. TPN_EXTENSIONS = {                 
# 'acs': {'atodtab': 'a2d',
#         'biasfile': 'bia',

try:
    TPN_EXTENSIONS = utils.evalfile(HERE + "/tpn_extensions.dat")
except Exception:
    log.error("Couldn't load tpn_extensions.dat")
    TPN_EXTENSIONS = {}

# =============================================================================

def get_filetype_map(context):
    """Generate the FILETYPE_TO_EXTENSION map below."""
    pipeline = rmap.get_cached_mapping(context)
    fmap = {}
    for instrument, imapping in pipeline.selections.items():
        fmap[instrument] = {}
        for filekind, rmapping in imapping.selections.items():
            for name in rmapping.reference_names():
                log.info("Scanning", instrument, filekind, name)
                try:
                    where = pipeline.locate.locate_server_reference(name)
                except KeyError:
                    log.error("Missing reference file", repr(name))
                    continue
                try:
                    header = pyfits.getheader(where)
                except IOError:
                    log.error("Error getting header/FILETYPE for", repr(where))
                    continue    
                filetype = header["FILETYPE"].lower()
                ext = name.split("_")[1].split(".")[0].lower()
                break
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

#.e.g. FILETYPE_TO_EXTENSION = {
# 'acs': {'analog-to-digital': 'a2d',
#         'bad pixels': 'bpx',

try:
    FILETYPE_TO_EXTENSION = utils.evalfile(HERE + "/tpn_filetypes.dat")
except Exception:
    log.error("Couldn't load tpn_filetypes.dat")
    FILETYPE_TO_EXTENSION = {}

# =============================================================================

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
            lines[-1] = lines[-1][:-1].strip() + line
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
            values = [v.upper() for v in values]
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

def tpn_filepath(instrument, extension):
    """Return the full path for the .tpn file corresponding to `instrument` and 
    CDBS filetype `extension`.
    """
    return os.path.join(HERE, "cdbs", "cdbs_tpns",
            INSTRUMENT_TO_TPN[instrument] + "_" + extension + ".tpn")

def get_tpninfos(instrument, filekind):
    """Load the map of TPN_info tuples corresponding to `instrument` and 
    `extension` from it's .tpn file.
    """
    extension = TPN_EXTENSIONS[instrument][filekind]
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
    filekind = EXTENSION_TO_FILEKIND[instrument][extension]
    return (instrument, filekind)

# =============================================================================

def reference_name_to_tpninfos(key):
    """Given a reference cache `key` for a reference's Validator,  return the 
    TpnInfo object which can be used to construct a Validator.
    """
    return get_tpninfos(*key)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        update_tpn_data(sys.argv[1])
    else:
        print "usage: python tpn.py <pipeline_context,  e.g. hst.pmap>"

