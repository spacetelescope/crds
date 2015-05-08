import os, tempfile, shutil

import crds
from crds import log, utils, client, config, tests

HERE = os.path.dirname(os.path.abspath(__file__))

def setup(cache=tests.CRDS_SOURCE_CACHE, url=tests.CRDS_FORWARDED_URL, download_mode="rpc"):
    old_state = config.get_crds_state(clear_existing=True)
    client.set_crds_server(url)
    os.environ["CRDS_SERVER_URL"] = url
    log.set_test_mode()
    old_state["OLD_CWD"] = os.getcwd()
    os.chdir(HERE)
    os.environ["CRDS_PATH"] = cache
    os.environ["CRDS_DOWNLOAD_MODE"] = download_mode
    utils.clear_function_caches()
    return old_state

def cleanup(old_state):
    """Strictly speaking test cleanup is more than restoring CRDS state."""
    os.chdir(old_state.pop("OLD_CWD"))
    config.set_crds_state(old_state)
    utils.clear_function_caches()
    
    
