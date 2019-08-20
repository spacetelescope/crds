"""This module defines functions for modifying rmaps in various ways,  generally
the transformations required to automate rmap maintenance on the CRDS website.
"""
import sys
import os.path

# ============================================================================

from crds.core import exceptions, rmap, log, cmdline
from crds.core.log import srepr
from crds import diff

# ============================================================================

class NoUseAfterError(ValueError):
    "The specified UseAfter datetime didn't exist in the rmap."

class NoMatchTupleError(ValueError):
    "The specified Match tuple didn't exist in the rmap."

# ============================================================================

def set_header_value(old_rmap, new_rmap, key, new_value):
    """Set the value of `key` in `filename` to `new_value` and rewrite the rmap.
    This is potentially lossy since rewriting the rmap may/will lose comments and
    formatting quirks.
    """
    mapping = rmap.load_mapping(old_rmap)
    mapping.header[key] = new_value
    mapping.write(new_rmap)

def del_header_value(old_rmap, new_rmap, key):
    """Set the value of `key` in `filename` to `new_value` and rewrite the rmap.
    This is potentially lossy since rewriting the rmap may/will lose comments and
    formatting quirks.
    """
    mapping = rmap.load_mapping(old_rmap)
    del mapping.header[key]
    mapping.write(new_rmap)

def update_derivation(new_path, old_basename=None):
    """Set the 'derived_from' and 'name' header fields of `new_path`.
    This function works for all Mapping classes:  pmap, imap, and rmap.
    """
    new = rmap.fetch_mapping(new_path)
    if old_basename is None:    # assume new is a copy of old, with old's name in header
        derived_from = new.name
    else:
        derived_from = old_basename
    new.header["derived_from"] = str(derived_from)
    new.header["name"] = str(os.path.basename(new_path))
    new.write(new_path)
    return str(derived_from)

# ============================================================================

def rmap_insert_references(old_rmap, new_rmap, inserted_references):
    """Given the full path of starting rmap `old_rmap`,  modify it by inserting
    or replacing all files in `inserted_references` and write out the result to
    `new_rmap`.    If no actions are performed, don't write out `new_rmap`.

    old_rmap  str     Filepath of source rmap into which `inserted_references` will be inserted
    new_rmap  str     Filepath of updated rmap written out
    inserted_references [ str, ...]    List of reference filepaths to be insterted

    Note that "inserting" a reference file can result in:

    1. adding a new match case,
    2. adding a new USEAFTER case
    3. exactly replacing an existing reference file.

    Other outcomes are also possible for non-standard rmap selector class configurations.

    Additional checking:

    1. Generates an ERROR if any of the inserted reference files have identical
    matching criteria since only one file with those criteria would be added to
    the rmap and the other(s) would be "replaced" by their own insertion set.
    Note: it is valid/common for an inserted reference to replace a reference
    which is already in `old_rmap`.  This ERROR only applies to equalities
    within the inserted_references list.

    2. Generates a WARNING if the matching criteria of any inserted reference
    file is a proper subset of inserted or existing references.  Thes subsets
    will generally lead to the addition of new matching cases.  Since CRDS
    inherited instances of these "subset overlaps" from HST CDBS, this warning
    is only visible with --verbose for HST, they exist.  Since this condition
    is bad both for understanding rmaps and for runtime complexity and
    performance, for JWST the warning is visible without --verbose and will
    also generate a runtime ERROR.  For JWST there is the expectation that an
    offending file submission will either be (a) cancelled and corrected or (b)
    provisionally accepted followed by an immediate manual rmap correction.
    Provisional acceptance gives the option of f keeping the work
    associated with large deliveries where the corrective measure might be to
    manually merge overlapping categories with rmap edits.

    Return None,  `new_rmap` is already the implicit result
    """
    new = old = rmap.fetch_mapping(old_rmap, ignore_checksum=True)
    inserted_cases = {}
    for reference in inserted_references:
        log.info("Inserting", os.path.basename(reference), "into", repr(new.name))
        new = new.insert_reference(reference)
        baseref = os.path.basename(reference)
        with log.warn_on_exception("Failed checking rmap update for", repr(baseref)):
            cases = new.file_matches(baseref)
            for fullcase in cases:
                case = fullcase[1:]
                if case not in inserted_cases:
                    inserted_cases[case] = baseref
                else:
                    log.error("-"*40 + "\nBoth", srepr(baseref),
                              "and", srepr(inserted_cases[case]),
                              "identically match case:\n", log.PP(case), """
Each reference would replace the other in the rmap.
Either reference file matching parameters need correction
or additional matching parameters should be added to the rmap
to enable CRDS to differentiate between the two files.
See the file submission section of the CRDS server user's guide here:
    https://jwst-crds.stsci.edu/static/users_guide/index.html
for more explanation.""")

    new.header["derived_from"] = old.basename
    log.verbose("Writing", repr(new_rmap))
    new.write(new_rmap)

def rmap_delete_references(old_rmap, new_rmap, deleted_references):
    """Given the full path of starting rmap `old_rmap`,  modify it by deleting
    all files in `deleted_references` and write out the result to
    `new_rmap`.    If no actions are performed, don't write out `new_rmap`.

    Return new ReferenceMapping named `new_rmap`
    """
    new = old = rmap.fetch_mapping(old_rmap, ignore_checksum=True)
    for reference in deleted_references:
        log.info("Deleting", repr(reference), "from", repr(new.name))
        new = new.delete(reference)
    new.header["derived_from"] = old.basename
    log.verbose("Writing", repr(new_rmap))
    new.write(new_rmap)
    formatted = new.format()
    for reference in deleted_references:
        reference = os.path.basename(reference)
        assert reference not in formatted, \
            "Rules update failure.  Deleted" + repr(reference) + " still appears in new rmap."
    return new

def rmap_check_modifications(old_rmap, new_rmap, old_ref, new_ref, expected=("add",)):
    """Check the differences between `old_rmap` and `new_rmap` and make sure they're
    limited to the types listed in `expected`.

    expected should be "add" or "replace".

    Returns as_expected,  True IFF all rmap modifications match `expected`.
    """
    diffs = diff.mapping_diffs(old_rmap, new_rmap)
    as_expected = True
    for difference in diffs:
        actual = diff.diff_action(difference)
        if actual in expected:
            pass   # white-list so it will fail when expected is bogus.
        else:
            log.error("Expected one of", repr(expected), "but got", repr(actual),
                      "from change", repr(difference))
            as_expected = False
    with open(old_rmap) as pfile:
        old_count = len([line for line in pfile.readlines() if os.path.basename(old_ref) in line])
    with open(new_rmap) as pfile:
        new_count = len([line for line in pfile.readlines() if os.path.basename(new_ref) in line])
    if "replace" in expected and old_count != new_count:
        log.error("Replacement COUNT DIFFERENCE replacing", repr(old_ref), "with", repr(new_ref), "in", repr(old_rmap),
                  old_count, "vs.", new_count)
        as_expected = False
    return as_expected

# ============================================================================

class RefactorScript(cmdline.Script):
    """Command line script for modifying .rmap files."""

    description = """
    Modifies a reference mapping by adding the specified reference files.
    """

    epilog = """
    """

    locate_file = cmdline.Script.locate_file_outside_cache

    def add_args(self):
        self.add_argument("command", choices=("insert", "delete", "set_header", "del_header"),
            help="Name of refactoring command to perform.")
        self.add_argument('old_rmap', type=cmdline.reference_mapping,
            help="Reference mapping to modify by inserting references.")
        self.add_argument('new_rmap', type=cmdline.reference_mapping,
            help="Name of modified reference mapping output file.")
        self.add_argument('references', type=str, nargs="+",
            help="Reference files to insert into (or delete from) `old_rmap` to produce `new_rmap`.")

    @property
    def old_rmap(self):
        return self.locate_file(self.args.old_rmap)

    @property
    def new_rmap(self):
        return self.locate_file(self.args.new_rmap)

    @property
    def ref_paths(self):
        self.args.files = self.args.references
        return self.files  # standard file location and @-handling for self.args.files

    def main(self):
        with log.error_on_exception("Refactoring operation FAILED"):
            if self.args.command == "insert":
                rmap_insert_references(self.old_rmap, self.new_rmap, self.ref_paths)
            elif self.args.command == "delete":
                rmap_delete_references(self.old_rmap, self.new_rmap, self.ref_paths)
            elif self.args.command == "set_header":
                field, setting = self.args.references[0], " ".join(self.args.references[1:])
                set_header_value(self.old_rmap, self.new_rmap, field, setting)
            elif self.args.command == "del_header":
                field = self.args.references[0]
                del_header_value(self.old_rmap, self.new_rmap, field)
            else:
                raise ValueError("Unknown refactoring command: " + repr(self.args.command))
        log.standard_status()
        return log.errors()

if __name__ == "__main__":
    sys.exit(RefactorScript()())
