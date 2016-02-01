"""This module defines functions for modifying rmaps in various ways,  generally
the transformations required to automate rmap maintenance on the CRDS website.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import os.path
import sys

from crds import (rmap, log, diff, cmdline, config)
from crds import exceptions as crexc

# ============================================================================
    
class NoUseAfterError(ValueError):
    "The specified UseAfter datetime didn't exist in the rmap."

class NoMatchTupleError(ValueError):
    "The specified Match tuple didn't exist in the rmap."

# ============================================================================
    
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

def set_rmap_header(rmapping, new_filename, header_key, header_value, *args, **keys):
    """Set the value of `key` in `filename` to `new_value` and rewrite the rmap.
    This is potentially lossy since rewriting the rmap may/will lose comments and 
    formatting quirks.
    """
    log.verbose("Setting header value in", repr(rmapping.basename), "for", repr(header_key), 
                "=", repr(header_value))
    rmapping.header[header_key] = header_value
    rmapping.write(new_filename)
    
def del_rmap_header(rmapping, new_filename, header_key):
    """Set the value of `key` in `filename` to `new_value` and rewrite the rmap.
    This is potentially lossy since rewriting the rmap may/will lose comments and 
    formatting quirks.
    """
    log.verbose("Deleting header value in", repr(rmapping.basename), "for", repr(header_key))
    del rmapping.header[header_key]
    rmapping.write(new_filename)

def del_rmap_parameter(rmapping, new_filename, parameter, *args, **keys):
    """Delete `parameter_name` from the parkey item of the `types` of the specified
    `instruments` in `context`.
    """
    log.info("Deleting parameter", repr(parameter), "from",repr(rmapping.basename))
    parkey = rmapping.parkey
    i, j = get_parameter_index(parkey, parameter)
    del_parkey = parkey[:i] +  ((parkey[i][:j] + parkey[i][j+1:]),)  + parkey[i+1:]
    log.verbose("Replacing", repr(parkey), "with", repr(del_parkey), "in", repr(rmapping.basename))
    rmapping.header["parkey"] = del_parkey
    rmapping.selector.delete_match_param(parameter)
    rmapping.write(new_filename)
                
def get_parameter_index(parkey, parameter_name):
    """Return the 2D parkey index for `parameter_name`:  (which_sub_tuple,  index_in_subtuple)."""
    for i, pars in enumerate(parkey):
        for j, par in enumerate(pars):
            if par.lower() == parameter_name.lower():
                return i, j
    raise crexc.CrdsError("Can't find index for", repr(parameter_name), "in parkey", repr(parkey))    
    
# ============================================================================

def set_rmap_parkey(rmapping, new_filename, parkey, *args, **keys):
    """Delete `parameter_name` from the parkey item of the `types` of the specified
    `instruments` in `context`.
    """
    log.info("Setting parkey, removing all references from", rmapping.basename)
    references = [config.locate_file(name, observatory=rmapping.observatory)
                  for name in rmapping.reference_names()]
    rmapping = rmap_delete_references(rmapping.filename, new_filename, references)
    log.info("Setting parkey", repr(parkey), "in",repr(rmapping.basename))
    rmapping.header["parkey"] = eval(parkey)
    rmapping.write(new_filename)
    rmapping = rmap_insert_references(new_filename, new_filename, references)

# ============================================================================

def replace_rmap_text(rmapping, new_filename, old_text, new_text, *args, **keys):
    """Do simple text replacement from `old_text` to `new_text` in `rmapping`.
    """
    log.info("Replacing", repr(old_text), "with", repr(new_text), "in", 
             repr(rmapping.basename), "to", repr(new_filename))
    original_rmap = str(rmapping)
    new_rmap = original_rmap.replace(old_text, new_text)
    new_mapping = rmap.ReferenceMapping.from_string(new_rmap, ignore_checksum=True)
    new_mapping.write(new_filename)

# ============================================================================

class RefactorScript(cmdline.Script):
    """Command line script for modifying .rmap files."""

    description = """
    Modifies a reference mapping as indicated by the specified command.
    """
    
    epilog = """

    The insert_reference and delete_reference commands add references to rmaps
    in a manner similar to that done on the website using Batch Submit References.

    1. Insert reference files A B C D... into rmap X creating rmap Y.

    python -m crds.refactor2 insert_reference --old-rmap X --new-rmap Y  --references A B C D...

    2. Delete references A B C D ... from rmap X creating rmap Y.

    python -m crds.refactor2 delete_reference --old-rmap Y --new-rmap Y  --references A B C D...

    The set_header, del_header, del_parameter, set_parkey, and replace commands operate on
    the set of rmaps found under a source context which correspond to the specified instruments and types.

    3. Set header key K to value V in rmap X creating rmap Y.
    source context C (e.g. jwst-operational) for types A B C... of instruments X Y Z...

    python -m crds.refactor2 set_header --header-key K --header-value V

    4. Delete header key K (e.g. description) in all the rmaps found under
    source context C (e.g. jwst-operational) for types A B C... of instruments X Y Z...

    python -m crds.refactor2 del_header --header-key K \\
           --source-context C --instruments X Y Z ... --types A B C ...

    5. Remove single parameter name N (e.g. META.SUBARRAY.NAME) in all the rmaps found under
    source context C (e.g. jwst-operational) for types A B C... of instruments X Y Z...
    This incudes modifying both parkey and all corresponding selector matching patterns.

    python -m crds.refactor2 del_parameter --parameter-name N \\
           --source-context C --instruments X Y Z ... --types A B C ...

    6. Set complete parkey in all rmaps found under
    source context C (e.g. jwst-operational) for types A B C... of instruments X Y Z...
    This removes all the existing references and re-inserts them under the new parkey approach.

    python -m crds.refactor2 set_parkey --parkey "(('META.INSTRUMENT.DETECTOR','META.SUBARRAY.NAME',))" \\
            --source-context jwst-operational --instruments X Y Z ... --types A B C ...
     
    7. Replace old text P1 with new text P2 in all rmaps found under
    source context C (e.g. jwst-operational) for types A B C... of instruments X Y Z...
    This is a simple text substitution.

    python -m crds.refactor2 replace_text --old-text P1  --new-text P2 \\
            --source-context jwst-operational --instruments X Y Z ... --types A B C ...
    """
    
    def add_args(self):
        self.add_argument("command", choices=("insert_reference", "delete_reference", "set_header", 
                                              "del_header", "del_parameter", "set_parkey", "replace_text"),
                          help="Name of refactoring command to perform.")
        self.add_argument('--old-rmap', type=cmdline.reference_mapping, default=None,
                          help="Reference mapping to modify by inserting references.")
        self.add_argument('--new-rmap', type=cmdline.reference_mapping, default=None,
                          help="Name of modified reference mapping output file.")
        self.add_argument('references', type=str, nargs="*",
                          help="Reference files, to insert into (or delete from) `old_rmap` to produce `new_rmap`.")
        self.add_argument('--source-context', type=str, default=None,
                          help="Source context from which to retrieve affected mappings.")
        self.add_argument('--instruments', type=str, nargs="*", help="Instruments to which to apply this operation.")
        self.add_argument('--types', type=str, nargs="*", help="Reference types to which to apply this operation.")
        self.add_argument('--header-key', type=str, default=None, help="Header keyword for header commands.")
        self.add_argument('--header-value', type=str, default=None, help="Value for header commands.")
        self.add_argument('--parkey', type=str, default=None, help="New parkey value for set_parkey.")
        self.add_argument('--parameter-name', type=str, default=None, help="Name of matching parameter to operate on.")
        self.add_argument('--old-text', type=str, default=None, help="Source text for replace_text command.")
        self.add_argument('--new-text', type=str, default=None, help="Replacement text for replace_text command.")
        self.add_argument('--inplace', action="store_true",
                          help="Rewrite files directly in cache replacing original copies.")

    def main(self):
        with log.error_on_exception("Refactoring operation FAILED"):
            if self.args.command == "insert_reference":
                rmap_insert_references(self.args.old_rmap, self.args.new_rmap, self.args.references)
            elif self.args.command == "delete_reference":
                rmap_delete_references(self.args.old_rmap, self.args.new_rmap, self.args.references)
            elif self.args.command == "del_header":
                self.del_header_key()
            elif self.args.command == "set_header":
                self.set_header_key()
            elif self.args.command == "del_parameter":
                self.del_parameter()
            elif self.args.command == "set_parkey":
                self.set_parkey()
            elif self.args.command == "replace_text":
                self.replace_text()
            else:
                raise ValueError("Unknown refactoring command: " + repr(self.args.command))
        log.standard_status()
        return log.errors()
    
    def rmap_apply(self, func, *args, **keys):
        """Apply `func()` to *args and **keys,  adding the pmap, imap, and rmap values
        associated with the elaboration of args.source_context, args.instruments, args.types.
        """
        keywords = dict(keys)
        source_context = self.resolve_context(self.args.source_context)
        pmapping = rmap.get_cached_mapping(source_context)
        for instr in self.args.instruments:
            with log.error_on_exception("Failed loading imap for", repr(instr), "from", 
                                        repr(source_context)):
                imapping = pmapping.get_imap(instr)
                for filekind in self.args.types:
                    with log.error_on_exception("Failed loading rmap for", repr(filekind), "from", 
                                                repr(imapping.basename), "of", 
                                                repr(source_context)):
                        rmapping = imapping.get_rmap(filekind).copy()
                        new_filename  = rmapping.filename if self.args.inplace else os.path.join(".", rmapping.basename)
                        keywords.update(locals())
                        func(*args, **keywords)

    def del_header_key(self):
        """Set args.header_key to string args.header_value in all rmaps elaborated under
        args.source_context, args.instruments, and args.types.
        """
        self.rmap_apply(del_rmap_header, key=self.args.header_key)
                        
    def set_header_key(self):
        """Set args.header_key to string args.header_value in all rmaps elaborated under
        args.source_context, args.instruments, and args.types.
        """
        self.rmap_apply(set_rmap_header, header_key=self.args.header_key, header_value=self.args.header_value)
                        
    def del_parameter(self):
        """Delete args.parameter_name from the parkey of each rmapping in the rmap
        elaboration of the command line parameters.   Somewhat redundant with set_parkey
        which replaces the entire header item,  but doesn't require viable reference 
        parameters to support reference file re-insertion.
        """
        self.rmap_apply(del_rmap_parameter, parameter=self.args.parameter_name)

    def set_parkey(self):
        """Change the parkey in rmaps elaborated from command line and automatically 
        delete and re-insert each reference to construct appropriate matching tuples.
        """
        self.rmap_apply(set_rmap_parkey, parkey=self.args.parkey)
        
    def replace_text(self):
        """Do simple text substitution in elaborated rmaps replacing `args.old_text` with `args.new_text`."""
        self.rmap_apply(replace_rmap_text, old_text=self.args.old_text,  new_text=self.args.new_text)

if __name__ == "__main__":
    sys.exit(RefactorScript()())

