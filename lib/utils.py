"""Generic utility routines used by a variety of modules.
"""
import sys
import os.path
import re
import sha
import cStringIO
import functools

# from crds import data_file,  import deferred until required

from crds import compat, log

CRDS_CHECKSUM_BLOCK_SIZE = 2**26

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
    ...   print "really doing it."
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

class xcached(object):
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
        return CachedFunction(func, *self.args, **self.keys)

class CachedFunction(object):
    """Class to support the @cached function decorator.   Called at runtime
    for typical caching version of function.
    """
    def __init__(self, func, omit_from_key=None):
        self.cache = dict()
        self.uncached = func
        self.omit_from_key = [] if omit_from_key is None else omit_from_key
    
    def cache_key(self, *args, **keys):
        """Compute the cache key for the given parameters."""
        args = tuple([ a for (i, a) in enumerate(args) if i not in self.omit_from_key])
        keys = tuple([item for item in keys.items() if item[0] not in self.omit_from_key])
        return args + keys
    
    def _readonly(self, *args, **keys):
        """Compute (cache_key, func(*args, **keys)).   Do not add to cache."""
        key = self.cache_key(*args, **keys)
        if key in self.cache:
            log.verbose("Cached call", self.uncached.func_name, repr(key), verbosity=80)
            return key, self.cache[key]
        else:
            log.verbose("Uncached call", self.uncached.func_name, repr(key), verbosity=80)
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

# ===================================================================

def capture_output(func):
    """Decorate a function with @capture_output to define a CapturedFunction()
    wrapper around it.   
    
    Doesn't currently capture non-python output but could with dup2.
    
    Decorate any function to wrap it in a CapturedFunction() wrapper:
    
    >>> @capture_output
    ... def f(x,y): 
    ...    print "hi"
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
    
    >>> f.outputs(1, 2)
    'hi\\n'
    
    If you need both the return value and captured output:
    
    >>> f.returns_outputs(1, 2)
    (3, 'hi\\n')
       
    """
    class CapturedFunction(object):
        """Closure on `func` which supports various forms of output capture."""
        
        def __repr__(self):
            return "CapturedFunction('%s')" % func.func_name

        def returns_outputs(self, *args, **keys):
            """Call the wrapped function,  capture output,  return (f(), output_from_f)."""
            oldout, olderr = sys.stdout, sys.stderr
            out = cStringIO.StringIO()
            sys.stdout, sys.stderr = out, out
            # handler = log.add_stream_handler(out)
            try:
                result = func(*args, **keys)
            finally:
                out.flush()
                # log.remove_stream_handler(handler)
                sys.stdout, sys.stderr = oldout, olderr
            out.seek(0)
            return result, out.read()
        
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

def invert_dict(dictionary):
    """Return the functional inverse of a dictionary,  raising an exception
    for values in `d` which map to more than one key producing an undefined
    inverse.
    """
    inverse = {}
    for key, value in dictionary.items():
        if value in inverse:
            raise ValueError("Undefined inverse because of duplicate value " + \
                             repr(value))
        inverse[value] = key
    return inverse
    
# ===================================================================

def evalfile(fname):
    """Evaluate and return the contents of file `fname`,  restricting
    expressions to data literals. 
    """
    with open(fname) as sourcefile:
        contents = sourcefile.read()
    return compat.literal_eval(contents)

# ===================================================================

def create_path(path, mode=0755):
    """Recursively traverses directory path creating directories as
    needed so that the entire path exists.
    """
    if path.startswith("./"):
        path = path[2:]
    if os.path.exists(path):
        return
    current = []
    for part in path.split("/"):
        if not part:
            current.append("/")
            continue
        current.append(str(part))
        subdir = os.path.join(*current)
        subdir.replace("//","/")
        if not os.path.exists(subdir):
            os.mkdir(subdir, mode)

def ensure_dir_exists(fullpath, mode=0755):
    """Creates dirs from `fullpath` if they don't already exist.
    """
    create_path(os.path.dirname(fullpath), mode)
    

def checksum(pathname):
    """Return the CRDS hexdigest for file at `pathname`.""" 
    xsum = sha.new()
    with open(pathname) as infile:
        size = 0
        insize = os.stat(pathname).st_size
        while size < insize:
            block = infile.read(CRDS_CHECKSUM_BLOCK_SIZE)
            size += len(block)
            xsum.update(block)
    return xsum.hexdigest()


def str_checksum(data):
    """Return the CRDS hexdigest for small strings.""" 
    xsum = sha.new()
    xsum.update(data)
    return xsum.hexdigest()

# ===================================================================

def get_file_properties(observatory, filename):
    """Return instrument,filekind fields associated with filename."""
    return get_locator_module(observatory).get_file_properties(filename)        

# ===================================================================

MODULE_PATH_RE = re.compile(r"^crds(\.\w+)+$")

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
    exec "from " + pkgpath + " import " + cls in namespace, namespace
    return namespace[cls]

# ==============================================================================

DONT_CARE_RE = re.compile(r"^" + r"|".join([
    # "-999","-999\.0",
    # "4294966297.0",
    r"-2147483648.0",
    r"\(\)","N/A","NOT APPLICABLE"]) + "$|^$")

NUMBER_RE = re.compile(r"^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$|^[+-]?[0-9]+\.$")

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
    >>> condition_value('')
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

# ==============================================================================

@cached
def instrument_to_observatory(instrument):
    """Given the name of an instrument,  return the associated observatory.
    
    >>> instrument_to_observatory("acs")
    'hst'
    >>> instrument_to_observatory("miri")
    'jwst'
    """
    instrument = instrument.lower()
    try:
        import crds.hst
        if instrument in crds.hst.INSTRUMENTS:
            return "hst"
    except ImportError:
        pass
    try:
        import crds.jwst
        if instrument in crds.jwst.INSTRUMENTS:
            return "jwst"
    except ImportError:
        pass
    raise ValueError("Unknown instrument " + repr(instrument))

@cached
def get_locator_module(observatory):
    """Return the observatory specific module for handling naming, file location, etc."""
    return get_object("crds." + observatory + ".locate")

@cached
def get_observatory_package(observatory):
    """Return the base observatory package."""
    return get_object("crds." + observatory)
    
def instrument_to_locator(instrument):
    """Given an instrument,  return the locator module associated with the
    observatory associated with the instrument.
    """
    return get_locator_module(instrument_to_observatory(instrument))


def reference_to_instrument(filename):
    """Given reference file `filename`,  return the associated instrument."""
    from crds import data_file
    try:
        header = data_file.get_conditioned_header(filename, needed_keys=["INSTRUME"])
        return header["INSTRUME"].lower()
    except KeyError:
        header = data_file.get_conditioned_header(filename, needed_keys=["META.INSTRUMENT.TYPE"])
        return header["META.INSTRUMENT.TYPE"]
    
def reference_to_locator(filename):
    """Given reference file `filename`,  return the associated observatory locator module."""
    return instrument_to_locator(reference_to_instrument(filename))

def reference_to_observatory(filename):
    """Return the name of the observatory corresponding to reference `filename`."""
    return instrument_to_observatory(reference_to_instrument(filename))


# These functions should actually be general,  working on both references and
# dataset files.
file_to_instrument = reference_to_instrument
file_to_locator = reference_to_locator
file_to_observatory = reference_to_observatory

def test():
    """Run doctests."""
    import doctest
    from . import utils
    return doctest.testmod(utils)

