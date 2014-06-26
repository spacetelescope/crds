import os, tempfile, shutil

# must set env before crds import,  even package __init___
os.environ["CRDS_PATH"] = os.path.join(tempfile.mkdtemp(), "test_cache")
os.environ["CRDS_SERVER_URL"] = "https://hst-crds.stsci.edu"

from crds import log

def setup():
    # log.set_verbose()
    # os.environ["CRDS_PATH"] = os.path.join(os.getcwd(), "test_cache")
    log.set_test_mode()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

def cleanup():
    try:
        shutil.rmtree(os.environ["CRDS_PATH"])
    except:
        pass
    try:
        del os.environ["CRDS_PATH"]
        del os.environ["CRDS_SERVER_URL"]
    except:
        pass
