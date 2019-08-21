"""
Tests for crds.misc.check_archive which is nominally used to check the
archive for file availability as an alternative to a true ACK from the
archive when their processing is complete.  Also supplies a function API
used by the server to determine and cache file availability status in the
CRDS catalog.
"""
import sys
import os
import time
import multiprocessing
import tempfile

# ===================================================================

from crds.core import log, config
from crds.misc import check_archive

# ===================================================================

from . import test_config

# ===================================================================

def dt_check_archive_file_api_true():
    """
    >>> old_state = test_config.setup()

    >> check_archive.file_available("hst.pmap")     XXXX DISABLED
    True

    >>> test_config.cleanup(old_state)
    """

def dt_check_archive_file_api_false():
    """
    >>> old_state = test_config.setup()

    >> check_archive.file_available("foo.pmap")     XXXX DISABLED
    CRDS - ERROR -  File 'foo.pmap' failed HTTP HEAD with code = 404 from '.../foo.pmap'
    False

    >>> test_config.cleanup(old_state)
    """

def dt_check_archive_script():
        """
    >>> old_state = test_config.setup()
    >>> check_archive.CheckArchiveScript("crds.misc.check_archive --files foo.map hst.pmap")()
    CRDS - INFO -  Mapping URL: '.../mappings/hst/'
    CRDS - INFO -  Reference URL: '.../references/hst/'
    CRDS - ERROR -  File 'foo.map' failed HTTP HEAD with code = 404 from '.../foo.map'
    CRDS - INFO -        2 files at    ... files-per-second
    CRDS - INFO -  1 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  3 infos
    >>> test_config.cleanup(old_state)
    """

# ==================================================================

def main():
    """Run module tests,  for now just doctests only."""
    from crds.tests import test_check_archive, tstmod
    return tstmod(test_check_archive)

if __name__ == "__main__":
    print(main())
