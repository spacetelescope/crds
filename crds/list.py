"""This module is a command line script which lists the reference and/or
mapping files associated with the specified contexts by consulting the CRDS
server.   More generally it's for printing out information on CRDS files.
"""
from __future__ import print_function

from crds import cmdline, rmap

class ListScript(cmdline.ContextsScript):
    """Command line script for listing information about CRDS reference and mapping files."""

    description = """Command line script for listing information about CRDS reference and mapping files."""
        
    epilog = """    
    Contexts to list can be specified explicitly:
    
    % python -m crds.list  --contexts hst_0001.pmap hst_0002.pmap --references
    vb41935ij_bia.fits 
    vb41935kj_bia.fits 
    ...
    
    Contexts to list can be specified as a range:
    
    % python -m crds.list --range 1:2 --references
    vb41935lj_bia.fits 
    vb41935oj_bia.fits
    ...
    
    Contexts to list can be specified as --all contexts:
    
    % python -m crds.list --all --mappings
    hst.pmap 
    hst_0001.pmap 
    hst_0002.pmap 
    hst_acs.imap 
    hst_acs_0001.imap 
    hst_acs_0002.imap 
    hst_acs_atodtab.rmap 
    ...
    
    The paths of locally cached mappings (files already synced to your computer) can be listed:
    
    % python -m crds.list --cached-mappings
    
    The paths of locally cached references (files already synced to your computer) can be listed:
    
    % python -m crds.list --cached-references
    """
    
    def add_args(self):
        self.add_argument('--references', action='store_true', dest="list_references",
            help='print names of reference files referred to by contexts')
        self.add_argument('--mappings', action='store_true', dest="list_mappings",
            help='print names of mapping files referred to by contexts')
        self.add_argument("--cached-references", action="store_true",
            help="prints out the paths of all references in the local cache.")
        self.add_argument("--cached-mappings", action="store_true",
            help="prints out the paths of all mappings in the local cache.")
        self.add_argument("--full-path", action="store_true",
            help="prints out the full paths of files for --cached-references and --cached-mappings.""")
        super(ListScript, self).add_args()
        
    def main(self):
        """List files."""
        if self.args.list_references:
            self.list_references()
        if self.args.list_mappings:
            self.list_mappings()
        if self.args.cached_references:
            self.list_cached_references()
        if self.args.cached_mappings:
            self.list_cached_mappings()

    def list_references(self):
        """Consult the server and print the names of all references associated with
        the given contexts.
        """
        _print_list(self.get_context_references())
    
    def list_mappings(self):
        """Consult the server and print the names of all CRDS mappings associated 
        with the given contexts.
        """
        _print_list(self.get_context_mappings())
    
    def list_cached_mappings(self):
        """List the mapping paths in the local cache."""
        _print_list(rmap.list_mappings("*.*map", self.observatory, full_path=self.args.full_path))
        
    def list_cached_references(self):
        """List the reference paths in the local cache."""
        _print_list(rmap.list_references("*", self.observatory, full_path=self.args.full_path))
    
def _print_list(files):
    """Print `files` one file per line."""
    for filename in files:
        print(filename)

if __name__ == "__main__":
    ListScript()()
