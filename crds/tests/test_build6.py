import doctest

from crds.core import log
from crds.client import api
from crds.misc.query_affected import QueryAffectedDatasetsScript

from crds.tests import test_config

def dt_get_context_history():
    """
    Test the web service which gets the context history from the JWST server for
    ticket #360, "Verify CRDS correctly reports historical configurations".

    Note this test is dependent on the JWST operational server.   A similar test
    can be performed for any of the I&T servers by changing the URL.   In I&T,
    setup for this test will involve correctly configuring CRDS_PATH and
    CRDS_SERVER_URL to point to the I&T CRDS cache and I&T CRDS Server respectively.

    >>> old_state = test_config.setup(url='https://jwst-crds.stsci.edu')
    >>> history = api.get_context_history("jwst")

    >>> history[0]
    ('2012-09-06 00:00:00', 'jwst.pmap', 'Bootstrap mappings')

    >>> history[32]
    ('2015-11-18 12:58:13', 'jwst_0105.pmap', 'Declared various EXP_TYPE as N/A for 15 WCS types for MIRI, NIRCAM, NIRSPEC. Replacement MIRI distortion references for CRDS #238.')

    >>> test_config.cleanup(old_state)
    """

def dt_query_affected_datasets_list():
    """
    This example demos the "--list" feature of the query_affected_datasets script used
    to query the CRDS reprocessing system for datasets affected by a context transition.
    Since the context history is integral to the affected datasets computation,  the query
    tool has a mode for listing the context history to orient any human operator.

    >>> old_state = test_config.setup(url='https://jwst-crds.stsci.edu')

    >>> QueryAffectedDatasetsScript("query_affected --list -x 0 -y 10")()
    (0, '2012-09-06 00:00:00', 'jwst.pmap', 'Bootstrap mappings')
    (1, '2012-09-27 00:00:00', 'jwst_0000.pmap', 'First rules and references from jwst_gentools stub development cloning.')
    (2, '2013-04-13 00:00:00', 'jwst_0001.pmap', 'Linearity and dark files.')
    (3, '2013-07-31 00:00:00', 'jwst_0002.pmap', 'Dark and Mask files.')
    (4, '2013-09-04 00:00:00', 'jwst_0003.pmap', 'Absolute Calibration (photom) additions and replacements.')
    (5, '2013-11-25 09:00:03', 'jwst_0005.pmap', 'set by system')
    (6, '2014-03-19 10:51:19', 'jwst_0012.pmap', 'Updated for META.INSTRUMENT.TYPE switch to META.INSTRUMENT.NAME\\r\\nNew linearity files for all instruments\\r\\nNew saturation files and rmaps for all instruments')
    (7, '2014-03-26 08:49:12', 'jwst_0013.pmap', 'New context jwst_0013.pmap adds Interpixel Capacitance references for all instruments.')
    (8, '2014-07-08 16:09:39', 'jwst_0022.pmap', 'Multiple MIRI FLAT changes, new references, added SUBARRAY as matching parameter.  See diffs.')
    (9, '2014-07-18 11:34:48', 'jwst_0023.pmap', 'First MIRI PHOTOM reference for MIRIMAGE detector with real data.')
    (10, '2014-07-24 18:49:03', 'jwst_0025.pmap', 'Replaced PHOTOM references for NIRSPEC and NIRISS.')

    >>> test_config.cleanup(old_state)
    """



def main():
    """Run module tests,  for now just doctests only.

    test_config.setup() and cleanup() are done inline above because bracketing
    the tests here does not get picked up by nose test discovery.  Combining
    tests into one giant docstring works but is hard to analyze and debug when
    things go wrong.
    """
    from crds.tests import test_build6, tstmod
    return tstmod(test_build6)

if __name__ == "__main__":
    print(main())
