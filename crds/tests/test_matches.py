"""This module contains doctests and unit tests which exercise the crds.matches program."""
import os, os.path
from pprint import pprint as pp

import crds
from crds.core import rmap, log, exceptions, config
from crds import tests
from crds.matches import MatchesScript
from crds.client import api
from crds.tests import test_config

from nose.tools import assert_raises, assert_true

# ==================================================================================

HERE = os.path.dirname(__file__) or "."

# ==================================================================================

def dt_matches_files():
    """
    >>> old_state = test_config.setup()

    >>> MatchesScript("crds.matches  --contexts hst_0001.pmap --files lc41311jj_pfl.fits")()
     lc41311jj_pfl.fits : ACS PFLTFILE DETECTOR='WFC' CCDAMP='A|ABCD|AC|AD|B|BC|BD|C|D' FILTER1='F625W' FILTER2='POL0V' OBSTYPE='IMAGING' FW1OFFST='N/A' FW2OFFST='N/A' FWSOFFST='N/A' DATE-OBS='1997-01-01' TIME-OBS='00:00:00'
    0
    >>> config.set_crds_state(old_state)
    """

def dt_matches_files_omit_parameters_brief():
    """
    >>> old_state = test_config.setup()
    >>> MatchesScript("crds.matches  --contexts hst_0001.pmap --files lc41311jj_pfl.fits --omit-parameter-names --brief-paths")()
     lc41311jj_pfl.fits :  'WFC' 'A|ABCD|AC|AD|B|BC|BD|C|D' 'F625W' 'POL0V' 'IMAGING' 'N/A' 'N/A' 'N/A' '1997-01-01' '00:00:00'
    0
    >>> config.set_crds_state(old_state)
    """

def dt_matches_tuple_format():
    """
    >>> old_state = test_config.setup()
    >>> MatchesScript("crds.matches --contexts hst.pmap --files lc41311jj_pfl.fits --tuple-format")()
     lc41311jj_pfl.fits : (('OBSERVATORY', 'HST'), ('INSTRUMENT', 'ACS'), ('FILEKIND', 'PFLTFILE'), ('DETECTOR', 'WFC'), ('CCDAMP', 'A|ABCD|AC|AD|B|BC|BD|C|D'), ('FILTER1', 'F625W'), ('FILTER2', 'POL0V'), ('OBSTYPE', 'IMAGING'), ('FW1OFFST', 'N/A'), ('FW2OFFST', 'N/A'), ('FWSOFFST', 'N/A'), ('DATE-OBS', '1997-01-01'), ('TIME-OBS', '00:00:00'))
    0
    >>> config.set_crds_state(old_state)
    """

def dt_matches_datasets_minimize_headers_contexts_condition():
    """
    >>> old_state = test_config.setup()
    >>> MatchesScript("crds.matches --datasets JBANJOF3Q --minimize-headers --contexts hst_0048.pmap hst_0044.pmap --condition-values")()
    JBANJOF3Q:JBANJOF3Q : hst_0044.pmap : APERTURE='WFC1-2K' ATODCORR='OMIT' BIASCORR='OMIT' CCDAMP='B' CCDCHIP='1.0' CCDGAIN='2.0' CRCORR='OMIT' DARKCORR='OMIT' DATE-OBS='2010-01-31' DETECTOR='WFC' DQICORR='PERFORM' DRIZCORR='OMIT' FILTER1='F502N' FILTER2='F660N' FLASHCUR='OFF' FLATCORR='OMIT' FLSHCORR='OMIT' FW1OFFST='0.0' FW2OFFST='0.0' FWSOFFST='0.0' GLINCORR='UNDEFINED' INSTRUME='ACS' LTV1='-2048.0' LTV2='-1.0' NUMCOLS='2070.0' NUMROWS='2046.0' OBSTYPE='INTERNAL' PCTECORR='OMIT' PHOTCORR='OMIT' REFTYPE='UNDEFINED' SHADCORR='OMIT' SHUTRPOS='B' TIME-OBS='01:07:14.960000' XCORNER='1.0' YCORNER='2072.0'
    JBANJOF3Q:JBANJOF3Q : hst_0048.pmap : APERTURE='WFC1-2K' ATODCORR='OMIT' BIASCORR='OMIT' CCDAMP='B' CCDCHIP='1.0' CCDGAIN='2.0' CRCORR='OMIT' DARKCORR='OMIT' DATE-OBS='2010-01-31' DETECTOR='WFC' DQICORR='PERFORM' DRIZCORR='OMIT' FILTER1='F502N' FILTER2='F660N' FLASHCUR='OFF' FLATCORR='OMIT' FLSHCORR='OMIT' FW1OFFST='0.0' FW2OFFST='0.0' FWSOFFST='0.0' GLINCORR='UNDEFINED' INSTRUME='ACS' LTV1='-2048.0' LTV2='-1.0' NUMCOLS='2070.0' NUMROWS='2046.0' OBSTYPE='INTERNAL' PCTECORR='OMIT' PHOTCORR='OMIT' REFTYPE='UNDEFINED' SHADCORR='OMIT' SHUTRPOS='B' TIME-OBS='01:07:14.960000' XCORNER='1.0' YCORNER='2072.0'
    0
    >>> config.set_crds_state(old_state)
    """

# ==================================================================================


def tst():
    """Run module tests,  for now just doctests only."""
    from crds.tests import test_matches, tstmod
    return tstmod(test_matches)

if __name__ == "__main__":
    print(tst())
