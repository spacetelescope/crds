"""This script gets the best references as determined by the same code which
runs in OPUS,  which under some circumstances might have different answers
than the catalog.
"""
import sys

import crds.pysh as pysh

DMS_HOST = "dmsdevvm4.stsci.edu"

def remote_bestrefs_output(dataset):
    dataset = dataset.lower()
    lines = pysh.lines("ssh ${DMS_HOST} bestref.py -m dball -d ${dataset}")
    return lines

def opus_bestrefs(dataset):
    lines = remote_bestrefs_output(dataset)
    bestrefs = {}
    for line in lines:
        words = line.split()
        db_colname = words[0]
        if db_colname.endswith(("file","tab")):
            keyword = db_colname.split("_")[2].upper()
            value = words[2].split("'")[1]
            bestrefs[keyword] = value
    return bestrefs

if __name__ == "__main__":
    print opus_bestrefs(sys.argv[1])


            
