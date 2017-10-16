"""
Tests for crds.core.crds_cache_locking which is nominally used to synchronize
access to the CRDS cache but is actually general purpose locking integrated
with
"""

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

# ===================================================================

import random
import time
import multiprocessing
import logging

# ===================================================================

from crds.core import log, config, crds_cache_locking

# ===================================================================

from . import test_config

# ===================================================================

def multiprocessing_instance(nothing):
    """Pretend to do something generic."""
    with crds_cache_locking.get_cache_lock():
        log.info("Doing something.")
        time.sleep(random.random()*1)

def try_multiprocessing():
    """Run some test functions using multiprocessing."""
    pool = multiprocessing.Pool(5)
    pool.map(multiprocessing_instance, [None]*5)
    pool.close()

def dt_default_locking():
    """
    Default locking configuration, enabled.

    >>> old_state = test_config.setup()
    >>> crds_cache_locking.init_locks()
    >>> _ = log.set_verbose()
    >>> crds_cache_locking.status()
    'enabled, multiprocessing'
    >>> try_multiprocessing()
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
    >>> try_multiprocessing()
    >>> test_config.cleanup(old_state)
    """

def dt_default_disabled():
    """
    Default locking configuration, enabled.

    >>> old_state = test_config.setup()
    >>> _ = config.USE_LOCKING.set(False)
    >>> crds_cache_locking.init_locks()
    CRDS - WARNING -  CRDS_USE_LOCKING = False. Cannot support downloading files while multiprocessing.
    CRDS - WARNING -  CRDS_USE_LOCKING = False. Cannot support downloading files while multiprocessing.
    >>> crds_cache_locking.status()
    'disabled, multiprocessing'
    >>> test_config.cleanup(old_state)
    """

def dt_default_readonly():
    """
    Default locking configuration, enabled.

    >>> old_state = test_config.setup()
    >>> _ = config.set_cache_readonly()
    >>> crds_cache_locking.init_locks()
    CRDS - WARNING -  CRDS_READONLY_CACHE = True. Cannot support downloading files while multiprocessing.
    CRDS - WARNING -  CRDS_READONLY_CACHE = True. Cannot support downloading files while multiprocessing.
    >>> crds_cache_locking.status()
    'disabled, multiprocessing'
    >>> test_config.cleanup(old_state)
    """

# ==================================================================================

def main():
    """Run module tests,  for now just doctests only."""
    from crds.tests import test_locking, tstmod
    return tstmod(test_locking)

if __name__ == "__main__":
    print(main())

