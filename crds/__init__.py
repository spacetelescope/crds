from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

# ============================================================================

import os
import os.path

# ============================================================================

__path__.append(os.path.join(os.path.dirname(__file__), "core"))

# ============================================================================

__version__ = "7.1.0"  
__rationale__ = "JWST Build 7.1 Development"

# ============================================================================

from . import exceptions
from .exceptions import *

# ============================================================================

__all__ = [ 
           "get_default_context", 
           "getreferences", 
           "getrecommendations",
           "get_cached_mapping",
           "get_pickled_mapping",
           "get_symbolic_mapping",
           "locate_mapping",
           "locate_file",
           ] + exceptions.__all__

# List of all the observatory package names
ALL_OBSERVATORIES = ["hst", "jwst", "tobs"]

# keywords used to identify instrument from headers
INSTRUMENT_KEYWORDS = ["INSTRUME", "META.INSTRUMENT.NAME",
                       "META_INSTRUMENT_NAME", "INSTRUMENT", 
                       "META.INSTRUMENT.TYPE", "META_INSTRUMENT_TYPE"]

# ============================================================================

from . import config   # module

from crds.client import get_default_context
from .heavy_client import getreferences, getrecommendations
from .heavy_client import get_symbolic_mapping, get_pickled_mapping
from .rmap import get_cached_mapping, locate_mapping, locate_file, asmapping

# ============================================================================

URL = os.environ.get("CRDS_SERVER_URL", "https://crds-serverless-mode.stsci.edu")
from crds.client import api
api.set_crds_server(URL)

# ============================================================================

def handle_version():
    """Handles --version printing for scripts."""
    import sys, crds
    if '--version' in sys.argv :
        print(crds.__version__)
        sys.exit(0)
