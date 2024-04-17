from crds.matches import MatchesScript
from pytest import mark


@mark.hst
@mark.matches
def test_matches_files(capsys, hst_default_cache_state):
    MatchesScript("crds.matches  --contexts hst_0001.pmap --files lc41311jj_pfl.fits")()
    out, _ = capsys.readouterr()
    out_to_check = """lc41311jj_pfl.fits : ACS PFLTFILE DETECTOR='WFC' CCDAMP='A|ABCD|AC|AD|B|BC|BD|C|D' \
FILTER1='F625W' FILTER2='POL0V' OBSTYPE='IMAGING' FW1OFFST='N/A' FW2OFFST='N/A' FWSOFFST='N/A' \
DATE-OBS='1997-01-01' TIME-OBS='00:00:00'"""
    assert out_to_check in out


@mark.hst
@mark.matches
def test_matches_files_omit_parameters_brief(capsys, hst_default_cache_state):
    MatchesScript(
        "crds.matches  --contexts hst_0001.pmap --files lc41311jj_pfl.fits --omit-parameter-names --brief-paths")()
    out, _ = capsys.readouterr()
    out_to_check = """lc41311jj_pfl.fits :  'WFC' 'A|ABCD|AC|AD|B|BC|BD|C|D' 'F625W' 'POL0V' 'IMAGING' \
'N/A' 'N/A' 'N/A' '1997-01-01' '00:00:00'"""
    assert out_to_check in out


@mark.hst
@mark.matches
def test_matches_tuple_format(capsys, hst_default_cache_state):
    MatchesScript("crds.matches --contexts hst.pmap --files lc41311jj_pfl.fits --tuple-format")()
    out, _ = capsys.readouterr()
    out_to_check = """lc41311jj_pfl.fits : (('OBSERVATORY', 'HST'), ('INSTRUMENT', 'ACS'), ('FILEKIND', 'PFLTFILE'), \
('DETECTOR', 'WFC'), ('CCDAMP', 'A|ABCD|AC|AD|B|BC|BD|C|D'), ('FILTER1', 'F625W'), ('FILTER2', 'POL0V'), ('OBSTYPE', \
'IMAGING'), ('FW1OFFST', 'N/A'), ('FW2OFFST', 'N/A'), ('FWSOFFST', 'N/A'), ('DATE-OBS', '1997-01-01'), ('TIME-OBS', \
'00:00:00'))"""
    assert out_to_check in out


@mark.hst
@mark.matches
def test_matches_datasets_minimize_headers_contexts_condition(capsys, hst_shared_cache_state):
    MatchesScript(
        "crds.matches --datasets JBANJOF3Q --minimize-headers --contexts hst_0048.pmap hst_0044.pmap --condition-values")()
    out, _ = capsys.readouterr()
    out_to_check = """JBANJOF3Q:JBANJOF3Q : hst_0044.pmap : APERTURE='WFC1-2K' ATODCORR='OMIT' BIASCORR='OMIT' \
CCDAMP='B' CCDCHIP='1.0' CCDGAIN='2.0' CRCORR='OMIT' DARKCORR='OMIT' DATE-OBS='2010-01-31' DETECTOR='WFC' \
DQICORR='PERFORM' DRIZCORR='OMIT' FILTER1='F502N' FILTER2='F660N' FLASHCUR='OFF' FLATCORR='OMIT' FLSHCORR='OMIT' \
FW1OFFST='0.0' FW2OFFST='0.0' FWSOFFST='0.0' GLINCORR='UNDEFINED' INSTRUME='ACS' LTV1='-2048.0' LTV2='-1.0' \
NUMCOLS='2070.0' NUMROWS='2046.0' OBSTYPE='INTERNAL' PCTECORR='OMIT' PHOTCORR='OMIT' REFTYPE='UNDEFINED' \
SHADCORR='OMIT' SHUTRPOS='B' TIME-OBS='01:07:14.960000' XCORNER='1.0' YCORNER='2072.0'
JBANJOF3Q:JBANJOF3Q : hst_0048.pmap : APERTURE='WFC1-2K' ATODCORR='OMIT' BIASCORR='OMIT' \
CCDAMP='B' CCDCHIP='1.0' CCDGAIN='2.0' CRCORR='OMIT' DARKCORR='OMIT' DATE-OBS='2010-01-31' DETECTOR='WFC' \
DQICORR='PERFORM' DRIZCORR='OMIT' FILTER1='F502N' FILTER2='F660N' FLASHCUR='OFF' FLATCORR='OMIT' FLSHCORR='OMIT' \
FW1OFFST='0.0' FW2OFFST='0.0' FWSOFFST='0.0' GLINCORR='UNDEFINED' INSTRUME='ACS' LTV1='-2048.0' LTV2='-1.0' \
NUMCOLS='2070.0' NUMROWS='2046.0' OBSTYPE='INTERNAL' PCTECORR='OMIT' PHOTCORR='OMIT' REFTYPE='UNDEFINED' \
SHADCORR='OMIT' SHUTRPOS='B' TIME-OBS='01:07:14.960000' XCORNER='1.0' YCORNER='2072.0'"""
    assert out_to_check in out
