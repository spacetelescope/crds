"""CRDS cache locking supports both file-based locks and in-memory multiprocessing locks. The `crds_lock()` function is a smart context manager that automatically detects if multiprocessing architecture is active (parent script initialized the multiprocessing manager), or if using a networked path (which defaults to file-based locking). This ensures proper locking behavior across different environments.

There are two distinct locking mechanisms: file-based (default) and multiprocessing locks.

_filelock_: Synchronizes disks/files for multi-application scaling across multiple processing/terminals/machines, including shared networks. This is the default locking mechanism when multiprocessing is not enabled or when the target path is on a networked filesystem. File locks are implemented using the `filelock` library, which creates a `.lock` file alongside the target file to indicate that it is currently locked. The lock file is automatically cleaned up when the lock is released, but orphaned lock files may remain if a process crashes or is terminated unexpectedly. The `clear_cache_locks()` function can be used to scan for and remove any stale lock files in the cache directory. The CRDS Sync script accepts an optional `--clear-locks` argument to automatically clear any stale locks before proceeding with synchronization.

_multiprocessing_: for multi-core scaling on a single machine/terminal. Synchronizes cores/CPUs. Multiprocessing locks do not work across multiple terminals or machines, and are not safe for networked paths (NFS, SMB, etc.). The multiprocessing locks are managed by a background Manager process that is lazily initialized when needed. This allows for safe sharing of locks across different processes spawned by the same parent script. NOTE: The parent script must call `initialize_multiprocessing_mode()` to set up the Manager and shared locks before any child processes are spawned. The locks are stored in a shared dictionary that is accessible to all child processes. 
"""
import os
import multiprocessing
import sys
import atexit
from contextlib import contextmanager
from pathlib import Path
from filelock import FileLock
from crds.core import log

# Multiprocessing locks to be reused across process tree
_MANAGER = None
_MULTIPROCESSING_LOCKS = None
_INTERNAL_REGINIT_LOCK = multiprocessing.Lock()


def initialize_multiprocessing_mode(shared_dict=None):
    """Call this function (without args) in the parent script before spawning child processes to boot up the central manager and enable multiprocessing locks. Lazily initializes the background Manager process only when needed to ensure no zombie processes are left behind on long-running CLI scripts. Passing values into the kwargs explicitly forces a child worker pool process to point to the parent's central synchronization manager.

    Parameters
    ----------
    shared_dict : dict, optional
        multiprocessing locks dict, by default None
    """
    global _MANAGER, _MULTIPROCESSING_LOCKS
    # worker processes inherit the parent's shared locks
    if shared_dict:
        _MULTIPROCESSING_LOCKS = shared_dict
        _MANAGER = None
        return
    # parent process initializes the manager and shared locks
    with _INTERNAL_REGINIT_LOCK:
        if _MANAGER is None:
            _MANAGER = multiprocessing.Manager()
            _MULTIPROCESSING_LOCKS = _MANAGER.dict()
            atexit.register(shutdown_mp_manager)


def shutdown_mp_manager():
    """Explicitly shuts down background process and clears memory. Safe for multiple calls."""
    global _MANAGER, _MULTIPROCESSING_LOCKS
    with _INTERNAL_REGINIT_LOCK:
        if _MANAGER is not None:
            try:
                _MANAGER.shutdown()
            except Exception:
                pass
            _MANAGER = None
            _MULTIPROCESSING_LOCKS = None


def is_network_path(path: str) -> bool:
    """Check if the given path is a shared network mount (forces file-based locking)."""
    resolved_path = Path(path).resolve()
    str_path = str(resolved_path)
    if sys.platform != "win32": # linux, darwin
        try:
            with open('/proc/mounts', 'r') as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 3 and parts[2] in ('nfs', 'nfs4', 'lustre', 'cifs', 'smbfs'):
                        if str_path.startswith(parts[1]):
                            return True
        except Exception:
            pass
        return False
    # windows
    if str_path.startswith(r"\\") or str_path.startswith("//"): # detect UNC "\\server\share:
        return True
    drive_letter = resolved_path.anchor # Detect mapped network drives "Z:\\" or "C:\\"
    if drive_letter and len(drive_letter) >= 2 and drive_letter[1] == ":":
        # ensure drive path ends with backslash for windows api
        drive_root = drive_letter if drive_letter.endswith(os.sep) else drive_letter + os.sep
        import ctypes
        try:
            drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive_root)
            if drive_type == 4: # mapped network drive (SMB/NFS)
                return True
        except Exception:
            pass
    return False


@contextmanager
def crds_lock(target_filepath: str, timeout: float = 30.0):
    """Smart context manager to acquire a lock on the given target file path.
    Uses multiprocessing.Lock for in-memory locks and FileLock for file-based locks.
    Memory-safe for long-running processes.
    """
    path_obj = Path(target_filepath)
    lock_name = path_obj.name
    if (is_network := is_network_path(target_filepath)):
        log.verbose(f"Networked path detected for {target_filepath}. Defaulting to file-based locking.", verbosity=55)
    # Check if parent script initialized multiprocessing manager
    use_mp_lock = (_MULTIPROCESSING_LOCKS is not None) and not is_network
    if use_mp_lock: # access shared proxy lock safely
        if lock_name not in _MULTIPROCESSING_LOCKS:
            try:
                _MULTIPROCESSING_LOCKS[lock_name] = _MANAGER.Lock()
            except Exception: # Fallback safeguard if manager connection drops
                use_mp_lock = False
    if not use_mp_lock: # Default to fine-grained file locking
        lock_path = f"{target_filepath}.lock"
        lock = FileLock(lock_path, timeout=timeout) # TODO OS-native locks work on NFS v4 - if v3 swap for SoftFileLock
        try:
            with lock:
                log.verbose(f"Acquired file lock: {lock_path}", verbosity=40)
                yield
        finally:
            # Clean up lock file safely if no longer needed
            try:
                os.remove(lock_path)
                log.verbose(f"Released file lock: {lock_path}", verbosity=40)
            except (OSError, FileNotFoundError):
                pass
    else: # Multiprocessing mode using inherited manager lock
        mp_lock = _MULTIPROCESSING_LOCKS[lock_name]
        acquired = mp_lock.acquire(timeout=timeout)
        if not acquired:
            raise TimeoutError(f"Could not acquire multiprocessing lock for {lock_name} within {timeout} seconds.")
        log.verbose(f"Acquired multiprocessing lock for {lock_name}", verbosity=40)
        try:
            yield
        finally:
            mp_lock.release()
            log.verbose(f"Released multiprocessing lock for {lock_name}", verbosity=40)


def clear_cache_locks(cache_root_dir: str):
    """Scans CRDS cache and removes any orphaned file locks (.lock files) that may have been left behind by aborted or crashed processes."""
    cache_path = Path(cache_root_dir)
    if not cache_path.exists():
        log.warning(f"Cache directory {cache_root_dir} does not exist. No locks to clear.")
        return
    log.info(f"Scanning {cache_root_dir} for stale file locks...", verbosity=55)
    lock_files = cache_path.rglob("*.lock")
    count = 0
    for lock_file in lock_files:
        try:
            lock_file.unlink()
            log.verbose(f"Removed stale lock: {lock_file}", verbosity=55)
            count += 1
        except Exception as e:
            log.error(f"Failed to remove lock {lock_file}: {e}")
    log.info(f"Cleared {count} stale file lock(s) from cache.")
