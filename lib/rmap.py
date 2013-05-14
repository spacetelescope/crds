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

>>> i = load_mapping("hst_acs.imap")

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
import re
import glob

from .compat import namedtuple, ast

import crds
from . import (log, utils, selectors, data_file, config)

# XXX For backward compatability until refactored away.
from .config import locate_file, locate_mapping, locate_reference
from .config import mapping_exists, is_mapping

from crds.selectors import ValidationError

# ===================================================================

Filetype = namedtuple("Filetype","header_keyword,extension,rmap")
Failure  = namedtuple("Failure","header_keyword,message")
Filemap  = namedtuple("Filemap","date,file,comment")

# ===================================================================

class MappingError(crds.CrdsError):
    """Exception in load_rmap."""
    def __init__(self, *args):
        crds.CrdsError.__init__(self, " ".join([str(x) for x in args]))

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
    def compile_and_check(self, text, source="<ast>", mode="exec"):
        """Parse `text` to verify that it's a legal mapping, and return a
        compiled code object.
        """
        if sys.version_info >= (2, 7, 0):
            self.visit(ast.parse(text))
        return compile(text, source, mode)

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

class LowerCaseDict(dict):
    """Used to return Mapping header string values uniformly as lower case.
    
    >>> d = LowerCaseDict([("this","THAT"), ("another", "(ESCAPED)")])
    
    Ordinarily,  all string values are mapped to lower case:
    
    >>> d["this"]
    'that'
    
    Values bracketed by () are returned unaltered in order to support header Python 
    expressions which are typically evaluated in the context of an incoming header 
    (FITS) dictionary,  all upper case:
    
    >>> d["another"]
    '(ESCAPED)'
    """
    def __getitem__(self, key):
        val = super(LowerCaseDict, self).__getitem__(key)
        # Return string values as lower case,  but exclude literal expressions surrounded by ()
        # for case-sensitive HST rmap relevance expressions.
        if isinstance(val, basestring) and not (val.startswith("(") and val.endswith(")")):
            val = val.lower()
        return val
    
    def __repr__(self):
        return self.__class__.__name__ + "(%s)" % super(LowerCaseDict, self).__repr__()

class Mapping(object):
    """Mapping is the abstract baseclass for PipelineContext,
    InstrumentContext, and ReferenceMapping.
    """
    required_attrs = []

    def __init__(self, filename, header, selector, **keys):
        self.filename = filename
        self.header = LowerCaseDict(header)
        self.selector = selector
        for name in self.required_attrs:
            if name not in self.header:
                raise MissingHeaderKeyError(
                    "Required header key " + repr(name) + " is missing.")

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
        rep = rep[:-2] + ")"
        return rep
    
    def __str__(self):
        """Return the source text of the Mapping."""
        return self.format()

    def __getattr__(self, attr):
        """Enable access to required header parameters as 'self.<parameter>'"""
        if attr in self.header:
            return self.header[attr]   # Note:  header is a class which mutates values,  see LowerCaseDict.
        else:
            raise AttributeError("Invalid or missing header key " + repr(attr))

    @classmethod
    def from_file(cls, basename, *args, **keys):
        """Load a mapping file `basename` and do syntax and basic validation."""
        text = open(config.locate_mapping(basename)).read()
        return cls.from_string(text, basename, *args, **keys)

    @classmethod
    def from_string(cls, text, basename="(noname)", *args, **keys):
        """Construct a mapping from string `text` nominally named `basename`."""
        header, selector = cls._parse_header_selector(text, basename)
        mapping = cls(basename, header, selector, **keys)
        ignore = keys.get("ignore_checksum", False) or config.get_ignore_checksum()
        try:
            mapping._check_hash(text)
        except ChecksumError, exc:
            if ignore == "warn":
                log.warning("Checksum error", ":", str(exc))
            elif ignore:
                pass
            else:
                raise
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
        return LowerCaseDict(header), selector

    @classmethod
    def _interpret(cls, code):
        """Interpret a valid rmap code object and return it's header and
        selector.
        """
        namespace = {}
        namespace.update(selectors.SELECTORS)
        exec code in namespace
        header = LowerCaseDict(namespace["header"])
        selector = namespace["selector"]
        if isinstance(selector, selectors.Parameters):
            return header, selector.instantiate(header)
        elif isinstance(selector, dict):
            return header, selector
        else:
            raise FormatError("selector must be a dict or a Selector.")

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
                if not config.mapping_exists(mapping) ]

    @property
    def locate(self):
        """Return the "locate" module associated with self.observatory."""
        if not hasattr(self, "_locate"):
            self._locate = utils.get_object("crds", self.observatory, "locate")
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
        """Return indented source code for nested `dict`."""
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
        self.header["sha1sum"] = self._get_checksum(self.format())
        with open(filename, "w+") as file:
            file.write(self.format())

    def _check_hash(self, text):
        """Verify that the mapping header has a checksum and that it is
        correct,  else raise an appropriate exception.
        """
        old = self.header.get("sha1sum", None)
        if old is None:
            raise ChecksumError("sha1sum is missing in " + repr(self.basename))
        if self._get_checksum(text) != self.header["sha1sum"]:
            raise ChecksumError("sha1sum mismatch in " + repr(self.basename))

    def _get_checksum(self, text):
        """Compute the rmap checksum over the original file contents.  Skip over the sha1sum line."""
        # Compute the new checksum over everything but the sha1sum line.
        # This will fail if sha1sum appears for some other reason.  It won't ;-)
        text = "".join([line for line in text.splitlines(True) if "sha1sum" not in line])
        return utils.str_checksum(text)

    rewrite_checksum = write
    #    """Re-write checksum updates the checksum for a Mapping writing the
    #    result out to `filename`.
    #    """

    def get_required_parkeys(self):
        """Determine the set of parkeys required for this mapping and all the mappings selected by it."""
        parkeys = set(self.parkey)
        if hasattr(self, "selections"):
            for selection in self.selections.values():
                key = selection.get_required_parkeys()
                parkeys = parkeys.union(set(key))
        return sorted(parkeys)

    def minimize_header(self, header):
        """Return only those items of `header` which are required to determine
        bestrefs.   Missing keys are set to 'UNDEFINED'.
        """
        header = self.locate.fits_to_parkeys(header)
        if isinstance(self, PipelineContext):
            instrument = self.get_instrument(header)
            mapping = self.get_imap(instrument)
            keys = mapping.get_required_parkeys() + [self.instrument_key]
        else:
            keys = self.get_required_parkeys()
        minimized = {}
        for key in keys:
            minimized[key] = header.get(key.lower(), 
                                        header.get(key.upper(), "UNDEFINED"))
        return minimized

    def get_minimum_header(self, dataset, original_name=None):
        """Return the names and values of `dataset`s header parameters which
        are required to compute best references for it.   `original_name` is
        used to determine file type when `dataset` is a temporary file with a
        useless name.
        """
        header = data_file.get_conditioned_header(dataset, original_name=original_name)
        return self.minimize_header(header)

    def validate_mapping(self,  trap_exceptions=False):
        """Validate `self` only implementing any checks to be performced by
        crds.certify.   ContextMappings are mostly validated at load time.
        Stick extra checks for context mappings here.
        """
        log.verbose("Validating", repr(self.basename))

    def difference(self, other, path=()):
        """Compare `self` with `other` and return a list of difference
        tuples,  prefixing each tuple with context `path`.
        """
        other = asmapping(other, cache="readonly")
        differences = []
        for key in self.selections:
            if key not in other.selections:
                differences.append(((self.filename, other.filename), key, 
                                    "deleted " + repr(self.selections[key].filename)))
            else:
                differences.extend(self.selections[key].difference(
                    other.selections[key],
                    path + ((self.filename, other.filename),)))
        for key in other.selections:
            if key not in self.selections:
                differences.append(((self.filename, other.filename), key, 
                                    "added " + repr(other.selections[key].filename)))
        return sorted(differences)
    
    def copy(self):
        """Return an in-memory copy of this rmap as a new object."""
        return self.from_string(self.format(), self.filename, ignore_checksum=True)
    
    def reference_names(self):
        """Returns set(ref_file_name...)"""
        return sorted({ reference for selector in self.selections.values() for reference in selector.reference_names() })

    def reference_name_map(self):
        """Returns { filekind : set( ref_file_name... ) }"""
        return { filekind:selector.reference_names() for (filekind, selector) in self.selections.items() }

    def mapping_names(self, full_path=False):
        """Returns a list of mapping files associated with this Mapping"""
        name = self.filename if full_path else self.basename
        return sorted([name] + [name for selector in self.selections.values() for name in selector.mapping_names(full_path)])
 
    def file_matches(self, filename):
        """Return the "extended match tuples" which can be followed to arrive at `filename`."""
        return sorted([match for value in self.selections.values() for match in value.file_matches(filename)])
    
    def get_derived_from(self):
        """Return the Mapping object `self` was derived from, or None."""
        derived_from = None
        derived_path = locate_mapping(self.derived_from)
        if "generated" in self.derived_from or "cloning" in self.derived_from:
            log.debug("Skipping derivation checks for root mapping", repr(self.basename),
                      "derived_from =", repr(self.derived_from))
        elif os.path.exists(derived_path):
            try:
                derived_from = fetch_mapping(derived_path)
            except Exception, exc:
                log.error("Can't load parent mapping", repr(derived_path), ":", str(exc))
        else:
            log.warning("Parent mapping for", repr(self.basename), "=", 
                        repr(self.derived_from), "does not exist.")
        return derived_from

    def _check_type(self, expected_type):
        """Verify that this mapping has `expected_type` as the value of header 'mapping'."""
        assert self.mapping == expected_type, \
            "Expected header mapping='{}' in '{}' but got mapping='{}'".format(
            expected_type.upper(), self.filename, self.mapping.upper())

    def _check_nested(self, key, upper, nested):
        """Verify that `key` in `nested's` header matches `key` in `self's` header."""
        assert  upper == getattr(nested, key), \
            "selector['{}']='{}' in '{}' doesn't match header['{}']='{}' in nested file '{}'.".format(
            upper, nested.filename, self.filename, key, getattr(nested, key), nested.filename)

# ===================================================================

class ContextMapping(Mapping):
    """.pmap and .imap base class."""
    def set_item(self, key, value):
        """Add or replace and element of this mapping's selector.   For re-writing only."""
        key = str(key)
        if key.upper() in self.selector:
            key = key.upper()
            replaced = self.selector[key]
        elif key.lower() in self.selector:
            key = key.lower()
            replaced = self.selector[key]
        else:
            replaced = None
        self.selector[key] = str(value)
        return replaced

# ===================================================================

class PipelineContext(ContextMapping):
    """A pipeline context describes the context mappings for each instrument
    of a pipeline.
    """
    # Last required attribute is "difference type".
    required_attrs = ["observatory", "mapping", "parkey",
                      "name", "derived_from"]

    def __init__(self, filename, header, selector, **keys):
        ContextMapping.__init__(self, filename, header, selector, **keys)
        self.observatory = self.header["observatory"]
        self.selections = {}
        self._check_type("pipeline")
        for instrument, imapname in selector.items():
            instrument = instrument.lower()
            self.selections[instrument] = ictx = _load(imapname, **keys)
            self._check_nested("observatory", self.observatory, ictx)
            self._check_nested("instrument", instrument, ictx)
        self.instrument_key = self.parkey[0].upper()   # e.g. INSTRUME

    def get_best_references(self, header, include=None):
        """Return the best references for keyword map `header`.  If `include`
        is None,  collect all filekinds,  else only those listed.
        """
        header = dict(header)   # make a copy
        instrument = self.get_instrument(header)
        imap = self.get_imap(instrument)
        return imap.get_best_references(header, include)

    def get_imap(self, instrument):
        """Return the InstrumentMapping corresponding to `instrument`."""
        try:
            return self.selections[instrument.lower()]
        except KeyError:
            raise crds.CrdsError("Unknown instrument " + repr(instrument) +
                                  " for context " + repr(self.basename))

    def get_filekinds(self, dataset):
        """Return the filekinds associated with `dataset` by examining
        it's parameters.  Currently returns ALL filekinds for
        `dataset`s instrument.   Not all are necessarily appropriate for
        the current mode.  `dataset` can be a filename or a header dictionary.
        """
        if isinstance(dataset, basestring):
            instrument = data_file.getval(dataset,  self.instrument_key)
        elif isinstance(dataset, dict):
            instrument = self.get_instrument(dataset)
        else:
            raise ValueError("Dataset should be a filename or header dictionary.")
        return self.get_imap(instrument).get_filekinds(dataset)

    def get_instrument(self, header):
        """Get the instrument name defined by `header`."""
        try:
            return header[self.instrument_key.upper()]
        except KeyError:
            try:
                return header[self.instrument_key.lower()]
            except KeyError:
                try: # This hack makes FITS headers work prior to back-mapping to data model names.
                    return header["INSTRUME"].lower()
                except:
                    raise crds.CrdsError("Missing '%s' keyword in header" % self.instrument_key)

    def get_item_key(self, filename):
        """Given `filename` nominally to insert, return the instrument it corresponds to."""
        instrument, _filekind = utils.get_file_properties(self.observatory, filename)
        return instrument.upper()

# ===================================================================

class InstrumentContext(ContextMapping):
    """An instrument context describes the rmaps associated with each filetype
    of an instrument.
    """
    required_attrs = PipelineContext.required_attrs + ["instrument"]
    type = "instrument"

    def __init__(self, filename, header, selector, **keys):
        ContextMapping.__init__(self, filename, header, selector)
        self.observatory = self.header["observatory"]
        self.instrument = self.header["instrument"]
        self.selections = {}
        self._check_type("instrument")
        for filekind, rmap_name in selector.items():
            filekind = filekind.lower()
            self.selections[filekind] = refmap = _load(rmap_name, **keys)
            self._check_nested("observatory", self.observatory, refmap)
            self._check_nested("instrument", self.instrument, refmap)
            self._check_nested("filekind", filekind, refmap)
        self._filekinds = [key.upper() for key in self.selections.keys()]

    def get_rmap(self, filekind):
        """Given `filekind`,  return the corresponding ReferenceMapping."""
        try:
            return self.selections[filekind.lower()]
        except KeyError:
            raise crds.CrdsError("Unknown reference type " + repr(str(filekind)))

    def get_best_ref(self, filekind, header):
        """Returns the single reference file basename appropriate for `header`
        corresponding to `filekind`.
        """
#        if self.get_instrument(header).lower() != self.instrument:
#            raise CrdsError("Dataset instrument value '{}' doesn't match CRDS rules instrument '{}' from file '{}'.".format(
#                            self.get_instrument(header), self.instrument, self.filename))
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
            except Exception, exc:
                refs[filekind] = "NOT FOUND " + str(exc)
        return refs

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
        return self._filekinds
        
    def get_item_key(self, filename):
        """Given `filename` nominally to insert, return the filekind it corresponds to."""
        _instrument, filekind = utils.get_file_properties(self.observatory, filename)
        return filekind.upper()

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
        self.observatory = self.header["observatory"]
        self.instrument = self.header["instrument"]
        self.filekind = self.header["filekind"]
        self._check_type("reference")

        # TPNs define the static definitive possibilities for parameter choices
        self._tpn_valid_values = self.get_valid_values_map()
        # rmaps define the actually appearing literal parameter values
        self._rmap_valid_values = self.selector.get_value_map()
        self._required_parkeys = self.get_required_parkeys()

        rmap_relevance = getattr(self, "rmap_relevance", "always")
        if rmap_relevance == "always":
            rmap_relevance = "True"
        self._rmap_relevance_expr = rmap_relevance, MAPPING_VALIDATOR.compile_and_check(
            rmap_relevance, source=self.basename, mode="eval")

        self._parkey_relevance_exprs = \
            { parkey: (expr, MAPPING_VALIDATOR.compile_and_check(expr, source=self.basename, mode="eval")) \
             for (parkey,expr) in getattr(self, "parkey_relevance", {}).items() }

        # header precondition method, e.g. crds.hst.acs.precondition_header
        # this is optional code which pre-processes and mutates header inputs
        # set to identity if not defined.
        try:
            preconditioner = utils.get_object("crds", self.observatory, self.instrument, "precondition_header")
        except ImportError:
            preconditioner = lambda self, header: header
        self._precondition_header = preconditioner

        # fallback routine called when standard best refs fails
        # set to return None if not defined.
        try:
            fallback = utils.get_object("crds", self.observatory, self.instrument, "fallback_header")
        except ImportError:
            fallback = lambda self, header: None
        self._fallback_header = fallback
        
    def get_best_ref(self, header_in):
        """Return the single reference file basename appropriate for
        `header_in` selected by this ReferenceMapping.
        """
        log.verbose("Getting bestrefs for", self.instrument, self.filekind,
                    "parkeys", self.parkey, verbosity=60)
        self.check_rmap_relevance(header_in)  # Is this rmap appropriate for header
        # Some filekinds, .e.g. ACS biasfile, mutate the header
        header = self._precondition_header(self, header_in)
        header = self.map_irrelevant_parkeys_to_na(header)
        try:
            return self.selector.choose(header)
        except Exception, exc:
            log.verbose("First selection failed: " + str(exc), verbosity=60)
            header = self._fallback_header(self, header_in)
            if header:
                header = self.minimize_header(header)
                log.verbose("Fallback lookup on", repr(header), verbosity=60)
                header = self.map_irrelevant_parkeys_to_na(header)
                return self.selector.choose(header)
            else:
                raise

    def reference_names(self):
        """Return the list of reference file basenames associated with this
        ReferenceMapping.
        """
        return self.selector.reference_names()

    def mapping_names(self, full_path=False):
        """Return name of this ReferenceMapping as degenerate list of 1 item."""
        return [self.filename if full_path else self.basename]

    def get_required_parkeys(self):
        """Return the list of parkey names needed to select from this rmap."""
        parkeys = []
        for key in self.parkey:
            if isinstance(key, tuple):
                parkeys += list(key)
            else:
                parkeys.append(key)
        return parkeys

    def get_extra_parkeys(self):
        """Return a tuple of parkeys which are not directly matched.   These correspond
        to HST dataset parkeys which were used to compute the values of other keys 
        which *are* used to match.   These keys appear in HST rmaps with constant
        universal values of N/A.  At rmap update time,  these keys need to be mapped
        to N/A in the event they're actually defined in the reference to avoid creating
        new rules for that specific case when the parameter is not really intended for matching.
        """
        return self.extra_keys if hasattr(self, "extra_keys") else ()

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
        required_keys = self.get_required_parkeys()
        valid_values = {}
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
                    values = tuple([utils.condition_value(val) for val in values])
                valid_values[info.name] = values
        return valid_values

    def validate_mapping(self, trap_exceptions=False):
        """Validate the contents of this rmap against the TPN for this
        filekind / reftype.   Each field of each Match tuple must have a value
        OK'ed by the TPN.  UseAfter dates must be correctly formatted.
        """
        log.verbose("Validating", repr(self.basename))
        try:
            self.selector.validate_selector(self._tpn_valid_values, trap_exceptions)
        except Exception, exc:
            if trap_exceptions == mapping_type(self):
                log.error("invalid mapping:", self.instrument, self.filekind, ":", str(exc))
            elif trap_exceptions == "debug":
                raise
            else:
                raise ValidationError(repr(self) + " : " + str(exc))

    def file_matches(self, filename):
        """Return a list of the match tuples which refer to `filename`."""
        sofar = ((("observatory", self.observatory),
                  ("instrument",self.instrument),
                  ("filekind", self.filekind),),)
        return sorted(self.selector.file_matches(filename, sofar))

    def difference(self, other, path=()):
        """Return the list of difference tuples between `self` and `other`,
        prefixing each tuple with context `path`.
        """
        other = asmapping(other, cache="readonly")
        return self.selector.difference(other.selector, path +
                ((self.filename, other.filename),))

    def check_rmap_relevance(self, header):
        """Raise an exception if this rmap's relevance expression evaluated
        in the context of `header` returns False.
        """
        # header keys and values are upper case.  rmap attrs are lower case.
        try:
            source, compiled = self._rmap_relevance_expr
            relevant = eval(compiled, {}, header)
            log.verbose("Filekind ", self.instrument, self.filekind,
                        "is relevant: ", relevant, repr(source), verbosity=60)
        except Exception, exc:
            log.warning("Relevance check failed: " + str(exc))
        else:
            if not relevant:
                raise IrrelevantReferenceTypeError(
                    "Rmap does not apply to the given parameter set.")

    def map_irrelevant_parkeys_to_na(self, header):
        """Evaluate any relevance expression for each parkey, and if it's
        false,  then change the value to N/A.
        """
        header2 = dict(header)
        for parkey in self._required_parkeys:  # ensure all parkeys defined
            if parkey not in header:
                header2[parkey] = "UNDEFINED"
        header = dict(header)  # copy
        for parkey in self._required_parkeys:  # Only add/overwrite irrelevant
            lparkey = parkey.lower()
            if lparkey in self._parkey_relevance_exprs:
                source, compiled = self._parkey_relevance_exprs[lparkey]
                relevant = eval(compiled, {}, header2)
                log.verbose("Parkey", self.instrument, self.filekind, lparkey,
                            "is relevant:", relevant, repr(source), verbosity=60)
                if not relevant:
                    header[parkey] = "N/A"
        return header
    
    def insert(self, header, value):
        """Dynamically add a new selection case to a copy of this rmap and
        return the copy.
        """
        new = self.copy()
        new.selector.modify(header, value, self._tpn_valid_values)
        return new
        
# ===================================================================

def _load(mapping, **keys):
    """Stand-off function to call load_mapping, fetch_mapping, or get_cached_mapping
    depending on the "loader" value of `keys`.
    """
    return keys["loader"](mapping, **keys)

def get_cached_mapping(mapping, **keys):
    """Load `mapping` from the file system or cache,  adding it and all it's
    descendents to the cache.
    
    NOTE:   mutations to the mapping are reflected in the cache.   This call is
    not suitable for experimental mappings which need to be reloaded from the
    file system since the cached version will be returned instead.   This call
    always returns the same Mapping object for a given set of parameters so it
    should not be used where a copy is required.

    Return a PipelineContext, InstrumentContext, or ReferenceMapping.
    """
    keys["loader"] = get_cached_mapping
    return _load_mapping(mapping, **keys)

def fetch_mapping(mapping, **keys):
    """Load any `mapping`,  exploiting Mapping's already in the cache but not
    adding anything extra.   This is safe for experimental mappings and temporaries
    because new mappings not in the cache are not added to the cache.
    
    This call only returns a copy of mappings not already in the cache.
    
    Return a PipelineContext, InstrumentContext, or ReferenceMapping.
    """
    keys["loader"] = fetch_mapping
    return _load_mapping.readonly(mapping, **keys)

def load_mapping(mapping, **keys):
    """Load any `mapping`,  ignoring the cache.   Returns a unique object
    for each call.   Slow but safe for any use,  reads every file and 
    returns a new copy.
    
    Return a PipelineContext, InstrumentContext, or ReferenceMapping.
    """
    keys["loader"] = load_mapping
    return _load_mapping.uncached(mapping, **keys)

@utils.xcached(omit_from_key=["loader", "ignore_checksum"])
def _load_mapping(mapping, **keys):
    """_load_mapping fetches `mapping` from the file system or cache."""
    if mapping.endswith(".pmap"):
        cls = PipelineContext
    elif mapping.endswith(".imap"):
        cls = InstrumentContext
    elif mapping.endswith(".rmap"):
        cls = ReferenceMapping
    else:
        m = Mapping.from_file(mapping, **keys)
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

def asmapping(filename_or_mapping, cached=False, **keys):
    """Return the Mapping object corresponding to `filename_or_mapping`.
    filename_or_mapping must either be a string (filename to be loaded) or 
    a Mapping subclass which is simply returned.
    """
    if isinstance(filename_or_mapping, Mapping):
        return filename_or_mapping
    elif isinstance(filename_or_mapping, basestring):
        if cached in [False, "uncached"]:
            return load_mapping(filename_or_mapping, **keys)
        elif cached in [True, "cached"]:
            return get_cached_mapping(filename_or_mapping, **keys)
        elif cached == "readonly":
            return fetch_mapping(filename_or_mapping, **keys)
        else:
            raise ValueError("asmapping: cached must be in [True, 'cached', False, 'uncached','readonly']")
    else:
        raise TypeError("asmapping: parameter should be a string or mapping.")

# =============================================================================

"""glob_pattern may not identify file type,  hence discrete versions."""

def list_references(glob_pattern, observatory, full_path=False):
    """Return the list of cached references for `observatory` which match `glob_pattern`."""
    pattern = config.locate_reference(glob_pattern, observatory)
    return _glob_list(pattern, full_path)

def list_mappings(glob_pattern, observatory, full_path=False):
    """Return the list of cached mappings for `observatory` which match `glob_pattern`."""
    pattern = config.locate_mapping(glob_pattern, observatory)
    return _glob_list(pattern, full_path)

def _glob_list(pattern, full_path=False):
    """Return the sorted glob of `pattern`, with/without path depending on `full_path`."""
    if full_path:
        return sorted(glob.glob(pattern))
    else:
        return sorted([os.path.basename(fpath) for fpath in glob.glob(pattern)])
        
# =============================================================================

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
        if config.is_mapping(mapping):
            return os.path.splitext(mapping)[1][1:]
        else:
            mapping = fetch_mapping(mapping, ignore_checksum=True)
    if isinstance(mapping, PipelineContext):
        return "pmap"
    elif isinstance(mapping, InstrumentContext):
        return "imap"
    elif isinstance(mapping, ReferenceMapping):
        return "rmap"
    else:
        raise ValueError("Unknown mapping type for " + repr(Mapping))
# ===================================================================

def get_best_references(context_file, header, include=None, condition=False):
    """Compute the best references for `header` for the given CRDS
    `context_file`.   This is a local computation using local rmaps and
    CPU resources.   If `include` is None,  return results for all
    filekinds appropriate to `header`,  otherwise return only those
    filekinds listed in `include`.
    """
    ctx = asmapping(context_file, cached=True)
    minheader = ctx.minimize_header(header)
    if condition:
        minheader = utils.condition_header(minheader)
    return ctx.get_best_references(minheader, include=include)


def test():
    """Run module doctests."""
    import doctest
    from crds import rmap
    return doctest.testmod(rmap)

if __name__ == "__main__":
    print test()
