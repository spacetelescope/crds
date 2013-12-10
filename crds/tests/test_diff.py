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

>>> import test_config
>>> test_config.setup()

>>> from crds.diff import DiffScript
>>> from crds.sync import SyncScript

DiffScript doesn't do network,  create cache:

    >>> SyncScript(argv="sync.py --contexts hst.pmap").run()
    CRDS  : INFO     0 errors
    CRDS  : INFO     0 warnings
    CRDS  : INFO     0 infos

Compute diffs for two .pmap's:

    >>> case = DiffScript(argv="diff.py data/hst_0001.pmap data/hst_0002.pmap")
    >>> case.run()
    (('data/hst_0001.pmap', 'data/hst_0002.pmap'), ('acs',), 'replaced data/hst_acs_0001.imap with data/hst_acs_0002.imap')
    (('data/hst_0001.pmap', 'data/hst_0002.pmap'), ('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00'), 'replaced data/hst_acs_biasfile_0001.fits with data/hst_acs_biasfile_0002.fits')
    (('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('biasfile',), 'replaced data/hst_acs_biasfile_0001.rmap with data/hst_acs_biasfile_0002.rmap')

Compute diffs for two .imap's:

    >>> case = DiffScript(argv="diff.py data/hst_acs_0001.imap data/hst_acs_0002.imap")
    >>> case.run()
    (('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('biasfile',), 'replaced data/hst_acs_biasfile_0001.rmap with data/hst_acs_biasfile_0002.rmap')
    (('data/hst_acs_0001.imap', 'data/hst_acs_0002.imap'), ('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00'), 'replaced data/hst_acs_biasfile_0001.fits with data/hst_acs_biasfile_0002.fits')

Compute diffs for two .rmap's:

    >>> case = DiffScript(argv="diff.py data/hst_acs_biasfile_0001.rmap data/hst_acs_biasfile_0002.rmap")
    >>> case.run()
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00'), 'replaced data/hst_acs_biasfile_0001.fits with data/hst_acs_biasfile_0002.fits')

Compute diffs for two .fits's:

    >>> case = DiffScript(argv="diff.py data/hst_acs_biasfile_0001.fits data/hst_acs_biasfile_0002.fits")
    >>> case.run()  # doctest:+ELLIPSIS
    <BLANKLINE>
    ...
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
             
Compute primitive diffs for two .rmap's:

    >>> case = DiffScript(argv="diff.py data/hst_acs_biasfile_0001.rmap data/hst_acs_biasfile_0002.rmap --primitive-diffs")
    >>> case.run()
    ================================================================================
    (('data/hst_acs_biasfile_0001.rmap', 'data/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00'), 'replaced data/hst_acs_biasfile_0001.fits with data/hst_acs_biasfile_0002.fits')
    <BLANKLINE>
     fitsdiff: 3.1.0
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

Compute diffs checking for reversions: (invert file order to simulate reverse filename progression)

    >>> case = DiffScript(argv="diff.py data/hst_0002.pmap data/hst_0001.pmap --check-diffs")
    >>> case.run()
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('acs',), 'replaced data/hst_acs_0002.imap with data/hst_acs_0001.imap')
    (('data/hst_0002.pmap', 'data/hst_0001.pmap'), ('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('data/hst_acs_biasfile_0002.rmap', 'data/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00'), 'replaced data/hst_acs_biasfile_0002.fits with data/hst_acs_biasfile_0001.fits')
    (('data/hst_acs_0002.imap', 'data/hst_acs_0001.imap'), ('biasfile',), 'replaced data/hst_acs_biasfile_0002.rmap with data/hst_acs_biasfile_0001.rmap')
    CRDS  : WARNING  Reversion at ('data/hst_0001.pmap', ('acs',)) replaced 'data/hst_acs_0002.imap' with 'data/hst_acs_0001.imap'
    CRDS  : WARNING  Reversion at ('data/hst_acs_biasfile_0001.rmap', ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00')) replaced 'data/hst_acs_biasfile_0002.fits' with 'data/hst_acs_biasfile_0001.fits'
    CRDS  : WARNING  Reversion at ('data/hst_acs_0001.imap', ('biasfile',)) replaced 'data/hst_acs_biasfile_0002.rmap' with 'data/hst_acs_biasfile_0001.rmap'

CLEANUP

   >>> test_config.cleanup()

"""

def test():
    """Run module tests,  for now just doctests only."""
    import test_diff, doctest
    return doctest.testmod(test_diff)

if __name__ == "__main__":
    print(test())
