"""Some simple console message functions w/counting features for
errors, warnings, and info.  Also error exception raising and
tracebacks.

>>> from crds.core import log
>>> log.set_test_mode()
>>> log.reset()

>>> log.warning("this is a test warning.")
CRDS - WARNING - this is a test warning.

>>> log.error("this is a test error.")
CRDS - ERROR - this is a test error.

>>> log.error("this is another test error.")
CRDS - ERROR - this is another test error.

>>> log.info("this is just informative.")
CRDS - INFO - this is just informative.

>>> log.errors()
2

>>> log.status()
(2, 1, 1)

>>> log.standard_status()
CRDS - INFO - 2 errors
CRDS - INFO - 1 warnings
CRDS - INFO - 1 infos

By default verbose messages are not emitted:

>>> log.verbose("this is a test verbose message.")

Calling set_verbose() turns on default verbosity=50:

>>> old_verbose = log.set_verbose()

>>> log.verbose("this is a test verbose message.")
CRDS - DEBUG - this is a test verbose message.

No output is expected since default verbosity=50:

>>> log.verbose("this is a test suppressed verbose 60 message.", verbosity=60)

Output should now occur since verbosity=60:

>>> log.set_verbose(60)
50
>>> log.verbose("this is a test verbose 60 message.", verbosity=60)
CRDS - DEBUG - this is a test verbose 60 message.

A number of context managers are defined for succinctly mapping nested
exceptions onto CRDS messages or adding information:

>>> with log.error_on_exception("Something bad happened and we trapped it"):
...     raise ValueError("some value was bad.")
CRDS - ERROR - Something bad happened and we trapped it : some value was bad.

>>> with log.augment_exception("A tad more parent info"):
...     raise ValueError("some vague deeply nested exception.")
Traceback (most recent call last):
...
ValueError: A tad more parent info : some vague deeply nested exception.

When the exception trap mode is set to False,  the exception context managers
let the exceptions pass through unmodified:

>>> old_trap = log.set_exception_trap(False)

>>> with log.error_on_exception("Something bad happened and we trapped it"):
...     raise ValueError("some value was bad.")
Traceback (most recent call last):
...
ValueError: some value was bad.

>>> with log.error_on_exception("Something bad happened and we trapped it"):
...     raise ValueError("some value was bad.")
...     print("this code not reached")
Traceback (most recent call last):
...
ValueError: some value was bad.

>>> with log.augment_exception("A tad more parent info"):
...     raise ValueError("some vague deeply nested exception.")
Traceback (most recent call last):
...
ValueError: some vague deeply nested exception.

Command line tools control the exception trap flag using --debug-traps,  this is
useful for debugging anomalies during type (or tool) development.   The key points
about the exception trap flag are that (a) traps are passed through and (b) exceptions
are carefully reraised so the original traceback is not destroyed.

>>> _ = log.set_verbose(old_verbose)
>>> _ = log.set_exception_trap(old_trap)

>>> old_verbose = log.set_verbose()

>>> with log.verbose_warning_on_exception("Testing expected verbose warning"):
...     raise ValueError("Force verbose warning.")
...     log.write("This code should not be exected.")
CRDS - WARNING -  Testing expected verbose warning : Force verbose warning.

>>> _ = log.set_verbose(old_verbose)
"""
import sys
import os
import optparse
import logging
import pprint
import contextlib

DEFAULT_VERBOSITY_LEVEL = 50

class CrdsLogger:
    def __init__(self, name="CRDS", enable_console=True, level=logging.DEBUG, enable_time=True):
        self.name = name

        self.handlers = []  # logging handlers, used e.g. to add console or file output streams
        self.filters = []   # simple CRDS filters, used e.g. to mutate message text

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False
        self.formatter = self.set_formatter()
        self.console = None
        if enable_console:
            self.add_console_handler(level)

        # CRDS internal counters of types of messages
        self.errors = 0
        self.warnings = 0
        self.infos = 0
        self.debugs = 0

        self.eol_pending = False

        # verbose_level handles CRDS verbosity,  defaulting to 0 for no debug
        try:
            verbose_level = os.environ.get("CRDS_VERBOSITY", 0)
            self.verbose_level =  int(verbose_level)
        except Exception:
            warning("Bad format for CRDS_VERBOSITY =", repr(verbose_level),
                        "Use e.g. -1 to squelch info, 0 for no debug,  50 for default debug output. 100 max debug.")
            self.verbose_level = DEFAULT_VERBOSITY_LEVEL

    def set_formatter(self, enable_time=False, enable_msg_count=True):
        """Set the formatter attribute of `self` to a logging.Formatter and return it."""
        self.formatter = logging.Formatter(
            '{}%(name)s - %(levelname)s - %(message)s'.format(
                "%(asctime)s - " if enable_time else "",
                ))
        for handler in self.handlers:
            handler.setFormatter(self.formatter)
        return self.formatter

    @property
    def msg_count(self):
        return "(%07d) -" % (self.infos + self.errors + self.warnings + self.debugs) if ADD_LOG_MSG_COUNT else ""

    def format(self, *args, **keys):
        end = keys.get("end", "\n")
        sep = keys.get("sep", " ")
        output = sep.join([str(arg) for arg in args]) + end
        for filter in self.filters:
            output = filter(output)
        return output

    def eformat(self, *args, **keys):
        keys["end"] = ""
        if self.eol_pending:
            self.write()
        return self.format(*args, **keys)

    def info(self, *args, **keys):
        self.infos += 1
        if self.verbose_level > -1:
            self.logger.info(self.eformat(self.msg_count, *args, **keys))

    def warn(self, *args, **keys):
        self.warnings += 1
        if self.verbose_level > -2:
            self.logger.warning(self.eformat(self.msg_count, *args, **keys))

    def error(self, *args, **keys):
        self.errors += 1
        if self.verbose_level > -3:
            self.logger.error(self.eformat(self.msg_count, *args, **keys))

    def debug(self, *args, **keys):
        self.debugs += 1
        self.logger.debug(self.eformat(self.msg_count, *args, **keys))

    def should_output(self, *args, **keys):
        verbosity = keys.get("verbosity", DEFAULT_VERBOSITY_LEVEL)
        return not self.verbose_level < verbosity

    def verbose(self, *args, **keys):
        if self.should_output(*args, **keys):
            self.debug(*args, **keys)

    def verbose_warning(self, *args, **keys):
        if self.should_output(*args, **keys):
            self.warn(*args, **keys)

    def write(self, *args, **keys):
        """Output a message to stdout, formatting each positional parameter
        as a string.
        """
        output = self.format(*args, **keys)
        self.eol_pending = not output.endswith("\n")
        sys.stderr.flush()
        sys.stdout.write(output)
        sys.stdout.flush()

    def status(self):
        return self.errors, self.warnings, self.infos

    def reset(self):
        self.errors = self.warnings = self.infos = self.debugs = 0

    def set_verbose(self, level=True):
        assert -3 <= level <= 100,  "verbosity level must be in range -3..100"
        old_verbose = self.verbose_level
        if level == True:
            level = DEFAULT_VERBOSITY_LEVEL
        elif level == False:
            level = 0
        self.verbose_level = level
        return old_verbose

    def get_verbose(self):
        return self.verbose_level

    def add_console_handler(self, level=logging.DEBUG, stream=sys.stderr):
        if self.console is None:
            self.console = self.add_stream_handler(stream)

    def remove_console_handler(self):
        if self.console is not None:
            self.remove_stream_handler(self.console)
            self.console = None

    def add_stream_handler(self, filelike, level=logging.DEBUG):
        handler = logging.StreamHandler(filelike)
        handler.setLevel(level)
        handler.propagate = False
        handler.setFormatter(self.formatter)
        self.handlers.append(handler)
        self.logger.addHandler(handler)
        return handler

    def remove_stream_handler(self, handler):
        self.handlers.remove(handler)
        self.logger.removeHandler(handler)

    def fatal_error(self, *args, **keys):
        error("(FATAL)", *args, **keys)
        sys.exit(-1)  # FATAL == totally unambiguous

    def prepend_crds_filter(self, filter):
        """Prepend a message `filter` to CRDS log output independent of logging framework."""
        if filter not in self.filters:
            self.filters = [filter] + self.filters

    def append_crds_filter(self, filter):
        """Append a message `filter` to CRDS log output independent of logging framework."""
        if filter not in self.filters:
            self.filters = self.filters + [filter]

    def remove_crds_filter(self, filter):
        """Remove `filter` from the sequence of CRDS message filters."""
        if filter in self.filters:
            self.filters.remove(filter)

THE_LOGGER = CrdsLogger("CRDS")

info = THE_LOGGER.info
error = THE_LOGGER.error
warning = THE_LOGGER.warn
verbose_warning = THE_LOGGER.verbose_warning
verbose = THE_LOGGER.verbose
should_output = THE_LOGGER.should_output
debug = THE_LOGGER.debug
fatal_error = THE_LOGGER.fatal_error
status = THE_LOGGER.status
reset = THE_LOGGER.reset
write = THE_LOGGER.write
set_verbose = THE_LOGGER.set_verbose
get_verbose = THE_LOGGER.get_verbose
add_console_handler = THE_LOGGER.add_console_handler
remove_console_handler = THE_LOGGER.remove_console_handler
add_stream_handler = THE_LOGGER.add_stream_handler
remove_stream_handler = THE_LOGGER.remove_stream_handler
append_crds_filter = THE_LOGGER.append_crds_filter
remove_crds_filter = THE_LOGGER.remove_crds_filter
prepend_crds_filter = THE_LOGGER.prepend_crds_filter
format = THE_LOGGER.format

def increment_errors(N=1):
    """Increment the error count by N without issuing a log message."""
    THE_LOGGER.errors += N

def errors():
    """Return the global count of errors."""
    return THE_LOGGER.errors

def warnings():
    """Return the global count of errors."""
    return THE_LOGGER.warnings

def infos():
    """Return the global count of infos."""
    return THE_LOGGER.infos

def set_test_mode():
    """Route log messages to standard output for testing with doctest."""
    remove_console_handler()
    add_console_handler(stream=sys.stdout)
    set_log_time(False)

def set_log_time(enable_time=False):
    """Set the flag for including time in log messages.  Ignore CRDS_LOG_TIME."""
    THE_LOGGER.set_formatter(enable_time)

# ===========================================================================

@contextlib.contextmanager
def reduced_verbosity(reduced_level, threshhold):
    """Sets the global verbosity level to `reduced_level` as long as it is already below `threshhold`
    within the scope of the with-block / context manager.

    If the global verbosity is above `threshhold`,  don't set to `reduced_level` enabling high verbosity settings
    to bypass the suppression.
    """
    old_verbose = get_verbose()
    if old_verbose < threshhold:
        set_verbose(min(old_verbose, reduced_level))
    try:
        yield
    finally:
        if old_verbose < threshhold:
            set_verbose(old_verbose)

# ===========================================================================

def exception_trap_logger(func):
    @contextlib.contextmanager
    def func_on_exception(*args, **keys):
        """func_on_exception is a context manager which issues a func() message if any statement
        in a with-block generates an exception.   The exception is suppressed.

        >> with warn_on_exception("As expected, it failed."):
        ...    print("do it.")
        do it.

        >> with warn_on_exception("As expected, it failed."):
        ...    raise Exception("It failed!")
        ...    print("do it.")

        Never printed 'do it.'  Nothing printed because the func() output is a log message.
        """
        try:
            yield
        except Exception as exc:
            reraise = func(*args + (":", str(exc)), **keys)
            if not CRDS_EXCEPTION_TRAP:
                # In python-2, distinction between raise and "raise something".  raise doesn't
                # wreck the traceback,  raising a new improved exception does.
                raise
            # Augmented,  the traceback is trashed from here down but the message is better when caught higher up.
            elif reraise:
                exc_class = keys.pop("exception_class", exc.__class__)
                keys["end"] = ""
                raise exc_class(format(*args + (":", str(exc)), **keys)) from exc
            else:
                pass # snuff the exception,  func() probably issued a log message.
    return func_on_exception

CRDS_EXCEPTION_TRAP = True

def get_exception_trap():
    """Return the value of the exception trap flag,  False means 'debug'."""
    return CRDS_EXCEPTION_TRAP

def set_exception_trap(flag):
    """Set the debug by-pass mode flag for log.error_on_exception() exception trap."""
    global CRDS_EXCEPTION_TRAP
    old_flag = CRDS_EXCEPTION_TRAP
    if flag is not None:
        CRDS_EXCEPTION_TRAP = flag
    return old_flag

def _reraise(*args, **keys):
    """Signal to exception_trap_logger to unconditionally reraise the exception,  probably augmented."""
    return True

info_on_exception = exception_trap_logger(info)
debug_on_exception = exception_trap_logger(debug)
verbose_on_exception = exception_trap_logger(verbose)
verbose_warning_on_exception = exception_trap_logger(verbose_warning)
warn_on_exception = exception_trap_logger(warning)
error_on_exception = exception_trap_logger(error)
fatal_error_on_exception = exception_trap_logger(fatal_error)

# Either supress-with-error or augment the exception in the enclosed block.
# Suppressing an exception results in less information to identify the problem
# but can also reveal multiple problems in a single program run if executed
# inside a loop that an augmented exception would have exited.
if bool(os.environ.get("CRDS_TRAP_AUGMENTED", False)):
    augment_exception = error_on_exception
else:
    augment_exception = exception_trap_logger(_reraise)

# ===========================================================================

ADD_LOG_MSG_COUNT = False

def set_add_log_msg_count(flag):
    global ADD_LOG_MSG_COUNT
    old_flag = ADD_LOG_MSG_COUNT
    ADD_LOG_MSG_COUNT = flag
    return old_flag

def get_add_log_msg_count():
    return ADD_LOG_MSG_COUNT

# ===========================================================================

class PP:
    """A wrapper to defer pretty printing until after it's known a verbose
    message will definitely be output.
    """
    def __init__(self, ppobj):
        self.ppobj = ppobj

    def __str__(self):
        return pprint.pformat(self.ppobj)

class Deferred:
    """A wrapper to delay calling a callable until after it's known a verbose
    message will definitely be output.
    """
    def __init__(self, ppobj):
        self.ppobj = ppobj

    def __str__(self):
        return str(self.ppobj())

# ===========================================================================

def handle_standard_options(
        args, parser=None, usage="usage: %prog [options] <inpaths...>"):
    '''Set some standard options on an optparser object,  many
    of which interplay with the log module itself.
    '''
    if parser is None:
        parser = optparse.OptionParser(usage)

    parser.add_option("-V", "--verbose", dest="verbose",
                      help="Set verbosity level.",
                      metavar="VERBOSITY", default=None)

    options, args = parser.parse_args(args)

    if options.verbose is not None:
        set_verbose(int(options.verbose))

    return options, args

def standard_status():
    """Print out errors, warnings, and infos."""
    errors, warnings, infos = THE_LOGGER.status()
    info(errors, "errors")
    info(warnings, "warnings")
    info(infos, "infos")

# ==============================================================================

def format_parameter_list(parameters):
    """Given an item list or dictionary of matching parameters,  return a formatted string.
    Typically used to format matching parameters or bestrefs dicts for debug.
    """
    items = sorted(dict(parameters).items())
    return " ".join(["=".join([key, repr(str(value))]) for (key,value) in items])

# ==============================================================================

def srepr(obj):
    """Return the repr() of the str() of obj"""
    return repr(str(obj))

# ==============================================================================

def divider(name="", char="-", n=75, func=info, **keys):
    """Create a log divider line consisting of `char` repeated `n` times
    possibly with `name` injected into the center of the divider.
    Output it as a string to logging function `func` defaulting to info().
    """
    if name:
        n2 = (n - len(name) - 2) // 2
        func(char*n2, name, char*n2, **keys)
    else:
        func(char*n, **keys)

# ===================================================================

def test():
    from crds.core import log
    import doctest
    return doctest.testmod(log)

if __name__ == "__main__":
    print(test())
