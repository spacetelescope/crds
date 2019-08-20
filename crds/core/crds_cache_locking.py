"""This module defines locking primitives for the CRDS cache used to prevent
simultaneous writes.  This is principally motivated by the JWST association
logic which may attempt to prefetch files for multiple images at the same time,
often in a multiprocessing expansion running multiple associations concurrently.

CRDS locking wraps more primitive locking functionality such as that provided by
the lockfile package or the multiprocessing module.  In general locks should be
assumed to be non-recursive and will deadlock if the owner attempts to acquire a
second instance.

A number of configuration env var settings control locking behavior, see
crds.core.config for more info.
"""
import os
import multiprocessing

# =========================================================================

# import lockfile,  deferred
# import filelock,  deferred

# =========================================================================

from . import log, config, utils

# =========================================================================

def _warn_required(locking_module):
    if config.LOCKING_MODE == locking_module:
        log.verbose_warning("Locking package '{}' is not installed.".format(locking_module))
        log.verbose_warning("CRDS locking cannot be used and will be bypassed.")
    return CrdsFakeLock

# =========================================================================

class CrdsAbstractLock:
    """At a design level this also serves as an abstract class defining the API."""

    _lock = None  # Overridden in most cases
    log = log.verbose

    def __init__(self, lockname):
        """Abstract lock initialization."""
        self.log("Creating lock", repr(lockname), verbosity=55)
        self.lockname = lockname

    def __repr__(self):
        """Abstract lock repr."""
        return self.__class__.__name__ + "('" + self.lockname + "')"

    def acquire(self, *args, **keys):
        """Acquire delegate lock,  adding CRDS verbose logging."""
        self.log("Acquiring lock", repr(self))
        self._acquire(*args, **keys)
        self.log("Lock acquired", repr(self))

    def release(self, *args, **keys):
        """Release delegate lock,  adding CRDS verbose logging."""
        self.log("Releasing lock", repr(self))
        self._release(*args, **keys)
        self.log("Lock released", repr(self))

    def break_lock(self):
        """Break delegate lock,  adding CRDS verbose logging."""
        self.log("Breaking lock", repr(self))
        self._break_lock()
        self.log("Broke lock", repr(self))

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
        with log.warn_on_exception("Failed releasing lock"):
            self._lock.release(*args, **keys)

    def _break_lock(self, *args, **keys):
        """Noop,  override as needed."""
        pass

# =========================================================================

# Always defined as fall back

class CrdsFakeLock(CrdsAbstractLock):
    """Placeholder dummy lock to do nothing,  silently since normal for pipeline."""

    def log(self, *args, **keys):
        """Fake locks are silent."""

    def _acquire(self, *args, **keys):
        """Fake _acquire does nothing."""

    def _release(self, *args, **keys):
        """Fake _acquire does nothing."""

    def _break_lock(self):
        """Fake _acquire does nothing."""

# =========================================================================

class failed_module_proxy:
    """Generate an exception only when module is actually used by runtime lock
    instantiation.
    """
    def __init__(self, name):
        self.name = name
    def __getattr__(self, attr):
        raise ImportError(repr(self.name) + " import failed.")

# =========================================================================

class CrdsMultiprocessingLock(CrdsAbstractLock):
    """Wrap multiprocessing.Lock as locking basis."""
    def __init__(self, lockname):
        super(CrdsMultiprocessingLock, self).__init__(lockname)
        self._lock = multiprocessing.Lock()

# =========================================================================

try:
    import filelock
except ImportError:
    filelock = failed_module_proxy("filelock")  # instantiating lock intentionally fails

class CrdsFileLock(CrdsAbstractLock):
    """Wrap filelock.FileLock as locking basis.  self.lockname is path."""
    def __init__(self, lockname):
        super(CrdsFileLock, self).__init__(config.get_crds_lockpath(lockname))
        self._lock = filelock.FileLock(self.lockname)

    def _break_lock(self, *args, **keys):
        """Destroy lock regardless of who owns it."""
        try:
            os.remove(self.lockname)
        except Exception:
            pass

# =========================================================================

try:
    import lockfile
except ImportError:
    lockfile = failed_module_proxy("lockfile")  # instantiating lock intentionally fails

class CrdsLockFile(CrdsAbstractLock):
    """Wrap lockfile.LockFile as locking basis.  self.lockname is path."""
    def __init__(self, lockname):
        super(CrdsLockFile, self).__init__(config.get_crds_lockpath(lockname))
        self._lock = lockfile.LockFile(self.lockname)

    def _break_lock(self,  *args, **keys):
        """Destroy lock regardless of who owns it."""
        try:
            self._lock.break_lock(*args, **keys)
        except Exception:
            pass
        try:
            os.remove(self.lockname)
        except Exception:
            pass

# =========================================================================

LOCKS = {}   #  { lockpath : CrdsAbstractLockSubclass, ... }

def get_lock(lockname):
    """Create, remember, and return the lock object globally referred to by string `lockname`."""
    if lockname in LOCKS:
        lock = LOCKS[lockname]
    else:
        with LOCKS["crds.master"]:
            lock = LOCKS[lockname] = create_lock(lockname)
    return lock

def get_lock_class():
    """Based on CRDS configuration,  return the lock class."""
    classes = {
        "multiprocessing" : CrdsMultiprocessingLock,
        "filelock" : CrdsFileLock,
        "lockfile" : CrdsLockFile,
    }
    return classes[config.LOCKING_MODE]

def create_lock(lockname):
    """Return a lock context manager to guard the CRDS cache against concurrent
writes."""
    lock = CrdsFakeLock(lockname)
    if not config.USE_LOCKING.get():
        _explain_once("CRDS_USE_LOCKING = False. Cannot support downloading CRDS files while multiprocessing.", log.verbose)
    elif not config.get_cache_readonly():
        lock_class = get_lock_class()
        try:
            lock = lock_class(lockname)
        except Exception as exc:
            _explain_once("Failed creating CRDS cache lock: " + str(exc),
                          log.warning)
    return lock

@utils.cached
def _explain_once(explain, logger):
    """Issue locking unsupported message `explain` to `logger` once."""
    logger(explain)

# =========================================================================

def clear_lock(lockname):
    """Make sure that `lock_filename` does not exist."""
    lock = get_lock(lockname)
    lock.break_lock()

def clear_locks():
    """Clear all CRDS cache file locks."""
    lock_names = list(LOCKS.keys())
    for name in lock_names:
        clear_lock(name)
        LOCKS.pop(name, None)

def locking_enabled():
    """Return True IFF almalgum of all config settings enable locking."""
    return not isinstance(get_cache_lock(), CrdsFakeLock)

def status():
    """Return configured/actual ability of CRDS to lock the cache."""
    val = "enabled" if locking_enabled() else "disabled"
    val += ", " + config.LOCKING_MODE
    return val

# =========================================================================

get_cache_lock = lambda: get_lock("crds.cache")
create_cache_lock = lambda: create_lock("crds.cache")
clear_cache_lock = lambda: clear_lock("crds.cache")
clear_cache_locks = clear_locks

# =========================================================================

# To avoid a race condition creating a multiprocessing lock,  at a minimum
# the default CRDS cache lock needs to be created at import time.

def init_lock(lockname):
    """Create lock `lockname` without guarding global LOCKS.  Warn on fail."""
    with log.warn_on_exception("Failed creating CRDS lock", repr(lockname)):
        LOCKS[lockname] = create_lock(lockname)

def init_locks():
    """Fully initialize/re-initialize standard locks."""
    # clear_locks()   This is not multi-tree multiprocessing safe
    init_lock("crds.master")
    init_lock("crds.cache")

init_locks()

# =========================================================================

def test():
    """Run module doctests."""
    import doctest
    from crds.core import crds_cache_locking
    return doctest.testmod(crds_cache_locking)

if __name__ == "__main__":
    print(test())
