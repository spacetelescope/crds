"""This module contains functions related to generating and comparing the time order
of CRDS file names.   Different projects have different naming conventions.
"""
import os
import re

from . import config, log, utils
from .exceptions import NameComparisonError
from .constants import ALL_OBSERVATORIES

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
    True

    >>> newer("bbbbb.fits", "s7g1700gl_dead.fits")
    False

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

    >>> newer("16n1832tm_tmc.fits", "06n1832tm_tmc.fits")
    True
    >>> newer("06n1832tm_tmc.fits", "16n1832tm_tmc.fits")
    False
    >>> newer("06n1832tm_tmc.fits", "16n1832tm_tmg.fits")
    False

    >>> newer("hst_cos_deadtab_0001.fits", "16n1832tm_tmg.fits")
    Traceback (most recent call last):
    ...
    NameComparisonError: Unhandled name comparison case:  ('crds', 'synphot')

    >>> newer("07g1700gl_dead.fits", "16n1832tm_tmg.fits")
    Traceback (most recent call last):
    ...
    NameComparisonError: Unhandled name comparison case:  ('newcdbs', 'synphot')

    >>> newer("16n1832tm_tmg.fits", "7g1700gl_dead.fits")
    Traceback (most recent call last):
    ...
    NameComparisonError: Unhandled name comparison case:  ('synphot', 'oldcdbs')

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
        ("oldsynphot", "oldsynphot") : "compare",
        ("newsynphot", "newsynphot") : "compare",

        ("crds", "oldcdbs") : True,
        ("oldcdbs", "crds") : False,

        ("newcdbs", "oldcdbs") : True,
        ("oldcdbs", "newcdbs") : False,

        ("newsynphot", "oldsynphot") : True,
        ("oldsynphot", "newsynphot") : False,
    }
    name1, name2 = crds_basename(name1), crds_basename(name2)
    class1 = classify_name(name1)
    class2 = classify_name(name2)
    case = cases.get((class1, class2), "raise")
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
    """Classify filename `name` as "crds", "synphot", "oldcdbs", or "newcdbs".

    >>> classify_name("jwst_miri_dark_0057.fits")
    'crds'

    >>> classify_name("s7g1700gl_dead.fits")
    'oldcdbs'

    >>> classify_name("07g1700gl_dead.fits")
    'newcdbs'

    >>> classify_name("16n1832tm_tmc.fits")
    'newsynphot'

    >>> classify_name("z6n1832tm_tmc.fits")
    'oldsynphot'

    Ad hoc names are generally mistakes which are immediately replaced.   Classify them
    as oldcdbs (oldest) so that comparison with anything else is interpreted as a
    replacement with something newer,  and nominal.

    >>> classify_name("bbbbbb.fits")
    'oldcdbs'
    """
    if name == "N/A":
        return "crds"
    elif crds_name(name):
        return "crds"
    elif old_synphot_name(name):
        return "oldsynphot"
    elif new_synphot_name(name):
        return "newsynphot"
    elif old_cdbs_name(name):
        return "oldcdbs"
    elif new_cdbs_name(name):
        return "newcdbs"
    else:
        # raise NameComparisonError("Failed to classify name", repr(name), "for determining time order.")
        log.warning("Failed to classify name", repr(name), "for determining time order.")
        return "oldcdbs"  # if it's a garbage name, make it oldest so replacing it is normal.

def crds_name(name):
    """Return True IFF `name` is a CRDS-style name, e.g. hst_acs.imap

    >>> crds_name("s7g1700gl_dead.fits")
    False
    >>> crds_name("1c82030ml_dead.fits")
    False
    >>> crds_name("hst.pmap")
    True
    >>> crds_name("hst_acs_darkfile_0001.fits")
    True
    >>> crds_name("16n1832tm_tmc.fits")
    False
    """
    return name.startswith(tuple(ALL_OBSERVATORIES))

OLD_CDBS = re.compile(config.complete_re(r"[A-Za-z][A-Za-z0-9]{8}_[A-Za-z0-9]{1,8}\.[A-Za-z0-9]{1,6}"))
NEW_CDBS = re.compile(config.complete_re(r"[0-9][A-Za-z0-9]{8}_[A-Za-z0-9]{1,8}\.[A-Za-z0-9]{1,6}"))

def old_cdbs_name(name1):
    """Return True IFF name1 is and original CDBS-style name.

    >>> old_cdbs_name("s7g1700gl_dead.fits")
    True
    >>> old_cdbs_name("1c82030ml_dead.fits")
    False
    >>> old_cdbs_name("16n1832tm_tmc.fits")
    False
    >>> old_cdbs_name("z6n1832tm_tmc.fits")
    True
    >>> old_cdbs_name("hst.pmap")
    False
    >>> old_cdbs_name("hst_acs_darkfile_0001.fits")
    False
    """
    return OLD_CDBS.match(name1) is not None

def new_cdbs_name(name1):
    """Return True IFF name1 is an extended CDBS-style name.

    >>> new_cdbs_name("s7g1700gl_dead.fits")
    False
    >>> new_cdbs_name("1c82030ml_dead.fits")
    True
    >>> new_cdbs_name("16n1832tm_tmc.fits")
    True
    >>> new_cdbs_name("z6n1832tm_tmc.fits")
    False
    >>> new_cdbs_name("hst.pmap")
    False
    >>> new_cdbs_name("hst_acs_darkfile_0001.fits")
    False
    """
    return NEW_CDBS.match(name1) is not None

NEW_SYNPHOT_RE = re.compile(config.complete_re(r"[0-9][a-zA-Za-z0-9]{7}m_(tmc|tmg|tmt)\.[A-Za-z0-9]{1,6}"))
OLD_SYNPHOT_RE = re.compile(config.complete_re(r"[A-Za-z][a-zA-Za-z0-9]{7}m_(tmc|tmg|tmt)\.[A-Za-z0-9]{1,6}"))

def synphot_name(name):
    """Return True IFF `name` is the name of an ETC master table file of some kind.

    >>> synphot_name("s7g1700gl_dead.fits")
    False
    >>> synphot_name("1c82030ml_dead.fits")
    False
    >>> synphot_name("16n1832tm_tmc.fits")
    True
    >>> synphot_name("16n1832tm_tmt.fits")
    True
    >>> synphot_name("16n1832tm_tmg.fits")
    True
    >>> synphot_name("hst.pmap")
    False
    >>> synphot_name("hst_acs_darkfile_0001.fits")
    False
    """
    return old_synphot_name(name) or new_synphot_name(name)

def new_synphot_name(name):
    """Return True IFF `name` is the name of an ETC master table file of some kind."""
    return NEW_SYNPHOT_RE.match(name) is not None

def old_synphot_name(name):
    """Return True IFF `name` is the name of an ETC master table file of some kind."""
    return OLD_SYNPHOT_RE.match(name) is not None

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
    assert isinstance(name, str)
    serial_search = re.search(r"_(\d+)\.\w+", name)
    if serial_search:
        return int(serial_search.groups()[0], 10)
    else:
        return -1
