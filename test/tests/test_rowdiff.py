"""
usage: /Users/eisenham/Documents/ssbdev/crds/crds/rowdiff.py
       [-h] [--ignore-fields IGNORE_FIELDS] [--fields FIELDS]
       [--mode-fields MODE_FIELDS] [-v] [--verbosity VERBOSITY] [-V] [-J] [-H]
       [--stats] [--profile PROFILE] [--pdb]
       tableA tableB

Perform FITS table difference by rows

positional arguments:
  tableA                First table to compare
  tableB                Second table to compare

optional arguments:
  -h, --help            show this help message and exit
  --ignore-fields IGNORE_FIELDS
                        List of fields to ignore
  --fields FIELDS       List of fields to compare
  --mode-fields MODE_FIELDS
                        List of fields to do a mode compare
  -v, --verbose         Set log verbosity to True,  nominal debug level.
  --verbosity VERBOSITY
                        Set log verbosity to a specific level: 0..100.
  -V, --version         Print the software version and exit.
  -J, --jwst            Force observatory to JWST for determining header conventions.
  -H, --hst             Force observatory to HST for determining header conventions.
  --stats               Track and print timing statistics.
  --profile PROFILE     Output profile stats to the specified file.
  --pdb                 Run under pdb.

Perform FITS table difference by rows

    Input:
      fits_a, fits_b: Paths or HDUList objects of the
                      two FITS files to compare.
      fields: List of fields to compare on.
      ignore-fields: List of fields to ignore.
      mode-fields: List of fields that define modes to compare

    Note: The parameters 'fields' and 'ignore-fields' are mutually exclusive.
          An error will be raised if both are specified.

    Output:
      object variables:
          diffs: tuple of the differences for each table extension found.
                 This is either None for no differences, or is again a
                 tuple consisting of:
                     - If mode-fields is specified, the tuple is described by
                       modediff
                     - Otherwise the tuple is described by rowdiff
      stdout: Human readable report.

----------
TEST CASES
----------

>>> from crds.tests import test_config
>>> old_state = test_config.setup()

>>> from crds.rowdiff import RowDiffScript

Only should work with Table extensions
    >>> case = RowDiffScript(argv="rowdiff.py data/hst_acs_biasfile_0001.fits data/hst_acs_biasfile_0002.fits")
    >>> case.run()
    <BLANKLINE>

Basic functionality: No differences
    >>> case = RowDiffScript(argv="rowdiff.py data/test-source.fits data/test-source.fits")
    >>> case.run()
        HDU extension #1 contains no differences

Row change
    >>> case = RowDiffScript(argv="rowdiff.py data/test-source.fits data/test-change-row1-valueLeft.fits")
    >>> case.run() # doctest: +ELLIPSIS
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

Row removal
    >>> case = RowDiffScript(argv="rowdiff.py data/test-source.fits data/test-single-modes.fits")
    >>> case.run() # doctest: +ELLIPSIS
    Row differences for HDU extension #1
    <BLANKLINE>
        Summary:
            Remove from a rows 1-3
            Remove from a rows 5-7
    <BLANKLINE>
        Row difference, unified diff format:
            --- Table A
    <BLANKLINE>
            +++ Table B
    <BLANKLINE>
            @@ -1,9 +1,3 @@
    <BLANKLINE>
             'yes', 'yes', 2988, -2779.03..., 'coquille'
            -'yes', 'no', 5748, 6357.97..., 'ferly'
            -'yes', 'maybe', 9735, -9132.5..., 'misreliance'
            -'no', 'yes', 425, -2689.26..., 'ogeed'
             'no', 'no', 8989, 9870.025..., 'readmittance'
            -'no', 'maybe', 3537, -8615.03..., 'anacatadidymus'
            -'maybe', 'yes', 1763, -2442.96..., 'monochromat'
            -'maybe', 'no', 8023, 4665.56..., 'ranarium'
             'maybe', 'maybe', 7347, 1705.58..., 'Dode'
    <BLANKLINE>

Row addition
    >>> case = RowDiffScript(argv="rowdiff.py data/test-single-modes.fits data/test-source.fits")
    >>> case.run() # doctest: +ELLIPSIS
    Row differences for HDU extension #1
    <BLANKLINE>
        Summary:
            Add to b rows 1-3
            Add to b rows 5-7
    <BLANKLINE>
        Row difference, unified diff format:
            --- Table A
    <BLANKLINE>
            +++ Table B
    <BLANKLINE>
            @@ -1,3 +1,9 @@
    <BLANKLINE>
             'yes', 'yes', 2988, -2779.03..., 'coquille'
            +'yes', 'no', 5748, 6357.97..., 'ferly'
            +'yes', 'maybe', 9735, -9132.53..., 'misreliance'
            +'no', 'yes', 425, -2689.26..., 'ogeed'
             'no', 'no', 8989, 9870.02..., 'readmittance'
            +'no', 'maybe', 3537, -8615.03..., 'anacatadidymus'
            +'maybe', 'yes', 1763, -2442.96..., 'monochromat'
            +'maybe', 'no', 8023, 4665.56..., 'ranarium'
             'maybe', 'maybe', 7347, 1705.58..., 'Dode'
    <BLANKLINE>

Test of switch ignore-fields
    >>> case = RowDiffScript(argv="rowdiff.py --ignore-fields=valueleft data/test-source.fits data/test-change-row1-valueLeft.fits")
    >>> case.run()
        HDU extension #1 contains no differences

    >>> case = RowDiffScript(argv="rowdiff.py --ignore-fields=modeup,modedown data/test-source.fits data/test-change-row1-valueLeft.fits")
    >>> case.run() # doctest: +ELLIPSIS
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
             2988, -2779.03..., 'coquille'
            -5748, 6357.97..., 'ferly'
            +-1, 6357.97..., 'ferly'
             9735, -9132.53..., 'misreliance'
             425, -2689.26..., 'ogeed'
             8989, 9870.02..., 'readmittance'
    <BLANKLINE>

Test of switch fields
    >>> case = RowDiffScript(argv="rowdiff.py --fields=modeup data/test-source.fits data/test-change-row1-valueLeft.fits")
    >>> case.run()
        HDU extension #1 contains no differences

    >>> case = RowDiffScript(argv="rowdiff.py --fields=valueleft data/test-source.fits data/test-change-row1-valueLeft.fits")
    >>> case.run()
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
             2988
            -5748
            +-1
             9735
             425
             8989
    <BLANKLINE>

Mode test: no differences
    >>> case = RowDiffScript(argv="rowdiff.py --mode-fields=modeup,modedown data/test-source.fits data/test-source.fits")
    >>> case.run()
    Difference for HDU extension #1
    <BLANKLINE>
        Table A has all modes.
    <BLANKLINE>
        Table B has all modes.
    <BLANKLINE>
        Table A and B share all modes.
    <BLANKLINE>
        All common modes are equivalent.
    <BLANKLINE>

Mode test: No mode changes, but change in rows selected
    >>> case = RowDiffScript(argv="rowdiff.py --mode-fields=modeup,modedown data/test-source.fits data/test-change-row1-valueLeft.fits")
    >>> case.run() # doctest: +ELLIPSIS
    Difference for HDU extension #1
    <BLANKLINE>
        Table A has all modes.
    <BLANKLINE>
        Table B has all modes.
    <BLANKLINE>
        Table A and B share all modes.
    <BLANKLINE>
        Common mode changes:
        If there were duplicate modes, the following may be nonsensical.
    <BLANKLINE>
            Changed Modes:
            From Table A:
    modeup modedown valueleft valueright wordage
    ------ -------- --------- ---------- -------
       yes       no      5748  6357.97...   ferly
    <BLANKLINE>
            To Table B:
    modeup modedown valueleft valueright wordage
    ------ -------- --------- ---------- -------
       yes       no        -1  6357.97...   ferly
    <BLANKLINE>

Mode test: removed modes
    >>> case = RowDiffScript(argv="rowdiff.py --mode-fields=modeup,modedown data/test-source.fits data/test-alternate-modes.fits")
    >>> case.run()
    Difference for HDU extension #1
    <BLANKLINE>
        Table A has all modes.
    <BLANKLINE>
        Table B changes:
    <BLANKLINE>
            Missing Modes:
    modeup modedown
    ------ --------
     maybe    maybe
        no       no
       yes      yes
    <BLANKLINE>
        Table A to B changes:
    <BLANKLINE>
            Missing Modes:
    modeup modedown
    ------ --------
     maybe    maybe
        no       no
       yes      yes
    <BLANKLINE>
        All common modes are equivalent.
    <BLANKLINE>

Mode test: duplicate modes
    >>> case = RowDiffScript(argv="rowdiff.py --mode-fields=modeup,modedown data/test-source.fits data/test-duplicate-mode.fits")
    >>> case.run()  # doctest: +ELLIPSIS
    Difference for HDU extension #1
    <BLANKLINE>
        Table A has all modes.
    <BLANKLINE>
        Table B changes:
    <BLANKLINE>
            Duplicated Modes:
    modeup modedown
    ------ --------
        no    maybe
    <BLANKLINE>
        Table A to B changes:
    <BLANKLINE>
            Duplicated Modes:
    modeup modedown
    ------ --------
        no    maybe
    <BLANKLINE>
        Common mode changes:
        If there were duplicate modes, the following may be nonsensical.
    <BLANKLINE>
            Changed Modes:
            From Table A:
    modeup modedown valueleft valueright wordage
    ------ -------- --------- ---------- -------
        no      yes       425 -2689.26...   ogeed
    <BLANKLINE>
            To Table B:
    modeup modedown valueleft valueright wordage
    ------ -------- --------- ---------- -------
        no      yes        -1 -2689.26...   ogeed
    <BLANKLINE>

CLEANUP

    >>> test_config.cleanup(old_state)

"""

def main():
    """Run module tests,  for now just doctests only."""
    from crds.tests import test_rowdiff, tstmod
    return tstmod(test_rowdiff)

if __name__ == "__main__":
    print(main())
