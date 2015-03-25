# The "crds" __version__ defined here should also reflect the behavior of 
# crds.client
__version__ = "1.6.0"   # > jwst_build4 

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
INSTRUMENT_KEYWORDS = ["INSTRUME", "META.INSTRUMENT.NAME",  "META_INSTRUMENT_NAME", "INSTRUMENT"]

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
        print crds.__version__
        sys.exit(0)
