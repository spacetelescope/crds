from crds.core import pysh
from crds.refactoring import newcontext
from pytest import mark
from crds.core import log
import logging
log.THE_LOGGER.logger.propagate=True

@mark.hst
@mark.refactoring
@mark.newcontext
def test_fake_name(default_shared_state, hst_data):
    out = newcontext.fake_name(f"{hst_data}/hst.pmap")
    assert out == './hst_0003.pmap'
    out = newcontext.fake_name(f"{hst_data}/hst_cos_0001.imap")
    assert out == './hst_cos_0001.imap'
    out = newcontext.fake_name(f"{hst_data}/hst_cos_deadtab_9999.rmap")
    assert out ==  './hst_cos_deadtab_10000.rmap'


@mark.hst
@mark.refactoring
@mark.newcontext
def test_new_context(default_shared_state, hst_data, caplog):
    with caplog.at_level(logging.INFO, logger="CRDS"):
        newcontext.NewContextScript(
            f"newcontext.py {hst_data}/hst.pmap {hst_data}/hst_cos_deadtab_9999.rmap \
{hst_data}/hst_acs_imphttab_9999.rmap")()
        out = caplog.text
    pysh.sh("rm \./*\.[pir]map")
    out_to_check = """
    Replaced 'hst_acs_imphttab.rmap' with
    hst_acs_imphttab_9999.rmap' for 'imphttab' in
    hst_acs.imap' producing
    hst_acs_10000.imap'
    Replaced 'hst_cos_deadtab.rmap' with
    hst_cos_deadtab_9999.rmap' for 'deadtab' in
    hst_cos.imap' producing
    hst_cos_0001.imap'
    Replaced
    hst_acs.imap' with
    hst_acs_10000.imap' for 'ACS' in
    hst.pmap' producing
    hst_0003.pmap'
    Replaced
    hst_cos.imap' with
    hst_cos_0001.imap' for 'COS' in
    hst.pmap' producing
    hst_0003.pmap'
    Adjusting name 'hst_0003.pmap' derived_from 'hst.pmap' in
    hst_0003.pmap'
    Adjusting name 'hst_acs_10000.imap' derived_from 'hst_acs.imap' in
    hst_acs_10000.imap'
    Adjusting name 'hst_cos_0001.imap' derived_from 'hst_cos.imap' in
    hst_cos_0001.imap'"""
    for msg in out_to_check.splitlines():
        assert msg.strip() in out
