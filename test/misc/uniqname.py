"""This module is used to generate unique time based file names for HST
calibration and synphot references.
"""
import os.path
import sys
import datetime

# ==============================================================================================

from crds.core import cmdline, config, log, naming
from crds.core.exceptions import CrdsError
from crds import data_file

# ==============================================================================================

class UniqnameScript(cmdline.Script):

    """Command line script for renaming references with official CRDS names."""

    description = """This script is used to rename references with unique official CRDS names for HST."""

    epilog = """This program is based loosely on the CDBS program uniqname modified to support
enhanced CDBS-style names with modified timestamps valid after 2016-01-01.

The CRDS uniqame is nominally run as follows::

    % crds uniqname --files s7g1700gl_dead.fits --brief --standard
    CRDS - INFO - Rewriting 's7g1700gl_dead.fits' --> 'zc52141pl_dead.fits'

CRDS uniqname also supports renaming synphot files not otherwise managed by CRDS::

    % crds uniqname --files s7g1700gl_tmt.fits --brief --standard
    CRDS - INFO - Rewriting 's7g1700gl_tmt.fits' --> 'zc52141pl_tmt.fits'

If -s or --standard is added then routinely used switches are added as a
predefined bundle.   Initially these are --add-keywords and --verify-file.

If --add-checksum is specified,  CRDS uniqname will add FITS checksums to the file.
If --add-checksum is not specified,  CRDS uniqname WILL REMOVE any existing checksum.

If --verify-file is specified,  CRDS uniqname will check the FITS checksum and validate
the FITS format of renamed files.

If  --add-keywords is specified CRDS uniqname will add/modify the FILENAME, ROOTNAME,
and HISTORY to document the renaming.

If --remove-original is specified then the original file is deleted after the renamed
file has been created and modified as specified (checksums, keywords, etc.)

Renamed files can be output to a different directory using --output-path.

--dry-run can be used to demo renaming by printing what the new name would be.
    """

    def __init__(self, *args, **keys):
        super(UniqnameScript, self).__init__(*args, **keys)

    def add_args(self):
        """Setup command line switch parsing."""
        self.add_argument('--files', nargs="+",
                          help="Files to rename.")
        self.add_argument('--dry-run', action='store_true',
                          help='Print how a file would be renamed without modifying it.')
        self.add_argument('-a', '--add-checksum', action='store_true',
                          help='Add FITS checksum.  Without, checksums *removed* if header modified.')
        self.add_argument('-f', '--add-keywords', action='store_true',
                          help='When renaming, add FILENAME, ROOTNAME, HISTORY keywords for the generated name.')
        self.add_argument('-e', '--verify-file', action='store_true',
                          help='Verify FITS compliance and any checksums before changing each file.')
        self.add_argument('-s', '--standard', action='store_true',
                          help='Same as --add-keywords --verify-file,  does not add checksums (add -a).')
        self.add_argument('-r', '--remove-original', action='store_true',
                          help='After renaming,  remove the orginal file.')
        self.add_argument('-o', '--output-path',
                          help='Output renamed files to this directory path.')
        self.add_argument('-b', '--brief', action='store_true',
                          help='Produce less output.')
        self.add_argument("--fits-errors", action="store_true",
                          help="When set, treat FITS compliance and checksum errors as fatal exceptions.")
        super(UniqnameScript, self).add_args()

    locate_file = cmdline.Script.locate_file_outside_cache

    def main(self):
        """Generate names corrsponding to files listed on the command line."""
        if self.args.standard:
            self.args.add_keywords = True
            self.args.verify_file = True

        if not self.args.files:
            return

        for filename in self.files:
            assert config.is_reference(filename), \
                "File " + repr(filename) + " does not appear to be a reference file.  Only references can be renamed."
            uniqname = naming.generate_unique_name(filename, self.observatory)
            if self.args.dry_run:
                log.info("Would rename", self.format_file(filename), "-->", self.format_file(uniqname))
            else:
                self.rewrite(filename, uniqname)
                if self.args.remove_original:
                    os.remove(filename)

        # XXXX script returns filename result not suitable as program exit status
        # XXXX filename result is insufficient if multiple files are specified.
        # XXXX filename result supports embedded use on web server returning new name.
        return uniqname

    def rewrite(self, filename, uniqname):
        """Add a FITS checksum to `filename.`"""
        with data_file.fits_open(filename, mode="readonly", checksum=self.args.verify_file, do_not_scale_image_data=True) as hdus:
            verify_mode = "fix+warn" if not self.args.fits_errors else "fix+exception"
            if self.args.verify_file:
                hdus.verify(verify_mode)
            basefile = os.path.basename(filename)
            baseuniq = os.path.basename(uniqname)
            if self.args.add_keywords:
                now = datetime.datetime.utcnow()
                hdus[0].header["FILENAME"] = baseuniq
                hdus[0].header["ROOTNAME"] = os.path.splitext(baseuniq)[0].upper()
                hdus[0].header["HISTORY"] = "{0} renamed to {1} on {2} {3} {4}".format(
                    basefile, baseuniq, MONTHS[now.month - 1], now.day, now.year)
            if self.args.output_path:
                uniqname = os.path.join(self.args.output_path, baseuniq)
            try:
                log.info("Rewriting", self.format_file(filename), "-->", self.format_file(uniqname))
                hdus.writeto(uniqname, output_verify=verify_mode, checksum=self.args.add_checksum)
            except Exception as exc:
                if os.path.exists(uniqname):
                    os.remove(uniqname)
                if "buffer is too small" in str(exc):
                    raise CrdsError(
                        "Failed to rename/rewrite", repr(basefile),
                        "as", repr(baseuniq), ":",
                        "probable file truncation", ":", str(exc)) from exc
                else:
                    raise CrdsError("Failed to rename/rewrite", repr(basefile),
                                    "as", repr(baseuniq), ":",
                                    str(exc)) from exc

    def format_file(self, filename):
        """Print absolute path or basename of `filename` depending on command line --brief"""
        return repr(os.path.basename(filename) if self.args.brief else filename)

MONTHS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

# ==============================================================================================

def has_checksum(filename):
    """Return True IFF `path` names a file which already has FITS checksums.  As a first guess,
    existing checksums should be maintained across file content updates required by the renaming.
    """
    with data_file.fits_open(filename, mode="readonly", do_not_scale_image_data=True) as hdus:
        for hdu in hdus:
            if "CHECKSUM" in hdu.header or "DATASUM" in hdu.header:
                add_checksum = True
                break
        else:
            add_checksum = False
    return add_checksum

def uniqname(old_path):
    """Rename file named `oldpath` to a newstyle HST uniqname format name.  This function
    is used to integrate uniqname with the HST CRDS servers as the approach for "Auto Rename".
    This function rewrites the original file at a new name/path and removes the original since
    the new file is not only renamed but different.

    Verify FITS compliance and any FITS checksums,  raising an exception on any problem.

    Add FILENAME, ROOTNAME, and HISTORY keywords.
    Preserve any FITS checksums.

    Returns  new_cdbs_style_name : str
    """
    add_checksums = "--add-checksum" if has_checksum(old_path) else ""
    new_name = UniqnameScript("crds.misc.uniqname --files {0} --standard --remove-original --fits-errors {1}".format(
        old_path, add_checksums))()
    return new_name

# ==============================================================================================

if __name__ == "__main__":
    UniqnameScript()()
    sys.exit(log.errors())
