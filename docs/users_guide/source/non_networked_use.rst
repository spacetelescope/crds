Non-Networked Use
=================

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
  >>> ctx = rmap.load_mapping("hst.pmap")

The load_mapping() function will take any mapping and instantiate it and all of
it's child mappings into various nested Mapping subclasses:  PipelineContext, 
InstrumentContext, or ReferenceMapping.   

Loading an rmap implicitly screens it for invalid syntax and requires that the 
rmap's checksum (sha1sum) be valid by default.

Since HST has on the order of 70  mappings, this is a fairly slow process
requiring a couple seconds to execute.  In order to speed up repeated access to
the same Mapping,  there's a mapping cache maintained by the rmap module and
accessed like this::

  >>> ctx = rmap.get_cached_mapping("hst.pmap")

The behavior of the cached mapping is identical to the "loaded" mapping and 
cached gets following the first are nearly instant.

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

  >>> atod = rmap.get_cached_mapping("hst_acs_atodtab.rmap")
  >>> atod.reference_names()
  ['j4d1435hj_a2d.fits',
   'kcb1734hj_a2d.fits',
   'kcb1734ij_a2d.fits',
   't3n1116mj_a2d.fits']


Computing Best References
~~~~~~~~~~~~~~~~~~~~~~~~~


Adding Checksums
----------------


Certifying Files
----------------


Which Mappings Reference this File?
-----------------------------------

