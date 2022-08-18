Library Use
===========

This section describes the formal top level interfaces for CRDS intended as the
main entry points for the calibration software or basic use.  Functions
at this level should be assumed to require network connectivity with the CRDS
server.   

To function correctly,  these API calls may require the user to set the
environment variables `CRDS_SERVER_URL` and `CRDS_PATH`. See the section on
*Installation* for more details.

crds.getrecommendations()
.........................

Given dataset header containing parameters required to determine best
references, and optionally a specific .pmap to use as the best references
context, and optionally a list of the reference types for which reference files
are to be determined, getrecommendations() will determine best references
and return a mapping from reference types to reference file basenames:

  .. code-block:: python
    
      def getrecommendations(parameters, reftypes=None, context=None, ignore_cache=False,
                       observatory="jwst", fast=False):
          """
          getrecommendations() returns the best references for the specified `parameters`
          and pipeline `context`.   Unlike getreferences(),  getrecommendations() does
          not attempt to cache the files locally.
              
          parameters      { str:  str,int,float,bool, ... }
          
            `parameters` should be a dictionary-like object mapping best reference 
            matching parameters to their values for this dataset.
          
          reftypes        [ str, ... ] 
          
            If `reftypes` is None,  return all possible reference types.   Otherwise
            return the reference types specified by `reftypes`.
          
          context         str
          
            Specifies the pipeline context, i.e. specific version (.pmap) of CRDS
            rules used to do the best references match.  If `context` is None, use
            the latest available context.

         ignore_cache    bool

           If `ignore_cache` is True,  download files from server even if already present.
    
         observatory     str
    
           nominally 'jwst' or 'hst'.
    
           fast            bool
    
          If fast is True, skip verbose output, parameter screening, implicit 
          config update, and bad reference checking.
    
         Returns { reftype : bestref_basename, ... }
    
           returns a mapping from types requested in `reftypes` to the path for each 
           cached reference file.
        """

crds.getreferences()
....................

Given dataset header containing parameters required to determine best
references, and optionally a specific .pmap to use as the best references
context, and optionally a list of the reference types for which reference files
are to be determined, getreferences() will determine best references, cache
them on the local file system, and return a mapping from reference types to
reference file paths:

  .. code-block:: python

      def getreferences(parameters, reftypes=None, context=None, ignore_cache=False,
                        observatory="jwst"):
          """Return the mapping from the requested `reftypes` to their 
          corresponding best reference file paths appropriate for a dataset 
          described by `parameters` with CRDS rules defined by `context`::
          
          parameters :    A mapping of parameter names to parameter value
                  strings for parameters which define best reference file matches.
      
                  { str  :   str, int, float, bool }
             
                 e.g.  {
                         'INSTRUME' : 'ACS',
                         'CCDAMP' : 'ABCD',
                         'CCDGAIN' : '2.0',
                         ...
                      }
      
          reftypes :    A list of reference type names.   For HST these are the keywords
                       used to record reference files in dataset headers.   For JWST,  these
                       are the identifiers which will appear in instrument contexts and
                       reference mappings.
                  
                      e.g.  [ 'darkfile', 'biasfile']
                      
                      If reftypes is None,  return all reference types defined by
                      the instrument mapping for the instrument specified in 
                      `parameters`.
                      
          context :   The name of the pipeline context mapping which should be
                  used to define best reference lookup rules,  or None.  If 
                  `context` is None,  use the latest operational pipeline mapping.
                  
                  str
                  
                  e.g. 'hst_0037.pmap'
                  
          ignore_cache :   If True,  download all required mappings and references
                  from the CRDS server.  If False,  download only those files not
                  already in the local caches.
          
          observatory :  The name of the observatory this query applies to,  needed
                  to support both 'hst' and 'jwst' from a single server.

          Returns
          -------
                  a mapping from reftypes to cached best reference file paths.
          
                  { str : str }
                  
                  e.g.   {
                      'biasfile' : '/path/to/file/hst_acs_biasfile_0042.fits',
                      'darkfile' : '/path/to/file/hst_acs_darkfile_0056.fits',
                      }
          """

crds.assign_bestrefs()
......................

The `assign_bestrefs()` higher level function call simulates the behavior of the
crds bestrefs program used in the archive pipeline for HST.  Essentially, it
populates the headers of FITS dataset files with the best choice for each
reference type:

  .. code-block:: python

      def assign_bestrefs(filepaths, context=None, reftypes=(),
                        sync_references=False, verbosity=-1):
        """Assign best references to FITS files specified by `filepaths` 
        filling in appropriate reference type keywords.
    
        Define best references using either .pmap `context` or the default
        CRDS operational context if context=None.
    
        If `reftypes` is defined, assign bestrefs to only the listed
        reftypes, otherwise assign all reftypes.
    
        If `sync_references` is True, download any missing reference files
        to the CRDS cache.
    
        Verbosity defines the level of CRDS log output:
        
        verbosity=-3    feeling lucky, no output
        verbosity=-2    only errors
        verbosity=-1    only warnings and errors
        verbosity=0     info, warnings, and errors
        verbosity=10    info + minimal progress output
        verbosity=30    info + simplified bestref assignments
        verbosity=50    info + keywords + exact values (standard)
        verbosity=60    info + bestrefs elimination
        ...
        -3 <= verbosity <= 100
    
        NOTE: While assign_bestrefs() may work for JWST, it is primarily intended
        for HST and does not precisely simulate the actions performed by the JWST
        CAL s/w to handle reference files.  The underlying machinery is the same,
        but header updates are not guaranteed to be identical, particularly
        regarding the reference types which are assigned values.
    
        Returns  count of errors
        """

crds.get_default_context()
..........................

`get_default_context()` returns the name of the pipeline mapping which is 
currently in operational use.

The default context defines the matching rules used to determine best 
reference files for a given set of parameters:

  .. code-block:: python

      def get_default_context():
          """Return the name of the latest pipeline mapping in use for processing
          files.  
          
          Returns   
          -------
          pipeline context name
          
              e.g.   'hst_0007.pmap'
          """

        
Basic Operations on Mappings
............................

Loading Rmaps
+++++++++++++

Perhaps the most fundamental thing you can do with a CRDS mapping is create an
active object version by loading the file:

  .. code-block:: python

      >>> import crds.rmap as rmap
      >>> hst = rmap.load_mapping("hst.pmap")

The `load_mapping()` function will take any mapping and instantiate it and all of
its child mappings into various nested Mapping subclasses:  `PipelineContext`, 
`InstrumentContext`, or `ReferenceMapping`.   

Loading an rmap implicitly screens it for invalid syntax and requires that the 
rmap's checksum (sha1sum) be valid by default.

Since HST has on the order of 70 mappings, this is a fairly slow process
requiring a couple seconds to execute.  In order to speed up repeated access to
the same Mapping, there's a mapping cache maintained by the rmap module and
accessed like this:

  .. code-block:: python

      >>> hst = rmap.get_cached_mapping("hst.pmap")

The behavior of the cached mapping is identical to the "loaded" mapping and 
subsequent calls are nearly instant.

Seeing Referenced Names
+++++++++++++++++++++++

CRDS Mapping classes all know how to show you the files referenced by themselves
and their descendents. The ACS instrument context has a reference mapping for
each of it's associated file kinds:

  .. code-block:: python

      >>> acs = rmap.get_cached_mapping("hst_acs.imap")
      >>> acs.mapping_names()
      ['hst_acs.imap',
       'hst_acs_idctab.rmap',
       'hst_acs_darkfile.rmap',
       'hst_acs_atodtab.rmap',
       'hst_acs_cfltfile.rmap',
       'hst_acs_spottab.rmap',
       'hst_acs_mlintab.rmap',
       'hst_acs_dgeofile.rmap',
       'hst_acs_bpixtab.rmap',
       'hst_acs_oscntab.rmap',
       'hst_acs_ccdtab.rmap',
       'hst_acs_crrejtab.rmap',
       'hst_acs_pfltfile.rmap',
       'hst_acs_biasfile.rmap',
       'hst_acs_mdriztab.rmap']

The ACS atod reference mapping (rmap) refers to 4 different reference files:

  .. code-block:: python

      >>> acs_atod = rmap.get_cached_mapping("hst_acs_atodtab.rmap")
      >>> acs_atod.reference_names()
      ['j4d1435hj_a2d.fits',
       'kcb1734hj_a2d.fits',
       'kcb1734ij_a2d.fits',
       't3n1116mj_a2d.fits']


Computing Best References
+++++++++++++++++++++++++

The primary function of CRDS is the computation of best reference files based
upon a dictionary of dataset metadata. Hence, both an `InstrumentContext` and a
`ReferenceMapping` can meaningfully return the best references for a dataset based
upon a parameter dictionary. It's possible to define a header as any Python 
dictionary provided you have sufficient knowledge of the parameters:

  .. code-block:: python

      >>>  hdr = { ... what matters most ... }

On the other hand, if your dataset is a FITS file and you want to do something
quick and dirty, you can ask CRDS what dataset metadata may matter for 
determining best references:

  .. code-block:: python

      >>> hdr = acs.get_minimum_header("test_data/j8bt05njq_raw.fits")
      {'CCDAMP': 'C',
       'CCDGAIN': '2.0',
       'DATE-OBS': '2002-04-13',
       'DETECTOR': 'HRC',
       'FILTER1': 'F555W',
       'FILTER2': 'CLEAR2S',
       'FW1OFFST': '0.0',
       'FW2OFFST': '0.0',
       'FWSOFFST': '0.0',
       'LTV1': '19.0',
       'LTV2': '0.0',
       'NAXIS1': '1062.0',
       'NAXIS2': '1044.0',
       'OBSTYPE': 'IMAGING',
       'TIME-OBS': '18:16:35'}

Here we say *may matter* because CRDS is currently unaware of specific instrument
configurations and is returning metadata about filekinds which may be
inappropriate.

Once you have your dataset parameters, you can ask an `InstrumentContext` for
the best references for *all* filekinds for that instrument:

  .. code-block:: python

      >>> acs.get_best_references(hdr)
      {'atodtab': 'kcb1734ij_a2d.fits',
      'biasfile': 'm4r1753rj_bia.fits',
      'bpixtab': 'm8r09169j_bpx.fits',
      'ccdtab': 'o1515069j_ccd.fits',
      'cfltfile': 'NOT FOUND n/a',
      'crrejtab': 'n4e12510j_crr.fits',
      'darkfile': 'n3o1059hj_drk.fits',
      'dgeofile': 'o8u2214mj_dxy.fits',
      'flshfile': 'NOT FOUND n/a',
      'idctab': 'p7d1548qj_idc.fits',
      'imphttab': 'vbb18105j_imp.fits',
      'mdriztab': 'ub215378j_mdz.fits',
      'mlintab': 'NOT FOUND n/a',
      'oscntab': 'm2j1057pj_osc.fits',
      'pfltfile': 'o3u1448rj_pfl.fits',
      'shadfile': 'kcb1734pj_shd.fits',
      'spottab': 'NOT FOUND n/a'}

In the above results, FITS files are the recommended best references, while
a value of "NOT FOUND n/a" indicates that no result was expected for the current
instrument mode as defined in the header. Other values of "NOT FOUND xxx"
include an error message xxx which hints at why no result was found, such as
an invalid dataset parameter value or simply a matching failure.

You can ask a `ReferenceMapping` for the best reference for single the filekind
it manages:

  .. code-block:: python

      >>> acs_atod.get_best_ref(hdr)
      >>> 'kcb1734ij_a2d.fits'

Often it is convenient to simply refer to a pipeline/observatory context file,
and hence `PipelineContext` can also return the best references for a dataset,
but this is really just shorthand for returning the best references for the 
instrument of that dataset:

  .. code-block:: python

      >>> hdr = hst.get_minimum_header("test_data/j8bt05njq_raw.fits")
      >>> hst.get_best_references(hdr)
      ... for this hdr, same as acs.get_best_references(hdr) ...

Here it is critical to call get_minimum_header on the pipeline context, hst,
because this will make it include the "INSTRUME" parameter needed to choose
the ACS instrument.

Mapping Checksums
.................

CRDS mappings contain sha1sum checksums over the entire contents of the mapping,
with the exception of the checksum itself. When a CRDS Mapping of any kind is
loaded, the checksum is transparently verified to ensure that the Mapping
contents are intact.

Ignoring Checksums!
+++++++++++++++++++

Ordinarily, during pipeline operations, ignoring checksums should not be done.
Ironically though, the first thing you may want to do as a developer is ignore 
the checksum while you load a mapping you've edited:

  .. code-block:: python

      >>> pipeline = rmap.load_mapping("hst.pmap", ignore_checksum=True)

Alternately you can set an environment variable to ignore the mapping checksum
while you iterate on new versions of the mapping:

  .. code-block:: bash

      $ export CRDS_IGNORE_MAPPING_CHECKSUM=1

Adding Checksums
++++++++++++++++

Once you've finished your masterpiece `ReferenceMapping`, it can be sealed with
a checksum like this:

  .. code-block:: bash

      $ crds checksum /where/it/really/is/hst_acs_my_masterpiece.rmap
