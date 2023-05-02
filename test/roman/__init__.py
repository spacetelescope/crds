import os.path

from crds.core import reftypes

HERE  = os.path.abspath(os.path.dirname(__file__) or ".")

TYPES = reftypes.from_package_file("roman", __file__)

OBSERVATORY = TYPES.observatory
INSTRUMENTS = TYPES.instruments
EXTENSIONS = TYPES.extensions
TEXT_DESCR = TYPES.text_descr
FILEKINDS = TYPES.filekinds

INSTRUMENT_FIXERS = {
}

TYPE_FIXERS = {
}

# List of keywords whose values are logged in certifier output when "dump provenance" is enabled:
PROVENANCE_KEYWORDS = ("ROMAN.META.DESCRIPTION", "ROMAN.META.PEDIGREE", "ROMAN.META.USEAFTER", "HISTORY", "ROMAN.META.AUTHOR")

USEAFTER_KEYWORDS = ("ROMAN.META.EXPOSURE.START_TIME",) # Dataset keywords matching in UseAfter selectors

DEFAULT_SELECTORS = ("Match", "UseAfter")   # Normal selector hierarchy in rmap
