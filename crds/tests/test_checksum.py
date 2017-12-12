"""
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os
import shutil
import doctest

from crds.core import log, utils
from crds import tests, data_file
from crds.tests import test_config

from crds.refactoring import checksum
from crds.refactoring.checksum import ChecksumScript

def dt_checksum_script_add():
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

def dt_checksum_script_remove():
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

def dt_checksum_script_verify_good():
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

def dt_checksum_script_verify_bad():
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
