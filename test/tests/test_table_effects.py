"""This tests, through the use of bestrefs, the functioning of table effects."""
import doctest

from crds import tests
from crds.tests import test_config
from crds.bestrefs import BestrefsScript

def dt_table_effects_default_always_reprocess():
    """
    Test: Default rule: always reprocess, based on STIS PCTAB.
    Test: STIS APERTAB: No reprocess

    >>> old_state = test_config.setup()

    >>> doctest.ELLIPSIS_MARKER = '...'
    >>> BestrefsScript(argv="bestrefs.py -z  --verbosity 25 --old-context hst_0003.pmap  --new-context hst_0268.pmap --datasets O8EX02EFQ")() # doctest: +ELLIPSIS
    CRDS - DEBUG -  Using explicit new context 'hst_0268.pmap' for computing updated best references.
    CRDS - DEBUG -  Using explicit old context 'hst_0003.pmap'
    CRDS - INFO -  Dumping dataset parameters from CRDS server at 'https://...' for ['O8EX02EFQ']
    CRDS - INFO -  Dumped 1 of 1 datasets from CRDS server at 'https://...'
    CRDS - INFO -  Computing bestrefs for datasets ['O8EX02EFQ']
    CRDS - DEBUG -  ===> Processing O8EX02010:O8EX02EFQ
    CRDS - DEBUG -  Deep Reference examination between .../n7p1032ao_apt.fits and .../y2r1559to_apt.fits initiated.
    CRDS - DEBUG -  Instantiating rules for reference type stis_apertab.
    CRDS - DEBUG -  Rule DeepLook_STISaperture: Reprocessing is not required.
    CRDS - DEBUG -  Rule DeepLook_STISaperture: Selection rules have executed and the selected rows are the same.
    CRDS - DEBUG -  Removing table update for STIS apertab O8EX02010:O8EX02EFQ no effective change from reference 'N7P1032AO_APT.FITS' --> 'Y2R1559TO_APT.FITS'
    CRDS - DEBUG -  Deep Reference examination between .../q5417413o_pct.fits and .../y2r16006o_pct.fits initiated.
    CRDS - DEBUG -  Instantiating rules for reference type stis_pctab.
    CRDS - DEBUG -  Rule DeepLook_Default: Reprocessing is required.
    CRDS - DEBUG -  Rule DeepLook_Default: Reference type cannot be examined, by definition.
    CRDS - DEBUG -  1 sources processed
    CRDS - DEBUG -  1 source updates
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  3 infos
    0

    >>> test_config.cleanup(old_state)
    """

def dt_table_effects_reprocess_test():
    """
    Test: COS WCPTAB, reprocess yes

    >>> old_state = test_config.setup()

    >>> doctest.ELLIPSIS_MARKER = '...'
    >>> BestrefsScript(argv="bestrefs.py -z  --verbosity 25 --old-context hst_0018.pmap  --new-context hst_0024.pmap --datasets LB6M01030")() # doctest: +ELLIPSIS
    CRDS - DEBUG -  Using explicit new context 'hst_0024.pmap' for computing updated best references.
    CRDS - DEBUG -  Using explicit old context 'hst_0018.pmap'
    CRDS - INFO -  Dumping dataset parameters from CRDS server at 'https://...' for ['LB6M01030']
    CRDS - INFO -  Dumped 1 of 1 datasets from CRDS server at 'https://...'
    CRDS - INFO -  Computing bestrefs for datasets ['LB6M01030']
    CRDS - DEBUG -  ===> Processing LB6M01030:LB6M01AVQ
    CRDS - DEBUG -  Deep Reference examination between .../x2i1559gl_wcp.fits and .../xaf1429el_wcp.fits initiated.
    CRDS - DEBUG -  Instantiating rules for reference type cos_wcptab.
    CRDS - DEBUG -  Rule DeepLook_COSOpt_elem: Reprocessing is required.
    CRDS - DEBUG -  Rule DeepLook_COSOpt_elem: Selection rules have executed and the selected rows are different.
    CRDS - DEBUG -  1 sources processed
    CRDS - DEBUG -  1 source updates
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  3 infos
    0

    >>> test_config.cleanup(old_state)
    """

def dt_table_effects_reprocess_no():
    """
    Test: COS WCPTAB, reprocess no

    >>> old_state = test_config.setup()

    >>> doctest.ELLIPSIS_MARKER = '...'
    >>> BestrefsScript(argv="bestrefs.py -z  --verbosity 25 --old-context hst_0018.pmap  --new-context hst_0024.pmap --datasets LBK617YRQ")() # doctest: +ELLIPSIS
    CRDS - DEBUG -  Using explicit new context 'hst_0024.pmap' for computing updated best references.
    CRDS - DEBUG -  Using explicit old context 'hst_0018.pmap'
    CRDS - INFO -  Dumping dataset parameters from CRDS server at 'https://...' for ['LBK617YRQ']
    CRDS - INFO -  Dumped 1 of 1 datasets from CRDS server at 'https://...'
    CRDS - INFO -  Computing bestrefs for datasets ['LBK617YRQ']
    CRDS - DEBUG -  ===> Processing LBK617010:LBK617YRQ
    CRDS - DEBUG -  Deep Reference examination between .../x2i1559gl_wcp.fits and .../xaf1429el_wcp.fits initiated.
    CRDS - DEBUG -  Instantiating rules for reference type cos_wcptab.
    CRDS - DEBUG -  Rule DeepLook_COSOpt_elem: Reprocessing is not required.
    CRDS - DEBUG -  Rule DeepLook_COSOpt_elem: Selection rules have executed and the selected rows are the same.
    CRDS - DEBUG -  Removing table update for COS wcptab LBK617010:LBK617YRQ no effective change from reference 'X2I1559GL_WCP.FITS' --> 'XAF1429EL_WCP.FITS'
    CRDS - DEBUG -  1 sources processed
    CRDS - DEBUG -  0 source updates
    CRDS - INFO -  0 errors
    CRDS - INFO -  0 warnings
    CRDS - INFO -  3 infos
    0

    >>> test_config.cleanup(old_state)
    """

def main():
    """Run module tests,  for now just doctests only."""
    from crds.tests import test_table_effects, tstmod
    return tstmod(test_table_effects)

if __name__ == "__main__":
    print(main())
