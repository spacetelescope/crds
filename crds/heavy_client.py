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
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import os
import pprint
import glob
import ast
import traceback
import uuid
import fnmatch 

from . import rmap, log, utils, config
from crds.client import api
from crds.log import srepr
from crds.exceptions import CrdsError, CrdsBadRulesError, CrdsBadReferenceError, CrdsNetworkError
from crds import python23

__all__ = ["getreferences", "getrecommendations"]

# ============================================================================

# ============================================================================

# !!!!! interface to jwst_lib.stpipe.crds_client
def getreferences(parameters, reftypes=None, context=None, ignore_cache=False,
                  observatory="jwst", fast=False):
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
       
    fast            bool
    
      If fast is True, skip verbose output, parameter screening, implicit config update, and bad reference checking.
    
    Returns { reftype : cached_bestref_path }
    
      returns a mapping from types requested in `reftypes` to the path for each
      cached reference file.
    """
    final_context, bestrefs = _initial_recommendations("getreferences",
        parameters, reftypes, context, ignore_cache, observatory, fast)
    
    # Attempt to cache the recommended references,  which unlike dump_mappings
    # should work without network access if files are already cached.
    best_refs_paths = api.cache_references(
        final_context, bestrefs, ignore_cache=ignore_cache)
    
    return best_refs_paths

def getrecommendations(parameters, reftypes=None, context=None, ignore_cache=False,
                       observatory="jwst", fast=False):
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
    
    fast            bool
    
      If fast is True, skip verbose output, parameter screening, implicit config update, and bad reference checking.
    
    Returns { reftype : bestref_basename }
    
      returns a mapping from types requested in `reftypes` to the path for each
      cached reference file.
    """
    _final_context, bestrefs = _initial_recommendations("getrecommendations",
        parameters, reftypes, context, ignore_cache, observatory, fast)    

    return bestrefs

def _initial_recommendations(
        name, parameters, reftypes=None, context=None, ignore_cache=False, observatory="jwst", fast=False):

    """shared logic for getreferences() and getrecommendations()."""

    if not fast:
        log.verbose("="*120)
        log.verbose(name + "() CRDS version: ", version_info())
        log.verbose(name + "() server:", api.get_crds_server())
        log.verbose(name + "() observatory:", observatory)
        log.verbose(name + "() parameters:\n", log.PP(parameters), verbosity=65)
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

    log.verbose("Final effective context is", repr(final_context))

    if mode == "local":
        log.verbose("Computing best references locally.")
        bestrefs = local_bestrefs(
            parameters, reftypes=reftypes, context=final_context, ignore_cache=ignore_cache)
    else:
        log.verbose("Computing best references remotely.")
        bestrefs = api.get_best_references(final_context, parameters, reftypes=reftypes)
    
    if not fast:   
        # nominally fast=True (this is skipped) in crds.bestrefs,  used for HST and reprocessing
        # because bestrefs sreprocessing determinations for two contexts which run on 100's of 
        # thousands of datasets and should only report bad files once and only when arising from 
        # the new vs. the old context.
        update_config_info(observatory)
        log.verbose(name + "() results:\n", log.PP(bestrefs), verbosity=65)
        warn_bad_references(observatory, bestrefs)
    
    return final_context, bestrefs

# ============================================================================

def warn_bad_context(observatory, context):
    """Issue a warning if `context` is a known bad file, or contains bad files."""
    bad_contained = get_bad_mappings_in_context(observatory, context)
    if bad_contained:
        msg = log.format("Final context", repr(context), 
                         "is marked as scientifically invalid based on:", log.PP(bad_contained))
        if config.ALLOW_BAD_RULES:
            log.warning(msg)
        else:
            raise CrdsBadRulesError(msg)

def warn_bad_references(observatory, bestrefs):
    """Scan `bestrefs` mapping { filekind : bestref_path, ...} for bad references."""
    for reftype, refpath in bestrefs.items():
        warn_bad_reference(observatory, reftype, refpath)

def warn_bad_reference(observatory, reftype, reference):
    """Return True IFF `reference` is in the set of scientifically invalid files for `observatory`.
    
    reference   the CRDS pathname or basename for a reference to check
    bad_files   None or a set of scientifically invalid files.
    
    """
    ref = os.path.basename(reference)
    bad_files = get_config_info(observatory).bad_files_set
    if ref in bad_files:
        msg = log.format("Recommended reference", repr(ref), "of type", repr(reftype), 
                         "is designated scientifically invalid.")
        if config.ALLOW_BAD_REFERENCES:
            log.warning(msg)
        else:
            raise CrdsBadReferenceError(msg)

def mapping_names(context):
    """Return the full set of mapping names associated with `context`,  compute locally if possible,
    else consult server.
    """
    try:
        mapping = crds.get_cached_mapping(context)
        contained_mappings = mapping.mapping_names()
    except IOError:
        contained_mappings = api.get_mapping_names(context)
    return set(contained_mappings)

def get_bad_mappings_in_context(observatory, context):
    """Return the list of bad files (defined by the server) contained by `context`."""
    bad_mappings = get_config_info(observatory).bad_files_set
    context_mappings = mapping_names(context)
    return sorted(list(context_mappings & bad_mappings))

# ============================================================================
def check_observatory(observatory):
    """Make sure `observatory` is valid."""
    assert observatory in ["hst", "jwst", "tobs"]

def check_parameters(header):
    """Make sure dict-like `header` is a mapping from strings to simple types."""
    header = dict(header)
    keys = list(header.keys())
    for key in keys:
        assert isinstance(key, python23.string_types), \
            "Non-string key " + repr(key) + " in parameters."
        try:
            header[key]
        except Exception as exc:
            raise ValueError("Can't fetch mapping key " + repr(key) + 
                             " from parameters: " + repr(str(exc)))
        if not isinstance(header[key], (python23.string_types, float, int, bool)):
            log.verbose_warning("Parameter " + repr(key) + " isn't a string, float, int, or bool.   Dropping.", verbosity=90)
            del header[key]

def check_reftypes(reftypes):
    """Make sure reftypes is a sequence of string identifiers."""
    assert isinstance(reftypes, (list, tuple, type(None))), \
        "reftypes must be a list or tuple of strings, or sub-class of those."
    if reftypes is not None:
        for reftype in reftypes:
            assert isinstance(reftype, python23.string_types), \
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
    # Make sure pmap_name is actually present in the local machine's cache.
    # First assume the context files are already here and try to load them.   
    # If that fails,  attempt to get them from the network, then load them.
    try:
        if ignore_cache:
            raise IOError("explicitly ignoring cache.")
        # Finally do the best refs computation using pmap methods from local code.
        return rmap.get_best_references(context, parameters, reftypes)
    except IOError as exc:
        log.verbose("Caching mapping files for context", srepr(context))
        try:
            api.dump_mappings(context, ignore_cache=ignore_cache)
        except CrdsError as exc:
            traceback.print_exc()
            raise CrdsNetworkError("Failed caching mapping files: " + str(exc))
        return rmap.get_best_references(context, parameters, reftypes)

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
        
    final_context = get_final_context(info, context)
    
    warn_bad_context(observatory, final_context)

    return info.effective_mode, final_context

def get_final_context(info, context):
    """Based on env CRDS_CONTEXT, the `context` parameter, and the server's reported,
    cached, or defaulted `operational_context`,  choose the pipeline mapping which 
    defines the reference selection rules.
    
    Returns   a .pmap name
    """
    env_context = config.get_crds_env_context()
    if context:  # context parameter trumps all, <observatory>-operational is default
        input_context = context
        log.verbose("Using reference file selection rules", srepr(input_context), "defined by caller.")
        info.status = "context parameter"
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
            if context == info.observatory + "-operational":
                return info["operational_context"]
            else:
                raise CrdsError("Specified CRDS context by date '{}' and CRDS server is not reachable.".format(context))
        try:
            translated = api.get_context_by_date(context, observatory=info.observatory)
        except Exception as exc:
            log.error("Failed to translate date based context", repr(context), ":", str(exc))
            raise
        log.verbose("Date based context spec", repr(context), "translates to", repr(translated) + ".", verbosity=80)
        return translated

# ============================================================================

class ConfigInfo(utils.Struct):
    """Encapsulate CRDS cache config info."""
    @property
    def bad_files_set(self):
        """Return the set of references and mappings which are considered scientifically invalid."""
        return set(self.bad_files_list)
    
    @property
    def effective_mode(self):
        """Based on environment CRDS_MODE,  connection status,  and server config force_remote_mode flag,
        determine whether best refs should be computed locally or on the server.   Simple unless 
        CRDS_MODE defaults to "auto" in which case the effective mode is "remote" when connected and
        the server sets force_remote_mode to True.
        
        returns 'local' or 'remote'
        """
        mode = config.get_crds_processing_mode()  # local, remote, auto
        if mode == "auto":
            eff_mode = "remote" if (self.connected and hasattr(self, "force_remote_mode") and self.force_remote_mode) else "local"
        else:
            eff_mode = mode   # explicitly local or remote
            if eff_mode == "remote" and not self.connected:
                raise CrdsError("Can't compute 'remote' best references while off-line.  Set CRDS_MODE to 'local' or 'auto'.")
            if eff_mode == "local" and self.force_remote_mode:
                log.warning("Computing bestrefs locally with obsolete client.   Recommended references may be sub-optimal.")
        return eff_mode

@utils.cached
def get_config_info(observatory):
    """Get the operational context and server s/w version from (in order of priority):
    
    1. The server.
    2. The cache from a prior server access.
    3. The basic CRDS installation.
    
    Return ConfigInfo
    """
    try:
        info = ConfigInfo(api.get_server_info())
        info.status = "server"
        info.connected = True
        log.verbose("Connected to server at", srepr(api.get_crds_server()))
        if info.effective_mode != "remote":
            if not config.writable_cache_or_verbose("Using cached configuration and default context."):
                info = load_server_info(observatory)
                info.status = "cache"
                info.connected = True
                log.verbose("Using CACHED CRDS reference assignment rules last updated on", repr(info.last_synced))
    except CrdsError as exc:
        if "serverless" not in api.get_crds_server():
            log.verbose_warning("Couldn't contact CRDS server:", srepr(api.get_crds_server()), ":", str(exc))
        info = load_server_info(observatory)
        info.status = "cache"
        info.connected = False
        log.verbose("Using CACHED CRDS reference assignment rules last updated on", repr(info.last_synced))
    return info

def update_config_info(observatory):
    """Write out any server update to the CRDS configuration information.
    Skip the update if: not connected to server, readonly cache, write protected config files.
    """
    if config.writable_cache_or_verbose("skipping config update."):
        info = get_config_info(observatory)
        if info.connected and info.effective_mode == "local":
            log.verbose("Connected to server and computing locally, updating CRDS cache config and operational context.")
            cache_server_info(info, observatory)  # save locally
        else:
            log.verbose("Not connected to CRDS server or operating in 'remote' mode,  skipping cache config update.", verbosity=65)

def cache_server_info(info, observatory):
    """Write down the server `info` dictionary to help configure off-line use."""
    path = config.get_crds_cfgpath(observatory)

    server_config_path = os.path.join(path, "server_config")
    cache_atomic_write(server_config_path, pprint.pformat(info), "SERVER INFO")

    # This is just a reference copy for debuggers,  the master is still the info file.
    bad_files_lines = "\n".join(info.bad_files_list)
    bad_files_path = os.path.join(path, "bad_files.txt")
    cache_atomic_write(bad_files_path, bad_files_lines, "BAD FILES LIST")

def cache_atomic_write(replace_path, contents, fail_warning):
    """Write string `contents` to cache file `replace_path` as an atomic action,
    issuing string `fail_warning` as a verbose exception warning if some aspect
    fails.   This is intended to support multiple processes using the CRDS
    cache in parallel,  as in parallel bestrefs in the pipeline.
    
    NOTE:  All writes to the cache configuration area should use this function
    to avoid concurrency issues with parallel processing.   Potentially this should
    be expanded to other non-config cache writes but is currently inappropriate
    for large data volumes (G's) since they're required to be in memory.
    """
    if utils.is_writable(replace_path, no_exist=True):
        try:
            log.verbose("CACHE updating:", repr(replace_path))
            utils.ensure_dir_exists(replace_path)
            temp_path = os.path.join(os.path.dirname(replace_path), str(uuid.uuid4()))
            with open(temp_path, "w+") as file_:
                file_.write(contents)
            os.rename(temp_path, replace_path)
        except Exception as exc:
            log.verbose_warning("CACHE Failed writing", repr(replace_path), 
                                ":", fail_warning, ":", repr(exc))
    else:
        log.verbose("CACHE Skipped update of readonly", repr(replace_path))

def load_server_info(observatory):
    """Return last connected server status to help configure off-line use."""
    server_config = os.path.join(config.get_crds_cfgpath(observatory), "server_config")
    with log.fatal_error_on_exception("CRDS server connection and cache load FAILED.  Cannot continue. "
                         " See https://hst-crds.stsci.edu/docs/cmdline_bestrefs/ or https://jwst-crds.stsci.edu/docs/cmdline_bestrefs/ for more information on configuring CRDS."):
        with open(server_config) as file_:
            info = ConfigInfo(ast.literal_eval(file_.read()))
        info.status = "cache"
    return info

# XXXX Careful with version string length here, FITS has a 68 char limit which degrades to CONTINUE records
# XXXX which cause problems for other systems.
def version_info():
    """Return CRDS checkout URL and revision,  client side."""
    try:
        from . import git_version
        branch = revision = "none"
        for line in git_version.__full_version_info__.strip().split("\n"):
            if line.startswith("branch:"):
                branch = line.split()[1].strip()
            if line.startswith("sha1"):
                revision = line.split()[1].strip()
        return crds.__version__ + ", " + branch + ", " + revision
    except Exception:
        return "unknown"

@utils.cached
def get_context_parkeys(context, instrument):
    """Return the parkeys required by `instrument` under `context`,  or the subset required by 
    the .rmap `context`,  presumably of `instrument`.  Unlike get_required_parkeys(),  uniformly
    returns a list regardless of context/mapping type.
    
    Returns [ matching_parameter, ... ]
    """
    try:
        parkeys = rmap.get_cached_mapping(context).get_required_parkeys()
    except Exception:
        parkeys = api.get_required_parkeys(context)
    if isinstance(parkeys, (list,tuple)):
        return list(parkeys)
    else:
        return list(parkeys[instrument])

# ============================================================================
def list_mappings(observatory, glob_pattern):
    """Optimized version of "list_mappings" server api function which leverages
    mappings list given in server_info api rather than separate rpc call.  
    """
    info = get_config_info(observatory)
    return sorted([mapping for mapping in info.mappings if fnmatch.fnmatch(mapping, glob_pattern)])

# ============================================================================

import crds # for __version__,  circular dependency.

