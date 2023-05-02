import os
import shutil
import doctest

from crds.core import log, utils
from crds import tests, data_file
from crds.tests import test_config

from crds.refactoring import checksum
from crds.refactoring.checksum import ChecksumScript

def dt_checksum_script_fits_add():
    """
    >>> old_state = test_config.setup()

    >>> _ = shutil.copy("data/s7g1700gl_dead.fits", "added.fits")
    >>> header = data_file.get_header("./added.fits")
    >>> assert "CHECKSUM" not in header
    >>> assert "DATASUM" not in header

    >>> ChecksumScript("crds.refactor.checksum ./added.fits")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Adding checksum for './added.fits'
    0

    >>> utils.clear_function_caches()
    >>> header = data_file.get_header("./added.fits")
    >>> assert "CHECKSUM" in header
    >>> assert "DATASUM" in header

    >>> ChecksumScript("crds.refactor.checksum --verify ./added.fits")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Verifying checksum for './added.fits'
    0

    >>> os.remove("added.fits")

    >>> test_config.cleanup(old_state)
    """

def dt_checksum_script_fits_remove():
    """
    >>> old_state = test_config.setup()

    >>> _ = shutil.copy("data/s7g1700gl_dead_good_xsum.fits", "removed.fits")
    >>> header = data_file.get_header("./removed.fits")
    >>> assert "CHECKSUM" in header
    >>> assert "DATASUM" in header

    >>> ChecksumScript("crds.refactor.checksum --remove ./removed.fits")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Removing checksum for './removed.fits'
    0

    >>> utils.clear_function_caches()
    >>> header = data_file.get_header("./removed.fits")
    >>> assert "CHECKSUM" not in header
    >>> assert "DATASUM" not in header

    >>> ChecksumScript("crds.refactor.checksum --verify ./removed.fits")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Verifying checksum for './removed.fits'
    0

    >>> os.remove("removed.fits")
    >>> test_config.cleanup(old_state)
    """

def dt_checksum_script_fits_verify_good():
    """
    >>> old_state = test_config.setup()

    >>> _ = shutil.copy("data/s7g1700gl_dead_good_xsum.fits", "verify_good.fits")
    >>> header = data_file.get_header("verify_good.fits")
    >>> header["CHECKSUM"]
    'i2PMi1MJi1MJi1MJ'
    >>> header["DATASUM"]
    '0'

    >>> ChecksumScript("crds.refactor.checksum --verify ./verify_good.fits")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Verifying checksum for './verify_good.fits'
    0

    >>> os.remove("verify_good.fits")
    >>> test_config.cleanup(old_state)
    """

def dt_checksum_script_fits_verify_bad():
    """
    >>> old_state = test_config.setup()
    >>> _ = shutil.copy("data/s7g1700gl_dead_bad_xsum.fits", "./verify_bad.fits")
    >>> ChecksumScript("crds.refactor.checksum --verify ./verify_bad.fits")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Verifying checksum for './verify_bad.fits'
    CRDS - WARNING -  AstropyUserWarning : astropy.io.fits.hdu.base : Checksum verification failed for HDU ('', 1).
    CRDS - WARNING -  AstropyUserWarning : astropy.io.fits.hdu.base : Datasum verification failed for HDU ('', 1).
    0
    >>> os.remove("verify_bad.fits")
    >>> test_config.cleanup(old_state)
    """

# ----------------------------------------------------------------------

def dt_checksum_script_rmap_verify_good():
    """
    >>> old_state = test_config.setup()
    >>> ChecksumScript("crds.refactor.checksum --verify data/hst.pmap")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Verifying checksum for 'data/hst.pmap'
    0
    >>> test_config.cleanup(old_state)
    """

def dt_checksum_script_rmap_add_bad():
    """
    >>> old_state = test_config.setup()
    >>> _ = shutil.copy("data/hst-bad-xsum.rmap", "./add_bad.rmap")

    >>> ChecksumScript("crds.refactor.checksum ./add_bad.rmap")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Adding checksum for './add_bad.rmap'
    0

    >>> ChecksumScript("crds.refactor.checksum --verify ./add_bad.rmap")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Verifying checksum for './add_bad.rmap'
    0

    >>> os.remove("add_bad.rmap")
    >>> test_config.cleanup(old_state)
    """

def dt_checksum_script_rmap_verify_bad():
    """
    >>> old_state = test_config.setup()
    >>> _ = shutil.copy("data/hst-bad-xsum.rmap", "./verify_bad.rmap")
    >>> ChecksumScript("crds.refactor.checksum --verify ./verify_bad.rmap")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Verifying checksum for './verify_bad.rmap'
    CRDS - ERROR -  Checksum operation FAILED : sha1sum mismatch in 'verify_bad.rmap'
    1
    >>> os.remove("verify_bad.rmap")
    >>> test_config.cleanup(old_state)
    """


def dt_checksum_script_rmap_remove_bad():
    """
    >>> old_state = test_config.setup()
    >>> _ = shutil.copy("data/hst-bad-xsum.rmap", "./remove_bad.rmap")
    >>> ChecksumScript("crds.refactor.checksum --remove ./remove_bad.rmap")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Removing checksum for './remove_bad.rmap'
    CRDS - ERROR -  Checksum operation FAILED : Mapping checksums cannot be removed for: './remove_bad.rmap'
    1
    >>> os.remove("remove_bad.rmap")
    >>> test_config.cleanup(old_state)
    """

def dt_checksum_script_rmap_verify_missing():
    """
    >>> old_state = test_config.setup()
    >>> _ = shutil.copy("data/hst-missing-xsum.rmap", "./verify_missing.rmap")

    >>> ChecksumScript("crds.refactor.checksum --verify ./verify_missing.rmap")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Verifying checksum for './verify_missing.rmap'
    CRDS - ERROR -  Checksum operation FAILED : sha1sum is missing in 'verify_missing.rmap'
    1

    >>> os.remove("verify_missing.rmap")
    >>> test_config.cleanup(old_state)
    """

def dt_checksum_script_unsupported_asdf():
    """
    >>> old_state = test_config.setup()
    >>> ChecksumScript("crds.refactor.checksum data/valid.asdf")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Adding checksum for 'data/valid.asdf'
    CRDS - ERROR -  Failed updating checksum for 'data/valid.asdf' : Method 'add_checksum' is not supported for file format 'ASDF'
    1
    >>> ChecksumScript("crds.refactor.checksum --remove data/valid.asdf")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Removing checksum for 'data/valid.asdf'
    CRDS - ERROR -  Checksum operation FAILED : Method 'remove_checksum' is not supported for file format 'ASDF'
    1
    >>> ChecksumScript("crds.refactor.checksum --verify data/valid.asdf")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Verifying checksum for 'data/valid.asdf'
    CRDS - ERROR -  Checksum operation FAILED : Method 'verify_checksum' is not supported for file format 'ASDF'
    1
    >>> test_config.cleanup(old_state)
    """

def dt_checksum_script_unsupported_json():
    """
    >>> old_state = test_config.setup()
    >>> ChecksumScript("crds.refactor.checksum data/valid.json")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Adding checksum for 'data/valid.json'
    CRDS - ERROR -  Failed updating checksum for 'data/valid.json' : Method 'add_checksum' is not supported for file format 'JSON'
    1
    >>> ChecksumScript("crds.refactor.checksum --remove data/valid.json")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Removing checksum for 'data/valid.json'
    CRDS - ERROR -  Checksum operation FAILED : Method 'remove_checksum' is not supported for file format 'JSON'
    1
    >>> ChecksumScript("crds.refactor.checksum --verify data/valid.json")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Verifying checksum for 'data/valid.json'
    CRDS - ERROR -  Checksum operation FAILED : Method 'verify_checksum' is not supported for file format 'JSON'
    1
    >>> test_config.cleanup(old_state)
    """

def dt_checksum_script_unsupported_text():
    """
    >>> old_state = test_config.setup()
    >>> ChecksumScript("crds.refactor.checksum data/opaque_fts.tmp")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Adding checksum for 'data/opaque_fts.tmp'
    CRDS - ERROR -  Checksum operation FAILED : File 'data/opaque_fts.tmp' does not appear to be a CRDS reference or mapping file.
    1
    >>> ChecksumScript("crds.refactor.checksum --remove ddata/opaque_fts.tmp")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Removing checksum for 'ddata/opaque_fts.tmp'
    CRDS - ERROR -  Checksum operation FAILED : File 'ddata/opaque_fts.tmp' does not appear to be a CRDS reference or mapping file.
    1
    >>> ChecksumScript("crds.refactor.checksum --verify data/opaque_fts.tmp")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Verifying checksum for 'data/opaque_fts.tmp'
    CRDS - ERROR -  Checksum operation FAILED : File 'data/opaque_fts.tmp' does not appear to be a CRDS reference or mapping file.
    1
    >>> test_config.cleanup(old_state)
    """

def test():
    """Run module tests,  for now just doctests only.

    test_config.setup() and cleanup() are done inline above because bracketing
    the tests here does not get picked up by nose test discovery.  Combining
    tests into one giant docstring works but is hard to analyze and debug when
    things go wrong.
    """
    from crds.tests import test_checksum, tstmod
    return tstmod(test_checksum)

if __name__ == "__main__":
    print(test())
