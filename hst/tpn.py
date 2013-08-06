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
of it's purpose to the corresponding TPN.   Reference file's typically identify 
their purpose using the FILETYPE keyword.

There are several additional complications not forseen at the time this was 
originally written:

1. The CDBS reference file database has a different matching value
vocabulary than reference files described by the _ld.tpn files.
The _ld.tpn files describe the keyword values of expanded
reference file keywords which are to be loaded into the CDBS database.

In CRDS,  these could describe the valid values for .rmaps,   but
in practice they are redundant with a combination of the .tpn files
and the .rules/substitutions.dat file.   The CRDS rmap valid values
maps should eventually be computed from these.


The values in CRDS mapping files for HST are the discrete parameter
settings a particular dataset might have been using.  In contrast, the
values in reference files describe the sets of dataset values to which
the reference applies.  (There is an additional subtlety that dataset
keywords are not always matched to identically named reference file
keywords; e.g.  DATE-OBS, TIME-OBS matches to USEAFTER.)  Further, the
values in reference files are subject to substitution rules described
in the CDBS .rules files and captured in crds.hst's substitutions.dat
file.  CRDS reference file keywords are described in the CDBS .tpn
files.  

It should be noted that the initial CRDS mappings for HST were derived
from the CDBS database.  The CDBS database lists only discrete
parameter values for reference files, not the un-substituted
/unexploded wildcard values.  In addition, the substitution rules of
CDBS changed over time, so there's no guarantee that current
substitution patterns will be found for all reference files.   While the
CRDS mapping generator does re-cluster the exploded CDBS database
into relatively compact rules using or-globs,  it does not attempt
to reverse wild card substitutions.   Consequently mapping files use
the exploded CDBS keyword vocabulary defined by the _ld.tpn files.

2. CDBS refines the basic pipeline -> instrument -> filetype hiearchy down one
additional level,  pipeline -> instrument -> filetype -> subtype.

This applies for reference file values only (.tpn, not _ld.tpn) but
not dataset/mapping values. The additional level of constraint
specialization is keyed off values in the reference file itself,
currently OBSTYPE=IMAGING or OBSTYPE=SPECTROSCOPIC mapping to
stis_ipfl.tpn, stis_ilfl.tpn, stis_spfl.tpn, stis_lpfl.tpn.  In CRDS
these should be referred to as "subtypes".  Note that there's an
asymmetry here and mapping's / _ld.tpn's don't currrently support
subtype values.

"""
import sys
import os.path
import pprint
from collections import defaultdict

from crds import rmap, log, utils, data_file
from crds.certify import TpnInfo

# =============================================================================

HERE = os.path.dirname(__file__) or "./"

# =============================================================================

def _evalfile_with_fail(filename):
    """Evaluate and return a dictionary file,  returning {} if the file
    cannot be found.
    """
    if os.path.exists(filename):
        result = utils.evalfile(filename)
    else:
        log.warning("Couldn't load CRDS config file", repr(filename))
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

# CRDS encoding of most of CDBS catalog.dat
TPN_CATALOG = _evalfile_with_fail(HERE + "/crds_tpn_catalog.dat")

# =============================================================================

class CdbsCat(object):
    """Represents one record from cdbscatalog.dat,  i.e. one filekind."""
    
    #INST   REFTYPE FTYPE   TEMPLATE FILE   EXT    HEADER KEYWORDS
    
    def __init__(self, inst, reftype, ftype, template, ext, *args):
        self.inst = inst
        self.reftype = reftype
        self.ftype = ftype
        self.template = template
        self.ext = ext
        self.header_items = self.parse_header(args)
        self.header = dict(self.header_items) 
    
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
        header = []
        for assgn in header_keywords:
            if not assgn:
                continue
            key, val = [x.strip() for x in assgn.split("=")]
            header.append((key.lower(),val.lower()))
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

# =============================================================================

def make_filetype_to_extension():
    """Generate a map  { instrument : { filetype : suffix_ext }}
    
    This function is only known to work for acs, cos, nicmos, stis, wfc3, wfpc, 
    wfpc2.
    """
    table = defaultdict(dict)
    for cat in _load_cdbs_catalog():
        instr = cat.header.get("instrument", cat.inst)
        if instr == "nic":
            instr = "nicmos"
        filetype = cat.header.get("filetype", cat.reftype).lower()
        table[instr][filetype] = cat.reftype # suffix_ext
    return dict(table)

def make_crds_tpn_catalog():
    """Process cdbscatalog.dat to create a mapping { instrument : { filekind : catalog_info } }
    """
    table = defaultdict(dict)
    skipped = defaultdict(set)
    for cat in _load_cdbs_catalog():
        instr = cat.header.get("instrument", cat.inst)
        if instr == "nic":
            instr = "nicmos"
        filetype = cat.header.get("filetype", cat.reftype).lower()
        try:
            filekind = filetype_to_filekind(instr, filetype)
        except:
            skipped[instr].add(filetype)
            continue
        if filekind not in table[instr]:
            table[instr][filekind] = []
        if len(cat.header_items) > 2:
            table[instr][filekind].append(
                (tuple(cat.header_items[2:]), (cat.template, cat.reftype, cat.ftype, cat.ext, filetype)))
        else:
            table[instr][filekind] = (cat.template, cat.reftype, cat.ftype, cat.ext, filetype)
    for instr in sorted(skipped):
        log.info("Skipped", repr(instr), "=", repr(sorted(skipped[instr])))
    return dict(table)

# =============================================================================

def filetype_to_filekind(instrument, filetype):
    """Map the value of a FILETYPE keyword onto it's associated
    keyword name,  i.e.  'dark image' --> 'darkfile'
    """
    instrument = instrument.lower()
    filetype = filetype.lower()
    if instrument == "nic":
        instrument = "nicmos"
    ext = FILETYPE_TO_SUFFIX[instrument][filetype]
    return SUFFIX_TO_FILEKIND[instrument][ext]

def extension_to_filekind(instrument, extension):
    """Map the value of an instrument and TPN extension onto it's
    associated filekind keyword name,  i.e. drk --> darkfile
    """
    if instrument == "nic":
        instrument = "nicmos"
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

@utils.cached
def load_tpn(fname):
    return _load_tpn(fname)


# =============================================================================

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

TPN_DIR_PATH = os.path.join(HERE, "cdbs", "cdbs_tpns")

def _implicit_tpn_filepath(instrument, filekind):
    """Return the full path for the .tpn file corresponding to `instrument` and 
    `filekind`,  the CRDS name for the header keyword which refers to this 
    reference.
    """
    if instrument == "wfpc2":
        file_suffix = WFPC2_HACK[filekind]
    else:
        file_suffix = FILEKIND_TO_SUFFIX[instrument][filekind]
    return os.path.join(TPN_DIR_PATH, INSTRUMENT_TO_TPN[instrument] + "_" + file_suffix + ".tpn")

def get_tpninfos(*args):
    """Load the list of TPN_info tuples corresponding to *args from it's .tpn file.
    Nominally args are (instrument, filekind),  but *args should be supported to 
    handle *key for any key returned by reference_name_to_validator_key.   In particular,
    for some subtypes,  *args will be (tpn_filename,).
    """
    if len(args) == 2:  # hackish,  should be (instrument, filekind)
        return load_tpn(_implicit_tpn_filepath(*args))
    else:  # should be explicit filename
        return load_tpn(os.path.join(TPN_DIR_PATH, args[0]))

# =============================================================================

def reference_name_to_validator_key(filename):
    """Given a reference filename `fitsname`,  return a dictionary key
    suitable for caching the reference type's Validator.
    
    Return (instrument, filekind)
    """
    header = data_file.get_header(filename)
    instrument = header["INSTRUME"].lower()
    filetype = header["FILETYPE"].lower()
    filekind = filetype_to_filekind(instrument, filetype)
    cat_info = TPN_CATALOG[instrument][filekind]
    if isinstance(cat_info, tuple):
        key = (cat_info[0],)  # tpn filename
    else:
        for (condition, cat) in cat_info:
            for (cvar, cval) in condition:
                hval = header.get(cvar.upper(), None)
                if hval != cval.upper():
                    break
            else:
                key = (cat[0],)  # tpn filename
                break
        else:
            raise ValueError("No TPN match for reference='{}' instrument='{}' reftype='{}'" % \
                                 (os.path.basename(filename), instrument, filekind))
    log.verbose("Validator key for", repr(filename), instrument, filekind, "=", key)
    return key

# =============================================================================

def reference_name_to_tpninfos(key):
    """Given a reference cache `key` for a reference's Validator,  return the 
    TpnInfo object which can be used to construct a Validator.
    """
    return get_tpninfos(*key)

# =============================================================================

def _update_tpn_data(pipeline_context):
    """Update the data files which relate reftypes, filekinds, and tpn
    extensions,  all somewhat redundant ways of saying the same thing,
    but the way HST is.
    """
    # XXX temporary for refactoring tpn_filetypes.dat
    log.info("Computing TPN filetype map")    
    tpn_filetypes = make_filetype_to_extension()
    open("tpn_filetypes.dat", "w+").write(pprint.pformat(tpn_filetypes))
                                          
    log.info("Computing CRDS catalog from CDBS catalog.dat")
    catalog = make_crds_tpn_catalog()
    open("crds_tpn_catalog.dat", "w+").write(pprint.pformat(catalog, width=200))
    
    log.standard_status()
    
if __name__ == "__main__":
    if len(sys.argv) == 2:
        _update_tpn_data(sys.argv[1])
    else:
        print "usage: python tpn.py <pipeline_context,  e.g. hst.pmap>"


