"""This module supports loading all the data components required to make
a CRDS lookup table for an instrument.

get_cached_mapping loads the closure of the given context file from the
local CRDS store,  caching the result.

>>> p = get_cached_mapping("hst.pmap")

The initial HST pipeline mappings are self-consistent and there are none
missing:

>>> p.missing_mappings()
[]

The available HST reference data seems to have a number of ACS 
references missing relative to the CDBS HTML table dump:

>>> len(p.missing_references()) > 100
False

There are 72 pmap, imap, and rmap files in the entire HST pipeline:

>>> len(p.mapping_names()) > 50
True

There are 5719 reference files known to the initial CRDS mappings scraped
from the CDBS HTML table dump:

>>> len(p.reference_names()) > 1000
True

Pipeline reference files are also broken down by instrument:

>>> sorted(p.reference_name_map().keys())
['acs', 'cos', 'stis', 'wfc3']

>>> i = InstrumentContext.from_file("hst_acs.imap")

The ACS instrument has 15 associated mappings,  including the instrument 
context:

>>> len(i.mapping_names()) > 10
True

The ACS instrument has 3983 associated reference files in the hst_acs.imap 
context:

>>> len(i.reference_names()) > 2000
True

Active instrument references are also broken down by filetype:

>>> sorted(i.reference_name_map()["crrejtab"])
['n4e12510j_crr.fits', 'n4e12511j_crr.fits']

>>> r = ReferenceMapping.from_file("hst_acs_biasfile.rmap")
>>> len(r.reference_names())  > 500
True
"""
import sys
import os
import os.path
import hashlib

from .compat import namedtuple

from . import (log, utils, selectors)

try:
    import ast
except ImportError:
    class ast(object):
        """Fake ast module for Python2.5 / googleapp."""
        class NodeVisitor(object):
            """Fake NodeVisitor class for Python2.5 / googleapp."""
            pass    

# ===================================================================

Filetype = namedtuple("Filetype","header_keyword,extension,rmap")
Failure  = namedtuple("Failure","header_keyword,message")
Filemap  = namedtuple("Filemap","date,file,comment")

# ===================================================================

class MappingError(Exception):
    """Exception in load_rmap."""
    def __init__(self, *args):
        Exception.__init__(self, " ".join([str(x) for x in args]))
        
class FormatError(MappingError):
    "Something wrong with context or rmap file format."

class ChecksumError(MappingError):
    "There's a problem with the mapping's checksum."

class MissingHeaderKeyError(MappingError):
    """A required key was not in the mapping header."""

class AstDumper(ast.NodeVisitor):
    """Debug class for dumping out rmap ASTs."""
    def visit(self, node):
        print ast.dump(node), "\n"
        ast.NodeVisitor.visit(self, node)

    def dump(self, node):
        print ast.dump(node), "\n"
        self.generic_visit(node)

    visit_Assign = dump
    visit_Call = dump

class MappingValidator(ast.NodeVisitor):
    """MappingValidator visits the parse tree of a CRDS mapping file and
    raises exceptions for invalid constructs.
    """
    def compile_and_check(self, filepath):
        """Parse the file at `filepath`,  verify that it's a legal mapping,
        and return a compiled code object.
        """
        text = open(filepath).read()
        if sys.version_info >= (2, 7, 0):
            self.visit(ast.parse(text))
        return compile(text, "<ast>", "exec")

    illegal_nodes = [
        "FunctionDef","ClassDef", "Return", "Delete", "AugAssign", "Print",
        "For", "While", "If", "With", "Raise", "TryExcept", "TryFinally",
        "Assert", "Import", "ImportFrom", "Exec","Global","Pass",
        "Repr", "Yield","Lambda","Attribute","Subscript"
        ]
    
    def visit_Illegal(self, node):
        self.assert_(False, node, "Illegal statement or expression in mapping")
    
    def __getattr__(self, attr):
        if attr.startswith("visit_"):
            if attr[len("visit_"):] in self.illegal_nodes:
                return visit_Illegal
            else:
                return self.generic_visit
        else:
            return ast.NodeVisitor.__getattribute__(self, attr)
        
    def assert_(self, node, flag, message):
        """Raise an appropriate FormatError exception based on `node`
        and `message` if `flag` is False.
        """
        if not flag:
            if hasattr(node, "lineno"):
                raise FormatError(message + " at line " + str(node.lineno))
            else:
                raise FormatError(message)
                
    def visit_Module(self, node):
        self.assert_(node, len(node.body) == 2, 
                     "define only 'header' and 'selector' sections")
        self.generic_visit(node)

    def visit_Assign(self, node):
        self.assert_(node, len(node.targets) == 1, 
                     "Invalid 'header' or 'selector' definition")
        self.assert_(node, isinstance(node.targets[0], ast.Name),
                     "Invalid 'header' or 'selector' definition")       
        self.assert_(node, node.targets[0].id in ["header","selector"],
                     "Only define 'header' or 'selector' sections")
        self.assert_(node, isinstance(node.value, (ast.Call, ast.Dict)),
                    "Section value must be a selector call or dictionary")
        self.generic_visit(node)

    def visit_Call(self, node):
        self.assert_(node, node.func.id in selectors.SELECTORS,
            "Selector " + repr(node.func.id) + 
            " is not one of supported Selectors: " + 
            repr(sorted(selectors.SELECTORS.keys())))
        self.generic_visit(node)

MAPPING_VALIDATOR = MappingValidator()

# =============================================================================

class Mapping(object):
    """Mapping is the abstract baseclass for PipelineContext, 
    InstrumentContext, and ReferenceMapping.
    """
    required_attrs = []
    
    def __init__(self, filename, header, selector, **keys):
        self.filename = filename
        self.header = header
        self.selector = selector
    
    def __repr__(self):
        """A subclass-safe repr which includes required parameters except for
        'mapping' which is implied by the classname. 
        """
        rep = self.__class__.__name__ + "("
        rep += repr(self.filename)+ ", "
        for attr in set(self.required_attrs)-set(["mapping"]):
            rep += attr + "=" + repr(getattr(self, attr)) + ", "
        rep = rep[:-2] + ")"
        return rep
            
    def __getattr__(self, attr):
        """Enable access to required header parameters as 'self.<parameter>'"""
        if attr in self.required_attrs:
            val = self.header[attr]
            return val.lower() if isinstance(val, str) else val
        else:
            raise AttributeError("Invalid or missing header key " + repr(attr))

    @classmethod
    def from_file(cls, basename, *args, **keys):
        """Load a mapping file `basename` and do syntax and basic validation.
        """
        where = locate_mapping(basename)
        header, selector = cls._parse_header_selector(where)
        mapping = cls(basename, header, selector, **keys)
        mapping._validate_file_load(keys)
        return mapping
    
    @classmethod
    def _parse_header_selector(cls, filepath):
        """Given a mapping at `filepath`,  validate it and return a fully
        instantiated (header, selector) tuple.
        """
        code = MAPPING_VALIDATOR.compile_and_check(filepath)
        try:
            header, selector = cls._interpret(code)
        except Exception, exc:
            raise MappingError("Can't load", cls.__name__, "file:", 
                               repr(os.path.basename(filepath)), str(exc))
        return header, selector
    
    @classmethod
    def _interpret(cls, code):
        """Interpret a valid rmap code object and return it's header and 
        selector.
        """
        namespace = {}
        namespace.update(selectors.SELECTORS)
        exec code in namespace
        header = namespace["header"]
        selector = namespace["selector"]
        if isinstance(selector, selectors.Parameters):
            return header, selector.instantiate(header["parkey"], header)
        elif isinstance(selector, dict):
            return header, selector
        else:
            raise FormatError("selector must be a dict or a Selector.")
            
    def _validate_file_load(self, keys):
        """Validate assertions about the contents of this rmap after it's 
        built.
        """
        for name in self.required_attrs:
            if name not in self.header:
                raise MissingHeaderKeyError(
                    "Required header key " + repr(name) + " is missing.")
        if not keys.get("ignore_hash", False):
            self._check_hash()

    def missing_references(self):
        """Get the references mentioned by the closure of this mapping but not
        known to CRDS.
        """
        return [ ref for ref in self.reference_names() \
                    if not self.locate.reference_exists(ref) ]

    def missing_mappings(self):
        """Get the mappings mentioned by the closure of this mapping but not
        known to CRDS.
        """
        return [ mapping for mapping in self.mapping_names() \
                if not self.locate.mapping_exists(mapping) ]

    @property
    def locate(self):
        """Return the "locate" module associated with self.observatory.
        """
        if not hasattr(self, "_locate"):
            self._locate = utils.get_object(
                "crds." + self.observatory + ".locate")
        return self._locate

    def format(self):
        """Return the string representation of this mapping, 
        i.e. pretty serialization.
        """
        return "header = %s\n\nselector = %s\n" % \
            (self._format_header(), self._format_selector())
        
    def _format_dict(self, dict_, indent=0):
        """Return indented source code for nested `dict`.
        """
        prefix = indent*" "*4
        output = "{\n"
        for key, val in sorted(dict_.items()):
            if isinstance(val, dict):
                rval = self._format_dict(val, indent+1)
            else:
                rval = repr(val)
            output += prefix + " "*4 + repr(key) + " : " + rval + ",\n"
        output += prefix + "}"
        return output
    
    def _format_header(self):
        """Return the code string for the mapping header."""
        return self._format_dict(self.header)
    
    def _format_selector(self):
        """Return the code string for the mapping body/selector."""
        if isinstance(self.selector, dict):
            return self._format_dict(self.selector)
        else:
            return self.selector.format()

    def write(self, filename=None):
        """Write out this mapping to the specified `filename`,  
        or else self.filename.
        """
        if filename is None:
            filename = self.filename
        if isinstance(filename, str):
            file_ = open(filename, "w+")
        else:
            file_ = filename
        self._add_hash()
        file_.write(self.format())
        
    def _check_hash(self):
        """Verify that the mapping header has a checksum and that it is
        correct,  else raise an appropriate exception.
        """
        old = self.header.pop("sha1sum", None)
        if old is None:
            raise ChecksumError("sha1sum is missing.")
        nosum = self.format()
        self.header["sha1sum"] = old
        new = hashlib.sha1(nosum).hexdigest()
        if old != new:
            raise ChecksumError("sha1sum mismatch.")

    def _add_hash(self):
        """Add a checksum to the mapping header,  replacing any old checksum."""
        _old = self.header.pop("sha1sum", None)
        nosum = self.format()
        new = hashlib.sha1(nosum).hexdigest()
        self.header["sha1sum"] = new

    def get_required_parkeys(self):
        """Determine the set of parkeys required for this mapping
        and all the selected by it.
        """
        parkeys = set(self.parkey)
        if hasattr(self, "selections"):
            for selection in self.selections.values():
                key = selection.get_required_parkeys()
                parkeys = parkeys.union(set(key))
        return tuple(sorted(parkeys))

# ===================================================================

"""
header = {
    'observatory':'HST',
    'parkey' : ('INSTRUME'),
    'mapping': 'pipeline',
}

selector = {
    'ACS': 'hst_acs_00023.imap',
    'COS':'hst_cos_00023.imap', 
    'STIS':'hst_stis_00023.imap',
    'WFC3':'hst_wfc3_00023.imap',
    'NICMOS':'hst_nicmos_00023.imap',
})
"""

class PipelineContext(Mapping):
    """A pipeline context describes the context mappings for each instrument
    of a pipeline.
    """
    required_attrs = ["observatory", "mapping", "parkey"]

    def __init__(self, filename, header, selector, **keys):
        Mapping.__init__(self, filename, header, selector, **keys)
        self.selections = {}
        for instrument, imapname in selector.items():
            instrument = instrument.lower()
            self.selections[instrument] = ictx = InstrumentContext.from_file(
                imapname, **keys)
            assert self.mapping == "pipeline", \
                "PipelineContext 'mapping' format is not 'pipeline' in header."
            assert self.observatory == ictx.observatory, \
                "Nested 'observatory' doesn't match in " + repr(filename)
            assert instrument == ictx.instrument, \
                "Nested 'instrument' doesn't match in " + repr(filename)
    
    def get_best_references(self, header):
        """Return the best references for keyword map `header`.
        """
        header = dict(header)   # make a copy
        instrument = header["INSTRUME"].lower()
        return self.selections[instrument].get_best_references(header)
    
    def reference_names(self):
        """Return the list of reference files associated with this pipeline
        context.
        """
        files = set()
        for instrument_files in self.reference_name_map().values():
            files.update(instrument_files)
        return sorted(files)

    def reference_name_map(self):
        """Returns { instrument : [ref_file_name...] ... }"""
        files = {}
        for instrument in self.selections:
            files[instrument] = set()
            irefs = self.selections[instrument].reference_name_map()
            for reftype_files in irefs.values():
                files[instrument].update(set(reftype_files))
        return files
    
    def mapping_names(self):
        """Return the list of pipeline, instrument, and reference map files 
        associated with this pipeline context.
        """
        files = set([os.path.basename(self.filename)])
        for instrument in self.selections:
            files.update(self.selections[instrument].mapping_names())
        return sorted(list(files))
    
# ===================================================================

"""
header = {
    'observatory':'HST',
    'instrument': 'ACS',
    'mapping':'instrument',
    'parkey' : ('REFTYPE',),
}

selector = Match({
    'BIAS':  'hst_acs_bias_0021.rmap',
    'CRREJ': 'hst_acs_crrej_0003.rmap',
    'CCD':   'hst_acs_ccd_0002.rmap',
    'IDC':   'hst_acs_idc_0005.rmap',
    'LIN':   'hst_acs_lin_0002.rmap',
    'DISTXY':'hst_acs_distxy_0004.rmap',
    'BPIX':  'hst_acs_bpic_0056.rmap',
    'MDRIZ': 'hst_acs_mdriz_0001.rmap',
    ...
})

"""

class InstrumentContext(Mapping):
    """An instrument context describes the rmaps associated with each filetype
    of an instrument.
    """
    required_attrs = PipelineContext.required_attrs + ["instrument"]

    def __init__(self, filename, header, selector, **keys):
        Mapping.__init__(self, filename, header, selector)
        self.selections = {}
        for reftype, (_rmap_ext, rmap_name) in selector.items():
            reftype = reftype.lower()
            self.selections[reftype] = refmap = ReferenceMapping.from_file(
                rmap_name, **keys)            
            assert self.mapping == "instrument", \
                "InstrumentContext 'mapping' format is not 'instrument'."
            assert self.observatory == refmap.observatory, \
                "Nested 'observatory' doesn't match for " +  \
                repr(reftype) + " in " + repr(filename)
            assert self.instrument == refmap.instrument, \
                "Nested 'instrument' doesn't match for " + \
                repr(reftype) + " in " + repr(filename)
            assert refmap.reftype == reftype, \
                "Nested 'reftype' doesn't match for " + \
                repr(reftype) + " in " + repr(filename)

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
            except Exception, exc:
                refs[reftype] = "NOT FOUND " + str(exc)
        return refs

    def get_binding(self, header):
        """Given a header,  return the binding of all keywords pertinent to all
        reftypes for this instrument.
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
        """Returns a list of mapping files associated with this 
        InstrumentContext.
        """
        files = [os.path.basename(self.filename)]
        for selector in self.selections.values():
            files.append(os.path.basename(selector.filename))
        return files
    
    def get_parkey_map(self):
        """Return { parkey : [legal values...], ... }
        """
        pmap = {}
        for selector in self.selections.values():
            for parkey, choices in selector.get_parkey_map().items():
                if parkey not in pmap:
                    pmap[parkey] = set()
                pmap[parkey] = pmap[parkey].union(choices)
        for parkey, choices in pmap.items():
            pmap[parkey] = sorted(list(pmap[parkey]))
        return pmap
    
# ===================================================================

class ReferenceMapping(Mapping):
    """ReferenceMapping manages loading the rmap associated with a single
    reference filetype and instantiate an appropriate selector tree from the 
    rmap header and data.
    """
    required_attrs = InstrumentContext.required_attrs + ["reftype"]
            
    def get_best_ref(self, header):
        """Return the single reference file basename appropriate for `header` 
        selected by this ReferenceMapping.
        """
        return self.selector.choose(header)
    
    def reference_names(self):
        """Return the list of reference file basenames associated with this
        ReferenceMapping.
        """
        return self.selector.reference_names()
    
    def get_required_parkeys(self):
        parkeys = set()
        for key in self.parkey:
            if isinstance(key, tuple):
                parkeys = parkeys.union(set(key))
            else:
                parkeys.add(key)
        return parkeys
    
    def get_parkey_map(self):
        """Return { parkey : [legal values, ...], ... }
        """
        return self.selector.get_parkey_map()

# ===================================================================

CACHED_MAPPINGS = {}

def get_cached_mapping(mapping_basename, **keys):
    """Retrieve the Mapping corresponding to the specified 
    `mapping_basename` from the global mapping cache,  recursively
    loading and caching it if it has not already been cached.
    
    Return a PipelineContext, InstrumentContext, or ReferenceMapping.
    """
    if mapping_basename not in CACHED_MAPPINGS:
        CACHED_MAPPINGS[mapping_basename] = _load_mapping(
            mapping_basename, **keys)
    return CACHED_MAPPINGS[mapping_basename]

def _load_mapping(mapping, **keys):
    """Load any of the pipeline, instrument, or reftype `mapping`s
    from the file system.   Not cached.
    """
    if mapping.endswith(".pmap"):
        cls = PipelineContext
    elif mapping.endswith(".imap"):
        cls = InstrumentContext
    elif mapping.endswith(".rmap"):
        cls = ReferenceMapping
    else:
        m = Mapping.from_file(mapping)
        if m.header["mapping"] == "pipeline":
            cls = PipelineContext
        elif m.header["mapping"] == "instrument":
            cls = InstrumentContext
        elif m.header["mapping"] == "reference":
            cls = ReferenceMapping
        else:
            raise ValueError("Unknown mapping type for " + repr(mapping))
    return cls.from_file(mapping, **keys)
    
def is_mapping(mapping):
    """Return True IFF `mapping` has an extension indicating a CRDS mapping 
    file.
    """
    return mapping.endswith((".pmap", ".imap", ".rmap"))

def locate_mapping(mappath):
    """Based on a possibly incomplete name,  figure out the absolute
    pathname for the mapping specified by `mappath`.   If `mappath` 
    already has a directory path or is present in the CWD,  use it as is.   
    Otherwise infer the project from the mappath's name and use the
    project's locator to determine where the mapping should be.
    """
    if os.path.dirname(mappath):
        return mappath
    # Convert the mapping basename into an absolute path by first looking
    # up the "locate" module for the observatory and then calling 
    # locate_mapping().
    observatory = utils.context_to_observatory(mappath)
    try:
        locate = utils.get_object("crds." + observatory + ".locate")
    except ImportError:
        raise ValueError(
            "No observatory associated with mapping file " + repr(mappath))
    where = locate.locate_mapping(mappath)
    return where

# ===================================================================

def get_best_references(context_file, header):
    """Compute the best references for `header` for the given CRDS 
    `context_file`.   This is a local computation using local rmaps and 
    CPU resources.
    """
    ctx = get_cached_mapping(context_file)
    return ctx.get_best_references(header)


def test():
    """Run module doctests."""
    import doctest, rmap
    return doctest.testmod(rmap)

if __name__ == "__main__":
    print test()

