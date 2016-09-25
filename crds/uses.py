"""uses.py defines functions which will list the files which use a given 
reference or mapping file.

>>> from pprint import pprint as pp
>>> pp(findall_mappings_using_reference("v2e20129l_flat.fits"))
['hst.pmap',
 'hst_0001.pmap',
 'hst_0002.pmap',
 'hst_0003.pmap',
 'hst_0004.pmap',
 'hst_0005.pmap',
 'hst_0006.pmap',
 'hst_cos.imap',
 'hst_cos_0001.imap',
 'hst_cos_flatfile.rmap',
 'hst_cos_flatfile_0002.rmap']
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import os.path

import crds
from . import pysh, config, cmdline, utils, log
from crds.client import api

def _clean_file_lines(files):
    """Return simple filenames from paths in `files`, ignoring error messages."""
    files = [os.path.basename(f.strip()) for f in files]
    return  [f for f in files if config.FILE_RE.match(str(f))]

def findall_rmaps_using_reference(filename, observatory="hst"):
    """Return the basename of all reference mappings which mention `filename`."""
    config.check_filename(filename) # x
    mapping_path = config.get_path("test.pmap", observatory)  # x
    rmaps = pysh.lines("find ${mapping_path} -name '*.rmap' | xargs grep -l ${filename}", raise_on_error=False) # secure
    return _clean_file_lines(rmaps)

def findall_imaps_using_rmap(filename, observatory="hst"):
    """Return the basenames of all instrument contexts which mention `filename`."""
    mapping_path = config.get_path("test.pmap", observatory)
    config.check_filename(filename)
    imaps = pysh.lines("find ${mapping_path} -name '*.imap' | xargs grep -l ${filename}", raise_on_error=False)  # secure
    return _clean_file_lines(imaps)

def findall_pmaps_using_imap(filename, observatory="hst"):
    """Return the basenames of all pipeline contexts which mention `filename`."""
    mapping_path = config.get_path("test.pmap", observatory)
    config.check_filename(filename)
    pmaps = pysh.lines("find ${mapping_path} -name '*.pmap' | xargs grep -l ${filename}", raise_on_error=False)  #secure
    return _clean_file_lines(pmaps)

def findall_mappings_using_reference(reference, observatory="hst"):
    """Return the basenames of all mapping files in the hierarchy which
    mentions reference `reference`.
    """
    mappings = []
    for rmap in findall_rmaps_using_reference(reference, observatory):
        mappings.append(rmap)
        for imap in findall_imaps_using_rmap(rmap, observatory):
            mappings.append(imap)
            for pmap in findall_pmaps_using_imap(imap, observatory):
                mappings.append(pmap)
    return sorted(list(set(mappings)))

def findall_mappings_using_rmap(rmap, observatory="hst"):
    """Return the basenames of all mapping files in the hierarchy which
    mentions reference mapping `rmap`.
    """
    mappings = []
    for imap in findall_imaps_using_rmap(rmap, observatory):
        mappings.append(imap)
        for pmap in findall_pmaps_using_imap(imap, observatory):
            mappings.append(pmap)
    return sorted(list(set(mappings)))

def uses(files, observatory="hst"):
    """Return the list of mappings which use any of `files`."""
    mappings = []
    for file_ in files:
        if file_.endswith(".rmap"):
            mappings.extend(findall_mappings_using_rmap(file_, observatory))
        elif file_.endswith(".imap"):
            mappings.extend(findall_pmaps_using_imap(file_, observatory))
        elif file_.endswith(".pmap"):
            pass  # nothing refers to a .pmap
        else:
            mappings.extend(findall_mappings_using_reference(file_, observatory))
    return sorted(list(set(mappings)))

class UsesScript(cmdline.Script):
    """Command line script for printing rmaps using references,  or datasets using references."""

    description = """
Prints out the mappings which refer to the specified mappings or references.

Prints out the datasets which historically used a particular reference as defined by DADSOPS.

IMPORTANT:  
   1. You must specify references or rules on which to operate with --files.
   2. You must set CRDS_PATH and CRDS_SERVER_URL to give crds.uses access to CRDS mappings and databases.
"""

    epilog = """
crds.uses can be invoked like this:

% python -m crds.uses --files n3o1022ij_drk.fits --hst
hst.pmap
hst_0001.pmap
hst_0002.pmap
hst_0003.pmap
...
hst_0041.pmap
hst_acs.imap
hst_acs_0001.imap
hst_acs_0002.imap
hst_acs_0003.imap
...
hst_acs_0008.imap
hst_acs_darkfile.rmap
hst_acs_darkfile_0001.rmap
hst_acs_darkfile_0002.rmap
hst_acs_darkfile_0003.rmap
...
hst_acs_darkfile_0005.rmap

"""
    def add_args(self):
        """Add command line parameters unique to this script."""
        super(UsesScript, self).add_args()
        self.add_argument("--files", nargs="+", 
            help="References for which to dump using mappings or datasets.")        
        self.add_argument("-i", "--include-used", action="store_true", dest="include_used",
            help="Include the used file in the output as the first column.")

    def main(self):
        """Process command line parameters in to a context and list of
        reference files.   Print out the match tuples within the context
        which contain the reference files.
        """
        if not self.args.files:
            self.print_help()
            sys.exit(-1)
        self.print_mappings_using_files()
        return log.errors()
            
    def locate_file(self, file_):
        """Just use basenames for identifying file references."""
        return os.path.basename(file_)
            
    def print_mappings_using_files(self):
        """Print out the mappings which refer to the specified mappings or references."""
        for file_ in self.files:
            for use in uses([file_], self.observatory):
                if self.args.include_used:
                    print(file_, use)
                else:
                    print(use)
    
def test():
    """Run the module doctest."""
    import doctest
    from . import uses
    return doctest.testmod(uses)

if __name__ == "__main__":
    sys.exit(UsesScript()())
