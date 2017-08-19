"""This module defines locking primitives for the CRDS cache used to prevent
simultaneous writes.  This is principally motivated by the JWST association
logic which may attempt to prefetch files for multiple images at the same time.

This module is a thin wrapper around the "lockfile" package designed to handle
import failure for lockfile as well as the readonly mode of the CRDS cache.

-----------------------------------------------------------------------------

This test really just verifies that lockfile imports,  particularly under Travis:

>> from crds.tests import test_config
>> old_state = test_config.setup()

>> _ = log.set_verbose()
>> with get_cache_lock():
...     pass

>> test_config.cleanup(old_state)
"""

from __future__ import print_function, absolute_import

# =========================================================================

from . import log, config, utils

# =========================================================================

try:
    import lockfile
except ImportError:
    lockfile = None

# =========================================================================

class CrdsFakeLockFile(object):
        
    def __init__(self, lockpath):
        self._lockpath = lockpath

    def acquire(self, *args, **keys):
        pass
    
    def release(self, *args, **keys):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        pass

    def break_lock(self):
        pass
    
if lockfile is not None:

    class CrdsLockFile(lockfile.LockFile):
        """Wrap LockFile to add CRDS log messages for acquire/release."""
        
        def __init__(self, lockpath):
            self._lockpath = lockpath
            super(CrdsLockFile, self).__init__(self._lockpath)
        
        def acquire(self, *args, **keys):
            log.verbose("Acquiring lock", repr(self))
            result = super(CrdsLockFile, self).acquire(*args, **keys)
            log.verbose("Lock acquired", repr(self))
            return result
        
        def release(self, *args, **keys):
            log.verbose("Releasing lock", repr(self))
            result = super(CrdsLockFile, self).release(*args, **keys)
            log.verbose("Lock released", repr(self))
            return result

        def break_lock(self):
            log.verbose("Breaking lock", repr(self))
            result = super(CrdsLockFile, self).break_lock()
            log.verbose("Broke lock", repr(self))

else:

    CrdsLockFile = CrdsFakeLockFile
 
# =========================================================================

DEFAULT_LOCK_FILENAME = "crds.cache.lock"   # filename only

def get_cache_lock(lock_filename=DEFAULT_LOCK_FILENAME):
    """Return a file lock context manager to guard the CRDS cache against
    concurrent writes.
    """
    lockpath = config.get_crds_lockpath(lock_filename)
    
    if not config.USE_LOCKING.get():
        return _fake_lock_verbose(lockpath, "CRDS_USE_LOCKING = False.")

    if config.get_cache_readonly():
        return _fake_lock_verbose(lockpath, "CRDS_READONLY_CACHE = True.")

    if not utils.is_writable(lockpath):
        return _fake_lock_verbose(lockpath, "CACHE LOCK not writable.")
        
    if lockfile is None:
        return _fake_lock_verbose(lockpath, "Failed importing 'lockfile' package.")
        
    try:
        # XXXX lock dir creation turns into a locking issue,  use pre-existing path.
        # Either initialize cache using "crds sync --last 1" or set CRDS_CACHE_LOCK_PATH
        # utils.ensure_dir_exists(lockpath)
        return CrdsLockFile(lockpath)
    except Exception as exc:
        log.warning("Failed creating CRDS cache lock file:", str(exc))
        return _fake_lock_verbose(lockpath, "Failed creating CRDS cache lock")

def _fake_lock_verbose(lockpath, explain):
    log.verbose(explain + " Cannot support downloading files while multiprocessing.")
    return CrdsFakeLockFile(lockpath)
                    
    
# =========================================================================

def clear_cache_lock(lock_filename=DEFAULT_LOCK_FILENAME):
    """Make sure that `lock_filename` does not exist."""
    lockpath = config.get_crds_lockpath(lock_filename)
    utils.ensure_dir_exists(lockpath)
    lock = get_cache_lock(lockpath)
    lock.break_lock()

def clear_cache_locks():
    """Clear all CRDS cache file locks."""
    clear_cache_lock(DEFAULT_LOCK_FILENAME)   # XXXX needs to be expanded if non-default locks are used.

# =========================================================================

def _locking_enabled():
    """Return True IFF almalgum of all config settings enable locking."""
    lock = get_cache_lock()
    return not isinstance(lock, CrdsFakeLockFile)
            
def status():
    """Return configured/actual ability of CRDS to lock the cache."""
    return "enabled" if _locking_enabled() else "disabled"

# =========================================================================

def test():
    import doctest
    from crds.core import crds_cache_locking
    return doctest.testmod(crds_cache_locking)

if __name__ == "__main__":
    print(test())
