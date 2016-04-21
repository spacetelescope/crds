"""This module consolidates a number of aspects of reference type definition which were
originally reverse engineered from CDBS and serveral different spec files.  It is 
organized around loading type specs or prototype rmaps from the "specs" subdirectory of 
an observatory/subsystem package.   For HST this reduces defining new types to adding 
a prototype rmap and defining .tpn files in the observatory package.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import os.path
import collections
import glob

from crds import rmap, log, utils, data_file
from crds import python23
# from crds.certify import TpnInfo

# =============================================================================
#  Global table loads used at operational runtime:

def _invert_instr_dict(dct):
    """Invert a set of nested dictionaries of the form {instr: {key: val}}
    to create a dict of the form {instr: {val: key}}.
    """
    inverted = {}
    for instr in dct:
        inverted[instr] = utils.invert_dict(dct[instr])
    return inverted

# =============================================================================

def write_spec(specpath, spec_dict):
    """Pretty print a spec dictionary."""
    with open(specpath, "w+") as spec:
        spec.write("{\n")
        for key, value in sorted(spec_dict.items()):
            spec.write("    {} : {},\n".format(repr(key), repr(value)))
        spec.write("}\n")

# =============================================================================

class TypeSpec(dict):
    """This class captures type definition parameters for a single type"""

    def __init__(self, header):
        """Initialize this TypeSpec from dict `header`,  enforcing requirments and creating suitable 
        defaults for missing fields.
        """
        header = utils.Struct(header)
        assert "suffix" in header
        assert "text_descr" in header or header.filetype == "all"
        if "tpn" not in header:
            header.tpn = header.instrument.lower() + "_" + header.suffix + ".tpn"
        if "ld_tpn" not in header:
            header.ld_tpn = header.instrument.lower() + "_" + header.suffix + "_ld.tpn"
        if "file_ext" not in header:
            header.file_ext = ".fits"
        if "unique_rowkeys" not in header:
            header.unique_rowkeys = None
        if "extra_keys" not in header:
            header.extra_keys = None
        super(TypeSpec, self).__init__(header.items())

    @classmethod
    def from_file(cls, filename):
        """For historical HST types,  build type info from a spec file derived from CDBS specs like
        reference_file_defs.xml or cdbscatalog.dat.  For new CRDS-only types,  use a prototype rmap
        with an enhanced header to define the type.   Prototypes should be submissible but should not
        contain references.
        """
        log.verbose("Loading type spec", repr(filename), verbosity=75)
        if filename.endswith(".spec"):
            return cls(utils.evalfile(filename))
        else:
            return cls(rmap.load_mapping(filename).header)

# =============================================================================

def from_package_file(pkg):
    """Given the __file__ from a package,  load specs from the package's specs subdirectory."""
    here = (os.path.dirname(pkg) or ".")
    specs_path = os.path.join(here, "specs") 
    unified_defs = load_specs(specs_path)
    return TypeParameters(unified_defs)

def load_specs(spec_path):
    """Return a dictionary of TypeSpecs loaded from directory `spec_path` of form:
    
    { instrument : { filetype : TypeSpec, ...}, ... }
    """
    with log.error_on_exception("Failed loading type specs."):
        specs = collections.defaultdict(dict)
        for spec in glob.glob(os.path.join(spec_path, "*.spec")) + glob.glob(os.path.join(spec_path, "*.rmap")):
            instr, reftype = os.path.splitext(os.path.basename(spec))[0].split("_")
            with log.error_on_exception("Failed loading", repr(spec)):
                specs[instr][reftype] = TypeSpec.from_file(spec)
        return specs
    return {}

class TypeParameters(object):
    """Inialized from a dictionary of TypeSpec's from load_specs(), compute observatory enumerations
    and type field inter-relationships and cache them as attributes.
    """
    def __init__(self, unified_defs):

        self.unified_defs = unified_defs

        sorted_udef_items = sorted(unified_defs.items())

        with log.error_on_exception("Can't determine instruments from specs."):
            self.instruments = [instr.lower() for instr in sorted(self.unified_defs.keys())]

        with log.error_on_exception("Can't determine types from specs."):
            self.filekinds = sorted(
                set(reftype.lower() for instr, reftypes in sorted_udef_items
                    for reftype in reftypes))

        with log.error_on_exception("Can't determine extensions from specs."):
            self.extensions = sorted(
                set(params.get("file_ext", ".fits") for instr, reftypes in sorted_udef_items
                    for reftype, params in reftypes.items())) + [".pmap", ".imap", ".rmap"]

        with log.error_on_exception("Can't determine type text descriptions from specs."):
            self.text_descr = {
                reftype.lower() : params["text_descr"] 
                for instr, reftypes in sorted_udef_items
                for reftype, params in reftypes.items()
                }

        with log.error_on_exception("Failed determining filekind_to_suffix"):
            self._filekind_to_suffix = {
                instr : {
                    filekind.lower() : self.unified_defs[instr][filekind]["suffix"].lower()
                    for filekind in self.unified_defs[instr]
                    }
                for instr in self.unified_defs
                }
            
        with log.error_on_exception("Failed determining suffix_to_filekind"):
            self._suffix_to_filekind = _invert_instr_dict(self._filekind_to_suffix)

        with log.error_on_exception("Failed determining filetype_to_suffix"):
            self._filetype_to_suffix = {
                instr : {
                    self.unified_defs[instr][filekind]["filetype"].lower() : self.unified_defs[instr][filekind]["suffix"].lower()
                    for filekind in self.unified_defs[instr]
                    }
                for instr in self.unified_defs
                }

        with log.error_on_exception("Failed determining suffix_to_filetype"):
            self.suffix_to_filetype = _invert_instr_dict(self._filetype_to_suffix)

        with log.error_on_exception("Failed determining unique_rowkeys"):
            self.row_keys = {
                instr : {
                    filekind.lower() : self.unified_defs[instr][filekind]["unique_rowkeys"]
                    for filekind in self.unified_defs[instr]
                    }
                for instr in self.unified_defs
                }

    def filetype_to_filekind(self, instrument, filetype):
        """Map the value of a FILETYPE keyword onto it's associated
        keyword name,  i.e.  'dark image' --> 'darkfile'
        """
        instrument = instrument.lower()
        filetype = filetype.lower()
        if instrument == "nic":
            instrument = "nicmos"
        suffix = self._filetype_to_suffix[instrument][filetype]
        return self._suffix_to_filekind[instrument][suffix]

    def suffix_to_filekind(self, instrument, suffix):
        """Map the value of an instrument and TPN suffix onto it's
        associated filekind keyword name,  i.e. drk --> darkfile
        """
        if instrument == "nic":
            instrument = "nicmos"
        return self._suffix_to_filekind[instrument][suffix]

    def filekind_to_suffix(self, instrument, filekind):
        """Given and instrument (e.g. acs) and filekind (e.g. darkfile)
        turn the associated file suffix (e.g. drk) for use in generating
        legacy filenames.
        """
        if instrument == "nic":
            instrument = "nicmos"
        return self._filekind_to_suffix[instrument][filekind]

# =============================================================================

    def mapping_validator_key(self, mapping):
        """Return (_ld.tpn name, ) corresponding to CRDS ReferenceMapping `mapping` object."""
        mapping = rmap.asmapping(mapping)
        return (self.unified_defs[mapping.instrument][mapping.filekind]["ld_tpn"], mapping.filename)
        # return reference_name_to_validator_key(mapping.filepath, field="ld_tpn")   # now has multiple values

    @utils.cached
    def reference_name_to_validator_key(self, filename, field="tpn"):
        """Return the sequence of validator keys associated with `filename`.   A validator key
        is nominally a .tpn filename and can vary by observatory, instrument, and type as well
        as by functions on the header of `filename`.
        """
        header = data_file.get_free_header(filename)
        observatory = utils.header_to_observatory(header)
        instrument, filekind = utils.get_file_properties(observatory, filename)
        results = []
        def append_tpn_level(results, instrument, filekind):
            """Append the validator key for associated with one level of the `instrument`
            and `filekind` to `results`.
            """
            try:
                validator_key = self._reference_name_to_validator_key(filename, field, header, observatory, instrument, filekind)
                log.verbose("Adding validator key", repr(validator_key))
                results.append(validator_key)
            except Exception as exc:
                log.verbose_warning("Can't find TPN key for", (filename, instrument, filekind), ":", str(exc), verbosity=75)
        append_tpn_level(results, "all", "all")
        append_tpn_level(results, instrument, "all")
        append_tpn_level(results, "all", filekind)
        append_tpn_level(results, instrument, filekind)
        return results

    def _reference_name_to_validator_key(self, filename, field, header, observatory, instrument, filekind):
        """Given a reference filename `fitsname`,  return a dictionary key
        suitable for caching the reference type's Validator.
        
        This revised version supports computing "subtype" .tpn files based
        on the parameters of the reference.   Most references have unconditional
        associations based on (instrument, filekind).   A select few have
        conditional lookups which select between several .tpn's for the same
        instrument and filetype.
        
        Returns (.tpn filename,)
        """
        try:
            tpnfile = self.unified_defs[instrument][filekind][field]
            if isinstance(tpnfile, python23.string_types):
                key = (tpnfile, filename)  # tpn filename
            else: # it's a list of conditional tpns
                for (condition, tpn) in tpnfile:
                    if eval(condition, header):
                        key = (tpn, filename)  # tpn filename
                        break
                else:
                    assert False
        except (AssertionError, KeyError):
            raise ValueError("No TPN match for reference='{}' instrument='{}' reftype='{}'".format(
                    os.path.basename(filename), instrument, filekind))
        log.verbose("Validator key for", field, "for", repr(filename), instrument, filekind, "=", key, verbosity=60)
        return key

    reference_name_to_tpn_key = reference_name_to_validator_key

    def reference_name_to_ld_tpn_key(self, filename):
        """Return the _ld.tpn file key associated with reference `filename`.
        Strictly speaking this should be driven by mapping_validator_key...  but the interface
        for that is wrong so slave it to reference_name_to_tpn_key instead,  historically
        one-for-one.
        """
        return self.reference_name_to_validator_key(filename, field="ld_tpn")

# =============================================================================

    def get_row_keys(self, instrument, filekind):
        """Return the row_keys which define unique table rows corresponding to mapping.
        
        These are used for "mode" checks to issue warnings when unique rows are deleted
        in a certify comparison check against the preceding version of a table.
        
        row_keys are now also utlized to perform "affected datasets" table row
        lookups which essentially requires emulating that aspect of the calibration
        software.  Consequently, row_keys now have a requirement for a higher level
        of fidelity since they were originally defined for mode checks, since the
        consequences of inadequate row keys becomes failed "affects checks" and not
        merely an extraneous warning.  In their capacity as affected datasets
        parameters,  row_keys must be supported by the interface which connects the
        CRDS server to the appropriate system dataset parameter database,  DADSOPS
        for HST.   That interface must be updated when row_keys.dat is changed.
        
        The certify mode checks have a shaky foundation since the concept of mode
        doesn't apply to all tables and sometimes "data" parameters are required to
        render rows unique.   The checks only issue warnings however so they can be
        ignored by file submitters.
        
        For HST calibration references mapping is an rmap.
        """
        try:
            return self.row_keys[instrument][filekind]
        except KeyError:
            log.verbose("No unique row keys defined for", repr((instrument, filekind)))
            return []
        
    def get_row_keys_by_instrument(self, instrument):
        """To support defining the CRDS server interface to DADSOPS, return the
        sorted list of row keys necessary to perform all the table lookups
        of an instrument.   These (FITS) keywords will be used to instrospect
        DADSOPS and identify table fields which provide the necessary parameters.
        """
        keyset = set()
        instrument = instrument.lower()
        for filekind in self.row_keys[instrument]:
            keyset |= set(self.row_keys[instrument][filekind] or [])
        return sorted([key.lower() for key in keyset])

# =============================================================================

    def get_filekinds(self, instrument):
        """Return the sequence of filekind strings for `instrument`."""
        instrument = instrument.lower()
        return sorted(self._filekind_to_suffix[instrument].keys())

    def get_item(self, instrument, filekind, name):
        """Return config item `name` for `instrument` and `filekind`"""
        instrument = instrument.lower()
        filekind = filekind.lower()
        return self.unified_defs[instrument][filekind][name]

