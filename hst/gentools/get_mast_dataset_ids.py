#! /usr/bin/env pysh
#-*-python-*-

"""This is a script to reduce the output of testall.err into a list
of datasets important enough to download.
"""
from crds.pysh import *

# Datasets: wfc3 biasfile 5 IBWVA2OUQ IBWV02OPQ IBWVA2P0Q IBWVA2P5Q IBWVA2PBQ 

def get_mismatched_objects(filename="testall.err"):
    objects = []
    for line in lines("grep 'Datasets:' ${filename}"):
        words = line.strip().split()
        instrument = words[1]
        filekind = words[2]
        count = int(words[3])
        datasets = words[4:]
        objects.append((count, datasets))
    return objects

def main(filename, important):    
    for mismatched in get_mismatched_objects(filename):
        if mismatched[0] > important:
            print " ".join(mismatched[1])

if __name__ == "__main__":
    usage("<source_file> <test_count_importance_threshhold>", 2, 2);
    main(sys.argv[1], int(sys.argv[2]))
