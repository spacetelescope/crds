"""This module defines functions for modifying rmaps in various ways,  generally
the transformations required to automate rmap maintenance on the CRDS website.
"""
import os.path
import sys

from crds.core import (log, utils, rmap, cmdline, config)
from crds.core import exceptions as crexc
from crds.core.log import srepr
from crds import (diff, sync, certify, matches)
import crds

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
    new.header["derived_from"] = old.basename
    for reference in inserted_references:
        baseref = os.path.basename(reference)
        with log.augment_exception("In reference", srepr(baseref)):
            log.info("Inserting", srepr(baseref), "into", srepr(new.name))
            new = new.insert_reference(reference)
            log.verbose("Writing", srepr(new_rmap))
            new.write(new_rmap)
    formatted = new.format()
    for reference in inserted_references:
        reference = os.path.basename(reference)
        assert reference in formatted, \
            "Rules update failure. " + srepr(reference) + " does not appear in new rmap." \
            "  May be identical match with other submitted references."
    return new

def rmap_insert_references_by_matches(old_rmap, new_rmap, references_headers):
    """Given the full path of starting rmap `old_rmap`,  modify it by inserting
    or replacing all files in dict `references_headers` which maps a reference file basename
    onto a list of headers under which it should be  matched.  Write out the result to
    `new_rmap`.    If no actions are performed, don't write out `new_rmap`.

    Return new ReferenceMapping named `new_rmap`
    """
    new = old = rmap.load_mapping(old_rmap, ignore_checksum=True)
    for baseref, header in references_headers.items():
        with log.augment_exception("In reference", srepr(baseref)):
            log.info("Inserting", srepr(baseref), "into", srepr(old_rmap))
            log.verbose("Inserting", srepr(baseref), "match case", srepr(header), "into", srepr(old_rmap))
            new = new.insert_header_reference(header, baseref)
    new.header["derived_from"] = old.basename
    log.verbose("Writing", srepr(new_rmap))
    new.write(new_rmap)
    formatted = new.format()
    for baseref in references_headers:
        assert baseref in formatted, \
            "Rules update failure. " + srepr(baseref) + " does not appear in new rmap." \
            "  May be identical match with other submitted references."
    return new

# ============================================================================

def rmap_delete_references(old_rmap, new_rmap, deleted_references):
    """Given the full path of starting rmap `old_rmap`,  modify it by deleting
    all files in `deleted_references` and write out the result to
    `new_rmap`.    If no actions are performed, don't write out `new_rmap`.

    Return new ReferenceMapping named `new_rmap`
    """
    new = old = rmap.load_mapping(old_rmap, ignore_checksum=True)
    for reference in deleted_references:
        baseref = os.path.basename(reference)
        log.info("Deleting", srepr(baseref), "from", srepr(new.name))
        with log.augment_exception("In reference", srepr(baseref)):
            new = new.delete(reference)
    new.header["derived_from"] = old.basename
    log.verbose("Writing", srepr(new_rmap))
    new.write(new_rmap)
    formatted = new.format()
    for reference in deleted_references:
        reference = os.path.basename(reference)
        assert reference not in formatted, \
            "Rules update failure.  Deleted " + srepr(reference) + " still appears in new rmap."
    return new

# ============================================================================

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
            log.error("Expected one of", srepr(expected), "but got", srepr(actual),
                      "from change", srepr(difference))
            as_expected = False
    with open(old_rmap) as pfile:
        old_count = len([line for line in pfile.readlines() if os.path.basename(old_ref) in line])
    with open(new_rmap) as pfile:
        new_count = len([line for line in pfile.readlines() if os.path.basename(new_ref) in line])
    if "replace" in expected and old_count != new_count:
        log.error("Replacement COUNT DIFFERENCE replacing", srepr(old_ref), "with",
                  srepr(new_ref), "in", srepr(old_rmap),
                  old_count, "vs.", new_count)
        as_expected = False
    return as_expected

# ============================================================================

def set_rmap_header(rmapping, new_filename, header_key, header_value, *args, **keys):
    """Set the value of `key` in `filename` to `new_value` and rewrite the rmap.
    This is potentially lossy since rewriting the rmap may/will lose comments and
    formatting quirks.
    """
    log.verbose("Setting header value in", srepr(rmapping.basename), "for", srepr(header_key),
                "=", srepr(header_value))
    try:
        rmapping.header[header_key] = eval(header_value)
    except Exception:
        rmapping.header[header_key] = header_value
    rmapping.write(new_filename)

def del_rmap_header(rmapping, new_filename, header_key):
    """Set the value of `key` in `filename` to `new_value` and rewrite the rmap.
    This is potentially lossy since rewriting the rmap may/will lose comments and
    formatting quirks.
    """
    log.verbose("Deleting header value in", srepr(rmapping.basename), "for", srepr(header_key))
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
    log.verbose("Replacing", srepr(parkey), "with", srepr(del_parkey), "in", srepr(rmapping.basename))
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
    """Set the parkey of `rmapping` to `parkey` and write out to `new_filename`.
    """
    log.info("Setting parkey, removing all references from", srepr(rmapping.basename))
    pktuple = eval(parkey)
    required_keywords = tuple(utils.flatten(pktuple))
    refnames = rmapping.reference_names()
    references_headers = { refname : get_refactoring_header(rmapping.filename, refname, required_keywords)
                           for refname in refnames }
    rmapping = rmap_delete_references(rmapping.filename, new_filename, refnames)
    log.info("Setting parkey", srepr(parkey), "in", srepr(rmapping.basename))
    rmapping.header["parkey"] = pktuple
    rmapping.write(new_filename)
    rmapping = rmap.load_mapping(new_filename)
    rmapping = rmap_insert_references_by_matches(new_filename, new_filename, references_headers)
    return rmapping

def get_refactoring_header(rmapping, refname, required_keywords):
    """Create a composite header which is derived from the file contents overidden by any values
    as they appear in the rmap.
    """
    rmapping = rmap.asmapping(rmapping)
    # A fallback source of information is the reference file headers
    header = rmapping.get_refactor_header(
        config.locate_file(refname, rmapping.observatory),
        extra_keys=("META.OBSERVATION.DATE", "META.OBSERVATION.TIME", "DATE-OBS","TIME-OBS") + required_keywords)
    # The primary source of information is the original rmap and the matching values defined there
    headers2 = matches.find_match_paths_as_dict(rmapping.filename, refname)
    # Combine the two,  using the rmap values to override anything duplicated in the reffile header
    assert len(headers2) == 1, "Can't refactor file with more than one match: " + srepr(refname)
    header.update(headers2[0])
    return header

# ============================================================================

def set_rmap_substitution(rmapping, new_filename, parameter_name, old_text, new_text, *args, **keys):
    log.info("Adding substitution for", srepr(parameter_name),
             "from", srepr(old_text), "to", srepr(new_text), "in", srepr(rmapping.basename))
    new_mapping = rmapping.copy()
    if "substitutions" not in new_mapping.header:
        new_mapping.header["substitutions"] = {}
    new_mapping.header["substitutions"][parameter_name] = { old_text : new_text }
    new_mapping.write(new_filename)

# ============================================================================

def cat_rmap(rmapping, new_filename, header_key, *args, **keys):
    """Cat/print rmapping's source text or the value of `header_key` in the rmap header."""
    if header_key is not None:
        log.info("In", srepr(rmapping.basename), "parameter", srepr(header_key), "=", srepr(rmapping.header[header_key]))
    else:
        log.info("-"*80)
        log.info("Rmap", srepr(rmapping.basename), "is:")
        log.info("-"*80)
        log.write(str(rmapping))

# ============================================================================

def add_rmap_useafter(rmapping, new_filename, *args, **keys):
    """Restructure the rmap in Match --> UseAfter form using JWST naming conventions."""
    set_rmap_header(rmapping, new_filename,
                    "classes", repr(rmapping.obs_package.DEFAULT_SELECTORS), *args, **keys)
    parkey = rmapping.obs_package.USEAFTER_KEYWORDS
    if parkey != rmapping.parkey[-1]:
        parkey = rmapping.parkey + (parkey,)
    else:
        parkey = rmapping.parkey
    set_rmap_parkey(rmapping, new_filename, repr(parkey), *args, **keys)
    fix_rmap_undefined_useafter(rmapping, new_filename, *args, **keys)

def fix_rmap_undefined_useafter(rmapping, new_filename, *args, **keys):
    """Change undefined USEAFTER dates to condig.FAKE_USEAFTER_VALUE"""
    rmapping = rmap.ReferenceMapping.from_file(new_filename)
    if "UNDEFINED UNDEFINED" in str(rmapping):
        rmap.replace_rmap_text(rmapping, new_filename, "UNDEFINED UNDEFINED",
                          "1900-01-01 00:00:00", *args, **keys)

# ============================================================================

def insert_rmap_references(rmapping, new_filename, *args, **keys):
    """Insert the appropriate references from the `categorized` references
    dictionary into `rmapping` writing the result to `new_filename`.
    """
    categorized = keys.pop("categorized")
    references = categorized[(rmapping.instrument, rmapping.filekind)]
    rmap_insert_references(rmapping.filename, new_filename, references)

# ============================================================================

def diff_rmap(rmapping, new_filename, *args, **keys):
    """Difference `rmapping` against refactored rmap `new_filename`."""
    script = diff.DiffScript("crds.diff {0} {1} --brief --mapping-text-diffs "
                             "--check-diffs --recurse-added-deleted".format(rmapping.filename, new_filename),
                             reset_log=False, print_status=False)
    script()

def certify_rmap(rmapping, new_filename, source_context=None, *args, **keys):
    """Certify `new_filename` to verify refactored rmap is valid."""
    script = certify.CertifyScript("crds.certify {0} --comparison-context {1}".format(new_filename, rmapping.filename),
                                   reset_log=False, print_status=False)
    script()

# ============================================================================

def apply_rmap_fixers(rmapping, new_filename, fixers, *args, **keys):
    """Apply the text replacements defined in list of colon separated
    old:new `fixers` list to `rmapping` writing results to `new_filename`.
    """
    keys = dict(keys)
    keys.pop("old_text", None)
    keys.pop("new_text", None)
    for fixer in fixers:
        old_text, new_text = fixer.split(":")
        rmap.replace_rmap_text(rmapping, new_filename, old_text, new_text, *args, **keys)
        rmapping = rmap.load_mapping(new_filename)

# ============================================================================

class RefactorScript2(cmdline.Script):
    """Command line script for modifying .rmap files."""

    description = """
    Modifies a reference mapping as indicated by the specified command.
    """

    epilog = """

    The insert_reference and delete_reference commands add references to rmaps
    in a manner similar to that done on the website using Batch Submit References.

    1. Insert reference files A B C D... into rmap X creating rmap Y.

    crds refactor2 insert_reference --old-rmap X --new-rmap Y  --references A B C D...

    2. Delete references A B C D ... from rmap X creating rmap Y.

    crds refactor2 delete_reference --old-rmap Y --new-rmap Y  --references A B C D...

    The set_header, del_header, del_parameter, set_parkey, and replace commands operate on
    the set of rmaps found under a source context which correspond to the specified instruments and types.

    3. Set header key K to value V in rmap X creating rmap Y.
    source context C (e.g. jwst-edit) for types A B C... of instruments X Y Z...

    crds refactor2 set_header --header-key K --header-value V

    4. Delete header key K (e.g. description) in all the rmaps found under
    source context C (e.g. jwst-edit) for types A B C... of instruments X Y Z...

    crds refactor2 del_header --header-key K \\
           --source-context C --instruments X Y Z ... --types A B C ...

    5. Remove single parameter name N (e.g. META.SUBARRAY.NAME) in all the rmaps found under
    source context C (e.g. jwst-edit) for types A B C... of instruments X Y Z...
    This incudes modifying both parkey and all corresponding selector matching patterns.

    crds refactor2 del_parameter --parameter-name N \\
           --source-context C --instruments X Y Z ... --types A B C ...

    6. Set complete parkey in all rmaps found under
    source context C (e.g. jwst-edit) for types A B C... of instruments X Y Z...
    This removes all the existing references and re-inserts them under the new parkey approach.

    crds refactor2 set_parkey --parkey "(('META.INSTRUMENT.DETECTOR','META.SUBARRAY.NAME',))" \\
            --source-context jwst-edit --instruments X Y Z ... --types A B C ... \\
            --fixers FGS1:GUIDER1 FGS2:GUIDER2 ANY:GENERIC FULL:GENERIC

    7. Replace old text P1 with new text P2 in all rmaps found under
    source context C (e.g. jwst-edit) for types A B C... of instruments X Y Z...
    This is a simple text substitution.

    crds refactor2 replace_text --old-text P1  --new-text P2 \\
            --source-context jwst-edit --instruments X Y Z ... --types A B C ...

    8. Add an unconditional load-time parameter value substitution to the rmap header.  For this example,
    the given substitution is added to the rmap "substitutions" header dictionary,  which has the effect
    that match tuples in the rmap are transparently altered at load-time, and SUBARRAY values of GENERIC
    are re-interpreted as N/A for the purposes of matching.

    crds refactor2 set_substitution --parameter-name META.SUBARRAY.NAME  --old-text GENERIC  --new-text N/A \\
            --source-context jwst-edit --instruments X Y Z ... --types A B C ...

    IOW,  this command adds/updates something similar to the following to the specified rmaps:

      'substitutions' : {
          'META.SUBARRAY.NAME' : { 'GENERIC' : 'N/A' },
      }

    9. All of the above commands which elaborate rmaps to refactor based on --source-context can also be
    driven by a direct specification of .rmap names using --rmaps:

    crds refactor2 set_substitution --parameter-name META.SUBARRAY.NAME  --old-text GENERIC  --new-text N/A \\
            --rmaps jwst_miri_dark_0007.rmap

    10. Add the nested UseAfter selector to early JWST rmaps based on Match-only.

    crds refactor2 add_useafter --rmaps jwst_miri_dark_0007.rmap

    11. Mass reference insertion for rehearsing large file deliveries based on --source-context

    It's possible to insert a list of --references into rmaps determined by each reference instrument and type
    and the --source-context.  This mode is active for insert_reference if --old-rmap is not supplied.  If
    the --source-context does not already contain a corresponding rmap for some reference,  CRDS attempts
    to fetch an empty-rmap-spec from the appropriate installed specs directory to use as the baseline rmap.

    This mode allows testing a heterogeneous group of reference types without having to individually specify
    the baseline rmap for each type.  By falling back to the type declaration specs as baseline rmaps, it
    supports reference insertion into rmaps not yet officially added to the --source-context.

    crds refactor2 insert_reference --references ./*.asdf --verbose --certify --diff

    ---------------------------------------------------------------------------------------------------------

    NOTE: In general,  when refactoring,  there are a number of CRDS and JWST calibration code data model
    environment variables which control allowing or passing bad values.   As of now:

    setenv CRDS_ALLOW_BAD_PARKEY_VALUES 1  # leave bad parkey values as-is rather than failing
    setenv CRDS_ALLOW_BAD_USEAFTER      1  # define bad or missing USEAFTER as 1900-01-01T00:00:00
    setenv CRDS_ALLOW_SCHEMA_VIOLATIONS 1  # treat data model schema violations as warnings not errors
    setenv PASS_INVALID_VALUES          1  # ask cal-code data model not to omit invalid values

    See --best-effort for a short cut switch to turn all of the above on from the command line.
    """

    def add_args(self):
        self.add_argument("command", choices=("insert_reference", "delete_reference", "set_header", "set_substitution",
                                              "del_header", "del_parameter", "set_parkey", "replace_text", "cat",
                                              "add_useafter", "diff_rmaps", "certify_rmaps"),
                          help="Name of refactoring command to perform.")
        self.add_argument('--old-rmap', type=cmdline.mapping_spec, default=None,
                          help="Reference mapping to modify by inserting references.")
        self.add_argument('--new-rmap', type=cmdline.mapping_spec, default=None,
                          help="Name of modified reference mapping output file.")
        self.add_argument('--references', type=str, nargs="*",
                          help="Reference files, to insert into (or delete from) `old_rmap` to produce `new_rmap`.")
        self.add_argument('--source-context', type=str, default=None,
                          help="Source context from which to retrieve affected mappings.")
        self.add_argument('--instruments', type=str, nargs="*", help="Instruments to which to apply this operation.")
        self.add_argument('--types', type=str, nargs="*", help="Reference types to which to apply this operation.")
        self.add_argument('--rmaps',  type=str, nargs="*", help="Explicitly specify list of rmaps for refactoring.")
        self.add_argument('--header-key', type=str, default=None, help="Header keyword for header commands.")
        self.add_argument('--header-value', type=str, default=None, help="Value for header commands.")
        self.add_argument('--parkey', type=str, default=None, help="New parkey value for set_parkey.")
        self.add_argument('--parameter-name', type=str, default=None, help="Name of matching parameter to operate on.")
        self.add_argument('--old-text', type=str, default=None, help="Source text for replace_text command.")
        self.add_argument('--new-text', type=str, default=None, help="Replacement text for replace_text command.")
        self.add_argument('--inplace', action="store_true",
                          help="Rewrite files directly in cache replacing original copies.")
        self.add_argument('--fixers', type=str, nargs="*", default=["FGS1:GUIDER1","FGS2:GUIDER2"],
                          help="Simple colon separated global replacements of form old:new ... applied before refactoring.")
        self.add_argument("--sync-files", dest="sync_files", action="store_true",
            help="Fetch any missing files needed for the requested refactoring from the CRDS server.")
        self.add_argument("--diff-rmaps", action="store_true",
                          help="After refactoring, crds.diff the refactored version against the original.")
        self.add_argument("--certify-rmaps", action="store_true",
                          help="After refactoring run crds.certify on refactored rmaps.")
        self.add_argument("--best-effort", action="store_true",
                          help="Shorthand for switching on error bypass env settings.  Generally pass bad values for manual correction later.")

    def main(self):

        if self.args.best_effort:
            config.PASS_INVALID_VALUES.set(True)           # JWST SSB cal code data model
            config.ALLOW_BAD_USEAFTER.set(True)            # Don't fail for bad USEAFTER values
            config.ALLOW_SCHEMA_VIOLATIONS.set(True)       # Don't fail for data model bad value errors
            config.ALLOW_BAD_PARKEY_VALUES.set(True)       # Don't fail for values which don't pass DM + .tpn checking

        if self.args.rmaps:   # clean up dead lines from file lists
            self.args.rmaps = [ self.resolve_context(mapping) for mapping in self.args.rmaps if mapping.strip() ]

        if self.args.references:
            self.args.references = [self.locate_file(reference) for reference in self.args.references]

        with log.error_on_exception("Refactoring operation FAILED"):
            if self.args.command == "insert_reference":
                if self.args.old_rmap:
                    old_rmap, new_rmap = self.resolve_context(self.args.old_rmap), self.resolve_context(self.args.new_rmap)
                    rmap_insert_references(old_rmap, new_rmap, self.args.references)
                else:
                    self.insert_references()  # figure it all out relative to --source-context
            elif self.args.command == "delete_reference":
                old_rmap, new_rmap = self.resolve_context(self.args.old_rmap), self.resolve_context(self.args.new_rmap)
                rmap_delete_references(old_rmap, new_rmap, self.args.references)
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
            elif self.args.command == "set_substitution":
                self.set_substitution()
            elif self.args.command == "cat":
                self.cat()
            elif self.args.command == "add_useafter":
                self.add_useafter()
            elif self.args.command == "diff_rmaps":
                self.diff_rmaps()
            elif self.args.command == "certify_rmaps":
                self.certify_rmaps()
            else:
                raise ValueError("Unknown refactoring command: " + repr(self.args.command))

        log.standard_status()
        return log.errors()

    def rmap_apply(self, func, *args, **keys):
        """Apply `func()` to *args and **keys,  adding the pmap, imap, and rmap values
        associated with the elaboration of args.source_context, args.instruments, args.types.
        """
        keywords = dict(keys)
        self._setup_source_context()
        if self.args.rmaps:
            for rmap_name in self.args.rmaps:
                with log.error_on_exception("Failed processing rmap", srepr(rmap_name)):
                    log.info("="*20, "Refactoring rmap", srepr(rmap_name), "="*20)
                    rmapping = rmap.load_mapping(rmap_name)
                    new_filename = self._process_rmap(func, rmapping=rmapping, **keywords)
                    self._diff_and_certify(rmapping=rmapping, new_filename=new_filename,
                                           source_context=self.source_context, **keywords)
        else:
            pmapping = rmap.load_mapping(self.source_context)
            instruments = pmapping.selections.keys() if "all" in self.args.instruments else self.args.instruments
            for instr in instruments:
                with log.augment_exception("Failed loading imap for", repr(instr), "from",
                                            repr(self.source_context)):
                    imapping = pmapping.get_imap(instr)
                types = imapping.selections.keys() if "all" in self.args.types else self.args.types
                for filekind in types:
                    with log.error_on_exception("Failed processing rmap for", repr(filekind)):
                        #, "from",
                        # repr(imapping.basename), "of", repr(self.source_context)):
                        try:
                            rmapping = imapping.get_rmap(filekind).copy()
                        except crds.exceptions.IrrelevantReferenceTypeError as exc:
                            log.info("Skipping type", srepr(filekind), "as N/A")
                            continue
                        log.info("="*20, "Refactoring rmap", srepr(rmapping.basename), "="*20)
                        new_filename = self._process_rmap(func, rmapping=rmapping, **keywords)
                        self._diff_and_certify(rmapping=rmapping, source_context=self.source_context,
                                               new_filename=new_filename, **keywords)

    def _diff_and_certify(self, *args, **keys):
        """Apply the diff and/or certify scripts if requested on the command line."""
        if self.args.diff_rmaps:
            diff_rmap(*args, **keys)
        if self.args.certify_rmaps:
            certify_rmap(*args, **keys)

    def _process_rmap(self, func, rmapping, *args, **keys):
        """Execute `func` on a single `rmapping` passing along *args and **keys"""
        keywords = dict(keys)
        rmapping_org = rmapping
        new_filename  = rmapping.filename if self.args.inplace else os.path.join(".", rmapping.basename)
        if os.path.exists(new_filename):
            log.info("Continuing refactoring from local copy", srepr(new_filename))
            rmapping = rmap.load_mapping(new_filename)
        keywords.update(locals())
        fixers = self.args.fixers
        if fixers:
            rmapping = rmap.load_mapping(rmapping.filename)
            keywords.update(locals())
            apply_rmap_fixers(*args, **keywords)
        func(*args, **keywords)
        return new_filename

    def _setup_source_context(self):
        """Default the --source-context if necessary and then translate any symbolic name to a literal .pmap
        name.  e.g.  jwst-edit -->  jwst_0109.pmap.   Then optionally sync the files to a local cache.
        """
        if self.args.source_context is None:
            self.source_context = self.observatory + "-edit"
            log.info("Defaulting --source-context to", srepr(self.source_context))
        else:
            self.source_context = self.args.source_context
        self.source_context = self.resolve_context(self.source_context)
        if self.args.sync_files:
            errs = sync.SyncScript("crds.sync --contexts {}".format(self.source_context))()
            assert not errs, "Errors occurred while syncing all rules to CRDS cache."

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
        self.rmap_apply(rmap.replace_rmap_text, old_text=self.args.old_text,  new_text=self.args.new_text)

    def set_substitution(self):
        """Do simple text substitution in elaborated rmaps replacing `args.old_text` with `args.new_text`."""
        self.rmap_apply(set_rmap_substitution, parameter_name=self.args.parameter_name, old_text=self.args.old_text,  new_text=self.args.new_text)

    def cat(self):
        """Either cat the text of the elaborated rmaps if no --parameter-name is specified,  or dump the specified
        --parameter-name from the rmap headers.
        """
        self.rmap_apply(cat_rmap, header_key=self.args.header_key)

    def add_useafter(self):
        """Restructure rmaps to Match -> UseAfter form."""
        self.rmap_apply(add_rmap_useafter)

    def diff_rmaps(self):
        """Apply crds.diff to the refactored rmaps."""
        self.rmap_apply(diff_rmap)

    def certify_rmaps(self):
        """Apply crds.certify to the refactored rmaps."""
        self.rmap_apply(certify_rmap)

    def insert_references(self):
        """Insert files specified by --references into the appropriate rmaps identified by --source-context."""
        self._setup_source_context()
        categorized = self.categorize_files(self.args.references)
        pmap = crds.get_pickled_mapping(self.source_context)  # reviewed
        self.args.rmaps = []
        for (instrument, filekind) in categorized:
            try:
                self.args.rmaps.append(pmap.get_imap(instrument).get_rmap(filekind).filename)
            except crexc.CrdsError:
                log.info("Existing rmap for", (instrument, filekind), "not found.  Trying empty spec.")
                spec_file = os.path.join(
                    os.path.dirname(self.obs_pkg.__file__), "specs", instrument + "_" + filekind + ".rmap")
                rmapping = rmap.asmapping(spec_file)
                log.info("Loaded spec file from", repr(spec_file))
                self.args.rmaps.append(spec_file)
        self.rmap_apply(insert_rmap_references, categorized=categorized)

if __name__ == "__main__":
    sys.exit(RefactorScript2()())
