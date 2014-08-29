"""This module is the interface to CRDS configuration information.  Predominantly
it is used to define CRDS file cache paths and file location functions.
"""

import os
import os.path
import re

# ============================================================================

CRDS_DATA_CHUNK_SIZE = 2**23   # file download transfer block size, 8M.  HTTP, but maybe not RPC.

CRDS_CHECKSUM_BLOCK_SIZE = 2**23   # size of block for utils.checksum(), also 8M

# ===========================================================================

def env_to_bool(varname, default=False):
    """Convert the specified environment variable `varname` into a Python bool
    defaulting to `default` if it's not defined in os.environ.
    """
    env_str = os.environ.get(varname, default)
    return env_str_to_bool(varname, env_str)

def env_str_to_bool(varname, val):
    """Convert the boolean environment value string `val` to a Python bool
    on behalf of environment variable `varname`.
    """
    if val in ["False", "false", "True", "true"]:
        rval = bool(val.capitalize())
    elif val in ["F", "f", "0", False, 0]:
        rval = False
    elif val in ["T", "t", "1", True, 1]:
        rval = True
    else:
        raise ValueError("Invalid value " +  repr(val) + 
                         " for boolean env var " + repr(varname))
    return rval

def env_to_int(varname, default):
    """Convert the specified environment variable `varname` into a Python int
    defaulting to `default` if it's not defined in os.environ.
    """
    env_str = os.environ.get(varname, default)
    return env_str_to_int(varname, env_str)

def env_str_to_int(varname, val):
    """Convert environment variable decimal value `val` from `varname` to an int and return it."""
    try:
        return int(val)
    except Exception:
        raise ValueError("Invalid value for " + repr(varname) + 
                         " should have a decimal integer value but is " + repr(str(val)))

# ===========================================================================

DEFAULT_CRDS_DIR = "/grp/crds/cache"

def _clean_path(path):
    """Fetch `name` from the environment,  or use `default`.  Trim trailing /'s from
    the resulting path.
    """
    while path.endswith("/"):
        path = path[:-1]
    return path

def _std_cache_path(observatory, root_env, subdir):
    """Do standard interpretation of environment variables for CRDS cache component location.
    
    Evaluated in order,  with first definition winning:  e.g. for mappings
    
    CRDS_MAPPATH_SINGLE  -->   <env path for mappings>
    CRDS_MAPPATH         -->   <env path for mappings for both observatories> + / + <observatory>
    CRDS_PATH_SINGLE     -->   <env path for overall cache for one observatory> + "/mappings/"
    CRDS_PATH            -->   <env path for overall cache for all observatories> + "/mappings/" + <observatory>
    """
    if root_env + "_SINGLE" in os.environ:
        path = os.environ[root_env + "_SINGLE"]
    elif root_env in os.environ:
        path = os.path.join(os.environ[root_env], observatory)
    elif "CRDS_PATH_SINGLE" in os.environ:
        path = os.path.join(os.environ["CRDS_PATH_SINGLE"], subdir)
    elif "CRDS_PATH" in os.environ:
        path = os.path.join(os.environ["CRDS_PATH"], subdir, observatory)
    else:
        path = os.path.join(DEFAULT_CRDS_DIR, subdir, observatory)
    return _clean_path(path)
    
def get_crds_path():
    """
    >>> temp = dict(os.environ)
    >>> os.environ = {}

    >>> get_crds_path()
    '/grp/crds/cache'
    
    >>> os.environ = {}
    >>> os.environ["CRDS_PATH_SINGLE"] = "/somewhere"
    >>> get_crds_path()
    '/somewhere'

    >>> os.environ = {}
    >>> os.environ["CRDS_PATH"] = "/somewhere_else"
    >>> get_crds_path()
    '/somewhere_else'
    
    >>> os.environ = temp
    """
    return _std_cache_path("", "*not-in-crds-environment*", "")

def get_crds_mappath(observatory):
    """get_crds_mappath() returns the base path of the CRDS mapping directory 
    tree where CRDS rules files (mappings) are stored.   This is extended by
    <observatory> once it is known.
    
    DEPRECATED:  only use in the config module.  Use locate_file() or locate_mapping() instead.
    
    >>> temp = dict(os.environ)
    >>> os.environ = {}
    
    >>> get_crds_mappath('jwst')
    '/grp/crds/cache/mappings/jwst'
    
    >>> os.environ["CRDS_PATH"] = '/somewhere'
    >>> get_crds_mappath('jwst')
    '/somewhere/mappings/jwst'
    
    >>> os.environ["CRDS_PATH_SINGLE"] = "/somewhere2"
    >>> get_crds_mappath('jwst')
    '/somewhere2/mappings'
    
    >>> os.environ["CRDS_MAPPATH"] = "/somewhere3/mappings2"
    >>> get_crds_mappath('jwst')
    '/somewhere3/mappings2/jwst'
    
    >>> os.environ["CRDS_MAPPATH_SINGLE"] = "/somewhere4/mappings3"
    >>> get_crds_mappath('jwst')
    '/somewhere4/mappings3'
    
    >>> os.environ = temp
    """
    return _std_cache_path(observatory, "CRDS_MAPPATH", "mappings")

def get_crds_refpath(observatory):
    """get_crds_refpath returns the base path of the directory tree where CRDS 
    reference files are stored.   This is extended by <observatory> once it is
    known.
    
    DEPRECATED: only use in config module.  Use locate_file() or locate_reference() instead.
    """
    return _std_cache_path(observatory, "CRDS_REFPATH", "references")

def get_crds_config_path(observatory):
    """Return the path to a writable directory used to store configuration info
    such as last known server status.   This is extended by <observatory> once
    it is known.   If CRDS_PATH doesn't point to a writable directory, then
    CRDS_CFGPATH should be defined.
    """
    return _std_cache_path(observatory, "CRDS_CFGPATH", "config")

# ===========================================================================

def get_crds_processing_mode():
    """Return the preferred location for computing best references when
    network connectivity is available.
    
    'local'   --   compute locally even if client CRDS is obsolete
    'remote'  --   compute remotely even if client CRDS is up-to-date
    'auto'    --   compute locally unless connected and client CRDS is obsolete
    """
    mode = os.environ.get("CRDS_MODE","auto")
    assert mode in ["local", "remote", "auto"], "Invalid CRDS_MODE: " + repr(mode)
    return mode

def get_crds_env_context():
    """If it has been specified in the environment by CRDS_CONTEXT,  return the 
    pipeline context which defines CRDS best reference rules,  else None.
    
    >>> os.environ["CRDS_CONTEXT"] = "jwst.pmap"
    >>> get_crds_env_context()
    'jwst.pmap'
    
    >>> os.environ["CRDS_CONTEXT"] = "jwst_miri_0022.imap"    
    >>> get_crds_env_context()
    Traceback (most recent call last):
    ...
    AssertionError: If set, CRDS_CONTEXT should specify a pipeline mapping,  e.g. 'jwst.pmap', not 'jwst_miri_0022.imap'
   
    >>> os.environ["CRDS_CONTEXT"] = "/nowhere/to/be/found/jwst_0042.pmap"    
    >>> get_crds_env_context()
    Traceback (most recent call last):
    ...
    AssertionError: Can't find pipeline mapping specified by CRDS_CONTEXT = '/nowhere/to/be/found/jwst_0042.pmap' at '/nowhere/to/be/found/jwst_0042.pmap'

    >>> del os.environ["CRDS_CONTEXT"]
    >>> get_crds_env_context()
    """
    context = os.environ.get("CRDS_CONTEXT", None)
    if context is not None:
        where = locate_mapping(context)
        assert context.endswith(".pmap"), \
            "If set, CRDS_CONTEXT should specify a pipeline mapping,  e.g. 'jwst.pmap', not " + repr(context)
        assert os.path.exists(where), \
            "Can't find pipeline mapping specified by CRDS_CONTEXT = " + repr(context) + " at " + repr(where)
    return context

def get_ignore_checksum():
    """Returns environment override for disabling mapping checksums during development."""
    return env_to_bool("CRDS_IGNORE_MAPPING_CHECKSUM", False)

# ===========================================================================

def get_crds_env_vars():
    """Return a dictionary of all env vars starting with 'CRDS'."""
    env_vars = {}
    for var in os.environ:
        if var.upper().startswith("CRDS"):
            env_vars[var] = os.environ[var]
    return env_vars

def get_crds_actual_paths(observatory):
    """Return a dictionary of the critical paths CRDS configuration resolves to."""
    return {
        "mapping root" : get_crds_mappath(observatory),
        "reference root" : get_crds_refpath(observatory),
        "config root" : get_crds_config_path(observatory),
        }

# ============================================================================

# client API related settings.

def get_download_mode():
    """Return the mode used to download references and mappings,  either normal
    "http" file transfer or json "rpc" based.   In theory HTTP optimizes better 
    with direct support for static files from Apache,  but RPC is more flexible
    and works through firewalls.   The key distinction is that HTTP mode can
    work with a server which is not the same as the CRDS server (perhaps an
    archive server).   Once/if a public archive server is available with normal 
    URLs,  that wopuld be the preferred means to get references and mappings.
    """
    mode = os.environ.get("CRDS_DOWNLOAD_MODE", "http").lower()
    assert mode in ["http","rpc"], \
        "Invalid CRDS_DOWNLOAD_MODE setting.  Use 'http' (preferred) " + \
        "or 'rpc' (through firewall)."
    return mode

def get_checksum_flag():
    """Return True if the environment is configured for checksums."""
    return env_to_bool("CRDS_DOWNLOAD_CHECKSUMS", True)

def get_client_retry_count():
    """Return the integer number of times a network transaction should be attempted.  No retries == 1."""
    return env_to_int("CRDS_CLIENT_RETRY_COUNT", 1)

def get_client_retry_delay_seconds():
    """Return the integer number of seconds CRDS should wait between retrying failed network transactions."""
    return env_to_int("CRDS_CLIENT_RETRY_DELAY_SECONDS", 0)

def enable_retries():
    """Set reasonable defaults for CRDS retries"""
    os.environ["CRDS_CLIENT_RETRY_COUNT"] = 20
    os.environ["CRDS_CLIENT_RETRY_DELAY_SECONDS"] = 10
    
def disable_retries():
    """Set the defaults for only one try for each network transaction."""
    os.environ["CRDS_CLIENT_RETRY_COUNT"] = 1
    os.environ["CRDS_CLIENT_RETRY_DELAY_SECONDS"] = 0

    
CRDS_DEFAULT_SERVERS = {
    "hst" : "https://hst-crds.stsci.edu",
    "jwst" : "https://jwst-crds.stsci.edu",
}

def get_server_url(observatory):
    """Return either the value of CRDS_SERVER_URL or an appropriate default server for `observatory`."""
    return os.environ.get("CRDS_SERVER_URL", CRDS_DEFAULT_SERVERS.get(observatory, None))

# ===========================================================================

_CRDS_CACHE_READONLY = False

def set_cache_readonly(readonly=True):
    """Set the flag controlling writes to the CRDS cache."""
    global _CRDS_CACHE_READONLY
    _CRDS_CACHE_READONLY = readonly
    return _CRDS_CACHE_READONLY

def get_cache_readonly():
    """Read the flag controlling writes to the CRDS cache.  When True,  no write to cache should occur."""
    return _CRDS_CACHE_READONLY or env_to_bool("CRDS_READONLY_CACHE", False)

# ===========================================================================

def get_path(filename, observatory):
    """Return the CRDS cache path of `filename` for `observatory`.   The path is
    similar to the one from locate_file(),  but includes dirname only,  not `filename` itself.
    """
    assert OBSERVATORY_RE.match(observatory), "Invalid observatory " + repr(observatory)
    fullpath = locate_file(filename, observatory)
    return os.path.dirname(fullpath)

def locate_file(filepath, observatory):
    """Figure out the absolute pathname where CRDS will stash a reference
    or mapping file.  If filepath already has a directory,  return filepath
    as-is.   Otherwise,  return the *client* path for a file.
    """
    if os.path.dirname(filepath):
        return filepath
    if is_mapping(filepath):
        return locate_mapping(filepath, observatory)
    else:
        return locate_reference(filepath, observatory)

def locate_config(cfg, observatory):
    """Return the absolute path where reference `ref` should be located."""
    if os.path.dirname(cfg):
        return cfg
    return os.path.join(get_crds_config_path(observatory), cfg)

def locate_reference(ref, observatory):
    """Return the absolute path where reference `ref` should be located."""
    if os.path.dirname(ref):
        return ref
    return os.path.join(get_crds_refpath(observatory), ref)

def is_mapping(mapping):
    """Return True IFF `mapping` has an extension indicating a CRDS mapping 
    file.
    """
    return isinstance(mapping, basestring) and mapping.endswith((".pmap", ".imap", ".rmap"))

def get_sqlite3_db_path(observatory):
    """Return the path to the downloadable CRDS catalog + history SQLite3 database file."""
    return locate_config("crds_db.sqlite3", observatory)

# -------------------------------------------------------------------------------------

def complete_re(regex_str):
    """Add ^$ to `regex_str` to force match to entire string."""
    return "^" + regex_str + "$"

OBSERVATORY_RE_STR = r"[a-zA-Z_0-9]{1,8}"
OBSERVATORY_RE = re.compile(complete_re(OBSERVATORY_RE_STR))
FILE_RE_STR = r"[A-Za-z0-9\._\- ]{1,128}"
FILE_RE = re.compile(complete_re(FILE_RE_STR)) # at min *should not* contain % < > \ { }
FILE_PATH_RE_STR = r"([/A-Za-z0-9_\- ]{1,256})?" + FILE_RE_STR
FILE_PATH_RE = re.compile(complete_re(FILE_PATH_RE_STR))  # at min *should not* contain % < > \ { }

def check_filename(filename):
    """Verify that `filename` is a basename with no dangerous characters."""
    assert FILE_RE.match(filename), "Invalid file name " + repr(filename)

def check_path(path):
    """Make sure `path` has no dangerous characters."""
    path = os.path.abspath(path)
    assert FILE_PATH_RE.match(path), "Invalid file path " + repr(path)
    return path

# -------------------------------------------------------------------------------------

# Standard date time format using T separator for command line use specifying contexts.
# e.g. 2040-02-22T12:01:30.4567
CONTEXT_DATETIME_RE_STR = r"\d\d\d\d\-\d\d\-\d\d(T\d\d:\d\d:\d\d(\.\d+)?)?"
CONTEXT_DATETIME_RE = re.compile(complete_re(CONTEXT_DATETIME_RE_STR))

# e.g.  hst, hst-acs, hst-acs-darkfile
CONTEXT_OBS_INSTR_KIND_RE_STR = r"[a-z]{1,8}(\-[a-z]{1,32}(\-[a-z]{1,32})?)?" 

# e.g.   2040-02-22T12:01:30.4567,  hst-2040-02-22T12:01:30.4567, hst-acs-2040-02-22T12:01:30.4567, ...
CONTEXT_RE_STR = r"(?P<context>" + CONTEXT_OBS_INSTR_KIND_RE_STR + r"\-)?((?P<date>" + CONTEXT_DATETIME_RE_STR + r"|edit|operational))"
CONTEXT_RE = re.compile(complete_re(CONTEXT_RE_STR))

def is_mapping_spec(mapping):
    """Return True IFF `mapping` is a mapping name *or* a date based mapping specification.
    
    Date-based specifications can be interpreted by the CRDS server with respect to the operational
    context history to determine the default operational context which was in use at that date.
    This function verifies syntax only,  not the existence of corresponding context.
    
    >>> is_mapping_spec("hst.pmap")
    True
    
    >>> is_mapping_spec("foo.pmap")
    True
    
    >>> is_mapping_spec("foo")
    False
    
    >>> is_mapping_spec("hst-2040-01-29T12:00:00")
    True

    >>> is_mapping_spec("hst-acs-2040-01-29T12:00:00")
    True

    >>> is_mapping_spec("hst-acs-darkfile-2040-01-29T12:00:00")
    True
    
    >>> is_mapping_spec("2040-01-29T12:00:00")
    True
    
    >>> is_mapping_spec("hst-edit")
    True
    
    >>> is_mapping_spec("jwst-operational")
    True
    
    >>> is_mapping_spec("hst-foo")
    False
    """
    return is_mapping(mapping) or (isinstance(mapping, basestring) and bool(CONTEXT_RE.match(mapping)))

def is_date_based_mapping_spec(mapping):
    """Return True IFF `mapping` is a date based specification (not a filename).
 
    >>> is_date_based_mapping_spec("2040-01-29T12:00:00")
    True
 
    >>> is_date_based_mapping_spec("hst.pmap")
    False
    """
    return is_mapping_spec(mapping) and not is_mapping(mapping)

def is_reference(reference):
    """Return True IFF file name `reference` is plausible as a reference file name.
    is_reference() does not *guarantee* that `reference` is a reference file name,
    in particular a dataset filename might pass as a reference.

    >>> is_reference("something.fits")
    True
    >>> is_reference("something.finf")
    True
    >>> is_reference("something.r0h")
    True
    >>> is_reference("something.foo")
    False
    >>> is_reference("/some/path/something.fits")
    True
    >>> is_reference("/some/path/something.pmap")
    False

    """
    extension = os.path.splitext(reference)[-1]
    return re.match(r"\.fits|\.finf|\.r\dh|\.yaml|\.json|\.text", extension) is not None

def filetype(filename):
    """Classify `filename`'s type so it can be processed or displayed."""
    if is_mapping(filename):
        return "mapping"
    elif filename.endswith(".fits"):
        return "fits"
    elif filename.endswith(".yaml"):
        return "yaml"
    elif filename.endswith(".json"):
        return "json"
    elif filename.endswith(".finf"):
        return "finf"
    elif filename.endswith(".txt"):
        return "text"
    elif re.match(".*\,r[0-9]h$", filename): # GEIS header
        return "text"
    else:
        return "unknown"

def locate_mapping(mappath, observatory=None):
    """Return the path where CRDS mapping `mappath` should be."""
    if os.path.dirname(mappath):
        return mappath
    if observatory is None:
        observatory = mapping_to_observatory(mappath)
    return os.path.join(get_crds_mappath(observatory), mappath)

def mapping_exists(mapping):
    """Return True IFF `mapping` exists on the local file system."""
    return os.path.exists(locate_mapping(mapping))

def file_in_cache(filename, observatory):
    """Return True IFF `filename` is in the local cache."""
    path = locate_file(os.path.basename(filename), observatory)
    return os.path.exists(path)

# These are name based but could be written as slower check-the-mapping
# style functions.
def mapping_to_observatory(context_file):
    """
    >>> mapping_to_observatory('hst.pmap')
    'hst'
    >>> mapping_to_observatory('hst_0000.pmap')
    'hst'
    >>> mapping_to_observatory('hst_acs_biasfile_0000.rmap')
    'hst'
    """
    return os.path.basename(context_file).split("_")[0].split(".")[0]

def mapping_to_instrument(context_file):
    """
    >>> mapping_to_instrument('hst_acs_biasfile.rmap')
    'acs'
    """
    return os.path.basename(context_file).split("_")[1].split(".")[0]

def mapping_to_filekind(context_file):
    """
    >>> mapping_to_filekind('hst_acs_biasfile.rmap')
    'biasfile'
    """
    return os.path.basename(context_file).split("_")[2].split(".")[0]

def test():
    """Run doctests on crds.config module."""
    import doctest
    from . import config
    return doctest.testmod(config)

