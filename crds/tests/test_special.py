from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os
import json
import shutil

from crds.bestrefs import BestrefsScript
from crds.tests import test_config

BESTREFS = {
        "FLATFILE": 'x5v1944hl_flat.fits',
        "BADTTAB" : "NOT FOUND n/a",
        "BRFTAB" : "UNDEFINED",
        "TRACETAB" : "NOT FOUND some other error",
        }

BESTREFS_DEFINED = {
        "FLATFILE": 'x5v1944hl_flat.fits',
        }

BESTREFS_NA = {
        "FLATFILE" : "NOT FOUND n/a",
        }

BESTREFS_UNDEFINED = {
        "FLATFILE" : "UNDEFINED",
        }

BESTREFS_OMITTED= {
        }

BESTREFS_ERROR = {
    "FLATFILE" : "NOT FOUND some other error",
    }

"""Special case tests verify behavior in various configurations:

--regression
--na-differences-matter
--undefined-differences-matter

"""

def dt_bestrefs_na_undefined_single_ctx_defaults():
    """
    >>> old_state = test_config.setup()
    
    Instantiate a BestrefsScript with default settings and dummy parameters,  simulating pipeline bestrefs defaults:

    >>> script = BestrefsScript(argv="crds.bestrefs --load-pickles data/bestrefs.special.json --new-context hst_0315.pmap")
    >>> script.complex_init()
    CRDS - INFO - Loading file 'data/bestrefs.special.json'
    CRDS - INFO - Loaded 1 datasets from file 'data/bestrefs.special.json' completely replacing existing headers.
    CRDS - INFO - No comparison context or source comparison requested.
    True

    Skip ahead past bestrefs (faked) into special values results evaluation.

    First a postitive result:  OK,  lowercase-original-result,  uppercase-final-result-for-update
    
    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "FLATFILE")
    (True, 'X5V1944HL_FLAT.FITS')
    
    Second a formal N/A result:  OK,  bestrefs string,  final update value

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "BADTTAB")
    (True, 'N/A')

    An explicit response of UNDEFINED,  by default converted to N/A for update,  considered OK
    
    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "BRFTAB")
    (True, 'N/A')
    
    An implicit response of UNDEFINED, i.e. OMIT, also coverted to N/A for update
    XTRACTAB intentionally omitted from BESTREFS

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "XTRACTAB")
    (True, 'N/A')

    An explicit error response from CRDS,  not OK

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "TRACETAB")
    CRDS - ERROR - instrument='COS' type='TRACETAB' data='LA9K03C3Q:LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    (False, 'NOT FOUND SOME OTHER ERROR')
    
    >>> test_config.cleanup(old_state)
    
    """

def dt_bestrefs_na_undefined_single_ctx_undefined_matters():
    """
    >>> old_state = test_config.setup()
    
    Instantiate a BestrefsScript with default settings and dummy parameters,  simulating pipeline bestrefs defaults:

    >>> script = BestrefsScript(argv="crds.bestrefs --load-pickles data/bestrefs.special.json --undefined-differences-matter --new-context hst_0315.pmap")
    >>> script.complex_init()
    CRDS - INFO - Loading file 'data/bestrefs.special.json'
    CRDS - INFO - Loaded 1 datasets from file 'data/bestrefs.special.json' completely replacing existing headers.
    CRDS - INFO - No comparison context or source comparison requested.
    True

    Skip ahead past bestrefs (faked) into special values results evaluation.

    First a postitive result:  OK,  lowercase-original-result,  uppercase-final-result-for-update
    
    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "FLATFILE")
    (True, 'X5V1944HL_FLAT.FITS')
    
    Second a formal N/A result:  OK,  bestrefs string,  final update value

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "BADTTAB")
    (True, 'N/A')

    An explicit response of UNDEFINED,  by default converted to N/A for update,  not OK since -undefined-differences-matter
    
    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "BRFTAB")
    CRDS - ERROR - instrument='COS' type='BRFTAB' data='LA9K03C3Q:LA9K03C3Q' ::  New: No match found: 'UNDEFINED'
    (False, 'UNDEFINED')
    
    An implicit response of UNDEFINED, i.e. OMIT, also coverted to N/A for update, not OK since -undefined-differences-matter

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "XTRACTAB")
    CRDS - ERROR - instrument='COS' type='XTRACTAB' data='LA9K03C3Q:LA9K03C3Q' ::  New: No match found: 'UNDEFINED'
    (False, 'UNDEFINED')

    An explicit error response from CRDS,  not OK

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "TRACETAB")
    CRDS - ERROR - instrument='COS' type='TRACETAB' data='LA9K03C3Q:LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    (False, 'NOT FOUND SOME OTHER ERROR')
    
    >>> test_config.cleanup(old_state)
    
    """

def dt_bestrefs_na_undefined_single_ctx_na_matters():
    """
    >>> old_state = test_config.setup()
    
    Instantiate a BestrefsScript with default settings and dummy parameters,  simulating pipeline bestrefs defaults:

    >>> script = BestrefsScript(argv="crds.bestrefs --load-pickles data/bestrefs.special.json --na-differences-matter --new-context hst_0315.pmap")
    >>> script.complex_init()
    CRDS - INFO - Loading file 'data/bestrefs.special.json'
    CRDS - INFO - Loaded 1 datasets from file 'data/bestrefs.special.json' completely replacing existing headers.
    CRDS - INFO - No comparison context or source comparison requested.
    True

    Skip ahead past bestrefs (faked) into special values results evaluation.

    First a postitive result:  OK,  lowercase-original-result,  uppercase-final-result-for-update
    
    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "FLATFILE")
    (True, 'X5V1944HL_FLAT.FITS')
    
    Second a formal N/A result:  OK,  bestrefs string,  final update value

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "BADTTAB")
    (True, 'N/A')

    An explicit response of UNDEFINED,  by default converted to N/A for update,  considered OK
    
    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "BRFTAB")
    (True, 'N/A')
    
    An implicit response of UNDEFINED, i.e. OMIT, also coverted to N/A for update

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "XTRACTAB")
    (True, 'N/A')

    An explicit error response from CRDS, not OK

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q:LA9K03C3Q", "COS", "TRACETAB")
    CRDS - ERROR - instrument='COS' type='TRACETAB' data='LA9K03C3Q:LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    (False, 'NOT FOUND SOME OTHER ERROR')
    
    >>> test_config.cleanup(old_state)
    
    """

kinds = ["DEFINED", "NA", "UNDEFINED", "OMITTED", "ERROR"]

def generate_comparisons(undef_matters, na_matters):
    for kind1 in kinds:
        for kind2 in kinds:
            bestrefs1 = globals()["BESTREFS_" + kind1]
            bestrefs2 = globals()["BESTREFS_" + kind2]
            print("""

def dt_compare_bestrefs_%s_%s_%s_%s():
    '''
    >>> old_state = test_config.setup()
    
    >>> script = BestrefsScript(argv="crds.bestrefs --load-pickles data/bestrefs.special.json --new-context hst_0315.pmap %s %s")
    >>> script.complex_init()
    CRDS - INFO - Loading file 'data/bestrefs.special.json'
    CRDS - INFO - Loaded 1 datasets from file 'data/bestrefs.special.json' completely replacing existing headers.
    CRDS - INFO - No comparison context or source comparison requested.
    True
    >>> script.compare_bestrefs('%s', '%s', %s, %s)

    >>> test_config.cleanup(old_state)
    ''' """ % ("undefmatters" if undef_matters else "undefok",
       "namatters" if na_matters else "naok",
       kind1.lower(),
       kind2.lower(),
       "--undefined-differences-matter" if undef_matters else "",
       "--na-differences-matter" if na_matters else "",
       "COS",
       "LA9K03C3Q:LA9K03C3Q",
       bestrefs1, bestrefs2))

def generate_all():
    for undef_matters in [False, True]:
        for na_matters in [False, True]:
            generate_comparisons(undef_matters, na_matters)

# ==================================================================================

def main():
    """Run module tests,  for now just doctests only."""
    from crds.tests import test_special, tstmod
    return tstmod(test_special)

if __name__ == "__main__":
    print(main())

# ==================================================================================

