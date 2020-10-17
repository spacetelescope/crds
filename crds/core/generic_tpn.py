"""This module manages the formal specification of reference file constraints
as a generic system.

The name TPN is a legacy term from the predecessor of CRDS, HST's CDBS.  It's
the file extension for files used to describe the constraints for a specific
instrument and type.

TPN files are unique to each project/telescope and are defined in the
observatory package in the "tpns" subdirectory.    Each TPN file defines
a number of constraints for references.   Each individual constraint is
represented in CRDS by a named tuple called a TpnInfo.  Each TpnInfo later
becomes the core specification of a Validator object that verifies one
file constraint.  The CRDS certifier applies a list of Validator objects
to reference files as the central mechanism for constraint checking.

Most HST .tpn files were inherited unchanged from CDBS.  HST .tpn files come
in two forms:

<instrument> _ <type_suffix> .tpn     (constrain reference files)
<instrument> _ <type_suffix> _ld.tpn  (constrain database, now rmaps)

In rare cases,  HST specializes .tpn files based on header keywords other
than instrument and type found in the reference file.  In general,  for
HST each instrument+type pair is defined.

JWST extensions reduce duplication in the specifications by extending the
generic .tpn framework to support these additional forms:

all _ all .tpn            (contraints for all instruments and types)
<instrument> _ all .tpn   (constraints for all types of one instrument)
all _ <type_suffix> .tpn  (constraints for all instruments for one type)

For JWST generally .tpn and _ld.tpn's are identical.  For JWST, most checks are
done using the extended forms.  As a matter of specification, all the .tpn
files are enforced equally; however, typically the more specialized forms of
specification (specific instrument, type, or both) define tighter constraints,
so there is an assumed process of narrowing.  e.g. Keywords defined as
"optional" at more generic levels may become required, and values only defined
broadly may be narrowed to those applicable to a specific instrument or type,
etc.

In addition, JWST processes the calibration code data model schema and converts
schema entries into optional TpnInfo objects; this enables CRDS to expose the
checks being applied by the data model and apply them directly in CRDS as well.
"""
import os.path
import collections
import re

# ============================================================================

from crds.core import log, utils, exceptions
#     from crds.core import rmap, heavy_client    # deferred

# ============================================================================

#
# Only the first character of the field is stored, i.e. Header == H
#
# name = field identifier
# keytype = (Header|Group|Column)
# datatype = (Integer|Real|Logical|Double|Character)
# presence = (Optional|Required)
# values = [...]
#
_TpnInfo = collections.namedtuple("TpnInfo", "name,keytype,datatype,presence,values")

class TpnInfo(_TpnInfo):
    """Named tuple describing a file checking constraint with enhanced repr()."""

    def __repr__(self):
        return ("(" + repr(self.name) + ", "
                + self._repr_keytype() + ", "
                + self._repr_datatype() + ", "
                + self._repr_presence() + ", "
                + self._repr_values() + ")")

    keytypes = {
        "H" : "HEADER",
        "C" : "COLUMN",
        "G" : "GROUP",
        "A" : "ARRAY_FORMAT",
        "D" : "ARRAY_DATA",
        "X" : "EXPRESSION",
    }

    def _repr_keytype(self):
        return repr(self.keytypes.get(self.keytype[0], self.keytype[0]))

    datatypes = {
        "C" : "CHARACTER",
        "I" : "INTEGER",
        "L" : "LOGICAL",
        "R" : "REAL",
        "D" : "DOUBLE",
        "X" : "EXPRESSION",
    }

    def _repr_datatype(self):
        return repr(self.datatypes.get(self.datatype[0], self.datatype[0]))

    presences = {
        "E" : "EXCLUDED",
        "R" : "REQUIRED",
        "P" : "REQUIRED",
        "W" : "WARN",
        "O" : "OPTIONAL",
        "F" : "IF_FULL_FRAME",
        "S" : "IF_SUBARRAY",
        "A" : "ANY_SUBARRAY"
    }

    def _repr_presence(self):
        if is_expression(self.presence):
            return "condition="+repr(self.presence)
        return repr(self.presences.get(self.presence[0], self.presence[0]))

    def _repr_values(self):
        if self.values and is_expression(self.values[0]):
            return "expression=" + repr(self.values[0])
        else:
            return "values=" + repr(self.values)

    @property
    def is_expression(self):
        """Return True IFF this is an expression constraint."""
        return self.datatype[0] == "X"

    @property
    def is_conditionally_applicable(self):
        """Return True IFF this constraint has an expression defining when it is applicable."""
        return is_expression(self.presence)

    @property
    def is_complex_constraint(self):
        """Used to eliminate infos not appropriate as rmap value lists."""
        return self.is_expression or self.is_conditionally_applicable

# =============================================================================

HERE = os.path.dirname(__file__) or "./"

# =============================================================================

def load_tpn(fname):
    """Load a TPN file and return it as a list of TpnInfo objects
    describing keyword requirements including acceptable values.
    """
    tpn = []
    for line in load_tpn_lines(fname):
        line = _fix_quoted_whitespace(line)
        items = line.split()
        items = _restore_embedded_spaces(items)
        items = _remove_quotes(items)
        if len(items) == 4:
            name, keytype, datatype, presence = items
            values = []
        else:
            name, keytype, datatype, presence, values = items
            values = _remove_quotes(values.split(",") if datatype != "X" else [values])
            values = [str(v) if is_expression(v) else str(v.upper()) for v in values]
        tpn.append(TpnInfo(name, keytype, datatype, presence, tuple(values)))
    return tpn

def is_expression(tpn_field):
    """Return True IFF .tpn value `tpn_field` defines a header expression.

    Initially `tpn_field` is either a value from the TpnInfo "values" field or
    it is the value of the "presence" field.  In both cases,  an expression
    is signified by bracketing the value in parens.
    """
    return tpn_field.startswith("(") and tpn_field.endswith(")")

@utils.cached
def load_tpn_lines(fname, replacements=()):
    """Load the lines of a CDBS .tpn file,  ignoring #-comments, blank lines,
     and joining lines ending in \\.  If a line begins with "include",  the
    second word should be a base filename that refers to a file in the same
    directory as `fname`.  The lines of the include file are recursively included.
    """
    log.verbose("Loading .tpn lines from", log.srepr(fname),
                "with replacements", log.srepr(replacements), verbosity=80)
    lines = []
    append = False
    dirname = os.path.dirname(fname)
    with open(fname) as pfile:
        for line in pfile:
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            if line.startswith("include"):   #  include tpn_file
                fname2 = os.path.join(dirname, line.split()[1])
                lines += load_tpn_lines(fname2, replacements)
                continue
            elif line.startswith("replace"): #  replace orig_str  new_str
                orig, replaced = replacement = tuple(line.split()[1:])
                if replacement not in replacements:
                    for replacement2 in replacements:
                        orig2, replaced2 = replacement2
                        if orig == orig2 and replaced != replaced2:
                            raise exceptions.InconsistentTpnReplaceError(
                                "In", repr(fname),
                                "Tpn replacement directive", repr(replacement),
                                "conflicts with directive", repr(replacement2))
                    else:
                        replacements = replacements + (replacement,)
                else:
                    log.verbose("Duplicate replacement", replacement, verbosity=80)
                continue
            for (orig, new) in replacements:
                line = re.sub(orig, new, line)
            if append:
                lines[-1] = lines[-1][:-1].strip() + line
            else:
                lines.append(line)
            append = line.endswith("\\")
    return lines

SPACE_MAGIC = "@@1324$$"

def _fix_quoted_whitespace(line):
    """Replace spaces and tabs which appear inside quotes in `line` with
    magic,  and return it.
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
                line = line[:i-1] + SPACE_MAGIC + line[i:]
    return line

def _restore_embedded_spaces(values):
    """Undo space encoding needed to make simple splits work for TpnInfos."""
    return [value.replace(SPACE_MAGIC, " ") for value in values]

def _remove_quotes(values):
    """Remove any quotes from quoted values."""
    removed = []
    for value in values:
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        removed.append(value)
    return removed

@utils.cached
def get_tpninfos(filepath):
    """Load the list of TPN info tuples from .tpn file at `filepath`.  Unlike
    load_tpn(), this function is structured such that missing files are an
    expected error and relegated to a verbose warning.  This is because for
    JWST the full pantheon of possible .tpn files is never created.
    """
    # XXXX Doesn't use verbose_warning_on_exception because --debug-traps would
    # always trigger since trapped exceptions are expected here,  debugging this
    # is trickier than normal.
    return load_tpn(filepath) if os.path.exists(filepath) else []

def get_tpn_path(tpn, observatory):
    """Return the absolute path to the `tpn` file belonging to `observatory`."""
    locator = utils.get_locator_module(observatory)
    return locator.tpn_path(tpn)

# =============================================================================

def load_all_type_constraints(observatory):
    """Load all the type constraint files from `observatory` package.

    There are constraints that apply to:

    ALL instruments and types
    ALL types of one instrument
    ALL instruments of one type
    One instrument and type

    Generally these should be thought of as designed for successive refinement,
    so all constraints are applied, but as their scope narrows they can become
    stricter.  Since increasing strictness and refinement require more knowledge,
    the development order of the constraints mirrored that.

    However, in the (revised) loading below, constraints are loaded by order of
    decreasing strictness; this makes it possible to define strict
    constants/replacements early in the loading process and to apply those
    to customize the more generalized constraints loaded later.
    """
    from crds.core import rmap, heavy_client
    pmap_name = heavy_client.load_server_info(observatory).operational_context
    pmap = rmap.get_cached_mapping(pmap_name)
    locator = utils.get_locator_module(observatory)
    for instr in pmap.selections:
        imap = pmap.get_imap(instr)
        for filekind in imap.selections:
            if imap.selections[filekind] == "N/A":
                continue
            try:
                suffix  = locator.TYPES.filekind_to_suffix(instr, filekind)
            except Exception as exc:
                log.warning("Missing suffix coverage for", repr((instr, filekind)), ":", exc)
            else:
                locator.get_all_tpninfos(instr, suffix, "tpn")  # With core schema,  one type loads all
                locator.get_all_tpninfos(instr, suffix, "ld_tpn")  # With core schema,  one type loads all
                locator.get_all_tpninfos("all", suffix, "tpn")  # With core schema,  one type loads all
                locator.get_all_tpninfos("all", suffix, "ld_tpn")  # With core schema,  one type loads all
        locator.get_all_tpninfos(instr, "all", "tpn")
        locator.get_all_tpninfos(instr, "all", "ld_tpn")
    locator.get_all_tpninfos("all","all","tpn")
    locator.get_all_tpninfos("all","all","ld_tpn")

# =============================================================================

def main():
    """Place holder function for running this module as cmd line program."""
    print("null tpn processing.")

if __name__ == "__main__":
    main()
