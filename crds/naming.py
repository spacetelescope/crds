"""This module contains functions related to generating and comparing the time order
of CRDS file names.   Different projects have different naming conventions.
"""

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from crds import python23

import os
import re

import crds
from crds import log, utils, config
from crds.client import api
from crds.exceptions import NameComparisonError

# =============================================================================================================

__all__ = [
    "newer",
    "generate_unique_name",
]

# =============================================================================================================

def generate_unique_name(filename, observatory=None, now=None):
    """Given and original filepath `filename` generate a unique CRDS name for the file."""
    if observatory is None:
        locator = utils.file_to_locator(filename)
    else:
        locator = utils.get_locator_module(observatory)
    return locator.generate_unique_name(filename, now)

# =============================================================================================================

def newer(name1, name2):
    """Determine if `name1` is a more recent file than `name2` accounting for 
    limited differences in naming conventions. Official CDBS and CRDS names are 
    comparable using a simple text comparison,  just not to each other.
    
    >>> newer("s7g1700gl_dead.fits", "hst_cos_deadtab_0001.fits")
    False

    >>> newer("hst_cos_deadtab_0001.fits", "s7g1700gl_dead.fits")
    True

    >>> newer("s7g1700gl_dead.fits", "bbbbb.fits")
    Traceback (most recent call last):
    ...
    NameComparisonError: Failed to classify name 'bbbbb.fits' for determining time order.

    >>> newer("bbbbb.fits", "s7g1700gl_dead.fits")
    Traceback (most recent call last):
    ...
    NameComparisonError: Failed to classify name 'bbbbb.fits' for determining time order.

    >>> newer("hst_cos_deadtab_0001.rmap", "hst_cos_deadtab_0002.rmap")
    False

    >>> newer("hst_cos_deadtab_0002.rmap", "hst_cos_deadtab_0001.rmap")
    True

    >>> newer("hst_cos_deadtab_0001.asdf", "hst_cos_deadtab_0050.fits")
    True

    >>> newer("hst_cos_deadtab_0051.fits", "hst_cos_deadtab_0050.asdf")
    False

    >>> newer("hst_cos_deadtab_0001.fits", "hst_cos_deadtab_99991.fits")
    False

    >>> newer("hst_cos_deadtab_99991.fits", "hst_cos_deadtab_0001.fits")
    True


    >>> newer("07g1700gl_dead.fits", "s7g1700gl_dead.fits")
    True

    >>> newer("s7g1700gl_dead.fits", "07g1700gl_dead.fits")
    False

    >>> newer("N/A", "s7g1700gl_dead.fits")
    False

    >>> newer("07g1700gl_dead.fits", "N/A")
    True

    >>> newer("N/A", "hst_cos_deadtab_0002.rmap")
    False                                                                                                                                    
    >>> newer("hst_cos_deadtab_0002.rmap", "N/A")
    True
                                                                                                                                    
    >>> newer("hst_cos_deadtab_0001.fits", "17g1700gl_dead.fits")
    Traceback (most recent call last):
    ...
    NameComparisonError: Unhandled name comparison case:  ('crds', 'newcdbs')
    
    >>> newer("17g1700gl_dead.fits", "hst_cos_deadtab_0001.fits")
    Traceback (most recent call last):
    ...
    NameComparisonError: Unhandled name comparison case:  ('newcdbs', 'crds')
    
    """
    cases = {
        ("crds", "crds")  : "compare_crds",
        ("oldcdbs", "oldcdbs") : "compare",
        ("newcdbs", "newcdbs") : "compare",

        ("crds", "oldcdbs") : True,
        ("oldcdbs", "crds") : False,

        ("newcdbs", "oldcdbs") : True,
        ("oldcdbs", "newcdbs") : False,

        ("crds", "newcdbs") : "raise",
        ("newcdbs", "crds") : "raise",
        }
    name1, name2 = crds_basename(name1), crds_basename(name2)
    class1 = classify_name(name1)
    class2 = classify_name(name2)
    case = cases[(class1, class2)]
    if name1 == "N/A":
        return False
    elif name2 =="N/A":
        result = True
    elif case == "compare_crds":
        if extension_rank(name1) == extension_rank(name2):
            serial1, serial2 = newstyle_serial(name1), newstyle_serial(name2)
            result = serial1 > serial2   # same extension compares by counter
        else:  
            result = extension_rank(name1) > extension_rank(name2)
    elif case == "compare":
        result = name1 > name2
    elif case in [True, False]:
        result = case
    elif case == "query":
        result = True
        with log.warn_on_exception("Failed obtaining file activation dates for files", 
                                   repr(name1), "and", repr(name2), 
                                   "from server.   can't determine time order."):
            info_map = api.get_file_info_map("hst", [name1, name2], fields=["activation_date"])
            result = info_map[name1]["activation_date"] > info_map[name2]["activation_date"]
    else:
        raise NameComparisonError("Unhandled name comparison case: ", repr((class1, class2)))
    log.verbose("Comparing filename time order:", repr(name1), ">", repr(name2), "-->", result)
    return result

def crds_basename(name):
    """basename() accounting for N/A pass thru."""
    if name == "N/A":
        return "N/A"
    else:
        return os.path.basename(name)

def classify_name(name):
    """Classify filename `name` as "crds", "oldcdbs", or "newcdbs".

    >>> classify_name("jwst_miri_dark_0057.fits")
    'crds'

    >>> classify_name("s7g1700gl_dead.fits")
    'oldcdbs'

    >>> classify_name("07g1700gl_dead.fits")
    'newcdbs'

    >>> classify_name("bbbbbb.fits")
    Traceback (most recent call last):
    ...
    NameComparisonError: Failed to classify name 'bbbbbb.fits' for determining time order.
    """
    if name == "N/A":
        return "crds"
    elif crds_name(name):
        return "crds"
    elif old_cdbs_name(name):
        return "oldcdbs"
    elif new_cdbs_name(name):
        return "newcdbs"
    else:
        raise NameComparisonError("Failed to classify name", repr(name), "for determining time order.")

def crds_name(name):
    """Return True IFF `name` is a CRDS-style name, e.g. hst_acs.imap
    
    >>> crds_name("s7g1700gl_dead.fits")
    False
    >>> crds_name("hst.pmap")
    True
    >>> crds_name("hst_acs_darkfile_0001.fits")
    True
    """
    return name.startswith(tuple(crds.ALL_OBSERVATORIES))

OLD_CDBS = re.compile(config.complete_re(r"[A-Za-z][A-Za-z0-9]{8}_[A-Za-z0-9]{1,8}\.[A-Za-z0-9]{1,6}"))
NEW_CDBS = re.compile(config.complete_re(r"[0-9][A-Za-z0-9]{8}_[A-Za-z0-9]{1,8}\.[A-Za-z0-9]{1,6}"))

def old_cdbs_name(name1):
    """Return True IFF name1 is and original CDBS-style name."""
    return OLD_CDBS.match(name1) is not None
    
def new_cdbs_name(name1):
    """Return True IFF name1 is an extended CDBS-style name."""
    return NEW_CDBS.match(name1) is not None
    
def extension_rank(filename):
    """Return a date ranking for `filename` based on extension, lowest numbers are oldest.
    
    >>> extension_rank("fooo.r0h")
    0.0
    >>> extension_rank("fooo.fits")
    1.0
    >>> extension_rank("fooo.json")
    2.0
    >>> extension_rank("fooo.yaml")
    3.0
    >>> extension_rank("/some/path/fooo.asdf")
    4.0
    """
    ext = os.path.splitext(filename)[-1]
    if re.match(r"\.r\dh", ext) or re.match(r"\.r\dd", ext):
        return 0.0
    elif ext == ".fits":
        return 1.0
    elif ext == ".json":
        return 2.0
    elif ext == ".yaml":
        return 3.0
    elif ext == ".asdf":
        return 4.0
    else:
        return 5.0

def newstyle_serial(name):
    """Return the serial number associated with a CRDS-style name.

    >>> newstyle_serial("hst_0042.pmap")
    42
    >>> newstyle_serial("hst_0990999.pmap")    
    990999
    >>> newstyle_serial("hst_cos_0999.imap")
    999
    >>> newstyle_serial("hst_cos_darkfile_0998.fits")
    998
    >>> newstyle_serial("hst.pmap")
    -1
    """
    assert isinstance(name, python23.string_types)
    serial_search = re.search(r"_(\d+)\.\w+", name)
    if serial_search:
        return int(serial_search.groups()[0], 10)
    else:
        return -1

