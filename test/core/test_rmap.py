"""This module tests some of the more complex features of the basic rmap infrastructure.
"""
from pytest import mark, fixture
import os
import json
import pickle
import sys
import crds
from crds import rmap, log, utils
from crds import config as crds_config
from crds.core.exceptions import *
import logging
log.THE_LOGGER.logger.propagate=True
log.set_verbose(50)


# ==================================================================================

@mark.hst
@mark.core
@mark.rmap
def test_get_derived_from_created(default_shared_state, caplog):
    p = rmap.get_cached_mapping("hst.pmap")
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        p.get_derived_from()
        out = caplog.text
    expected = " Skipping derivation checks for root mapping 'hst.pmap' derived_from = 'created by hand 12-23-2011'"
    for msg in expected.splitlines():
        assert msg.strip() in out


@mark.hst
@mark.core
@mark.rmap
def test_get_derived_from_phony(default_shared_state, caplog, hst_data):
    r = rmap.get_cached_mapping(f"{hst_data}/hst_acs_darkfile_phony_derive.rmap")
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        r.get_derived_from()
        out = caplog.text
    expected = " Parent mapping for 'hst_acs_darkfile_phony_derive.rmap' = 'phony.rmap' does not exist."
    for msg in expected.splitlines():
        assert msg.strip() in out


@mark.hst
@mark.core
@mark.rmap
def test_rmap_missing_references(default_shared_state, hst_data):
    """
    These are all missing because there is no reference file cache in this mode.
    """
    r = rmap.get_cached_mapping(f"{hst_data}/hst_acs_darkfile_comment.rmap")
    missing = r.missing_references()
    expected = [
        'lcb12060j_drk.fits',
        'n3o1022cj_drk.fits',
        'n3o1022ej_drk.fits',
        'n3o1022fj_drk.fits',
        'n3o1022hj_drk.fits',
        'n3o1022ij_drk.fits',
        'n3o1022kj_drk.fits',
        'n3o1022lj_drk.fits',
        'r1u1415ij_drk.fits',
        'r1u1415kj_drk.fits',
        'r1u1415mj_drk.fits'
    ]
    for i in expected:
        assert i in missing


@mark.hst
@mark.core
@mark.rmap
def test_rmap_minimum_header(default_shared_state, hst_data):
    p = rmap.get_cached_mapping("hst.pmap")
    header = p.get_minimum_header(f"{hst_data}/cos_N8XTZCAWQ.fits")
    expected = {
        'CAMERA': '3.0',
        'DATE-OBS': '2005-05-13',
        'FILTER': 'F160W',
        'INSTRUME': 'NICMOS',
        'NREAD': '1.0',
        'OBSMODE': 'MULTIACCUM',
        'READOUT': 'FAST',
        'REFTYPE': 'UNDEFINED',
        'SAMP_SEQ': 'SPARS64',
        'TIME-OBS': '11:00:47'
    }
    for k, v in expected.items():
        assert header[k] == v


@mark.hst
@mark.core
@mark.rmap
def test_rmap_str(default_shared_state, hst_data):
    r = rmap.get_cached_mapping(f"{hst_data}/hst_cos_bpixtab_0252.rmap")
    header = str(r)
    expected = "header = {\n    'derived_from' : 'hst_cos_bpixtab_0251.rmap',\n    'filekind' : 'BPIXTAB',\n    'instrument' : 'COS',\n    'mapping' : 'REFERENCE',\n    'name' : 'hst_cos_bpixtab_0252.rmap',\n    'observatory' : 'HST',\n    'parkey' : (('DETECTOR',), ('DATE-OBS', 'TIME-OBS')),\n    'reffile_format' : 'TABLE',\n    'reffile_required' : 'NONE',\n    'reffile_switch' : 'NONE',\n    'rmap_relevance' : 'ALWAYS',\n    'sha1sum' : 'd2024dade52a406af70fcdf27a81088004d67cae',\n}\n\nselector = Match({\n    ('FUV',) : UseAfter({\n        '1996-10-01 00:00:00' : 's7g1700dl_bpix.fits',\n        '2009-05-11 00:00:00' : 'z1r1943fl_bpix.fits',\n    }),\n    ('NUV',) : UseAfter({\n        '1996-10-01 00:00:00' : 's7g1700pl_bpix.fits',\n        '2009-05-11 00:00:00' : 'uas19356l_bpix.fits',\n    }),\n})\n"
    assert expected == header


@mark.hst
@mark.core
@mark.rmap
def test_rmap_obs_package(default_shared_state, hst_data):
    p = rmap.get_cached_mapping(f"{hst_data}/hst_acs_darkfile.rmap")
    assert p.obs_package.__name__ == 'crds.hst'


@mark.hst
@mark.core
@mark.rmap
def test_rmap_format_with_comment(default_shared_state, hst_data):
    r = rmap.get_cached_mapping(f"{hst_data}/hst_acs_darkfile_comment.rmap")
    comment = r.comment
    expected = "\nThis is a block comment which can be used to store additional metadata\nabout the state and evolution of this type and files.\n"
    assert comment == expected
    header = str(r)
    expected = 'header = {\n    \'derived_from\' : \'generated from CDBS database 2013-01-11 13:58:14.664182\',\n    \'filekind\' : \'DARKFILE\',\n    \'instrument\' : \'ACS\',\n    \'mapping\' : \'REFERENCE\',\n    \'name\' : \'hst_acs_darkfile_comment.rmap\',\n    \'observatory\' : \'HST\',\n    \'parkey\' : ((\'DETECTOR\', \'CCDAMP\', \'CCDGAIN\'), (\'DATE-OBS\', \'TIME-OBS\')),\n    \'parkey_relevance\' : {\n        \'ccdamp\' : \'(DETECTOR != "SBC")\',\n        \'ccdgain\' : \'(DETECTOR != "SBC")\',\n    },\n    \'rmap_relevance\' : \'ALWAYS\',\n    \'sha1sum\' : \'0b3af86642812a1af65b77d429886e186acef915\',\n}\n\ncomment = """\nThis is a block comment which can be used to store additional metadata\nabout the state and evolution of this type and files.\n"""\n\nselector = Match({\n    (\'HRC\', \'A|ABCD|AD|B|BC|C|D\', \'1.0|2.0|4.0|8.0\') : UseAfter({\n        \'1992-01-01 00:00:00\' : \'lcb12060j_drk.fits\',\n        \'2002-03-01 00:00:00\' : \'n3o1022cj_drk.fits\',\n        \'2002-03-18 00:00:00\' : \'n3o1022ej_drk.fits\',\n        \'2002-03-19 00:34:31\' : \'n3o1022fj_drk.fits\',\n        \'2002-03-20 00:34:32\' : \'n3o1022hj_drk.fits\',\n        \'2002-03-21 00:34:31\' : \'n3o1022ij_drk.fits\',\n        \'2002-03-22 00:34:30\' : \'n3o1022kj_drk.fits\',\n        \'2002-03-23 00:34:28\' : \'n3o1022lj_drk.fits\',\n        \'2007-01-21 02:09:05\' : \'r1u1415ij_drk.fits\',\n        \'2007-01-22 00:40:13\' : \'r1u1415kj_drk.fits\',\n        \'2007-01-26 00:07:33\' : \'r1u1415mj_drk.fits\',\n    }),\n})\n'
    assert header == expected


@mark.multimission
@mark.core
@mark.rmap
def test_rmap_warn_checksum(default_shared_state, caplog):
    string = '''header = {
        'derived_from' : 'generated from CDBS database 2013-01-11 13:58:14.664182',
        'filekind' : 'DARKFILE','instrument' : 'ACS',
        'mapping' : 'REFERENCE',
        'name' : 'hst_acs_darkfile_comment.rmap',
        'observatory' : 'HST',
        'parkey' : (('DETECTOR', 'CCDAMP', 'CCDGAIN'), ('DATE-OBS', 'TIME-OBS')),
        'sha1sum' : "something bad",
    }
selector = Match({
('HRC', 'A|ABCD|AD|B|BC|C|D', '1.0|2.0|4.0|8.0') : UseAfter({
'1992-01-01 00:00:00' : 'lcb12060j_drk.fits',
'2002-03-01 00:00:00' : 'n3o1022cj_drk.fits',
}),})'''
    with caplog.at_level(logging.INFO, logger="CRDS"):
        rmap.ReferenceMapping.from_string(string, ignore_checksum='warn')
        out = caplog.text
    expected = " Checksum error : sha1sum mismatch in '(noname)'"
    assert expected in out


@mark.jwst
@mark.core
@mark.rmap
def test_rmap_get_reference_parkeys(default_shared_state, jwst_data):
    r = rmap.get_cached_mapping(f"{jwst_data}/jwst_miri_specwcs_0004.rmap")
    assert r.parkey == (('META.INSTRUMENT.DETECTOR', 'META.INSTRUMENT.CHANNEL', 'META.INSTRUMENT.BAND', 'META.SUBARRAY.NAME'),)
    assert r.get_reference_parkeys() == ('BAND', 'CHANNEL', 'DETECTOR', 'META.EXPOSURE.TYPE', 'META.INSTRUMENT.BAND', 'META.INSTRUMENT.CHANNEL', 'META.INSTRUMENT.DETECTOR', 'META.INSTRUMENT.LAMP_STATE', 'META.SUBARRAY.NAME', 'META.VISIT.TSOVISIT', 'SUBARRAY')


@mark.hst
@mark.core
@mark.rmap
def test_rmap_get_valid_values_map(default_shared_state):
    i = rmap.get_cached_mapping("hst_acs.imap")
    vvmap = i.get_valid_values_map()
    expected = {'APERTURE': ['NONE',
                  'SBC',
                  'SBC-FIX',
                  'WFC',
                  'WFC-FIX',
                  'WFC1',
                  'WFC1-1K',
                  'WFC1-2K',
                  'WFC1-512',
                  'WFC1-CTE',
                  'WFC1-FIX',
                  'WFC1-IRAMP',
                  'WFC1-IRAMPQ',
                  'WFC1-MRAMP',
                  'WFC1-MRAMPQ',
                  'WFC1-POL0UV',
                  'WFC1-POL0V',
                  'WFC1-POL120UV',
                  'WFC1-POL120V',
                  'WFC1-POL60UV',
                  'WFC1-POL60V',
                  'WFC1-SMFL',
                  'WFC1A-1K',
                  'WFC1A-2K',
                  'WFC1A-512',
                  'WFC1B-1K',
                  'WFC1B-2K',
                  'WFC1B-512',
                  'WFC2',
                  'WFC2-1K',
                  'WFC2-2K',
                  'WFC2-512',
                  'WFC2-FIX',
                  'WFC2-MRAMP',
                  'WFC2-MRAMPQ',
                  'WFC2-ORAMP',
                  'WFC2-ORAMPQ',
                  'WFC2-POL0UV',
                  'WFC2-POL0V',
                  'WFC2-POL120UV',
                  'WFC2-POL120V',
                  'WFC2-POL60UV',
                  'WFC2-POL60V',
                  'WFC2-SMFL',
                  'WFC2C-1K',
                  'WFC2C-2K',
                  'WFC2C-512',
                  'WFC2D-1K',
                  'WFC2D-2K',
                  'WFC2D-512',
                  'WFCENTER'],
     'ATODCORR': [],
     'BIASCORR': [],
     'CCDAMP': ['A', 'ABCD', 'AC', 'AD', 'B', 'BC', 'BD', 'C', 'D'],
     'CCDCHIP': [],
     'CCDGAIN': ['0.5', '1.0', '1.4', '2.0', '4.0', '8.0'],
     'CRCORR': [],
     'DARKCORR': [],
     'DETECTOR': ['HRC', 'SBC', 'WFC'],
     'DQICORR': [],
     'DRIZCORR': [],
     'FILTER1': ['BLOCK1',
                 'BLOCK2',
                 'BLOCK3',
                 'BLOCK4',
                 'CLEAR1L',
                 'CLEAR1S',
                 'F115LP',
                 'F122M',
                 'F125LP',
                 'F140LP',
                 'F150LP',
                 'F165LP',
                 'F475W',
                 'F502N',
                 'F550M',
                 'F555W',
                 'F606W',
                 'F625W',
                 'F658N',
                 'F775W',
                 'F850LP',
                 'F892N',
                 'G800L',
                 'POL0UV',
                 'POL120UV',
                 'POL60UV',
                 'PR110L',
                 'PR130L'],
     'FILTER2': ['CLEAR2L',
                 'CLEAR2S',
                 'F220M',
                 'F220W',
                 'F250W',
                 'F330W',
                 'F344N',
                 'F410W',
                 'F435W',
                 'F660N',
                 'F814W',
                 'FR1016N',
                 'FR388N',
                 'FR423N',
                 'FR459M',
                 'FR462N',
                 'FR505N',
                 'FR551N',
                 'FR555N',
                 'FR601N',
                 'FR647M',
                 'FR656N',
                 'FR716N',
                 'FR782N',
                 'FR853N',
                 'FR914M',
                 'FR931N',
                 'G800L',
                 'POL0V',
                 'POL120V',
                 'POL60V',
                 'PR200L'],
     'FLASHCUR': ['HIGH', 'LOW', 'MED'],
     'FLATCORR': [],
     'FLSHCORR': [],
     'FW1OFFST': ['-1', '0', '1', '2'],
     'FW2OFFST': ['-1', '0', '1', '2'],
     'FWSOFFST': ['-1', '0', '1', '2'],
     'GLINCORR': [],
     'LTV1': [],
     'LTV2': [],
     'NUMCOLS': [],
     'NUMROWS': [],
     'OBSTYPE': ['CORONAGRAPHIC', 'IMAGING', 'INTERNAL', 'SPECTROSCOPIC'],
     'PCTECORR': [],
     'PHOTCORR': [],
     'SHADCORR': [],
     'SHUTRPOS': ['A', 'B'],
     'XCORNER': [],
     'YCORNER': []}
    assert vvmap == expected

    ccdmap = i.get_valid_values_map(remove_special=False)["CCDGAIN"]
    assert ccdmap == ['0.5', '1.0', '1.4', '2.0', '4.0', '8.0']

    fw1map = i.get_valid_values_map(condition=True)["FW1OFFST"]
    assert fw1map == ['-1.0', '0.0', '1.0', '2.0']


@mark.hst
@mark.core
@mark.rmap
def test_rmap_get_valid_values_map_range(default_shared_state, hst_data):
    r = rmap.get_cached_mapping(f"{hst_data}/hst_wfpc2_flatfile.rmap")
    vvmap = r.get_valid_values_map() 
    assert vvmap == {'FILTER1': ('0.0', '1.0', '2.0', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0', '9.0', '10.0', '11.0', '12.0', '13.0', '14.0', '15.0', '16.0', '17.0', '18.0', '19.0', '20.0', '21.0', '22.0', '23.0', '24.0', '25.0', '26.0', '27.0', '28.0', '29.0', '30.0', '31.0', '32.0', '33.0', '34.0', '35.0', '36.0', '37.0', '38.0', '39.0', '40.0', '41.0', '42.0', '43.0', '44.0', '45.0', '46.0', '47.0', '48.0', '49.0', '50.0', '51.0', '52.0', '53.0', '54.0', '55.0', '56.0', '57.0', '58.0', '59.0', '60.0', '61.0', '62.0', '63.0', '64.0', '65.0', '66.0', '67.0', '68.0', '69.0', '70.0', '71.0'), 'FILTER2': ('0.0', '1.0', '2.0', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0', '9.0', '10.0', '11.0', '12.0', '13.0', '14.0', '15.0', '16.0', '17.0', '18.0', '19.0', '20.0', '21.0', '22.0', '23.0', '24.0', '25.0', '26.0', '27.0', '28.0', '29.0', '30.0', '31.0', '32.0', '33.0', '34.0', '35.0', '36.0', '37.0', '38.0', '39.0', '40.0', '41.0', '42.0', '43.0', '44.0', '45.0', '46.0', '47.0', '48.0', '49.0', '50.0', '51.0', '52.0', '53.0', '54.0', '55.0', '56.0', '57.0', '58.0', '59.0', '60.0', '61.0', '62.0', '63.0', '64.0', '65.0', '66.0', '67.0', '68.0', '69.0', '70.0', '71.0'), 'MODE': ('FULL', 'AREA')}


@mark.hst
@mark.core
@mark.rmap
def test_rmap_get_best_references_fail(default_shared_state):   
    i = rmap.get_cached_mapping("hst_acs.imap")
    out = i.get_best_references({
    "DETECTOR" : "HRC",
    "CCDAMP" : "B",
    "CCDGAIN" : "7.0",
    "DARKCORR" : "PERFORM",
    "DATE-OBS" : "2015-04-30",
    "TIME-OBS" : "16:43:00",
    }, include=["darkfile"])
    assert out == {'darkfile': 'NOT FOUND No match found.'}


@mark.hst
@mark.core
@mark.rmap
def test_validate_mapping_valid(default_shared_state, hst_data):
    r = rmap.get_cached_mapping(f"{hst_data}/hst_acs_darkfile.rmap")
    r.validate_mapping()


@mark.hst
@mark.core
@mark.rmap
def test_validate_mapping_ambiguous(default_shared_state, hst_data, caplog):
    default_shared_state.url = "https://hst-crds.stsci.edu"
    default_shared_state.config_setup()
    r = rmap.get_cached_mapping(f"{hst_data}/hst_acs_darkfile_ewsc.rmap")
    with caplog.at_level(logging.INFO, logger="CRDS"):
        r.validate_mapping()
        out = caplog.text
    expected = """ Match('DETECTOR', 'CCDAMP', 'CCDGAIN') : ('HRC', 'C', '1.0|2.0|4.0|8.0') : 
----------------------------------------
Match case
('HRC', 'C', '1.0|2.0|4.0|8.0') : UseAfter({
    '2003-11-06 15:11:06' : nc113178j_drk.fits
is an equal weight special case of
('HRC', 'A|ABCD|AD|B|BC|C|D', '1.0|2.0|4.0|8.0') : UseAfter({
    '1992-01-01 00:00:00' : lcb12060j_drk.fits
Cancel the submission and regenerate the reference files
with different parameter values which coincide with an existing category.
For some parameter sets, CRDS interprets both matches as equally good.
For more explanation, see the file submission section of the CRDS server user's guide here:
https://hst-crds.stsci.edu/static/users_guide/index.html
----------------------------------------
    Match('DETECTOR', 'CCDAMP', 'CCDGAIN') : ('HRC', 'C', '2.0') : 
----------------------------------------
Match case
('HRC', 'C', '2.0') : UseAfter({
    '2002-03-26 00:00:00' : m3t1633tj_drk.fits
is an equal weight special case of
('HRC', 'A|ABCD|AD|B|BC|C|D', '1.0|2.0|4.0|8.0') : UseAfter({
    '1992-01-01 00:00:00' : lcb12060j_drk.fits
Cancel the submission and regenerate the reference files
with different parameter values which coincide with an existing category.
For some parameter sets, CRDS interprets both matches as equally good.
For more explanation, see the file submission section of the CRDS server user's guide here:
https://hst-crds.stsci.edu/static/users_guide/index.html
----------------------------------------
    Match('DETECTOR', 'CCDAMP', 'CCDGAIN') : ('HRC', 'D', '1.0|2.0|4.0|8.0') : 
----------------------------------------
Match case
('HRC', 'D', '1.0|2.0|4.0|8.0') : UseAfter({
    '1991-01-01 00:00:00' : j4d1435nj_drk.fits
is an equal weight special case of
('HRC', 'A|ABCD|AD|B|BC|C|D', '1.0|2.0|4.0|8.0') : UseAfter({
    '1992-01-01 00:00:00' : lcb12060j_drk.fits
Cancel the submission and regenerate the reference files
with different parameter values which coincide with an existing category.
For some parameter sets, CRDS interprets both matches as equally good.
For more explanation, see the file submission section of the CRDS server user's guide here:
https://hst-crds.stsci.edu/static/users_guide/index.html
----------------------------------------
    Match('DETECTOR', 'CCDAMP', 'CCDGAIN') : ('WFC', 'ABCD', '1.0') : 
----------------------------------------
Match case
('WFC', 'ABCD', '1.0') : UseAfter({
    '2003-10-25 01:18:03' : nba1143tj_drk.fits
is an equal weight special case of
('WFC', 'A|ABCD|AC|AD|B|BC|BD|C|D', '1.0') : UseAfter({
    '2003-09-13 00:48:08' : na11410lj_drk.fits
Cancel the submission and regenerate the reference files
with different parameter values which coincide with an existing category.
For some parameter sets, CRDS interprets both matches as equally good.
For more explanation, see the file submission section of the CRDS server user's guide here:
https://hst-crds.stsci.edu/static/users_guide/index.html
----------------------------------------
    Match('DETECTOR', 'CCDAMP', 'CCDGAIN') : ('WFC', 'A|ABCD|AC|AD|B|BC|BD|C|D', '1.0') : 
----------------------------------------
Match case
('WFC', 'A|ABCD|AC|AD|B|BC|BD|C|D', '1.0') : UseAfter({
    '2003-09-13 00:48:08' : na11410lj_drk.fits
is an equal weight special case of
('WFC', 'A|ABCD|AC|AD|B|BC|BD|C|D', '1.0|2.0|4.0|8.0') : UseAfter({
    '1991-01-01 00:00:00' : lcb1202gj_drk.fits
Cancel the submission and regenerate the reference files
with different parameter values which coincide with an existing category.
For some parameter sets, CRDS interprets both matches as equally good.
For more explanation, see the file submission section of the CRDS server user's guide here:
https://hst-crds.stsci.edu/static/users_guide/index.html
----------------------------------------
    Match('DETECTOR', 'CCDAMP', 'CCDGAIN') : ('WFC', 'A|ABCD|AD|B|BC|C|D', '1.0|2.0|4.0|8.0') : 
----------------------------------------
Match case
('WFC', 'A|ABCD|AD|B|BC|C|D', '1.0|2.0|4.0|8.0') : UseAfter({
    '2006-07-30 02:04:10' : q9520146j_drk.fits
is an equal weight special case of
('WFC', 'A|ABCD|AC|AD|B|BC|BD|C|D', '1.0|2.0|4.0|8.0') : UseAfter({
    '1991-01-01 00:00:00' : lcb1202gj_drk.fits
Cancel the submission and regenerate the reference files
with different parameter values which coincide with an existing category.
For some parameter sets, CRDS interprets both matches as equally good.
For more explanation, see the file submission section of the CRDS server user's guide here:
https://hst-crds.stsci.edu/static/users_guide/index.html
----------------------------------------
"""
    for line in expected.splitlines():
        assert line.strip() in out


@mark.roman
@mark.core
@mark.rmap
def test_validate_mapping_ambiguous_roman(roman_serverless_state, roman_data, caplog):
    r = rmap.get_cached_mapping(f"{roman_data}/roman_wfi_flat_ewsc.rmap")
    with caplog.at_level(logging.INFO, logger="CRDS"):
        r.validate_mapping()
        out = caplog.text
    expected = """ Match('ROMAN.META.INSTRUMENT.DETECTOR [DETECTOR]', 'ROMAN.META.INSTRUMENT.OPTICAL_ELEMENT [FITS unknown]') : ('WFI01', 'F158') : 
----------------------------------------
Match case
('WFI01', 'F158') : UseAfter({
    '2020-01-01 00:00:00' : roman_wfi_flat_0002.asdf
is an equal weight special case of
('WFI01', 'F158|F184|F213') : UseAfter({
    '2021-08-01 11:11:11' : roman_wfi_flat_0004.asdf
Cancel the submission and regenerate the reference files
with different parameter values which coincide with an existing category.
For some parameter sets, CRDS interprets both matches as equally good.
For more explanation, see the file submission section of the CRDS server user's guide here:
https://roman-crds.stsci.edu/static/users_guide/index.html
----------------------------------------
"""
    for line in expected.splitlines():
        assert line.strip() in out


@mark.hst
@mark.core
@mark.rmap
def test_validate_mapping_invalid1(default_shared_state, hst_data, caplog):
    r = rmap.get_cached_mapping(f"{hst_data}/hst_acs_darkfile_invalid1.rmap")
    with caplog.at_level(logging.INFO, logger="CRDS"):
        r.validate_mapping()
        out = caplog.text
    expected = """  Match('DETECTOR', 'CCDAMP', 'CCDGAIN') : ('HRC', 'A|ABCD|AD|B|BC|C|DDDD', '1.0|2.0|4.0|8.0') :  parameter='CCDAMP' value='DDDD' is not in ('A', 'B', 'C', 'D', 'AC', 'AD', 'BC', 'BD', 'ABCD', 'N/A')"""
    for line in expected.splitlines():
        assert line.strip() in out


@mark.hst
@mark.core
@mark.rmap
def test_validate_mapping_invalid2(default_shared_state, hst_data, caplog):
    r = rmap.get_cached_mapping(f"{hst_data}/hst_acs_darkfile_invalid2.rmap")
    with caplog.at_level(logging.INFO, logger="CRDS"):
        r.validate_mapping()
        out = caplog.text
    expected = """ Match('DETECTOR', 'CCDAMP', 'CCDGAIN') : ('FOOBAR', 'A|ABCD|AD|B|BC|C|DDDD', '1.0|2.0|4.0|8.0') :  parameter='DETECTOR' value='FOOBAR' is not in ('WFC', 'HRC', 'SBC')"""
    for line in expected.splitlines():
        assert line.strip() in out


@mark.hst
@mark.core
@mark.rmap
def test_rmap_asmapping_readonly(default_shared_state, hst_data):
    r = rmap.asmapping(f"{hst_data}/hst_acs_darkfile.rmap", cached="readonly")


@mark.hst
@mark.core
@mark.rmap
def test_rmap_get_equivalent_mapping_missing(default_shared_state, caplog):
    p = rmap.get_cached_mapping("hst.pmap")
    with caplog.at_level(logging.INFO, logger="CRDS"):
        p.get_equivalent_mapping("hst_cos_twozxtab_0001.rmap")
        out = caplog.text
    expected = """ No equivalent filekind in 'hst_cos.imap' corresponding to 'hst_cos_twozxtab_0001.rmap'"""
    for line in expected.splitlines():
        assert line.strip() in out


@mark.hst
@mark.core
@mark.rmap
def test_imap_match_not_applicable(default_shared_state, hst_data):
    p = rmap.get_cached_mapping(f"{hst_data}/hst_acs_9999.imap")
    na = p.get_best_references({
        "DETECTOR" : "SBC",
        "CCDAMP" : "A",
        "CCDGAIN" : "1.0",
        "DATE-OBS" : "1993-01-01",
        "TIME-OBS" : "12:00:00",
        "OBSTYPE" : "IMAGING",
        "FLATCORR" : "PERFORM",
        "DQICORR" : "PERFORM",
        "DRIZCORR" : "PERFORM",
        "PHOTCORR" : "PERFORM",
        "DRIZCORR" : "PERFORM",
    })["pctetab"]
    assert na == 'NOT FOUND n/a'


@mark.hst
@mark.core
@mark.rmap
def test_imap_match_omit(default_shared_state, hst_data):
    p = rmap.get_cached_mapping(f"{hst_data}/hst_acs_9999.imap")
    assert "mlintab" not in p.get_best_references({
        "DETECTOR" : "SBC",
        "CCDAMP" : "A",
        "CCDGAIN" : "1.0",
        "DATE-OBS" : "2002-03-19",
        "TIME-OBS" : "00:34:32",
        "OBSTYPE" : "IMAGING",
        "FLATCORR" : "PERFORM",
        "DQICORR" : "PERFORM",
        "DRIZCORR" : "PERFORM",
        "PHOTCORR" : "PERFORM",
        "DRIZCORR" : "PERFORM",
    })


@mark.hst
@mark.core
@mark.rmap
def test_pickling(default_shared_state, hst_data):
    from crds import data_file
    p = rmap.get_cached_mapping("hst.pmap")
    s = pickle.dumps(p)
    q = pickle.loads(s)
    assert str(q) == str(p)
    assert p.difference(q) == []
    assert q.difference(p) == []
    p.validate_mapping()
    q.validate_mapping()
    header = data_file.get_header(f"{hst_data}/j8bt06o6q_raw.fits")
    refs_p = p.get_best_references(header)
    refs_q = q.get_best_references(header)
    assert refs_p == refs_q


# ==================================================================================


@mark.hst
@mark.core
@mark.rmap
def test_rmap_get_imap_except(default_shared_state):
    r = rmap.get_cached_mapping("hst.pmap")
    try:
        r.get_imap("foo")
    except CrdsUnknownInstrumentError:
        assert True


@mark.hst
@mark.core
@mark.rmap
def test_rmap_get_filekind(default_shared_state, hst_data):
    r = rmap.get_cached_mapping("hst.pmap")
    filekinds = set(r.get_filekinds(f"{hst_data}/j8bt05njq_raw.fits"))
    assert filekinds == {'atodtab','biasfile','bpixtab','ccdtab','cfltfile','crrejtab',
                        'd2imfile','darkfile','dgeofile','drkcfile','flshfile','idctab',
                        'imphttab','mdriztab','mlintab','npolfile','oscntab','pctetab',
                        'pfltfile','shadfile','spottab'}


@mark.hst
@mark.core
@mark.rmap
def test_rmap_get_equivalent_mapping(default_shared_state, hst_data):
    i = rmap.get_cached_mapping(f"{hst_data}/hst_acs_0002.imap")
    assert i.get_equivalent_mapping("hst.pmap") is None
    assert i.get_equivalent_mapping(f"{hst_data}/hst_acs_0001.imap").name == "hst_acs.imap"
    assert i.get_equivalent_mapping(f"{hst_data}/hst_acs_biasfile_0002.rmap").name ==  "hst_acs_biasfile.rmap"


@mark.multimission
@mark.core
@mark.rmap
def test_rmap_list_mappings(default_shared_state, hst_data, jwst_data, roman_data):
    os.environ["CRDS_MAPPATH_SINGLE"] = hst_data
    maps = sorted(rmap.list_mappings("*.imap", "hst"))
    expected = [
        'hst_acs.imap',
        'hst_acs_0001.imap',
        'hst_acs_0002.imap',
        'hst_acs_0491.imap',
        'hst_acs_9999.imap',
        'hst_cos.imap',
        'hst_nicmos.imap',
        'hst_stis.imap',
        'hst_wfc3.imap',
        'hst_wfpc2.imap'
    ]
    assert maps == expected
    os.environ["CRDS_MAPPATH_SINGLE"] = jwst_data
    maps = sorted(rmap.list_mappings("*.imap", "jwst"))
    expected = ['jwst_fgs_na.imap', 'jwst_miri_omit.imap', 'jwst_niriss_na_omit.imap']
    assert maps == expected
    os.environ["CRDS_MAPPATH_SINGLE"] = roman_data
    maps = sorted(rmap.list_mappings("*.imap", "roman"))
    expected = ['roman_wfi_0001.imap']
    assert maps == expected


@mark.hst
@mark.core
@mark.rmap
def test_rmap_list_references(default_shared_state, hst_data):
    os.environ["CRDS_REFPATH_SINGLE"] = hst_data
    crds_config.CRDS_REF_SUBDIR_MODE = "flat"
    refs = sorted(rmap.list_references("*.r1h", "hst"))
    assert refs == ['dbu1405fu.r1h', 'dbu1405iu.r1h', 'e1b09593u.r1h', 'e1b09594u.r1h', 'valid.r1h']


@mark.hst
@mark.core
@mark.rmap
def test_rmap_get_derived_from(default_shared_state, hst_data):
    os.environ["CRDS_MAPPATH_SINGLE"] = hst_data
    r = rmap.get_cached_mapping(f"{hst_data}/hst_acs_flshfile_0252.rmap")
    assert r.get_derived_from().name == 'hst_acs_flshfile_0251.rmap'


@mark.hst
@mark.core
@mark.rmap
def test_missing_required_header_key(default_shared_state, hst_data):
    try:
        r = rmap.load_mapping(f"{hst_data}/hst_acs_darkfile_missing_key.rmap")
    except MissingHeaderKeyError:
        assert True


@mark.hst
@mark.core
@mark.rmap
def test_load_rmap_bad_expr(default_shared_state, hst_data):
    try:
        r = rmap.get_cached_mapping(f"{hst_data}/hst_acs_darkfile_badexpr.rmap")
    except SyntaxError:
        assert True


@mark.hst
@mark.core
@mark.rmap
def test_rmap_get_parkey_map(default_shared_state):
    i = rmap.get_cached_mapping("hst_acs.imap")
    try:
        i.get_rmap("foo")
    except CrdsUnknownReftypeError:
        assert True
    

@mark.multimission
@mark.core
@mark.rmap
def test_rmap_missing_checksum(default_shared_state):
    string = '''header = {
'derived_from' : 'generated from CDBS database 2013-01-11 13:58:14.664182',
'filekind' : 'DARKFILE',
'instrument' : 'ACS',
'mapping' : 'REFERENCE',
'name' : 'hst_acs_darkfile_comment.rmap',
'observatory' : 'HST',
'parkey' : (('DETECTOR', 'CCDAMP', 'CCDGAIN'), ('DATE-OBS', 'TIME-OBS')),
}

selector = Match({
('HRC', 'A|ABCD|AD|B|BC|C|D', '1.0|2.0|4.0|8.0') : UseAfter({
    '1992-01-01 00:00:00' : 'lcb12060j_drk.fits',
    '2002-03-01 00:00:00' : 'n3o1022cj_drk.fits',
}),
})
'''
    try:
        rmap.ReferenceMapping.from_string(string)
    except ChecksumError:
        assert True


@mark.multimission
@mark.core
@mark.rmap
def test_rmap_schema_uri(default_shared_state):
    string = '''header = {
'derived_from' : 'jwst_nircam_pars-tweakregstep_0001.rmap',
'file_ext' : '.asdf',
'filekind' : 'pars-tweakregstep',
'filetype' : 'pars-tweakregstep',
'instrument' : 'NIRCAM',
'mapping' : 'REFERENCE',
'name' : 'jwst_nircam_pars-tweakregstep_0002.rmap',
'observatory' : 'JWST',
'parkey' : (('META.EXPOSURE.TYPE', 'META.INSTRUMENT.FILTER', 'META.INSTRUMENT.PUPIL'), ('META.OBSERVATION.DATE', 'META.OBSERVATION.TIME')),
'schema_uri' : 'http://stsci.edu/schemas/asdf/core/ndarray-1.0.0',
'sha1sum' : '186bb16c5b4ec498d9cc7d03ff564ae22f221d6f',
'suffix' : 'pars-tweakregstep',
'text_descr' : 'TweakRegStep runtime parameters',
}

selector = Match({
})
'''
    r = rmap.ReferenceMapping.from_string(string, ignore_checksum=True)
    assert r.schema_uri == 'http://stsci.edu/schemas/asdf/core/ndarray-1.0.0'
    r.validate()


@mark.multimission
@mark.core
@mark.rmap
def test_rmap_schema_uri_missing(default_shared_state):
    string = '''header = {
'derived_from' : 'jwst_nircam_pars-tweakregstep_0001.rmap',
'file_ext' : '.asdf',
'filekind' : 'pars-tweakregstep',
'filetype' : 'pars-tweakregstep',
'instrument' : 'NIRCAM',
'mapping' : 'REFERENCE',
'name' : 'jwst_nircam_pars-tweakregstep_0002.rmap',
'observatory' : 'JWST',
'parkey' : (('META.EXPOSURE.TYPE', 'META.INSTRUMENT.FILTER', 'META.INSTRUMENT.PUPIL'), ('META.OBSERVATION.DATE', 'META.OBSERVATION.TIME')),
'schema_uri' : 'http://stsci.edu/schemas/asdf/core/does_not_exist-1.0.0',
'sha1sum' : '186bb16c5b4ec498d9cc7d03ff564ae22f221d6f',
'suffix' : 'pars-tweakregstep',
'text_descr' : 'TweakRegStep runtime parameters',
}

selector = Match({
})
'''
    r = rmap.ReferenceMapping.from_string(string, ignore_checksum=True)
    try:
        r.validate()
    except FileNotFoundError:
        assert True


@mark.hst
@mark.core
@mark.rmap
def test_rmap_get_best_references_include(default_shared_state, hst_data):
    r = rmap.get_cached_mapping(f"{hst_data}/hst_acs_darkfile_comment.rmap")
    header = {
        'CCDAMP': 'ABCD',
        'CCDGAIN': '1.0',
        'DARKCORR': 'UNDEFINED',
        'DATE-OBS': '2002-07-18',
        'DETECTOR': 'WFC',
        'TIME-OBS': '18:09:15.773332'
    }
    try:
        r.get_best_references(header, include=["flatfile"])
    except CrdsUnknownReftypeError:
        assert True


@mark.hst
@mark.core
@mark.rmap
def test_rmap_get_parkey_map(default_shared_state):
    i = rmap.get_cached_mapping("hst_acs.imap")
    parkey_map = i.get_parkey_map() 
    exp = {
        'DETECTOR': ['HRC', 'SBC', 'WFC'],
        'ATODCORR': ['UNDEFINED', 'PERFORM', 'COMPLETE', 'NONE', 'OMIT'],
        'CCDAMP': ['A', 'ABCD', 'AC', 'AD', 'B', 'BC', 'BD', 'C', 'D', 'N/A'],
        'CCDGAIN': ['0.5', '1.0', '1.4', '2.0', '4.0', '8.0', 'N/A'],
        'APERTURE': [
            '*',
            'WFC',
            'WFC-FIX',
            'WFC1',
            'WFC1-1K',
            'WFC1-2K',
            'WFC1-512',
            'WFC1-CTE',
            'WFC1-FIX',
            'WFC1-IRAMP',
            'WFC1-IRAMPQ',
            'WFC1-MRAMP',
            'WFC1-MRAMPQ',
            'WFC1-POL0UV',
            'WFC1-POL0V',
            'WFC1-POL120UV',
            'WFC1-POL120V',
            'WFC1-POL60UV',
            'WFC1-POL60V',
            'WFC1-SMFL',
            'WFC2',
            'WFC2-2K',
            'WFC2-FIX',
            'WFC2-MRAMP',
            'WFC2-ORAMP',
            'WFC2-ORAMPQ',
            'WFC2-POL0UV',
            'WFC2-POL0V',
            'WFC2-POL120UV',
            'WFC2-POL120V',
            'WFC2-POL60UV',
            'WFC2-POL60V',
            'WFC2-SMFL',
            'WFCENTER'
        ],
        'NUMCOLS': [
            '1046.0',
            '1062.0',
            '2070.0',
            '2300.0',
            '4144.0',
            '512.0',
            '534.0',
            'N/A'
        ],
        'NUMROWS': ['1024.0', '1044.0', '2046.0', '2068.0', '400.0', '512.0', 'N/A'],
        'LTV1': [
            '-1816.0',
            '-2048.0',
            '-3072.0',
            '-3584.0',
            '-3604.0',
            '19.0',
            '22.0',
            '24.0',
            'N/A'
        ],
        'LTV2': [
            '-1.0',
            '-1023.0',
            '-1535.0',
            '-1591.0',
            '-57.0',
            '-824.0',
            '0.0',
            '20.0',
            'N/A'
        ],
        'XCORNER': ['N/A'],
        'YCORNER': ['N/A'],
        'CCDCHIP': ['N/A'],
        'BIASCORR': ['UNDEFINED', 'PERFORM', 'COMPLETE', 'NONE', 'OMIT'],
        'DQICORR': ['UNDEFINED', 'PERFORM', 'COMPLETE', 'NONE', 'OMIT'],
        'FILTER1': [
            '*',
            'BLOCK1',
            'BLOCK2',
            'BLOCK3',
            'BLOCK4',
            'CLEAR1L',
            'CLEAR1S',
            'F115LP',
            'F122M',
            'F125LP',
            'F140LP',
            'F150LP',
            'F165LP',
            'F475W',
            'F502N',
            'F550M',
            'F555W',
            'F606W',
            'F625W',
            'F658N',
            'F775W',
            'F850LP',
            'F892N',
            'G800L',
            'N/A',
            'POL0UV',
            'POL120UV',
            'POL60UV',
            'PR110L',
            'PR130L'
        ],
        'FILTER2': [
            'CLEAR2L',
            'CLEAR2S',
            'F220M',
            'F220W',
            'F250W',
            'F330W',
            'F344N',
            'F410W',
            'F435W',
            'F660N',
            'F814W',
            'FR1016N',
            'FR388N',
            'FR423N',
            'FR459M',
            'FR462N',
            'FR505N',
            'FR551N',
            'FR555N',
            'FR601N',
            'FR647M',
            'FR656N',
            'FR716N',
            'FR782N',
            'FR853N',
            'FR914M',
            'FR931N',
            'N/A',
            'POL0V',
            'POL120V',
            'POL60V',
            'PR200L'
        ],
        'OBSTYPE': ['CORONAGRAPHIC', 'IMAGING', 'SPECTROSCOPIC'],
        'CRCORR': ['UNDEFINED', 'PERFORM', 'COMPLETE', 'NONE', 'OMIT'],
        'DRIZCORR': ['UNDEFINED', 'PERFORM', 'COMPLETE', 'NONE', 'OMIT'],
        'DARKCORR': ['UNDEFINED', 'PERFORM', 'COMPLETE', 'NONE', 'OMIT'],
        'PCTECORR': ['UNDEFINED', 'PERFORM', 'COMPLETE', 'NONE', 'OMIT'],
        'FLASHCUR': ['HIGH', 'LOW', 'MED'],
        'SHUTRPOS': ['A', 'B'],
        'FLSHCORR': ['UNDEFINED', 'PERFORM', 'COMPLETE', 'NONE', 'OMIT'],
        'PHOTCORR': ['UNDEFINED', 'PERFORM', 'COMPLETE', 'NONE', 'OMIT'],
        'GLINCORR': ['UNDEFINED', 'PERFORM', 'COMPLETE', 'NONE', 'OMIT'],
        'FW1OFFST': ['-1.0', '1.0', 'N/A'],
        'FW2OFFST': ['-1.0', '1.0', 'N/A'],
        'FWSOFFST': ['N/A'],
        'FLATCORR': ['UNDEFINED', 'PERFORM', 'COMPLETE', 'NONE', 'OMIT'],
        'SHADCORR': ['UNDEFINED', 'PERFORM', 'COMPLETE', 'NONE', 'OMIT']
    }
    for k, v in exp.items():
        assert sorted(parkey_map[k]) == sorted(v)


@mark.hst
@mark.core
@mark.rmap
def test_rmap_todict(default_shared_state, hst_data):
    r = rmap.get_cached_mapping(f"{hst_data}/hst_cos_bpixtab_0252.rmap")
    assert r.todict() == {'text_descr': 'Data Quality (Bad Pixel) Initialization Table', 'selections': [('FUV', '1996-10-01 00:00:00', 's7g1700dl_bpix.fits'), ('FUV', '2009-05-11 00:00:00', 'z1r1943fl_bpix.fits'), ('NUV', '1996-10-01 00:00:00', 's7g1700pl_bpix.fits'), ('NUV', '2009-05-11 00:00:00', 'uas19356l_bpix.fits')], 'header': {'sha1sum': 'd2024dade52a406af70fcdf27a81088004d67cae', 'reffile_switch': 'none', 'filekind': 'bpixtab', 'instrument': 'cos', 'derived_from': 'hst_cos_bpixtab_0251.rmap', 'reffile_format': 'table', 'observatory': 'hst', 'parkey': (('DETECTOR',), ('DATE-OBS', 'TIME-OBS')), 'reffile_required': 'none', 'rmap_relevance': 'always', 'mapping': 'reference', 'name': 'hst_cos_bpixtab_0252.rmap'}, 'parameters': ('DETECTOR', 'USEAFTER', 'REFERENCE')}


@mark.hst
@mark.core
@mark.rmap
def test_rmap_tojson(default_shared_state, hst_data):
    r = rmap.get_cached_mapping(f"{hst_data}/hst_cos_bpixtab_0252.rmap")
    assert json.loads(r.tojson()) == {u'header': {u'observatory': u'hst', u'name': u'hst_cos_bpixtab_0252.rmap', u'reffile_required': u'none', u'parkey': [[u'DETECTOR'], [u'DATE-OBS', u'TIME-OBS']], u'mapping': u'reference', u'filekind': u'bpixtab', u'instrument': u'cos', u'derived_from': u'hst_cos_bpixtab_0251.rmap', u'reffile_switch': u'none', u'reffile_format': u'table', u'rmap_relevance': u'always', u'sha1sum': u'd2024dade52a406af70fcdf27a81088004d67cae'}, u'text_descr': u'Data Quality (Bad Pixel) Initialization Table', u'parameters': [u'DETECTOR', u'USEAFTER', u'REFERENCE'], u'selections': [[u'FUV', u'1996-10-01 00:00:00', u's7g1700dl_bpix.fits'], [u'FUV', u'2009-05-11 00:00:00', u'z1r1943fl_bpix.fits'], [u'NUV', u'1996-10-01 00:00:00', u's7g1700pl_bpix.fits'], [u'NUV', u'2009-05-11 00:00:00', u'uas19356l_bpix.fits']]}


@mark.hst
@mark.core
@mark.rmap
def test_rmap_match_not_applicable(default_shared_state, hst_data):
    r = rmap.get_cached_mapping(f"{hst_data}/hst_acs_darkfile_na_omit.rmap")
    r.get_best_ref({
            "DETECTOR" : "SBC",
            "CCDAMP" : "A",
            "CCDGAIN" : "1.0",
            "DATE-OBS" : "1993-01-01",
            "TIME-OBS" : "12:00:00",
            }) == "NOT FOUNT n/a"


@mark.hst
@mark.core
@mark.rmap
def test_rmap_match_omit(default_shared_state, hst_data):
    r = rmap.get_cached_mapping(f"{hst_data}/hst_acs_darkfile_na_omit.rmap")
    r.get_best_ref({
            "DETECTOR" : "SBC",
            "CCDAMP" : "A",
            "CCDGAIN" : "1.0",
            "DATE-OBS" : "2002-03-19",
            "TIME-OBS" : "00:34:32",
            }) is None


@mark.hst
@mark.core
@mark.rmap
def test_rmap_todict(default_shared_state):
    p = rmap.get_cached_mapping("hst.pmap")
    p.todict()


@mark.jwst
@mark.core
@mark.rmap
def test_rmap_match_tjson(jwst_test_cache_state):
    cache_path = jwst_test_cache_state.cache
    os.environ["CRDS_PATH"] = cache_path
    p = rmap.get_cached_mapping("jwst.pmap")
    p.tojson()


def _get_rmap():
    log.set_verbose(55)
    return rmap.ReferenceMapping.from_string("""
header = {
'derived_from' : 'hst_wfc3_darkfile_0379.rmap',
'filekind' : 'DARKFILE',
'instrument' : 'WFC3',
'mapping' : 'REFERENCE',
'name' : 'hst_wfc3_darkfile_0379.rmap',
'observatory' : 'HST',
'comment_parkeys' : ('BINAXIS1',),
'parkey' : (('DETECTOR', 'CCDAMP', 'BINAXIS1', 'BINAXIS2', 'CCDGAIN', 'SAMP_SEQ', 'SUBTYPE'), ('DATE-OBS', 'TIME-OBS')),
'parkey_relevance' : {
    'binaxis1' : '(DETECTOR == "UVIS")',
    'binaxis2' : '(DETECTOR == "UVIS")',
    'ccdgain' : '(DETECTOR == "IR")',
    'samp_seq' : '(DETECTOR == "IR")',
    'subtype' : '(DETECTOR == "IR")',
},
'reffile_format' : 'IMAGE',
'reffile_required' : 'NONE',
'reffile_switch' : 'DARKCORR',
'rmap_relevance' : '(DARKCORR != "OMIT")',
'sha1sum' : '16cfa985b83a7fb9db414dc8f339a95b9c03c5fa',
}

selector = Match({
('IR', 'ABCD', 'N/A', 'N/A', 1.0, 'MIF1200', 'FULLIMAG') : UseAfter({
    '2008-02-19 00:00:00' : 't3n16499i_drk.fits',
    '2008-02-20 00:00:00' : 't3n1649ai_drk.fits',
}),
('UVIS', 'ABCD', 1, 1, 'N/A', 'N/A', 'N/A') : UseAfter({
    '2007-12-17 00:00:00' : 's9q1628ci_drk.fits',
    '2007-12-18 00:00:00' : 's9q1628ei_drk.fits',
    '2008-02-19 00:00:00' : 't3420175i_drk.fits',
    '2008-02-20 00:00:00' : 't3420177i_drk.fits',
}),
})
""", ignore_checksum=True)


@mark.hst
@mark.core
@mark.rmap
def test_ref_to_dataset_ir(default_shared_state):
    # rmap update time conversions don't map comment parkeys to N/A
    r = _get_rmap()
    header = dict(
        DETECTOR="IR", CCDAMP="ABCD", BINAXIS1="1.0", BINAXIS2="2.0",
        CCDGAIN="1.0", SAMP_SEQ="MIF1200", SUBTYPE="FULLIMAG", DARKCORR="PERFORM")
    # transform for rmap updates
    dheader = utils.Struct(r.reference_to_dataset_header(header))
    assert dheader.DETECTOR == "IR"
    assert dheader.CCDAMP == "ABCD"
    assert dheader.BINAXIS1 == "1.0"   # comment
    assert dheader.BINAXIS2 == "N/A"   # non-comment
    assert dheader.CCDGAIN == "1.0"
    assert dheader.SAMP_SEQ == "MIF1200"
    assert dheader.SUBTYPE == "FULLIMAG"
    assert dheader.DARKCORR == "N/A"


@mark.hst
@mark.core
@mark.rmap
def test_ref_to_dataset_uvis(default_shared_state):
    r = _get_rmap()
    header = dict(
        DETECTOR="UVIS", CCDAMP="ABCD", BINAXIS1="1.0", BINAXIS2="2.0",
        CCDGAIN="1.0", SAMP_SEQ="MIF1200", SUBTYPE="FULLIMAG", DARKCORR="PERFORM")
    # transform for rmap updates
    dheader = utils.Struct(r.reference_to_dataset_header(header))
    assert dheader.DETECTOR == "UVIS"
    assert dheader.CCDAMP == "ABCD"
    assert dheader.BINAXIS1 == "1.0" # comment
    assert dheader.BINAXIS2 == "2.0"  # non-comment
    assert dheader.CCDGAIN == "N/A"
    assert dheader.SAMP_SEQ == "N/A"
    assert dheader.SUBTYPE == "N/A"
    assert dheader.DARKCORR == "N/A"


@mark.hst
@mark.core
@mark.rmap
def test_na_parkeys_ir(default_shared_state):
    r = _get_rmap()
    # bestrefs time conversions still map comment parkeys to N/A
    header = dict(
        DETECTOR="IR", CCDAMP="ABCD", BINAXIS1="1.0", BINAXIS2="2.0",
        CCDGAIN="1.0", SAMP_SEQ="MIF1200", SUBTYPE="FULLIMAG", DARKCORR="PERFORM")
    # transform for bestrefs
    dheader = utils.Struct(r.map_irrelevant_parkeys_to_na(header))
    assert dheader.DETECTOR == "IR"
    assert dheader.CCDAMP == "ABCD"
    assert dheader.BINAXIS1 == "N/A" # comment
    assert dheader.BINAXIS2 == "N/A" # non-comment
    assert dheader.CCDGAIN == "1.0"
    assert dheader.SAMP_SEQ == "MIF1200"
    assert dheader.SUBTYPE == "FULLIMAG"
    assert dheader.DARKCORR == "PERFORM"


@mark.hst
@mark.core
@mark.rmap
def test_na_parkeys_uvis(default_shared_state):
    r = _get_rmap()
    header = dict(
        DETECTOR="UVIS", CCDAMP="ABCD", BINAXIS1="1.0", BINAXIS2="2.0",
        CCDGAIN="1.0", SAMP_SEQ="MIF1200", SUBTYPE="FULLIMAG", DARKCORR="PERFORM")
    # transform for bestrefs
    dheader = utils.Struct(r.map_irrelevant_parkeys_to_na(header))
    assert dheader.DETECTOR == "UVIS"
    assert dheader.CCDAMP == "ABCD"
    assert dheader.BINAXIS1 == "N/A" # comment
    assert dheader.BINAXIS2 == "2.0" # non-comment
    assert dheader.CCDGAIN == "N/A"
    assert dheader.SAMP_SEQ == "N/A"
    assert dheader.SUBTYPE == "N/A"
    assert dheader.DARKCORR == "PERFORM"



# ===== Higher level mapping based tests for selectors not covered by HST  =====

@mark.multimission
@mark.core
@mark.rmap
@mark.selectors
class TestSelectors:

    @fixture(autouse=True)
    def _set_config(self, tobs_test_cache_state):
        self._config = tobs_test_cache_state
    
    @property
    def _rmap(self):
        return rmap.get_cached_mapping("tobs_tinstr_tfilekind.rmap")

    def assertEqual(self, expected, result):
        assert expected == result

    def _selector_testcase(self, case, parameter, result):
        header = {
            "TEST_CASE": case,
            "PARAMETER": parameter,
        }
        bestref = self._rmap.get_best_ref(header)
        self.assertEqual(bestref, result)

    def test_use_after_bad_datetime(self):
        header = { "TEST_CASE":"USE_AFTER", "PARAMETER": '4.5' }
        bestref = self._rmap.get_best_ref(header)
        assert bestref.startswith("NOT FOUND UseAfter Invalid date/time format")

    def test_use_after_no_time(self):
        self._selector_testcase('USE_AFTER', '2005-12-20', 'o9f15549j_bia.fits')

    def test_use_after_nominal(self):
        self._selector_testcase('USE_AFTER', '2005-12-20 12:00:00', 'o9f15549j_bia.fits')

    def test_use_after_tuple(self):
        self._selector_testcase('USE_AFTER',  '2004-04-25 21:31:01', ('foo_bia.fits', 'bar_bia.fits'))

    def test_use_after_dict(self):
        self._selector_testcase('USE_AFTER',  '2004-04-25 21:31:02', {'foo':'foo_bia1.fits', 'bar':'bar_bia2.fits'})

    def test_use_after_missing_parameter(self):
        header = { "TEST_CASE": "USE_AFTER" }  # no PARAMETER
        bestref = self._rmap.get_best_ref(header)
        assert bestref.startswith("NOT FOUND UseAfter required lookup parameter 'PARAMETER' is undefined.")

    def test_select_version1(self):
        self._selector_testcase('SELECT_VERSION', '4.5', 'cref_flatfield_73.fits')
    def test_select_version2(self):
        self._selector_testcase('SELECT_VERSION', '5', 'cref_flatfield_123.fits')
    def test_select_version3(self):
        self._selector_testcase('SELECT_VERSION', '6', 'cref_flatfield_123.fits')
    def test_select_version4(self):
        self._selector_testcase('SELECT_VERSION', '2.0', 'cref_flatfield_65.fits')

    def test_closest_time1(self):
        self._selector_testcase('CLOSEST_TIME', '2016-05-05', 'cref_flatfield_123.fits')
    def test_closest_time2(self):
        self._selector_testcase('CLOSEST_TIME', '2016-04-24', 'cref_flatfield_123.fits')
    def test_closest_time3(self):
        self._selector_testcase('CLOSEST_TIME', '2018-02-02', 'cref_flatfield_222.fits')
    def test_closest_time4(self):
        self._selector_testcase('CLOSEST_TIME', '2019-03-01', 'cref_flatfield_123.fits')
    def test_closest_time5(self):
        self._selector_testcase('CLOSEST_TIME', '2016-04-15', 'cref_flatfield_123.fits')
    def test_closest_time6(self):
        self._selector_testcase('CLOSEST_TIME', '2016-04-16', 'cref_flatfield_123.fits')

    def test_bracket1(self):
        self._selector_testcase('BRACKET', '1.25',
            ('cref_flatfield_120.fits', 'cref_flatfield_124.fits'))
    def test_bracket2(self):
        self._selector_testcase('BRACKET', '1.2',
            ('cref_flatfield_120.fits', 'cref_flatfield_120.fits'))
    def test_bracket3(self):
        self._selector_testcase('BRACKET', '1.5',
            ('cref_flatfield_124.fits', 'cref_flatfield_124.fits'))
    def test_bracket4(self):
        self._selector_testcase('BRACKET', '5.0',
            ('cref_flatfield_137.fits', 'cref_flatfield_137.fits'))
    def test_bracket5(self):
        self._selector_testcase('BRACKET', '1.0',
            ('cref_flatfield_120.fits', 'cref_flatfield_120.fits'))
    def test_bracket6(self):
        self._selector_testcase('BRACKET', '6.0',
            ('cref_flatfield_137.fits', 'cref_flatfield_137.fits'))

    def test_geometrically_nearest1(self):
        self._selector_testcase("GEOMETRICALLY_NEAREST", '1.0', 'cref_flatfield_120.fits')
    def test_geometrically_nearest2(self):
        self._selector_testcase("GEOMETRICALLY_NEAREST", '1.2', 'cref_flatfield_120.fits')
    def test_geometrically_nearest3(self):
        self._selector_testcase("GEOMETRICALLY_NEAREST", '1.25', 'cref_flatfield_120.fits')
    def test_geometrically_nearest4(self):
        self._selector_testcase("GEOMETRICALLY_NEAREST", '1.4', 'cref_flatfield_124.fits')
    def test_geometrically_nearest5(self):
        self._selector_testcase("GEOMETRICALLY_NEAREST", '3.25', 'cref_flatfield_124.fits')
    def test_geometrically_nearest6(self):
        self._selector_testcase("GEOMETRICALLY_NEAREST", '3.26', 'cref_flatfield_137.fits')
    def test_geometrically_nearest7(self):
        self._selector_testcase("GEOMETRICALLY_NEAREST", '5.0', 'cref_flatfield_137.fits')
    def test_geometrically_nearest8(self):
        self._selector_testcase("GEOMETRICALLY_NEAREST", '5.1', 'cref_flatfield_137.fits')

    def test_reference_names(self):
        assert self._rmap.reference_names() == ['bar_bia.fits', 'bar_bia2.fits', 'cref_flatfield_120.fits',
                                               'cref_flatfield_123.fits', 'cref_flatfield_124.fits',
                                               'cref_flatfield_137.fits', 'cref_flatfield_222.fits',
                                               'cref_flatfield_65.fits', 'cref_flatfield_73.fits',
                                               'foo_bia.fits', 'foo_bia1.fits', 'nal1503ij_bia.fits',
                                               'o3913216j_bia.fits', 'o5d10135j_bia.fits', 'o9f15549j_bia.fits',
                                               'o9s16388j_bia.fits', 'o9t1525sj_bia.fits']

# =============================================================================

@mark.multimission
@mark.core
@mark.rmap
@mark.selectors
class TestInsert:
    """Tests for checking automatic rmap update logic for adding new references."""
    # Note:  load_mapping must deliver a unique copy of the specified rmap
        
    @fixture(autouse=True)
    def _set_config(self, tobs_test_cache_state):
        self._config = tobs_test_cache_state
    
    @property
    def _rmap(self):
        return rmap.get_cached_mapping("tobs_tinstr_tfilekind.rmap")
    
    def original(self):
        return rmap.load_mapping("tobs_tinstr_tfilekind.rmap")

    def class_name(self, selector_name):
        return "".join([x.capitalize() for x in selector_name.split("_")])

    def set_classes(self, classes):
        self._rmap.selector._rmap_header["classes"] = classes

    def terminal_insert(self, selector_name, param, value):
        """Check the bottom level insert functionality."""
        header = {
                  "TEST_CASE" : selector_name,
                  "PARAMETER" : param,
        }
        inner_class = self.class_name(selector_name)
        self.set_classes(("Match", inner_class))
        result = self._rmap.insert(header, value)
        diffs = self._rmap.difference(result)
        log.verbose("diffs:", diffs)
        assert len(diffs) == 1, "Fewer/more differences than expected"
        assert diffs[0][0] == ('tobs_tinstr_tfilekind.rmap', 'tobs_tinstr_tfilekind.rmap'), "unexpected file names in diff"
        assert diffs[0][1] == (selector_name,), "unexpected match case in diff"
        assert diffs[0][2] == (str(param),), "unexpected parameter value in diff"
        assert diffs[0][3] == "added terminal " + repr(value), "diff is not an addition " + repr(diffs[0])

    def terminal_replace(self, selector_name, param, value):
        """Check the bottom level replace functionality."""
        header = {
                  "TEST_CASE" : selector_name,
                  "PARAMETER" : param,
        }
        inner_class = self.class_name(selector_name)
        self.set_classes(("Match", inner_class))
        result = self._rmap.insert(header, value)
        diffs = self._rmap.difference(result)
        log.verbose("diffs:", diffs)
        assert len(diffs) == 1, "Fewer/more differences than expected"
        assert diffs[0][0] == ('tobs_tinstr_tfilekind.rmap', 'tobs_tinstr_tfilekind.rmap'), "unexpected file names in diff"
        assert diffs[0][1] == (selector_name,), "unexpected match case in diff"
        assert diffs[0][2] == (str(param),), "unexpected parameter value in diff"
        assert "replaced" in diffs[0][3], "diff is not a replacement " + repr(diffs[0])
        assert diffs[0][3].endswith(repr(value))

    def test_useafter_insert_before(self):
        self.terminal_insert("USE_AFTER", '2003-09-25 01:28:00', 'foo.fits')

    def test_useafter_replace_before(self):
        self.terminal_replace("USE_AFTER", '2003-09-26 01:28:00', 'foo.fits')

    def test_useafter_insert_mid(self):
        self.terminal_insert("USE_AFTER", '2004-06-18 04:36:01', 'foo.fits')

    def test_useafter_replace_mid(self):
        self.terminal_replace("USE_AFTER", '2004-06-18 04:36:00', 'foo.fits')

    def test_useafter_insert_after(self):
        self.terminal_insert("USE_AFTER", '2004-07-14 16:52:01', 'foo.fits')

    def test_useafter_replace_after(self):
        self.terminal_replace("USE_AFTER", '2004-07-14 16:52:00', 'foo.fits')

    """
           '<3.1':    'cref_flatfield_65.fits',
           '<5':      'cref_flatfield_73.fits',
           'default': 'cref_flatfield_123.fits',
    """
    def test_select_version_insert_before(self):
        self.terminal_insert("SELECT_VERSION", '<3.0', 'foo.fits')

    def test_select_version_insert_mid(self):
        self.terminal_insert("SELECT_VERSION", '<4', 'foo.fits')

    # There's *nothing* after default,  so no insert possible.
    #    def test_select_version_insert_after(self):
    #        self.terminal_insert("SELECT_VERSION", 'default', 'foo.fits')

    def test_select_version_replace_before(self):
        self.terminal_replace("SELECT_VERSION", '<3.1', 'foo.fits')

    def test_select_version_replace_mid(self):
        self.terminal_replace("SELECT_VERSION", '<5', 'foo.fits')

    def test_select_version_replace_after(self):
        self.terminal_replace("SELECT_VERSION", 'default', 'foo.fits')

    """
            '2017-04-24': "cref_flatfield_123.fits",
            '2018-02-01':  "cref_flatfield_222.fits",
            '2019-04-15': "cref_flatfield_123.fits",
    """
    def test_closest_time_insert_before(self):
         self.terminal_insert("CLOSEST_TIME", '2017-04-20 00:00:00', 'foo.fits')
    def test_closest_time_insert_mid(self):
         self.terminal_insert("CLOSEST_TIME", '2018-01-20 00:57', 'foo.fits')
    def test_closest_time_insert_after(self):
         self.terminal_insert("CLOSEST_TIME", '2020-04-20 00:00:00', 'foo.fits')

    def test_closest_time_replace_before(self):
         self.terminal_replace("CLOSEST_TIME", '2017-04-24', 'foo.fits')
    def test_closest_time_replace_mid(self):
         self.terminal_replace("CLOSEST_TIME", '2018-02-01', 'foo.fits')
    def test_closest_time_replace_after(self):
         self.terminal_replace("CLOSEST_TIME", '2019-04-15', 'foo.fits')

    """
            1.2: "cref_flatfield_120.fits",
            1.5: "cref_flatfield_124.fits",
            5.0: "cref_flatfield_137.fits",
    """
    def test_bracket_insert_before(self):
         self.terminal_insert("BRACKET", 1.0, 'foo.fits')
    def test_bracket_insert_mid(self):
         self.terminal_insert("BRACKET", 1.3, 'foo.fits')
    def test_bracket_insert_after(self):
         self.terminal_insert("BRACKET", 5.1, 'foo.fits')

    def test_bracket_replace_before(self):
         self.terminal_replace("BRACKET", 1.2, 'foo.fits')
    def test_bracket_replace_mid(self):
         self.terminal_replace("BRACKET", 1.5, 'foo.fits')
    def test_bracket_replace_after(self):
         self.terminal_replace("BRACKET", 5.0, 'foo.fits')

    """
            1.2 : "cref_flatfield_120.fits",
            1.5 : "cref_flatfield_124.fits",
            5.0 : "cref_flatfield_137.fits",
    """
    def test_geometrically_nearest_insert_before(self):
         self.terminal_insert("GEOMETRICALLY_NEAREST", 1.0, 'foo.fits')
    def test_geometrically_nearest_insert_mid(self):
         self.terminal_insert("GEOMETRICALLY_NEAREST", 1.3, 'foo.fits')
    def test_geometrically_nearest_insert_after(self):
         self.terminal_insert("GEOMETRICALLY_NEAREST", 5.1, 'foo.fits')

    def test_geometrically_nearest_replace_before(self):
         self.terminal_replace("GEOMETRICALLY_NEAREST", 1.2, 'foo.fits')
    def test_geometrically_nearest_replace_mid(self):
         self.terminal_replace("GEOMETRICALLY_NEAREST", 1.5, 'foo.fits')
    def test_geometrically_nearest_replace_after(self):
         self.terminal_replace("GEOMETRICALLY_NEAREST", 5.0, 'foo.fits')

# =============================================================================

# Test Classes below use the following functions with varying parameters

def recursive_modify_rmap(_rmap_str, insert_header, result_filename): # , header, value, classes):
    # Load the test rmap from a string.   The top level selector must exist.
    # This is not a "realistic" test case.   It's a test of the recursive
    # insertion capabilities of all the Selector classes in one go.
    log.verbose("-"*60)
    r = rmap.ReferenceMapping.from_string(_rmap_str, "./test.rmap", ignore_checksum=True)
    log.verbose("insert_header:", log.PP(insert_header))
    result = r.insert(insert_header, "foo.fits")
    result.write(result_filename)
    diffs = r.difference(result)
    log.verbose("diffs:", diffs)
    diffs = [diff for diff in diffs if "Selector" not in diff[-1]]
    assert len(diffs) == 1, "Fewer/more differences than expected: " + repr(diffs)
    log.verbose("recursive insert result rmap:")
    log.verbose(open(result_filename).read())

def recursive_use_rmap(result_filename, lookup_header, expected_lookup_result):
    r = rmap.load_mapping(result_filename)
    result = r.get_best_ref(lookup_header)
    log.verbose("recursive lookup result:", result)
    assert result == expected_lookup_result, "Recursively generated rmap produced wrong result."

def recursive_tear_down(result_filename):
    os.remove(result_filename)


RMAP_STR = '''
header = {
    'derived_from' : 'Hand written 01-15-2013',
    'filekind' : 'TFILEKIND',
    'instrument' : 'TINSTR',
    'mapping' : 'REFERENCE',
    'name' : 'test.rmap',
    'observatory' : 'TOBS',
    'parkey' : (('MATCH_PAR1','MATCH_PAR2'), ('DATE-OBS','TIME-OBS',), ('SW_VERSION',), ('CLOSETIME',), ('BRACKET_PAR',), ('GEOM_PAR',),),
    'sha1sum' : 'd412b94d1af1a0871fe39d7096e65aea1187c3b7',
    'classes' : ('Match','UseAfter','SelectVersion','ClosestTime','Bracket','GeometricallyNearest')
}

selector = Match({
})
'''

RMAP_STR_SELECT = '''
header = {
    'derived_from' : 'Hand written 01-15-2013',
    'filekind' : 'TFILEKIND',
    'instrument' : 'TINSTR',
    'mapping' : 'REFERENCE',
    'name' : 'test.rmap',
    'observatory' : 'TOBS',
    'parkey' : (('SW_VERSION',), ('MATCH_PAR1','MATCH_PAR2'),),
    'sha1sum' : 'd412b94d1af1a0871fe39d7096e65aea1187c3b7',
    'classes' : ('SelectVersion','Match',)
}

selector = SelectVersion({
    '<3.1': Match({
    }),
    '<5' : Match({
    }),
    'default' : Match({
    }),
})
'''

RMAP_GEO = '''
header = {
    'derived_from' : 'Hand written 01-15-2013',
    'filekind' : 'TFILEKIND',
    'instrument' : 'TINSTR',
    'mapping' : 'REFERENCE',
    'name' : 'test.rmap',
    'observatory' : 'TOBS',
    'parkey' : (('GEOM_PAR',), ('MATCH_PAR1','MATCH_PAR2'),),
    'sha1sum' : 'd412b94d1af1a0871fe39d7096e65aea1187c3b7',
    'classes' : ('GeometricallyNearest','Match',)
}

selector = GeometricallyNearest({
    0.1: Match({
        ('MPX', '98.7') : 'bar.fits',
    }),
    2.8 : Match({
    }),
    99.0 : Match({
    }),
})
'''

@mark.multimission
@mark.core
@mark.rmap
@mark.selectors
class TestDeepRecursiveModify:
    """Tests for checking automatic rmap update logic for adding new references."""

    insert_header = lookup_header = {
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "DATE-OBS" : "2017-04-20",
          "TIME-OBS" : "00:00:00",
          "SW_VERSION" : "1.2",
          "CLOSETIME" : "2017-05-30 00:01:02",
          "BRACKET_PAR" : "4.4",   # try a number
          "PARAMETER" : "2012-09-09 03:07",
          "GEOM_PAR" : "2.7",  # try a string-formatted number
    }
    result_filename = "./recursive_deep.rmap"
    expected_lookup_result = ("foo.fits", "foo.fits")
    _rmap_str = RMAP_STR

    @fixture(autouse=True)
    def _set_config(self, tobs_test_cache_state):
        self._config = tobs_test_cache_state

    @property
    def _rmap(self):
        return rmap.get_cached_mapping("tobs_tinstr_tfilekind.rmap")

    def test_deep_recursive_modify_rmap(self):
        recursive_modify_rmap(self._rmap_str, self.insert_header, self.result_filename)
    
    def test_deep_recursive_use_rmap(self):
        recursive_use_rmap(self.result_filename, self.lookup_header, self.expected_lookup_result)
    
    def test_deep_recursive_teardown(self):
        recursive_tear_down(self.result_filename)


@mark.multimission
@mark.core
@mark.rmap
@mark.selectors
class TestRecursiveUseAfter:

    insert_header = lookup_header = {
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "DATE-OBS" : "2017-04-20",
          "TIME-OBS" : "00:00:00",
          "SW_VERSION" : "1.2",
          "CLOSETIME" : "2017-05-30 00:01:02",
          "BRACKET_PAR" : "4.4",   # try a number
          "PARAMETER" : "2012-09-09 03:07",
          "GEOM_PAR" : "2.7",  # try a string-formatted number
    }
    result_filename = "./recursive_useafter.rmap"
    expected_lookup_result = "foo.fits"
    _rmap_str = '''
header = {
    'derived_from' : 'Hand written 01-15-2013',
    'filekind' : 'TFILEKIND',
    'instrument' : 'TINSTR',
    'mapping' : 'REFERENCE',
    'name' : 'test.rmap',
    'observatory' : 'TOBS',
    'parkey' : (('DATE-OBS','TIME-OBS',), ('MATCH_PAR1','MATCH_PAR2'),),
    'sha1sum' : 'd412b94d1af1a0871fe39d7096e65aea1187c3b7',
    'classes' : ('UseAfter','Match',)
}

selector = UseAfter({
    '2015-04-01 01:02:03' : Match({
    }),
    '2017-04-20 01:02:03' : Match({
    }),
    '2018-04-03 01:02:03' : Match({
    }),
})
'''

    @fixture(autouse=True)
    def _set_config(self, tobs_test_cache_state):
        self._config = tobs_test_cache_state
    
    @property
    def _rmap(self):
        return rmap.get_cached_mapping("tobs_tinstr_tfilekind.rmap")

    def test_recursive_useafter_modify_rmap(self):
        recursive_modify_rmap(self._rmap_str, self.insert_header, self.result_filename)
    
    def test_recursive_useafter_use_rmap(self):
        recursive_use_rmap(self.result_filename, self.lookup_header, self.expected_lookup_result)
    
    def test_recursive_useafter_teardown(self):
        recursive_tear_down(self.result_filename)

@mark.multimission
@mark.core
@mark.rmap
@mark.selectors
class TestRecursiveClosestTime:

    insert_header = lookup_header = {
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "DATE-OBS" : "2017-04-20",
          "TIME-OBS" : "00:00:00",
          "SW_VERSION" : "1.2",
          "CLOSETIME" : "2017-05-30 00:01:02",
          "BRACKET_PAR" : "4.4",   # try a number
          "PARAMETER" : "2012-09-09 03:07",
          "GEOM_PAR" : "2.7",  # try a string-formatted number
    }
    result_filename = "./recursive_closest_time.rmap"
    expected_lookup_result = "foo.fits"
    _rmap_str = '''
header = {
    'derived_from' : 'Hand written 01-15-2013',
    'filekind' : 'TFILEKIND',
    'instrument' : 'TINSTR',
    'mapping' : 'REFERENCE',
    'name' : 'test.rmap',
    'observatory' : 'TOBS',
    'parkey' : (('CLOSETIME',), ('MATCH_PAR1','MATCH_PAR2'),),
    'sha1sum' : 'd412b94d1af1a0871fe39d7096e65aea1187c3b7',
    'classes' : ('ClosestTime','Match',)
}

selector = ClosestTime({
    '2015-04-01 01:02:03' : Match({
    }),
    '2017-04-20 01:02:03' : Match({
    }),
    '2018-04-03 01:02:03' : Match({
    }),
})
'''

    @fixture(autouse=True)
    def _set_config(self, tobs_test_cache_state):
        self._config = tobs_test_cache_state

    @property
    def _rmap(self):
        return rmap.get_cached_mapping("tobs_tinstr_tfilekind.rmap")

    def test_recursive_closesttime_modify_rmap(self):
        recursive_modify_rmap(self._rmap_str, self.insert_header, self.result_filename)
    
    def test_recursive_closesttime_use_rmap(self):
        recursive_use_rmap(self.result_filename, self.lookup_header, self.expected_lookup_result)
    
    def test_recursive_closesttime_teardown(self):
        recursive_tear_down(self.result_filename)

@mark.multimission
@mark.core
@mark.rmap
@mark.selectors
class TestRecursiveSelectVersion:

    insert_header = lookup_header = {
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "SW_VERSION" : "1.2",
        }
    result_filename = "./recursive_select_version.rmap"
    expected_lookup_result = "foo.fits"
    _rmap_str = RMAP_STR_SELECT

    @fixture(autouse=True)
    def _set_config(self, tobs_test_cache_state):
        self._config = tobs_test_cache_state

    @property
    def _rmap(self):
        return rmap.get_cached_mapping("tobs_tinstr_tfilekind.rmap")

    def test_recursive_selectversion_modify_rmap(self):
        recursive_modify_rmap(self._rmap_str, self.insert_header, self.result_filename)
    
    def test_recursive_selectversion_use_rmap(self):
        recursive_use_rmap(self.result_filename, self.lookup_header, self.expected_lookup_result)
    
    def test_recursive_selectversion_teardown(self):
        recursive_tear_down(self.result_filename)


@mark.multimission
@mark.core
@mark.rmap
@mark.selectors
class TestRecursiveSelectVersion_MatchingVersion:
    insert_header = {
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "SW_VERSION" : "<3.1",
        }
    lookup_header = {
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "SW_VERSION" : "3.0",
        }
    result_filename = "./recursive_select_version.rmap"
    expected_lookup_result = "foo.fits"
    _rmap_str = RMAP_STR_SELECT

    @fixture(autouse=True)
    def _set_config(self, tobs_test_cache_state):
        self._config = tobs_test_cache_state

    @property
    def _rmap(self):
        return rmap.get_cached_mapping("tobs_tinstr_tfilekind.rmap")

    def test_recursive_selectmatching_modify_rmap(self):
        recursive_modify_rmap(self._rmap_str, self.insert_header, self.result_filename)
    
    def test_recursive_selectmatching_use_rmap(self):
        recursive_use_rmap(self.result_filename, self.lookup_header, self.expected_lookup_result)
    
    def test_recursive_selectmatching_teardown(self):
        recursive_tear_down(self.result_filename)


@mark.multimission
@mark.core
@mark.rmap
@mark.selectors
class TestRecursiveSelectVersion_DefaultVersion:

    _rmap_str = RMAP_STR_SELECT
    result_filename = "./recursive_select_version.rmap"
    expected_lookup_result = "foo.fits"
    insert_header = lookup_header = {
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "SW_VERSION" : "default",
        }

    @fixture(autouse=True)
    def _set_config(self, tobs_test_cache_state):
        self._config = tobs_test_cache_state
    
    @property
    def _rmap(self):
        return rmap.get_cached_mapping("tobs_tinstr_tfilekind.rmap")

    def test_recursive_selectmatching_modify_rmap(self):
        recursive_modify_rmap(self._rmap_str, self.insert_header, self.result_filename)
    
    def test_recursive_selectmatching_use_rmap(self):
        recursive_use_rmap(self.result_filename, self.lookup_header, self.expected_lookup_result)
    
    def test_recursive_selectmatching_teardown(self):
        recursive_tear_down(self.result_filename)


@mark.multimission
@mark.core
@mark.rmap
@mark.selectors
class TestRecursiveGeometricallyNearest:

    result_filename = "./recursive_geometrically_nearest.rmap"
    expected_lookup_result = "foo.fits"
    insert_header = lookup_header = {
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "GEOM_PAR" : "1.2",
    }
    _rmap_str = RMAP_GEO
    
    @fixture(autouse=True)
    def _set_config(self, tobs_test_cache_state):
        self._config = tobs_test_cache_state
    
    @property
    def _rmap(self):
        return rmap.get_cached_mapping("tobs_tinstr_tfilekind.rmap")

    def test_recursive_geometric_modify_rmap(self):
        recursive_modify_rmap(self._rmap_str, self.insert_header, self.result_filename)
    
    def test_recursive_geometric_use_rmap(self):
        recursive_use_rmap(self.result_filename, self.lookup_header, self.expected_lookup_result)
    
    def test_recursive_geometric_teardown(self):
        recursive_tear_down(self.result_filename)


@mark.multimission
@mark.core
@mark.rmap
@mark.selectors
class TestRecursiveGeometricallyNearestExact:
    insert_header = lookup_header = {
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "GEOM_PAR" : "0.1",
        }
    result_filename = "./recursive_geometrically_nearest.rmap"
    expected_lookup_result = "foo.fits"
    _rmap_str = '''
header = {
    'derived_from' : 'Hand written 01-15-2013',
    'filekind' : 'TFILEKIND',
    'instrument' : 'TINSTR',
    'mapping' : 'REFERENCE',
    'name' : 'test.rmap',
    'observatory' : 'TOBS',
    'parkey' : (('GEOM_PAR',), ('MATCH_PAR1','MATCH_PAR2'),),
    'sha1sum' : 'd412b94d1af1a0871fe39d7096e65aea1187c3b7',
    'classes' : ('GeometricallyNearest','Match',)
}

selector = GeometricallyNearest({
    0.1: Match({
        ('MPX', '98.7') : 'bar.fits',
    }),
    2.8 : Match({
    }),
    99.0 : Match({
    }),
})
'''
    
    @fixture(autouse=True)
    def _set_config(self, tobs_test_cache_state):
        self._config = tobs_test_cache_state
    
    @property
    def _rmap(self):
        return rmap.get_cached_mapping("tobs_tinstr_tfilekind.rmap")

    def test_recursive_geoexact_modify_rmap(self):
        recursive_modify_rmap(self._rmap_str, self.insert_header, self.result_filename)
    
    def test_recursive_geoexact_use_rmap(self):
        recursive_use_rmap(self.result_filename, self.lookup_header, self.expected_lookup_result)
    
    def test_recursive_geoexact_teardown(self):
        recursive_tear_down(self.result_filename)


@mark.multimission
@mark.core
@mark.rmap
@mark.selectors
class TestRecursiveBracket:

    result_filename = "./recursive_bracket.rmap"
    expected_lookup_result = ("foo.fits", "foo.fits")
    insert_header = lookup_header = {
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "BRACKET_PAR" : "0.5",
        }
    _rmap_str = '''
header = {
    'derived_from' : 'Hand written 01-15-2013',
    'filekind' : 'TFILEKIND',
    'instrument' : 'TINSTR',
    'mapping' : 'REFERENCE',
    'name' : 'test.rmap',
    'observatory' : 'TOBS',
    'parkey' : (('BRACKET_PAR',), ('MATCH_PAR1','MATCH_PAR2'),),
    'sha1sum' : 'd412b94d1af1a0871fe39d7096e65aea1187c3b7',
    'classes' : ('Bracket','Match',)
}

selector = Bracket({
    0.1: Match({
        ('MPX', '98.7') : 'bar.fits',
    }),
    2.8 : Match({
        ('MPX', '98.7') : 'bar.fits',
    }),
    99.0 : Match({
    }),
})
'''
    
    @fixture(autouse=True)
    def _set_config(self, tobs_test_cache_state):
        self._config = tobs_test_cache_state

    @property
    def _rmap(self):
        return rmap.get_cached_mapping("tobs_tinstr_tfilekind.rmap")

    def test_recursive_bracket_modify_rmap(self):
        recursive_modify_rmap(self._rmap_str, self.insert_header, self.result_filename)
    
    def test_recursive_bracket_use_rmap(self):
        recursive_use_rmap(self.result_filename, self.lookup_header, self.expected_lookup_result)
    
    def test_recursive_bracket_teardown(self):
        recursive_tear_down(self.result_filename)


@mark.multimission
@mark.core
@mark.rmap
@mark.selectors
class TestRecursiveBracketExact:

    result_filename = "./recursive_bracket.rmap"
    expected_lookup_result = ("foo.fits", "foo.fits")
    insert_header = lookup_header = {
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "BRACKET_PAR" : "0.1",
        }
    _rmap_str = '''
header = {
    'derived_from' : 'Hand written 01-15-2013',
    'filekind' : 'TFILEKIND',
    'instrument' : 'TINSTR',
    'mapping' : 'REFERENCE',
    'name' : 'test.rmap',
    'observatory' : 'TOBS',
    'parkey' : (('BRACKET_PAR',), ('MATCH_PAR1','MATCH_PAR2'),),
    'sha1sum' : 'd412b94d1af1a0871fe39d7096e65aea1187c3b7',
    'classes' : ('Bracket','Match',)
}

selector = Bracket({
    0.1: Match({
        ('MPX', '98.7') : 'bar.fits',
    }),
    2.8 : Match({
        ('MPX', '98.7') : 'bar.fits',
    }),
    99.0 : Match({
    }),
})
'''
    
    @fixture(autouse=True)
    def _set_config(self, tobs_test_cache_state):
        self._config = tobs_test_cache_state

    @property
    def _rmap(self):
        return rmap.get_cached_mapping("tobs_tinstr_tfilekind.rmap")

    def test_recursive_brackexact_modify_rmap(self):
        recursive_modify_rmap(self._rmap_str, self.insert_header, self.result_filename)
    
    def test_recursive_brackexact_use_rmap(self):
        recursive_use_rmap(self.result_filename, self.lookup_header, self.expected_lookup_result)
    
    def test_recursive_brackexact_teardown(self):
        recursive_tear_down(self.result_filename)


@mark.multimission
@mark.core
@mark.rmap
@mark.selectors
class TestRecursiveBracketExactMidLookup:

    result_filename = "./recursive_bracket.rmap"
    expected_lookup_result = ("foo.fits", "bar.fits")
    insert_header = {
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "BRACKET_PAR" : "0.1",
        }
    lookup_header = {
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "BRACKET_PAR" : "0.5",
        }
    _rmap_str = '''
header = {
    'derived_from' : 'Hand written 01-15-2013',
    'filekind' : 'TFILEKIND',
    'instrument' : 'TINSTR',
    'mapping' : 'REFERENCE',
    'name' : 'test.rmap',
    'observatory' : 'TOBS',
    'parkey' : (('BRACKET_PAR',), ('MATCH_PAR1','MATCH_PAR2'),),
    'sha1sum' : 'd412b94d1af1a0871fe39d7096e65aea1187c3b7',
    'classes' : ('Bracket','Match',)
}

selector = Bracket({
    0.1: Match({
        ('MP1', '99.9') : 'bar.fits',
    }),
    2.8 : Match({
        ('MP1', '99.9') : 'bar.fits',
    }),
    99.0 : Match({
    }),
})
'''
    
    @fixture(autouse=True)
    def _set_config(self, tobs_test_cache_state):
        self._config = tobs_test_cache_state

    @property
    def _rmap(self):
        return rmap.get_cached_mapping("tobs_tinstr_tfilekind.rmap")

    def test_recursive_brackmid_modify_rmap(self):
        recursive_modify_rmap(self._rmap_str, self.insert_header, self.result_filename)
    
    def test_recursive_brackmid_use_rmap(self):
        recursive_use_rmap(self.result_filename, self.lookup_header, self.expected_lookup_result)
    
    def test_recursive_brackmid_teardown(self):
        recursive_tear_down(self.result_filename)


@mark.multimission
@mark.core
@mark.rmap
@mark.selectors
class TestDeleteTest:

    result_filename = "./delete.rmap"
    lookup_header = {
          "MATCH_PAR1" : "MP1",
          "MATCH_PAR2" : "99.9",
          "BRACKET_PAR" : "0.5",
        }
    _rmap_str = '''
header = {
    'derived_from' : 'Hand written 01-15-2013',
    'filekind' : 'TFILEKIND',
    'instrument' : 'TINSTR',
    'mapping' : 'REFERENCE',
    'name' : 'test.rmap',
    'observatory' : 'TOBS',
    'parkey' : (('BRACKET_PAR',), ('MATCH_PAR1','MATCH_PAR2'),),
    'sha1sum' : 'd412b94d1af1a0871fe39d7096e65aea1187c3b7',
    'classes' : ('Bracket','Match',)
}

selector = Bracket({
    0.1: Match({
        ('MP1', '99.9') : 'bar.fits',
    }),
    2.8 : Match({
        ('MP1', '99.9') : 'bar.fits',
    }),
    99.0 : Match({
    }),
})
'''
    
    @fixture(autouse=True)
    def _set_config(self, tobs_test_cache_state):
        self._config = tobs_test_cache_state

    @property
    def _rmap(self):
        return rmap.get_cached_mapping("tobs_tinstr_tfilekind.rmap")

    def test_recursive_modify_rmap(self): # , header, value, classes):
        # Load the test rmap from a string.   The top level selector must exist.
        # This is not a "realistic" test case.   It's a test of the recursive
        # insertion capabilities of all the Selector classes in one go.
        log.verbose("-"*60)
        r = rmap.ReferenceMapping.from_string(self._rmap_str, "./test.rmap", ignore_checksum=True)
        result = r.delete("bar.fits")
        result.write(self.result_filename)
        log.verbose("result:\n", str(result))
        diffs = r.difference(result)
        log.verbose("diffs:", diffs)
        diffs = [diff for diff in diffs if "Selector" not in diff[-1]]
        assert len(diffs) == 2, "Fewer/more differences than expected: " + repr(diffs)
        for diff in diffs:
            assert "deleted Bracket rule" in diff[-1], "Bad difference " + repr(diff)
        log.verbose("recursive delete result rmap:")
        log.verbose(open(self.result_filename).read())

    def test_recursive_use_rmap(self):
        r = rmap.load_mapping(self.result_filename)
        ref = r.get_best_ref(self.lookup_header)
        log.verbose("ref:", ref)
        assert ref.startswith("NOT FOUND list index out of range")

    def test_delete_fails(self):
        log.verbose("-"*60)
        r = rmap.ReferenceMapping.from_string(self._rmap_str, "./test.rmap", ignore_checksum=True)
        try:
            result = r.delete("shazaam.fits")
        except crds.CrdsError:
            pass
        else:
            assert False, "Expected delete to fail."

    def test_recursive_tear_down(self):
        os.remove(self.result_filename)
