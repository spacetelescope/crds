"""rowdiff unit test module
"""
from pathlib import Path
from pytest import mark

from crds.core import log, utils

from crds.rowdiff import RowDiffScript

# For log capture tests, need to ensure that the CRDS
# logger propagates its events.
log.THE_LOGGER.logger.propagate = True


@mark.hst
@mark.rowdiff
def test_withtableexts(hst_data, capsys):
    """Only should work with Table extensions"""
    fits1_path = Path(hst_data) / 'hst_acs_biasfile_0001.fits'
    fits2_path = Path(hst_data) / 'hst_acs_biasfile_0002.fits'
    argv = f'crds.rowdiff {str(fits1_path)} {str(fits2_path)}'
    RowDiffScript(argv)()

    # Success if there is only a blank line
    assert '\n' == capsys.readouterr().out


@mark.multimission
@mark.rowdiff
def test_nodiff(test_data, capsys):
    """Basic functionality: No differences"""
    fits_path = str(Path(test_data) / 'test-source.fits')
    argv = f'crds.rowdiff {fits_path} {fits_path}'
    RowDiffScript(argv)()

    assert 'HDU extension #1 contains no differences' in capsys.readouterr().out


@mark.multimission
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


@mark.multimission
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


@mark.multimission
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


@mark.multimission
@mark.rowdiff
def test_ignorefields(test_data, capsys):
    """Test of switch ignore-fields"""
    fits1_path = Path(test_data) / 'test-source.fits'
    fits2_path = Path(test_data) / 'test-change-row1-valueLeft.fits'
    argv = f'crds.rowdiff --ignore-fields=valueleft {str(fits1_path)} {str(fits2_path)}'
    RowDiffScript(argv)()

    expected = """HDU extension #1 contains no differences"""
    out = capsys.readouterr().out
    for msg in expected.splitlines():
        assert msg.strip() in out


@mark.multimission
@mark.rowdiff
def test_ignorefields_specific(test_data, capsys):
    """Test ignoring specific fields"""
    fits1_path = Path(test_data) / 'test-source.fits'
    fits2_path = Path(test_data) / 'test-change-row1-valueLeft.fits'
    argv = f'crds.rowdiff --ignore-fields=modeup,modedown {str(fits1_path)} {str(fits2_path)}'
    RowDiffScript(argv)()

    expected = """Row differences for HDU extension #1\n\n
    Summary:\n
    a rows 1-1 differ from b rows 1-1\n\n
    Row difference, unified diff format:\n
    --- Table A\n\n
    +++ Table B\n\n
    @@ -1,5 +1,5 @@\n\n
    2988, -2779.0352, 'coquille'\n
    -5748, 6357.9727, 'ferly'\n
    +-1, 6357.9727, 'ferly'\n
    9735, -9132.532, 'misreliance'\n
    425, -2689.2646, 'ogeed'\n
    8989, 9870.025, 'readmittance'
    """
    out = capsys.readouterr().out
    for msg in expected.splitlines():
        assert msg.strip() in out


@mark.multimission
@mark.rowdiff
def test_switchfields_nodiff(test_data, capsys):
    """Test of switching fields that have no differences"""
    fits1_path = Path(test_data) / 'test-source.fits'
    fits2_path = Path(test_data) / 'test-change-row1-valueLeft.fits'
    argv = f'crds.rowdiff --fields=modeup {str(fits1_path)} {str(fits2_path)}'
    RowDiffScript(argv)()

    expected = """HDU extension #1 contains no differences"""
    out = capsys.readouterr().out
    for msg in expected.splitlines():
        assert msg.strip() in out


@mark.multimission
@mark.rowdiff
def test_switchfields_withdiff(test_data, capsys):
    """Test of switching fields that do have differences"""
    fits1_path = Path(test_data) / 'test-source.fits'
    fits2_path = Path(test_data) / 'test-change-row1-valueLeft.fits'
    argv = f'crds.rowdiff --fields=valueleft {str(fits1_path)} {str(fits2_path)}'
    RowDiffScript(argv)()

    expected = """Row differences for HDU extension #1\n\n
    Summary:\n
    a rows 1-1 differ from b rows 1-1\n\n
    Row difference, unified diff format:\n
    --- Table A\n\n
    +++ Table B\n\n
    @@ -1,5 +1,5 @@\n\n
    2988\n
    -5748\n
    +-1\n
    9735\n
    425\n
    8989"""
    out = capsys.readouterr().out
    for msg in expected.splitlines():
        assert msg.strip() in out


@mark.multimission
@mark.rowdiff
def test_nodiff(test_data, capsys):
    """Mode test: no differences"""
    fits_path = Path(test_data) / 'test-source.fits'
    argv = f'crds.rowdiff --mode-fields=modeup,modedown {str(fits_path)} {str(fits_path)}'
    RowDiffScript(argv)()

    expected = """Difference for HDU extension #1\n\n
    Table A has all modes.\n\n
    Table B has all modes.\n\n
    Table A and B share all modes.\n\n
    All common modes are equivalent."""
    out = capsys.readouterr().out
    for msg in expected.splitlines():
        assert msg.strip() in out


@mark.multimission
@mark.rowdiff
def test_nodiff_diffrows(test_data, capsys):
    """Mode test: No mode changes, but change in rows selected"""
    fits1_path = Path(test_data) / 'test-source.fits'
    fits2_path = Path(test_data) / 'test-change-row1-valueLeft.fits'
    argv = f'crds.rowdiff --mode-fields=modeup,modedown {str(fits1_path)} {str(fits2_path)}'
    RowDiffScript(argv)()

    expected = """Difference for HDU extension #1\n\n
    Table A has all modes.\n\n
    Table B has all modes.\n\n
    Table A and B share all modes.\n\n
    Common mode changes:\n
    If there were duplicate modes, the following may be nonsensical.\n\n
    Changed Modes:\n
    From Table A:\nmodeup modedown valueleft valueright wordage\n
    ------ -------- --------- ---------- -------\n
    yes       no      5748  6357.9727   ferly\n\n
    To Table B:\n
    modeup modedown valueleft valueright wordage\n
    ------ -------- --------- ---------- -------\n
    yes       no        -1  6357.9727   ferly"""
    out = capsys.readouterr().out
    for msg in expected.splitlines():
        assert msg.strip() in out


@mark.multimission
@mark.rowdiff
def test_removedmodes(test_data, capsys):
    """Mode test: removed modes"""
    fits1_path = Path(test_data) / 'test-source.fits'
    fits2_path = Path(test_data) / 'test-alternate-modes.fits'
    argv = f'crds.rowdiff --mode-fields=modeup,modedown {str(fits1_path)} {str(fits2_path)}'
    RowDiffScript(argv)()

    expected = """Difference for HDU extension #1\n\n
    Table A has all modes.\n\n
    Table B changes:\n\n
    Missing Modes:\nmodeup modedown\n
    ------ --------\n
    maybe    maybe\n
    no       no\n
    yes      yes\n\n
    Table A to B changes:\n\n
    Missing Modes:\n
    modeup modedown\n
    ------ --------\n
    maybe    maybe\n
    no       no\n
    yes      yes\n\n
    All common modes are equivalent."""
    out = capsys.readouterr().out
    for msg in expected.splitlines():
        assert msg.strip() in out


@mark.multimission
@mark.rowdiff
def test_duplicatemodes(test_data, capsys):
    """Mode test: duplicate modes"""
    fits1_path = Path(test_data) / 'test-source.fits'
    fits2_path = Path(test_data) / 'test-duplicate-mode.fits'
    argv = f'crds.rowdiff --mode-fields=modeup,modedown {str(fits1_path)} {str(fits2_path)}'
    RowDiffScript(argv)()

    expected = """Difference for HDU extension #1\n\n
    Table A has all modes.\n\n
    Table B changes:\n\n
    Duplicated Modes:\n
    modeup modedown\n
    ------ --------\n
    no    maybe\n\n
    Table A to B changes:\n\n
    Duplicated Modes:\n
    modeup modedown\n
    ------ --------\n
    no    maybe\n\n
    Common mode changes:\n
    If there were duplicate modes, the following may be nonsensical.\n\n
    Changed Modes:\n
    From Table A:\n
    modeup modedown valueleft valueright wordage\n
    ------ -------- --------- ---------- -------\n
    no      yes       425 -2689.2646   ogeed\n\n
    To Table B:\n
    modeup modedown valueleft valueright wordage\n
    ------ -------- --------- ---------- -------\n
    no      yes        -1 -2689.2646   ogeed"""
    out = capsys.readouterr().out
    for msg in expected.splitlines():
        assert msg.strip() in out
