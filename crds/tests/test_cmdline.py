from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os
import doctest

from crds import log, tests, cmdline, utils
from crds.cmdline import Script, ContextsScript, UniqueErrorsMixin
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

    >>> os.environ["CRDS_OBSERVATORY"] = "hst"
    >>> utils.clear_function_caches()
    >>> Script("cmdline.Script").observatory
    'hst'
    
    >>> test_config.cleanup(old_state)
    """

def dt_print_help():
    """
    >>> old_state = test_config.setup()

    >> Script().print_help()

    >>> test_config.cleanup(old_state)
    """

def dt_require_server_connnection():
    """
    >>> old_state = test_config.setup()
    >>> Script().require_server_connection()
    >>> test_config.cleanup(old_state)
    """

def dt_no_files_in_class():
    """
    >>> old_state = test_config.setup()
    >>> Script().files
    Traceback (most recent call last):
    ...
    NotImplementedError: Class must implement list of `self.args.files` raw file paths.
    >>> test_config.cleanup(old_state) 
   """

def dt_get_files():
    """
    >>> old_state = test_config.setup()

    >>> s = Script()
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

    >>> s = Script()

    >>> s.get_file_properties("hst_acs_biasfile_0005.rmap") 
    ('acs', 'biasfile')
    >>> s.get_file_properties("hst_acs_biasfile_0005.fits")
    ('acs', 'biasfile')

    >>> s = Script("crds.Script --jwst")
    >>> s.get_file_properties("data/valid.asdf")
    ('miri', 'distortion')
   
    >>> test_config.cleanup(old_state)
    """


def dt_categorize_files():
    """
    >>> old_state = test_config.setup()

    >>> s = Script()
    >>> cats = s.categorize_files(["hst.pmap", "data/hst_acs_9999.imap", "data/acs_new_idc.fits"])
    >>> sorted(cats.items())
    [(('', ''), ['hst.pmap']), (('acs', ''), ['data/hst_acs_9999.imap']), (('acs', 'idctab'), ['data/acs_new_idc.fits'])]

    >>> test_config.cleanup(old_state)
    """

def dt_dump_files():
    """
    >>> old_state = test_config.setup()

    >>> s = Script()
    >>> s.dump_files(files=["hst.pmap","hst_acs_biasfile_0250.rmap"])

    >>> test_config.cleanup(old_state)
    """

def dt_dump_mappings():
    """
    >>> old_state = test_config.setup()

    >>> os.environ.pop("CRDS_SERVER_URL", None)
    >>> utils.clear_function_caches()
    >>> s = Script("cmdline.Script --ignore-cache")
    >>> s.dump_mappings(["hst_acs.imap"])
    CRDS - INFO -  Fetching  /Users/jmiller/crds_cache_ops/mappings/hst/hst_acs_spottab.rmap      666 bytes  (1 / 22 files) (0 / 498.6 K bytes)
    CRDS - INFO -  Fetching  /Users/jmiller/crds_cache_ops/mappings/hst/hst_acs_shadfile.rmap      785 bytes  (2 / 22 files) (666 / 498.6 K bytes)
    CRDS - INFO -  Fetching  /Users/jmiller/crds_cache_ops/mappings/hst/hst_acs_pfltfile.rmap   69.2 K bytes  (3 / 22 files) (1.5 K / 498.6 K bytes)
    CRDS - INFO -  Fetching  /Users/jmiller/crds_cache_ops/mappings/hst/hst_acs_pctetab.rmap      640 bytes  (4 / 22 files) (70.7 K / 498.6 K bytes)
    CRDS - INFO -  Fetching  /Users/jmiller/crds_cache_ops/mappings/hst/hst_acs_oscntab.rmap      846 bytes  (5 / 22 files) (71.3 K / 498.6 K bytes)
    CRDS - INFO -  Fetching  /Users/jmiller/crds_cache_ops/mappings/hst/hst_acs_npolfile.rmap    3.1 K bytes  (6 / 22 files) (72.1 K / 498.6 K bytes)
    CRDS - INFO -  Fetching  /Users/jmiller/crds_cache_ops/mappings/hst/hst_acs_mlintab.rmap      641 bytes  (7 / 22 files) (75.2 K / 498.6 K bytes)
    CRDS - INFO -  Fetching  /Users/jmiller/crds_cache_ops/mappings/hst/hst_acs_mdriztab.rmap      793 bytes  (8 / 22 files) (75.9 K / 498.6 K bytes)
    CRDS - INFO -  Fetching  /Users/jmiller/crds_cache_ops/mappings/hst/hst_acs_imphttab.rmap      793 bytes  (9 / 22 files) (76.7 K / 498.6 K bytes)
    CRDS - INFO -  Fetching  /Users/jmiller/crds_cache_ops/mappings/hst/hst_acs_idctab.rmap    1.7 K bytes  (10 / 22 files) (77.4 K / 498.6 K bytes)
    CRDS - INFO -  Fetching  /Users/jmiller/crds_cache_ops/mappings/hst/hst_acs_flshfile.rmap    3.1 K bytes  (11 / 22 files) (79.2 K / 498.6 K bytes)
    CRDS - INFO -  Fetching  /Users/jmiller/crds_cache_ops/mappings/hst/hst_acs_drkcfile.rmap  100.6 K bytes  (12 / 22 files) (82.3 K / 498.6 K bytes)
    CRDS - INFO -  Fetching  /Users/jmiller/crds_cache_ops/mappings/hst/hst_acs_dgeofile.rmap    3.2 K bytes  (13 / 22 files) (183.0 K / 498.6 K bytes)
    CRDS - INFO -  Fetching  /Users/jmiller/crds_cache_ops/mappings/hst/hst_acs_darkfile.rmap  178.6 K bytes  (14 / 22 files) (186.2 K / 498.6 K bytes)
    CRDS - INFO -  Fetching  /Users/jmiller/crds_cache_ops/mappings/hst/hst_acs_d2imfile.rmap      625 bytes  (15 / 22 files) (364.8 K / 498.6 K bytes)
    CRDS - INFO -  Fetching  /Users/jmiller/crds_cache_ops/mappings/hst/hst_acs_crrejtab.rmap      920 bytes  (16 / 22 files) (365.4 K / 498.6 K bytes)
    CRDS - INFO -  Fetching  /Users/jmiller/crds_cache_ops/mappings/hst/hst_acs_cfltfile.rmap    1.2 K bytes  (17 / 22 files) (366.3 K / 498.6 K bytes)
    CRDS - INFO -  Fetching  /Users/jmiller/crds_cache_ops/mappings/hst/hst_acs_ccdtab.rmap    1.4 K bytes  (18 / 22 files) (367.5 K / 498.6 K bytes)
    CRDS - INFO -  Fetching  /Users/jmiller/crds_cache_ops/mappings/hst/hst_acs_bpixtab.rmap    1.5 K bytes  (19 / 22 files) (369.0 K / 498.6 K bytes)
    CRDS - INFO -  Fetching  /Users/jmiller/crds_cache_ops/mappings/hst/hst_acs_biasfile.rmap  126.1 K bytes  (20 / 22 files) (370.5 K / 498.6 K bytes)
    CRDS - INFO -  Fetching  /Users/jmiller/crds_cache_ops/mappings/hst/hst_acs_atodtab.rmap      888 bytes  (21 / 22 files) (496.6 K / 498.6 K bytes)
    CRDS - INFO -  Fetching  /Users/jmiller/crds_cache_ops/mappings/hst/hst_acs.imap    1.2 K bytes  (22 / 22 files) (497.5 K / 498.6 K bytes)

    >>> test_config.cleanup(old_state)
    """

def dt_sync_files():
    """
    >>> old_state = test_config.setup()

    >>> s = Script()

    >>> test_config.cleanup(old_state)
    """

def dt_are_all_mappings():
    """
    >>> old_state = test_config.setup()

    >>> s = Script()

    >>> test_config.cleanup(old_state)
    """



class TestCmdline(test_config.CRDSTestCase):    
    script_class = ListScript
    # server_url = "https://hst-crds-dev.stsci.edu"
    cache = test_config.CRDS_TESTING_CACHE

    def test_console_profile(self):
        self.run_script("crds.list --status --profile=console",
                        expected_errs=None)
        
    def test_file_profile(self):
        self.run_script("crds.list --status --profile=profile.stats",
                        expected_errs=None)
        os.remove("profile.stats")

    def test_file_outside_cache_pathless(self):
        s = Script()
        path = s.locate_file_outside_cache("hst_0001.pmap")
        assert path.endswith('crds/tests/hst_0001.pmap'), path

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

    def test_determine_contexts_after(self):
        s = ContextsScript("cmdline.ContextsScript --contexts hst.pmap")
        s.contexts = contexts = s.determine_contexts()
        assert len(contexts) == 1, log.format(len(contexts), contexts)
        assert contexts[0] == "hst.pmap", log.format(len(contexts), contexts)
        mappings = s.get_context_mappings()
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

    from crds.tests import tstmod, test_cmdline
    return tstmod(test_cmdline)

if __name__ == "__main__":
    print(main())
