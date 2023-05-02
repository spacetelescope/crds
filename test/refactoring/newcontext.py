"""This module manages the automatic generation of new context files based on
a list of new rmaps and a baseline context.
"""
import os.path
import sys
import shutil
import re
import glob

import crds
from crds.core import (rmap, utils, log, cmdline, config)
from . import refactor

# =============================================================================

# Code used by the website to determine affected

def get_update_map(old_pipeline, updated_rmaps):
    """Given the name of a pipeline context, `old_pipeline`, and a list
    of new rmap names, `updated_rmaps`,  return the mapping:

        { imap_name : [ updates_for_that_imap, ... ], ... }

    Updated rmaps can be rmap names or strings of the form:

        <instrument>_<filekind>_"n/a"

    e.g.  miri_dflat_n/a
    """
    pctx = crds.get_pickled_mapping(old_pipeline)   # reviewed
    updates = {}
    for update in sorted(updated_rmaps):
        if update.endswith(("_n/a","_N/A")):
            instrument, _filekind, na = update.split("_")
        else:  # should be an rmap name
            instrument, _filekind = utils.get_file_properties(pctx.observatory, update)
        imap_name = pctx.get_imap(instrument).filename
        if imap_name not in updates:
            updates[imap_name] = []
        assert update not in updates[imap_name], "Duplicate update for " + repr(update)
        updates[imap_name].append(update)
    return updates

# =============================================================================

# Code used by the website to generate new contexts.

def generate_new_contexts(old_pipeline, updates, new_names):
    """Generate new pipeline and instrument context files given:
    old_pipeline -- name of pipeline mapping
    updates --   { old_imap : [ new_rmaps ], ... }
    new_names --   { old_pmap : new_pmap, old_imaps : new_imaps }
    """
    new_names = dict(new_names)
    for imap_name in sorted(updates):
        hack_in_new_maps(imap_name, new_names[imap_name], updates[imap_name])
    new_pipeline = new_names.pop(old_pipeline)
    new_imaps = list(new_names.values())
    hack_in_new_maps(old_pipeline, new_pipeline, new_imaps)
    return [new_pipeline] + new_imaps

def hack_in_new_maps(old, new, updated_maps):
    """Given mapping named `old`,  create a modified copy named `new` which
    installs each map of `updated_maps` in place of it's predecessor.
    """
    copy_mapping(old, new)
    for mapping in sorted(updated_maps):
        key, replaced, replacement = insert_mapping(new, mapping)
        if replaced:
            log.info("Replaced", repr(replaced), "with", repr(replacement), "for", repr(key), "in", repr(old), "producing", repr(new))
        else:
            log.info("Added", repr(replacement), "for", repr(key), "in", repr(old), "producing", repr(new))

def insert_mapping(context, mapping):
    """Replace the filename in file `context` with the same generic name
    as `mapping` with `mapping`.  Re-write `context` in place.

    If mapping is of the form <instrument>_<type>_"n/a",  then it specifies
    that <type> of <instrument> should be set to "N/A".
    """
    # 'ACS' : 'hst_acs.imap',
    where = config.locate_mapping(context)
    # readonly caching is ok because this call is always made on a newly named
    # copy of the original rmap;  the only thing mutated is the uncached new mapping.
    loaded = rmap.asmapping(context, cache="readonly")
    if mapping.endswith(("_n/a", "_N/A")):
        instrument, key, special = mapping.split("_")
        replacement = special.upper()
    else:
        key = loaded.get_item_key(mapping)
        replacement = mapping
    key, replaced = loaded.set_item(key, os.path.basename(replacement))
    loaded.write(where)
    return key, replaced, replacement

def copy_mapping(old_map, new_map):
    """Make a copy of mapping `old_map` named `new_map`."""
    old_path = config.locate_mapping(old_map)
    new_path = config.locate_mapping(new_map)
    assert not os.path.exists(new_path), "New mapping file " + repr(new_map) + " already exists."
    shutil.copyfile(old_path, new_path)

# =============================================================================

# Code for making "fake/test" new contexts on the command line.

def new_context(old_pipeline, updated_rmaps):
    """Given a pipeline mapping name `old_pipeline`, and a list of the names
    of new rmaps, `updated_rmaps`, generate new imaps as needed and a single
    pmap which refers to them all.

    Returns  { old_name : fake_names }
    """
    updates = get_update_map(old_pipeline, updated_rmaps)
    new_names = generate_fake_names(old_pipeline, updates)
    generate_new_contexts(old_pipeline, updates, new_names)
    return new_names

def generate_fake_names(old_pipeline, updates):
    """Generate a map from old pipeline and instrument context names to new
    names for their updated replacements.   "Fake" names only work locally
    and may collide with CRDS server names...  and hence would not be
    submissible.
    """
    new_names = {}
    new_names[old_pipeline] = fake_name(old_pipeline)
    for old_imap in sorted(updates):
        new_names[old_imap] = fake_name(old_imap)
    return new_names

def fake_name(old_map):
    """Given and old mapping name, `old_map`, adjust the serial number to
    create a new mapping name of the same series.   This name is fake in the
    sense that it is local to a developer's machine.
    """
    if re.search(r"_\d+", old_map):
        map_glob = re.sub(r"_\d+(\..map)", r"_*\1", old_map)
        same_maps = sorted(glob.glob(config.locate_mapping(map_glob)))
        if same_maps:
            last_map = same_maps[-1]
            match = re.search(r"_(\d+)\..map", last_map)
            serial = int(match.group(1), 10) + 1
            new_map = re.sub(r"_(\d+)(\.[pir]map)", r"_%04d\2" % serial, old_map)
        else:
            new_map = old_map
    elif re.search(r"\w+[^\d]+\..map", old_map):
        # if no serial,  start off existing sequence as 0001
        parts = os.path.splitext(old_map)
        new_map = parts[0] + "_0001" + parts[1]
        new_map = fake_name(new_map)
    else:
        raise ValueError("Unrecognized mapping filename " + repr(old_map))
    if os.path.exists(config.locate_mapping(new_map)):
        # recurse until there's a free name,  or eventually fail.
        return fake_name(new_map)
    else:
        if not new_map.startswith("./"):
            new_map = "./" + os.path.basename(new_map)
        return new_map

def update_header_names(name_map):
    """Update the .name and .derived_from fields in mapping new_path.header
    to reflect derivation from old_path and name new_path.
    """
    for old_path, new_path in sorted(name_map.items()):
        old_base, new_base = os.path.basename(old_path), os.path.basename(new_path)
        refactor.update_derivation(new_path, old_base)
        log.info("Adjusting name", repr(new_base), "derived_from", repr(old_base),
                 "in", repr(new_path))
    return name_map # no change

# ============================================================================

class NewContextScript(cmdline.Script):
    """Defines the command line handler for crds newcontext."""

    description = """Based on `old_pmap`,  generate a new .pmap and .imaps as
needed in order to support `new_rmaps`.   Currently generated contexts have
fake names and are for local test purposes only,  not formal distribution.
"""
    def add_args(self):
        self.add_argument("old_pmap")
        self.add_argument("new_rmap", nargs="+", help="Names of new rmaps to insert into the new context.""")

    def main(self):
        name_map = new_context(self.args.old_pmap, self.args.new_rmap)
        update_header_names(name_map)
        return log.errors()

if __name__ == "__main__":
    sys.exit(NewContextScript()())
