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

    Checks a CRDS reference or mapping file.
        
    positional arguments:
      files
    
    optional arguments:
      -h, --help            show this help message and exit
      -d, --deep            Certify reference files referred to by mappings have valid contents.
      -r, --dont-recurse-mappings
                            Do not load and validate mappings recursively,  checking only directly specified files.
      -a, --dont-parse      Skip slow mapping parse based checks,  including mapping duplicate entry checking.
      -e, --exist           Certify reference files referred to by mappings exist.
      -m, --mapping         Ignore extensions, the files being certified are mappings.
      -p, --dump-provenance
                            Dump provenance keywords.
      -t TRAP_EXCEPTIONS, --trap-exceptions TRAP_EXCEPTIONS
                            Capture exceptions at level: pmap, imap, rmap, selector, debug, none
      -x COMPARISON_CONTEXT, --comparison-context COMPARISON_CONTEXT
                            Pipeline context defining comparison files.
      -y COMPARISON_REFERENCE, --comparison-reference COMPARISON_REFERENCE
                            Comparison reference for table certification.
      --dump-unique-errors  Record and dump the first instance of each kind of error.
      --unique-errors-file UNIQUE_ERRORS_FILE
                            Write out data names (ids or filenames) for first instance of unique errors to specified file.
      --all-errors-file ALL_ERRORS_FILE
                            Write out all err'ing data names (ids or filenames) to specified file.
      -v, --verbose         Set log verbosity to True,  nominal debug level.
      --verbosity VERBOSITY
                            Set log verbosity to a specific level: 0..100.
      -R, --readonly-cache  Don't modify the CRDS cache.  Not compatible with options which implicitly modify the cache.
      -V, --version         Print the software version and exit.
      -J, --jwst            Force observatory to JWST for determining header conventions.
      -H, --hst             Force observatory to HST for determining header conventions.
                            
crds.certify is invoked as, e.g.::

    % python -m crds.certify --comparison-context=hst_0027.pmap   some_reference.fits
    
    % python -m crds.certify hst.pmap
    
Invoking crds.certify on a context mapping recursively certifies all sub-mappings.

crds.diff
---------

crds.diff compares two reference or mapping files and reports differences.  For
references crds.diff is currently a thin wrapper around fitsdiff but may expand.   

For CRDS mappings crds.diff performs a recursive logical difference which shows 
the full match path to each bottom level change.   crds.diff --help yields::

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
        
        % python -m crds.diff hst_0001.pmap  hst_0005.pmap  --mapping-text-diffs --primitive-diffs
        
    Will recursively produce logical, textual, and FITS diffs for all changes between the two contexts.
        
        NOTE: mapping logical differences (the default) do not compare CRDS mapping headers,  use
        --include-header-diffs to get those as well.
    

For standard CRDS filenames,  crds.diff can guess the observatory.   For 
non-standard names,  the observatory needs to be specified.  crds.diff can be
invoked like::

  % python -m crds.diff   jwst_nircam_dark_0010.fits  jwst_nircam_dark_0011.fits

  % python -m crds.diff  jwst_0001.pmap   jwst_0002.pmap
  (('hst.pmap', 'hst_0004.pmap'), ('hst_acs.imap', 'hst_acs_0004.imap'), ('hst_acs_darkfile.rmap', 'hst_acs_darkfile_0003.rmap'), ('WFC', 'A|ABCD|AD|B|BC|C|D', '0.5|1.0|1.4|2.0'), '2011-03-16 23:34:35', "replaced 'v441434ej_drk.fits' with 'hst_acs_darkfile_0003.fits'")


crds.rowdiff
------------
Modules that are based on FITSDiff, such as crds.diff, compare
tabular data on a column-by-column basis. Rowdiff compares tabular data
on a row-by-row basis, producing UNIX diff-like output instead.
Non-tabular extensions are ignored.

    usage: rowdiff.py [-J] [-H]
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

The parameters --fields and --ignore-fields define which columns
are compared between each table extension. These are mutually
exclusive parameters and an error will generate if both are specified.

First a summary of the changes between the table extension is given.
Then, row-by-row difference is given, using unified diff syntax.

The parameter --mode-fields initiates a different algorithm.
Here, it is presumed the tabular data contains columns that can essentially
be treated as keys upon with rows are selected. The fields specified are those
key columns.

All possible coombinations of values are determined be examining both
extensions. Then, each table is compared against both this list and between
each other, looking for multiply specified combinations, missing combinations,
and, for the common combinations between the tables, whether the rest of the
rows are equivalent or not.

Examples:

    % python -m crds.rowdiff s9m1329lu_off.fits s9518396u_off.fits 

    % python -m rowdiff s9m1329lu_off.fits s9518396u_off.fits --mode-fields=detchip,obsdate


crds.uses
---------

crds.uses searches the files in the local cache for mappings which refer to the 
specified files.  Since the **local cache** is used only mappings present in the 
local cache will be included in the results given.  crds.uses is invoked as::

   % python -m crds.uses <observatory=hst|jwst> <mapping or reference>...

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
    
    % python -m crds.uses --files n3o1022ij_drk.fits --hst
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
    
    % python -m crds.uses --files n3o1022ij_drk.fits --print-datasets --hst
    J8BA0HRPQ
    J8BA0IRTQ
    J8BA0JRWQ
    J8BA0KT4Q
    J8BA0LIJQ
    
    % python -m crds.uses --files @dropped --hst --print-datasets --include-used
    vb41934lj_bia.fits JA7P21A2Q
    vb41934lj_bia.fits JA7P21A4Q
    vb41934lj_bia.fits JA7P21A6Q

crds.matches
------------

crds.matches reports the match patterns which are associated with the given
reference files::

    usage: matches.py
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

crds.matches can dump reference file match cases with respect to particular contexts::
    
    % python -m crds.matches  --contexts hst_0001.pmap --files lc41311jj_pfl.fits
    lc41311jj_pfl.fits : ACS PFLTFILE DETECTOR='WFC' CCDAMP='A|ABCD|AC|AD|B|BC|BD|C|D' FILTER1='F625W' FILTER2='POL0V' DATE-OBS='1997-01-01' TIME-OBS='00:00:00'
    
    % python -m crds.matches --contexts hst.pmap --files lc41311jj_pfl.fits --omit-parameter-names --brief-paths
    lc41311jj_pfl.fits :  'WFC' 'A|ABCD|AC|AD|B|BC|BD|C|D' 'F625W' 'POL0V' '1997-01-01' '00:00:00'
    
    % python -m crds.matches --contexts hst.pmap --files lc41311jj_pfl.fits --tuple-format
    lc41311jj_pfl.fits : (('OBSERVATORY', 'HST'), ('INSTRUMENT', 'ACS'), ('FILEKIND', 'PFLTFILE'), ('DETECTOR', 'WFC'), ('CCDAMP', 'A|ABCD|AC|AD|B|BC|BD|C|D'), ('FILTER1', 'F625W'), ('FILTER2', 'POL0V'), ('DATE-OBS', '1997-01-01'), ('TIME-OBS', '00:00:00'))
    
crds.matches can dump database matching parameters for specified datasets with respect to specified contexts::
    
    % python -m crds.matches --datasets JBANJOF3Q --minimize-headers --contexts hst_0048.pmap hst_0044.pmap
    JBANJOF3Q : hst_0044.pmap : APERTURE='WFC1-2K' ATODCORR='NONE' BIASCORR='NONE' CCDAMP='B' CCDCHIP='1.0' CCDGAIN='2.0' CRCORR='NONE' DARKCORR='NONE' DATE-OBS='2010-01-31' DETECTOR='WFC' DQICORR='NONE' DRIZCORR='NONE' FILTER1='F502N' FILTER2='F660N' FLASHCUR='OFF' FLATCORR='NONE' FLSHCORR='NONE' FW1OFFST='0.0' FW2OFFST='0.0' FWSOFFST='0.0' GLINCORR='NONE' INSTRUME='ACS' LTV1='-2048.0' LTV2='-1.0' NUMCOLS='UNDEFINED' NUMROWS='UNDEFINED' OBSTYPE='INTERNAL' PCTECORR='NONE' PHOTCORR='NONE' REFTYPE='UNDEFINED' SHADCORR='NONE' SHUTRPOS='B' TIME-OBS='01:07:14.960000' XCORNER='1.0' YCORNER='2072.0'
    JBANJOF3Q : hst_0048.pmap : APERTURE='WFC1-2K' ATODCORR='NONE' BIASCORR='NONE' CCDAMP='B' CCDCHIP='1.0' CCDGAIN='2.0' CRCORR='NONE' DARKCORR='NONE' DATE-OBS='2010-01-31' DETECTOR='WFC' DQICORR='NONE' DRIZCORR='NONE' FILTER1='F502N' FILTER2='F660N' FLASHCUR='OFF' FLATCORR='NONE' FLSHCORR='NONE' FW1OFFST='0.0' FW2OFFST='0.0' FWSOFFST='0.0' GLINCORR='NONE' INSTRUME='ACS' LTV1='-2048.0' LTV2='-1.0' NAXIS1='2070.0' NAXIS2='2046.0' OBSTYPE='INTERNAL' PCTECORR='NONE' PHOTCORR='NONE' REFTYPE='UNDEFINED' SHADCORR='NONE' SHUTRPOS='B' TIME-OBS='01:07:14.960000' XCORNER='1.0' YCORNER='2072.0'
    
crds.matches can be invoked in various ways with different output formatting::
    
    % python -m crds.matches  --contexts hst_0001.pmap --files lc41311jj_pfl.fits
    lc41311jj_pfl.fits : ACS PFLTFILE DETECTOR='WFC' CCDAMP='A|ABCD|AC|AD|B|BC|BD|C|D' FILTER1='F625W' FILTER2='POL0V' DATE-OBS='1997-01-01' TIME-OBS='00:00:00'
    
    % python -m crds.matches --contexts hst.pmap --files lc41311jj_pfl.fits --omit-parameter-names --brief-paths
    lc41311jj_pfl.fits :  'WFC' 'A|ABCD|AC|AD|B|BC|BD|C|D' 'F625W' 'POL0V' '1997-01-01' '00:00:00'
    
    % python -m crds.matches --contexts hst.pmap --files lc41311jj_pfl.fits --tuple-format
    lc41311jj_pfl.fits : (('OBSERVATORY', 'HST'), ('INSTRUMENT', 'ACS'), ('FILEKIND', 'PFLTFILE'), ('DETECTOR', 'WFC'), ('CCDAMP', 'A|ABCD|AC|AD|B|BC|BD|C|D'), ('FILTER1', 'F625W'), ('FILTER2', 'POL0V'), ('DATE-OBS', '1997-01-01'), ('TIME-OBS', '00:00:00'))


crds.sync 
---------

The CRDS sync tool is used to download CRDS rules and references from the CRDS server::
    
    usage: python -m crds.sync
       [-h] [--contexts [CONTEXT [CONTEXT ...]]] [--range MIN:MAX] [--all]
       [--last N] [-i] [--files [FILES [FILES ...]]]
       [--datasets [DATASET [DATASET ...]]] [--fetch-references]
       [--purge-references] [--purge-mappings] [--dry-run] [-k] [-s] [-r]
       [--purge-rejected] [--purge-blacklisted] [--fetch-sqlite-db] [-v]
       [--verbosity VERBOSITY] [-R] [-V] [-J] [-H] 

    Synchronize local mapping and reference caches for the given contexts by
    downloading missing files from the CRDS server and/or archive.

optional arguments::

  -h, --help            show this help message and exit
  --contexts [CONTEXT [CONTEXT ...]]
                        Specify a list of CRDS mappings to operate on: .pmap, .imap, or .rmap or date-based specification
  --range MIN:MAX       Operate for pipeline context ids (.pmaps) between <MIN> and <MAX>.
  --all                 Operate with respect to all known CRDS contexts.
  --last N              Operate with respect to the last N contexts.
  -i, --ignore-cache    Download required files even if they're already in the cache.
  --files [FILES [FILES ...]]
                        Explicitly list files to be synced.
  --datasets [DATASET [DATASET ...]]
                        Cache references for the specified datasets.
  --fetch-references    Cache all the references for the specified contexts.
  --purge-references    Remove reference files not referred to by contexts from the cache.
  --purge-mappings      Remove mapping files not referred to by contexts from the cache.
  --dry-run             Don't remove purged files, or repair files,  just print out their names.
  -k, --check-files     Check cached files against the CRDS database and report anomalies.
  -s, --check-sha1sum   For --check-files,  also verify file sha1sums.
  -r, --repair-files    Repair or re-download files noted as bad by --check-files
  --purge-rejected      Purge files noted as rejected by --check-files
  --purge-blacklisted   Purge files (and their mapping anscestors) noted as blacklisted by --check-files
  --fetch-sqlite-db     Download a sqlite3 version of the CRDS file catalog.
  -v, --verbose         Set log verbosity to True,  nominal debug level.
  --verbosity VERBOSITY
                        Set log verbosity to a specific level: 0..100.
  -R, --readonly-cache  Don't modify the CRDS cache.  Not compatible with options which implicitly modify the cache.
  -V, --version         Print the software version and exit.
  -J, --jwst            Force observatory to JWST for determining header conventions.
  -H, --hst             Force observatory to HST for determining header conventions.


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
  
NOTE:  Fetching references required to support contexts has to be done explicitly::

    % python -m crds.sync  --contexts hst_0001.pmap hst_0002.pmap  --fetch-references

will download all the references mentioned by contexts 0001 and 0002.   
this can be a huge (1T+) network download and should generally only be used by
institutions,  not individual researchers.
    
* Removing files:
              
Files from unspecified contexts can be removed like this::
        
    % python -m crds.sync  --contexts hst_0004.pmap hst_0005.pmap --purge-mappings

this would remove mappings which are *not* in contexts 4 or 5.
    
    % python -m crds.sync  --contexts hst_0004.pmap hst_0005.pmap --purge-references

this would remove reference files which are *not* in 4 or 5.
    
* References for particular datasets can be cached like this::
                
    % python -m crds.sync  --contexts hst_0001.pmap hst_0002.pmap --datasets  <dataset_files...>

this will fetch all the references required to support the listed datasets for contexts 0001 and 0002.
this mode does not update dataset file headers.  See also crds.bestrefs for header updates.
              
* Checking the cache::
        
    % python -m crds.sync --contexts hst_0001.pmap --fetch-references --check-files --check-sha1sum --repair-files
    
would first sync the cache downloading all the files in hst_0001.pmap.  Both mappings and references would then
be checked for correct length, sha1sum, and status.   Any files with bad length or checksum
would then be deleted and re-downloaded.   This is really intended for an *existing* cache.
      
Removing blacklisted or rejected files::
              
    % python -m crds.sync --contexts hst_0001.pmap --fetch-references --check-files --purge-rejected --purge-blacklisted

would first sync the cache downloading all the files in hst_0001.pmap.  Both mappings and references would then
be checked for correct length.   Files reported as rejected or blacklisted by the server would be removed.

crds.bestrefs
-------------

crds.bestrefs computes the best references with respect to a particular context or contexts
for a set of FITS files, dataset ids,  or instruments::

    usage: python -m crds.bestrefs
           [-h] [-n NEW_CONTEXT] [-o OLD_CONTEXT] [-c] [-f FILES [FILES ...]]
           [-d IDs [IDs ...]] [--all-instruments]
           [-i INSTRUMENTS [INSTRUMENTS ...]]
           [-t REFERENCE_TYPES [REFERENCE_TYPES ...]]
           [-k SKIPPED_REFERENCE_TYPES [SKIPPED_REFERENCE_TYPES ...]]
           [--diffs-only] [--datasets-since DATASETS_SINCE]
           [-p [LOAD_PICKLES [LOAD_PICKLES ...]]] [-a SAVE_PICKLE]
           [--only-ids [IDS [IDS ...]]] [-u] [--print-affected]
           [--print-affected-details] [--print-new-references]
           [--print-update-counts] [-r] [-m SYNC_MAPPINGS] [-s SYNC_REFERENCES]
           [--differences-are-errors] [-e] [--undefined-differences-matter]
           [--na-differences-matter] [--compare-cdbs] [-z] [--dump-unique-errors]
           [--unique-errors-file UNIQUE_ERRORS_FILE]
           [--all-errors-file ALL_ERRORS_FILE] [-v] [--verbosity VERBOSITY] [-R]
           [-V] [-J] [-H] 

* Determines best references with respect to a context or contexts.   
* Optionally compares new results to prior results.
* Optionally prints source data names affected by the new context.
* Optionally updates the headers of file-based data with new recommendations.

* optional arguments::
    
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
                          Dataset ids to consult database for matching parameters and old results.
    --all-instruments     Compute best references for cataloged datasets for all supported instruments in database.
    -i INSTRUMENTS [INSTRUMENTS ...], --instruments INSTRUMENTS [INSTRUMENTS ...]
                          Instruments to compute best references for, all historical datasets in database.
    -t REFERENCE_TYPES [REFERENCE_TYPES ...], --types REFERENCE_TYPES [REFERENCE_TYPES ...]
                          A list of reference types to process,  defaulting to all types.
    -k SKIPPED_REFERENCE_TYPES [SKIPPED_REFERENCE_TYPES ...], --skip-types SKIPPED_REFERENCE_TYPES [SKIPPED_REFERENCE_TYPES ...]
                          A list of reference types which should not be processed,  defaulting to nothing.
    --diffs-only          For context-to-context comparison, choose only instruments and types from context differences.
    --datasets-since DATASETS_SINCE
                          Cut-off date for datasets, none earlier than this.  Use 'auto' to exploit reference USEAFTER.
    -p [LOAD_PICKLES [LOAD_PICKLES ...]], --load-pickles [LOAD_PICKLES [LOAD_PICKLES ...]]
                          Load dataset headers and prior bestrefs from pickle files,  in worst-to-best update order.
    -a SAVE_PICKLE, --save-pickle SAVE_PICKLE
                          Write out the combined dataset headers to the specified pickle file.
    --only-ids [IDS [IDS ...]]
                          If specified, process only the listed dataset ids.
    -u, --update-bestrefs
                          Update dataset headers with new best reference recommendations.
    --print-affected      Print names of products for which the new context would assign new references for some exposure.
    --print-affected-details
                          Include instrument and affected types in addition to compound names of affected exposures.
    --print-new-references
                          Prints one line per reference file change.  If no comparison requested,  prints all bestrefs.
    --print-update-counts
                          Prints dictionary of update counts by instrument and type,  status on updated files.
    -r, --remote-bestrefs
                          Compute best references on CRDS server,  convenience for env var CRDS_MODE='remote'
    -m SYNC_MAPPINGS, --sync-mappings SYNC_MAPPINGS
                          Fetch the required context mappings to the local cache.  Defaults TRUE.
    -s SYNC_REFERENCES, --sync-references SYNC_REFERENCES
                          Fetch the refefences recommended by new context to the local cache. Defaults FALSE.
    --differences-are-errors
                          Treat recommendation differences between new context and original source as errors.
    -e, --bad-files-are-errors
                          Treat recommendations of known bad/invalid files as errors, not warnings.
    --undefined-differences-matter
                          If not set, a transition from UNDEFINED to anything else is not considered a difference error.
    --na-differences-matter
                          If not set,  either CDBS or CRDS recommending N/A is OK to mismatch.
    --compare-cdbs        Abbreviation for --compare-source-bestrefs --differences-are-errors --dump-unique-errors --stats
    -z, --optimize-tables
                          If set, apply row-based optimizations to screen out inconsequential table updates.
    --dump-unique-errors  Record and dump the first instance of each kind of error.
    --unique-errors-file UNIQUE_ERRORS_FILE
                          Write out data names (ids or filenames) for first instance of unique errors to specified file.
    --all-errors-file ALL_ERRORS_FILE
                          Write out all err'ing data names (ids or filenames) to specified file.
    -v, --verbose         Set log verbosity to True,  nominal debug level.
    --verbosity VERBOSITY
                          Set log verbosity to a specific level: 0..100.
    -R, --readonly-cache  Don't modify the CRDS cache.  Not compatible with options which implicitly modify the cache.
    -V, --version         Print the software version and exit.
    -J, --jwst            Force observatory to JWST for determining header conventions.
    -H, --hst             Force observatory to HST for determining header conventions.

Bestrefs has a number of command line parameters which make it operate in different modes. 

...........
New Context
...........

crds.bestrefs always computes best references with respect to a context which can be explicitly specified with the 
--new-context parameter.    If --new-context is not specified,  the default operational context is determined by 
consulting the CRDS server or looking in the local cache.  

........................
Lookup Parameter Sources
........................

The two primary modes for bestrefs involve the source of reference file matching parameters.   Conceptually 
lookup parameters are always associated with particular datasets and used to identify the references
required to process those datasets.

The options --files, --datasets, --instruments, and --all-instruments determine the source of lookup parameters:

1. To find best references for a list of files do something like this:

    % python -m crds.bestrefs --new-context hst.pmap --files j8bt05njq_raw.fits j8bt06o6q_raw.fits j8bt09jcq_raw.fits

the first parameter, hst.pmap,  is the context with respect to which best references are determined.

2. To find best references for a list of catalog dataset ids do something like this:

    % python -m crds.bestrefs --new-context hst.pmap --datasets j8bt05njq j8bt06o6q j8bt09jcq

3. To do mass scale testing for all cataloged datasets for a particular instrument(s) do:

    % python -m crds.bestrefs --new-context hst.pmap --instruments acs

4. To do mass scale testing for all supported instruments for all cataloged datasets do:

    % python -m crds.bestrefs --new-context hst.pmap --all-instruments
    
    or to test for differences between two contexts

    % python -m crds.bestrefs --new-context hst_0002.pmap --old-context hst_0001.pmap --all-instruments

................
Comparison Modes
................

The --old-context and --compare-source-bestrefs parameters define the best references comparison mode.  Each names
the origin of a set of prior recommendations and implicitly requests a comparison to the recommendations from 
the newly computed bestrefs determined by --new-context.

Context-to-Context
::::::::::::::::::

--old-context can be used to specify a second context for which bestrefs are dynamically computed; --old-context 
implies that a bestrefs comparison will be made with --new-context.   If --old-context is not specified,  it 
defaults to None.

Prior Source Recommendations
::::::::::::::::::::::::::::

--compare-source-bestrefs requests that the bestrefs from --new-context be compared to the bestrefs which are
recorded with the lookup parameter data,  either in the file headers of data files,  or in the catalog.   In both
cases the prior best references are recorded static values,  not dynamically computed bestrefs.
    
............
Output Modes
............

crds.bestrefs supports several output modes for bestrefs and comparison results to standard out.

If --print-affected is specified,  crds.bestrefs will print out the name of any file for which at least one update for
one reference type was recommended.   This is essentially a list of files to be reprocessed with new references.::

    % python -m crds.bestrefs --new-context hst.pmap --files j8bt05njq_raw.fits j8bt06o6q_raw.fits j8bt09jcq_raw.fits \
        --compare-source-bestrefs --print-affected
    j8bt05njq_raw.fits
    j8bt06o6q_raw.fits
    j8bt09jcq_raw.fits
    
............
Update Modes
............

crds.bestrefs initially supports one mode for updating the best reference recommendations recorded in data files::

    % python -m crds.bestrefs --new-context hst.pmap --files j8bt05njq_raw.fits j8bt06o6q_raw.fits j8bt09jcq_raw.fits \
        --compare-source-bestrefs --update-bestrefs

.........
Verbosity
.........

crds.bestrefs has --verbose and --verbosity=N parameters which can increase the amount of informational 
and debug output.


pipeline_bestrefs
-----------------

The pipeline_bestrefs script is a shim around crds.bestrefs which simplifies the command line interface,
tuning it to the more limited case of updating FITS dataset headers with best references::

    usage: pipeline_bestref [-d] [-v] [-h] [--print-affected] <crds_context> <dataset_file(s)>...
    
    -d                     dry run,  do not update file headers
    -v                     verbose,  output additional diagnostic messages
    -h                     help,  print this help
    --print-affected       print files with updated bestrefs
    
    Updates dataset FITS files with best references recommended by <crds_context>.
    
    <crds_context> is a CRDS context file, explicitly named e.g. hst_0004.pmap
    <crds_context> can be specified abstractly,  e.g.  hst-edit or hst-operational
    <crds_context> can be specified by date,  e.g.  hst-2013-01-29T12:00:00
    
    <dataset_file(s)> are raw dataset files for which best references are
    computed and updated.



