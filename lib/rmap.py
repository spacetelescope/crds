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

>>> len(p.missing_references()) > 0
True

There are 72 pmap, imap, and rmap files in the entire HST pipeline:

>>> len(p.mapping_names()) > 50
True

There are over 9000 reference files known to the initial CRDS mappings scraped
from the CDBS HTML table dump:

>>> len(p.reference_names()) > 1000
True

Pipeline reference files are also broken down by instrument:

>>> sorted(p.reference_name_map().keys())
['acs', 'cos', 'nicmos', 'stis', 'wfc3', 'wfpc2']

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
['j4d1435lj_crr.fits', 'lci1518ej_crr.fits', 'lci1518fj_crr.fits', 'n4e12510j_crr.fits', 'n4e12511j_crr.fits']

>>> r = ReferenceMapping.from_file("hst_acs_biasfile.rmap")
>>> len(r.reference_names())  > 500
True
"""
import sys
import os
import os.path
import hashlib
import re
import tempfile
import shutil
import glob

import pyfits

from .compat import namedtuple

from . import (log, utils, selectors, data_file)
from crds.selectors import ValidationError

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

class MappingError(utils.CrdsError):
    """Exception in load_rmap."""
    def __init__(self, *args):
        utils.CrdsError.__init__(self, " ".join([str(x) for x in args]))
        
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
    raises exceptions for invalid constructs.   MappingValidator is concerned
    with limiting rmaps to safe code,  not deep semantic checks.
    """
    def compile_and_check(self, text):
        """Parse `text` to verify that it's a legal mapping, and return a 
        compiled code object.
        """
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
                return self.visit_Illegal
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
        
    @property
    def basename(self):
        return os.path.basename(self.filename)

    def __repr__(self):
        """A subclass-safe repr which includes required parameters except for
        'mapping' which is implied by the classname. 
        """
        rep = self.__class__.__name__ + "("
        rep += repr(self.filename)
        rep += ", "
#        for attr in set(self.required_attrs)-set(["mapping"]):
#            rep += attr + "=" + repr(getattr(self, attr)) + ", "
        rep = rep[:-2] + ")"
        return rep
            
    def __getattr__(self, attr):
        """Enable access to required header parameters as 'self.<parameter>'"""
        if attr in self.header:
            val = self.header[attr]
            if isinstance(val, str):
                if val.startswith("(") and val.endswith(")"):
                    return val
                else:
                    return val.lower()
            else:
                return val
        else:
            raise AttributeError("Invalid or missing header key " + repr(attr))

    @classmethod
    def from_file(cls, basename, *args, **keys):
        """Load a mapping file `basename` and do syntax and basic validation.
        """
        where = locate_mapping(basename)
        text = open(where).read()
        header, selector = cls._parse_header_selector(text, where)
        mapping = cls(basename, header, selector, **keys)
        mapping._validate_file_load(keys)
        return mapping
    
    @classmethod
    def from_string(cls, text, basename="(noname)", **keys):
        """Construct a mapping from string `text` nominally named `basename`.
        """
        header, selector = cls._parse_header_selector(text, basename)
        mapping = cls(basename, header, selector, **keys)
        mapping._validate_file_load(keys)
        return mapping
    
    @classmethod
    def _parse_header_selector(cls, text, where=""):
        """Given a mapping at `filepath`,  validate it and return a fully
        instantiated (header, selector) tuple.
        """
        code = MAPPING_VALIDATOR.compile_and_check(text)
        try:
            header, selector = cls._interpret(code)
        except Exception, exc:
            raise MappingError("Can't load file " + where + " : " + str(exc))
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
        if not keys.get("ignore_checksum", False):
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
                if not mapping_exists(mapping) ]

    @property
    def locate(self):
        """Return the "locate" module associated with self.observatory.
        """
        if not hasattr(self, "_locate"):
            self._locate = utils.get_object(
                "crds." + self.observatory + ".locate")
        return self._locate

    def format(self):
        """Return the string representation of this mapping, i.e. pretty 
        serialization.   This is currently limited to initially creating rmaps,
        not rewriting them since it is based on internal representations and
        therefore loses comments.
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
        or else self.filename. DOES NOT PRESERVE COMMENTS.
        """
        if filename is None:
            filename = self.filename
        else:
            self.filename = filename
        self.header["sha1sum"] = "99999"
        file = open(filename, "w+")
        file.write(self.format())
        file.close()
        self.rewrite_checksum()  # inefficient, but rare and consistent

    def _check_hash(self):
        """Verify that the mapping header has a checksum and that it is
        correct,  else raise an appropriate exception.
        """
        old = self.header.get("sha1sum", None)
        if old is None:
            raise ChecksumError("sha1sum is missing in " + repr(self.basename))
        if self._get_checksum() != self.header["sha1sum"]:
            raise ChecksumError("sha1sum mismatch.")

    def _get_checksum(self):
        """Compute the rmap checksum over the original file contents.
        Skip over the sha1sum line.   Preserves comments.
        """
        where = locate_mapping(self.filename)
        # Compute the new checksum over everything but the sha1sum line.
        # This will fail if sha1sum appears for some other reason.  It won't ;-)
        lines = [line for line in open(where).readlines() \
                 if "sha1sum" not in line]
        text = "".join(lines)
        return hashlib.sha1(text).hexdigest()
        
    def rewrite_checksum(self, filename=None):
        """Re-write checksum updates the checksum for a Mapping which must
        have been loaded from a file.  Preserves comments.   Outputs results
        to `filename` or the original file.
        """
        if self.filename is None:
            raise ValueError("rewrite_checksums() only works on rmaps"
                             " that were read from a file.")
            
        _handle, tmpname = tempfile.mkstemp()
        
        xsum = self._get_checksum()
        
        # re-write the file we loaded from,  inserting the new checksum,
        # outputting to a temporary file.
        assert "sha1sum" in open(self.filename).read(), \
            "no sha1sum field in " + repr(self.filename)
        file = open(tmpname, "w+")
        for line in open(self.filename).readlines():
            line = re.sub(r"('sha1sum'\s*:\s*)('[^']+')",
                          r"\1" + repr(str(xsum)), 
                          line)
            file.write(line)
        file.close()
        
        # If user specified a filename,  copy the new file to that.
        # Otherwise,  overwrite the original mapping file.
        if filename is not None:
            where = filename
        else:
            where = self.filename

        # rename might fail if `tmp` is not on same file system as `where`
        shutil.copyfile(tmpname, where)
        os.remove(tmpname)
      
    def get_required_parkeys(self):
        """Determine the set of parkeys required for this mapping
        and all the mappings selected by it.
        """
        parkeys = set(self.parkey)
        if hasattr(self, "selections"):
            for selection in self.selections.values():
                key = selection.get_required_parkeys()
                parkeys = parkeys.union(set(key))
        return sorted(parkeys)
    
    def get_minimum_header(self, dataset, original_name=None):
        """Return the names and values of `dataset`s header parameters which 
        are required to compute best references for it.   `original_name` is
        used to determine file type when `dataset` is a temporary file with a
        useless name.
        """
        header = data_file.get_conditioned_header(
            dataset, original_name=original_name)
        return self.minimize_header(header)

    def minimize_header(self, header):
        """Return only those items of `header` which are required to determine
        bestrefs.
        """
        if isinstance(self, PipelineContext):
            mapping = self.get_imap(header["INSTRUME"].lower())
        else:
            mapping = self
        minimized = {}
        for key in mapping.get_required_parkeys() + ["INSTRUME",]:
            try:
                minimized[key] = header[key]
            except KeyError:
                minimized[key] = "NOT FOUND"
        return minimized
    
    def validate_mapping(self,  trap_exceptions=False):
        """Recursively validate this mapping,  performing the checks
        required by crds.certify.
        """
        log.info("Validating", self.basename)
        for key, sel in self.selections.items():
            try:
                sel.validate_mapping(trap_exceptions)
            except Exception, exc:
                if trap_exceptions == mapping_type(self):
                    log.error()
                elif trap_exceptions == "debug":
                    raise
                else:
                    raise ValidationError(repr(self) + " : " + str(exc))

    def file_matches(self, filename):
        """Return the "extended match tuples" which can be followed to 
        arrive at `filename`.
        """
        more = []
        for key, value in self.selections.items():
            more += value.file_matches(filename)
        return sorted(more)

    def difference(self, other, path=()):
        """Compare `self` with `other` and return a list of difference
        tuples,  prefixing each tuple with context `path`.
        """
        differences = []
        for key in self.selections:
            if key not in other.selections:
                msg = repr(other.basename) + " deleted " + repr(key)
                differences.append(msg)
            else:
                differences.extend(self.selections[key].difference(
                    other.selections[key], 
                    path + ((self.basename, other.basename),)))
        for key in other.selections:
            if key not in self.selections:
                msg = repr(other.basename) + " added " + repr(key)
                differences.append(msg)
        return sorted(differences)
                
# ===================================================================

class PipelineContext(Mapping):
    """A pipeline context describes the context mappings for each instrument
    of a pipeline.
    """
    # Last required attribute is "difference type".
    required_attrs = ["observatory", "mapping", "parkey", 
                      "name", "derived_from"]
    
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
    
    def get_best_references(self, header, include=None):
        """Return the best references for keyword map `header`.  If `include`
        is None,  collect all filekinds,  else only those listed.
        """
        header = dict(header)   # make a copy
        instrument = header["INSTRUME"].lower()
        try:
            imap = self.selections[instrument]
        except KeyError:
            raise utils.CrdsError("Unknown instrument " + repr(instrument) +
                                  " for context " + repr(self.name))
        return imap.get_best_references(header, include)
    
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
            for filekind_files in irefs.values():
                files[instrument].update(set(filekind_files))
        return files
    
    def mapping_names(self):
        """Return the list of pipeline, instrument, and reference map files 
        associated with this pipeline context.
        """
        files = set([self.basename])
        for instrument in self.selections:
            files.update(self.selections[instrument].mapping_names())
        return sorted(list(files))
    
    def get_imap(self, instrument):
        """Return the InstrumentMapping corresponding to `instrument`."""
        return self.selections[instrument.lower()]
    
    def get_filekinds(self, dataset):
        """Return the filekinds associated with `dataset` by examining
        it's parameters.  Currently returns ALL filekinds for 
        `dataset`s instrument.   Not all are necessarily appropriate for
        the current mode.
        """
        instrument = pyfits.getval(dataset, "INSTRUME")
        return self.get_imap(instrument).get_filekinds(dataset)

# ===================================================================

class InstrumentContext(Mapping):
    """An instrument context describes the rmaps associated with each filetype
    of an instrument.
    """
    required_attrs = PipelineContext.required_attrs + ["instrument"]
    type = "instrument"

    def __init__(self, filename, header, selector, **keys):
        Mapping.__init__(self, filename, header, selector)
        self.selections = {}
        for filekind, rmap_name in selector.items():
            filekind = filekind.lower()
            self.selections[filekind] = refmap = ReferenceMapping.from_file(
                rmap_name, **keys)            
            assert self.mapping == "instrument", \
                "InstrumentContext 'mapping' format is not 'instrument'."
            assert self.observatory == refmap.observatory, \
                "Nested 'observatory' doesn't match for " +  \
                repr(filekind) + " in " + repr(filename)
            assert self.instrument == refmap.instrument, \
                "Nested 'instrument' doesn't match for " + \
                repr(filekind) + " in " + repr(filename)
            assert refmap.filekind == filekind, \
                "Nested 'filekind' doesn't match for " + \
                repr(filekind) + " in " + repr(filename)
                
    def get_rmap(self, filekind):
        """Given `filekind`,  return the corresponding ReferenceMapping.
        """
        try:
            return self.selections[filekind.lower()]
        except KeyError:
            raise utils.CrdsError("Unknown reference type " + repr(str(filekind)))

    def get_best_ref(self, filekind, header):
        """Returns the single reference file basename appropriate for `header`
        corresponding to `filekind`.
        """
        return self.get_rmap(filekind).get_best_ref(header)

    def get_best_references(self, header, include=None):
        """Returns a map of best references { filekind : reffile_basename } 
        appropriate for this `header`.   If `include` is None, include all
        filekinds in the results,  otherwise compute and include only 
        those filekinds listed.
        """
        refs = {}
        if not include:
            include = self.selections
        for filekind in include:
            filekind = filekind.lower()
            try:
                refs[filekind] = self.get_best_ref(filekind, header)
            except IrrelevantReferenceTypeError:
                refs[filekind] = "NOT FOUND n/a"
#                log.verbose("Reference type",repr(filekind),
#                            "is irrelevant for this dataset.")
            except Exception, exc:
                refs[filekind] = "NOT FOUND " + str(exc)
        return refs

    def reference_names(self):
        """Returns [ref_file_name...]
        """
        files = set()
        for filekind_files in self.reference_name_map().values():
            files.update(set(filekind_files))
        return sorted(files)

    def reference_name_map(self):
        """Returns { filekind : set( ref_file_name... ) }
        """
        files = {}
        for filekind, selector in self.selections.items():
            files[filekind] = sorted(selector.reference_names())
        return files
    
    def mapping_names(self):
        """Returns a list of mapping files associated with this 
        InstrumentContext.
        """
        files = [self.basename]
        for selector in self.selections.values():
            files.append(selector.basename)
        return files
    
    def get_parkey_map(self):
        """Infers the legal values of each parkey from the rmap itself.
        This is a potentially different answer than that defined by the TPNs,
        the latter being considered definitive.
        Return { parkey : [legal values...], ... }
        """
        pkmap = {}
        for selection in self.selections.values():
            for parkey, choices in selection.get_parkey_map().items():
                if parkey not in pkmap:
                    pkmap[parkey] = set()
                pkmap[parkey] = pkmap[parkey].union(choices)
        for parkey, choices in pkmap.items():
            pkmap[parkey] = sorted(list(pkmap[parkey]))
        return pkmap
    
    def get_valid_values_map(self, condition=False, remove_special=True):
        """Based on the TPNs,  return a mapping from parkeys to their valid
        values for all parkeys for all filekinds of this instrument.   This will
        return the definitive lists of legal values,  not all of which are 
        required to be represented in rmaps;  these are the values that *could*
        be in an rmap,  not necessarily what is in any given rmap to match.
        
        If `condition` is True,  values are filtered with 
        utils.condition_value() to match their rmap string appearance.   If 
        False,  values are returned as raw TPN values and types.
        
        If `remove_special` is True,  values of ANY or N/A are removed from the
        lists of valid values.
        """
        pkmap = {}
        for selection in self.selections.values():
            rmap_pkmap = selection.get_valid_values_map(condition)
            for key in rmap_pkmap:
                if key not in pkmap:
                    pkmap[key] = set()
                pkmap[key] = pkmap[key].union(set(rmap_pkmap[key]))
        for key in self.get_parkey_map():
            if key not in pkmap:
                pkmap[key] = []    # flag a need for an unconstrained input
        if remove_special:
            specials = set(["ANY","N/A"])
            for key in pkmap:  # remove specials like ANY or N/A
                if pkmap[key]:
                    pkmap[key] = pkmap[key] - specials
        for key in pkmap:  # convert to sorted lists
            pkmap[key] = sorted(pkmap[key])
        return pkmap
    
    def get_filekinds(self, dataset=None):
        """Return the filekinds associated with this dataset,  ideally
        the minimum set associated with `dataset`,  but initially all
        for dataset's instrument,  assumed to be self.instrument.
        """
        return [key.upper() for key in self.selections.keys()]
    
# ===================================================================

class IrrelevantReferenceTypeError(LookupError):
    """The reference determined by this rmap does not apply to the instrument
    mode specified by the dataset header.
    """

class ReferenceMapping(Mapping):
    """ReferenceMapping manages loading the rmap associated with a single
    reference filetype and instantiate an appropriate selector tree from the 
    rmap header and data.
    """
    required_attrs = InstrumentContext.required_attrs + ["filekind"]

    def __init__(self, *args, **keys):
        Mapping.__init__(self, *args, **keys)
        self._tpn_valid_values = self.get_valid_values_map()
        self._rmap_valid_values = self.selector.get_value_map()
        self._required_parkeys = self.get_required_parkeys()  
        self._relevance_expr = getattr(self, "relevance", "ALWAYS")

        # header precondition method, e.g. crds.hst.acs.precondition_header
        # this is optional code which pre-processes and mutates header inputs
        # set to identity if not defined.
        try:  
            self._precondition_header = utils.get_object(
                ".".join(["crds", self.observatory, self.instrument, 
                          "precondition_header"]))
        except ImportError:
            self._precondition_header = lambda self, header: header
        # fallback routine called when standard best refs fails
        # set to return None if not defined.
        try:
            self._fallback_header = utils.get_object(
                ".".join(["crds", self.observatory, self.instrument, 
                          "fallback_header"]))    
        except ImportError:
            self._fallback_header = lambda self, header: None

    def get_best_ref(self, header_in):
        """Return the single reference file basename appropriate for 
        `header_in` selected by this ReferenceMapping.
        """
        log.verbose("Getting bestrefs for", self.instrument, self.filekind, 
                    "parkeys", self.parkey)
        self.check_relevance(header_in)  # Is this rmap appropriate for header
        # Some filekinds, .e.g. ACS biasfile, mutate the header 
        header = self._precondition_header(self, header_in)
        try:
            return self.selector.choose(header)
        except Exception, exc:
            log.verbose("First selection failed: " + str(exc))
            header = self._fallback_header(self, header_in)
            if header:
                log.verbose("Fallback lookup on", repr(header))
                return self.selector.choose(header)
            else:
                raise
            
    def reference_names(self):
        """Return the list of reference file basenames associated with this
        ReferenceMapping.
        """
        return self.selector.reference_names()
    
    def mapping_names(self):
        """Return name of this ReferenceMapping as degenerate list of 1 item."""
        return [self.basename]
    
    def get_required_parkeys(self):
        """Return the list of parkey names needed to select from this rmap."""
        parkeys = []
        for key in self.parkey:
            if isinstance(key, tuple):
                parkeys += list(key)
            else:
                parkeys.append(key)
        return parkeys
    
    def get_parkey_map(self):
        """Based on the rmap,  return the mapping from parkeys to their
        handled values,  i.e. what this rmap says it matches against.
        Note that these are the values seen in the rmap prior to any 
        substitutions which are defined in the header.
        
        Return { parkey : [match values, ...], ... }
        """
        return self.selector.get_parkey_map()
    
    def get_valid_values_map(self, condition=True):
        """Based on the TPNs,  return a mapping from each of the required
        parkeys to its valid values, 
   
        i.e. the definitive source for what is legal for this filekind.
        
        return { parkey : [ valid values ] }
        """
        tpninfos = self.locate.get_tpninfos(self.instrument, self.filekind)
        valid_values = {}
        required_keys = self.get_required_parkeys()
        for info in tpninfos:
            if info.name in required_keys:
                values = info.values
                if len(values) == 1 and ":" in values[0]:
                    limits = values[0].split(":")
                    try:
                        limits = [int(float(x)) for x in limits]
                    except:
                        sys.exc_clear()
                    else:
                        values = range(limits[0], limits[1]+1)
                if condition:
                    values = list(values)
                    for i, value in enumerate(values):
                        values[i] = utils.condition_value(value)
                    values = tuple(values)
                valid_values[info.name] = values 
        return valid_values
    
    def validate_mapping(self, trap_exceptions=False):
        """Validate the contents of this rmap against the TPN for this
        filekind / reftype.   Each field of each Match tuple must have a value
        OK'ed by the TPN.  UseAfter dates must be correctly formatted.
        """
        log.info("Validating", self.basename)
        try:
            self.selector.validate_selector(self._tpn_valid_values, trap_exceptions)
        except Exception, exc:
            if trap_exceptions == mapping_type(self):
                log.error()
            elif trap_exceptions == "debug":
                raise
            else:
                raise ValidationError(repr(self) + " : " + str(exc))

    def file_matches(self, filename):
        """Return a list of the match tuples which refer to `filename`."""
        sofar = ((("observatory", self.observatory), 
                  ("INSTRUME",self.instrument), 
                  ("filekind", self.filekind),),)
        return sorted(self.selector.file_matches(filename, sofar))
    
    def difference(self, other, path=()):
        """Return the list of difference tuples between `self` and `other`,
        prefixing each tuple with context `path`.
        """
        return self.selector.difference(other.selector, path + 
                ((self.basename, other.basename),))

    def check_relevance(self, header):
        """Raise an exception if this rmap's relevance expression evaluated
        in the context of `header` returns False.
        """
        # header keys and values are upper case.  rmap attrs are lower case.
        try:
            if self._relevance_expr != "always":
                relevant = eval(self._relevance_expr, {}, header)
                log.verbose("Filekind ", self.instrument, self.filekind, 
                            "is relevant: ", relevant)
            else:
                relevant = True
        except Exception, exc:
            log.warning("Relevance check failed: " + str(exc))
        else:
            if not relevant:
                raise IrrelevantReferenceTypeError(
                    "Rmap does not apply to the given parameter set.")

# ===================================================================

CACHED_MAPPINGS = {}

def get_cached_mapping(mapping_basename, **keys):
    """Retrieve the Mapping corresponding to the specified 
    `mapping_basename` from the global mapping cache,  recursively
    loading and caching it if it has not already been cached.
    
    Return a PipelineContext, InstrumentContext, or ReferenceMapping.
    """
    if mapping_basename not in CACHED_MAPPINGS:
        CACHED_MAPPINGS[mapping_basename] = load_mapping(
            mapping_basename, **keys)
    return CACHED_MAPPINGS[mapping_basename]

def load_mapping(mapping, **keys):
    """Load any of the pipeline, instrument, or filekind `mapping`s
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
        mapping_type = m.header["mapping"].lower()
        if  mapping_type == "pipeline":
            cls = PipelineContext
        elif mapping_type == "instrument":
            cls = InstrumentContext
        elif mapping_type == "reference":
            cls = ReferenceMapping
        else:
            raise ValueError("Unknown mapping type for " + repr(mapping))
    return cls.from_file(mapping, **keys)
    
# =============================================================================

HERE = os.path.dirname(__file__) or "./"

def get_crds_mappath():
    """CRDS_MAPPATH is the location of the client or sever side mapping 
    directory tree,  defaulting to the package directory of crds.mappings.
    """
    default = os.path.dirname(utils.get_object("crds.mappings").__file__)
    return os.environ.get("CRDS_MAPPATH", default)

def get_crds_refpath():
    """CRDS_REFPATH is the path to the local/client copy of reference files,
    defaulting to the package directory for crds.references.
    """
    default = os.path.dirname(utils.get_object("crds.references").__file__)
    return os.environ.get("CRDS_REFPATH", default)

# =============================================================================

def locate_file(filepath, observatory="hst"):
    """Figure out the absolute pathname where CRDS will stash a reference
    or mapping file.  If filepath already has a directory,  return filepath
    as-is.   Otherwise,  return the *client* path for a file.
    """
    if os.path.dirname(filepath):
        return filepath
    if is_mapping(filepath):
        return locate_mapping(filepath, observatory)
    else:
        return locate_reference(filepath, observatory)

def locate_reference(ref, observatory="hst"):
    """Return the absolute path where reference `ref` should be located."""
    if os.path.dirname(ref):
        return ref
    return os.path.join(get_crds_refpath(), observatory, ref)

# =============================================================================

def is_mapping(mapping):
    """Return True IFF `mapping` has an extension indicating a CRDS mapping 
    file.
    """
    return mapping.endswith((".pmap", ".imap", ".rmap"))

def locate_mapping(mappath, observatory=None):
    """Return the absolute path where CRDS mapping `mappath` should be."""
    if os.path.dirname(mappath):
        return mappath
    if observatory is None:
        observatory = mapping_to_observatory(mappath)
    return os.path.join(get_crds_mappath(), observatory, mappath)

def list_mappings(glob_pattern, observatory="hst"):
    """Return the list of mappings for `observatory` which match `glob_pattern`.
    """    
    path = os.path.join(get_crds_mappath(), observatory, glob_pattern)
    return [os.path.basename(fpath) for fpath in glob.glob(path)]

def mapping_exists(mapping):
    """Return True IFF `mapping` exists on the local file system."""
    return os.path.exists(locate_mapping(mapping))

def mapping_to_observatory(context_file):
    """
    >>> mapping_to_observatory('hst_acs_biasfile.rmap')
    'hst'
    """
    return os.path.basename(context_file).split("_")[0].split(".")[0]

def mapping_to_instrument(context_file):
    """
    >>> mapping_to_instrument('hst_acs_biasfile.rmap')
    'acs'
    """
    return os.path.basename(context_file).split("_")[1].split(".")[0]

def mapping_to_filekind(context_file):
    """
    >>> mapping_to_filekind('hst_acs_biasfile.rmap')
    'biasfile'
    """
    return os.path.basename(context_file).split("_")[2].split(".")[0]

def mapping_type(mapping):
    """
    >>> mapping_type("hst.pmap")
    'pmap'
    >>> mapping_type("hst_acs.imap")
    'imap'
    >>> mapping_type("hst_acs_biasfile.rmap")
    'rmap'
    >>> try:
    ...    mapping_type("hst_acs.foo")
    ... except IOError:
    ...    pass
    >>> mapping_type(get_cached_mapping('hst.pmap'))
    'pmap'
    >>> mapping_type(get_cached_mapping('hst_acs.imap'))
    'imap'
    >>> mapping_type(get_cached_mapping('hst_acs_darkfile.rmap'))
    'rmap'
    """
    if isinstance(mapping, (str, unicode)):
        if is_mapping(mapping):
            return os.path.splitext(mapping)[1][1:]
        else:
            mapping = load_mapping(mapping)
    if isinstance(mapping, PipelineContext):
        return "pmap"
    elif isinstance(mapping, InstrumentContext):
        return "imap"
    elif isinstance(mapping, ReferenceMapping):
        return "rmap"
    else:
        raise ValueError("Unknown mapping type for " + repr(Mapping))
# ===================================================================

def get_best_references(context_file, header, include=None):
    """Compute the best references for `header` for the given CRDS 
    `context_file`.   This is a local computation using local rmaps and 
    CPU resources.   If `include` is None,  return results for all
    filekinds appropriate to `header`,  otherwise return only those
    filekinds listed in `include`.
    """
    ctx = get_cached_mapping(context_file)
    return ctx.get_best_references(header, include=include)


def test():
    """Run module doctests."""
    import doctest, rmap
    return doctest.testmod(rmap)

if __name__ == "__main__":
    print test()

