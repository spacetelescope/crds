"""This module implements the "heavy" getreferences() top level interface.  

The "light" client is defined in the crds.client package and is entirely
dependent on the server for computing best references.  The advantage of the
"light" client is that it is comparatively simple code which is has shallower
dependencies on the core library.

In contrast, the "heavy" client defined here provides a number of advanced 
features which depend on a full installation of the core library:

1. The ability to compute best references locally as a baseline behavior.

2. The ability to automatically "fall up" to the server when the local code 
is deemed obsolete.

3. The ability to "fall back" to local code when the server cannot be reached.

4. The ability to make client-vs-server CRDS s/w version comparisons to determine
when local code is obsolete.

5. The ability to record the last operational context and use it when the 
server cannot be contacted.
"""
import pprint

import crds.client as light_client
from . import rmap, log, utils, compat, config

# ============================================================================

def getreferences(parameters, reftypes=None, context=None, ignore_cache=False,
                  observatory="jwst"):
    """
    This is the top-level get reference call for all of CRDS.  Based on
    `parameters`, getreferences() will download/cache the corresponding best
    reference and mapping files and return a map from reference file types to
    local reference file locations.
    
    parameters      { str:  str,int,float,bool, ... }
    
      `parameters` should be a dictionary-like object mapping best reference 
      matching parameters to their values for this dataset.
    
    reftypes        [ str, ... ] 
    
      If `reftypes` is None,  return all possible reference types.   Otherwise
      return the reference types specified by `reftypes`.
    
    context         str
    
      Specifies the pipeline context,  i.e. specific version of CRDS rules used 
      to do the best references match.   If `context` is None,  use the latest 
      available context.

    ignore_cache    bool

      If `ignore_cache` is True,  download files from server even if already present.
    
    observatory     str
    
       nominally 'jwst' or 'hst'.
    
    Returns { reftype : cached_bestref_path }
    
      returns a mapping from types requested in `reftypes` to the path for each
      cached reference file.
    """
    check_observatory(observatory)
    check_parameters(parameters)
    check_reftypes(reftypes)
    check_context(context)  

    mode, final_context = get_processing_mode(observatory, context)

    if mode == "local":
        bestrefs = local_bestrefs(
            parameters, reftypes=reftypes, context=final_context, ignore_cache=ignore_cache)
    else:
        log.verbose("Computing best references remotely.")
        bestrefs = light_client.get_best_references(
            final_context, parameters, reftypes=reftypes)

    # Attempt to cache the recommended references,  which unlike dump_mappings
    # should work without network access if files are already cached.
    best_refs_paths = light_client.cache_references(
        final_context, bestrefs, ignore_cache=ignore_cache)
    
    return best_refs_paths

# ============================================================================
def check_observatory(observatory):
    assert observatory in ["hst", "jwst", "tobs"]

def check_parameters(header):
    """Make sure dict-like `header` is a mapping from strings to simple types."""
    for key in header:
        assert isinstance(key, basestring), \
            "Non-string key " + repr(key) + " in parameters."
        try:
            header[key]
        except Exception, exc:
            raise ValueError("Can't fetch mapping key " + repr(key) + 
                             " from parameters: " + repr(str(exc)))
        assert isinstance(header[key], (basestring, float, int, bool)), \
            "Parameter " + repr(key) + " isn't a string, float, int, or bool."
    
def check_reftypes(reftypes):
    """Make sure reftypes is a sequence of string identifiers."""
    assert isinstance(reftypes, (list, tuple, type(None))), \
        "reftypes must be a list or tuple of strings, or sub-class of those."
    if reftypes is not None:
        for reftype in reftypes:
            assert isinstance(reftype, basestring), \
                "each reftype must be a string, .e.g. biasfile or darkfile."
                
def check_context(context):
    """Make sure `context` is a pipeline mapping."""
    if context is None:
        return
    assert isinstance(context, basestring) and context.endswith(".pmap"), \
                "context should specify a pipeline mapping, .e.g. hst_0023.pmap"

# ============================================================================

def local_bestrefs(parameters, reftypes, context, ignore_cache=False):
    """Perform bestref computations locally,  contacting the network only to
    obtain references or mappings which are not already cached locally.
    In the case of the default "auto" mode,  assuming it has an up-to-date client
    CRDS will only use the server for status and to transfer files.
    """
    log.verbose("Computing best references locally.")
    # Make sure pmap_name is actually present in the local machine's cache.
    # First assume the context files are already here and try to load them.   
    # If that fails,  attempt to get them from the network, then load them.
    try:
        if ignore_cache:
            raise IOError("explicitly ignoring cache.")
        pmap = rmap.get_cached_mapping(context)
        log.verbose("Using cached context", srepr(context))
    except IOError, exc:
        log.verbose("Caching mapping files:", srepr(exc))
        try:
            light_client.dump_mappings(context, ignore_cache=ignore_cache)
        except crds.CrdsError, exc:
            raise crds.CrdsNetworkError("Network failure caching mapping files: " + str(exc))
        pmap = rmap.get_cached_mapping(context)
    # Finally do the best refs computation using pmap methods from local code.
    min_header = pmap.minimize_header(parameters)
    bestrefs = pmap.get_best_references(min_header, reftypes)
    return bestrefs

# ============================================================================

# Because get_processing_mode is a cached function,  it's results will not
# change after the first call without some special action.

@utils.cached
def get_processing_mode(observatory, context):
    """Return the processing mode (local, remote) and the server information
    including the observatory and operational context.   Map mode 'auto' onto
    'local' or 'remote' depending on client s/w version status.
    """
    try:
        info = light_client.get_server_info()
    except light_client.CrdsError:
        log.warning("Error contacting CRDS server %s.  Attempting off-line mode.  References may be sub-optimal." % \
                    light_client.get_crds_server())
        info = load_server_info(observatory)
        connected = False
    else:
        cache_server_info(observatory, info)  # save locally
        connected = True
    mode = config.get_crds_processing_mode()
    obsolete = local_version_obsolete(info)
    if mode == "auto":
        effective_mode = "remote" if connected and obsolete else "local"
    else:
        effective_mode = mode
    if mode == "remote" and not connected:
        raise crds.CrdsError("Can't compute 'remote' best references while off-line.  Set CRDS_MODE to 'local' or 'auto'.")
    if effective_mode == "local" and obsolete:
        log.warning("Computing bestrefs locally with obsolete client.   Recommended references may be sub-optimal.")
    new_context = str(context if context else info["operational_context"])
    return effective_mode, new_context

def minor_version(vers):
    """Strip the revision number off of `vers` and conver to float.
     e.g. "1.1.7"  --> 1.1
     """
    return float(".".join(vers.split(".")[:2]))
 
def local_version_obsolete(info):
    """Extract the CRDS server version from `info` and compare it to the minor
    version number of the CRDS client,  e.g. 1.2 vs. 1.1.
    """
    server_version = minor_version(info["crds_version"]["str"])
    client_version = minor_version(crds.__version__)
    obsolete = client_version < server_version
    log.verbose("CRDS client version=", srepr(client_version),
                " server version=", srepr(server_version),
                " client is ", "obsolete" if obsolete else "up-to-date", sep="")
    return obsolete
# ============================================================================

def cache_server_info(observatory, info):
    """Write down the server `info` dictionary to help configure off-line use."""
    server_config = config.get_crds_config_path() + "/" + observatory + "/server_config"
    try:
        utils.ensure_dir_exists(server_config)
        with open(server_config, "w+") as file_:
            file_.write(pprint.pformat(info))
    except IOError, exc:
        log.warning("Couldn't save CRDS server info:", repr(exc), "offline mode won't work.")
 
def load_server_info(observatory):
    """Return last connected server status to help configure off-line use."""
    server_config = config.get_crds_config_path() + "/" + observatory + "/server_config"
    log.verbose("Loading CRDS context and server s/w version from", repr(server_config))
    try:
        with open(server_config) as file_:
            info = compat.literal_eval(file_.read())
    except IOError, exc:
        raise crds.CrdsError("Off-line and error with cached server info: " + str(exc))
    return info

# ============================================================================

def srepr(obj):
    """Return the repr() of the str() of obj"""  
    return repr(str(obj))

# ============================================================================

import crds # for __version__,  circular dependency.

