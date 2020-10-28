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

PROVENANCE_KEYWORDS = ("META.DESCRIPTION", "META.PEDIGREE", "META.USEAFTER","HISTORY", "META.AUTHOR", "META.MODEL_TYPE")

USEAFTER_KEYWORDS = ("META.OBSERVATION.DATE", "META.OBSERVATION.TIME") # Dataset keywords matching in UseAfter selectors

DEFAULT_SELECTORS = ("Match", "UseAfter")   # Normal selector hierarchy in rmap
