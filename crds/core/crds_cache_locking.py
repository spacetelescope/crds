"""This module defines locking primitives for the CRDS cache used to prevent
simultaneous writes.  This is principally motivated by the JWST association
logic which may attempt to prefetch files for multiple images at the same time.

CRDS locking wraps more primitive locking functionality such as that provided by
the lockfile package or the multiprocessing module.

A number of configuration env var settings control locking behavior:

CRDS_USE_LOCKING    boolean control setting turn locks on/off
CRDS_LOCK_PATH      directory path for lock files  (must pre-exist)
CRDS_LOCKING_MODE   (filelock, lockfile, or multiprocessing)
"""

from __future__ import print_function, absolute_import

# =========================================================================

import os
import multiprocessing

# =========================================================================

try:
    import lockfile
except ImportError:
    lockfile = None
    
try:
    import filelock
except ImportError:
    filelock = None

# =========================================================================

from . import log, config, utils

# =========================================================================

class CrdsAbstractLock(object):
    """At a design level this also serves as an abstract class defining the API."""
    
    _lock = None  # normally overridden as attribute by subclass

    def __init__(self, lockpath):
        self._lockpath = lockpath
        
    def __repr__(self):
        return self.__class__.__name__ + "('" + self._lockpath + "')"

    def acquire(self, *args, **keys):
        """Acquire delegate lock,  adding CRDS verbose logging."""
        log.verbose("Acquiring lock", repr(self))
        self._acquire(*args, **keys)
        log.verbose("Lock acquired", repr(self))
    
    def release(self, *args, **keys):
        """Release delegate lock,  adding CRDS verbose logging."""
        log.verbose("Releasing lock", repr(self))
        self._release(*args, **keys)
        log.verbose("Lock released", repr(self))

    def break_lock(self):
        """Break delegate lock,  adding CRDS verbose logging."""
        log.verbose("Breaking lock", repr(self))
        self._break_lock()
        log.verbose("Broke lock", repr(self))
    
    def __enter__(self, *args, **keys):
        """Support context manager protocol, with...:"""
        self.acquire(*args, **keys)
        return self

    def __exit__(self, *args, **keys):
        """Support context manager protocol, with...:"""
        self.release()

    # ----------------------------------------------------
        
    def _acquire(self, *args, **keys):
        """Delegates to self._lock's acquire,  override as needed."""
        self._lock.acquire(*args, **keys)
    
    def _release(self, *args, **keys):
        """Delegates to self._lock's release,  override as needed."""
        self._lock.release(*args, **keys)

    def _break_lock(self, *args, **keys):
        """Noop,  override as needed."""
        pass

# =========================================================================

# Always defined as fall back

class CrdsFakeLock(CrdsAbstractLock):
    """Placeholder dummy lock to do nothing."""

    def acquire(self, *args, **keys):
        """Silent dummy acquire."""
        pass
    
    def release(self, *args, **keys):
        """Silent dummy release."""
        pass
    
    def break_lock(self):
        """Silent dummy break."""
        pass
    
# =========================================================================

if config.LOCKING_MODE == "multiprocessing":

    class CrdsMultiprocessingLock(CrdsAbstractLock):
        """Wrap multiprocessing.Lock as locking basis."""
        
        def __init__(self, lockpath):
            self._lock = multiprocessing.Lock()
            super(CrdsMultiprocessingLock, self).__init__(lockpath)
        
    CrdsLock = CrdsMultiprocessingLock
    
elif config.LOCKING_MODE == "filelock":

    class CrdsFileLock(CrdsAbstractLock):
        """Wrap filelock.FileLock as locking basis."""
        
        def __init__(self, lockpath):
            if filelock is None:
                raise RuntimeError("Locking package 'filelock' is not installed.")
            self._lock = filelock.FileLock(lockpath)
            super(CrdsFileLock, self).__init__(lockpath)
            
        def _break_lock(self, *args, **keys):
            """Destroy lock regardless of who owns it."""
            try:
                os.remove(self._lockpath)
            except Exception:
                pass
        
    CrdsLock = CrdsFileLock

elif config.LOCKING_MODE == "lockfile":

    class CrdsLockFile(CrdsAbstractLock):
        """Wrap lockfile.LockFile as locking basis."""
        
        def __init__(self, lockpath):
            if filelock is None:
                raise RuntimeError("Locking package 'lockfile' is not installed.")
            self._lock = lockfile.LockFile(lockpath)
            super(CrdsLockFile, self).__init__(lockpath)
        
        def _break_lock(self,  *args, **keys):
            """Destroy lock regardless of who owns it."""
            self._lock.break_lock(*args, **keys)
            try:
                os.remove(self._lockpath)
            except Exception:
                pass
    
    CrdsLock = CrdsLockFile

else:

    CrdsLock = CrdsFakeLock
 
# =========================================================================

DEFAULT_LOCK_FILENAME = "crds.cache"   # filename only

LOCKS = {}   #  { lockpath : CrdsAbstractLockSubclass, ... }

def get_cache_lock(lockname=DEFAULT_LOCK_FILENAME):
    """Create, remember, and return the lock object globally referred to by string `lockname`."""
    if lockname in LOCKS:
        lock = LOCKS[lockname]
    else:
        lock = LOCKS[lockname] = create_cache_lock(lockname)
    return lock

def create_cache_lock(lockname=DEFAULT_LOCK_FILENAME):
    """Return a lock context manager to guard the CRDS cache against concurrent writes."""
    lockpath = config.get_crds_lockpath(lockname)
    if not config.USE_LOCKING.get():
        lock = _fake_lock_verbose(lockpath, "CRDS_USE_LOCKING = False.")
    elif config.get_cache_readonly():
        lock = _fake_lock_verbose(lockpath, "CRDS_READONLY_CACHE = True.")
    elif not utils.is_writable(lockpath):
        lock = _fake_lock_verbose(lockpath, "CACHE LOCK not writable.")
    else:
        try:
            lock = CrdsLock(lockpath)
        except Exception as exc:
            lock = _fake_lock_verbose(lockpath, "Failed creating CRDS cache lock: " + str(exc))
    return lock

def _fake_lock_verbose(lockpath, explain):
    """Issue a verbose log message based on `explain` indicating why fake 
    locks are being used.
    
    Returns a fake lock for `lockpath`.
    """
    log.verbose(explain + " Cannot support downloading files while multiprocessing.")
    return CrdsFakeLock(lockpath)
    
def clear_cache_lock(lock_filename=DEFAULT_LOCK_FILENAME):
    """Make sure that `lock_filename` does not exist."""
    lockpath = config.get_crds_lockpath(lock_filename)
    utils.ensure_dir_exists(lockpath)
    lock = get_cache_lock(lockpath)
    lock.break_lock()

def clear_cache_locks():
    """Clear all CRDS cache file locks."""
    lock_names = list(LOCKS.keys())
    for name in lock_names:
        clear_cache_lock(name)
        del LOCKS[name]
        
def _locking_enabled():
    """Return True IFF almalgum of all config settings enable locking."""
    lock = get_cache_lock()
    return not isinstance(lock, CrdsFakeLock)
            
def status():
    """Return configured/actual ability of CRDS to lock the cache."""
    val = "enabled" if _locking_enabled() else "disabled"
    val += ", " + config.LOCKING_MODE
    return val

# =========================================================================

# To avoid a race condition creating a multiprocessing lock,  at a minimum
# the default CRDS cache lock needs to be created at import time.

_LOCKPATH = config.get_crds_lockpath(DEFAULT_LOCK_FILENAME)
with log.warn_on_exception("Failed creating CRDS cache lock", repr(_LOCKPATH)):
    get_cache_lock(DEFAULT_LOCK_FILENAME)

# =========================================================================

def test():
    """Run module doctests."""
    import doctest
    from crds.core import crds_cache_locking
    return doctest.testmod(crds_cache_locking)

if __name__ == "__main__":
    print(test())
