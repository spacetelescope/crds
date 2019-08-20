"""This module contains doctests and unit tests which exercise refactoring
code,  modules used to automatically update mappings.

"""
import os
from pprint import pprint as pp

import crds
from crds.core import log, exceptions
from crds import data_file, diff

from crds.diff import DiffScript
from crds.bestrefs import BestrefsScript
from crds.refactoring import refactor
from crds.refactoring.refactor import RefactorScript
from crds.certify import CertifyScript
from crds.tests import test_config

from nose.tools import assert_raises, assert_true

# ==================================================================================

def dt_or_bars_certify_bad_keyword():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> CertifyScript("crds.certify data/jwst_miri_ipc.bad-keyword.fits --comparison-context jwst_0361.pmap")() # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/jwst_miri_ipc.bad-keyword.fits' (1/1) as 'FITS' relative to context 'jwst_0361.pmap'
    CRDS - INFO -  FITS file 'jwst_miri_ipc.bad-keyword.fits' conforms to FITS standards.
    CRDS - WARNING -  CRDS-pattern-like keyword 'P_DETEC' w/o CRDS translation to corresponding dataset keyword.
    CRDS - INFO -  Pattern-like keyword 'P_DETEC' may be misspelled or missing its translation in CRDS.  Pattern will not be used.
    CRDS - INFO -  The translation for 'P_DETEC' can be defined in crds.jwst.locate or rmap header reference_to_dataset field.
    CRDS - INFO -  If this is not a pattern keyword, adding a translation to 'not-a-pattern' will suppress this warning.
    CRDS - WARNING -  Missing suggested keyword 'META.MODEL_TYPE [DATAMODL]'
    CRDS - INFO -  Checking JWST datamodels.
    CRDS - WARNING -  NoTypeWarning : ...jwst.datamodels.util : model_type not found...
    CRDS - INFO -  ########################################
    CRDS - INFO -  0 errors
    CRDS - INFO -  3 warnings
    CRDS - INFO -  8 infos
    0
    >>> test_config.cleanup(old_state)
    """

def dt_or_bars_certify_bad_value():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> CertifyScript("crds.certify data/jwst_miri_ipc.bad-value.fits --comparison-context jwst_0361.pmap")() # doctest: +ELLIPSIS
    CRDS - INFO -  ########################################
    CRDS - INFO -  Certifying 'data/jwst_miri_ipc.bad-value.fits' (1/1) as 'FITS' relative to context 'jwst_0361.pmap'
    CRDS - INFO -  FITS file 'jwst_miri_ipc.bad-value.fits' conforms to FITS standards.
    CRDS - INFO -  Setting 'META.INSTRUMENT.BAND [BAND]' = None to value of 'P_BAND' = 'LONG'
    CRDS - INFO -  Setting 'META.INSTRUMENT.DETECTOR [DETECTOR]' = 'MIRIMAGE' to value of 'P_DETECT' = 'MIRIFUSHORT|FOO|'
    CRDS - ERROR -  instrument='MIRI' type='IPC' data='data/jwst_miri_ipc.bad-value.fits' ::  Checking 'META.INSTRUMENT.DETECTOR [DETECTOR]' : Value 'FOO' is not one of ['ANY', 'MIRIFULONG', 'MIRIFUSHORT', 'MIRIMAGE', 'N/A']
    CRDS - WARNING -  Missing suggested keyword 'META.MODEL_TYPE [DATAMODL]'
    CRDS - INFO -  Checking JWST datamodels.
    CRDS - WARNING -  NoTypeWarning : ...jwst.datamodels.util : model_type not found...
    CRDS - INFO -  ########################################
    CRDS - INFO -  1 errors
    CRDS - INFO -  2 warnings
    CRDS - INFO -  7 infos
    1
    >>> test_config.cleanup(old_state)
    """

def dt_or_bars_refactor_add_file():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> RefactorScript("crds.refactor insert data/jwst_miri_ipc_0002.rmap ./jwst_miri_ipc_0003.add.rmap data/jwst_miri_ipc_0003.add.fits")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Inserting jwst_miri_ipc_0003.add.fits into 'jwst_miri_ipc_0002.rmap'
    CRDS - INFO -  Setting 'META.INSTRUMENT.BAND [BAND]' = 'UNDEFINED' to value of 'P_BAND' = 'SHORT | MEDIUM |'
    CRDS - INFO -  Setting 'META.INSTRUMENT.DETECTOR [DETECTOR]' = 'MIRIMAGE' to value of 'P_DETECT' = 'MIRIFUSHORT|MIRIFULONG|'
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  3 infos
    0

    >>> diff.DiffScript("crds.diff data/jwst_miri_ipc_0002.rmap ./jwst_miri_ipc_0003.add.rmap")()
    (('data/jwst_miri_ipc_0002.rmap', './jwst_miri_ipc_0003.add.rmap'), ('MIRIFULONG|MIRIFUSHORT', 'MEDIUM|SHORT'), ('2014-01-01', '00:00:00'), 'added Match rule for jwst_miri_ipc_0003.add.fits')
    1

    >>> pp(refactor.rmap_check_modifications("data/jwst_miri_ipc_0002.rmap", "./jwst_miri_ipc_0003.add.rmap", "none", "data/jwst_miri_ipc_0003.add.fits", expected=("add_rule",)))
    True

    >>> _ = os.system("rm ./*.rmap")

    >>> test_config.cleanup(old_state)
    """

def dt_or_bars_refactor_replace_file():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> RefactorScript("crds.refactor insert data/jwst_miri_ipc_0002.rmap ./jwst_miri_ipc_0004.replace.rmap data/jwst_miri_ipc_0004.replace.fits")()  # doctest: +ELLIPSIS
    CRDS - INFO -  Inserting jwst_miri_ipc_0004.replace.fits into 'jwst_miri_ipc_0002.rmap'
    CRDS - INFO -  Setting 'META.INSTRUMENT.BAND [BAND]' = 'UNDEFINED' to value of 'P_BAND' = 'LONG |'
    CRDS - INFO -  Setting 'META.INSTRUMENT.DETECTOR [DETECTOR]' = 'MIRIMAGE' to value of 'P_DETECT' = 'MIRIFULONG|'
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  3 infos
    0

    >>> diff.DiffScript("crds.diff data/jwst_miri_ipc_0002.rmap ./jwst_miri_ipc_0004.replace.rmap")()
    (('data/jwst_miri_ipc_0002.rmap', './jwst_miri_ipc_0004.replace.rmap'), ('MIRIFULONG', 'LONG'), ('1900-01-01', '00:00:00'), 'replaced jwst_miri_ipc_0004.fits with jwst_miri_ipc_0004.replace.fits')
    1

    >>> pp(refactor.rmap_check_modifications("data/jwst_miri_ipc_0002.rmap", "./jwst_miri_ipc_0004.replace.rmap", "jwst_miri_ipc_0004.fits", "data/jwst_miri_ipc_0004.replace.fits", expected=("replace",)))
    True

    >>> refactor.rmap_check_modifications("data/jwst_miri_ipc_0002.rmap", "./jwst_miri_ipc_0004.replace.rmap", "data/jwst_miri_ipc_0004.fits", "data/jwst_miri_ipc_0004.replace.fits",
    ...                          expected=("replace",))
    True

    >>> _ = os.system("rm ./*.rmap")

    >>> test_config.cleanup(old_state)
    """

# ==================================================================================


def tst():
    """Run module tests,  for now just doctests only."""
    from crds.tests import test_or_bars, tstmod
    return tstmod(test_or_bars)

if __name__ == "__main__":
    print(tst())
