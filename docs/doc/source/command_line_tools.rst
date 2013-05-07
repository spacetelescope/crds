Command Line Tools
==================

Using the command line tools requires a local installation of the CRDS library.
Some of the command line tools also interact with the CRDS server in order to
implement their functionality.

Specifying Files
----------------

The command line tools operate on CRDS reference and mapping files in various
ways.  To specify a file in your local CRDS file cache,  as defined by CRDS_PATH,
use no path on the file::

  % python -m crds.diff hst.pmap  hst_0001.pmap  # assumes paths in CRDS cache

To specify a particular file which is not located in your cache,  give at least
a relative path to the file, ./ will do::
  
  % python -m crds.diff /some/path/hst.pmap ./hst_0002.pmap   # uses given paths

crds.certify
------------

crds.certify checks a reference or mapping file against constraints on legal
matching parameter values.   For reference files,  crds.certify also performs checks
of the FITS format and when given a context,  and will compare the given file against
the file it replaces looking for new or missing table rows. 

crds.certify --help yields::

    usage: certify.py [-d] [-e] [-m] [-p] [-t TRAP_EXCEPTIONS] [-x CONTEXT] [-J] [-H]
                      files [files ...]
    
    Checks a CRDS reference or mapping file.
        
    positional arguments:
      files
    
    optional arguments:
      -d, --deep            Certify reference files referred to by mappings have valid contents.
      -e, --exist           Certify reference files referred to by mappings exist.
      -m, --mapping         Ignore extensions, the files being certified are mappings.
      -p, --dump-provenance
                            Dump provenance keywords.
      -t TRAP_EXCEPTIONS, --trap-exceptions TRAP_EXCEPTIONS
                            Capture exceptions at level: pmap, imap, rmap, selector, debug, none
      -x CONTEXT, --context CONTEXT
                            Pipeline context defining comparison files.
      -J, --jwst            Force observatory to JWST for determining header conventions.
      -H, --hst             Force observatory to HST for determining heder conventions.
                            
crds.certify is invoked as, e.g.::

    % python -m crds.certify --context=hst_0027.pmap   some_reference.fits
    
    % python -m crds.certify hst.pmap
    
Invoking crds.certify on a context mapping recursively certifies all sub-mappings.

crds.diff
---------

crds.diff compares two reference or mapping files and reports differences.  For
references crds.diff is currently a thin wrapper around fitsdiff but may expand.   

For CRDS mappings crds.diff performs a recursive logical difference which shows 
the full match path to each bottom level change.   crds.diff --help yields::

    usage: diff.py [-P] [-K] [-J] [-H]  old_file new_file
    
    Difference CRDS mapping or reference files.
    
    positional arguments:
      old_file              Prior file of difference.
      new_file              New file of difference.
    
    optional arguments:
      -P, --primitive-diffs
                            Include primitive differences on replaced files.
      -K, --check-diffs     Issue warnings about new rules, deletions, or reversions.
      -J, --jwst            Force observatory to JWST for determining header conventions.
      -H, --hst             Force observatory to HST for determining heder conventions.

For standard CRDS filenames,  crds.diff can guess the observatory.   For 
non-standard names,  the observatory needs to be specified.  crds.diff can be
invoked like::

  % python -m crds.diff   jwst_nircam_dark_0010.fits  jwst_nircam_dark_0011.fits

  % python -m crds.diff  jwst_0001.pmap   jwst_0002.pmap
  (('hst.pmap', 'hst_0004.pmap'), ('hst_acs.imap', 'hst_acs_0004.imap'), ('hst_acs_darkfile.rmap', 'hst_acs_darkfile_0003.rmap'), ('WFC', 'A|ABCD|AD|B|BC|C|D', '0.5|1.0|1.4|2.0'), '2011-03-16 23:34:35', "replaced 'v441434ej_drk.fits' with 'hst_acs_darkfile_0003.fits'")
 

crds.uses
---------

crds.uses searches the files in the local cache for mappings which refer to the 
specified files.  Since the **local cache** is used only mappings present in the 
local cache will be included in the results given.  crds.uses is invoked as::

   % python -m crds.uses <observatory=hst|jwst> <mapping or reference>...

e.g.::

   % python -m crds.uses hst s7g1700gl_dead.fits
   hst.pmap
   hst_cos.imap
   hst_cos_deadtab.rmap


crds.matches
------------

crds.matches reports the match patterns which are associated with the given
reference files::

    Usage: matches.py [options] <context> <references...>

    Options:
      -h, --help            show this help message and exit
      -f, --full            Show the complete match path through the mapping
                            hierarchy.
      -V VERBOSITY, --verbose=VERBOSITY
                            Set verbosity level.

*crds.matches* can be invoked as::    

    % python -m crds.matches hst.pmap o8u2214fj_dxy.fits
    ('HRC', 'CLEAR1S', 'F220W')
    
    % python -m crds.matches --full hst.pmap o8u2214fj_dxy.fits
    ('hst', 'acs', 'dgeofile', 'HRC', 'CLEAR1S', 'F220W', '2002-03-01', '00:00:00')


crds.sync 
---------

The CRDS sync tool is used to download CRDS rules and references from the CRDS server::
    
    usage: python -m crds.sync
    
           [-h] [--contexts [CONTEXT [CONTEXT ...]]] [--range MIN:MAX] [--all]
           [--files [FILES [FILES ...]]] [--datasets [DATASET [DATASET ...]]]
           [--fetch-references] [--purge-references] [--purge-mappings] [-i]
           [--dry-run] [-v] [--verbosity VERBOSITY] [-V] [-J] [-H]
           [--profile PROFILE] [--pdb]
    
        Synchronize local mapping and reference caches for the given contexts by
        downloading missing files from the CRDS server and/or archive.
        
    
    optional arguments:
      -h, --help            show this help message and exit
      --contexts [CONTEXT [CONTEXT ...]]
                            Specify a list of CRDS mappings to operate on: .pmap, .imap, or .rmap
      --range MIN:MAX       Operate for pipeline context ids (.pmaps) between <MIN> and <MAX>.
      --all                 Operate with respect to all known CRDS contexts.
      --files [FILES [FILES ...]]
                            Explicitly list files to be synced.
      --datasets [DATASET [DATASET ...]]
                            Cache references for the specified datasets.
      --fetch-references    Cache all the references for the specified contexts.
      --purge-references    Remove reference files not referred to by contexts from the cache.
      --purge-mappings      Remove mapping files not referred to by contexts from the cache.
      -i, --ignore-cache    Download sync'ed files even if they're already in the cache.
      --dry-run             Don't remove purged files,  just print out their names.
      -v, --verbose         Set log verbosity to True,  nominal debug level.
      --verbosity VERBOSITY
                            Set log verbosity to a specific level: 0..100.
      -V, --version         Print the software version and exit.
      -J, --jwst            Force observatory to JWST for determining header conventions.
      -H, --hst             Force observatory to HST for determining header conventions.
      --profile PROFILE     Output profile stats to the specified file.
      --pdb                 Run under pdb.
    
        
* Primitive syncing can be done by explicitly listing the files you wish to cache::

        % python -m crds.sync  --files hst_0001.pmap hst_acs_darkfile_0037.fits
     
     this will download only those two files.

* Typically syncing CRDS files is done with respect to particular CRDS contexts:

    Synced contexts can be explicitly listed::
    
        % python -m crds.sync  --contexts hst_0001.pmap hst_0002.pmap
      
    this will recursively download all the mappings referred to by .pmaps 0001 and 0002.
    
    Synced contexts can be specified as a numerical range::
    
        % python -m crds.sync --range 1:3
    
    this will also recursively download all the mappings referred to by .pmaps 0001, 002, 0003.
    
    Synced contexts can be specified as --all contexts::
    
        % python -m crds.sync --all
    
    this will recursively download all CRDS mappings for all time.
      
    *NOTE*:  Fetching references required to support contexts has to be done explicitly::
    
        % python -m crds.sync  --contexts hst_0001.pmap hst_0002.pmap  --fetch-references    
    
    will download all the references mentioned by contexts 0001 and 0002.   
    this can be a huge undertaking and should be done with care.
    
* Removing files:
      
    Rules/mappings from specified contexts can be removed like this::
    
        % python -m crds.sync  --contexts hst_0004.pmap hst_0005.pmap --purge-mappings
    
    this would remove mapping files which are *not* in 4 or 5.

    References from specified contexts can be removed like this::

      % python -m crds.sync  --contexts hst_0004.pmap hst_0005.pmap --purge-references
    
    this would remove reference files which are *not* in 4 or 5.

* References for particular datasets can be cached like this::
        
            % python -m crds.sync  --contexts hst_0001.pmap hst_0002.pmap --datasets  <dataset_files...>

      this will fetch all the references required to support the listed datasets for contexts 0001 and 0002.
      this mode does not update dataset file headers.  See also crds.bestrefs for header updates.

    
crds.bestrefs
-------------

crds.bestrefs computes the best references with respect to a particular context or contexts
for a set of FITS files, dataset ids,  or instruments::

    usage: python -m crds.bestfefs ...
           [-h] [-n NEW_CONTEXT] [-o OLD_CONTEXT] [-c] [-f FILES [FILES ...]]
           [-d IDs [IDs ...]] [-i INSTRUMENTS [INSTRUMENTS ...]]
           [--all-instruments] [-t REFERENCE_TYPES [REFERENCE_TYPES ...]] [-u]
           [--print-affected] [--print-new-references] [-r] [-s] [-v]
           [--verbosity VERBOSITY] [-V] [-J] [-H] [--profile PROFILE] [--pdb]
    
* Determines best references with respect to a context or contexts.   
* Optionally compares new results to prior results.
* Optionally prints source data names affected by the new context.
* Optionally updates the headers of file-based data with new recommendations.
        
Bestrefs has a number of command line parameters which make it operate in different modes:: 
    
    optional arguments:
      -h, --help            show this help message and exit
      -n NEW_CONTEXT, --new-context NEW_CONTEXT
                            Compute the updated best references using this context. Uses current operational context by default.
      -o OLD_CONTEXT, --old-context OLD_CONTEXT
                            Compare bestrefs recommendations from two contexts.
      -c, --compare-source-bestrefs
                            Compare new bestrefs recommendations to recommendations from data source,  files or database.
      -f FILES [FILES ...], --files FILES [FILES ...]
                            Dataset files to compute best references for.
      -d IDs [IDs ...], --datasets IDs [IDs ...]
                            Dataset ids to compute best references for.
      -i INSTRUMENTS [INSTRUMENTS ...], --instruments INSTRUMENTS [INSTRUMENTS ...]
                            Instruments to compute best references for, all historical datasets.
      --all-instruments     Compute best references for cataloged datasets for all supported instruments.
      -t REFERENCE_TYPES [REFERENCE_TYPES ...], --types REFERENCE_TYPES [REFERENCE_TYPES ...]
                            A list of reference types to process,  defaulting to all types.
      -u, --update-bestrefs
                            Update dataset headers with new best reference recommendations.
      --print-affected      Print names of data sets for which the new context would assign new references.
      --print-new-references
                            Prints messages detailing each reference file change.   If no comparison was requested,  prints all best references.
      -r, --remote-bestrefs
                            Compute best references from CRDS server
      -s, --sync-references
                            Fetch the refefences recommended by new context to the local cache.
      -v, --verbose         Set log verbosity to True,  nominal debug level.
      --verbosity VERBOSITY
                            Set log verbosity to a specific level: 0..100.
      -V, --version         Print the software version and exit.
      -J, --jwst            Force observatory to JWST for determining header conventions.
      -H, --hst             Force observatory to HST for determining header conventions.
      --profile PROFILE     Output profile stats to the specified file.
      --pdb                 Run under pdb.
    
...........
New Context
...........

crds.bestrefs always computes best references with respect to a context which can be explicitly specified with the 
``--new-context parameter``.    If ``--new-context`` is not specified,  the default operational context is determined by 
consulting the CRDS server or looking in the local cache.  

........................
Lookup Parameter Sources
........................

The two primary modes for bestrefs involve the source of reference file matching parameters.   Conceptually 
lookup parameters are always associated with particular datasets and used to identify the references
required to process those datasets.

The options ``--files``, ``--datasets``, ``--instruments``, and ``--all`` determine the source of lookup parameters:

1. To find best references for a list of files do something like this::

    % python -m crds.bestrefs --new-context hst.pmap --files j8bt05njq_raw.fits j8bt06o6q_raw.fits j8bt09jcq_raw.fits

the first parameter, hst.pmap,  is the context with respect to which best references are determined.

2. To find best references for a list of catalog dataset ids do something like this::

    % python -m crds.bestrefs --new-context hst.pmap --datasets j8bt05njq j8bt06o6q j8bt09jcq

3. To do mass scale testing for all cataloged datasets for a particular instrument(s) do::

    % python -m crds.bestrefs --new-context hst.pmap --instruments acs

4. To do mass scale testing for all supported instruments for all cataloged datasets do::

    % python -m crds.bestrefs --new-context hst.pmap --all
    
or to test for differences between two contexts do::

    % python -m crds.bestrefs --new-context hst_0002.pmap --old-context hst_0001.pmap --all

................
Comparison Modes
................

The ``--old-context`` and ``--compare-source-bestrefs`` parameters define the best references comparison mode.  Each names
the origin of a set of prior recommendations and implicitly requests a comparison to the recommendations from 
the newly computed bestrefs determined by ``--new-context``.

Context-to-Context
::::::::::::::::::

``--old-context`` can be used to specify a second context for which bestrefs are dynamically computed; ``--old-context`` 
implies that a bestrefs comparison will be made with ``--new-context``.   If ``--old-context`` is not specified,  it 
defaults to None.::
    
    % python -m crds.bestrefs --new-context hst_0042.pmap  --old-context hst_0040.pmap \
    --instruments acs
    
Prior Source Recommendations
::::::::::::::::::::::::::::

``--compare-source-bestrefs`` requests that the bestrefs from ``--new-context`` be compared to the bestrefs which are
recorded with the lookup parameter data,  either in the file headers of data files,  or in the catalog.   In both
cases the prior best references are recorded static values,  not dynamically computed bestrefs.::
 
     % python -m crds.bestrefs --new-context hst_0042.pmap  --compare-source-bestrefs \
    --datasets j8bt05njq j8bt06o6q
    
   
............
Output Modes
............

crds.bestrefs supports several output modes for bestrefs and comparison results to standard out.

If ``--print-affected`` is specified,  crds.bestrefs will print out the name of any file for which at least one update for
one reference type was recommended.   This is essentially a list of files to be reprocessed with new references.::

    % python -m crds.bestrefs --new-context hst.pmap --files j8bt05njq_raw.fits j8bt06o6q_raw.fits \
     --compare-source-bestrefs --print-affected
    j8bt05njq_raw.fits
    j8bt06o6q_raw.fits
    j8bt09jcq_raw.fits
    
............
Update Modes
............

crds.bestrefs initially supports one mode for updating the best reference recommendations recorded in data files::

    % python -m crds.bestrefs --new-context hst.pmap --files j8bt05njq_raw.fits j8bt06o6q_raw.fits \
     --compare-source-bestrefs --update-bestrefs

.........
Verbosity
.........

crds.bestrefs has ``--verbose`` and ``--verbosity=N`` parameters which can increase the amount of informational and debug output.



