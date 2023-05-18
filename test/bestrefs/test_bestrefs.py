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


# Currently hung up on how to test the property decorated functions "only_ids" and "drop_ids"
#@pytest.mark.parametrize('line, expected',
#                          [
#                              ([], [])
#                              (['id1', 'Id2:iD2'], ['ID1:ID1', 'ID2:ID2']),
#                          ])
#def test_only_ids():
#    """Test should demonstrate normalization of ID list."""
#    test_brs = br.BestrefsScript()
#    print(test_brs.args)
#    print(test_brs.only_ids)
#    assert test_brs.only_ids == expected

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
#def test_complex_init():

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

