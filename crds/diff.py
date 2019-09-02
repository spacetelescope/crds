"""This module differences two CRDS reference or mapping files on the local
system.   It supports specification of the files using only the basenames or
a full path.   Currently it operates on mapping, FITS, or text files.
"""
import os
import sys
from collections import defaultdict
import tempfile
import json
import pprint
import re

# ============================================================================

# from astropy.io.fits import FITSDiff     # deferred

# ============================================================================

import crds
from crds.core import config, log, pysh, utils, rmap
from crds.core import cmdline, naming
from crds import rowdiff, sync

# ============================================================================

__all__ = [
    "DiffScript",
    "difference",
    "get_affected",
    "get_added_references",
    "get_deleted_references",
    "diff_action",
    "diff_replace_old_new",
    "mapping_check_diffs",
    "mapping_diffs",
]

# ============================================================================

def mapping_diffs(old_file, new_file, *args, **keys):
    """Return the logical differences between CRDS mappings named `old_file`
    and `new_file`.

    IFF include_header_diffs,  include differences in mapping headers.   Some are "boring", e.g. sha1sum or name.

    IFF recurse_added_deleted,  include difference tuples for all nested adds and deletes whenever a higher level
        mapping is added or deleted.   Else, only include the higher level mapping,  not contained files.
    """
    observatory = keys.pop("observatory", None)
    differ = MappingDifferencer(observatory, old_file, new_file, *args, **keys)
    return differ.mapping_diffs()

def get_affected(old_pmap, new_pmap, *args, **keys):
    """Examine the diffs between `old_pmap` and `new_pmap` and return sorted lists of affected instruments and types.

    Returns { affected_instrument : { affected_type, ... } }
    """
    observatory = keys.pop("observatory", crds.get_pickled_mapping(old_pmap).observatory)  # reviewed
    differ = MappingDifferencer(observatory, old_pmap, new_pmap, *args, **keys)
    return differ.get_affected()

# ==============================================================================================================

def difference(observatory, old_file, new_file, *args, **keys):
    """Difference different kinds of CRDS files (mappings, FITS references, etc.)
    named `old_file` and `new_file` against one another and print out the results
    on stdout.

    Returns:

    0 no differences
    1 some differences
    2 errors in subshells

    """
    filetype = config.filetype(old_file)
    differs = {
        "mapping" : MappingDifferencer,
        "asdf" : AsdfDifferencer,
        "fits" : FitsDifferencer,
        "text" : TextDifferencer,
        "yaml" : TextDifferencer,
        "json" : JsonDifferencer,
        }
    differ_class = differs.get(filetype, None)
    if differ_class is None:
        log.warning("Cannot difference file of type", repr(filetype), ":", repr(old_file), repr(new_file))
        status = 2   #  arguably, this should be an error not a warning.  wary of changing now.
    else:
        differ = differ_class(observatory, old_file, new_file, *args, **keys)
        status = differ.difference()
    return status

# ============================================================================

def decolorize(output):
    """Remove ANSI color codes,  particularly for doc-testing."""
    return re.sub(r"\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]", "", output)

# ==============================================================================================================

class Differencer:
    """This baseclass provides a standard set of (largely optional) parameters to subclasses.

    observatory           str  nominally hst or jwst
    old_file              str  name of first/old file in difference
    new_file              str  name of second/new file in difference
    primitive_diffs       bool difference replaced reference files using fitsdiff
    check_diffs           bool check for name reversions, file deletions, rule changes, class changes, and parameter changes
    check_references      bool check for reference additions or deletions, regardless of matching criteria
    mapping_text_diffs    bool print out UNIX text diffs for mapping changes
    include_header_diffs  bool include header changes in logical diff output for mappings
    hide_boring_diffs     bool hide boring header changes in logical diff output (name, sha1sum, derived_from, etc.)
    recurse_added_deleted bool recursively include all files of added or deleted mapping as also added or deleted
    lowest_mapping_only   bool in each logical diff output,  only show the lowest level mapping,  not the full context traversal
    remove_paths          bool remove paths from mapping names in logical diffs
    """

    def __init__(self, observatory, old_file, new_file, primitive_diffs=False, check_diffs=False, mapping_text_diffs=False,
                 include_header_diffs=False, hide_boring_diffs=False, recurse_added_deleted=False,
                 lowest_mapping_only=False, remove_paths=False, squash_tuples=False, check_references=False,
                 cache1=None, cache2=None):
        self.observatory = observatory
        self.old_file = old_file
        self.new_file = new_file
        self.primitive_diffs = primitive_diffs
        self.check_diffs = check_diffs
        self.check_references = check_references
        self.mapping_text_diffs = mapping_text_diffs
        self.include_header_diffs = include_header_diffs
        self.hide_boring_diffs = hide_boring_diffs
        self.recurse_added_deleted = recurse_added_deleted
        self.lowest_mapping_only = lowest_mapping_only
        self.remove_paths = remove_paths
        self.squash_tuples = squash_tuples
        self.cache1 = cache1
        self.cache2 = cache2
        self.mappings_cache1 = os.path.join(self.cache1, "mappings", self.observatory) if cache1 else None
        self.mappings_cache2 = os.path.join(self.cache2, "mappings", self.observatory) if cache2 else None

    def locate_file(self, filename, cache=None):
        """Return the full path for `filename` implementing default CRDS file cache
        location behavior,  and verifying that the resulting path is safe.  If cache
        is defined,  override CRDS_PATH and any path included in `filename`.
        """
        if cache is not None:
            os.environ["CRDS_PATH"] = cache
            filename = os.path.basename(filename)
        path = config.locate_file(filename, self.observatory)
        config.check_path(path)  # check_path returns abspath,  bad for listsings.
        return path

    def locate_file1(self, filename):
        """Locate `filename` inside CRDS cache,  potentially redefining cache as self.cache1."""
        return self.locate_file(filename, self.cache1)

    def locate_file2(self, filename):
        """Locate `filename` inside CRDS cache,  potentially redefining cache as self.cache1."""
        return self.locate_file(filename, self.cache2)

    def difference(self):
        """Run diff() method on `old_file` and `new_file` and print() output.

        Returns the output status and

        Returns:
        0 no differences
        1 some differences
        2 errors

        NOTE:  often overridden
        """
        status, out_err = self.diff()
        print(out_err, end="")
        return status

    def diff(self):
        """Placeholder diff() method for abstract class."""
        raise NotImplementedError("Differencer is an abstract class.")
# ==============================================================================================================

class MappingDifferencer(Differencer):
    """This class recursively differences a mapping hierarchy."""

    def __init__(self, *args, **keys):
        super(MappingDifferencer, self).__init__(*args, **keys)
        assert config.is_mapping(self.old_file), \
            "File " + repr(self.old_file) + " is not a CRDS mapping."
        assert config.is_mapping(self.new_file), \
            "File " + repr(self.new_file) + " is not a CRDS mapping."
        assert os.path.splitext(self.old_file)[-1] == os.path.splitext(self.new_file)[-1], \
            "Files " + repr(self.old_file) + " and " + repr(self.new_file) + \
            " are not the same kind of CRDS mapping:  .pmap, .imap, .rmap"

    def difference(self):
        """Print the logical differences between CRDS mappings named `old_file`
        and `new_file`.

        IFF primitive_differences,  recursively difference any replaced files found
        in the top level logical differences.

        IFF check_diffs, issue warnings about critical differences.   See
        mapping_check_diffs().
        """
        differences = self.mapping_diffs()
        if self.mapping_text_diffs:   # only banner when there's two kinds to differentiate
            log.write("="*20, "logical differences",  repr(self.old_file), "vs.", repr(self.new_file), "="*20)
        if self.hide_boring_diffs:
            differences = remove_boring(differences)
        for diff in sorted(differences):
            diff1 = unquote_diff(diff)
            if self.primitive_diffs:
                log.write("="*80)
            diff2 = simplify_to_lowest_mapping(diff1) if self.lowest_mapping_only else diff1
            diff2 = remove_diff_paths(diff2) if self.remove_paths else diff2
            if not self.squash_tuples:
                log.write(diff2)
            else:
                log.write(self.squash_diff_tuples(diff2))
            if self.primitive_diffs and "header" not in diff_action(diff1):
                # XXXX fragile, coordinate with selector.py and rmap.py
                if "replaced" in diff[-1]:
                    old, new = diff_replace_old_new(diff)
                    if old and new:
                        from crds import diff
                        diff.difference(self.observatory, old, new, primitive_diffs=self.primitive_diffs,
                                        recurse_added_deleted=self.recurse_added_deleted)
        pairs = sorted(set(mapping_pairs(differences) +  [(self.old_file, self.new_file)]))
        for (old, new) in pairs:
            if self.mapping_text_diffs:
                log.write("="*20, "text difference", repr(old), "vs.", repr(new), "="*20)
                text_difference(self.observatory, old, new)
                log.write("="*80)
            if self.check_references:
                mapping_check_references(new, old)

        if self.check_diffs:
            mapping_check_diffs_core(differences)

        return 1 if differences else 0

    def squash_diff_tuples(self, diff2):
        """Change notation of diff tuples into -- separated components for readability."""
        return " -- ".join([" ".join(diff) if isinstance(diff, tuple) else diff for diff in diff2])

    def mapping_diffs(self):
        """Return the logical differences between CRDS mappings named `old_file`
        and `new_file`.

        IFF include_header_diffs,  include differences in mapping headers.   Some are "boring", e.g. sha1sum or name.

        IFF recurse_added_deleted,  include difference tuples for all nested adds and deletes whenever a higher level
        mapping is added or deleted.   Else, only include the higher level mapping,  not contained files.

        """
        # At this time,  the fetch_mapping path parameter appears to exist only to thwart CRDS mapping caching.
        old_map = rmap.fetch_mapping(self.locate_file1(self.old_file), ignore_checksum=True, path=self.mappings_cache1)
        new_map = rmap.fetch_mapping(self.locate_file2(self.new_file), ignore_checksum=True, path=self.mappings_cache2)
        differences = old_map.difference(new_map, include_header_diffs=self.include_header_diffs,
                                         recurse_added_deleted=self.recurse_added_deleted)
        return differences

    def get_affected(self):
        """Examine the diffs between `old_pmap` and `new_pmap` and return sorted lists of affected instruments and types.

        Returns { affected_instrument : { affected_type, ... } }
        """
        instrs = defaultdict(set)
        diffs = self.mapping_diffs()
        diffs = remove_boring(diffs)
        for diff in diffs:
            for step in diff:
                # Walking down the diff steps 1-by-1 eventually hits an rmap comparison which
                # will define both instrument and type.  pmaps and imaps leave at least one blank.
                if len(step) == 2 and config.is_mapping(step[0]):
                    instrument, filekind = utils.get_file_properties(self.observatory, step[0])
                # This is inefficient since diff doesn't vary by step,  but set logic cleans up the redundancy
                # New rmaps imply reprocessing the entire type.
                elif isinstance(diff[-1],str) and diff[-1].startswith(("added","deleted")) and \
                        diff[-1].endswith(".rmap'"):
                    rmap_name = diff[-1].split()[-1].replace("'","")
                    rmapping = rmap.fetch_mapping(rmap_name, ignore_checksum=True)
                    instrument, filekind = rmapping.instrument, rmapping.filekind
                if instrument.strip() and filekind.strip():
                    if filekind not in instrs[instrument]:
                        log.verbose("Affected", (instrument, filekind), "based on diff", diff, verbosity=20)
                        instrs[instrument].add(filekind)
        return { key:list(val) for (key, val) in instrs.items() }

    def header_modified(self):
        """Return true IFF there were changes in an rmap header."""
        return self._find_diff_str("header")

    def files_deleted(self):
        """Return True IFF files were deleted in an rmap."""
        return self._find_diff_str("delete")

    def _find_diff_str(self, diff_str):
        """Return True IFF `diff_str` is in some rmap diff."""
        diffs = self.mapping_diffs()
        diffs = remove_boring(diffs)
        for diff in diffs:
            for step in diff:
                if len(step) == 2 and config.is_mapping(step[0]):
                    if diff_str in diff_action(diff):
                        log.verbose("Found", repr(diff_str), "diff between", repr(step[0:1]))
                        return True
        return False


# ==============================================================================================================

class FitsDifferencer(Differencer):

    """Differences FITS format files including row differences."""

    def __init__(self, *args, **keys):
        super(FitsDifferencer, self).__init__(*args, **keys)
        assert self.old_file.endswith(".fits"), \
            "File " + repr(self.old_file) + " is not a FITS file."
        assert self.new_file.endswith(".fits"), \
            "File " + repr(self.new_file) + " is not a FITS file."

    def difference(self):
        """Run fitsdiff on files named `old_file` and `new_file`.

        Returns:

        0 no differences
        1 some differences
        """
        loc_old_file = self.locate_file1(self.old_file)
        loc_new_file = self.locate_file2(self.new_file)

        # Do the standard diff.
        from astropy.io.fits import FITSDiff           # deferred
        fdiff = FITSDiff(loc_old_file, loc_new_file)

        # Do the diff by rows.
        rdiff = rowdiff.RowDiff(loc_old_file, loc_new_file)

        if not fdiff.identical:
            fdiff.report(fileobj=sys.stdout)
            print('\n', rdiff)

        return 0 if fdiff.identical else 1

# ==============================================================================================================

class TextDifferencer(Differencer):
    """Run UNIX diff on two text files named `old_file` and `new_file`."""

    def __init__(self, *args, **keys):
        """Initialize TextDifferencer validating identical extensions for both files."""
        super(TextDifferencer, self).__init__(*args, **keys)
        assert os.path.splitext(self.old_file)[-1] == os.path.splitext(self.new_file)[-1], \
            "Files " + repr(self.old_file) + " and " + repr(self.new_file) + " are of different types."

    def diff(self):
        """Returns the diff status and combined output from stdout and stderr of the diff command."""
        loc_old_file = self.locate_file1(self.old_file)
        loc_new_file = self.locate_file2(self.new_file)
        status, out_err = pysh.status_out_err("diff -b -c ${loc_old_file} ${loc_new_file}", raise_on_error=False)   # secure
        return status, out_err

# ==============================================================================================================

class AsdfDifferencer(Differencer):
    """Run UNIX diff on two text files named `old_file` and `new_file`."""

    def __init__(self, *args, **keys):
        """Initialize TextDifferencer validating identical extensions for both files."""
        super(AsdfDifferencer, self).__init__(*args, **keys)
        assert os.path.splitext(self.old_file)[-1] == os.path.splitext(self.new_file)[-1], \
            "Files " + repr(self.old_file) + " and " + repr(self.new_file) + " are of different types."

    def diff(self):
        """Returns the diff status and combined output from stdout and stderr of the diff command."""
        loc_old_file = self.locate_file1(self.old_file)
        loc_new_file = self.locate_file2(self.new_file)
        status, out_err = pysh.status_out_err("asdftool diff ${loc_old_file} ${loc_new_file}", raise_on_error=False)   # secure
        if not status and len(out_err) != 0:
            # convert asdftool "no errors" to diff-style "diffs exist"
            status = 1
        if len(out_err) == 0:
            out_err = ""  # otherwise b''
        else:
            # asdftool colorizes diffs using ANSI color escape sequences.
            out_err = decolorize(out_err)
        return status, out_err

# ==============================================================================================================

class JsonDifferencer(TextDifferencer):
    """Run UNIX diff on two text files named `old_file` and `new_file`."""

    def __init__(self, *args, **keys):
        """Initialize JsonDifferencer capturing optional keyword parameter pretty_print=True."""
        super(JsonDifferencer, self).__init__(*args, **keys)
        self.pretty_print = keys.pop("pretty_print", True)
        self.remove_files = []

    def locate_file(self, filename):
        """Create a temporary file based on source filename source name IFF self.pretty_print."""
        if not self.pretty_print:
            return super(JsonDifferencer, self).locate_file(filename)
        else:
            source_path = config.check_path(filename)
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            with open(source_path) as source_file:
                source_json = json.load(source_file)
            source_pp = pprint.pformat(utils.fix_json_strings(source_json))
            temp_file.write(source_pp)
        self.remove_files += [temp_file.name]
        return temp_file.name

    def difference(self):
        """Run UNIX diff on two json files named `old_file` and `new_file`.
        If self.pretty_print is True,  reformat the files as temporaries

        Returns:
        0 no differences
        1 some differences
        2 errors
        """
        result, out_err = super(JsonDifferencer, self).diff()
        out_err = out_err.replace(self.remove_files[0], self.old_file)
        out_err = out_err.replace(self.remove_files[1], self.new_file)
        print(out_err, end="")
        if self.pretty_print:
            for fname in self.remove_files:
                with log.verbose_warning_on_exception("Failed removing", repr(fname)):
                    os.remove(fname)
        return result

# ============================================================================

def simplify_to_lowest_mapping(diff):
    """For diffs which affect nested mappings,  pop-off the path of the higher level mappings
    and show only the name of the leaf mapping.

    >>> simplify_to_lowest_mapping((('jwst_0063.pmap', 'jwst_0074.pmap'), ('jwst_nirspec_0024.imap', 'jwst_nirspec_0027.imap'),
    ...                            ('jwst_nirspec_saturation_0001.rmap', 'jwst_nirspec_saturation_0002.rmap'),
    ...                            "header replaced 'parkey' = (('META.INSTRUMENT.DETECTOR', 'META.INSTRUMENT.FILTER'),) with (('META.INSTRUMENT.DETECTOR',),)"))
    (('jwst_nirspec_saturation_0001.rmap', 'jwst_nirspec_saturation_0002.rmap'), "header replaced 'parkey' = (('META.INSTRUMENT.DETECTOR', 'META.INSTRUMENT.FILTER'),) with (('META.INSTRUMENT.DETECTOR',),)")
    """
    log.verbose("simplify_to_lowest_mapping:", diff)
    lowest_ranked_mapping = None
    for tup in diff:
        if isinstance(tup, tuple) and  len(tup) == 2 and isinstance(tup[0], str) and tup[0].endswith("map"):
            lowest_ranked_mapping = tup[0]
    simplified = []
    for tup in diff:
        if len(tup) == 2 and isinstance(tup[0], str) and tup[0].endswith("map"):
            if tup[0] != lowest_ranked_mapping:
                continue
        simplified.append(tup)
    return tuple(simplified)

def remove_diff_paths(diff):
    """Remove the paths from leading diff file names."""
    simplified = []
    for tup in diff:
        if len(tup) == 2 and isinstance(tup[0], str) and tup[0].endswith("map"):
            tup = tuple([os.path.basename(t) for t in tup])
        simplified.append(tup)
    return tuple(simplified)

def mapping_pairs(differences):
    """Return the sorted list of all mapping tuples found in differences."""
    pairs = set()
    for diff in differences:
        for pair in diff:
            if len(pair) == 2 and config.is_mapping(pair[0]):
                pairs.add(pair)
    return sorted(pairs)

def unquote_diff(diff):
    """Remove repr str quoting in `diff` tuple,  don't change header diffs."""
    return diff[:-1] + (diff[-1].replace("'",""),) if "header" not in diff[-1] else diff

def unquote(name):
    """Remove string quotes from simple `name` repr."""
    return name.replace("'","").replace('"','')

# XXXX fragile,  coordinate with selector.py and rmap.py
def diff_replace_old_new(diff):
    """Return the (old, new) filenames from difference tuple `diff`."""
    match = re.search(r"replaced '(.+)' with '(.+)'", diff[-1])
    if match:
        return match.group(1), match.group(2)
    else:
        return None, None

# XXXX fragile,  coordinate with selector.py and rmap.py
def diff_added_new(diff):
    """Return the (old, new) filenames from difference tuple `diff`."""
    new = diff[-1].split()[-1]
    return unquote(new)

# XXXX fragile,  coordinate with selector.py and rmap.py
def diff_action(diff):
    """Return 'add', 'replace', or 'delete' based on action represented by
    difference tuple `d`.   Append "_rule" if the change is a Selector.
    """
    if "replace" in diff[-1]:
        result = "replace"
    elif "add" in diff[-1]:
        result = "add"
    elif "delete" in diff[-1]:
        result = "delete"
    elif "different classes" in diff[-1]:
        result = "class_difference"
    elif "different parameter" in diff[-1]:
        result = "parkey_difference"
    else:
        raise ValueError("Bad difference action: "  + repr(diff))
    if "rule" in diff[-1]:
        result += "_rule"
    elif "header" in diff[-1]:
        result += "_header"
    return result
# ============================================================================

def mapping_affected_modes(old_file, new_file, include_header_diffs=True):
    """Return a sorted set of flat tuples describing the matching parameters affected by the differences
    between old_file and new_file.
    """
    affected = defaultdict(int)
    differences = mapping_diffs(old_file, new_file, include_header_diffs=include_header_diffs)
    for diff in differences:
        mode = affected_mode(diff)
        if mode is not None:
            affected[mode] += 1
    return [ tup + (("DIFF_COUNT", str(affected[tup])),) for tup in sorted(affected) ]

DEFAULT_EXCLUDED_PARAMETERS = ("DATE-OBS", "TIME-OBS",
                               "META.OBSERVATION.DATE", "META.OBSERVATION.TIME",
                               "META_OBSERVATION_DATE", "META_OBSERVATION_TIME",
                               "DIFFERENCE", "INSTRUME", "REFTYPE")

BORING_VARS = ["NAME", "DERIVED_FROM", "SHA1SUM", "ROW_KEYS"]  # XXX ROW_KEYS obsolete

def affected_mode(diff, excluded_parameters=DEFAULT_EXCLUDED_PARAMETERS):
    """Return a list of parameter items which characterize the effect of a difference in
    terms of instrument, type, and instrument mode.
    """
    instrument = filekind = None
    affected = []
    flat = diff.flat
    for (i, val) in enumerate(flat):
        var = flat.parameter_names[i]
        if var == "PipelineContext":
            pass
        elif var == "InstrumentContext":
            instrument = diff.instrument
        elif var == "ReferenceMapping":
            instrument = diff.instrument
            filekind = diff.filekind
        elif var not in excluded_parameters:
            affected.append((var, val))
        elif var == "DIFFERENCE" and "header" in val:
            for boring in BORING_VARS:
                if "REPLACED " + repr(boring) in val.upper():
                    break
            else:
                affected.append((var, val))
    if not affected:
        return None
    if filekind:
        affected = [("REFTYPE", filekind.upper())] + affected
    if instrument:
        affected = [("INSTRUMENT", instrument.upper())] + affected
    return tuple(affected)

def format_affected_mode(mode):
    """Format an affected mode as a string."""
    return " ".join(["=".join([item[0], repr(item[1])]) for item in mode])

def remove_boring(diffs):
    """Remove routine differences from a list of diff tuples."""
    result = diffs[:]
    for diff in diffs:
        for var in BORING_VARS:
            if var.lower() in diff[-1]:
                result.remove(diff)
    return result

# ============================================================================

def mapping_check_references(mapping, derived_from):
    """Regardless of matching criteria,  do a simple check listing added or deleted
    references as appropritate.
    """
    mapping = rmap.asmapping(mapping, cached="readonly")
    derived_from = rmap.asmapping(derived_from, cached="readonly")
    old_refs = set(derived_from.reference_names())
    new_refs = set(mapping.reference_names())
    if old_refs - new_refs:
        log.warning("Deleted references for", repr(derived_from.filename), "and", repr(mapping.filename), "=",
                 list(old_refs - new_refs))
    if new_refs - old_refs:
        log.warning("Added references for", repr(derived_from.filename), "and", repr(mapping.filename), "=",
                 list(new_refs - old_refs))

def mapping_check_diffs(mapping, derived_from):
    """Issue warnings for *deletions* in self relative to parent derived_from
    mapping.  Issue warnings for *reversions*,  defined as replacements which
    where the replacement is older than the original,  as defined by the names.

    This is intended to check for missing modes and for inadvertent reversions
    to earlier versions of files.   For speed and simplicity,  file time order
    is currently determined by the names themselves,  not file contents, file
    system,  or database info.
    """
    mapping = rmap.asmapping(mapping, cached="readonly")
    derived_from = rmap.asmapping(derived_from, cached="readonly")
    log.info("Checking diffs from", repr(derived_from.basename), "to", repr(mapping.basename))
    diffs = derived_from.difference(mapping)
    mapping_check_diffs_core(diffs)

def mapping_check_diffs_core(diffs):
    """Perform the core difference checks on difference tuples `diffs`."""
    categorized = sorted([ (diff_action(d), d) for d in diffs ])
    for action, msg in categorized:
        if "header" in action:
            log.verbose("In", _diff_tail(msg)[:-1], msg[-1])
        elif action == "add":
            log.verbose("In", _diff_tail(msg)[:-1], msg[-1])
        elif "rule" in action:
            log.warning("Rule change at", _diff_tail(msg)[:-1], msg[-1])
        elif action == "replace":
            old_val, new_val = diff_replace_old_new(msg)
            if old_val and new_val:
                old_val, new_val = [x for x in diff_replace_old_new(msg)]
                if naming.newer(new_val, old_val):
                    log.verbose("In", _diff_tail(msg)[:-1], msg[-1])
                else:
                    log.warning("Reversion at", _diff_tail(msg)[:-1], msg[-1])
            else:
                log.warning("Unusual replacement", _diff_tail(msg)[:-1], msg[-1])
        elif action == "delete":
            log.warning("Deletion at", _diff_tail(msg)[:-1], msg[-1])
        elif action == "parkey_difference":
            log.warning("Different lookup parameters", _diff_tail(msg)[:-1], msg[-1])
        elif action == "class_difference":
            log.warning("Different classes at", _diff_tail(msg)[:-1], msg[-1])
        else:
            raise ValueError("Unexpected difference action:", action)

def _diff_tail(msg):
    """`msg` is an arbitrary length difference "path",  which could
    be coming from any part of the mapping hierarchy and ending in any kind of
    selector tree.   The last item is always the change message: add, replace,
    delete <blah>.  The next to last should always be a selector key of some kind.
    Back up from there to find the first mapping tuple.
    """
    tail = []
    for part in msg[::-1]:
        if isinstance(part, tuple) and len(part) == 2 and isinstance(part[0], str) and part[0].endswith("map"):
            tail.append(part[1])
            break
        else:
            tail.append(part)
    return tuple(reversed(tail))

# ============================================================================


def fits_difference(*args, **keys):
    """Difference two FITS files with parameters specified as Differencer class."""
    differ = FitsDifferencer(*args, **keys)
    return differ.difference()

def text_difference(*args, **keys):
    """Run UNIX diff on two text files named `old_file` and `new_file`.  Parameters
    are specified as Differencer class.

    Returns:
      0 no differences
      1 some differences
      2 errors
    """
    differ = TextDifferencer(*args, **keys)
    return differ.difference()

# ==============================================================================================================

def get_added_references(old_pmap, new_pmap, cached=True):
    """Return the list of references from `new_pmap` which were not in `old_pmap`."""
    old_pmap = rmap.asmapping(old_pmap, cached=cached)
    new_pmap = rmap.asmapping(new_pmap, cached=cached)
    return sorted(list(set(new_pmap.reference_names()) - set(old_pmap.reference_names())))

def get_deleted_references(old_pmap, new_pmap, cached=True):
    """Return the list of references from `new_pmap` which were not in `old_pmap`."""
    old_pmap = rmap.asmapping(old_pmap, cached=cached)
    new_pmap = rmap.asmapping(new_pmap, cached=cached)
    return sorted(list(set(old_pmap.reference_names()) - set(new_pmap.reference_names())))

def get_updated_files(context1, context2):
    """Return the sorted list of files names which are in `context2` (or any intermediate context)
    but not in `context1`.   context2 > context1.
    """
    extension1 = os.path.splitext(context1)[1]
    extension2 = os.path.splitext(context2)[1]
    assert extension1 == extension2, "Only compare mappings of same type/extension."
    old_map = crds.get_cached_mapping(context1)
    old_files = set(old_map.mapping_names() + old_map.reference_names())
    all_mappings = rmap.list_mappings("*"+extension1, old_map.observatory)
    updated = set()
    context1, context2 = os.path.basename(context1), os.path.basename(context2)
    for new in all_mappings:
        new = os.path.basename(new)
        if context1 < new <= context2:
            new_map = crds.get_cached_mapping(new)
            updated |= set(new_map.mapping_names() + new_map.reference_names())
    return sorted(list(updated - old_files))

# ==============================================================================================================

class DiffScript(cmdline.Script):
    """Python command line script to difference mappings or references."""

    description = """Difference CRDS mapping or reference files."""

    epilog = """Reference files are nominally differenced using FITS-diff or diff.

Mapping files are differenced using CRDS machinery to recursively compare too mappings and
their sub-mappings.

Differencing two mappings will find all the logical differences between the two contexts
and any nested mappings.

By specifying --mapping-text-diffs,  UNIX diff will be run on mapping files in addition to
CRDS logical diffs.   (Duplicate/overlapping cases can be collapsed by the default mapping loader
and hence missed in logical differences,  but are revealed by text differences.   crds.certify
can also detect duplicate entries,  but at the cost of mapping load speed.)

By specifying --primitive-diffs,  FITS diff will be run on all references which are replaced
in the logical differences between two mappings.

For example:

    % crds diff hst_0001.pmap  hst_0005.pmap  --brief

Or to include UNIX diff style diffs of rules as well:

    % crds diff hst_0001.pmap  hst_0005.pmap  --brief --mapping-text-diffs

Or for more recursive diffs,  including reference file diffs similar to fitsdiff:

    % crds diff hst_0001.pmap  hst_0005.pmap  --brief --primitive-diffs

NOTE: mapping logical differences (the default) do not compare CRDS mapping headers,  use
--brief or read --help about other switch options.

NOTE: mapping logical differences do not normally include nested files which are implicitly
added or deleted by a hgher level mapping change.  See --recurse-added-deleted to include those.

RETURNS: crds.diff has "non-standard" exit status similar to UNIX diff:
     0 no differences
     1 some differences
     2 errors or warnings

Differencing two sets of rules (withing the same cache) with simplified output:

    % crds diff jwst_0080.pmap jwst_0081.pmap --brief --squash-tuples
    jwst_miri_regions_0004.rmap jwst_miri_regions_0005.rmap -- MIRIFUSHORT 12 SHORT N/A -- added Match rule for jwst_miri_regions_0006.fits
    jwst_miri_0048.imap jwst_miri_0049.imap -- regions -- replaced jwst_miri_regions_0004.rmap with jwst_miri_regions_0005.rmap
    jwst_0080.pmap jwst_0081.pmap -- miri -- replaced jwst_miri_0048.imap with jwst_miri_0049.imap

Differencing two sets of rules (from two different pre-synced caches, e.g. from TEST and OPS)  rules only:

    # First make sure two rules caches are up to date by syncing
    % .... sync cache #1 using crds.sync and server #1
    % .... sync cache #2 using crds.sync and server #2

    % crds diff --cache1=/Users/fred/crds_cache_test --cache2=/Users/fred/crds_cache_ops hst_0382.pmap hst_0422.pmap  -F -Q
    ...

    --cache1 and --cache2 are required as a pair.

    This is a direct approach for recursively differencing a version of rules from the TEST pipeline with rules from the OPS pipeline.
    Not all differencing modes work for this feature,  it's intended only for comparing rules,  doesn't support direct sync'ing, etc.
    A key point is that different rules files in TEST and OPS can have the same name.

    NOTE:  For cache-to-cache differences,  --sync-files is not supported.  Compared caches are assumed to pre-exist.

Mutually Exclusive Modes

    The following switches define diffencing modes which cannot be run together:

    --print-new-files
    --print-all-new-files
    --print-affected-instruments
    --print-affected-types
    --print-affected-modes
    --cache1 (or --cache2)
    (default differencing with none of the above)

    --sync-files and --cache1 / --cache2 are also mutally exclusive

    """
    def __init__(self, *args, **keys):
        super(DiffScript, self).__init__(*args, **keys)
        self.old_file = None
        self.new_file = None

    locate_file = cmdline.Script.locate_file_outside_cache

    def add_args(self):
        """Add diff-specific command line parameters."""
        self.add_argument("old_file",  help="Prior file of difference.""")
        self.add_argument("new_file",  help="New file of difference.""")

        self.add_argument("-P", "--primitive-diffs", dest="primitive_diffs",
            help="Fitsdiff replaced reference files when diffing mappings.",
            action="store_true")

        self.add_argument("-T", "--mapping-text-diffs",  dest="mapping_text_diffs", action="store_true",
            help="In addition to CRDS mapping logical differences,  run UNIX context diff for mappings.")
        self.add_argument("-i", "--include-header-diffs", dest="include_header_diffs", action="store_true",
            help="Include mapping header differences in logical diffs: rmap_relevance, sha1sum, derived_from, etc.")
        self.add_argument("-B", "--hide-boring-diffs", dest="hide_boring_diffs", action="store_true",
            help="Remove boiler-plate header differences in logical diffs: sha1sum, derived_from, etc.")
        self.add_argument("-U", "--recurse-added-deleted",  dest="recurse_added_deleted", action="store_true",
            help="When a mapping is added or deleted, include all nested files as also added or deleted.  Else only top mapping change listed.")

        self.add_argument("-K", "--check-diffs", dest="check_diffs", action="store_true",
            help="Issue warnings about new rules, deletions, or reversions.")
        self.add_argument("--check-references", dest="check_references", action="store_true",
            help="Issue warnings if references are added to or deleted from either mapping.")

        group = self.get_exclusive_arg_group(required=False)
        group.add_argument("-N", "--print-new-files", dest="print_new_files", action="store_true",
            help="Rather than printing diffs for mappings,  print the names of new or replacement files.  Excludes intermediaries.")
        group.add_argument("-A", "--print-all-new-files", dest="print_all_new_files", action="store_true",
            help="Print the names of every new or replacement file in diffs between old and new.  Includes intermediaries.")
        group.add_argument("--print-affected-instruments", dest="print_affected_instruments", action="store_true",
            help="Print out the names of instruments which appear in diffs,  rather than diffs.")
        group.add_argument("--print-affected-types", dest="print_affected_types", action="store_true",
            help="Print out the names of instruments and types which appear in diffs,  rather than diffs.")
        group.add_argument("--print-affected-modes", dest="print_affected_modes", action="store_true",
            help="Print out the names of instruments, types, and matching parameters,  rather than diffs.")
        group.add_argument("--cache1",  dest="cache1", default=None,
            help="CRDS_PATH for the first cache in a cache-to-cache difference.  Mappings only.""")

        # Can't exclude both cache1 and cache2
        # --sync-files exludes --cache1 and --cache2 but not all the others,  --cache1 and --cache2 required together
        group2 = self.get_exclusive_arg_group(required=False)
        group2.add_argument("--cache2",  dest="cache2", default=None,
            help="CRDS_PATH for the second cache in a cache-to-cache difference.  Mappings only.""")
        group2.add_argument("--sync-files", dest="sync_files", action="store_true",
            help="Fetch any missing files needed for the requested difference from the CRDS server.")

        self.add_argument("-L", "--lowest-mapping-only", dest="lowest_mapping_only", action="store_true",
            help="Only include the name of the leaf mapping being diffed,  not all anscestor mappings.")
        self.add_argument("-E", "--remove-paths", dest="remove_paths", action="store_true",
            help="Remove path names from files in output.")
        self.add_argument("-Q", "--squash-tuples", dest="squash_tuples", action="store_true",
            help="Simplify formatting of difference results (remove tuple notations)")
        self.add_argument("-F", "--brief", dest="brief", action="store_true",
            help="Switch alias for --lowest-mapping-only --remove-paths --hide-boring-diffs --include-headers")

    def main(self):
        """Perform the differencing."""
        self.args.files = [ self.args.old_file, self.args.new_file ]   # for defining self.observatory
        self.old_file = self.locate_file(self.args.old_file)
        self.new_file = self.locate_file(self.args.new_file)
        if self.args.brief:
            self.args.lowest_mapping_only = True
            self.args.remove_paths = True
            self.args.hide_boring_diffs = True
            self.args.include_header_diffs = True
        if self.args.sync_files:
            assert not (self.args.cache1 or self.args.cache2), \
                "--sync-files is not compatible with cache-to-cache differences."
            if self.args.print_all_new_files:
                serial_old = naming.newstyle_serial(self.old_file)
                serial_new = naming.newstyle_serial(self.new_file) + 1
                if None not in [serial_old, serial_new]:
                    errs = sync.SyncScript("crds.sync --range {0}:{1}".format(serial_old, serial_new))()
                    assert not errs, "Errors occurred while syncing all rules to CRDS cache."
                else:
                    log.warning("Cannot sync non-standard mapping names,  results may be incomplete.")
            else:
                self.sync_files([self.old_file, self.new_file])
        elif self.args.print_all_new_files:
            log.warning("--print-all-new-files requires a complete set of rules.  suggest --sync-files.")

        # self.args.files = [ self.old_file, self.new_file ]   # for defining self.observatory

        assert (self.args.cache1 and self.args.cache2) or (not self.args.cache1 and not self.args.cache2), \
            "Cache-to-cache comparison requires both --cache1 and --cache2;  otherwise neither for single cache comparison."

        if self.args.print_new_files:
            status = self.print_new_files()
        elif self.args.print_all_new_files:
            status = self.print_all_new_files()
        elif self.args.print_affected_instruments:
            status = self.print_affected_instruments()
        elif self.args.print_affected_types:
            status = self.print_affected_types()
        elif self.args.print_affected_modes:
            status = self.print_affected_modes()
        else:
            status = difference(self.observatory, self.old_file, self.new_file,
                                primitive_diffs=self.args.primitive_diffs,
                                check_diffs=self.args.check_diffs,
                                check_references=self.args.check_references,
                                mapping_text_diffs=self.args.mapping_text_diffs,
                                include_header_diffs=self.args.include_header_diffs,
                                hide_boring_diffs=self.args.hide_boring_diffs,
                                recurse_added_deleted=self.args.recurse_added_deleted,
                                lowest_mapping_only=self.args.lowest_mapping_only,
                                remove_paths=self.args.remove_paths,
                                squash_tuples=self.args.squash_tuples,
                                cache1=self.args.cache1,
                                cache2=self.args.cache2)
        if log.errors() or log.warnings():
            return 2
        else:
            return status

    def print_new_files(self):
        """Print the references or mappings which are in the second (new) context and not
        the firtst (old) context.
        """
        if not config.is_mapping(self.old_file) or not config.is_mapping(self.new_file):
            log.error("--print-new-files really only works for mapping differences.")
            return -1
        old = crds.get_pickled_mapping(self.old_file)   # reviewed
        new = crds.get_pickled_mapping(self.new_file)   # reviewed
        old_mappings = set(old.mapping_names())
        new_mappings = set(new.mapping_names())
        old_references = set(old.reference_names())
        new_references = set(new.reference_names())
        status = 0
        for name in sorted(new_mappings - old_mappings):
            print(name)
            status = 1
        for name in sorted(new_references - old_references):
            print(name)
            status = 1
        return status

    def print_all_new_files(self):
        """Print the names of all files which are in `new_file` (or any intermediary context) but not
        in `old_file`.   new_file > old_file.  Both new_file and old_file are similar mappings.
        """
        updated = get_updated_files(self.old_file, self.new_file)
        for mapping in updated:
            if config.is_mapping(mapping):
                print(mapping, self.instrument_filekind(mapping))
        for reference in updated:
            if not config.is_mapping(reference):
                print(reference, self.instrument_filekind(reference))
        return 1 if updated else 0

    def instrument_filekind(self, filename):
        """Return the instrument and filekind of `filename` as a space separated string."""
        instrument, filekind = utils.get_file_properties(self.observatory, filename)
        return instrument + " " + filekind

    def print_affected_instruments(self):
        """Print the instruments affected in a switch from `old_pmap` to `new_pmap`."""
        instrs = get_affected(self.old_file, self.new_file, include_header_diffs=self.args.include_header_diffs,
                              observatory=self.observatory)
        for instrument in sorted(instrs):
            print(instrument)
        return 1 if instrs else 0

    def print_affected_types(self):
        """Print the (instrument, filekind) pairs affected in a switch from `old_pmap` to `new_pmap`."""
        instrs = get_affected(self.old_file, self.new_file, include_header_diffs=self.args.include_header_diffs,
                              observatory=self.observatory)
        status = 0
        for instrument in sorted(instrs):
            for filekind in sorted(instrs[instrument]):
                if filekind.strip():
                    print("%-10s %-10s" % (instrument, filekind))
                    status = 1
        return status

    def print_affected_modes(self):
        """Print out all the affected mode tuples associated with the differences."""
        assert config.is_mapping(self.old_file) and config.is_mapping(self.new_file), \
            "for --print-affected-modes both files must be mappings."
        modes = mapping_affected_modes(self.old_file, self.new_file, self.args.include_header_diffs)
        for affected in modes:
            print(format_affected_mode(affected))
        return 1 if modes else 0

def test():
    """Run unit tests on this module."""
    import doctest
    from crds import diff
    return doctest.testmod(diff)

if __name__ == "__main__":
    sys.exit(DiffScript()())
