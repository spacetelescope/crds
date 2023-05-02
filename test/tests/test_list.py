from crds.list import ListScript
from crds.tests import test_config

"""
usage: crds list ...

usage: /Users/jmiller/work/workspace_crds/CRDS/crds/list.py
       [-h] [--references] [--mappings] [--cached-references]
       [--cached-mappings] [--cached-pickles] [--full-path]
       [--dataset-ids-for-instruments INSTRUMENTS [INSTRUMENTS ...]]
       [--dataset-headers IDS [IDS ...]] [--id-expansions-only]
       [--first-id-expansion-only] [--minimize-headers] [--json-headers]
       [--config] [--status] [--cat [FILES [FILES ...]]]
       [--keywords KEYWORDS [KEYWORDS ...]] [--add-filenames]
       [--operational-context] [--remote-context PIPELINE]
       [--resolve-contexts] [--required-parkeys]
       [--contexts [CONTEXT [CONTEXT ...]] | --range MIN:MAX | --all |
       --last-n-contexts N | --up-to-context CONTEXT | --after-context
       CONTEXT] [-v] [--verbosity VERBOSITY] [--dump-cmdline] [-R] [-I] [-V]
       [-J] [-H] [--stats] [--profile PROFILE] [--log-time] [--pdb]
       [--debug-traps]

crds.list prints out a variety of information about CRDS configuration, the
cache, reference and mapping files, default context names, and dataset headers
and ids used for CRDS reprocessing recommendations.


optional arguments:
  -h, --help            show this help message and exit
  --references          print names of reference files referred to by contexts
  --mappings            print names of mapping files referred to by contexts
  --cached-references   print the paths of all references in the local cache. very primitive.
  --cached-mappings     print the paths of all mappings in the local cache. very primitive.
  --cached-pickles      print the paths of all pickles in the local cache. very primitive.
  --full-path           print the full paths of listed files.
  --dataset-ids-for-instruments INSTRUMENTS [INSTRUMENTS ...]
                        print the dataset ids known to CRDS associated for the specified instruments.
  --dataset-headers IDS [IDS ...]
                        print matching parameters for the specified dataset ids.
  --id-expansions-only  print out only the <product>:<exposure> expansion associated with the specified --dataset-headers ids.
  --first-id-expansion-only
                        print out only the first exposure ID (header or expanded) associated with a particular product ID.
  --minimize-headers    print out only header parameters required by a particular CRDS context.
  --json-headers        print out header parameters in JSON format suited for crds.bestrefs and grepping.
  --config              print CRDS configuration information.
  --status              print brief, basic, CRDS configuration information.
  --cat [FILES [FILES ...]]
                        print the text of the specified mapping files.
  --keywords KEYWORDS [KEYWORDS ...]
                        limited list of keywords to be catted from reference headers.
  --add-filenames       prefix each line of a cat'ed file with the filename.
  --operational-context
                        print the name of the operational context on the central CRDS server.
  --remote-context PIPELINE
                        print the name of the context reported as in use by the specified pipeline.
  --resolve-contexts    print the literal names of the contexts defined by the command line context specifiers.
  --required-parkeys    print the names of the parkeys required to compute bestrefs for the specified mappings.
  --contexts [CONTEXT [CONTEXT ...]]
                        Specify a list of CRDS mappings to operate on: .pmap, .imap, or .rmap or date-based specification
  --range MIN:MAX       Operate for pipeline context ids (.pmaps) between <MIN> and <MAX>.
  --all                 Operate with respect to all known CRDS contexts.
  --last-n-contexts N   Operate with respect to the last N contexts.
  --up-to-context CONTEXT
                        Operate on all contexts up to and including the specified context.
  --after-context CONTEXT
                        Operate on all contexts after and including the specified context.
  -v, --verbose         Set log verbosity to True,  nominal debug level.
  --verbosity VERBOSITY
                        Set log verbosity to a specific level: 0..100.
  --dump-cmdline        Dump the command line parameters used to start the script to the log.
  -R, --readonly-cache  Don't modify the CRDS cache.  Not compatible with options which implicitly modify the cache.
  -I, --ignore-cache    Download required files even if they're already in the cache.
  -V, --version         Print the software version and exit.
  -J, --jwst            Force observatory to JWST for determining header conventions.
  -H, --hst             Force observatory to HST for determining header conventions.
  --stats               Track and print timing statistics.
  --profile PROFILE     Output profile stats to the specified file.
  --log-time            Add date/time to log messages.
  --pdb                 Run under pdb.
  --debug-traps         Bypass exception error message traps and re-raise exception.

    General categories of information driven by switches include:

    0. Overall CRDS configuration
    1. CRDS server file lists
    2. CRDS cache file lists and paths
    3. Cached file contents or headers
    4. CRDS reprocessing dataset ids and parameters
    5. Listing global default and installed pipeline contexts
    6. Resolving context specifiers into literal context names

    --------------------------------------------------------------------------
    0. Configuration information governing the behavior of CRDS for simple
    configurations can be dumped:

    % crds list --status
    CRDS Version = '7.0.7, bump-version, 7432326'
    CRDS_MODE = 'auto'
    CRDS_PATH = '/Users/jmiller/crds_cache_ops'
    CRDS_SERVER_URL = 'https://jwst-crds.stsci.edu'
    Effective Context = 'jwst_0204.pmap'
    Last Synced = '2016-09-20 08:00:09.115330'
    Python Executable = '/Users/jmiller/anaconda/bin/python'
    Python Version = '3.5.2.final.0'
    Readonly Cache = False

    More comprehensive configuration information is also available for advanced
    configurations:

    % crds list --config
    ... lots of info ....

    --------------------------------------------------------------------------
   1. Files known by the CRDS server to belong to specified contexts can be listed
    even if the files are not installed in a local CRDS Cache.

    The --mappings command recursively evaluates and includes all the sub-mappings,
    i.e. imaps and pmaps, of the specified contexts.

    Contexts to list can be specified in a variety of ways:

    -- To list the references contained by several contexts

    % crds list  --references --contexts hst_0001.pmap hst_0002.pmap ...
    vb41935ij_bia.fits
    vb41935kj_bia.fits
    ...

    -- To list the references in a numerical range of contexts

    % crds list --references --range 1:2 --references
    vb41935lj_bia.fits
    vb41935oj_bia.fits
    ...

    -- To list all mappings, even those not referenced by an imap or pmap

    % crds list --mappings --all
    hst.pmap
    hst_0001.pmap
    hst_0002.pmap
    hst_acs.imap
    hst_acs_0001.imap
    hst_acs_0002.imap
    hst_acs_atodtab.rmap
    ...

    --references, --mappings, or both can be listed.

    --------------------------------------------------------------------------
    2. Locally cached files (files already synced to your computer) can be listed:

    % crds list --cached-mappings --full-path
    ...

    % crds list --cached-references --full-path
    ...

    In both cases adding --full-path prints the path of the file within the CRDS cache.

    These are merely simple directory listings which ignore the context specifiers
    and can be grep'ed for finer grained answers.

    --------------------------------------------------------------------------
    3. The contents of cached mappings or references (header only) can be printed to stdout like this:

    % crds list --contexts jwst-fgs-linearity-edit jwst-nirspec-linearity-edit --cat --add-filename | grep parkey
    CRDS - INFO - Symbolic context 'jwst-fgs-linearity-edit' resolves to 'jwst_fgs_linearity_0008.rmap'
    CRDS - INFO - Symbolic context 'jwst-nirspec-linearity-edit' resolves to 'jwst_nirspec_linearity_0009.rmap'
    /cache/path/mappings/jwst/jwst_fgs_linearity_0008.rmap:     'parkey' : (('META.INSTRUMENT.DETECTOR', 'META.SUBARRAY.NAME'), ('META.OBSERVATION.DATE', 'META.OBSERVATION.TIME')),
    /cache/path/mappings/jwst/jwst_nirspec_linearity_0009.rmap:     'parkey' : (('META.INSTRUMENT.DETECTOR', 'META.SUBARRAY.NAME'), ('META.OBSERVATION.DATE', 'META.OBSERVATION.TIME')),

    this prints the contents of the specified rmaps.

    The -edit specifier above refers to mappings contained by the default starting point (.pmap) of future
    server submissions.  It tracks on-going submission work that precedes the adoption of a new context
    as the default in use by the pipeline.

    crds.list --cat can be applied to references and prints out the reference metadata that CRDS views
    abstractly as the file header.

    References need to be catted explicitly by name,  but the list can come from the --references command
    explained above:

    % crds list --cat jwst_nirspec_dark_0036.fits
    CRDS - INFO - Symbolic context 'jwst-operational' resolves to 'jwst_0167.pmap'
    ##########################################################################################
    File:  '.../references/jwst/jwst_nirspec_dark_0036.fits'
    ##########################################################################################
    {'A1_COL_C': '8.9600000e+002',
    'A1_CONF1': '2.1846000e+004',
    ...
    }

   --------------------------------------------------------------------------
   4. Information about the dataset IDs and their associated parameters used
   for CRDS reprocessing can be printed:

    % crds list --dataset-headers jcl403010 --first-id --minimize-header
    CRDS - INFO - Symbolic context 'hst-operational' resolves to 'hst_0462.pmap'
    CRDS - INFO - Dataset pars for 'JCL403010:JCL403ECQ' with respect to 'hst_0462.pmap':
    {'APERTURE': 'WFC1',
     'ATODCORR': 'OMIT',
     'BIASCORR': 'COMPLETE',
     'CCDAMP': 'ABCD',
     'CCDCHIP': '-999.0',
     'CCDGAIN': '2.0',
     'CRCORR': 'OMIT',
     'DARKCORR': 'COMPLETE',
     'DATE-OBS': '2016-02-20',
     'DETECTOR': 'WFC',
     'DQICORR': 'COMPLETE',
     'DRIZCORR': 'COMPLETE',
     'FILTER1': 'CLEAR1L',
     'FILTER2': 'F814W',
     'FLASHCUR': 'LOW',
     'FLATCORR': 'COMPLETE',
     'FLSHCORR': 'OMIT',
     'FW1OFFST': '0.0',
     'FW2OFFST': '0.0',
     'FWSOFFST': '0.0',
     'GLINCORR': 'UNDEFINED',
     'INSTRUME': 'ACS',
     'LTV1': '0.0',
     'LTV2': '0.0',
     'NAXIS1': '4144.0',
     'NAXIS2': '4136.0',
     'OBSTYPE': 'IMAGING',
     'PCTECORR': 'UNDEFINED',
     'PHOTCORR': 'COMPLETE',
     'RPTCORR': 'UNDEFINED',
     'SHADCORR': 'OMIT',
     'SHUTRPOS': 'A',
     'TIME-OBS': '17:32:29.666665',
     'XCORNER': '0.0',
     'YCORNER': '0.0',
     'dataset_id': 'JCL403010:JCL403ECQ'}

    Sometimes it's desirable to know the individual exposures CRDS associates with a product id:

    % crds list --dataset-headers jcl403010 --id-expansions-only
    CRDS - INFO - Symbolic context 'hst-operational' resolves to 'hst_0462.pmap'
    JCL403010:JCL403ECQ
    JCL403010:JCL403EEQ
    JCL403010:JCL403EGQ
    JCL403010:JCL403EIQ
    JCL403010:JCL403EKQ
    JCL403010:JCL403EMQ
    JCL403010:JCL403EOQ
    JCL403010:JCL403EQQ
    JCL403010:JCL403ESQ
    JCL403010:JCL403EUQ

    Headers available can possibly vary by CRDS context and will be dumped for
    every specified or implicit context.  Generally the default context is
    sufficient.  Often all exposures of an association have identical
    parameters but CRDS is designed so that this does not have to be the case.

    These dataset header services require setting CRDS_SERVER_URL to a valid CRDS server to
    provide a source for the headers.

   --------------------------------------------------------------------------
    5. Information about the default context can be printed.  There are two variations and a subtle distinction:

    % python m crds.list --operational-context
    jwst_0204.pmap

    lists the context which has been *commanded* as default on the CRDS server.

    While:

    % crds list --remote-context jwst-ops-pipeline
    jwst_0101.pmap

    lists the context which is *in actual use* in the associated archive pipeline as reported by
    a cache sync echo.

    During the interval between commanding a new default on the CRDS server and syncing the pipeline
    CRDS cache,  the commanded and actual pipeline contexts can differ.

   --------------------------------------------------------------------------
    6. Resolving context specifiers

    Some CRDS tools, including crds.list and crds.sync, support multiple
    mechanisms for specifying context.  The --resolve-contexts command
    interprets those specifiers into a non-recursive list of literal mapping
    names and prints them out.  --resolve-contexts differs from --mappings
    because it does not implicitly include all sub-mappings of the specified
    contexts.

    % crds list --resolve-contexts --all
    jwst.pmap
    jwst_0000.pmap
    jwst_0001.pmap
    jwst_0002.pmap
    jwst_0003.pmap
    ...

    % crds list --resolve-contexts --last 5
    jwst_0205.pmap
    jwst_0206.pmap
    jwst_0207.pmap
    jwst_0208.pmap
    jwst_0209.pmap

    % crds list --resolve-contexts  --contexts jwst-miri-dark-operational
    jwst_miri_dark_0012.rmap

    % crds list --resolve-contexts --contexts jwst-niriss-superbias-2016-01-01T00:00:00
    jwst_niriss_superbias_0005.rmap


----------
TEST CASES
----------
"""

from crds.core import log
from crds import tests
from crds.tests import test_config

from crds.diff import DiffScript

def dt_list_mappings():
    """
    >>> old_state = test_config.setup()
    >>> ListScript("crds.list --mappings --contexts hst.pmap")() # doctest: +ELLIPSIS
    hst.pmap
    hst_acs.imap
    hst_acs_atodtab.rmap
    hst_acs_biasfile.rmap
    hst_acs_bpixtab.rmap
    hst_acs_ccdtab.rmap
    hst_acs_cfltfile.rmap
    hst_acs_crrejtab.rmap
    hst_acs_d2imfile.rmap
    hst_acs_darkfile.rmap
    hst_acs_dgeofile.rmap
    hst_acs_drkcfile.rmap
    hst_acs_flshfile.rmap
    ...
    hst_wfpc2_shadfile.rmap
    hst_wfpc2_wf4tfile.rmap
    0
    >>> test_config.cleanup(old_state)
    """

def dt_list_cached_mappings():
    """
    >>> old_state = test_config.setup()
    >>> import doctest
    >>> doctest.ELLIPSIS_MARKER = '-ignore-'
    >>> ListScript("crds.list --cached-mappings --full-path")() # doctest: +ELLIPSIS
    -ignore-/mappings/hst/hst.pmap
    -ignore-/mappings/hst/hst_0001.pmap
    -ignore-/mappings/hst/hst_0002.pmap
    -ignore-
    0
    >>> doctest.ELLIPSIS_MARKER = '...'
    >>> test_config.cleanup(old_state)
    """

def dt_list_references():
    """
    >>> old_state = test_config.setup()
    >>> ListScript("crds.list --references --contexts hst.pmap")() # doctest: +ELLIPSIS
    d6n1328ou.r6h
    d6n13293u.r6h
    d6n13298u.r6h
    d6n1329fu.r6h
    d6n1329qu.r6h
    ...
    x781756sj_dkc.fits
    x781933ij_drk.fits
    x781933jj_dkc.fits
    0
    >>> test_config.cleanup(old_state)
    """

def dt_list_cached_references():
    """
    >>> import doctest
    >>> doctest.ELLIPSIS_MARKER = '-ignore-'
    >>> old_state = test_config.setup(cache=test_config.CRDS_TESTING_CACHE, observatory="hst")
    >>> ListScript("crds.list --cached-references --full-path")() # doctest: +ELLIPSIS
    -ignore-/crds-cache-test/references/hst/v8q14451j_idc.fits
    -ignore-/crds-cache-test/references/hst/z1q2219el_2zx.fits
    -ignore-/crds-cache-test/references/hst/z1r1943el_1dx.fits
    -ignore-/crds-cache-test/references/hst/z2d19237l_1dx.fits
    -ignore-/crds-cache-test/references/hst/z2d1925ql_2zx.fits
    0
    >>> test_config.cleanup(old_state)
    >>> doctest.ELLIPSIS_MARKER = '...'
    """

def dt_list_dataset_ids():
    """
    >>> old_state = test_config.setup()
    >>> ListScript("crds.list --dataset-ids wfpc2")()   # doctest: +ELLIPSIS
    U20L0U01T:U20L0U01T
    U20L0U02T:U20L0U02T
    U20L0U03T:U20L0U03T
    U21U0201T:U21U0201T
    ...
    0
    >>> test_config.cleanup(old_state)
    """

def dt_list_dataset_headers():
    """
    >>> old_state = test_config.setup()
    >>> ListScript("crds.list --dataset-headers U20L0U01T:U20L0U01T --minimize-header --contexts hst.pmap")()   # doctest: +ELLIPSIS
    Dataset pars for 'U20L0U01T:U20L0U01T' with respect to 'hst.pmap':
     {'ATODGAIN': '15.0',
     'CRDS_CTX': 'hst.pmap',
     'DATE-OBS': '1993-12-07',
     'FILTER1': '0.0',
     'FILTER2': '0.0',
     'FILTNAM1': 'UNDEFINED',
     'FILTNAM2': 'UNDEFINED',
     'IMAGETYP': 'BIAS',
     'INSTRUME': 'WFPC2',
     'LRFWAVE': '0.0',
     'MODE': 'FULL',
     'SERIALS': 'OFF',
     'SHUTTER': 'A',
     'TIME-OBS': '10:07:16.929999',
     'dataset_id': 'U20L0U01T:U20L0U01T'}
    0
    >>> test_config.cleanup(old_state)
    """

def dt_list_dataset_headers_json():
    """
    >>> old_state = test_config.setup()
    >>> import doctest
    >>> doctest.ELLIPSIS_MARKER = '-ignore-'
    >>> ListScript("crds.list --dataset-headers U20L0U01T:U20L0U01T --contexts hst.pmap --json")()   # doctest: +ELLIPSIS
    -ignore-
    0
    >>> test_config.cleanup(old_state)
    >>> doctest.ELLIPSIS_MARKER = '...'
    """

def dt_list_dataset_headers_bogus():
    """
    >>> old_state = test_config.setup()
    >>> ListScript("crds.list --dataset-headers BAR:BAR --contexts hst.pmap")()   # doctest: +ELLIPSIS
    CRDS - ERROR -  Failed fetching dataset parameters with repect to 'hst.pmap' for ['BAR:BAR'] : CRDS jsonrpc failure 'get_dataset_headers_by_id' OtherError: Can't determine instrument for dataset ...'BAR'
    1
    >>> test_config.cleanup(old_state)
    """

def dt_list_dataset_headers_id_expansions_only():
    """
    >>> old_state = test_config.setup()
    >>> ListScript("crds.list --dataset-headers I9ZF01010 --id-expansions-only --contexts hst.pmap")()   # doctest: +ELLIPSIS
    I9ZF01010:I9ZF01DZQ
    I9ZF01010:I9ZF01E0Q
    I9ZF01010:I9ZF01E1Q
    I9ZF01010:I9ZF01E3Q
    0
    >>> test_config.cleanup(old_state)
    """

def dt_list_required_parkeys_pmap():
    """
    >>> old_state = test_config.setup()
    >>> ListScript("crds.list --required-parkeys --contexts hst.pmap")() # doctest: +ELLIPSIS
    --------------------- Parkeys required for 'hst.pmap' ---------------------
    acs = ['INSTRUME', 'APERTURE', 'ATODCORR', 'BIASCORR', 'CCDAMP', 'CCDCHIP', 'CCDGAIN', 'CRCORR', 'DARKCORR', 'DATE-OBS', 'DETECTOR', 'DQICORR', 'DRIZCORR', 'FILTER1', 'FILTER2', 'FLASHCUR', 'FLATCORR', 'FLSHCORR', 'FW1OFFST', 'FW2OFFST', 'FWSOFFST', 'GLINCORR', 'LTV1', 'LTV2', 'NUMCOLS', 'NUMROWS', 'OBSTYPE', 'PCTECORR', 'PHOTCORR', 'REFTYPE', 'SHADCORR', 'SHUTRPOS', 'TIME-OBS', 'XCORNER', 'YCORNER']
    cos = ['INSTRUME', 'BADTCORR', 'BRSTCORR', 'DATE-OBS', 'DEADCORR', 'DETECTOR', 'EXPTYPE', 'FLATCORR', 'FLUXCORR', 'LIFE_ADJ', 'OBSMODE', 'OBSTYPE', 'OPT_ELEM', 'REFTYPE', 'TDSCORR', 'TIME-OBS', 'WALKCORR']
    nicmos = ['INSTRUME', 'CAMERA', 'DATE-OBS', 'FILTER', 'NREAD', 'OBSMODE', 'READOUT', 'REFTYPE', 'SAMP_SEQ', 'TIME-OBS']
    stis = ['INSTRUME', 'APERTURE', 'BINAXIS1', 'BINAXIS2', 'CCDAMP', 'CCDGAIN', 'CCDOFFST', 'CENWAVE', 'DATE-OBS', 'DETECTOR', 'OBSTYPE', 'OPT_ELEM', 'REFTYPE', 'TIME-OBS']
    wfc3 = ['INSTRUME', 'APERTURE', 'ATODCORR', 'BIASCORR', 'BINAXIS1', 'BINAXIS2', 'CCDAMP', 'CCDGAIN', 'CHINJECT', 'DARKCORR', 'DATE-OBS', 'DETECTOR', 'DQICORR', 'DRIZCORR', 'FILTER', 'FLASHCUR', 'FLATCORR', 'FLSHCORR', 'PHOTCORR', 'REFTYPE', 'SAMP_SEQ', 'SHUTRPOS', 'SUBARRAY', 'SUBTYPE', 'TIME-OBS']
    wfpc2 = ['INSTRUME', 'ATODGAIN', 'DATE-OBS', 'FILTER1', 'FILTER2', 'FILTNAM1', 'FILTNAM2', 'IMAGETYP', 'LRFWAVE', 'MODE', 'REFTYPE', 'SERIALS', 'SHUTTER', 'TIME-OBS']
    0
    >>> test_config.cleanup(old_state)
    """

def dt_list_required_parkeys_imap():
    """
    >>> old_state = test_config.setup()
    >>> ListScript("crds.list --required-parkeys --contexts hst_acs.imap")() # doctest: +ELLIPSIS
    atodtab: ['DETECTOR', 'DATE-OBS', 'TIME-OBS', 'ATODCORR']
    biasfile: ['DETECTOR', 'CCDAMP', 'CCDGAIN', 'APERTURE', 'NUMCOLS', 'NUMROWS', 'LTV1', 'LTV2', 'XCORNER', 'YCORNER', 'CCDCHIP', 'DATE-OBS', 'TIME-OBS', 'BIASCORR', 'XCORNER', 'YCORNER', 'CCDCHIP']
    bpixtab: ['DETECTOR', 'DATE-OBS', 'TIME-OBS', 'DQICORR']
    ccdtab: ['DETECTOR', 'DATE-OBS', 'TIME-OBS']
    cfltfile: ['DETECTOR', 'FILTER1', 'FILTER2', 'OBSTYPE', 'DATE-OBS', 'TIME-OBS']
    crrejtab: ['DETECTOR', 'DATE-OBS', 'TIME-OBS', 'CRCORR']
    d2imfile: ['DATE-OBS', 'TIME-OBS', 'DRIZCORR']
    darkfile: ['DETECTOR', 'CCDAMP', 'CCDGAIN', 'DATE-OBS', 'TIME-OBS', 'DARKCORR']
    dgeofile: ['DETECTOR', 'FILTER1', 'FILTER2', 'DATE-OBS', 'TIME-OBS']
    drkcfile: ['DETECTOR', 'CCDAMP', 'CCDGAIN', 'DATE-OBS', 'TIME-OBS', 'PCTECORR']
    flshfile: ['DETECTOR', 'CCDAMP', 'CCDGAIN', 'FLASHCUR', 'SHUTRPOS', 'DATE-OBS', 'TIME-OBS', 'FLSHCORR']
    idctab: ['DETECTOR', 'DATE-OBS', 'TIME-OBS']
    imphttab: ['DETECTOR', 'DATE-OBS', 'TIME-OBS', 'PHOTCORR']
    mdriztab: ['DETECTOR', 'DATE-OBS', 'TIME-OBS', 'DRIZCORR']
    mlintab: ['DETECTOR', 'DATE-OBS', 'TIME-OBS', 'GLINCORR']
    npolfile: ['DETECTOR', 'FILTER1', 'FILTER2', 'DATE-OBS', 'TIME-OBS', 'DRIZCORR']
    oscntab: ['DETECTOR', 'DATE-OBS', 'TIME-OBS']
    pctetab: ['DETECTOR', 'DATE-OBS', 'TIME-OBS', 'PCTECORR']
    pfltfile: ['DETECTOR', 'CCDAMP', 'FILTER1', 'FILTER2', 'OBSTYPE', 'FW1OFFST', 'FW2OFFST', 'FWSOFFST', 'DATE-OBS', 'TIME-OBS', 'FLATCORR']
    shadfile: ['DETECTOR', 'DATE-OBS', 'TIME-OBS', 'SHADCORR']
    spottab: ['DETECTOR', 'OBSTYPE', 'DATE-OBS', 'TIME-OBS']
    0
    >>> test_config.cleanup(old_state)
    """

def dt_list_required_parkeys_rmap():
    """
    >>> old_state = test_config.setup()
    >>> ListScript("crds.list --required-parkeys --contexts hst_acs_darkfile.rmap")() # doctest: +ELLIPSIS
    hst_acs_darkfile.rmap: ['DETECTOR', 'CCDAMP', 'CCDGAIN', 'DATE-OBS', 'TIME-OBS', 'DARKCORR']
    0
    >>> test_config.cleanup(old_state)
    """

def dt_list_resolve_contexts_range():
    """
    >>> old_state = test_config.setup()
    >>> ListScript("crds.list --resolve-contexts --range 0:5")() # doctest: +ELLIPSIS
    hst_0001.pmap
    hst_0002.pmap
    hst_0003.pmap
    hst_0004.pmap
    hst_0005.pmap
    0
    >>> test_config.cleanup(old_state)
    """

def dt_list_resolve_contexts_date():
    """
    >>> old_state = test_config.setup()
    >>> ListScript("crds.list --resolve-contexts --contexts hst-2014-11-11T00:00:00")() # doctest: +ELLIPSIS
    hst_0297.pmap
    0
    >>> test_config.cleanup(old_state)
    """

def dt_list_remote_context():
    """
    >>> old_state = test_config.setup()
    >>> ListScript("crds.list --remote-context hst-ops-pipeline")() # doctest: +ELLIPSIS
    hst_....pmap
    >>> test_config.cleanup(old_state)
    """

def dt_list_operational_context():
    """
    >>> old_state = test_config.setup()
    >>> ListScript("crds.list --operational-context")() # doctest: +ELLIPSIS
    hst_....pmap
    >>> test_config.cleanup(old_state)
    """

def dt_list_references_by_context():
    """
    >>> old_state = test_config.setup()
    >>> ListScript("crds.list --references --contexts hst-cos-deadtab-2014-11-11T00:00:00")() # doctest: +ELLIPSIS
    s7g1700gl_dead.fits
    s7g1700ql_dead.fits
    0
    >>> test_config.cleanup(old_state)
    """

def dt_list_references_by_context():
    """
    >>> old_state = test_config.setup()
    >>> ListScript("crds.list --references --contexts hst-cos-deadtab-2014-11-11T00:00:00")() # doctest: +ELLIPSIS
    s7g1700gl_dead.fits
    s7g1700ql_dead.fits
    0
    >>> test_config.cleanup(old_state)
    """

def dt_list_cat_mappings():
    """
    >>> old_state = test_config.setup()
    >>> ListScript("crds.list --cat --mappings --contexts hst-cos-deadtab-2014-11-11T00:00:00")() # doctest: +ELLIPSIS
    ################################################################################
    File: .../mappings/hst/hst_cos_deadtab_0250.rmap
    --------------------------------------------------------------------------------
    header = {
        'derived_from' : 'generated from CDBS database 2014-05-09 23:24:57.840119',
        'filekind' : 'DEADTAB',
        'instrument' : 'COS',
        'mapping' : 'REFERENCE',
        'name' : 'hst_cos_deadtab_0250.rmap',
        'observatory' : 'HST',
        'parkey' : (('DETECTOR',), ('DATE-OBS', 'TIME-OBS')),
        'reffile_format' : 'TABLE',
        'reffile_required' : 'NONE',
        'reffile_switch' : 'DEADCORR',
        'rmap_relevance' : '(DEADCORR != "OMIT")',
        'sha1sum' : 'bde314f1848b67891d6309b30eaa5c95611f86e2',
    }
    <BLANKLINE>
    selector = Match({
        ('FUV',) : UseAfter({
            '1996-10-01 00:00:00' : 's7g1700gl_dead.fits',
        }),
        ('NUV',) : UseAfter({
            '1996-10-01 00:00:00' : 's7g1700ql_dead.fits',
        }),
    })
    --------------------------------------------------------------------------------
    Catalog Info:
    ................................................................................
    {'activation_date': '2014-05-15 15:31:54',
     'aperture': 'none',
     'blacklisted': 'false',
     'change_level': 'severe',
     'comment': 'none',
     'creator_name': 'todd miller',
     'delivery_date': '2014-05-11 08:14:02',
     'derived_from': 'generated from cdbs database 2014-05-09 23:24:57.840119',
     'description': 'rebaselined hst rmaps as 250-series for opus 2014.2',
     'filekind': 'deadtab',
     'history': 'none',
     'instrument': 'cos',
     'name': 'hst_cos_deadtab_0250.rmap',
     'observatory': 'hst',
     'pedigree': '',
     'reference_file_type': '',
     'rejected': 'false',
     'replaced_by_filename': '',
     'sha1sum': '41cbdf620d41586fbc3de3e26d14d14eb42cc244',
     'size': '711',
     'state': 'operational',
     'type': 'mapping',
     'uploaded_as': 'hst_cos_deadtab_0250.rmap',
     'useafter_date': '2050-01-01 00:00:00'}

    >>> test_config.cleanup(old_state)
    """


def dt_list_status():
    """
    >>> old_state = test_config.setup()
    >>> ListScript("crds.list --status")() # doctest: +ELLIPSIS
    CRDS Summary = '...'
    CRDS Version = '...'
    CRDS_MODE = 'auto'
    CRDS_PATH = '...'
    CRDS_SERVER_URL = 'https://....stsci.edu'
    Cache Locking = 'enabled, multiprocessing'
    Effective Context = 'hst_....pmap'
    Last Synced = '...'
    Python Executable = '...'
    Python Version = '...'
    Readonly Cache = False
    0
    >>> test_config.cleanup(old_state)
    """

def dt_list_config():
    """
    >>> old_state = test_config.setup()
    >>> ListScript("crds.list --config")() # doctest: +ELLIPSIS
    CRDS Environment
    ...
    CRDS Client Config
    ...
    CRDS Actual Paths
    ...
    CRDS Server Info
    ...
    Calibration Environment
    ...
    Python Environment
    ...
    0
    >>> test_config.cleanup(old_state)
    """

def main():
    """Run module tests,  for now just doctests only.

    test_config.setup() and cleanup() are done inline above because bracketing
    the tests here does not get picked up by nose test discovery.  Combining
    tests into one giant docstring works but is hard to analyze and debug when
    things go wrong.
    """
    from crds.tests import test_list, tstmod
    return tstmod(test_list)

if __name__ == "__main__":
    print(main())
