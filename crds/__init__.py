import os
import os.path
import sys
import importlib

import warnings

warnings.filterwarnings(
    "ignore", ".*found in sys.modules after import of package.*")

# ============================================================================

__version__ = "10.3.8"   # XXXX  see also ../setup.cfg
__rationale__ = "Support for HST ACS SATUFILE, additional JWST step parameter references, and bestrefs bug fix"

__all__ = [
    "getrecommendations",
    "getreferences",
    "assign_bestrefs",
    "get_pickled_mapping",
    "get_symbolic_mapping",
    "get_cached_mapping",
    "get_context_name",
    "asmapping",
    "locate_mapping",
    "locate_file",
    "get_default_context",
    ]

# ============================================================================

from .core import config   # module

from .core.rmap import get_cached_mapping, asmapping
from .core.config import locate_mapping, locate_file

from .core import exceptions
from .core.exceptions import *
from .core.constants import ALL_OBSERVATORIES, INSTRUMENT_KEYWORDS

from .core.heavy_client import getreferences, getrecommendations
from .core.heavy_client import get_symbolic_mapping, get_pickled_mapping
from .core.heavy_client import get_context_name

from crds.client import api
from crds.client import get_default_context

from crds.bestrefs import assign_bestrefs

# ============================================================================

'''This code section supports moving modules from the root crds namespace into
sub-packages while still supporting the original CRDS package external interface.
This allows the code to be partitioned without changing external imports.  This
is made more difficult by the inapplicability of namespace packages because this
__init__ is not empty.

The strategy employed here is to implement core packages normally in crds.core,
then alias them into the top level crds namespace using importlib.import_module()
and sys.modules to make it appear as if each core package has already been imported
and belongs to the top level namespace.
'''
def _alias_subpackage_module(subpkg, modules):
    """Alias each module from `modules` of `subpkg` to appear in this
    namespace.
    """
    for module in modules:
        globals()[module] = importlib.import_module(subpkg + "." + module)
        sys.modules["crds." + module] = sys.modules[subpkg + "." + module]

_CORE_MODULES = [
    "pysh",
    "python23",
    "exceptions",
    "log",
    "config",
    "constants",
    "utils",
    "crds_cache_locking",
    "timestamp",
    "custom_dict",
    "selectors",
    "mapping_verifier",
    "substitutions",
    "rmap",
    "heavy_client",
    "cmdline",
    "naming",
    "git_version",
]

# e.g. make crds.rmap importable same as crds.core.rmap reorganized code
_alias_subpackage_module("crds.core", _CORE_MODULES)

# ============================================================================

# e.g. python -m crds.newcontext now called as python -m crds.refactoring.newcontext

_REFACTORING_MODULES = [
    "checksum",
    "newcontext",
    "refactor",
    "refactor2",
]

# e.g. make crds.rmap importable same as crds.core.rmap reorganized code
_alias_subpackage_module("crds.refactoring", _REFACTORING_MODULES)

# ============================================================================

# e.g. python -m crds.uniqname now called as -m crds.refactoring.uniqname

_MISC_MODULES = [
    "datalvl",               # external interface with pipelines
    "query_affected",        # external interface with pipelines
    "uniqname",              # external interface with submitters

    "check_archive",         # misc utility
    "sql",                   # prototype convenience wrapper
]

# e.g. make crds.rmap importable same as crds.core.rmap reorganized code
_alias_subpackage_module("crds.misc", _MISC_MODULES)

# ============================================================================

URL = os.environ.get("CRDS_SERVER_URL", "https://crds-serverless-mode.stsci.edu")
api.set_crds_server(URL)
