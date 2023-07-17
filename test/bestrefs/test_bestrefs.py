import pytest
import os, os.path
import sys
import re
import datetime
import crds
import logging
from crds.hst import locate
from crds.core import log, config, utils, timestamp, cmdline, heavy_client
from crds.hst import TYPES, INSTRUMENTS, FILEKINDS, EXTENSIONS, INSTRUMENT_FIXERS, TYPE_FIXERS
from crds.client import api
from crds.bestrefs import bestrefs as br
from crds.core.timestamp import format_date, parse_date
from astropy.time import Time


@pytest.fixture(autouse=True)
def reset_log():
    yield
    log.reset()


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
    log.reset()
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


def test_warn_bad_context(capsys):
    """Test logs an error or warning if the named context is a known bad context."""
    log.reset()
    # Send logs to stdout
    log.set_test_mode()
    argv = """crds.bestrefs -n jwst_1091.pmap -o jwst_1090.pmap --instruments miri --jwst"""
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
#    log.reset()
    # Send logs to stdout
    log.set_test_mode()
    argv = """crds.bestrefs -n jwst_1091.pmap -o jwst_1090.pmap --jwst --instruments miri"""
    test_brs = br.BestrefsScript(argv)
    test_brs.warn_bad_reference('jwst_miri_dark_0008.rmap','miri', 'ANY', 'jwst_miri_flat_0002.rmap')
    out, _ = capsys.readouterr()
    check_msg = """CRDS - ERROR -  instrument='MIRI' type='ANY' data='jwst_miri_dark_0008.rmap'"""
    assert check_msg in out
    argv = """crds.bestrefs -n jwst_1091.pmap -o jwst_1090.pmap --jwst --instruments miri
    --allow-bad-references"""
    test_brs = br.BestrefsScript(argv)
    test_brs.warn_bad_reference('jwst_miri_dark_0008.rmap', 'miri', 'ANY', 'jwst_miri_flat_0002.rmap')
    out, _ = capsys.readouterr()
    check_msg = """CRDS - WARNING -  For jwst_miri_dark_0008.rmap miri ANY File 'jwst_miri_flat_0002.rmap'"""
    assert check_msg in out


def test_verbose_with_prefix(capsys):
    """Test checks that verbose log message has had a prefix format made."""
    log.reset()
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
#    log.reset()
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


#Still figuring this out
# def test_warn_bad_updates():
#     """Test issues a warning for each of the 3 bad references provided."""
#     os.environ['CRDS_SERVER_URL'] = 'https://jwst-crds.stsci.edu'
#     argv = """crds.bestrefs -n jwst_1091.pmap -o jwst_1090.pmap --jwst --instruments miri"""
#     test_brs = br.BestrefsScript(argv)
#     print('\n')
#     print(test_brs.bad_files)
#     print(test_brs.updates)
#     print(test_brs.warn_bad_updates())


# Templates
#def test_init_headers():

#def test_init_comparison():

#def test_main():

#def test_process():

#def test__process():

#def test_determine_reftypes():




#def test_compare_bestrefs():

#def test__compare_bestrefs():



#def test_log_and_track_error():

#def test_post_processing():

#def test_optimize_tables():

#def test_unkilled_updates():

#def test_print_affected():

#def test_dataset_to_product_id():

#def test_print_affected_details():

#def test_print_update_stats():

#def test_print_new_references():

#def test_eliminate_duplicate_cases():

#def test_updates_repr():

#def test_sync_references():

# Scrap template for testing output
#@pytest.mark.paramatrize('line, expected',
#                          [
#                              (,),
#                          ])
#def test_():
    #""""""
    #argv = """argv="crds.bestrefs --load-pickles data/bestrefs.special.json
    #    --new-context hst_0315.pmap
    #    """

    ### Identifying values of self.args for bestrefs
    #test_brs2 = br.BestrefsScript(argv="crds.bestrefs --regression")
    #print('\n\n')
    #for argy in test_brs2.args.__dict__:
    #    if argy == 'compare_source_bestrefs':
    #        print(f'{argy} == {test_brs2.args.__dict__[argy]}')


