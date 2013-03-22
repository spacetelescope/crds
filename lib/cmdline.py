"""This module defines a base class for CRDS command line scripts.

MAYBE integrate rc, environment, and command line parameters.
"""
import sys
import argparse
import pdb
import cProfile as profile
import re

from argparse import RawTextHelpFormatter

from crds import rmap, log, data_file, heavy_client
from crds.client import api

# =============================================================================

def _show_version():
    """Dump CRDS version information and exit python."""
    import crds, crds.svn_version
    log.info("crds version", crds.__version__, "revision", crds.svn_version.__svn_version__)
    sys.exit(-1)

# =============================================================================

# command line parameter type coercion / verification functions

def dataset(filename):
    """Ensure `filename` names a dataset."""
    if data_file.is_dataset(filename):
        return filename
    else:
        raise ValueError("Parameter " + repr(filename) + " does not appear to be a dataset filename.")

def reference_file(filename):
    """Ensure `filename` is a reference file."""
    assert filename.endswith((".fits", ".finf")), "A .fits or .finf file is required but got: '%s'" % filename
    return filename

def mapping(filename):
    """Ensure `filename` is a CRDS mapping file."""
    assert rmap.is_mapping(filename), "A .rmap, .imap, or .pmap file is required but got: '%s'" % filename
    return filename

def pipeline_mapping(filename):
    """Ensure `filename` is a .pmap file."""
    assert filename.endswith(".pmap"), "A .pmap file is required but got: '%s'" % filename
    return filename

def instrument_mapping(filename):
    """Ensure `filename` is a .imap file."""
    assert filename.endswith(".imap"), "A .imap file is required but got: '%s'" % filename
    return filename

def reference_mapping(filename):
    """Ensure `filename` is a .rmap file."""
    assert filename.endswith(".rmap"), "A .rmap file is required but got: '%s'" % filename
    return filename

#def mapping(filename):
#    """Ensure that `filename` is any known CRDS mapping."""
#    if api.is_known_mapping(filename):
#        return filename
#    else:
#        raise ValueError("Parameter " + repr(filename) + " is not a known CRDS mapping.")

def observatory(obs):
    """Verify that `obs` is the name of an observatory and return it."""
    obs = obs.lower()
    assert obs in ["hst", "jwst", "tobs"], "Unknown observatory " + repr(obs)
    return obs

def nrange(string):
    """Verify a context range expression MIN:MAX and return (MIN, MAX)."""
    assert re.match(r"\d+:\d+", string), \
        "Invalid context range specification " + repr(string)
    rmin, rmax = [int(x) for x in string.split(":")]
    assert 0 <= rmin <= rmax, "Invalid range values"
    return rmin, rmax
    

# =============================================================================

class Script(object):
    """Base class for CRDS command line scripts with standard properties."""
    
    decription = epilog = usage = None
    formatter_class = RawTextHelpFormatter
    
    def __init__(self, **parser_pars):
        self._server_info = None
        for key in ["description", "epilog", "usage", "formatter_class"]: 
            self._add_key(key, parser_pars)
        if "--version" in sys.argv:   # hack this since it's non-standard.
            _show_version()
        self.parser = argparse.ArgumentParser(**parser_pars)
        self.add_args()
        self.add_standard_args()
        self.args = self.parser.parse_args()
        log.set_verbose(self.args.verbosity or self.args.verbose)
        
    def main(self):
        """Write a main method to perform the actions of the script using self.args."""
        raise NotImplementedError("Script subclasses have to define main().")
        
    def add_args(self):
        """Add script-specific argparse add_argument calls here on self.parser"""
        raise NotImplementedError("Script subclasses have to define add_args().")
    
    @property
    def observatory(self):
        """Return either the command-line override observatory,  or the one determined
        by the client/server exchange.
        """
        if self.args.jwst:
            obs = "jwst"
            assert not self.args.hst, "Can only specify one of --hst or --jwst"
        elif self.args.hst:
            obs = "hst"
            assert not self.args.jwst, "Can only specify one of --hst or --jwst"
        else:
            obs = api.get_default_observatory()
        return obs
        
    def _add_key(self, key, parser_pars):
        """Add any defined class attribute for `key` to dict `parser_pars`."""
        inlined = getattr(self, key, parser_pars)
        if inlined is not None:  
            parser_pars[key] = inlined
        return parser_pars
    
    def add_argument(self, *args, **keys):
        """Add a parser argument."""
        self.parser.add_argument(*args, **keys)

    def add_standard_args(self):
        """Add standard CRDS command line parameters."""
        self.add_argument("-v", "--verbose", 
            help="Set log verbosity to True,  nominal debug level.", action="store_true")
        self.add_argument("--verbosity", 
            help="Set log verbosity to a specific level: 0..100.", type=int, default=0)
        self.add_argument("-J", "--jwst", dest="jwst", action="store_true",
            help="Force observatory to JWST for determining header conventions.""")
        self.add_argument("-H", "--hst",  dest="hst", action="store_true",
            help="Force observatory to HST for determining header conventions.""")
        self.add_argument("--profile", 
            help="Output profile stats to the specified file.", type=str, default="")
        self.add_argument("--pdb", 
            help="Run under pdb.", action="store_true")
    
    def test_server_connection(self):
        """Check the server connection and remember the server_info."""
        connected, server_info = heavy_client.get_config_info(self.observatory)
        if not connected:
            log.error("Failed connecting to CRDS server at", repr(api.get_crds_server()))
            sys.exit(-1)
        return server_info
            
    @property
    def server_info(self):
        """Return the server_info dict from the CRDS server."""
        if self._server_info is None:
            self._server_info = self.test_server_connection()
        return self._server_info

    @property
    def default_context(self):
        """Return the default operational .pmap defined by the CRDS server or cache."""
        return self.server_info["operational_context"]

    def get_files(self, file_list):
        """Process a file list,  expanding @-files into corresponding lists of
        files.   Return a flat, depth-first,  file list.
        """
        files = []
        for fname in file_list:
            if fname.startswith("@"):
                files.extend(self.load_file_list(fname[1:]))
            else:
                files.append(fname)
        return files
    
    def load_file_list(self, at_file):
        """Recursively load an @-file, returning a list of words/files.
        Any stripped line beginning with # is a comment line to be ignored.
        Any word beginning with @ is a file to load recursively.
        Each line is split into words/files using whitespace.
        """
        files = []
        with open(at_file) as atf:
            for line in atf.readlines():
                fname = line.strip()
                if fname.startswith("#"):
                    continue
                if fname.startswith("@"):
                    more = self.load_file_list(fname[1:])
                else:
                    more = fname.split()
                files.extend(more)
        return self.get_files(files)   # another pass to fix paths

    @property
    def files(self):
        """Handle @-files and add cache_paths to command line file parameters.""" 
        if not hasattr(self.args, "files"):
            raise NotImplementedError("Class must implement list of `self.args.files` raw file paths.")
        return [rmap.locate_file(fname, observatory=self.observatory) 
                    for fname in self.get_files(self.args.files)]

    def __call__(self):
        """Run the script's main() according to command line parameters."""
        if self.args.profile:
            profile.runctx("self.main()", locals(), locals(), self.args.profile)
        elif self.args.pdb:
            pdb.runctx("self.main()", locals(), locals())
        else:
            self.main()

# =============================================================================

class ContextsScript(Script):
    """Baseclass for a script proving support for command line specified contexts."""
    
    def __init__(self, *args, **keys):
        super(ContextsScript, self).__init__(*args, **keys)
        self._contexts = None

    def add_args(self):
        self.add_argument('--contexts', metavar='CONTEXT', type=mapping, nargs='*',
            help="Specify a list of .pmap's.")        
        self.add_argument('--all', action='store_true',
            help='Operate with respect to all known contexts.')
        self.add_argument("--range", metavar="MIN:MAX",  type=nrange, dest="range", default=None,
            help='Fetch files for pipeline context ids between <MIN> and <MAX>.')

    @property
    def contexts(self):
        """Return a list of contexts defined by the command line parameters."""
        if self._contexts is None:
            self._contexts = self.determine_contexts()
        return self._contexts

    def determine_contexts(self):
        """Support explicit specification of contexts, context id range, or all."""
        args = self.args
        all_contexts = api.list_mappings(glob_pattern="*.pmap")
        if args.contexts:
            assert not args.range, 'Cannot specify explicit contexts and --range'
            assert not args.all, 'Cannot specify explicit contexts and --all'
            # permit instrument and reference mappings,  not just pipelines:
            all_contexts = api.list_mappings(glob_pattern="*.*map")
            for context in args.contexts:
                assert context in all_contexts, "Unknown context " + repr(context)
            contexts = args.contexts
        elif args.all:
            assert not args.range, "Cannot specify --all and --range"
            contexts = all_contexts
        elif args.range:
            rmin, rmax = args.range
            contexts = []
            for context in all_contexts:
                match = re.match(r"\w+_(\d+).pmap", context)
                if match:
                    serial = int(match.group(1))
                    if rmin <= serial <= rmax:
                        contexts.append(context)
        else:
            contexts = []
        return sorted(contexts)
    
    def get_context_mappings(self):
        """Return the set of mappings which are pointed to by the mappings
        in `contexts`.
        """
        files = set()
        for context in self.contexts:
            pmap = rmap.get_cached_mapping(context)
            files = files.union(pmap.mapping_names())
        return sorted(files)
    
    def get_context_references(self):
        """Return the set of mappings which are pointed to by the mappings
        in `contexts`.
        """
        files = set()
        for context in self.contexts:
            files = files.union(api.get_reference_names(context))
        return sorted(files)

    def main(self):
        """Write a main method to perform the actions of the script using self.args."""
        raise NotImplementedError("ScriptWithContexts subclasses have to define main().")
        
