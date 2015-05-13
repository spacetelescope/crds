from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import os, tempfile, shutil

import crds
from crds import log, utils, client, config, tests

HERE = os.path.dirname(os.path.abspath(__file__))

def setup(cache=tests.CRDS_SHARED_GROUP_CACHE, url=None):
    log.set_test_mode()

    old_state = config.get_crds_state(clear_existing=True)

    old_state["OLD_CWD"] = os.getcwd()
    os.chdir(HERE)

    if url is not None:
        os.environ["CRDS_SERVER_URL"] = url
    else:
        os.environ["CRDS_SERVER_URL"] = client.get_crds_server() 
    client.set_crds_server(os.environ["CRDS_SERVER_URL"])

    if cache is not None:
        os.environ["CRDS_PATH"] = cache
    elif hasattr(old_state, "CRDS_PATH"):
        os.environ["CRDS_PATH"] = old_state["CRDS_PATH"]
    utils.clear_function_caches()
    return old_state

def cleanup(old_state):
    """Strictly speaking test cleanup is more than restoring CRDS state."""
    os.chdir(old_state.pop("OLD_CWD"))
    config.set_crds_state(old_state)
    url = os.environ.get("CRDS_SERVER_URL", None)
    if url is not None:
        client.set_crds_server(url)
    utils.clear_function_caches()
