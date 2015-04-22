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

INSTRUMENT_FIXERS = {
}

TYPE_FIXERS = {
}
