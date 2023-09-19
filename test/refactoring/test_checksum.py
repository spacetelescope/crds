import doctest
import os
from pathlib import Path
from pytest import mark
import shutil

from crds.core import log, utils
from crds import data_file

from crds.refactoring import checksum
from crds.refactoring.checksum import ChecksumScript

# For log capture tests, need to ensure that the CRDS
# logger propagates its events.
log.THE_LOGGER.logger.propagate = True


@mark.refactoring
@mark.checksum
def test_checksum_script_fits_add(default_test_cache_state, hst_data, tmpdir):
    """Test adding checksum to FITS files"""

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
def test_checksum_script_fits_remove(default_test_cache_state, hst_data, tmpdir):
    """Test removing chedsum from FITS files"""

    # setup test file which should not have any checksum data.
    fits_path = tmpdir / "removed.fits"
    shutil.copy(Path(hst_data) / 's7g1700gl_dead_good_xsum.fits', fits_path)
    header = data_file.get_header(str(fits_path))
    assert "CHECKSUM" in header
    assert "DATASUM" in header

    # Remove the checksum and test.
    argv = f'crds.refactor.checksum --remove {str(fits_path)}'
    assert ChecksumScript(argv)() == 0  # 0 = successful run
    utils.clear_function_caches()
    header = data_file.get_header(str(fits_path))
    assert "CHECKSUM" not in header
    assert "DATASUM" not in header


@mark.refactoring
@mark.checksum
def test_checksum_script_fits_verify_good(default_test_cache_state, hst_data, tmpdir):
    """Test checksum verification of a good file"""

    # setup test file and confirm it contains checksum information.
    fits_path = tmpdir / "verify_good.fits"
    shutil.copy(Path(hst_data) / "s7g1700gl_dead_good_xsum.fits", fits_path)
    header = data_file.get_header(str(fits_path))
    assert header["CHECKSUM"] == 'i2PMi1MJi1MJi1MJ'
    assert header["DATASUM"] == '0'

    # Verify checksum information
    argv = f'crds.refactor.checksum --verify {str(fits_path)}'
    assert ChecksumScript(argv)() == 0


@mark.refactoring
@mark.checksum
def test_checksum_script_fits_verify_bad(default_test_cache_state, hst_data, tmpdir, caplog):
    """Test checksum verification of a bad file"""

    # setup test file.
    fits_path = tmpdir / 'verify_bad.fits'
    shutil.copy(Path(hst_data) / 's7g1700gl_dead_bad_xsum.fits', fits_path)

    # Verify that bad information is found.
    argv = f'crds.refactor.checksum --verify {str(fits_path)}'
    script = ChecksumScript(argv)
    caplog.clear()
    assert script() == 0  # 0 == successful run
    assert f"Verifying checksum for '{str(fits_path)[:10]}" in caplog.text
    assert "Checksum verification failed for HDU ('', 1)." in caplog.text
    assert "Datasum verification failed for HDU ('', 1)." in caplog.text


# ----------------------------------------------------------------------


@mark.refactoring
@mark.checksum
def test_checksum_script_rmap_verify_good(default_test_cache_state, hst_data):
    """Test checksum verification for rmaps"""

    map_path = Path(hst_data) / 'hst.pmap'
    argv = f'crds.refactor.checksum --verify {str(map_path)}'
    assert ChecksumScript(argv)() == 0


@mark.refactoring
@mark.checksum
def test_checksum_script_rmap_add_bad(default_test_cache_state, hst_data, tmpdir, caplog):
    """TEst adding checksum to an rmap file"""

    # setup test file which should bad checksum data.
    map_path = tmpdir / "add_bad.rmap"
    shutil.copy(Path(hst_data) / 'hst-bad-xsum.rmap', map_path)
    argv_verify = f'crds.refactor.checksum --verify {str(map_path)}'
    assert ChecksumScript(argv_verify)() == 1
    assert 'Checksum operation FAILED : sha1sum mismatch' in caplog.text

    # add checksum and test
    argv = f'crds.refactor.checksum {str(map_path)}'
    assert ChecksumScript(argv)() == 0  # 0 == successful run
    assert ChecksumScript(argv_verify)() == 0


@mark.refactoring
@mark.checksum
def test_checksum_script_rmap_verify_bad(default_test_cache_state, hst_data, caplog):
    """Test bad checksum in rmap"""

    argv = f'crds.refactor.checksum --verify {str(Path(hst_data) / "hst-bad-xsum.rmap")}'
    assert ChecksumScript(argv)() == 1
    assert 'Checksum operation FAILED : sha1sum mismatch' in caplog.text


@mark.refactoring
@mark.checksum
def test_checksum_script_rmap_remove_bad(default_test_cache_state, hst_data, tmpdir, caplog):
    """Test removing a bad checksum from a rmap"""

    # setup test file which should bad checksum data.
    map_path = tmpdir / "remove_bad.rmap"
    shutil.copy(Path(hst_data) / 'hst-bad-xsum.rmap', map_path)

    # Attempt removing checksum
    assert ChecksumScript(f"crds.refactor.checksum --remove {str(map_path)}")() == 1
    assert 'Checksum operation FAILED : Mapping checksums cannot be removed for:' in caplog.text


@mark.refactoring
@mark.checksum
def test_checksum_script_rmap_verify_missing(default_test_cache_state, hst_data, caplog):
    """Test that checksum information is missing from a map"""

    map_path = Path(hst_data) / 'hst-missing-xsum.rmap'
    argv = f'crds.refactor.checksum --verify {str(map_path)}'
    assert ChecksumScript(argv)() == 1
    assert 'Checksum operation FAILED : sha1sum is missing in' in caplog.text


@mark.refactoring
@mark.checksum
def test_checksum_script_unsupported_asdf(default_test_cache_state, jwst_data, tmpdir, caplog):
    """Test that ASDF is still unsupported with-respect-to checksum"""

    # setup test file which should bad checksum data.
    asdf_path = tmpdir / 'valid.asdf'
    shutil.copy(Path(jwst_data) / 'valid.asdf', asdf_path)

    # Test that adding is not supported.
    argv = f'crds.refactor.checksum {str(asdf_path)}'
    assert ChecksumScript(argv)() == 1
    assert "Method 'add_checksum' is not supported for file format 'ASDF'" in caplog.text

    # Test that removing is not supported.
    caplog.clear()
    argv = f'crds.refactor.checksum --remove {str(asdf_path)}'
    assert ChecksumScript(argv)() == 1
    assert "Method 'remove_checksum' is not supported for file format 'ASDF'" in caplog.text

    # Test that verification is not supported.
    caplog.clear()
    argv = f'crds.refactor.checksum --verify {str(asdf_path)}'
    assert ChecksumScript(argv)() == 1
    assert "Method 'verify_checksum' is not supported for file format 'ASDF'" in caplog.text


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
