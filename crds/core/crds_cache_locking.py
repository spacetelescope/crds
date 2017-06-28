"""This module defines locking primitives for the CRDS cache used to prevent
simultaneous writes.  This is principally motivated by the JWST association
logic.
"""

# =========================================================================

import contextlib
import os.path

# =========================================================================

from . import log, config

# =========================================================================

try:
    import lockfile
except ImportError:
    log.verbose_warning("Failed importing 'lockfile' package.  "
                        "CRDS cannot support cache syncs while multiprocessing.")

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

def get_cache_lock():
    """Return a file lock context manager to guard the CRDS cache against
    concurrent writes.
    """
    if config.writable_cache_or_warning("cannot sync files or create cache file lock."):
        lockpath = config.CACHE_LOCK.get()
        try:
#             utils.ensure_dir_exists(lockpath)  XXXX this itself turns into a locking issue,  use one lock.
            return lockfile.LockFile(lockpath)
        except Exception as exc:
            log.verbose_warning("Failed creating CRDS cache lock file during cache sync. "
                        "Cannot support multiprocessing while syncing reference files.")
            log.verbose_warning("Exception was:", str(exc))
            return get_fake_crds_lock(lockpath)
    else:
        return get_fake_crds_lock(lockpath)
