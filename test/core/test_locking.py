from crds.core import log, config, crds_cache_locking
import logging
import time
import multiprocessing
import tempfile
from pytest import mark
log.THE_LOGGER.logger.propagate = True
log.set_verbose(10)


# Copied from tests/test_locking
def multiprocessing_instance(output_file_name):
    """Pretend to do something generic."""
    output_file = open(output_file_name, "a")
    with crds_cache_locking.get_cache_lock():
        for char in "testing":
            output_file.write(char)
            output_file.flush()
            time.sleep(0.2)
        output_file.write("\n")
        output_file.flush()


# Copied from tests/test_locking
def try_multiprocessing():
    """Run some test functions using multiprocessing."""
    # Starting with Python 3.8, the default start method in macOS is
    # "spawn", which causes the CRDS lock to be recreated for each
    # process.
    context = multiprocessing.get_context("fork")
    pool = context.Pool(5)
    with tempfile.NamedTemporaryFile(mode="a") as output_file:
        pool.map(multiprocessing_instance, [output_file.name]*5)
        pool.close()
        reader = open(output_file.name)
        print(reader.read())


@mark.multimission
@mark.locking
def test_default_locking(default_shared_state, capsys):
    crds_cache_locking.init_locks()
    status = crds_cache_locking.status()
    try_multiprocessing()
    out, _ = capsys.readouterr()
    out_to_check = """testing
testing
testing
testing
testing

"""
    assert out_to_check in out
    assert status == "enabled, multiprocessing"
    

@mark.multimission
@mark.locking
def test_multiprocessing_locking(default_shared_state, capsys):
    config.LOCKING_MODE.set("multiprocessing")
    crds_cache_locking.init_locks()
    status = crds_cache_locking.status()
    try_multiprocessing()
    out, _ = capsys.readouterr()
    out_to_check = """testing
testing
testing
testing
testing

"""
    assert out_to_check in out
    assert status == "enabled, multiprocessing"
    

@mark.multimission
@mark.locking
def test_filelock_locking(default_shared_state, capsys):
    config.LOCKING_MODE.set("filelock")
    crds_cache_locking.init_locks()
    status = crds_cache_locking.status()
    cache = crds_cache_locking.get_cache_lock()
    try_multiprocessing()
    out, _ = capsys.readouterr()
    out_to_check = """testing
testing
testing
testing
testing

"""
    assert out_to_check in out
    assert status == "enabled, filelock"
    assert cache == crds_cache_locking.get_lock("crds.cache")
    

@mark.multimission
@mark.locking
def test_default_disabled(default_shared_state, capsys, caplog):
    config.USE_LOCKING.set(False)
    log.set_verbose()
    crds_cache_locking.init_locks()
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        out = caplog.text
    status = crds_cache_locking.status()
    try_multiprocessing()
    # Including capsys in test even though not used since otherwise "ttttteeeeessssstttttiiiiinnnnnggggg"
    # gets printed to console from try_multiprocessing().
    _, _ = capsys.readouterr()
    out_to_check = "CRDS_USE_LOCKING = False. Cannot support downloading CRDS files while multiprocessing."
    assert status == "disabled, multiprocessing"
    assert out_to_check in out
    

@mark.multimission
@mark.locking
def test_default_readonly(default_shared_state, capsys):
    config.set_cache_readonly()
    log.set_verbose()
    crds_cache_locking.init_locks()
    status = crds_cache_locking.status()
    try_multiprocessing()
    # Same reason to include capsys as in default_disabled()
    _, _ = capsys.readouterr()
    assert status == "disabled, multiprocessing"
    





