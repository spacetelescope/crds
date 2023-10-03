from crds.core import pysh
from crds.refactoring import newcontext
from pytest import mark
from crds.core import log
import logging
log.THE_LOGGER.logger.propagate=True


@mark.newcontext
def test_fake_name(default_shared_state, hst_data):
    out = newcontext.fake_name(f"{hst_data}/hst.pmap")
    assert out == './hst_0003.pmap'
    out = newcontext.fake_name(f"{hst_data}/hst_cos_0001.imap")
    assert out == './hst_cos_0001.imap'
    out = newcontext.fake_name(f"{hst_data}/hst_cos_deadtab_9999.rmap")
    assert out ==  './hst_cos_deadtab_10000.rmap'
    default_shared_state.cleanup()

@mark.newcontext
def test_new_context(default_shared_state, hst_data, caplog):
    with caplog.at_level(logging.INFO, logger="CRDS"):
        newcontext.NewContextScript(
            f"newcontext.py {hst_data}/hst.pmap {hst_data}/hst_cos_deadtab_9999.rmap \
{hst_data}/hst_acs_imphttab_9999.rmap")()
        out = caplog.text
    pysh.sh("rm \./*\.[pir]map")
    out_to_check = """Replaced 'hst_cos_deadtab.rmap' with \
'/home/runner/work/crds/crds/test/data/hst/hst_cos_deadtab_9999.rmap' for 'deadtab' in 'test/data/hst/hst_cos.imap' \
producing './hst_cos_0001.imap'"""
    assert out_to_check in out
    out_to_check = """Replaced 'test/data/hst/hst_acs.imap' with './hst_acs_10000.imap' for 'ACS' in \
'/home/runner/work/crds/crds/test/data/hst/hst.pmap' producing './hst_0003.pmap'"""
    assert out_to_check in out
    out_to_check = """Replaced 'test/data/hst/hst_cos.imap' with './hst_cos_0001.imap' for 'COS' in \
'/home/runner/work/crds/crds/test/data/hst/hst.pmap' producing './hst_0003.pmap'"""
    assert out_to_check in out
    out_to_check = """Adjusting name 'hst_0003.pmap' derived_from 'hst.pmap' in './hst_0003.pmap'"""
    assert out_to_check in out
    out_to_check = """Adjusting name 'hst_acs_10000.imap' derived_from 'hst_acs.imap' in './hst_acs_10000.imap'"""
    assert out_to_check in out
    out_to_check = """Adjusting name 'hst_cos_0001.imap' derived_from 'hst_cos.imap' in './hst_cos_0001.imap'"""
    assert out_to_check in out
    default_shared_state.cleanup()




