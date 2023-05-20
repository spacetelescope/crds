import pytest
import sys
import re
import datetime
from crds.bestrefs import bestrefs as br
from crds.core.timestamp import format_date, parse_date
from astropy.time import Time


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




# Templates
#def test_auto_datasets_since():

#def test_add_args():

#def test_setup_contexts():

#def test_warn_bad_context():

#def test_warn_bad_reference():

#def test_warn_bad_updates():

#def test_locate_file():

#def test_init_headers():

#def test_init_comparison():

#def test_main():

#def test_process():

#def test__process():

#def test_get_bestrefs():

#def test_determine_reftypes():

#def test_update_promise():

#def test_verbose_with_prefix():

#def test_screen_bestrefs():

#def test__screen_bestrefs():

#def test_compare_bestrefs():

#def test__compare_bestrefs():

#def test_handle_na_and_not_found():

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
#    """"""
#    test_brs = br.BestrefsScript()

