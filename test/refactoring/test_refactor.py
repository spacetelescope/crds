"""
This module contains doctests and unit tests which exercise refactoring
code,  modules used to automatically update mappings.
"""
from pytest import mark
import os
import logging
from crds.core import log
from crds import diff
from crds.refactoring.refactor import RefactorScript, rmap_check_modifications

log.THE_LOGGER.logger.propagate = True

@mark.hst
@mark.refactoring
@mark.refactor
def test_refactor_add_files(default_shared_state, hst_data, test_temp_dir, caplog, capsys):
    with caplog.at_level(logging.INFO, logger="CRDS"):
        RefactorScript(f"crds.refactor insert {hst_data}/hst_cos_deadtab.rmap {test_temp_dir}/hst_cos_deadtab_insert.rmap {hst_data}/s7g1700hl_dead.fits")()
        out = caplog.text
    expected_log = """Inserting s7g1700hl_dead.fits into 'hst_cos_deadtab.rmap'
0 errors
0 warnings""".splitlines()
    ndiffs = diff.DiffScript(f"crds.diff {hst_data}/hst_cos_deadtab.rmap {test_temp_dir}/hst_cos_deadtab_insert.rmap").run()
    caplog.clear()
    rmap_chk1 = rmap_check_modifications(f"{hst_data}/hst_cos_deadtab.rmap", f"{test_temp_dir}/hst_cos_deadtab_insert.rmap", "none", f"{hst_data}/s7g1700hl_dead.fits", expected=("add",))
    out2, _ = capsys.readouterr()
    expected_out = f"""(('{hst_data}/hst_cos_deadtab.rmap', '{test_temp_dir}/hst_cos_deadtab_insert.rmap'), ('FUV',), ('1997-10-01', '01:01:01'), 'added terminal s7g1700hl_dead.fits')"""
    with caplog.at_level(logging.INFO, logger="CRDS"):
        rmap_chk2 = rmap_check_modifications(f"{hst_data}/hst_cos_deadtab.rmap", f"{test_temp_dir}/hst_cos_deadtab_insert.rmap", f"{hst_data}/s7g1700gl_dead.fits", f"{hst_data}/s7g1700hl_dead.fits", expected=("replace",))
        out3 = caplog.text
    expected_err = f"""Expected one of ('replace',) but got 'add' from change (('{hst_data}/hst_cos_deadtab.rmap', '{test_temp_dir}/hst_cos_deadtab_insert.rmap'), ('FUV',), ('1997-10-01', '01:01:01'), "added terminal 's7g1700hl_dead.fits'")"""
    assert ndiffs == 1
    for line in expected_log:
        assert line in out
    assert rmap_chk1 is True
    assert expected_out in out2
    assert rmap_chk2 is False
    assert expected_err in out3


@mark.hst
@mark.refactoring
@mark.refactor
def test_refactor_delete_files(default_shared_state, hst_data, test_temp_dir, caplog, capsys):
    with caplog.at_level(logging.INFO, logger="CRDS"):
        RefactorScript(f"refactor.py delete {hst_data}/hst_cos_deadtab.rmap {test_temp_dir}/hst_cos_deadtab_delete.rmap {hst_data}/s7g1700gl_dead.fits")()
        out = caplog.text
    expected_log = f"""Deleting '{hst_data}/s7g1700gl_dead.fits' from 'hst_cos_deadtab.rmap'
0 errors
0 warnings""".splitlines()
    caplog.clear()
    ndiffs = diff.DiffScript(f"diff.py {hst_data}/hst_cos_deadtab.rmap {test_temp_dir}/hst_cos_deadtab_delete.rmap").run()
    out2, _ = capsys.readouterr()
    expected_out = f"""(('{hst_data}/hst_cos_deadtab.rmap', '{test_temp_dir}/hst_cos_deadtab_delete.rmap'), ('FUV',), ('1996-10-01', '00:00:00'), 'deleted Match rule for s7g1700gl_dead.fits')"""
    rmap_chk = rmap_check_modifications(f"{hst_data}/hst_cos_deadtab.rmap", f"{test_temp_dir}/hst_cos_deadtab_delete.rmap", "none", f"{hst_data}/s7g1700gl_dead.fits", expected=("delete_rule",))
    with caplog.at_level(logging.INFO, logger="CRDS"):
        RefactorScript(f"refactor.py delete {hst_data}/hst_cos_deadtab.rmap {test_temp_dir}/hst_cos_deadtab_delete2.rmap {hst_data}/foobar.fits")()
        out3 = caplog.text
    expected_err = f"""Deleting '{hst_data}/foobar.fits' from 'hst_cos_deadtab.rmap'
Refactoring operation FAILED : Terminal 'foobar.fits' could not be found and deleted.
1 errors
0 warnings""".splitlines()
    for line in expected_log:
        assert line in out
    assert ndiffs == 1
    assert expected_out in out2
    assert rmap_chk is True
    for line in expected_err:
        assert line in out3
    assert os.path.exists(f"{test_temp_dir}/hst_cos_deadtab_delete2.rmap") is False


@mark.hst
@mark.refactoring
@mark.refactor
def test_refactor_add_header(default_shared_state, hst_data, test_temp_dir, caplog, capsys):
    with caplog.at_level(logging.INFO, logger="CRDS"):
        RefactorScript(f"refactor.py set_header {hst_data}/hst_cos_deadtab.rmap {test_temp_dir}/hst_cos_deadtab_add_header.rmap new_key some new value")()
        out1 = caplog.text
    expected1 = """0 errors
0 warnings""".splitlines()
    caplog.clear()
    ndiffs = diff.DiffScript(f"diff.py {hst_data}/hst_cos_deadtab.rmap {test_temp_dir}/hst_cos_deadtab_add_header.rmap --include-header-diffs --hide-boring-diffs").run()
    out2, _ = capsys.readouterr()
    expected2 = f"""(('{hst_data}/hst_cos_deadtab.rmap', '{test_temp_dir}/hst_cos_deadtab_add_header.rmap'), "header added 'new_key' = 'some new value'")"""
    rmap_chk = rmap_check_modifications(f"{hst_data}/hst_cos_deadtab.rmap", f"{test_temp_dir}/hst_cos_deadtab_add_header.rmap", "none", "none", expected=("add_header",))
    for line in expected1:
        assert line in out1
    assert ndiffs == 1
    assert expected2 in out2
    assert rmap_chk is True


@mark.hst
@mark.refactoring
@mark.refactor
def test_refactor_replace_header(default_shared_state, hst_data, test_temp_dir, caplog, capsys):
    with caplog.at_level(logging.INFO, logger="CRDS"):
        RefactorScript(f"refactor.py set_header {hst_data}/hst_cos_deadtab.rmap {test_temp_dir}/hst_cos_deadtab_replace_header.rmap reffile_format something new")()
        out1 = caplog.text
    expected1 = """0 errors
0 warnings""".splitlines()
    caplog.clear()
    ndiffs = diff.DiffScript(f"diff.py {hst_data}/hst_cos_deadtab.rmap {test_temp_dir}/hst_cos_deadtab_replace_header.rmap --include-header-diffs --hide-boring-diffs").run()
    out2, _ = capsys.readouterr()
    expected2 = f"""(('{hst_data}/hst_cos_deadtab.rmap', '{test_temp_dir}/hst_cos_deadtab_replace_header.rmap'), "header replaced 'reffile_format' = 'table' with 'something new'")"""
    rmap_chk = rmap_check_modifications(f"{hst_data}/hst_cos_deadtab.rmap", f"{test_temp_dir}/hst_cos_deadtab_replace_header.rmap", "none", "none", expected=("replace_header",))
    for line in expected1:
        assert line in out1
    assert ndiffs == 1
    assert expected2 in out2
    assert rmap_chk is True


@mark.hst
@mark.refactoring
@mark.refactor
def test_refactor_del_header(default_shared_state, hst_data, test_temp_dir, caplog, capsys):
    with caplog.at_level(logging.INFO, logger="CRDS"):
        RefactorScript(f"refactor.py del_header {hst_data}/hst_cos_deadtab.rmap {test_temp_dir}/hst_cos_deadtab_del_header.rmap reffile_format")()
        out1 = caplog.text
    expected1 = """0 errors
0 warnings""".splitlines()
    caplog.clear()
    ndiffs = diff.DiffScript(f"diff.py {hst_data}/hst_cos_deadtab.rmap {test_temp_dir}/hst_cos_deadtab_del_header.rmap --include-header-diffs --hide-boring-diffs").run()
    out2, _ = capsys.readouterr()
    expected2 = f"""(('{hst_data}/hst_cos_deadtab.rmap', '{test_temp_dir}/hst_cos_deadtab_del_header.rmap'), "deleted header 'reffile_format' = 'table'")"""
    rmap_chk = rmap_check_modifications(f"{hst_data}/hst_cos_deadtab.rmap", f"{test_temp_dir}/hst_cos_deadtab_del_header.rmap", "none", "none", expected=("del_header",))
    for line in expected1:
        assert line in out1
    assert ndiffs == 1
    assert expected2 in out2
    assert rmap_chk is True


@mark.hst
@mark.refactoring
@mark.refactor
def test_refactor_bad_modify_count(default_shared_state, hst_data, caplog, capsys):
    with caplog.at_level(logging.INFO, logger="CRDS"):
        rmap_chk = rmap_check_modifications(f"{hst_data}/hst_cos_deadtab.rmap", f"{hst_data}/hst_cos_deadtab_9998.rmap", f"{hst_data}/s7g1700gl_dead.fits", f"{hst_data}/s7g1700hl_dead.fits", expected=("add",))
        out1 = caplog.text
    expected1 = f"""Expected one of ('add',) but got 'replace' from change (('{hst_data}/hst_cos_deadtab.rmap', '{hst_data}/hst_cos_deadtab_9998.rmap'), ('FUV',), ('1996-10-01', '00:00:00'), "replaced 's7g1700gl_dead.fits' with 's7g1700hl_dead.fits'")
Expected one of ('add',) but got 'replace' from change (('{hst_data}/hst_cos_deadtab.rmap', '{hst_data}/hst_cos_deadtab_9998.rmap'), ('NUV',), ('1996-10-01', '00:00:00'), "replaced 's7g1700ql_dead.fits' with 's7g1700hl_dead.fits'")""".splitlines()
    rmap_chk2 = rmap_check_modifications(f"{hst_data}/hst_cos_deadtab.rmap", f"{hst_data}/hst_cos_deadtab_9998.rmap", f"{hst_data}/s7g1700gl_dead.fits", f"{hst_data}/s7g1700hl_dead.fits", expected=("replace",))
    out2, _ = capsys.readouterr()
    expected2 = f"""Replacement COUNT DIFFERENCE replacing '{hst_data}/s7g1700gl_dead.fits' with '{hst_data}/s7g1700hl_dead.fits' in '{hst_data}/hst_cos_deadtab.rmap' 1 vs. 2"""
    assert rmap_chk is False
    for line in expected1:
        assert line in out1
    assert rmap_chk2 is False
    assert out2 in expected2


@mark.jwst
@mark.refactoring
@mark.refactor
@mark.or_bars
def test_or_bars_refactor_add_file(jwst_serverless_state, jwst_data, test_temp_dir, caplog, capsys):
    files = f"{jwst_data}/jwst_miri_ipc_0002.rmap \
        {test_temp_dir}/jwst_miri_ipc_0003.add.rmap \
            {jwst_data}/jwst_miri_ipc_0003.add.fits"
    with caplog.at_level(logging.INFO, logger="CRDS"):
        RefactorScript(f"crds.refactor insert {files}")()
        out = caplog.text
    expected = """Inserting jwst_miri_ipc_0003.add.fits into 'jwst_miri_ipc_0002.rmap'
Setting 'META.INSTRUMENT.BAND [BAND]' = 'UNDEFINED' to value of 'P_BAND' = 'SHORT | MEDIUM |'
Setting 'META.INSTRUMENT.DETECTOR [DETECTOR]' = 'MIRIMAGE' to value of 'P_DETECT' = 'MIRIFUSHORT|MIRIFULONG|'
0 errors""".splitlines()
    ndiffs = diff.DiffScript(f"crds.diff {jwst_data}/jwst_miri_ipc_0002.rmap {test_temp_dir}/jwst_miri_ipc_0003.add.rmap")()
    sout, _ = capsys.readouterr()
    print(sout)
    exp_sout = f"(('{jwst_data}/jwst_miri_ipc_0002.rmap', '{test_temp_dir}/jwst_miri_ipc_0003.add.rmap'), ('MIRIFULONG|MIRIFUSHORT', 'MEDIUM|SHORT'), ('2014-01-01', '00:00:00'), 'added Match rule for jwst_miri_ipc_0003.add.fits')"
    rmap_chk = rmap_check_modifications(f"{jwst_data}/jwst_miri_ipc_0002.rmap", f"{test_temp_dir}/jwst_miri_ipc_0003.add.rmap", "none", f"{jwst_data}/jwst_miri_ipc_0003.add.fits", expected=("add_rule",))
    for line in expected:
        assert line in out    
    assert ndiffs == 1
    assert exp_sout in sout
    assert rmap_chk is True


@mark.jwst
@mark.refactoring
@mark.refactor
@mark.or_bars
def test_or_bars_refactor_replace_file(jwst_serverless_state, jwst_data, test_temp_dir, caplog, capsys):
    files = f"{jwst_data}/jwst_miri_ipc_0002.rmap \
        {test_temp_dir}/jwst_miri_ipc_0004.replace.rmap \
        {jwst_data}/jwst_miri_ipc_0004.replace.fits"
    with caplog.at_level(logging.INFO, logger="CRDS"):
        RefactorScript(f"crds.refactor insert {files}")()
        out = caplog.text
    expected = """Inserting jwst_miri_ipc_0004.replace.fits into 'jwst_miri_ipc_0002.rmap'
Setting 'META.INSTRUMENT.BAND [BAND]' = 'UNDEFINED' to value of 'P_BAND' = 'LONG |'
Setting 'META.INSTRUMENT.DETECTOR [DETECTOR]' = 'MIRIMAGE' to value of 'P_DETECT' = 'MIRIFULONG|'
0 errors""".splitlines()
    ndiffs = diff.DiffScript(f"crds.diff {jwst_data}/jwst_miri_ipc_0002.rmap {test_temp_dir}/jwst_miri_ipc_0004.replace.rmap")()
    sout, _ = capsys.readouterr()
    print(sout)
    exp_sout = f"(('{jwst_data}/jwst_miri_ipc_0002.rmap', '{test_temp_dir}/jwst_miri_ipc_0004.replace.rmap'), ('MIRIFULONG', 'LONG'), ('1900-01-01', '00:00:00'), 'replaced jwst_miri_ipc_0004.fits with jwst_miri_ipc_0004.replace.fits')" 
    rmap_chk1 = rmap_check_modifications(f"{jwst_data}/jwst_miri_ipc_0002.rmap", f"{test_temp_dir}/jwst_miri_ipc_0004.replace.rmap", "jwst_miri_ipc_0004.fits", f"{jwst_data}/jwst_miri_ipc_0004.replace.fits", expected=("replace",))
    rmap_chk2 = rmap_check_modifications(f"{jwst_data}/jwst_miri_ipc_0002.rmap", f"{test_temp_dir}/jwst_miri_ipc_0004.replace.rmap", f"{jwst_data}/jwst_miri_ipc_0004.fits", f"{jwst_data}/jwst_miri_ipc_0004.replace.fits", expected=("replace",))
    assert ndiffs == 1
    assert rmap_chk1 is True
    assert rmap_chk2 is True
    for line in expected:
        assert line in out
    assert exp_sout in sout
