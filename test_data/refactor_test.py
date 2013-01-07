#! /usr/bin/env pysh
#-*-python-*-

"""This module runs the refactoring code on a sequence of reference
files in order to test automatic rmap refactoring.  Based on the
reference file and a given context, this code determines which rmap to
modify and attempts to add the new reference file to it.

When --replace is specified on the command line, this code expects
that the given references are already in the rmaps and should replace
the originals when re-inserted.   This changes the expected actions from
"insert" to "replace" and defines what looks interesting.
"""

import sys
import random
import shutil
import os.path

from crds import (rmap, log, refactor, pysh, matches, utils, selectors, diff)
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

def main(context, new_references, expected_action_type):
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

        new_rmap_path = "./temp.rmap"
            
        new_refpath = newfile(refpath)      # a different looking file to insert
        pysh.sh("ln -s ${refpath} ${new_refpath}")
        
        try:
            do_refactoring(context, new_rmap_path, old_rmap_path, new_refpath, refpath, 0, expected_action_type)
        except Exception, exc:
            if log.get_verbose():
                raise
            log.error("Exception", str(exc))
        
        pysh.sh("rm -f ${new_rmap_path} ${new_refpath}")

    sys.stdout.flush()
    sys.stderr.flush()
    log.write()
    separator("=")
    log.standard_status()

def do_refactoring(context, new_rmap_path, old_rmap_path, new_refpath, old_refpath, verbosity=0,
                   expected="add"):

    separator("=")
    log.info("Inserting reference", os.path.basename(old_rmap_path), old_refpath)

    pysh.sh("rm -f ${new_rmap_path}")
    refactor.rmap_insert_references(old_rmap_path, new_rmap_path, [new_refpath])
    as_expected = refactor.rmap_check_modifications(old_rmap_path, new_rmap_path, expected)

    if not as_expected or verbosity:
        generation_info = pysh.out_err("grep %s ../../hst_gentools/gen_rmaps.out" % 
                                       os.path.basename(old_refpath))
        generation_info += pysh.out_err("grep %s ../../hst_gentools/gen_rmaps.out" % 
                                        os.path.basename(new_refpath))
        if generation_info.strip():
            separator()
            log.warning("rmap generation anomalies in gen_rmaps.out:")
            log.write(generation_info.strip())
        pysh.sh("rm -f ${new_rmap_path}")
        old = log.set_verbose(verbosity or 55)
        refactor.rmap_insert_references(old_rmap_path, new_rmap_path, [new_refpath])
        log.set_verbose(old)
        separator()
        log.write("diffing", repr(new_rmap_path), "from", repr(old_rmap_path))
        sys.stdout.flush()
        sys.stderr.flush()
        pysh.sh("diff -c ${old_rmap_path} ${new_rmap_path}")
        sys.stdout.flush()
        sys.stderr.flush()
        separator()
        pysh.sh("cd ../../hst_gentools; python db_test.py info ${old_refpath}")

def get_corresponding_rmap(context, refpath):
    """Return the path to the rmap which *would* refer to `reference` in `context.`
    """
    pmap = rmap.get_cached_mapping(context)
    instrument, filekind = utils.get_file_properties(pmap.observatory, refpath)
    old_rmap = rmap.locate_mapping(pmap.get_imap(instrument).get_rmap(filekind).name)
    return instrument, filekind, old_rmap

if __name__ == "__main__":

    if "--replace" in sys.argv:
       sys.argv.remove("--replace")
       expected_action_type = "replace"
    else:
       expected_action_type = "add"
       
    if "--verbose" in sys.argv:
        sys.argv.remove("--verbose")
        log.set_verbose(55)

    if len(sys.argv) < 3:
        log.write("usage: %s  [--verbose] [--replace] <context>  @file_list | <reference_file>..." % sys.argv[0])
        sys.exit(-1)
    if sys.argv[2].startswith("@"):
        references = new_references(sys.argv[2][1:])
    else:
        references = sys.argv[2:]

    context = sys.argv[1]
    assert rmap.is_mapping(context), "First parameter should be a .pmap"

    import cProfile
    cProfile.runctx('main(context, references, expected_action_type)', globals(), locals(), "refactor.stats")
