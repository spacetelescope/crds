"""This module is the interface to CRDS configuration information.
Predominantly it is used to define CRDS file cache paths and file location
functions.
"""
import os
import os.path
import re
import glob
import getpass
import configparser

# ===========================================================================

from crds.core import log, exceptions

# ===========================================================================

def _get_crds_ini_path():
    """Return the path to the CRDS rc file defining CRDS parameter settings."""
    default_rc = os.path.expanduser("~/.crds.ini")
    return os.environ.get("CRDS_INI_FILE", default_rc)

# Re-reading and re-parsing the rc file is probably too slow not to cache.
# Implement brute-force caching to avoid circular dependency with crds.utils
CRDS_INI_PARSER = None

def _get_crds_ini_parser():
    """Load and return the environment from the CRDS rc file."""
    global CRDS_INI_PARSER
    if CRDS_INI_PARSER is None:
        parser = configparser.SafeConfigParser()
        with log.warn_on_exception("Failed reading CRDS rc file"):
            ini_path = _get_crds_ini_path()
            if os.path.exists(ini_path):
                mode = os.stat(ini_path).st_mode
                if mode & 0o077:
                    raise exceptions.CrdsWebAuthenticationError("You must 'chmod 0600 $HOME/.crds.ini' to make it secret.")
                parser.read(ini_path)
                CRDS_INI_PARSER = parser
            else:
                log.verbose("No CRDS .ini file found at", repr(ini_path))
    else:
        parser = CRDS_INI_PARSER
    return parser

# Not caching this enables doing env overrides on-the-fly in os.environ,  including
# the basic machinery of ConfigItem.set() which is a non-permanent set.
def get_crds_env_str(section, varname, default):
    """Return the compsite env obtained by reading the .crds.ini file and overriding
    from os.environ.
    """
    if section:
        ini_parser = _get_crds_ini_parser()
        try:
            ini_val = ini_parser.get(section, varname)
        except configparser.NoSectionError:
            ini_val = None
        except configparser.NoOptionError:
            ini_val = None
    else:
        ini_val = None
    if ini_val in ["None", "none", "NONE"]:
        ini_val = None
    result = os.environ.get(varname, ini_val)  # os.environ overrides ini file.
    return result if result is not None else default

# ===========================================================================

def env_to_bool(varname, default=False, section=None):
    """Convert the specified environment variable `varname` into a Python bool
    defaulting to `default` if it's not defined in os.environ.
    """
    env_str = get_crds_env_str(section, varname, default)
    return env_str_to_bool(varname, env_str)

def env_str_to_bool(varname, val):
    """Convert the boolean environment value string `val` to a Python bool
    on behalf of environment variable `varname`.
    """
    if val in ["False", "false", "FALSE", "F", "f", "0", False, 0]:
        rval = False
    elif val in ["True", "true", "TRUE", "T", "t", "1", True, 1]:
        rval = True
    else:
        raise ValueError("Invalid value " +  repr(val) +
                         " for boolean env var " + repr(varname))
    return rval

def env_to_int(varname, default, section=None):
    """Convert the specified environment variable `varname` into a Python int
    defaulting to `default` if it's not defined in os.environ.
    """
    env_str = get_crds_env_str(section, varname, default)
    return env_str_to_int(varname, env_str)

def env_str_to_int(varname, val):
    """Convert environment variable decimal value `val` from `varname` to an int and return it."""
    try:
        return int(val)
    except Exception:
        raise ValueError("Invalid value for " + repr(varname) +
                         " should have a decimal integer value but is " + repr(str(val)))

# ===========================================================================

class ConfigItem:
    """CRDS environment control item base class.  These are driven by environment variables
    but conceptually could extend to a CRDS .rc file of some kind.

    >>> CFG = ConfigItem("CRDS_CFG_ITEM", "999", "Test config item", valid_values=["999", "1000"])
    >>> CFG.get()
    '999'
    >>> import os
    >>> os.environ["CRDS_CFG_ITEM"] = "1000"
    >>> CFG.get()
    '1000'
    >>> os.environ["CRDS_CFG_ITEM"] = "2"   # Don't do this!
    >>> CFG.get()
    Traceback (most recent call last):
    ...
    AssertionError: Invalid value for 'CRDS_CFG_ITEM' of '2' is not one of ['999', '1000']
    >>> os.environ["CRDS_CFG_ITEM"] = "1000"    # cleaup .set() can't do

    >>> CFG.set("999")
    '1000'
    >>> CFG.get()
    '999'
    >>> os.environ["CRDS_CFG_ITEM"]
    '999'
    """
    def __init__(self, env_var, default, comment=None, valid_values=None, lower=False, ini_section=None):
        """Defines CRDS environment item named `env_var` which has the value `default` when not specified anywhere."""
        self.env_var = env_var  # for starters,  this IS an env var,  bu conceptually it is an identifier.
        self.default = default
        self.comment = comment
        self.valid_values = valid_values
        self.lower = lower
        self.ini_section = ini_section
        self.get()

    def check_value(self, value):
        """Verify that `value` is valid for this config item."""
        if self.valid_values:
            assert value in self.valid_values, "Invalid value for " + repr(self.env_var) + " of " + repr(value)  + \
                " is not one of " + repr(self.valid_values)
        return value

    def get(self):
        """Return the value of this control item,  or the default if it is not set."""
        value = get_crds_env_str(self.ini_section, self.env_var, self.default)
        value = self._set(value)
        return value

    def set(self, value):
        """Set the value of the control item,  for the sake of this runtime session only."""
        old = self.get()
        self._set(value)
        return old

    def _set(self, value):
        """Set the value of the control item,  for the sake of this runtime session only."""
        if self.lower and isinstance(value, str):
            value = value.lower()
        self.check_value(value)
        os.environ[self.env_var] = str(value)
        return value

    def reset(self):
        """Restore this variable to it's default value,  clearing any environment setting."""
        os.environ.pop(self.env_var, None)

class StrConfigItem(ConfigItem):
    """Config item for a string value,  currently no difference from base ConfigItem.

    >>> CFG = StrConfigItem("CRDS_CFG", "something", "CRDS configuration",
    ...       valid_values=["something","else","other"])

    >>> CFG.set("foo")
    Traceback (most recent call last):
    ...
    AssertionError: Invalid value for 'CRDS_CFG' of 'foo' is not one of ['something', 'else', 'other']

    >>> CFG + "_foo"
    'something_foo'

    >>> "foo_" + CFG
    'foo_something'

    >>> CFG == 'something'
    True

    >>> 'something' == CFG
    True

    >>> CFG == 'foo'
    False

    >>> 'foo' == CFG
    False

    >>> str(CFG)
    'something'
    """

    def __str__(self):
        """Return value of string config item."""
        return str(self.get())

    def __hash__(self):
        """Use str() of StrConfigItem as hash()"""
        return hash(str(self))

    def __eq__(self, other):
        """Test string value of config item for equality with `other`."""
        return str(self.get()) == other

    def __add__(self, other):
        """Add string value of config item to following parameter `other`."""
        return str(self) + str(other)

    def __radd__(self, other):
        """Add string value of config item to preceding parameter `other`."""
        return str(other) + str(self)

class BooleanConfigItem(ConfigItem):
    """Represents a boolean environment setting for CRDS.

    >>> BOOL = BooleanConfigItem("CRDS_BOOL_ITEM", False, "Test boolean config item")
    >>> if BOOL:
    ...    print("True")
    ... else:
    ...    print("False")
    False

    >>> os.environ["CRDS_BOOL_ITEM"] = "True"
    >>> if BOOL:
    ...    print("True")
    ... else:
    ...    print("False")
    True

    >>> BOOL.set("True")  # .set() returns old value
    True
    >>> if BOOL:
    ...    print("True")
    ... else:
    ...    print("False")
    True

    >>> BOOL.set("False")
    True

    >>> if BOOL:
    ...    print("True")
    ... else:
    ...    print("False")
    False

    """
    def __init__(self, var, default, *args, **keys):
        keys = dict(keys)
        keys["valid_values"] = ["0", "1", "true", "false", "t", "f", "False", "True",
                                False, True, 0, 1]
        keys["lower"] = True
        super(BooleanConfigItem, self).__init__(var, str(default), *args, **keys)

    def get(self):
        """Return the bool value of this config item."""
        return env_str_to_bool(self.env_var, super(BooleanConfigItem, self).get())

    def set(self, val):
        """Set the bool value of this config item to `val`,  coercing to bool.  Return old value."""
        return super(BooleanConfigItem, self).set(str(env_str_to_bool(self.env_var, str(val))))

    def __nonzero__(self):
        """Support using this boolean config item be used as a conditional expression."""
        return self.get()

    __bool__ = __nonzero__


class IntConfigItem(ConfigItem):
    """Represents a boolean environment setting for CRDS.

    >>> INT = IntConfigItem(
    ...             "CRDS_INT_ITEM", '57', "Test int config item")
    >>> if INT.get():
    ...    print("True")
    ... else:
    ...    print("False")
    True

    >>> os.environ["CRDS_INT_ITEM"] = "0"
    >>> if INT.get():
    ...    print("True")
    ... else:
    ...    print("False")
    False

    >>> INT.get()
    0

    >>> INT.set("42")  # .set() returns old value
    0

    >>> INT.get()
    42
    """
    def __init__(self, var, default, *args, **keys):
        keys = dict(keys)
        keys["valid_values"] = None
        super(IntConfigItem, self).__init__(var, str(default), *args, **keys)

    def get(self):
        """Return the bool value of this config item."""
        return int(super(IntConfigItem,self).get())

    def set(self, val):
        """Set the bool value of this config item to `val`,  coercing to bool.  Return old value."""
        return super(IntConfigItem, self).set(str(int(val)))

    def __nonzero__(self):
        """Support using this boolean config item be used as
        a conditional expression."""
        return self.get() != 0

# ===========================================================================

FITS_IGNORE_MISSING_END = BooleanConfigItem("CRDS_FITS_IGNORE_MISSING_END", False,
    "When True, ignore missing END records in the FITS primary header.  Otherwise fail.")

FITS_VERIFY_CHECKSUM = BooleanConfigItem("CRDS_FITS_VERIFY_CHECKSUM", True,
    "When True, verify that FITS header CHECKSUM and DATASUM values are correct.  Otherwise fail.")

ADD_LOG_MSG_COUNTER = BooleanConfigItem(
    "CRDS_ADD_LOG_MSG_COUNTER", False, "When True, add a running counter.")
log.set_add_log_msg_count(ADD_LOG_MSG_COUNTER)

# ===========================================================================

# Runtime bad file options for end users

ALLOW_BAD_REFERENCES  = BooleanConfigItem("CRDS_ALLOW_BAD_REFERENCES", False,
    "When True, references which are designated as BAD (scientifically invalid) on the server can be used with warnings.")

ALLOW_BAD_RULES = BooleanConfigItem("CRDS_ALLOW_BAD_RULES", False,
    "When True, rules which are designated as BAD (scientifically invalid) on the server can be used with warnings.")

# ===========================================================================

# Refactoring options

PASS_INVALID_VALUES = BooleanConfigItem("PASS_INVALID_VALUES", False,
    "When True,  return invalid values detected by data model schema. These are still be errors.")

ALLOW_SCHEMA_VIOLATIONS = BooleanConfigItem("CRDS_ALLOW_SCHEMA_VIOLATIONS", False,
    "When True, don't map data model warnings onto CRDS errors.")

ALLOW_BAD_PARKEY_VALUES = BooleanConfigItem("CRDS_ALLOW_BAD_PARKEY_VALUES", False,
    "When True, turn off parkey value checking when loading rmaps.  For refactoring with bad 'legacy' references.")

ALLOW_BAD_USEAFTER = BooleanConfigItem("CRDS_ALLOW_BAD_USEAFTER", False,
    "When True,  when USEAFTER won't parse,  fake it as the primal default.")

# ============================================================================

CRDS_DATA_CHUNK_SIZE = 2**23
#   IntConfigItem("CRDS_DATA_CHUNK_SIZE", 2**23,
#   "File download transfer block size, 8M.  HTTP mode only.")

CRDS_CHECKSUM_BLOCK_SIZE = 2**23

# IntConfigItem("CRDS_CHECKSUM_BLOCK_SIZE", 2**23,
#    "Size of data read into memory at once for utils.checksum.")

# ===========================================================================

# To support testing, the default cache is configurable.  Ordinarily
# the default cache is reserved for configuration free onsite use.
# The correct approach (outside the realm of testing) for configuring
# CRDS is to use CRDS_PATH and related settings.
CRDS_DEFAULT_CACHE = os.environ.get("CRDS_DEFAULT_CACHE", "/grp/crds/cache")

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

    XXXX `observatory` should accept pseudo-observatory "all"
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
        path = os.path.join(CRDS_DEFAULT_CACHE, subdir, observatory)
    return _clean_path(path)

def get_crds_path():
    """
    >>> temp = dict(os.environ)
    >>> os.environ = {}

    >>> get_crds_path() == CRDS_DEFAULT_CACHE
    True

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

    >>> get_crds_mappath('jwst') == CRDS_DEFAULT_CACHE + "/mappings/jwst"
    True

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

def get_crds_cfgpath(observatory):
    """Return the path to a writable directory used to store configuration info
    such as last known server status.   This is extended by <observatory> once
    it is known.   If CRDS_PATH doesn't point to a writable directory, then
    CRDS_CFGPATH should be defined.
    """
    return _std_cache_path(observatory, "CRDS_CFGPATH", "config")

def get_crds_root_cfgpath():
    """Return the root multi-project config path. Used for e.g. lockfiles.

    >>> temp = dict(os.environ)
    >>> os.environ = {}

    >>> os.environ["CRDS_PATH"] = '/somewhere'
    >>> get_crds_root_cfgpath()
    '/somewhere/config'

    >>> os.environ["CRDS_PATH_SINGLE"] = "/somewhere2"
    >>> get_crds_root_cfgpath()
    '/somewhere2/config'

    >>> os.environ["CRDS_CFGPATH"] = "/somewhere3/cfg2"
    >>> get_crds_root_cfgpath()
    '/somewhere3/cfg2'

    >>> os.environ["CRDS_CFGPATH_SINGLE"] = "/somewhere4/cfg3"
    >>> get_crds_root_cfgpath()
    '/somewhere4/cfg3'

    >>> os.environ = temp
    """
    dirname = get_crds_cfgpath("all")
    if dirname.endswith("all"):
        return os.path.dirname(dirname)
    else:
        return dirname

def get_crds_refpath(observatory):
    """get_crds_refpath returns the base path of the directory tree where CRDS
    reference files are stored.   This is extended by <observatory> once it is
    known.

    DEPRECATED: only use in config module.  Use locate_file() or locate_reference() instead.
    """
    return _std_cache_path(observatory, "CRDS_REFPATH", "references")

def locate_config(cfg, observatory):
    """Return the absolute path where reference `cfg` should be located."""
    if os.path.dirname(cfg):
        return cfg
    return os.path.join(get_crds_cfgpath(observatory), cfg)

def override_crds_paths(crds_path):
    """Overrides all CRDS PATH definition environment variables
    (e.g. CRDS_MAPPATH, CRDS_MAPPATH_SINGLE, CRDS_REFPATH, ...)
    as if the user had only specified CRDS_PATH=crds_path and let
    all other cache subpaths be defined at default locations.
    """
    for name in os.environ:
        if "CRDS_" in name and "PATH" in name:
            del os.environ[name]
    os.environ["CRDS_PATH"] = crds_path


# -------------------------------------------------------------------------------------

def get_crds_picklepath(observatory):
    """Return the directory name where CRDS stores pickles for `observatory`."""
    return _std_cache_path(observatory, "CRDS_PICKLEPATH", "pickles")

def locate_pickle(mapping, observatory=None):
    """Return the absolute path where reference `ref` should be located."""
    if os.path.dirname(mapping):
        return mapping
    if observatory is None:
        observatory = mapping_to_observatory(mapping)
    return os.path.join(get_crds_picklepath(observatory), mapping + ".pkl")

USE_PICKLED_CONTEXTS = BooleanConfigItem("CRDS_USE_PICKLED_CONTEXTS", False,
    "When True,  CRDS contexts should be loaded from a pickled version if possible.")

AUTO_PICKLE_CONTEXTS = BooleanConfigItem("CRDS_AUTO_PICKLE_CONTEXTS", False,
    "When True, CRDS contexts should be automatically pickled and cached after loading.")

# -------------------------------------------------------------------------------------

FORCE_COMPLETE_LOAD = BooleanConfigItem("CRDS_FORCE_COMPLETE_LOAD", False,
    "When True, force CRDS contexts to load in their entirety rather than based on what is actually used.")

EXPLICIT_GARBAGE_COLLECTION = BooleanConfigItem("CRDS_EXPLICIT_GARBAGE_COLLECTION", True,
    "When False, the @gc_collected function decorator skips garbage collection.")
# -------------------------------------------------------------------------------------

def get_sqlite3_db_path(observatory):
    """Return the path to the downloadable CRDS catalog + history SQLite3 database file."""
    return locate_config("crds_db.sqlite3", observatory)

# ===========================================================================

CRDS_SUBDIR_TAG_FILE = "ref_cache_subdir_mode"
CRDS_REF_SUBDIR_MODES = ["instrument", "flat", "legacy"]
CRDS_REF_SUBDIR_MODE = "None"  # does not make cache consistent with env,  test only!!

def get_crds_ref_subdir_mode(observatory):
    """Return the mode value defining how reference files are located."""
    global CRDS_REF_SUBDIR_MODE
    if CRDS_REF_SUBDIR_MODE in ["None", None]:
        mode_path = get_crds_ref_subdir_file(observatory)
        try:
            with open(mode_path) as pfile:
                mode = pfile.read().strip()
            # log.verbose("Determined cache format from", repr(mode_path), "as", repr(mode))
        except IOError:
            if len(glob.glob(os.path.join(get_crds_refpath(observatory), "*"))) > 20:
                mode = "flat"
                log.verbose("No cache config tag found, looks like a 'flat' cache based on existing references.")
            else:
                mode = "instrument"
                log.verbose("No cache config tag found, defaulting to 'instrument' based cache.")
            with log.verbose_on_exception("Failed saving default subdir mode to", repr(mode)):
                set_crds_ref_subdir_mode(mode, observatory)
        check_crds_ref_subdir_mode(mode)
        CRDS_REF_SUBDIR_MODE = mode
    else:
        mode = CRDS_REF_SUBDIR_MODE
    return mode

def set_crds_ref_subdir_mode(mode, observatory):
    """Set the reference file location subdirectory `mode`."""
    global CRDS_REF_SUBDIR_MODE
    check_crds_ref_subdir_mode(mode)
    CRDS_REF_SUBDIR_MODE = mode
    mode_path = get_crds_ref_subdir_file(observatory)
    if writable_cache_or_verbose("skipping subdir mode write."):
        from crds.core import heavy_client as hv   #  yeah,  kinda gross
        hv.cache_atomic_write(mode_path, mode, "Couldn't save sub-directory mode config")

def get_crds_ref_subdir_file(observatory):
    """Return path to CRDS config file defining cache organization.  Created
    automatically,  this is nominally for CRDS internal use only and cleanup.

    Returns <path to cache organization config file>
    """
    return os.path.join(get_crds_cfgpath(observatory), CRDS_SUBDIR_TAG_FILE)


def check_crds_ref_subdir_mode(mode):
    """Check for valid reference location subdirectory `mode`."""
    assert mode in CRDS_REF_SUBDIR_MODES, "Invalid CRDS cache subdirectory mode = " + repr(mode)
    return mode

# ===========================================================================

CRDS_MODE = StrConfigItem("CRDS_MODE", default="auto",
    comment="""Selects where bestrefs are performed, locally, remotely (on the CRDS server),
    or automatically chosen by comparing client version to server version.""",
    valid_values=["local", "remote", "auto"])

def get_crds_processing_mode():
    """Return the preferred location for computing best references when
    network connectivity is available.

    'local'   --   compute locally even if client CRDS is obsolete
    'remote'  --   compute remotely even if client CRDS is up-to-date
    'auto'    --   compute locally unless connected and client CRDS is obsolete
    """
    return CRDS_MODE.get()

# ===============================================================================================

# CRDS_CONTEXT = StrConfigItem("CRDS_CONTEXT", default=None)

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
    AssertionError: Only set CRDS_CONTEXT to a literal or symbolic context (.pmap), e.g. jwst_0042.pmap,  jwst-2014-10-15T00:15:21, jwst-operational,  not 'jwst_miri_0022.imap'

    >>> del os.environ["CRDS_CONTEXT"]
    >>> get_crds_env_context()
    """
    context = os.environ.get("CRDS_CONTEXT", None)
    if context:
        assert is_context_spec(context), \
            "Only set CRDS_CONTEXT to a literal or symbolic context (.pmap), e.g. jwst_0042.pmap,  jwst-2014-10-15T00:15:21, jwst-operational,  not " + repr(context)
    return context

CRDS_IGNORE_MAPPING_CHECKSUM = BooleanConfigItem("CRDS_IGNORE_MAPPING_CHECKSUM", False,
    "disables mapping checksums during development.")

def get_ignore_checksum():
    """Returns environment override for disabling mapping checksums during development."""
    return env_to_bool("CRDS_IGNORE_MAPPING_CHECKSUM", False)

def get_log_time():
    """Returns override flag for outputting time in log messages."""
    return env_to_bool("CRDS_LOG_TIME", False)

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
        "config root" : get_crds_cfgpath(observatory),
        "pickle root" : get_crds_picklepath(observatory),
        }

# ============================================================================

# client API related settings.

CRDS_DOWNLOAD_MODE = StrConfigItem("CRDS_DOWNLOAD_MODE", "http",
    "Selects the mode used by the CRDS client for downloading rules and references.",
    ["http", "plugin"], lower=True)

def get_download_mode():
    """Return the mode used to download references and mappings,  either normal
    "http" file transfer or "plugin" based.   "rpc" mode has been removed.

    Returns "http" or "plugin"
    """
    return CRDS_DOWNLOAD_MODE.get()

def get_download_plugin():
    """Fetch a command template from the environment to use a as a substitute for CRDS
    built-in downloaders.   This can be used to apply "wget" or "curl", etc, to perform
    downloads as sub-processes rather than as a direct Python http implementation.
    """
    if "CRDS_DOWNLOAD_MODE" in os.environ and os.environ["CRDS_DOWNLOAD_MODE"].lower() != "plugin":
        return None
    elif "CRDS_DOWNLOAD_PLUGIN" in os.environ:
        return os.environ["CRDS_DOWNLOAD_PLUGIN"]
    elif get_download_mode() == "plugin":
        for path in ["/usr/local/bin", "/usr/bin", "/sw/bin"]:
            program = os.path.join(path, "wget")
            if os.path.exists(program):
                return program + " --no-check-certificate --quiet ${SOURCE_URL}  -O ${OUTPUT_PATH}"
    return None

# -------------------------------------------------------------------------------------

# This permits an AWS environment to override the URLs normally supplied by the
# CRDS server with locally defined (S3) source URLs.  This can keep actual file
# downloads local to AWS and scalable with S3.

CRDS_CONFIG_URI = StrConfigItem("CRDS_CONFIG_URI", None,
    "Defines the URL/URI from which CRDS config files are downloaded.",
    lower=True)

CRDS_MAPPING_URI = StrConfigItem("CRDS_MAPPING_URI", None,
    "Defines the URL/URI from which CRDS mapping files are downloaded.",
    lower=True)

CRDS_REFERENCE_URI = StrConfigItem("CRDS_REFERENCE_URI", None,
    "Defines the URL/URI from which CRDS reference files are downloaded.",
    lower=True)

CRDS_PICKLE_URI = StrConfigItem("CRDS_PICKLE_URI", None,
    "Defines the URL/URI from which CRDS pickle files are downloaded.",
    lower=True)

# -------------------------------------------------------------------------------------

DOWNLOAD_CHECKSUMS = BooleanConfigItem(
    "CRDS_DOWNLOAD_CHECKSUMS", True, "Verify downloaded files match server's sha1sum.  If false,  allow bad checksums.")

DOWNLOAD_LENGTHS = BooleanConfigItem(
    "CRDS_DOWNLOAD_LENGTHS", True, "Verify downloaded files match server's file length.  If false,  allow bad lengths.")

def get_checksum_flag():
    """Return True if the environment is configured for checksums."""
    return DOWNLOAD_CHECKSUMS.get()

def get_length_flag():
    """Return True if the environment is configured for verifying downloaded file lengths.
    """
    return DOWNLOAD_LENGTHS.get()

# -------------------------------------------------------------------------------------

CLIENT_RETRY_COUNT = IntConfigItem(
    "CRDS_CLIENT_RETRY_COUNT", 1, "Integer number of times CRDS should retry download errors.  No retries == 1.")

def get_client_retry_count():
    """Return the integer number of times a network transaction should be attempted.  No retries == 1."""
    return CLIENT_RETRY_COUNT.get()

CLIENT_RETRY_DELAY_SECONDS = IntConfigItem(
    "CRDS_CLIENT_RETRY_DELAY_SECONDS", 0, "Seconds CRDS should wait between retries.  Defaults to 0.")

def get_client_retry_delay_seconds():
    """Return the integer number of seconds CRDS should wait between retrying failed network transactions."""
    return CLIENT_RETRY_DELAY_SECONDS.get()

def enable_retries(retry_count=20, delay_seconds=10):
    """Set reasonable defaults for CRDS retries"""
    CLIENT_RETRY_COUNT.set(retry_count)
    CLIENT_RETRY_DELAY_SECONDS.set(delay_seconds)

def disable_retries():
    """Set the defaults for only one try for each network transaction."""
    CLIENT_RETRY_COUNT.set(1)
    CLIENT_RETRY_DELAY_SECONDS.set(0)

# -------------------------------------------------------------------------------------

CRDS_DEFAULT_SERVERS = {
    "hst" : "https://hst-crds.stsci.edu",
    "jwst" : "https://jwst-crds.stsci.edu",
    "roman" : "https://roman-crds.stsci.edu",
    # None : "https://crds-serverless-mode.stsci.edu"
}

def get_server_url(observatory):
    """Return either the value of CRDS_SERVER_URL or an appropriate default server for `observatory`."""
    return os.environ.get("CRDS_SERVER_URL", CRDS_DEFAULT_SERVERS.get(observatory, None))

# ===========================================================================

USERNAME = None

def get_username(override=None):
    """Initialize the USERNAME config item and return the value, setting it to
    `override` is override is not None.  (nominally command line override).
    Defer username initialization until requested to avoid unneeded dialogs.
    """
    global USERNAME
    if USERNAME is None:
        # get env_var or ini_file
        USERNAME = StrConfigItem(
            "CRDS_USERNAME", None, ini_section="authentication",
            comment="User's e-mail on CRDS server, defaulting to current login.")
        # ultimately: override or env_var or ini_file or fallback function
        username = override or USERNAME.get()
        if username in ["None", "none", None]:
            username = getpass.getuser()
        USERNAME.set(username)
    return USERNAME.get()

PASSWORD = None

def get_password(override=None):
    """Initialize the PASSWORD config item and return the value setting it to
    `override` if override is not None.  (nominally command line override.)
    Defer password initialization until requested to avoid unneeded dialogs.
    """
    global PASSWORD
    if PASSWORD is None:
        # ultimately: override or env_var or ini_file or fallback function
        PASSWORD = StrConfigItem(
            "MAST_API_TOKEN", None, ini_section="authentication",
            comment="User's MAST_API_TOKEN, defaulting to echo-less key entry.")
        password = override or PASSWORD.get()
        if password in ["None", "none", None]:
            password = getpass.getpass("MAST_API_TOKEN: ")
        PASSWORD.set(password)
    return PASSWORD.get()

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

def writable_cache_abort(func):
    """Generator a filter by decorating `func`.  These call `func` and return False when the CRDS cache is
    readonly,  otherwise they return True.

    Use like this:

    if writable_cache_or_info(... log message parameters...):
        block of code requiring writable cache
    """
    def func_check_writable(*args, **keys):
        """func_check_writable is a wrapper which issues a func() message when CRDS
        is configured for a readonly cache.
        """
        if get_cache_readonly():  # message and quit
            func("READONLY CACHE", *args, **keys)
            return False
        else:
            return True
        func_check_writable.__name__ = "wrapped_writable_" + func.__name__
        func_check_writable._wrapped_writable = True
    return func_check_writable

writable_cache_or_info = writable_cache_abort(log.info)
writable_cache_or_verbose = writable_cache_abort(log.verbose)
writable_cache_or_warning = writable_cache_abort(log.warning)

# ===========================================================================

def filetype(filename):
    """Classify `filename`'s type so it can be processed or displayed.

    >>> filetype("foo.fits")
    'fits'

    >>> filetype("foo.yaml")
    'yaml'

    >>> filetype("foo.pmap")
    'mapping'

    >>> filetype("foo.json")
    'json'

    >>> filetype("foo.txt")
    'text'

    >>> filetype("foo.r0h")
    'geis'

    >>> filetype("foo.r0d")
    'geis'

    >>> filetype('foo.exe')
    'unknown'
    """
    if is_mapping(filename):
        return "mapping"
    elif filename.endswith(".fits"):
        return "fits"
    elif filename.endswith(".yaml"):
        return "yaml"
    elif filename.endswith(".json"):
        return "json"
    elif filename.endswith(".asdf"):
        return "asdf"
    elif filename.endswith(".txt"):
        return "text"
    elif re.match(r".*\.r[0-9][hd]$", filename): # GEIS header
        return "geis"
    else:
        return "unknown"

def file_in_cache(filename, observatory):
    """Return True IFF `filename` is in the local cache."""
    path = locate_file(os.path.basename(filename), observatory)
    return os.path.exists(path)

# ===========================================================================

def get_path(filename, observatory):
    """Return the CRDS cache path of `filename` for `observatory`.   The path is
    similar to the one from locate_file(),  but includes dirname only,  not `filename` itself.
    """
    assert OBSERVATORY_RE.match(observatory), "Invalid observatory " + repr(observatory)
    fullpath = locate_file(filename, observatory)
    return os.path.dirname(fullpath)

def locate_file(filepath, observatory):
    """Returns CRDS cache path if `filepath` has no directory, otherwise `filepath` as-is.

   Cannot always determine CRDS cache location for hypothetical files if not
   sufficiently identified in basename of `filepath`.

   Used to determine cache locations for directory-less `filepaths` from CRDS rules.

   Returns complex filepaths as-is for supporting operations on external files.
    """
    if os.path.dirname(filepath):
        return filepath
    return relocate_file(filepath, observatory)

def pop_crds_uri(filepath):
    """Pop off crds:// from a filepath,  yielding a pathless filename."""
    if filepath.startswith("crds://"):
        filepath = filepath[len("crds://"):]
        assert not os.path.dirname(filepath), "crds:// must prefix a filename with no path."
    return filepath

def relocate_file(filepath, observatory):
    """Returns path in CRDS cache where `filepath` would be relocated if it were
    copied into the CRDS cache.

    Able to determine CRDS cache location based on filename or file
    contents when `filepath` points to a real file.
    """
    # IMPORTANT:  since the outcome of relocate_file is ALWAYS a CRDS cache path,
    # the "dirname alresady defined" short-cut should not be used here.  The existing
    # dirname is irrelevant execept for determining file properties from badly named
    # reference files by inspecting the header.
    if is_mapping(filepath):
        return relocate_mapping(filepath, observatory)
    else:
        return relocate_reference(filepath, observatory)

# ===========================================================================

def locate_reference(ref, observatory):
    """Returns CRDS cache path for `ref` if it specifies no directory, otherwise
    `ref` as-is.
    """
    if os.path.dirname(ref):
        return ref
    return relocate_reference(ref, observatory)

def relocate_reference(ref, observatory):
    """Returns CRDS cache location where `ref` would be copied if it
    was copied into the CRDS cache.  When `ref` specifies a path to an
    existing file, the contents of `ref` can be exploited to determine
    the CRDS cache location.  Otherwise, the basename of `ref` must be
    in a standard form which implies location.
    """
    # This limited case is required for the server and dealing with temporary filenames
    # which cannot be used to determine instrument subdirectory based on name.
    if ref == "N/A":
        return ref
    if get_crds_ref_subdir_mode(observatory) == "flat":
        return os.path.join(get_crds_refpath(observatory), os.path.basename(ref))
    else:
        from crds.core import utils
        return utils.get_locator_module(observatory).locate_file(ref)

# ===========================================================================
if os.path.exists("/tmp"):
    DEFAULT_LOCK_PATH = "/tmp"
else:
    DEFAULT_LOCK_PATH = os.path.join(get_crds_root_cfgpath(), "locks")

CACHE_LOCK_PATH = StrConfigItem(
    "CRDS_LOCK_PATH", DEFAULT_LOCK_PATH,
    "Lock directory used to store lock files,  nominally for CRDS cache.")

USE_LOCKING = BooleanConfigItem("CRDS_USE_LOCKING", True,
    "Set to False to turn off CRDS cache locking.")

LOCKING_MODE = StrConfigItem("CRDS_LOCKING_MODE",  "multiprocessing",
    "Form of locking used by CRDS cache.",
    valid_values=["lockfile", "filelock", "multiprocessing"],
    lower=True)

def get_crds_lockpath(lock_filename):
    """Return the full path of `lock_filename` filename based on CRDS lock path configuration."""
    return os.path.join(CACHE_LOCK_PATH.get(), lock_filename)

# ===========================================================================

def complete_re(regex_str):
    """Add ^$ to `regex_str` to force match to entire string."""
    return "^" + regex_str + "$"

OBSERVATORY_RE_STR = r"[a-zA-Z]{1,8}"
OBSERVATORY_RE = re.compile(complete_re(OBSERVATORY_RE_STR))
FILE_RE_STR = r"[A-Za-z0-9\._\- ]{1,128}|N/A|OMIT"
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

def is_reference(reference):
    """Return True IFF file name `reference` is plausible as a reference file name.
    is_reference() does not *guarantee* that `reference` is a reference file name,
    in particular a dataset filename might pass as a reference.

    >>> is_reference("something.fits")
    True
    >>> is_reference("something.asdf")
    True
    >>> is_reference("something.json")
    True
    >>> is_reference("something.yaml")
    True
    >>> is_reference("something.text")
    True
    >>> is_reference("something.r0h")
    True
    >>> is_reference("something.r0d")
    True
    >>> is_reference("something.foo")
    False
    >>> is_reference("/some/path/something.fits")
    True
    >>> is_reference("/some/path/something.pmap")
    False
    >>> is_reference("/some/path/something.imap")
    False
    >>> is_reference("something.rmap")
    False
    """
    extension = os.path.splitext(reference)[-1].lower()
    return bool(re.match(r"\.fits|\.asdf|\.r\d[hd]|\.yaml|\.json|\.text", extension))

# -------------------------------------------------------------------------------------

# max len name component == 32.  max components == 3.
# no digits in CRDS name components,  except serial no
CRDS_OBS_RE_STR = r"(?P<observatory>" + r"[a-z][a-z]{1,8})" # No hyphens or digits
CRDS_INSTR_RE_STR = r"(?P<instrument>" + r"[a-z][a-z0-9]{1,16})"   # No hyphens
CRDS_FILEKIND_RE_STR = r"(?P<filekind>" + r"[a-z][a-z0-9\-]{1,32})"
CRDS_BASE_NAME_RE_STR = (r"(" +
        CRDS_OBS_RE_STR + r"(_" +
            CRDS_INSTR_RE_STR + r"(_" +
                CRDS_FILEKIND_RE_STR +
            r")?" +
        r")?" +
    r")")

CRDS_SYM_NAME_RE_STR = (r"(" +
        CRDS_OBS_RE_STR + r"(\-" +
            CRDS_INSTR_RE_STR + r"(\-" +
                CRDS_FILEKIND_RE_STR +
            r")?" +
        r")?" +
    r")")

CRDS_NAME_RE_STR = CRDS_BASE_NAME_RE_STR + r"(_\d\d\d\d)?\."
CRDS_NAME_RE = re.compile(CRDS_NAME_RE_STR)   # intentionally not complete. no ^ or $

# s7g1700gl_dead.fits
CDBS_NAME_RE_STR = r"[a-z0-9_]{1,52}\.(fits|r\d[hd])"
CDBS_NAME_RE = re.compile(complete_re(CDBS_NAME_RE_STR))

# -------------------------------------------------------------------------------------

def is_valid_reference_name(filename):
    """Return True IFF `filename` has a valid CRDS reference filename format.

    >>> is_valid_reference_name("hst_acs_darkfile_0027.rmap")
    False

    >>> is_valid_reference_name("hst_acs_darkfile_0027.fits")
    True

    >>> is_valid_reference_name("s7g1700gl_dead.fits")
    True

    >>> is_valid_reference_name("jwst_miri_pars-tweakreg_0001.asdf")
    True
    """
    name = os.path.basename(filename)
    return is_reference(name) and (is_crds_name(name) or is_cdbs_name(name))

def is_crds_name(name):
    """Return True IFF `name` is a valid CRDS-style name.

    >>> is_crds_name("hst_acs_darkfile_0027.rmap")
    True

    >>> is_crds_name("hst_acs.imap")
    True

    >>> is_crds_name("hst_acs_darkfile_0027.fits")
    True

    >>> is_crds_name("s7g1700gl_dead.fits")
    False

    >>> is_crds_name("jwst_miri_pars-tweakreg_0001.asdf")
    True

    >>> is_crds_name("jwst_miri_pars-tweakreg_0001.rmap")
    True
    """
    name = os.path.basename(name).lower()
    return bool(CRDS_NAME_RE.match(name))

def is_cdbs_name(name):
    """Return True IFF `name is a valid CDBS-style name.

    >>> is_cdbs_name("hst_acs_darkfile_0027.rmap")
    False

    >>> is_cdbs_name("s7g1700gl_dead.fits")
    True

    >>> is_cdbs_name("jwst_miri_pars-tweakreg_0001.asdf")
    False
    """
    name = os.path.basename(name).lower()
    return bool(CDBS_NAME_RE.match(name))

# -------------------------------------------------------------------------------------

# Standard date time format using T separator for command line use specifying contexts.
# e.g. 2040-02-22T12:01:30.4567
CONTEXT_DATETIME_RE_STR = (
    r"\d\d\d\d\-\d\d\-\d\d" +
        r"(T\d\d:\d\d:\d\d" +
            r"(\.\d+)?" +
        r")?"
    )

CONTEXT_DATETIME_RE = re.compile(complete_re(CONTEXT_DATETIME_RE_STR))

CONTEXT_OBS_RE_STR = r"[a-z]{1,8}"

# e.g.   2040-02-22T12:01:30.4567,  hst-2040-02-22T12:01:30.4567, hst-acs-2040-02-22T12:01:30.4567, ...
CONTEXT_RE_STR = (
    r"(" +
        r"(?P<context>" + CRDS_SYM_NAME_RE_STR + ")" +
        r"(" +
            r"(\-" +
                r"(?P<date>" +
                    r"(" + CONTEXT_DATETIME_RE_STR + r")" +
                        r"|" +
                    r"(" + "edit|operational|versions" + r")" +
                r")" +
            r")" +
        r")" +
    r")" +
        r"|" +
    r"(" +
        r"(" + CONTEXT_DATETIME_RE_STR + r")" +
    r")"
    )
CONTEXT_RE = re.compile(complete_re(CONTEXT_RE_STR))

PIPELINE_CONTEXT_RE_STR = (
    r"(" +
        r"(?P<context>" + CRDS_OBS_RE_STR + ")" +
        r"(" +
            r"(\-" +
                r"(" +
                    r"(?P<date>" + CONTEXT_DATETIME_RE_STR + r")" +
                        "|" +
                    r"(?P<context_tag>" + "edit|operational|versions" + r")" +
                r")" +
            r")" +
        r")"
    r")" +
        r"|" +
    r"(" +
        r"(" + CONTEXT_DATETIME_RE_STR + r")" +
    r")"
    )
PIPELINE_CONTEXT_RE = re.compile(complete_re(PIPELINE_CONTEXT_RE_STR))

MAPPING_RE_STR = CRDS_NAME_RE_STR + r"[pir]map"
MAPPING_RE = re.compile(complete_re(MAPPING_RE_STR))

# -------------------------------------------------------------------------------------

def is_mapping(mapping):
    """Return True IFF `mapping` has an extension indicating a CRDS mapping file."""
    return isinstance(mapping, str) and mapping.endswith((".pmap", ".imap", ".rmap"))

def is_simple_crds_mapping(mapping):
    """Return True IFF `mapping` implicitly or explicitly exists in the CRDS cache.

    Return False for ad hoc mappings outside the CRDS Cache.

    Nominally this function is one determinant of whether or not a mapping is
    picklable at the level of the overall CRDS runtime system.

    >>> is_simple_crds_mapping(locate_mapping("hst.pmap"))
    True

    is_simple_crds_mapping() is not a full guarantee that a mapping actually exists in
    CRDS,  merely a guarantee that if it did it would be located implicitly in
    the CRDS cache and has a basic name format which is not a date based context
    specifier.

    >>> is_simple_crds_mapping("hst_foo.pmap")
    True

    >>> is_simple_crds_mapping(locate_mapping("hst.fits"))
    False

    >>> is_simple_crds_mapping("tests/data/hst.pmap")
    False

    >>> is_simple_crds_mapping("hst-2040-01-29T12:00:00")
    False

    >>> is_simple_crds_mapping("hst-acs-2040-01-29T12:00:00")
    False

    >>> is_simple_crds_mapping("hst-acs-darkfile-2040-01-29T12:00:00")
    False

    >>> is_simple_crds_mapping("2040-01-29T12:00:00")
    False

    >>> is_simple_crds_mapping("hst-edit")
    False

    >>> is_simple_crds_mapping("hst-cos-deadtab-edit")
    False

    >>> is_simple_crds_mapping("jwst-operational")
    False

    >>> is_simple_crds_mapping("hst-foo")
    False
    """
    if isinstance(mapping, str):
        basename = os.path.basename(mapping)
        return is_valid_mapping_name(basename) and (locate_mapping(mapping) == locate_mapping(basename))
    else:
        return False

def is_valid_mapping_name(mapping):
    """Return True IFF `mapping` has a CRDS-style root name and a mapping extension."""
    return is_mapping(mapping) and bool(MAPPING_RE.match(mapping))

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

    >>> is_mapping_spec("jwst-miri-pars-tweakreg-2040-01-29T12:00:00")
    True

    >>> is_mapping_spec("jwst-miri-pars-tweakreg-edit")
    True

    >>> is_mapping_spec("2040-01-29T12:00:00")
    True

    >>> is_mapping_spec("hst-edit")
    True

    >>> is_mapping_spec("hst-cos-deadtab-edit")
    True

    >>> is_mapping_spec("jwst-operational")
    True

    >>> is_mapping_spec("hst-foo")
    False

    >>> is_mapping_spec("hst_wfc3_0001.imap")
    True
    """
    return is_mapping(mapping) or (isinstance(mapping, str) and bool(CONTEXT_RE.match(mapping)))

def is_context(mapping):
    """Return True IFF `mapping` has an extension indicating a CRDS CONTEXT, i.e. .pmap."""
    return isinstance(mapping, str) and mapping.endswith((".pmap",))

def is_context_spec(mapping):
    """Return True IFF `mapping` is a mapping name *or* a date based mapping specification.

    Date-based specifications can be interpreted by the CRDS server with respect to the operational
    context history to determine the default operational context which was in use at that date.
    This function verifies syntax only,  not the existence of corresponding context.

    >>> is_context_spec("hst_0042.pmap")
    True

    >>> is_context_spec("hst.pmap")
    True

    >>> is_context_spec("foo.pmap")
    True

    >>> is_context_spec("foo")
    False

    >>> is_context_spec("hst-edit")
    True

    >>> is_context_spec("hst-2040-01-29T12:00:00")
    True

    >>> is_context_spec("hst-acs-2040-01-29T12:00:00")
    False
    """
    return is_context(mapping) or (isinstance(mapping, str) and bool(PIPELINE_CONTEXT_RE.match(mapping)))

def is_date_based_mapping_spec(mapping):
    """Return True IFF `mapping` is a date based specification (not a filename).

    >>> is_date_based_mapping_spec("2040-01-29T12:00:00")
    True

    >>> is_date_based_mapping_spec("jwst-miri-pars-tweakreg-2040-01-29T12:00:00")
    True

    >>> is_date_based_mapping_spec("hst.pmap")
    False
    """
    return is_mapping_spec(mapping) and not is_mapping(mapping)

def locate_mapping(mappath, observatory=None):
    """Return the CRDS cache path for mapping `mappath` if it has no directory,
    otherwise returns mappath as-is.
    """
    if os.path.dirname(mappath):
        return mappath
    return relocate_mapping(mappath, observatory)

def relocate_mapping(mappath, observatory=None):
    """Return the CRDS cache path where CRDS mapping `mappath` should be
    be located,  replacing the path in `mappath` with the cache path.
    """
    if observatory is None:
        observatory = mapping_to_observatory(mappath)
    if mappath == "N/A":
        return mappath
    return os.path.join(get_crds_mappath(observatory), os.path.basename(mappath))

def mapping_exists(mapping):
    """Return True IFF `mapping` exists on the local file system."""
    return os.path.exists(locate_mapping(mapping))

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

# -------------------------------------------------------------------------------------
def is_config(filename):
    """Return True IFF `filename` names a CRDS configuration file."""
    filename = os.path.basename(filename)
    if filename in ["server_config"]:
        return True
    return False

# -------------------------------------------------------------------------------------
def is_pickle(filename):
    """Return True IFF `filename` names a CRDS pickle file."""
    filename = os.path.basename(filename)
    if filename.endswith(".pkl"):
        return True
    return False

# -------------------------------------------------------------------------------------

def get_crds_state():
    """Capture the current CRDS configuration and return it as a dictionary.
    Intended for customizing state during self-tests and restoring during teardown.
    """
    from .log import get_verbose
    env = { key : val for key, val in os.environ.items() if key.startswith("CRDS_") }
    env["CRDS_REF_SUBDIR_MODE"] = CRDS_REF_SUBDIR_MODE
    env["_CRDS_CACHE_READONLY"] = get_cache_readonly()
    env["PASS_INVALID_VALUES"] = PASS_INVALID_VALUES.get()
    env["CRDS_VERBOSITY"] = get_verbose()
    return env

def set_crds_state(old_state):
    """Restore the configuration of CRDS returned by get_crds_state()."""
    from crds.client import api   # deferred circular import
    from .log import set_verbose
    # determination of observatory and server URL are intertwined
    global CRDS_REF_SUBDIR_MODE, _CRDS_CACHE_READONLY
    clear_crds_state()
    log.set_verbose(old_state["CRDS_VERBOSITY"])
    _CRDS_CACHE_READONLY = old_state.pop("_CRDS_CACHE_READONLY")
    CRDS_REF_SUBDIR_MODE = old_state["CRDS_REF_SUBDIR_MODE"]
    for key, val in old_state.items():
        os.environ[key] = str(val)
    if os.environ.get("CRDS_SERVER_URL"):
        api.set_crds_server(os.environ["CRDS_SERVER_URL"])
    if os.environ.get("CRDS_CWD"):
        os.chdir(os.environ["CRDS_CWD"])

def clear_crds_state():
    """Wipe out the existing configuration variable state of CRDS.
    """
    global CRDS_REF_SUBDIR_MODE, _CRDS_CACHE_READONLY
    for var in list(os.environ.keys()):
        if var.startswith("CRDS_"):
            del os.environ[var]
    CRDS_REF_SUBDIR_MODE = "None"
    _CRDS_CACHE_READONLY = False

# -------------------------------------------------------------------------------------
# Identifier used  to connect to remote status channels to monitor submission status, etc.

PROCESS_KEY_RE_STR = r"[a-zA-Z0-9:\.\-]{1,128}"   #  character "/" must be excluded
PROCESS_KEY_RE = re.compile(complete_re(PROCESS_KEY_RE_STR))

USER_NAME_RE_STR = r"[a-z_]+"
USER_NAME_RE = re.compile(complete_re(USER_NAME_RE_STR))

# -------------------------------------------------------------------------------------

# approximate regex to validate semver.org version numbers.

VERSION_RE_STR = complete_re(
    r"(\d{1,8}(\.\d{1,8}(\.\d{1,8})?)?)[a-zA-Z0-9_\+\-\.]{0,128}")
VERSION_RE = re.compile(VERSION_RE_STR)

def simplify_version(version):
    """
    >>> simplify_version('0.13.2a.dev185+gdb49aea9')
    '0.13.2'
    >>> simplify_version('0.7.8rc1.dev305')
    '0.7.8'
    >>> simplify_version('0.7.8')
    '0.7.8'
    >>> simplify_version('0.7')
    '0.7'
    >>> simplify_version('0')
    '0'
    >>> simplify_version('0.foo')
    '0'
    """
    return VERSION_RE.match(version).group(1)

# -------------------------------------------------------------------------------------

# These configure CRDS to stream mappings directly from S3 and return s3:// URLs to
# reference files.  It is expected that the files be stored on S3 in the "flat" structure
# (no instrument in the key).

S3_ENABLED = BooleanConfigItem("CRDS_S3_ENABLED", False, "When True, enables S3 streaming")

S3_RETURN_URI = BooleanConfigItem("CRDS_S3_RETURN_URI", False, "When True, getreferences() returns S3 URIs instead of cache paths.")

OBSERVATORY = StrConfigItem("CRDS_OBSERVATORY", None,
    "Configured observatory, required for S3 streaming",
    lower=True
)

# -------------------------------------------------------------------------------------
def get_uri(filename):
    """Return an appropriate s3:// or https:// URI for the specified filename based
    on optional CRDS config variables:

    CRDS_CONFIG_URI
    CRDS_MAPPING_URI
    CRDS_REFERENCE_URI
    CRDS_PICKLE_URI

    If the appropriate env var is not defined,  return "none".
    """
    if is_exception_condition(filename):
        return filename
    elif is_config(filename):
        uri = CRDS_CONFIG_URI.get()
    elif is_pickle(filename):
        uri = CRDS_PICKLE_URI.get()
    elif is_mapping(filename):
        uri = CRDS_MAPPING_URI.get()
    elif is_reference(filename):
        uri = CRDS_REFERENCE_URI.get()
    else:
        raise exceptions.CrdsError(f"Uknown file type for: '{filename}'")
    if uri == "none":
        return  uri
    else:
        if not uri.endswith("/"):
            uri += "/"
        uri += filename
        return uri

def is_exception_condition(filename):
    """Return True IFF `filename` describes some form of error or warning condition
    instead of a true filename.
    """
    return filename.upper().startswith("NOT FOUND")

# -------------------------------------------------------------------------------------

def test():
    """Run doctests on crds.config module."""
    import doctest
    from . import config
    return doctest.testmod(config)

if __name__ ==  "__main__":
    print(test())
