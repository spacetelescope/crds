from pytest import mark
import logging

# ==================================================================================

from crds.core import log
from crds.core import substitutions

# ==================================================================================

log.THE_LOGGER.logger.propagate=True
log.set_verbose(50)


@mark.hst
@mark.substitutions
@mark.core
def test_substitutions_validate_hst(hst_serverless_state, caplog):
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        substitutions.validate_substitutions("hst-operational")
        out = caplog.text
    # Using CACHED CRDS reference assignment rules last updated on '...'
    expected_out =""" For 'acs' parameter 'LRFWAVE' with value 'between 3710 3826' is unchecked.
 For 'acs' parameter 'LRFWAVE' with value 'between 3826 3936' is unchecked.
 For 'acs' parameter 'LRFWAVE' with value 'between 3936 4051' is unchecked.
 For 'acs' parameter 'LRFWAVE' with value 'between 4051 4167' is unchecked.
 For 'acs' parameter 'LRFWAVE' with value 'between 4167 4296' is unchecked.
 For 'acs' parameter 'LRFWAVE' with value 'between 4296 4421' is unchecked.
 For 'acs' parameter 'LRFWAVE' with value 'between 4421 4554' is unchecked.
 For 'acs' parameter 'LRFWAVE' with value 'between 4554 4686' is unchecked.
 For 'acs' parameter 'LRFWAVE' with value 'between 4686 4821' is unchecked.
 For 'acs' parameter 'LRFWAVE' with value 'between 4821 5271' is unchecked.
 For 'acs' parameter 'LRFWAVE' with value 'between 5271 5751' is unchecked.
 For 'acs' parameter 'LRFWAVE' with value 'between 5751 6271' is unchecked.
 For 'acs' parameter 'LRFWAVE' with value 'between 6271 6851' is unchecked.
 For 'acs' parameter 'LRFWAVE' with value 'between 6851 7471' is unchecked.
 For 'acs' parameter 'LRFWAVE' with value 'between 7471 8161' is unchecked.
 For 'acs' parameter 'LTV1' with value 'ANY' is unchecked.
 For 'acs' parameter 'LTV2' with value 'ANY' is unchecked.
 For 'acs' parameter 'NAXIS1' with value 'ANY' is unchecked.
 For 'acs' parameter 'NAXIS2' with value 'ANY' is unchecked.
 For 'acs' parameter 'RAW_LTV1' with value 'ANY' is unchecked.
 For 'acs' parameter 'RAW_LTV2' with value 'ANY' is unchecked.
 Instrument 'nicmos' has no substitutions.
 Instrument 'synphot' has no substitutions.
 For 'wfc3' parameter 'FILTER' with value 'BLANK' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'CLEAR' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F093W' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F098M' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F105W' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F110W' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F125W' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F126N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F127M' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F128N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F130N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F132N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F139M' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F140W' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F153M' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F160W' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F164N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F167N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F200LP' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F218W' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F225W' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F275W' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F280N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F300X' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F336W' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F343N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F350LP' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F373N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F390M' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F390W' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F395N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F410M' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F438W' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F467M' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F469N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F475W' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F475X' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F487N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F502N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F547M' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F555W' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F588N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F600LP' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F606W' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F621M' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F625W' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F631N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F645N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F656N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F657N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F658N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F665N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F673N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F680N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F689M' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F763M' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F775W' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F814W' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F845M' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F850LP' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'F953N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'FQ232N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'FQ243N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'FQ378N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'FQ387N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'FQ422M' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'FQ436N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'FQ437N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'FQ492N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'FQ508N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'FQ575N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'FQ619N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'FQ634N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'FQ672N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'FQ674N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'FQ727N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'FQ750N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'FQ889N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'FQ906N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'FQ924N' is unchecked.
 For 'wfc3' parameter 'FILTER' with value 'FQ937N' is unchecked.
 For 'wfc3' parameter 'SAMP_SEQ' with value 'MIF1200' is unchecked.
 For 'wfc3' parameter 'SAMP_SEQ' with value 'MIF1500' is unchecked.
 For 'wfc3' parameter 'SAMP_SEQ' with value 'MIF600' is unchecked.
 For 'wfc3' parameter 'SAMP_SEQ' with value 'MIF900' is unchecked.
 For 'wfc3' parameter 'SAMP_SEQ' with value 'NONE' is unchecked.
 For 'wfc3' parameter 'SAMP_SEQ' with value 'RAPID' is unchecked.
 For 'wfc3' parameter 'SAMP_SEQ' with value 'SPARS10' is unchecked.
 For 'wfc3' parameter 'SAMP_SEQ' with value 'SPARS100' is unchecked.
 For 'wfc3' parameter 'SAMP_SEQ' with value 'SPARS200' is unchecked.
 For 'wfc3' parameter 'SAMP_SEQ' with value 'SPARS25' is unchecked.
 For 'wfc3' parameter 'SAMP_SEQ' with value 'SPARS350' is unchecked.
 For 'wfc3' parameter 'SAMP_SEQ' with value 'SPARS50' is unchecked.
 For 'wfc3' parameter 'SAMP_SEQ' with value 'STEP100' is unchecked.
 For 'wfc3' parameter 'SAMP_SEQ' with value 'STEP200' is unchecked.
 For 'wfc3' parameter 'SAMP_SEQ' with value 'STEP25' is unchecked.
 For 'wfc3' parameter 'SAMP_SEQ' with value 'STEP400' is unchecked.
 For 'wfc3' parameter 'SAMP_SEQ' with value 'STEP50' is unchecked.
 For 'wfc3' parameter 'SAMP_SEQ' with value 'UNKNOWN' is unchecked.
 Instrument 'wfpc2' has no substitutions."""
    for msg in expected_out.splitlines():
        assert msg.strip() in out
    

@mark.jwst
@mark.substitutions
@mark.core
def test_substitutions_validate_jwst(jwst_serverless_state, caplog):
    jwst_serverless_state.cache = None
    jwst_serverless_state.obs = None
    jwst_serverless_state.config_setup()
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        substitutions.validate_substitutions("jwst-operational")
        out = caplog.text
    expected_out = """ Instrument 'fgs' has no substitutions.
 Instrument 'miri' has no substitutions.
 Instrument 'nircam' has no substitutions.
 Instrument 'niriss' has no substitutions.
 Instrument 'nirspec' has no substitutions.
 Instrument 'system' has no substitutions."""
    for msg in expected_out.splitlines():
        assert msg.strip() in out
    

@mark.roman
@mark.substitutions
@mark.core
def test_substitutions_validate_roman(roman_test_cache_state, caplog):
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        substitutions.validate_substitutions("roman-operational")
        out = caplog.text
    expected_out = """ Instrument 'wfi' has no substitutions."""
    for msg in expected_out.splitlines():
        assert msg.strip() in out
