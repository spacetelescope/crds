#! /usr/bin/env pysh
#-*-python-*-

"""This module runs the refactoring code on a sequence of reference files in order
to test automatic rmap refactoring.   Based on the reference file and a given
context,  this code determines which rmap to modify and attempts to add the new
reference file to it.
"""

import sys
import random
import shutil
import os.path

from crds import (rmap, log, refactor, pysh, matches, utils)
import crds.client as client

def newfile(fname):
   root, ext = os.path.splitext(fname)
   return "./" + os.path.basename(root) + "_new" + ext

def new_references(new_file):
    for line in open(new_file):
        if not line.strip():
            continue
        new_reference = line.split()[0]
        yield new_reference

def separator(char="-", len=80):
    log.write(char*len)        

def main(context, new_references):
    """Insert `new_references` into `context`, outputting debug information
    when the insertion doesn't result in the expected action.   For files already
    in `context`,  the expected action is a replacement.   For files not in
    `context`,  the expected action is an insertion.   Here "in" refers to
    """
    for reference in new_references:
        
        pmap = rmap.get_cached_mapping(context)

        try:
           refpath = pmap.locate.locate_server_reference(reference)
        except KeyError:
           log.error("Can't locate reference file", repr(reference))
           continue

        try:
            instrument, filekind, old_rmap_path = get_corresponding_rmap(context, refpath)
        except Exception, exc:
            log.error("Failed getting corresponding rmap for", repr(reference), repr(str(exc)))
            continue

        separator("=")
        log.info("Reference", os.path.basename(old_rmap_path), os.path.basename(refpath))

        new_rmap_path = "./temp.rmap"
            
        new_refpath = newfile(refpath)      # a different looking file to insert
        pysh.sh("ln -s ${refpath} ${new_refpath}")
        
        try:
            expected_change = do_refactoring(context, new_rmap_path, old_rmap_path, new_refpath, refpath)
            if not expected_change:
                do_refactoring(context, new_rmap_path, old_rmap_path, new_refpath, refpath, verbosity=60)
        except Exception, exc:
            log.error("Exception", str(exc))
        
        pysh.sh("rm -f ${new_rmap_path} ${new_refpath}")

    sys.stdout.flush()
    sys.stderr.flush()
    log.write()
    separator("=")
    log.standard_status()

def do_refactoring(context, new_rmap_path, old_rmap_path, new_refpath, old_refpath, verbosity=0):
    log.set_verbose(verbosity)

    mtchs = [x[1:] for x in matches.find_full_match_paths(context, os.path.basename(old_refpath))]
    if mtchs:
        keys = simplified_path(mtchs[0])[0]
        values = [simplified_path(match)[1] for match in mtchs]
        log.verbose("Original matches at:", keys, values)
        expected_action = "replace"
    else:
        log.verbose("No matches for",repr(old_refpath))
        expected_action = "insert"

    pysh.sh("rm -f ${new_rmap_path}")
    actions = refactor.rmap_insert_references(
       old_rmap_path, new_rmap_path, [new_refpath])
    as_expected = ((len(actions) == 1) and (actions[0].action == expected_action))

    if verbosity:
        separator()
        log.write("diffing", repr(new_rmap_path), "from", repr(old_rmap_path))
        sys.stdout.flush()
        sys.stderr.flush()
        pysh.sh("diff -c ${old_rmap_path} ${new_rmap_path}")
        sys.stdout.flush()
        sys.stderr.flush()
        separator()
        pysh.sh("cd ../../hst_gentools; python db_test.py info ${old_refpath}")

    return as_expected

    
def simplified_path(match_path):
    keys = []
    values = []
    for tup in match_path:
        for key,val in tup:
            keys.append(key)
            values.append(val)
    return keys, tuple(values)
    
def get_corresponding_rmap(context, refpath):
    """Return the path to the rmap which *would* refer to `reference` in `context.`
    """
    pmap = rmap.get_cached_mapping(context)
    instrument, filekind = utils.get_file_properties(pmap.observatory, refpath)
    old_rmap = rmap.locate_mapping(pmap.get_imap(instrument).get_rmap(filekind).name)
    return instrument, filekind, old_rmap

if __name__ == "__main__":
    # log.set_verbose(60)
    context = sys.argv[1]
    if len(sys.argv) < 3 or not rmap.is_mapping(context):
        log.write("usage: %s  <context>  @file_list | <reference_file>..." % sys.argv[0])
        sys.exit(-1)
    if sys.argv[2].startswith("@"):
        references = new_references(sys.argv[2][1:])
    else:
        references = sys.argv[2:]
    import cProfile
    cProfile.runctx('main(context, references)', globals(), locals(), "refactor.stats")
