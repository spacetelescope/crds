"""Special case tests verify behavior in various configurations:

--regression
--na-differences-matter
--undefined-differences-matter

"""
from pytest import mark, fixture
from collections import namedtuple
from crds.bestrefs import BestrefsScript
from crds.core import log
import logging

log.THE_LOGGER.logger.propagate=True

UpdateTuple = namedtuple("UpdateTuple", ["instrument", "filekind", "old_reference", "new_reference"])

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

BESTREFS_OMITTED= {}

BESTREFS_ERROR = {
    "FLATFILE" : "NOT FOUND some other error",
}


def check_logs(expected, out):
    for line in expected.splitlines():
        assert line.strip() in out

@mark.hst
@mark.special
def test_bestrefs_na_undefined_single_ctx_defaults(hst_shared_cache_state, hst_data, caplog):
    # Instantiate a BestrefsScript with default settings and dummy parameters, simulating pipeline bestrefs defaults
    with caplog.at_level(logging.INFO, logger="CRDS"):
        script = BestrefsScript(argv=f"crds.bestrefs --load-pickles {hst_data}/bestrefs.special.json --new-context hst_0315.pmap")
        script.complex_init()
        out = caplog.text
    expected = f"""Loading file '{hst_data}/bestrefs.special.json'
    Loaded 1 datasets from file '{hst_data}/bestrefs.special.json' completely replacing existing headers.
    No comparison context or source comparison requested."""
    check_logs(expected, out)
    
    #Skip ahead past bestrefs (faked) into special values results evaluation.
    exp_res = [
        (True, 'X5V1944HL_FLAT.FITS'),
        (True, 'N/A'),
        (True, 'N/A'),
        (True, 'N/A'),
        (False, 'NOT FOUND SOME OTHER ERROR')
    ]
    #First a positive result:  OK,  lowercase-original-result,  uppercase-final-result-for-update
    b0 = script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "FLATFILE")

    #Second a formal N/A result:  OK,  bestrefs string,  final update value
    b1 = script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "BADTTAB")

    # An explicit response of UNDEFINED,  by default converted to N/A for update,  considered OK
    b2 = script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "BRFTAB")

    #An implicit response of UNDEFINED, i.e. OMIT, also coverted to N/A for update
    b3 = script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "XTRACTAB")

    #An explicit error response from CRDS,  not OK
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="CRDS"):
        b4 = script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "TRACETAB")
        out = caplog.text

    for i, b in enumerate([b0, b1, b2, b3, b4]):
        assert b == exp_res[i]
    assert """instrument='COS' type='TRACETAB' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error""" in out


@mark.hst
@mark.special
def test_bestrefs_na_undefined_single_ctx_undefined_matters(hst_shared_cache_state, hst_data, caplog):
    # Instantiate a BestrefsScript with default settings and dummy parameters, simulating pipeline bestrefs defaults
    with caplog.at_level(logging.INFO, logger="CRDS"):
        script = BestrefsScript(argv=f"crds.bestrefs --load-pickles {hst_data}/bestrefs.special.json --undefined-differences-matter --new-context hst_0315.pmap")
        script.complex_init()
        out = caplog.text
    expected = f"""Loading file '{hst_data}/bestrefs.special.json'
    Loaded 1 datasets from file '{hst_data}/bestrefs.special.json' completely replacing existing headers.
    No comparison context or source comparison requested."""
    check_logs(expected, out)

    # Skip ahead past bestrefs (faked) into special values results evaluation.
    exp_res = [
        (True, 'X5V1944HL_FLAT.FITS'),
        (True, 'N/A'),
        (False, 'UNDEFINED'),
        (False, 'UNDEFINED'),
        (False, 'NOT FOUND SOME OTHER ERROR')
    ]
    # First a postitive result:  OK,  lowercase-original-result,  uppercase-final-result-for-update
    b0 = script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "FLATFILE")

    #Second a formal N/A result:  OK,  bestrefs string,  final update value
    b1 = script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "BADTTAB")

    #An explicit response of UNDEFINED,  by default converted to N/A for update,  not OK since -undefined-differences-matter
    with caplog.at_level(logging.INFO, logger="CRDS"):
        b2 = script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "BRFTAB")
        out1 = caplog.text
    err1 = "instrument='COS' type='BRFTAB' data='LA9K03C3Q' ::  New: No match found: 'UNDEFINED'"
    caplog.clear()

    #An implicit response of UNDEFINED, i.e. OMIT, also coverted to N/A for update, not OK since -undefined-differences-matter
    with caplog.at_level(logging.INFO, logger="CRDS"):
        b3 = script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "XTRACTAB")
        out2 = caplog.text
    err2 = "instrument='COS' type='XTRACTAB' data='LA9K03C3Q' ::  New: No match found: 'UNDEFINED'"
    caplog.clear()

    #An explicit error response from CRDS,  not OK
    with caplog.at_level(logging.INFO, logger="CRDS"):
        b4 = script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "TRACETAB")
        out3 = caplog.text

    err3 = "instrument='COS' type='TRACETAB' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error"
    for i, b in enumerate([b0, b1, b2, b3, b4]):
        assert b == exp_res[i]
    for err, msg in zip([err1, err2, err3], [out1, out2, out3]):
        assert err in msg


@mark.hst
@mark.special
def test_bestrefs_na_undefined_single_ctx_na_matters(hst_shared_cache_state, hst_data, caplog):
    script = BestrefsScript(argv=f"crds.bestrefs --load-pickles {hst_data}/bestrefs.special.json --na-differences-matter --new-context hst_0315.pmap")
    script.complex_init()
    expected = f"""Loading file '{hst_data}/bestrefs.special.json'
    Loaded 1 datasets from file '{hst_data}/bestrefs.special.json' completely replacing existing headers.
    No comparison context or source comparison requested."""

    #Skip ahead past bestrefs (faked) into special values results evaluation.
    exp_res = [
        (True, 'X5V1944HL_FLAT.FITS'),
        (True, 'N/A'),
        (True, 'N/A'),
        (True, 'N/A'),
        (False, 'NOT FOUND SOME OTHER ERROR'),
    ]
    #First a postitive result:  OK,  lowercase-original-result,  uppercase-final-result-for-update
    b0 = script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "FLATFILE")

    #Second a formal N/A result:  OK,  bestrefs string,  final update value
    b1 = script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "BADTTAB")

    #An explicit response of UNDEFINED,  by default converted to N/A for update,  considered OK
    b2 = script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "BRFTAB")

    #An implicit response of UNDEFINED, i.e. OMIT, also coverted to N/A for update
    b3 = script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "XTRACTAB")

    #An explicit error response from CRDS, not OK
    with caplog.at_level(logging.INFO, logger="CRDS"):
        b4 = script.handle_na_and_not_found("New:", BESTREFS, "LA9K03C3Q", "COS", "TRACETAB")
        out = caplog.text

    for i, b in enumerate([b0, b1, b2, b3, b4]):
        assert b == exp_res[i]
    err = "instrument='COS' type='TRACETAB' data='LA9K03C3Q' ::  New: Bestref FAILED:  some other error"
    assert err in out

# SCRIPT_UNDEFMATTERS_NAMATTERS
@fixture()
def undefmatters_namatters(hst_shared_cache_state, hst_data):
    script  = BestrefsScript(argv=f"crds.bestrefs --load-pickles {hst_data}/bestrefs.special.json --new-context hst_0315.pmap --undefined-differences-matter --na-differences-matter")
    script.complex_init()
    return script

# SCRIPT_UNDEFOK_NAMATTERS
@fixture()
def undefok_namatters(hst_shared_cache_state, hst_data):
    script = BestrefsScript(argv=f"crds.bestrefs --load-pickles {hst_data}/bestrefs.special.json --new-context hst_0315.pmap --na-differences-matter")
    script.complex_init()
    return script

# SCRIPT_UNDEFOK_NAOK
@fixture()
def undefok_naok(hst_shared_cache_state, hst_data):
    script = BestrefsScript(argv=f"crds.bestrefs --load-pickles {hst_data}/bestrefs.special.json --new-context hst_0315.pmap")
    script.complex_init()
    return script

# SCRIPT_UNDEFMATTERS_NAOK
@fixture()
def undefmatters_naok(hst_shared_cache_state, hst_data):
    script = BestrefsScript(argv=f"crds.bestrefs --load-pickles {hst_data}/bestrefs.special.json --new-context hst_0315.pmap --undefined-differences-matter")
    script.complex_init()
    return script

@fixture()
def br_scripts(undefmatters_namatters, undefok_namatters, undefok_naok, undefmatters_naok):
    return dict(
        undefmatters_namatters=undefmatters_namatters,
        undefok_namatters=undefok_namatters,
        undefok_naok=undefok_naok,
        undefmatters_naok=undefmatters_naok
    )


KINDS = ["DEFINED", "NA", "UNDEFINED", "OMITTED", "ERROR"]


res1 = [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='X5V1944HL_FLAT.FITS', new_reference='N/A')]
res2 = [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='N/A', new_reference='X5V1944HL_FLAT.FITS')]

res3 = [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='NOT FOUND SOME OTHER ERROR', new_reference='X5V1944HL_FLAT.FITS')]
res4 = [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='NOT FOUND SOME OTHER ERROR', new_reference='N/A')]

res5 = [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='UNDEFINED', new_reference='X5V1944HL_FLAT.FITS')]
res6 = [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='UNDEFINED', new_reference='N/A')]




EXPECTED_BRS = dict(
    undefok_naok=dict(
        defined_defined=[],
        defined_na=res1, 
        defined_undefined=res1,
        defined_omitted=res1,
        defined_error=[],
        na_defined=res2,
        na_na=[],
        na_undefined=[],
        na_omitted=[],
        na_error=[],
        undefined_defined=res2,
        undefined_na=[],
        undefined_undefined=[],
        undefined_omitted=[],
        undefined_error=[],
        omitted_defined=res2,
        omitted_na=[],
        omitted_undefined=[],
        omitted_omitted=[],
        omitted_error=[],
        error_defined=res3,
        error_na=res4,
        error_undefined=res4,
        error_omitted=res4,
        error_error=[]
    ),
    undefok_namatters=dict(
        defined_defined=[],
        defined_na=res1, 
        defined_undefined=res1,
        defined_omitted=res1,
        defined_error=[],
        na_defined=res2,
        na_na=[],
        na_undefined=[],
        na_omitted=[],
        na_error=[],
        undefined_defined=res2,
        undefined_na=[],
        undefined_undefined=[],
        undefined_omitted=[],
        undefined_error=[],
        omitted_defined=res2,
        omitted_na=[],
        omitted_undefined=[],
        omitted_omitted=[],
        omitted_error=[],
        error_defined=res3,
        error_na=res4,
        error_undefined=res4,
        error_omitted=res4,
        error_error=[]
    ),
    undefmatters_naok=dict(
        defined_defined=[],
        defined_na=res1, 
        defined_undefined=[],
        defined_omitted=[],
        defined_error=[],
        na_defined=res2,
        na_na=[],
        na_undefined=[],
        na_omitted=[],
        na_error=[],
        undefined_defined=res5,
        undefined_na=res6,
        undefined_undefined=[],
        undefined_omitted=[],
        undefined_error=[],
        omitted_defined=res5,
        omitted_na=res6,
        omitted_undefined=[],
        omitted_omitted=[],
        omitted_error=[],
        error_defined=res3,
        error_na=res4,
        error_undefined=[],
        error_omitted=[],
        error_error=[]
    ),
    undefmatters_namatters=dict(
        defined_defined=[],
        defined_na=res1, 
        defined_undefined=[],
        defined_omitted=[],
        defined_error=[],
        na_defined=res2,
        na_na=[],
        na_undefined=[],
        na_omitted=[],
        na_error=[],
        undefined_defined=res5,
        undefined_na=res6,
        undefined_undefined=[],
        undefined_omitted=[],
        undefined_error=[],
        omitted_defined=res5,
        omitted_na=res6,
        omitted_undefined=[],
        omitted_omitted=[],
        omitted_error=[],
        error_defined=res3,
        error_na=res4,
        error_undefined=[],
        error_omitted=[],
        error_error=[],
    )
)

@mark.multimission
@mark.special
@mark.parametrize('undef_matters, na_matters', 
                  [
                      (False, False),
                      (False, True),
                      (True, False),
                      (True, True)
                    ])
def test_generate_comparisons(undef_matters, na_matters, br_scripts):
    for kind1 in KINDS:
        for kind2 in KINDS:
            bestrefs1 = globals()["BESTREFS_" + kind1]
            bestrefs2 = globals()["BESTREFS_" + kind2]
            undef = "undefmatters" if undef_matters else "undefok"
            na = "namatters" if na_matters else "naok"
            script = br_scripts[f"{undef}_{na}"]
            matters_key = f"{undef}_{na}"
            kind_key = f"{kind1.lower()}_{kind2.lower()}"
            brs = script.compare_bestrefs('COS', 'LA9K03C3Q', bestrefs1, bestrefs2)
            assert brs == EXPECTED_BRS[matters_key][kind_key]

# ==================================================================================


@mark.hst
@mark.special
def test_compare_bestrefs_defined_defined2_undefok_namatters(hst_shared_cache_state, undefok_namatters):
    brs = undefok_namatters.compare_bestrefs('COS', 'LA9K03C3Q', {'FLATFILE': 'x5v1944hl_flat.fits'}, {'FLATFILE': 'y5v1944hl_flat.fits'})
    assert brs == [UpdateTuple(instrument='COS', filekind='flatfile', old_reference='X5V1944HL_FLAT.FITS', new_reference='Y5V1944HL_FLAT.FITS')]


# ==================================================================================
