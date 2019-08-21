import doctest

"""
usage: /Users/jmiller/work/normal/lib/python2.7/site-packages/crds/diff.py
       [-h] [-P] [-T] [-K] [-v] [--verbosity VERBOSITY] [-V] [-J] [-H]
       [--profile PROFILE] [--pdb]
       old_file new_file

Difference CRDS mapping or reference files.

positional arguments:
  old_file              Prior file of difference.
  new_file              New file of difference.

optional arguments:
  -h, --help            show this help message and exit
  -P, --primitive-diffs
                        Fitsdiff replaced reference files when diffing mappings.
  -T, --mapping-text-diffs
                        In addition to CRDS mapping logical differences,  run UNIX context diff for mappings.
  -K, --check-diffs     Issue warnings about new rules, deletions, or reversions.
  -v, --verbose         Set log verbosity to True,  nominal debug level.
  --verbosity VERBOSITY
                        Set log verbosity to a specific level: 0..100.
  -V, --version         Print the software version and exit.
  -J, --jwst            Force observatory to JWST for determining header conventions.
  -H, --hst             Force observatory to HST for determining header conventions.
  --profile PROFILE     Output profile stats to the specified file.
  --pdb                 Run under pdb.

Reference files are nominally differenced using FITS-diff or diff.

Mapping files are differenced using CRDS machinery to recursively compare too mappings and
their sub-mappings.

Differencing two mappings will find all the logical differences between the two contexts
and any nested mappings.

By specifying --mapping-text-diffs,  UNIX diff will be run on mapping files in addition to
CRDS logical diffs.

By specifying --primitive-diffs,  FITS diff will be run on all references which are replaced
in the logical differences between two mappings.

For example:

    % crds diff hst_0001.pmap  hst_0005.pmap  --mapping-text-diffs --primitive-diffs

Will recursively produce logical, textual, and FITS diffs for all changes between the two contexts.

    NOTE: mapping logical differences (the default) to not compare CRDS mapping headers.

----------
TEST CASES
----------
"""

from crds.core import log
from crds import tests
from crds.tests import test_config

from crds.diff import DiffScript

def dt_diff_pmap_diffs():
    """
    Compute diffs for two .pmap's:

    >>> old_state = test_config.setup()
    >>> DiffScript("crds.diff data/hst_0001.pmap data/hst_0002.pmap")()
    (('data/hst_0001.pmap', 'data/hst_0002.pmap'), ('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00'), 'replaced data/hst_acs_biasfile_0001.fits with data/hst_acs_biasfile_0002.fits')
    (('data/hst_0001.pmap', 'data/hst_0002.pmap'), ('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'deleted Match rule for m991609tj_bia.fits')
    (('data/hst_0001.pmap', 'data/hst_0002.pmap'), ('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'deleted Match rule for q9e1206kj_bia.fits')
    (('data/hst_0001.pmap', 'data/hst_0002.pmap'), ('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:42:53'), 'deleted Match rule for q9e12071j_bia.fits')
    (('data/hst_0001.pmap', 'data/hst_0002.pmap'), ('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'added Match rule for m991609tj_bia.fits')
    (('data/hst_0001.pmap', 'data/hst_0002.pmap'), ('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'added Match rule for q9e1206kj_bia.fits')
    (('data/hst_0001.pmap', 'data/hst_0002.pmap'), ('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:43:54'), 'added Match rule for q9e12071j_bia.fits')
    (('data/hst_0001.pmap', 'data/hst_0002.pmap'), ('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('biasfile',), 'replaced data/hst_acs_biasfile_0001.rmap with data/hst_acs_biasfile_0002.rmap')
    (('data/hst_0001.pmap', 'data/hst_0002.pmap'), ('acs',), 'replaced data/hst_acs_0001.imap with data/hst_acs_0002.imap')
    1
    >>> test_config.cleanup(old_state)
    """

def dt_diff_imap_diffs():
    """
    Compute diffs for two .imap's:

    >>> old_state = test_config.setup()
    >>> DiffScript("crds.diff data/hst_acs_0001.imap data/hst_acs_0002.imap")()
    (('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00'), 'replaced data/hst_acs_biasfile_0001.fits with data/hst_acs_biasfile_0002.fits')
    (('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'deleted Match rule for m991609tj_bia.fits')
    (('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'deleted Match rule for q9e1206kj_bia.fits')
    (('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:42:53'), 'deleted Match rule for q9e12071j_bia.fits')
    (('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'added Match rule for m991609tj_bia.fits')
    (('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'added Match rule for q9e1206kj_bia.fits')
    (('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:43:54'), 'added Match rule for q9e12071j_bia.fits')
    (('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('biasfile',), 'replaced data/hst_acs_biasfile_0001.rmap with data/hst_acs_biasfile_0002.rmap')
    1
    >>> test_config.cleanup(old_state)
    """

def dt_diff_rmap_diffs():
    """
    Compute diffs for two .rmap's:

    >>> old_state = test_config.setup()
    >>> DiffScript("crds.diff data/hst_acs_biasfile_0001.rmap data/hst_acs_biasfile_0002.rmap --include-header-diffs")()
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00'), 'replaced data/hst_acs_biasfile_0001.fits with data/hst_acs_biasfile_0002.fits')
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'deleted Match rule for m991609tj_bia.fits')
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'deleted Match rule for q9e1206kj_bia.fits')
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:42:53'), 'deleted Match rule for q9e12071j_bia.fits')
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'added Match rule for m991609tj_bia.fits')
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'added Match rule for q9e1206kj_bia.fits')
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:43:54'), 'added Match rule for q9e12071j_bia.fits')
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), 'deleted header \\'rmap_relevance\\' = \\'((DETECTOR != "SBC") and (BIASCORR != "OMIT"))\\'')
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), "header added 'extra_info' = 'some other piece of information.'")
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), "header replaced 'extra_keys' = ('XCORNER', 'YCORNER', 'CCDCHIP') with ('ZCORNER', 'YCORNER', 'CCDCHIP')")
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), "header replaced 'reffile_required' = 'yes' with 'no'")
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), "header replaced 'sha1sum' = '90a43965be5d044f1e8fcf5f141b3f64b763ca89' with '32df61d8f1cd4d398d84d05e1706b5565712d87d'")
    1
    >>> test_config.cleanup(old_state)
    """

def dt_diff_fits_diff():
    """
    Compute diffs for two .fits's:

    >>> old_state = test_config.setup()

    >>> DiffScript("crds.diff data/hst_acs_biasfile_0001.fits data/hst_acs_biasfile_0002.fits")() # doctest: +ELLIPSIS
    <BLANKLINE>
     fitsdiff: ...
     a: data/hst_acs_biasfile_0001.fits
     b: data/hst_acs_biasfile_0002.fits
     Maximum number of different data values to be reported: 10
     Relative tolerance: 0.0, Absolute tolerance: 0.0
    <BLANKLINE>
    Primary HDU:
    <BLANKLINE>
       Headers contain differences:
         Extra keyword 'ADD_1'  in a: 'added to hst_acs_biasfile_0001.fits'
         Extra keyword 'ADD_2'  in b: 'added to hst_acs_biasfile_0002.fits'
         Keyword DIFF_12  has different values:
            a> value in 1
             ?          ^
            b> value in 2
             ?          ^
    <BLANKLINE>
    <BLANKLINE>
    1

    >>> test_config.cleanup(old_state)
    """

def dt_diff_asdf():
    """
    Compute diffs for two .asdf's:

    >>> old_state = test_config.setup()

    >>> DiffScript("crds.diff data/jwst_nircam_specwcs_0010.asdf data/jwst_nircam_specwcs_0011.asdf")() # doctest: +ELLIPSIS
            ndarrays differ by contents
            ndarrays differ by contents
            ndarrays differ by contents
            ndarrays differ by contents
    tree:
      history:
        -
          description:
    >       Created from NIRCAM_modA_R.conf
    <       Created from NIRCAM_modA_C.conf
          time:
    >       2017-09-08 16:57:27.004949
    <       2017-09-08 16:57:26.927451
            ndarrays differ by contents
            ndarrays differ by contents
            ndarrays differ by contents
            ndarrays differ by contents
      meta:
        date:
    >     2017-09-08T12:57:27.006
    <     2017-09-08T12:57:26.928
        description:
    >     GRISMR dispersion models
    <     GRISMC dispersion models
        filename:
    >     NIRCAM_modA_R.asdf
    <     NIRCAM_modA_C.asdf
        instrument:
          pupil:
    >       GRISMR
    <       GRISMC
    1

     >>> DiffScript("crds.diff data/jwst_nircam_specwcs_0010.asdf data/jwst_nircam_specwcs_0010.asdf")() # doctest: +ELLIPSIS
     0

    >>> test_config.cleanup(old_state)
    """

def dt_diff_rmap_primitive_diffs():
    """
    Compute primitive diffs for two .rmap's:

    >>> old_state = test_config.setup()

    >>> DiffScript("crds.diff data/hst_acs_biasfile_0001.rmap data/hst_acs_biasfile_0002.rmap --primitive-diffs")()  #doctest: +ELLIPSIS
    ================================================================================
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00'), 'replaced data/hst_acs_biasfile_0001.fits with data/hst_acs_biasfile_0002.fits')
    <BLANKLINE>
     fitsdiff: ...
     a: data/hst_acs_biasfile_0001.fits
     b: data/hst_acs_biasfile_0002.fits
     Maximum number of different data values to be reported: 10
     Relative tolerance: 0.0, Absolute tolerance: 0.0
    <BLANKLINE>
    Primary HDU:
    <BLANKLINE>
       Headers contain differences:
         Extra keyword 'ADD_1'  in a: 'added to hst_acs_biasfile_0001.fits'
         Extra keyword 'ADD_2'  in b: 'added to hst_acs_biasfile_0002.fits'
         Keyword DIFF_12  has different values:
            a> value in 1
             ?          ^
            b> value in 2
             ?          ^
    <BLANKLINE>
    <BLANKLINE>
    ================================================================================
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'deleted Match rule for m991609tj_bia.fits')
    ================================================================================
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'deleted Match rule for q9e1206kj_bia.fits')
    ================================================================================
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:42:53'), 'deleted Match rule for q9e12071j_bia.fits')
    ================================================================================
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'added Match rule for m991609tj_bia.fits')
    ================================================================================
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'added Match rule for q9e1206kj_bia.fits')
    ================================================================================
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:43:54'), 'added Match rule for q9e12071j_bia.fits')
    1

    >>> test_config.cleanup(old_state)
    """

def dt_diff_file_reversions():
    """
    Compute diffs checking for reversions: (invert file order to simulate reverse filename progression)

    >>> old_state = test_config.setup()

    >>> DiffScript("crds.diff data/hst_0002.pmap data/hst_0001.pmap --check-diffs")()
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('data/hst_acs_biasfile_0002.rmap', 'data/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00'), 'replaced data/hst_acs_biasfile_0002.fits with data/hst_acs_biasfile_0001.fits')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('data/hst_acs_biasfile_0002.rmap', 'data/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'added Match rule for m991609tj_bia.fits')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('data/hst_acs_biasfile_0002.rmap', 'data/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'added Match rule for q9e1206kj_bia.fits')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('data/hst_acs_biasfile_0002.rmap', 'data/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:42:53'), 'added Match rule for q9e12071j_bia.fits')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('data/hst_acs_biasfile_0002.rmap', 'data/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'deleted Match rule for m991609tj_bia.fits')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('data/hst_acs_biasfile_0002.rmap', 'data/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'deleted Match rule for q9e1206kj_bia.fits')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('data/hst_acs_biasfile_0002.rmap', 'data/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:43:54'), 'deleted Match rule for q9e12071j_bia.fits')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('biasfile',), 'replaced data/hst_acs_biasfile_0002.rmap with data/hst_acs_biasfile_0001.rmap')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('acs',), 'replaced data/hst_acs_0002.imap with data/hst_acs_0001.imap')
    CRDS - WARNING - Rule change at ('data/hst_acs_biasfile_0001.rmap', ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00')) added Match rule for 'm991609tj_bia.fits'
    CRDS - WARNING - Rule change at ('data/hst_acs_biasfile_0001.rmap', ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35')) added Match rule for 'q9e1206kj_bia.fits'
    CRDS - WARNING - Rule change at ('data/hst_acs_biasfile_0001.rmap', ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:42:53')) added Match rule for 'q9e12071j_bia.fits'
    CRDS - WARNING - Rule change at ('data/hst_acs_biasfile_0001.rmap', ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00')) deleted Match rule for 'm991609tj_bia.fits'
    CRDS - WARNING - Rule change at ('data/hst_acs_biasfile_0001.rmap', ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35')) deleted Match rule for 'q9e1206kj_bia.fits'
    CRDS - WARNING - Rule change at ('data/hst_acs_biasfile_0001.rmap', ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:43:54')) deleted Match rule for 'q9e12071j_bia.fits'
    CRDS - WARNING - Reversion at ('data/hst_acs_biasfile_0001.rmap', ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00')) replaced 'data/hst_acs_biasfile_0002.fits' with 'data/hst_acs_biasfile_0001.fits'
    CRDS - WARNING - Reversion at ('data/hst_acs_0001.imap', ('biasfile',)) replaced 'data/hst_acs_biasfile_0002.rmap' with 'data/hst_acs_biasfile_0001.rmap'
    CRDS - WARNING - Reversion at ('data/hst_0001.pmap', ('acs',)) replaced 'data/hst_acs_0002.imap' with 'data/hst_acs_0001.imap'
    2

    >>> test_config.cleanup(old_state)
    """

def dt_diff_row_change():
    """
    Row change

    >>> old_state = test_config.setup()

    >>> DiffScript("crds.diff data/test-source.fits data/test-change-row1-valueLeft.fits")()  #doctest: +ELLIPSIS
    <BLANKLINE>
     fitsdiff: ...
     a: data/test-source.fits
     b: data/test-change-row1-valueLeft.fits
     Maximum number of different data values to be reported: 10
     Relative tolerance: 0.0, Absolute tolerance: 0.0
    <BLANKLINE>
    Extension HDU 1:
    <BLANKLINE>
       Data contains differences:
         Column valueLeft data differs in row 1:
            a> 5748
            b> -1
         1 different table data element(s) found (2.22% different).
    <BLANKLINE>
     Row differences for HDU extension #1
    <BLANKLINE>
        Summary:
            a rows 1-1 differ from b rows 1-1
    <BLANKLINE>
        Row difference, unified diff format:
            --- Table A
    <BLANKLINE>
            +++ Table B
    <BLANKLINE>
            @@ -1,5 +1,5 @@
    <BLANKLINE>
             'yes', 'yes', 2988, -2779.03..., 'coquille'
            -'yes', 'no', 5748, 6357.97..., 'ferly'
            +'yes', 'no', -1, 6357.97..., 'ferly'
             'yes', 'maybe', 9735, -9132.53..., 'misreliance'
             'no', 'yes', 425, -2689.26..., 'ogeed'
             'no', 'no', 8989, 9870.02..., 'readmittance'
    <BLANKLINE>
    1

    >>> test_config.cleanup(old_state)
    """

def dt_diff_rmap_primitive_diffs():
    """
    Compute primitive diffs for two .rmap's:

    >>> old_state = test_config.setup()

    >>> DiffScript("crds.diff data/hst_acs_biasfile_0001.rmap data/hst_acs_biasfile_0002.rmap --primitive-diffs")()  #doctest: +ELLIPSIS
    ================================================================================
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00'), 'replaced data/hst_acs_biasfile_0001.fits with data/hst_acs_biasfile_0002.fits')
    <BLANKLINE>
     fitsdiff: ...
     a: data/hst_acs_biasfile_0001.fits
     b: data/hst_acs_biasfile_0002.fits
     Maximum number of different data values to be reported: 10
     Relative tolerance: 0.0, Absolute tolerance: 0.0
    <BLANKLINE>
    Primary HDU:
    <BLANKLINE>
       Headers contain differences:
         Extra keyword 'ADD_1'  in a: 'added to hst_acs_biasfile_0001.fits'
         Extra keyword 'ADD_2'  in b: 'added to hst_acs_biasfile_0002.fits'
         Keyword DIFF_12  has different values:
            a> value in 1
             ?          ^
            b> value in 2
             ?          ^
    <BLANKLINE>
    <BLANKLINE>
    ================================================================================
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'deleted Match rule for m991609tj_bia.fits')
    ================================================================================
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'deleted Match rule for q9e1206kj_bia.fits')
    ================================================================================
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:42:53'), 'deleted Match rule for q9e12071j_bia.fits')
    ================================================================================
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'added Match rule for m991609tj_bia.fits')
    ================================================================================
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'added Match rule for q9e1206kj_bia.fits')
    ================================================================================
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:43:54'), 'added Match rule for q9e12071j_bia.fits')
    1

    >>> test_config.cleanup(old_state)
    """

def dt_diff_file_reversions():
    """
    Compute diffs checking for reversions: (invert file order to simulate reverse filename progression)

    >>> old_state = test_config.setup()

    >>> DiffScript("crds.diff data/hst_0002.pmap data/hst_0001.pmap --check-diffs")()
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('data/hst_acs_biasfile_0002.rmap', 'data/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00'), 'replaced data/hst_acs_biasfile_0002.fits with data/hst_acs_biasfile_0001.fits')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('data/hst_acs_biasfile_0002.rmap', 'data/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'added Match rule for m991609tj_bia.fits')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('data/hst_acs_biasfile_0002.rmap', 'data/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'added Match rule for q9e1206kj_bia.fits')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('data/hst_acs_biasfile_0002.rmap', 'data/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:42:53'), 'added Match rule for q9e12071j_bia.fits')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('data/hst_acs_biasfile_0002.rmap', 'data/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'deleted Match rule for m991609tj_bia.fits')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('data/hst_acs_biasfile_0002.rmap', 'data/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'deleted Match rule for q9e1206kj_bia.fits')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('data/hst_acs_biasfile_0002.rmap', 'data/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:43:54'), 'deleted Match rule for q9e12071j_bia.fits')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('biasfile',), 'replaced data/hst_acs_biasfile_0002.rmap with data/hst_acs_biasfile_0001.rmap')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('acs',), 'replaced data/hst_acs_0002.imap with data/hst_acs_0001.imap')
    CRDS - WARNING - Rule change at ('data/hst_acs_biasfile_0001.rmap', ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00')) added Match rule for 'm991609tj_bia.fits'
    CRDS - WARNING - Rule change at ('data/hst_acs_biasfile_0001.rmap', ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35')) added Match rule for 'q9e1206kj_bia.fits'
    CRDS - WARNING - Rule change at ('data/hst_acs_biasfile_0001.rmap', ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:42:53')) added Match rule for 'q9e12071j_bia.fits'
    CRDS - WARNING - Rule change at ('data/hst_acs_biasfile_0001.rmap', ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00')) deleted Match rule for 'm991609tj_bia.fits'
    CRDS - WARNING - Rule change at ('data/hst_acs_biasfile_0001.rmap', ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35')) deleted Match rule for 'q9e1206kj_bia.fits'
    CRDS - WARNING - Rule change at ('data/hst_acs_biasfile_0001.rmap', ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:43:54')) deleted Match rule for 'q9e12071j_bia.fits'
    CRDS - WARNING - Reversion at ('data/hst_acs_biasfile_0001.rmap', ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00')) replaced 'data/hst_acs_biasfile_0002.fits' with 'data/hst_acs_biasfile_0001.fits'
    CRDS - WARNING - Reversion at ('data/hst_acs_0001.imap', ('biasfile',)) replaced 'data/hst_acs_biasfile_0002.rmap' with 'data/hst_acs_biasfile_0001.rmap'
    CRDS - WARNING - Reversion at ('data/hst_0001.pmap', ('acs',)) replaced 'data/hst_acs_0002.imap' with 'data/hst_acs_0001.imap'
    2
    >>> test_config.cleanup(old_state)
    """

def dt_diff_row_change():
    """
    Row change

    >>> old_state = test_config.setup()

    >>> DiffScript("crds.diff data/test-source.fits data/test-change-row1-valueLeft.fits")()  #doctest: +ELLIPSIS
    <BLANKLINE>
     fitsdiff: ...
     a: data/test-source.fits
     b: data/test-change-row1-valueLeft.fits
     Maximum number of different data values to be reported: 10
     Relative tolerance: 0.0, Absolute tolerance: 0.0
    <BLANKLINE>
    Extension HDU 1:
    <BLANKLINE>
       Data contains differences:
         Column valueLeft data differs in row 1:
            a> 5748
            b> -1
         1 different table data element(s) found (2.22% different).
    <BLANKLINE>
     Row differences for HDU extension #1
    <BLANKLINE>
        Summary:
            a rows 1-1 differ from b rows 1-1
    <BLANKLINE>
        Row difference, unified diff format:
            --- Table A
    <BLANKLINE>
            +++ Table B
    <BLANKLINE>
            @@ -1,5 +1,5 @@
    <BLANKLINE>
             'yes', 'yes', 2988, -2779.03..., 'coquille'
            -'yes', 'no', 5748, 6357.97..., 'ferly'
            +'yes', 'no', -1, 6357.97..., 'ferly'
             'yes', 'maybe', 9735, -9132.53..., 'misreliance'
             'no', 'yes', 425, -2689.26..., 'ogeed'
             'no', 'no', 8989, 9870.02..., 'readmittance'
    <BLANKLINE>
    1
    >>> test_config.cleanup(old_state)
    """

def dt_diff_print_affected_modes():
    """
    >>> old_state = test_config.setup()
    >>> DiffScript("crds.diff data/hst_cos_deadtab.rmap data/hst_cos_deadtab_9998.rmap --print-affected-modes")()
    INSTRUMENT='COS' REFTYPE='DEADTAB' DETECTOR='FUV' DIFF_COUNT='1'
    INSTRUMENT='COS' REFTYPE='DEADTAB' DETECTOR='NUV' DIFF_COUNT='1'
    1
    >>> test_config.cleanup(old_state)
    """

def dt_diff_print_all_new_files():
    """
    >>> old_state = test_config.setup(cache=test_config.CRDS_TESTING_CACHE)
    >>> DiffScript("crds.diff data/hst_0001.pmap data/hst_0008.pmap --print-all-new-files --sync-files --include-header-diffs --hide-boring")()
    CRDS - INFO - 0 errors
    CRDS - INFO - 0 warnings
    CRDS - INFO - 0 infos
    hst_0002.pmap
    hst_0003.pmap
    hst_0004.pmap
    hst_0005.pmap
    hst_0006.pmap
    hst_0007.pmap
    hst_0008.pmap
    hst_acs.imap acs
    hst_acs_0002.imap acs
    hst_acs_biasfile.rmap acs biasfile
    hst_acs_biasfile_0002.rmap acs biasfile
    hst_cos_0001.imap cos
    hst_cos_0002.imap cos
    hst_cos_flatfile_0002.rmap cos flatfile
    hst_cos_flatfile_0003.rmap cos flatfile
    hst_cos_fluxtab.rmap cos fluxtab
    hst_cos_xtractab.rmap cos xtractab
    hst_stis_0001.imap stis
    hst_stis_0002.imap stis
    hst_stis_biasfile_0001.rmap stis biasfile
    hst_stis_biasfile_0002.rmap stis biasfile
    hst_stis_darkfile_0001.rmap stis darkfile
    hst_stis_darkfile_0002.rmap stis darkfile
    hst_wfc3_0001.imap wfc3
    hst_wfc3_0002.imap wfc3
    hst_wfc3_0003.imap wfc3
    hst_wfc3_darkfile_0001.rmap wfc3 darkfile
    hst_wfc3_darkfile_0004.rmap wfc3 darkfile
    hst_wfc3_flshfile_0001.rmap wfc3 flshfile
    data/hst_acs_biasfile_0002.fits acs biasfile
    s7g17006l_1dx.fits cos xtractab
    s7g17007l_1dx.fits cos xtractab
    s7g1700kl_phot.fits cos fluxtab
    s7g1700nl_1dx.fits cos xtractab
    s7g1700ol_1dx.fits cos xtractab
    s7g1700tl_flat.fits cos flatfile
    s7g17011l_phot.fits cos fluxtab
    t9h1220sl_phot.fits cos fluxtab
    u8k1433ql_phot.fits cos fluxtab
    w5g1439sl_1dx.fits cos xtractab
    x1v17414l_1dx.fits cos xtractab
    x1v17416l_phot.fits cos fluxtab
    x5v1944hl_flat.fits cos flatfile
    x6q17586l_1dx.fits cos xtractab
    x6q17587l_phot.fits cos fluxtab
    x7h1457mi_drk.fits wfc3 darkfile
    x7h1457ni_drk.fits wfc3 darkfile
    x7h1457oi_drk.fits wfc3 darkfile
    x7h1457pi_drk.fits wfc3 darkfile
    x7v2004ri_drk.fits wfc3 darkfile
    x7v2004si_drk.fits wfc3 darkfile
    x7v2004ti_drk.fits wfc3 darkfile
    x8c16266o_bia.fits stis biasfile
    x8c16267o_bia.fits stis biasfile
    x8c16268o_bia.fits stis biasfile
    x8c16269o_bia.fits stis biasfile
    x8c1626ao_bia.fits stis biasfile
    x8c1626bo_bia.fits stis biasfile
    x8c1626co_drk.fits stis darkfile
    x8c1626do_drk.fits stis darkfile
    x8c1626eo_drk.fits stis darkfile
    x8c1626fo_drk.fits stis darkfile
    x8k1551hi_drk.fits wfc3 darkfile
    x8k1551ii_drk.fits wfc3 darkfile
    x8k1551ji_drk.fits wfc3 darkfile
    x8k1551ki_drk.fits wfc3 darkfile
    x8k1551li_drk.fits wfc3 darkfile
    x9618368i_drk.fits wfc3 darkfile
    x9618369i_drk.fits wfc3 darkfile
    x961836ai_drk.fits wfc3 darkfile
    x961836bi_drk.fits wfc3 darkfile
    x9c1801qo_bia.fits stis biasfile
    x9c1801ro_bia.fits stis biasfile
    x9c1801so_bia.fits stis biasfile
    x9c1801to_bia.fits stis biasfile
    x9c18020o_bia.fits stis biasfile
    x9c18021o_drk.fits stis darkfile
    x9c18022o_drk.fits stis darkfile
    x9c18023o_drk.fits stis darkfile
    1

    >>> test_config.cleanup(old_state)
    """

def dt_diff_print_new_files():
    """
    >>> old_state = test_config.setup()
    >>> DiffScript("crds.diff data/hst_0001.pmap data/hst_0002.pmap --print-new-files")()
    hst_0002.pmap
    hst_acs_0002.imap
    hst_acs_biasfile_0002.rmap
    data/hst_acs_biasfile_0002.fits
    1
    >>> test_config.cleanup(old_state)
    """

def dt_diff_print_affected_types():
    """
    >>> old_state = test_config.setup()
    >>> DiffScript("crds.diff data/hst_cos_deadtab.rmap data/hst_cos_deadtab_9998.rmap --print-affected-types")()
    cos        deadtab
    1
    >>> test_config.cleanup(old_state)
    """

def dt_diff_print_affected_instruments():
    """
    >>> old_state = test_config.setup()
    >>> DiffScript("crds.diff data/hst_cos_deadtab.rmap data/hst_cos_deadtab_9998.rmap --print-affected-instruments")()
    cos
    1
    >>> test_config.cleanup(old_state)
    """

def dt_diff_recurse_added_deleted_na():
    """
    For this test,  checking recursive terminal adds/deletes and N/A + OMIT at all levels:

    Changed hst_wfpc2.imap to N/A
    Replaced hst_cos.imap with data/hst_cos.imap results in recursive COS changes
    Deleted hst_cos_fluxtab.rmap,  results in deleted terminals, rmap
    Added hst_cos_twozxtab_0262.rmap,  results in added terminals, rmap
    Added COS TRACETAB as N/A
    Replaced COS XTRACTAB with OMIT
    Changed two COS FLATFILE references to OMIT and N/A

    >>> old_state = test_config.setup()
    >>> DiffScript("crds.diff crds://hst.pmap data/hst.pmap --recurse-added-deleted")()  # doctest: +ELLIPSIS
    (('.../mappings/hst/hst.pmap', 'data/hst.pmap'), ('hst_cos.imap',), 'data/hst_cos_twozxtab_0262.rmap', ('FUV', 'SPECTROSCOPIC', '3.0'), ('2009-05-11', '00:00:00'), 'added terminal z2d1925ql_2zx.fits')
    (('.../mappings/hst/hst.pmap', 'data/hst.pmap'), ('hst_cos.imap',), 'hst_cos_fluxtab.rmap', ('FUV', 'SPECTROSCOPIC'), ('1996-10-01', '00:00:00'), 'deleted terminal s7g1700kl_phot.fits')
    (('.../mappings/hst/hst.pmap', 'data/hst.pmap'), ('hst_cos.imap',), 'hst_cos_fluxtab.rmap', ('FUV', 'SPECTROSCOPIC'), ('2009-05-11', '00:00:00'), 'deleted terminal u8k1433ql_phot.fits')
    (('.../mappings/hst/hst.pmap', 'data/hst.pmap'), ('hst_cos.imap',), 'hst_cos_fluxtab.rmap', ('FUV', 'SPECTROSCOPIC'), ('2009-05-11', '00:00:01'), 'deleted terminal x1v17416l_phot.fits')
    (('.../mappings/hst/hst.pmap', 'data/hst.pmap'), ('hst_cos.imap',), 'hst_cos_fluxtab.rmap', ('FUV', 'SPECTROSCOPIC'), ('2009-05-11', '00:00:02'), 'deleted terminal x6q17587l_phot.fits')
    (('.../mappings/hst/hst.pmap', 'data/hst.pmap'), ('hst_cos.imap',), 'hst_cos_fluxtab.rmap', ('NUV', 'SPECTROSCOPIC'), ('1996-10-01', '00:00:00'), 'deleted terminal s7g17011l_phot.fits')
    (('.../mappings/hst/hst.pmap', 'data/hst.pmap'), ('hst_cos.imap',), 'hst_cos_fluxtab.rmap', ('NUV', 'SPECTROSCOPIC'), ('2009-05-11', '00:00:00'), 'deleted terminal t9h1220sl_phot.fits')
    (('.../mappings/hst/hst.pmap', 'data/hst.pmap'), ('hst_cos.imap',), 'hst_cos_xtractab.rmap', ('FUV', 'SPECTROSCOPIC', '-1|1'), ('2009-05-11', '00:00:01'), 'deleted terminal x1v17414l_1dx.fits')
    (('.../mappings/hst/hst.pmap', 'data/hst.pmap'), ('hst_cos.imap',), 'hst_cos_xtractab.rmap', ('FUV', 'SPECTROSCOPIC', '-2147483648'), ('1996-10-01', '00:00:00'), 'deleted terminal s7g17006l_1dx.fits')
    (('.../mappings/hst/hst.pmap', 'data/hst.pmap'), ('hst_cos.imap',), 'hst_cos_xtractab.rmap', ('FUV', 'SPECTROSCOPIC', '-2147483648'), ('2006-10-01', '00:00:00'), 'deleted terminal s7g17007l_1dx.fits')
    (('.../mappings/hst/hst.pmap', 'data/hst.pmap'), ('hst_cos.imap',), 'hst_cos_xtractab.rmap', ('FUV', 'SPECTROSCOPIC', '2'), ('2009-05-11', '00:00:02'), 'deleted terminal x6q17586l_1dx.fits')
    (('.../mappings/hst/hst.pmap', 'data/hst.pmap'), ('hst_cos.imap',), 'hst_cos_xtractab.rmap', ('NUV', 'SPECTROSCOPIC', '-1|1'), ('2009-05-11', '00:00:00'), 'deleted terminal w5g1439sl_1dx.fits')
    (('.../mappings/hst/hst.pmap', 'data/hst.pmap'), ('hst_cos.imap',), 'hst_cos_xtractab.rmap', ('NUV', 'SPECTROSCOPIC', '-2147483648'), ('1996-10-01', '00:00:00'), 'deleted terminal s7g1700nl_1dx.fits')
    (('.../mappings/hst/hst.pmap', 'data/hst.pmap'), ('hst_cos.imap',), 'hst_cos_xtractab.rmap', ('NUV', 'SPECTROSCOPIC', '-2147483648'), ('2006-10-01', '00:00:00'), 'deleted terminal s7g1700ol_1dx.fits')
    (('.../mappings/hst/hst.pmap', 'data/hst.pmap'), ('hst_cos.imap', 'data/hst_cos.imap'), ('hst_cos_flatfile.rmap', 'data/hst_cos_flatfile.rmap'), ('FUV', 'G130M|G140L|G160M'), ('1996-10-01', '00:00:00'), 'replaced n9n20182l_flat.fits with OMIT')
    (('.../mappings/hst/hst.pmap', 'data/hst.pmap'), ('hst_cos.imap', 'data/hst_cos.imap'), ('hst_cos_flatfile.rmap', 'data/hst_cos_flatfile.rmap'), ('FUV', 'G160M'), ('1996-10-01', '00:00:00'), 'deleted Match rule for v4s17227l_flat.fits')
    (('.../mappings/hst/hst.pmap', 'data/hst.pmap'), ('hst_cos.imap', 'data/hst_cos.imap'), ('hst_cos_flatfile.rmap', 'data/hst_cos_flatfile.rmap'), ('NUV', 'G160M'), ('1996-10-01', '00:00:00'), 'added Match rule for v4s17227l_flat.fits')
    (('.../mappings/hst/hst.pmap', 'data/hst.pmap'), ('hst_cos.imap', 'data/hst_cos.imap'), ('hst_cos_flatfile.rmap', 'data/hst_cos_flatfile.rmap'), ('NUV', 'G185M|G225M|G230L|G285M|MIRRORA|MIRRORB'), ('1996-10-01', '00:00:00'), 'replaced s7g1700tl_flat.fits with N/A')
    (('.../mappings/hst/hst.pmap', 'data/hst.pmap'), ('hst_cos.imap', 'data/hst_cos.imap'), ('flatfile',), 'replaced hst_cos_flatfile.rmap with data/hst_cos_flatfile.rmap')
    (('.../mappings/hst/hst.pmap', 'data/hst.pmap'), ('hst_cos.imap', 'data/hst_cos.imap'), ('fluxtab',), 'deleted hst_cos_fluxtab.rmap')
    (('.../mappings/hst/hst.pmap', 'data/hst.pmap'), ('hst_cos.imap', 'data/hst_cos.imap'), ('tracetab',), 'added N/A')
    (('.../mappings/hst/hst.pmap', 'data/hst.pmap'), ('hst_cos.imap', 'data/hst_cos.imap'), ('twozxtab',), 'added data/hst_cos_twozxtab_0262.rmap')
    (('.../mappings/hst/hst.pmap', 'data/hst.pmap'), ('hst_cos.imap', 'data/hst_cos.imap'), ('xtractab',), 'replaced hst_cos_xtractab.rmap with OMIT')
    (('.../mappings/hst/hst.pmap', 'data/hst.pmap'), ('cos',), 'replaced hst_cos.imap with data/hst_cos.imap')
    1
    >>> test_config.cleanup(old_state)
    """

def main():
    """Run module tests,  for now just doctests only.

    test_config.setup() and cleanup() are done inline above because bracketing
    the tests here does not get picked up by nose test discovery.  Combining
    tests into one giant docstring works but is hard to analyze and debug when
    things go wrong.
    """
    from crds.tests import test_diff, tstmod
    return tstmod(test_diff)

if __name__ == "__main__":
    print(main())
