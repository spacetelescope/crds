from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# The "crds" __version__ defined here should also reflect the behavior of 
# crds.client
__version__ = "6.0.1"   #  jwst_build6,  also change ../setup.cfg

# ============================================================================

from . import exceptions

__all__ = [ 
           "get_default_context", 
           "getreferences", 
           "getrecommendations",
           "get_cached_mapping",           
           ] + exceptions.__all__

# List of all the observatory package names
ALL_OBSERVATORIES = ["hst", "jwst", "tobs"]

# keywords used to identify instrument from headers
INSTRUMENT_KEYWORDS = ["INSTRUME", "META.INSTRUMENT.NAME",  "META_INSTRUMENT_NAME", "INSTRUMENT", 
                       "META.INSTRUMENT.TYPE", "META_INSTRUMENT_TYPE"]

# ============================================================================

from . import config   # module

from .exceptions import *

from crds.client import get_default_context
from .heavy_client import getreferences, getrecommendations
from .rmap import get_cached_mapping, locate_mapping, locate_file

# ============================================================================

def handle_version():
    """Handles --version printing for scripts."""
    import sys, crds
    if '--version' in sys.argv :
        print(crds.__version__)
        sys.exit(0)
