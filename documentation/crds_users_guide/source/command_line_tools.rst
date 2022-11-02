Command Line Tools
==================

Using the command line tools requires a local installation of the CRDS library.
Some of the command line tools also interact with the CRDS server in order to
implement their functionality.

Master program (crds)
---------------------

Much like git,  the `crds` master command provides a wrapper around
CRDS sub-commands like `list`, `certify`, `checksum`, `uniqname`, etc.:

  .. code-block:: bash

      $ crds --help
   
      usage: crds <command> <parameters...>

      'crds' is a wrapper used to invoke various CRDS sub-programs.

      For example, to assign HST best reference files, do:

          $ crds bestrefs --files *.fits  --update-bestrefs

      Available commands:
   
      list                -- print information about CRDS configuration, etc. 
      certify             -- check CRDS reference and rules files
      bestrefs            -- assign bestrefs to datasets, regressions, repro
      sync                -- manage local CRDS cache, download rules + references
      diff                -- difference CRDS rules and references
      rowdiff             -- difference reference tables
      matches             -- list matching criteria relative to particular rules
      checksum            -- update rmap checksum
      query_affected      -- download CRDS new reference files affected dataset IDs
      uniqname            -- rename HST files with new CDBS-style names
      get_synphot         -- download synphot references
      newcontext          -- automatically generates updated imaps and pmaps
      refactor            -- automatically modifies rmaps

      For more detail about individual commands use --help:

      e.g. crds list --help


.................
CRDS list command
.................

To print your CRDS configuration settings, use the `list` command:

.. code-block:: bash

    $ crds list --status

    CRDS Summary = 'The __rationale__ variable is no longer maintained and will be removed in a future release.'
    CRDS Version = '11.16.9, b11.4.0'
    CRDS_MODE = 'auto'
    CRDS_PATH = '/home/developer/crds_cache'
    CRDS_SERVER_URL = 'https://hst-crds.stsci.edu'
    Cache Locking = 'enabled, multiprocessing'
    Effective Context = 'hst_1006.pmap'
    Last Synced = '2022-08-16 11:32:12.247687'
    Python Executable = '/home/developer/venv/bin/python3'
    Python Version = '3.9.2.final.0'
    Readonly Cache = False



Specifying File Paths
---------------------

The command line tools operate on CRDS reference and mapping files both inside
and outside the CRDS cache.

In all releases CRDS has interpreted an absolute or relative path normally. For example, CRDS interprets `"./"` to mean "in the current working directory".

As of v7.3.1 and higher, CRDS assumes filenames without a path are in the current working directory. (Prior to v7.3.1 CRDS interpreted filenames with no path as meaning "located inside the CRDS cache" with a path based on CRDS_PATH and/or other environment variables.) For example, if the current working directory contains some .fits files, you can simply pass in `*.fits` to the `--files` arg and CRDS will now interpret this as `./*.fits` automatically (see examples below).

In all releases CRDS interprets a prefix of `crds://` as meaning "located inside
the CRDS cache" with a path defined based on `CRDS_PATH` and/or other environment
variables.  This same prefix is recorded in JWST and Roman data products and then
interpreted on the fly by calibration s/w as needed.

.................
In the CRDS cache
.................

After v7.3.1, to specify a file inside the CRDS file cache, use either an
explicit path (absolute or relative) or prefix the filename with crds:// to
imply a cache path based on CRDS_PATH and/or other CRDS environment variables.

  .. code-block:: bash

      $ crds diff crds://hst.pmap  crds://hst_0001.pmap  

Symbolic filenames like "jwst-edit" or "roman-edit" are assumed to be in the CRDS cache and
do not need or permit the crds:// prefix.

........................
In the current directory
........................
  
Files in the current working directory are referred to normally after 7.3.1:

  .. code-block:: bash
    
      $ crds diff hst_acs_darkfile_0250.rmap  hst_acs_darkfile_0251.rmap

Prior to 7.3.1 the easiest method was to use an explicit relative path:

  .. code-block:: bash
  
      $ crds diff ./hst_acs_darkfile_0250.rmap  ./hst_acs_darkfile_0251.rmap


crds.bestrefs
-------------

The `crds.bestrefs` program runs the CRDS library to interpret CRDS reference
file assignment rules with respect to dataset parameters.  

crds.bestrefs has several use cases which have different modes for fetching
input parameters, evaluating bestrefs and/or doing comparisons, and producing output.

crds.bestrefs runs in the HST archive pipeline to populate dataset headers FITS
keywords (e.g. DARKFILE) with best reference files.

Other modes of crds.bestrefs are used to support CRDS reprocessing or to test new
versions of CRDS rules.

The crds.bestrefs program is not normally used for JWST/Roman because best references 
are assigned automatically as a consequence of running the CAL code.

* Determines best references with respect to a context or contexts.   
* Optionally updates the headers of file-based data with new recommendations.
* Optionally compares new results to prior results.
* Optionally prints source data names affected by the new context.

.......................
crds.bestrefs use cases
.......................

  1. File (HST Pipeline) Mode

  The `--files` switch can be used to specify a list of FITS dataset files to
  process.  This is used in the HST pipeline in conjunction with
  `--update-headers` to fill in dataset FITS headers with recommended best
  references::

    $ crds bestrefs  --update-headers  --files j8bt05njq_raw.fits ...

  The outcome of this command is updating the best references in the FITS
  headers of the specified .fits files.

  Omitting `--update-headers` can be used to evaluate bestrefs without altering
  the input FITS files::

    $ crds bestrefs --print-new-references --files  j8bt05njq_raw.fits ...

  The `--new-context` switch can be used to choose a context which is not the
  current default::

    $ crds bestrefs --new-context hst_0457.pmap --files ...

  2. Reprocessing Mode

  The bestrefs reprocessing mode is used in conjunction with archive databases
  to determine datasets which should be reprocessed as a consequence of the
  delivery of new reference files.

  Reprocessing mode evaluates the same dataset parameters with respect to an
  old context and a new context and recommends reprocessing datasets where some
  reference file assignment changes.

  Bestrefs reprocessing mode is run automatically on the CRDS servers whenever
  new reference files are delivered, after the new CRDS context is selected for
  use by the archive pipeline.  It is run e.g. like this::

    $ crds bestrefs --affected-datasets --old-context  hst_0001.pmap --new-context hst_0002.pmap  
  
  --affected-datasets is a "bundle switch" that captures standard options for
  reprocessing.  See *crds bestrefs --help* for more information on individual
  switches.

  Running reprocessing mode requires setting `CRDS_SERVER_URL`.

  3. Context Testing Mode

  CRDS bestrefs and the archive reprocessing parameters can also provide a
  quick way to evaluate a new context and/or residual errors.  It can answer
  the question "what classes of errors still exist for the latest context with
  respect to known parameter sets?"

  Context testing mode can be run like this::

    $ crds bestrefs --check-context --new-context jwst-edit

  Context testing also requires setting *CRDS_SERVER_URL* to obtain archived
  dataset parameters.  Note that during JWST and Roman pre-I&T the archive database often
  contains parameter sets related to obsolete test cases.

  Undesired test cases can be weeded out like this::

    $ crds bestrefs --check-context --new-context jwst-edit --drop-ids JW93135336001_02102_00001.MIRIFUSHORT:JW93135336001_02102_00001.MIRIFUSHORT

...........
New Context
...........

crds.bestrefs always computes best references with respect to a context which
can be explicitly specified with the `--new-context` parameter.  If `--new-context`
is not specified, the default operational context is determined by consulting
the CRDS server or looking in the local cache.

...........
Old Context
...........

`--old-context` can be used to specify a second context for which bestrefs
are dynamically computed; `--old-context` implies that a bestrefs comparison
will be made with `--new-context`.  If `--old-context` is not specified, it
defaults to None.  `--old-context` is only used for context-to-context
comparisons,  nominally for CRDS repro.

........................
Lookup Parameter Sources
........................

The following methods can be used to define parameter sets for which to compute
best references:

  * `--files` can be used to specify a list of FITS or ASDF files from which to load
    parameters and optionally update headers.

  * `--instruments` can be used to specify a list of instruments.  Without
    `--diffs-only` or `--datasets-since` this choice selects ALL datasets for the
    specified instruments.

  * `--all-instruments` is shorthand for all `--instruments` supported by the project.
    This parameter can be so memory intensive as to be infeasible.

  * `--datasets` is used to specify a list of dataset IDs as would be found under --instruments.

  * `--load-pickles` can be used to specify a list of .pkl or .json files that define parameter
    sets.  These can most easily be created using `--save-pickle`.

................
Comparison Modes
................

The `--old-context` and `--compare-source-bestrefs` parameters define the best
references comparison mode.  Each names the origin of a set of prior
recommendations and implicitly requests a comparison to the recommendations
from the newly computed bestrefs determined by `--new-context`.

`--old-context CONTEXT` specifies that the reference results should be
*computed* using the named context.

`--compare-source-bestrefs` directs that prior reference assignments should be
taken from the same *stored source* which provides matching parameters.  These
could be from FITS or ASDF header keywords (e.g. DARKFILE), from live archive
parameters, or from prior parameter sets that have been stored in CRDS .json or
Python pickle files.

......................
Pickle and .json saves
......................

crds.bestrefs can load parameters and past results from a sequence of .pkl or
.json files using `--load-pickles`.  These are combined into a single parameter
source in command line order.

crds.bestrefs can save the parameters obtained from various sources into .pkl
or .json formatted save files using `--save-pickle`.  The single combined result
of multiple pickle or instrument parameter sources is saved.  The file
extension (.json or .pkl) defines the format used.

The preferred .json format defines a singleton { id: parameters}
dictionary on each line as a series of isolated .json objects.  Strictly
speaking only each individual line is .json,  but this localizes any errors.

.json format is preferred over .pkl because it is more transparent and robust
across different versions of Python.

.........
Verbosity
.........

crds.bestrefs has `--verbose` and `--verbosity=N` parameters which can increase the
amount of informational and debug output.  Verbosity ranges from 0..100 where 0
means "no debug output" and 100 means "all debug output".  50 is the default
for `--verbose`.

.........
Bad Files
.........

CRDS files can be designated as scientifically invalid on the CRDS server by
the CRDS team.  Knowledge of bad files is synchronized to remote caches by
crds.bestrefs and crds.sync.  By default, attempting to use bad rules or assign
bad references will generate errors and fail.  crds.bestrefs supports two
command line switches: `---allow-bad-rules` and `---allow-bad-references` to
override the default handling of bad files and enable their use with warnings.
Environment variables **CRDS_ALLOW_BAD_RULES** and
**CRDS_ALLOW_BAD_REFERENCES** can also be set to 1 to establish warnings rather
than errors as the default.


crds.sync 
---------

The CRDS sync tool is used to download CRDS rules and references from the CRDS
server.  While the sync tool can download files which are specified explicitly,
it's primary purpose is to download and manage files with respect to specified
versions of CRDS rules.   While the download directory of files can be
explicitly specified,  sync is primarily used to download files to a CRDS
cache which organizes and can locate files in a standard way.

.. tip::

  `crds.sync` detects the observatory based on whichever environment variables have
  been set, or a flag for the desired observatory included in the command (`--hst`, 
  `--jwst`, `--roman`). If no flag is included and the environment variables were 
  not set, `crds.sync` will default to JWST.

  To sync with HST without any environment variables set, you would need to include 
  the `--hst` flag:

  .. code-block:: bash
    
      crds.sync --hst --files 2cd1621ei_dkc.fits --output-dir

  Or set the correct server url environment variable first:

  .. code-block:: bash

      export CRDS_SERVER_URL=https://hst-crds.stsci.edu
      crds sync --files 2cd1621ei_dkc.fits --output-dir

  The below command produces an error because no environment variables were set 
  and the --hst flag is not included in the command, so crds.sync defaults 
  to JWST even though the user is trying to sync an HST file:

  .. code-block:: bash
    
      crds sync --files 2cd1621ei_dkc.fits --output-dir


* Dry-Running Cache Changes
   
   Since CRDS cache operations can involve significant network downloads, as a
   general note, crds.sync can be run with `---readonly-cache ---verbose`
   switches to better determine what the effects of any command should be.
   This can be used to gauge download sizes or list files before deleting them.

* Syncing Rules

    Typically syncing CRDS files is done with respect to particular CRDS
    contexts:
    
    Synced contexts can be explicitly listed:

      .. code-block:: bash
    
          $ crds sync  --contexts hst_0001.pmap hst_0002.pmap
      
    this will recursively download all the mappings referred to by .pmaps 0001
    and 0002.
    
    Synced contexts can be specified as a numerical range:

      .. code-block:: bash
    
          $ crds sync --range 1:3
    
    this will also recursively download all the mappings referred to by .pmaps
    0001, 002, 0003.
    
    Synced contexts can be specified as `--all` contexts:

      .. code-block:: bash
    
          $ crds sync --all
    
    this will recursively download all CRDS mappings for all time.

* Syncing References By Context
    
    Because complete reference downloads can be enormous, you must explicitly
    specify when you wish to fetch the references which are enumerated in
    particular CRDS rules:

      .. code-block:: bash
          
          $ crds sync  --contexts hst_0001.pmap hst_0002.pmap  --fetch-references
    
    will download all the references mentioned by contexts 0001 and 0002.   
        
* Syncing Specific Files

    Downloading an explicit list of files can be done by like this:

      .. code-block:: bash
    
          $ crds sync  --files hst_0001.pmap hst_acs_darkfile_0037.fits

    this will download only those two files.

    Specific files can also be downloaded using symbolic names and output
    to a specified directory,  for example,  like this:

      .. code-block:: bash

          $ crds sync --files jwst-nircam-flat-edit --output-dir .

    Will download the latest NIRCAM FLAT .rmap to the current working
    directory, which can be useful when doing CRDS rmap adjustments.
    
* Removing Unused Files
              
        CRDS rules from **unspecified** contexts can be removed like this:

          .. code-block:: bash
        
              $ crds sync  --contexts hst_0004.pmap hst_0005.pmap --purge-mappings
        
        while this would remove references which are *not* in contexts 4 or 5:

          .. code-block:: bash
        
              $ crds sync  --contexts hst_0004.pmap hst_0005.pmap --purge-references

        Again, both of these commands remove cached files which are not specified or implied.
    
* References for Dataset Files
    
        References required by particular dataset files can be cached like this:

          .. code-block:: bash
                
              $ crds sync  --contexts hst_0001.pmap hst_0002.pmap --dataset-files  <dataset_files...> e.g. acs_J8D219010.fits
        
        This will fetch all the references required to support the listed
        datasets for contexts 0001 and 0002.
        
        This mode does not update dataset file headers.  See also crds.bestrefs
        for similar functionality with header updates.
              
* References for Dataset Ids
    
        References for particular dataset ids can be cached like this:

          .. code-block:: bash
                
              $ crds sync  --contexts hst_0001.pmap hst_0002.pmap --dataset-ids  <ids...>  e.g. J6M915030
        
        This will fetch all the references required to support the listed dataset ids for contexts 0001 and 0002.
              
* Checking and Repairing Large Caches

    Large Institutional caches can be checked and/or repaired like this:

      .. code-block:: bash
    
          $ crds sync --contexts hst_0001.pmap --fetch-references --check-sha1sum --repair-files
    
    will download all the files in hst_0001.pmap not already present.
    
    Both mappings and references would then be checked for correct length,
    sha1sum, and status.
    
    Any files with bad length or checksum would then be deleted and
    re-downloaded.  This is really intended for a large *existing* cache.
    
    File checksum verification is optional because it is time consuming.
    Verifying the contents of the current HST shared cache requires 8-10 hours.
    In contrast, doing simple length, existence, and status checks takes 5-10
    minutes, sufficient for a quick check but not foolproof.
        
* Checking Smaller Caches,  Identifying Foreign Files

    The simplest approach for "repairing" a small cache is to delete it and
    resync.  One might do this after making temporary modifications to cached
    files to return to the archived version:

      .. code-block:: bash
    
          $ rm -rf $CRDS_PATH
          $ crds sync  -- ...  # repeat whatever syncs you did to cache files of interest
    
    A more complicated but also more precise approach can operate only on files
    already in the CRDS cache:

      .. code-block:: bash
        
          $ crds sync --repair-files --check-sha1sum --files `crds list --all --cached-mappings --cached-references`
       
    This approach works by using the crds.list command to dump the file names
    of all files in the CRDS cache and then using the crds.sync command to
    check exactly those files.
    
    Since crds.list will print the name of any file in the cache, not just
    files from CRDS, the second approach can also be used to detect (most
    likely test) files which are not from CRDS.
    
    For smaller caches `--check-sha1sum` is likekly to be less of a
    performance/runtime issue and should be used to detect files which have
    changed in contents but not in length.
  
* Removing Blacklisted or Rejected Files

    crds.sync can be used to remove the files from specific contexts which have
    been marked as "bad":

      .. code-block:: bash
          
          $ crds sync --contexts hst_0001.pmap --fetch-references --check-files --purge-rejected --purge-blacklisted
    
    would first sync the cache downloading all the files in hst_0001.pmap.
    Both mappings and references would then be checked for correct length.
    Files reported as rejected or blacklisted by the server would be removed.
  
* Reorganizing cache structure
    
        CRDS now supports two cache structures for organizing references: flat
        and instrument. `flat` places all references for a telescope in a
        single directory, e.g. references/hst.  `instrument` segregates
        references into subdirectories which name instruments or legacy
        environment variables, e.g. acs or jref.
        
        Newly created caches will default to the *instrument* organization.  To
        migrate a legacy cache with a flat single directory layout to the new
        structure, sync with `--organize=instrument`:

          .. code-block:: bash
        
              $ crds sync --organize=instrument --verbose
           
        To migrate to the flat structure,  use --organize=flat:

          .. code-block:: bash
            
              $ crds sync --organize=flat --verbose
           
        While reorganizing, if CRDS makes note of "junk files" in your cache which are
        obstructing the process of reorganizing, you can allow CRDS to delete the junk
        by adding `--organize-delete-junk`.
        
        The `--organize` switches are intended to be used only on inactive file caches
        when calibration software is not running and actively using CRDS.

crds.certify
------------

`crds.certify` checks a reference or mapping file against constraints on legal
matching parameter values.  For reference files, crds.certify also performs
checks of the FITS or ASDF format and when given a context, will compare the given
file against the file it replaces looking for new or missing table rows.

* `crds certify --help` yields:

  .. code-block:: bash

      usage: crds certify ...
         [-h] [-d] [-r] [-a] [-e] [-p] [-x COMPARISON_CONTEXT]
         [-y COMPARISON_REFERENCE] [-s] [--dump-unique-errors]
         [--unique-errors-file UNIQUE_ERRORS_FILE]
         [--all-errors-file ALL_ERRORS_FILE] [-v] [--verbosity VERBOSITY] [-R]
         [-I] [-V] [-J] [-H] [--stats] [--profile PROFILE] [--log-time] [--pdb]
         [--debug-traps]
         files [files ...]

* Checks a CRDS reference or mapping file::

    1. Verifies basic file format: .fits, .json, .yaml, .asdf, .pmap, .imap, .rmap 
    2. Checks references for required keywords and values, where constraints are defined.
    3. Checks CRDS rules for permissible values with respect to defined reference constraints.
    4. Checks CRDS rules for accidental file reversions or duplicate lines.
    5. Checks CRDS rules for noteworthy version-to-version changes such as new or removed match cases.
    6. Checks tables for deleted or duplicate rows relative to a comparison table.
    7. Finds comparison references with respect to old CRDS contexts.
    
* positional arguments::

    files

* optional arguments::

  -h, --help            show this help message and exit
  -d, --deep            Certify reference files referred to by mappings have valid contents.
  -r, --dont-recurse-mappings   Do not load and validate mappings recursively,  checking only directly specified files.
  -a, --dont-parse      Skip slow mapping parse based checks,  including mapping duplicate entry checking.
  -e, --exist           Certify reference files referred to by mappings exist.
  -p, --dump-provenance  Dump provenance keywords.
  -x COMPARISON_CONTEXT, --comparison-context COMPARISON_CONTEXT   Pipeline context defining comparison files.  Defaults to operational context,  use 'none' to suppress.
  -y COMPARISON_REFERENCE, --comparison-reference COMPARISON_REFERENCE  Comparison reference for tables certification.
  -s, --sync-files      Fetch any missing files needed for the requested difference from the CRDS server.
  -v, --verbose         Set log verbosity to True,  nominal debug level.
  --verbosity VERBOSITY Set log verbosity to a specific level: 0..100.
  -R, --readonly-cache  Don't modify the CRDS cache.  Not compatible with options which implicitly modify the cache.
         
* crds.certify is normally invoked like e.g.:

  .. code-block:: bash

      $ crds certify --comparison-context=hst_0027.pmap --run-fitsverify --dump-provenance ./some_reference.fits
    
      $ crds certify ./hst_acs_darkfile_00250.rmap
    
* To run crds.certify on a reference(s) to verify basic file format and parameter constraints:

  .. code-block:: bash

      $ crds certify --comparison-context=hst_0027.pmap   ./some_reference.fits...

  If some_reference.fits is a table, a comparison table will be found in the
  comparison context, if appropriate.

* For recursively checking CRDS rules do this:

  .. code-block:: bash

      $ crds certify hst_0311.pmap --comparison-context=hst_0312.pmap

  If a comparison context is defined, checked mappings will be compared against
  their peers (if they exist) in the comparison context.  Many classes of
  mapping differences will result in warnings.

* For reference table checks, a comparison reference can also be specified
  directly rather than inferred from context:

    .. code-block:: bash

        $ crds certify ./some_reference.fits --comparison-reference=old_reference_version.fits --run-fitsverify --dump-provenance

* For more information on the checks being performed, use `--verbose` or -`-verbosity=N` where N > 50.

  .. code-block:: bash
    
      $ crds certify --verbose ...

* Invoking crds.certify on a context mapping recursively certifies all
  sub-mappings.

* Adding `--deep` when specifying mappings causes CRDS to certify not just the
  mappings, but every reference file referred to by the mappings:

    .. code-block:: bash

        $ crds certify --deep jwst-edit

  asks CRDS to certify all of the latest CRDS rules and references.

crds.list
---------

crds.list is a swiss army knife program for dumping various forms of CRDS
information.

General categories of information driven by switches include:

0. Overall CRDS configuration
1. CRDS server file lists
2. CRDS cache file lists and paths
3. Cached file contents or headers
4. CRDS reprocessing dataset ids and parameters
5. Listing global default and installed pipeline contexts
6. Resolving context specifiers into literal context names

Many crds list services require setting `CRDS_SERVER_URL` to a valid CRDS 
server to provide a source for the headers.

.. tabs::

   .. group-tab:: HST

       .. code-block:: bash

           $ export CRDS_SERVER_URL=https://hst-crds.stsci.edu

   .. group-tab:: JWST

       .. code-block:: bash

           $ export CRDS_SERVER_URL=https://jwst-crds.stsci.edu

   .. group-tab:: ROMAN

       .. code-block:: bash

           $ export CRDS_SERVER_URL=https://roman-crds.stsci.edu


0. Configuration information governing the behavior of CRDS for simple
configurations can be dumped:

  .. code-block:: bash

      $ crds list --status
      CRDS Version = '7.0.7, bump-version, 7432326'
      CRDS_MODE = 'auto'
      CRDS_PATH = '/Users/homer/crds_cache_ops'
      CRDS_SERVER_URL = 'https://jwst-crds.stsci.edu'
      Effective Context = 'jwst_0204.pmap'
      Last Synced = '2016-09-20 08:00:09.115330'
      Python Executable = '/Users/homer/anaconda/bin/python'
      Python Version = '3.5.2.final.0'
      Readonly Cache = False

More comprehensive configuration information is also available for advanced
configurations:

  .. code-block:: bash

      $ crds list --config
      ... lots of info ....

1. Files known by the CRDS server to belong to specified contexts can be listed
even if the files are not installed in a local CRDS Cache.

The `--mappings` command recursively evaluates and includes all the sub-mappings,
i.e. imaps and pmaps, of the specified contexts.

Contexts to list can be specified in a variety of ways:

-- To list the references contained by several contexts:

  .. code-block:: bash

      $ crds list  --references --contexts hst_0001.pmap hst_0002.pmap ...
      vb41935ij_bia.fits 
      vb41935kj_bia.fits 
      ...

-- To list the references in a numerical range of contexts:

  .. code-block:: bash

      $ crds list --references --range 1:2 --references
      vb41935lj_bia.fits 
      vb41935oj_bia.fits
      ...

-- To list all mappings, even those not referenced by an imap or pmap:

  .. code-block:: bash

      $ crds list --mappings --all
      hst.pmap 
      hst_0001.pmap 
      hst_0002.pmap 
      hst_acs.imap 
      hst_acs_0001.imap 
      hst_acs_0002.imap 
      hst_acs_atodtab.rmap 
      ...

`--references`, `--mappings`, or both can be listed.

2. Locally cached files (files already synced to your computer) can be listed:

  .. code-block:: bash

      $ crds list --cached-mappings --full-path
      ...
      
      $ crds list --cached-references --full-path
      ...

In both cases adding `--full-path` prints the path of the file within the CRDS cache.

These are merely simple directory listings which ignore the context specifiers
and can be grep'ed for finer grained answers.

3. The contents of cached mappings or references (header only) can be printed to stdout like this:

  .. code-block:: bash

      $ crds list --contexts jwst-fgs-linearity-edit jwst-nirspec-linearity-edit --cat --add-filename | grep parkey
      CRDS - INFO - Symbolic context 'jwst-fgs-linearity-edit' resolves to 'jwst_fgs_linearity_0008.rmap'
      CRDS - INFO - Symbolic context 'jwst-nirspec-linearity-edit' resolves to 'jwst_nirspec_linearity_0009.rmap'
      /cache/path/mappings/jwst/jwst_fgs_linearity_0008.rmap:     'parkey' : (('META.INSTRUMENT.DETECTOR', 'META.SUBARRAY.NAME'), ('META.  OBSERVATION.DATE', 'META.OBSERVATION.TIME')),
      /cache/path/mappings/jwst/jwst_nirspec_linearity_0009.rmap:     'parkey' : (('META.INSTRUMENT.DETECTOR', 'META.SUBARRAY.NAME'), ('META.  OBSERVATION.DATE', 'META.OBSERVATION.TIME')),

this prints the contents of the specified rmaps.

The `-edit` specifier above refers to mappings contained by the default starting point (.pmap) of future
server submissions.  It tracks on-going submission work that precedes the adoption of a new context
as the default in use by the pipeline.

`crds.list --cat` can be applied to references and prints out the reference metadata that CRDS views
abstractly as the file header.

References need to be catted explicitly by name,  but the list can come from the `--references` command
explained above:

  .. code-block:: bash

      $ crds list --cat jwst_nirspec_dark_0036.fits
      CRDS - INFO - Symbolic context 'jwst-operational' resolves to 'jwst_0167.pmap'
      File:  '/grp/crds/jwst/references/jwst/jwst_nirspec_dark_0036.fits'
      {'A1_COL_C': '8.9600000e+002',
      'A1_CONF1': '2.1846000e+004',
      ...
      }

4. Information about the dataset IDs and parameters used for CRDS reprocessing 
and regressions can be printed or stored.

 Parameter set IDs can be listed for one or more instruments as follows:

   .. code-block:: bash

       $ crds list --dataset-ids-for-instruments wfc3...
       JCL403010:JCL403ECQ
       ... hundreds to hundreds of thousands of IDs as shown above ...
 
 IDs can also be captured to a file using UNIX I/O redirection:

   .. code-block:: bash
 
       $ crds list --dataset-ids-for-instruments wfc3   >wfc3.ids    
 
 IDs for HST are of the form <product>:<exposure> where many exposures feed into 
 the construction of one product and recalibrating any component exposure suggests 
 recalibrating the combined product.

 CRDS stores dataset parameters for regression testing as a JSON dictionaries 
 specifying one set of dataset parameters per line of the file:

   .. code-block:: bash
 
       $ crds list --dataset-headers @wfc3.ids --json > wfc3.headers.json
 
 NOTE:  while IDs can be specified directly on the command line,  CRDS has an 
 @-notation that means "take IDs from this file".
 
 The JSON headers are suitable for running through crds.bestrefs to perform 
 reprocessing checks or single context reference file coverage checks shown here:

   .. code-block:: bash
 
       $ crds bestrefs --load-pickle wfc3.headers.json --dump-unique-errors --stats
       ...  errors related to looking up references for these parameter sets ...
 
 The script crds_dataset_capture combines the process of dumping all IDs for an 
 instrument and dumping their corresponding dataset parameters.  IDs files and
 header files are placed in a dated regression capture directory:

   .. code-block:: bash
 
       $ crds_dataset_capture wfc3 acs ...
       ... downloads IDs and headers for WFC3, ACS to dated directory ...

 The default multi-line format for dataset parameters is more readable than the 
 `--json` form:

   .. code-block:: bash

       $ crds list --dataset-headers jcl403010 --first-id --minimize-header
       CRDS - INFO - Symbolic context 'hst-operational' resolves to 'hst_0462.pmap'
       CRDS - INFO - Dataset pars for 'JCL403010:JCL403ECQ' with respect to 'hst_0462.pmap'
       {'APERTURE': 'WFC1',
        'ATODCORR': 'OMIT',
        'BIASCORR': 'COMPLETE',
        'CCDAMP': 'ABCD',
        'CCDCHIP': '-999.0',
        'CCDGAIN': '2.0',
        'CRCORR': 'OMIT',
        'DARKCORR': 'COMPLETE',
        'DATE-OBS': '2016-02-20',
        'DETECTOR': 'WFC',
        'DQICORR': 'COMPLETE',
        'DRIZCORR': 'COMPLETE',
        'FILTER1': 'CLEAR1L',
        'FILTER2': 'F814W',
        'FLASHCUR': 'LOW',
        'FLATCORR': 'COMPLETE',
        'FLSHCORR': 'OMIT',
        'FW1OFFST': '0.0',
        'FW2OFFST': '0.0',
        'FWSOFFST': '0.0',
        'GLINCORR': 'UNDEFINED',
        'INSTRUME': 'ACS',
        'LTV1': '0.0',
        'LTV2': '0.0',
        'NAXIS1': '4144.0',
        'NAXIS2': '4136.0',
        'OBSTYPE': 'IMAGING',
        'PCTECORR': 'UNDEFINED',
        'PHOTCORR': 'COMPLETE',
        'RPTCORR': 'UNDEFINED',
        'SHADCORR': 'OMIT',
        'SHUTRPOS': 'A',
        'TIME-OBS': '17:32:29.666665',
        'XCORNER': '0.0',
        'YCORNER': '0.0',
        'dataset_id': 'JCL403010:JCL403ECQ'}

Sometimes it's desirable to know the individual exposures CRDS associates with a product id:

  .. code-block:: bash

      $ crds list --dataset-headers jcl403010 --id-expansions-only
      CRDS - INFO - Symbolic context 'hst-operational' resolves to 'hst_0462.pmap'
      JCL403010:JCL403ECQ
      JCL403010:JCL403EEQ
      JCL403010:JCL403EGQ
      JCL403010:JCL403EIQ
      JCL403010:JCL403EKQ
      JCL403010:JCL403EMQ
      JCL403010:JCL403EOQ
      JCL403010:JCL403EQQ
      JCL403010:JCL403ESQ
      JCL403010:JCL403EUQ

5. Information about the default context can be printed.  There are two variations and a subtle distinction:

  .. code-block:: bash

      $ python m crds.list --operational-context
      jwst_0204.pmap 

lists the context which has been *commanded* as default on the CRDS server.

While:

  .. code-block:: bash

      $ crds list --remote-context jwst-ops-pipeline
      jwst_0101.pmap

lists the context which is *in actual use* in the associated archive pipeline as reported by
a cache sync echo.

During the interval between commanding a new default on the CRDS server and syncing the pipeline
CRDS cache,  the commanded and actual pipeline contexts can differ.

6. Resolving context specifiers

Some CRDS tools, including crds.list and crds.sync, support multiple
mechanisms for specifying context.  The `--resolve-contexts` command
interprets those specifiers into a non-recursive list of literal mapping
names and prints them out.  `--resolve-contexts` differs from `--mappings`
because it does not implicitly include all sub-mappings of the specified
contexts:

  .. code-block:: bash

      $ crds list --resolve-contexts --all
      jwst.pmap
      jwst_0000.pmap
      jwst_0001.pmap
      jwst_0002.pmap
      jwst_0003.pmap
      ...
      
      $ crds list --resolve-contexts --last 5
      jwst_0205.pmap
      jwst_0206.pmap
      jwst_0207.pmap
      jwst_0208.pmap
      jwst_0209.pmap
      
      $ crds list --resolve-contexts  --contexts jwst-miri-dark-operational 
      jwst_miri_dark_0012.rmap
      
      $ crds list --resolve-contexts --contexts jwst-niriss-superbias-2016-01-01T00:00:00
      jwst_niriss_superbias_0005.rmap
    

crds.diff
---------

crds.diff compares two reference or mapping files and reports differences.  For
references crds.diff is currently a thin wrapper around fitsdiff but may expand.   

For CRDS mappings crds.diff performs a recursive logical difference which shows 
the full match path to each bottom level change.   `crds.diff --help` yields:

  .. code-block::

      Difference CRDS mapping or reference files.
      
      positional arguments:
        old_file              Prior file of difference.
        new_file              New file of difference.
      
      optional arguments:
        -h, --help            show this help message and exit
        -P, --primitive-diffs
                              Fitsdiff replaced reference files when diffing mappings.
        -T, --mapping-text-diffs
                              In addition to CRDS mapping logical differences,  run UNIX context diff for mappings.
        -K, --check-diffs     Issue warnings about new rules, deletions, or reversions.
        -N, --print-new-files
                              Rather than printing diffs for mappings,  print the names of new or replacement files.  Excludes intermediaries.
        -A, --print-all-new-files
                              Print the names of every new or replacement file in diffs between old and new.  Includes intermediaries.
        -i, --include-header-diffs
                              Include mapping header differences in logical diffs: sha1sum, derived_from, etc.
        -B, --hide-boring-diffs
                              Include mapping header differences in logical diffs: sha1sum, derived_from, etc.
        --print-affected-instruments
                              Print out the names of instruments which appear in diffs,  rather than diffs.
        --print-affected-types
                              Print out the names of instruments and types which appear in diffs,  rather than diffs.
        --print-affected-modes
                              Print out the names of instruments, types, and matching parameters,  rather than diffs.
        -v, --verbose         Set log verbosity to True,  nominal debug level.
        --verbosity VERBOSITY
                              Set log verbosity to a specific level: 0..100.
        -R, --readonly-cache  Don't modify the CRDS cache.  Not compatible with options which implicitly modify the cache.
        -V, --version         Print the software version and exit.
        -J, --jwst            Force observatory to JWST for determining header conventions.
        -H, --hst             Force observatory to HST for determining header conventions.
      
      Reference files are nominally differenced using FITS-diff or diff.
          
      Mapping files are differenced using CRDS machinery to recursively compare too mappings and 
      their sub-mappings.
          
      Differencing two mappings will find all the logical differences between the two contexts
      and any nested mappings.
          
      By specifying --mapping-text-diffs,  UNIX diff will be run on mapping files in addition to 
      CRDS logical diffs.
          
      By specifying --primitive-diffs,  FITS diff will be run on all references which are replaced
      in the logical differences between two mappings.
          
      For example:
          
          % crds diff hst_0001.pmap  hst_0005.pmap  --mapping-text-diffs --primitive-diffs
          
      Will recursively produce logical, textual, and FITS diffs for all changes between the two contexts.
          
          NOTE: mapping logical differences (the default) do not compare CRDS mapping headers,  use
          --include-header-diffs to get those as well.
      

For standard CRDS filenames,  crds.diff can guess the observatory.   For 
non-standard names,  the observatory needs to be specified.  crds.diff can be
invoked like:

  .. code-block:: bash

      $ crds diff   ./jwst_nircam_dark_0010.fits  ./jwst_nircam_dark_0011.fits

      $ crds diff  jwst_0001.pmap   jwst_0002.pmap
      (('hst.pmap', 'hst_0004.pmap'), ('hst_acs.imap', 'hst_acs_0004.imap'), ('hst_acs_darkfile.rmap', 'hst_acs_darkfile_0003.rmap'), ('WFC', 'A|    ABCD|AD|B|BC|C|D', '0.5|1.0|1.4|2.0'), '2011-03-16 23:34:35', "replaced 'v441434ej_drk.fits' with 'hst_acs_darkfile_0003.fits'")


crds.rowdiff
------------
Modules that are based on FITSDiff, such as crds.diff, compare
tabular data on a column-by-column basis. Rowdiff compares tabular data
on a row-by-row basis, producing UNIX diff-like output instead.
Non-tabular extensions are ignored.

  .. code-block:: bash

      usage: crds rowdiff [-J] [-H]
             [--ignore-fields IGNORE_FIELDS] 
             [--fields FIELDS]
             [--mode-fields MODE_FIELDS] old_file new_file
      
      Perform FITS table difference by rows
      
      positional arguments:
        old_file                First FITS table to compare
        new_file                Second FITS table to compare
      
      optional arguments:
        --ignore-fields IGNORE_FIELDS
                              List of fields to ignore
        --fields FIELDS       List of fields to compare
        --mode-fields MODE_FIELDS
                              List of fields to do a mode compare
        -J, --jwst            Force observatory to JWST for determining header conventions.
        -H, --hst             Force observatory to HST for determining header conventions.

The FITS data to be compared are required to be similar: they must have
the same number of extensions and the types of extensions must match.

The parameters `--fields` and `--ignore-fields` define which columns
are compared between each table extension. These are mutually
exclusive parameters and an error will generate if both are specified.

First a summary of the changes between the table extension is given.
Then, row-by-row difference is given, using unified diff syntax.

The parameter `--mode-fields` initiates a different algorithm.
Here, it is presumed the tabular data contains columns that can essentially
be treated as keys upon with rows are selected. The fields specified are those
key columns.

All possible coombinations of values are determined be examining both
extensions. Then, each table is compared against both this list and between
each other, looking for multiply specified combinations, missing combinations,
and, for the common combinations between the tables, whether the rest of the
rows are equivalent or not.

Examples:

  .. code-block:: bash

      $ crds rowdiff s9m1329lu_off.fits s9518396u_off.fits 

      $ crds rowdiff s9m1329lu_off.fits s9518396u_off.fits --mode-fields=detchip,obsdate


crds.uses
---------

`crds.uses` searches the files in the local cache for mappings which refer to the 
specified files.  Since the **local cache** is used only mappings present in the 
local cache will be included in the results given.  crds.uses is invoked as:

  .. code-block:: bash

      $ crds uses <observatory=hst|jwst> <mapping or reference>...

e.g.::

    Prints out the mappings which refer to the specified mappings or references.
    
    Prints out the datasets which historically used a particular reference as defined by DADSOPS.
    
    IMPORTANT:  
       1. You must specify references on which to operate with --files.
       2. You must set CRDS_PATH and CRDS_SERVER_URL to give crds.uses access to CRDS mappings and databases.
    
    optional arguments:
      -h, --help            show this help message and exit
      --files FILES [FILES ...]
                            References for which to dump using mappings or datasets.
      -d, --print-datasets  Print the ids of datasets last historically using a reference.
      -i, --include-used    Include the used file in the output as the first column.
      -v, --verbose         Set log verbosity to True,  nominal debug level.
      --verbosity VERBOSITY
                            Set log verbosity to a specific level: 0..100.
      -R, --readonly-cache  Don't modify the CRDS cache.  Not compatible with options which implicitly modify the cache.
      -V, --version         Print the software version and exit.
      -J, --jwst            Force observatory to JWST for determining header conventions.
      -H, --hst             Force observatory to HST for determining header conventions.
    
crds.uses can be invoked like this:

  .. code-block:: bash
    
      $ crds uses --files n3o1022ij_drk.fits --hst
      hst.pmap
      hst_0001.pmap
      hst_0002.pmap
      hst_0003.pmap
      ...
      hst_0041.pmap
      hst_acs.imap
      hst_acs_0001.imap
      hst_acs_0002.imap
      hst_acs_0003.imap
      ...
      hst_acs_0008.imap
      hst_acs_darkfile.rmap
      hst_acs_darkfile_0001.rmap
      hst_acs_darkfile_0002.rmap
      hst_acs_darkfile_0003.rmap
      ...
      hst_acs_darkfile_0005.rmap
      
      $ crds uses --files n3o1022ij_drk.fits --print-datasets --hst
      J8BA0HRPQ
      J8BA0IRTQ
      J8BA0JRWQ
      J8BA0KT4Q
      J8BA0LIJQ
      
      $ crds uses --files @dropped --hst --print-datasets --include-used
      vb41934lj_bia.fits JA7P21A2Q
      vb41934lj_bia.fits JA7P21A4Q
      vb41934lj_bia.fits JA7P21A6Q

crds.matches
------------

crds.matches reports the match patterns which are associated with the given
reference files:

  .. code-block::

      usage: crds matches ...
             [-h] [--contexts [CONTEXT [CONTEXT ...]]] 
             [--files FILES [FILES ...]] [-b] [-o] [-t] 
      
      Prints out the selection criteria by which the specified references are matched
      with respect to a particular context.
        
      optional arguments:
        -h, --help            show this help message and exit
        --contexts [CONTEXT [CONTEXT ...]]
                              Specify a list of CRDS mappings to operate on: .pmap, .imap, or .rmap or date-based specification
        --range MIN:MAX       Operate for pipeline context ids (.pmaps) between <MIN> and <MAX>.
        --all                 Operate with respect to all known CRDS contexts.
        --last N              Operate with respect to the last N contexts.
        -i, --ignore-cache    Download required files even if they're already in the cache.
        --files FILES [FILES ...]
                              References for which to dump selection criteria.
        -b, --brief-paths     Don't the instrument and filekind.
        -o, --omit-parameter-names
                              Hide the parameter names of the selection criteria,  just show the values.
        -t, --tuple-format    Print the match info as Python tuples.
        -d DATASETS [DATASETS ...], --datasets DATASETS [DATASETS ...]
                              Dataset ids for which to dump matching parameters from DADSOPS or equivalent database.
        -c, --condition-values
                              When dumping dataset parameters, first apply CRDS value conditioning / normalization.
        -m, --minimize-header
                              When dumping dataset parameters,  limit them to matching parameters, not historical bestrefs.
        -v, --verbose         Set log verbosity to True,  nominal debug level.
        --verbosity VERBOSITY
                              Set log verbosity to a specific level: 0..100.
        -R, --readonly-cache  Don't modify the CRDS cache.  Not compatible with options which implicitly modify the cache.
        -V, --version         Print the software version and exit.
        -J, --jwst            Force observatory to JWST for determining header conventions.
        -H, --hst             Force observatory to HST for determining header conventions.

`crds.matches` can dump reference file match cases with respect to particular contexts:

  .. code-block:: bash
    
      $ crds matches  --contexts hst_0001.pmap --files lc41311jj_pfl.fits
      lc41311jj_pfl.fits : ACS PFLTFILE DETECTOR='WFC' CCDAMP='A|ABCD|AC|AD|B|BC|BD|C|D' FILTER1='F625W' FILTER2='POL0V' DATE-OBS='1997-01-01'   TIME-OBS='00:00:00'
      
      $ crds matches --contexts hst.pmap --files lc41311jj_pfl.fits --omit-parameter-names --brief-paths
      lc41311jj_pfl.fits :  'WFC' 'A|ABCD|AC|AD|B|BC|BD|C|D' 'F625W' 'POL0V' '1997-01-01' '00:00:00'
      
      $ crds matches --contexts hst.pmap --files lc41311jj_pfl.fits --tuple-format
      lc41311jj_pfl.fits : (('OBSERVATORY', 'HST'), ('INSTRUMENT', 'ACS'), ('FILEKIND', 'PFLTFILE'), ('DETECTOR', 'WFC'), ('CCDAMP', 'A|ABCD|  AC|AD|B|BC|BD|C|D'), ('FILTER1', 'F625W'), ('FILTER2', 'POL0V'), ('DATE-OBS', '1997-01-01'), ('TIME-OBS', '00:00:00'))
    
crds.matches can dump database matching parameters for specified datasets with respect to specified contexts:

  .. code-block:: bash
    
      $ crds matches --datasets JBANJOF3Q --minimize-headers --contexts hst_0048.pmap hst_0044.pmap

      JBANJOF3Q : hst_0044.pmap : APERTURE='WFC1-2K' ATODCORR='NONE' BIASCORR='NONE' CCDAMP='B' CCDCHIP='1.0' CCDGAIN='2.0' CRCORR='NONE'   DARKCORR='NONE' DATE-OBS='2010-01-31' DETECTOR='WFC' DQICORR='NONE' DRIZCORR='NONE' FILTER1='F502N' FILTER2='F660N' FLASHCUR='OFF'   FLATCORR='NONE' FLSHCORR='NONE' FW1OFFST='0.0' FW2OFFST='0.0' FWSOFFST='0.0' GLINCORR='NONE' INSTRUME='ACS' LTV1='-2048.0' LTV2='-1.0'   NUMCOLS='UNDEFINED' NUMROWS='UNDEFINED' OBSTYPE='INTERNAL' PCTECORR='NONE' PHOTCORR='NONE' REFTYPE='UNDEFINED' SHADCORR='NONE'   SHUTRPOS='B' TIME-OBS='01:07:14.960000' XCORNER='1.0' YCORNER='2072.0' 
      JBANJOF3Q : hst_0048.pmap : APERTURE='WFC1-2K' ATODCORR='NONE' BIASCORR='NONE' CCDAMP='B' CCDCHIP='1.0' CCDGAIN='2.0' CRCORR='NONE'   DARKCORR='NONE' DATE-OBS='2010-01-31' DETECTOR='WFC' DQICORR='NONE' DRIZCORR='NONE' FILTER1='F502N' FILTER2='F660N' FLASHCUR='OFF'   FLATCORR='NONE' FLSHCORR='NONE' FW1OFFST='0.0' FW2OFFST='0.0' FWSOFFST='0.0' GLINCORR='NONE' INSTRUME='ACS' LTV1='-2048.0' LTV2='-1.0'   NAXIS1='2070.0' NAXIS2='2046.0' OBSTYPE='INTERNAL' PCTECORR='NONE' PHOTCORR='NONE' REFTYPE='UNDEFINED' SHADCORR='NONE' SHUTRPOS='B'   TIME-OBS='01:07:14.960000' XCORNER='1.0' YCORNER='2072.0'
    
crds.matches can be invoked in various ways with different output formatting:

  .. code-block:: bash
    
      $ crds matches  --contexts hst_0001.pmap --files lc41311jj_pfl.fits
      lc41311jj_pfl.fits : ACS PFLTFILE DETECTOR='WFC' CCDAMP='A|ABCD|AC|AD|B|BC|BD|C|D' FILTER1='F625W' FILTER2='POL0V' DATE-OBS='1997-01-01'   TIME-OBS='00:00:00'
      
      $ crds matches --contexts hst.pmap --files lc41311jj_pfl.fits --omit-parameter-names --brief-paths
      lc41311jj_pfl.fits :  'WFC' 'A|ABCD|AC|AD|B|BC|BD|C|D' 'F625W' 'POL0V' '1997-01-01' '00:00:00'
      
      $ crds matches --contexts hst.pmap --files lc41311jj_pfl.fits --tuple-format
      lc41311jj_pfl.fits : (('OBSERVATORY', 'HST'), ('INSTRUMENT', 'ACS'), ('FILEKIND', 'PFLTFILE'), ('DETECTOR', 'WFC'), ('CCDAMP', 'A|ABCD|  AC|AD|B|BC|BD|C|D'), ('FILTER1', 'F625W'), ('FILTER2', 'POL0V'), ('DATE-OBS', '1997-01-01'), ('TIME-OBS', '00:00:00'))

crds uniqname
-------------
CRDS uniqname is used to rename references with unique official CRDS names for HST.
It supports renaming both calibration and synphot reference files with modernized
HST CDBS-style names.

  .. code-block:: bash

      usage:
          crds uniqname
          [-h] [--files FILES [FILES ...]] [--dry-run] [-a] [-f] [-e] [-s] [-r]
          [-o OUTPUT_PATH] [-b] [--fits-errors] [-v] [--verbosity VERBOSITY] 
          [--dump-cmdline] [-R] [-I] [-V] [-J] [-H] [--roman] [--stats] 
          [--profile PROFILE] [--log-time] [--pdb] [--debug-traps]

      optional arguments:
          -h, --help            show this help message and exit
          --files FILES [FILES ...]
                                Files to rename.
          --dry-run             Print how a file would be renamed without modifying it.
          -a, --add-checksum    Add FITS checksum.  Without, checksums *removed* if header modified.
          -f, --add-keywords    When renaming, add FILENAME, ROOTNAME, HISTORY keywords for the generated name.
          -e, --verify-file     Verify FITS compliance and any checksums before changing each file.
          -s, --standard        Same as --add-keywords --verify-file,  does not add checksums (add -a).
          -r, --remove-original
                                After renaming,  remove the orginal file.
          -o OUTPUT_PATH, --output-path OUTPUT_PATH
                                Output renamed files to this directory path.
          -b, --brief           Produce less output.
          --fits-errors         When set, treat FITS compliance and checksum errors as fatal exceptions.
          -v, --verbose         Set log verbosity to True,  nominal debug level.
          --verbosity VERBOSITY
                                Set log verbosity to a specific level: 0..100.
          --dump-cmdline        Dump the command line parameters used to start the script to the log.
          -R, --readonly-cache  Do not modify the CRDS cache.  Not compatible with options which implicitly modify the cache.
          -I, --ignore-cache    Download required files even if they are already in the cache.
          -V, --version         Print the software version and exit.
          -J, --jwst            Force observatory to JWST for determining header conventions.
          -H, --hst             Force observatory to HST for determining header conventions.
          --roman               Force observatory to Roman for determining header conventions.
          --stats               Track and print timing statistics.
          --profile PROFILE     Output profile stats to the specified file.
          --log-time            Add date/time to log messages.
          --pdb                 Run under pdb.
          --debug-traps         Bypass exception error message traps and re-raise exception.

This program is based loosely on the CDBS program uniqname modified to support
enhanced CDBS-style names with modified timestamps valid after 2016-01-01.

The CRDS uniqame is nominally run as follows:

  .. code-block:: bash

      $ crds uniqname --files s7g1700gl_dead.fits --brief --standard
      CRDS - INFO - Rewriting 's7g1700gl_dead.fits' --> 'zc52141pl_dead.fits'

CRDS uniqname also supports renaming synphot files not otherwise managed by CRDS:

  .. code-block:: bash

      $ crds uniqname --files s7g1700gl_tmt.fits --brief --standard
      CRDS - INFO - Rewriting 's7g1700gl_tmt.fits' --> 'zc52141pl_tmt.fits'

If `-s` or `--standard` is added then routinely used switches are added as a
predefined bundle. Initially these are `--add-keywords` and `--verify-file`.

If `--add-checksum` is specified,  CRDS uniqname will add FITS checksums to the file.
If --add-checksum is not specified,  CRDS uniqname WILL REMOVE any existing checksum.

If `--verify-file` is specified,  CRDS uniqname will check the FITS checksum and validate
the FITS format of renamed files.

If  `--add-keywords` is specified CRDS uniqname will add/modify the FILENAME, ROOTNAME,
and HISTORY to document the renaming.

If `--remove-original` is specified then the original file is deleted after the renamed
file has been created and modified as specified (checksums, keywords, etc.)

Renamed files can be output to a different directory using `--output-path`.

`--dry-run` can be used to demo renaming by printing what the new name would be.

crds checksum
-------------

  .. code-block:: bash

      usage: crds checksum
      [-h] [--remove] [--verify] [-v] [--verbosity VERBOSITY] 
      [--dump-cmdline] [-R] [-I] [-V] [-J] [-H] [--roman] 
      [--stats] [--profile PROFILE] [--log-time] [--pdb] 
      [--debug-traps] files [files ...]

      Add, remove, or verify checksums in CRDS rules or reference files.
      
      1. Default operation is to ADD checksums::
  
      % crds checksum  *.rmap
  
      % crds checksum  *.fits
  
      2. Reference files may support REMOVING checksums::
  
      % crds checksum --remove *.fits
  
      NOTE: CRDS mapping / rules files do not support removing checksums.
  
      3. Checksums can be VERIFIED without attempting to update or remove::
  
      % crds checksum --verify  *.rmap
  
      % crds checksum --verify *.fits
  
      Currently only FITS references support checksum operations.
      Checksums can be added or verified on all CRDS mapping types.
      
      
      positional arguments:
        files                 Files to operate on, CRDS rule or reference files.
      
      optional arguments:
        -h, --help            show this help message and exit
        --remove              Remove checksums when specified.  Invalid for CRDS mappings.
        --verify              Verify checksums when specified.
        -v, --verbose         Set log verbosity to True,  nominal debug level.
        --verbosity VERBOSITY
                              Set log verbosity to a specific level: 0..100.
        --dump-cmdline        Dump the command line parameters used to start the script to the log.
        -R, --readonly-cache  Do not modify the CRDS cache.  Not compatible with options which implicitly modify the cache.
        -I, --ignore-cache    Download required files even if they are already in the cache.
        -V, --version         Print the software version and exit.
        -J, --jwst            Force observatory to JWST for determining header conventions.
        -H, --hst             Force observatory to HST for determining header conventions.
        --roman               Force observatory to Roman for determining header conventions.
        --stats               Track and print timing statistics.
        --profile PROFILE     Output profile stats to the specified file.
        --log-time            Add date/time to log messages.
        --pdb                 Run under pdb.
        --debug-traps         Bypass exception error message traps and re-raise exception.


safe_bestrefs
-------------

The `safe_bestrefs` script is a shim around *crds bestrefs* which configures it for operation in
the pipeline using a readonly cache and no connection to the server.  Typical usage might be::

      $ export CRDS_PATH=<pipeline's CRDS cache path>
      $ safe_bestrefs --files <datasets FITS files...>

This script is intended to be run in parallel with multiple pipeline bestrefs
and a concurrent cron_sync.  The "safe" aspect refers to not modifying the
CRDS cache itself, and to not stumbling into inconsistent cache states while
another process is updating the cache.

To control when information is received from the server,  and to prevent pipeline stalls
when the CRDS server is unavailable, safe_bestrefs is configured with a bad server IP address.
    
Using a readonly CRDS cache enables the use of bestrefs in a multiprocessing environment
where multiple copies of bestrefs are running simultaneously.

Configuring bestrefs to run with no connection to the CRDS server makes it impossible for bestrefs
to do file downloads and keeps the pipeline independent of the server during routine operations.   
See *cron_sync* for more info on updating the CRDS cache in pipeline environments.

cron_sync
---------

The `cron_sync` script is a wrapper around the *crds sync* tool that tunes it for updating the CRDS
cache in a highly concurrent environment where bestrefs may be running during the cache update.

*cron_sync* uses file locks to prevent more than one copy of itself from running at the
same time, particularly if run periodically as a cron job which may take longer than the period
to fully download file updates.

Typical setup and execution is::

    $ export CRDS_PATH=<pipeline's CRDS cache path>
    $ export CRDS_SERVER_URL=<project's CRDS server>
    $ export CRDS_LOCKS=<directory for cron_sync lock files, defaults to $CRDS_PATH>
    $ cron_sync --all --check-files --fetch-references

*cron_sync* co-exists with an operating copy of *safe_bestrefs* by writing out the cache configuration 
information last.   The cache configuration information controls the context switch.  While files
corresponding to the new context are downloading,  the cache remains safe and continues to operate
under the old context.

The HST, JWST and Roman pipeline environments currently further wrap the *cron_sync* script to establish
the environment settings and required Python stack and eliminate all parameters:

  .. code-block:: bash

      $ crds_sync_wrapper.csh

Operators typically execute *crds_sync_wrapper.csh* rather than *cron_sync*.    


