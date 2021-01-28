"""This module supports loading all the data components required to make
a CRDS lookup table for an instrument.

get_cached_mapping loads the closure of the given context file from the
local CRDS store,  caching the result.

>>> p = get_cached_mapping("hst.pmap")

The initial HST pipeline mappings are self-consistent and there are none
missing:

>>> p.missing_mappings()
[]

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
import os.path
import glob
import json

from collections import namedtuple

# ===================================================================

from pkg_resources import Requirement

from . import log, utils, config, selectors, substitutions

# XXX For backward compatability until refactored away.
from .config import locate_file, locate_mapping, locate_reference
from .config import mapping_exists, is_mapping

from . import exceptions as crexc
from .custom_dict import LazyFileDict
from .mapping_verifier import MAPPING_VERIFIER
from .log import srepr
from .constants import ALL_OBSERVATORIES, INSTRUMENT_KEYWORDS

# from crds import data_file   (deferred to actual uses)

# ===================================================================

__all__ = [
    "Mapping",
    "ContextMapping",
    "PipelineContext",
    "InstrumentContext",
    "ReferenceMapping",
    "get_cached_mapping",
    "load_mapping",
    "fetch_mapping",
    "asmapping",
    "locate_mapping",
    "list_mappings",
    "list_references",
    "get_best_references",
    "mapping_type",
]

# ===================================================================

Filetype = namedtuple("Filetype","header_keyword,extension,rmap")
Failure  = namedtuple("Failure","header_keyword,message")
Filemap  = namedtuple("Filemap","date,file,comment")

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
        if isinstance(val, str) and not (val.startswith("(") and val.endswith(")")):
            val = val.lower()
        return val

    def get(self, key, default):
        if key in self:
            return self[key]
        else:
            return default

    def __repr__(self):
        """
        >> LowerCaseDict([("this","THAT"), ("another", "(ESCAPED)")])
        LowerCaseDict({'this': 'that', 'another': '(ESCAPED)'})
        """
        return self.__class__.__name__ + "({})".format(repr({ key: self[key] for key in self }))

# ===================================================================

class Mapping:
    """Mapping is the abstract baseclass for PipelineContext,
    InstrumentContext, and ReferenceMapping.
    """
    required_attrs = ["mapping", "parkey", "name", "derived_from"]

    # Strictly speaking,  belongs to ContextMapping, need some default though
    # If False,  only specifies nested Mappings by filename
    specifies_references = False

    # no precursor file if derived_from contains any of these.
    null_derivation_substrings = ("generated", "cloning", "by hand")

    def __init__(self, filename, header, selector, **keys):
        self.filename = filename
        self.header = LowerCaseDict(header)   # consistent lower case values
        self.selector = selector
        self.keys = keys
        # Keys should already be as good as they get
        self.comment = keys.pop("comment", None)
        self.path = keys.get("path", None)
        for name in self.required_attrs:
            if name not in self.header:
                raise crexc.MissingHeaderKeyError(
                    "Required header key " + repr(name) + " is missing.")
        # Header aren't known good/present until checked above.
        self.mapping = self.header["mapping"]
        self.parkey = self.header["parkey"]
        self.extra_keys = tuple(self.header.get("extra_keys", ()))

    def _check_type(self):
        """Verify that the 'mapping' element of the header matches 'self.mapping_type'."""
        assert self.mapping == self.mapping_type, \
            "Expected header mapping='{}' but got mapping='{}' in '{}'".format(
                self.mapping_type, self.mapping.upper(), self.filename)

    def validate_mapping(self):
        """Validate `self` only implementing any checks to be performed by
        crds.certify.   ContextMappings are mostly validated at load time.
        Stick extra checks for context mappings here.
        """
        log.verbose("Validating", repr(self.basename), "with parameters", repr(self.parkey))
        self.validate()

    def validate(self):
        """Perform generic recursive Mapping checks, including definition of all
        required header fields as defined by Mapping class/sub-class.  Since
        this requires loading all sub-mappings, it is factored out to facilitate
        demand based loading elsewhere.

        Other methods of validation are performed when a Mapping is loaded,  including
        sha1sum and acceptability of byte codes,  neither of which requires loading
        sub-mappings.
        """
        self._check_type()

    def check_observatory(self):
        """Verify self.observatory is a supported observatory."""
        assert self.observatory in ALL_OBSERVATORIES, \
            "Invalid observatory " + repr(self.observatory) + " in " + repr(self.filename)

    def check_instrument(self):
        """Verify self.instrument is a supported instrument."""
        assert self.instrument in self.obs_package.INSTRUMENTS, \
            "Invalid instrument " + repr(self.instrument) + " in " + repr(self.filename)

    def check_filekind(self):
        """Verify self.filekind is a supported filekind."""
        assert self.filekind in self.obs_package.FILEKINDS, \
            "Invalid filekind " + repr(self.filekind) + " in " + repr(self.filename)

    def _trace_compare(self, other, show_equal=False):
        utils.trace_compare(self, other, show_equal)
        for key in self.selections:
            self.selections[key]._trace_compare(other.selections[key], show_equal)

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
        if "header" in self.__dict__ and attr in self.header:
            return self.header[attr]   # Note:  header is a class which mutates values,  see LowerCaseDict.
        else:
            raise AttributeError("Invalid or missing header key " + repr(attr))

    @classmethod
    def from_s3(cls, basename, *args, **keys):
        log.verbose("Loading mapping from S3", repr(basename), verbosity=55)
        s3_uri = config.get_uri(basename)
        text = utils.get_uri_content(s3_uri)
        return cls.from_string(text, basename, *args, **keys)

    @classmethod
    def from_file(cls, basename, *args, **keys):
        """Load a mapping file `basename` and do syntax and basic validation.  If `path` is
        specified, recursively load all files relative to `path` and include path in the
        name of the mapping.
        """
        log.verbose("Loading mapping", repr(basename), verbosity=55)
        path = keys.get("path", None)
        if path:
            filename = os.path.join(path, os.path.basename(basename))
            basename = filename
        else:
            filename = config.locate_mapping(basename)
        text = utils.get_uri_content(filename)
        return cls.from_string(text, basename, *args, **keys)

    @classmethod
    def from_string(cls, text, basename="(noname)", *args, **keys):
        """Construct a mapping from string `text` nominally named `basename`."""
        keys.pop("comment", None) #  discard comment if defined
        header, selector, comment = cls._parse_header_selector(text, basename)
        mapping = cls(basename, header, selector, comment=comment, **keys)
        try:
            mapping._check_hash(text)
        except crexc.ChecksumError as exc:
            ignore = keys.get("ignore_checksum", False) or config.get_ignore_checksum()
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
        with log.augment_exception("Can't load file " + where,
                                   exception_class=crexc.MappingError):
            code = MAPPING_VERIFIER.compile_and_check(text)
            header, selector, comment = cls._interpret(code)
        return LowerCaseDict(header), selector, comment

    @classmethod
    def _interpret(cls, code):
        """Interpret a valid rmap code object and return it's header and
        selector.
        """
        namespace = {}
        namespace.update(selectors.SELECTORS)
        exec(code, namespace)
        header = LowerCaseDict(namespace["header"])
        selector = namespace["selector"]
        comment = namespace.get("comment", None)
        if isinstance(selector, selectors.Parameters):
            return header, selector.instantiate(header), comment
        elif isinstance(selector, dict):
            return header, selector, comment
        else:
            raise crexc.MappingFormatError("selector must be a dict or a Selector.")

    def missing_references(self):
        """Get the references mentioned by the closure of this mapping but not in the cache."""
        return [ ref for ref in self.reference_names() if not config.file_in_cache(self.name, self.observatory) ]

    def missing_mappings(self):
        """Get the mappings mentioned by the closure of this mapping but not in the cache."""
        return [ mapping for mapping in self.mapping_names() if not config.file_in_cache(self.name, self.observatory) ]

    @property
    def locate(self):
        """Return the "locate" module associated with self.observatory."""
        return utils.get_object("crds", self.observatory, "locate")

    @property
    def obs_package(self):
        """Return the package (__init__) associated with self.observatory."""
        return utils.get_observatory_package(self.observatory)

    @property
    def instr_package(self):
        """Return the module associated with self.instrument."""
        return utils.get_object("crds", self.observatory, self.instrument)

    def format(self):
        """Return the string representation of this mapping, i.e. pretty
        serialization.   This is currently limited to initially creating rmaps,
        not rewriting them since it is based on internal representations and
        therefore loses comments.
        """
        if self.comment:
            return "header = {0}\n\ncomment = {1}\n\nselector = {2}\n" .format(
                self._format_header(), self._format_comment(), self._format_selector())
        else:
            return "header = {0}\n\nselector = {1}\n".format(self._format_header(), self._format_selector())

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

    def _format_comment(self):
        """Return the string representation of the multi-line comment block."""
        return '"""' + self.comment + '"""'

    def write(self, filename=None):
        """Write out this mapping to the specified `filename`,
        or else self.filename. DOES NOT PRESERVE COMMENTS.
        """
        if filename is None:
            filename = self.filename
        else:
            self.filename = filename
        self.header["sha1sum"] = self._get_checksum(self.format())
        with open(filename, "w+") as handle:
            handle.write(self.format())

    def _check_hash(self, text):
        """Verify that the mapping header has a checksum and that it is
        correct,  else raise an appropriate exception.
        """
        old = self.header.get("sha1sum", None)
        if old is None:
            raise crexc.ChecksumError("sha1sum is missing in " + repr(self.basename))
        if self._get_checksum(text) != self.header["sha1sum"]:
            raise crexc.ChecksumError("sha1sum mismatch in " + repr(self.basename))

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

    @utils.cached
    def get_required_parkeys(self):
        """Determine the set of parkeys required for this mapping and all the mappings selected by it."""
        parkeys = set(self.parkey)
        parkeys |= set(self.header.get("extra_keys",[]))
        if hasattr(self, "selections"):
            for selection in self.selections.normal_values():
                parkeys |= set(selection.get_required_parkeys())
        return sorted(parkeys)

    def minimize_header(self, header):
        """Return only those items of `header` which are required to determine
        bestrefs.   Missing keys are set to 'UNDEFINED'.
        """
        header = self.locate.fits_to_parkeys(header)   # reference vocab --> dataset vocab
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
        from crds import data_file
        header = data_file.get_conditioned_header(dataset, original_name=original_name)
        return self.minimize_header(header)

    def difference(self, new_mapping, path=(), pars=(), include_header_diffs=False, recurse_added_deleted=False):
        """Compare `self` with `new_mapping` and return a list of difference
        tuples,  prefixing each tuple with context `path`.
        """
        new_mapping = asmapping(new_mapping, cache="readonly")
        log.verbose("Difference:", self.filename, "vs.",new_mapping.filename)
        differences = self.difference_header(new_mapping, path=path, pars=pars) if include_header_diffs else []
        for key in self.selections:  # Check for deleted or replaced keys in self / old mapping.
            if key not in new_mapping.selections:   # deletions from self
                diff = selectors.DiffTuple(
                    * path + ((self.filename, new_mapping.filename), (key,),
                    "deleted " + repr(self._value_name(key))),
                    parameter_names = pars + (self.diff_name, self.parkey, "DIFFERENCE",))
                if recurse_added_deleted and self._is_normal_value(key):
                    # Get tuples for all implicitly deleted nested files.
                    nested_diffs = self.selections[key].diff_files("deleted",
                        path = path + ((self.filename,),), pars = pars + (self.diff_name,),)
                else: # either no recursion or key is special and cannot be recursed.
                    nested_diffs = []
            elif self._value_name(key) != new_mapping._value_name(key):
                # replacements in self
                # different basenames identify context-to-context updates
                # different filenames identify cache-to-cache differences
                if self._value_xsum(key) != new_mapping._value_xsum(key):
                    # omit identical files from report of diffs (cache-to-cache)
                    # if contents are different,  include a diff tuple
                    # otherwise assume higher level file at different path
                    diff = selectors.DiffTuple(
                        * (path + ((self.filename, new_mapping.filename), (key,),
                                   "replaced " + repr(self._value_name(key)) + " with " + repr(new_mapping._value_name(key)))),
                        parameter_names = pars + (self.diff_name, self.parkey, "DIFFERENCE",))
                else:
                    # higher levels file identical, nested cache-to-cache files may differ
                    diff = None
                if self._is_normal_value(key) and new_mapping._is_normal_value(key):   # mapping replacements
                    # recursion needed if both selections are mappings.
                    nested_diffs = self.selections[key].difference( new_mapping.selections[key],
                        path = path + ((self.filename, new_mapping.filename,), ), pars = pars + (self.diff_name,),
                        include_header_diffs=include_header_diffs, recurse_added_deleted=recurse_added_deleted)
                elif recurse_added_deleted:  # include added/deleted cases from normal mapping replacing special, vice versa
                    if self._is_normal_value(key):  # new_mapping is special
                        nested_diffs = self.selections[key].diff_files("deleted",
                            path = path + ((self.filename,),), pars = pars + (self.diff_name,),)
                    elif new_mapping._is_normal_value(key):   # self is special
                        nested_diffs = new_mapping.selections[key].diff_files("added",
                            path = path + ((self.filename,),), pars = pars + (self.diff_name,),)
                    else:  # recurse but both special,  handled by basic diff above.
                        nested_diffs = []
                else:  # No recursion,  handled by basic diff above.
                    nested_diffs = []
            else:  # values are the same,  no diff or nested diffs.
                diff = None
                nested_diffs = []
            # Nullify intermediate diffs based solely on path names for cache-to-cache comparisons
            # Cache-to-cache difference is tricky,  because recursion is required but higher level
            # diffs by path-only are uninteresting.
            if self.basename == new_mapping.basename and not nested_diffs:
                diff = None
            if diff:
                differences.append(diff)
            differences.extend(nested_diffs)
        for key in new_mapping.selections:
            if key not in self.selections:      # Additions to self
                diff = selectors.DiffTuple(
                    * path + ((self.filename, new_mapping.filename), (key,),
                    "added " + repr(new_mapping._value_name(key))),
                    parameter_names = pars + (self.diff_name, self.parkey, "DIFFERENCE",))
                differences.append(diff)
                if recurse_added_deleted and new_mapping._is_normal_value(key):
                    # Get tuples for all implicitly added nested files.
                    nested_adds = new_mapping.selections[key].diff_files("added",
                        path = path + ((self.filename,),), pars = pars + (self.diff_name,),)
                    differences.extend(nested_adds)
            else: # replacement case already handled in first for-loop,  not needed in reverse.
                pass
        return sorted(differences)

    def diff_files(self, added_deleted, path=(), pars=()):
        """Return the list of diff tuples for all nested changed files in a higher level addition
        or deletion.   added_deleted should be "added" or "deleted"
        """
        diffs = []
        for key, selection in self.selections.items():
            if self._is_normal_value(key):
                diffs.extend(selection.diff_files(added_deleted, path + (key,), pars + (self.diff_name,)))
            else:
                delete_special = selectors.DiffTuple(
                        * (path + ((self.filename,), (key,),
                        added_deleted + " " + repr(self._value_name(key)))),
                        parameter_names = pars + (self.diff_name, self.parkey, "DIFFERENCE",))
                diffs.append(delete_special)
        return diffs

    def _is_normal_value(self, key):
        """Return True IFF the value of selection `key` is not special, i.e. N/A or OMIT."""
        return not MappingSelectionsDict.is_special_value(self.selections[key])

    def _value_name(self, key):
        """Return either a special value,  or the filename of the loaded mapping."""
        value = self.selections[key]
        return value if MappingSelectionsDict.is_special_value(value) else value.filename

    def _value_xsum(self, key):
        """Return selections[key] if it is a special value, otherwise assume it is a mapping
        and return the sha1sum header field.
        """
        value = self.selections[key]
        return value if MappingSelectionsDict.is_special_value(value) else value.sha1sum

    def difference_header(self, other, path=(), pars=()):
        """Compare `self` with `other` and return a list of difference
        tuples,  prefixing each tuple with context `path`.
        """
        other = asmapping(other, cache="readonly")
        differences = []
        for key in self.header:
            if key not in other.header:
                diff = selectors.DiffTuple(
                    * path + ((self.filename, other.filename), "deleted header " + repr(key) + " = " + repr(self.header[key])),
                    parameter_names = pars + (self.diff_name, "DIFFERENCE",))
                differences.append(diff)
            elif self.header[key] != other.header[key]:
                diff = selectors.DiffTuple(
                    * path + ((self.filename, other.filename), "header replaced " + repr(key) + " = " + repr(self.header[key]) + " with " + repr(other.header[key])),
                    parameter_names = pars + (self.diff_name, "DIFFERENCE",))
                differences.append(diff)
        for key in other.header:
            if key not in self.header:
                diff = selectors.DiffTuple(
                    * path + ((self.filename, other.filename), "header added " + repr(key) + " = " + repr(other.header[key])),
                    parameter_names = pars + (self.diff_name, "DIFFERENCE",))
                differences.append(diff)
        return sorted(differences)

    @property
    def diff_name(self):
        """Name used to identify mapping item in DiffTuple's"""
        return self.__class__.__name__ # .replace("Context","").replace("Mapping","")

    def copy(self):
        """Return an in-memory copy of this rmap as a new object."""
        return self.from_string(self.format(), self.filename, ignore_checksum=True)

    def reference_names(self):
        """Returns set(ref_file_name...)"""
        return sorted({ reference for selector in self.selections.normal_values() for reference in selector.reference_names() })

    def reference_name_map(self):
        """Returns { filekind : set( ref_file_name... ) }"""
        name_map = { filekind:selector.reference_names() for (filekind, selector) in self.selections.normal_items() }
        name_map.update(dict(self.selections.special_items()))
        return name_map

    def mapping_names(self):
        """Returns a list of mapping files associated with this Mapping"""
        return sorted([self.basename] + [name for selector in self.selections.normal_values() for name in selector.mapping_names()])

    def file_matches(self, filename):
        """Return the "extended match tuples" which can be followed to arrive at `filename`."""
        return sorted([match for value in self.selections.normal_values() for match in value.file_matches(filename)])

    def get_derived_from(self):
        """Return the Mapping object `self` was derived from, or None."""
        for substring in self.null_derivation_substrings:
            if substring in self.derived_from:
                log.info("Skipping derivation checks for root mapping", repr(self.basename),
                         "derived_from =", repr(self.derived_from))
                return None
        derived_path = locate_mapping(self.derived_from)
        if os.path.exists(derived_path):
            with log.error_on_exception("Can't load parent mapping", repr(derived_path)):
                derived_from = fetch_mapping(derived_path)
                return derived_from
            return None
        else:
            log.warning("Parent mapping for", repr(self.basename), "=", repr(self.derived_from), "does not exist.")
            return None

    def _check_nested(self, key, self_val, nested):
        """Verify that `key` in `nested's` header matches `key` in `self's` header."""
        nested_val = getattr(nested, key)
        assert  self_val == nested_val, \
            "selector['{}']='{}' in '{}' doesn't match header['{}']='{}' in nested file '{}'.".format(
            key, self_val, self.filename, key, nested_val, nested.filename)

    def todict(self, recursive=10):
        """Return a 'pure data' dictionary representation of this mapping and it's children
        suitable for conversion to json.  If `recursive` is non-zero,  return that many
        levels of the hierarchy starting with this one.   If recursive is zero,  only
        return the filename and header of the next levels down,  not the contents.
        """
        # dict required here for subsequent update.
        selections = dict([(key, val.todict(recursive-1)) if recursive-1
                            else (val.basename, val.header)
                            for (key,val) in self.selections.normal_items()])
        selections.update(dict([(key, {"name": val, "text_descr": self.obs_package.TEXT_DESCR[key]})
                                for (key,val) in self.selections.special_items()]))
        # selections.items() critical below for prior interface,  web context display
        return {
                "header" : { key: self.header[key] for key in self.header },
                "name" : self.header["name"],
                "parameters" : tuple(self.parkey),
                "selections" : list(sorted(selections.items())),
                }

    def tojson(self, recursive=10):
        """Return a JSON representation of this mapping and it's children."""
        return json.dumps(self.todict(recursive=recursive))

    def get_instrument(self, header):
        """Return the name of the instrument which corresponds to `header`.   Called for unknown-mapping types.
        Overridden by PipelineMapping which figures it out from header.
        """
        return self.instrument.upper()

    def locate_file(self, filename):
        """Return the full path (in cache or absolute) of `filename` as determined by the current environment."""
        return locate_file(filename, self.observatory)

# ===================================================================

class ContextMapping(Mapping):
    """.pmap and .imap base class."""

    required_attrs = Mapping.required_attrs + ["observatory"]

    def __init__(self, filename, header, selector, **keys):
        super(ContextMapping, self).__init__(filename, header, selector, **keys)
        self.observatory = self.header["observatory"]
        self.selections = MappingSelectionsDict(selector, self.keys)
        if config.FORCE_COMPLETE_LOAD:
            self.force_load()

    def force_load(self):
        """Ensure that all submappings are loaded, i.e. make artificial demand."""
        for selection in self.selections.normal_values():
            selection.force_load()

    def set_item(self, key, value):
        """Add or replace and element of this mapping's selector.   For re-writing only.

        Return the case-corrected value of `key` and the value that was replaced or None
        as (corrected_key, replaced_value).
        """
        key, value = str(key), str(value)
        key = self.locate.match_context_key(key)
        replaced = self.selector.get(key, None)
        self.selector[key] = value
        return key, replaced

    def validate(self):
        """Validate nested mappings, common properties for all context mappings."""
        super(ContextMapping, self).validate()
        self.check_observatory()
        for key, mapping in self.selections.normal_items():
            self._check_nested("observatory", self.observatory, mapping)
            # mapping.validate()

# ===================================================================

class PipelineContext(ContextMapping):
    """A pipeline context describes the context mappings for each instrument
    of a pipeline.
    """
    mapping_type = "pipeline"

    def __init__(self, filename, header, selector, **keys):
        super(PipelineContext, self).__init__(filename, header, selector, **keys)
        self.instrument_key = self.parkey[0].upper()   # e.g. INSTRUME

    def validate(self):
        """Implement PipelineContext validations which require loading sub-mappings here."""
        super(PipelineContext, self).validate()
        for instrument, imap in self.selections.normal_items():
            self._check_nested("instrument", instrument, imap)

        # Will raise pkg_resources.RequirementParseError if the requirement
        # is malformed:
        self.get_asdf_standard_requirement()

    def get_best_references(self, header, include=None):
        """Return the best references for keyword map `header`.  If `include`
        is None,  collect all filekinds,  else only those listed.
        """
        header = dict(header)   # make a copy
        instrument = self.get_instrument(header)
        imap = self.get_imap(instrument)
        return imap.get_best_references(header, include)

    def get_old_references(self, header, include=None):
        """Return the old references defined in keyword map `header` using this
        context to define the types to return when `include` is None.

        >>> p = get_cached_mapping("hst.pmap")

        >>> h = {'CENTERA1': '513.0', 'CENTERA2': '513.0', 'PHOTCORR': 'UNDEFINED', 'FLSHCORR': 'UNDEFINED', 'MEMBER_NAME': 'I9ZF01DZQ', 'MEMBER_TYPE': 'EXP-DTH', 'SUBTYPE': 'FULLIMAG', 'OSCNTAB': 'Q911321MI_OSC.FITS', 'MEANEXP': '0.0', 'PFLTFILE': 'UC72113PI_PFL.FITS', 'CHINJECT': 'NONE', 'CCDCHIP': '0.0', 'EXPSTART': '2009-12-07 16:10:34.380000', 'FLATCORR': 'UNDEFINED', 'CRTHRESH': '0.0', 'CRRADIUS': '0.0', 'ASN_ID': 'I9ZF01010', 'INSTRUME': 'WFC3', 'SUBARRAY': 'F', 'CCDAMP': 'ABCD', 'CCDOFSTA': 'UNDEFINED', 'APERTURE': 'IR', 'SIZAXIS2': '1024.0', 'SIZAXIS1': '1024.0', 'FLSHFILE': 'N/A', 'BINAXIS1': '1.0', 'BINAXIS2': '1.0', 'CCDTAB': 'T2C16200I_CCD.FITS', 'IDCTAB': 'W3M18525I_IDC.FITS', 'SKYSUB': 'UNDEFINED', 'CCDOFSTB': 'UNDEFINED', 'CCDOFSTC': 'UNDEFINED', 'CCDOFSTD': 'UNDEFINED', 'DQICORR': 'UNDEFINED', 'FLASHCUR': 'UNDEFINED', 'DATA_SET': 'I9ZF01010', 'CRSIGMAS': 'UNDEFINED', 'DARKCORR': 'UNDEFINED', 'SAMP_SEQ': 'STEP200', 'SCALENSE': '0.0', 'DRIZCORR': 'UNDEFINED', 'INITGUES': 'UNDEFINED', 'IMPHTTAB': 'WBJ1825RI_IMP.FITS', 'SHADCORR': 'UNDEFINED', 'DATA_SET_EXP': 'I9ZF01DZQ', 'CRMASK': 'F', 'MDRIZTAB': 'UBI1853PI_MDZ.FITS', 'OBSMODE': 'MULTIACCUM', 'NLINFILE': 'U1K1727MI_LIN.FITS', 'ATODCORR': 'UNDEFINED', 'BADINPDQ': '0.0', 'SHUTRPOS': 'UNDEFINED', 'DATE-OBS': '2009-12-07', 'ATODTAB': 'N/A', 'TIME-OBS': '16:10:34.380000', 'DARKFILE': 'XAG19298I_DRK.FITS', 'FILTER': 'F110W', 'BPIXTAB': 'Y711519RI_BPX.FITS', 'CCDGAIN': '2.5', 'DETECTOR': 'IR', 'BIASFILE': 'N/A', 'CRSPLIT': 'UNDEFINED', 'CRREJTAB': 'U6A1748RI_CRR.FITS', 'BIASCORR': 'UNDEFINED'}

        >>> import pprint
        >>> pprint.pprint(p.get_old_references(h))
        {'ATODTAB': 'N/A',
         'BIASFILE': 'N/A',
         'BPIXTAB': 'Y711519RI_BPX.FITS',
         'CCDTAB': 'T2C16200I_CCD.FITS',
         'CRREJTAB': 'U6A1748RI_CRR.FITS',
         'DARKFILE': 'XAG19298I_DRK.FITS',
         'FLSHFILE': 'N/A',
         'IDCTAB': 'W3M18525I_IDC.FITS',
         'IMPHTTAB': 'WBJ1825RI_IMP.FITS',
         'MDRIZTAB': 'UBI1853PI_MDZ.FITS',
         'NLINFILE': 'U1K1727MI_LIN.FITS',
         'OSCNTAB': 'Q911321MI_OSC.FITS',
         'PFLTFILE': 'UC72113PI_PFL.FITS'}
        """
        header = dict(header)   # make a copy
        instrument = self.get_instrument(header)
        imap = self.get_imap(instrument)
        return imap.get_old_references(header, include)

    def get_imap(self, instrument):
        """Return the InstrumentMapping corresponding to `instrument`."""
        instrument_hacks = {
                "wfii" : "wfpc2",
            }
        instrument = instrument_hacks.get(instrument.lower(), instrument.lower())
        try:
            return self.selections[instrument]
        except (crexc.IrrelevantReferenceTypeError, crexc.OmitReferenceTypeError):
            raise
        except KeyError as exc:
            raise crexc.CrdsUnknownInstrumentError("Unknown instrument " + repr(instrument) +
                                  " for context " + repr(self.basename)) from exc

    def get_filekinds(self, dataset):
        """Return the filekinds associated with `dataset` by examining
        it's parameters.  Currently returns ALL filekinds for
        `dataset`s instrument.   Not all are necessarily appropriate for
        the current mode.  `dataset` can be a filename or a header dictionary.
        """
        if isinstance(dataset, str):
            from crds import data_file
            instrument = data_file.getval(dataset,  self.instrument_key)
        elif isinstance(dataset, dict):
            instrument = self.get_instrument(dataset)
        else:
            raise ValueError("Dataset should be a filename or header dictionary.")
        return self.get_imap(instrument).get_filekinds(dataset)

    def get_instrument(self, header):
        """Get the instrument name defined by file `header`."""
        for key in [self.instrument_key.upper(), self.instrument_key.lower()] + INSTRUMENT_KEYWORDS:
            try: # This hack makes FITS headers work prior to back-mapping to data model names.
                instr = header[key]
            except KeyError:
                continue
            else:
                if instr.upper() != "UNDEFINED":
                    break
        else:
            raise crexc.CrdsError("Missing '%s' keyword in header for determining instrument." % self.instrument_key)
        return instr.upper()

    def get_item_key(self, filename):
        """Given `filename` nominally to insert, return the instrument it corresponds to."""
        instrument, _filekind = utils.get_file_properties(self.observatory, filename)
        return instrument.upper()

    def get_equivalent_mapping(self, mapping):
        """Return the Mapping equivalent to name `mapping` in pmap `self`,  or None."""
        if mapping.endswith(".pmap"):
            return self
        else:
            instrument, _filekind = utils.get_file_properties(self.observatory, mapping)
            try:
                imap = self.get_imap(instrument)
            except Exception:
                log.warning("No equivalent instrument in", repr(self.name), "corresponding to", repr(mapping))
                return None
            else:
                return imap.get_equivalent_mapping(mapping)

    @utils.cached
    def get_required_parkeys(self):
        """Return a dictionary of matching parameters for each instrument:

            { instrument : [ matching_parkey_name, ... ], }
        """
        return { instrument : list(self.parkey) + self.selections[instrument].get_required_parkeys()
                 for instrument in self.selections.normal_keys() }

    def get_asdf_standard_requirement(self):
        raw_requirement = self.header.get("asdf_standard_requirement", None)
        if raw_requirement:
            raw_requirement = "asdf_standard " + raw_requirement
        else:
            raw_requirement = "asdf_standard"

        return Requirement.parse(raw_requirement)

# ===================================================================

class InstrumentContext(ContextMapping):
    """An instrument context describes the rmaps associated with each filetype
    of an instrument.
    """
    mapping_type = "instrument"

    required_attrs = ContextMapping.required_attrs + ["instrument"]

    def __init__(self, filename, header, selector, **keys):
        super(InstrumentContext, self).__init__(filename, header, selector, **keys)
        self.instrument = self.header["instrument"]

    def validate(self):
        """Perform InstrumentContext semantic checks which require can loading sub-mappings."""
        super(InstrumentContext, self).validate()
        self.check_instrument()
        for filekind, refmap in self.selections.normal_items():
            self._check_nested("instrument", self.instrument, refmap)
            self._check_nested("filekind", filekind, refmap)

    def get_rmap(self, filekind):
        """Given `filekind`,  return the corresponding ReferenceMapping."""
        filekind = str(filekind).lower()
        if filekind not in self.selections:
            raise crexc.CrdsUnknownReftypeError("Unknown reference type", repr(filekind))
        if MappingSelectionsDict.is_na_value(self.selections[filekind]):
            log.verbose("Reference type", repr(filekind),
                        "is declared N/A at the instrument level for", repr(self.instrument), verbosity=70)
            raise crexc.IrrelevantReferenceTypeError("Type", repr(filekind), "is N/A for", repr(self.instrument))
        if  MappingSelectionsDict.is_omit_value(self.selections[filekind]):
            log.verbose("Reference type", repr(filekind),
                        "is omitted at the instrument level for", repr(self.instrument), verbosity=70)
            raise crexc.OmitReferenceTypeError("Type", repr(filekind), "is OMITTED for", repr(self.instrument))
        return self.selections[filekind]

    def get_imap(self, instrument):
        """Make sequences like get_cached_mapping(mapping).get_imap(instrument)... work where `mapping` is an
        instrument mapping.
        """
        return self

    def get_best_references(self, header, include=None):
        """Returns a map of best references { filekind : reffile_basename }
        appropriate for this `header`.   If `include` is None, include all
        filekinds in the results,  otherwise compute and include only
        those filekinds listed.
        """
        refs = {}
        if not include:
            include = self.selections.keys()
        for filekind in include:
            log.verbose("-"*120, verbosity=55)
            filekind = filekind.lower()
            ref = None
            try:
                ref = self.get_rmap(filekind).get_best_ref(header)
            except crexc.IrrelevantReferenceTypeError:
                ref = "NOT FOUND n/a"
            except crexc.OmitReferenceTypeError:
                ref = None
            except Exception as exc:
                ref = "NOT FOUND " + str(exc)
            if ref is not None:
                refs[filekind] = ref
        log.verbose("-"*120, verbosity=55)
        return refs

    def get_old_references(self, header, include=None):
        """Returns a map of old references which were recorded in `header`,
        returning only those types listed in `include` or all types if
        `include` is None.
        """
        refs = {}
        if not include:
            include = self.selections.keys()
        include = [ key.upper() for key in include ]
        header = { key.upper() : val.strip() for (key, val) in header.items() }
        for filekind in include:
            try:
                ref = header[filekind]
                if ref == "NOT FOUND n/a":
                    ref = "N/A"
                refs[filekind] = ref
            except KeyError:
                refs[filekind] = "UNDEFINED"
        return refs

    def get_parkey_map(self):
        """Infers the legal values of each parkey from the rmap itself.
        This is a potentially different answer than that defined by the TPNs,
        the latter being considered definitive.
        Return { parkey : [legal values...], ... }
        """
        pkmap = {}
        for selection in self.selections.normal_values():
            for parkey, choices in selection.get_parkey_map().items():
                if parkey not in pkmap:
                    pkmap[parkey] = set()
                pkmap[parkey] |= set(choices)
        for parkey, choices in pkmap.items():
            pkmap[parkey] = list(pkmap[parkey])
            if "CORR" not in parkey:
                pkmap[parkey].sort()
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
        for selection in self.selections.normal_values():
            rmap_pkmap = selection.get_valid_values_map(condition)
            for key in rmap_pkmap:
                if key not in pkmap:
                    pkmap[key] = set()
                pkmap[key] |= set(rmap_pkmap[key])
        for key in self.get_parkey_map():
            if key not in pkmap:
                pkmap[key] = []    # flag a need for an unconstrained input
        if remove_special:
            specials = {"ANY","N/A"}
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
        return list(sorted(self.selections.keys()))

    def get_item_key(self, filename):
        """Given `filename` nominally to insert, return the filekind it corresponds to."""
        _instrument, filekind = utils.get_file_properties(self.observatory, filename)
        return filekind.upper() if self.observatory == "jwst" else filekind.lower()

    def get_equivalent_mapping(self, mapping):
        """Return the Mapping equivalent to name `mapping` in imap `self`, or None."""
        if mapping.endswith(".pmap"):
            log.warning("Invalid comparison context", repr(self.name), "for", repr(mapping))
            return None
        if mapping.endswith(".imap"):
            return self
        else:
            _instrument, filekind = utils.get_file_properties(self.observatory, mapping)
            try:
                rmap = self.get_rmap(filekind)
            except Exception:
                log.warning("No equivalent filekind in", repr(self.name), "corresponding to", repr(mapping))
                return None
            else:  # I think it's always just "rmap".
                return rmap.get_equivalent_mapping(mapping)

    def difference(self, *args, **keys):
        """difference specialized to add .instrument to diff."""
        diffs = super(InstrumentContext, self).difference(*args, **keys)
        for diff in diffs:
            diff.instrument = self.instrument
        return diffs

# ===================================================================

class ReferenceMapping(Mapping):
    """ReferenceMapping manages loading the rmap associated with a single
    reference filetype and instantiate an appropriate selector tree from the
    rmap header and data.
    """
    mapping_type = "reference"
    required_attrs = Mapping.required_attrs + ["observatory","instrument","filekind"]
    specifies_references = True

    def __init__(self, *args, **keys):
        super(ReferenceMapping, self).__init__(*args, **keys)
        self.observatory = self.header["observatory"]
        self.instrument = self.header["instrument"]
        self.filekind = self.header["filekind"]

        self.schema_uri = self.header.get("schema_uri", None)

        self._reffile_switch = self.header.get("reffile_switch", "NONE").upper()
        self._reffile_format = self.header.get("reffile_format", "IMAGE").upper()
        self._reffile_required = self.header.get("reffile_required", "NONE").upper()

        # header precondition method, e.g. crds.hst.acs.precondition_header
        # TPNs define the static definitive possibilities for parameter choices
        # rmaps define the actually appearing literal parameter values
        self._rmap_valid_values = self.selector.get_value_map()
        self._required_parkeys = self.get_required_parkeys()

        # For "rmap_relevance" and "rmap_omit" expressions,  the expressions are enclosed in ()
        # to ensure no case conversions occur in LowerCaseDict.  Since ALWAYS is not in (),  it
        # shows up here as the standard "always".

        # if _rmap_relevance_expr evaluates to True at match-time,  this is a relevant type for that header.
        self._rmap_relevance_expr = None

        # if _rmap_omit_expr evaluates to True at match-time,  this type should be omitted from bestrefs results.
        self._rmap_omit_expr = None

        # for each parkey in parkey_relevance_exprs,  if the expr evaluates False,  it is mapped to N/A at match time.
        self._parkey_relevance_exprs = None

        # header precondition method, e.g. crds.hst.acs.precondition_header
        # this is optional code which pre-processes and mutates header inputs
        # set to identity if not defined.
        self._precondition_header = None

        # function to mutate to secondary lookup header if first lookup fails,  if defined.
        self._fallback_header = None

        # rmap-update-time hook to generate reference header variations for more complex but otherwise static lookups
        # this is a potential alternative to preconditioning and fallback which are *runtime* hooks and non-transparent
        # to someone looking at the rmap.
        self._rmap_update_headers = None

        # Actually compile lambdas for the hooks above.
        self._init_compiled()

    def __getstate__(self):
        """Return rmap pickling state,  minus lambdas and anything else that doesn't pickle."""
        state = dict(self.__dict__)
        del state["_rmap_relevance_expr"]
        del state["_rmap_omit_expr"]
        del state["_parkey_relevance_exprs"]
        del state["_precondition_header"]
        del state["_fallback_header"]
        del state["_rmap_update_headers"]
        return state

    def __setstate__(self, state):
        """Recreate rmap object from `state`,  recompiling missing __getstate__ objects on the fly."""
        self.__dict__ = dict(state)
        self._init_compiled()

    def force_load(self):
        """Nothing below ReferenceMapping is loaded."""
        pass

    def _init_compiled(self):
        """Initialize object fields which contain compiled code objects, special handling for pickling."""
        self._comment_parkeys = tuple(name.lower() for name in self.header.get("comment_parkeys", ()))
        self._rmap_relevance_expr = self.get_expr(self.header.get("rmap_relevance", "always").replace("always", "True"))
        self._rmap_omit_expr = self.get_expr(self.header.get("rmap_omit", "False"))

        relevant  = dict(self.header.get("parkey_relevance", {}))
        relevant.update({
            name : "keep_comments" for name in self._comment_parkeys
        })
        self._parkey_relevance_exprs = {
            name.lower() : self.get_expr(expr) for (name, expr) in relevant.items()
            }

        self._precondition_header = self.get_hook("precondition_header", (lambda self, header: header))
        self._fallback_header = self.get_hook("fallback_header", (lambda self, header: None))
        self._rmap_update_headers = self.get_hook("rmap_update_headers", None)

    def validate(self):
        """Validate the contents of this rmap against the TPN for this
        filekind / reftype.   Each field of each Match tuple must have a value
        OK'ed by the TPN.  UseAfter dates must be correctly formatted.
        """
        super(ReferenceMapping, self).validate()
        self.check_observatory()
        self.check_instrument()
        self.check_filekind()
        self.check_schema_uri()
        if "reference_to_dataset" in self.header:
            parkeys = self.get_required_parkeys()
            for _reference, dataset in self.reference_to_dataset.items():
                assert dataset.upper() in parkeys, \
                    "reference_to_dataset dataset keyword not in parkey keywords."
        with log.augment_exception("Invalid mapping:", self.instrument, self.filekind):
            self.selector.validate_selector(self.tpn_valid_values)

    def check_schema_uri(self):
        """
        Check that the schema URI corresponds to a schema that
        ASDF knows how to load.
        """
        import asdf

        if self.schema_uri is not None:
            with log.augment_exception("Invalid ASDF schema URI:", self.schema_uri):
                asdf.schema.load_schema(self.schema_uri)

    def get_expr(self, expr):  # secured
        """Return (expr, compiled_expr) for some rmap header expression, generally a predicate which is evaluated
        in the context of the matching header to fine tune behavior.   Screen the expr for dangerous code.
        """
        expr = utils.condition_source_code_keys(expr, self.get_required_parkeys())
        try:
            return expr, MAPPING_VERIFIER.compile_and_check(expr, source=self.basename, mode="eval")
        except crexc.MappingFormatError as exc:
            raise crexc.MappingFormatError("Can't load file " + repr(self.basename) + " : " + str(exc)) from exc

    def get_hook(self, name, default):
        """Return plugin hook function generically named `name` or `default` if `name` is not defined in
        the associated instrument package or in the rmap header.   Until hooks is defined in header,  get_hook
        will return the generically named function in the instrument package.   hooks in rmap header supports
        future versions of hooks without breaking past rmaps.

        Hooks are called basically like methods, typically as hook(self, header).   Hooks return hook-specific values.

        Nth generation hooks defined by name in rmap header "hooks" { unversioned_name : versioned_hook_name } dict.
        To unplug a hook,  define it in rmap header "hooks" like { "precondition_header" : "none" }
        """
        hooks = self.header.get("hooks", None)
        if hooks:  # Either get the replacement name,  or use the original name if not found.
            hook_name = hooks.get(name, name)
        else:  # No hooks dict,  just use the original name.
            hook_name = "_".join([name, self.instrument, self.filekind, "v1"])
        hook = getattr(self.instr_package, hook_name, default)
        if hook is not default:
            log.verbose("Using hook", repr(hook_name), "for rmap", repr(self.basename), verbosity=55)
        return hook

    # Unusual caching style implements deferred loading of .tpn files,  fairly slow.
    @property
    @utils.cached
    def tpn_valid_values(self):
        """Property, dictionary of valid values for each parameter loaded from .tpn files or equivalent."""
        return self.get_valid_values_map()

    def get_filekinds(self, dataset=None):
        """Return the filekinds associated with this dataset, but for an rmap,
        just the rmap's filekind.
        """
        return [self.filekind]

    def get_best_references(self, header, include=None):
        """Shim so that .rmaps can be used for bestrefs in place of a .pmap or .imap for single type development."""
        if include is not None and self.filekind not in include:
            raise crexc.CrdsUnknownReftypeError(self.__class__.__name__, repr(self.basename),
                                          "can only compute bestrefs for type", repr(self.filekind), "not", include)
        bestref = self.get_best_ref(header)
        if bestref is not None:
            return { self.filekind : self.get_best_ref(header) }
        else:
            return {}

    def get_best_ref(self, header):
        """Return a single best reference value associated with this .rmap and `header`.  Map exceptions
        from nested methods onto simple "NOT FOUND..." strings which are exempted from reference downloads.
        """
        try:
            return self._get_best_ref(header)
        except crexc.IrrelevantReferenceTypeError:
            return "NOT FOUND n/a"
        except crexc.OmitReferenceTypeError:
            return None
        except Exception as exc:
            if log.get_exception_trap():
                return "NOT FOUND " + str(exc)
            else:
                raise

    def _get_best_ref(self, header_in):
        """Return the single reference file basename appropriate for
        `header_in` selected by this ReferenceMapping.
        """
        header_in = dict(header_in)
        log.verbose("Getting bestrefs:", self.basename, verbosity=55)
        expr_header = utils.condition_header_keys(header_in)
        self.check_rmap_omit(expr_header)     # Should bestref be omitted based on rmap_omit expr?
        self.check_rmap_relevance(expr_header)  # Should bestref be set N/A based on rmap_relevance expr?
        # Some filekinds, .e.g. ACS biasfile, mutate the header
        header = self._precondition_header(self, header_in) # Execute type-specific plugin if applicable
        header = self.map_irrelevant_parkeys_to_na(header)  # Execute rmap parkey_relevance conditions
        try:
            bestref = self.selector.choose(header)
        except Exception as exc:
            log.verbose("First selection failed:", str(exc), verbosity=55)
            header = self._fallback_header(self, header_in) # Execute type-specific plugin if applicable
            try:
                if header:
                    header = self.minimize_header(header)
                    log.verbose("Fallback lookup on", repr(header), verbosity=55)
                    header = self.map_irrelevant_parkeys_to_na(header) # Execute rmap parkey_relevance conditions
                    bestref = self.selector.choose(header)
                else:
                    raise
            except Exception as exc:
                log.verbose("Fallback selection failed:", str(exc), verbosity=55)
                if self._reffile_required in ["YES", "NONE"]:
                    log.verbose("No match found and reference is required:",  str(exc), verbosity=55)
                    raise
                else:
                    log.verbose("No match found but reference is not required:",  str(exc), verbosity=55)
                    raise crexc.IrrelevantReferenceTypeError("No match found and reference type is not required.") from exc
        log.verbose("Found bestref", repr(self.instrument), repr(self.filekind), "=", repr(bestref), verbosity=55)
        if MappingSelectionsDict.is_na_value(bestref):
            raise crexc.IrrelevantReferenceTypeError("Rules define this type as Not Applicable for these observation parameters.")
        if MappingSelectionsDict.is_omit_value(bestref):
            raise crexc.OmitReferenceTypeError("Rules define this type to be Omitted for these observation parameters.")
        return bestref

    def reference_names(self):
        """Return the list of reference file basenames associated with this
        ReferenceMapping.
        """
        return [name for name in self.selector.reference_names() if not is_special_value(name)]

    def mapping_names(self):
        """Return name of this ReferenceMapping as degenerate list of 1 item."""
        return [self.basename]

    @utils.cached
    def get_required_parkeys(self, include_reffile_switch=True):
        """Return the list of parkey names needed to select from this rmap."""
        parkeys = []
        for key in self.parkey:
            if isinstance(key, tuple):
                parkeys += list(key)
            else:
                parkeys.append(key)
        if include_reffile_switch and self._reffile_switch != "NONE":
            parkeys.append(self._reffile_switch)
        parkeys.extend(list(self.extra_keys))
        parkeys.extend(getattr(self.obs_package, "extra_keys", []))
        return parkeys

    def get_extra_parkeys(self):
        """Return a tuple of parkeys which are not directly matched.   These correspond
        to HST dataset parkeys which were used to compute the values of other keys
        which *are* used to match.   These keys appear in HST rmaps with constant
        universal values of N/A.  At rmap update time,  these keys need to be mapped
        to N/A in the event they're actually defined in the reference to avoid creating
        new rules for that specific case when the parameter is not really intended for matching.
        """
        extra = list(self.extra_keys)
        if self._reffile_switch != "NONE":
            extra.append(self._reffile_switch)
        return tuple(extra)

    def get_parkey_map(self):
        """Based on the rmap,  return the mapping from parkeys to their
        handled values,  i.e. what this rmap says it matches against.
        Note that these are the values seen in the rmap prior to any
        substitutions which are defined in the header.

        Return { parkey : [match values, ...], ... }
        """
        parkey_map = self.selector.get_parkey_map()
        tpn_values = self.tpn_valid_values
        for key in self.get_extra_parkeys():
            if key in parkey_map and "CORR" not in key:
                continue
            parkey_map[key] = tpn_values.get(key, [])
            if key.endswith("CORR"):  #  and parkey_map[key] == []:
                parkey_map[key] = ["PERFORM", "OMIT", "NONE", "COMPLETE", "UNDEFINED"]
        return parkey_map

    def get_valid_values_map(self, condition=True):
        """Based on the TPNs,  return a mapping from each of the required
        parkeys to its valid values,

        i.e. the definitive source for what is legal for this filekind.

        return { parkey : [ valid values ] }
        """
        tpninfos = self.locate.get_all_tpninfos(self.instrument, self.filekind, "ld_tpn")
        required_keys = self.get_required_parkeys()
        valid_values = {}
        for info in tpninfos:
            if info.is_complex_constraint:
                continue
            if info.name in required_keys:
                values = info.values
                if len(values) == 1 and ":" in values[0]:
                    limits = values[0].split(":")
                    try:
                        limits = [int(float(x)) for x in limits]
                    except Exception:
                        pass
                        # sys.exc_clear()
                    else:
                        values = list(range(limits[0], limits[1]+1))
                if condition:
                    values = tuple([utils.condition_value(val) for val in values])
                valid_values[info.name] = values
        return valid_values

    def file_matches(self, filename):
        """Return a list of the match tuples which refer to `filename`."""
        sofar = ((("observatory", self.observatory),
                  ("instrument",self.instrument),
                  ("filekind", self.filekind),),)
        return sorted(self.selector.file_matches(filename, sofar))

    def difference(self, other, path=(), pars=(), include_header_diffs=False, recurse_added_deleted=False):
        """Return the list of difference tuples between `self` and `other`, prefixing each tuple with context `path`.
        Elements of `path` are named by correspnding elements of `pars`.
        """
        other = asmapping(other, cache="readonly")
        header_diffs = self.difference_header(other, path=path, pars=pars) if include_header_diffs else []
        body_diffs = self.selector.difference(other.selector,
                path = path + ((self.filename, other.filename),),
                pars = pars + (self.diff_name,))
        diffs = header_diffs + body_diffs
        for diff in diffs:
            diff.instrument = self.instrument
            diff.filekind = self.filekind
        return diffs

    def diff_files(self, added_deleted, path=(), pars=()):
        """Return the list of diff tuples for all nested changed files in a higher level addition
        or deletion.   added_deleted should be "added" or "deleted"
        """
        body_diffs = self.selector.flat_diff(added_deleted + " terminal",
                path = path + ((self.filename,)), pars = pars + (self.diff_name,))
        for diff in body_diffs:
            diff.instrument = self.instrument
            diff.filekind = self.filekind
        return body_diffs

    def check_rmap_relevance(self, header):
        """Raise an exception if this rmap's relevance expression evaluated in the context of `header` returns False.
        """
        try:
            source, compiled = self._rmap_relevance_expr
            relevant = eval(compiled, {}, header)   # secured
            log.verbose("Filekind ", repr(self.instrument), repr(self.filekind),
                        "is relevant:", relevant, repr(source), verbosity=55)
        except Exception as exc:
            log.warning("Failed checking relevance for", repr(self.instrument),
                        repr(self.filekind), "with expr", repr(source),
                        ":", str(exc))
        else:
            if not relevant:
                raise crexc.IrrelevantReferenceTypeError(
                    "Rmap does not apply to the given parameter set based on rmap_relevance expression.")

    def check_rmap_omit(self, header):
        """Return True IFF this type should be omitted based on the 'rmap_omit' header expression."""
        source, compiled = self._rmap_omit_expr
        try:
            omit = eval(compiled, {}, header)   # secured
            log.verbose("Filekind ", repr(self.instrument), repr(self.filekind),
                        "should be omitted: ", omit, repr(source), verbosity=55)
        except Exception as exc:
            log.warning("Failed checking OMIT for", repr(self.instrument),
                        repr(self.filekind), "with expr", repr(source),
                        ":", str(exc))
        else:
            if omit:
                raise crexc.OmitReferenceTypeError("rmap_omit expression indicates this type should be omitted.")

    def map_irrelevant_parkeys_to_na(self, header, keep_comments=False):
        """Evaluate any relevance expression for each parkey, and if it's
        false,  then change the value to N/A.   Changing a parkey to N/A effectively
        removes it as a consideration for bestrefs.   Changing a parkey to N/A during
        rmap updates facilitates exact case matches (replacements) ignoring irrelevant
        parameters while defining the case.   If `keep_comments` is set to True then
        irrelevant_parkeys which are also comments are not converted to N/A.

        COME FROM: This function is called both on dataset headers during bestrefs and
        on reference file headers during rmap updates with the presumption that any
        parameter required by the relevance expressions is defined in both datasets and
        reference files.
        """
        from crds import data_file
        expr_header = dict(header)
        expr_header = data_file.ensure_keys_defined(expr_header, needed_keys=self._required_parkeys)
        expr_header = utils.condition_header_keys(expr_header)
        header = dict(header)  # copy
        expr_header["keep_comments"] = keep_comments
        for parkey in self._required_parkeys:  # Only add/overwrite irrelevant
            lparkey = parkey.lower()
            if lparkey in self._parkey_relevance_exprs:
                source, compiled = self._parkey_relevance_exprs[lparkey]
                relevant = eval(compiled, {}, expr_header)  # secured
                log.verbose("Parkey", self.instrument, self.filekind, lparkey,
                            "is relevant:", relevant, repr(source), verbosity=55)
                if not relevant:
                    log.verbose("Setting irrelevant parkey", repr(parkey), "to N/A")
                    header[parkey] = "N/A"
        return header

    def insert_reference(self, reffile):
        """Returns new ReferenceMapping made from `self` inserting `reffile`."""
        header = self.get_refactor_header(reffile)
        return self.insert_header_reference(header, os.path.basename(reffile))

    def get_refactor_header(self, reffile, extra_keys=()):
        """Give reference path `reffile` return the header which should be used to insert
        the file into this rmap based on the reffile contents.

        1. Loads basic header from reffile.
        2. Ensures required parkeys are at least defined as UNDEFINED or N/A.
        3. Maps from reference file keywords and values to dataset keywords and values rmaps match on.
        """
        # Since expansion rules may depend on keys not used in matching,  get entire header
        from crds import data_file
        header = data_file.get_header(reffile, observatory=self.observatory)
        needed_keys = tuple(self.get_reference_parkeys()) + tuple(extra_keys)
        header = data_file.ensure_keys_defined(header, needed_keys=needed_keys)
        # NOTE: required parkeys are in terms of *dataset* headers,  not reference headers.
        log.verbose("insert_reference raw reffile header:\n",
                    log.PP([ (key,val) for (key,val) in header.items() if key in self.get_reference_parkeys() ]),
                    verbosity=70)
        header = self.reference_to_dataset_header(header)
        log.verbose("insert_reference transformed-to-dataset header:\n",
                    log.PP([ (key,val) for (key,val) in header.items() if key in self.get_reference_parkeys() ]),
                    verbosity=70)
        return header

    def reference_to_dataset_header(self, header):
        """Convert the applicable keys in `header` from how they appear in the reference
        file to how they appear in the rmap. Multiple conversion activities:

        1. Mapping from reference file keywwords to corresponding dataset keywords.
        2. Expansion of conditional substitutions defined in e.g. crds.hst.substitutions.dat
        3. Any header conditioning,  normalization of values.
        4. Irrelevant parkeys are mapped to N/A if discernable based on `header`.
        5. extra_parkey keys are mapped to N/A.
        """
        # The reference file key and dataset key matched aren't always the same!
        # Specifically ACS BIASFILE NUMCOLS,NUMROWS and NAXIS1,NAXIS2
        # Also, DATE-OBS, TIME-OBS  <-->  USEAFTER
        header = self.locate.reference_keys_to_dataset_keys(self, header)

        # Reference files specify things like ANY which must be expanded to
        # glob patterns for matching with the reference file.
        header = substitutions.expand_wildcards(self, header)

        # Translate header values to .rmap normalized form,  e.g. utils.condition_value()
        header = self.locate.condition_matching_header(self, header)

        # Evaluate parkey relevance rules in the context of header to map
        # mode irrelevant parameters to N/A.
        # XXX not clear if/how this works with expanded wildcard or-patterns.
        header = self.map_irrelevant_parkeys_to_na(header, keep_comments=True)

        # The "extra" parkeys always appear in the rmap with values of "N/A".
        # The dataset value of the parkey is typically used to compute other parkeys
        # for HST corner cases.   It's a little stupid for them to appear in the
        # rmap match tuples,  but the dataset values for those parkeys are indeed
        # relevant,  and it does provide a hint that magic is going on.  At rmap update
        # time,  these parkeys need to be set to N/A even if they're actually defined.
        for key in self.get_extra_parkeys():
            log.verbose("Mapping extra parkey", repr(key), "from", header[key], "to 'N/A'.")
            header[key] = "N/A"
        return header

    def insert_header_reference(self, header, reffile):
        """Returns new ReferenceMapping made from `self` inserting `reffile`."""
        if self._rmap_update_headers:
            # Generate variations on header as needed to emulate header "pre-conditioning" and fall back scenarios.
            for hdr in self._rmap_update_headers(self, header):
                new = self.insert(hdr, reffile)
        else:
            # almost all instruments/types do this.
            new = self.insert(header, reffile)
        return new

    def get_reference_parkeys(self):
        """Return parkey names from the reference file perspective,  this can be a superset
        of the obvious parkey count due to redundant keyword expressions resulting from
        reference_to_dataset and mixed filetypes (some translated,  some not.)
        """
        dataset_parkeys = self.get_required_parkeys()
        if "reference_to_dataset" in self.header:
            for reference, dataset in self.reference_to_dataset.items():
                if dataset in dataset_parkeys:
                    dataset_parkeys.append(reference)
        return tuple(sorted(set(dataset_parkeys)))

    def insert(self, header, value):
        """Given reference file `header` and terminal `value`, insert the value into a copy
        of this rmap and return it.
        """
        new = self.copy()
        new.selector.insert(header, value,
            self.tpn_valid_values if not config.ALLOW_BAD_PARKEY_VALUES else {})
        return new

    def delete(self, terminal):
        """Remove all instances of `terminal` (nominally a filename) from `self`."""
        new = self.copy()
        terminal = os.path.basename(terminal)
        deleted_count = new.selector.delete(terminal)
        if deleted_count == 0:
            raise crexc.CrdsError("Terminal '%s' could not be found and deleted." % terminal)
        return new

    def todict(self, recursive=10):
        """Return a 'pure data' dictionary representation of this mapping and it's children
        suitable for conversion to json.  `recursive` is ignored.
        """
        nested = self.selector.todict_flat()
        return {
                "header" : { key : self.header[key] for key in self.header },
                "text_descr" : self.obs_package.TEXT_DESCR[self.filekind],
                "parameters" : tuple(nested["parameters"]),
                "selections" : nested["selections"]
                }

    def get_equivalent_mapping(self, mapping):
        """Return `self` for comparison if `mapping` name specifies an rmap, otherwise None."""
        if not mapping.endswith(".rmap"):
            log.warning("Invalid comparison context", repr(self.name), "for", repr(mapping))
            return None
        return self

    def _trace_compare(self, other, show_equal=False):
        utils.trace_compare(self, other, show_equal)

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
        if config.S3_ENABLED:
            m = Mapping.from_s3(mapping, **keys)
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

    if config.S3_ENABLED:
        return cls.from_s3(mapping, **keys)
    else:
        return cls.from_file(mapping, **keys)

def asmapping(filename_or_mapping, cached=False, **keys):
    """Return the Mapping object corresponding to `filename_or_mapping`.
    filename_or_mapping must either be a string (filename to be loaded) or
    a Mapping subclass which is simply returned.

    cached can be set to:

    False, "uncached"   ignore the mappings cache,  always reload,  don't add to cache
    "readonly"          load the mapping from the cache if possible,  don't add to the cache if not present
    True, "cached"      load the mapping from the cache if possible, add it to the cache if not present

    'readonly' is for experimental/proposed mappings which should not permanently exist in the
    cache because they may later be rejected and/or redefined.
    """
    if isinstance(filename_or_mapping, Mapping):
        return filename_or_mapping
    elif isinstance(filename_or_mapping, str):
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

class MappingSelectionsDict(LazyFileDict):
    """MappingSelectionsDict is a LazyFileDict with customized special values specific to CRDS.
    Mappings.

    >>> selections = MappingSelectionsDict({"this" : "N/A", "that":"hst_acs.imap"})

    >>> selections.normal_keys()
    ['that']

    >>> selections.special_keys()
    ['this']

    >>> selections.normal_values()
    [InstrumentContext('hst_acs.imap')]

    >>> selections.special_values()
    ['N/A']

    >>> list(selections.normal_items())
    [('that', InstrumentContext('hst_acs.imap'))]

    >>> list(selections.special_items())
    [('this', 'N/A')]

    """
    na_values_set = { "N/A", "TEMP_N/A", "n/a", "temp_n/a"}
    omit_values_set = { "OMIT", "TEMP_OMIT", "omit", "temp_n/a"}
    special_values_set = na_values_set | omit_values_set

    test_descr = {
        "N/A" : "Not Applicable",
        "TEMP_N/A" : "Temporarily Not Applicable",
        }

    def __init__(self, selector, load_keys={}):
        if "loader" not in load_keys:
            load_keys["loader"] = load_mapping
        super(MappingSelectionsDict, self).__init__(selector, load_keys)

    def transform_key(self, key):
        """Perform key lookups uniformly in lower case regardless of input."""
        return key.lower()

    @classmethod
    def is_na_value(cls, value):
        return isinstance(value, str) and value in cls.na_values_set

    @classmethod
    def is_omit_value(cls, value):
        return isinstance(value, str) and value in cls.omit_values_set

# =============================================================================

"""glob_pattern may not identify file type,  hence discrete versions."""

def list_references(glob_pattern, observatory, full_path=False):
    """Return the list of cached references for `observatory` which match `glob_pattern`."""
    references = []
    for path in utils.get_reference_paths(observatory):
        pattern = os.path.join(path, glob_pattern)
        references.extend(_glob_list(pattern, full_path))
    if full_path:
        references = [ref for ref in references if not os.path.isdir(ref)]
    return sorted(set(references))

def list_mappings(glob_pattern, observatory, full_path=False):
    """Return the list of cached mappings for `observatory` which match `glob_pattern`."""
    pattern = config.locate_mapping(glob_pattern, observatory)
    mappings = _glob_list(pattern, full_path)
    if full_path:
        mappings = [mapping for mapping in mappings if not os.path.isdir(mapping)]
    return sorted(set(mappings))

def list_pickles(glob_pattern, observatory, full_path=False):
    """Return the list of cached mappings for `observatory` which match `glob_pattern`."""
    pattern = config.locate_pickle(glob_pattern, observatory)
    pickles = _glob_list(pattern, full_path)
    if full_path:
        pickles = [pkl for pkl in pickles if not os.path.isdir(pkl)]
    return sorted(set(pickles))

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
    if isinstance(mapping, str):
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

def is_special_value(filename):
    """Return True IFF `filename` is one of the special values which
    does not correspond to a file, e.g. N/A.

    >>> is_special_value("foo.fits")
    False

    >>> is_special_value("N/A")
    True
    """
    return MappingSelectionsDict.is_special_value(str(filename))

# ============================================================================

def replace_rmap_text(rmapping, new_filename, old_text, new_text, *args, **keys):
    """Do simple text replacement from `old_text` to `new_text` in `rmapping`.
    """
    log.info("Replacing", srepr(old_text), "with", srepr(new_text), "in",
             srepr(rmapping.basename), "to", srepr(new_filename))
    original_rmap = str(rmapping)
    new_rmap = original_rmap.replace(old_text, new_text)
    new_mapping = ReferenceMapping.from_string(new_rmap, ignore_checksum=True)
    new_mapping.write(new_filename)

# ===================================================================

def get_best_references(context_file, header, include=None, condition=True):
    """Compute the best references for `header` for the given CRDS
    `context_file`.   This is a local computation using local rmaps and
    CPU resources.   If `include` is None,  return results for all
    filekinds appropriate to `header`,  otherwise return only those
    filekinds listed in `include`.
    """
    ctx = asmapping(context_file, cached=True)
    minheader = ctx.minimize_header(header)
    log.verbose("Bestrefs header:\n", log.PP(minheader))
    if condition:
        minheader = utils.condition_header(minheader)
    return ctx.get_best_references(minheader, include=include)


def test():
    """Run module doctests."""
    import doctest
    from crds.core import rmap
    return doctest.testmod(rmap)

if __name__ == "__main__":
    print(test())
