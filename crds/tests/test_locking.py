"""
Tests for crds.core.crds_cache_locking which is nominally used to synchronize
access to the CRDS cache but is actually general purpose locking integrated
with
"""
import sys
import os
import time
import multiprocessing
import tempfile
import doctest

# ===================================================================

from crds.core import log, config, crds_cache_locking

# ===================================================================

from . import test_config

# ===================================================================

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

def dt_default_locking():
    """
    Default locking configuration, enabled.

    >>> old_state = test_config.setup()
    >>> crds_cache_locking.init_locks()
    >>> _ = log.set_verbose()
    >>> crds_cache_locking.status()
    'enabled, multiprocessing'
    >>> try_multiprocessing()
    testing
    testing
    testing
    testing
    testing
    <BLANKLINE>
    >>> test_config.cleanup(old_state)
    """

def dt_multiprocessing_locking():
    """
    Default locking configuration, enabled.

    >>> old_state = test_config.setup()
    >>> _ = config.LOCKING_MODE.set("multiprocessing")
    >>> crds_cache_locking.init_locks()
    >>> _ = log.set_verbose()
    >>> crds_cache_locking.status()
    'enabled, multiprocessing'
    >>> try_multiprocessing()
    testing
    testing
    testing
    testing
    testing
    <BLANKLINE>
    >>> test_config.cleanup(old_state)
    """

def dt_filelock_locking():
    """
    Default locking configuration, enabled.

    >>> old_state = test_config.setup()
    >>> _ = config.LOCKING_MODE.set("filelock")
    >>> crds_cache_locking.init_locks()
    >>> _ = log.set_verbose()
    >>> crds_cache_locking.status()
    'enabled, filelock'
    >>> crds_cache_locking.get_cache_lock()
    CrdsFileLock('/tmp/crds.cache')
    >>> try_multiprocessing()
    testing
    testing
    testing
    testing
    testing
    <BLANKLINE>
    >>> test_config.cleanup(old_state)
    """

def dt_lockfile_locking():
    """
    Default locking configuration, enabled.

    >>> old_state = test_config.setup()
    >>> _ = config.LOCKING_MODE.set("lockfile")
    >>> crds_cache_locking.init_locks()
    >>> _ = log.set_verbose()
    >>> crds_cache_locking.status()
    'enabled, lockfile'
    >>> crds_cache_locking.get_cache_lock()
    CrdsLockFile('/tmp/crds.cache')

    >> try_multiprocessing()    XXXXX lockfile is broken
    testing
    testing
    testing
    testing
    testing
    <BLANKLINE>

    >>> test_config.cleanup(old_state)
    """

def dt_default_disabled():
    """
    Default locking configuration, disabled.   All bets are off
    for unlocked program output behavior...  just make sure it
    doesn't crash.

    >>> old_state = test_config.setup()
    >>> _ = config.USE_LOCKING.set(False)
    >>> _ = log.set_verbose()
    >>> crds_cache_locking.init_locks()
    CRDS - DEBUG -  CRDS_USE_LOCKING = False. Cannot support downloading CRDS files while multiprocessing.
    >>> crds_cache_locking.status()
    'disabled, multiprocessing'
    >>> doctest.ELLIPSIS_MARKER = '-ignore-'
    >>> try_multiprocessing() # doctest: +ELLIPSIS
    -ignore-
    >>> doctest.ELLIPSIS_MARKER = '...'
    >>> test_config.cleanup(old_state)
    """

def dt_default_readonly():
    """
    Default locking configuration, readonly cache, locking disabled.

    >>> old_state = test_config.setup()
    >>> _ = config.set_cache_readonly()
    >>> _ = log.set_verbose()
    >>> crds_cache_locking.init_locks()
    >>> crds_cache_locking.status()
    'disabled, multiprocessing'
    >>> doctest.ELLIPSIS_MARKER = '-ignore-'
    >>> try_multiprocessing() # doctest: +ELLIPSIS
    -ignore-
    >>> doctest.ELLIPSIS_MARKER = '...'
    >>> test_config.cleanup(old_state)
    """

# ==================================================================================

def main():
    """Run module tests,  for now just doctests only."""
    from crds.tests import test_locking, tstmod
    return tstmod(test_locking)

if __name__ == "__main__":
    print(main())
