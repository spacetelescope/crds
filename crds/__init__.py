from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

# ============================================================================

import os
import os.path
import sys
import importlib

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
    "pysh",
    "python23",
    "exceptions",
    "log",
    "config",
    "constants",
    "utils",
    "timestamp",
    "custom_dict",
    "selectors",
    "mapping_verifier",
    "reftypes",
    "substitutions",
    "rmap",
    "heavy_client",
    "cmdline",
]


for core_module in CORE_MODULES:
    globals()[core_module] = importlib.import_module("crds.core" + "." + core_module)
    sys.modules["crds." + core_module] = sys.modules["crds.core." + core_module]

# ============================================================================

URL = os.environ.get("CRDS_SERVER_URL", "https://crds-serverless-mode.stsci.edu")
api.set_crds_server(URL)

