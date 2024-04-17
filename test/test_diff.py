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
import subprocess
import os
import asdf
from pytest import mark, fixture
from crds.diff import DiffScript


@fixture(scope="module")
def fitsdiff_version() -> str:
    return subprocess.check_output("fitsdiff --version", shell=True).decode().split()[1]


@mark.hst
@mark.diff
def test_diff_pmap_diffs(capsys, default_shared_state, hst_data):
    """
    Compute diffs for two .pmap's:
    """
    status = DiffScript(f"crds.diff {hst_data}/hst_0001.pmap {hst_data}/hst_0002.pmap")()
    output = capsys.readouterr().out
    assert status == 1
    assert output == f"""(('{hst_data}/hst_0001.pmap', '{hst_data}/hst_0002.pmap'), ('test/data/hst/hst_acs_0001.imap', 'test/data/hst/hst_acs_0002.imap'), ('test/data/hst/hst_acs_biasfile_0001.rmap', 'test/data/hst/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00'), 'replaced test/data/hst/hst_acs_biasfile_0001.fits with test/data/hst/hst_acs_biasfile_0002.fits')
(('{hst_data}/hst_0001.pmap', '{hst_data}/hst_0002.pmap'), ('test/data/hst/hst_acs_0001.imap', 'test/data/hst/hst_acs_0002.imap'), ('test/data/hst/hst_acs_biasfile_0001.rmap', 'test/data/hst/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'deleted Match rule for m991609tj_bia.fits')
(('{hst_data}/hst_0001.pmap', '{hst_data}/hst_0002.pmap'), ('test/data/hst/hst_acs_0001.imap', 'test/data/hst/hst_acs_0002.imap'), ('test/data/hst/hst_acs_biasfile_0001.rmap', 'test/data/hst/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'deleted Match rule for q9e1206kj_bia.fits')
(('{hst_data}/hst_0001.pmap', '{hst_data}/hst_0002.pmap'), ('test/data/hst/hst_acs_0001.imap', 'test/data/hst/hst_acs_0002.imap'), ('test/data/hst/hst_acs_biasfile_0001.rmap', 'test/data/hst/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:42:53'), 'deleted Match rule for q9e12071j_bia.fits')
(('{hst_data}/hst_0001.pmap', '{hst_data}/hst_0002.pmap'), ('test/data/hst/hst_acs_0001.imap', 'test/data/hst/hst_acs_0002.imap'), ('test/data/hst/hst_acs_biasfile_0001.rmap', 'test/data/hst/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'added Match rule for m991609tj_bia.fits')
(('{hst_data}/hst_0001.pmap', '{hst_data}/hst_0002.pmap'), ('test/data/hst/hst_acs_0001.imap', 'test/data/hst/hst_acs_0002.imap'), ('test/data/hst/hst_acs_biasfile_0001.rmap', 'test/data/hst/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'added Match rule for q9e1206kj_bia.fits')
(('{hst_data}/hst_0001.pmap', '{hst_data}/hst_0002.pmap'), ('test/data/hst/hst_acs_0001.imap', 'test/data/hst/hst_acs_0002.imap'), ('test/data/hst/hst_acs_biasfile_0001.rmap', 'test/data/hst/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:43:54'), 'added Match rule for q9e12071j_bia.fits')
(('{hst_data}/hst_0001.pmap', '{hst_data}/hst_0002.pmap'), ('test/data/hst/hst_acs_0001.imap', 'test/data/hst/hst_acs_0002.imap'), ('biasfile',), 'replaced test/data/hst/hst_acs_biasfile_0001.rmap with test/data/hst/hst_acs_biasfile_0002.rmap')
(('{hst_data}/hst_0001.pmap', '{hst_data}/hst_0002.pmap'), ('acs',), 'replaced test/data/hst/hst_acs_0001.imap with test/data/hst/hst_acs_0002.imap')
"""


@mark.hst
@mark.diff
def test_diff_imap_diffs(capsys, default_shared_state, hst_data):
    """
    Compute diffs for two .imap's:
    """
    status = DiffScript(f"crds.diff {hst_data}/hst_acs_0001.imap {hst_data}/hst_acs_0002.imap")()
    output = capsys.readouterr().out
    assert status == 1
    assert output == f"""(('{hst_data}/hst_acs_0001.imap', '{hst_data}/hst_acs_0002.imap'), ('test/data/hst/hst_acs_biasfile_0001.rmap', 'test/data/hst/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00'), 'replaced test/data/hst/hst_acs_biasfile_0001.fits with test/data/hst/hst_acs_biasfile_0002.fits')
(('{hst_data}/hst_acs_0001.imap', '{hst_data}/hst_acs_0002.imap'), ('test/data/hst/hst_acs_biasfile_0001.rmap', 'test/data/hst/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'deleted Match rule for m991609tj_bia.fits')
(('{hst_data}/hst_acs_0001.imap', '{hst_data}/hst_acs_0002.imap'), ('test/data/hst/hst_acs_biasfile_0001.rmap', 'test/data/hst/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'deleted Match rule for q9e1206kj_bia.fits')
(('{hst_data}/hst_acs_0001.imap', '{hst_data}/hst_acs_0002.imap'), ('test/data/hst/hst_acs_biasfile_0001.rmap', 'test/data/hst/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:42:53'), 'deleted Match rule for q9e12071j_bia.fits')
(('{hst_data}/hst_acs_0001.imap', '{hst_data}/hst_acs_0002.imap'), ('test/data/hst/hst_acs_biasfile_0001.rmap', 'test/data/hst/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'added Match rule for m991609tj_bia.fits')
(('{hst_data}/hst_acs_0001.imap', '{hst_data}/hst_acs_0002.imap'), ('test/data/hst/hst_acs_biasfile_0001.rmap', 'test/data/hst/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'added Match rule for q9e1206kj_bia.fits')
(('{hst_data}/hst_acs_0001.imap', '{hst_data}/hst_acs_0002.imap'), ('test/data/hst/hst_acs_biasfile_0001.rmap', 'test/data/hst/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:43:54'), 'added Match rule for q9e12071j_bia.fits')
(('{hst_data}/hst_acs_0001.imap', '{hst_data}/hst_acs_0002.imap'), ('biasfile',), 'replaced test/data/hst/hst_acs_biasfile_0001.rmap with test/data/hst/hst_acs_biasfile_0002.rmap')
"""


@mark.hst
@mark.diff
def test_diff_rmap_diffs(capsys, default_shared_state, hst_data):
    """
    Compute diffs for two .rmap's:
    """
    status = DiffScript(f"crds.diff {hst_data}/hst_acs_biasfile_0001.rmap {hst_data}/hst_acs_biasfile_0002.rmap --include-header-diffs")()
    output = capsys.readouterr().out
    assert status == 1
    assert output == f"""(('{hst_data}/hst_acs_biasfile_0001.rmap', '{hst_data}/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00'), 'replaced test/data/hst/hst_acs_biasfile_0001.fits with test/data/hst/hst_acs_biasfile_0002.fits')
(('{hst_data}/hst_acs_biasfile_0001.rmap', '{hst_data}/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'deleted Match rule for m991609tj_bia.fits')
(('{hst_data}/hst_acs_biasfile_0001.rmap', '{hst_data}/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'deleted Match rule for q9e1206kj_bia.fits')
(('{hst_data}/hst_acs_biasfile_0001.rmap', '{hst_data}/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:42:53'), 'deleted Match rule for q9e12071j_bia.fits')
(('{hst_data}/hst_acs_biasfile_0001.rmap', '{hst_data}/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'added Match rule for m991609tj_bia.fits')
(('{hst_data}/hst_acs_biasfile_0001.rmap', '{hst_data}/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'added Match rule for q9e1206kj_bia.fits')
(('{hst_data}/hst_acs_biasfile_0001.rmap', '{hst_data}/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:43:54'), 'added Match rule for q9e12071j_bia.fits')
(('{hst_data}/hst_acs_biasfile_0001.rmap', '{hst_data}/hst_acs_biasfile_0002.rmap'), 'deleted header \\'rmap_relevance\\' = \\'((DETECTOR != "SBC") and (BIASCORR != "OMIT"))\\'')
(('{hst_data}/hst_acs_biasfile_0001.rmap', '{hst_data}/hst_acs_biasfile_0002.rmap'), "header added 'extra_info' = 'some other piece of information.'")
(('{hst_data}/hst_acs_biasfile_0001.rmap', '{hst_data}/hst_acs_biasfile_0002.rmap'), "header replaced 'extra_keys' = ('XCORNER', 'YCORNER', 'CCDCHIP') with ('ZCORNER', 'YCORNER', 'CCDCHIP')")
(('{hst_data}/hst_acs_biasfile_0001.rmap', '{hst_data}/hst_acs_biasfile_0002.rmap'), "header replaced 'reffile_required' = 'yes' with 'no'")
(('{hst_data}/hst_acs_biasfile_0001.rmap', '{hst_data}/hst_acs_biasfile_0002.rmap'), "header replaced 'sha1sum' = 'ac75f7fb502e1be56588207a06bc19330846e9f7' with 'c3bc544b6daaef797f3dc6025d0288e658d50016'")
"""


@mark.hst
@mark.diff
def test_diff_fits_diff(capsys, default_shared_state, hst_data, fitsdiff_version):
    """
    Compute diffs for two .fits's:
    """
    status = DiffScript(f"crds.diff {hst_data}/hst_acs_biasfile_0001.fits {hst_data}/hst_acs_biasfile_0002.fits")() # doctest: +ELLIPSIS
    output = capsys.readouterr().out
    assert status == 1
    assert output == f"""
 fitsdiff: {fitsdiff_version}
 a: {hst_data}/hst_acs_biasfile_0001.fits
 b: {hst_data}/hst_acs_biasfile_0002.fits
 Maximum number of different data values to be reported: 10
 Relative tolerance: 0.0, Absolute tolerance: 0.0

Primary HDU:

   Headers contain differences:
     Extra keyword 'ADD_1'  in a: 'added to hst_acs_biasfile_0001.fits'
     Extra keyword 'ADD_2'  in b: 'added to hst_acs_biasfile_0002.fits'
     Keyword DIFF_12  has different values:
        a> value in 1
         ?          ^
        b> value in 2
         ?          ^

 
"""


@mark.jwst
@mark.diff
def test_diff_asdf(capsys, jwst_shared_cache_state, jwst_data):
    """
    Compute diffs for two .asdf's:
    """
    status = DiffScript(f"crds.diff {jwst_data}/jwst_nircam_specwcs_0010.asdf {jwst_data}/jwst_nircam_specwcs_0011.asdf")() # doctest: +ELLIPSIS
    output = capsys.readouterr().out

    if asdf.__version__ < "3.0.0":
        expected_output = """        ndarrays differ by contents
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
"""

    else:
        expected_output = """tree:
  dispx:
    -
      coefficients:
>       ndarrays differ by contents
<       ndarrays differ by contents
    -
      coefficients:
>       ndarrays differ by contents
<       ndarrays differ by contents
  dispy:
    -
      coefficients:
>       ndarrays differ by contents
<       ndarrays differ by contents
    -
      coefficients:
>       ndarrays differ by contents
<       ndarrays differ by contents
  history:
    -
      description:
>       Created from NIRCAM_modA_R.conf
<       Created from NIRCAM_modA_C.conf
      time:
>       2017-09-08 16:57:27.004949
<       2017-09-08 16:57:26.927451
  invdispx:
    -
      coefficients:
>       ndarrays differ by contents
<       ndarrays differ by contents
    -
      coefficients:
>       ndarrays differ by contents
<       ndarrays differ by contents
  invdispy:
    -
      coefficients:
>       ndarrays differ by contents
<       ndarrays differ by contents
    -
      coefficients:
>       ndarrays differ by contents
<       ndarrays differ by contents
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
"""
    assert output == expected_output
    assert status == 1
    status = DiffScript(f"crds.diff {jwst_data}/jwst_nircam_specwcs_0010.asdf {jwst_data}/jwst_nircam_specwcs_0010.asdf")() # doctest: +ELLIPSIS
    assert status == 0


@mark.hst
@mark.diff
def test_diff_rmap_primitive_diffs(capsys, default_shared_state, hst_data, fitsdiff_version):
    """
    Compute primitive diffs for two .rmap's:
    """
    status = DiffScript(f"crds.diff {hst_data}/hst_acs_biasfile_0001.rmap {hst_data}/hst_acs_biasfile_0002.rmap --primitive-diffs")()  #doctest: +ELLIPSIS
    output = capsys.readouterr().out
    assert status == 1
    assert output == f"""================================================================================
(('{hst_data}/hst_acs_biasfile_0001.rmap', '{hst_data}/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00'), 'replaced test/data/hst/hst_acs_biasfile_0001.fits with test/data/hst/hst_acs_biasfile_0002.fits')

 fitsdiff: {fitsdiff_version}
 a: test/data/hst/hst_acs_biasfile_0001.fits
 b: test/data/hst/hst_acs_biasfile_0002.fits
 Maximum number of different data values to be reported: 10
 Relative tolerance: 0.0, Absolute tolerance: 0.0

Primary HDU:

   Headers contain differences:
     Extra keyword 'ADD_1'  in a: 'added to hst_acs_biasfile_0001.fits'
     Extra keyword 'ADD_2'  in b: 'added to hst_acs_biasfile_0002.fits'
     Keyword DIFF_12  has different values:
        a> value in 1
         ?          ^
        b> value in 2
         ?          ^

 
================================================================================
(('{hst_data}/hst_acs_biasfile_0001.rmap', '{hst_data}/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'deleted Match rule for m991609tj_bia.fits')
================================================================================
(('{hst_data}/hst_acs_biasfile_0001.rmap', '{hst_data}/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'deleted Match rule for q9e1206kj_bia.fits')
================================================================================
(('{hst_data}/hst_acs_biasfile_0001.rmap', '{hst_data}/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:42:53'), 'deleted Match rule for q9e12071j_bia.fits')
================================================================================
(('{hst_data}/hst_acs_biasfile_0001.rmap', '{hst_data}/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'added Match rule for m991609tj_bia.fits')
================================================================================
(('{hst_data}/hst_acs_biasfile_0001.rmap', '{hst_data}/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'added Match rule for q9e1206kj_bia.fits')
================================================================================
(('{hst_data}/hst_acs_biasfile_0001.rmap', '{hst_data}/hst_acs_biasfile_0002.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:43:54'), 'added Match rule for q9e12071j_bia.fits')
"""


@mark.hst
@mark.diff
def test_diff_file_reversions(capsys, default_shared_state, hst_data):
    """
    Compute diffs checking for reversions: (invert file order to simulate reverse filename progression)
    """
    status = DiffScript(f"crds.diff {hst_data}/hst_0002.pmap {hst_data}/hst_0001.pmap --check-diffs")()
    output = capsys.readouterr().out
    assert status == 2
    assert output == f"""(('{hst_data}/hst_0002.pmap', '{hst_data}/hst_0001.pmap'), ('test/data/hst/hst_acs_0002.imap', 'test/data/hst/hst_acs_0001.imap'), ('test/data/hst/hst_acs_biasfile_0002.rmap', 'test/data/hst/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00'), 'replaced test/data/hst/hst_acs_biasfile_0002.fits with test/data/hst/hst_acs_biasfile_0001.fits')
(('{hst_data}/hst_0002.pmap', '{hst_data}/hst_0001.pmap'), ('test/data/hst/hst_acs_0002.imap', 'test/data/hst/hst_acs_0001.imap'), ('test/data/hst/hst_acs_biasfile_0002.rmap', 'test/data/hst/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'added Match rule for m991609tj_bia.fits')
(('{hst_data}/hst_0002.pmap', '{hst_data}/hst_0001.pmap'), ('test/data/hst/hst_acs_0002.imap', 'test/data/hst/hst_acs_0001.imap'), ('test/data/hst/hst_acs_biasfile_0002.rmap', 'test/data/hst/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'added Match rule for q9e1206kj_bia.fits')
(('{hst_data}/hst_0002.pmap', '{hst_data}/hst_0001.pmap'), ('test/data/hst/hst_acs_0002.imap', 'test/data/hst/hst_acs_0001.imap'), ('test/data/hst/hst_acs_biasfile_0002.rmap', 'test/data/hst/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '4.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:42:53'), 'added Match rule for q9e12071j_bia.fits')
(('{hst_data}/hst_0002.pmap', '{hst_data}/hst_0001.pmap'), ('test/data/hst/hst_acs_0002.imap', 'test/data/hst/hst_acs_0001.imap'), ('test/data/hst/hst_acs_biasfile_0002.rmap', 'test/data/hst/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('1992-01-01', '00:00:00'), 'deleted Match rule for m991609tj_bia.fits')
(('{hst_data}/hst_0002.pmap', '{hst_data}/hst_0001.pmap'), ('test/data/hst/hst_acs_0002.imap', 'test/data/hst/hst_acs_0001.imap'), ('test/data/hst/hst_acs_biasfile_0002.rmap', 'test/data/hst/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-04', '11:32:35'), 'deleted Match rule for q9e1206kj_bia.fits')
(('{hst_data}/hst_0002.pmap', '{hst_data}/hst_0001.pmap'), ('test/data/hst/hst_acs_0002.imap', 'test/data/hst/hst_acs_0001.imap'), ('test/data/hst/hst_acs_biasfile_0002.rmap', 'test/data/hst/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '5.0', '*', '1062', '1044', '19.0', '20.0', 'N/A', 'N/A', 'N/A'), ('2006-07-15', '04:43:54'), 'deleted Match rule for q9e12071j_bia.fits')
(('{hst_data}/hst_0002.pmap', '{hst_data}/hst_0001.pmap'), ('test/data/hst/hst_acs_0002.imap', 'test/data/hst/hst_acs_0001.imap'), ('biasfile',), 'replaced test/data/hst/hst_acs_biasfile_0002.rmap with test/data/hst/hst_acs_biasfile_0001.rmap')
(('{hst_data}/hst_0002.pmap', '{hst_data}/hst_0001.pmap'), ('acs',), 'replaced test/data/hst/hst_acs_0002.imap with test/data/hst/hst_acs_0001.imap')
"""


@mark.hst
@mark.diff
def test_diff_row_change(capsys, default_shared_state, hst_data, fitsdiff_version):
    """
    Row change
    """
    status = DiffScript(f"crds.diff {hst_data}/test-source.fits {hst_data}/test-change-row1-valueLeft.fits")()  #doctest: +ELLIPSIS
    output = capsys.readouterr().out
    assert status == 1
    assert output == f"""
 fitsdiff: {fitsdiff_version}
 a: {hst_data}/test-source.fits
 b: {hst_data}/test-change-row1-valueLeft.fits
 Maximum number of different data values to be reported: 10
 Relative tolerance: 0.0, Absolute tolerance: 0.0

Extension HDU 1:

   Data contains differences:
     Column valueLeft data differs in row 1:
        a> 5748
        b> -1
     1 different table data element(s) found (2.22% different).

 Row differences for HDU extension #1

    Summary:
        a rows 1-1 differ from b rows 1-1

    Row difference, unified diff format:
        --- Table A

        +++ Table B

        @@ -1,5 +1,5 @@

         'yes', 'yes', 2988, -2779.0352, 'coquille'
        -'yes', 'no', 5748, 6357.9727, 'ferly'
        +'yes', 'no', -1, 6357.9727, 'ferly'
         'yes', 'maybe', 9735, -9132.532, 'misreliance'
         'no', 'yes', 425, -2689.2646, 'ogeed'
         'no', 'no', 8989, 9870.025, 'readmittance'

"""


@mark.hst
@mark.diff
def test_diff_print_affected_modes(capsys, default_shared_state, hst_data):
    status = DiffScript(f"crds.diff {hst_data}/hst_cos_deadtab.rmap {hst_data}/hst_cos_deadtab_9998.rmap --print-affected-modes")()
    output = capsys.readouterr().out
    assert status == 1
    assert output == """INSTRUMENT='COS' REFTYPE='DEADTAB' DETECTOR='FUV' DIFF_COUNT='1'
INSTRUMENT='COS' REFTYPE='DEADTAB' DETECTOR='NUV' DIFF_COUNT='1'
"""


@mark.hst
@mark.diff
def test_diff_print_all_new_files(capsys, hst_default_cache_state, hst_data):
    status = DiffScript(f"crds.diff {hst_data}/hst_0001.pmap {hst_data}/hst_0008.pmap --print-all-new-files --sync-files --include-header-diffs --hide-boring")()
    output = capsys.readouterr().out
    assert output == f"""hst_0002.pmap  
hst_0003.pmap  
hst_0004.pmap  
hst_0005.pmap  
hst_0006.pmap  
hst_0007.pmap  
hst_0008.pmap  
hst_acs.imap acs 
hst_acs_biasfile.rmap acs biasfile
hst_acs_d2imfile_0001.rmap acs d2imfile
hst_cos_0001.imap cos 
hst_cos_0002.imap cos 
hst_cos_flatfile_0002.rmap cos flatfile
hst_cos_flatfile_0003.rmap cos flatfile
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
x5u17177j_d2i.fits acs d2imfile
x5v1944hl_flat.fits cos flatfile
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
"""
    assert status == 1


@mark.hst
@mark.diff
def test_diff_print_new_files(capsys, hst_default_cache_state, hst_data):
    status = DiffScript(f"crds.diff {hst_data}/hst_0001.pmap {hst_data}/hst_0002.pmap --print-new-files")()
    output = capsys.readouterr().out
    assert output == f"""hst_0002.pmap
hst_acs_0002.imap
hst_acs_biasfile_0002.rmap
test/data/hst/hst_acs_biasfile_0002.fits
"""
    assert status == 1


@mark.hst
@mark.diff
def test_diff_print_affected_types(capsys, default_shared_state, hst_data):
    status = DiffScript(f"crds.diff {hst_data}/hst_cos_deadtab.rmap {hst_data}/hst_cos_deadtab_9998.rmap --print-affected-types")()
    output = capsys.readouterr().out
    assert output == "cos        deadtab   \n"
    assert status == 1


@mark.hst
@mark.diff
def test_diff_print_affected_instruments(capsys, default_shared_state, hst_data):
    status = DiffScript(f"crds.diff {hst_data}/hst_cos_deadtab.rmap {hst_data}/hst_cos_deadtab_9998.rmap --print-affected-instruments")()
    output = capsys.readouterr().out
    assert output == "cos\n"
    assert status == 1


@mark.hst
@mark.diff
def test_diff_recurse_added_deleted_na(capsys, hst_default_cache_state, hst_data):
    """
    For this test, checking recursive terminal adds/deletes and N/A + OMIT at all levels
    """
    crds_path = hst_default_cache_state.cache
    test_cache_pmap = f"{crds_path}/mappings/hst/hst.pmap"
    hst_pmap = f"{hst_data}/hst.pmap"
    hst_rel = "test/data/hst"
    status = DiffScript(f"crds.diff crds://hst.pmap {hst_pmap} --recurse-added-deleted")()
    output = capsys.readouterr().out
    assert status == 1
    expected_output = [
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_acs.imap', '{hst_rel}/hst_acs.imap'), ('hst_acs_biasfile.rmap', '{hst_rel}/hst_acs_biasfile_0001.rmap'), ('HRC', 'A', '1.0', '*', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'), ('1992-01-02', '00:00:00'), 'added terminal {hst_rel}/hst_acs_biasfile_0001.fits')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_cos.imap',), 'hst_cos_fluxtab.rmap', ('FUV', 'SPECTROSCOPIC'), ('1996-10-01', '00:00:00'), 'deleted terminal s7g1700kl_phot.fits')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_cos.imap',), 'hst_cos_fluxtab.rmap', ('FUV', 'SPECTROSCOPIC'), ('2009-05-11', '00:00:00'), 'deleted terminal u8k1433ql_phot.fits')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_cos.imap',), 'hst_cos_fluxtab.rmap', ('FUV', 'SPECTROSCOPIC'), ('2009-05-11', '00:00:01'), 'deleted terminal x1v17416l_phot.fits')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_cos.imap',), 'hst_cos_fluxtab.rmap', ('FUV', 'SPECTROSCOPIC'), ('2009-05-11', '00:00:02'), 'deleted terminal x6q17587l_phot.fits')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_cos.imap',), 'hst_cos_fluxtab.rmap', ('NUV', 'SPECTROSCOPIC'), ('1996-10-01', '00:00:00'), 'deleted terminal s7g17011l_phot.fits')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_cos.imap',), 'hst_cos_fluxtab.rmap', ('NUV', 'SPECTROSCOPIC'), ('2009-05-11', '00:00:00'), 'deleted terminal t9h1220sl_phot.fits')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_cos.imap',), 'hst_cos_xtractab.rmap', ('FUV', 'SPECTROSCOPIC', '-1|1'), ('2009-05-11', '00:00:01'), 'deleted terminal x1v17414l_1dx.fits')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_cos.imap',), 'hst_cos_xtractab.rmap', ('FUV', 'SPECTROSCOPIC', '-2147483648'), ('1996-10-01', '00:00:00'), 'deleted terminal s7g17006l_1dx.fits')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_cos.imap',), 'hst_cos_xtractab.rmap', ('FUV', 'SPECTROSCOPIC', '-2147483648'), ('2006-10-01', '00:00:00'), 'deleted terminal s7g17007l_1dx.fits')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_cos.imap',), 'hst_cos_xtractab.rmap', ('FUV', 'SPECTROSCOPIC', '2'), ('2009-05-11', '00:00:02'), 'deleted terminal x6q17586l_1dx.fits')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_cos.imap',), 'hst_cos_xtractab.rmap', ('NUV', 'SPECTROSCOPIC', '-1|1'), ('2009-05-11', '00:00:00'), 'deleted terminal w5g1439sl_1dx.fits')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_cos.imap',), 'hst_cos_xtractab.rmap', ('NUV', 'SPECTROSCOPIC', '-2147483648'), ('1996-10-01', '00:00:00'), 'deleted terminal s7g1700nl_1dx.fits')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_cos.imap',), 'hst_cos_xtractab.rmap', ('NUV', 'SPECTROSCOPIC', '-2147483648'), ('2006-10-01', '00:00:00'), 'deleted terminal s7g1700ol_1dx.fits')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_cos.imap',), '{hst_rel}/hst_cos_twozxtab_0262.rmap', ('FUV', 'SPECTROSCOPIC', '3.0'), ('2009-05-11', '00:00:00'), 'added terminal z2d1925ql_2zx.fits')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_cos.imap', '{hst_rel}/hst_cos.imap'), ('hst_cos_flatfile.rmap', '{hst_rel}/hst_cos_flatfile.rmap'), ('FUV', 'G130M|G140L|G160M'), ('1996-10-01', '00:00:00'), 'replaced n9n20182l_flat.fits with OMIT')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_cos.imap', '{hst_rel}/hst_cos.imap'), ('hst_cos_flatfile.rmap', '{hst_rel}/hst_cos_flatfile.rmap'), ('FUV', 'G160M'), ('1996-10-01', '00:00:00'), 'deleted Match rule for v4s17227l_flat.fits')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_cos.imap', '{hst_rel}/hst_cos.imap'), ('hst_cos_flatfile.rmap', '{hst_rel}/hst_cos_flatfile.rmap'), ('NUV', 'G160M'), ('1996-10-01', '00:00:00'), 'added Match rule for v4s17227l_flat.fits')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_cos.imap', '{hst_rel}/hst_cos.imap'), ('hst_cos_flatfile.rmap', '{hst_rel}/hst_cos_flatfile.rmap'), ('NUV', 'G185M|G225M|G230L|G285M|MIRRORA|MIRRORB'), ('1996-10-01', '00:00:00'), 'replaced s7g1700tl_flat.fits with N/A')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_acs.imap', '{hst_rel}/hst_acs.imap'), ('biasfile',), 'replaced hst_acs_biasfile.rmap with {hst_rel}/hst_acs_biasfile_0001.rmap')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_cos.imap', '{hst_rel}/hst_cos.imap'), ('flatfile',), 'replaced hst_cos_flatfile.rmap with {hst_rel}/hst_cos_flatfile.rmap')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_cos.imap', '{hst_rel}/hst_cos.imap'), ('fluxtab',), 'deleted hst_cos_fluxtab.rmap')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_cos.imap', '{hst_rel}/hst_cos.imap'), ('tracetab',), 'added N/A')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_cos.imap', '{hst_rel}/hst_cos.imap'), ('twozxtab',), 'added {hst_rel}/hst_cos_twozxtab_0262.rmap')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('hst_cos.imap', '{hst_rel}/hst_cos.imap'), ('xtractab',), 'replaced hst_cos_xtractab.rmap with OMIT')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('acs',), 'replaced hst_acs.imap with {hst_rel}/hst_acs.imap')",
        f"(('{test_cache_pmap}', '{hst_pmap}'), ('cos',), 'replaced hst_cos.imap with {hst_rel}/hst_cos.imap')",
    ]
    for line in expected_output:
        assert line in output.splitlines()
