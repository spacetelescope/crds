"""
usage: /Users/jmiller/work/workspace_crds/CRDS/crds/misc/uniqname.py
       [-h] [--files FILES [FILES ...]] [--dry-run] [-a] [-f] [-e] [-s] [-r]
       [-o OUTPUT_PATH] [-b] [--fits-errors] [-v] [--verbosity VERBOSITY]
       [--dump-cmdline] [-R] [-I] [-V] [-J] [-H] [--stats] [--profile PROFILE]
       [--log-time] [--pdb] [--debug-traps]

This script is used to rename references with unique official CRDS names.

optional arguments:
  -h, --help            show this help message and exit
  --files FILES [FILES ...]
                        Files to rename.
  --dry-run             Print how a file would be renamed without modifying it.
  -a, --add-checksum    Add FITS checksum.  Without, checksums *removed* if header modified.
  -f, --add-keywords    When renaming, add FILENAME, ROOTNAME, HISTORY keywords for the generated name.
  -e, --verify-file     Verify FITS compliance when changing files.
  -s, --standard        Same as --add-keywords --verify-file,  does not add checksums (add -a).
  -r, --remove-original
                        After renaming,  remove the orginal file.
  -o OUTPUT_PATH, --output-path OUTPUT_PATH
                        Output renamed files to this directory path.
  -b, --brief           Produce less output.
  --fits-errors         When set, treat FITS compliance and checksum errors as fatal exceptions.
  -v, --verbose         Set log verbosity to True,  nominal debug level.
  --verbosity VERBOSITY
                        Set log verbosity to a specific level: 0..100.
  --dump-cmdline        Dump the command line parameters used to start the script to the log.
  -R, --readonly-cache  Don't modify the CRDS cache.  Not compatible with options which implicitly modify the cache.
  -I, --ignore-cache    Download required files even if they're already in the cache.
  -V, --version         Print the software version and exit.
  -J, --jwst            Force observatory to JWST for determining header conventions.
  -H, --hst             Force observatory to HST for determining header conventions.
  --stats               Track and print timing statistics.
  --profile PROFILE     Output profile stats to the specified file.
  --log-time            Add date/time to log messages.
  --pdb                 Run under pdb.
  --debug-traps         Bypass exception error message traps and re-raise exception.

This program is based loosely on the CDBS program uniqname modified to support
enhanced CDBS-style names with modified timestamps valid after 2016-01-01.

The CRDS uniqame is nominally run as follows:

    % crds uniqname --files s7g1700gl_dead.fits --brief --standard
    CRDS - INFO - Rewriting 's7g1700gl_dead.fits' --> 'zc52141pl_dead.fits'

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
import os
import doctest

from crds.core import log
from crds import tests
from crds.tests import test_config

from crds.misc import uniqname
from crds.misc.uniqname import UniqnameScript

def dt_synphot_uniqname():
    """
    Compute diffs for two .pmap's:

    >>> old_state = test_config.setup()
    >>> name = UniqnameScript("crds.misc.uniqname --dry-run --files data/16n1832tm_tmc.fits")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Would rename 'data/16n1832tm_tmc.fits' --> 'data/...m_tmc.fits'
    >>> test_config.cleanup(old_state)
    """

def dt_cdbs_uniqname():
    """
    Compute diffs for two .pmap's:

    >>> old_state = test_config.setup()
    >>> name = UniqnameScript("crds.misc.uniqname --standard --files data/s7g1700gl_dead.fits")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Rewriting 'data/s7g1700gl_dead.fits' --> 'data/..._dead.fits'
    >>> name1 = uniqname.uniqname(name)
    CRDS - INFO -  Rewriting '..._dead.fits' --> '..._dead.fits'
    >>> os.remove(name1)
    >>> test_config.cleanup(old_state)
    """

def dt_has_checksum():
    """
    Compute diffs for two .pmap's:

    >>> old_state = test_config.setup()
    >>> uniqname.has_checksum("data/16n1832tm_tmc.fits")  # doctest: +ELLIPSIS
    False
    >>> uniqname.has_checksum("data/s7g1700gl_dead_good_xsum.fits") # doctest: +ELLIPSIS
    True
    >>> test_config.cleanup(old_state)
    """

def test():
    """Run module tests,  for now just doctests only.

    test_config.setup() and cleanup() are done inline above because bracketing
    the tests here does not get picked up by nose test discovery.  Combining
    tests into one giant docstring works but is hard to analyze and debug when
    things go wrong.
    """
    from crds.tests import test_uniqname, tstmod
    return tstmod(test_uniqname)

if __name__ == "__main__":
    print(test())
