"""This module implements the "heavy" getreferences() top level interface.  

The "light" client is defined in the crds.client package and is entirely
dependent on the server for computing best references.  The advantage of the
"light" client is that it is comparatively simple code which is (or can be)
completely independent of the core CRDS library.

In contrast, the "heavy" client defined here provides a number of advanced 
features which depend on a full installation of the core library:

1. The ability to compute best references locally as a baseline behavior.

2. The ability to automatically "fall up" to the server when the local code 
is deemed obsolete.

3. The ability to "fall back" to local code when the server cannot be reached.

4. The ability to make client-vs-server s/w version comparisons to determine
when local code is obsolete.

5. The ability to record the last operational context and use it when the 
server cannot be contacted.
"""
import pprint

import crds.client as light_client
from . import get_default_context, CrdsLookupError, CrdsError, CrdsNetworkError
from . import rmap, log, utils, compat
from .rmap import get_cached_mapping

# ============================================================================

def getreferences(parameters, reftypes=None, context=None, ignore_cache=False):
    """
    This is the top-level get reference call for all of CRDS.  Based on
    `parameters`, getreferences() will download/cache the corresponding best
    reference and mapping files and return a map from reference file types to
    local reference file locations.
    
    `parameters` should be a dictionary-like object mapping { str:
    str,int,float,bool } for critical best reference related input parameters.
    
    If `reftypes` is None,  return all possible reference types.
    
    If `context` is None,  use the latest available context.

    If `ignore_cache` is True,  download files from server even if already present.
    """
    if context is None:
        # observatory = get_observatory(parameters)
        try:
            pmap_name = get_default_context()
        except CrdsError, exc:
            raise CrdsNetworkError("Network connection error: " + str(exc))
    else:
        assert isinstance(context, str) and context.endswith(".pmap"), \
            "context should specify a pipeline mapping, .e.g. hst_0023.pmap"
        pmap_name = context

    # Make sure pmap_name is actually present on the local machine.
    light_client.dump_mappings(pmap_name, ignore_cache=ignore_cache)
    
    header = parameters
    for key in parameters:
        assert isinstance(key, str), \
            "Non-string key " + repr(key) + " in parameters."
        try:
            parameters[key]
        except Exception:
            raise ValueError("Can't fetch mapping key " + repr(key) + 
                             " from parameters.")
        assert isinstance(parameters[key], (str,float,int,bool)), \
            "Parameter " + repr(key) + " isn't a string, float, int, or bool."
    
    # Use the pmap's knowledge of what CRDS needs to shrink the header
    # Note that at this point the min_header consists of unconditioned values.            
    #    pmap = rmap.get_cached_mapping(pmap_name)
    #    min_header = pmap.minimize_header(header)
    min_header = header
    
    assert isinstance(reftypes, (list, tuple, type(None))), \
        "reftypes must be a list or tuple of strings, or sub-class of those."

    if reftypes is not None:
        for reftype in reftypes:
            assert isinstance(reftype, str), \
                "each reftype must be a string, .e.g. biasfile or darkfile."

    bestrefs = light_client.get_best_references(pmap_name, min_header, reftypes=reftypes)
    
    best_refs_paths = light_client.cache_references(pmap_name, bestrefs, ignore_cache=ignore_cache)
        
    return best_refs_paths

def local_bestrefs(parameters, reftypes=None, context=None):
    """Compute bestrefs locally using the latest known local context."""
    pmap_name = context or get_best_known_local_context()
    log.warning("CRDS network getreferences() failed.  Using latest known local context", repr(pmap_name),
                   "and computing best references locally.")
    pmap = rmap.get_cached_mapping(pmap_name)
    min_header = pmap.get_minimum_header(parameters)
    bestrefs = pmap.get_best_references(header, list(reftypes))
    return { filekind:rmap.locate_file(reffile, pmap.observatory) for (filekind, reffile) in bestrefs }
 
# ============================================================================

def cache_server_info(info):
    """Write down the server `info` dictionary to help configure offline use."""
    observatory = info["observatory"]
    server_config = config.get_crds_config_path() + "/" + observatory + "/server_config"
    try:
        utils.ensure_dir_exists(server_config)
        with open(server_config, "w+") as f:
            f.write(pprint.pformat(info))
    except IoError, exc:
        log.warning("Couldn't save CRDS server info:", repr(exc))
 
def load_server_info():
    """Return last connected server status to help configure offline use."""
    observatory = config.get_crds_offline_observatory()
    server_config = config.get_crds_config_path() + "/" + observatory + "/server_config"
    log.write("Loading last known CRDS state from", repr(server_config))
    with open(server_config) as f:
        info = compat.literal_eval(f.read())
    return info

# ============================================================================

def establish_processing_mode():
    """Return the processing mode (local, remote) and the server information
    including the observatory and operational context.
    """
    try:
        info = client.get_server_info()
    except client.CrdsNetworkError:
        log.warning("Error contacting server %s,  attempting offline mode." % \
                    client.get_crds_server())
        info = load_server_info()
        connected = False
    else:
        cache_server_info(info)
        connected = True
    mode = config.get_crds_processing_mode()
    if connected and mode == "auto":
        mode = "remote" if local_version_obsolete(info) else "local"
    return mode, info

def get_best_known_local_context():
     """Determine the latest local context,  nominally for use as a fallback when network connection is unavailable.
     """
     return sorted(rmap.list_mappings("*.pmap"))[-1]
 
def minor_version(vers):
    """Strip the revision number off of `vers` and conver to float.
     e.g. "1.1.7"  --> 1.1
     """
    return float(".".join(vers.split(".")[:2]))
 
def local_version_obsolete(info):
    """Extract the CRDS server version from `info` and compare it to the minor
    version number of the CRDS client,  e.g. 1.2 vs. 1.1.
    """
    server_version = info["crds_version"]["str"]
    server_version = minor_version(server_version)
    client_version = minor_version(crds.__version__)
    return client_version < server_version
 
