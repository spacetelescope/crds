import sys
import os
import doctest

from crds.core import log, cmdline, utils, config
from crds.core.cmdline import Script, ContextsScript, UniqueErrorsMixin
from crds import tests
from crds.tests import test_config
from crds.list import ListScript

def dt_dataset():
    """
    command line parameter checking filter for dataset files  plausibility only.

    >>> old_state = test_config.setup()

    >>> cmdline.dataset("foo.nothing")
    Traceback (most recent call last):
    ...
    ValueError: Parameter 'foo.nothing' does not appear to be a dataset filename.

    >>> cmdline.dataset("data/j8bt05njq_raw.fits")
    'data/j8bt05njq_raw.fits'

    >>> test_config.cleanup(old_state)
    """

def dt_mapping():
    """
    command line parameter checking filter for mapping files.

    >>> old_state = test_config.setup()

    >>> cmdline.mapping("foo.fits")
    Traceback (most recent call last):
    ...
    AssertionError: A .rmap, .imap, or .pmap file is required but got: 'foo.fits'

    >>> cmdline.mapping("hst.pmap")
    'hst.pmap'

    >>> test_config.cleanup(old_state)
    """

def dt_context_spec():
    """
    >>> old_state = test_config.setup()

    >>> cmdline.context_spec("hst_0042.pmap")
    'hst_0042.pmap'

    >>> cmdline.context_spec("hst.pmap")
    'hst.pmap'

    >>> cmdline.context_spec("hst-2040-01-29T12:00:00")
    'hst-2040-01-29T12:00:00'

    >>> cmdline.context_spec("hst-acs-2040-01-29T12:00:00")
    Traceback (most recent call last):
    ...
    AssertionError: Parameter should be a .pmap or abstract context specifier, not: 'hst-acs-2040-01-29T12:00:00'

    >>> test_config.cleanup(old_state)
    """

def dt_observatory():
    """
    >>> old_state = test_config.setup()

    >>> cmdline.observatory("hst")
    'hst'

    >>> cmdline.observatory("jwst")
    'jwst'

    >>> cmdline.observatory("foo")
    Traceback (most recent call last):
    ...
    AssertionError: Unknown observatory 'foo'

    >>> test_config.cleanup(old_state)
    """

def dt_process_key():
    """
    >>> old_state = test_config.setup()

    >>> cmdline.process_key("foo")
    'foo'

    >>> cmdline.process_key("81323850-9517-416c-ae88-e6481de10a71")
    '81323850-9517-416c-ae88-e6481de10a71'

    >>> cmdline.process_key("/foo/bar")
    Traceback (most recent call last):
    ...
    AssertionError: Invalid format for process key: '/foo/bar'

    >>> test_config.cleanup(old_state)
    """

def dt_user_name():
    """
    >>> old_state = test_config.setup()

    >>> cmdline.user_name("foo")
    'foo'

    >>> cmdline.user_name("81323850-9517-416c-ae88-e6481de10a71")
    Traceback (most recent call last):
    ...
    AssertionError: Invalid user name '81323850-9517-416c-ae88-e6481de10a71'

    >>> cmdline.user_name('hst.pmap')
    Traceback (most recent call last):
    ...
    AssertionError: Invalid user name 'hst.pmap'

    >>> cmdline.user_name("/foo/bar")
    Traceback (most recent call last):
    ...
    AssertionError: Invalid user name '/foo/bar'

    >>> test_config.cleanup(old_state)
    """

def dt_observatories_obs_pkg():
    """
    >>> old_state = test_config.setup()

    >>> utils.clear_function_caches()
    >>> s = Script("cmdline.Script --hst")
    >>> s.obs_pkg.__name__
    'crds.hst'
    >>> s.observatory
    'hst'

    >>> utils.clear_function_caches()
    >>> s = Script("cmdline.Script --jwst")
    >>> s.obs_pkg.__name__
    'crds.jwst'
    >>> s.observatory
    'jwst'

    >>> _ = os.environ.pop("CRDS_SERVER_URL", None)

    >>> _ = config.OBSERVATORY.set("hst")
    >>> utils.clear_function_caches()
    >>> Script("cmdline.Script").observatory
    'hst'

    >>> test_config.cleanup(old_state)
    """

def dt_print_help():
    """
    >>> old_state = test_config.setup()

    >> Script("cmdline.Script").print_help()

    >>> test_config.cleanup(old_state)
    """

def dt_require_server_connnection():
    """
    >>> old_state = test_config.setup()
    >>> Script("cmdline.Script").require_server_connection()
    >>> test_config.cleanup(old_state)
    """

def dt_no_files_in_class():
    """
    >>> old_state = test_config.setup()
    >>> Script("cmdline.Script").files
    Traceback (most recent call last):
    ...
    NotImplementedError: Class must implement list of `self.args.files` raw file paths.
    >>> test_config.cleanup(old_state)
   """

def dt_get_files():
    """
    >>> old_state = test_config.setup()

    >>> s = Script("cmdline.Script")
    >>> s.get_files(["data/file_list1"])
    ['data/file_list1']

    >>> s.get_files(["@data/file_list1"])
    ['hst.pmap', 'hst_0002.pmap', 'hst_0001.pmap']

    >>> test_config.cleanup(old_state)
    """

def dt_resolve_context():
    """
    >>> old_state = test_config.setup()

    >>> s = Script("cmdline.Script --hst")
    >>> s.resolve_context("hst-2016-01-01")
    CRDS - INFO -  Symbolic context 'hst-2016-01-01' resolves to 'hst_0379.pmap'
    'hst_0379.pmap'

    >>> test_config.cleanup(old_state)
    """


def dt_get_file_properties():
    """
    >>> old_state = test_config.setup()

    >>> s = Script("cmdline.Script")

    >>> s.get_file_properties("hst_acs_biasfile_0005.rmap")
    ('acs', 'biasfile')
    >>> s.get_file_properties("hst_acs_biasfile_0005.fits")
    ('acs', 'biasfile')

    >>> s = Script("crds.Script --jwst")
    >>> s.get_file_properties("data/valid.asdf")
    ('nirspec', 'wavecorr')

    >>> test_config.cleanup(old_state)
    """


def dt_categorize_files():
    """
    >>> old_state = test_config.setup()

    >>> s = Script("cmdline.Script")
    >>> cats = s.categorize_files(["hst.pmap", "data/hst_acs_9999.imap", "data/acs_new_idc.fits"])
    >>> sorted(cats.items())
    [(('', ''), ['hst.pmap']), (('acs', ''), ['data/hst_acs_9999.imap']), (('acs', 'idctab'), ['data/acs_new_idc.fits'])]

    >>> test_config.cleanup(old_state)
    """

def dt_dump_files():
    """
    >>> old_state = test_config.setup()

    >>> s = Script("cmdline.Script")
    >>> s.dump_files(files=["hst.pmap","hst_acs_biasfile_0250.rmap"])

    >>> test_config.cleanup(old_state)
    """

def dt_sync_files():
    """
    >>> old_state = test_config.setup()

    >>> s = Script("cmdline.Script")

    >>> test_config.cleanup(old_state)
    """

def dt_are_all_mappings():
    """
    >>> old_state = test_config.setup()

    >>> s = Script("cmdline.Script")

    >>> test_config.cleanup(old_state)
    """



class TestCmdline(test_config.CRDSTestCase):
    script_class = ListScript
    # server_url = "https://hst-crds-dev.stsci.edu"
    cache = test_config.CRDS_TESTING_CACHE

    # def test_console_profile(self):
    #     self.run_script("crds.list --status --profile=console",
    #                     expected_errs=None)

    # def test_file_profile(self):
    #     self.run_script("crds.list --status --profile=profile.stats",
    #                     expected_errs=None)
    #     os.remove("profile.stats")

    def test_file_outside_cache_pathless(self):
        s = Script("cmdline.Script")
        path = s.locate_file_outside_cache("hst_0001.pmap")
        assert path.endswith('./hst_0001.pmap'), path

    def test_file_outside_cache_uri(self):
        """Explicit crds:// notation for files inside cache."""
        s = Script("cmdline.Script --jwst")
        path = s.locate_file_outside_cache("crds://jwst_0001.pmap")
        assert path.endswith("crds-cache-test/mappings/jwst/jwst_0001.pmap"), path

    def test_file_outside_cache_mapping_spec(self):
        s = Script("cmdline.Script --hst")
        path = s.locate_file_outside_cache("hst-2016-01-01")
        assert path.endswith("crds-cache-test/mappings/hst/hst_0379.pmap"), path

    def test_resolve_context_operational(self):
        s = Script("cmdline.Script --hst")
        context = s.resolve_context("hst-operational")
        assert context.startswith("hst_") and context.endswith(".pmap"), context

    def test_dump_mappings(self):
        s = Script("cmdline.Script --ignore-cache")
        s.dump_mappings(["hst_acs.imap"])

class TestContextsScript(test_config.CRDSTestCase):
    script_class = ContextsScript
    # server_url = "https://hst-crds-dev.stsci.edu"
    cache = test_config.CRDS_TESTING_CACHE

    def test_determine_contexts_all(self):
        s = ContextsScript("cmdline.ContextsScript --all")
        contexts = s.determine_contexts()
        assert len(contexts) > 100, contexts

    def test_determine_contexts_last_n(self):
        s = ContextsScript("cmdline.ContextsScript --last 5")
        contexts = s.determine_contexts()
        assert len(contexts) == 5, contexts

    def test_determine_contexts_range(self):
        s = ContextsScript("cmdline.ContextsScript --range 1:7")
        contexts = s.determine_contexts()
        assert len(contexts) == 7, contexts

    def test_determine_contexts_upto(self):
        s = ContextsScript("cmdline.ContextsScript --up-to-context hst-2016-01-01")
        contexts = s.determine_contexts()
        assert len(contexts) == 195, log.format(len(contexts), contexts)
        assert contexts[0] == "hst.pmap", log.format(len(contexts), contexts)

    def test_determine_contexts_after(self):
        s = ContextsScript("cmdline.ContextsScript --after-context hst-2016-01-01")
        contexts = s.determine_contexts()
        assert len(contexts) >= 108, log.format(len(contexts), contexts)
        assert contexts[0] == "hst_0379.pmap", log.format(len(contexts), contexts)

    def test_determine_contexts_direct(self):
        s = ContextsScript("cmdline.ContextsScript --contexts hst.pmap")
        s.contexts = contexts = s.determine_contexts()
        assert len(contexts) == 1, log.format(len(contexts), contexts)
        assert contexts[0] == "hst.pmap", log.format(len(contexts), contexts)
        mappings = sorted(list(set(s.get_context_mappings())))
        assert len(mappings) == 116, log.format(len(mappings), mappings)

def main():
    """Run module tests,  for now just doctests only.

    test_config.setup() and cleanup() are done inline above because bracketing
    the tests here does not get picked up by nose test discovery.  Combining
    tests into one giant docstring works but is hard to analyze and debug when
    things go wrong.
    """
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCmdline)
    unittest.TextTestRunner().run(suite)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestContextsScript)
    unittest.TextTestRunner().run(suite)

    if sys.version_info >= (3,0,0):
        from crds.tests import tstmod, test_cmdline
        return tstmod(test_cmdline)

if __name__ == "__main__":
    print(main())
