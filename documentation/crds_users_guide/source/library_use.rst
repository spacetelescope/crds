Library Use
===========

This section describes the formal top level interfaces for CRDS intended as the
main entry points for the calibration software or basic use.  Functions
at this level should be assumed to require network connectivity with the CRDS
server.   

To function correctly,  these API calls may require the user to set the
environment variables CRDS_SERVER_URL and CRDS_PATH.   See the section on
*Installation* for more details.

crds.getreferences()
....................

Given  dataset header containing parameters required to determine best
references, and optionally a specific .pmap to use as the best references
context,  and optionally a list of the reference types for which reference files
are to be determined,  getreferences() will determine best references,  cache
them on the local file system,  and return a mapping from reference types to
reference file paths::

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


crds.get_default_context()
..........................

get_default_context() returns the name of the pipeline mapping which is 
currently in operational use.   When no

The default context defines the matching rules used to determine best 
reference files for a given set of parameters::

    def get_default_context():
        """Return the name of the latest pipeline mapping in use for processing
        files.  
        
        Returns   
        -------
        pipeline context name
        
            e.g.   'hst_0007.pmap'
        """

        
Overview of Features
....................
Using the crds package it's possible to:

- Load and operate on rmaps
- Determine best reference files for a dataset
- Check mapping syntax and verify checksum
- Certify that a mapping and all it's dependencies exist and are valid
- Certify that a reference file meets important constraints
- Add checksums to mappings
- Determine the closure of mappings which reference a particular file.

Important Modules
.................

There are really two important modules which anyone doing low-level and non-
networked CRDS development will first be concerned with:

- crds.rmap module
    -- defines classes which load and operate on mapping files
        * Mapping
        * PipelineContext (.pmap)
        * InstrumentContext (.imap),
        * ReferenceMapping (.rmap)
    -- defines get_cached_mapping() function
        * loads and caches a Mapping or subclass instances from files,  
          typically this is a recursive process loading pipeline or instrument
          contexts as well as all associated reference mappings.
        * this *cache* is an object cache to speed up access to mappings,  
          not the file *cache* used by crds.client to avoid repeated network
          file transfers.
- crds.selectors module
    -- defines classes implementing best reference logic
       * MatchSelector
       * UseAfterSelector
       * Other experimental Selector classes

Basic Operations on Mappings
............................

Loading Rmaps
+++++++++++++

Perhaps the most fundamental thing you can do with a CRDS mapping is create an
active object version by loading the file::

  % python
  >>> import crds.rmap as rmap
  >>> hst = rmap.load_mapping("hst.pmap")

The load_mapping() function will take any mapping and instantiate it and all of
it's child mappings into various nested Mapping subclasses:  PipelineContext, 
InstrumentContext, or ReferenceMapping.   

Loading an rmap implicitly screens it for invalid syntax and requires that the 
rmap's checksum (sha1sum) be valid by default.

Since HST has on the order of 70  mappings, this is a fairly slow process
requiring a couple seconds to execute.  In order to speed up repeated access to
the same Mapping,  there's a mapping cache maintained by the rmap module and
accessed like this::

  >>> hst = rmap.get_cached_mapping("hst.pmap")

The behavior of the cached mapping is identical to the "loaded" mapping and 
subsequent calls are nearly instant.

Seeing Referenced Names
+++++++++++++++++++++++

CRDS Mapping classes all know how to show you the files referenced by themselves
and their descendents.   The ACS instrument context has a reference mapping for
each of it's associated file kinds::

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

The ACS atod reference mapping (rmap) refers to 4 different reference files::

  >>> acs_atod = rmap.get_cached_mapping("hst_acs_atodtab.rmap")
  >>> acs_atod.reference_names()
  ['j4d1435hj_a2d.fits',
   'kcb1734hj_a2d.fits',
   'kcb1734ij_a2d.fits',
   't3n1116mj_a2d.fits']


Computing Best References
+++++++++++++++++++++++++

The primary function of CRDS is the computation of best reference files based
upon a dictionary of dataset metadata.   Hence,  both an InstrumentContext and a
ReferenceMapping can meaningfully return the best references for a dataset based
upon a parameter dictionary.   It's possible define a header as any Python 
dictionary provided you have sufficient knowledge of the parameters::

>>>  hdr = { ... what matters most ... }

On the other hand,  if your dataset is a FITS file and you want to do something
quick and dirty,  you can ask CRDS what dataset metadata may matter for 
determining best references::

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

Here I say *may matter* because CRDS is currently dumb about specific instrument
configurations and is returning metadata about filekinds which may be
inappropriate.

Once you have your dataset parameters,  you can ask an InstrumentContext for
the best references for *all* filekinds for that instrument::

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

In the above results,  FITS files are the recommended best references,  while
a value of "NOT FOUND n/a" indicates that no result was expected for the current
instrument mode as defined in the header.   Other values of "NOT FOUND xxx"
include an error message xxx which hints at why no result was found,  such as
an invalid dataset parameter value or simply a matching failure.

You can ask a ReferenceMapping for the best reference for single the filekind
it manages::

  >>> acs_atod.get_best_ref(hdr)
  >>> 'kcb1734ij_a2d.fits'

Often it is convenient to simply refer to a pipeline/observatory context file,
and hence PipelineContext can also return the best references for a dataset,
but this is really just shorthand for returning the best references for the 
instrument of that dataset::

  >>> hdr = hst.get_minimum_header("test_data/j8bt05njq_raw.fits")
  >>> hst.get_best_references(hdr)
  ... for this hdr, same as acs.get_best_references(hdr) ...

Here it is critical to call get_minimum_header on the pipeline context, hst,
because this will make it include the "INSTRUME" parameter needed to choose
the ACS instrument.

Mapping Checksums
.................

CRDS mappings contain sha1sum checksums over the entire contents of the mapping,
with the exception of the checksum itself.   When a CRDS Mapping of any kind is
loaded,  the checksum is transparently verified to ensure that the Mapping
contents are intact.   

Ignoring Checksums!
+++++++++++++++++++

Ordinarily,  during pipeline operations,  ignoring checksums should not be done.
Ironically though,  the first thing you may want to do as a developer is ignore 
the checksum while you load a mapping you've edited::

  >>> pipeline = rmap.load_mapping("hst.pmap", ignore_checksum=True)

Alternately you can set an environment variable to ignore the mapping checksum
while you iterate on new versions of the mapping::

   % setenv CRDS_IGNORE_MAPPING_CHECKSUM 1

Adding Checksums
++++++++++++++++

Once you've finished your masterpiece ReferenceMapping,  it can be sealed with
a checksum like this::

   % crds checksum /where/it/really/is/hst_acs_my_masterpiece.rmap
  
