from pathlib import Path
from pytest import mark
import shutil

from crds.core import log, utils
from crds import data_file

from crds.refactoring.checksum import ChecksumScript

# For log capture tests, need to ensure that the CRDS
# logger propagates its events.
log.THE_LOGGER.logger.propagate = True

@mark.hst
@mark.refactoring
@mark.checksum
def test_checksum_script_fits_add(hst_data, tmpdir):
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


@mark.hst
@mark.refactoring
@mark.checksum
def test_checksum_script_fits_remove(hst_data, tmpdir):
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


@mark.hst
@mark.refactoring
@mark.checksum
def test_checksum_script_fits_verify_good(hst_data, tmpdir):
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


@mark.hst
@mark.refactoring
@mark.checksum
def test_checksum_script_fits_verify_bad(hst_data, tmpdir, caplog):
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


@mark.hst
@mark.refactoring
@mark.checksum
def test_checksum_script_rmap_verify_good(hst_data):
    """Test checksum verification for rmaps"""
    map_path = Path(hst_data) / 'hst.pmap'
    argv = f'crds.refactor.checksum --verify {str(map_path)}'
    assert ChecksumScript(argv)() == 0


@mark.hst
@mark.refactoring
@mark.checksum
def test_checksum_script_rmap_add_bad(hst_data, tmpdir, caplog):
    """Test adding checksum to an rmap file"""
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


@mark.hst
@mark.refactoring
@mark.checksum
def test_checksum_script_rmap_verify_bad(hst_data, caplog):
    """Test bad checksum in rmap"""
    argv = f'crds.refactor.checksum --verify {str(Path(hst_data) / "hst-bad-xsum.rmap")}'
    assert ChecksumScript(argv)() == 1
    assert 'Checksum operation FAILED : sha1sum mismatch' in caplog.text


@mark.hst
@mark.refactoring
@mark.checksum
def test_checksum_script_rmap_remove_bad(hst_data, tmpdir, caplog):
    """Test removing a bad checksum from a rmap"""
    # setup test file which should bad checksum data.
    map_path = tmpdir / "remove_bad.rmap"
    shutil.copy(Path(hst_data) / 'hst-bad-xsum.rmap', map_path)
    # Attempt removing checksum
    assert ChecksumScript(f"crds.refactor.checksum --remove {str(map_path)}")() == 1
    assert 'Checksum operation FAILED : Mapping checksums cannot be removed for:' in caplog.text


@mark.hst
@mark.refactoring
@mark.checksum
def test_checksum_script_rmap_verify_missing(hst_data, caplog):
    """Test that checksum information is missing from a map"""
    map_path = Path(hst_data) / 'hst-missing-xsum.rmap'
    argv = f'crds.refactor.checksum --verify {str(map_path)}'
    assert ChecksumScript(argv)() == 1
    assert 'Checksum operation FAILED : sha1sum is missing in' in caplog.text


@mark.jwst
@mark.refactoring
@mark.checksum
def test_checksum_script_unsupported_asdf(jwst_data, tmpdir, caplog):
    """Test that ASDF is still unsupported with-respect-to checksum"""
    # setup test file
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


@mark.jwst
@mark.refactoring
@mark.checksum
def test_checksum_script_unsupported_json(jwst_data, tmpdir, caplog):
    """Test that JSON is still unsupported with-respect-to-checksum"""
    # setup test file
    json_path = tmpdir / 'valid.json'
    shutil.copy(Path(jwst_data) / 'valid.json', json_path)
    # Test that adding is not supported.
    argv = f'crds.refactor.checksum {str(json_path)}'
    assert ChecksumScript(argv)() == 1
    assert "Method 'add_checksum' is not supported for file format 'JSON'" in caplog.text
    # Test that removing is not supported.
    caplog.clear()
    argv = f'crds.refactor.checksum --remove {str(json_path)}'
    assert ChecksumScript(argv)() == 1
    assert "Method 'remove_checksum' is not supported for file format 'JSON'" in caplog.text
    # Test that verification is not supported.
    caplog.clear()
    argv = f'crds.refactor.checksum --verify {str(json_path)}'
    assert ChecksumScript(argv)() == 1
    assert "Method 'verify_checksum' is not supported for file format 'JSON'" in caplog.text


@mark.hst
@mark.refactoring
@mark.checksum
def test_checksum_script_unsupported_text(hst_data, tmpdir, caplog):
    """Test that unrecognized files types are not supported"""
    # setup test file
    file_path = tmpdir / 'opaque_fts.tmp'
    shutil.copy(Path(hst_data) / 'opaque_fts.tmp', file_path)
    # Test that adding is not supported.
    argv = f'crds.refactor.checksum {str(file_path)}'
    assert ChecksumScript(argv)() == 1
    assert "does not appear to be a CRDS reference or mapping file." in caplog.text
    # Test that removing is not supported.
    caplog.clear()
    argv = f'crds.refactor.checksum --remove {str(file_path)}'
    assert ChecksumScript(argv)() == 1
    assert "does not appear to be a CRDS reference or mapping file." in caplog.text
    # Test that verification is not supported.
    caplog.clear()
    argv = f'crds.refactor.checksum --verify {str(file_path)}'
    assert ChecksumScript(argv)() == 1
    assert "does not appear to be a CRDS reference or mapping file." in caplog.text
