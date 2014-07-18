Core Library Functions
======================

This section describes using the core crds package without access to the
network.  Using the crds package in isolation it is possible to develop and use
new reference files and mappings.   Note that a default install of CRDS will
also include crds.client and crds.hst or crds.jwst.  In particular,  the 
observatory packages define how mappings are named, where they are placed,
and how reference files are checked.

Overview of Features
--------------------
Using the crds package it's possible to:

- Load and operate on rmaps
- Determine best reference files for a dataset
- Check mapping syntax and verify checksum
- Certify that a mapping and all it's dependencies exist and are valid
- Certify that a reference file meets important constraints
- Add checksums to mappings
- Determine the closure of mappings which reference a particular file.

Important Modules
-----------------

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
----------------------------

Loading Rmaps
~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~

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
-----------------

CRDS mappings contain sha1sum checksums over the entire contents of the mapping,
with the exception of the checksum itself.   When a CRDS Mapping of any kind is
loaded,  the checksum is transparently verified to ensure that the Mapping
contents are intact.   

Ignoring Checksums!
~~~~~~~~~~~~~~~~~~~

Ordinarily,  during pipeline operations,  ignoring checksums should not be done.
Ironically though,  the first thing you may want to do as a developer is ignore 
the checksum while you load a mapping you've edited::

  >>> pipeline = rmap.load_mapping("hst.pmap", ignore_checksum=True)

Alternately you can set an environment variable to ignore the mapping checksum
while you iterate on new versions of the mapping::

   % setenv CRDS_IGNORE_MAPPING_CHECKSUM 1

Adding Checksums
~~~~~~~~~~~~~~~~

Once you've finished your masterpiece ReferenceMapping,  it can be sealed with
a checksum like this::

   % python -m crds.checksum /where/it/really/is/hst_acs_my_masterpiece.rmap


