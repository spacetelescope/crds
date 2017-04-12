from __future__ import division # confidence high
from __future__ import with_statement
from __future__ import print_function
from __future__ import absolute_import

# ==================================================================================

import os

# ==================================================================================
import numpy as np

from nose.tools import assert_raises, assert_true

# ==================================================================================

from crds.core import utils, log, exceptions
from crds.io import factory

from crds.tests import test_config

# ==================================================================================

def test_get_fits_type():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> factory.get_filetype("data/valid.fits")
    'fits'
    >>> test_config.cleanup(old_state)
    """

def test_get_fits_type_opaque():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> factory.get_filetype("data/opaque_fts.tmp")
    'fits'
    >>> test_config.cleanup(old_state)
    """

def test_get_asdf_type():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> factory.get_filetype("data/valid.asdf")
    'asdf'
    >>> test_config.cleanup(old_state)
    """

def test_get_fits_type_opaque():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> factory.get_filetype("data/opaque_asd.tmp")
    'asdf'
    >>> test_config.cleanup(old_state)
    """
# ==================================================================================

def main():
    """Run module tests,  for now just doctests only."""
    from crds.tests import test_io, tstmod
    return tstmod(test_io)

if __name__ == "__main__":
    print(main())

