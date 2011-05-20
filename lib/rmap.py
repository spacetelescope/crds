"""This module supports loading all the data components required to make
a CRDS lookup table for an instrument.

get_cached_mapping loads the closure of the given context file from the
local CRDS store,  caching the result.

>>> p = get_cached_mapping("hst.pmap")

Mappings round-trip through json OK:

>>> _ = p.to_json()
>>> p = PipelineContext.from_json(_)

The initial HST pipeline mappings are self-consistent and there are none
missing:

>>> p.missing_mappings()
[]

The available HST reference data seems to have a number of ACS 
references missing relative to the CDBS HTML table dump:

>>> len(p.missing_references())
88

There are 72 pmap, imap, and rmap files in the entire HST pipeline:

>>> len(p.mapping_names())
72

There are 5719 reference files known to the initial CRDS mappings scraped
from the CDBS HTML table dump:

>>> len(p.reference_names())
5719

Pipeline reference files are also broken down by instrument:

>>> sorted(p.reference_name_map().keys())
['acs', 'cos', 'stis', 'wfc3']

>>> i = InstrumentContext.from_file("hst_acs.imap", "hst", "acs")
>>> _ = i.to_json()
>>> i = InstrumentContext.from_json(_)

The ACS instrument has 15 associated mappings,  including the instrument context:

>>> len(i.mapping_names())
15

The ACS instrument has 3983 associated reference files in the hst_acs.imap context:

>>> len(i.reference_names())
3983

Active instrument references are also broken down by filetype:

>>> sorted(i.reference_name_map()["crrejtab"])
['n4e12510j_crr.fits', 'n4e12511j_crr.fits']

>>> r = ReferenceMapping.from_file("hst_acs_biasfile.rmap", "hst", "acs", "biasfile")
>>> _ = r.to_json()
>>> r = ReferenceMapping.from_json(_)
>>> len(r.reference_names())
729
"""
import os
import os.path
import re

try:
    from collections import namedtuple
except:
    from crds.collections2 import namedtuple

try:
    from ast import literal_eval
except:
    literal_eval = lambda expr: eval(expr, {}, {})

try:
    import json
except:
    import simplejson as json

from crds import log, timestamp, utils
from crds.config import CRDS_ROOT

# ===================================================================

Filetype = namedtuple("Filetype","header_keyword,extension,rmap")
Failure = namedtuple("Failure","header_keyword,message")
Filemap = namedtuple("Filemap","date,file,comment")

# ===================================================================

class MappingError(Exception):
    """Exception in load_rmap."""
    def __init__(self, *args):
        Exception.__init__(self, " ".join([str(x) for x in args]))
        
class FormatError(MappingError):
    "Something wrong with context or rmap file format."
    pass

# ===================================================================

class Mapping(object):
    """An Mapping is the abstract baseclass for loading anything with the
    general structure of a header followed by data.
    """
    def __init__(self, filename, header, data, **keys):
        self.filename = filename
        self.header = header
        self.data = data
        
    def __repr__(self):
        r = self.__class__.__name__ + "("
        for attr in self.check_attrs:
            r += attr + "=" + repr(getattr(self, attr)) + ", "
        r = r[:-2] + ")"
        return r
            
    @classmethod
    def check_file_format(cls, filename):
        """Make sure the basic file format for `filename` is valid and safe."""
        lines = open(filename).readlines()
        clean = cls._clean_lines(lines)
        basename = os.path.basename(filename)
        remainder = cls._check_syntax(basename, "header", clean)
        remainder = cls._check_syntax(basename, "data", remainder)
        if remainder != ["},"]:
            raise FormatError("Extraneous input following data in " + repr(basename))
    
    @classmethod
    def _clean_lines(cls, lines):
        """Remove empty lines and comment lines"""
        clean = []
        for line in lines:
            line = line.strip()
            if (not line) or line.startswith("#"):
                continue
            clean.append(line.strip())
        return clean

    @classmethod
    def _key_value_split(cls, line):
        """Split line on first : not inside quoted string or tuple."""
        inside_quote = False
        inside_tuple = 0
        for index, char in enumerate(line):
            if char == "'":
                inside_quote = not inside_quote
            elif inside_quote:
                continue
            elif char == '(':
                inside_tuple += 1
            elif char == ')':
                inside_tuple -= 1
            elif char == ":" and (not inside_quote) and (not inside_tuple):
                key = line[:index]
                value = line[index+1:]
                value = value.split("#")[0]
                return key.strip(), value.strip()
        return line, None

    @classmethod
    def _check_syntax(cls, filename, section, lines):
        if not re.match("^(}, )?{$", lines[0]):
            raise FormatError("Invalid %s block opening in " % (section,) + repr(filename))        
        for lineno, line in enumerate(lines[1:]):
            key, value = cls._key_value_split(line)
            if key in ["}", "}, {"] and value is None:
                break
            elif key == "}," and value is None:
                continue
            elif not cls._match_key(key):
                raise FormatError("Invalid %s keyword " % section + repr(key) + " in " + repr(filename))
            elif not cls._match_value(value):
                raise FormatError("Invalid %s value for " % section + key + " = " + repr(value) + " in " + repr(filename))
        return lines[lineno+1:]  # should be no left-overs

    @classmethod
    def _match_key(cls, key):
        return cls._match_simple(key) or cls._match_string_tuple(key)
    
    @classmethod
    def _match_value(cls, value):
        return (value == "{") or cls._match_simple(value) or cls._match_string_tuple(value)

    @classmethod
    def _match_simple(cls, value):
        return re.match("^'[A-Za-z0-9_.:/ \*\%\-]*',?$", value)
    
    @classmethod
    def _match_string_tuple(cls, value):
        return re.match("^\((\s*'[A-Za-z0-9_.:/ \*\%\-]*',?\s*)*\),?$", value)

    @classmethod
    def from_file(cls, basename, *args, **keys):
        """Load a mapping file `basename` and do syntax and basic validation.
        """
        # Convert the mapping basename into an absolute path by first looking
        # up the "locate" module for the observatory and then calling locate_mapping().
        observatory = utils.context_to_observatory(basename)
        locate = utils.get_object("crds." + observatory + ".locate")
        where = locate.locate_mapping(basename)
        
        cls.check_file_format(where)
        try:
            header, data = literal_eval(open(where).read())
        except Exception, exc:
            raise MappingError("Can't load", cls.__name__, "file:", repr(os.path.basename(where)), str(exc))
        mapping = cls(basename, header, data, *args, **keys)
        mapping.validate_file_load()
        return mapping
    
    def validate_file_load(self):
        """Validate assertions about the contents of this rmap."""
        for name in self.check_attrs:
            self.check_header_attr(name)
#        if "parkey" not in self.header:
#            raise MappingError("Missing header keyword: 'parkey'.")
    
    def missing_references(self):
        """Get the references mentioned by the closure of this mapping but not known to CRDS."""
        return [ ref for ref in self.reference_names() if not self.locate.reference_exists(ref)]

    def missing_mappings(self):
        """Get the references mentioned by the closure of this mapping but not known to CRDS."""
        return [ mapping for mapping in self.mapping_names() if not self.locate.mapping_exists(mapping)]

    def check_header_attr(self, name):
        """Verify that the mapping header keyword `name` exists and matches self's attribute value.
        """
        attr = getattr(self, name)
        if not attr:   # skip empty-strings as don't care
            return
        try:
            hdr = self.header[name].lower()
        except KeyError:
            raise MappingError("Missing header keyword:", repr(name))
        if hdr != attr:
            raise MappingError("Header mismatch. Expected",repr(name),"=",repr(attr),"but got",name,"=",repr(hdr))
            
    def to_json(self):
        """Encode this Mapping as a string of JSON.
        """
        rmap = dict(header=self.header, data=self.data, filename=self.filename)
        return json.dumps(keys_to_strings(rmap))
    
    @classmethod
    def from_json(cls, json_str):
        """Decode a string of JSON from to_json() into a Mapping.
        """
        rmap = strings_to_keys(json.loads(json_str))
        header = rmap["header"]
        data = rmap["data"]
        filename = rmap["filename"]
        return cls(filename, header, data, **header)
    
    @property
    def locate(self):
        """Return the "locate" module associated with self.observatory.
        """
        if not hasattr(self, "_locate"):
            self._locate = utils.get_object("crds." + self.observatory + ".locate")
        return self._locate
    
# ===================================================================

def keys_to_strings(d):
    """Convert non-string keys of `d` into strings for json encoding."""
    if not isinstance(d, dict):
        return d
    results = {}
    for key, value in d.items():
        converted = keys_to_strings(value)
        if not isinstance(key, (str, unicode)):
            results[repr(key)] = converted
        else:
            results[key] = converted
    return results
    
def strings_to_keys(d):
    """Convert string keys of `d` which contain tuple reprs back into tuples.""" 
    if not isinstance(d, dict):
        return d
    results = {}
    for key, value in d.items():
        converted = strings_to_keys(value)
        if isinstance(key, (str, unicode)) and "(" in key:
            results[literal_eval(key)] = converted
        else:
            results[key] = converted
    return results

# ===================================================================

"""
{
    'observatory':'HST',
    'parkey' : ('INSTRUME'),
}, {
    'ACS': 'hst_acs_00023.imap',
    'COS':'hst_cos_00023.imap', 
    'STIS':'hst_stis_00023.imap',
    'WFC3':'hst_wfc3_00023.imap',
    'NICMOS':'hst_nicmos_00023.imap',
}
"""



class PipelineContext(Mapping):
    """A pipeline context describes the context mappings for each instrument
    of a pipeline.
    """
    check_attrs = ["observatory"]

    def __init__(self, filename, header, data, observatory="", **keys):
        Mapping.__init__(self, filename, header, data)
        self.observatory = observatory.lower()
        self.selections = {}
        for instrument, imap in data.items():
            instrument = instrument.lower()
            self.selections[instrument] = InstrumentContext.from_file(imap, observatory, instrument)

    def get_best_references(self, header, date=None):
        """Return the best references for keyword map `header`.
        """
        header = dict(header.items())
        instrument = header["INSTRUME"].lower()
        if date == "now":
            date = timestamp.now()
        if date:
            header["DATE"] = date
        else:
            header["DATE"] = header["DATE-OBS"] + " " + header["TIME-OBS"]
        header["DATE"] = timestamp.reformat_date(header["DATE"])
        return self.selections[instrument].get_best_references(header)
    
    def reference_names(self):
        """Return the list of reference files associated with this pipeline context."""
        files = set()
        for instrument_files in self.reference_name_map().values():
            files.update(instrument_files)
        return sorted(files)

    def reference_name_map(self):
        """Returns { instrument : [ref_file_name...] ... }"""
        files = {}
        for instrument in self.selections:
            files[instrument] = set() 
            for reftype_files in self.selections[instrument].reference_name_map().values():
                files[instrument].update(set(reftype_files))
        return files
    
    def mapping_names(self):
        """Return the list of pipeline, instrument, and reference map files associated with
        this pipeline context.
        """
        files = set([os.path.basename(self.filename)])
        for instrument in self.selections:
            files.update(self.selections[instrument].mapping_names())
        return sorted(list(files))

    def tpn_map(self):
        """Return the map of 3 character tpn extensions used by CDBS:  
        
        { instrument : { reftype : extension } }
        """
        tpns = {}
        for instrument, instr_sel in self.selections.items():
            tpns[instrument] = {}
            for reftype, reftype_sel in instr_sel.selections.items():
                tpns[instrument][reftype] = reftype_sel.extension
        return tpns

# ===================================================================

"""
{
    'observatory':'HST',
    'instrument': 'ACS',
    'parkey' : ('REFTYPE',),
}, {
    'BIAS':  'hst_acs_bias_0021.rmap',
    'CRREJ': 'hst_acs_crrej_0003.rmap',
    'CCD':   'hst_acs_ccd_0002.rmap',
    'IDC':   'hst_acs_idc_0005.rmap',
    'LIN':   'hst_acs_lin_0002.rmap',
    'DISTXY':'hst_acs_distxy_0004.rmap',
    'BPIX':  'hst_acs_bpic_0056.rmap',
    'MDRIZ': 'hst_acs_mdriz_0001.rmap',
    ...
}
"""

class InstrumentContext(Mapping):
    """An instrument context describes the rmaps associated with each filetype
    of an instrument.
    """
    check_attrs = ["observatory","instrument"]

    def __init__(self, filename, header, data, observatory="", instrument="", **keys):
        Mapping.__init__(self, filename, header, data)
        self.observatory = observatory.lower()
        self.instrument = instrument.lower()
        self.selections = {}
        for reftype, rmap_info in data.items():
            rmap_ext, rmap_name = rmap_info
            self.selections[reftype] = ReferenceMapping.from_file(
                rmap_name, self.observatory, self.instrument, reftype, rmap_ext)

    def get_best_ref(self, reftype, header):
        """Returns the single reference file basename appropriate for `header`
        corresponding to `reftype`.
        """
        return self.selections[reftype.lower()].get_best_ref(header)

    def get_best_references(self, header):
        """Returns a map of best references { reftype : reffile_basename } 
        appropriate for this `header`.
        """
        refs = {}
        for reftype in self.selections:
            log.verbose("\nGetting bestref for", repr(reftype))
            try:
                refs[reftype] = self.get_best_ref(reftype, header)
            except Exception, e:
                refs[reftype] = "NOT FOUND " + str(e)
        return refs

    def get_binding(self, header):
        """Given a header,  return the binding of all keywords pertinent to all reftypes
        for this instrument.
        """
        binding = {}
        for reftype in self.selections:
            binding.update(self.selections[reftype].get_binding(header))
        return binding
    
    def reference_names(self):
        """Returns [ref_file_name...]
        """
        files = set()
        for reftype_files in self.reference_name_map().values():
            files.update(set(reftype_files))
        return sorted(files)

    def reference_name_map(self):
        """Returns { reftype : set( ref_file_name... ) }
        """
        files = {}
        for reftype, selector in self.selections.items():
            files[reftype] = sorted(selector.reference_names())
        return files
    
    def mapping_names(self):
        """Returns a list of mapping files associated with this InstrumentContext."""
        files = [os.path.basename(self.filename)]
        for selector in self.selections.values():
            files.append(os.path.basename(selector.filename))
        return files
    
# ===================================================================

class ReferenceMapping(Mapping):
    """ReferenceMapping manages loading the rmap associated with a single reference
    filetype and instantiating an appropriate selector from the rmap header and data.
    """
    check_attrs = ["observatory","instrument","reftype"]
    
    def __init__(self, filename, header, data, observatory="", instrument="", reftype="", extension="", **keys):
        Mapping.__init__(self, filename, header, data)
        self.instrument = instrument.lower()
        self.observatory = observatory.lower()
        self.reftype = reftype.lower()
        self.extension = extension.lower()
        cls = utils.get_object(header.get("class", "crds.selectors.ReferenceSelector"))
        self._selector = cls(header, data)
        
    def get_best_ref(self, header):
        """Return the single reference file basename appropriate for `header` selected
        by this ReferenceMapping.
        """
        return self._selector.choose(header)
    
    def reference_names(self):
        """Return the list of reference file basenames associated with this ReferenceMapping.
        """
        return self._selector.reference_names()
    
# ===================================================================

def write_rmap(filename, header, data):
    """Write out the specified `header` and `data` to `filename` in rmap format."""
    file = open(filename,"w+")
    write_rmap_dict(file, header)
    write_rmap_dict(file, data)
    file.write("\n")

def write_rmap_dict(file, the_dict, indent_level=1):
    """Write out a (nested) dictionary in a simple format amenable to validation
    and differencing.
    """
    indent = " "*4*indent_level
    file.write("{\n")
    for key, value in the_dict.items():
        file.write(indent + repr(key) + " : ")
        if isinstance(value, dict):
            write_rmap_dict(file, value, indent_level+1)
        elif isinstance(value, Filemap):
            file.write(repr(value.file) + ", #" + value.comment + "\n")
        else:
            file.write(repr(value) + ",\n")
    indent_level -= 1
    if indent_level > 0:
        file.write(indent_level*" "*4 + "},\n")
    else:
        file.write("}, ")
        
# ===================================================================

CACHED_MAPPINGS = {}

def get_cached_mapping(mapping_basename):
    """Retrieve the Mapping corresponding to the specified 
    `mapping_basename` from the global mapping cache,  recursively
    loading and caching it if it has not already been cached.
    
    Return a PipelineContext, InstrumentContext, or ReferenceMapping.
    """
    if mapping_basename not in CACHED_MAPPINGS:
        CACHED_MAPPINGS[mapping_basename] = load_mapping(mapping_basename)
    return CACHED_MAPPINGS[mapping_basename]

def load_mapping(mapping):
    """Load any of the pipeline, instrument, or reftype `mapping`s
    from the file system.
    """
    observatory = utils.context_to_observatory(mapping)
    if mapping.endswith(".pmap"):
        return PipelineContext.from_file(mapping, observatory)
    elif mapping.endswith(".imap"):
        instrument = utils.context_to_instrument(mapping)
        return InstrumentContext.from_file(mapping, observatory, instrument)
    elif mapping.endswith(".rmap"):
        instrument = utils.context_to_instrument(mapping)
        reftype = utils.context_to_reftype(mapping)
        return ReferenceMapping.from_file(mapping, observatory, instrument, reftype)
    else:
        raise ValueError("Unknown mapping extension for " + repr(mapping))
    
def is_mapping(mapping):
    """Return True IFF `mapping` has an extension indicating a CRDS mapping file.
    """
    return mapping.endswith((".pmap",".imap",".rmap"))

# ===================================================================

def get_best_references(context_file, header):
    """Compute the best references for `header` for the given CRDS `context_file`.   This
    is a local computation using local rmaps and CPU resources.
    """
    ctx = get_cached_mapping(context_file)
    return ctx.get_best_references(header)


def test():
    """Run module doctests."""
    import doctest, rmap
    return doctest.testmod(rmap)

if __name__ == "__main__":
    print test()

