"""This script gets the best references as determined by the same code which
runs in OPUS,  which under some circumstances might have different answers
than the catalog.
"""
import sys
import pprint
import cPickle

from crds import pysh, log

DMS_HOST = "dmsdevvm4.stsci.edu"

BESTREF_PKL = "../../../datasets/opus_bestref.pkl"

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

def load_alternate_dataset_headers():
    try:
        alternate_headers = cPickle.load(open(BESTREF_PKL))
        log.info("Loading opus dataset headers.")
    except:
        alternate_headers = {}
        log.warning("Loading opus headers failed.")
    return alternate_headers

def main():
    alternates = load_alternate_dataset_headers()
    for dataset in sys.argv[1:]:
        if log.VERBOSE_FLAG:
            log.write(dataset)
        else:
            log.write(".", eol="", sep="")
        try:
            bestrefs = opus_bestrefs(dataset)
            alternates[dataset] = bestrefs
            log.verbose("Bestrefs for", dataset, "=", bestrefs)
        except Exception, exc:
            log.error("Exception on dataset", dataset)
    with open(BESTREF_PKL, "w+") as f:
        cPickle.dump(alternates, f)

if __name__ == "__main__":
    main()
