""" Test crds.misc.uniqname
"""
from pathlib import Path
from pytest import mark

from crds.core import log

from crds.misc import uniqname
from crds.misc.uniqname import UniqnameScript

# For log capture tests, need to ensure that the CRDS
# logger propagates its events.
log.THE_LOGGER.logger.propagate = True


@mark.misc
@mark.uniqname
def test_synphot_uniqname(default_shared_state, caplog):
    """Compute diffs for two .pmap's:"""

    name = UniqnameScript("crds.misc.uniqname --dry-run --files data/16n1832tm_tmc.fits")()
    out = caplog.text

    assert name.endswith('_tmc.fits')

    expected = """Would rename 'data/16n1832tm_tmc.fits' --> 'data/
    m_tmc.fits'"""
    for msg in expected.splitlines():
        assert msg.strip() in out


@mark.misc
@mark.uniqname
def test_cdbs_uniqname():
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

@mark.misc
@mark.uniqname
def test_has_checksum():
    """
    Compute diffs for two .pmap's:

    >>> old_state = test_config.setup()
    >>> uniqname.has_checksum("data/16n1832tm_tmc.fits")  # doctest: +ELLIPSIS
    False
    >>> uniqname.has_checksum("data/s7g1700gl_dead_good_xsum.fits") # doctest: +ELLIPSIS
    True
    >>> test_config.cleanup(old_state)
    """
