"""This module is used to generate unique time based file names."""

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os.path
import sys

from astropy.io import fits

from crds import cmdline, log, naming

class UniqnameScript(cmdline.Script):

    """Command line script for renaming files with official CRDS names."""

    description = """This script is used to rename files with unique official CRDS names."""
        
    epilog = """    
    """

    def __init__(self, *args, **keys):
        super(UniqnameScript, self).__init__(*args, **keys)
    
    def add_args(self):
        """Setup command line switch parsing."""
        self.add_argument('--files', nargs="*", 
                          help="Files to rename.")
        self.add_argument('--dry-run', action='store_true',
                          help='Print how a file would be renamed without modifying it.')
        self.add_argument('-f', '--set-filename-keyword', action='store_true',
                          help='When renaming, set the FILENAME keyword of the file to the generated name.')
        self.add_argument('-e', '--verify-file', action='store_true', 
                          help='Verify FITS compliance and any checksums before changing each file.')
        self.add_argument('-s', '--standard', action='store_true', 
                          help='Same as --set-filename-keyword --verify-file,  does not add checksums (add -a).')
        self.add_argument('-r', '--remove-original', action='store_true',
                          help='After renaming,  remove the orginal file.')
        self.add_argument('-o', '--output-path',
                          help='Output renamed files to this directory path.')
        group = self.get_exclusive_arg_group(required=False)
        group.add_argument('-a', '--add-checksum', action='store_true',
                           help='Add FITS checksum.  Without, checksums *removed* if header modified.')
        group.add_argument('-d', '--delete-checksum', action='store_true',
                           help='Delete FITS checksum. Make sure checksums are removed.')
        super(UniqnameScript, self).add_args()
        
    def main(self):
        """Generate names corrsponding to files listed on the command line."""
        if self.args.standard:
            self.args.set_filename_keyword = True
            self.args.verify_file = True
            self.args.remove_original = True

        for filename in self.files:
            uniqname = naming.generate_unique_name(filename, self.observatory)
            if self.args.dry_run:
                log.info("Would rename", repr(filename), "-->", repr(uniqname))
            else:
                self.rewrite(filename, uniqname)
                if self.args.remove_original:
                    os.remove(filename)
    
    def rewrite(self, filename, uniqname):
        """Add a FITS checksum to `filename.`"""
        hdus = fits.open(filename, mode="readonly", checksum=self.args.verify_file)
        if self.args.verify_file:
            hdus.verify("fix+warn")
        basename = os.path.basename(uniqname)
        if self.args.set_filename_keyword:
            hdus[0].header["FILENAME"] = basename
        if self.args.output_path:
            uniqname = os.path.join(self.args.outpath, basename)
        log.info("Rewriting", repr(filename), "-->", repr(uniqname))
        hdus.writeto(uniqname, output_verify="fix+warn", checksum=self.args.add_checksum)
            
if __name__ == "__main__":
    sys.exit(UniqnameScript()())
