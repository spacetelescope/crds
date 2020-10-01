"""This module defines a base class for CRDS command line scripts.

MAYBE integrate rc, environment, and command line parameters.
"""
# -----------------------------------------------------------------------------

import sys
import os
import argparse
import pdb
import cProfile, pstats
import re
from collections import Counter, defaultdict

# -----------------------------------------------------------------------------

from argparse import RawTextHelpFormatter

# -----------------------------------------------------------------------------

from . import log, heavy_client, constants
from . import config, utils, exceptions, rmap
from crds.client import api

# from crds import data_file  :   deferred,  see below

# =============================================================================

def _show_version():
    """Dump CRDS version information and exit python."""
    print(heavy_client.version_info())
    sys.exit(-1)

# =============================================================================

# command line parameter type coercion / verification functions

def dataset(filename):
    """Ensure `filename` names a dataset."""
    from crds import data_file
    if data_file.is_dataset(filename):
        return filename
    else:
        raise ValueError("Parameter", repr(filename),
                         "does not appear to be a dataset filename.")

def reference_file(filename):
    """Ensure `filename` is a reference file."""
    assert config.is_reference(filename), \
        "A reference file is required but got bad type: '%s'" % filename
    return filename

def mapping(filename):
    """Ensure `filename` is a CRDS mapping file."""
    assert config.is_mapping(filename), "A .rmap, .imap, or .pmap file is required but got: '%s'" % filename
    return filename

def mapping_spec(spec):
    """Ensure `spec` is a CRDS mapping specification, a filename or a date based spec."""
    assert config.is_mapping_spec(spec), "A .rmap, .imap, or .pmap file or date base specification is required but got: '%s'" % spec
    return spec

def context_spec(spec):
    """Ensure filename is a .pmap or abstract .pmap like "jwst-edit" or date based context spec."""
    assert config.is_context_spec(spec), \
        "Parameter should be a .pmap or abstract context specifier, not: " + repr(spec)
    return spec

def reference_mapping(filename):
    """Ensure `filename` is a .rmap file."""
    assert filename.endswith(".rmap"), "A .rmap file is required but got: '%s'" % filename
    return filename

#def mapping(filename):
#    """Ensure that `filename` is any known CRDS mapping."""
#    if api.is_known_mapping(filename):
#        return filename
#    else:
#        raise ValueError("Parameter", repr(filename),
#                         "is not a known CRDS mapping.")

def observatory(obs):
    """Verify that `obs` is the name of an observatory and return it."""
    obs = obs.lower()
    assert obs in constants.ALL_OBSERVATORIES, \
        "Unknown observatory " + repr(obs)
    return obs

def nrange(string):
    """Verify a context range expression MIN:MAX and return (MIN, MAX)."""
    assert re.match(r"\d+:\d+", string), \
        "Invalid context range specification " + repr(string)
    rmin, rmax = [int(x) for x in string.split(":")]
    assert 0 <= rmin <= rmax, "Invalid range values"
    return rmin, rmax

def process_key(string):
    """Check the format of a remote process identification  key."""
    assert config.PROCESS_KEY_RE.match(string),  "Invalid format for process key: " + repr(string)
    return string

def user_name(string):
    """Check the format of a server user name string."""
    assert config.USER_NAME_RE.match(string), "Invalid user name " + repr(string)
    return string

# =============================================================================
# =============================================================================

class Script:
    """Base class for CRDS command line scripts with standard properties.

    `args` is either a string of command line parameters or a parameter list of command line words.  If
           defaulted to None then `args` is treated as sys.argv (default argparse handling). Note that `args`
           shoulld include the program name as args[0].  Explicitly specifying `args` is used to
           instantiate a script in code for testing, etc.
    """

    decription = epilog = usage = None
    formatter_class = RawTextHelpFormatter

    def __init__(self, argv=None, parser_pars=None, reset_log=True, print_status=False):
        self.stats = utils.TimingStats()
        self._already_reported_stats = False
        if isinstance(argv, str):
            argv = argv.split()
        elif argv is None:
            argv = sys.argv
        self._argv = argv
        if parser_pars is None:
            parser_pars = {}
        for key in ["description", "epilog", "usage", "formatter_class"]:
            self._add_key(key, parser_pars)
        self.parser = argparse.ArgumentParser(prog=argv[0], **parser_pars)
        self.add_args()
        self.add_standard_args()
        self.args = self.parser.parse_args(argv[1:])
        if self.args.readonly_cache:
            config.set_cache_readonly(True)
        log.set_verbose(log.get_verbose() or self.args.verbosity or self.args.verbose)
        log.set_log_time(config.get_log_time() or self.args.log_time)
        output_cmd = log.info if self.args.dump_cmdline else log.verbose
        output_cmd("Command:", [os.path.basename(argv[0])] + argv[1:], verbosity=30)
        self.print_status = print_status
        self.reset_log = reset_log
        if self.reset_log:
            log.reset()  # reset the infos, warnings, and errors counters as if new commmand line run.
        self._exit_status = None
        self.show_context_resolution = True

    def main(self):
        """Write a main method to perform the actions of the script using self.args."""
        raise NotImplementedError("Script subclasses have to define main().")

    def _main(self):
        """_main() completes any complex generic setup,  like determining contexts, and then
        calls self.main() which does the real work of the script.   _main() defines the full
        call tree of code which is run inside the profiler or debugger.
        """
        self.contexts = self.determine_contexts()
        self._exit_status = self.main()
        self.report_stats()  # here if not called already
        if self.print_status:
            log.standard_status()
        return self._exit_status

    # @data_file.hijack_warnings
    def __call__(self):
        """Run the script's _main() according to command line parameters."""
        try:
            if self.args.debug_traps:
                log.set_exception_trap(False)
            if self.args.version:
                _show_version()
            elif self.args.profile:
                self._profile()
            elif self.args.pdb:
                pdb.runctx("self._main()", globals(), locals())
            else:
                self._main()
        except KeyboardInterrupt as exc:
            if self.args.pdb:
                raise
            else:
                raise KeyboardInterrupt("Interrupted... quitting.") from exc
        return self._exit_status

    @property
    def locator(self):
        """Return the module for observatory specific file locations and plugins functions."""
        return utils.get_locator_module(self.observatory)

    @property
    def obs_pkg(self):
        """Return the package __init__ for observatory specific constants."""
        return utils.get_observatory_package(self.observatory)

    def determine_contexts(self):
        """Return the list of contexts used by this invocation of the script.  Empty for Script."""
        return []

    def add_args(self):
        """Add script-specific argparse add_argument calls here on self.parser"""
        # raise NotImplementedError("Script subclasses have to define add_args().")

    @property
    def readonly_cache(self):
        """Return True of the cache is readonly."""
        return config.get_cache_readonly()

    @property
    @utils.cached
    def observatory(self):
        """Return either the command-line override observatory,  or the one determined
        by the client/server exchange.
        """
        if self.args.jwst:
            return self.set_server("jwst")
        if self.args.hst:
            return self.set_server("hst")
        if self.args.roman:
            return self.set_server("roman")

        obs = config.OBSERVATORY.get()
        if obs != "none":
            return self.set_server(obs.lower())

        url = os.environ.get("CRDS_SERVER_URL", None)
        if url is not None:
            for obs in constants.ALL_OBSERVATORIES:
                if obs in url.lower():
                    return self.set_server(obs)

        files = []
        if hasattr(self, "contexts"):
            files += self.contexts
        if hasattr(self.args, "files"):
            files += self.args.files if self.args.files else []

        for file_ in files:
            if file_.startswith("hst"):
                return self.set_server("hst")
            if file_.startswith("jwst"):
                return self.set_server("jwst")

        for file_ in files:
            with log.verbose_on_exception("Failed file_to_observatory for", repr(file_)):
                return self.set_server(utils.file_to_observatory(file_))

        return api.get_default_observatory()

    @property
    def exit_status(self):
        """Retrieve the script's exit status as it would have been sent to
        sys.exit(...), had the script been run from the commandline."""

        if self._exit_status is None:
            raise RuntimeError("exit_status is not available until script has completed")
        return self._exit_status

    def set_server(self, observatory):
        """Based on `observatory`,  set the CRDS server to an appropriate default,  particularly
        for the case where CRDS_SERVER_URL is not set.
        """
        url = config.get_server_url(observatory)
        if url is not None:
            api.set_crds_server(url)
        return observatory

    def _add_key(self, key, parser_pars):
        """Add any defined class attribute for `key` to dict `parser_pars`."""
        inlined = getattr(self, key, parser_pars)
        if inlined is not None:
            parser_pars[key] = inlined
        return parser_pars

    def add_argument(self, *args, **keys):
        """Add a parser argument."""
        self.parser.add_argument(*args, **keys)

    def get_exclusive_arg_group(self, *args, **keys):
        """Return a mutually exlusive argument group."""
        return self.parser.add_mutually_exclusive_group(*args, **keys)

    def add_standard_args(self):
        """Add standard CRDS command line parameters."""
        self.add_argument("-v", "--verbose",
            help="Set log verbosity to True,  nominal debug level.", action="store_true")
        self.add_argument("--verbosity",
            help="Set log verbosity to a specific level: 0..100.", type=int, default=0)
        self.add_argument("--dump-cmdline", action="store_true",
            help="Dump the command line parameters used to start the script to the log.")
        self.add_argument("-R", "--readonly-cache", action="store_true",
            help="Don't modify the CRDS cache.  Not compatible with options which implicitly modify the cache.")
        self.add_argument('-I', '--ignore-cache', action='store_true', dest="ignore_cache",
                          help="Download required files even if they're already in the cache.")
        self.add_argument("-V", "--version",
            help="Print the software version and exit.", action="store_true")
        self.add_argument("-J", "--jwst", dest="jwst", action="store_true",
            help="Force observatory to JWST for determining header conventions.""")
        self.add_argument("-H", "--hst",  dest="hst", action="store_true",
            help="Force observatory to HST for determining header conventions.""")
        self.add_argument("--roman",  dest="roman", action="store_true",
            help="Force observatory to Roman for determining header conventions.""")
        self.add_argument("--stats", action="store_true",
            help="Track and print timing statistics.")
        self.add_argument("--profile",
            help="Output profile stats to the specified file.", type=str, default="")
        self.add_argument("--log-time", action="store_true",
            help="Add date/time to log messages.")
        self.add_argument("--pdb",
            help="Run under pdb.", action="store_true")
        self.add_argument("--debug-traps",
            help="Bypass exception error message traps and re-raise exception.", action="store_true")

    def print_help(self):
        """Print out command line help."""
        self.parser.print_help()

    def require_server_connection(self):
        """Check a *required* server connection and ERROR/exit if offline."""
        try:
            if not self.server_info.connected:
                raise RuntimeError("Required server connection unavailable.")
        except Exception as exc:
            self.fatal_error("Failed connecting to CRDS server at CRDS_SERVER_URL =",
                             repr(api.get_crds_server()), "::", str(exc))

    @property
    @utils.cached
    def server_info(self):   # see also crds.sync server_info which does not update.
        """Return the server_info dict from the CRDS server *or* cache config for non-networked use where possible."""
        info = heavy_client.get_config_info(self.observatory)
        heavy_client.update_config_info(self.observatory)
        return info

    @property
    @utils.cached
    def bad_files(self):
        """Return the current set of ALL known bad mappings and references, not context-specific."""
        return self.server_info.bad_files_set

    @property
    def default_context(self):
        """Return the default operational .pmap defined by the CRDS server or cache."""
        return self.server_info["operational_context"]

    def get_words(self, word_list):
        """Process a file list,  expanding @-files into corresponding lists of
        files.   Return a flat, depth-first,  file list.
        """
        words = []
        for word in word_list:
            if word.startswith("@"):
                words.extend(self._load_word_list(word[1:]))
            else:
                words.append(word)
        return words # [word.lower() for word in words]

    def _load_word_list(self, at_file):
        """Recursively load an @-file, returning a list of words.
        Any stripped line beginning with # is a comment line to be ignored.
        Any word beginning with @ is a file to load recursively.
        Each line is split into words/words using whitespace.
        """
        words = []
        with open(at_file) as atf:
            for line in atf.readlines():
                word = line.strip()
                if word.startswith("#"):
                    continue
                if word.startswith("@"):
                    more = self._load_word_list(word[1:])
                else:
                    more = word.split()
                words.extend(more)
        return self.get_words(words)   # another pass to fix paths

    def get_files(self, file_list):

        """Expand a list of files by treating any filename beginning with an
        @-sign as a file containing one word per line.
        """
        return self.get_words(file_list)

    @property
    def files(self):
        """Handle @-files and add cache_paths to command line file parameters.
        Nominally self.files are assumed to be references or mappings.  Override locate_file()
        to handle other files.
        """
        if not hasattr(self.args, "files"):
            raise NotImplementedError("Class must implement list of `self.args.files` raw file paths.")
        files1 = self.get_files(self.args.files)
        files2 = []
        for file in files1:
            files2.extend(expand_all_instruments(self.observatory, file))
        return [self.locate_file(fname) for fname in files2]


    #
    # NOTES:
    # crds:// will always mean "inside the cache"
    # ./ will always mean "current directory"
    # pathless files are more ambiguous,  historically in CRDS they mean "in the cache"
    #    but in most/all OSes pathless means "current directory" so concievably could change
    #
    def locate_file(self, filename):
        """Locate file defines how members of the self.args.files list are located.
        The default behavior is to locate CRDS cached files,  either references or mappings.
        This is inappropriate for datasets so in some cases locate_file needs to be overridden.
        Symbolic context names, e.g. hst-operatonal, resolved to literal contexts, e.g. hst_0320.pmap
        """
        filename = config.pop_crds_uri(filename)   # nominally crds://
        filename = self.resolve_context(filename) if config.is_date_based_mapping_spec(filename) else filename
        return config.locate_file(filename, observatory=self.observatory)

    def locate_file_outside_cache(self, filename):
        """This is essentially normal filename syntax,  except crds:// is interpreted to mean
        locate filename inside the CRDS cache.  symbolic context names are also resolved to
        literal context filenames.
        """
        filename2 = config.pop_crds_uri(filename)   # nominally crds://
        filename2 = self.resolve_context(filename2) # e.g. hst-operational -->  hst_0320.pmap
        if filename != filename2:  # Had crds:// or was date based
            return config.locate_file(filename2, self.observatory)
        else:
            if not os.path.dirname(filename2):
                return "./" + filename2
            else:
                return filename2
            # return os.path.abspath(filename2)

    def _profile(self):
        """Run _main() under the Python profiler."""
        if self.args.profile == "console":
            self._console_profile(self._main)
        else:
            cProfile.runctx("self._main()", locals(), locals(), self.args.profile)

    def _console_profile(self, function):
        """Run `function` under the profiler and print results to console."""
        prof = cProfile.Profile()
        prof.enable()
        function()
        prof.disable()
        prof_stats = pstats.Stats(prof).sort_stats("cumulative")
        prof_stats.print_stats(100)

    def report_stats(self):
        """Print out collected statistics."""
        if self.args.stats and not self._already_reported_stats:
            self.stats.report()
            self._already_reported_stats = True

    def increment_stat(self, name, amount=1):
        """Add `amount` to the statistics counter for `name`."""
        self.stats.increment(name, amount)

    def get_stat(self, name):
        """Return statistic `name`."""
        return self.stats.get_stat(name)

    def run(self, *args, **keys):
        """script.run() is the same thing as script() but more explicit."""
        return self.__call__(*args, **keys)

    def resolve_context(self, context):
        """Resolve context spec `context` into a .pmap, .imap, or .rmap filename,  interpreting
        date based specifications against the CRDS server operational context history.
        """
        if isinstance(context, str) and context.lower() == "none":
            return None
        if not config.is_date_based_mapping_spec(context):
            return context
        final_context = heavy_client.get_context_name(self.observatory, context)
        if self.show_context_resolution:
            log.info("Symbolic context", repr(context), "resolves to", repr(final_context))
        return final_context

    def get_conjugates(self, file_list):
        """Given a list of references,  return any GEIS data files associated with them."""
        from crds import data_file
        return [ data_file.get_conjugate(ref) for ref in file_list if data_file.get_conjugate(ref) is not None]

    def get_file_properties(self, filename):
        """Return (instrument, filekind) corresponding to `file`, and '' for none."""
        return utils.get_file_properties(self.observatory, filename)

    def categorize_files(self, filepaths):
        """Organize files in list `filepaths` into a dictionary of lists as follows:
            { (instrument, filekind) : filepath, ... }
        """
        categorized = defaultdict(list)
        for path in filepaths:
            instrument, filekind = self.get_file_properties(path)
            categorized[(instrument, filekind)].append(path)
        return dict(categorized)

    def fatal_error(self, *args, **keys):
        """Issue an error message and terminate the program."""
        log.fatal_error(*args, **keys)

    def dump_files(self, context=None, files=None, ignore_cache=None):
        """Download mapping or reference `files1` with respect to `context`,  tracking stats."""
        if context is None:
            context = self.default_context
        if ignore_cache is None:
            ignore_cache = self.args.ignore_cache
        _localpaths, downloads, nbytes = api.dump_files(
            context, files, ignore_cache=ignore_cache, raise_exceptions=self.args.pdb)
        self.increment_stat("total-files", downloads)
        self.increment_stat("total-bytes", nbytes)

    def dump_mappings(self, mappings, ignore_cache=None):
        """Download all `mappings` and their dependencies if not already cached.."""
        if ignore_cache is None:
            ignore_cache = self.args.ignore_cache
        if not self.server_info.connected:
            log.verbose("Not connected to server. Skipping dump_mappings", mappings, verbosity=55)
            return
        for mapping in mappings:
            _localpaths, downloads, nbytes = api.dump_mappings3(
                mapping, ignore_cache=ignore_cache, raise_exceptions=self.args.pdb)
            self.increment_stat("total-files", downloads)
            self.increment_stat("total-bytes", nbytes)

    def sync_files(self, files, context=None, ignore_cache=None):
        """Like dump_files(),  but dumps recursive closure of any mappings rather than just the listed mapping."""
        mappings = [ os.path.basename(filename)
                     for filename in files if config.is_mapping(filename) ]
        references = [os.path.basename(filename)
                      for filename in files if not config.is_mapping(filename) ]
        if mappings:
            self.dump_mappings(mappings, ignore_cache)
        if references:
            self.dump_files(context, references, ignore_cache)

    def are_all_references(self, files):
        """Return True IFF every file in files is a reference."""
        for filename in files:
            if not config.is_reference(filename):
                return False
        else:
            return True

    def are_all_mappings(self, files):
        """Return True IFF every file in files is a mapping."""
        for filename in files:
            if not config.is_mapping(filename):
                return False
        else:
            return True

# =============================================================================

class UniqueErrorsMixin:
    """This mixin supports tracking certain errors messages."""
    def __init__(self, *args, **keys):

        self.ue_mixin = self.get_empty_mixin()

        # Exception trap context manager for use in "with" blocks
        # trapping exceptions.
        self.error_on_exception = log.exception_trap_logger(
            self.log_and_track_error)  # can be overridden

    def get_empty_mixin(self):
        """Return a bundle of freshly initialized counters and tracking information.   The
        bundle is used to isolate mixin parameters from subclass parameters to prevent
        accidental overrides.
        """
        class Struct:
            pass
        mixin = Struct()
        mixin.messages = {}
        mixin.count = Counter()
        mixin.tracked_errors = 0
        mixin.unique_data_names = set()
        mixin.all_data_names = set()
        mixin.data_names_by_key = defaultdict(list)
        mixin.announce_suppressed = Counter()
        return mixin

    def clear_error_counts(self):
        """Clear the error tracking status by re-initializing/zeroing mixin data structures."""
        self.ue_mixin = self.get_empty_mixin()

    def add_args(self):
        """Add command line parameters to Script arg parser."""
        self.add_argument("--dump-unique-errors", action="store_true",
            help="Record and dump the first instance of each kind of error.")
        self.add_argument("--unique-errors-file",
            help="Write out data names (ids or filenames) for first instance of unique errors to specified file.")
        self.add_argument("--all-errors-file",
            help="Write out all err'ing data names (ids or filenames) to specified file.")
        self.add_argument("--unique-threshold", type=int, default=1,
            help="Only print unique error classes with this many or more instances.")
        self.add_argument("--max-errors-per-class", type=int, default=500, metavar="N",
            help="Only print the first N detailed errors of any particular class.")
        self.add_argument("--unique-delimiter", type=str, default=None,
            help="Use the given delimiter (e.g. semicolon) in tracked error messages to make them amenable to spreadsheets.")

    def log_and_track_error(self, data, instrument, filekind, *params, **keys):
        """Issue an error message and record the first instance of each unique kind of error,  where "unique"
        is defined as (instrument, filekind, msg_text) and omits data id.
        """
        # Always count messages
        self.ue_mixin.tracked_errors += 1
        msg = self.format_prefix(data, instrument, filekind, *params, **keys)
        key = log.format(instrument, filekind.upper(), *params, **keys)
        if key not in self.ue_mixin.messages:
            self.ue_mixin.messages[key] = msg
            self.ue_mixin.unique_data_names.add(data)
        self.ue_mixin.count[key] += 1
        self.ue_mixin.all_data_names.add(data)
        self.ue_mixin.data_names_by_key[key].append(data)
        # Past a certain max,  supress the error log messages.
        if self.ue_mixin.count[key] < self.args.max_errors_per_class:
            log.error(msg)
        else:
            log.increment_errors()
            # Before suppressing,  announce the suppression
            if not self.ue_mixin.announce_suppressed[key]:
                self.ue_mixin.announce_suppressed[key] += 1 # flag
                log.info("Max error count %d exceeded for:" % self.args.max_errors_per_class,
                         key.strip(), "suppressing remaining error messages.")
        return None # for log.exception_trap_logger  --> don't reraise

    def format_prefix(self, data, instrument, filekind, *params, **keys):
        """Create a standard (instrument,filekind,data) prefix for log messages."""
        delim = self.args.unique_delimiter  # for spreadsheets
        data, instrument, filekind = str(data), str(instrument), str(filekind) # squash 2.7 unicode
        if delim:
            return log.format(delim, instrument.upper(), delim, filekind.upper(), delim, data, delim,
                              *params, end="", **keys)
        else:
            return log.format("instrument="+repr(instrument.upper()), "type="+repr(filekind.upper()), "data="+repr(data), ":: ",
                              *params, end="", **keys)

    def dump_unique_errors(self):
        """Print out the first instance of errors recorded by log_and_track_error().  Write out error list files."""
        if self.args.dump_unique_errors:
            if self.args.unique_threshold > 1:
                log.info("Limiting error class reporting to cases with at least",
                         self.args.unique_threshold, "instances.")
            log.info("="*20, "unique error classes", "="*20)
            classes = len(self.ue_mixin.messages)
            for key in sorted(self.ue_mixin.messages):
                if self.ue_mixin.count[key] >= self.args.unique_threshold:
                    log.info("%06d" % self.ue_mixin.count[key], "errors like::", self.ue_mixin.messages[key])
                else:
                    self.drop_error_class(key)
                    classes -= 1
            log.info("All unique error types:", classes)
            log.info("Untracked errors:", log.errors() - self.ue_mixin.tracked_errors)
            log.info("="*20, "="*len("unique error classes"), "="*20)
        if self.args.all_errors_file:
            self.dump_error_data(self.args.all_errors_file, self.ue_mixin.all_data_names)
        if self.args.unique_errors_file:
            self.dump_error_data(self.args.unique_errors_file, self.ue_mixin.unique_data_names)

    def drop_error_class(self, key):
        """Remove the errors classified by `key` from the error classes and counts."""
        for data in self.ue_mixin.data_names_by_key[key]:
            self.ue_mixin.all_data_names = self.ue_mixin.all_data_names - set([data])
            self.ue_mixin.unique_data_names = self.ue_mixin.unique_data_names - set([data])
            self.ue_mixin.count[key] -= 1

    def dump_error_data(self, filename, error_list):
        "Write out list of err'ing filenames or dataset ids to `filename`."""
        with open(filename, "w+") as err_file:
            err_file.write("\n".join(sorted(error_list))+"\n")

# =============================================================================

class ContextsScript(Script):
    """Baseclass for a script proving support for command line specified contexts."""

    def __init__(self, *args, **keys):
        super(ContextsScript, self).__init__(*args, **keys)
        self.contexts = []

    def add_args(self):
        group = self.get_exclusive_arg_group(required=False)
        group.add_argument('--contexts', metavar='CONTEXT', type=mapping_spec, nargs='*',
            help="Specify a list of CRDS mappings to operate on: .pmap, .imap, or .rmap or date-based specification")
        group.add_argument("--range", metavar="MIN:MAX",  type=nrange, dest="range", default=None,
            help='Operate for pipeline context ids (.pmaps) between <MIN> and <MAX>.')
        group.add_argument('--all', action='store_true',
            help='Operate with respect to all known CRDS contexts.')
        group.add_argument('--last-n-contexts', metavar="N", type=int, default=None,
            help='Operate with respect to the last N contexts.')
        group.add_argument("--up-to-context", metavar='CONTEXT', type=mapping_spec, nargs=1, default=None,
            help='Operate on all contexts up to and including the specified context.')
        group.add_argument("--after-context", metavar='CONTEXT', type=mapping_spec, nargs=1, default=None,
            help='Operate on all contexts after and including the specified context.')

        self.add_argument('--include-orphans', action='store_true',
            help='Include reference files not mentioned by any contexts.')

    def determine_contexts(self):
        """Support explicit specification of contexts, context id range, or all."""
        log.verbose("Determining contexts.", verbosity=55)
        if self.args.contexts:
            # permit instrument and reference mappings,  not just pipelines:
            _contexts2 = []
            for ctx in self.args.contexts:
                _contexts2.extend(expand_all_instruments(self.observatory, ctx))
            contexts = []
            for ctx in _contexts2:
                resolved = self.resolve_context(ctx)
                if resolved != 'N/A':
                    contexts.append(resolved)
        elif self.args.all:
            contexts = self._list_mappings("*.pmap")
        elif self.args.last_n_contexts:
            contexts = self._list_mappings("*.pmap")[-self.args.last_n_contexts:]
        elif self.args.range:
            rmin, rmax = self.args.range
            contexts = []
            all_contexts = self._list_mappings("*.pmap")
            for context in all_contexts:
                match = re.match(r"\w+_(\d+).pmap", context)
                if match:
                    serial = int(match.group(1))
                    if rmin <= serial <= rmax:
                        contexts.append(context)
        elif self.args.up_to_context:
            pmaps = self._list_mappings("*.pmap")
            with log.augment_exception("Invalid --up-to-context", repr(self.args.up_to_context[0]), exc_class=exceptions.CrdsError):
                up_to_context = self.resolve_context(self.args.up_to_context[0])
                up_to_ix = pmaps.index(up_to_context)+1
                contexts = pmaps[:up_to_ix]
        elif self.args.after_context:
            pmaps = self._list_mappings("*.pmap")
            with log.augment_exception("Invalid --after-context", repr(self.args.after_context[0]), exc_class=exceptions.CrdsError):
                after_context = self.resolve_context(self.args.after_context[0])
                after_ix = pmaps.index(after_context)
                contexts = pmaps[after_ix:]
        elif config.get_crds_env_context():
            contexts = [self.resolve_context(config.get_crds_env_context())]
        else:
            contexts = [self.resolve_context(self.observatory + "-operational")]
        log.verbose("Determined contexts: ", contexts, verbosity=55)
        return sorted(contexts)

    def _list_mappings(self, glob_pattern="*.pmap"):
        """Return a list of all the .pmap's on the CRDS Server."""
        self.require_server_connection()
        return heavy_client.list_mappings(self.observatory, glob_pattern)

    def _list_references(self, glob_pattern="*"):
        self.require_server_connection()
        return api.list_references(self.observatory, glob_pattern)

    def _orphan_references(self):
        """Return the set of reference files which exist the CRDS catalog but
        which cannot be found within the reference files referred to by any .pmap.
        """
        all_references = self._list_references()
        all_references = set(all_references)
        all_pmaps = self._list_mappings("*.pmap")
        pmap_references = self._get_context_references(all_pmaps)
        return set(all_references - pmap_references)

    def dump_files(self, context, files=None, ignore_cache=None):
        """Download mapping or reference `files1` with respect to `context`,  tracking stats."""
        if ignore_cache is None:
            ignore_cache = self.args.ignore_cache
        _localpaths, downloads, nbytes = api.dump_files(
            context, files, ignore_cache=ignore_cache, raise_exceptions=self.args.pdb)
        self.increment_stat("total-files", downloads)
        self.increment_stat("total-bytes", nbytes)

    def get_context_mappings(self):
        """Return the list of mappings which are pointed to by the mappings in `self.contexts`.

        If --all was specified,  include orphan mappings not reachable from any .pmap.
        """
        if not self.contexts:
            return []
        log.verbose("Getting all mappings for specified contexts.", verbosity=55)
        if self.args.all:
            mappings = self._list_mappings("*.*map")
            with log.verbose_warning_on_exception("Downloading all mappings failed"):
                self.dump_files(self.default_context, mappings)
        else:
            mappings = self.contexts

        useable_contexts, mapping_closure = self._dump_and_vet_mappings(mappings)
        self.contexts = useable_contexts   # XXXX reset self.contexts
        log.verbose("Got mappings from specified (usable) contexts: ", self.contexts, verbosity=55)

        return mapping_closure

    def _dump_and_vet_mappings(self, mappings):
        """Ensure all mapping files listed in `mappings` are in the CRDS cache.

        Returns  (list(useable_contexts), list(mappings_closures))
        """
        log.verbose("Getting and checking specified mappings.", verbosity=55)

        # Based on the specified mappings,  identify the  mappings they refer to
        mapping_closure = set()
        for mapping in mappings:
            with log.warn_on_exception("Failed loading context", repr(mapping)):
                try:
                    loadable = rmap.get_cached_mapping(mapping)
                    loadable_names = loadable.mapping_names()
                except Exception as exc:
                    log.verbose("Failed loading", repr(mapping),
                                "using API call to get mapping names", str(exc))
                    loadable_names = api.get_mapping_names(mapping)
                mapping_closure |= set(loadable_names)

        # Dump all missing files in one call
        with log.verbose_warning_on_exception("Mapping closure download failed"):
            self.dump_files(self.default_context, mapping_closure)

        # After attempting to sync,  identify which mappings are actually loadable now.
        useable_contexts = []
        for mapping in mappings:
            with log.warn_on_exception("Failed loading", repr(mapping)):
                _loaded = rmap.get_cached_mapping(mapping)
                useable_contexts.append(mapping)

        return sorted(useable_contexts), sorted(mapping_closure)

    def _get_context_references(self, mappings=None):
        """Return the set of references which are pointed to by the mappings in `mappings`
        or self.get_context_mappings() when mappings is None.
        """
        references = set()
        mappings = self.get_context_mappings() if mappings is None else mappings
        for context in mappings:
            try:
                pmap = rmap.get_cached_mapping(context)
                references |= set(pmap.reference_names())
                log.verbose("Determined references from cached mapping", repr(context))
            except Exception:  # only ask the server if loading context fails
                log.verbose("Determined references from CRDS server service", repr(context))
                references |= set(api.get_reference_names(context))
        return references

    def get_context_references(self):
        """Return the sorted list of references defined by the closure of the specified
        contexts.   If --include-orphans was specified,  also include reference files
        from the CRDS catalog which do not appear in any .pmap.
        """
        references = self._get_context_references(self.contexts)
        if self.args.include_orphans:
            references |= self._orphan_references()
        return sorted(list(references))

def expand_all_instruments(observatory, context):
    """Expand symbolic context specifiers for rmaps with "all" for instrument
    into the list of rmaps for every instrument in the related context (e.g. edit or operational).

    e.g.  jwst-all-photom-operational -->  [jwst-miri-photom-operational, jwst-nircam-photom-operational, ...]

    Expansion of "all" is determined by instruments in e.g. jwst-operational
    """
    mtch = config.CONTEXT_RE.match(context)
    if mtch and mtch.group("instrument") == "all":
        root_context = observatory + "-" + mtch.group("date")
        pmap = heavy_client.get_symbolic_mapping(root_context)
        observatory = mtch.group("observatory")
        filekind = mtch.group("filekind")
        date = mtch.group("date")
        all_maps = [ "-".join([observatory, instrument, filekind, date])
                for instrument in pmap.selections.keys() if instrument != "system"]
    else:
        all_maps = [context]
    return all_maps
