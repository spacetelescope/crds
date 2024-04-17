"""
Tests for crds.misc.check_archive which is nominally used to check the
archive for file availability as an alternative to a true ACK from the
archive when their processing is complete.  Also supplies a function API
used by the server to determine and cache file availability status in the
CRDS catalog.
"""
from pytest import mark
import logging
import sys
from crds.core import log
from crds.misc import check_archive

# ensure CRDS logger propagates events to pytest log capture.
log.THE_LOGGER.logger.propagate = True

# prevent pytest args from being passed to CheckArchive script
[sys.argv.remove(a) for a in sys.argv]

@mark.hst
@mark.misc
def test_check_archive_file_api_true(hst_shared_cache_state):
    chk = check_archive.file_available("hst.pmap")
    assert chk is True


@mark.hst
@mark.misc
def test_check_archive_file_api_false(hst_shared_cache_state, caplog):
    with caplog.at_level(logging.INFO, logger="CRDS"):
        chk = check_archive.file_available("foo.pmap")
        out = caplog.text
    assert chk is False
    assert "File 'foo.pmap' failed HTTP HEAD with code = 404 from 'https://hst-crds.stsci.edu/unchecked_get/mappings/hst/foo.pmap'" in out


@mark.hst
@mark.misc
def test_check_archive_script(hst_shared_cache_state, caplog):
    with caplog.at_level(logging.INFO, logger="CRDS"):
        check_archive.CheckArchiveScript("crds.misc.check_archive --files foo.map hst.pmap")()
        out = caplog.text
    expected = """Mapping URL: 'https://hst-crds.stsci.edu/unchecked_get/mappings/hst/'
Reference URL: 'https://hst-crds.stsci.edu/unchecked_get/references/hst/'
File 'foo.map' failed HTTP HEAD with code = 404 from 'https://hst-crds.stsci.edu/unchecked_get/references/hst/foo.map'
1 errors
0 warnings"""
    for line in expected.splitlines():
        assert line in out
