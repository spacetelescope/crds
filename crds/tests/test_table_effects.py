"""
This tests, through the use of bestrefs, the functioning of table effects.

----------
TEST CASES
----------

>>> import test_config
>>> test_config.setup()

>>> from crds.bestrefs import BestrefsScript

Test: Default rule: always reprocess, based on STIS PCTAB.
Test: STIS APERTAB: No reprocess

    >>> case = BestrefsScript(argv="bestrefs.py -z  --verbosity 25 --old-context hst_0003.pmap  --new-context hst_0268.pmap --datasets O8EX02EFQ")
    >>> status = case.run()
    CRDS  : DEBUG    Using explicit new context 'hst_0268.pmap' for computing updated best references.
    CRDS  : DEBUG    Using explicit old context 'hst_0003.pmap'
    CRDS  : INFO     Dumping dataset parameters from CRDS server at 'https://hst-crds-dev.stsci.edu' for ['O8EX02EFQ']
    CRDS  : INFO     Dumped 1 of 1 datasets from CRDS server at 'https://hst-crds-dev.stsci.edu'
    CRDS  : INFO     Computing bestrefs for datasets ['O8EX02EFQ']
    CRDS  : DEBUG    ===> Processing O8EX02010:O8EX02EFQ
    CRDS  : DEBUG    Deep Reference examination between /grp/crds/cache/references/hst/n7p1032ao_apt.fits and /grp/crds/cache/references/hst/y2r1559to_apt.fits initiated.
    CRDS  : DEBUG    Instantiating rules for reference type stis_apertab.
    CRDS  : DEBUG    Rule DeepLook_STISaperture: Reprocessing is not required.
    CRDS  : DEBUG    Rule DeepLook_STISaperture: Selection rules have executed and the selected rows are the same.
    CRDS  : DEBUG    Removing table update for STIS apertab O8EX02010:O8EX02EFQ no effective change from reference 'N7P1032AO_APT.FITS' --> 'Y2R1559TO_APT.FITS'
    CRDS  : DEBUG    Deep Reference examination between /grp/crds/cache/references/hst/q5417413o_pct.fits and /grp/crds/cache/references/hst/y2r16006o_pct.fits initiated.
    CRDS  : DEBUG    Instantiating rules for reference type stis_pctab.
    CRDS  : DEBUG    Rule DeepLook_Default: Reprocessing is required.
    CRDS  : DEBUG    Rule DeepLook_Default: Reference type cannot be examined, by definition.
    CRDS  : INFO     0 errors
    CRDS  : INFO     0 warnings
    CRDS  : INFO     3 infos

Test: COS WCPTAB, reprocess yes

    >>> case = BestrefsScript(argv="bestrefs.py -z  --verbosity 25 --old-context hst_0018.pmap  --new-context hst_0024.pmap --datasets LB6M01030")
    >>> status = case.run()
    CRDS  : DEBUG    Using explicit new context 'hst_0024.pmap' for computing updated best references.
    CRDS  : DEBUG    Using explicit old context 'hst_0018.pmap'
    CRDS  : INFO     Dumping dataset parameters from CRDS server at 'https://hst-crds-dev.stsci.edu' for ['LB6M01030']
    CRDS  : INFO     Dumped 1 of 1 datasets from CRDS server at 'https://hst-crds-dev.stsci.edu'
    CRDS  : INFO     Computing bestrefs for datasets ['LB6M01030']
    CRDS  : DEBUG    ===> Processing LB6M01030:LB6M01AVQ
    CRDS  : DEBUG    Deep Reference examination between /grp/crds/cache/references/hst/x2i1559gl_wcp.fits and /grp/crds/cache/references/hst/xaf1429el_wcp.fits initiated.
    CRDS  : DEBUG    Instantiating rules for reference type cos_wcptab.
    CRDS  : DEBUG    Rule DeepLook_COSOpt_elem: Reprocessing is required.
    CRDS  : DEBUG    Rule DeepLook_COSOpt_elem: Selection rules have executed and the selected rows are different.
    CRDS  : INFO     0 errors
    CRDS  : INFO     0 warnings
    CRDS  : INFO     3 infos

Test: COS WCPTAB, reprocess no

    >>> case = BestrefsScript(argv="bestrefs.py -z  --verbosity 25 --old-context hst_0018.pmap  --new-context hst_0024.pmap --datasets LBK617YRQ")
    >>> status = case.run()
    CRDS  : DEBUG    Using explicit new context 'hst_0024.pmap' for computing updated best references.
    CRDS  : DEBUG    Using explicit old context 'hst_0018.pmap'
    CRDS  : INFO     Dumping dataset parameters from CRDS server at 'https://hst-crds-dev.stsci.edu' for ['LBK617YRQ']
    CRDS  : INFO     Dumped 1 of 1 datasets from CRDS server at 'https://hst-crds-dev.stsci.edu'
    CRDS  : INFO     Computing bestrefs for datasets ['LBK617YRQ']
    CRDS  : DEBUG    ===> Processing LBK617010:LBK617YRQ
    CRDS  : DEBUG    Deep Reference examination between /grp/crds/cache/references/hst/x2i1559gl_wcp.fits and /grp/crds/cache/references/hst/xaf1429el_wcp.fits initiated.
    CRDS  : DEBUG    Instantiating rules for reference type cos_wcptab.
    CRDS  : DEBUG    Rule DeepLook_COSOpt_elem: Reprocessing is not required.
    CRDS  : DEBUG    Rule DeepLook_COSOpt_elem: Selection rules have executed and the selected rows are the same.
    CRDS  : DEBUG    Removing table update for COS wcptab LBK617010:LBK617YRQ no effective change from reference 'X2I1559GL_WCP.FITS' --> 'XAF1429EL_WCP.FITS'
    CRDS  : INFO     0 errors
    CRDS  : INFO     0 warnings
    CRDS  : INFO     3 infos

CLEANUP: blow away the test cache

    >>> test_config.cleanup()

"""

def test():
    """Run module tests,  for now just doctests only."""
    import test_table_effects, doctest
    return doctest.testmod(test_table_effects)

if __name__ == "__main__":
    print(test())
