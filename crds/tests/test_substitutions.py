import os
import tempfile

# ==================================================================================
import numpy as np

from nose.tools import assert_raises, assert_true

# ==================================================================================

from crds.core import utils, log, exceptions
from crds.core import substitutions
from crds import hst, jwst

from crds.tests import test_config

# ==================================================================================

def substitutions_validate_hst():
    """
    >>> old_state = test_config.setup(url="https://hst-serverless-mode.stsci.edu")
    >>> old_verbose = log.set_verbose()
    >>> substitutions.validate_substitutions("hst-operational")
    CRDS - DEBUG -  Using CACHED CRDS reference assignment rules last updated on '...'
    CRDS - DEBUG -  For 'acs' parameter 'LRFWAVE' with value 'between 3710 3826' is unchecked.
    CRDS - DEBUG -  For 'acs' parameter 'LRFWAVE' with value 'between 3826 3936' is unchecked.
    CRDS - DEBUG -  For 'acs' parameter 'LRFWAVE' with value 'between 3936 4051' is unchecked.
    CRDS - DEBUG -  For 'acs' parameter 'LRFWAVE' with value 'between 4051 4167' is unchecked.
    CRDS - DEBUG -  For 'acs' parameter 'LRFWAVE' with value 'between 4167 4296' is unchecked.
    CRDS - DEBUG -  For 'acs' parameter 'LRFWAVE' with value 'between 4296 4421' is unchecked.
    CRDS - DEBUG -  For 'acs' parameter 'LRFWAVE' with value 'between 4421 4554' is unchecked.
    CRDS - DEBUG -  For 'acs' parameter 'LRFWAVE' with value 'between 4554 4686' is unchecked.
    CRDS - DEBUG -  For 'acs' parameter 'LRFWAVE' with value 'between 4686 4821' is unchecked.
    CRDS - DEBUG -  For 'acs' parameter 'LRFWAVE' with value 'between 4821 5271' is unchecked.
    CRDS - DEBUG -  For 'acs' parameter 'LRFWAVE' with value 'between 5271 5751' is unchecked.
    CRDS - DEBUG -  For 'acs' parameter 'LRFWAVE' with value 'between 5751 6271' is unchecked.
    CRDS - DEBUG -  For 'acs' parameter 'LRFWAVE' with value 'between 6271 6851' is unchecked.
    CRDS - DEBUG -  For 'acs' parameter 'LRFWAVE' with value 'between 6851 7471' is unchecked.
    CRDS - DEBUG -  For 'acs' parameter 'LRFWAVE' with value 'between 7471 8161' is unchecked.
    CRDS - DEBUG -  For 'acs' parameter 'LTV1' with value 'ANY' is unchecked.
    CRDS - DEBUG -  For 'acs' parameter 'LTV2' with value 'ANY' is unchecked.
    CRDS - DEBUG -  For 'acs' parameter 'NAXIS1' with value 'ANY' is unchecked.
    CRDS - DEBUG -  For 'acs' parameter 'NAXIS2' with value 'ANY' is unchecked.
    CRDS - DEBUG -  Instrument 'nicmos' has no substitutions.
    CRDS - DEBUG -  Instrument 'synphot' has no substitutions.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'BLANK' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'CLEAR' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F093W' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F098M' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F105W' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F110W' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F125W' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F126N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F127M' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F128N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F130N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F132N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F139M' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F140W' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F153M' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F160W' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F164N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F167N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F200LP' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F218W' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F225W' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F275W' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F280N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F300X' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F336W' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F343N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F350LP' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F373N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F390M' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F390W' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F395N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F410M' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F438W' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F467M' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F469N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F475W' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F475X' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F487N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F502N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F547M' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F555W' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F588N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F600LP' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F606W' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F621M' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F625W' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F631N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F645N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F656N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F657N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F658N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F665N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F673N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F680N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F689M' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F763M' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F775W' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F814W' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F845M' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F850LP' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'F953N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'FQ232N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'FQ243N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'FQ378N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'FQ387N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'FQ422M' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'FQ436N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'FQ437N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'FQ492N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'FQ508N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'FQ575N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'FQ619N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'FQ634N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'FQ672N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'FQ674N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'FQ727N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'FQ750N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'FQ889N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'FQ906N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'FQ924N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'FILTER' with value 'FQ937N' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'SAMP_SEQ' with value 'MIF1200' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'SAMP_SEQ' with value 'MIF1500' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'SAMP_SEQ' with value 'MIF600' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'SAMP_SEQ' with value 'MIF900' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'SAMP_SEQ' with value 'NONE' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'SAMP_SEQ' with value 'RAPID' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'SAMP_SEQ' with value 'SPARS10' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'SAMP_SEQ' with value 'SPARS100' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'SAMP_SEQ' with value 'SPARS200' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'SAMP_SEQ' with value 'SPARS25' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'SAMP_SEQ' with value 'SPARS350' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'SAMP_SEQ' with value 'SPARS50' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'SAMP_SEQ' with value 'STEP100' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'SAMP_SEQ' with value 'STEP200' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'SAMP_SEQ' with value 'STEP25' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'SAMP_SEQ' with value 'STEP400' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'SAMP_SEQ' with value 'STEP50' is unchecked.
    CRDS - DEBUG -  For 'wfc3' parameter 'SAMP_SEQ' with value 'UNKNOWN' is unchecked.
    CRDS - DEBUG -  Instrument 'wfpc2' has no substitutions.
    >>> _ = log.set_verbose(old_verbose)
    >>> test_config.cleanup(old_state)
    """

def substitutions_validate_jwst():
    """
    >>> old_state = test_config.setup(url="https://jwst-serverless-mode.stsci.edu")
    >>> old_verbose = log.set_verbose()
    >>> substitutions.validate_substitutions("jwst-operational")  # doctest: +ELLIPSIS
    CRDS - DEBUG -  Using CACHED CRDS reference assignment rules last updated on '...'
    CRDS - DEBUG -  Instrument 'fgs' has no substitutions.
    CRDS - DEBUG -  Instrument 'miri' has no substitutions.
    CRDS - DEBUG -  Instrument 'nircam' has no substitutions.
    CRDS - DEBUG -  Instrument 'niriss' has no substitutions.
    CRDS - DEBUG -  Instrument 'nirspec' has no substitutions.
    CRDS - DEBUG -  Instrument 'system' has no substitutions.
    >>> _ = log.set_verbose(old_verbose)
    >>> test_config.cleanup(old_state)
    """

def substitutions_validate_roman():
    """
    >>> old_state = test_config.setup(url="https://roman-crds-serverless.stsci.edu", cache=test_config.CRDS_TESTING_CACHE)
    >>> old_verbose = log.set_verbose()
    >>> substitutions.validate_substitutions("roman-operational")  # doctest: +ELLIPSIS
    CRDS - DEBUG -  Using CACHED CRDS reference assignment rules last updated on '...'
    CRDS - DEBUG -  Instrument 'wfi' has no substitutions.
    >>> _ = log.set_verbose(old_verbose)
    >>> test_config.cleanup(old_state)
    """
# ==================================================================================

def main():
    """Run module tests,  for now just doctests only."""
    from crds.tests import test_substitutions, tstmod
    return tstmod(test_substitutions)

if __name__ == "__main__":
    print(main())
