"""This module is used to profile getrecommendations() and bestreds.BestrefsScript()."""
from crds.core import utils, log, heavy_client
from crds import bestrefs
from crds.tests.test_config import run_and_profile

HST_HEADER = {
    'INSTRUME' : 'ACS',
    'DETECTOR': 'SBC',
    'CCDAMP': 'N/A',
    'FILTER1' : 'PR110L',
    'FILTER2' : 'N/A',
    'OBSTYPE': 'SPECTROSCOPIC',
    'FW1OFFST' : 'N/A',
    'FW2OFFST': 'N/A',
    'FWOFFST': 'N/A',
    'DATE-OBS': '1991-01-01',
    'TIME-OBS': '00:00:00'
    }

JWST_HEADER = {
    "meta.instrument.name": "NIRISS",
    "meta.observation.date": "2012-07-25",
    "meta.observation.time": "00:00:00",
    "meta.instrument.detector" : "NIS",
    "meta.instrument.filter" : "F380M",
    "meta.subarray.name" : "FULL",
    "meta.exposture.readpatt" : "FAST",
    "meta.exposure.type" : "NIS_IMAGE",
    }

if __name__ == "__main__":
    run_and_profile("JWST getrecommendations()", 'heavy_client.getrecommendations(JWST_HEADER, observatory="jwst", ignore_cache=False)', globals())
    run_and_profile("HST getrecommendations()", 'heavy_client.getrecommendations(HST_HEADER, observatory="hst", ignore_cache=False)', globals())
    run_and_profile("HST bestrefs file", "bestrefs.BestrefsScript('crds.bestrefs --files data/j8bt09jcq_raw.fits --log-time --stats')()", globals())

# run_and_profile("JWST bestrefs file", "bestrefs.BestrefsScript('crds.bestrefs --files data/ --log-time --stats')()")
