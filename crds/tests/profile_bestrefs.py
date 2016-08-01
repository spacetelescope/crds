"""This module is used to profile getrecommendations() and bestreds.BestrefsScript()."""

import cProfile, pstats, os

from crds import heavy_client, bestrefs, utils, log

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
    }

def run_and_profile(name, case):
    """Using `name` for a banner and divider,  execute code string `case` in the
    global namespace,  both evaled printing result and under the profiler.
    """
    utils.clear_function_caches()
    log.divider()
    log.divider(name + " example")
    log.divider()
    print(eval(case, locals(), globals()))
    utils.clear_function_caches()
    log.divider()
    log.divider(name + " profile")
    log.divider()
    cProfile.run(case, "profile.stats")
    stats = pstats.Stats('profile.stats')
    stats.strip_dirs()
    stats.sort_stats('cumulative')
    stats.print_stats(100)
    os.remove('profile.stats')


run_and_profile("JWST getrecommendations()", 'heavy_client.getrecommendations(JWST_HEADER, observatory="jwst", ignore_cache=False)')

run_and_profile("HST getrecommendations()", 'heavy_client.getrecommendations(HST_HEADER, observatory="hst", ignore_cache=False)')


run_and_profile("HST bestrefs file", "bestrefs.BestrefsScript('crds.bestrefs --files data/j8bt09jcq_raw.fits --log-time --stats')()")

# run_and_profile("JWST bestrefs file", "bestrefs.BestrefsScript('crds.bestrefs --files data/ --log-time --stats')()")

