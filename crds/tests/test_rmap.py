"""This module contains doctests and unit tests which exercise some of the more
complex features of the basic rmap infrastructure.
"""
import os
import json
from pprint import pprint as pp
import pickle

from crds import rmap, log, config, tests, utils
from crds.client import api
from crds.exceptions import *
from crds.tests import test_config

from nose.tools import assert_raises, assert_true

# ==================================================================================

def dt_get_derived_from_created():
    """
    >>> old_state = test_config.setup()
    >>> p = rmap.get_cached_mapping("hst.pmap")
    >>> p.get_derived_from()
    CRDS - INFO - Skipping derivation checks for root mapping 'hst.pmap' derived_from = 'created by hand 12-23-2011'
    >>> test_config.cleanup(old_state)
    """
def dt_get_derived_from_phony():
    """
    >>> old_state = test_config.setup()
    >>> r = rmap.get_cached_mapping("data/hst_acs_darkfile_phony_derive.rmap")
    >>> r.get_derived_from()
    CRDS - WARNING - Parent mapping for 'hst_acs_darkfile_phony_derive.rmap' = 'phony.rmap' does not exist.
    >>> test_config.cleanup(old_state)
    """

def dt_rmap_missing_references():
    """
    These are all missing because there is no reference file cache in this mode.

    >>> old_state = test_config.setup()
    >>> r = rmap.get_cached_mapping("data/hst_acs_darkfile_comment.rmap")
    >>> pp(r.missing_references())
    ['lcb12060j_drk.fits',
     'n3o1022cj_drk.fits',
     'n3o1022ej_drk.fits',
     'n3o1022fj_drk.fits',
     'n3o1022hj_drk.fits',
     'n3o1022ij_drk.fits',
     'n3o1022kj_drk.fits',
     'n3o1022lj_drk.fits',
     'r1u1415ij_drk.fits',
     'r1u1415kj_drk.fits',
     'r1u1415mj_drk.fits']
    >>> test_config.cleanup(old_state)
    """

def dt_rmap_minimum_header():
    """
    >>> old_state = test_config.setup()
    >>> p = rmap.get_cached_mapping("hst.pmap")
    >>> pp(p.get_minimum_header("data/cos_N8XTZCAWQ.fits"))
    {'CAMERA': '3.0',
     'DATE-OBS': '2005-05-13',
     'FILTER': 'F160W',
     'INSTRUME': 'NICMOS',
     'NREAD': '1.0',
     'OBSMODE': 'MULTIACCUM',
     'READOUT': 'FAST',
     'REFTYPE': 'UNDEFINED',
     'SAMP_SEQ': 'SPARS64',
     'TIME-OBS': '11:00:47'}
    >>> test_config.cleanup(old_state)
    """



def dt_rmap_str():
    """
    >>> old_state = test_config.setup()
    >>> r = rmap.get_cached_mapping("data/hst_cos_bpixtab_0252.rmap")
    >>> print(str(r), end="")
    header = {
        'derived_from' : 'hst_cos_bpixtab_0251.rmap',
        'filekind' : 'BPIXTAB',
        'instrument' : 'COS',
        'mapping' : 'REFERENCE',
        'name' : 'hst_cos_bpixtab_0252.rmap',
        'observatory' : 'HST',
        'parkey' : (('DETECTOR',), ('DATE-OBS', 'TIME-OBS')),
        'reffile_format' : 'TABLE',
        'reffile_required' : 'NONE',
        'reffile_switch' : 'NONE',
        'rmap_relevance' : 'ALWAYS',
        'sha1sum' : 'd2024dade52a406af70fcdf27a81088004d67cae',
    }
    <BLANKLINE>
    selector = Match({
        ('FUV',) : UseAfter({
            '1996-10-01 00:00:00' : 's7g1700dl_bpix.fits',
            '2009-05-11 00:00:00' : 'z1r1943fl_bpix.fits',
        }),
        ('NUV',) : UseAfter({
            '1996-10-01 00:00:00' : 's7g1700pl_bpix.fits',
            '2009-05-11 00:00:00' : 'uas19356l_bpix.fits',
        }),
    })
    >>> test_config.cleanup(old_state)
    """

def dt_rmap_obs_package():
    """
    >>> old_state = test_config.setup()
    >>> p = rmap.get_cached_mapping("data/hst_acs_darkfile.rmap")
    >>> p.obs_package.__name__
    'crds.hst'
    >>> test_config.cleanup(old_state)
    """

def dt_rmap_format_with_comment():
    '''
    >>> old_state = test_config.setup()
    >>> r = rmap.get_cached_mapping("data/hst_acs_darkfile_comment.rmap")
    >>> print(r.comment, end="")
    <BLANKLINE>
    This is a block comment which can be used to store additional metadata
    about the state and evolution of this type and files.

    >>> print(r, end="")
    header = {
        'derived_from' : 'generated from CDBS database 2013-01-11 13:58:14.664182',
        'filekind' : 'DARKFILE',
        'instrument' : 'ACS',
        'mapping' : 'REFERENCE',
        'name' : 'hst_acs_darkfile_comment.rmap',
        'observatory' : 'HST',
        'parkey' : (('DETECTOR', 'CCDAMP', 'CCDGAIN'), ('DATE-OBS', 'TIME-OBS')),
        'parkey_relevance' : {
            'ccdamp' : '(DETECTOR != "SBC")',
            'ccdgain' : '(DETECTOR != "SBC")',
        },
        'rmap_relevance' : 'ALWAYS',
        'sha1sum' : '0b3af86642812a1af65b77d429886e186acef915',
    }
    <BLANKLINE>
    comment = """
    This is a block comment which can be used to store additional metadata
    about the state and evolution of this type and files.
    """
    <BLANKLINE>
    selector = Match({
        ('HRC', 'A|ABCD|AD|B|BC|C|D', '1.0|2.0|4.0|8.0') : UseAfter({
            '1992-01-01 00:00:00' : 'lcb12060j_drk.fits',
            '2002-03-01 00:00:00' : 'n3o1022cj_drk.fits',
            '2002-03-18 00:00:00' : 'n3o1022ej_drk.fits',
            '2002-03-19 00:34:31' : 'n3o1022fj_drk.fits',
            '2002-03-20 00:34:32' : 'n3o1022hj_drk.fits',
            '2002-03-21 00:34:31' : 'n3o1022ij_drk.fits',
            '2002-03-22 00:34:30' : 'n3o1022kj_drk.fits',
            '2002-03-23 00:34:28' : 'n3o1022lj_drk.fits',
            '2007-01-21 02:09:05' : 'r1u1415ij_drk.fits',
            '2007-01-22 00:40:13' : 'r1u1415kj_drk.fits',
            '2007-01-26 00:07:33' : 'r1u1415mj_drk.fits',
        }),
    })
    >>> test_config.cleanup(old_state)
    '''

def dt_rmap_warn_checksum():
    """
    >>> old_state = test_config.setup()
    >>> r = rmap.ReferenceMapping.from_string('''
    ... header = {
    ...    'derived_from' : 'generated from CDBS database 2013-01-11 13:58:14.664182',
    ...    'filekind' : 'DARKFILE',
    ...    'instrument' : 'ACS',
    ...    'mapping' : 'REFERENCE',
    ...    'name' : 'hst_acs_darkfile_comment.rmap',
    ...    'observatory' : 'HST',
    ...    'parkey' : (('DETECTOR', 'CCDAMP', 'CCDGAIN'), ('DATE-OBS', 'TIME-OBS')),
    ...    'sha1sum' : "something bad",
    ... }
    ...
    ... selector = Match({
    ...    ('HRC', 'A|ABCD|AD|B|BC|C|D', '1.0|2.0|4.0|8.0') : UseAfter({
    ...        '1992-01-01 00:00:00' : 'lcb12060j_drk.fits',
    ...        '2002-03-01 00:00:00' : 'n3o1022cj_drk.fits',
    ...     }),
    ... })
    ... ''', ignore_checksum='warn')
    CRDS - WARNING - Checksum error : sha1sum mismatch in '(noname)'
    >>> test_config.cleanup(old_state)
    """

def dt_rmap_get_reference_parkeys():
    """
    >>> old_state = test_config.setup()
    >>> r = rmap.get_cached_mapping("data/jwst_miri_specwcs_0004.rmap")
    >>> r.parkey
    (('META.INSTRUMENT.DETECTOR', 'META.INSTRUMENT.CHANNEL', 'META.INSTRUMENT.BAND', 'META.SUBARRAY.NAME'),)
    >>> r.get_reference_parkeys()
    ('BAND', 'CHANNEL', 'DETECTOR', 'META.EXPOSURE.TYPE', 'META.INSTRUMENT.BAND', 'META.INSTRUMENT.CHANNEL', 'META.INSTRUMENT.DETECTOR', 'META.INSTRUMENT.LAMP_STATE', 'META.SUBARRAY.NAME', 'META.VISIT.TSOVISIT', 'SUBARRAY')
    >>> test_config.cleanup(old_state)
    """

def dt_rmap_get_valid_values_map():
    """
    >>> old_state = test_config.setup()
    >>> i = rmap.get_cached_mapping("hst_acs.imap")
    >>> pp(i.get_valid_values_map())
    {'APERTURE': ['NONE',
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

    >>> pp(i.get_valid_values_map(remove_special=False)["CCDGAIN"])
    ['0.5', '1.0', '1.4', '2.0', '4.0', '8.0']

    >>> pp(i.get_valid_values_map(condition=True)["FW1OFFST"])
    ['-1.0', '0.0', '1.0', '2.0']
    >>> test_config.cleanup(old_state)
    """

def dt_rmap_get_valid_values_map_range():
    """
    >>> old_state = test_config.setup()
    >>> r = rmap.get_cached_mapping("data/hst_wfpc2_flatfile.rmap")
    >>> r.get_valid_values_map() == {'FILTER1': ('0.0', '1.0', '2.0', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0', '9.0', '10.0', '11.0', '12.0', '13.0', '14.0', '15.0', '16.0', '17.0', '18.0', '19.0', '20.0', '21.0', '22.0', '23.0', '24.0', '25.0', '26.0', '27.0', '28.0', '29.0', '30.0', '31.0', '32.0', '33.0', '34.0', '35.0', '36.0', '37.0', '38.0', '39.0', '40.0', '41.0', '42.0', '43.0', '44.0', '45.0', '46.0', '47.0', '48.0', '49.0', '50.0', '51.0', '52.0', '53.0', '54.0', '55.0', '56.0', '57.0', '58.0', '59.0', '60.0', '61.0', '62.0', '63.0', '64.0', '65.0', '66.0', '67.0', '68.0', '69.0', '70.0', '71.0'), 'FILTER2': ('0.0', '1.0', '2.0', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0', '9.0', '10.0', '11.0', '12.0', '13.0', '14.0', '15.0', '16.0', '17.0', '18.0', '19.0', '20.0', '21.0', '22.0', '23.0', '24.0', '25.0', '26.0', '27.0', '28.0', '29.0', '30.0', '31.0', '32.0', '33.0', '34.0', '35.0', '36.0', '37.0', '38.0', '39.0', '40.0', '41.0', '42.0', '43.0', '44.0', '45.0', '46.0', '47.0', '48.0', '49.0', '50.0', '51.0', '52.0', '53.0', '54.0', '55.0', '56.0', '57.0', '58.0', '59.0', '60.0', '61.0', '62.0', '63.0', '64.0', '65.0', '66.0', '67.0', '68.0', '69.0', '70.0', '71.0'), 'MODE': ('FULL', 'AREA')}
    True
    >>> test_config.cleanup(old_state)
    """

def dt_rmap_get_best_references_fail():
    """
    >>> old_state = test_config.setup()
    >>> i = rmap.get_cached_mapping("hst_acs.imap")
    >>> i.get_best_references({
    ... "DETECTOR" : "HRC",
    ... "CCDAMP" : "B",
    ... "CCDGAIN" : "7.0",
    ... "DARKCORR" : "PERFORM",
    ... "DATE-OBS" : "2015-04-30",
    ... "TIME-OBS" : "16:43:00",
    ... }, include=["darkfile"])
    {'darkfile': 'NOT FOUND No match found.'}
    >>> test_config.cleanup(old_state)
    """

def dt_validate_mapping_valid():
    """
    >>> old_state = test_config.setup()
    >>> r = rmap.get_cached_mapping("data/hst_acs_darkfile.rmap")
    >>> r.validate_mapping()
    >>> test_config.cleanup(old_state)
    """

def dt_validate_mapping_invalid1():
    """
    >>> old_state = test_config.setup()
    >>> r = rmap.get_cached_mapping("data/hst_acs_darkfile_invalid1.rmap")
    >>> r.validate_mapping()
    CRDS - ERROR - Match('DETECTOR', 'CCDAMP', 'CCDGAIN') : ('HRC', 'A|ABCD|AD|B|BC|C|DDDD', '1.0|2.0|4.0|8.0') :  parameter='CCDAMP' value='DDDD' is not in ('A', 'B', 'C', 'D', 'AC', 'AD', 'BC', 'BD', 'ABCD', 'N/A')
    >>> test_config.cleanup(old_state)
    """

def dt_validate_mapping_invalid2():
    """
    >>> old_state = test_config.setup()
    >>> r = rmap.get_cached_mapping("data/hst_acs_darkfile_invalid2.rmap")
    >>> r.validate_mapping()
    CRDS - ERROR - Match('DETECTOR', 'CCDAMP', 'CCDGAIN') : ('FOOBAR', 'A|ABCD|AD|B|BC|C|DDDD', '1.0|2.0|4.0|8.0') :  parameter='DETECTOR' value='FOOBAR' is not in ('WFC', 'HRC', 'SBC')
    >>> test_config.cleanup(old_state)
    """

def dt_rmap_asmapping_readonly():
    """
    >>> old_state = test_config.setup()
    >>> r = rmap.asmapping("data/hst_acs_darkfile.rmap", cached="readonly")
    >>> test_config.cleanup(old_state)
    """

def dt_rmap_get_equivalent_mapping_missing():
    """
    >>> old_state = test_config.setup()
    >>> p = rmap.get_cached_mapping("hst.pmap")
    >>> p.get_equivalent_mapping("hst_cos_twozxtab_0001.rmap")
    CRDS - WARNING - No equivalent filekind in 'hst_cos.imap' corresponding to 'hst_cos_twozxtab_0001.rmap'
    >>> test_config.cleanup(old_state)
    """

def dt_imap_match_not_applicable():
    """
    >>> old_state = test_config.setup()
    >>> p = rmap.get_cached_mapping("data/hst_acs_9999.imap")
    >>> p.get_best_references({
    ...      "DETECTOR" : "SBC",
    ...      "CCDAMP" : "A",
    ...      "CCDGAIN" : "1.0",
    ...      "DATE-OBS" : "1993-01-01",
    ...      "TIME-OBS" : "12:00:00",
    ...      "OBSTYPE" : "IMAGING",
    ...      "FLATCORR" : "PERFORM",
    ...      "DQICORR" : "PERFORM",
    ...      "DRIZCORR" : "PERFORM",
    ...      "PHOTCORR" : "PERFORM",
    ...      "DRIZCORR" : "PERFORM",
    ... })["pctetab"]
    'NOT FOUND n/a'
    >>> test_config.cleanup(old_state)
    """

def dt_imap_match_omit():
    """
    >>> old_state = test_config.setup()
    >>> p = rmap.get_cached_mapping("data/hst_acs_9999.imap")
    >>> "mlintab" in p.get_best_references({
    ...      "DETECTOR" : "SBC",
    ...      "CCDAMP" : "A",
    ...      "CCDGAIN" : "1.0",
    ...      "DATE-OBS" : "2002-03-19",
    ...      "TIME-OBS" : "00:34:32",
    ...      "OBSTYPE" : "IMAGING",
    ...      "FLATCORR" : "PERFORM",
    ...      "DQICORR" : "PERFORM",
    ...      "DRIZCORR" : "PERFORM",
    ...      "PHOTCORR" : "PERFORM",
    ...      "DRIZCORR" : "PERFORM",
    ... })
    False
    >>> test_config.cleanup(old_state)
    """

def dt_pickling():
    """
    >>> from crds import data_file

    >>> old_state = test_config.setup()

    >>> p = rmap.get_cached_mapping("hst.pmap")

    >>> s = pickle.dumps(p)
    >>> q = pickle.loads(s)

    >>> str(q) == str(p)
    True

    >>> p.difference(q)
    []
    >>> q.difference(p)
    []

    >>> p.validate_mapping()
    >>> q.validate_mapping()

    >>> header = data_file.get_header("data/j8bt06o6q_raw.fits")
    >>> refs_p = p.get_best_references(header)
    >>> refs_q = q.get_best_references(header)
    >>> refs_p == refs_q
    True

    >>> test_config.cleanup(old_state)
    """

# ==================================================================================

class TestRmap(test_config.CRDSTestCase):

    def test_rmap_get_imap_except(self):
        r = rmap.get_cached_mapping("hst.pmap")
        with self.assertRaises(CrdsUnknownInstrumentError):
            r.get_imap("foo")

    def test_rmap_get_filekind(self):
        r = rmap.get_cached_mapping("hst.pmap")
        self.assertEqual(set(r.get_filekinds("data/j8bt05njq_raw.fits")),
                         {'atodtab','biasfile','bpixtab','ccdtab','cfltfile','crrejtab',
                          'd2imfile','darkfile','dgeofile','drkcfile','flshfile','idctab',
                          'imphttab','mdriztab','mlintab','npolfile','oscntab','pctetab',
                          'pfltfile','shadfile','spottab'})

    def test_rmap_get_equivalent_mapping(self):
        i = rmap.get_cached_mapping("data/hst_acs_0002.imap")
        self.assertEqual(i.get_equivalent_mapping("hst.pmap"), None)
        self.assertEqual(i.get_equivalent_mapping("data/hst_acs_0001.imap").name, "hst_acs.imap")
        self.assertEqual(i.get_equivalent_mapping("data/hst_acs_biasfile_0002.rmap").name, "hst_acs_biasfile.rmap")

    def test_rmap_list_mappings(self):
        os.environ["CRDS_MAPPATH_SINGLE"] = self.data_dir
        self.assertEqual(rmap.list_mappings("*.imap", "hst"), [
                'hst_acs.imap', 'hst_acs_0001.imap', 'hst_acs_0002.imap', 'hst_acs_9999.imap',
                'hst_cos.imap', 'hst_nicmos.imap', 'hst_stis.imap', 'hst_wfc3.imap', 'hst_wfpc2.imap',
                'jwst_fgs_na.imap', 'jwst_miri_omit.imap', 'jwst_niriss_na_omit.imap', 'roman_wfi_0001.imap'])

    def test_rmap_list_references(self):
        os.environ["CRDS_REFPATH_SINGLE"] = self.data_dir
        config.CRDS_REF_SUBDIR_MODE = "flat"
        self.assertEqual(rmap.list_references("*.r1h", "hst"), ['dbu1405fu.r1h', 'dbu1405iu.r1h', 'e1b09593u.r1h', 'e1b09594u.r1h', 'valid.r1h'])

    def test_rmap_get_derived_from(self):
        # api.dump_mappings("hst.pmap", mappings=["hst_acs_flshfile_0251.rmap"])
        os.environ["CRDS_MAPPATH_SINGLE"] = self.data_dir
        r = rmap.get_cached_mapping("data/hst_acs_flshfile_0252.rmap")
        self.assertEqual(r.get_derived_from().name, 'hst_acs_flshfile_0251.rmap')

    def test_missing_required_header_key(self):
        with self.assertRaises(MissingHeaderKeyError):
            r = rmap.load_mapping("data/hst_acs_darkfile_missing_key.rmap")

    def test_load_rmap_bad_expr(self):
        with self.assertRaises(SyntaxError):
            r = rmap.get_cached_mapping("data/hst_acs_darkfile_badexpr.rmap")

    def test_rmap_get_parkey_map(self):
        i = rmap.get_cached_mapping("hst_acs.imap")
        with self.assertRaises(CrdsUnknownReftypeError):
            i.get_rmap("foo")

    def test_rmap_missing_checksum(self):
        with self.assertRaises(ChecksumError):
            r = rmap.ReferenceMapping.from_string('''
header = {
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
''')

    def test_rmap_schema_uri(self):
        r = rmap.ReferenceMapping.from_string('''
header = {
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
''', ignore_checksum=True)
        self.assertEquals(r.schema_uri, 'http://stsci.edu/schemas/asdf/core/ndarray-1.0.0')
        r.validate()

    def test_rmap_schema_uri_missing(self):
        r = rmap.ReferenceMapping.from_string('''
header = {
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
''', ignore_checksum=True)
        with self.assertRaises(FileNotFoundError):
            r.validate()

    def test_rmap_get_best_references_include(self):
        r = rmap.get_cached_mapping("data/hst_acs_darkfile_comment.rmap")
        header = {
            'CCDAMP': 'ABCD',
            'CCDGAIN': '1.0',
            'DARKCORR': 'UNDEFINED',
            'DATE-OBS': '2002-07-18',
            'DETECTOR': 'WFC',
            'TIME-OBS': '18:09:15.773332'}
        with self.assertRaises(CrdsUnknownReftypeError):
            r.get_best_references(header, include=["flatfile"])

    def test_rmap_get_parkey_map(self):
        i = rmap.get_cached_mapping("hst_acs.imap")
        i.get_parkey_map() == {'APERTURE': ['*',
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
                  'WFCENTER'],
     'ATODCORR': ['PERFORM', 'NONE', 'OMIT', 'COMPLETE', 'UNDEFINED'],
     'BIASCORR': ['PERFORM', 'NONE', 'OMIT', 'COMPLETE', 'UNDEFINED'],
     'CCDAMP': ['A', 'ABCD', 'AC', 'AD', 'B', 'BC', 'BD', 'C', 'D', 'N/A'],
     'CCDCHIP': ['N/A'],
     'CCDGAIN': ['0.5', '1.0', '1.4', '2.0', '4.0', '8.0', 'N/A'],
     'CRCORR': ['PERFORM', 'NONE', 'OMIT', 'COMPLETE', 'UNDEFINED'],
     'DARKCORR': ['PERFORM', 'NONE', 'OMIT', 'COMPLETE', 'UNDEFINED'],
     'DETECTOR': ['HRC', 'SBC', 'WFC'],
     'DQICORR': ['PERFORM', 'NONE', 'OMIT', 'COMPLETE', 'UNDEFINED'],
     'DRIZCORR': ['NONE', 'COMPLETE', 'PERFORM', 'OMIT', 'UNDEFINED'],
     'FILTER1': ['*',
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
                 'N/A',
                 'POL0V',
                 'POL120V',
                 'POL60V',
                 'PR200L'],
     'FLASHCUR': ['HIGH', 'LOW', 'MED'],
     'FLATCORR': ['PERFORM', 'NONE', 'OMIT', 'COMPLETE', 'UNDEFINED'],
     'FLSHCORR': ['PERFORM', 'NONE', 'OMIT', 'COMPLETE', 'UNDEFINED'],
     'FW1OFFST': ['-1.0', '1.0', 'N/A'],
     'FW2OFFST': ['-1.0', '1.0', 'N/A'],
     'FWSOFFST': ['N/A'],
     'GLINCORR': ['PERFORM', 'NONE', 'OMIT', 'COMPLETE', 'UNDEFINED'],
     'LTV1': ['-1816.0',
              '-2048.0',
              '-3072.0',
              '-3584.0',
              '-3604.0',
              '19.0',
              '22.0',
              '24.0',
              'N/A'],
     'LTV2': ['-1.0',
              '-1023.0',
              '-1535.0',
              '-1591.0',
              '-57.0',
              '-824.0',
              '0.0',
              '20.0',
              'N/A'],
     'NUMCOLS': ['1046.0',
                 '1062.0',
                 '2070.0',
                 '2300.0',
                 '4144.0',
                 '512.0',
                 '534.0',
                 'N/A'],
     'NUMROWS': ['1024.0', '1044.0', '2046.0', '2068.0', '400.0', '512.0', 'N/A'],
     'OBSTYPE': ['CORONAGRAPHIC', 'IMAGING', 'SPECTROSCOPIC'],
     'PCTECORR': ['NONE', 'COMPLETE', 'PERFORM', 'OMIT', 'UNDEFINED'],
     'PHOTCORR': ['PERFORM', 'NONE', 'OMIT', 'COMPLETE', 'UNDEFINED'],
     'SHADCORR': ['PERFORM', 'NONE', 'OMIT', 'COMPLETE', 'UNDEFINED'],
     'SHUTRPOS': ['A', 'B'],
     'XCORNER': ['N/A'],
     'YCORNER': ['N/A']}

    maxDiff = None

    def test_rmap_todict(self):
        r = rmap.get_cached_mapping("data/hst_cos_bpixtab_0252.rmap")
        self.assertEqual(r.todict(), {'text_descr': 'Data Quality (Bad Pixel) Initialization Table', 'selections': [('FUV', '1996-10-01 00:00:00', 's7g1700dl_bpix.fits'), ('FUV', '2009-05-11 00:00:00', 'z1r1943fl_bpix.fits'), ('NUV', '1996-10-01 00:00:00', 's7g1700pl_bpix.fits'), ('NUV', '2009-05-11 00:00:00', 'uas19356l_bpix.fits')], 'header': {'sha1sum': 'd2024dade52a406af70fcdf27a81088004d67cae', 'reffile_switch': 'none', 'filekind': 'bpixtab', 'instrument': 'cos', 'derived_from': 'hst_cos_bpixtab_0251.rmap', 'reffile_format': 'table', 'observatory': 'hst', 'parkey': (('DETECTOR',), ('DATE-OBS', 'TIME-OBS')), 'reffile_required': 'none', 'rmap_relevance': 'always', 'mapping': 'reference', 'name': 'hst_cos_bpixtab_0252.rmap'}, 'parameters': ('DETECTOR', 'USEAFTER', 'REFERENCE')})

    def test_rmap_tojson(self):
        r = rmap.get_cached_mapping("data/hst_cos_bpixtab_0252.rmap")
        self.assertEqual(json.loads(r.tojson()), {u'header': {u'observatory': u'hst', u'name': u'hst_cos_bpixtab_0252.rmap', u'reffile_required': u'none', u'parkey': [[u'DETECTOR'], [u'DATE-OBS', u'TIME-OBS']], u'mapping': u'reference', u'filekind': u'bpixtab', u'instrument': u'cos', u'derived_from': u'hst_cos_bpixtab_0251.rmap', u'reffile_switch': u'none', u'reffile_format': u'table', u'rmap_relevance': u'always', u'sha1sum': u'd2024dade52a406af70fcdf27a81088004d67cae'}, u'text_descr': u'Data Quality (Bad Pixel) Initialization Table', u'parameters': [u'DETECTOR', u'USEAFTER', u'REFERENCE'], u'selections': [[u'FUV', u'1996-10-01 00:00:00', u's7g1700dl_bpix.fits'], [u'FUV', u'2009-05-11 00:00:00', u'z1r1943fl_bpix.fits'], [u'NUV', u'1996-10-01 00:00:00', u's7g1700pl_bpix.fits'], [u'NUV', u'2009-05-11 00:00:00', u'uas19356l_bpix.fits']]})

    def test_rmap_match_not_applicable(self):
        r = rmap.get_cached_mapping("data/hst_acs_darkfile_na_omit.rmap")
        r.get_best_ref({
                "DETECTOR" : "SBC",
                "CCDAMP" : "A",
                "CCDGAIN" : "1.0",
                "DATE-OBS" : "1993-01-01",
                "TIME-OBS" : "12:00:00",
                }) == "NOT FOUNT n/a"

    def test_rmap_match_omit(self):
        r = rmap.get_cached_mapping("data/hst_acs_darkfile_na_omit.rmap")
        r.get_best_ref({
                "DETECTOR" : "SBC",
                "CCDAMP" : "A",
                "CCDGAIN" : "1.0",
                "DATE-OBS" : "2002-03-19",
                "TIME-OBS" : "00:34:32",
                }) is None

    def test_rmap_todict(self):
        p = rmap.get_cached_mapping("hst.pmap")
        p.todict()

    def test_rmap_match_tjson(self):
        os.environ["CRDS_PATH"] = test_config.CRDS_TESTING_CACHE
        p = rmap.get_cached_mapping("jwst.pmap")
        p.tojson()

    def _get_rmap(self):
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

    def test_ref_to_dataset_ir(self):

        # rmap update time conversions don't map comment parkeys to N/A

        r = self._get_rmap()

        header = dict(
            DETECTOR="IR", CCDAMP="ABCD", BINAXIS1="1.0", BINAXIS2="2.0",
            CCDGAIN="1.0", SAMP_SEQ="MIF1200", SUBTYPE="FULLIMAG", DARKCORR="PERFORM")

        # transform for rmap updates
        dheader = utils.Struct(r.reference_to_dataset_header(header))

        self.assertEqual(dheader.DETECTOR, "IR")
        self.assertEqual(dheader.CCDAMP, "ABCD")
        self.assertEqual(dheader.BINAXIS1, "1.0")   # comment
        self.assertEqual(dheader.BINAXIS2, "N/A")   # non-comment
        self.assertEqual(dheader.CCDGAIN, "1.0")
        self.assertEqual(dheader.SAMP_SEQ, "MIF1200")
        self.assertEqual(dheader.SUBTYPE, "FULLIMAG")
        self.assertEqual(dheader.DARKCORR, "N/A")

    def test_ref_to_dataset_uvis(self):

        r = self._get_rmap()

        header = dict(
            DETECTOR="UVIS", CCDAMP="ABCD", BINAXIS1="1.0", BINAXIS2="2.0",
            CCDGAIN="1.0", SAMP_SEQ="MIF1200", SUBTYPE="FULLIMAG", DARKCORR="PERFORM")

        # transform for rmap updates
        dheader = utils.Struct(r.reference_to_dataset_header(header))

        self.assertEqual(dheader.DETECTOR, "UVIS")
        self.assertEqual(dheader.CCDAMP, "ABCD")
        self.assertEqual(dheader.BINAXIS1, "1.0")   # comment
        self.assertEqual(dheader.BINAXIS2, "2.0")   # non-comment
        self.assertEqual(dheader.CCDGAIN, "N/A")
        self.assertEqual(dheader.SAMP_SEQ, "N/A")
        self.assertEqual(dheader.SUBTYPE, "N/A")
        self.assertEqual(dheader.DARKCORR, "N/A")

    def test_na_parkeys_ir(self):

        r = self._get_rmap()

        # bestrefs time conversions still map comment parkeys to N/A

        header = dict(
            DETECTOR="IR", CCDAMP="ABCD", BINAXIS1="1.0", BINAXIS2="2.0",
            CCDGAIN="1.0", SAMP_SEQ="MIF1200", SUBTYPE="FULLIMAG", DARKCORR="PERFORM")

        # transform for bestrefs
        dheader = utils.Struct(r.map_irrelevant_parkeys_to_na(header))

        self.assertEqual(dheader.DETECTOR, "IR")
        self.assertEqual(dheader.CCDAMP, "ABCD")
        self.assertEqual(dheader.BINAXIS1, "N/A")   # comment
        self.assertEqual(dheader.BINAXIS2, "N/A")   # non-comment
        self.assertEqual(dheader.CCDGAIN, "1.0")
        self.assertEqual(dheader.SAMP_SEQ, "MIF1200")
        self.assertEqual(dheader.SUBTYPE, "FULLIMAG")
        self.assertEqual(dheader.DARKCORR, "PERFORM")

    def test_na_parkeys_uvis(self):

        r = self._get_rmap()

        header = dict(
            DETECTOR="UVIS", CCDAMP="ABCD", BINAXIS1="1.0", BINAXIS2="2.0",
            CCDGAIN="1.0", SAMP_SEQ="MIF1200", SUBTYPE="FULLIMAG", DARKCORR="PERFORM")

        # transform for bestrefs
        dheader = utils.Struct(r.map_irrelevant_parkeys_to_na(header))

        self.assertEqual(dheader.DETECTOR, "UVIS")
        self.assertEqual(dheader.CCDAMP, "ABCD")
        self.assertEqual(dheader.BINAXIS1, "N/A")   # comment
        self.assertEqual(dheader.BINAXIS2, "2.0")   # non-comment
        self.assertEqual(dheader.CCDGAIN, "N/A")
        self.assertEqual(dheader.SAMP_SEQ, "N/A")
        self.assertEqual(dheader.SUBTYPE, "N/A")
        self.assertEqual(dheader.DARKCORR, "PERFORM")

# ==================================================================================


def tst():
    """Run module tests,  for now just doctests only."""
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRmap)
    unittest.TextTestRunner().run(suite)

    from crds.tests import test_rmap, tstmod
    return tstmod(test_rmap)

if __name__ == "__main__":
    print(tst())
