from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import doctest

"""
"""

from crds import log, tests, client
from crds.query_affected import QueryAffectedDatasetsScript

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
    >>> history = client.get_context_history("jwst")

    >>> history[0]
    ('2012-09-06 00:00:00', 'jwst.pmap', 'Bootstrap mappings')

    >>> history[32]
    ('2015-11-18 12:58:13', 'jwst_0105.pmap', 'Declared various EXP_TYPE as N/A for 15 WCS types for MIRI, NIRCAM, NIRSPEC. Replacement MIRI distortion references for ticket #238.')

    >>> test_config.cleanup(old_state)
    """

def dt_query_affected_datasets_list():
    """
    This example demos the "--list" feature of the query_affected_datasets script used
    to query the CRDS reprocessing system for datasets affected by a context transition.
    Since the context history is integral to the affected datasets computation,  the query
    tool has a mode for listing the context history to orient any human operator.

    >>> old_state = test_config.setup(url='https://jwst-crds.stsci.edu')
    
    >>> QueryAffectedDatasetsScript("query_affected --list")()  # doctest: +ELLIPSIS
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
    (11, '2014-09-25 18:30:27', 'jwst_0034.pmap', 'Build-3 References')
    (12, '2014-11-25 10:51:09', 'jwst_0036.pmap', 'FGS DETECTOR value switch from FGS1/FGS2 to GUIDER1/GUIDER2.\\r\\n\\r\\nAdded rmap_relevance expressions for MIRI and NIRSPEC WCS types to generate N/A for unsupported modes instead of raising exceptions which crashed reference prefetch.')
    (13, '2015-01-12 14:23:12', 'jwst_0039.pmap', 'Jira tickets JP-16, 17, 19, 20, 25, 30.  Generally drop FILTER from several MIRI types and add SUBARRAY and SUBARRAY=N/A for existing references except MIRI DARK.  Added new MIRI DARK references explicitly covering SUBARRAY modes,  removed most old DARKs.')
    (14, '2015-02-17 11:17:39', 'jwst_0043.pmap', 'Added NIRISS THROUGHPUT references for AMI modes F277W, F380M, F430M, F480M.   Build-4 first draft context.')
    (15, '2015-04-13 08:10:26', 'jwst_0053.pmap', 'Level-2a files from the MIRI IDT CDP-3 delivery from November, 2014.\\r\\nAdded MIRI references from 03-29-2015, new FLAT cases, replacement PHOTOM, FRINGE, STRAYMASK files.\\r\\nChanged DETECTOR=NIRISS to DETECTOR=NIS.   Added READPATT as MIRI READNOISE matching parameter.\\r\\nModified MIRI SUBARRAY handling to use GENERIC, FULL, and specific SUBARRAY values.\\r\\nModified MIRI FLAT to consistently use ANY and to remove obsolete references 0029 and 0030.')
    (16, '2015-05-05 08:33:44', 'jwst_0059.pmap', 'Added SUPERBIAS type support and initial stub references for FGS, NIRISS, NIRCAM, NIRSPEC.')
    (17, '2015-06-28 19:39:54', 'jwst_0061.pmap', 'Changes to designate some WCS types as N/A,  see context differences for more information.')
    (18, '2015-07-15 10:50:58', 'jwst_0063.pmap', 'Updated context to latest prefetch N/A related tweaks.')
    (19, '2015-08-10 10:02:17', 'jwst_0074.pmap', 'Removed FILTER as matching parameter from SATURATION, READNOISE, MASK, LINEARITY, GAIN, and DARK for all instruments.   First suite of real references for NIRISS, minus ILLUM FLAT. bad pixel mask, bias, gain, pixel flat, ipc, linearity, photometric calibration, pixel area, read noise, saturation. Omitted dark since submitted earlier out of sequence, identical, already jwst_niriss_dark_0005.fits.   First suite of real references for NIRISS, minus ILLUM FLAT. bad pixel mask, bias, gain, pixel flat, ipc, linearity, photometric calibration, pixel area, read noise, saturation.')
    (20, '2015-09-11 09:51:40', 'jwst_0079.pmap', 'Added PIXEL AREA rmaps and references for MIRI, NIRCAM, NIRSPEC.  Augmented AREA rmap for NIRISS.')
    (21, '2015-09-16 09:18:20', 'jwst_0080.pmap', 'Added  DETECTOR=MIRFULONG  BAND=N/A  REFERENCE=N/A for MIRI STRAYMASK')
    (22, '2015-09-30 16:17:55', 'jwst_0081.pmap', 'Added jwst_miri_regions_0006.fits back to rules,  MIRIFUSHORT SHORT case accidentally deleted during parameter schema change.')
    (23, '2015-10-02 11:28:26', 'jwst_0082.pmap', 'NIRSpec flat-field reference files from the instrument team to support the Build 5 pipeline.')
    (24, '2015-10-21 17:04:45', 'jwst_0084.pmap', 'First EXTRACT1D references for MIRI, NIRISS, NIRSPEC.')
    (25, '2015-10-30 11:38:16', 'jwst_0095.pmap', 'First round addition of ASDF WCS references and EXTRACT1D files.')
    (26, '2015-10-30 14:46:35', 'jwst_0096.pmap', 'Manual PMAP update for preceding WCS IMAP manual changes to declare types N/A.')
    (27, '2015-10-30 14:48:14', 'jwst_0097.pmap', 'Manual PMAP update for preceding WCS IMAP manual changes to declare types N/A.')
    (28, '2015-10-31 07:50:49', 'jwst_0098.pmap', 'Explicitly declared some EXP_TYPE values as N/A for some WCS types of all instruments except FGS.')
    (29, '2015-10-31 11:01:45', 'jwst_0099.pmap', 'Corrected WCS rmaps for parameter value typos detected by certify')
    (30, '2015-10-31 17:41:40', 'jwst_0100.pmap', 'Defined V2V3 is N/A for NIRSPEC.')
    (31, '2015-11-04 14:02:24', 'jwst_0101.pmap', 'Updated operational context for NIRCAM WAVELENGTHRANGE.')
    (32, '2015-11-18 12:58:13', 'jwst_0105.pmap', 'Declared various EXP_TYPE as N/A for 15 WCS types for MIRI, NIRCAM, NIRSPEC. Replacement MIRI distortion references for ticket #238.')
    ...

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
