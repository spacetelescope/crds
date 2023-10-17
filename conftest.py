import json
from pathlib import Path
from pytest import fixture
import os, os.path
from pytest import TempPathFactory
import cProfile
import pstats
import mock
import yaml

# ==============================================================================

import crds
from crds.core import log, utils
from crds.core import config as crds_config

# ==============================================================================
HERE = os.path.abspath(os.path.dirname(__file__) or ".")
CRDS_DIR = os.path.abspath(os.path.dirname(crds.__file__))
RETENTION_COUNT=1
RETENTION_POLICY='none'

def pytest_addoption(parser):
    parser.addoption(
        "--test_data",
        action="store",
        dest="test_data",
        default=os.path.abspath("test/data"),
        help="Default pytest data path",
    )
    parser.addoption(
        "--test_cache",
        action="store",
        dest="test_cache",
        default=os.environ.get("CRDS_TESTING_CACHE", "no-test-cache-defined-see-TESTING"),
        help="Default CRDS Test Cache",
    )


@fixture(scope='session')
def test_data(request):
    return request.config.getoption("test_data")


@fixture(scope='session')
def test_cache(request):
    return request.config.getoption("test_cache")


@fixture(scope='session')
def test_mappath(test_cache):
    return os.path.join(test_cache, "mappings")


@fixture(scope='session')
def crds_forwarded_url():
    return "https://localhost:8001/"


@fixture(scope='function')
def crds_shared_group_cache():
    return crds_config.get_crds_path()


@fixture(scope='session')
def test_temp_dir(request):
    try:
        tmp_path_factory = TempPathFactory(
            request.config.option.basetemp, 
            RETENTION_COUNT, 
            RETENTION_POLICY,
            trace=request.config.trace.get("tmpdir"),
            _ispytest=True
        )
    except Exception: # pytest < 7.3
        tmp_path_factory = TempPathFactory(
            request.config.option.basetemp, trace=request.config.trace.get("tmpdir"), _ispytest=True
        )
    basepath = tmp_path_factory.getbasetemp()
    return basepath


@fixture(scope='function')
def hst_data(test_data):
    return f"{test_data}/hst"


@fixture(scope='function')
def jwst_data(test_data):
    return f"{test_data}/jwst"


@fixture(scope='function')
def roman_data(test_data):
    return f"{test_data}/roman"


# ==============================================================================


@fixture(scope='function')
def tmp_rc(test_temp_dir):
    _tmprc = os.path.join(test_temp_dir, 'tmp_rc_submit_')
    os.makedirs(_tmprc, exist_ok=True)
    return _tmprc


@fixture(scope='function')
def submit_test_files(tmp_rc):
    # Create empty test files in the temporary directory:
    filenames = ['ipppssoot_ccd.fits', 'opppssoot_bia.fits']
    tempfiles = [os.path.join(tmp_rc, x) for x in filenames]
    for fpath in tempfiles:
        with open(fpath, 'a'):
            os.utime(fpath, None)
    return tempfiles


@fixture(scope='function')
def mock_submit_form(tmp_rc, test_data):
    # Create a file handle to use as a mockup of the urllib.request object:
    mockup_form = os.path.join(tmp_rc, 'mocked_redcat_description.yml')
    with open(os.path.join(test_data, "rc_description.yaml")) as yml:
        form_description_yml = yaml.safe_load(yml)
    with open(mockup_form, 'w') as f:
        yaml.dump(form_description_yml)
    return mockup_form



# ==============================================================================

class ConfigState:

    def __init__(self, cache=None, url=None, clear_existing=True, observatory=None, mode=None):
        self.cache = cache
        self.url = url
        self.clear_existing = clear_existing
        self.observatory = observatory
        self.mode = mode
        self.old_state = None
        self.new_state = None

    def config_setup(self):
        """Reset the CRDS configuration state to support testing given the supplied parameters."""
        # cache=crds_shared_group_cache, url=None, observatory=None, clear_existing=False
        log.set_test_mode()
        self.old_state = crds_config.get_crds_state()
        self.old_state["CRDS_CWD"] = os.getcwd()
        if self.clear_existing:
            crds_config.clear_crds_state()
        self.new_state = dict(self.old_state)
        self.new_state["CRDS_CWD"] = HERE
        if self.url is not None:
            self.new_state["CRDS_SERVER_URL"] = self.url
        if self.cache is not None:
            self.new_state["CRDS_PATH"] = self.cache
        if self.observatory is not None:
            self.new_state["CRDS_OBSERVATORY"] = self.observatory
        if self.mode is not None:
            self.new_state['CRDS_MODE'] = self.mode
        crds_config.set_crds_state(self.new_state)
        utils.clear_function_caches()

    def cleanup(self):
        """Strictly speaking test cleanup is more than restoring CRDS state."""
        crds_config.set_crds_state(self.old_state)
        utils.clear_function_caches()


@fixture(scope='function')
def default_shared_state(crds_shared_group_cache):
    cfg = ConfigState(cache=crds_shared_group_cache)
    cfg.config_setup()
    yield cfg
    cfg.cleanup()


@fixture(scope='function')
def hst_shared_cache_state(crds_shared_group_cache):
    cfg = ConfigState(cache=crds_shared_group_cache, url="https://hst-crds.stsci.edu", observatory="hst")
    cfg.config_setup()
    yield cfg
    cfg.cleanup()


@fixture()
def hst_temp_cache_state(test_temp_dir):
    cfg = ConfigState(
        cache=str(test_temp_dir),
        url="https://hst-crds.stsci.edu",
        observatory="hst",
    )
    cfg.config_setup()
    yield cfg
    cfg.cleanup()


@fixture(scope='function')
def jwst_no_cache_state():
    #os.environ["CRDS_MAPPATH_SINGLE"] = test_data
    cfg = ConfigState(
        cache=None,
        url="https://jwst-crds.stsci.edu",
        observatory="jwst",
        mode='local')
    cfg.config_setup()
    yield cfg
    cfg.cleanup()


@fixture(scope='function')
def jwst_shared_cache_state(crds_shared_group_cache):
    cfg = ConfigState(
        cache=crds_shared_group_cache,
        url="https://jwst-crds.stsci.edu",
        observatory="jwst")
    cfg.config_setup()
    yield cfg
    cfg.cleanup()


@fixture(scope='function')
def jwst_serverless_state(crds_shared_group_cache):
    cfg = ConfigState(
        cache=crds_shared_group_cache,
        url="https://jwst-crds-serverless.stsci.edu",
        observatory="jwst"
    )
    cfg.config_setup()
    yield cfg
    cfg.cleanup()


@fixture(scope='function')
def hst_serverless_state(crds_shared_group_cache):
    cfg = ConfigState(
        cache=crds_shared_group_cache,
        url="https://hst-serverless-mode.stsci.edu",
        observatory="hst"
    )
    cfg.config_setup()
    yield cfg
    cfg.cleanup()

@fixture()
def hst_persistent_state(test_cache):
    cfg = ConfigState(
        cache=test_cache,
        clear_existing=False,
        observatory="hst",
    )
    cfg.config_setup()
    yield cfg
    cfg.cleanup()


@fixture(scope='function')
def roman_serverless_state(crds_shared_group_cache):
    cfg = ConfigState(
        cache=crds_shared_group_cache,
        url="https://roman-crds-serverless.stsci.edu",
        observatory="roman"
    )
    cfg.config_setup()
    yield cfg
    cfg.cleanup()


@fixture(scope='function')
def broken_state():
    cfg = ConfigState(cache="/nowhere", url="https://server-is-out-of-town")
    cfg.config_setup()
    yield cfg
    cfg.cleanup()


@fixture(scope='function')
def default_test_cache_state(test_cache):
    cfg = ConfigState(cache=test_cache)
    cfg.config_setup()
    yield cfg
    cfg.cleanup()


@fixture(scope='function')
def jwst_test_cache_state(test_cache):
    cfg = ConfigState(cache=test_cache, observatory="jwst")
    cfg.config_setup()
    yield cfg
    cfg.cleanup()


@fixture(scope='function')
def roman_test_cache_state(test_cache):
    cfg = ConfigState(cache=test_cache, url="https://roman-serverless-mode.stsci.edu", observatory="roman")
    cfg.config_setup()
    yield cfg
    cfg.cleanup()


@fixture(scope='function')
def tobs_test_cache_state(test_cache):
    cfg = ConfigState(cache=test_cache, url="https://tobs-serverless-mode.stsci.edu", clear_existing=False)
    cfg.config_setup()
    yield cfg
    cfg.cleanup()

 

# ==============================================================================

def run_and_profile(name, case, globs={}, locs={}):
    """Using `name` for a banner and divider,  execute code string `case` in the
    global namespace,  both evaled printing result and under the profiler.
    """
    utils.clear_function_caches()
    log.divider()
    log.divider(name + " example")
    log.divider()
    print(eval(case, globs, locs))
    utils.clear_function_caches()
    log.divider()
    log.divider(name + " profile")
    log.divider()
    cProfile.run(case, "profile.stats")
    stats = pstats.Stats('profile.stats')
    stats.strip_dirs()
    stats.sort_stats('cumulative')
    stats.print_stats(100)
    os.remove('profile.stats')


@fixture
def combined_spec(scope='session'):
    return json.load(
        open(Path(__file__).parent.parent / "crds" / "roman" / "specs" / "combined_specs.json", 'r'))
