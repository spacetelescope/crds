"""This module is the interface to CRDS configuration information.  Predominantly
it is used to define CRDS file cache paths and file location functions.
"""

import os
import os.path
import re

# ===========================================================================

DEFAULT_CRDS_DIR = "/grp/crds/jwst"

def get_crds_path():
    """Return the root directory of the CRDS cache."""
    return os.environ.get("CRDS_PATH", DEFAULT_CRDS_DIR)

# ===========================================================================

def get_crds_mappath():
    """get_crds_mappath() returns the base path of the CRDS mapping directory 
    tree where CRDS rules files (mappings) are stored.   This is extended by
    <observatory> once it is known.
    
    DEPRECATED:  only use in the config module.  Use locate_file() or locate_mapping() instead.
    """
    try:
        return os.environ["CRDS_MAPPATH"]
    except KeyError:
        return  get_crds_path() + "/mappings"

def get_crds_refpath():
    """get_crds_refpath returns the base path of the directory tree where CRDS 
    reference files are stored.   This is extended by <observatory> once it is
    known.
    
    DEPRECATED: only use in config module.  Use locate_file() or locate_reference() instead.
    """
    try:
        return os.environ["CRDS_REFPATH"]
    except KeyError:
        return get_crds_path() + "/references"

def get_crds_config_path():
    """Return the path to a writable directory used to store configuration info
    such as last known server status.   This is extended by <observatory> once
    it is known.   If CRDS_PATH doesn't point to a writable directory, then
    CRDS_CFGPATH should be defined.
    """
    try:
        return os.environ["CRDS_CFGPATH"]
    except KeyError:
        return get_crds_path() + "/config"

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
    return bool(os.environ.get("CRDS_IGNORE_MAPPING_CHECKSUM", False))

# ===========================================================================

def get_crds_env_vars():
    """Return a dictionary of all env vars starting with 'CRDS'."""
    vars = {}
    for var in os.environ:
        if var.upper().startswith("CRDS"):
            vars[var] = os.environ[var]
    return vars

# ===========================================================================

def get_path(filename, observatory):
    """Return the CRDS cache path of `filename` for `observatory`.   The path is
    similar to the one from locate_file(),  but includes dirname only,  not `filename` itself.
    """
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
    return os.path.join(get_crds_refpath(), observatory, cfg)

def locate_reference(ref, observatory):
    """Return the absolute path where reference `ref` should be located."""
    if os.path.dirname(ref):
        return ref
    return os.path.join(get_crds_refpath(), observatory, ref)

def is_mapping(mapping):
    """Return True IFF `mapping` has an extension indicating a CRDS mapping 
    file.
    """
    return isinstance(mapping, basestring) and mapping.endswith((".pmap", ".imap", ".rmap"))

def get_sqlite3_db_path(observatory):
    return locate_config("crds_db.sqlite3", observatory)

# -------------------------------------------------------------------------------------

# e.g.  hst, hst-acs, hst-acs-darkfile
CONTEXT_OBS_INSTR_KIND_RE_STR = r"[a-z]+(\-[a-z]+(\-[a-z]+)?)?" 

# Standard date time format using T separator for command line use specifying contexts.
# e.g. 2040-02-22T12:01:30.4567
CONTEXT_DATETIME_RE_STR = r"\d\d\d\d\-\d\d\-\d\dT\d\d:\d\d:\d\d(\.\d+)?"
CONTEXT_DATETIME_RE = re.compile(CONTEXT_DATETIME_RE_STR)

# e.g.   2040-02-22T12:01:30.4567,  hst-2040-02-22T12:01:30.4567, hst-acs-2040-02-22T12:01:30.4567, ...
CONTEXT_RE_STR = r"(?P<context>" + CONTEXT_OBS_INSTR_KIND_RE_STR + r"\-)?((?P<date>" + CONTEXT_DATETIME_RE_STR + r"|edit|operational))"
CONTEXT_RE = re.compile(CONTEXT_RE_STR)

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
    return re.match(".fits|.finf|.r\dh", extension) is not None

def locate_mapping(mappath, observatory=None):
    """Return the path where CRDS mapping `mappath` should be."""
    if os.path.dirname(mappath):
        return mappath
    if observatory is None:
        observatory = mapping_to_observatory(mappath)
    return os.path.join(get_crds_mappath(), observatory, mappath)

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
    import doctest
    from . import config
    return doctest.testmod(config)

