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

UNDEFINED_PARKEY_SUBST_VALUE = "N/A"

INSTRUMENT_FIXERS = {
}

TYPE_FIXERS = {
}

# PROVENANCE_KEYWORDS = ("META.REFFILE.DESCRIPTION", "META.REFFILE.PEDIGREE", "META.REFFILE.USEAFTER","META.REFFILE.HISTORY", "META.REFFILE.AUTHOR")
PROVENANCE_KEYWORDS = ("DESCRIP", "PEDIGREE", "USEAFTER","HISTORY", "AUTHOR")

# When loading headers,  make sure each keyword in a tuple is represented with
# the same value enabling any form to be used.  Case insensitive.
CROSS_STRAPPED_KEYWORDS = [
    ("INSTRUME", "INSTRUMENT", "META.INSTRUMENT.NAME","META.INSTRUMENT.TYPE"),
    ("TELESCOP","TELESCOPE", "META.TELESCOPE",),
    ("AUTHOR", "META.REFFILE.AUTHOR",),
    ("PEDIGREE", "META.REFFILE.PEDIGREE",),
    ("USEAFTER", "META.REFFILE.USEAFTER",),
    ("DESCRIP", "DESCRIPTION", "META.REFFILE.DESCRIPTION",),
    ]

