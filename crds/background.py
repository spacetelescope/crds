"""This module supplies the @background decorator and background_complete() results
wait/retrieval function.
"""

import threading

# ==================================================================================================

class ThreadWithExceptions(threading.Thread):
    def __init__(self, target, *args, **keys):
        super(ThreadWithExceptions, self).__init__(*args, **keys)
        self.target = target
        self.exc = None
        self.rexc = None
        self.result = None

    def run(self):
        try:
            self.result = self.target()
            self.exc = None
        except:
            exc = sys.exc_value
            self.result = None
            self.rexc = repr(exc)
            self.exc = str(exc)

def background(f):
    """A threading decorator use @background above the function you want to run in the background.

    The decorated function returns a daemon thread.   The result is captured by the background_complete
    function which either does the necessary join and results extraction *or* simply returns the result
    making it easy to stop backgrounding by commenting out the decorator but retaining the join control
    flow.
    """

    def run_thread(*args, **keys):
        def target_func():
            return f(*args, **keys)
        t = ThreadWithExceptions(target=target_func, name=f.__name__)
        t.daemon = True
        t.start()
        return t

    run_thread.__name__ = f.__name__ + "[background]"

    return run_thread

def background_complete(t):
    if isinstance(t, threading.Thread):
        while t.isAlive():
            t.join(1.0)
        if t.exc is None:
            return t.result
        else:
            raise exceptions.RuntimeError("Threading exception in", repr(t.name), ":", repr(t.exc))
    else:
        return t

# ==================================================================================================

