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



Adding Checksums
----------------


Certifying Files
----------------


Which Mappings Reference this File?
-----------------------------------

