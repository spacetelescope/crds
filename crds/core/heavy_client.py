"""This module implements a number of cache oriented top level interfaces
including getreferences(), getrecommendations().

The "light" client is defined in the crds.client package and is entirely
dependent on the server for computing best references.  The "light" client has
minimal dependencies on the core library, generally just a Python interface to
JSONRPC web services.

In contrast, the "heavy" client defined here provides a number of advanced
features which depend on a full installation of the core library and manage
and utilize the CRDS cache,  particularly as it pertains to best refs.

Some of the features are:

1. The ability to compute best references locally as a baseline behavior.

2. Automatic demand-based cache management for bestrefs, This includes
automatically syncing required rules and references when enabled.

3. Logging and "firewalling" for incoming parameters on the fundamental
bestrefs interface, getreferences(), particularly as it pertains to integration
with JWST CAL code.

4. The ability to record the last operational context and use it when the
server cannot be contacted.

5. The ability to define the context based on an env var.

6. The ability to fall back to pre-installed contexts if no context is defined
through the network, parameter, or environment variable mechanisms.

7. Implementation of bad files handling,  resulting in an exception or warning
when bad rules or references are used anyway.

8. Implementation of context pickling.

9. Translation of symbolic contexts where used (e.g. jwst-edit
vs. jwst_0442.pmap).

10. Features related to minimizing or eliminating communication with the CRDS
server via caching.

The original concept of the CRDS cache was to dynamically update and operate in
a connected state with the CRDS server.  While that remains a viable mode of
operation for end users, current archive pipelines operate entirely from their
CRDS cache during calibrations, connecting to the server only during serial
cache sync operations.  This module provides some of the fall back mechanisms
necessary for operating without a server connection at all.
"""
import os
import pprint
import ast
import traceback
import uuid
import fnmatch
import pickle

# ============================================================================

from . import rmap, log, utils, config
from .constants import ALL_OBSERVATORIES
from .log import srepr
from .exceptions import CrdsError, CrdsBadRulesError, CrdsBadReferenceError, CrdsConfigError, CrdsDownloadError
from crds.client import api

# import crds  # forward

# ============================================================================

__all__ = [
    "getreferences", "getrecommendations",
    "get_config_info", "update_config_info", "load_server_info",
    "get_processing_mode", "get_context_name",
    "version_info",
    "get_bad_mappings_in_context", "list_mappings",
]

# ============================================================================

# !!!!! interface to jwst.stpipe.crds_client
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

        # for var in os.environ:
        #    if var.upper().startswith("CRDS"):
        #        log.verbose(var, "=", repr(os.environ[var]))
        log.verbose("CRDS_PATH =", os.environ.get("CRDS_PATH", "UNDEFINED"))
        log.verbose("CRDS_SERVER_URL =", os.environ.get("CRDS_SERVER_URL", "UNDEFINED"))

        check_observatory(observatory)
        parameters = check_parameters(parameters)
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
        instrument = utils.header_to_instrument(parameters)
        warn_bad_context(observatory, final_context, instrument)
        warn_bad_references(observatory, bestrefs)

    return final_context, bestrefs

# ============================================================================

# This is cached because it should only produce output *once* per program run.
@utils.cached
def warn_bad_context(observatory, context, instrument=None):
    """Issue a warning if `context` is a known bad file, or contains bad files."""
    bad_contained = get_bad_mappings_in_context(observatory, context, instrument)
    if bad_contained:
        msg = log.format("Final context", repr(context),
                         "is marked as scientifically invalid based on:", log.PP(bad_contained))
        if config.ALLOW_BAD_RULES:
            log.warning(msg)
        else:
            raise CrdsBadRulesError(msg)

# This is cached because it can be called multiple times for a single dataset,
# both within warn_bad_mappings and elsewhere.
@utils.cached
def get_bad_mappings_in_context(observatory, context, instrument=None):
    """Return the list of bad files (defined by the server) contained by `context`."""
    try:
        check_context = rmap.get_cached_mapping(context).get_imap(instrument).basename
    except Exception:
        check_context = context
    bad_mappings = get_config_info(observatory).bad_files_set
    context_mappings = mapping_names(check_context)
    return sorted(list(context_mappings & bad_mappings))

def mapping_names(context):
    """Return the full set of mapping names associated with `context`,  compute locally if possible,
    else consult server.
    """
    try:
        mapping = get_symbolic_mapping(context)
        contained_mappings = mapping.mapping_names()
    except Exception:
        contained_mappings = api.get_mapping_names(context)
    return set(contained_mappings)

# ============================================================================

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

# ============================================================================

def check_observatory(observatory):
    """Make sure `observatory` is valid."""
    assert observatory in ALL_OBSERVATORIES

def check_parameters(header):
    """Make sure dict-like `header` is a mapping from strings to simple types.
    Drop non-simple values with a verbose warning.
    """
    header = dict(header)
    keys = list(header.keys())
    for key in keys:
        assert isinstance(key, str), \
            "Non-string key " + repr(key) + " in parameters."
        try:
            header[key]
        except Exception as exc:
            raise ValueError("Can't fetch mapping key", repr(key),
                             "from parameters:", repr(str(exc))) from exc
        if not isinstance(header[key], (str, float, int, bool)):
            log.verbose_warning("Parameter " + repr(key) + " isn't a string, float, int, or bool.   Dropping.", verbosity=90)
            del header[key]
    return header

def check_reftypes(reftypes):
    """Make sure reftypes is a sequence of string identifiers."""
    assert isinstance(reftypes, (list, tuple, type(None))), \
        "reftypes must be a list or tuple of strings, or sub-class of those."
    if reftypes is not None:
        for reftype in reftypes:
            assert isinstance(reftype, str), \
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
        return hv_best_references(context, parameters, reftypes)
    except IOError as exc:
        log.verbose("Caching mapping files for context", srepr(context))
        try:
            api.dump_mappings(context, ignore_cache=ignore_cache)
        except CrdsError as exc:
            traceback.print_exc()
            raise CrdsDownloadError(
                "Failed caching mapping files:", str(exc)) from exc
        return hv_best_references(context, parameters, reftypes)

# =============================================================================

def hv_best_references(context_file, header, include=None, condition=True):
    """Compute the best references for `header` for the given CRDS
    `context_file`.   This is a local computation using local rmaps and
    CPU resources.   If `include` is None,  return results for all
    filekinds appropriate to `header`,  otherwise return only those
    filekinds listed in `include`.
    """
    ctx = get_symbolic_mapping(context_file, cached=True)
    conditioned = utils.condition_header(header) if condition else header
    if include is None:
        # requires conditioned header,  or compatible header
        include = set(ctx.locate.header_to_reftypes(conditioned, context_file))
        ctx_filekinds = set(ctx.get_filekinds(conditioned))
        include = list(ctx_filekinds & include)
    minheader = ctx.minimize_header(conditioned)
    log.verbose("Bestrefs header:\n", log.PP(minheader))
    return ctx.get_best_references(minheader, include=include)

# ============================================================================

# !!!!! interface to jwst.stpipe.crds_client

# Because get_processing_mode is a cached function,  it's results will not
# change after the first call without some special action.

@utils.cached
def get_processing_mode(observatory, context=None):
    """Return the processing mode (local, remote) and the .pmap name to be used
    for best references selections.
    """
    info = get_config_info(observatory)

    final_context = get_final_context(info, context)

    return info.effective_mode, final_context

@utils.cached
def get_context_name(observatory, context=None):
    """Return the .pmap name of the default context based on:

    1. literal definitiion in `context` (jwst_0001.pmap)
    2. symbolic definition in `context` (jwst-operational or jwst-edit)
    3. date-based definition in `context` (jwst-2017-01-15T00:05:00)
    4. CRDS_CONTEXT env var override

    Symbolic and date-based contexts may require definition of CRDS_SERVER_URL
    to enable server-side translations of the symbolic names.
    """
    return get_processing_mode(observatory, context)[1]

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
        log.verbose("Using reference file selection rules", srepr(input_context), "defined by", info.status + ".")
    final_context = translate_date_based_context(input_context, info.observatory)
    return final_context

def translate_date_based_context(context, observatory=None):
    """Check to see if `input_context` is based upon date rather than a context filename.  If it's
    just a filename,  return it.  If it's a date spec,  ask the server to interpret the date into
    a context filename.   If it's a date spec and not `connected`,  raise an exception.
    """
    if config.is_mapping(context):
        return context

    if observatory is None:
        for observatory in ALL_OBSERVATORIES:
            if context.startswith(observatory):
                break
        else:
            raise CrdsError("Cannot determine observatory to translate mapping '{}'".format(context))

    info = get_config_info(observatory)

    if context == info.observatory + "-operational":
        return info["operational_context"]
    elif context == info.observatory + "-edit":
        return info["edit_context"]
    elif context == info.observatory + "-versions":
        return info["versions_context"]

    if not info.connected:
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
    def __init__(self, *args, **keys):
        self.status = None
        self.connected = None
        super(ConfigInfo, self).__init__(*args, **keys)

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
    if info.observatory != observatory:
        raise CrdsConfigError(
            "CRDS server at", repr(api.get_crds_server()),
            "is inconsistent with observatory", repr(observatory) + ".",
            "You may be configured for the wrong project.  "
            "Check CRDS_SERVER_URL and CRDS_OBSERVATORY "
            "environment settings.  See https://jwst-crds.stsci.edu/docs/cmdline_bestrefs/ (JWST) "
            "or https://hst-crds.stsci.edu/docs/cmdline_bestrefs/ (HST) for information on configuring CRDS.")
    return info

@utils.cached # effectively a "once" directive
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
            mode = "w+" if isinstance(contents, str) else "wb+"
            with open(temp_path, mode) as file_:
                file_.write(contents)
            os.rename(temp_path, replace_path)
        except Exception as exc:
            log.verbose_warning("CACHE Failed writing", repr(replace_path),
                                ":", fail_warning, ":", repr(exc))
    else:
        log.verbose("CACHE Skipped update of readonly", repr(replace_path), ":", fail_warning)

def load_server_info(observatory):
    """Return last connected server status to help configure off-line use."""
    with log.fatal_error_on_exception("CRDS server connection and cache load FAILED.  Cannot continue.\n"
                         " See https://hst-crds.stsci.edu/docs/cmdline_bestrefs/ or https://jwst-crds.stsci.edu/docs/cmdline_bestrefs/\n"
                         " for more information on configuring CRDS,  particularly CRDS_PATH and CRDS_SERVER_URL."):
        server_config = config.get_uri("server_config")
        if server_config == "none":
            server_config = config.locate_config("server_config", observatory)
        config_data = utils.get_uri_content(server_config)
        info = ConfigInfo(ast.literal_eval(config_data))
        info.status = "cache"
        return info

# XXXX Careful with version string length here, FITS has a 68 char limit which degrades to CONTINUE records
# XXXX which cause problems for other systems.
def version_info():
    """Return CRDS checkout URL and revision,  client side."""
    import crds
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
        parkeys = get_symbolic_mapping(context).get_required_parkeys()
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

def get_symbolic_mapping(
    mapping, observatory=None, cached=True, use_pickles=None, save_pickles=None, **keys):
    """Return a loaded mapping object,  first translating any date based or
    named contexts into a more primitive serial number only mapping name.

    This is basically the symbolic form of get_pickled_mapping().  Since the default
    setting of 'cached' is True,  it performs much like crds.get_cached_mapping()
    but also accepts abstract or date-based names.

    Typically the latest files submitted on the server but not yet operational:

    >> get_symbolic_mapping("jwst-edit")
    PipelineMapping('jwst_0153.pmap')

    What's running in the pipeline now:

    >> get_symbolic_mapping("jwst-operational")
    PipelineMapping('jwst_0126.pmap')

    What was running for a particular instrument, type, and date:

    >> get_symbolic_mapping("jwst-miri-flat-2015-01-01T00:20:05")
    ReferenceMapping('jwst_miri_flat_0012.rmap')

    WARNING: this is a high level feature which *requires* a server connection
    to interpret the symbolic name into a primitive name.
    """
    abs_mapping = translate_date_based_context(mapping, observatory)
    return get_pickled_mapping(   # reviewed
        abs_mapping, cached=cached, use_pickles=use_pickles, save_pickles=save_pickles, **keys)


# ============================================================================

@utils.cached   # check callers for .uncached before removing.
def get_pickled_mapping(mapping, cached=True, use_pickles=None, save_pickles=None, **keys):
    """Load CRDS mapping from a context pickle if possible, nominally as a file
    system optimization to prevent 100+ file reads.
    """
    assert config.is_mapping(mapping) or isinstance(mapping, rmap.Mapping), \
        "`mapping` must be a literal CRDS mapping name, not a date-based context specification."
    if use_pickles is None:
        use_pickles = config.USE_PICKLED_CONTEXTS
    if save_pickles is None:
        save_pickles = config.AUTO_PICKLE_CONTEXTS
    if use_pickles and config.is_simple_crds_mapping(mapping):
        try:
            loaded = load_pickled_mapping(mapping)
        except Exception:
            loaded = rmap.asmapping(mapping, cached=cached, **keys)
            if save_pickles:
                save_pickled_mapping(mapping, loaded)
    else:
        loaded = rmap.asmapping(mapping, cached=cached, **keys)
    return loaded

def load_pickled_mapping(mapping):
    """Load the pickle for `mapping` where `mapping` is canonically named and
    located in the CRDS cache.

    Although pickles for sub-mappings may exist, only the highest level pickle
    in the hierarchy is read.  In general pickles for sub-mappings should not
    exist because of storage waste.
    """
    pickle_uri = config.get_uri(mapping + ".pkl")
    if pickle_uri == "none":
        pickle_uri = config.locate_pickle(mapping)
    pickled = utils.get_uri_content(pickle_uri, mode="binary")
    loaded = pickle.loads(pickled)
    log.info("Loaded pickled context", repr(mapping))
    return loaded

def save_pickled_mapping(mapping, loaded):
    """Save live mapping `loaded` as a pickle under named based on `mapping` name."""
    pickle_file = config.locate_pickle(mapping)
    if not utils.is_writable(pickle_file):  # Don't even bother pickling
        log.verbose("Pickle file", repr(pickle_file), "is not writable,  skipping pickle save.")
        return
    with log.verbose_warning_on_exception("Failed saving pickle for", repr(mapping), "to", repr(pickle_file)):
        loaded.force_load()
        pickled = pickle.dumps(loaded)
        cache_atomic_write(pickle_file, pickled, "CONTEXT PICKLE")
        log.info("Saved pickled context", repr(pickle_file))

def remove_pickled_mapping(mapping):
    """Delete the pickle for `mapping` from the CRDS cache."""
    pickle_file = config.locate_pickle(mapping)
    if not utils.is_writable(pickle_file):  # Don't even bother pickling
        log.verbose("Pickle file", repr(pickle_file), "is not writable,  skipping pickle remove.")
        return
    if not os.path.exists(pickle_file):
        log.verbose("Pickl file", repr(pickle_file), "does not exist,  skipping pickle remove.")
        return
    with log.warn_on_exception("Failed removing pickle for", repr(mapping)):
        os.remove(pickle_file)
        log.info("Removed pickle for context", repr(pickle_file))
