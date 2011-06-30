import os.path
import re

import crds.log as log

def create_path(path):
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
        # log.write("Creating", current)
        d = os.path.join(*current)
        d.replace("//","/")
        if not os.path.exists(d):
            os.mkdir(d)

def ensure_dir_exists(fullpath):
    """Creates dirs from `fullpath` if they don't already exist.
    """
    create_path(os.path.dirname(fullpath))


# ===================================================================

def get_locator_module(observatory):
     exec("import crds."+observatory+".locate as locate", locals(), locals())
     return locate
 
def get_crds_mappath(observatory):
    locate = get_locator_module(observatory)
    return locate.get_crds_mappath()

def get_crds_refpath(observatory):
    locate = get_locator_module(observatory)
    return locate.get_crds_refpath()

def context_to_observatory(context_file):
    """
    >>> context_to_observatory('hst_acs_biasfile.rmap')
    'hst'
    """
    return os.path.basename(context_file).split("_")[0].split(".")[0]

def context_to_instrument(context_file):
    """
    >>> context_to_instrument('hst_acs_biasfile.rmap')
    'acs'
    """
    return os.path.basename(context_file).split("_")[1].split(".")[0]

def context_to_reftype(context_file):
    """
    >>> context_to_reftype('hst_acs_biasfile.rmap')
    'biasfile'
    """
    return os.path.basename(context_file).split("_")[2].split(".")[0]

# ===================================================================

def get_object(dotted_name):
    """Import the given `dotted_name` and return the object."""
    parts = dotted_name.split(".")
    pkgpath = ".".join(parts[:-1])
    cls = parts[-1]
    namespace = {}
    exec "from " + pkgpath + " import " + cls in namespace, namespace
    return namespace[cls]

# ===================================================================

def get_header_union(fname, needed_keys=[]):
    """Get the union of keywords from all header extensions of `fname`.  In
    the case of collisions,  keep the first value found as extensions are loaded
    in numerical order.
    """
    import pyfits
    union = {}
    for hdu in pyfits.open(fname):
        for key in hdu.header:
            newval = condition_value(hdu.header[key])
            if key not in union:
                if key in needed_keys or ("*"+key in needed_keys):
                    union[key] = newval
            elif union[key] != newval:
                log.verbose("*** WARNING: Header union collision on", repr(key), repr(union[key]), repr(hdu.header[key]))
    return union


# ==============================================================================

DONT_CARE_RE = re.compile("^" + "|".join(["ANY","-999","-999\.0","N/A","\(\)"]) + "$|^$")

NUMBER_RE = re.compile("^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$")

def condition_value(value):
    """Condition `value`,  ostensibly taken from a FITS header or CDBS
    reference file table,  such that it is suitable for appearing in or
    matching an rmap MatchingSelector key.

    >>> condition_value('ANY')
    '*'
    >>> condition_value('-999')
    '*'
    >>> condition_value('-999.0')
    '*'
    >>> condition_value('N/A')
    '*'
    >>> condition_value('')
    '*'
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
    >>> condition_value('foo')
    'FOO'
    >>> condition_value('iref$uaf12559i_drk.fits')
    'IREF$UAF12559I_DRK.FITS'
    """
    value = str(value).strip().upper()
    if NUMBER_RE.match(value):
        value = str(float(value))
    if DONT_CARE_RE.match(value):
        value = "*"
    elif value in ["T", "TRUE"]:
        value = "T"
    elif value in ["F", "FALSE"]:
        value = "F"
    return value

