"""This module supports loading all the data components required to make
a CRDS lookup table for an instrument.
"""
import os
import os.path
import collections
import re
import ast
import json

from crds import log, timestamp, utils
from crds.config import CRDS_ROOT

# ===================================================================

Filetype = collections.namedtuple("Filetype","header_keyword,extension,rmap")
Failure = collections.namedtuple("Failure","header_keyword,message")
Filemap = collections.namedtuple("Filemap","date,file,comment")

# ===================================================================

class RmapError(Exception):
    """Exception in load_rmap."""
    def __init__(self, *args):
        Exception.__init__(self, " ".join([str(x) for x in args]))
        
class FormatError(RmapError):
    "Something wrong with context or rmap file format."
    pass

# ===================================================================

class Rmap(object):
    """An Rmap is the abstract baseclass for loading anything with the
    general structure of a header followed by data.
    """
    def __init__(self, filename, header, data, **keys):
        self.filename = filename
        self.header = header
        self.data = data
    
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
            header, data = ast.literal_eval(open(where).read())
        except Exception, exc:
            raise RmapError("Can't load", cls.__name__, "file:", repr(os.path.basename(where)), str(exc))
        rmap = cls(basename, header, data, *args, **keys)
        rmap.validate_file_load()
        return rmap
    
    def validate_file_load(self):
        """Validate assertions about the contents of this rmap."""
        for name in self.check_attrs:
            self.check_header_attr(name)
#        if "parkey" not in self.header:
#            raise RmapError("Missing header keyword: 'parkey'.")
    
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
            raise RmapError("Missing header keyword:", repr(name))
        if hdr != attr:
            raise RmapError("Header mismatch. Expected",repr(name),"=",repr(attr),"but got",name,"=",repr(hdr))
            
    def to_json(self):
        rmap = dict(header=self.header, data=self.data)
        return json.dumps(keys_to_strings(rmap))
    
    @classmethod
    def from_json(cls, json_str):
        rmap = strings_to_keys(json.loads(json_str))
        header = rmap["header"]
        data = rmap["data"]
        return cls("<json>", header, data, **header)
    
    @property
    def locate(self):
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
            results[ast.literal_eval(key)] = converted
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



class PipelineContext(Rmap):
    """A pipeline context describes the context mappings for each instrument
    of a pipeline.
    """
    check_attrs = ["observatory"]

    def __init__(self, filename, header, data, observatory=""):
        Rmap.__init__(self, filename, header, data)
        self.observatory = observatory.lower()
        self.selections = {}
        for instrument, imap in data.items():
            instrument = instrument.lower()
            self.selections[instrument] = InstrumentContext.from_file(imap, observatory, instrument)

    def get_best_refs(self, header, date=None):
        header = dict(header.items())
        instrument = header["INSTRUME"].lower()
        if date == "now":
            date = timestamp.now()
        if date:
            header["DATE"] = date
        else:
            header["DATE"] = header["DATE-OBS"] + " " + header["TIME-OBS"]
        header["DATE"] = timestamp.reformat_date(header["DATE"])
        return self.selections[instrument].get_best_refs(header)
    
    def reference_names(self):
        """Return the list of reference files associated with this pipeline context."""
        files = set()
        for instrument in self.selections:
            for file in self.selections[instrument].reference_names():
                files.add(file)
        return sorted(list(files))
    
    def mapping_names(self):
        """Return the list of pipeline, instrument, and reference map files associated with
        this pipeline context.
        """
        files = set([os.path.basename(self.filename)])
        for instrument in self.selections:
            files.update(self.selections[instrument].mapping_names())
        return sorted(list(files))

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

class InstrumentContext(Rmap):
    """An instrument context describes the rmaps associated with each filetype
    of an instrument.
    """
    check_attrs = ["observatory","instrument"]

    def __init__(self, filename, header, data, observatory="", instrument=""):
        Rmap.__init__(self, filename, header, data)
        self.observatory = observatory.lower()
        self.instrument = instrument.lower()
        self._selectors = {}
        for reftype, rmap_info in data.items():
            _rmap_ext, rmap_name = rmap_info
            self._selectors[reftype] = ReferenceRmap.from_file(
                rmap_name, self.observatory, self.instrument, reftype)

    def get_best_ref(self, reftype, header):
        return self._selectors[reftype.lower()].get_best_ref(header)

    def get_best_refs(self, header):
        refs = {}
        for reftype in self._selectors:
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
        for reftype in self._selectors:
            binding.update(self._selectors[reftype].get_binding(header))
        return binding
    
    def reference_names(self):
        files = set()
        for selector in self._selectors.values():
            for file in selector.reference_names():
                files.add(file)
        return sorted(list(files))
    
    def mapping_names(self):
        files = [os.path.basename(self.filename)]
        for selector in self._selectors.values():
            files.append(os.path.basename(selector.filename))
        return files
    
# ===================================================================

class ReferenceRmap(Rmap):
    """ReferenceRmap manages loading the rmap associated with a single reference
    filetype and instantiating an appropriate selector from the rmap header and data.
    """
    check_attrs = ["observatory","instrument","reftype"]
    
    def __init__(self, filename, header, data, observatory="", instrument="", reftype="", **keys):
        Rmap.__init__(self, filename, header, data)
        self.instrument = instrument.lower()
        self.observatory = observatory.lower()
        self.reftype = reftype.lower()
        cls = utils.get_object(header.get("class", "crds.selectors.ReferenceSelector"))
        self._selector = cls(header, data)
        
    def get_best_ref(self, header):
        return self._selector.choose(header)
    
    def reference_names(self):
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

PIPELINE_CONTEXTS = {}

def get_pipeline_context(context_file):
    """Recursively load the specified `context_file` and add it to
    the global pipeline cache.
    """
    if context_file not in PIPELINE_CONTEXTS:
        PIPELINE_CONTEXTS[context_file] = _load_context(context_file)
    return PIPELINE_CONTEXTS[context_file]

def _load_context(mapping):
    """Load any of the pipeline, instrument, or reftype `mapping`s
    from the file system.
    """
    observatory = utils.context_to_observatory(mapping)
    if mapping.endswith(".pmap"):
        return PipelineContext.from_file(mapping, observatory)
    elif mapping.endswith(".imap"):
        return InstrumentContext.from_file(mapping, observatory)
    elif mapping.endswith(".rmap"):
        return ReferenceRmap.from_file(mapping, observatory)
    else:
        raise ValueError("Unknown mapping extension for " + repr(mapping))

# ===================================================================

def get_best_refs(context_file, header):
    """Compute the best references for `header` for the given CRDS `context_file`.   This
    is a local computation using local rmaps and CPU resources.
    """
    ctx = get_pipeline_context(context_file)
    return ctx.get_best_refs(header)


def test():
    """Run module doctests."""
    import doctest, rmap
    return doctest.testmod(rmap)

if __name__ == "__main__":
    print test()

