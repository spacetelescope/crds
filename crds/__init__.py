# The "crds" __version__ defined here should also reflect the behavior of 
# crds.client
__version__ = "1.5.0"   # >= OPUS-2015.1 and/or OPUS-2014.4a server

# ============================================================================

__all__ = [ 
           "get_default_context", 
           "getreferences", 
           "getrecommendations",
           "get_cached_mapping",
           
           "CrdsError", 
           "CrdsNetworkError", 
           "CrdsLookupError", 
           "CrdsDownloadError",
           
           "CrdsUnknownInstrumentError",
           "CrdsUnknownRefypeError",
           ]

# List of all the observatory package names
ALL_OBSERVATORIES = ["hst", "jwst", "tobs"]

# ============================================================================

from . import config   # module
from crds.client import CrdsError, CrdsLookupError, CrdsNetworkError, CrdsDownloadError
from crds.client import get_default_context

from .heavy_client import getreferences, getrecommendations

from .rmap import get_cached_mapping, locate_mapping, locate_file
from .rmap import CrdsUnknownInstrumentError, CrdsUnknownReftypeError

# ============================================================================

def handle_version():
    """Handles --version printing for scripts."""
    import sys, crds
    if '--version' in sys.argv :
        print crds.__version__
        sys.exit(0)
