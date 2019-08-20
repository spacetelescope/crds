"""This module supplies the @background decorator and background_complete() results
wait/retrieval function.
"""
import sys
import threading

from crds import exceptions

# ==================================================================================================

class ThreadWithExceptions(threading.Thread):
    """ThreadWithExceptions captures any exception raised during the Thread and stores
    both the result or the exception str() and repr() as attributes.
    """
    def __init__(self, target, *args, **keys):
        super(ThreadWithExceptions, self).__init__(*args, **keys)
        self.target = target
        self.exc = None
        self.rexc = None
        self.result = None

    def run(self):
        """Run the target function, capturing both the return value and any exception
        raised.
        """
        try:
            self.result = self.target()
            self.exc = None
        except:
            _type, exc, _traceb = sys.exc_info()
            self.result = None
            self.rexc = repr(exc)
            self.exc = str(exc)

def background(func):
    """A threading decorator use @background above the function you want to run in
    the background.

    The decorated function returns a daemon thread which allows the main
    program to exit without background task completion.  Unfinished background
    threads shutdown abruptly.
    """

    def run_thread(*args, **keys):
        """Function wrapper which runs the function as a background thread and
        returns the started daemon thread.
        """
        def target_func():
            """Binding function which creates closure of function with passed args
            for purposes of parameterless function for threading.
            """
            return func(*args, **keys)
        thread = ThreadWithExceptions(target=target_func, name=func.__name__)
        thread.daemon = True
        thread.start()
        return thread

    run_thread.__name__ = func.__name__ + "[background]"

    return run_thread

def background_complete(thread):
    """Complete a background task `t` which is either a ThreadWithExceptions object or
    an ordinary return value (which is not a thread).  This structure facilitates un-decorating
    background tasks to make them ordinary functions without restructuring overall control-flow.

    Does a join() iterating every second while thread alive to provide
    foreground thread a guaranteed place to recieve exceptions.

    If background task `t` raises an exception it is reraised here.

    Returns the result of background task.
    """
    if isinstance(thread, threading.Thread):
        while thread.isAlive():
            thread.join(1.0)
        if thread.exc is None:
            return thread.result
        else:
            raise exceptions.CrdsBackgroundError("Exception in", repr(thread.name), ":", repr(thread.exc))
    else:
        return thread

# ==================================================================================================
