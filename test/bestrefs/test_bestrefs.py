import pytest
import os, os.path
import json
#import sys
#import re
import datetime
import shutil
#import crds
#import logging
#from crds.hst import locate
from crds.core import log#, config, utils, timestamp, cmdline, heavy_client
#from crds.hst import TYPES, INSTRUMENTS, FILEKINDS, EXTENSIONS, INSTRUMENT_FIXERS, TYPE_FIXERS
#from crds.client import api
from crds.bestrefs import bestrefs as br
#from crds.core.timestamp import format_date, parse_date
#from astropy.time import Time
#from collections import namedtuple, OrderedDict
from crds.bestrefs import BestrefsScript
from crds import assign_bestrefs
from crds.tests import test_config


@pytest.fixture(autouse=True)
def reset_log():
   yield
   log.reset()


# Would like to add a fixture that runs setup and cleanup before and after a test respectively but doesn't seem
# to work with capsys very well.
# @pytest.fixture(autouse=True, scope="session")
# def set_config():
#     old_state = test_config.setup()
#     yield old_state
#     test_config.cleanup(old_state)


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


def test_bestrefs_3_files(capsys):
    """Test computes simple bestefs for 3 files."""
    old_state = test_config.setup()
    argv = """bestrefs.py --new-context hst.pmap --files data/j8bt05njq_raw.fits
           data/j8bt06o6q_raw.fits data/j8bt09jcq_raw.fits"""
    br.BestrefsScript(argv)()
    out, _ = capsys.readouterr()
    out_to_check = """CRDS - INFO -  No comparison context or source comparison requested.
CRDS - INFO -  No file header updates requested;  dry run.  Use --update-bestrefs to update FITS headers.
CRDS - INFO -  ===> Processing data/j8bt05njq_raw.fits
CRDS - INFO -  ===> Processing data/j8bt06o6q_raw.fits
CRDS - INFO -  ===> Processing data/j8bt09jcq_raw.fits
CRDS - INFO -  0 errors
CRDS - INFO -  0 warnings
CRDS - INFO -  5 infos"""
    assert out_to_check in out
    test_config.cleanup(old_state)


def test_bestrefs_compare_source_files(capsys):
    """Test prints files with at least one reference change."""
    old_state = test_config.setup()
    argv = """bestrefs.py --new-context hst.pmap --files data/j8bt05njq_raw.fits data/j8bt06o6q_raw.fits
    data/j8bt09jcq_raw.fits --print-affected --compare-source-bestrefs"""
    br.BestrefsScript(argv)()
    out, _ = capsys.readouterr()
    out_to_check = """CRDS - INFO -  No file header updates requested;  dry run.  Use --update-bestrefs to update FITS headers.
CRDS - INFO -  ===> Processing data/j8bt05njq_raw.fits
CRDS - INFO -  instrument='ACS' type='ATODTAB' data='data/j8bt05njq_raw.fits' ::  New best reference: 'kcb1734ij_a2d.fits' --> 'n/a' :: Would update.
CRDS - INFO -  instrument='ACS' type='CRREJTAB' data='data/j8bt05njq_raw.fits' ::  New best reference: 'n4e12510j_crr.fits' --> 'n/a' :: Would update.
CRDS - INFO -  instrument='ACS' type='IMPHTTAB' data='data/j8bt05njq_raw.fits' ::  New best reference: 'n/a' --> 'w3m1716tj_imp.fits' :: Would update.
CRDS - INFO -  instrument='ACS' type='NPOLFILE' data='data/j8bt05njq_raw.fits' ::  New best reference: 'n/a' --> 'v9718263j_npl.fits' :: Would update.
CRDS - INFO -  instrument='ACS' type='SHADFILE' data='data/j8bt05njq_raw.fits' ::  New best reference: 'kcb1734pj_shd.fits' --> 'n/a' :: Would update.
CRDS - INFO -  ===> Processing data/j8bt06o6q_raw.fits
CRDS - INFO -  instrument='ACS' type='ATODTAB' data='data/j8bt06o6q_raw.fits' ::  New best reference: 'kcb1734ij_a2d.fits' --> 'n/a' :: Would update.
CRDS - INFO -  instrument='ACS' type='CRREJTAB' data='data/j8bt06o6q_raw.fits' ::  New best reference: 'n4e12510j_crr.fits' --> 'n/a' :: Would update.
CRDS - INFO -  instrument='ACS' type='IMPHTTAB' data='data/j8bt06o6q_raw.fits' ::  New best reference: 'n/a' --> 'w3m1716tj_imp.fits' :: Would update.
CRDS - INFO -  instrument='ACS' type='NPOLFILE' data='data/j8bt06o6q_raw.fits' ::  New best reference: 'n/a' --> 'v9718264j_npl.fits' :: Would update.
CRDS - INFO -  instrument='ACS' type='SHADFILE' data='data/j8bt06o6q_raw.fits' ::  New best reference: 'kcb1734pj_shd.fits' --> 'n/a' :: Would update.
CRDS - INFO -  ===> Processing data/j8bt09jcq_raw.fits
CRDS - INFO -  instrument='ACS' type='ATODTAB' data='data/j8bt09jcq_raw.fits' ::  New best reference: 'kcb1734ij_a2d.fits' --> 'n/a' :: Would update.
CRDS - INFO -  instrument='ACS' type='IMPHTTAB' data='data/j8bt09jcq_raw.fits' ::  New best reference: 'n/a' --> 'w3m1716tj_imp.fits' :: Would update.
CRDS - INFO -  instrument='ACS' type='NPOLFILE' data='data/j8bt09jcq_raw.fits' ::  New best reference: 'n/a' --> 'v9718260j_npl.fits' :: Would update.
CRDS - INFO -  instrument='ACS' type='SHADFILE' data='data/j8bt09jcq_raw.fits' ::  New best reference: 'kcb1734pj_shd.fits' --> 'n/a' :: Would update.
CRDS - INFO -  Affected products = 3
data/j8bt05njq_raw.fits
data/j8bt06o6q_raw.fits
data/j8bt09jcq_raw.fits
CRDS - INFO -  0 errors
CRDS - INFO -  0 warnings
CRDS - INFO -  19 infos"""
    assert out_to_check in out
    test_config.cleanup(old_state)


def test_bestrefs_3_files_default_context_from_server(capsys):
    """Test computes simple bestrefs for 3 files using the default context from the server."""
    old_state = test_config.setup()
    argv = """bestrefs.py --new-context=hst.pmap --files data/j8bt05njq_raw.fits data/j8bt06o6q_raw.fits
     data/j8bt09jcq_raw.fits"""
    br.BestrefsScript(argv)()
    out, _ = capsys.readouterr()
    out_to_check = """CRDS - INFO -  No comparison context or source comparison requested.
CRDS - INFO -  No file header updates requested;  dry run.  Use --update-bestrefs to update FITS headers.
CRDS - INFO -  ===> Processing data/j8bt05njq_raw.fits
CRDS - INFO -  ===> Processing data/j8bt06o6q_raw.fits
CRDS - INFO -  ===> Processing data/j8bt09jcq_raw.fits
CRDS - INFO -  0 errors
CRDS - INFO -  0 warnings
CRDS - INFO -  5 infos"""
    assert out_to_check in out
    test_config.cleanup(old_state)


def test_bestrefs_broken_dataset_file(capsys):
    """Test tests error status when one broken file is included."""
    old_state = test_config.setup()
    argv = """bestrefs.py --new-context hst.pmap --files data/j8bt05njq_raw.fits data/j8bt05njq_raw_broke.fits
    data/j8bt06o6q_raw.fits data/j8bt09jcq_raw.fits"""
    br.BestrefsScript(argv)()
    out, _ = capsys.readouterr()
    out_to_check = """CRDS - INFO -  No comparison context or source comparison requested.
CRDS - INFO -  No file header updates requested;  dry run.  Use --update-bestrefs to update FITS headers.
CRDS - INFO -  ===> Processing data/j8bt05njq_raw.fits
CRDS - INFO -  ===> Processing data/j8bt05njq_raw_broke.fits
CRDS - ERROR -  instrument='ACS' type='BIASFILE' data='data/j8bt05njq_raw_broke.fits' ::  New: Bestref FAILED:   parameter='CCDAMP' value='FOOBAR' is not in ['A', 'ABCD', 'AC', 'AD', 'B', 'BC', 'BD', 'C', 'D']
CRDS - INFO -  ===> Processing data/j8bt06o6q_raw.fits
CRDS - INFO -  ===> Processing data/j8bt09jcq_raw.fits
CRDS - INFO -  1 errors
CRDS - INFO -  0 warnings
CRDS - INFO -  6 infos"""
    assert out_to_check in out
    test_config.cleanup(old_state)


# Hard to test due to failures
# def test_bestrefs_broken_cache_and_server(capsys):
#     """Test """
#     old_state = test_config.setup(cache="/nowhere", url="https://server-is-out-of-town")
#     argv = """bestrefs.py --new-context hst.pmap --files data/j8bt05njq_raw.fits"""
#     try:
#         br.BestrefsScript(argv)()
#     except OSError as e:
#         pass
#     out, err = capsys.readouterr()
#     #print(err)
# #    out_to_check = “”””””
# #    assert out_to_check in out
# #    test_config.cleanup(old_state)


def test_bestrefs_catalog_dataset(capsys):
    old_state = test_config.setup()
    argv = """bestrefs.py --new-context hst.pmap --hst --datasets LB6M01030"""
    br.BestrefsScript(argv)()
    out, _ = capsys.readouterr()
    out_to_check = """CRDS - INFO -  Dumping dataset parameters from CRDS server at 'https://hst-crds.stsci.edu' for ['LB6M01030']
CRDS - INFO -  Dumped 1 of 1 datasets from CRDS server at 'https://hst-crds.stsci.edu'
CRDS - INFO -  Computing bestrefs for datasets ['LB6M01030']
CRDS - INFO -  No comparison context or source comparison requested.
CRDS - INFO -  0 errors
CRDS - INFO -  0 warnings
CRDS - INFO -  4 infos"""
    assert out_to_check in out
    test_config.cleanup(old_state)


def test_bestrefs_context_to_context(capsys):
    old_state = test_config.setup()
    argv = """bestrefs.py --new-context data/hst_0001.pmap  --old-context hst.pmap --files data/j8bt05njq_raw.fits
    data/j8bt06o6q_raw.fits data/j8bt09jcq_raw.fits"""
    br.BestrefsScript(argv)()
    out, _ = capsys.readouterr()
    out_to_check = """CRDS - INFO -  No file header updates requested;  dry run.  Use --update-bestrefs to update FITS headers.
CRDS - INFO -  ===> Processing data/j8bt05njq_raw.fits
CRDS - INFO -  ===> Processing data/j8bt06o6q_raw.fits
CRDS - INFO -  ===> Processing data/j8bt09jcq_raw.fits
CRDS - INFO -  0 errors
CRDS - INFO -  0 warnings
CRDS - INFO -  4 infos"""
    assert out_to_check in out
    test_config.cleanup(old_state)


def test_bestrefs_all_instruments_hst(capsys):
    old_state = test_config.setup()
    argv = """bestrefs.py --new-context data/hst_0001.pmap --hst --old-context hst.pmap --all-instruments"""
    test_brs = br.BestrefsScript(argv)
    test_brs.complex_init()
    out, _ = capsys.readouterr()
    out_to_check = """CRDS - INFO -  Computing bestrefs for db datasets for ['acs', 'cos', 'nicmos', 'stis', 'wfc3', 'wfpc2']
CRDS - INFO -  Dumping dataset parameters for 'acs' from CRDS server at 'https://hst-crds.stsci.edu'
CRDS - INFO -  Downloaded  221101 dataset ids for 'acs' since None
CRDS - INFO -  Dumping dataset parameters for 'cos' from CRDS server at 'https://hst-crds.stsci.edu'
CRDS - INFO -  Downloaded  54271 dataset ids for 'cos' since None
CRDS - INFO -  Dumping dataset parameters for 'nicmos' from CRDS server at 'https://hst-crds.stsci.edu'
CRDS - INFO -  Downloaded  282999 dataset ids for 'nicmos' since None
CRDS - INFO -  Dumping dataset parameters for 'stis' from CRDS server at 'https://hst-crds.stsci.edu'
CRDS - INFO -  Downloaded  478619 dataset ids for 'stis' since None
CRDS - INFO -  Dumping dataset parameters for 'wfc3' from CRDS server at 'https://hst-crds.stsci.edu'
CRDS - INFO -  Downloaded  339162 dataset ids for 'wfc3' since None
CRDS - INFO -  Dumping dataset parameters for 'wfpc2' from CRDS server at 'https://hst-crds.stsci.edu'
CRDS - INFO -  Downloaded  186480 dataset ids for 'wfpc2' since None"""
    assert out_to_check in out
    test_config.cleanup(old_state)


def test_bestrefs_datasets_since_auto_hst(capsys):
    old_state = test_config.setup()
    argv = """bestrefs.py --old-context hst.pmap --new-context data/hst_0001.pmap --hst --diffs-only --datasets-since=auto"""
    test_brs = br.BestrefsScript(argv)
    test_brs.complex_init()
    out, _ = capsys.readouterr()
    out_to_check = """CRDS - INFO -  Mapping differences from 'hst.pmap' --> 'data/hst_0001.pmap' affect:
 {'acs': ['biasfile']}
CRDS - INFO -  Possibly affected --datasets-since dates determined by 'hst.pmap' --> 'data/hst_0001.pmap' are:
 {'acs': '1992-01-02 00:00:00'}
CRDS - INFO -  Computing bestrefs for db datasets for ['acs']
CRDS - INFO -  Dumping dataset parameters for 'acs' from CRDS server at 'https://hst-crds.stsci.edu' since '1992-01-02 00:00:00'
CRDS - INFO -  Downloaded  221101 dataset ids for 'acs' since '1992-01-02 00:00:00'"""
    assert out_to_check in out
    test_config.cleanup(old_state)


def test_bestrefs_dataset_drop_ids(capsys):
    old_state = test_config.setup()
    argv = """bestrefs.py --new-context data/hst_0001.pmap  --old-context hst.pmap --load-pickle data/test_cos.json --drop-ids LCE31SW6Q:LCE31SW6Q"""
    test_brs = br.BestrefsScript(argv)
    test_brs.complex_init()
    out, _ = capsys.readouterr()
    out_to_check = """CRDS - INFO -  Loading file 'data/test_cos.json'
CRDS - INFO -  Loaded 1 datasets from file 'data/test_cos.json' completely replacing existing headers."""
    assert out_to_check in out
    test_config.cleanup(old_state)


def test_bestrefs_dataset_only_ids(capsys):
    old_state = test_config.setup()
    argv = """bestrefs.py --new-context data/hst_0001.pmap  --old-context hst.pmap --load-pickle data/test_cos.json --only-ids LPPPPPP6Q:LCE31SW6Q"""
    test_brs = br.BestrefsScript(argv)
    test_brs.complex_init()
    out, _ = capsys.readouterr()
    out_to_check = """CRDS - INFO -  Loading file 'data/test_cos.json'
CRDS - INFO -  Loaded 1 datasets from file 'data/test_cos.json' completely replacing existing headers."""
    assert out_to_check in out
    test_config.cleanup(old_state)


def test_bestrefs_compare_source_canary(capsys):
    old_state = test_config.setup()
    argv = """crds.bestrefs --new-context hst_0551.pmap --compare-source --load-pickles data/canary.json --differences-are-errors --hst"""
    test_brs = br.BestrefsScript(argv)()
    out, _ = capsys.readouterr()
    out_to_check = """CRDS - INFO -  Loading file 'data/canary.json'
CRDS - INFO -  Loaded 1 datasets from file 'data/canary.json' completely replacing existing headers.
CRDS - ERROR -  instrument='COS' type='BPIXTAB' data='LA7803FIQ' ::  Comparison difference: 'bar.fits' --> 'yae1249sl_bpix.fits' :: Would update.
CRDS - ERROR -  instrument='COS' type='XWLKFILE' data='LA7803FIQ' ::  Comparison difference: 'foo.fits' --> '14o2013ql_xwalk.fits' :: Would update.
CRDS - INFO -  2 errors
CRDS - INFO -  0 warnings
CRDS - INFO -  2 infos"""
    assert out_to_check in out
    test_config.cleanup(old_state)

def test_bestrefs_donotreprocess_datasets(capsys):
    old_state = test_config.setup()
    argv = """crds.bestrefs --old-context hst_0628.pmap --new-context hst_0633.pmap --hst --datasets JA9553LVQ JBBGRCGFQ"""
    test_brs = br.BestrefsScript(argv)()
    out, _ = capsys.readouterr()
    out_to_check = """CRDS - INFO -  Dumping dataset parameters from CRDS server at 'https://hst-crds.stsci.edu' for ['JA9553LVQ', 'JBBGRCGFQ']
CRDS - INFO -  Dumped 2 of 2 datasets from CRDS server at 'https://hst-crds.stsci.edu'
CRDS - INFO -  Computing bestrefs for datasets ['JA9553LVQ', 'JBBGRCGFQ']
CRDS - INFO -  0 errors
CRDS - INFO -  0 warnings
CRDS - INFO -  3 infos"""
    assert out_to_check in out
    test_config.cleanup(old_state)


def test_bestrefs_donotreprocess_fix(capsys):
    old_state = test_config.setup()
    argv = """crds.bestrefs --hst --old-context hst_0628.pmap --new-context hst_0633.pmap --print-affected --load-pickle data/bestrefs_dnr_fix.json --verbosity=30"""
    test_brs = br.BestrefsScript(argv)()
    out, _ = capsys.readouterr()
    out_to_check = """CRDS - DEBUG -  Command: ['crds.bestrefs', '--hst', '--old-context', 'hst_0628.pmap', '--new-context', 'hst_0633.pmap', '--print-affected', '--load-pickle', 'data/bestrefs_dnr_fix.json', '--verbosity=30']
CRDS - DEBUG -  Using explicit new context 'hst_0633.pmap' for computing updated best references.
CRDS - DEBUG -  Using explicit old context 'hst_0628.pmap'
CRDS - INFO -  Loading file 'data/bestrefs_dnr_fix.json'
CRDS - INFO -  Loaded 1 datasets from file 'data/bestrefs_dnr_fix.json' completely replacing existing headers.
CRDS - DEBUG -  ===> Processing JA9553M3Q:JA9553M3Q
CRDS - DEBUG -  instrument='ACS' type='ATODTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='BIASFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='BPIXTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 't3n1116nj_bpx.fits' :: No update.
CRDS - DEBUG -  instrument='ACS' type='CCDTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'uc82140bj_ccd.fits' :: No update.
CRDS - DEBUG -  instrument='ACS' type='CFLTFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='CRREJTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='D2IMFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - INFO -  instrument='ACS' type='DARKFILE' data='JA9553M3Q:JA9553M3Q' ::  New best reference: '1ag2019jj_drk.fits' --> '25815071j_drk.fits' :: Would update.
CRDS - DEBUG -  instrument='ACS' type='DGEOFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'qbu16423j_dxy.fits' :: No update.
CRDS - INFO -  instrument='ACS' type='DRKCFILE' data='JA9553M3Q:JA9553M3Q' ::  New best reference: '1ag20119j_dkc.fits' --> '2581508ij_dkc.fits' :: Would update.
CRDS - DEBUG -  instrument='ACS' type='FLSHFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='IDCTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: '0461802dj_idc.fits' :: No update.
CRDS - DEBUG -  instrument='ACS' type='IMPHTTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='MDRIZTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='MLINTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='NPOLFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='OSCNTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: '17717071j_osc.fits' :: No update.
CRDS - DEBUG -  instrument='ACS' type='PCTETAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: '19i16323j_cte.fits' :: No update.
CRDS - DEBUG -  instrument='ACS' type='PFLTFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='SHADFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='SNKCFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='SPOTTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - INFO -  Affected products = 1
ja9553m3q
CRDS - DEBUG -  1 sources processed
CRDS - DEBUG -  1 source updates
CRDS - INFO -  0 errors
CRDS - INFO -  0 warnings
CRDS - INFO -  5 infos"""
    assert out_to_check in out
    test_config.cleanup(old_state)


def test_bestrefs_multiple_updates_with_error(capsys):
    old_state = test_config.setup()
    argv = """crds.bestrefs --hst --old-context hst_0628.pmap --new-context hst_0633.pmap --print-affected --load-pickle data/bestrefs_new_error.json --verbosity=30"""
    test_brs = br.BestrefsScript(argv)()
    out, _ = capsys.readouterr()
    out_to_check = """CRDS - DEBUG -  Command: ['crds.bestrefs', '--hst', '--old-context', 'hst_0628.pmap', '--new-context', 'hst_0633.pmap', '--print-affected', '--load-pickle', 'data/bestrefs_new_error.json', '--verbosity=30']
CRDS - DEBUG -  Using explicit new context 'hst_0633.pmap' for computing updated best references.
CRDS - DEBUG -  Using explicit old context 'hst_0628.pmap'
CRDS - INFO -  Loading file 'data/bestrefs_new_error.json'
CRDS - INFO -  Loaded 1 datasets from file 'data/bestrefs_new_error.json' completely replacing existing headers.
CRDS - DEBUG -  ===> Processing JA9553M3Q:JA9553M3Q
CRDS - DEBUG -  instrument='ACS' type='ATODTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - ERROR -  instrument='ACS' type='BIASFILE' data='JA9553M3Q' ::  Old: Bestref FAILED:   parameter='CCDGAIN' value='2.4' is not in ['0.5', '1.0', '1.4', '2.0', '4.0', '8.0']
CRDS - ERROR -  instrument='ACS' type='BIASFILE' data='JA9553M3Q' ::  New: Bestref FAILED:   parameter='CCDGAIN' value='2.4' is not in ['1.0', '2.0', '4.0', '8.0']
CRDS - DEBUG -  instrument='ACS' type='BPIXTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 't3n1116nj_bpx.fits' :: No update.
CRDS - DEBUG -  instrument='ACS' type='CCDTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'uc82140bj_ccd.fits' :: No update.
CRDS - DEBUG -  instrument='ACS' type='CFLTFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='CRREJTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='D2IMFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='DARKFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='DGEOFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'qbu16423j_dxy.fits' :: No update.
CRDS - DEBUG -  instrument='ACS' type='DRKCFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='FLSHFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='IDCTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: '0461802dj_idc.fits' :: No update.
CRDS - DEBUG -  instrument='ACS' type='IMPHTTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='MDRIZTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='MLINTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='NPOLFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='OSCNTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: '17717071j_osc.fits' :: No update.
CRDS - DEBUG -  instrument='ACS' type='PCTETAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: '19i16323j_cte.fits' :: No update.
CRDS - DEBUG -  instrument='ACS' type='PFLTFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='SHADFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='SNKCFILE' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - DEBUG -  instrument='ACS' type='SPOTTAB' data='JA9553M3Q:JA9553M3Q' ::  Lookup MATCHES: 'n/a' :: No update.
CRDS - INFO -  Affected products = 0
CRDS - DEBUG -  1 sources processed
CRDS - DEBUG -  0 source updates
CRDS - INFO -  2 errors
CRDS - INFO -  0 warnings
CRDS - INFO -  3 infos"""
    assert out_to_check in out
    test_config.cleanup(old_state)


def test_cleanpath(capsys):
    """Test removes prefixes added to reference files prior to writing into FITS headers."""
    assert br.cleanpath('jref$foo.fits') == 'foo.fits'
    assert br.cleanpath('crds://foo.fits') == 'foo.fits'
    assert br.cleanpath('crds://foo.fits') == 'foo.fits'
    assert br.cleanpath('something/foo.fits') == 'something/foo.fits'


def test_hst_tobs_header_to_reftypes(capsys):
    """Test demonstrates header_to_reftypes will get reftypes to list form."""
    from crds.hst.locate import header_to_reftypes
    assert header_to_reftypes({}, "hst.pmap") == []
    from crds.tobs.locate import header_to_reftypes
    assert header_to_reftypes({}, "tobs.pmap") == []
    from crds.jwst.locate import header_to_reftypes
    ref_to_c = ['ipc', 'linearity', 'mask', 'refpix', 'rscd', 'saturation', 'superbias']
    assert header_to_reftypes({"EXP_TYPE": "MIR_DARK", "CAL_VER": "0.7.0"}, "jwst_0301.pmap") == ref_to_c
    assert header_to_reftypes({"EXP_TYPE": "NIR_IMAGE", "CAL_VER": "0.7.0"}, "jwst_0301.pmap") == []
    out, _ = capsys.readouterr()
    out_to_check = """CRDS - WARNING -  Failed determining reftypes for {'CAL_VER': '0.7.0', 'EXP_TYPE': 'NIR_IMAGE'} : "Failed determining required pipeline .cfgs for EXP_TYPE 'NIR_IMAGE' : 'NIR_IMAGE'"
    """
    assert out in out_to_check
    ref_to_c = ['area', 'camera', 'collimator', 'dark', 'disperser', 'distortion', 'filteroffset', 'fore', 'fpa',
                'gain', 'ifufore', 'ifupost', 'ifuslicer', 'ipc', 'linearity', 'mask', 'msa', 'ote', 'photom',
                'readnoise', 'refpix', 'regions', 'rscd', 'saturation', 'specwcs', 'superbias', 'v2v3',
                'wavelengthrange']

    assert header_to_reftypes({"EXP_TYPE":"MIR_IMAGE", "CAL_VER": "0.7.0"}, "jwst_0301.pmap") == ref_to_c


class TestBestrefs(test_config.CRDSTestCase):

    script_class = BestrefsScript
    # server_url = "https://hst-crds-dev.stsci.edu"
    cache = test_config.CRDS_TESTING_CACHE

    def get_10_days_ago(self):
        now = datetime.datetime.now()
        now -= datetime.timedelta(days=10)
        return now.isoformat().split("T")[0]

    def test_bestrefs_affected_datasets(self):
        self.run_script(f"crds.bestrefs --affected-datasets --old-context hst_0978.pmap --new-context hst_0980.pmap "
                        f"--datasets-since {self.get_10_days_ago()}",
                        expected_errs=0)

    def test_bestrefs_from_pickle(self):
        self.run_script("crds.bestrefs --new-context hst_0315.pmap --load-pickle data/test_cos.pkl --stats --print-affected-details",
                        expected_errs=0)

    def test_bestrefs_to_pickle(self):
        self.run_script("crds.bestrefs --datasets LA9K03C3Q:LA9K03C3Q LA9K03C5Q:LA9K03C5Q LA9K03C7Q:LA9K03C7Q "
                        "--new-context hst_0315.pmap --save-pickle test_cos.pkl --stats",
                        expected_errs=0)
        os.remove("test_cos.pkl")

    def test_bestrefs_from_json(self):
        self.run_script("crds.bestrefs --new-context hst_0315.pmap --load-pickle data/test_cos.json --stats",
                        expected_errs=1)

    def test_bestrefs_to_json(self):
        self.run_script(f"crds.bestrefs --instrument cos --new-context hst_0315.pmap --save-pickle test_cos.json "
                        f"--datasets-since {self.get_10_days_ago()}", expected_errs=None)
        os.remove("test_cos.json")

    def test_bestrefs_at_file(self):
        self.run_script("crds.bestrefs --files @data/bestrefs_file_list  --new-context hst_0315.pmap --stats",
                        expected_errs=0)

    def test_bestrefs_remote(self):
        self.run_script("crds.bestrefs --files @data/bestrefs_file_list  --new-context hst_0315.pmap --remote --stats",
                        expected_errs=0)

    def test_bestrefs_new_references(self):
        self.run_script("crds.bestrefs --files @data/bestrefs_file_list  --new-context hst_0315.pmap --print-new-references --stats",
                        expected_errs=0)

    def test_bestrefs_default_new_context(self):
        self.run_script("crds.bestrefs --files @data/bestrefs_file_list  --stats",
                        expected_errs=0)

    def test_bestrefs_update_file_headers(self):
        shutil.copy("data/j8bt06o6q_raw.fits", "j8bt06o6q_raw.fits")
        self.run_script("crds.bestrefs --files ./j8bt06o6q_raw.fits --new-context hst_0315.pmap --update-bestrefs",
                       expected_errs=0)
        os.remove("j8bt06o6q_raw.fits")

    def test_bestrefs_update_bestrefs(self):
        # """update_bestrefs modifies dataset file headers"""
        shutil.copy("data/j8bt06o6q_raw.fits", "j8bt06o6q_raw.fits")
        self.run_script("crds.bestrefs --files ./j8bt06o6q_raw.fits --new-context hst_0315.pmap --update-bestrefs",
                       expected_errs=0)
        os.remove("j8bt06o6q_raw.fits")

    def test_bestrefs_bad_sources(self):
        with self.assertRaises(AssertionError):
            self.run_script("crds.bestrefs --all-instruments --instrument cos --new-context hst_0315.pmap",
                            expected_errs=1)

    def test_bestrefs_update_headers(self):
        # """update_headers updates original headers from a pickle saving a new pickle withn orginal + overrides."""
        self.run_script("crds.bestrefs --new-context hst_0315.pmap --datasets LCE31SW6Q:LCE31SW6Q --load-pickle data/test_cos_update.json "
                        " --save-pickle ./test_cos_combined.json --update-bestrefs --update-pickle", expected_errs=1)
        with open("./test_cos_combined.json") as pfile:
            header = json.load(pfile)
        header = header["LCE31SW6Q:LCE31SW6Q"]
        badttab = header["BADTTAB"]
        self.assertEqual(badttab, "N/A")
        gsagtab = header["GSAGTAB"]
        self.assertEqual(gsagtab, "X6L1439EL_GSAG.FITS")
        flatfile = header["FLATFILE"]
        self.assertEqual(flatfile, "N/A")
        os.remove("./test_cos_combined.json")

    def test_assign_bestrefs(self):
        test_copy = "cos_N8XTZCAWQ_updated.fits"
        shutil.copy("data/cos_N8XTZCAWQ.fits", test_copy)

        errors = assign_bestrefs([test_copy], context="hst_0500.pmap")
        self.assertEqual(errors, 0)

        os.remove(test_copy)



# # New tests
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


@pytest.mark.parametrize('line, expected',
                         [
                             ('\u0068\u0065\u006C\u006C\u006F', "'hello'"),
                         ])
def test_sreprlow(line, expected):
    """Test should return lowercase repr() of input."""
    assert br.sreprlow(line) == expected


@pytest.mark.parametrize('line, expected',
                         [
                             ('jref$n4e12510j_crr.fits', 'n4e12510j_crr.fits'),
                             ('crds://jwst_miri_dark_0070.fits', 'jwst_miri_dark_0070.fits'),
                         ])
def test_cleanpath(line, expected):
    """Test should demonstrate that filename is cleaned of 'ref$' and 'crds://' prepends."""
    assert br.cleanpath(line) == expected


def test_init_func():
    test_brs = br.BestrefsScript()
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
    test_brs2 = br.BestrefsScript(argv)
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


def test_complex_init():
    """Test should initiate complex init and show each argument working."""
    argv = """crds.bestrefs --load-pickles data/bestrefs.special.json
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
    assert test_brs.args.load_pickles == ['data/bestrefs.special.json']
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
    argv = """crds.bestrefs --new-context data/hst_0001.pmap
           --old-context data/hst.pmap --hst --diffs-only"""
    test_brs = br.BestrefsScript(argv)
    test_brs.complex_init()
    assert test_brs.args.diffs_only is True
    assert test_brs.args.hst is True

    # all_instruments
    argv = """crds.bestrefs --all-instruments --hst"""
    test_brs = br.BestrefsScript(argv)
    test_brs.complex_init()
    assert test_brs.args.all_instruments is True

    # instruments
    argv = "crds.bestrefs --instruments acs cos stis wfc3 --hst"
    test_brs = br.BestrefsScript(argv)
    test_brs.complex_init()
    assert test_brs.args.instruments == ['acs', 'cos', 'stis', 'wfc3']

    # datasets
    argv = """crds.bestrefs --datasets LB6M01030 --hst"""
    test_brs = br.BestrefsScript(argv)
    test_brs.complex_init()
    assert test_brs.args.datasets == ['LB6M01030']

    # files
    argv = """crds.bestrefs --files data/j8bt05njq_raw.fits --hst"""
    test_brs = br.BestrefsScript(argv)
    test_brs.complex_init()
    assert test_brs.args.files == ['data/j8bt05njq_raw.fits']


@pytest.mark.parametrize('line, expected',
                        [
                            ('jw01444-o002_20220618t005802_spec3_001',
                             'JW01444-O002_20220618T005802_SPEC3_001:JW01444-O002_20220618T005802_SPEC3_001'),
                            ('icir09ehq:icir09ehq', 'ICIR09EHQ:ICIR09EHQ'),
                        ])
def test_normalize_id(line, expected):
    """Test should show that datasets are converted to uppercase and given <exposure>:<exposure> form."""
    test_brs = br.BestrefsScript()
    assert test_brs.normalize_id(line) == expected


def test_only_ids():
    """Test should demonstrate only_ids is set to None."""
    test_brs = br.BestrefsScript()
    assert test_brs.only_ids is None


def test_drop_ids():
    """Test should demonstrate drop_ids is set to []."""
    test_brs = br.BestrefsScript()
    assert isinstance(test_brs.drop_ids, list)
    assert len(test_brs.drop_ids) == 0


@pytest.mark.parametrize('line, expected',
                         [
                             (['id1', 'Id2:iD2'], ['ID1:ID1', 'ID2:ID2']),
                             ([], [])
                         ])
def test__normalized(line, expected):
    """Test should demonstrate that a list of dataset IDs is normalized."""
    test_brs = br.BestrefsScript()
    assert test_brs._normalized(line) == expected


@pytest.mark.parametrize('line, expected',
                         [
                             ('lezcg2010', 'lezcg2010'),
                         ])
def test_locate_file(line, expected):
    """Test should demonstrate that a list of dataset IDs is normalized."""
    test_brs = br.BestrefsScript()
    assert test_brs.locate_file(line) == expected


def test_auto_datasets_since():
    """Test makes a call to the server to identify datasets affected by incrementing pmap."""
    test_dict = {
        'acs': '1992-01-02 00:00:00'
    }
    argv = """crds.bestrefs  --old-context hst.pmap --new-context data/hst_0001.pmap
    --diffs-only --hst --datasets-since=auto
    """
    test_brs = br.BestrefsScript(argv)
    test_brs.complex_init()
    test_val = test_brs.auto_datasets_since()
    assert test_val == test_dict


def test_setup_contexts():
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

    argv = """crds.bestrefs --diffs-only --new-context data/hst_0001.pmap"""
    test_brs = br.BestrefsScript(argv)
    new, old = test_brs.setup_contexts()
    assert new == 'data/hst_0001.pmap'


def test_update_promise():
    """Test outputs a message if the bestrefs would be updated or it updating has started."""
    argv = """crds.bestrefs --new-context data/hst_0001.pmap
            --old-context data/hst.pmap --hst --diffs-only"""
    test_brs = br.BestrefsScript(argv)
    test_val = test_brs.update_promise
    assert test_brs.update_promise == ":: Would update."
    argv = """crds.bestrefs --new-context data/hst_0001.pmap --update-bestrefs
                --old-context data/hst.pmap --hst --diffs-only --verbosity=55"""
    test_brs = br.BestrefsScript(argv)
    test_val = test_brs.update_promise
    assert test_brs.update_promise == ":: Updating."

def test_get_bestrefs():
    """Test gets bestrefs for supplied header."""
    # A function that looks a little simple on the surface, this function actually touches some
    # 10 other functions in several other modules to calculate bestrefs. It took alot of time to look
    # through them and I still don't think I quite understand how to trigger the system to actually
    # retrieve the best references, as I tried a dozen or so variations of the supplied header dict
    # to no avail. I'd like to revisit this at a later time and flesh out more testing capabilities
    # for one of the namesake functions of the bestrefs module.
    argv = """crds.bestrefs --hst"""
    test_brs = br.BestrefsScript(argv)
    value_to_test = test_brs.get_bestrefs('acs', 'data/hst_acs_atodtab_0251.rmap', 'hst_1000.pmap',
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


def test_verbose_with_prefix(capsys):
    """Test checks that verbose log message has had a prefix format made."""
    argv = """crds.bestrefs --hst --instrument=acs --verbosity=55"""
    test_brs = br.BestrefsScript(argv)
    # Send logs to stdout
    log.set_test_mode()
    test_brs.verbose_with_prefix('data/j8bt05njq_raw.fits', 'acs', 'ANY')
    msg_to_check = """CRDS - DEBUG -  instrument='ACS' type='ANY' data='data/j8bt05njq_raw.fits' ::"""
    out, _ = capsys.readouterr()
    assert msg_to_check in out


def test_screen_bestrefs(capsys):
    """Test checks for references that are atypical or known to be avoided."""
    argv = """crds.bestrefs --hst --instrument=acs --verbosity=55"""
    test_brs = br.BestrefsScript(argv)
    test_brs.skip_filekinds.append("brftab")
    # Send logs to stdout
    log.set_test_mode()
    bestrefs_dict = {"BRFTAB": "N/A", "SEGMENT": "N/A", "WCPTAB": "XAF1429EL_WCP.FITS"}
    tuple1, tuple2 = test_brs.screen_bestrefs('acs', 'data/j8bt05njq_raw.fits', bestrefs_dict)
    out, err = capsys.readouterr()
    check_msg1 = """type='BRFTAB' data='data/j8bt05njq_raw.fits' ::  Skipping type."""
    check_msg2 = """type='SEGMENT' data='data/j8bt05njq_raw.fits' ::  Bestref FOUND: 'n/a' :: Would update."""
    check_msg3 = """'WCPTAB' data='data/j8bt05njq_raw.fits' ::  Bestref FOUND: 'xaf1429el_wcp.fits' :: Would update."""
    assert check_msg1 in out
    assert check_msg2 in out
    assert check_msg3 in out
    assert tuple1[0] == 'acs'
    assert tuple1[1] == 'segment'
    assert tuple1[2] is None
    assert tuple1[3] == 'N/A'
    assert tuple2[0] == 'acs'
    assert tuple2[1] == 'wcptab'
    assert tuple2[2] is None
    assert tuple2[3] == 'XAF1429EL_WCP.FITS'


def test_handle_na_and_not_found(capsys):
    """Test obtains bestref if available and handles matched N/A or NOT FOUND references."""
    argv = """crds.bestrefs --hst --instrument=acs --verbosity=55"""
    test_brs = br.BestrefsScript(argv)
    log.set_test_mode()
    # No match, => 'N/A'
    bestrefs_dict = {"BRFTAB": "N/A", "SEGMENT": "N/A", "WCPTAB": "XAF1429EL_WCP.FITS"}
    test_brs.handle_na_and_not_found('Old', bestrefs_dict, 'data/j8bt05njq_raw.fits', 'acs', 'jref$n4e12510j_crr.fits')
    out, _ = capsys.readouterr()
    msg_to_check = """Old No match found: 'UNDEFINED'  => 'N/A'"""
    assert msg_to_check in out
    # No match, without => 'N/A'
    argv = """crds.bestrefs --hst --instrument=acs --check-context --old-context hst_0315.pmap --verbosity=55"""
    test_brs = br.BestrefsScript(argv)
    test_brs.handle_na_and_not_found('New', bestrefs_dict, 'data/j8bt05njq_raw.fits', 'acs', 'jref$n4e12510j_crr.fits')
    out, _ = capsys.readouterr()
    msg_to_check = """New No match found: 'UNDEFINED'"""
    msg_not_seen = """=> 'N/A'"""
    assert msg_to_check in out
    assert msg_not_seen not in out
    # Match, natural N/A
    argv = """crds.bestrefs --hst --instrument=acs --check-context --old-context hst_0315.pmap --verbosity=55"""
    test_brs = br.BestrefsScript(argv)
    bestrefs_dict = {"BRFTAB": "N/A", "SEGMENT": "N/A", "JREF$N4E12510J_CRR.FITS": "NOT FOUND N/A"}
    ref_ok, ref = test_brs.handle_na_and_not_found('New', bestrefs_dict, 'data/j8bt05njq_raw.fits',
                                                   'acs', 'jref$n4e12510j_crr.fits')
    assert ref_ok is True
    assert ref == 'N/A'
    # Match, Failed
    argv = """crds.bestrefs --hst --instrument=acs --check-context --old-context hst_0315.pmap --verbosity=55"""
    test_brs = br.BestrefsScript(argv)
    bestrefs_dict = {"BRFTAB": "N/A", "SEGMENT": "N/A", "JREF$N4E12510J_CRR.FITS": "NOT FOUND"}
    ref_ok, ref = test_brs.handle_na_and_not_found('New', bestrefs_dict, 'data/j8bt05njq_raw.fits',
                                                   'acs', 'jref$n4e12510j_crr.fits')
    out, _ = capsys.readouterr()
    msg_to_check = """New Bestref FAILED:"""
    assert msg_to_check in out
    # Match, good
    argv = """crds.bestrefs --hst --instrument=acs --check-context --old-context hst_0315.pmap --verbosity=55"""
    test_brs = br.BestrefsScript(argv)
    bestrefs_dict = {"BRFTAB": "N/A", "SEGMENT": "N/A", "JREF$N4E12510J_CRR.FITS": "jref$n4e12510j_crr.fits"}
    ref_ok, ref = test_brs.handle_na_and_not_found('New', bestrefs_dict, 'data/j8bt05njq_raw.fits',
                                                   'acs', 'jref$n4e12510j_crr.fits')
    assert ref_ok is True
    assert ref == 'N4E12510J_CRR.FITS'


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


def test_dataset_to_product_id():
    """Test confirms that product ID is returned by function."""
    argv = """crds.bestrefs --hst --verbosity=0"""
    test_brs = br.BestrefsScript(argv)
    dataset_to_test = 'icir09ehq:ICIR09EHQ'
    product_id = dataset_to_test.split(":")[0].lower()
    assert test_brs.dataset_to_product_id(dataset_to_test) == product_id


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






