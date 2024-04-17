import os
import crds
from crds.core import log, exceptions
from crds.core import config as crds_config
from crds.bestrefs import BestrefsScript
from pytest import mark

# ensure CRDS logger propagates events to pytest log capture.
log.THE_LOGGER.logger.propagate = True

# Contrived headers which will select bad files.

HST_HEADER = {
    'INSTRUME': 'ACS',
    'REFTYPE': 'PFLTFILE',
    'DETECTOR': 'SBC',
    'CCDAMP': 'N/A',
    'FILTER1': 'PR110L',
    'FILTER2': 'N/A',
    'OBSTYPE': 'SPECTROSCOPIC',
    'FW1OFFST': 'N/A',
    'FW2OFFST': 'N/A',
    'FWOFFST': 'N/A',
    'DATE-OBS': '1991-01-01',
    'TIME-OBS': '00:00:00'
    }

JWST_HEADER = {
    "meta.instrument.name": "MIRI",
    "meta.observation.date": "2012-07-25T00:00:00",
    "meta.instrument.detector": "MIRIMAGE",
    "meta.instrument.filter": "F1000W",
    "meta.subarray.name": "FULL",
    }


@mark.hst
@mark.bad_files
def test_bad_references_error_cache_config(default_shared_state):
    crds_config.ALLOW_BAD_RULES.reset()
    crds_config.ALLOW_BAD_REFERENCES.reset()
    out_to_check = "Recommended reference 'l2d0959cj_pfl.fits' of type 'pfltfile' is designated scientifically invalid."
    try:
        crds.getreferences(HST_HEADER, observatory='hst', context='hst_0282.pmap', reftypes=['pfltfile'])
    except exceptions.CrdsBadReferenceError as cbre:
        assert out_to_check in cbre.args[0]


@mark.hst
@mark.bad_files
def test_bad_References_warning_Cache_config(capsys, default_shared_state):
    cache = default_shared_state.cache
    crds_config.ALLOW_BAD_RULES.set("1")
    crds_config.ALLOW_BAD_REFERENCES.set("1")
    crds.getreferences(HST_HEADER, observatory='hst', context='hst_0282.pmap', reftypes=['pfltfile'])
    _, err = capsys.readouterr()
    out_to_check = """Recommended reference 'l2d0959cj_pfl.fits' of type 'pfltfile' is designated scientifically \
invalid."""
    assert out_to_check in err


@mark.hst
@mark.bad_files
def test_bad_references_fast_mode(default_shared_state):
    cache = default_shared_state.cache
    crds_config.ALLOW_BAD_RULES.reset()
    crds_config.ALLOW_BAD_REFERENCES.reset()
    val = crds.getreferences(HST_HEADER, observatory='hst', context='hst_0282.pmap', reftypes=['pfltfile'], fast=True)
    val_to_check = {}
    val_to_check['pfltfile'] = f'{cache}/references/hst/l2d0959cj_pfl.fits'
    assert val == val_to_check


@mark.hst
@mark.bad_files
def test_bad_references_bestrefs_script_error(caplog, default_shared_state, hst_data):
    """Test for error messages from the script for bad references

    Notes
    -----
    The `config` object cannot be used for the script test. The script depends totally
    on the option `--allow-bad-references`. The absence of this option means do not allow
    and produce an error.
    """
    args = f"crds.bestrefs --new-context hst_0282.pmap --files {hst_data}/j8btxxx_raw_bad.fits"
    old_verbosity = log.set_verbose(0)  # Take down the verbosity. Anything higher produces different error messages.
    try:
        BestrefsScript(args)()
        out = caplog.text
        print('out is')
        print(out)
    finally:
        log.set_verbose(old_verbosity)

    out_to_check = """No comparison context or source comparison requested.
    No file header updates requested;  dry run.  Use --update-bestrefs to update FITS headers.
    ===> Processing
    j8btxxx_raw_bad.fits
    instrument='ACS' type='PFLTFILE' data='
    j8btxxx_raw_bad.fits' ::  File 'L2D0959CJ_PFL.FITS' is bad. Use is not recommended,  results may not be scientifically valid.
    1 errors
    0 warnings""".splitlines()
    for line in out_to_check:
        assert line.strip() in out


@mark.hst
@mark.bad_files
def test_bad_references_bestrefs_script_warning(caplog, default_shared_state, hst_data):
    """Test for warning messages from the script for bad references

    Notes
    -----
    The `config` object cannot be used for the script test. The script depends totally
    on the option `--allow-bad-references`. The presence of this option means allow
    and produce a warning.
    """
    args = f"crds.bestrefs --new-context hst_0282.pmap --files {hst_data}/j8btxxx_raw_bad.fits --allow-bad-references"
    old_verbosity = log.set_verbose(0)  # Take down the verbosity. Anything higher produces different error messages.
    try:
        BestrefsScript(args)()
        out = caplog.text
        print('out is')
        print(out)
    finally:
        log.set_verbose(old_verbosity)

    out_to_check = f"""No comparison context or source comparison requested.
    No file header updates requested;  dry run.  Use --update-bestrefs to update FITS headers.
    ===> Processing
    j8btxxx_raw_bad.fits
    For
    j8btxxx_raw_bad.fits ACS pfltfile File 'L2D0959CJ_PFL.FITS' is bad. Use is not recommended,  results may not be scientifically valid.
    0 errors
    1 warnings""".splitlines()
    for line in out_to_check:
        assert line.strip() in out


@mark.jwst
@mark.bad_files
def test_bad_rules_jwst_getreferences_error(jwst_serverless_state, default_cache):
    jwst_serverless_state.cache = default_cache
    jwst_serverless_state.mode = 'auto'
    jwst_serverless_state.config_setup()
    crds_config.ALLOW_BAD_RULES.reset()
    crds_config.ALLOW_BAD_REFERENCES.reset()
    out_to_check = """Final context 'jwst_0017.pmap' is marked as scientifically \
invalid based on: ['jwst_miri_flat_0003.rmap']"""
    try:
        crds.getreferences(JWST_HEADER, observatory='jwst', context='jwst_0017.pmap', reftypes=["flat"])
    except exceptions.CrdsBadRulesError as cbre:
        assert out_to_check in cbre.args[0]

@mark.jwst
@mark.bad_files
def test_bad_rules_jwst_getreferences_warning(jwst_serverless_state, default_cache):
    jwst_serverless_state.cache = default_cache
    jwst_serverless_state.mode = 'auto'
    jwst_serverless_state.config_setup()
    crds_config.ALLOW_BAD_RULES.set("1")
    refs = crds.getreferences(JWST_HEADER, observatory='jwst', context='jwst_0017.pmap', reftypes=["flat"])
    assert list(refs.keys()) == ['flat']
    assert os.path.basename(refs['flat']) == 'jwst_miri_flat_0006.fits'


@mark.jwst
@mark.bad_files
def test_bad_rules_jwst_bestrefs_script_error(jwst_serverless_state, default_cache):
    jwst_serverless_state.cache = default_cache
    jwst_serverless_state.mode = 'auto'
    jwst_serverless_state.config_setup()
    crds_config.ALLOW_BAD_RULES.reset()
    out_to_check = """Final context 'jwst_0017.pmap' is marked as scientifically invalid based \
on: ['jwst_miri_flat_0003.rmap']"""
    try:
        crds.getrecommendations(JWST_HEADER, reftypes=["gain"], context="jwst_0017.pmap")
    except exceptions.CrdsBadRulesError as cbre:
        assert out_to_check in cbre.args[0]
