""" Test crds.misc.uniqname
"""
from pathlib import Path
from pytest import mark
import shutil

from crds.core import log

from crds.misc import uniqname
from crds.misc.uniqname import UniqnameScript

# For log capture tests, need to ensure that the CRDS
# logger propagates its events.
log.THE_LOGGER.logger.propagate = True

@mark.hst
@mark.misc
@mark.uniqname
def test_synphot_uniqname(hst_shared_cache_state, caplog):
    """Compute diffs for two .pmap's:"""
    name = UniqnameScript("crds.misc.uniqname --dry-run --files data/16n1832tm_tmc.fits")()
    out = caplog.text

    assert name.endswith('_tmc.fits')

    expected = """Would rename 'data/16n1832tm_tmc.fits' --> 'data/
    m_tmc.fits'"""
    for msg in expected.splitlines():
        assert msg.strip() in out


@mark.hst
@mark.misc
@mark.uniqname
def test_cdbs_uniqname(hst_shared_cache_state, hst_data, caplog, tmpdir):
    """Compute diffs for two .pmap's"""
    fname = 's7g1700gl_dead.fits'
    path = tmpdir / fname
    shutil.copy(Path(hst_data) / fname, path)
    name = UniqnameScript(f'crds.misc.uniqname --standard --files {path}')()
    out = caplog.text

    expected = f"""Rewriting '{str(path)}' --> '{name}'"""
    for msg in expected.splitlines():
        assert msg.strip() in out

    name1 = uniqname.uniqname(name)
    out = caplog.text
    expected = f"""Rewriting '{name}' --> '{name1}'"""
    for msg in expected.splitlines():
        assert msg.strip() in out


@mark.hst
@mark.misc
@mark.uniqname
def test_has_checksum(hst_shared_cache_state, hst_data, caplog):
    """Compute diffs for two .pmap's"""

    hst_data = Path(hst_data)
    assert not uniqname.has_checksum(hst_data / "16n1832tm_tmc.fits")
    assert uniqname.has_checksum(hst_data / "s7g1700gl_dead_good_xsum.fits")
