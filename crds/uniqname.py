"""This module is used to generate unique time based file names."""

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os.path
import sys

from crds import cmdline, log, data_file, naming

class UniqnameScript(cmdline.Script):

    """Command line script for renaming files with official CRDS names."""

    description = """This script is used to rename files with unique official CRDS names."""
        
    epilog = """    
    """

    def __init__(self, *args, **keys):
        super(UniqnameScript, self).__init__(*args, **keys)
    
    def add_args(self):
        self.add_argument('--files', nargs="*", help="Files to rename.")
        self.add_argument('-r', '--rename-files', action='store_true', dest='rename_files',
                          help='Rename the given files to their generated unique names.')
        self.add_argument('-f', '--set-filename', action='store_true', dest='set_filename', 
                          help='When renaming, set the FILENAME keyword of the file to the generated name.')
        super(UniqnameScript, self).add_args()
        
    def main(self):
        """Generate names corrsponding to files listed on the command line."""
        for filename in self.files:
            if self.args.rename_files:
                self.rename_file(filename)
            else:
                self.print_name(filename)

    def print_name(self, filename):
        """Print a demo version of how filename would be renamed."""
        uniqname = naming.generate_unique_name(filename)
        print("Generating", repr(filename), "-->", repr(uniqname))

    def rename_file(self, filename):
        """Rename `filename` to a unique name."""
        uniqname = naming.generate_unique_name(filename)
        print("Renaming", repr(filename), "-->", repr(uniqname))
        if self.args.set_filename:
            with log.error_on_exception("Failed to set FILENAME keyword for", repr(filename)):
                data_file.setval(filename, "FILENAME", os.path.basename(uniqname))
        with log.error_on_exception("Failed to rename file", repr(filename)):
            os.rename(filename, uniqname)
    
if __name__ == "__main__":
    sys.exit(UniqnameScript()())
