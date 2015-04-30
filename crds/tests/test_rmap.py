"""This module contains doctests and unit tests which exercise some of the more
complex features of the basic rmap infrastructure.

"""

from __future__ import division # confidence high
from __future__ import with_statement
from __future__ import print_function

import unittest
import os
from pprint import pprint as pp

from crds import rmap, log, exceptions
from crds.tests import CRDSTestCase

from nose.tools import assert_raises, assert_true

# ==================================================================================

def test_get_derived_from():
    """
    >>> r = rmap.get_cached_mapping("hst_acs_flshfile_0252.rmap")
    >>> r.get_derived_from().name
    'hst_acs_flshfile_0251.rmap'
    """

def test_missing_required_header_key():
    """
    >>> r = rmap.load_mapping("data/hst_acs_darkfile_missing_key.rmap")
    Traceback (most recent call last):
    ...
    MissingHeaderKeyError: Required header key 'mapping' is missing.
    """

def test_rmap_str():
    """
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
    """

def test_rmap_obs_package():
    """
    >>> p = rmap.get_cached_mapping("data/hst_acs_darkfile.rmap")
    >>> p.obs_package.__name__
    'crds.hst'
    """
    
def test_rmap_format_with_comment():
    '''
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
    '''

def test_rmap_missing_checksum():
    """
    >>> r = rmap.ReferenceMapping.from_string('''
    ... header = {
    ...    'derived_from' : 'generated from CDBS database 2013-01-11 13:58:14.664182',
    ...    'filekind' : 'DARKFILE',
    ...    'instrument' : 'ACS',
    ...    'mapping' : 'REFERENCE',
    ...    'name' : 'hst_acs_darkfile_comment.rmap',
    ...    'observatory' : 'HST',
    ...    'parkey' : (('DETECTOR', 'CCDAMP', 'CCDGAIN'), ('DATE-OBS', 'TIME-OBS')),
    ... }
    ...
    ... selector = Match({
    ...    ('HRC', 'A|ABCD|AD|B|BC|C|D', '1.0|2.0|4.0|8.0') : UseAfter({
    ...        '1992-01-01 00:00:00' : 'lcb12060j_drk.fits',
    ...        '2002-03-01 00:00:00' : 'n3o1022cj_drk.fits',
    ...     }),
    ... })
    ... ''')
    Traceback (most recent call last):
    ...
    ChecksumError: sha1sum is missing in '(noname)'
    """

def test_rmap_todict():
    """
    >>> r = rmap.get_cached_mapping("data/hst_cos_bpixtab_0252.rmap")
    >>> pp(r.todict())
    {'header': LowerCaseDict({'observatory': 'HST', 'name': 'hst_cos_bpixtab_0252.rmap', 'reffile_required': 'NONE', 'parkey': (('DETECTOR',), ('DATE-OBS', 'TIME-OBS')), 'mapping': 'REFERENCE', 'filekind': 'BPIXTAB', 'instrument': 'COS', 'derived_from': 'hst_cos_bpixtab_0251.rmap', 'reffile_switch': 'NONE', 'reffile_format': 'TABLE', 'rmap_relevance': 'ALWAYS', 'sha1sum': 'd2024dade52a406af70fcdf27a81088004d67cae'}),
     'parameters': ('DETECTOR', 'USEAFTER', 'REFERENCE'),
     'selections': [('FUV', '1996-10-01 00:00:00', 's7g1700dl_bpix.fits'),
                    ('FUV', '2009-05-11 00:00:00', 'z1r1943fl_bpix.fits'),
                    ('NUV', '1996-10-01 00:00:00', 's7g1700pl_bpix.fits'),
                    ('NUV', '2009-05-11 00:00:00', 'uas19356l_bpix.fits')],
     'text_descr': 'Data Quality (Bad Pixel) Initialization Table'}
    """
def test_rmap_tojson():
    """
    >>> r = rmap.get_cached_mapping("data/hst_cos_bpixtab_0252.rmap")
    >>> pp(r.tojson())
    '{"header": {"observatory": "hst", "name": "hst_cos_bpixtab_0252.rmap", "reffile_required": "none", "parkey": [["DETECTOR"], ["DATE-OBS", "TIME-OBS"]], "mapping": "reference", "filekind": "bpixtab", "instrument": "cos", "derived_from": "hst_cos_bpixtab_0251.rmap", "reffile_switch": "none", "reffile_format": "table", "rmap_relevance": "always", "sha1sum": "d2024dade52a406af70fcdf27a81088004d67cae"}, "selections": [["FUV", "1996-10-01 00:00:00", "s7g1700dl_bpix.fits"], ["FUV", "2009-05-11 00:00:00", "z1r1943fl_bpix.fits"], ["NUV", "1996-10-01 00:00:00", "s7g1700pl_bpix.fits"], ["NUV", "2009-05-11 00:00:00", "uas19356l_bpix.fits"]], "parameters": ["DETECTOR", "USEAFTER", "REFERENCE"], "text_descr": "Data Quality (Bad Pixel) Initialization Table"}'
    """

def test_get_filekinds():
    """
    >>> r = rmap.get_cached_mapping("hst.pmap")
    """
    
# ==================================================================================

class CrdsRmapTests(CRDSTestCase):

    def test_get_imap_except(self):
        r = rmap.get_cached_mapping("hst.pmap")
        with self.assertRaises(exceptions.CrdsUnknownInstrumentError):
            r.get_imap("foo")

    def test_get_filekind(self):
        r = rmap.get_cached_mapping("hst.pmap")
        self.assertEqual(r.get_filekinds("data/j8bt05njq_raw.fits"),
                         [ 'PCTETAB', 'CRREJTAB', 'DARKFILE', 'D2IMFILE', 'BPIXTAB', 'ATODTAB', 'BIASFILE',
                           'SPOTTAB', 'MLINTAB', 'DGEOFILE', 'FLSHFILE', 'NPOLFILE', 'OSCNTAB', 'CCDTAB',
                           'SHADFILE', 'IDCTAB', 'IMPHTTAB', 'PFLTFILE', 'DRKCFILE', 'CFLTFILE', 'MDRIZTAB'])

# ==================================================================================


def test():
    """Run module tests,  for now just doctests only."""
    unittest.main()
    import test_rmap, doctest
    return doctest.testmod(test_rmap)

if __name__ == "__main__":
    print(test())
