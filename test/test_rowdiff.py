"""rowdiff unit test module
"""
from pathlib import Path
from pytest import mark

from crds.core import log, utils

from crds.rowdiff import RowDiffScript

# For log capture tests, need to ensure that the CRDS
# logger propagates its events.
log.THE_LOGGER.logger.propagate = True

@mark.rowdiff
def test_withtableexts(hst_data, capsys):
    """Only should work with Table extensions"""
    fits1_path = Path(hst_data) / 'hst_acs_biasfile_0001.fits'
    fits2_path = Path(hst_data) / 'hst_acs_biasfile_0002.fits'
    argv = f'crds.rowdiff {str(fits1_path)} {str(fits2_path)}'
    RowDiffScript(argv)()

    # Success if there is only a blank line
    assert '\n' == capsys.readouterr().out


@mark.rowdiff
def test_nodiff(test_data, capsys):
    """Basic functionality: No differences"""
    fits_path = str(Path(test_data) / 'test-source.fits')
    argv = f'crds.rowdiff {fits_path} {fits_path}'
    RowDiffScript(argv)()

    assert 'HDU extension #1 contains no differences' in capsys.readouterr().out


@mark.rowdiff
def test_rowchange(test_data, capsys):
    """Row change"""
    fits1_path = Path(test_data) / 'test-source.fits'
    fits2_path = Path(test_data) / 'test-change-row1-valueLeft.fits'
    argv = f'crds.rowdiff {str(fits1_path)} {str(fits2_path)}'
    RowDiffScript(argv)()

    expected = """Row differences for HDU extension #1\n\n
    Summary:\n
    a rows 1-1 differ from b rows 1-1\n\n
    Row difference, unified diff format:\n
    --- Table A\n\n
    +++ Table B\n\n
    @@ -1,5 +1,5 @@\n\n
    'yes', 'yes', 2988, -2779.0352, 'coquille'\n
    -'yes', 'no', 5748, 6357.9727, 'ferly'\n
    +'yes', 'no', -1, 6357.9727, 'ferly'\n
    'yes', 'maybe', 9735, -9132.532, 'misreliance'\n
    'no', 'yes', 425, -2689.2646, 'ogeed'\n
    'no', 'no', 8989, 9870.025, 'readmittance'
    """
    out = capsys.readouterr().out
    for msg in expected.splitlines():
        assert msg.strip() in out


@mark.rowdiff
def test_rowremoval(test_data, capsys):
    """Test Row removal"""
    fits1_path = Path(test_data) / 'test-source.fits'
    fits2_path = Path(test_data) / 'test-single-modes.fits'
    argv = f'crds.rowdiff {str(fits1_path)} {str(fits2_path)}'
    RowDiffScript(argv)()

    expected = """Row differences for HDU extension #1\n\n
    Summary:\n
    Remove from a rows 1-3\n
    Remove from a rows 5-7\n\n
    Row difference, unified diff format:\n
    --- Table A\n\n
    +++ Table B\n\n
    @@ -1,9 +1,3 @@\n\n
    'yes', 'yes', 2988, -2779.0352, 'coquille'\n
    -'yes', 'no', 5748, 6357.9727, 'ferly'\n
    -'yes', 'maybe', 9735, -9132.532, 'misreliance'\n
    -'no', 'yes', 425, -2689.2646, 'ogeed'\n
    'no', 'no', 8989, 9870.025, 'readmittance'\n
    -'no', 'maybe', 3537, -8615.033, 'anacatadidymus'\n
    -'maybe', 'yes', 1763, -2442.9683, 'monochromat'\n
    -'maybe', 'no', 8023, 4665.564, 'ranarium'\n
    'maybe', 'maybe', 7347, 1705.5876, 'Dode'
    """
    out = capsys.readouterr().out
    for msg in expected.splitlines():
        assert msg.strip() in out


@mark.rowdiff
def test_rowaddition(test_data, capsys):
    """Test Row addition"""
    fits1_path = Path(test_data) / 'test-single-modes.fits'
    fits2_path = Path(test_data) / 'test-source.fits'
    argv = f'crds.rowdiff {str(fits1_path)} {str(fits2_path)}'
    RowDiffScript(argv)()

    expected = """Row differences for HDU extension #1\n\n
    Summary:\n
    Add to b rows 1-3\n
    Add to b rows 5-7\n\n
    Row difference, unified diff format:\n
    --- Table A\n\n
    +++ Table B\n\n
    @@ -1,3 +1,9 @@\n\n
    'yes', 'yes', 2988, -2779.0352, 'coquille'\n
    +'yes', 'no', 5748, 6357.9727, 'ferly'\n
    +'yes', 'maybe', 9735, -9132.532, 'misreliance'\n
    +'no', 'yes', 425, -2689.2646, 'ogeed'\n
    'no', 'no', 8989, 9870.025, 'readmittance'\n
    +'no', 'maybe', 3537, -8615.033, 'anacatadidymus'\n
    +'maybe', 'yes', 1763, -2442.9683, 'monochromat'\n
    +'maybe', 'no', 8023, 4665.564, 'ranarium'\n
    'maybe', 'maybe', 7347, 1705.5876, 'Dode
    """
    out = capsys.readouterr().out
    for msg in expected.splitlines():
        assert msg.strip() in out

"""
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
