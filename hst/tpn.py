"""This module defines functions for loading HST's CDBS .tpn files which
describe reference parameters and their values.   The .tpn files are used to
validate headers or tables in the original CDBS system and list the parameters 
each filekind must define.   This module also loads the file cdbscatalog.dat
which defines naming relationships for each filekind with respect to TPNs.
Whereas filekinds tend to be 7-8 character header keywords,  TPNs refer to the 
same thing,  essentially a type of reference file,  using a 3-or-so character 
filename suffix or extension.

There's a lot of entropy here given HST's 20 year history and changes in 
convention and file formatting.   Originally file extensions conveyed both format
and purpose.   Later with the switch to .fits filenames convey only format and
a TPN suffix conveys purpose.  This suffix generally but not always seems to be
named "reftype" in cdbscatalog.dat.

CRDS terminology is derived from the CDBS web site instrument indices.  Those
pages display an "extension" column which is included in CRDS imaps and called,
not surprisingly, "extension".   That "extension" column seems to correspond 
to cdbscatalog.dat column "ext" and "reftype" combined, depending on file format.
For .fits,  CRDS extension == catalog reftype.  For supported non-FITS,  CRDS
extension == catalog ext.

The importance of sorting all this out is being able to map 
{ filekind : tpn_file } by combining info from the CDBS web pages with info
in cdbscatalog.dat.

Another somewhat difficult mapping is going from a reference file's description
of it's purpose to the corresponding TPN.   Reference file's identify their
purpose using the FILETYPE keyword.
"""
import sys
import os.path
import pprint

from crds import rmap, log, utils, data_file
from crds.certify import TpnInfo

# =============================================================================

HERE = os.path.dirname(__file__) or "./"

# =============================================================================

def _update_tpn_data(pipeline_context):
    """Update the data files which relate reftypes, filekinds, and tpn
    extensions,  all somewhat redundant ways of saying the same thing,
    but the way HST is.
    """
    log.info("Computing TPN filetype map")    
    tpn_filetypes = get_filetype_to_extension(pipeline_context)
    tpn_filetypes["nicmos"] = tpn_filetypes.pop("nic")   # XXX hack
    open("tpn_filetypes.dat", "w+").write(pprint.pformat(tpn_filetypes))
    log.standard_status()
    
# =============================================================================

def _evalfile_with_fail(filename):
    """Evaluate and return a dictionary file,  returning {} if the file
    cannot be found.
    """
    if os.path.exists(filename):
        result = utils.evalfile(filename)
    else:
        result = {}
    return result

def _invert_instr_dict(map):
    """Invert a set of nested dictionaries of the form {instr: {key: val}}
    to create a dict of the form {instr: {val: key}}.
    """
    inverted = {}
    for instr in map:
        inverted[instr] = utils.invert_dict(map[instr])
    return inverted

# .e.g. FILEKIND_TO_SUFFIX = {                 
# 'acs': {'atodtab': 'a2d',
#         'biasfile': 'bia',
FILEKIND_TO_SUFFIX = _evalfile_with_fail(HERE + "/filekind_ext.dat")
SUFFIX_TO_FILEKIND = _invert_instr_dict(FILEKIND_TO_SUFFIX)

#.e.g. FILETYPE_TO_SUFFIX = {
# 'acs': {'analog-to-digital': 'a2d',
#         'bad pixels': 'bpx',
FILETYPE_TO_SUFFIX = _evalfile_with_fail(HERE + "/tpn_filetypes.dat")
SUFFIX_TO_FILETYPE = _invert_instr_dict(FILETYPE_TO_SUFFIX)


# =============================================================================

class CdbsCat(object):
    """Represents one record from cdbscatalog.dat,  i.e. one filekind."""
    def __init__(self, inst, reftype, ftype, template, ext, *args):
        self.inst = inst
        self.reftype = reftype
        self.ftype = ftype
        self.template = template
        self.ext = ext
        self.header = self.parse_header(args)
    
    def parse_header(self, args):
        """In general the last parameter in a catalog looks like this:

        "key=value,key=value".   
        
        parse_header() is called with the split() of the trailing parameters of
        the catalog record.  parse_header() recombines them separated by a single
        space and converts the result into a dictionary:
        
        { key: value, key: value }.

        The splitting and recombination is lossy with respect to whitespace but
        works for existing records.
        """
        header_keywords = " ".join(args)
        if header_keywords.startswith('"'):
            header_keywords = header_keywords[1:-1]
        header_keywords = header_keywords.split(",")
        header = {}
        for assgn in header_keywords:
            if not assgn:
                continue
            key, val = [x.strip() for x in assgn.split("=")]
            header[key] = val  
        return header

    def __repr__(self):
        rep = "CdbsCat("
        for name in "inst,reftype,ftype,template,ext,header".split(","):
            rep += name + "=" + repr(getattr(self, name)) + ", "
        return rep[:-2] + ")"

def _load_cdbs_catalog():
    """Return a list of CdbsCat objects read from cdbscatalog.dat"""
    catpath = os.path.join(HERE, "cdbs", "cdbs_tpns","cdbscatalog.dat")
    catalog = []
    for line in open(catpath):
        line = line.strip()
        if line.startswith("#") or "_ld.tpn" in line:
            continue
        words = line.split()
        catalog.append(CdbsCat(*words))
    return catalog

CDBS_CATALOG = _load_cdbs_catalog()

# =============================================================================

def get_filetype_to_extension(context):
    """Generate a map  { instrument : { filetype : suffix_ext }}
    
    This function is only known to work for acs, cos, nicmos, stis, wfc3, wfpc, 
    wfpc2.
    """
    map = {}
    for cat in CDBS_CATALOG:
        instr = cat.header.get("instrument", cat.inst)
        if instr not in map:
            map[instr] = {}
        filetype = cat.header.get("filetype", cat.reftype).lower()
        suffix_ext = cat.reftype
#       if cat.ext == ".fits":
#       else:
#            suffix_ext = cat.ext
        map[instr][filetype] = suffix_ext
    return map

# =============================================================================

def filetype_to_filekind(instrument, filetype):
    """Map the value of a FILETYPE keyword onto it's associated
    keyword name,  i.e.  'dark image' --> 'darkfile'
    """
    instrument = instrument.lower()
    filetype = filetype.lower()
    ext = FILETYPE_TO_SUFFIX[instrument][filetype]
    return SUFFIX_TO_FILEKIND[instrument][ext]

def extension_to_filekind(instrument, extension):
    """Map the value of an instrument and TPN extension onto it's
    associated filekind keyword name,  i.e. drk --> darkfile
    """
    return SUFFIX_TO_FILEKIND[instrument][extension]

# =============================================================================

def _load_tpn_lines(fname):
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


def _fix_quoted_whitespace(line):
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

def _load_tpn(fname):
    """Load a TPN file and return it as a list of TpnInfo objects
    describing keyword requirements including acceptable values.
    """
    tpn = []
    for line in _load_tpn_lines(fname):
        line = _fix_quoted_whitespace(line)
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


WFPC2_HACK = {'atodfile': 'a2d',
           'biasfile': 'bas',
           'darkfile': 'drk',
           # 'deltadark': '.r6h',
           'dgeofile': 'dxy',
           'flatfile': 'flt',
           'idctab': 'idc',
           'maskfile': 'msk',
           'offtab': 'off',
           'shadfile': 'shd',
           'wf4tfile': 'w4t'
}

def _tpn_filepath(instrument, filekind):
    """Return the full path for the .tpn file corresponding to `instrument` and 
    `filekind`,  the CRDS name for the header keyword which refers to this 
    reference.
    """
    rootpath = os.path.join(
        HERE, "cdbs", "cdbs_tpns", INSTRUMENT_TO_TPN[instrument])
    if instrument == "wfpc2":
        file_suffix = WFPC2_HACK[filekind]
    else:
        file_suffix = FILEKIND_TO_SUFFIX[instrument][filekind]
    path = rootpath + "_" + file_suffix + ".tpn"
    return path

def get_tpninfos(instrument, filekind):
    """Load the map of TPN_info tuples corresponding to `instrument` and 
    `extension` from it's .tpn file.
    """
    return _load_tpn(_tpn_filepath(instrument, filekind))

# =============================================================================

def reference_name_to_validator_key(filename):
    """Given a reference filename `fitsname`,  return a dictionary key
    suitable for caching the reference type's Validator.
    
    Return (instrument, filekind)
    """
    header = data_file.get_header(filename)
    instrument = header["INSTRUME"].lower()
    filetype = header["FILETYPE"].lower()
    extension = FILETYPE_TO_SUFFIX[instrument][filetype]
    filekind = SUFFIX_TO_FILEKIND[instrument][extension]
    return (instrument, filekind)

# =============================================================================

def reference_name_to_tpninfos(key):
    """Given a reference cache `key` for a reference's Validator,  return the 
    TpnInfo object which can be used to construct a Validator.
    """
    return get_tpninfos(*key)

# =============================================================================

INSTRUMENTS = FILEKIND_TO_SUFFIX.keys()

FILEKINDS = set()
for instr in FILEKIND_TO_SUFFIX:
    FILEKINDS.update(FILEKIND_TO_SUFFIX[instr].keys())
FILEKINDS = list(FILEKINDS)

# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) == 2:
        _update_tpn_data(sys.argv[1])
    else:
        print "usage: python tpn.py <pipeline_context,  e.g. hst.pmap>"


