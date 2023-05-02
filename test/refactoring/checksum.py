"""Originally this script was used to update the checksums in CRDS mapping
files.   It has been extended so that it is capable of handling FITS reference
file checksums as well::

    % crds checksum  hst.pmap  hst_acs_0020.imap   hst_acs_darkfile_0057.rmap

    % crds checksum ./test.fits
    % crds checksum --remove ./*.fits
    % crds checksum --verify ./*.fits

no switch  adds / updates FITS or CRDS mapping checksums
--remove   removing FITS checksums  (mappings not supported)
--verify   verifying FITS or mapping checksums.

"""
import sys

# ============================================================================

from crds.core import log, rmap, cmdline, config, exceptions
from crds.certify import mapping_parser
from crds import data_file

# ============================================================================

def update_checksum(file_):
    """Rewrite the checksum of a single mapping, in place.   Reports duplicate cases being dropped."""
    if not check_duplicates(file_):
        mapping = rmap.Mapping.from_file(file_, ignore_checksum=True)
        mapping.write()

# Interim step to making update_checksums universal.  Switch to update_mapping_checksums now.
update_mapping_checksum = update_checksum

def check_duplicates(file_):
    """Before rewriting an rmap to update the checksum, certify to ensure no
    duplicates (or other certify errors) exist prior to rewriting checksum.
    """
    old_errs = log.errors()
    parsing = mapping_parser.parse_mapping(file_)
    mapping_parser.check_duplicates(parsing)
    new_errs = log.errors()
    return new_errs > old_errs

# ============================================================================

def add_checksum(file_):
    """Add checksums to file_."""
    log.info("Adding checksum for", repr(file_))
    if config.is_reference(file_):
        with log.error_on_exception("Failed updating checksum for", repr(file_)):
            data_file.add_checksum(file_)
    elif config.is_mapping(file_):
        update_mapping_checksum(file_)
    else:
        raise exceptions.CrdsError(
            "File", repr(file_), "does not appear to be a CRDS reference or mapping file.")

def remove_checksum(file_):
    """Remove checksums from `file_`."""
    log.info("Removing checksum for", repr(file_))
    if config.is_reference(file_):
        data_file.remove_checksum(file_)
    elif config.is_mapping(file_):
        raise exceptions.CrdsError("Mapping checksums cannot be removed for:", repr(file_))
    else:
        raise exceptions.CrdsError(
            "File", repr(file_), "does not appear to be a CRDS reference or mapping file.")

def verify_checksum(file_):
    """Verify checksums in `file_`."""
    log.info("Verifying checksum for", repr(file_))
    if config.is_reference(file_):
        data_file.verify_checksum(file_)
    elif config.is_mapping(file_):
        if config.CRDS_IGNORE_MAPPING_CHECKSUM.get():
            log.warning("Mapping checksums are disabled by config.CRDS_IGNORE_MAPPING_CHECKSM.")
        rmap.load_mapping(file_)
    else:
        raise exceptions.CrdsError(
            "File", repr(file_), "does not appear to be a CRDS reference or mapping file.")

# ============================================================================

class ChecksumScript(cmdline.Script):
    """Command line script for updating CRDS rule and reference file checksums."""

    description = """
    Add, remove, or verify checksums in CRDS rules or reference files.

    1. Default operation is to ADD checksums::

    % crds checksum  *.rmap

    % crds checksum  *.fits

    2. Reference files may support REMOVING checksums::

    % crds checksum --remove *.fits

    NOTE: CRDS mapping / rules files do not support removing checksums.

    3. Checksums can be VERIFIED without attempting to update or remove::

    % crds checksum --verify  *.rmap

    % crds checksum --verify *.fits

    Currently only FITS references support checksum operations.
    Checksums can be added or verified on all CRDS mapping types.
    """

    epilog = """
    """

    locate_file = cmdline.Script.locate_file_outside_cache

    def add_args(self):
        self.add_argument(
            "files", type=str, nargs="+",
            help="Files to operate on, CRDS rule or reference files.")

        self.add_argument(
            "--remove", action="store_true",
            help="Remove checksums when specified.  Invalid for CRDS mappings.")

        self.add_argument(
            "--verify", action="store_true",
            help="Verify checksums when specified.")

    def main(self):
        for file_ in self.files:
            with log.error_on_exception("Checksum operation FAILED"):
                if self.args.remove:
                    remove_checksum(file_)
                elif self.args.verify:
                    verify_checksum(file_)
                else:
                    add_checksum(file_)
        return log.errors()

if __name__ == "__main__":
    sys.exit(ChecksumScript()())
