from crds.core.utils import deprecated
from contextlib import contextmanager, nullcontext

# Temporary for deprecated function in crds_cache_locking.py until removed
@contextmanager
def get_cache_lock_noop():
    yield nullcontext()

@deprecated(removed_in="15.0.0", alternative="crds/core/cache_locker.crds_lock")
def get_cache_lock():
    """Deprecated function to provide a no-op context manager for cache locking."""
    return get_cache_lock_noop()

@deprecated(removed_in="15.0.0", alternative="crds/core/cache_locker.clear_cache_locks")
def clear_cache_locks():
    return
