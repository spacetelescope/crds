from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

# ============================================================================

import os
import os.path
import sys

# ============================================================================

__version__ = "7.1.0"  
__rationale__ = "JWST Build 7.1 Development"

# ============================================================================

from crds.core import config   # module

from crds.core.heavy_client import getreferences, getrecommendations
from crds.core.heavy_client import get_symbolic_mapping, get_pickled_mapping
from crds.core.rmap import get_cached_mapping, asmapping
from crds.core.config import locate_mapping, locate_file

from crds.core import exceptions
from crds.core.exceptions import *
from crds.core.constants import ALL_OBSERVATORIES, INSTRUMENT_KEYWORDS

from crds.client import api
from crds.client import get_default_context

# ============================================================================

CORE_MODULES = [
    "cmdline",
    "config",
    "constants",
    "custom_dict",
    "exceptions",
    "heavy_client",
    "log",
    "mapping_verifier",
    "pysh",
    "python23",
    "reftypes",
    "rmap",
    "selectors",
    "substitutions",
    "timestamp",
    "utils",
]

__import__("crds.core", None, None, CORE_MODULES)

for core_module in CORE_MODULES:
    sys.modules["crds." + core_module] = sys.modules["crds.core." + core_module]

# ============================================================================

URL = os.environ.get("CRDS_SERVER_URL", "https://crds-serverless-mode.stsci.edu")
api.set_crds_server(URL)

# ============================================================================

def handle_version():
    """Handles --version printing for scripts."""
    import sys, crds
    if '--version' in sys.argv :
        print(crds.__version__)
        sys.exit(0)

