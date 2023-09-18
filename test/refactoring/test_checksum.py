import doctest
import os
from pathlib import Path
from pytest import mark
import shutil

from crds.core import log, utils
from crds import data_file

from crds.refactoring import checksum
from crds.refactoring.checksum import ChecksumScript


@mark.refactoring
@mark.checksum
def test_checksum_script_fits_add(default_test_cache_state, hst_data, tmpdir):

    # setup test file which should not have any checksum data.
    fits_path = tmpdir / "added.fits"
    shutil.copy(Path(hst_data) / 's7g1700gl_dead.fits', fits_path)
    header = data_file.get_header(str(fits_path))
    assert "CHECKSUM" not in header
    assert "DATASUM" not in header

    # add checksum and test
    argv = f'crds.refactor.checksum {str(fits_path)}'
    assert ChecksumScript(argv)() == 0  # 0 == successful run
    utils.clear_function_caches()
    header = data_file.get_header(str(fits_path))
    assert "CHECKSUM" in header
    assert "DATASUM" in header


@mark.refactoring
@mark.checksum
def test_checksum_script_fits_remove():
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


@mark.refactoring
@mark.checksum
def test_checksum_script_fits_verify_good():
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


@mark.refactoring
@mark.checksum
def test_checksum_script_fits_verify_bad():
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


@mark.refactoring
@mark.checksum
def test_checksum_script_rmap_verify_good():
    """
    >>> old_state = test_config.setup()
    >>> ChecksumScript("crds.refactor.checksum --verify data/hst.pmap")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Verifying checksum for 'data/hst.pmap'
    0
    >>> test_config.cleanup(old_state)
    """


@mark.refactoring
@mark.checksum
def test_checksum_script_rmap_add_bad():
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


@mark.refactoring
@mark.checksum
def test_checksum_script_rmap_verify_bad():
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


@mark.refactoring
@mark.checksum
def test_checksum_script_rmap_remove_bad():
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


@mark.refactoring
@mark.checksum
def test_checksum_script_rmap_verify_missing():
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


@mark.refactoring
@mark.checksum
def test_checksum_script_unsupported_asdf():
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


@mark.refactoring
@mark.checksum
def test_checksum_script_unsupported_json():
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


@mark.refactoring
@mark.checksum
def test_checksum_script_unsupported_text():
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
