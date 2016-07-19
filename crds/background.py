"""Implements background multi-threaded processing for CRDS,  primarily for multi-threaded file
submissions,  based on "futures" package.
"""
import sys

if sys.version_info >= (3, 0, 0):
    from concurrent import futures
else:
    from concurrent import futures

# -------------------------------------------------------------------------------------

CRDS_MAX_THREADS = 10   # number of background threads,  primarily for file submission

EXECUTOR = None

# -------------------------------------------------------------------------------------

def init_futures():
    global EXECUTOR
    if EXECUTOR is None:
        EXECUTOR = futures.ThreadPoolExecutor(max_workers=CRDS_MAX_THREADS)
    
def background(f):
    """a threading decorator use @background above the function you want to run in the background.
    The decorated function returns (thread, queue) where queue will contain the function result
    and thead is already started but not joined.
    """
    def run_thread(*args, **keys):
        init_futures()
        future = EXECUTOR.submit(f, *args, **keys)
        return future

    run_thread.__name__ = f.__name__ + "[background]"

    return run_thread

def background_complete(future):
    """Wait for background task `future` to complete and return the result of the background
    function.
    """
    if isinstance(future, futures.Future):
        return future.result()
    else:
        return future
