"""Generic utility routines used by a variety of modules.
"""

import os.path
import re
import sha

# from crds import data_file,  import deferred until required

from crds import compat

CRDS_CHECKSUM_BLOCK_SIZE = 2**26

# ===================================================================

def cached(func):
    """The cached decorator embeds a dictionary in a function wrapper to
    capture prior results.   The wrapped function works like the original,
    except it's faster because it fetches results for prior calls from the
    cache.   The wrapped function has two extra attributes
    
    .cache         -- { parameters: old_result } dictionary
    .uncached      -- original unwrapped function
        
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
    """
    cache = dict()
    def cacher(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    cacher.func_name = func.func_name
    cacher.__dict__["cache"] = cache
    cacher.__dict__["uncached"] = func
    return cacher

# ===================================================================

def invert_dict(d):
    """Return the functional inverse of a dictionary,  raising an exception
    for values in `d` which map to more than one key producing an undefined
    inverse.
    """
    inverse = {}
    for key, value in d.items():
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
    for c in path.split("/"):
        if not c:
            current.append("/")
            continue
        current.append(str(c))
        d = os.path.join(*current)
        d.replace("//","/")
        if not os.path.exists(d):
            os.mkdir(d, mode)

def ensure_dir_exists(fullpath, mode=0755):
    """Creates dirs from `fullpath` if they don't already exist.
    """
    create_path(os.path.dirname(fullpath), mode)
    

def checksum(pathname):
    """Return the CRDS hexdigest for file at `pathname`.""" 
    sum = sha.new()
    with open(pathname) as infile:
        size = 0
        insize = os.stat(pathname).st_size
        while size < insize:
            block = infile.read(CRDS_CHECKSUM_BLOCK_SIZE)
            size += len(block)
            sum.update(block)
    return sum.hexdigest()



# ===================================================================

LOCATORS = {
    }

def get_file_properties(observatory, filename):
    """Return instrument,filekind,id fields associated with filename.
    """
    if observatory not in LOCATORS:
        locator = get_object("crds." + observatory + ".locate")
        LOCATORS[observatory] = locator
    else:
        locator = LOCATORS[observatory]
    return locator.get_file_properties(filename)        

# ===================================================================

MODULE_PATH_RE = re.compile(r"^crds(\.\w+)+$")

def get_object(dotted_name):
    """Import the given `dotted_name` and return the object.
    
    >>> rmap = get_object("crds.rmap")
    >>> fail = get_object("crds.rmap; eval('2+2')")
    Traceback (most recent call last):
    ...
    AssertionError: Invalid dotted name for get_object() : "crds.rmap; eval('2+2')"
    """
    assert MODULE_PATH_RE.match(dotted_name), \
        "Invalid dotted name for get_object() : " + repr(dotted_name)   
    parts = dotted_name.split(".")
    pkgpath = ".".join(parts[:-1])
    cls = parts[-1]
    namespace = {}
    exec "from " + pkgpath + " import " + cls in namespace, namespace
    return namespace[cls]

# ==============================================================================

DONT_CARE_RE = re.compile("^" + "|".join([
    # "-999","-999\.0",
    # "4294966297.0",
    "-2147483648.0",
    "\(\)","N/A","NOT APPLICABLE"]) + "$|^$")

NUMBER_RE = re.compile("^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$|^[+-]?[0-9]+\.$")

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

def instrument_to_observatory(instrument):
    """Given the name of an instrument,  return the associated observatory."""
    instrument = instrument.lower()
    try:
        import crds.hst
    except ImportError:
        pass
    else:
        if instrument in crds.hst.INSTRUMENTS:
            return "hst"
    try:
        import crds.jwst
    except ImportError:
        pass
    else:
        if instrument in crds.jwst.INSTRUMENTS:
            return "jwst"
    raise ValueError("Unknown instrument " + repr(instrument))

def get_locator_module(observatory):
    """Return the observatory specific module for handling naming, file location, etc."""
    return get_object("crds." + observatory + ".locate")
    
def instrument_to_locator(instrument):
    """Given an instrument,  return the locator module associated with the
    observatory associated with the instrument.
    """
    return get_locator_module(instrument_to_observatory(instrument))


# XXXX TODO  use of INSTRUME probably won't work with .finf metadata but does
# work with JWST .fits references typically accessed through the data model.
def reference_to_instrument(filename):
    """Given reference file `filename`,  return the associated instrument.
    """
    from crds import data_file
    try:
        header = data_file.get_conditioned_header(filename, needed_keys=["INSTRUME"])
        return header["INSTRUME"].lower()
    except KeyError:
        header = data_file.get_conditioned_header(filename, needed_keys=["META.INSTRUMENT.TYPE"])
        return header["META.INSTRUMENT.TYPE"]

def reference_to_locator(filename):
    """Given reference file `filename`,  return the associated observatory 
    locator module.
    """
    return instrument_to_locator(reference_to_instrument(filename))

def reference_to_observatory(filename):
    """Return the name of the observatory corresponding to reference
    `filename`.
    """
    return instrument_to_observatory(reference_to_instrument(filename))

