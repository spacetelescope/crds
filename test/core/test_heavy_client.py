from pytest import mark
import os
import re
from crds.core import log, heavy_client, utils
from crds.core import config as crds_config
from crds.core.exceptions import *
from crds.client import api


@mark.jwst
@mark.core
@mark.heavy_client
def test_getreferences_rmap_na(jwst_no_cache_state, jwst_data):
    utils.clear_function_caches()
    os.environ["CRDS_MAPPATH_SINGLE"] = jwst_data
    refs = heavy_client.getreferences({
        "META.INSTRUMENT.NAME":"NIRISS", "META.INSTRUMENT.DETECTOR":"NIS",
        "META.INSTRUMENT.FILTER":"BOGUS2", "META.EXPOSURE.TYPE":"NIS_IMAGE"
    },
    observatory="jwst", 
    context=os.path.join(jwst_data, "jwst_na_omit.pmap"),
    ignore_cache=False, 
    reftypes=["flat"])
    assert refs == {'flat': 'NOT FOUND n/a'}


@mark.jwst
@mark.core
@mark.heavy_client
def test_getreferences_rmap_omit(jwst_no_cache_state, jwst_data):
    utils.clear_function_caches()
    os.environ["CRDS_MAPPATH_SINGLE"] = jwst_data
    refs = heavy_client.getreferences(
        {
            "META.INSTRUMENT.NAME":"NIRISS", 
            "META.INSTRUMENT.DETECTOR":"NIS", 
            "META.INSTRUMENT.FILTER":"BOGUS1", 
            "META.EXPOSURE.TYPE":"NIS_IMAGE"
        },
        observatory="jwst", 
        context=os.path.join(jwst_data, "jwst_na_omit.pmap"),
        ignore_cache=False, 
        reftypes=["flat"]
    )
    assert refs == {}


@mark.jwst
@mark.core
@mark.heavy_client
def test_getreferences_imap_na(jwst_no_cache_state, jwst_data):
    utils.clear_function_caches()
    os.environ["CRDS_MAPPATH_SINGLE"] = jwst_data
    refs = heavy_client.getreferences(
        {
            "META.INSTRUMENT.NAME":"FGS",
            "META.EXPOSURE.TYPE":"FGS_IMAGE"
        },
        observatory="jwst",
        context=os.path.join(jwst_data, "jwst_na_omit.pmap"),
        ignore_cache=False,
        reftypes=["flat"]
    )
    assert refs == {'flat': 'NOT FOUND n/a'}


@mark.jwst
@mark.core
@mark.heavy_client
def test_getreferences_imap_omit(jwst_no_cache_state, jwst_data):
    utils.clear_function_caches()
    os.environ["CRDS_MAPPATH_SINGLE"] = jwst_data
    refs = heavy_client.getreferences(
        {
            "META.INSTRUMENT.NAME":"MIRI",
            "META.EXPOSURE.TYPE":"MIR_IMAGE"
        },
        observatory="jwst",
        context=os.path.join(jwst_data, "jwst_na_omit.pmap"),
        ignore_cache=False,
        reftypes=["flat"]
    )
    assert refs == {}


@mark.jwst
@mark.core
@mark.heavy_client
def test_getreferences_ignore_cache(jwst_shared_cache_state):
    header = {
        "META.INSTRUMENT.NAME":"MIRI",
        "META.EXPOSURE.TYPE":"MIR_IMAGE",
        "META.OBSERVATION.DATE":"2018-05-25",
        "META.OBSERVATION.TIME":"00:00:00"
    }
    refs = heavy_client.getreferences(
        header,
        observatory="jwst",
        context="jwst_miri.imap",
        ignore_cache=True,
        reftypes=["flat"]
    )
    cache_path = jwst_shared_cache_state.cache
    assert refs == {'flat': f'{cache_path}/references/jwst/jwst_miri_flat_0001.fits'}


@mark.jwst
@mark.core
@mark.heavy_client
def test_cache_references_multiple_bad_files(default_shared_state):
    """
    Define bestrefs with multiple errors which should all be reported
    prior to raising an exception.

    To work effectively for JWST reference file coverage improvement,
    CRDS needs to report ALL bad references in a given Step or
    prefetch, not just raise an exception on the first bad reference
    found.
    """
    error_message = None
    expected = "Error determining best reference for 'dark'  =   something else went wrong for dark."
    bestrefs = {
        "flat": "NOT FOUND something went wrong for flat.",
        "dark": "NOT FOUND something else went wrong for dark.",
    }
    try:
        api.cache_references("jwst.pmap", bestrefs)
    except CrdsLookupError as e:
        error_message = str(e)
    assert error_message == expected


@mark.jwst
@mark.core
@mark.heavy_client
def test_get_context_name_literal(jwst_serverless_state):
    jwst_serverless_state.mode = 'local'
    jwst_serverless_state.config_setup()
    context = heavy_client.get_context_name("jwst", "jwst_0341.pmap")
    assert context == 'jwst_0341.pmap'


@mark.jwst
@mark.core
@mark.heavy_client
def test_get_context_name_crds_context(jwst_serverless_state):
    jwst_serverless_state.mode = 'local'
    jwst_serverless_state.config_setup()
    os.environ["CRDS_CONTEXT"] = "jwst_0399.pmap"
    context = heavy_client.get_context_name("jwst")
    del os.environ["CRDS_CONTEXT"]
    assert context == 'jwst_0399.pmap'


@mark.jwst
@mark.core
@mark.heavy_client
def test_get_context_name_symbolic(jwst_serverless_state):
    jwst_serverless_state.mode = 'local'
    jwst_serverless_state.config_setup()
    pattern = re.compile("jwst_[0-9]{4}.pmap")
    ops_context = heavy_client.get_context_name("jwst", "jwst-operational")
    edit_context = heavy_client.get_context_name("jwst", "jwst-edit")
    ver_context = heavy_client.get_context_name("jwst", "jwst-versions")

    for context in [ops_context, edit_context, ver_context]:
        matches = re.match(pattern, context)
        assert matches.group() is not None


@mark.jwst
@mark.core
@mark.heavy_client
def test_translate_date_based_context_no_observatory(jwst_serverless_state):
    try:
        heavy_client.translate_date_based_context("foo-edit", observatory=None)
    except CrdsError as e:
        error = str(e)
    assert error == "Cannot determine observatory to translate mapping 'foo-edit'"


@mark.jwst
@mark.core
@mark.heavy_client
def test_translate_date_based_context_bad_date(jwst_serverless_state):
    try:
        heavy_client.translate_date_based_context("jwst-2018-01-01T00:00:00")
    except CrdsError as e:
        error = str(e)
    assert error == "Specified CRDS context by date 'jwst-2018-01-01T00:00:00' and CRDS server is not reachable."
    

@mark.jwst
@mark.core
@mark.heavy_client
def test_translate_date_based_context_bad_instrument(jwst_shared_cache_state):
    jwst_shared_cache_state.observatory = "jwst"
    jwst_shared_cache_state.config_setup()
    try:
        heavy_client.translate_date_based_context("jwst-foo-2018-01-01T00:00:00")
    except ServiceError as e:
        error = str(e)
    assert error == "CRDS jsonrpc failure 'get_context_by_date' InvalidDateBasedContext: Bad instrument 'foo' in CRDS date based context specification."


@mark.jwst
@mark.core
@mark.heavy_client
def test_get_bad_mappings_in_context_no_instrument(jwst_serverless_state):
    mappings = heavy_client.get_bad_mappings_in_context("jwst", "jwst_0016.pmap")
    assert mappings == ['jwst_miri_flat_0002.rmap']
    

@mark.jwst
@mark.core
@mark.heavy_client
def test_pickled_mappings(default_shared_state):
    cache_path = default_shared_state.cache
    pickle_file = crds_config.locate_pickle("jwst_0016.pmap","jwst")
    assert pickle_file == f"{cache_path}/pickles/jwst/jwst_0016.pmap.pkl"
    _ = heavy_client.get_pickled_mapping("jwst_0016.pmap", cached=True, use_pickles=True, save_pickles=True)
    assert os.path.exists(pickle_file)
    p2 = heavy_client.get_pickled_mapping("jwst_0016.pmap", cached=False, use_pickles=False, save_pickles=False)
    assert p2.name == "jwst_0016.pmap"
    p3 = heavy_client.get_pickled_mapping("jwst_0016.pmap", cached=False, use_pickles=True, save_pickles=False)
    assert p3.name == "jwst_0016.pmap"
    p4 = heavy_client.load_pickled_mapping("jwst_0016.pmap")
    assert p4.name == 'jwst_0016.pmap'
    _ = log.set_verbose()
    os.chmod(pickle_file, 0o444)
    heavy_client.remove_pickled_mapping("jwst_0016.pmap")
    assert os.path.exists(pickle_file)
    os.chmod(pickle_file, 0o666)
    heavy_client.remove_pickled_mapping("jwst_0016.pmap")
    assert not os.path.exists(pickle_file)
    

@mark.jwst
@mark.core
@mark.heavy_client
def test_check_parameters(jwst_serverless_state):
    header1 = { "NAME" : "VALID_VALUE",  "NAME1" : 1.0, "META.VALID.NAME3" : 1,   "NAME4" : True}
    out1 = heavy_client.check_parameters(header1)
    header2 = { (1,2,3) : "something for invalid key" }
    try:
        heavy_client.check_parameters(header2)
    except AssertionError as e:
        err = str(e)
    header3 = { "META.BAD.VALUE" : object() }
    out3 = heavy_client.check_parameters(header3)
    assert out1 == {'NAME': 'VALID_VALUE', 'NAME1': 1.0, 'META.VALID.NAME3': 1, 'NAME4': True}
    assert err == "Non-string key (1, 2, 3) in parameters."
    assert out3 == {}


@mark.multimission
@mark.core
@mark.heavy_client
def test_check_context():
    heavy_client.check_context(None)


@mark.jwst
@mark.core
@mark.heavy_client
def dt_get_context_parkeys(jwst_serverless_state):
    parkeys = heavy_client.get_context_parkeys("jwst.pmap","miri")
    assert parkeys == [
        'META.INSTRUMENT.TYPE',
        'META.INSTRUMENT.LAMP_STATE',
        'META.OBSERVATION.DATE',
        'META.VISIT.TSOVISIT',
        'REFTYPE'
    ]
    parkeys2 = heavy_client.get_context_parkeys("jwst_miri.imap","miri")
    assert parkeys2 == ['META.INSTRUMENT.LAMP_STATE', 'META.OBSERVATION.DATE', 'META.VISIT.TSOVISIT', 'REFTYPE']
    parkeys3 = heavy_client.get_context_parkeys("jwst_miri_flat.rmap","miri")
    assert parkeys3 == ['META.OBSERVATION.DATE', 'META.VISIT.TSOVISIT', 'META.INSTRUMENT.LAMP_STATE']
