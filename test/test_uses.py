"""This module contains doctests and unit tests which exercise the crds.uses
module that identifies mappings that reference a file.
"""
from pytest import mark

from crds.core import log

from crds.uses import UsesScript

# For log capture tests, need to ensure that the CRDS
# logger propagates its events.
log.THE_LOGGER.logger.propagate = True


@mark.hst
@mark.uses
@mark.slow
def test_uses_findall_mappings_using_reference(hst_shared_cache_state, capsys):
    """Test finding maps where a reference is located"""

    argv = 'crds.uses --files v2e20129l_flat.fits'
    UsesScript(argv=argv)()
    out = capsys.readouterr().out

    expected = """
    hst.pmap
    hst_0001.pmap
    hst_0002.pmap
    hst_0003.pmap
    hst_0004.pmap
    hst_0005.pmap
    hst_0006.pmap
    hst_cos.imap
    hst_cos_0001.imap
    hst_cos_flatfile.rmap
    hst_cos_flatfile_0002.rmap
    """
    for msg in expected.splitlines():
        assert msg.strip() in out


@mark.hst
@mark.uses
@mark.slow
def test_uses_rmaps(hst_shared_cache_state, capsys):
    """Test finding maps where an rmap is used"""

    argv = 'crds.uses --files hst_cos_flatfile.rmap hst_acs_darkfile.rmap --include-used'
    UsesScript(argv=argv)()
    out = capsys.readouterr().out

    expected = """
    hst_cos_flatfile.rmap hst.pmap
    hst_cos_flatfile.rmap hst_0001.pmap
    hst_cos_flatfile.rmap hst_0002.pmap
    hst_cos_flatfile.rmap hst_cos.imap
    hst_acs_darkfile.rmap hst.pmap
    hst_acs_darkfile.rmap hst_0001.pmap
    hst_acs_darkfile.rmap hst_0002.pmap
    hst_acs_darkfile.rmap hst_0003.pmap
    hst_acs_darkfile.rmap hst_0004.pmap
    hst_acs_darkfile.rmap hst_0005.pmap
    hst_acs_darkfile.rmap hst_0006.pmap
    hst_acs_darkfile.rmap hst_0007.pmap
    hst_acs_darkfile.rmap hst_0008.pmap
    hst_acs_darkfile.rmap hst_0009.pmap
    hst_acs_darkfile.rmap hst_0010.pmap
    hst_acs_darkfile.rmap hst_0011.pmap
    hst_acs_darkfile.rmap hst_0012.pmap
    hst_acs_darkfile.rmap hst_0013.pmap
    hst_acs_darkfile.rmap hst_0014.pmap
    hst_acs_darkfile.rmap hst_acs.imap
    hst_acs_darkfile.rmap hst_acs_0001.imap
    """
    for msg in expected.splitlines():
        assert msg.strip() in out


@mark.hst
@mark.uses
@mark.slow
def test_uses_imap(hst_shared_cache_state, capsys):
    """TEst finding maps where an imap is used"""

    argv = 'crds.uses --files hst_cos.imap'
    UsesScript(argv=argv)()
    out = capsys.readouterr().out

    expected = """
    hst.pmap
    hst_0001.pmap
    hst_0002.pmap
    """
    for msg in expected.splitlines():
        assert msg.strip() in out
