# The "crds" __version__ defined here should also reflect the behavior of 
# crds.client
__version__ = "0.1.0"

from crds.client import getreferences, cache_references, get_default_context, CrdsLookupError
from crds.utils import CrdsError

def handle_version():
    """Handles --version printing for scripts."""
    import sys, crds
    if '--version' in sys.argv :
        print crds.__version__
        sys.exit(0)
