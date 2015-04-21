"""
CRDS can designate files as scientifically invalid which is reflected in the catalog
on a the CRDS server and also recorded in the configuration info and as a bad files list
which are written down in the "config" directory.

A key aspect of bad files management is the location and contents of the cache config
directory.  The current HST cache in trunk/crds/cache has a config area and 4 bad files.

>>> import crds
>>> from crds import utils, log, client

>>> import os
>>> os.environ["CRDS_PATH"] = "/grp/crds/cache"
>>> os.environ["CRDS_SERVER_URL"] = "https://hst-crds-dev.stsci.edu"
>>> client.set_crds_server("https://hst-crds-dev.stsci.edu")
>>> utils.clear_function_caches()
>>> log.set_test_mode()
>>> os.chdir(os.path.dirname(os.path.abspath(__file__)))

Here I contrived a header which will select one of the current 4 bad files from an old
context which still assigned it:

>>> header = {
...   'INSTRUME' : 'ACS',
...   'REFTYPE' : 'PFLTFILE',
...   'DETECTOR': 'SBC',
...   'CCDAMP': 'N/A',
...   'FILTER1' : 'PR110L',
...   'FILTER2' : 'N/A',
...   'OBSTYPE': 'SPECTROSCOPIC',
...   'FW1OFFST' : 'N/A',
...   'FW2OFFST': 'N/A',
...   'FWOFFST': 'N/A',
...   'DATE-OBS': '1991-01-01',
...   'TIME-OBS': '00:00:00'
... }

The default handling when a bad reference file is assigned is to raise an exception:

>>> from crds import config
>>> config.ALLOW_BAD_RULES.reset()
>>> config.ALLOW_BAD_REFERENCES.reset()

>>> crds.getreferences(header, observatory='hst', context='hst_0282.pmap', reftypes=['pfltfile'])
Traceback (most recent call last):
    ...
CrdsBadReferenceError: Recommended reference 'l2d0959cj_pfl.fits' of type 'pfltfile' is designated scientifically invalid.
<BLANKLINE>

A secondary behaviour is to permit use of bad references with a warning:

>>> config.ALLOW_BAD_RULES.set("1")
>>> config.ALLOW_BAD_REFERENCES.set("1")

>>> crds.getreferences(header, observatory='hst', context='hst_0282.pmap', reftypes=['pfltfile'])
CRDS  : WARNING  Recommended reference 'l2d0959cj_pfl.fits' of type 'pfltfile' is designated scientifically invalid.
<BLANKLINE>
{'pfltfile': '/grp/crds/cache/references/hst/l2d0959cj_pfl.fits'}


When run in 'fast' mode as is done for the calls from crds.bestrefs,  no exception or warning is possible:

>>> crds.getreferences(header, observatory='hst', context='hst_0282.pmap', reftypes=['pfltfile'], fast=True)
{'pfltfile': '/grp/crds/cache/references/hst/l2d0959cj_pfl.fits'}


The crds.bestrefs program handles bad files differently because it frequently operates on
multiple contexts at the same time,  and recommending bad files under the old context is OK.

>>> config.ALLOW_BAD_RULES.reset()
>>> config.ALLOW_BAD_REFERENCES.reset()

By default,  in crds.bestrefs use of a bad reference is an error:

>>> from crds.bestrefs import BestrefsScript

>>> BestrefsScript("crds.bestrefs --new-context hst_0282.pmap --files data/j8btxxx_raw_bad.fits")()
CRDS  : INFO     No comparison context or source comparison requested.
CRDS  : INFO     No file header updates requested;  dry run.
CRDS  : INFO     ===> Processing data/j8btxxx_raw_bad.fits
CRDS  : ERROR    instrument='ACS' type='PFLTFILE' data='data/j8btxxx_raw_bad.fits' ::  File 'L2D0959CJ_PFL.FITS' is bad. Use is not recommended,  results may not be scientifically valid.
CRDS  : INFO     1 errors
CRDS  : INFO     0 warnings
CRDS  : INFO     3 infos
1

As a backward compatibility measure,  the --bad-files-are-errors switch is still accepted but is a tautology:

>>> BestrefsScript("crds.bestrefs --new-context hst_0282.pmap --files data/j8btxxx_raw_bad.fits --bad-files-are-errors")()
CRDS  : INFO     No comparison context or source comparison requested.
CRDS  : INFO     No file header updates requested;  dry run.
CRDS  : INFO     ===> Processing data/j8btxxx_raw_bad.fits
CRDS  : ERROR    instrument='ACS' type='PFLTFILE' data='data/j8btxxx_raw_bad.fits' ::  File 'L2D0959CJ_PFL.FITS' is bad. Use is not recommended,  results may not be scientifically valid.
CRDS  : INFO     1 errors
CRDS  : INFO     0 warnings
CRDS  : INFO     3 infos
1

Using bad references with crds.bestrefs can be allowed:

>>> BestrefsScript("crds.bestrefs --new-context hst_0282.pmap --files data/j8btxxx_raw_bad.fits --allow-bad-references")()
CRDS  : INFO     No comparison context or source comparison requested.
CRDS  : INFO     No file header updates requested;  dry run.
CRDS  : INFO     ===> Processing data/j8btxxx_raw_bad.fits
CRDS  : WARNING  For data/j8btxxx_raw_bad.fits ACS pfltfile File 'L2D0959CJ_PFL.FITS' is bad. Use is not recommended,  results may not be scientifically valid.
CRDS  : INFO     0 errors
CRDS  : INFO     1 warnings
CRDS  : INFO     3 infos
0

Do some setup to switch to a JWST serverless mode.

>>> utils.clear_function_caches()
>>> os.environ["CRDS_PATH"] = "/grp/crds/cache"
>>> os.environ["CRDS_SERVER_URL"] = "https://jwst-serverless-mode.stsci.edu"
>>> client.set_crds_server("https://jwst-serverless-mode.stsci.edu")
>>> old_server_url = os.environ.pop("CRDS_SERVER_URL", None)

There is also a check for use of bad rules. JWST has a few,  including jwst_0017.pmap by "inheritance"
since it includes some bad rules.

>>> header = {
...   "meta.instrument.name": "NIRISS",
...   "meta.observation.date": "2012-07-25T00:00:00",
...   "meta.instrument.detector" : "NIRISS",
...   "meta.instrument.filter" : "CLEAR",
...   "meta.subarray.name" : "FULL",
... }

>>> config.ALLOW_BAD_RULES.reset()
>>> config.ALLOW_BAD_REFERENCES.reset()
>>> utils.clear_function_caches()

>>> crds.getreferences(header, observatory='jwst', context='jwst_0017.pmap', reftypes=["flat"])
Traceback (most recent call last):
       ...
CrdsBadRulesError: Final context 'jwst_0017.pmap' is marked as scientifically invalid based on: ['jwst_miri_flat_0003.rmap']
<BLANKLINE>

Similarly,  the use of bad rules can be permitted:

>>> config.ALLOW_BAD_RULES.set("1")
>>> utils.clear_function_caches()

>>> crds.getreferences(header, observatory='jwst', context='jwst_0017.pmap', reftypes=["flat"])
CRDS  : WARNING  Final context 'jwst_0017.pmap' is marked as scientifically invalid based on: ['jwst_miri_flat_0003.rmap']
<BLANKLINE>
{'flat': '/grp/crds/cache/references/jwst/jwst_niriss_flat_0000.fits'}

Here try bad rules for a JWST dataset:

>>> utils.clear_function_caches()
>>> config.ALLOW_BAD_RULES.set("0")

>>> script = BestrefsScript("crds.bestrefs --jwst --new-context jwst_0017.pmap --files data/jw_nrcb1_uncal_sloper_image.fits --types gain")
>>> script()
CRDS  : ERROR    instrument='ALL' type='ALL' data='ALL' ::  New-context = 'jwst_0017.pmap' is bad or contains bad rules.  Use is not recommended,  results may not be scientifically valid.
CRDS  : INFO     No comparison context or source comparison requested.
CRDS  : INFO     No file header updates requested;  dry run.
CRDS  : INFO     ===> Processing data/jw_nrcb1_uncal_sloper_image.fits
CRDS  : ERROR    Failed processing 'data/jw_nrcb1_uncal_sloper_image.fits' : Failed computing bestrefs for data 'data/jw_nrcb1_uncal_sloper_image.fits' with respect to 'jwst_0017.pmap' : Final context 'jwst_0017.pmap' is marked as scientifically invalid based on: ['jwst_miri_flat_0003.rmap']
<BLANKLINE>
CRDS  : INFO     2 errors
CRDS  : INFO     0 warnings
CRDS  : INFO     3 infos
2

>>> os.environ["CRDS_SERVER_URL"] = old_server_url

"""

def test():
    """Run module tests,  for now just doctests only."""
    import doctest
    from crds.tests import test_bad_files
    return doctest.testmod(test_bad_files)

if __name__ == "__main__":
    print(test())
