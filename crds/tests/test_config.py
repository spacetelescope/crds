import os, tempfile, shutil

from crds import log, utils

def setup():
    # log.set_verbose()
    # os.environ["CRDS_PATH"] = os.path.join(os.getcwd(), "test_cache")
    # OLD_PATH = os.environ["CRDS_PATH"]
    # OLD_URL = os.environ["CRDS_SERVER_URL"]
    os.environ["CRDS_PATH"] = "/grp/crds/cache"
    os.environ["CRDS_SERVER_URL"] = "https://hst-crds-dev.stsci.edu"
    utils.clear_function_caches()
    log.set_test_mode()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

def cleanup():
    try:
        pass
        # shutil.rmtree(os.environ["CRDS_PATH"])
    except:
        pass
    try:
        del os.environ["CRDS_PATH"]
        del os.environ["CRDS_SERVER_URL"]
    except:
        pass
