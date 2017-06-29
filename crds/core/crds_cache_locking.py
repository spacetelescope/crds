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

import contextlib
import os.path

# =========================================================================

from . import log, config, utils

# =========================================================================

try:
    import lockfile
except ImportError:
    lockfile = None

# =========================================================================

@contextlib.contextmanager
def get_fake_crds_lock(lockpath):    
    """Return an empty lock context manager so that CRDS does not outright crash in
    all cases because it attempts to support e.g. sync'ing references for multiple
    association images concurrently.
    """
    try:
        yield
    finally:
        pass

# =========================================================================

class CrdsLockFile(lockfile.LockFile):

    def __init__(self, lockpath):
        self._lockpath = lockpath
        super(CrdsLockFile, self).__init__(self._lockpath)
        
    def __enter__(self):
        log.verbose("Acquiring lock", repr(self))
        result = super(CrdsLockFile, self).__enter__()
        log.verbose("Lock acquired", repr(self))
        return result
        
    def __exit__(self, *exc):
        log.verbose("Releasing lock", repr(self))
        result = super(CrdsLockFile, self).__exit__(*exc)
        log.verbose("Lock released", repr(self))
        return result
    
 
# =========================================================================

DEFAULT_LOCK_FILENAME = ".crds.cache.lock"   # filename only

def get_cache_lock(lock_filename=DEFAULT_LOCK_FILENAME):
    """Return a file lock context manager to guard the CRDS cache against
    concurrent writes.
    """
    lockpath = config.get_crds_lockpath(lock_filename)
    
    if lockfile is None:
        log.warning("Failed importing 'lockfile' package.  "
                    "Cannot support downloading files while multiprocessing.")
        
    if config.get_cache_readonly():
        log.verbose("CRDS cache is readonly, omitting cache file locking.")
        return get_fake_crds_lock(lockpath)
        
    try:
        # XXXX lock dir creation turns into a locking issue,  use pre-existing path.
        # Either initialize cache using "crds sync --last 1" or set CRDS_CACHE_LOCK_PATH
        # utils.ensure_dir_exists(lockpath)
        return CrdsLockFile(lockpath)
    except Exception as exc:
        log.warning("Failed creating CRDS cache lock file. "
                    "Cannot support multiprocessing while syncing reference files.")
        log.warning("Exception was:", str(exc))
        return get_fake_crds_lock(lockpath)

def clear_cache_lock(lock_filename=DEFAULT_LOCK_FILENAME):
    """Make sure that `lock_filename` does not exist."""
    lockpath = config.get_crds_lockpath(lock_filename)
    utils.remove(lockpath, "all")  # all is observatory for root config dir.

# =========================================================================

def test():
    import doctest
    from crds import crds_cache_locking
    return doctest.testmod(crds_cache_locking)

if __name__ == "__main__":
    print(test())

