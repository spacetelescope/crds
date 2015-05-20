"""This module contains doctests and unit tests which exercise the crds.matches program."""

from __future__ import division # confidence high
from __future__ import with_statement
from __future__ import print_function

import os, os.path
from pprint import pprint as pp

import crds
from crds import rmap, log, exceptions, config, tests
from crds.matches import MatchesScript
from crds.client import api
from crds.tests import CRDSTestCase, test_config

from nose.tools import assert_raises, assert_true

# ==================================================================================

HERE = os.path.dirname(__file__) or "."

# ==================================================================================

def test_matches_script():
    """
    >>> old_state = test_config.setup()
    >>> old_state = config.get_crds_state(clear_existing=True)
    >>> os.environ["CRDS_MAPPATH"] = tests.CRDS_DIR + "/cache/mappings"
    >>> os.environ["CRDS_SERVER_URL"] = "hst-crds-dev.stsci.edu"
    
    >>> _ = MatchesScript("crds.matches  --contexts hst_0001.pmap --files lc41311jj_pfl.fits")()
     lc41311jj_pfl.fits : ACS PFLTFILE DETECTOR='WFC' CCDAMP='A|ABCD|AC|AD|B|BC|BD|C|D' FILTER1='F625W' FILTER2='POL0V' OBSTYPE='IMAGING' FW1OFFST='N/A' FW2OFFST='N/A' FWSOFFST='N/A' DATE-OBS='1997-01-01' TIME-OBS='00:00:00'
    
    >>> _ = MatchesScript("crds.matches  --contexts hst_0001.pmap --files lc41311jj_pfl.fits --omit-parameter-names --brief-paths")()
     lc41311jj_pfl.fits :  'WFC' 'A|ABCD|AC|AD|B|BC|BD|C|D' 'F625W' 'POL0V' 'IMAGING' 'N/A' 'N/A' 'N/A' '1997-01-01' '00:00:00'
    
    >>> _ = MatchesScript("crds.matches --contexts hst.pmap --files lc41311jj_pfl.fits --tuple-format")()
     lc41311jj_pfl.fits : (('OBSERVATORY', 'HST'), ('INSTRUMENT', 'ACS'), ('FILEKIND', 'PFLTFILE'), ('DETECTOR', 'WFC'), ('CCDAMP', 'A|ABCD|AC|AD|B|BC|BD|C|D'), ('FILTER1', 'F625W'), ('FILTER2', 'POL0V'), ('OBSTYPE', 'IMAGING'), ('FW1OFFST', 'N/A'), ('FW2OFFST', 'N/A'), ('FWSOFFST', 'N/A'), ('DATE-OBS', '1997-01-01'), ('TIME-OBS', '00:00:00'))
    
    >>> _ = MatchesScript("crds.matches --datasets JBANJOF3Q --minimize-headers --contexts hst_0048.pmap hst_0044.pmap --condition-values")()
    JBANJOF3Q:JBANJOF3Q : hst_0044.pmap : APERTURE='WFC1-2K' ATODCORR='UNDEFINED' BIASCORR='UNDEFINED' CCDAMP='B' CCDCHIP='1.0' CCDGAIN='2.0' CRCORR='UNDEFINED' DARKCORR='UNDEFINED' DATE-OBS='2010-01-31' DETECTOR='WFC' DQICORR='UNDEFINED' DRIZCORR='UNDEFINED' FILTER1='F502N' FILTER2='F660N' FLASHCUR='OFF' FLATCORR='UNDEFINED' FLSHCORR='UNDEFINED' FW1OFFST='0.0' FW2OFFST='0.0' FWSOFFST='0.0' GLINCORR='UNDEFINED' INSTRUME='ACS' LTV1='-2048.0' LTV2='-1.0' NUMCOLS='2070.0' NUMROWS='2046.0' OBSTYPE='INTERNAL' PCTECORR='UNDEFINED' PHOTCORR='UNDEFINED' REFTYPE='UNDEFINED' SHADCORR='UNDEFINED' SHUTRPOS='B' TIME-OBS='01:07:14.960000' XCORNER='1.0' YCORNER='2072.0'
    JBANJOF3Q:JBANJOF3Q : hst_0048.pmap : APERTURE='WFC1-2K' ATODCORR='UNDEFINED' BIASCORR='UNDEFINED' CCDAMP='B' CCDCHIP='1.0' CCDGAIN='2.0' CRCORR='UNDEFINED' DARKCORR='UNDEFINED' DATE-OBS='2010-01-31' DETECTOR='WFC' DQICORR='UNDEFINED' DRIZCORR='UNDEFINED' FILTER1='F502N' FILTER2='F660N' FLASHCUR='OFF' FLATCORR='UNDEFINED' FLSHCORR='UNDEFINED' FW1OFFST='0.0' FW2OFFST='0.0' FWSOFFST='0.0' GLINCORR='UNDEFINED' INSTRUME='ACS' LTV1='-2048.0' LTV2='-1.0' NUMCOLS='2070.0' NUMROWS='2046.0' OBSTYPE='INTERNAL' PCTECORR='UNDEFINED' PHOTCORR='UNDEFINED' REFTYPE='UNDEFINED' SHADCORR='UNDEFINED' SHUTRPOS='B' TIME-OBS='01:07:14.960000' XCORNER='1.0' YCORNER='2072.0'
    
    >>> config.set_crds_state(old_state)
    """
    
# ==================================================================================


class TestRmap(CRDSTestCase):

    '''
    def test_rmap_get_imap_except(self):
        r = rmap.get_cached_mapping("hst.pmap")
        with self.assertRaises(exceptions.CrdsUnknownInstrumentError):
            r.get_imap("foo")
    '''

# ==================================================================================


def tst():
    """Run module tests,  for now just doctests only."""
    from crds.tests import test_matches
    import unittest, doctest
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRmap)
    unittest.TextTestRunner().run(suite)
    return doctest.testmod(test_matches)

if __name__ == "__main__":
    print(tst())
