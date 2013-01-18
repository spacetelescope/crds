"""This module defines a base class for CRDS command line scripts.

MAYBE integrate rc, environment, and command line parameters.
"""

import argparse
import pdb
import cProfile as profile

from crds import log

class Script(object):
    """Base class for CRDS command line scripts with standard properties."""
    
    decription = epilog = usage = None
    
    def __init__(self, **parser_pars):
        for key in ["description", "epilog", "usage"]: 
            self._add_key(key, parser_pars)
        self.parser = argparse.ArgumentParser(**parser_pars)
        self.parser.add_argument("-v", "--verbose", help="Set log verbosity to True,  nominal debug level.", action="store_true")
        self.parser.add_argument("--verbosity", help="Set log verbosity to a specific level: 0..100.", type=int, default=0)
        self.parser.add_argument("--profile", help="Output profile stats to the specified file.", type=str, default="")
        self.parser.add_argument("--pdb", help="Run under pdb.", action="store_true")
        self.add_args()
        self.args = self.parser.parse_args()
        log.set_verbose(self.args.verbosity or self.args.verbose)
    
    def _add_key(self, key, parser_pars):
        """Add any defined class attribute for `key` to dict `parser_pars`."""
        inlined = getattr(self, key, parser_pars)
        if inlined is not None:  
            parser_pars[key] = inlined
        return parser_pars

    def add_args(self):
        """Add additional argparse add_argument calls here on self.parser"""
        
    def __call__(self):
        """Run the script's main() according to command line parameters."""
        if self.args.profile:
            profile.runctx("self.main()", locals(), locals())
        elif self.args.pdb:
            pdb.runctx("self.main()", locals(), locals())
        else:
            self.main()

    def main(self):
        """Write a main method to perform the actions of the script using self.args."""
    