"""Some simple console message functions w/counting features for
errors, warnings, and info.  Also error exception raising and
tracebacks.
"""
import sys
import optparse
import traceback
import StringIO
import profile
import pdb
import datetime
import os.path

def format(*args, **keys):
    """Format a string from log-output-function parameters.
    """
    eol = keys.get("eol", "\n")
    sep = keys.get("sep", " ")
    file = StringIO.StringIO()
    for arg in args:
        file.write(str(arg) + sep)
    file.write(eol)
    file.seek(0)
    return file.read()

# A partial line has been written out.  Force an EOL before ERROR or WARNING.
EOL_PENDING = False

def write(*args, **keys):
    """Output a message to stdout, formatting each positional parameter
    as a string.
    """
    global EOL_PENDING
    s = format(*args, **keys)
    EOL_PENDING = not s.endswith("\n")
    sys.stdout.write(s)
    sys.stdout.flush()
    if LOG:
        LOG.write(s)
        LOG.flush()
    if TEST_ERR:
        TEST_ERR.write(s)
        TEST_ERR.flush()

def exception(*args, **keys):
    """Format an exception message and raise an exception.
    """
    exception = keys.get("exception",Exception)
    s = format(*args, **keys)
    raise exception(s)


LOG = None
LOG_TIMESTAMPS = False
def set_log(filename, append=False, timestamps=False):
    """Capture log output in the specified file.
    """
    global LOG, LOG_TIMESTAMPS
    LOG_TIMESTAMPS = timestamps
    if filename:
        ensure_dir_exists(filename)
        LOG = open(filename, append and "a+" or "w+")
    elif LOG:
        LOG.close()
        LOG = None

TEST_ERR=None
ROOTFILE=""
def set_test_err(filename):
    """Open/close a third per-test log file."""
    global TEST_ERR, ROOTFILE
    if TEST_ERR is not None:
        TEST_ERR.close()
        TEST_ERR = None
    if filename is None:
        TEST_ERR = None
        ROOTFILE = ""
        return
    else:
        ensure_dir_exists(filename)
        TEST_ERR = open(filename, "a+")
        ROOTFILE = "[" + os.path.basename(os.path.splitext(filename)[0]) + "]"

def create_path(path):
    """Recursively traverses directory path creating directories as
    needed so that the entire path exists.
    """
    if path.startswith("./"):
        path = path[2:]
    if os.path.exists(path):
        return
    current = []
    for c in path.split("/"):
        if not c:
            current.append("/")
            continue
        current.append(str(c))
        # log.write("Creating", current)
        d = os.path.join(*current)
        d.replace("//","/")
        if not os.path.exists(d):
            os.mkdir(d)

def ensure_dir_exists(fullpath):
    """Creates dirs from `fullpath` if they don't already exist.
    """
    create_path(os.path.dirname(fullpath))


VERBOSE_FLAG = False
def set_verbose(flag):
    global VERBOSE_FLAG
    VERBOSE_FLAG = flag

def get_verbose():
    return VERBOSE_FLAG

def verbose(*args, **keys):
    """Print out the args if in verbose mode."""
    if VERBOSE_FLAG:
        write(*args, **keys)

def quiet(*args, **keys):
    """Print out the args if NOT in verbose mode."""
    if not VERBOSE_FLAG:
        write(*args, **keys)

def logtime():
    if LOG_TIMESTAMPS:
        return "[" + str(datetime.datetime.now())[:-4] + "]"
    else:
        return ""

INFOS = 0
def info(*args, **keys):
    """logs and count an info message."""
    global INFOS, EOL_PENDING
    INFOS += 1
    if EOL_PENDING: write()
    write(*(("INFO:[%d]%s:" % (INFOS, logtime()),) + args), **keys)

def infos():
    """Returns count of logged warnings."""
    return INFOS

WARNINGS = 0
def warning(*args):
    """logs and count a warning message."""
    global WARNINGS, EOL_PENDING
    WARNINGS += 1
    if EOL_PENDING: write()
    write(*(("WARNING[%d]%s%s:" % (WARNINGS, ROOTFILE, logtime()),) + args))

def verbose_warning(*args):
    """Issue a warning message only in verbose mode."""
    if VERBOSE_FLAG:
        warning(*args)

def warnings():
    """Returns count of logged warnings."""
    return WARNINGS

ERRORS = 0
DEBUG_ERRORS = False
DEBUG_ERRNO = -1
SHOW_TRACEBACKS = False

class DebugBreak(Exception):
    pass

def error(*args, **keys):
    """logs and counts and error message.  In general, presumes a
    caught exception.
    """
    global ERRORS, EOL_PENDING, ROOTFILE

    exc = sys.exc_info()
    if (DEBUG_ERRORS or DEBUG_ERRNO == ERRORS+1) and not exc[2]:
        # If this error didn't come from an exception, and debugging
        # errors, create an exception to unwind the stack and re-catch
        # the error later.  Don't increment error number now because
        # the same error number will need to be re-caught later.
        # Hopefully the way this works will be intuitive even if the
        # implementation is not.  This will create a stack trace
        # starting at the original error call.
        write(*(("ERROR[%d]%s%s:" % (ERRORS+1, ROOTFILE, logtime(),),) + args), **keys)
        raise DebugBreak("Forced debug exception.")

    ERRORS += 1

    keys.update({ "eol": "" })
    no_traceback = keys.pop("no_traceback", False)

    if EOL_PENDING: write()
    write(*(("ERROR[%d]%s%s:" % (ERRORS, ROOTFILE, logtime(),),) + args), **keys)

    if exc[0]:
        write(":", exc[1])
    else:
        write()

    if (DEBUG_ERRORS or DEBUG_ERRNO == ERRORS):
        if exc[2]:
            import pdb
            pdb.post_mortem(exc[2])
        else:
            write("No exception for specified error no.")
    elif SHOW_TRACEBACKS and not no_traceback:
        # If exception not re-raised,  optionally log the traceback.
        if exc[2]:
            write("Log TRACEBACK:")
            tb_list = traceback.extract_tb(exc[2])
            for l in traceback.format_list(tb_list):
                write(l)
    sys.exc_clear()

def errors():
    """Returns count of logged warnings."""
    return ERRORS

def set_debug_errors(flag=True, errno=None):
    """Makes calls to error() raise an exception when `flag` is True.
    Only raises an exception when `errno` is None or `errno` equals
    ERRORS.
    """
    global DEBUG_ERRORS, DEBUG_ERRNO
    DEBUG_ERRORS = flag
    DEBUG_ERRNO = errno and int(errno)

def set_show_tracebacks(flag=True):
    global SHOW_TRACEBACKS
    SHOW_TRACEBACKS = flag

FAILS = 0
def fail(*args, **keys):
    """logs and counts and failure messages, a test which ran but failed."""
    global FAILS, EOL_PENDING
    FAILS += 1
    if EOL_PENDING: write()
    write(*(("FAILED:[%d]%s: " % (FAILS, logtime()),) + args), **keys)

def failures():
    """Returns count of logged warnings."""
    return FAILS

def increment_failures():
    global FAILS
    FAILS += 1

def status():
    return WARNINGS, ERRORS

def handle_standard_options(
        args, parser=None, usage="usage: %prog [options] <inpaths...>",
        show_info=True, default_outpath=None):
    '''Set some standard options on an optparser object,  many
    of which interplay with the log module itself.
    '''
    if parser is None:
        parser = optparse.OptionParser(usage)
    
    parser.add_option("-o","--outpath",dest="output_dir",
                      help="Path to write tests to.",
                      metavar="OUTPATH", default=default_outpath)

    parser.add_option("-v","--verbose",dest="verbose",
                      help="Set verbose output mode.", action="store_true")

    parser.add_option("-X","--profile",dest="profile",
                      help="Run under the python profiler.",
                      action="store_true", default=False)

    parser.add_option("-Z","--debug-all",dest="debug_all",
                      help="Run under pdb, for stepping everything.",
                      action="store_true", default=False)

    parser.add_option("-d","--debug",dest="debug_errors",
                      help="Debug first logged error in pdb.",
                      action="store_true", default=False)

    parser.add_option("-e","--debug-errno",dest="debug_errno",
                      help="Debug a specific logged error number in pdb.",
                      metavar="ERRNO", default=-1)

    parser.add_option("-t","--show-tracebacks",dest="show_tracebacks",
                      help="Cause error messages to print an exception traceback.",
                      action="store_true", default=False)

    parser.add_option("-l","--log-file",dest="log_file",
                      help="Log output to this file.  Default off.",
                      metavar="LOG_FILE", default="")

    parser.add_option("-a","--log-append",dest="log_append",
                      help="Append to any logfile if it exists already.  Requires -l.  Defaults off.",
                      action="store_true", default=False)

    parser.add_option("-T","--timestamp-log",dest="log_timestamp",
                      help="Add timestamps to log messages.",
                      action="store_true", default=False)

    options, args = parser.parse_args(args)

    set_verbose(options.verbose)
    set_debug_errors(options.debug_errors, options.debug_errno)
    set_show_tracebacks(options.show_tracebacks)
    set_log(options.log_file, options.log_append, options.log_timestamp)

    return options, args

def standard_run(run_str, options, globals_dict, locals_dict, show_info=True):
    """Use options to step run_str, profile run_str,  or just run it."""
    if options.debug_all:
        pdb.runctx(run_str, globals_dict, locals_dict)
    elif options.profile:
        profile.runctx(run_str, globals_dict, locals_dict)
    else:
        try:
            exec run_str in globals_dict, locals_dict
        except DebugBreak:
            exc = sys.exc_info()
            import pdb
            pdb.post_mortem(exc[2])
            
    if show_info:
        info("[%s] done." % (str(datetime.datetime.now())[:-7],), eol="")

def standard_status():
    write(errors(), "errors")
    write(warnings(), "warnings")
    write(infos(), "infos")
    write("")
