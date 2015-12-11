"""This module defines functions for modifying rmaps in various ways,  generally
the transformations required to automate rmap maintenance on the CRDS website.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import os.path
import sys

from crds import (rmap, log, diff, cmdline)
from crds import exceptions as crexc

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
    log.verbose("Setting header value in", repr(new_rmap), "for", repr(key), "=", repr(new_value))
    mapping = rmap.load_mapping(old_rmap)
    mapping.header[key] = new_value
    mapping.write(new_rmap)
    
def del_header_value(old_rmap, new_rmap, key):
    """Set the value of `key` in `filename` to `new_value` and rewrite the rmap.
    This is potentially lossy since rewriting the rmap may/will lose comments and 
    formatting quirks.
    """
    log.verbose("Deleting header value in", repr(new_rmap), "for", repr(key))
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
    
    Return new ReferenceMapping named `new_rmap`
    """
    new = old = rmap.fetch_mapping(old_rmap, ignore_checksum=True)
    for reference in inserted_references:
        log.info("Inserting", os.path.basename(reference), "into", repr(new.name))
        new = new.insert_reference(reference)
    new.header["derived_from"] = old.basename
    log.verbose("Writing", repr(new_rmap))
    new.write(new_rmap)
    formatted = new.format()
    for reference in inserted_references:
        reference = os.path.basename(reference)
        assert reference in formatted, \
            "Rules update failure. " + repr(reference) + " does not appear in new rmap." \
            "  May be identical match with other submitted references."
    return new

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

def del_rmap_parameter(context, instruments, types, parameter_name, modify_inplace=False):
    """Delete `parameter_name` from the parkey item of the `types` of the specified
    `instruments` in `context`.
    """
    pmap = rmap.get_cached_mapping(context)
    for instr in instruments:
        with log.error_on_exception("Failed loading imap for", repr(instr), "from", repr(context)):
            imap = pmap.get_imap(instr)
            for filekind in types:
                with log.error_on_exception("Failed loading rmap for", repr(filekind), "from", 
                                            repr(imap.basename), "of", repr(context)):
                    r = imap.get_rmap(filekind).copy()
                    log.info("Deleting parameter", repr(parameter_name), "from",repr(r.basename))
                    parkey = r.parkey
                    i, j = get_parameter_index(parkey, parameter_name)
                    
                    del_parkey = parkey[:i] +  ((parkey[i][:j] + parkey[i][j+1:]),)  + parkey[i+1:]
                    log.verbose("Replacing", repr(parkey), "with", repr(del_parkey), "in", repr(r.basename))
                    new_filename  = r.filename if modify_inplace else os.path.join(".", r.basename)
                    r.header["parkey"] = del_parkey
                    # set_header_value(r.filename, new_filename, "parkey", del_parkey)
                    r.selector.delete_match_param(parameter_name)
                    r.write(new_filename)
                
def get_parameter_index(parkey, parameter_name):
    """Return the 2D parkey index for `parameter_name`:  (which_sub_tuple,  index_in_subtuple)."""
    for i, pars in enumerate(parkey):
        for j, par in enumerate(pars):
            if par.lower() == parameter_name.lower():
                return i, j
    raise crexc.CrdsError("Can't find index for", repr(parameter_name), "in parkey", repr(parkey))
    
# ============================================================================

class RefactorScript(cmdline.Script):
    """Command line script for modifying .rmap files."""

    description = """
    Modifies a reference mapping by adding the specified reference files.
    """
    
    epilog = """    
    """
    
    def add_args(self):
        self.add_argument("command", choices=("insert_reference", "delete_reference", "set_header", "del_header", "delete_parameter"),
            help="Name of refactoring command to perform.")
        self.add_argument('--old-rmap', type=cmdline.reference_mapping, default=None,
            help="Reference mapping to modify by inserting references.")
        self.add_argument('--new-rmap', type=cmdline.reference_mapping, default=None,
            help="Name of modified reference mapping output file.")
        self.add_argument('--references', type=str, nargs="*",
            help="Reference files to insert into (or delete from) `old_rmap` to produce `new_rmap`.")
        self.add_argument('--source-context', type=str, default=None,
            help="Source context from which to retrieve affected mappings.")
        self.add_argument('--instruments', type=str, nargs="*",
            help="Instruments to which to apply this operation.")
        self.add_argument('--types', type=str, nargs="*",
            help="Reference types to which to apply this operation.")
        self.add_argument('--parameter-name', type=str, default=None,
            help="Name of matching parameter to operate on.")
        self.add_argument('--inplace', action="store_true",
            help="Rewrite files directly in cache replacing original copies.")

    def main(self):
        with log.error_on_exception("Refactoring operation FAILED"):
            if self.args.command == "insert_reference":
                rmap_insert_references(self.args.old_rmap, self.args.new_rmap, self.args.references)
            elif self.args.command == "delete_reference":
                rmap_delete_references(self.args.old_rmap, self.args.new_rmap, self.args.references)
            elif self.args.command == "set_header":
                set_header_value(self.args.old_rmap, self.args.new_rmap, self.args.references[0], 
                                 " ".join(self.args.references[1:]))
            elif self.args.command == "del_header":
                del_header_value(self.args.old_rmap, self.args.new_rmap, self.args.references[0])
            elif self.args.command == "delete_parameter":
                source_context = self.resolve_context(self.args.source_context)
                del_rmap_parameter(source_context, self.args.instruments, self.args.types, self.args.parameter_name, self.args.inplace)
            else:
                raise ValueError("Unknown refactoring command: " + repr(self.args.command))
        return log.errors()

if __name__ == "__main__":
    sys.exit(RefactorScript()())

