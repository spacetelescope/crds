import os, tempfile, shutil

from crds import log

def setup():
    # log.set_verbose()
    # os.environ["CRDS_PATH"] = os.path.join(os.getcwd(), "test_cache")
    os.environ["CRDS_PATH"] = os.path.join(tempfile.mkdtemp(), "test_cache")
    os.environ["CRDS_SERVER_URL"] = "https://hst-crds.stsci.edu"
    log.set_test_mode()

def cleanup():
    shutil.rmtree(os.environ["CRDS_PATH"])

