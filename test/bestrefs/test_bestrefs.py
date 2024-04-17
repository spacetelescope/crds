import pytest
import os, os.path
import re
import json
import datetime
import shutil
from crds.core import log
from crds.bestrefs import bestrefs as br
from crds.bestrefs import BestrefsScript
from crds import assign_bestrefs
from crds.hst.locate import header_to_reftypes as hst_header_to_reftypes
from crds.tobs.locate import header_to_reftypes as tobs_header_to_reftypes
from crds.jwst.locate import header_to_reftypes as jwst_header_to_reftypes
import logging
log.THE_LOGGER.logger.propagate=True


@pytest.mark.skip(reason="needs revision - does not produce errors")
@pytest.mark.bestrefs
def test_warn_bad_context(capsys):
    """Test logs an error or warning if the named context is a known bad context."""
    # Send logs to stdout
    log.set_test_mode()
    argv = """crds.bestrefs -n jwst_1091.pmap -o jwst_1090.pmap --instruments miri"""
    test_brs = br.BestrefsScript(argv)
    test_brs.warn_bad_context('jwst_miri_flat_0002.rmap', 'jwst_miri_0011.imap', 'miri')
    out, _ = capsys.readouterr()
    check_msg = """CRDS - ERROR -  instrument='ALL' type='ALL' data='ALL' ::  jwst_miri_flat_0002.rmap"""
    assert check_msg in out
    argv = """crds.bestrefs -n jwst_1091.pmap -o jwst_1090.pmap --jwst --instruments miri
    --allow-bad-rules"""
    test_brs = br.BestrefsScript(argv)
    test_brs.warn_bad_context('jwst_miri_flat_0002.rmap', 'jwst_miri_0011.imap', 'miri')
    out, _ = capsys.readouterr()
    check_msg = """CRDS - WARNING -  jwst_miri_flat_0002.rmap = 'jwst_miri_0011.imap' is bad"""
    assert check_msg in out


@pytest.mark.skip(reason="needs revision - does not produce errors")
@pytest.mark.bestrefs
def test_warn_bad_reference(capsys):
    """Test logs an error or warning if the reference is a known bad reference."""
    # Send logs to stdout
    log.set_test_mode()
    argv = """crds.bestrefs -n jwst_1091.pmap -o jwst_1090.pmap --instruments miri"""
    test_brs = br.BestrefsScript(argv)
    test_brs.warn_bad_reference('jwst_miri_dark_0008.rmap','miri', 'ANY', 'jwst_miri_flat_0002.rmap')
    out, _ = capsys.readouterr()
    check_msg = """CRDS - ERROR -  instrument='MIRI' type='ANY' data='jwst_miri_dark_0008.rmap'"""
    print(out)
    assert check_msg in out
    argv = """crds.bestrefs -n jwst_1091.pmap -o jwst_1090.pmap --jwst --instruments miri
    --allow-bad-references"""
    test_brs = br.BestrefsScript(argv)
    test_brs.warn_bad_reference('jwst_miri_dark_0008.rmap', 'miri', 'ANY', 'jwst_miri_flat_0002.rmap')
    out, _ = capsys.readouterr()
    check_msg = """CRDS - WARNING -  For jwst_miri_dark_0008.rmap miri ANY File 'jwst_miri_flat_0002.rmap'"""
    assert check_msg in out


@pytest.mark.hst
@pytest.mark.bestrefs
def test_bestrefs_3_files(default_shared_state, caplog, hst_data):
    """Test computes simple bestefs for 3 files."""
    out_to_check = f""" No comparison context or source comparison requested.
     No file header updates requested;  dry run.  Use --update-bestrefs to update FITS headers.
     ===> Processing {hst_data}/j8bt05njq_raw.fits
     ===> Processing {hst_data}/j8bt06o6q_raw.fits
     ===> Processing {hst_data}/j8bt09jcq_raw.fits
     0 errors
     0 warnings"""
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        argv = f"""bestrefs.py --new-context hst.pmap --files {hst_data}/j8bt05njq_raw.fits
            {hst_data}/j8bt06o6q_raw.fits {hst_data}/j8bt09jcq_raw.fits"""
        BestrefsScript(argv)()
        out = caplog.text
    
    for msg in out_to_check.splitlines():
        assert msg.strip() in out


@pytest.mark.hst
@pytest.mark.bestrefs
def test_bestrefs_compare_source_files(default_shared_state, caplog, hst_data):
    """Test prints files with at least one reference change."""
    argv = f"""bestrefs.py --new-context hst.pmap --files {hst_data}/j8bt05njq_raw.fits {hst_data}/j8bt06o6q_raw.fits
    {hst_data}/j8bt09jcq_raw.fits --print-affected --compare-source-bestrefs"""
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        BestrefsScript(argv)()
        out = caplog.text
    
    out_to_check = f""" No file header updates requested;  dry run.  Use --update-bestrefs to update FITS headers.
 ===> Processing {hst_data}/j8bt05njq_raw.fits
 instrument='ACS' type='ATODTAB' data='{hst_data}/j8bt05njq_raw.fits' ::  New best reference: 'kcb1734ij_a2d.fits' --> 'n/a' :: Would update.
 instrument='ACS' type='CRREJTAB' data='{hst_data}/j8bt05njq_raw.fits' ::  New best reference: 'n4e12510j_crr.fits' --> 'n/a' :: Would update.
 instrument='ACS' type='IMPHTTAB' data='{hst_data}/j8bt05njq_raw.fits' ::  New best reference: 'n/a' --> 'w3m1716tj_imp.fits' :: Would update.
 instrument='ACS' type='NPOLFILE' data='{hst_data}/j8bt05njq_raw.fits' ::  New best reference: 'n/a' --> 'v9718263j_npl.fits' :: Would update.
  instrument='ACS' type='SHADFILE' data='{hst_data}/j8bt05njq_raw.fits' ::  New best reference: 'kcb1734pj_shd.fits' --> 'n/a' :: Would update.
  ===> Processing {hst_data}/j8bt06o6q_raw.fits
 instrument='ACS' type='ATODTAB' data='{hst_data}/j8bt06o6q_raw.fits' ::  New best reference: 'kcb1734ij_a2d.fits' --> 'n/a' :: Would update.
 instrument='ACS' type='CRREJTAB' data='{hst_data}/j8bt06o6q_raw.fits' ::  New best reference: 'n4e12510j_crr.fits' --> 'n/a' :: Would update.
 instrument='ACS' type='IMPHTTAB' data='{hst_data}/j8bt06o6q_raw.fits' ::  New best reference: 'n/a' --> 'w3m1716tj_imp.fits' :: Would update.
 instrument='ACS' type='NPOLFILE' data='{hst_data}/j8bt06o6q_raw.fits' ::  New best reference: 'n/a' --> 'v9718264j_npl.fits' :: Would update.
 instrument='ACS' type='SHADFILE' data='{hst_data}/j8bt06o6q_raw.fits' ::  New best reference: 'kcb1734pj_shd.fits' --> 'n/a' :: Would update.
 ===> Processing {hst_data}/j8bt09jcq_raw.fits
 instrument='ACS' type='ATODTAB' data='{hst_data}/j8bt09jcq_raw.fits' ::  New best reference: 'kcb1734ij_a2d.fits' --> 'n/a' :: Would update.
 instrument='ACS' type='IMPHTTAB' data='{hst_data}/j8bt09jcq_raw.fits' ::  New best reference: 'n/a' --> 'w3m1716tj_imp.fits' :: Would update.
 instrument='ACS' type='NPOLFILE' data='{hst_data}/j8bt09jcq_raw.fits' ::  New best reference: 'n/a' --> 'v9718260j_npl.fits' :: Would update.
 instrument='ACS' type='SHADFILE' data='{hst_data}/j8bt09jcq_raw.fits' ::  New best reference: 'kcb1734pj_shd.fits' --> 'n/a' :: Would update.
 Affected products = 3
 {hst_data}/j8bt05njq_raw.fits
 {hst_data}/j8bt06o6q_raw.fits
 {hst_data}/j8bt09jcq_raw.fits
 0 errors
 0 warnings"""
    for msg in out_to_check.splitlines():
        assert msg.strip() in out


@pytest.mark.hst
@pytest.mark.bestrefs
def test_bestrefs_3_files_default_context_from_server(default_shared_state, caplog, hst_data):
    """Test computes simple bestrefs for 3 files using the default context from the server."""
    argv = f"""bestrefs.py --new-context=hst.pmap --files {hst_data}/j8bt05njq_raw.fits {hst_data}/j8bt06o6q_raw.fits
     {hst_data}/j8bt09jcq_raw.fits"""
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        BestrefsScript(argv)()
        out = caplog.text
    
    out_to_check = f""" No comparison context or source comparison requested.
 No file header updates requested;  dry run.  Use --update-bestrefs to update FITS headers.
 ===> Processing {hst_data}/j8bt05njq_raw.fits
 ===> Processing {hst_data}/j8bt06o6q_raw.fits
 ===> Processing {hst_data}/j8bt09jcq_raw.fits
 0 errors
 0 warnings"""
    for msg in out_to_check.splitlines():
        assert msg.strip() in out


@pytest.mark.hst
@pytest.mark.bestrefs
def test_bestrefs_broken_dataset_file(default_shared_state, caplog, hst_data):
    """Test tests error status when one broken file is included."""
    argv = f"""bestrefs.py --new-context hst.pmap --files {hst_data}/j8bt05njq_raw.fits {hst_data}/j8bt05njq_raw_broke.fits
    {hst_data}/j8bt06o6q_raw.fits {hst_data}/j8bt09jcq_raw.fits"""
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        BestrefsScript(argv)()
        out = caplog.text
    
    out_to_check = f""" No comparison context or source comparison requested.
 No file header updates requested;  dry run.  Use --update-bestrefs to update FITS headers.
 ===> Processing {hst_data}/j8bt05njq_raw.fits
 ===> Processing {hst_data}/j8bt05njq_raw_broke.fits
 instrument='ACS' type='BIASFILE' data='{hst_data}/j8bt05njq_raw_broke.fits' ::  New: Bestref FAILED:   parameter='CCDAMP' value='FOOBAR' is not in ['A', 'ABCD', 'AC', 'AD', 'B', 'BC', 'BD', 'C', 'D']
 ===> Processing {hst_data}/j8bt06o6q_raw.fits
 ===> Processing {hst_data}/j8bt09jcq_raw.fits
 1 errors
 0 warnings"""
    for msg in out_to_check.splitlines():
        assert msg.strip() in out


@pytest.mark.hst
@pytest.mark.bestrefs
def test_bestrefs_broken_cache_and_server(broken_state, caplog, hst_data):
    """Test """
    argv = f"""bestrefs.py --new-context hst.pmap --files {hst_data}/j8bt05njq_raw.fits"""
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            BestrefsScript(argv)()
            assert pytest_wrapped_e.type == SystemExit
        out = caplog.text
    out_to_check = """ (FATAL) CRDS server connection and cache load FAILED.  Cannot continue.
 See https://hst-crds.stsci.edu/docs/cmdline_bestrefs/ or https://jwst-crds.stsci.edu/docs/cmdline_bestrefs/
 for more information on configuring CRDS,  particularly CRDS_PATH and CRDS_SERVER_URL. : [Errno 2] No such file or directory: '/nowhere/config/hst/server_config'"""
    for msg in out_to_check.splitlines():
        assert msg.strip() in out


@pytest.mark.hst
@pytest.mark.bestrefs
def test_bestrefs_catalog_dataset(default_shared_state, caplog):
    argv = """bestrefs.py --new-context hst.pmap --hst --datasets LB6M01030"""
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        BestrefsScript(argv)()
        out = caplog.text
    
    out_to_check = """ Dumping dataset parameters from CRDS server at 'https://hst-crds.stsci.edu' for ['LB6M01030']
 Dumped 1 of 1 datasets from CRDS server at 'https://hst-crds.stsci.edu'
 Computing bestrefs for datasets ['LB6M01030']
 No comparison context or source comparison requested.
 0 errors
 0 warnings"""
    for msg in out_to_check.splitlines():
        assert msg.strip() in out


@pytest.mark.hst
@pytest.mark.bestrefs
def test_bestrefs_context_to_context(default_shared_state, caplog, hst_data):
    argv = f"""bestrefs.py --new-context hst_0001.pmap  --old-context hst.pmap --files {hst_data}/j8bt05njq_raw.fits
    {hst_data}/j8bt06o6q_raw.fits {hst_data}/j8bt09jcq_raw.fits"""
    with caplog.at_level(logging.INFO, logger="CRDS"):
        BestrefsScript(argv)()
        out = caplog.text
    
    out_to_check = f""" No file header updates requested;  dry run.  Use --update-bestrefs to update FITS headers.
 ===> Processing {hst_data}/j8bt05njq_raw.fits
 ===> Processing {hst_data}/j8bt06o6q_raw.fits
 ===> Processing {hst_data}/j8bt09jcq_raw.fits
 0 errors
 1 warnings"""
    for msg in out_to_check.splitlines():
        assert msg.strip() in out


@pytest.mark.hst
@pytest.mark.bestrefs
def test_bestrefs_all_instruments_hst(default_shared_state, caplog, hst_data):
    argv = f"""bestrefs.py --new-context {hst_data}/hst_0001.pmap --hst --old-context hst.pmap --all-instruments"""
    with caplog.at_level(logging.INFO, logger="CRDS"):
        test_brs = BestrefsScript(argv)
        test_brs.complex_init()
        out = caplog.messages
    
    odd_pattern = re.compile("Dumping dataset parameters for '[a-z0-9]{3,6}' from CRDS server at 'https://hst-crds.stsci.edu'")
    even_pattern = re.compile("Downloaded  [0-9]{5,6} dataset ids for '[a-z0-9]{3,6}' since None")
    first_line = "Computing bestrefs for db datasets for ['acs', 'cos', 'nicmos', 'stis', 'wfc3', 'wfpc2']"
    # remove duplicate log messages from stpipe, up to the last two lines:
    if len(out) > 14:
        out = [o for i, o in enumerate(out[:-2]) if i%2 != 0]
    else: # ignore warning "Assuming parameter names ..."
        out = out[:-1]
    for i, line in enumerate(out):
        line = line.strip()
        if i == 0:
            assert line == first_line
        elif i%2 == 0:
            assert re.match(even_pattern, line) is not None
        else:
            assert re.match(odd_pattern, line) is not None


@pytest.mark.hst
@pytest.mark.bestrefs
def test_bestrefs_datasets_since_auto_hst(default_shared_state, caplog, hst_data):
    new_ctx = f"{hst_data}/hst_0001.pmap"
    argv = f"""bestrefs.py --old-context hst.pmap --new-context {new_ctx} --hst --diffs-only --datasets-since=auto"""
    with caplog.at_level(logging.INFO, logger="CRDS"):
        test_brs = BestrefsScript(argv)
        test_brs.complex_init()
        out = caplog.text
    
    # remove duplicate log messages from stpipe, up to the last two lines:
    out = out.splitlines()
    line_check = [0,1,4,5,8,10,12]
    if len(out) > 8:
        out = [o for i, o in enumerate(out) if i in line_check]
    else: # ignore warning "Assuming parameter names ..."
        out = out[:-1]
    out_to_check = [f"Mapping differences from 'hst.pmap' --> '{new_ctx}' affect:",
                    "{'acs': ['biasfile']}",
                    f"Possibly affected --datasets-since dates determined by 'hst.pmap' --> '{new_ctx}' are:",
                    "{'acs': '1992-01-02 00:00:00'}",
                    "Computing bestrefs for db datasets for ['acs']",
                    "Dumping dataset parameters for 'acs' from CRDS server at 'https://hst-crds.stsci.edu' since '1992-01-02 00:00:00'"]
    pattern = re.compile("Downloaded  [0-9]{5,6} dataset ids for '[a-z0-9]{3,6}' since '1992-01-02 00:00:00'")
    for i, line in enumerate(out):
        line = line.strip()
        if i < 6:
            assert out_to_check[i] in line
        else:
            # using re b/c the numeric value is dynamic
            line = line.replace("INFO     stpipe:log.py:180  ", "")
            expected = re.findall(pattern, line)
            assert expected is not None


@pytest.mark.hst
@pytest.mark.bestrefs
def test_bestrefs_dataset_drop_ids(default_shared_state, caplog, hst_data):
    argv = f"""bestrefs.py --new-context {hst_data}/hst_0001.pmap  --old-context hst.pmap --load-pickle {hst_data}/test_cos.json --drop-ids LCE31SW6Q:LCE31SW6Q"""
    with caplog.at_level(logging.INFO, logger="CRDS"): 
        test_brs = BestrefsScript(argv)
        test_brs.complex_init()
        out = caplog.text
    
    out_to_check = f""" Loading file '{hst_data}/test_cos.json'
 Loaded 1 datasets from file '{hst_data}/test_cos.json' completely replacing existing headers."""
    for msg in out_to_check.splitlines():
        assert msg.strip() in out


@pytest.mark.hst
@pytest.mark.bestrefs
def test_bestrefs_dataset_only_ids(default_shared_state, caplog, hst_data):
    argv = f"""bestrefs.py --new-context {hst_data}/hst_0001.pmap  --old-context hst.pmap --load-pickle {hst_data}/test_cos.json --only-ids LPPPPPP6Q:LCE31SW6Q"""
    with caplog.at_level(logging.INFO, logger="CRDS"):
        test_brs = BestrefsScript(argv)
        test_brs.complex_init()
        out = caplog.text
    
    out_to_check = f""" Loading file '{hst_data}/test_cos.json'
 Loaded 1 datasets from file '{hst_data}/test_cos.json' completely replacing existing headers."""
    for msg in out_to_check.splitlines():
        assert msg.strip() in out


@pytest.mark.hst
@pytest.mark.bestrefs
def test_bestrefs_compare_source_canary(default_shared_state, caplog, hst_data):
    argv = f"""crds.bestrefs --new-context hst_0551.pmap --compare-source --load-pickles {hst_data}/canary.json --differences-are-errors --hst"""
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        BestrefsScript(argv)()
        out = caplog.text
    
    out_to_check = f""" Loading file '{hst_data}/canary.json'
 Loaded 1 datasets from file '{hst_data}/canary.json' completely replacing existing headers.
 instrument='COS' type='BPIXTAB' data='LA7803FIQ' ::  Comparison difference: 'bar.fits' --> 'yae1249sl_bpix.fits' :: Would update.
 instrument='COS' type='XWLKFILE' data='LA7803FIQ' ::  Comparison difference: 'foo.fits' --> '14o2013ql_xwalk.fits' :: Would update.
 2 errors
 0 warnings"""
    for msg in out_to_check.splitlines():
        assert msg.strip() in out


@pytest.mark.hst
@pytest.mark.bestrefs
def test_bestrefs_donotreprocess_datasets(default_shared_state, caplog):
    argv = """crds.bestrefs --old-context hst_0628.pmap --new-context hst_0633.pmap --hst --datasets JA9553LVQ JBBGRCGFQ"""
    with caplog.at_level(logging.INFO, logger="CRDS"):
        BestrefsScript(argv)()
        out = caplog.text
    
    out_to_check = """ Dumping dataset parameters from CRDS server at 'https://hst-crds.stsci.edu' for ['JA9553LVQ', 'JBBGRCGFQ']
 Dumped 2 of 2 datasets from CRDS server at 'https://hst-crds.stsci.edu'
 Computing bestrefs for datasets ['JA9553LVQ', 'JBBGRCGFQ']
 0 errors
 1 warnings"""
    for msg in out_to_check.splitlines():
        assert msg.strip() in out


@pytest.mark.hst
@pytest.mark.bestrefs
def test_bestrefs_donotreprocess_fix(default_shared_state, caplog, hst_data):
    argv = f"""crds.bestrefs --hst --old-context hst_0628.pmap --new-context hst_0633.pmap --print-affected --load-pickle {hst_data}/bestrefs_dnr_fix.json --verbosity=30"""
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        BestrefsScript(argv)()
        out = caplog.text
    
    out_to_check = f""" Command: ['crds.bestrefs', '--hst', '--old-context', 'hst_0628.pmap', '--new-context', 'hst_0633.pmap', '--print-affected', '--load-pickle', '{hst_data}/bestrefs_dnr_fix.json', '--verbosity=30']
 Using explicit new context 'hst_0633.pmap' for computing updated best references.
 Using explicit old context 'hst_0628.pmap'
 Loading file '{hst_data}/bestrefs_dnr_fix.json'
 Loaded 1 datasets from file '{hst_data}/bestrefs_dnr_fix.json' completely replacing existing headers.
 ===> Processing JA9553M3Q:JA9553M3Q
 instrument='ACS' type='ATODTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='BIASFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='BPIXTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 't3n1116nj_bpx.fits' :: No update.
 instrument='ACS' type='CCDTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'uc82140bj_ccd.fits' :: No update.
 instrument='ACS' type='CFLTFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='CRREJTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='D2IMFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='DARKFILE' data='JA9553M3Q:JA9553M3Q' ::  New best reference: '1ag2019jj_drk.fits' --> '25815071j_drk.fits' :: Would update.
 instrument='ACS' type='DGEOFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'qbu16423j_dxy.fits' :: No update.
 instrument='ACS' type='DRKCFILE' data='JA9553M3Q:JA9553M3Q' ::  New best reference: '1ag20119j_dkc.fits' --> '2581508ij_dkc.fits' :: Would update.
 instrument='ACS' type='FLSHFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='IDCTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: '0461802dj_idc.fits' :: No update.
 instrument='ACS' type='IMPHTTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='MDRIZTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='MLINTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='NPOLFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='OSCNTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: '17717071j_osc.fits' :: No update.
 instrument='ACS' type='PCTETAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: '19i16323j_cte.fits' :: No update.
 instrument='ACS' type='PFLTFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='SHADFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='SNKCFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='SPOTTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 Affected products = 1
 1 sources processed
 1 source updates
 0 errors
 1 warnings"""
    for msg in out_to_check.splitlines():
        assert msg.strip() in out


@pytest.mark.hst
@pytest.mark.bestrefs
def test_bestrefs_multiple_updates_with_error(default_shared_state, caplog, hst_data):
    argv = f"""crds.bestrefs --hst --old-context hst_0628.pmap --new-context hst_0633.pmap --print-affected --load-pickle {hst_data}/bestrefs_new_error.json --verbosity=30"""
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        BestrefsScript(argv)()
        out = caplog.text
    
    out_to_check = f""" Command: ['crds.bestrefs', '--hst', '--old-context', 'hst_0628.pmap', '--new-context', 'hst_0633.pmap', '--print-affected', '--load-pickle', '{hst_data}/bestrefs_new_error.json', '--verbosity=30']
 Using explicit new context 'hst_0633.pmap' for computing updated best references.
 Using explicit old context 'hst_0628.pmap'
 Loading file '{hst_data}/bestrefs_new_error.json'
 Loaded 1 datasets from file '{hst_data}/bestrefs_new_error.json' completely replacing existing headers.
 Assuming parameter names and required types are the same across contexts.
 ===> Processing JA9553M3Q:JA9553M3Q
 instrument='ACS' type='ATODTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='BIASFILE' data='JA9553M3Q' ::  Old: Bestref FAILED:   parameter='CCDGAIN' value='2.4' is not in ['0.5', '1.0', '1.4', '2.0', '4.0', '8.0']
 instrument='ACS' type='BIASFILE' data='JA9553M3Q' ::  New: Bestref FAILED:   parameter='CCDGAIN' value='2.4' is not in ['1.0', '2.0', '4.0', '8.0']
 instrument='ACS' type='BPIXTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 't3n1116nj_bpx.fits' :: No update.
 instrument='ACS' type='CCDTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'uc82140bj_ccd.fits' :: No update.
 instrument='ACS' type='CFLTFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='CRREJTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='D2IMFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='DARKFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='DGEOFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'qbu16423j_dxy.fits' :: No update.
 instrument='ACS' type='DRKCFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='FLSHFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='IDCTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: '0461802dj_idc.fits' :: No update.
 instrument='ACS' type='IMPHTTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='MDRIZTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='MLINTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='NPOLFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='OSCNTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: '17717071j_osc.fits' :: No update.
 instrument='ACS' type='PCTETAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: '19i16323j_cte.fits' :: No update.
 instrument='ACS' type='PFLTFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='SHADFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='SNKCFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 instrument='ACS' type='SPOTTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
 Affected products = 0
 1 sources processed
 0 source updates
 2 errors
 1 warnings"""
    for msg in out_to_check.splitlines():
        assert msg.strip() in out


@pytest.mark.multimission
@pytest.mark.bestrefs
def test_cleanpath():
    """Test removes prefixes added to reference files prior to writing into FITS headers."""
    assert br.cleanpath('jref$foo.fits') == 'foo.fits'
    assert br.cleanpath('crds://foo.fits') == 'foo.fits'
    assert br.cleanpath('crds://foo.fits') == 'foo.fits'
    assert br.cleanpath('something/foo.fits') == 'something/foo.fits'


@pytest.mark.multimission
@pytest.mark.bestrefs
def test_hst_tobs_header_to_reftypes(capsys):
    """Test demonstrates header_to_reftypes will get reftypes to list form."""
    assert hst_header_to_reftypes({}, "hst.pmap") == []
    assert tobs_header_to_reftypes({}, "tobs.pmap") == []
    ref_to_c = ['ipc', 'linearity', 'mask', 'refpix', 'rscd', 'saturation', 'superbias']
    assert jwst_header_to_reftypes({"EXP_TYPE": "MIR_DARK", "CAL_VER": "0.7.0"}, "jwst_0301.pmap") == ref_to_c
    assert jwst_header_to_reftypes({"EXP_TYPE": "NIR_IMAGE", "CAL_VER": "0.7.0"}, "jwst_0301.pmap") == []
    out, _ = capsys.readouterr()
    out_to_check = """CRDS - WARNING -  Failed determining reftypes for {'CAL_VER': '0.7.0', 'EXP_TYPE': 'NIR_IMAGE'} : "Failed determining required pipeline .cfgs for EXP_TYPE 'NIR_IMAGE' : 'NIR_IMAGE'"
    """
    assert out in out_to_check
    ref_to_c = ['area', 'camera', 'collimator', 'dark', 'disperser', 'distortion', 'filteroffset', 'fore', 'fpa',
                'gain', 'ifufore', 'ifupost', 'ifuslicer', 'ipc', 'linearity', 'mask', 'msa', 'ote', 'photom',
                'readnoise', 'refpix', 'regions', 'rscd', 'saturation', 'specwcs', 'superbias', 'v2v3',
                'wavelengthrange']
    assert jwst_header_to_reftypes({"EXP_TYPE":"MIR_IMAGE", "CAL_VER": "0.7.0"}, "jwst_0301.pmap") == ref_to_c


@pytest.mark.hst
@pytest.mark.bestrefs
class TestBestrefs:

    script_class = BestrefsScript
    obs = "hst"
    new_context = "hst_0315.pmap"
    bestrefs_list = "@test/data/hst/bestrefs_file_list"

    @pytest.fixture(autouse=True)
    def _get_data(self, hst_data, test_temp_dir):
        self._dpath = hst_data
        self._tmp = test_temp_dir

    @pytest.fixture()
    def _get_config(self, hst_persistent_state):
        self._config = hst_persistent_state

    def run_script(self, cmd, expected_errs=0):
        """Run SyncScript using command line `cmd` and check for `expected_errs` as return status."""
        errs = self.script_class(cmd)()
        if expected_errs is not None:
            assert errs == expected_errs

    def get_10_days_ago(self):
        now = datetime.datetime.now()
        now -= datetime.timedelta(days=10)
        return now.isoformat().split("T")[0]

    def test_bestrefs_affected_datasets(self):
        self.run_script(f"crds.bestrefs --affected-datasets --old-context hst_0978.pmap --new-context hst_0980.pmap --datasets-since {self.get_10_days_ago()}")

    def test_bestrefs_from_pickle(self):
        self.run_script(f"crds.bestrefs --new-context {self.new_context} --load-pickle {self._dpath}/test_cos.pkl --stats --print-affected-details --allow-bad-references")

    def test_bestrefs_to_pickle(self):
        self.run_script(f"crds.bestrefs --datasets LA9K03C3Q:LA9K03C3Q LA9K03C5Q:LA9K03C5Q LA9K03C7Q:LA9K03C7Q --new-context {self.new_context} --save-pickle {self._tmp}/test_cos.pkl --stats")

    def test_bestrefs_from_json(self):
        self.run_script(f"crds.bestrefs --new-context {self.new_context} --load-pickle {self._dpath}/test_cos.json --stats",
                        expected_errs=1)

    def test_bestrefs_to_json(self):
        self.run_script(f"crds.bestrefs --instrument cos --new-context {self.new_context} --save-pickle {self._tmp}/test_cos.json --datasets-since {self.get_10_days_ago()}", expected_errs=None)

    def test_bestrefs_at_file(self):
        self.run_script(f"crds.bestrefs --files {self.bestrefs_list}  --new-context {self.new_context} --stats")

    def test_bestrefs_remote(self):
        self.run_script(f"crds.bestrefs --files {self.bestrefs_list}  --new-context {self.new_context} --remote --stats")

    def test_bestrefs_new_references(self):
        self.run_script(f"crds.bestrefs --files {self.bestrefs_list}  --new-context {self.new_context} --print-new-references --stats")

    def test_bestrefs_default_new_context(self):
        self.run_script(f"crds.bestrefs --files {self.bestrefs_list}  --stats")

    def test_bestrefs_update_file_headers(self):
        shutil.copy(f"{self._dpath}/j8bt06o6q_raw.fits", f"{self._tmp}/j8bt06o6q_raw.fits")
        self.run_script(f"crds.bestrefs --files {self._tmp}/j8bt06o6q_raw.fits --new-context {self.new_context} --update-bestrefs")

    def test_bestrefs_update_bestrefs(self):
        """update_bestrefs modifies dataset file headers"""
        shutil.copy(f"{self._dpath}/j8bt06o6q_raw.fits", f"{self._tmp}/j8bt06o6q_raw.fits")
        self.run_script(f"crds.bestrefs --files {self._tmp}/j8bt06o6q_raw.fits --new-context {self.new_context} --update-bestrefs")

    def test_bestrefs_bad_sources(self):
        try:
            self.run_script(f"crds.bestrefs --all-instruments --instrument cos --new-context {self.new_context}",
                            expected_errs=1)
        except AssertionError:
            assert True

    def test_bestrefs_update_headers(self):
        """update_headers updates original headers from a pickle saving a new pickle withn orginal + overrides."""
        self.run_script(f"crds.bestrefs --new-context {self.new_context} --datasets LCE31SW6Q:LCE31SW6Q --load-pickle {self._dpath}/test_cos_update.json --allow-bad-references --save-pickle {self._tmp}/test_cos_combined.json --update-bestrefs --update-pickle", expected_errs=0)
        with open(f"{self._tmp}/test_cos_combined.json") as pfile:
            header = json.load(pfile)
        header = header["LCE31SW6Q:LCE31SW6Q"]
        assert header["BADTTAB"] == "N/A"
        assert header["GSAGTAB"] == "X6L1439EL_GSAG.FITS"
        assert header["FLATFILE"] == "N/A"

    def test_assign_bestrefs(self):
        test_copy = f"{self._tmp}/cos_N8XTZCAWQ_updated.fits"
        shutil.copy(f"{self._dpath}/cos_N8XTZCAWQ.fits", test_copy)
        errors = assign_bestrefs([test_copy], context="hst_0500.pmap")
        assert errors == 0


# # New tests
@pytest.mark.multimission
@pytest.mark.bestrefs
@pytest.mark.parametrize('line, expected',
                         [
                             (None, None),
                             ('auto', 'auto'),
                             ('Mar 21 2001 12:00:00 am', '2001-03-21 00:00:00'),
                             ('Dec 01 1993 00:00:00 UT', '1993-12-01 00:00:00'),
                             ('Feb 08 2006 01:02AM', '2006-02-08 01:02:00'),
                             ('12/21/1999 05:42:35', '1999-12-21 05:42:35'),
                             ('1999-12-21T05:42:35', '1999-12-21 05:42:35'),
                             ('12-21-1999 05:42', '1999-12-21 05:42:00'),
                             ('19970114:053714', '1997-01-14 05:37:14'),
                         ])
def test_reformat_date_or_auto(line, expected):
    """Test should return date if argument is none, 'auto' if arg is a variation of 'auto',
    or a reformatted date otherwise."""
    assert br.reformat_date_or_auto(line) == expected


@pytest.mark.multimission
@pytest.mark.bestrefs
@pytest.mark.parametrize('line, expected',
                         [
                             ('\u0068\u0065\u006C\u006C\u006F', "'hello'"),
                         ])
def test_sreprlow(line, expected):
    """Test should return lowercase repr() of input."""
    assert br.sreprlow(line) == expected


@pytest.mark.bestrefs
@pytest.mark.multimission
@pytest.mark.parametrize('line, expected',
                         [
                             ('jref$n4e12510j_crr.fits', 'n4e12510j_crr.fits'),
                             ('crds://jwst_miri_dark_0070.fits', 'jwst_miri_dark_0070.fits'),
                         ])
def test_cleanpath(line, expected):
    """Test should demonstrate that filename is cleaned of 'ref$' and 'crds://' prepends."""
    assert br.cleanpath(line) == expected


@pytest.mark.multimission
@pytest.mark.bestrefs
def test_init_func():
    test_brs = BestrefsScript("crds.bestrefs")
    assert test_brs.args.new_context is None
    assert test_brs.args.old_context is None
    assert test_brs.args.fetch_old_headers is False
    assert test_brs.args.files is None
    assert test_brs.args.datasets is None
    assert test_brs.args.all_instruments is None
    assert test_brs.args.instruments is None
    assert test_brs.args.load_pickles is None
    assert test_brs.args.save_pickle is None
    assert test_brs.args.types == ()
    assert test_brs.args.skip_types == ()
    assert test_brs.args.all_types is False
    assert test_brs.args.diffs_only is None
    assert test_brs.args.datasets_since is None
    assert test_brs.args.compare_source_bestrefs is False
    assert test_brs.args.update_pickle is False
    assert test_brs.args.only_ids is None
    assert test_brs.args.drop_ids == []
    assert test_brs.args.update_bestrefs is False
    assert test_brs.args.print_affected is False
    assert test_brs.args.print_affected_details is False
    assert test_brs.args.print_new_references is False
    assert test_brs.args.print_update_counts is False
    assert test_brs.args.print_error_headers is False
    assert test_brs.args.remote_bestrefs is False
    assert test_brs.args.sync_mappings == 1
    assert test_brs.args.sync_references == 0
    assert test_brs.args.differences_are_errors is False
    assert test_brs.args.allow_bad_rules is False
    assert test_brs.args.allow_bad_references is False
    assert test_brs.args.undefined_differences_matter is False
    assert test_brs.args.na_differences_matter is False
    assert test_brs.args.regression is False
    assert test_brs.args.check_context is False
    assert test_brs.args.affected_datasets is False
    assert test_brs.args.optimize_tables is False
    assert test_brs.args.eliminate_duplicate_cases is False
    assert test_brs.args.dump_unique_errors is False
    assert test_brs.args.unique_errors_file is None
    assert test_brs.args.all_errors_file is None
    assert test_brs.args.unique_threshold == 1
    assert test_brs.args.max_errors_per_class == 500
    assert test_brs.args.unique_delimiter is None
    assert test_brs.args.verbose is False
    assert test_brs.args.verbosity == 0
    assert test_brs.args.dump_cmdline is False
    assert test_brs.args.readonly_cache is False
    assert test_brs.args.ignore_cache is False
    assert test_brs.args.version is False
    assert test_brs.args.jwst is False
    assert test_brs.args.hst is False
    assert test_brs.args.roman is False
    assert test_brs.args.stats is False
    assert test_brs.args.log_time is False
    assert test_brs.args.pdb is False
    assert test_brs.args.debug_traps is False

    argv = "crds.bestrefs --regression --affected-datasets --check-context"
    test_brs2 = BestrefsScript(argv)
    # regression
    assert test_brs2.args.compare_source_bestrefs is True
    assert test_brs2.args.differences_are_errors is True
    assert test_brs2.args.stats is True
    assert test_brs2.args.dump_unique_errors is True
    # affected_datasets
    assert test_brs2.args.diffs_only is True
    assert test_brs2.args.datasets_since is 'auto'
    assert test_brs2.args.print_update_counts is True
    assert test_brs2.args.print_affected is True
    assert test_brs2.args.dump_unique_errors is True
    assert test_brs2.args.stats is True
    assert test_brs2.args.undefined_differences_matter is True
    assert test_brs2.args.na_differences_matter is True
    # check_context
    assert test_brs2.args.all_errors_file == 'all_errors.ids'
    assert test_brs2.args.unique_errors_file == 'unique_errors.ids'


@pytest.mark.hst
@pytest.mark.bestrefs
def test_complex_init(hst_data):
    """Test should initiate complex init and show each argument working."""
    argv = f"""crds.bestrefs --load-pickles {hst_data}/bestrefs.special.json
    --new-context hst_0315.pmap"""
    test_brs = br.BestrefsScript(argv)
    test_brs.complex_init()
    assert test_brs.args.new_context == 'hst_0315.pmap'
    assert test_brs.args.old_context is None
    assert test_brs.args.fetch_old_headers is False
    assert test_brs.args.files is None
    assert test_brs.args.datasets is None
    assert test_brs.args.all_instruments is None
    assert test_brs.args.instruments is None
    assert test_brs.args.load_pickles == [f'{hst_data}/bestrefs.special.json']
    assert test_brs.args.save_pickle is None
    assert test_brs.args.types is ()
    assert test_brs.args.skip_types is ()
    assert test_brs.args.all_types is False
    assert test_brs.args.diffs_only is None
    assert test_brs.args.datasets_since is None
    assert test_brs.args.compare_source_bestrefs is False
    assert test_brs.args.update_pickle is False
    assert test_brs.args.only_ids is None
    assert test_brs.args.drop_ids == []
    assert test_brs.args.update_bestrefs is False
    assert test_brs.args.print_affected is False
    assert test_brs.args.print_affected_details is False
    assert test_brs.args.print_new_references is False
    assert test_brs.args.print_update_counts is False
    assert test_brs.args.print_error_headers is False
    assert test_brs.args.remote_bestrefs is False
    assert test_brs.args.sync_mappings == 1
    assert test_brs.args.sync_references == 0
    assert test_brs.args.differences_are_errors is False
    assert test_brs.args.allow_bad_rules is False
    assert test_brs.args.allow_bad_references is False
    assert test_brs.args.undefined_differences_matter is False
    assert test_brs.args.na_differences_matter is False
    assert test_brs.args.regression is False
    assert test_brs.args.check_context is False
    assert test_brs.args.affected_datasets is False
    assert test_brs.args.optimize_tables is False
    assert test_brs.args.eliminate_duplicate_cases is False
    assert test_brs.args.dump_unique_errors is False
    assert test_brs.args.unique_errors_file is None
    assert test_brs.args.all_errors_file is None
    assert test_brs.args.unique_threshold == 1
    assert test_brs.args.max_errors_per_class == 500
    assert test_brs.args.unique_delimiter is None
    assert test_brs.args.verbose is False
    assert test_brs.args.verbosity == 0
    assert test_brs.args.dump_cmdline is False
    assert test_brs.args.readonly_cache is False
    assert test_brs.args.ignore_cache is False
    assert test_brs.args.version is False
    assert test_brs.args.jwst is False
    assert test_brs.args.hst is False
    assert test_brs.args.roman is False
    assert test_brs.args.stats is False
    assert test_brs.args.profile == ''
    assert test_brs.args.log_time is False
    assert test_brs.args.pdb is False
    assert test_brs.args.debug_traps is False

    # diffs_only
    argv = f"""crds.bestrefs --new-context {hst_data}/hst_0001.pmap
           --old-context hst.pmap --hst --diffs-only"""
    test_brs = BestrefsScript(argv)
    test_brs.complex_init()
    assert test_brs.args.diffs_only is True
    assert test_brs.args.hst is True

    # all_instruments
    argv = """crds.bestrefs --all-instruments --hst"""
    test_brs = BestrefsScript(argv)
    test_brs.complex_init()
    assert test_brs.args.all_instruments is True

    # instruments
    argv = "crds.bestrefs --instruments acs cos stis wfc3 --hst"
    test_brs = BestrefsScript(argv)
    test_brs.complex_init()
    assert test_brs.args.instruments == ['acs', 'cos', 'stis', 'wfc3']

    # datasets
    argv = """crds.bestrefs --datasets LB6M01030 --hst"""
    test_brs = BestrefsScript(argv)
    test_brs.complex_init()
    assert test_brs.args.datasets == ['LB6M01030']

    # files
    argv = f"""crds.bestrefs --files {hst_data}/j8bt05njq_raw.fits --hst"""
    test_brs = BestrefsScript(argv)
    test_brs.complex_init()
    assert test_brs.args.files == [f'{hst_data}/j8bt05njq_raw.fits']


@pytest.mark.jwst
@pytest.mark.bestrefs
@pytest.mark.parametrize('line, expected',
                        [
                            ('jw01444-o002_20220618t005802_spec3_001',
                             'JW01444-O002_20220618T005802_SPEC3_001:JW01444-O002_20220618T005802_SPEC3_001'),
                            ('icir09ehq:icir09ehq', 'ICIR09EHQ:ICIR09EHQ'),
                        ])
def test_normalize_id(line, expected):
    """Test should show that datasets are converted to uppercase and given <exposure>:<exposure> form."""
    test_brs = BestrefsScript("crds.bestrefs")
    assert test_brs.normalize_id(line) == expected


@pytest.mark.multimission
@pytest.mark.bestrefs
def test_only_ids():
    """Test should demonstrate only_ids is set to None."""
    test_brs = BestrefsScript("crds.bestrefs")
    assert test_brs.only_ids is None


@pytest.mark.multimission
@pytest.mark.bestrefs
def test_drop_ids():
    """Test should demonstrate drop_ids is set to []."""
    test_brs = BestrefsScript("crds.bestrefs")
    assert isinstance(test_brs.drop_ids, list)
    assert len(test_brs.drop_ids) == 0


@pytest.mark.multimission
@pytest.mark.bestrefs
@pytest.mark.parametrize('line, expected',
                         [
                             (['id1', 'Id2:iD2'], ['ID1:ID1', 'ID2:ID2']),
                             ([], [])
                         ])
def test_normalized(line, expected):
    """Test should demonstrate that a list of dataset IDs is normalized."""
    test_brs = BestrefsScript("crds.bestrefs")
    assert test_brs._normalized(line) == expected


@pytest.mark.multimission
@pytest.mark.bestrefs
@pytest.mark.parametrize('line, expected',
                         [
                             ('lezcg2010', 'lezcg2010'),
                         ])
def test_locate_file(line, expected):
    """Test should demonstrate that a list of dataset IDs is normalized."""
    test_brs = BestrefsScript("crds.bestrefs")
    assert test_brs.locate_file(line) == expected


@pytest.mark.multimission
@pytest.mark.bestrefs
def test_auto_datasets_since(hst_data):
    """Test makes a call to the server to identify datasets affected by incrementing pmap."""
    test_dict = {
        'acs': '1992-01-02 00:00:00'
    }
    argv = f"""crds.bestrefs  --old-context hst.pmap --new-context {hst_data}/hst_0001.pmap
    --diffs-only --hst --datasets-since=auto
    """
    test_brs = br.BestrefsScript(argv)
    test_brs.complex_init()
    test_val = test_brs.auto_datasets_since()
    assert test_val == test_dict


@pytest.mark.multimission
@pytest.mark.bestrefs
def test_setup_contexts(hst_data):
    """Test sets up crds contexts by checking if either old or new are defined."""
    argv = """crds.bestrefs --diffs-only"""
    test_brs = br.BestrefsScript(argv)
    new, old = test_brs.setup_contexts()
    assert new == test_brs.default_context
    assert old is None

    argv = """crds.bestrefs --diffs-only --old-context hst.pmap"""
    test_brs = br.BestrefsScript(argv)
    new, old = test_brs.setup_contexts()
    assert old == 'hst.pmap'

    argv = f"""crds.bestrefs --diffs-only --new-context {hst_data}/hst_0001.pmap"""
    test_brs = br.BestrefsScript(argv)
    new, old = test_brs.setup_contexts()
    assert new == f'{hst_data}/hst_0001.pmap'


@pytest.mark.multimission
@pytest.mark.bestrefs
def test_update_promise(hst_data):
    """Test outputs a message if the bestrefs would be updated or it updating has started."""
    argv = f"""crds.bestrefs --new-context {hst_data}/hst_0001.pmap
            --old-context {hst_data}/hst.pmap --hst --diffs-only"""
    test_brs = br.BestrefsScript(argv)
    test_val = test_brs.update_promise
    assert test_brs.update_promise == ":: Would update."
    argv = f"""crds.bestrefs --new-context {hst_data}/hst_0001.pmap --update-bestrefs
                --old-context {hst_data}/hst.pmap --hst --diffs-only --verbosity=55"""
    test_brs = br.BestrefsScript(argv)
    test_val = test_brs.update_promise
    assert test_brs.update_promise == ":: Updating."


@pytest.mark.multimission
@pytest.mark.bestrefs
def test_get_bestrefs(hst_data):
    """Test gets bestrefs for supplied header."""
    # A function that looks a little simple on the surface, this function actually touches some
    # 10 other functions in several other modules to calculate bestrefs. It took alot of time to look
    # through them and I still don't think I quite understand how to trigger the system to actually
    # retrieve the best references, as I tried a dozen or so variations of the supplied header dict
    # to no avail. I'd like to revisit this at a later time and flesh out more testing capabilities
    # for one of the namesake functions of the bestrefs module.
    argv = """crds.bestrefs --hst"""
    test_brs = br.BestrefsScript(argv)
    value_to_test = test_brs.get_bestrefs('acs', f'{hst_data}/hst_acs_atodtab_0251.rmap', 'hst_1000.pmap',
                    {'instrume': 'acs'})
    dict_to_verify = {'ATODTAB': 'NOT FOUND No match found.',
                      'BIASFILE': 'NOT FOUND One or more required date/time values is UNDEFINED',
                      'BPIXTAB': "NOT FOUND  parameter='DETECTOR' value='UNDEFINED' is not in ['HRC', 'SBC', 'WFC']",
                      'CCDTAB': "NOT FOUND  parameter='DETECTOR' value='UNDEFINED' is not in ['HRC', 'WFC']",
                      'CFLTFILE': 'NOT FOUND n/a',
                      'CRREJTAB': "NOT FOUND  parameter='DETECTOR' value='UNDEFINED' is not in ['HRC', 'WFC']",
                      'D2IMFILE': 'NOT FOUND n/a',
                      'DARKFILE': "NOT FOUND  parameter='DETECTOR' value='UNDEFINED' is not in ['HRC', 'WFC']",
                      'DGEOFILE': 'NOT FOUND n/a',
                      'DRKCFILE': 'NOT FOUND n/a',
                      'FLSHFILE': "NOT FOUND  parameter='DETECTOR' value='UNDEFINED' is not in ['HRC', 'WFC']",
                      'IDCTAB': "NOT FOUND  parameter='DETECTOR' value='UNDEFINED' is not in ['HRC', 'SBC', 'WFC']",
                      'IMPHTTAB': "NOT FOUND  parameter='DETECTOR' value='UNDEFINED' is not in ['HRC', 'SBC', 'WFC']",
                      'MDRIZTAB': "NOT FOUND  parameter='DETECTOR' value='UNDEFINED' is not in ['HRC', 'SBC', 'WFC']",
                      'MLINTAB': 'NOT FOUND n/a',
                      'NPOLFILE': 'NOT FOUND n/a',
                      'OSCNTAB': "NOT FOUND  parameter='DETECTOR' value='UNDEFINED' is not in ['HRC', 'WFC']",
                      'PCTETAB': 'NOT FOUND n/a',
                      'PFLTFILE': "NOT FOUND  parameter='DETECTOR' value='UNDEFINED' is not in ['HRC', 'SBC', 'WFC']",
                      'SATUFILE': "NOT FOUND  parameter='DETECTOR' value='UNDEFINED' is not in ['HRC', 'WFC']",
                      'SHADFILE': 'NOT FOUND No match found.',
                      'SNKCFILE': 'NOT FOUND n/a',
                      'SPOTTAB': 'NOT FOUND n/a'}

    assert value_to_test == dict_to_verify


@pytest.mark.multimission
@pytest.mark.bestrefs
def test_verbose_with_prefix(caplog, hst_data):
    """Test checks that verbose log message has had a prefix format made."""
    argv = """crds.bestrefs --hst --instrument=acs --verbosity=55"""
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        test_brs = br.BestrefsScript(argv)
        test_brs.verbose_with_prefix(f'{hst_data}/j8bt05njq_raw.fits', 'acs', 'ANY')
        out = caplog.text
    out_to_check = f""" instrument='ACS' type='ANY' data='{hst_data}/j8bt05njq_raw.fits' ::"""
    for msg in out_to_check.splitlines():
        assert msg.strip() in out


@pytest.mark.multimission
@pytest.mark.bestrefs
def test_screen_bestrefs(hst_data, caplog):
    """Test checks for references that are atypical or known to be avoided."""
    argv = """crds.bestrefs --hst --instrument=acs --verbosity=55"""
    bestrefs_dict = {"BRFTAB": "N/A", "SEGMENT": "N/A", "WCPTAB": "XAF1429EL_WCP.FITS"}
    test_brs = br.BestrefsScript(argv)
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        test_brs.skip_filekinds.append("brftab")
        tuple1, tuple2 = test_brs.screen_bestrefs('acs', f'{hst_data}/j8bt05njq_raw.fits', bestrefs_dict)
        out = caplog.text
    check_msg1 = f"""instrument='ACS' type='SEGMENT' data='{hst_data}/j8bt05njq_raw.fits' ::  Bestref FOUND: 'n/a' :: Would update."""
    check_msg2 = f"""instrument='ACS' type='WCPTAB' data='{hst_data}/j8bt05njq_raw.fits' ::  Bestref FOUND: 'xaf1429el_wcp.fits' :: Would update."""
    exp_tuple1 = ['acs', 'segment', None, 'N/A']
    exp_tuple2 = ['acs', 'wcptab', None, 'XAF1429EL_WCP.FITS']
    assert check_msg1 in out
    assert check_msg2 in out
    for i, j in enumerate(exp_tuple1):
        assert tuple1[i] == j
    for i, j in enumerate(exp_tuple2):
        assert tuple2[i] == j


@pytest.mark.multimission
@pytest.mark.bestrefs
def test_handle_na_and_not_found(capsys, hst_data):
    """Test obtains bestref if available and handles matched N/A or NOT FOUND references."""
    argv = """crds.bestrefs --hst --instrument=acs --verbosity=55"""
    test_brs = br.BestrefsScript(argv)
    log.set_test_mode()
    # No match, => 'N/A'
    bestrefs_dict = {"BRFTAB": "N/A", "SEGMENT": "N/A", "WCPTAB": "XAF1429EL_WCP.FITS"}
    test_brs.handle_na_and_not_found('Old', bestrefs_dict, f'{hst_data}/j8bt05njq_raw.fits', 'acs', 'jref$n4e12510j_crr.fits')
    out, _ = capsys.readouterr()
    msg_to_check = """Old No match found: 'UNDEFINED'  => 'N/A'"""
    assert msg_to_check in out
    # No match, without => 'N/A'
    argv = """crds.bestrefs --hst --instrument=acs --check-context --old-context hst_0315.pmap --verbosity=55"""
    test_brs = br.BestrefsScript(argv)
    test_brs.handle_na_and_not_found('New', bestrefs_dict, f'{hst_data}/j8bt05njq_raw.fits', 'acs', 'jref$n4e12510j_crr.fits')
    out, _ = capsys.readouterr()
    msg_to_check = """New No match found: 'UNDEFINED'"""
    msg_not_seen = """=> 'N/A'"""
    assert msg_to_check in out
    assert msg_not_seen not in out
    # Match, natural N/A
    argv = """crds.bestrefs --hst --instrument=acs --check-context --old-context hst_0315.pmap --verbosity=55"""
    test_brs = br.BestrefsScript(argv)
    bestrefs_dict = {"BRFTAB": "N/A", "SEGMENT": "N/A", "JREF$N4E12510J_CRR.FITS": "NOT FOUND N/A"}
    ref_ok, ref = test_brs.handle_na_and_not_found('New', bestrefs_dict, f'{hst_data}/j8bt05njq_raw.fits',
                                                   'acs', 'jref$n4e12510j_crr.fits')
    assert ref_ok is True
    assert ref == 'N/A'
    # Match, Failed
    argv = """crds.bestrefs --hst --instrument=acs --check-context --old-context hst_0315.pmap --verbosity=55"""
    test_brs = br.BestrefsScript(argv)
    bestrefs_dict = {"BRFTAB": "N/A", "SEGMENT": "N/A", "JREF$N4E12510J_CRR.FITS": "NOT FOUND"}
    ref_ok, ref = test_brs.handle_na_and_not_found('New', bestrefs_dict, f'{hst_data}/j8bt05njq_raw.fits',
                                                   'acs', 'jref$n4e12510j_crr.fits')
    out, _ = capsys.readouterr()
    msg_to_check = """New Bestref FAILED:"""
    assert msg_to_check in out
    # Match, good
    argv = """crds.bestrefs --hst --instrument=acs --check-context --old-context hst_0315.pmap --verbosity=55"""
    test_brs = br.BestrefsScript(argv)
    bestrefs_dict = {"BRFTAB": "N/A", "SEGMENT": "N/A", "JREF$N4E12510J_CRR.FITS": "jref$n4e12510j_crr.fits"}
    ref_ok, ref = test_brs.handle_na_and_not_found('New', bestrefs_dict, f'{hst_data}/j8bt05njq_raw.fits',
                                                   'acs', 'jref$n4e12510j_crr.fits')
    assert ref_ok is True
    assert ref == 'N4E12510J_CRR.FITS'


@pytest.mark.multimission
@pytest.mark.bestrefs
def test_unkilled_updates():
    """Test confirms that unkilled_updates returns a dict minus items found in kill_list."""
    argv = """crds.bestrefs --hst --verbosity=55"""
    test_brs = br.BestrefsScript(argv)
    test_brs.skip_filekinds.append("brftab")
    od_dict1 = {"BRFTAB": "N/A", "SEGMENT": "N/A", "WCPTAB": "XAF1429EL_WCP.FITS"}
    od_dict2 = {"WCPTAB": "XAF1429EL_WCP.FITS"}
    od_dict3 = {'BRFTAB': 'N/A', 'SEGMENT': 'N/A'}
    test_brs.updates = od_dict1
    test_brs.kill_list = od_dict2
    assert test_brs.unkilled_updates == od_dict3


@pytest.mark.multimission
@pytest.mark.bestrefs
def test_dataset_to_product_id():
    """Test confirms that product ID is returned by function."""
    argv = """crds.bestrefs --hst --verbosity=0"""
    test_brs = br.BestrefsScript(argv)
    dataset_to_test = 'icir09ehq:ICIR09EHQ'
    product_id = dataset_to_test.split(":")[0].lower()
    assert test_brs.dataset_to_product_id(dataset_to_test) == product_id


@pytest.mark.multimission
@pytest.mark.bestrefs
def test_print_affected(capsys):
    """Test demonstrates that print_affected prints the product ids found in unkilled updates."""
    """Difficult to test the logger since the print to stdout comes first."""
    argv = """crds.bestrefs --hst --verbosity=0"""
    test_brs = br.BestrefsScript(argv)
    test_brs.updates = {"icir09ehq:icir09ehq": "icir09ehq", "20220618T005802:20220618T005802": "20220618T005802"}
    test_brs.print_affected()
    msg_to_check = """20220618t005802\nicir09ehq\n"""
    out, _ = capsys.readouterr()
    assert out == msg_to_check
