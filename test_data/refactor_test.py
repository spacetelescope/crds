#! /usr/bin/env pysh
#-*-python-*-

import sys
import random
import shutil
import os.path

from crds import (rmap, log, refactor, pysh, matches)
import crds.client as client

def newfile(fname):
   root, ext = os.path.splitext(fname)
   return "./" + os.path.basename(root) + "_new" + ext

def get_reference(context, r):
   nerrors = 0
   references = r.reference_names()
   while True:
      n = int(len(references) * random.random())
      old_ref = references[n]
      try:
         log.write("dumping", repr(old_ref))
         client.dump_references(context, [old_ref])
         return rmap.locate_file(old_ref)
      except Exception:
         raise
         log.error()
         nerrors += 1
         if nerrors > 10:
            raise RuntimeError("too many missing references")


def main():
   # usage("<context> [seed]", 1, 2)

   log.set_verbose(True)

   context = sys.argv[1]
   if len(sys.argv) == 3:
      random.seed(sys.argv[2])
   else:
      random.seed("0")
   map = rmap.get_cached_mapping(context)

   for mapping in map.mapping_names():
      
      r = rmap.get_cached_mapping(mapping)
      
      if isinstance(r, rmap.ReferenceMapping):

         log.write("="*70)
         log.write("Testing", repr(mapping))

         try:
            old_ref = get_reference(context, r)
         except Exception:
            log.error("Skipping", r.name)
            continue

         new_ref = newfile(old_ref)      # a different looking file to insert
         shutil.copy(old_ref, new_ref)
         
         old_rmap = rmap.locate_file(mapping)
         shutil.copy(old_rmap, "./" + mapping)
         new_rmap = newfile(old_rmap)    # a place to write the updated rmap

         mtchs = [x[1:] for x in matches.find_full_match_paths(
            context, os.path.basename(old_ref))]
         log.write("Original matches at:", mtchs) 

         try:
            pysh.sh("rm ${new_rmap}")
            actions = refactor.rmap_insert_references(
               old_rmap, new_rmap, [new_ref])
            # for action in actions:
            #    log.write(action)
            log.write("diffing", repr(new_rmap), "from", repr(mapping))
            sys.stdout.flush()
            sys.stderr.flush()
            pysh.sh("diff -c ${old_rmap} ${new_rmap}")
            sys.stdout.flush()
            sys.stderr.flush()
         except:
            log.error()

   sys.stdout.flush()
   sys.stderr.flush()
   log.write()
   log.standard_status()

if __name__ == "__main__":
   main()

