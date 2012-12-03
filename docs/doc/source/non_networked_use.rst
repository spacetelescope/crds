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

Certifying Files
----------------

CRDS has a module which will certify that a mapping or reference file is
valid,  for some limited definition of *valid*.   By design only valid files can
be submitted to the CRDS server and archive.

Certifying Mappings
~~~~~~~~~~~~~~~~~~~

For Mappings,  crds.certify will ensure that:

  * the mapping and it's descendents successfully load
  * the mapping checksum is valid
  * the mapping does not contain hostile code
  * the mapping defines certain generic parameters
  * references required by the mapping exist on the local file system
  
You can check the validity of your mapping or reference file like this::

  % python -m crds.certify /where/it/really/is/hst_acs_my_masterpiece.rmap
  0 errors 
  0 warnings 
  0 infos 

By default, running certify on a mapping *does not* verify that the required
reference files are valid,  only that they exist.

Later versions of CRDS may have additional semantic checks on the correctness of
Mappings but these are not yet implemented and hence fall to the developer to
verify in some other fashion.

Certifying Reference Files
~~~~~~~~~~~~~~~~~~~~~~~~~~

For reference files certify has better semantic checks.   For reference files,
crds.certify currently ensures that:

  * the FITS format is valid
  * critical reference file header parameters have acceptable values

You can certify reference files the same way as mappings,  like this::

  % python -m crds.certify /where/it/is/my_reference_file.fits
  0 errors 
  0 warnings 
  0 infos 


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

Adding Checksums
~~~~~~~~~~~~~~~~

Once you've finished your masterpiece ReferenceMapping,  it can be sealed with
a checksum like this::

   % python -m crds.checksum /where/it/really/is/hst_acs_my_masterpiece.rmap


Which Mappings Use this File?
-----------------------------

Particularly in legacy contexts,  such as HST,  reference file names can be
rather cryptic.   Further,  by design CRDS will have a complex set of fluid
and versioned mappings.   Hence it may become rather difficult for a human to
discern which mappings refer to a particular mapping or reference file.   CRDS
has the crds.uses module to help answer this question::

   % python -m crds.uses hst kcb1734ij_a2d.fits
   hst.pmap
   hst_acs.imap
   hst_acs_atodtab.rmap
   
The first parameter indicates the observatory for which files should be
considered.   Additional parameters specify mapping or reference files which are
used.   The printed result consists of those mappings which directly or 
indirectly refer to the used files.

Note that the above results represent the highly simplified context of the
current HST prototype,  prior to the introduction of mapping evolution and
version numbering.   In practice,  each of the above files might include several
numbered versions,  and some versions of the above files might not require
kcb1734ij_a2d.fits.

crds.uses knows about only the mappings cached locally.  Hence the official CRDS
server will have a more definitive answer than someone's development machine.
The CRDS web site has a link for running crds.uses over all known "official"
mappings.   crds.uses is especially applicable for understanding the implications
of blacklisting a particular file;  when a file is blacklisted,   all files
indicated by crds.uses are also blacklisted.

Finding Matches for a Reference in a Context
--------------------------------------------

Given a particular context and reference file name,  CRDS can also determine all
possible matches for the reference within that context::

  % python -m crds.matches hst.pmap kcb1734ij_a2d.fits

  ((('observatory', 'hst'), ('INSTRUME', 'acs'), ('filekind', 'atodtab')), (('DETECTOR', 'HRC'), ('CCDGAIN', '1.0'), ('CCDAMP', 'A')), (('DATE-OBS', '1992-01-01'), ('TIME-OBS', '00:00:00'))) 
  ((('observatory', 'hst'), ('INSTRUME', 'acs'), ('filekind', 'atodtab')), (('DETECTOR', 'HRC'), ('CCDGAIN', '1.0'), ('CCDAMP', 'ABCD')), (('DATE-OBS', '1992-01-01'), ('TIME-OBS', '00:00:00'))) 
  ((('observatory', 'hst'), ('INSTRUME', 'acs'), ('filekind', 'atodtab')), (('DETECTOR', 'HRC'), ('CCDGAIN', '1.0'), ('CCDAMP', 'AD')), (('DATE-OBS', '1992-01-01'), ('TIME-OBS', '00:00:00'))) 
  ((('observatory', 'hst'), ('INSTRUME', 'acs'), ('filekind', 'atodtab')), (('DETECTOR', 'HRC'), ('CCDGAIN', '1.0'), ('CCDAMP', 'B')), (('DATE-OBS', '1992-01-01'), ('TIME-OBS', '00:00:00'))) 
  ((('observatory', 'hst'), ('INSTRUME', 'acs'), ('filekind', 'atodtab')), (('DETECTOR', 'HRC'), ('CCDGAIN', '1.0'), ('CCDAMP', 'BC')), (('DATE-OBS', '1992-01-01'), ('TIME-OBS', '00:00:00'))) 
  ((('observatory', 'hst'), ('INSTRUME', 'acs'), ('filekind', 'atodtab')), (('DETECTOR', 'HRC'), ('CCDGAIN', '1.0'), ('CCDAMP', 'C')), (('DATE-OBS', '1992-01-01'), ('TIME-OBS', '00:00:00'))) 
  ((('observatory', 'hst'), ('INSTRUME', 'acs'), ('filekind', 'atodtab')), (('DETECTOR', 'HRC'), ('CCDGAIN', '1.0'), ('CCDAMP', 'D')), (('DATE-OBS', '1992-01-01'), ('TIME-OBS', '00:00:00'))) 
  ((('observatory', 'hst'), ('INSTRUME', 'acs'), ('filekind', 'atodtab')), (('DETECTOR', 'HRC'), ('CCDGAIN', '2.0'), ('CCDAMP', 'A')), (('DATE-OBS', '1992-01-01'), ('TIME-OBS', '00:00:00'))) 
  ((('observatory', 'hst'), ('INSTRUME', 'acs'), ('filekind', 'atodtab')), (('DETECTOR', 'HRC'), ('CCDGAIN', '2.0'), ('CCDAMP', 'ABCD')), (('DATE-OBS', '1992-01-01'), ('TIME-OBS', '00:00:00'))) 
  ((('observatory', 'hst'), ('INSTRUME', 'acs'), ('filekind', 'atodtab')), (('DETECTOR', 'HRC'), ('CCDGAIN', '2.0'), ('CCDAMP', 'AD')), (('DATE-OBS', '1992-01-01'), ('TIME-OBS', '00:00:00'))) 
  ((('observatory', 'hst'), ('INSTRUME', 'acs'), ('filekind', 'atodtab')), (('DETECTOR', 'HRC'), ('CCDGAIN', '2.0'), ('CCDAMP', 'B')), (('DATE-OBS', '1992-01-01'), ('TIME-OBS', '00:00:00'))) 
  ((('observatory', 'hst'), ('INSTRUME', 'acs'), ('filekind', 'atodtab')), (('DETECTOR', 'HRC'), ('CCDGAIN', '2.0'), ('CCDAMP', 'BC')), (('DATE-OBS', '1992-01-01'), ('TIME-OBS', '00:00:00'))) 
  ((('observatory', 'hst'), ('INSTRUME', 'acs'), ('filekind', 'atodtab')), (('DETECTOR', 'HRC'), ('CCDGAIN', '2.0'), ('CCDAMP', 'C')), (('DATE-OBS', '1992-01-01'), ('TIME-OBS', '00:00:00'))) 
  ((('observatory', 'hst'), ('INSTRUME', 'acs'), ('filekind', 'atodtab')), (('DETECTOR', 'HRC'), ('CCDGAIN', '2.0'), ('CCDAMP', 'D')), (('DATE-OBS', '1992-01-01'), ('TIME-OBS', '00:00:00'))) 
  ...
   
What is printed out is a sequence of match tuples,  with each tuple nominally
consisting of three parts::

  (pmap_imap_rmap_path, match, use_after)
  
Each part in turn consists of nested tuples of the form::

  (parkey, value)
  
