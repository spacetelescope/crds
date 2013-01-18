"""This module defines a base class for CRDS command line scripts.

MAYBE integrate rc, environment, and command line parameters.
"""
import sys
import argparse
import pdb
import cProfile as profile

from argparse import RawTextHelpFormatter

from crds import log

# =============================================================================

def _show_version():
    """Dump CRDS version information and exit python."""
    import crds, crds.svn_version
    log.info("crds version", crds.__version__, "revision", crds.svn_version.__svn_version__)
    sys.exit(-1)

# =============================================================================

class Script(object):
    
    """Base class for CRDS command line scripts with standard properties."""
    
    decription = epilog = usage = None
    formatter_class = RawTextHelpFormatter
    
    def __init__(self, **parser_pars):
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
        
    def add_args(self):
        """Add script-specific argparse add_argument calls here on self.parser"""
    
    def get_observatory(self, filename=None):
        """Determine the observatory corresponding to the differenced files."""
        observatory = "jwst"
        if self.args.jwst:
            observatory = "jwst"
            assert not self.args.hst, "Can only specify one of --hst or --jwst"
        elif self.args.hst:
            observatory = "hst"
            assert not self.args.jwst, "Can only specify one of --hst or --jwst"
        elif filename is not None:
            if "hst_" in filename:
                observatory = "hst"
            elif "jwst_" in filename:
                observatory = "jwst"
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

    def add_standard_args(self):
        """Add standard CRDS command line parameters."""
        self.add_argument("-v", "--verbose", help="Set log verbosity to True,  nominal debug level.", action="store_true")
        self.add_argument("--verbosity", help="Set log verbosity to a specific level: 0..100.", type=int, default=0)
        self.add_argument("-J", "--jwst", 
            help="Force observatory to JWST for determining header conventions.""",
            action="store_true")
        self.add_argument("-H", "--hst", 
            help="Force observatory to HST for determining heder conventions.""",
            action="store_true")
        self.add_argument("--profile", help="Output profile stats to the specified file.", type=str, default="")
        self.add_argument("--pdb", help="Run under pdb.", action="store_true")

    def __call__(self):
        """Run the script's main() according to command line parameters."""
        if self.args.profile:
            profile.runctx("self.main()", locals(), locals(), self.args.profile)
        elif self.args.pdb:
            pdb.runctx("self.main()", locals(), locals())
        else:
            self.main()
    