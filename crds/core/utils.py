"""Generic utility routines used by a variety of modules."""

#  XXXX lots of bogus pylint warnings here,  verify before removing imports.

import sys
import os   # False pylint warning unused import,  verify before removing.
import os.path
import shutil  # False pylint warning unused import,  verify before removing.
import stat
import re
import hashlib
import io
import functools
from collections import Counter, defaultdict
import datetime
import ast
import gc
import json
import warnings

# ===================================================================

# import yaml

# ===================================================================

# from crds import data_file,  import deferred until required

from . import log, config, pysh, exceptions
from .constants import ALL_OBSERVATORIES, INSTRUMENT_KEYWORDS

# from crds.client import api  # deferred import below to simplify basic dependencies

# ===================================================================

def deprecate(deprecated, after_date, alternative):
    """Issue a standard deprecation warning for `deprecated` feature
    (e.g. function name) to be removed `after_date` with suggested
    `alternative` feature as the replacement functionality.
    """
    message = f"Feature {deprecated} has been deprecated " \
              f"and will be removed sometime after {after_date}. " \
              f"Feature {alternative} provides alternative functionality."
    warnings.warn(message, DeprecationWarning)

# ===================================================================

class Struct(dict):
    """A dictionary which supports dotted access to members."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, val):
        self[name] = val

# ===================================================================

def combine_dicts(*post_dicts, **post_vars):
    """Combine positional parameters (dictionaries) and individual
    variables specified by keyword into a single parameter dict.
    """
    vars = dict()
    for pars in post_dicts:
        vars.update(pars)
    vars.update(post_vars)
    return vars

# ===================================================================

def trace_compare(self, other, show_equal=False):
    """Recursively compare object `self` to `other` printing differences
    and optionally equal members.
    """
    log.divider(repr(self) + ":")
    for key, value in self.__dict__.items():
        try:
            ovalue = other.__dict__[key]
        except KeyError:
            print(key, "not present in other")
            continue
        equal = (value == ovalue)
        if show_equal or not equal:
            print(key, equal, value, ovalue)
        if hasattr(value, "_trace_compare"):
            value._trace_compare(ovalue)
    for key in other.__dict__:
        try:
            self.__dict__[key]
        except KeyError:
            print(key, "value not present in self")

# ===================================================================

def flatten(sequence):
    """Given a sequence possibly containing nested lists or tuples,
    flatten the sequence to a single non-nested list of primitives.

    >>> flatten((('META.INSTRUMENT.DETECTOR', 'META.SUBARRAY.NAME'), ('META.OBSERVATION.DATE', 'META.OBSERVATION.TIME')))
    ['META.INSTRUMENT.DETECTOR', 'META.SUBARRAY.NAME', 'META.OBSERVATION.DATE', 'META.OBSERVATION.TIME']
    """
    flattened = []
    for elem in sequence:
        if isinstance(elem, (list, tuple)):
            elem = flatten(elem)
        else:
            elem = [elem]
        flattened.extend(elem)
    return flattened

# ===================================================================

def traced(func):
    """Issue a verbose message showing parameters and possibly return val."""
    @functools.wraps(func)
    def func2(*args, **keys):
        "Decoration wrapper for @trace."
        log.verbose("trace:", func.__name__, args if args else "", keys if keys else "", verbosity=55)
        result = func(*args, **keys)
        log.verbose("trace result:", func.__name__, ":", result, verbosity=55)
        return result
    func2.__name__ = func.__name__ + " [traced]"
    func2.__doc__ = func.__doc__
    func2._traced = True
    return func2

# ===================================================================

def gc_collected(func):
    """Run Python's gc.collect() before and after the decorated function.

    This is pretty slow and may be overkill but was motivated by file
    submission use cases such as "certify" and "insert_references" which
    iterate over large numbers of reference files and,  particularly when
    examining arrays,  may easily exhaust memory,  sometimes leading to
    silent OS or shell level crashes with no traceback.
    """
    @functools.wraps(func)
    def func2(*args, **keys):
        "Decoration wrapper for @gc_collected."
        if config.EXPLICIT_GARBAGE_COLLECTION:
            gc.collect()
        result = None
        try:
            result = func(*args, **keys)
        finally:
            if config.EXPLICIT_GARBAGE_COLLECTION:
                gc.collect()
        return result
    func2.__name__ = func.__name__ + " [gc_collected]"
    func2.__doc__ = func.__doc__
    func2._gc_collected = True
    return func2

# ===================================================================

def cached(func):
    """The cached decorator embeds a dictionary in a function wrapper to
    capture prior results.

    The wrapped function works like the original, except it's faster because it
    fetches results for prior calls from the cache.   The wrapped function has
    extra attributes:

    .cache                      -- { key(parameters): old_result } dictionary
    .uncached(*args, **keys)    -- original unwrapped function
    .readonly(*args, **keys)    -- function variant which uses but doesn't update cache
    .cache_key(*args, **keys)   -- returns tuple used to locate a function call result

    >>> @cached
    ... def sum(x,y):
    ...   print("really doing it.")
    ...   return x+y

    The first call should actually call the unwrapped sum():

    >>> sum(1,2)
    really doing it.
    3

    The second call will return the prior result found in the cache:

    >>> sum(1,2)
    3

    Dump or operate on the cache like this, it's just a dict:

    >>> sum.cache
    {(1, 2): 3}

    By-pass the cache and call the undecorated function like this:

    >>> sum.uncached(1,2)
    really doing it.
    3

    Clear the cache like this:

    >>> sum.cache.clear()
    >>> sum(1,2)
    really doing it.
    3

    A variant of the function which reads but does not update the cache is available.
    After calling the read_only variant the cache is not updated:

    >>> sum.cache.clear()
    >>> sum.readonly(1,2)
    really doing it.
    3
    >>> sum(1,2)
    really doing it.
    3

    However,  the readonly variant will exploit any values in the cache already:

    >>> sum(1,2)
    3
    """
    return CachedFunction(func)

class xcached:
    """Caching decorator which supports auxilliary caching parameters.

    omit_from_key lists keywords or positional indices to be excluded from cache
    key creation:

    >>> @xcached(omit_from_key=[0, "x"])
    ... def sum(x, y, z):
    ...     return x + y + z

    >>> sum(1,2,3)
    6

    >>> sum(2,2,3)
    6

    >>> sum.uncached(2,2,3)
    7

    >>> sum.readonly(2,2,3)
    6
    """
    def __init__(self, *args, **keys):
        """Stash the decorator parameters"""
        self.args = args
        self.keys = keys

    def __call__(self, func):
        """Create a CachedFunction for `func` with extra qualifiers *args and **keys.
        Nomnially executes at import time.
        """
        cached = CachedFunction(func, *self.args, **self.keys)
        cached.__name__ = cached.uncached.__name__ + " [xcached]"
        cached.__doc__ = cached.uncached.__doc__
        return cached

class CachedFunction:
    """Class to support the @cached function decorator.   Called at runtime
    for typical caching version of function.
    """

    cache_set = set()

    def __init__(self, func, omit_from_key=None):
        self.cache = dict()
        self.uncached = func
        self.omit_from_key = [] if omit_from_key is None else omit_from_key
        self.cache_set.add(self)
        self.__doc__ = self.uncached.__doc__
        self.__module__ = self.uncached.__module__
        self.__name__ = self.uncached.__name__ + " [cached]"

    def cache_key(self, *args, **keys):
        """Compute the cache key for the given parameters."""
        args = tuple([ a for (i, a) in enumerate(args) if i not in self.omit_from_key])
        keys = tuple([item for item in keys.items() if item[0] not in self.omit_from_key])
        return args + keys

    def _readonly(self, *args, **keys):
        """Compute (cache_key, func(*args, **keys)).   Do not add to cache."""
        key = self.cache_key(*args, **keys)
        if key in self.cache:
            log.verbose("Cached call", self.uncached.__name__, repr(key), verbosity=80)
            return key, self.cache[key]
        else:
            log.verbose("Uncached call", self.uncached.__name__, repr(key), verbosity=80)
            return key, self.uncached(*args, **keys)

    def readonly(self, *args, **keys):
        """Compute or fetch func(*args, **keys) but do not add to cache.
        Return func(*args, **keys)
        """
        _key, result = self._readonly(*args, **keys)
        return result

    def __call__(self, *args, **keys):
        """Compute or fetch func(*args, **keys).  Add the result to the cache.
        return func(*args, **keys)
        """
        key, result = self._readonly(*args, **keys)
        self.cache[key] = result
        return result

    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        return functools.partial(self.__call__, obj)

def clear_function_caches():
    "Clear all the caches created using @utils.cached or @utils.xcached."""
    for cache_func in CachedFunction.cache_set:
        log.verbose("Clearing cache for", repr(cache_func.uncached), verbosity=80)
        cache_func.cache = dict()

def list_cached_functions():
    """List all the functions supporting caching under @utils.cached or @utils.xcached."""
    for cache_func in sorted(CachedFunction.cache_set):
        print(repr(cache_func.uncached))

# ===================================================================

def capture_output(func):
    """Decorate a function with @capture_output to define a CapturedFunction()
    wrapper around it.

    Doesn't currently capture non-python output but could with dup2.

    Decorate any function to wrap it in a CapturedFunction() wrapper:

    >>> @capture_output
    ... def f(x,y):
    ...    print("hi")
    ...    return x + y

    >>> f
    CapturedFunction('f')

    Calling a captured function suppresses its output:

    >>> f(1, 2)
    3

    To call the original undecorated function:

    >>> f.uncaptured(1, 2)
    hi
    3

    If you don't care about the return value,  but want the output:

    >>> f.outputs(1, 2) == 'hi\\n'
    True

    If you need both the return value and captured output:

    >>> f.returns_outputs(1, 2) == (3, 'hi\\n')
    True

    """
    class CapturedFunction:
        """Closure on `func` which supports various forms of output capture."""

        def __repr__(self):
            return "CapturedFunction('%s')" % func.__name__

        def returns_outputs(self, *args, **keys):
            """Call the wrapped function,  capture output,  return (f(), output_from_f)."""
            sys.stdout.flush()
            sys.stderr.flush()
            oldout, olderr = sys.stdout, sys.stderr
            if sys.version_info < (3,0,0):
                out = io.BytesIO()
            else:
                out = io.TextIOWrapper(io.BytesIO())
            sys.stdout, sys.stderr = out, out
            try:
                result = func(*args, **keys)
                out.flush()
                out.seek(0)
                return result, out.read()
            finally:
                sys.stdout, sys.stderr = oldout, olderr

        def suppressed(self, *args, **keys):
            """Call the wrapped function, suppress output,  return f() normally."""
            return self.returns_outputs(*args, **keys)[0]

        def outputs(self, *args, **keys):
            """Call the wrapped function, capture output,  return output_from_f."""
            return self.returns_outputs(*args, **keys)[1]

        def __call__(self, *args, **keys):
            """Call the undecorated function,  capturing and discarding it's output,  returning the result."""
            return self.suppressed(*args, **keys)

        def uncaptured(self, *args, **keys):
            """Call the undecorated function and return the result."""
            return func(*args, **keys)

    return CapturedFunction()

# ===================================================================

def compare_dicts(dict1, dict2):
    """Compare two dictionaries and return a dictionary of added, deleted, and replaced items."""
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return (dict1, dict2)
    deleted = { key: dict1[key] for key in dict1 if key not in dict2 }
    added = { key: dict2[key] for key in dict2 if key not in dict1 }
    replaced = { key: compare_dicts(dict1[key], dict2[key]) for key in dict1 if key in dict2 and dict1[key] != dict2[key] }
    return dict(deleted=deleted, added=added, replaced=replaced)

# ===================================================================

class TimingStats:
    """Track and compute counts and counts per second."""
    def __init__(self, output=None):
        self.counts = Counter()
        self.started = None
        self.stopped = None
        self.elapsed = None
        self.output = log.info if output is None else output
        self.start()

    def get_stat(self, name):
        """Return the value of statistic `name`."""
        return self.counts[name]

    def increment(self, name, amount=1):
        """Add `amount` to stat count for `name`."""
        self.counts[name] += amount

    def start(self):
        """Start the timing interval."""
        self.started = datetime.datetime.now()
        return self

    def stop(self):
        """Stop the timing interval."""
        self.stopped = datetime.datetime.now()
        self.elapsed = self.stopped - self.started

    def report(self):
        """Output all stats."""
        if not self.stopped:
            self.stop()
        self.msg("STARTED", str(self.started)[:-4])
        self.msg("STOPPED", str(self.stopped)[:-4])
        self.msg("ELAPSED", str(self.elapsed)[:-4])
        for kind in self.counts:
            self.report_stat(kind)

    def report_stat(self, name):
        """Output stats on `name`."""
        count, rate = self.status(name)
        self.msg(count, "at", rate)

    def raw_status(self, name):
        self.stop()
        counts = self.counts[name]
        rate = self.counts[name] / self.elapsed.total_seconds()
        return counts, rate

    def status(self, name):
        """Return human readable (count, rate) for `name`."""
        counts, rate = self.raw_status(name)
        count_str = human_format_number(counts) + " " + name
        rate_str = human_format_number(rate) + " " + name + "-per-second"
        return count_str, rate_str

    def log_status(self, name, intro, total=None):
        """Do log output about stat `name` using `intro` as the descriptive lead-in to
        the stats.
        """
        stat, stat_per_sec = self.raw_status(name)
        if total is not None:
            self.msg(intro, "[",
                     human_format_number(stat), "/",
                     human_format_number(total), name, "]",
                     "[",
                     human_format_number(stat_per_sec), name + "-per-second ]")
        else:
            self.msg(intro,
                     "[", human_format_number(stat), name, "]",
                     "[", human_format_number(stat_per_sec), name + "-per-second ]")

    def msg(self, *args):
        """Format (*args, **keys) using log.format() and call output()."""
        self.output(*args, eol="")

# ===================================================================

def total_size(filepaths):
    """Return the total size of all files in `filepaths` as an integer."""
    return sum([os.stat(filename).st_size for filename in filepaths])

# ===================================================================

def file_size(filepath):
    """Return the size of `filepath` as an integer."""
    return os.stat(filepath).st_size

# ===================================================================

def elapsed_time(func):
    """Decorator to report on elapsed time for a function call."""
    def elapsed_wrapper(*args, **keys):
        stats = TimingStats()
        stats.start()
        result = func(*args, **keys)
        stats.stop()
        stats.msg("Timing for", repr(func.__name__))
        stats.report()
        return result
    elapsed_wrapper.__name__ = func.__name__ + "[elapsed_time]"
    elapsed_wrapper.__doc__ = func.__doc__
    return elapsed_wrapper

# ===================================================================

def human_format_number(number):
    """Reformat `number` by switching to engineering units and dropping to two fractional digits,
    10s of megs for G-scale files.
    """
    convert = [
        (1e12, "T"),
        (1e9 , "G"),
        (1e6 , "M"),
        (1e3 , "K"),
        ]
    for limit, sym in convert:
        if isinstance(number, (float, int)) and number > limit:
            number /= limit
            break
    else:
        sym = ""
    if isinstance(number, int):
        # numstr = "%d" % number
        numstr = "{}".format(number)
    else:
        numstr = "{:0.1f} {}".format(number, sym)
    return "{!s:>7}".format(numstr)

# ===================================================================

def invert_dict(dictionary):
    """Return the functional inverse of a dictionary,  raising an exception
    for values in `d` which map to more than one key producing an undefined
    inverse.
    """
    inverse = {}
    for key, value in dictionary.items():
        if value in inverse and inverse[value] != key:
            raise ValueError("Undefined inverse because of duplicates for " +
                             repr(value) + " of " + repr(key) + " vs. " +
                             repr(inverse[value]))
        inverse[value] = key
    return inverse

# ===================================================================

def evalfile(fname):
    """Evaluate and return the contents of file `fname`,  restricting
    expressions to data literals.
    """
    with open(fname) as sourcefile:
        contents = sourcefile.read()
    return ast.literal_eval(contents)

# ===================================================================

UMASK = 0o002
with log.verbose_warning_on_exception("Failed determining UMASK"):
    UMASK = os.umask(0)
    os.umask(UMASK)

DEFAULT_DIR_PERMS = ~UMASK & 0o777

def create_path(path, mode=DEFAULT_DIR_PERMS):
    """Recursively traverses directory path creating directories as
    needed so that the entire path exists.
    """
    path = os.path.abspath(path)
    if os.path.exists(path):
        return
    current = []
    for part in path.split("/"):
        if not part:
            current.append("/")
            continue
        current.append(str(part))
        subdir = os.path.abspath(os.path.join(*current))
        if not os.path.exists(subdir):
            log.verbose("Creating", repr(subdir), "with permissions %o" % mode)
            os.mkdir(subdir, mode)
            with log.verbose_warning_on_exception(
                    "Failed chmod'ing new directory", repr(subdir), "to %o." % mode):
                os.chmod(subdir, mode)

def ensure_dir_exists(fullpath, mode=DEFAULT_DIR_PERMS):
    """Creates dirs from `fullpath` if they don't already exist.  fullpath
    is assumed to include a filename which will not be created.
    """
    create_path(os.path.dirname(fullpath), mode)

# ===================================================================

def is_writable(filepath, no_exist=True):
    """Interpret the mode bits of `filepath` in terms of the current user and it's groups,
    returning True if any of user, group, or other have write permission on the path.

    If `filepath` doesn't exist,  return `no_exist` if the directory is writable.
    """
    if not os.path.exists(filepath):   # If file doesn't exist,  make sure directory is writable.
        return no_exist and len(os.path.dirname(filepath)) and is_writable(os.path.dirname(filepath))
    stats = os.stat(filepath)
    user_writeable = bool(stats.st_mode & stat.S_IWUSR)
    effective_user_matches =  bool(stats.st_uid == os.geteuid())
    group_writeable = bool(stats.st_mode & stat.S_IWGRP)
    group_matches = bool(stats.st_gid in os.getgroups())
    other_writeable = bool(stats.st_mode & stat.S_IWOTH)
    return bool((user_writeable and effective_user_matches) or
                (group_writeable and group_matches) or
                (other_writeable))

# ===================================================================

def remove(rmpath, observatory):
    """Wipe out directory at 'rmpath' somewhere in cache for `observatory`."""
    if config.writable_cache_or_verbose("Skipped removing", repr(rmpath)):
        with log.error_on_exception("Failed removing", repr(rmpath)):
            abs_path = os.path.abspath(rmpath)
            abs_cache = os.path.abspath(config.get_crds_path())
            abs_config = os.path.abspath(config.get_crds_cfgpath(observatory))
            abs_root_config = os.path.abspath(config.get_crds_root_cfgpath())
            abs_references = os.path.abspath(config.get_crds_refpath(observatory))
            abs_mappings = os.path.abspath(config.get_crds_mappath(observatory))
            abs_pickles = os.path.abspath(config.get_crds_picklepath(observatory))
            assert abs_path.startswith((abs_cache, abs_config, abs_root_config,
                                        abs_references, abs_mappings, abs_pickles)), \
                "remove() only works on files in CRDS cache. not: " + repr(rmpath)
            log.verbose("CACHE removing:", repr(rmpath))
            if os.path.isfile(rmpath):
                os.remove(rmpath)
            else:
                pysh.sh("rm -rf ${rmpath}", raise_on_error=True)

# ===================================================================

def _no_message(*args):
    """Do nothing message handler."""

def copytree(src, dst, symlinks=False, fnc_directory=_no_message,
             fnc_file=_no_message, fnc_symlink=_no_message):
    """Derived from shutil.copytree() example with added function hooks called
    on a per-directory, per-file, and per-symlink basis with (src, dest)
    parameters.  Removes exception trapping since partial copies are useless
    for CRDS.  Cannot handle devices or sockets, only regular files and
    directories.   File stats not preserved.
    """
    os.makedirs(dst)
    for name in os.listdir(src):
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        if symlinks and os.path.islink(srcname):
            linkto = os.readlink(srcname)
            fnc_symlink("Linking", log.srepr(linkto), "to", log.srepr(dstname))
            os.symlink(linkto, dstname)
        elif os.path.isdir(srcname):
            fnc_directory("Copying dir", log.srepr(srcname), "to", log.srepr(dstname))
            copytree(srcname, dstname, symlinks)
        else:
            fnc_file("Coping", log.srepr(srcname), "to", log.srepr(dstname))
            shutil.copy(srcname, dstname)

# ===================================================================

def get_s3_uri_content(s3_uri, mode="text"):
    """Perform a direct read of an AWS S3 URI using the AWS SDK.

    Returns  contents of `s3_uri`.
    """
    log.verbose(f"Fetching content from URI: '{s3_uri}'")
    bucket_name, key = s3_uri.replace("s3://", "").split("/", 1)
    import boto3
    s3 = boto3.resource("s3")
    obj = s3.Object(bucket_name, key)
    binary = obj.get()["Body"].read()
    if mode == "text":
        text = binary.decode("utf-8")
        return text
    return binary

def get_url_content(url, mode="text"):
    """Return the contents of `url` as a string."""
    log.verbose(f"Fetching content from URL: '{url}'")
    import requests
    r = requests.get(url)
    r.raise_for_status()
    if mode == "text":
        return r.text
    return r.content

def get_uri_content(uri, mode="text"):
    """Reads and returns the contents of the given s3://, https://
    or filename uri.   Reads to memory, intended for small files.
    """
    if uri.startswith("s3://"):
        return get_s3_uri_content(uri, mode)
    elif uri.startswith(("http://", "https://")):
        return get_url_content(uri, mode)
    else:
        mode = "r" if (mode=="text") else "rb"
        with open(uri, mode) as file:
            return file.read()

# ===================================================================

def checksum(pathname):
    """Return the CRDS hexdigest for file at `pathname`.   See also
    copy_and_checksum() below which must match sha1sum results.
    """
    xsum = hashlib.sha1()
    with open(pathname, "rb") as infile:
        size = 0
        insize = os.stat(pathname).st_size
        while size < insize:
            block = infile.read(config.CRDS_CHECKSUM_BLOCK_SIZE)
            size += len(block)
            xsum.update(block)
    return xsum.hexdigest()

def copy_and_checksum(source, destination):
    """Copy file from `source` path to `destination` path computing
    sha1sum of source during the copy.   This is a *gross* server-side
    optimization to prevent copying 10's of G's of data and then reading
    it back just to compute sha1sum.   This is necessitated because it's
    not possible to take ownership of files you can both read and delete
    but it is possible to make a personally owned copy which replaces the
    original.  See also checksum() which must have matching results.
    """
    xsum = hashlib.sha1()
    with open(source, "rb") as source_file:
        with open(destination, "wb+") as destination_file:
            size = 0
            insize = os.stat(source).st_size
            while size < insize:
                block = source_file.read(config.CRDS_CHECKSUM_BLOCK_SIZE)
                destination_file.write(block)
                size += len(block)
                xsum.update(block)
    return xsum.hexdigest()

def str_checksum(data):
    """Return the CRDS hexdigest for small strings.   Likewise,  must
    match checksum() and copy_and_checksum() above.

    >>> str_checksum("this is a test.")
    '7728f8eb7bf75ec3cc49364861eec852fc814870'

    """
    if not isinstance(data, bytes):
        data = data.encode("utf-8")
    xsum = hashlib.sha1()
    xsum.update(data)
    return xsum.hexdigest()

# ===================================================================

def get_file_properties(observatory, filename):
    """Return instrument,filekind fields associated with filename."""
    path = config.locate_file(filename, observatory)
    try:
        return get_locator_module(observatory).get_file_properties(path)
    except Exception as exc:
        raise exceptions.FilePropertiesError(f"Failed to determine '{observatory}' instrument or reftype for '{filename}' : '{str(exc)}'") from exc

def get_instruments_filekinds(observatory, filepaths):
    """Given a list of filepaths return the mapping of instruments and
    filekinds covered by the files.
    """
    itmapping = defaultdict(set)
    for filepath in filepaths:
        instrument, filekind = get_file_properties(observatory, filepath)
        itmapping[instrument] |= set([filekind])
    return { instr : sorted([filekind for filekind in itmapping[instr]]) for instr in  itmapping}

def organize_files(observatory, files):
    """Given and `observatory` name and list of `files`, return a dictionary
    that partitions `files` into lists based upon common instrument and
    filekind.

    Returns:  { (instrument, filekind) : [ file1, file4, ...], ... }
    """
    organized = defaultdict(list)
    for file_ in files:
        instrument, filekind = get_file_properties(observatory, file_)
        organized[(instrument,filekind)].append(file_)
    return dict(organized)

# ===================================================================

MODULE_PATH_RE = re.compile(r"^crds(_server)?(\.\w{1,64}){0,10}$")

@cached
def get_object(*args):
    """Import the given `dotted_name` and return the object.

    >>> rmap = get_object("crds.rmap")
    >>> fail = get_object("crds.rmap; eval('2+2')")
    Traceback (most recent call last):
    ...
    AssertionError: Invalid dotted name for get_object() : "crds.rmap; eval('2+2')"
    >>> rmap = get_object("crds","rmap")
    """
    dotted_name = ".".join(args)
    assert MODULE_PATH_RE.match(dotted_name), \
        "Invalid dotted name for get_object() : " + repr(dotted_name)
    parts = dotted_name.split(".")
    pkgpath = ".".join(parts[:-1])
    cls = parts[-1]
    namespace = {}
    import_cmd = "from " + pkgpath + " import " + cls
    with log.augment_exception("Error importing", repr(import_cmd)):
        exec(import_cmd, namespace, namespace)
        return namespace[cls]

# ==============================================================================

DONT_CARE_RE = re.compile(r"^" + r"|".join([
    # "-999","-999\.0",
    # "4294966297.0",
    r"-2147483648.0",
    r"\(\)","N/A","NOT APPLICABLE", "NOT_APPLICABLE"]) + "$")

NUMBER_RE = re.compile(r"^([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?|[+-]?[0-9]+\.)$")

def condition_value(value):
    """Condition `value`,  ostensibly taken from a FITS header or CDBS
    reference file table,  such that it is suitable for appearing in or
    matching an rmap MatchSelector key.

    >>> condition_value('ANY')
    '*'

    # >>> condition_value('-999')
    'N/A'
    # >>> condition_value('-999.0')
    'N/A'
    # >> condition_value('4294966297.0')   # -999
    'N/A'

    >>> condition_value('N/A')
    'N/A'
    >>> condition_value('NOT APPLICABLE')
    'N/A'
    >>> condition_value('NOT_APPLICABLE')
    'N/A'

    >> condition_value('')
    'N/A'

    >>> condition_value('4294967295')
    '-1.0'

    >>> condition_value(False)
    'F'
    >>> condition_value(True)
    'T'

    >>> condition_value(1)
    '1.0'
    >>> condition_value('-9')
    '-9.0'
    >>> condition_value('1.0')
    '1.0'
    >>> condition_value('1.')
    '1.0'

    >>> condition_value('foo')
    'FOO'

    >>> condition_value('iref$uaf12559i_drk.fits')
    'IREF$UAF12559I_DRK.FITS'

    >>> condition_value('2013-11-05 15:21:34')
    '2013-11-05 15:21:34'
    """
    value = str(value).strip().upper()
    if NUMBER_RE.match(value):
        value = str(float(value))
    if DONT_CARE_RE.match(value):
        value = "N/A"
    if value == "ANY":
        value = "*"
    elif value == "4294967295.0":
        value = "-1.0"
    elif value in ["T", "TRUE"]:
        value = "T"
    elif value in ["F", "FALSE"]:
        value = "F"
    return value

def condition_header(header, needed_keys=None):
    """Return a dictionary of all `needed_keys` from `header` after passing
    their values through the CRDS value conditioner.
    """
    header = { key.upper():val for (key, val) in header.items() }
    if not needed_keys:
        needed_keys = header.keys()
    else:
        needed_keys = [ key.upper() for key in needed_keys ]
    conditioned = { key:condition_value(header[key]) for key in needed_keys }
    return conditioned

def _eval_keys(keys):
    """Return the replacement mapping from rmap-visible parkeys to eval-able keys.

    >>> _eval_keys(("META.INSTRUMENT.NAME",))
    {'META.INSTRUMENT.NAME': 'META_INSTRUMENT_NAME'}

    """
    evalable_map = {}
    for key in keys:
        replacement = key.replace(".", "_")
        if replacement != key:
            evalable_map[key] = replacement
    return evalable_map

def condition_header_keys(header):
    """Convert a matching parameter header into the form which supports eval(), ie.
    JWST-style header keys.   Nominally for JWST data model style keys.

    >>> from pprint import pprint as pp
    >>> pp(condition_header_keys({"META.INSTRUMENT.NAME": "NIRISS"}))
    {'META.INSTRUMENT.NAME': 'NIRISS', 'META_INSTRUMENT_NAME': 'NIRISS'}

    """
    header = dict(header)
    evalable_map = _eval_keys(header.keys())
    if evalable_map:
        header.update({ evalable_map[key] : header[key] for key in evalable_map })
    return header

def condition_source_code_keys(code, parkeys):
    """Convert source code expressed in terms of parkeys into source code which works
    with the evalable form of the parkey.   Nominally for JWST data model style keys.

    >>> condition_source_code_keys('META.INSTRUMENT.NAME != "MIRI"', ('META.INSTRUMENT.NAME',))
    'META_INSTRUMENT_NAME != "MIRI"'

    """
    evalable_map = _eval_keys(parkeys)
    for key, replacement in evalable_map.items():
        code = code.replace(key, replacement)
    return code

# ==============================================================================

# Since this imports all observatory packages,  better to cache than put in global.
@cached
def observatory_instrument_tuples():
    """Yield all the installed tuples of (observatory, instrument) available."""
    tuples = []
    for obs in ALL_OBSERVATORIES:
        try:
            instruments = get_object("crds." + obs + ".INSTRUMENTS")
        except ImportError:
            continue
        for instr in instruments:
            tuples.append((obs, instr))
    return tuples

def file_to_observatory(filename):
    """Return the observatory corresponding to reference, mapping, or dataset `filename`."""
    basename = os.path.basename(filename).lower()
    for obs in ALL_OBSERVATORIES:
        if basename.startswith(obs + "_") or (("_" + obs + ".") in basename) or (basename == obs + ".pmap"):
            return obs
    else:
        return instrument_to_observatory(file_to_instrument(filename))

@cached
def instrument_to_observatory(instrument):
    """Given the name of an instrument,  return the associated observatory.

    >>> instrument_to_observatory("acs")
    'hst'
    >>> instrument_to_observatory("ACS")
    'hst'
    >>> instrument_to_observatory("miri")
    'jwst'
    >>> instrument_to_observatory("foo")
    Traceback (most recent call last):
    ...
    ValueError: Unknown instrument 'foo'
    """
    instrument = fix_instrument(instrument.lower())
    for (obs, instr) in observatory_instrument_tuples():
        if instrument == instr:
            return obs
    else:
        raise ValueError("Unknown instrument " + repr(instrument))

@cached
def get_locator_module(observatory):
    """Return the observatory specific module for handling naming, file location, etc."""
    return get_object("crds." + observatory + ".locate")

@cached
def get_observatory_package(observatory):
    """Return the base observatory package."""
    return get_object("crds." + observatory)

def file_to_locator(filename):
    """Given reference or dataset `filename`,  return the associated observatory locator module."""
    return instrument_to_locator(file_to_instrument(filename))

def instrument_to_locator(instrument):
    """Given an instrument,  return the locator module associated with the
    observatory associated with the instrument.
    """
    return get_locator_module(instrument_to_observatory(instrument))

def file_to_instrument(filename):
    """Given reference or dataset `filename`,  return the associated instrument.
    A key aspect of this function versus get_file_properties() is that observatory is not known.
    """
    basename = os.path.basename(filename).lower()
    for (_obs, instr) in observatory_instrument_tuples():
        if ("_" + instr + "_" in basename) or basename.startswith(instr + "_"):
            return instr.upper()
    from crds import data_file
    header = data_file.get_unconditioned_header(filename, needed_keys=tuple(INSTRUMENT_KEYWORDS))
    return header_to_instrument(header)

def header_to_instrument(header, default=None):
    """Given reference or dataset `header`, return the associated instrument.

    >>> header_to_instrument({"INSTRUME":"ACS"}, default="UNDEFINED")
    'ACS'

    >>> header_to_instrument({"META.INSTRUMENT.NAME":"MIRI"}, default=None)
    'MIRI'

    >>> header_to_instrument({"FOO":"MIRI"}, default="UNDEFINED")
    'UNDEFINED'
    """
    val = get_any_of(header,  INSTRUMENT_KEYWORDS, default)
    val = fix_instrument(val)
    if val is None:
        raise KeyError("No instrument keyword defined in header.")
    else:
        return val.upper()

def fix_instrument(instr):
    """"Apply instrument fixers to `instr` to replace obsolete synonyms with standard version."""
    return get_all_instrument_fixers().get(instr, instr)

@cached
def get_all_instrument_fixers():
    """Return the dictionary which maps all weird instrument name synonymns to standard names
    for the combination of all obersvatories.
    """
    all_fixers = {}
    for obs in ALL_OBSERVATORIES:
        obs_pkg = get_observatory_package(obs)
        try:
            obs_fixers = obs_pkg.INSTRUMENT_FIXERS
        except AttributeError:
            continue
        assert not (set(all_fixers.keys()) & set(obs_fixers.keys())), \
            "Two observatories are using the same instrument fixer."
        all_fixers.update(obs_fixers)
    return all_fixers

def get_any_of(getter,  possible_keys,  default=None):
    """Search for the value of any of `possible_keys` in `dictionary`,  returning `default` if none are found.

    >>> get_any_of( {"A":1},  ["C","D","A"], "UNDEFINED")
    1
    >>> get_any_of( {"X":1},  ["C","D","A"], "UNDEFINED")
    'UNDEFINED'
    """
    for key in possible_keys:
        val = getter.get(key.upper(), None)
        if val is None:
            val = getter.get(key.lower(), None)
        if val is not None and val not in ["undefined", "UNDEFINED"]:
            return val
    else:
        return default

def header_to_observatory(header):
    """Given reference or dataset `header`,  return the associated observatory.

    >>> header_to_observatory({"META.INSTRUMENT.NAME":"MIRI"})
    'jwst'
    """
    instr = header_to_instrument(header)
    observ = instrument_to_observatory(instr)
    return observ

def header_to_locator(header):
    """Given reference or dataset `header` dict,  return the observatory's locator module."""
    instr = header_to_instrument(header)
    locator = instrument_to_locator(instr)
    return locator

def get_reference_paths(observatory):
    """Return the list of subdirectories involved with storing references of all instruments."""
    pkg = get_observatory_package(observatory)
    locate = get_locator_module(observatory)
    return sorted({locate.locate_dir(instrument) for instrument in pkg.INSTRUMENTS})

# ===================================================================

def param_combinations(key_values):
    """Recursively combine the value lists that appear in a keyword values dict
    into dictionaries describing combinations of simple values.

    More directly, it reduces a dict describing valid keyword values to
    CRDS bestrefs header dicts:

    { valid keyword values dict... } -->
        [ bestrefs_header1, bestrefs_header2, ...]

    or in more detail:

    { keyword1 : [values_for_keyword1, ...], ...}  -->
        [{ keyword1 : simple_value_for_keyword1, ...}, ...]
    """
    if isinstance(key_values, dict):
        key_values = list(key_values.items())
    if key_values:
        combs = []
        key, values = key_values[0]
        for subcomb in param_combinations(key_values[1:]):
            if len(values):
                for value in values:
                    comb = dict(subcomb)
                    comb[key] = value
                    combs.append(comb)
            else:
                combs.append(subcomb)
        return combs
    else:
        return [{}]

def write_combs_json(outpath, combs):
    """Write out a list of header dictionaries in JSON format
    suitable for CRDS bestrefs --load-pickles,  inventing "case"
    names for each combination.
    """
    with open(outpath, "w+") as outfile:
        for i, comb in enumerate(combs):
            case = { "CASE_" + str(i) : comb }
            outfile.write(json.dumps(case) + "\n")

def yaml_pars_to_json_bestrefs(yaml_filename, json_filename=None):
    """Given an input file describing parameter values that need
    to be covered,  convert the coverage specification into
    discrete parameter combinations (nominally bestrefs headers)
    and write them out in JSON format suitable for bestrefs.

    META.INSTRUMENT.NAME:
        [ NIRCAM ]

    META.EXPOSURE.READPATT:
        [DEEP8, DEEP2, MEDIUM8, MEDIUM2, SHALLOW4, SHALLOW2,
        BRIGHT2, BRIGHT1,RAPID]
    """
    import yaml
    if json_filename is None:
        json_filename = os.path.splitext(yaml_filename)[0] + ".json"
    with open(yaml_filename) as yaml_file:
        pars = yaml.safe_load(yaml_file)
    combs = param_combinations(pars)
    write_combs_json(json_filename, combs)

# ===================================================================

def fix_json_strings(source_json):
    """Squash unicode in nested json object `source_json`."""
    if sys.version_info >= (3, 0, 0):
        return source_json
    if isinstance(source_json, dict):
        result = {}
        for key, val in source_json.items():
            result[str(key)] = fix_json_strings(val)
    elif isinstance(source_json, (list, tuple)):
        result = []
        for val in source_json:
            result.append(fix_json_strings(val))
    elif isinstance(source_json, str):
        result = str(source_json)
    else:
        result = source_json
    return result

# These functions should actually be general,  working on both references and
# dataset files.
reference_to_instrument = file_to_instrument
reference_to_locator = file_to_locator

def get_observatory_plugin(plugin_name, observatory=None):
    """Get the mission-specific plugin object `plugin_name` which is typically a
    customization function.

    Can be called from contexts where `observatory` is not known locally but
    won't work correctly in all configurations of CRDS;  works best when
    CRDS_OBSERVATORY is defined or `observatory` appears in CRDS_SERVER_URL.

    Returns locator object named `plugin_name`.
    """
    if observatory is None:
        from crds.client import api
        observatory = api.get_default_observatory()
    locator = get_locator_module(observatory)
    return get_object(f"crds.{observatory}.locate.{plugin_name}")

def test():
    """Run doctests."""
    import doctest
    from crds.core import utils
    return doctest.testmod(utils)

if __name__ == "__main__":
    print(test())
