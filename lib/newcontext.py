"""This module manages the automatic generation of new context files based on
a list of new rmaps and a baseline context.
"""
import os.path
import shutil
import re

from crds import (rmap, utils, checksum, log)

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
    
def get_update_map(old_pipeline, updated_rmaps):
    """Given the name of a pipeline context, `old_pipeline`, and a list
    of new rmap names, `updated_rmaps`,  return the mapping:
        { imap_name : [ updates_for_that_imap, ... ], ... }
    """
    pctx = rmap.get_cached_mapping(old_pipeline)
    updates = {}
    for update in updated_rmaps:
        instrument, _filekind = utils.get_file_properties(
                pctx.observatory, update)
        imap_name = pctx.get_imap(instrument).filename
        if imap_name not in updates:
            updates[imap_name] = []
        assert update not in updates[imap_name], \
            "Duplicate update for " + repr(update)
        updates[imap_name].append(update)
    return updates
            
def generate_new_contexts(old_pipeline, updates, new_names, observatory=None):
    """Generate new pipeline and instrument context files given:
    old_pipeline -- name of pipeline mapping
    updates --   { old_imap : [ new_rmaps ], ... }
    new_names --   { old_pmap : new_pmap, old_imaps : new_imaps }
    """
    if observatory is None:
        observatory = rmap.get_cached_mapping(old_pipeline).observatory
    new_names = dict(new_names)
    for imap_name in updates:
        hack_in_new_maps(imap_name, new_names[imap_name], updates[imap_name], 
                         observatory=observatory)
    new_pipeline = new_names.pop(old_pipeline)
    new_imaps = new_names.values()
    hack_in_new_maps(old_pipeline, new_pipeline, new_imaps, observatory=observatory)
    where = [ rmap.locate_mapping(m) for m in [new_pipeline] + new_imaps]
    checksum.update_checksums(where)
    return [new_pipeline] + new_imaps
    
def generate_fake_names(old_pipeline, updates):
    """Generate a map from old pipeline and instrument context names to new
    names for their updated replacements.   "Fake" names only work locally
    and may collide with CRDS server names...  and hence would not be
    submissible.
    """
    new_names = {}
    new_names[old_pipeline] = fake_name(old_pipeline)
    for old_imap in updates:
        new_names[old_imap] = fake_name(old_imap)
    return new_names

def hack_in_new_maps(old, new, updated_maps, observatory):
    """Given mapping named `old`,  create a modified copy named `new` which
    installs each map of `updated_maps` in place of it's predecessor.
    """
    copy_mapping(old, new)                    
    for map in updated_maps:
        replaced = replace_mapping(new, map)
        if replaced:
            log.info("Replaced", repr(replaced), "in", repr(new), "with", repr(map))
        else:
            instrument, filekind = utils.get_file_properties(observatory, map)
            if old.endswith(".imap"):
                add_mapping(new, filekind, map)
                log.info("Added", repr(map), "to", repr(new), "for", repr(filekind))
            else:  # .pmap,  other things probably preclude this from ever working...
                add_mapping(new, instrument, map)
                log.info("Added", repr(map), "to", repr(new), "for", repr(instrument))
            
def copy_mapping(old_map, new_map):
    """Make a copy of mapping `old_map` named `new_map`."""
    old_path = rmap.locate_mapping(old_map)
    new_path = rmap.locate_mapping(new_map)
    assert not os.path.exists(new_path), \
        "New mapping file " + repr(new_map) + " already exists."
    shutil.copyfile(old_path, new_path)

def fake_name(old_map):
    """Given and old mapping name, `old_map`, adjust the serial number to 
    create a new mapping name of the same series.   This name is fake in the
    sense that it is local to a developer's machine.
    """
    m = re.search(r"_(\d+)\.[pir]map", old_map)
    if m:
        serial = int(m.group(1)) + 1
        new_map = re.sub(r"_(\d+)(\.[pir]map)", r"_%04d\2" % serial, old_map)
    elif re.match(r"\w+\.[pir]map", old_map):   
        # if no serial,  start off existing sequence as 0
        parts = os.path.splitext(old_map)
        new_map = fake_name(parts[0] + "_0000" + parts[1])
    else:
        raise ValueError("Unrecognized mapping filename " + repr(old_map))
    if os.path.exists(rmap.locate_mapping(new_map)):
        # recurse until there's a free name,  or eventually fail.
        return fake_name(new_map)   
    else:
        return new_map
        
def replace_mapping(context, mapping):
    """Replace the filename in file `context` with the same generic name
    as `mapping` with `mapping`.  Re-write `context` in place.
    """
    #    'ACS' : 'hst_acs.imap',
    ppmap = r"(\s*'\w+'\s*:\s*')(\S+)(',.*)"
    generic_mapping = generic_name(mapping)
    lines = []
    where = rmap.locate_mapping(context)
    replaced = None
    with open(where) as old_file:
        for line in old_file.readlines():
            m = re.match(ppmap, line)
            if m and generic_name(m.group(2)) == generic_mapping:
                line = re.sub(ppmap, r"\1%s\3" % mapping, line)
                replaced = m.group(2)
            lines.append(line)
    if replaced:
        new_contents = "".join(lines)
        with open(where,"w+") as new_file:
            new_file.write(new_contents)
    return replaced

def add_mapping(context, key, mapping):
    """Add the filename `mapping` to `context` at `key`."""
    where = rmap.locate_mapping(context)
    with open(where) as old_file:
        in_selector = False
        lines = []
        for line in old_file.readlines():
            if in_selector and line.startswith("}"):
                lines.append("    " + repr(key) + " : " + repr(mapping) + ",\n")
                in_selector = False
            if line.startswith("selector = {"):
                in_selector = True
            lines.append(line)
    with open(where, "w+") as new_file:
        new_file.write("".join(lines))

def generic_name(mapping):
    """Return `mapping` with serial number chopped out.
    
    >>> generic_name("hst_acs_00001.imap")
    'hst_acs.imap'
    """
    name, ext = os.path.splitext(mapping)
    parts = name.split("_")
    if re.match("\d+", parts[-1]):
        parts = parts[:-1]
    return "_".join(parts) + ext

