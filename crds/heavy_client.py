"""This module implements the "heavy" getreferences() top level interface.  

The "light" client is defined in the crds.client package and is entirely
dependent on the server for computing best references.  The advantage of the
"light" client is that it is comparatively simple code that has shallower
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

6. The ability to define the context based on an env var.

7. The ability to fall back to pre-installed contexts if no context is defined
through the network, parameter, or environment variable mechanisms.
"""
import os
import pprint
import glob
import ast
import traceback

import crds.client as light_client
from . import rmap, log, utils, config

__all__ = ["getreferences", "getrecommendations"]

# ============================================================================

# !!!!! interface to jwst_lib.stpipe.crds_client
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
    final_context, bestrefs = _initial_recommendations("getreferences",
        parameters, reftypes, context, ignore_cache, observatory)
    
    # Attempt to cache the recommended references,  which unlike dump_mappings
    # should work without network access if files are already cached.
    best_refs_paths = light_client.cache_references(
        final_context, bestrefs, ignore_cache=ignore_cache)
    
    return best_refs_paths

def getrecommendations(parameters, reftypes=None, context=None, ignore_cache=False,
                       observatory="jwst"):
    """
    getrecommendations() returns the best references for the specified `parameters`
    and pipeline `context`.   Unlike getreferences(),  getrecommendations() does
    not attempt to cache the files locally.
        
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
    
    Returns { reftype : bestref_basename }
    
      returns a mapping from types requested in `reftypes` to the path for each
      cached reference file.
    """
    _final_context, bestrefs = _initial_recommendations("getrecommendations",
        parameters, reftypes, context, ignore_cache, observatory)    

    return bestrefs

def _initial_recommendations(
        name, parameters, reftypes=None, context=None, ignore_cache=False, observatory="jwst"):
    """shared logic for getreferences() and getrecommendations()."""
    
    log.verbose(name + "() CRDS version: ", version_info())
    log.verbose(name + "() server:", light_client.get_crds_server())
    log.verbose(name + "() observatory:", observatory)
    log.verbose(name + "() parameters:\n", log.PP(parameters))
    log.verbose(name + "() reftypes:", reftypes)
    log.verbose(name + "() context:", repr(context))
    log.verbose(name + "() ignore_cache:", ignore_cache)
    
    for var in os.environ:
        if var.upper().startswith("CRDS"):
            log.verbose(var, "=", repr(os.environ[var]))

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
        bestrefs = light_client.get_best_references(final_context, parameters, reftypes=reftypes)
    
    warn_bad_context(observatory, final_context)
    warn_bad_references(observatory, bestrefs)
        
    return final_context, bestrefs

# ============================================================================

def warn_bad_context(observatory, context):
    """Issue a warning if `context` is a known bad file, or contains bad files."""
    bad_contained = get_bad_mappings_in_context(observatory, context)
    if bad_contained:
        log.warning("Final context", repr(context), 
                    "is bad or contains bad rules.  It may produce scientifically invalid results.")
        log.verbose("Final context", repr(context), "contains bad files:", repr(bad_contained))

def get_bad_mappings_in_context(observatory, context):
    """Return the list of bad files (defined by the server) contained by `context`."""
    mode, _jnk = get_processing_mode(observatory, context)
    if mode == "remote":
        contained_mappings = set(light_client.get_mapping_names(context))
    else:
        mapping = crds.get_cached_mapping(context)
        contained_mappings = set(mapping.mapping_names())
    bad_mappings = get_config_info(observatory).bad_files_set
    return sorted(list(contained_mappings.intersection(bad_mappings)))

def warn_bad_references(observatory, bestrefs):
    """Scan `bestrefs` mapping { filekind : bestref_path, ...} for bad references."""
    bad_files = get_config_info(observatory).bad_files_set
    base_bestrefs = { reftype:os.path.basename(ref) for (reftype, ref) in bestrefs.items() }
    for reftype, ref in base_bestrefs.items():
        if ref in bad_files:
            log.warning("Recommended reference", repr(ref), "for type", repr(reftype), 
                        "is a known bad file.  It may produce scientifically invalid results.")
    
# ============================================================================
def check_observatory(observatory):
    """Make sure `observatory` is valid."""
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
    """Make sure `context` is a pipeline or instrument mapping."""
    if context is None:
        return
    assert config.is_mapping_spec(context), \
                "context should specify a pipeline or instrument mapping, .e.g. hst_0023.pmap,  or a date based spec, e.g. hst-2018-01-21T12:32:05"

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
        _pmap = rmap.get_cached_mapping(context)
        log.verbose("Loading context file", srepr(context),"from cache.")
    except IOError, exc:
        log.verbose("Caching mapping files for context", srepr(context))
        try:
            light_client.dump_mappings(context, ignore_cache=ignore_cache)
        except crds.CrdsError, exc:
            traceback.print_exc()
            raise crds.CrdsNetworkError("Failed caching mapping files: " + str(exc))
    # Finally do the best refs computation using pmap methods from local code.
    bestrefs = rmap.get_best_references(context, parameters, reftypes)
    return bestrefs

# ============================================================================

# !!!!! interface to jwst_lib.stpipe.crds_client

# Because get_processing_mode is a cached function,  it's results will not
# change after the first call without some special action.

@utils.cached
def get_processing_mode(observatory, context=None):
    """Return the processing mode (local, remote) and the .pmap name to be used
    for best references selections.
    """
    info = get_config_info(observatory)
        
    effective_mode = get_effective_mode(info.connected, info.crds_version["str"])

    final_context = get_final_context(info, context)

    return effective_mode, final_context

def get_effective_mode(connected,  server_version):
    """Based on environment CRDS_MODE,  connection status,  server s/w version, 
    and the installed client s/w version,  determine whether best refs should be
    computed locally or on the server.
    
    returns 'local' or 'remote'
    """
    mode = config.get_crds_processing_mode()  # local, remote, auto
    obsolete = local_version_obsolete(server_version)
    if mode == "auto":
        effective_mode = "remote" if (connected and obsolete) else "local"
    else:
        effective_mode = mode   # explicitly local or remote
    if effective_mode == "remote" and not connected:
        raise crds.CrdsError("Can't compute 'remote' best references while off-line.  Set CRDS_MODE to 'local' or 'auto'.")
    if effective_mode == "local" and obsolete:
        log.warning("Computing bestrefs locally with obsolete client.   Recommended references may be sub-optimal.")
    return effective_mode

def get_final_context(info, context):
    """Based on env CRDS_CONTEXT, the `context` parameter, and the server's reported,
    cached, or defaulted `operational_context`,  choose the pipeline mapping which 
    defines the reference selection rules.
    
    Returns   a .pmap name
    """
    env_context = config.get_crds_env_context()
    if context and not context.endswith("-operational"):    # context parameter trumps all, <observatory>-operational is default
        input_context = context
        log.verbose("Using reference file selection rules", srepr(input_context), "defined by caller.")
        info.status = "getreferences() context parameter"
    elif env_context:
        input_context = env_context
        log.verbose("Using reference file selection rules", srepr(input_context), 
                    "defined by environment CRDS_CONTEXT.")
        info.status = "env var CRDS_CONTEXT"
    else:
        input_context = str(info.operational_context)
        log.verbose("Using reference selection rules", srepr(input_context), "defined by", info.status + ".")
    final_context = translate_date_based_context(info, input_context)
    return final_context

def translate_date_based_context(info, context):
    """Check to see if `input_context` is based upon date rather than a context filename.  If it's 
    just a filename,  return it.  If it's a date spec,  ask the server to interpret the date into 
    a context filename.   If it's a date spec and not `connected`,  raise an exception.
    """
    if config.is_mapping(context):
        return context
    else:
        if not info.connected:
            raise crds.CrdsError("Specified CRDS context by date and CRDS server is not reachable.")
        try:
            translated = light_client.get_context_by_date(context, observatory=info.observatory)
        except Exception, exc:
            log.error("Failed to translate date based context", repr(context), ":", str(exc))
            raise
        log.verbose("Date based context spec", repr(context), "translates to", repr(translated) + ".", verbosity=20)
        return translated

def local_version_obsolete(server_version):
    """Compare `server_version` to the minor version number of the locally 
    installed CRDS client,  e.g. 1.2 vs. 1.1.
    """
    server_version = minor_version(server_version)
    client_version = minor_version(crds.__version__)
    obsolete = client_version < server_version
    log.verbose("CRDS client version=", srepr(client_version),
                " server version=", srepr(server_version),
                " client is ", srepr("obsolete" if obsolete else "up-to-date"),
                sep="")
    return obsolete

def minor_version(vers):
    """Strip the revision number off of `vers` and conver to float.
     e.g. "1.1.7"  --> 1.1
     """
    return float(".".join(vers.split(".")[:2]))
 
# ============================================================================

class ConfigInfo(utils.Struct):
    """Encapsulate CRDS cache config info."""
    @property
    def bad_files_set(self):
        """Return the set of references and mappings which are considered scientifically invalid."""
        return set(self.get("bad_files", "").split())

@utils.cached
def get_config_info(observatory):
    """Get the operational context and server s/w version from (in order of priority):
    
    1. The server.
    2. The cache from a prior server access.
    3. The basic CRDS installation.
    
    Return ConfigInfo
    """
    try:
        info = ConfigInfo(light_client.get_server_info())
        info.status = "server"
        info.connected = True
        log.verbose("Connected to server at", repr(light_client.get_crds_server()))
    except light_client.CrdsError:
        log.verbose_warning("Couldn't contact CRDS server:", srepr(light_client.get_crds_server()))
        info = load_server_info(observatory)
        info.connected = False
    if info.connected:
        cache_server_info(info, observatory)  # save locally
    info.readonly = config.get_cache_readonly()
    return info

def cache_server_info(info, observatory):
    """Write down the server `info` dictionary to help configure off-line use."""
    if config.get_cache_readonly():
        log.verbose("Readonly cache, skipping cache config write.", verbosity=70)
        return
    path = config.get_crds_config_path(observatory)
    try:
        server_config = os.path.join(path, "server_config")
        utils.ensure_dir_exists(server_config)
        with open(server_config, "w+") as file_:
            file_.write(pprint.pformat(info))
    except Exception, exc:
        log.verbose_warning("Couldn't save CRDS server info:", repr(exc))
    try:
        bad_files = os.path.join(path, "bad_files.txt")
        utils.ensure_dir_exists(bad_files)
        bad_files_lines = "\n".join(info.get("bad_files","").split()) + "\n"
        with open(bad_files, "w+") as file_:
            file_.write(bad_files_lines)
    except Exception, exc:
        log.verbose_warning("Couldn't save CRDS bad files list:", repr(exc))
        
def load_server_info(observatory):
    """Return last connected server status to help configure off-line use."""
    server_config = os.path.join(config.get_crds_config_path(observatory), "server_config")
    try:
        with open(server_config) as file_:
            info = ConfigInfo(ast.literal_eval(file_.read()))
        info.status = "cache"
        log.verbose_warning("Loading server context and version info from cache '%s'." % server_config, 
                            "References may be sub-optimal.")
    except IOError:
        log.verbose_warning("Couldn't load cached server info from '%s'." % server_config,
                            "Using pre-installed CRDS context.  References may be sub-optimal." )
        info = get_installed_info(observatory)
    return info

def get_installed_info(observatory):
    """Make up a bare-bones server info dictionary to define the pipeline context
    using pre-installed mappings for `observatory`.   Choose the most recent
    pipeline context as the default operational context as determined by the 
    context numbering scheme,  highest serial number wins.
    
    These are the ultimate fall-back settings for CRDS in serverless-mode and 
    assume the mappings are pre-installed and/or visible on the Central Store.
    
    By providing a config directory and server config file,  the results of this
    code should not be used in so-called "server-less mode".   This code is the
    fallback for remote users when network connectivity has failed and they do
    not *already* have cached server config (and mappings).
    """
    try:
        # lexical sort of pmap names yields most recent (highest numbered) last.
        os.environ["CRDS_MAPPATH"] = crds.__path__[0] + "/cache/mappings"
        where = config.locate_mapping("*.pmap", observatory)
        pmap = os.path.basename(sorted(glob.glob(where))[-1])
        log.warning("CRDS cache failure,  using pre-installed mappings at", repr(where),
                    "and highest numbered pipeline context", repr(pmap), "as default. Bad file checking is disabled.")
    except IndexError, exc:
        raise crds.CrdsError("Configuration or install error.  Can't find any .pmaps at " + 
                        repr(where) + " : " + str(exc))
    return ConfigInfo(
            edit_context = pmap,
            operational_context = pmap,
            observatory = observatory,
            bad_files = "",
            status = "s/w install",
            crds_version = dict( str="0.0.0"),
            last_synced = "Not connected and not cached,  using installed mappings only.",
            reference_url = "Not connected",
            mapping_url = "Not connected"
            )
    
# XXXX Careful with version string length here, FITS has a 68 char limit which degrades to CONTINUE records
# XXXX which cause problems for other systems.
def version_info():
    """Return CRDS checkout URL and revision."""
    try:
        from . import svn_version
        lines = svn_version.__full_svn_info__.strip().split("\n")
        svn = ", ".join([line for line in lines if line.startswith(("URL","Revision"))])
        svn = svn.replace("URL: ", "").replace("Revision: ", "")
        return crds.__version__ + ", " + svn
    except Exception:
        return "unknown"
# ============================================================================

def srepr(obj):
    """Return the repr() of the str() of obj"""  
    return repr(str(obj))

# ============================================================================

import crds # for __version__,  circular dependency.

