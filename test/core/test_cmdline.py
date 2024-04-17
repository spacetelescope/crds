from pytest import mark
import os
import logging
from crds.core import cmdline, utils, log
from crds.core import config as crds_config
from crds.core.cmdline import Script, ContextsScript

log.THE_LOGGER.logger.propagate=True

@mark.hst
@mark.core
@mark.cmdline
def test_valid_and_invalid_dataset(default_shared_state, hst_data):
    """
    command line parameter checking filter for dataset files  plausibility only.
    """
    try:
        cmdline.dataset("foo.nothing")
    except ValueError:
        assert True
    fpath = cmdline.dataset(f"{hst_data}/j8bt05njq_raw.fits")
    assert fpath == f"{hst_data}/j8bt05njq_raw.fits"
    

@mark.hst
@mark.core
@mark.cmdline
def test_valid_and_invalid_mapping(default_shared_state, hst_data):
    """
    command line parameter checking filter for mapping files.
    """
    try:
        cmdline.mapping("foo.fits")
    except AssertionError:
        assert True
    mp = cmdline.mapping("hst.pmap")
    assert mp == 'hst.pmap'
    

@mark.hst
@mark.core
@mark.cmdline
def test_context_spec(default_shared_state):
    ctx1 = cmdline.context_spec("hst_0042.pmap")
    assert ctx1 == 'hst_0042.pmap'
    ctx2 = cmdline.context_spec("hst.pmap")
    assert ctx2 == 'hst.pmap'
    ctx3 = cmdline.context_spec("hst-2040-01-29T12:00:00")
    assert ctx3 == 'hst-2040-01-29T12:00:00'
    try:
        cmdline.context_spec("hst-acs-2040-01-29T12:00:00")
    except AssertionError:
        assert True
    

@mark.multimission
@mark.core
@mark.cmdline
def test_observatory_valid_and_invalid(default_shared_state):
    obs = cmdline.observatory("hst")
    assert obs == 'hst'
    obs = cmdline.observatory("jwst")
    assert obs == 'jwst'
    try:
        cmdline.observatory("foo")
    except AssertionError:
        assert True
    

@mark.multimission
@mark.core
@mark.cmdline
def test_process_key(default_shared_state):
    key1 = cmdline.process_key("foo")
    assert key1 == 'foo'
    key2 = cmdline.process_key("81323850-9517-416c-ae88-e6481de10a71")
    assert key2 == '81323850-9517-416c-ae88-e6481de10a71'
    try:
        cmdline.process_key("/foo/bar")
    except AssertionError:
        assert True
    

@mark.multimission
@mark.core
@mark.cmdline
def test_user_name(default_shared_state):
    uname = cmdline.user_name("foo")
    assert uname == 'foo'
    try:
        cmdline.user_name("81323850-9517-416c-ae88-e6481de10a71")
    except AssertionError:
        assert True
    try:
        cmdline.user_name('hst.pmap')
    except AssertionError: 
        assert True
    try:
        cmdline.user_name("/foo/bar")
    except AssertionError:
        assert True
    

@mark.multimission
@mark.core
@mark.cmdline
def test_observatories_obs_pkg(default_shared_state):
    utils.clear_function_caches()
    s = Script("cmdline.Script --hst")
    assert s.obs_pkg.__name__ == 'crds.hst'
    assert s.observatory == 'hst'
    utils.clear_function_caches()
    s = Script("cmdline.Script --jwst")
    assert s.obs_pkg.__name__ == 'crds.jwst'
    assert s.observatory == 'jwst'
    _ = os.environ.pop("CRDS_SERVER_URL", None)
    _ = crds_config.OBSERVATORY.set("hst")
    utils.clear_function_caches()
    obs = Script("cmdline.Script").observatory
    assert obs == 'hst'


@mark.skip(reason="argparse attribute error")
@mark.core
@mark.cmdline
def test_print_help(default_shared_state):
    Script("cmdline.Script").print_help()
    

@mark.multimission
@mark.core
@mark.cmdline
def test_require_server_connnection(default_shared_state):
    Script("cmdline.Script").require_server_connection()
    

@mark.multimission
@mark.core
@mark.cmdline
def test_no_files_in_class(default_shared_state):
    try:
        Script("cmdline.Script").files
    except NotImplementedError:
        assert True
    

@mark.hst
@mark.core
@mark.cmdline
def test_get_files(default_shared_state, hst_data):
    s = Script("cmdline.Script")
    files = s.get_files([f"{hst_data}/file_list1"]) 
    assert files == [f'{hst_data}/file_list1']
    files = s.get_files(["@test/data/hst/file_list1"])
    assert files == ['hst.pmap', 'hst_0002.pmap', 'hst_0001.pmap']
    

@mark.hst
@mark.core
@mark.cmdline
def test_resolve_context(default_shared_state, caplog):
    s = Script("cmdline.Script --hst")
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        ctx = s.resolve_context("hst-2016-01-01")
        out = caplog.messages
    assert ctx == 'hst_0379.pmap'
    expected = " Symbolic context 'hst-2016-01-01' resolves to 'hst_0379.pmap'"
    assert expected in out
    

@mark.jwst
@mark.core
@mark.cmdline
def test_get_file_properties(default_shared_state, jwst_data):
    s = Script("cmdline.Script")
    props = s.get_file_properties("hst_acs_biasfile_0005.rmap")
    assert props == ('acs', 'biasfile')
    props = s.get_file_properties("hst_acs_biasfile_0005.fits")
    assert props == ('acs', 'biasfile')
    s = Script("crds.Script --jwst")
    props = s.get_file_properties(f"{jwst_data}/valid.asdf")
    assert props == ('nirspec', 'wavecorr')
    

@mark.hst
@mark.core
@mark.cmdline
def test_categorize_files(default_shared_state, hst_data):
    s = Script("cmdline.Script")
    cats = s.categorize_files(["hst.pmap", f"{hst_data}/hst_acs_9999.imap", f"{hst_data}/acs_new_idc.fits"])
    assert sorted(cats.items()) == [(('', ''), ['hst.pmap']), (('acs', ''), [f'{hst_data}/hst_acs_9999.imap']), (('acs', 'idctab'), [f'{hst_data}/acs_new_idc.fits'])]
    

@mark.hst
@mark.core
@mark.cmdline
def test_dump_files(default_shared_state):
    s = Script("cmdline.Script")
    s.dump_files(files=["hst.pmap","hst_acs_biasfile_0250.rmap"])
    

@mark.hst
@mark.core
@mark.cmdline
def test_sync_files(default_shared_state):
    s = Script("cmdline.Script")
    s.sync_files(["hst_acs_biasfile_0250.rmap"])
    

@mark.hst
@mark.core
@mark.cmdline
def test_are_all_mappings(default_shared_state):
    s = Script("cmdline.Script")
    allmaps = s.are_all_mappings(["hst_acs_biasfile_0250.rmap"])
    assert allmaps is True
    notallmaps = s.are_all_mappings(["hst_acs_biasfile_0250.rmap", "somethingelse.fits"])
    assert notallmaps is False
    

@mark.hst
@mark.core
@mark.cmdline
def test_file_outside_cache_pathless(default_shared_state):
    s = Script("cmdline.Script")
    path = s.locate_file_outside_cache("hst_0001.pmap")
    assert path.endswith('./hst_0001.pmap')
    

@mark.jwst
@mark.core
@mark.cmdline
def test_file_outside_cache_uri(default_test_cache_state):
    """Explicit crds:// notation for files inside cache."""
    s = Script("cmdline.Script --jwst")
    path = s.locate_file_outside_cache("crds://jwst_0001.pmap")
    assert path.endswith("crds-cache-test/mappings/jwst/jwst_0001.pmap")


@mark.hst
@mark.core
@mark.cmdline
def test_file_outside_cache_mapping_spec(default_test_cache_state):
    s = Script("cmdline.Script --hst")
    path = s.locate_file_outside_cache("hst-2016-01-01")
    assert path.endswith("crds-cache-test/mappings/hst/hst_0379.pmap")


@mark.hst
@mark.core
@mark.cmdline
def test_resolve_context_operational(default_test_cache_state):
    s = Script("cmdline.Script --hst")
    context = s.resolve_context("hst-operational")
    assert context.startswith("hst_") and context.endswith(".pmap")


@mark.hst
@mark.core
@mark.cmdline
def test_dump_mappings(default_test_cache_state):
    s = Script("cmdline.Script --ignore-cache")
    s.dump_mappings(["hst_acs.imap"])


@mark.multimission
@mark.core
@mark.cmdline
def test_determine_contexts_all(default_test_cache_state):
    s = ContextsScript("cmdline.ContextsScript --all")
    contexts = s.determine_contexts()
    assert len(contexts) > 100


@mark.multimission
@mark.core
@mark.cmdline
def test_determine_contexts_last_n(default_test_cache_state):
    s = ContextsScript("cmdline.ContextsScript --last 5")
    contexts = s.determine_contexts()
    assert len(contexts) == 5


@mark.multimission
@mark.core
@mark.cmdline
def test_determine_contexts_range(default_test_cache_state):
    s = ContextsScript("cmdline.ContextsScript --range 1:7")
    contexts = s.determine_contexts()
    assert len(contexts) == 7


@mark.hst
@mark.core
@mark.cmdline
def test_determine_contexts_upto(default_test_cache_state):
    s = ContextsScript("cmdline.ContextsScript --up-to-context hst-2016-01-01")
    contexts = s.determine_contexts()
    assert len(contexts) == 195
    assert contexts[0] == "hst.pmap"


@mark.hst
@mark.core
@mark.cmdline
def test_determine_contexts_after(default_test_cache_state):
    s = ContextsScript("cmdline.ContextsScript --after-context hst-2016-01-01")
    contexts = s.determine_contexts()
    assert len(contexts) >= 108
    assert contexts[0] == "hst_0379.pmap"


@mark.hst
@mark.core
@mark.cmdline
def test_determine_contexts_direct(default_test_cache_state):
    s = ContextsScript("cmdline.ContextsScript --contexts hst.pmap")
    s.contexts = contexts = s.determine_contexts()
    assert len(contexts) == 1
    assert contexts[0] == "hst.pmap"
    mappings = sorted(list(set(s.get_context_mappings())))
    assert len(mappings) >= 116
