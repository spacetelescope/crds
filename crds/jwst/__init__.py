from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import os.path

from crds import reftypes

HERE  = os.path.dirname(__file__) or "."

TYPES = reftypes.from_package_file(__file__)

INSTRUMENTS = TYPES.instruments
EXTENSIONS = TYPES.extensions
TEXT_DESCR = TYPES.text_descr
FILEKINDS = TYPES.filekinds

UNDEFINED_PARKEY_SUBST_VALUE = "UNDEFINED"

INSTRUMENT_FIXERS = {
}

TYPE_FIXERS = {
}

PROVENANCE_KEYWORDS = ("META.REFFILE.DESCRIPTION", "META.REFFILE.PEDIGREE", "META.REFFILE.USEAFTER","META.REFFILE.HISTORY", "META.REFFILE.AUTHOR")
# PROVENANCE_KEYWORDS = ("DESCRIP", "PEDIGREE", "USEAFTER","HISTORY", "AUTHOR")
USEAFTER_KEYWORDS = ("META.OBSERVATION.DATE", "META.OBSERVATION.TIME") # Dataset keywords matching in UseAfter selectors

DEFAULT_SELECTORS = ("Match", "UseAfter")   # Normal selector hierarchy in rmap

# When loading headers,  make sure each keyword in a tuple is represented with
# the same value enabling any form to be used.  Case insensitive.
CROSS_STRAPPED_KEYWORDS = {
    "META.INSTRUMENT.NAME" : ["INSTRUME", "INSTRUMENT", "META.INSTRUMENT.TYPE"],
    "META.TELESCOPE" : ["TELESCOP","TELESCOPE"],
    "META.REFFILE.AUTHOR" : ["AUTHOR"],
    "META.REFFILE.PEDIGREE" : ["PEDIGREE"],
    "META.REFFILE.USEAFTER" : ["USEAFTER"],
    "META.REFFILE.DESCRIPTION" : ["DESCRIP","DESCRIPTION"],
    "META.REFFILE.HISTORY" : ["HISTORY"],
    }
