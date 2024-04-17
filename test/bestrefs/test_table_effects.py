"""This tests, through the use of bestrefs, the functioning of table effects."""
from pathlib import Path
from pytest import mark

from crds.core import log, utils
from crds import data_file

from crds.bestrefs import BestrefsScript

# For log capture tests, need to ensure that the CRDS
# logger propagates its events.
log.THE_LOGGER.logger.propagate = True

@mark.multimission
@mark.bestrefs
@mark.table_effects
def test_table_effects_default_always_reprocess(default_shared_state, caplog):
    """Test: Default rule: always reprocess, based on STIS PCTAB.
    Test: STIS APERTAB: No reprocess
    """
    argv="""bestrefs.py -z  --verbosity 25
    --old-context hst_0003.pmap  --new-context hst_0268.pmap --datasets O8EX02EFQ"""
    assert BestrefsScript(argv=argv)() == 0
    out = caplog.text

    expected = """Using explicit new context 'hst_0268.pmap' for computing updated best references.
    Using explicit old context 'hst_0003.pmap'
    Dumping dataset parameters from CRDS server
    for ['O8EX02EFQ']
    Dumped 1 of 1 datasets from CRDS server at
    Computing bestrefs for datasets ['O8EX02EFQ']
    ===> Processing O8EX02010:O8EX02EFQ
    Deep Reference examination between
    n7p1032ao_apt.fits and
    y2r1559to_apt.fits initiated.
    Instantiating rules for reference type stis_apertab.
    Rule DeepLook_STISaperture: Reprocessing is not required.
    Rule DeepLook_STISaperture: Selection rules have executed and the selected rows are the same.
    Removing table update for STIS apertab O8EX02010:O8EX02EFQ no effective change from reference 'N7P1032AO_APT.FITS' --> 'Y2R1559TO_APT.FITS'
    Deep Reference examination between
    q5417413o_pct.fits and
    y2r16006o_pct.fits initiated.
    Instantiating rules for reference type stis_pctab.
    Rule DeepLook_Default: Reprocessing is required.
    Rule DeepLook_Default: Reference type cannot be examined, by definition.
    1 sources processed
    1 source updates
    0 errors"""
    for msg in expected.splitlines():
        assert msg.strip() in out


@mark.multimission
@mark.bestrefs
@mark.table_effects
def test_table_effects_reprocess_test(default_shared_state, caplog):
    """Test: COS WCPTAB, reprocess yes"""
    argv="""bestrefs.py -z  --verbosity 25
    --old-context hst_0018.pmap  --new-context hst_0024.pmap --datasets LB6M01030"""
    assert BestrefsScript(argv=argv)() == 0
    out = caplog.text

    expected = """Using explicit new context 'hst_0024.pmap' for computing updated best references.
    Using explicit old context 'hst_0018.pmap'
    Dumping dataset parameters from CRDS server at
    for ['LB6M01030']
    Dumped 1 of 1 datasets from CRDS server at
    Computing bestrefs for datasets ['LB6M01030']
    ===> Processing LB6M01030:LB6M01AVQ
    Deep Reference examination between
    x2i1559gl_wcp.fits and
    xaf1429el_wcp.fits initiated.
    Instantiating rules for reference type cos_wcptab.
    Rule DeepLook_COSOpt_elem: Reprocessing is required.
    Rule DeepLook_COSOpt_elem: Selection rules have executed and the selected rows are different.
    1 sources processed
    1 source updates
    0 errors"""
    for msg in expected.splitlines():
        assert msg.strip() in out


@mark.multimission
@mark.bestrefs
@mark.table_effects
def test_table_effects_reprocess_no(default_shared_state, caplog):
    """Test: COS WCPTAB, reprocess no"""
    argv="""bestrefs.py -z  --verbosity 25
    --old-context hst_0018.pmap  --new-context hst_0024.pmap --datasets LBK617YRQ"""
    assert BestrefsScript(argv=argv)() == 0
    out = caplog.text

    expected = """Using explicit new context 'hst_0024.pmap' for computing updated best references.
    Using explicit old context 'hst_0018.pmap'
    Dumping dataset parameters from CRDS server at
    for ['LBK617YRQ']
    Dumped 1 of 1 datasets from CRDS server at
    Computing bestrefs for datasets ['LBK617YRQ']
    ===> Processing LBK617010:LBK617YRQ
    Deep Reference examination between
    x2i1559gl_wcp.fits and
    xaf1429el_wcp.fits initiated.
    Instantiating rules for reference type cos_wcptab.
    Rule DeepLook_COSOpt_elem: Reprocessing is not required.
    Rule DeepLook_COSOpt_elem: Selection rules have executed and the selected rows are the same.
    Removing table update for COS wcptab LBK617010:LBK617YRQ no effective change from reference 'X2I1559GL_WCP.FITS' --> 'XAF1429EL_WCP.FITS'
    1 sources processed
    0 source updates
    0 errors"""
