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

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "FLATFILE")
    (True, 'X5V1944HL_FLAT.FITS')

    Second a formal N/A result:  OK,  bestrefs string,  final update value

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "BADTTAB")
    (True, 'N/A')

    An explicit response of UNDEFINED,  by default converted to N/A for update,  considered OK

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "BRFTAB")
    (True, 'N/A')

    An implicit response of UNDEFINED, i.e. OMIT, also coverted to N/A for update
    XTRACTAB intentionally omitted from BESTREFS

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "XTRACTAB")
    (True, 'N/A')

    An explicit error response from CRDS,  not OK

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "TRACETAB")
    CRDS - ERROR - instrument='COS' type='TRACETAB' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error
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

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "FLATFILE")
    (True, 'X5V1944HL_FLAT.FITS')

    Second a formal N/A result:  OK,  bestrefs string,  final update value

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "BADTTAB")
    (True, 'N/A')

    An explicit response of UNDEFINED,  by default converted to N/A for update,  not OK since -undefined-differences-matter

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "BRFTAB")
    CRDS - ERROR - instrument='COS' type='BRFTAB' data='LA9K03C3Q' ::  New: No match found: 'UNDEFINED'
    (False, 'UNDEFINED')

    An implicit response of UNDEFINED, i.e. OMIT, also coverted to N/A for update, not OK since -undefined-differences-matter

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "XTRACTAB")
    CRDS - ERROR - instrument='COS' type='XTRACTAB' data='LA9K03C3Q' ::  New: No match found: 'UNDEFINED'
    (False, 'UNDEFINED')

    An explicit error response from CRDS,  not OK

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "TRACETAB")
    CRDS - ERROR - instrument='COS' type='TRACETAB' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error
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

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "FLATFILE")
    (True, 'X5V1944HL_FLAT.FITS')

    Second a formal N/A result:  OK,  bestrefs string,  final update value

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "BADTTAB")
    (True, 'N/A')

    An explicit response of UNDEFINED,  by default converted to N/A for update,  considered OK

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "BRFTAB")
    (True, 'N/A')

    An implicit response of UNDEFINED, i.e. OMIT, also coverted to N/A for update

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "XTRACTAB")
    (True, 'N/A')

    An explicit error response from CRDS, not OK

    >>> script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "TRACETAB")
    CRDS - ERROR - instrument='COS' type='TRACETAB' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    (False, 'NOT FOUND SOME OTHER ERROR')

    >>> test_config.cleanup(old_state)

    """

kinds = ["DEFINED", "NA", "UNDEFINED", "OMITTED", "ERROR"]

old_state = test_config.setup()

SCRIPT_UNDEFMATTERS_NAMATTERS  = BestrefsScript(argv="crds.bestrefs --load-pickles data/bestrefs.special.json --new-context hst_0315.pmap --undefined-differences-matter --na-differences-matter")
SCRIPT_UNDEFMATTERS_NAMATTERS.complex_init()

SCRIPT_UNDEFOK_NAMATTERS  = BestrefsScript(argv="crds.bestrefs --load-pickles data/bestrefs.special.json --new-context hst_0315.pmap --na-differences-matter")
SCRIPT_UNDEFOK_NAMATTERS.complex_init()

SCRIPT_UNDEFOK_NAOK  = BestrefsScript(argv="crds.bestrefs --load-pickles data/bestrefs.special.json --new-context hst_0315.pmap")
SCRIPT_UNDEFOK_NAOK.complex_init()

SCRIPT_UNDEFMATTERS_NAOK  = BestrefsScript(argv="crds.bestrefs --load-pickles data/bestrefs.special.json --new-context hst_0315.pmap --undefined-differences-matter")
SCRIPT_UNDEFMATTERS_NAOK.complex_init()

test_config.cleanup(old_state)
del old_state

def generate_comparisons(undef_matters, na_matters):
    for kind1 in kinds:
        for kind2 in kinds:
            bestrefs1 = globals()["BESTREFS_" + kind1]
            bestrefs2 = globals()["BESTREFS_" + kind2]
            undef = "undefmatters" if undef_matters else "undefok"
            na = "namatters" if na_matters else "naok"
            print("""

def dt_compare_bestrefs_%s_%s_%s_%s():
    '''
    >>> old_state = test_config.setup()

    >>> script_%s_%s.compare_bestrefs('%s', '%s', %s, %s)

    >>> test_config.cleanup(old_state)
    ''' """ % (

       kind1.lower(),
       kind2.lower(),
       undef,
       na,

       undef, na,

       "COS","LA9K03C3Q", bestrefs1, bestrefs2))

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

def dt_compare_bestrefs_defined_defined_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'x5v1944hl_flat.fits'}, {'FLATFILE': 'x5v1944hl_flat.fits'})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_defined_na_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'x5v1944hl_flat.fits'}, {'FLATFILE': 'NOT FOUND n/a'})
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='X5V1944HL_FLAT.FITS', new_reference='N/A')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_defined_undefined_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'x5v1944hl_flat.fits'}, {'FLATFILE': 'UNDEFINED'})
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='X5V1944HL_FLAT.FITS', new_reference='N/A')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_defined_omitted_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'x5v1944hl_flat.fits'}, {})
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='X5V1944HL_FLAT.FITS', new_reference='N/A')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_defined_error_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'x5v1944hl_flat.fits'}, {'FLATFILE': 'NOT FOUND some other error'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_na_defined_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND n/a'}, {'FLATFILE': 'x5v1944hl_flat.fits'})
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='N/A', new_reference='X5V1944HL_FLAT.FITS')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_na_na_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND n/a'}, {'FLATFILE': 'NOT FOUND n/a'})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_na_undefined_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND n/a'}, {'FLATFILE': 'UNDEFINED'})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_na_omitted_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND n/a'}, {})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_na_error_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND n/a'}, {'FLATFILE': 'NOT FOUND some other error'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_undefined_defined_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'UNDEFINED'}, {'FLATFILE': 'x5v1944hl_flat.fits'})
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='N/A', new_reference='X5V1944HL_FLAT.FITS')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_undefined_na_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'UNDEFINED'}, {'FLATFILE': 'NOT FOUND n/a'})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_undefined_undefined_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'UNDEFINED'}, {'FLATFILE': 'UNDEFINED'})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_undefined_omitted_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'UNDEFINED'}, {})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_undefined_error_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'UNDEFINED'}, {'FLATFILE': 'NOT FOUND some other error'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_omitted_defined_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {}, {'FLATFILE': 'x5v1944hl_flat.fits'})
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='N/A', new_reference='X5V1944HL_FLAT.FITS')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_omitted_na_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {}, {'FLATFILE': 'NOT FOUND n/a'})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_omitted_undefined_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {}, {'FLATFILE': 'UNDEFINED'})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_omitted_omitted_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {}, {})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_omitted_error_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {}, {'FLATFILE': 'NOT FOUND some other error'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_error_defined_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND some other error'}, {'FLATFILE': 'x5v1944hl_flat.fits'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: Bestref FAILED:  some other error
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='NOT FOUND SOME OTHER ERROR', new_reference='X5V1944HL_FLAT.FITS')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_error_na_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND some other error'}, {'FLATFILE': 'NOT FOUND n/a'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: Bestref FAILED:  some other error
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='NOT FOUND SOME OTHER ERROR', new_reference='N/A')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_error_undefined_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND some other error'}, {'FLATFILE': 'UNDEFINED'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: Bestref FAILED:  some other error
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='NOT FOUND SOME OTHER ERROR', new_reference='N/A')]
    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_error_omitted_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND some other error'}, {})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: Bestref FAILED:  some other error
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='NOT FOUND SOME OTHER ERROR', new_reference='N/A')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_error_error_undefok_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND some other error'}, {'FLATFILE': 'NOT FOUND some other error'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: Bestref FAILED:  some other error
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_defined_defined_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'x5v1944hl_flat.fits'}, {'FLATFILE': 'x5v1944hl_flat.fits'})
    []

    >>> test_config.cleanup(old_state)
    '''
def dt_compare_bestrefs_defined_defined2_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'x5v1944hl_flat.fits'}, {'FLATFILE': 'y5v1944hl_flat.fits'})
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='X5V1944HL_FLAT.FITS', new_reference='Y5V1944HL_FLAT.FITS')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_defined_na_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'x5v1944hl_flat.fits'}, {'FLATFILE': 'NOT FOUND n/a'})
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='X5V1944HL_FLAT.FITS', new_reference='N/A')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_defined_undefined_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'x5v1944hl_flat.fits'}, {'FLATFILE': 'UNDEFINED'})
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='X5V1944HL_FLAT.FITS', new_reference='N/A')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_defined_omitted_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'x5v1944hl_flat.fits'}, {})
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='X5V1944HL_FLAT.FITS', new_reference='N/A')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_defined_error_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'x5v1944hl_flat.fits'}, {'FLATFILE': 'NOT FOUND some other error'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_na_defined_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND n/a'}, {'FLATFILE': 'x5v1944hl_flat.fits'})
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='N/A', new_reference='X5V1944HL_FLAT.FITS')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_na_na_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND n/a'}, {'FLATFILE': 'NOT FOUND n/a'})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_na_undefined_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND n/a'}, {'FLATFILE': 'UNDEFINED'})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_na_omitted_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND n/a'}, {})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_na_error_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND n/a'}, {'FLATFILE': 'NOT FOUND some other error'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_undefined_defined_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'UNDEFINED'}, {'FLATFILE': 'x5v1944hl_flat.fits'})
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='N/A', new_reference='X5V1944HL_FLAT.FITS')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_undefined_na_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'UNDEFINED'}, {'FLATFILE': 'NOT FOUND n/a'})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_undefined_undefined_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'UNDEFINED'}, {'FLATFILE': 'UNDEFINED'})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_undefined_omitted_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'UNDEFINED'}, {})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_undefined_error_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'UNDEFINED'}, {'FLATFILE': 'NOT FOUND some other error'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_omitted_defined_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {}, {'FLATFILE': 'x5v1944hl_flat.fits'})
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='N/A', new_reference='X5V1944HL_FLAT.FITS')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_omitted_na_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {}, {'FLATFILE': 'NOT FOUND n/a'})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_omitted_undefined_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {}, {'FLATFILE': 'UNDEFINED'})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_omitted_omitted_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {}, {})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_omitted_error_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {}, {'FLATFILE': 'NOT FOUND some other error'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_error_defined_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND some other error'}, {'FLATFILE': 'x5v1944hl_flat.fits'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: Bestref FAILED:  some other error
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='NOT FOUND SOME OTHER ERROR', new_reference='X5V1944HL_FLAT.FITS')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_error_na_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND some other error'}, {'FLATFILE': 'NOT FOUND n/a'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: Bestref FAILED:  some other error
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='NOT FOUND SOME OTHER ERROR', new_reference='N/A')]

    >>> test_config.cleanup(old_state)
    '''

def dt_compare_bestrefs_error_undefined_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND some other error'}, {'FLATFILE': 'UNDEFINED'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: Bestref FAILED:  some other error
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='NOT FOUND SOME OTHER ERROR', new_reference='N/A')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_error_omitted_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND some other error'}, {})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: Bestref FAILED:  some other error
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='NOT FOUND SOME OTHER ERROR', new_reference='N/A')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_error_error_undefok_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFOK_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND some other error'}, {'FLATFILE': 'NOT FOUND some other error'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: Bestref FAILED:  some other error
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_defined_defined_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'x5v1944hl_flat.fits'}, {'FLATFILE': 'x5v1944hl_flat.fits'})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_defined_na_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'x5v1944hl_flat.fits'}, {'FLATFILE': 'NOT FOUND n/a'})
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='X5V1944HL_FLAT.FITS', new_reference='N/A')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_defined_undefined_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'x5v1944hl_flat.fits'}, {'FLATFILE': 'UNDEFINED'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: No match found: 'UNDEFINED'
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_defined_omitted_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'x5v1944hl_flat.fits'}, {})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: No match found: 'UNDEFINED'
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_defined_error_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'x5v1944hl_flat.fits'}, {'FLATFILE': 'NOT FOUND some other error'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_na_defined_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND n/a'}, {'FLATFILE': 'x5v1944hl_flat.fits'})
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='N/A', new_reference='X5V1944HL_FLAT.FITS')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_na_na_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND n/a'}, {'FLATFILE': 'NOT FOUND n/a'})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_na_undefined_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND n/a'}, {'FLATFILE': 'UNDEFINED'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: No match found: 'UNDEFINED'
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_na_omitted_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND n/a'}, {})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: No match found: 'UNDEFINED'
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_na_error_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND n/a'}, {'FLATFILE': 'NOT FOUND some other error'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_undefined_defined_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'UNDEFINED'}, {'FLATFILE': 'x5v1944hl_flat.fits'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: No match found: 'UNDEFINED'
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='UNDEFINED', new_reference='X5V1944HL_FLAT.FITS')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_undefined_na_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'UNDEFINED'}, {'FLATFILE': 'NOT FOUND n/a'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: No match found: 'UNDEFINED'
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='UNDEFINED', new_reference='N/A')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_undefined_undefined_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'UNDEFINED'}, {'FLATFILE': 'UNDEFINED'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: No match found: 'UNDEFINED'
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: No match found: 'UNDEFINED'
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_undefined_omitted_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'UNDEFINED'}, {})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: No match found: 'UNDEFINED'
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: No match found: 'UNDEFINED'
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_undefined_error_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'UNDEFINED'}, {'FLATFILE': 'NOT FOUND some other error'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: No match found: 'UNDEFINED'
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_omitted_defined_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {}, {'FLATFILE': 'x5v1944hl_flat.fits'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: No match found: 'UNDEFINED'
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='UNDEFINED', new_reference='X5V1944HL_FLAT.FITS')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_omitted_na_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {}, {'FLATFILE': 'NOT FOUND n/a'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: No match found: 'UNDEFINED'
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='UNDEFINED', new_reference='N/A')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_omitted_undefined_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {}, {'FLATFILE': 'UNDEFINED'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: No match found: 'UNDEFINED'
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: No match found: 'UNDEFINED'
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_omitted_omitted_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {}, {})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_omitted_error_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {}, {'FLATFILE': 'NOT FOUND some other error'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: No match found: 'UNDEFINED'
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_error_defined_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND some other error'}, {'FLATFILE': 'x5v1944hl_flat.fits'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: Bestref FAILED:  some other error
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='NOT FOUND SOME OTHER ERROR', new_reference='X5V1944HL_FLAT.FITS')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_error_na_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND some other error'}, {'FLATFILE': 'NOT FOUND n/a'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: Bestref FAILED:  some other error
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='NOT FOUND SOME OTHER ERROR', new_reference='N/A')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_error_undefined_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND some other error'}, {'FLATFILE': 'UNDEFINED'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: Bestref FAILED:  some other error
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: No match found: 'UNDEFINED'
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_error_omitted_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND some other error'}, {})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: Bestref FAILED:  some other error
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: No match found: 'UNDEFINED'
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_error_error_undefmatters_naok():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAOK.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND some other error'}, {'FLATFILE': 'NOT FOUND some other error'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: Bestref FAILED:  some other error
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_defined_defined_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'x5v1944hl_flat.fits'}, {'FLATFILE': 'x5v1944hl_flat.fits'})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_defined_na_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'x5v1944hl_flat.fits'}, {'FLATFILE': 'NOT FOUND n/a'})
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='X5V1944HL_FLAT.FITS', new_reference='N/A')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_defined_undefined_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'x5v1944hl_flat.fits'}, {'FLATFILE': 'UNDEFINED'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: No match found: 'UNDEFINED'
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_defined_omitted_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'x5v1944hl_flat.fits'}, {})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: No match found: 'UNDEFINED'
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_defined_error_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'x5v1944hl_flat.fits'}, {'FLATFILE': 'NOT FOUND some other error'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_na_defined_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND n/a'}, {'FLATFILE': 'x5v1944hl_flat.fits'})
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='N/A', new_reference='X5V1944HL_FLAT.FITS')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_na_na_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND n/a'}, {'FLATFILE': 'NOT FOUND n/a'})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_na_undefined_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND n/a'}, {'FLATFILE': 'UNDEFINED'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: No match found: 'UNDEFINED'
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_na_omitted_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND n/a'}, {})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: No match found: 'UNDEFINED'
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_na_error_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND n/a'}, {'FLATFILE': 'NOT FOUND some other error'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_undefined_defined_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'UNDEFINED'}, {'FLATFILE': 'x5v1944hl_flat.fits'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: No match found: 'UNDEFINED'
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='UNDEFINED', new_reference='X5V1944HL_FLAT.FITS')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_undefined_na_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'UNDEFINED'}, {'FLATFILE': 'NOT FOUND n/a'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: No match found: 'UNDEFINED'
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='UNDEFINED', new_reference='N/A')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_undefined_undefined_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'UNDEFINED'}, {'FLATFILE': 'UNDEFINED'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: No match found: 'UNDEFINED'
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: No match found: 'UNDEFINED'
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_undefined_omitted_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'UNDEFINED'}, {})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: No match found: 'UNDEFINED'
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: No match found: 'UNDEFINED'
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_undefined_error_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'UNDEFINED'}, {'FLATFILE': 'NOT FOUND some other error'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: No match found: 'UNDEFINED'
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_omitted_defined_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {}, {'FLATFILE': 'x5v1944hl_flat.fits'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: No match found: 'UNDEFINED'
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='UNDEFINED', new_reference='X5V1944HL_FLAT.FITS')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_omitted_na_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {}, {'FLATFILE': 'NOT FOUND n/a'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: No match found: 'UNDEFINED'
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='UNDEFINED', new_reference='N/A')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_omitted_undefined_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {}, {'FLATFILE': 'UNDEFINED'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: No match found: 'UNDEFINED'
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: No match found: 'UNDEFINED'
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_omitted_omitted_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {}, {})
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_omitted_error_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {}, {'FLATFILE': 'NOT FOUND some other error'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: No match found: 'UNDEFINED'
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_error_defined_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND some other error'}, {'FLATFILE': 'x5v1944hl_flat.fits'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: Bestref FAILED:  some other error
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='NOT FOUND SOME OTHER ERROR', new_reference='X5V1944HL_FLAT.FITS')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_error_na_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND some other error'}, {'FLATFILE': 'NOT FOUND n/a'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: Bestref FAILED:  some other error
    [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='NOT FOUND SOME OTHER ERROR', new_reference='N/A')]

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_error_undefined_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND some other error'}, {'FLATFILE': 'UNDEFINED'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: Bestref FAILED:  some other error
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: No match found: 'UNDEFINED'
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_error_omitted_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND some other error'}, {})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: Bestref FAILED:  some other error
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: No match found: 'UNDEFINED'
    []

    >>> test_config.cleanup(old_state)
    '''


def dt_compare_bestrefs_error_error_undefmatters_namatters():
    '''
    >>> old_state = test_config.setup()

    >>> SCRIPT_UNDEFMATTERS_NAMATTERS.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'NOT FOUND some other error'}, {'FLATFILE': 'NOT FOUND some other error'})
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  Old: Bestref FAILED:  some other error
    CRDS - ERROR - instrument='COS' type='FLATFILE' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error
    []

    >>> test_config.cleanup(old_state)
    '''
