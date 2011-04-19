#! /usr/bin/env python

"""pysh is syntactic sugar which simplifies using the Python
subprocess module for writing command line utility scripts that one
might ordinarily write in a UNIX shell, .e.g. bash, ksh, or csh.  One
of my dirty secrets is that I can no longer remember the little I ever
knew of bash and csh.  A second dirty secret is that shellscript still
lures me back with it's simplicity...  but then breaks down as my
scripts get more complicated.  pysh is for those times when I want to
quickly write what I would type on the command line, but find myself
struggling to learn or remember the more cryptic syntax of shells.
So, shellscript can be very terse, but seems increasingly ugly as
applications grow beyond a few lines.

While the subprocess module provides a flexible basis for launching
other programs in a wide variety of contexts, it does lack the
simplicity of shell script for basic tasks.  Pysh is simple sugar
intended to glue a limited subset of shell script into Python.

Taking from the shellscript example of the subprocess module
implementation illustrates what pysh is really about:

First,  shellscript might look like this:

   output=`dmesg | grep hda`

This shellscript can be translated into Python subprocess module code
like this:

   p1 = Popen(["dmesg"], stdout=PIPE)
   p2 = Popen(["grep", "hda"], stdin=p1.stdout, stdout=PIPE)
   output = p2.communicate()[0]

But using pysh,  built upon the subprocess module,  one would say this:

   output = out("dmesg | grep hda")

The real advantage of pysh comes into play when control flow
constructs such as if-then-else, for, and while come into play, let
alone any of the more powerful features of Python such as modules,
classes, functions, lists, mappings, sets, strings, exception handling,
etc.
"""

# =========================================================================

import sys
import os
import re
import glob
import os.path
import cStringIO

import select
import subprocess
from subprocess import PIPE, STDOUT, Popen

# =========================================================================

__all__ = [
    "sys", "os", "re", "glob",

    "sh", "out", "err", "out_err", "status", "words", "lines",

    "Shell", "pysh_execfile"
]

# =========================================================================

# XXX support multi-line command input


class SubprocessFailure(RuntimeError):
    pass

# =========================================================================

class Shell:
    def __init__(self, args, **keys):

        self._context = keys.pop("context", None)
        self._input = keys.pop("input", None)
        capture_output = keys.pop("capture_output", False)
        independent_error = keys.pop("independent_error", False)

        if self._context is None:    
            # subclasses, were there any,  would need to pass this in
            # when calling __init__ from the subclass since it would
            # change the depth of the stack and invalidate the below.
            self._context = _context(1)  
        # print "shell:", repr(self._context)

        args = self._handle_args(args)
        # print "shell:", repr(args)

        if capture_output:
            if independent_error:
                self._popen = Popen(
                    args, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, **keys)
            else:                
                self._popen = Popen(
                    args, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, **keys)
        else:
            # The real utility of this branch is when you want to see
            # output on your terminal like an ordinary shellscript.
            # The downside is that output is no longer captured.
            self._popen = Popen(args, shell=True, stdin=PIPE, **keys)

        self._args = args
        self._keys = keys
        self.out  = "" # string results stdout, stderr
        self.err  = ""   

    def _handle_args(self, args):
        if isinstance(args, str):
            args = [args]
        else:
            args = list(args)
        for i,a in enumerate(args):
            args[i] = expand_vars(a, self._context)
        return args

    def __call__(self, raise_on_error):
        self.out, self.err = self._popen.communicate(self._input)
        self.status = self._popen.returncode
        if raise_on_error and self._popen.returncode:
            raise SubprocessFailure("status = " + str(self._popen.returncode))
        else:
            return self._popen.returncode

    def __repr__(self):
        return "Shell(%s, %s)" % (repr(self._args, self._keys),)

# =========================================================================

# handle peeking back up the call tree into the caller's namespace so that
# caller variable names can be substituted using ${} notation.  Also handle
# command line parameters using $* and $1, etc.

def _context(n):
    """Peek back up the call tree into the namespace of the caller.  Return
    a namespace dictionary combining his globals and locals.  `n` is the number
    of stack frames to back up relative to the caller of _context().
    """
    frame = sys._getframe(n+1)
    c = dict()
    c.update(os.environ)
    # c.update(frame.f_builtins)
    c.update(frame.f_globals)
    c.update(frame.f_locals)
    return c

# This could also be made to handle simple $N sys.argv
ENV_VAR = re.compile("[$]([a-zA-Z_0-9]+)")
ENV_VAR_NUM = re.compile("[$]([0-9]+)")
ENV_VAR_CURLY = re.compile("[$]{([a-zA-Z_0-9]+)}")
ENV_VAR_STAR = re.compile("([$][*])")

def _replace_dollar(match):
    return "%(" + match.group(1) + ")s"

def _replace_sysarg(match):
    return sys.argv[int(match.group(1))]

def _replace_star(match):
    return " ".join(sys.argv[1:])

def _env_to_percent_var(s):
    s = ENV_VAR_NUM.sub(_replace_sysarg, s)
    s = ENV_VAR_STAR.sub(_replace_star, s)
    s = ENV_VAR.sub(_replace_dollar, s)
    return ENV_VAR_CURLY.sub(_replace_dollar, s)

def expand_vars(string, context=None):
    if context is None:
        context = _context(2)
    return _env_to_percent_var(string) % context

# =========================================================================

def sh(command, **keys):
    """Run a subprogram,  inheriting stdout and stderr from the calller, and
    return the program exit status.  Output is not captured.
    If raise_on_error is True,  raise an exception on non-zero program exit.
    """
    s = Shell(command, context=_context(1), capture_output=False)
    s(keys.pop("raise_on_error", False))
    return s.status

def _captured_output(command, **keys):
    s = Shell(command, context=_context(2), capture_output=True, 
              independent_error=keys.pop("independent_error", True))
    s(keys.pop("raise_on_error", False))
    return s

def status(command, **keys):
    """Run a subprogram capturing it's output and return the exit status."""
    return _captured_output(command, **keys).status

def out(command, **keys):
    """Run a subprogram and return it's stdout."""
    return _captured_output(command, **keys).out

def err(command, **keys):
    """Run a subprogram and return it's stderr."""
    return _captured_output(command, **keys).err

def out_err(command, **keys):
    """Run a subprogram and return it's interleaved stdout and stderr."""
    keys["independent_error"] = False
    return _captured_output(command, **keys).out

def words(command, **keys):
    """Return the standard output of `command` split into a sequence
    of words.
    """
    return out(command, **keys).split()

def lines(command, **keys):
    """Return the standard output of `command` split into a sequence
    of lines.
    """
    # keys["independent_error"] = False
    return cStringIO.StringIO(_captured_output(command, **keys).out).readlines()

# =========================================================================

# Convenience routines not related to subprocesses here.

def cd(directory):
    os.chdir(directory)

def fail(*args, **keys):
    """Quit the program,  issuing a message which is the join of *args.
    Use keyword `status` as the program exit code or -1 if unspecified.
    """
    print >>sys.stderr, " ".join(args)
    sys.exit(keys.pop("status", -1))

def usage(description, min_args, max_args=sys.maxint):
    """Emit a standard program usage message based on the min and max
    command line parameter counts.   If the program takes at least
    one parameter,  min_args should be 1.   If the program takes at most
    one parameter, max_args should also be 1.
    """
    progname = os.path.split(sys.argv[0])[1]
    if not (min_args <= len(sys.argv)-1 <= max_args):
        fail("usage: " + progname + " "  + description)

# =========================================================================

# Code for rewriting a file of pysh-script as an ordinary python module.

def __rewrite_shell_statement(match):
    return match.group(1) + "sh('''" + match.group(2) + "''')"

SHELL_STATEMENT = re.compile("^(\s*)% (.*)$")

def _rewrite_shell_statement(line):
    return SHELL_STATEMENT.sub(__rewrite_shell_statement, line)

def pysh_execfile(fname, globals=None, locals=None):
    """Handle special pysh-notations
    """
    import tempfile
    lines =  open(fname).readlines()
    for i, l in enumerate(lines):
        lines[i] = _rewrite_shell_statement(l)
    (handle, fname) = tempfile.mkstemp()
    for l in lines:
        os.write(handle, l)
    try:
        execfile(fname, globals, locals)
    finally:
        os.remove(fname)

# =========================================================================

# The execution sequence for when pysh is used as a program shell.

if __name__ == "__main__":
    if len(sys.argv) > 1:
        sys.argv = sys.argv[1:]
        pysh_execfile(sys.argv[0], globals(), locals())
    else:
        print >>sys.stderr, "usage: pysh <pysh-scriptname>"
