"""
Bestrefs has a number of command line parameters which make it operate in different modes. 

-----------
NEW CONTEXT
-----------

crds.bestrefs always computes best references with respect to a context which can be explicitly specified with the 
--new-context parameter.    If no --new-context is specified,  the default operational context is determined by 
consulting the CRDS server or looking in the local cache as a fallback.  

------------------------
LOOKUP PARAMETER SOURCES
------------------------

The two primary modes for bestrefs involve the source of reference file matching parameters.   Conceptually 
lookup parameters are always associated with particular datasets and used to identify the references
required to process those datasets.

The options --files, --datasets, --instruments, and --all determine the source of lookup parameters:

1. To find best references for a list of files do something like this:

    % python -m crds.bestrefs --new-context hst.pmap --files j8bt05njq_raw.fits j8bt06o6q_raw.fits j8bt09jcq_raw.fits

the first parameter, hst.pmap,  is the context with respect to which best references are determined.

2. To find best references for a list of catalog dataset ids do something like this:

    % python -m crds.bestrefs --new-context hst.pmap --datasets j8bt05njq j8bt06o6q j8bt09jcq

3. To do mass scale testing for all cataloged datasets for a particular instrument(s) do:

    % python -m crds.bestrefs --new-context hst.pmap --instruments acs

4. To do mass scale testing for all supported instruments for all cataloged datasets do:

    % python -m crds.bestrefs --new-context hst.pmap --all

----------------
COMPARISON MODES
----------------

The --old-context and --compare-source-bestrefs parameters define the best references comparison mode.  Each names
the origin of a set of prior recommendations and implicitly requests a comparison to the recommendations from 
the newly computed bestrefs determined by --new-context.

CONTEXT-TO-CONTEXT
..................

--old-context can be used to specify a second context for which bestrefs are dynamically computed; --old-context implies 
that a bestrefs comparison will be made with --new-context.   

PRIOR SOURCE RECOMMENDATIONS
............................

--compare-source-bestrefs requests that the bestrefs from --new-context be compared to the bestrefs which are
recorded with the lookup parameter data,  either in the file headers of data files,  or in the catalog.   In both
cases the prior best references are recorded static values,  not dynamically computed bestrefs.

------------
UPDATE MODES
------------

Currently there is only one update mode.   When --files are specified as the input source,  --update-bestrefs can 
also be specified to update the input data file headers with new bestrefs recommendations.   In this case the data
files are used as both the source of matching parameters and as the destination for best reference recommendations.

------------
OUTPUT MODES
------------

crds.bestrefs supports several output modes for bestrefs and comparison results.

If --print-affected is specified,  crds.bestrefs will print out the name of any file for which at least one update for
one reference type was recommended.   This is essentially a list of files to be reprocessed with new references.

    % python -m crds.bestrefs --new-context hst.pmap --files j8bt05njq_raw.fits j8bt06o6q_raw.fits j8bt09jcq_raw.fits --compare-source-bestrefs --print-affected
    j8bt05njq_raw.fits
    j8bt06o6q_raw.fits
    j8bt09jcq_raw.fits

----------
TEST CASES
----------

>>> import os
>>> os.environ["CRDS_PATH"] = os.path.join(os.getcwd(), "test_cache")
>>> os.environ["CRDS_SERVER_URL"] = "http://hst-crds.stsci.edu"
>>> from crds import log
>>> log.set_test_mode()

>>> from crds.bestrefs import BestrefsScript

Compute simple bestrefs for 3 files:

    >>> case = BestrefsScript(argv="bestrefs.py --new-context hst.pmap --files data/j8bt05njq_raw.fits data/j8bt06o6q_raw.fits data/j8bt09jcq_raw.fits")
    >>> case.files
    ['data/j8bt05njq_raw.fits', 'data/j8bt06o6q_raw.fits', 'data/j8bt09jcq_raw.fits']
    >>> case.new_context
    'hst.pmap'
    >>> case.run()
    CRDS  : INFO     No comparison context or source comparison requested.
    CRDS  : INFO     0 errors
    CRDS  : INFO     0 warnings
    CRDS  : INFO     1 infos

Compute and print files with at least one reference change:

    >>> case = BestrefsScript(argv="bestrefs.py --new-context hst.pmap --files data/j8bt05njq_raw.fits data/j8bt06o6q_raw.fits data/j8bt09jcq_raw.fits --print-affected")
    >>> case.files
    ['data/j8bt05njq_raw.fits', 'data/j8bt06o6q_raw.fits', 'data/j8bt09jcq_raw.fits']
    >>> case.run()
    CRDS  : WARNING  No comparison bestref for data 'data/j8bt05njq_raw.fits' type 'IMPHTTAB' recommending --> 'W3M1716TJ_IMP.FITS'
    CRDS  : WARNING  No comparison bestref for data 'data/j8bt05njq_raw.fits' type 'NPOLFILE' recommending --> 'V9718263J_NPL.FITS'
    CRDS  : WARNING  No comparison bestref for data 'data/j8bt06o6q_raw.fits' type 'IMPHTTAB' recommending --> 'W3M1716TJ_IMP.FITS'
    CRDS  : WARNING  No comparison bestref for data 'data/j8bt06o6q_raw.fits' type 'NPOLFILE' recommending --> 'V9718264J_NPL.FITS'
    CRDS  : WARNING  No comparison bestref for data 'data/j8bt09jcq_raw.fits' type 'IMPHTTAB' recommending --> 'W3M1716TJ_IMP.FITS'
    CRDS  : WARNING  No comparison bestref for data 'data/j8bt09jcq_raw.fits' type 'NPOLFILE' recommending --> 'V9718260J_NPL.FITS'
    data/j8bt05njq_raw.fits
    data/j8bt09jcq_raw.fits
    data/j8bt06o6q_raw.fits
    CRDS  : INFO     0 errors
    CRDS  : INFO     6 warnings
    CRDS  : INFO     4 infos

Compute simple bestrefs for 3 files using the default context from the server:

    >>> case = BestrefsScript(argv="bestrefs.py --files data/j8bt05njq_raw.fits data/j8bt06o6q_raw.fits data/j8bt09jcq_raw.fits")
    >>> case.files
    ['data/j8bt05njq_raw.fits', 'data/j8bt06o6q_raw.fits', 'data/j8bt09jcq_raw.fits']

    Can't really know what the default context will be over time, so check vaguely.
    
    >>> case.new_context.startswith("hst") and case.new_context.endswith(".pmap")
    True
    >>> case.run()
    CRDS  : INFO     No comparison context or source comparison requested.
    CRDS  : INFO     0 errors
    CRDS  : INFO     6 warnings
    CRDS  : INFO     8 infos

Compute simple bestrefs for 3 catalog datasets using hst.pmap:

    >>> case = BestrefsScript(argv="bestrefs.py --new-context hst.pmap  --datasets j59l54010 j6d508010 j6d508011")
    >>> case.args.datasets
    ['j59l54010', 'j6d508010', 'j6d508011']
    >>> case.run()
    
Compute comparison bestrefs between two contexts:

    >>> case = BestrefsScript(argv="bestrefs.py --new-context data/hst_9999.pmap  --old-context hst.pmap --files data/j8bt05njq_raw.fits data/j8bt06o6q_raw.fits data/j8bt09jcq_raw.fits --verbose")
    >>> case.run()

"""

def test():
    """Run module tests,  for now just doctests only."""
    import test_bestrefs, doctest
    return doctest.testmod(test_bestrefs)

if __name__ == "__main__":
    print(test())
