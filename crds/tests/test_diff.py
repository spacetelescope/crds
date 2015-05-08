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
    
    % python -m crds.diff hst_0001.pmap  hst_0005.pmap  --mapping-text-diffs --primitive-diffs
    
Will recursively produce logical, textual, and FITS diffs for all changes between the two contexts.
    
    NOTE: mapping logical differences (the default) to not compare CRDS mapping headers.
    

----------
TEST CASES
----------
"""

from crds import log
from crds.diff import DiffScript
from crds.tests import test_config

def test_diff_pmap_diffs():
    """
    Compute diffs for two .pmap's:

    >>> case = DiffScript("crds.diff data/hst_0001.pmap data/hst_0002.pmap")
    >>> case.run()
    (('data/hst_0001.pmap', 'data/hst_0002.pmap'), ('acs',), 'replaced data/hst_acs_0001.imap with data/hst_acs_0002.imap')
    (('data/hst_0001.pmap', 'data/hst_0002.pmap'), ('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('biasfile',), 'replaced data/hst_acs_biasfile_0001.rmap with data/hst_acs_biasfile_0002.rmap')
    (('data/hst_0001.pmap', 'data/hst_0002.pmap'), ('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00'), 'replaced data/hst_acs_biasfile_0001.fits with data/hst_acs_biasfile_0002.fits')
    (('data/hst_0001.pmap', 'data/hst_0002.pmap'), ('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'deleted Match rule for m991609tj_bia.fits')
    (('data/hst_0001.pmap', 'data/hst_0002.pmap'), ('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'deleted Match rule for q9e1206kj_bia.fits')
    (('data/hst_0001.pmap', 'data/hst_0002.pmap'), ('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:42:53'), 'deleted Match rule for q9e12071j_bia.fits')
    (('data/hst_0001.pmap', 'data/hst_0002.pmap'), ('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'added Match rule for m991609tj_bia.fits')
    (('data/hst_0001.pmap', 'data/hst_0002.pmap'), ('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'added Match rule for q9e1206kj_bia.fits')
    (('data/hst_0001.pmap', 'data/hst_0002.pmap'), ('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:43:54'), 'added Match rule for q9e12071j_bia.fits')
    0
    """

def test_diff_imap_diffs():
    """
    Compute diffs for two .imap's:

    >>> case = DiffScript("crds.diff data/hst_acs_0001.imap data/hst_acs_0002.imap")
    >>> case.run()
    (('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('biasfile',), 'replaced data/hst_acs_biasfile_0001.rmap with data/hst_acs_biasfile_0002.rmap')
    (('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00'), 'replaced data/hst_acs_biasfile_0001.fits with data/hst_acs_biasfile_0002.fits')
    (('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'deleted Match rule for m991609tj_bia.fits')
    (('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'deleted Match rule for q9e1206kj_bia.fits')
    (('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:42:53'), 'deleted Match rule for q9e12071j_bia.fits')
    (('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'added Match rule for m991609tj_bia.fits')
    (('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'added Match rule for q9e1206kj_bia.fits')
    (('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:43:54'), 'added Match rule for q9e12071j_bia.fits')
    0
    """

def test_diff_rmap_diffs():
    """
    Compute diffs for two .rmap's:

    >>> case = DiffScript("crds.diff data/hst_acs_biasfile_0001.rmap data/hst_acs_biasfile_0002.rmap --include-header-diffs")
    >>> case.run()
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), 'deleted header \\'rmap_relevance\\' = \\'((DETECTOR != "SBC") and (BIASCORR != "OMIT"))\\'')
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), "header added 'extra_info' = 'some other piece of information.'")
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), "header replaced 'extra_keys' = ('XCORNER', 'YCORNER', 'CCDCHIP') with ('ZCORNER', 'YCORNER', 'CCDCHIP')")
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), "header replaced 'reffile_required' = 'yes' with 'no'")
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), "header replaced 'sha1sum' = '90a43965be5d044f1e8fcf5f141b3f64b763ca89' with '32df61d8f1cd4d398d84d05e1706b5565712d87d'")
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00'), 'replaced data/hst_acs_biasfile_0001.fits with data/hst_acs_biasfile_0002.fits')
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'deleted Match rule for m991609tj_bia.fits')
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'deleted Match rule for q9e1206kj_bia.fits')
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:42:53'), 'deleted Match rule for q9e12071j_bia.fits')
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'added Match rule for m991609tj_bia.fits')
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'added Match rule for q9e1206kj_bia.fits')
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:43:54'), 'added Match rule for q9e12071j_bia.fits')
    0
    """

def test_diff_fits_diff():
    """
    Compute diffs for two .fits's:

    >>> case = DiffScript("crds.diff data/hst_acs_biasfile_0001.fits data/hst_acs_biasfile_0002.fits")
    >>> import doctest
    >>> doctest.ELLIPSIS_MARKER = '-etc-'
    >>> case.run()  # doctest:+ELLIPSIS
    -etc-
     a: data/hst_acs_biasfile_0001.fits
     b: data/hst_acs_biasfile_0002.fits
     Maximum number of different data values to be reported: 10
     Data comparison level: 0.0
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
    0
    """

def test_diff_rmap_primitive_diffs():
    """
    Compute primitive diffs for two .rmap's:

    >>> case = DiffScript("crds.diff data/hst_acs_biasfile_0001.rmap data/hst_acs_biasfile_0002.rmap --primitive-diffs")
    >>> import doctest
    >>> doctest.ELLIPSIS_MARKER = '-etc-'
    >>> case.run()  #doctest:+ELLIPSIS
    ================================================================================
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00'), 'replaced data/hst_acs_biasfile_0001.fits with data/hst_acs_biasfile_0002.fits')
    -etc-
     a: data/hst_acs_biasfile_0001.fits
     b: data/hst_acs_biasfile_0002.fits
     Maximum number of different data values to be reported: 10
     Data comparison level: 0.0
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
    0
    """

def test_diff_file_reversions():
    """
    Compute diffs checking for reversions: (invert file order to simulate reverse filename progression)

    >>> old_state = test_config.setup()
    >>> case = DiffScript("crds.diff data/hst_0002.pmap data/hst_0001.pmap --check-diffs")
    >>> case.run()
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('acs',), 'replaced data/hst_acs_0002.imap with data/hst_acs_0001.imap')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('biasfile',), 'replaced data/hst_acs_biasfile_0002.rmap with data/hst_acs_biasfile_0001.rmap')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('data/hst_acs_biasfile_0002.rmap', 'data/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00'), 'replaced data/hst_acs_biasfile_0002.fits with data/hst_acs_biasfile_0001.fits')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('data/hst_acs_biasfile_0002.rmap', 'data/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'added Match rule for m991609tj_bia.fits')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('data/hst_acs_biasfile_0002.rmap', 'data/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'added Match rule for q9e1206kj_bia.fits')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('data/hst_acs_biasfile_0002.rmap', 'data/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:42:53'), 'added Match rule for q9e12071j_bia.fits')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('data/hst_acs_biasfile_0002.rmap', 'data/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'deleted Match rule for m991609tj_bia.fits')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('data/hst_acs_biasfile_0002.rmap', 'data/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'deleted Match rule for q9e1206kj_bia.fits')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('data/hst_acs_biasfile_0002.rmap', 'data/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:43:54'), 'deleted Match rule for q9e12071j_bia.fits')
    CRDS  : WARNING  Rule change at ('data/hst_acs_biasfile_0001.rmap', ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00')) added Match rule for 'm991609tj_bia.fits'
    CRDS  : WARNING  Rule change at ('data/hst_acs_biasfile_0001.rmap', ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35')) added Match rule for 'q9e1206kj_bia.fits'
    CRDS  : WARNING  Rule change at ('data/hst_acs_biasfile_0001.rmap', ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:42:53')) added Match rule for 'q9e12071j_bia.fits'
    CRDS  : WARNING  Rule change at ('data/hst_acs_biasfile_0001.rmap', ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00')) deleted Match rule for 'm991609tj_bia.fits'
    CRDS  : WARNING  Rule change at ('data/hst_acs_biasfile_0001.rmap', ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35')) deleted Match rule for 'q9e1206kj_bia.fits'
    CRDS  : WARNING  Rule change at ('data/hst_acs_biasfile_0001.rmap', ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:43:54')) deleted Match rule for 'q9e12071j_bia.fits'
    CRDS  : WARNING  Reversion at ('data/hst_0001.pmap', ('acs',)) replaced 'data/hst_acs_0002.imap' with 'data/hst_acs_0001.imap'
    CRDS  : WARNING  Reversion at ('data/hst_acs_0001.imap', ('biasfile',)) replaced 'data/hst_acs_biasfile_0002.rmap' with 'data/hst_acs_biasfile_0001.rmap'
    CRDS  : WARNING  Reversion at ('data/hst_acs_biasfile_0001.rmap', ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00')) replaced 'data/hst_acs_biasfile_0002.fits' with 'data/hst_acs_biasfile_0001.fits'
    0
    """

def test_diff_row_change():
    """
    Row change
    >>> case = DiffScript("crds.diff data/test-source.fits data/test-change-row1-valueLeft.fits")
    >>> import doctest
    >>> doctest.ELLIPSIS_MARKER = '-etc-'
    >>> case.run()  #doctest:+ELLIPSIS
    -etc-
     a: data/test-source.fits
     b: data/test-change-row1-valueLeft.fits
     Maximum number of different data values to be reported: 10
     Data comparison level: 0.0
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
             'yes', 'yes', 2988, -2779.0352, 'coquille'
            -'yes', 'no', 5748, 6357.9727, 'ferly'
            +'yes', 'no', -1, 6357.9727, 'ferly'
             'yes', 'maybe', 9735, -9132.5322, 'misreliance'
             'no', 'yes', 425, -2689.2646, 'ogeed'
             'no', 'no', 8989, 9870.0254, 'readmittance'
    <BLANKLINE>
    0
    """
    
def test_diff_print_affected_modes():
    """
    >>> DiffScript("crds.diff data/hst_cos_deadtab.rmap data/hst_cos_deadtab_9998.rmap --print-affected-modes")()
    INSTRUMENT='COS' REFTYPE='DEADTAB' DETECTOR='FUV' DIFF_COUNT='1'
    INSTRUMENT='COS' REFTYPE='DEADTAB' DETECTOR='NUV' DIFF_COUNT='1'
    0
    """

def test_diff_print_all_new_files():
    """
    >>> log.set_test_mode()
    >>> DiffScript("crds.diff data/hst.pmap data/hst_0002.pmap --print-all-new-files --sync-files")()
    CRDS  : INFO     0 errors
    CRDS  : INFO     0 warnings
    CRDS  : INFO     0 infos
    hst_0001.pmap  
    hst_0002.pmap  
    hst_stis_0001.imap stis 
    hst_stis_biasfile_0001.rmap stis biasfile
    hst_stis_darkfile_0001.rmap stis darkfile
    hst_wfc3_0001.imap wfc3 
    hst_wfc3_darkfile_0001.rmap wfc3 darkfile
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
    x9618368i_drk.fits wfc3 darkfile
    x9618369i_drk.fits wfc3 darkfile
    x961836ai_drk.fits wfc3 darkfile
    x961836bi_drk.fits wfc3 darkfile
    0
    """

def test_diff_print_new_files():
    """
    >>> DiffScript("crds.diff data/hst_0001.pmap data/hst_0002.pmap --print-new-files")()
    hst_0002.pmap
    hst_acs_0002.imap
    hst_acs_biasfile_0002.rmap
    data/hst_acs_biasfile_0002.fits
    0
    """

def test_diff_print_affected_types():
    """
    >>> DiffScript("crds.diff data/hst_cos_deadtab.rmap data/hst_cos_deadtab_9998.rmap --print-affected-types")()
    cos        deadtab   
    0
    """

def test_diff_print_affected_instruments():
    """
    >>> DiffScript("crds.diff data/hst_cos_deadtab.rmap data/hst_cos_deadtab_9998.rmap --print-affected-instruments")()
    cos
    0
    """


def test():
    """Run module tests,  for now just doctests only."""
    old_state = test_config.setup()
    import test_diff, doctest
    doctest.ELLIPSIS_MARKER = '-etc-'
    results = doctest.testmod(test_diff, optionflags=doctest.ELLIPSIS)
    test_config.cleanup(old_state)
    return results

if __name__ == "__main__":
    print(test())
