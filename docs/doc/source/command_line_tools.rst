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

    Usage: certify.py [options] <inpaths...>
    
    Options:
      -h, --help            show this help message and exit
      -d, --deep            Certify reference files referred to by mappings have
                            valid contents.
      -e, --exist           Certify reference files referred to by mappings exist.
      -m, --mapping         Ignore extensions, the files being certified are
                            mappings.
      -p, --dump-provenance
                            Print provenance keyword values.
      -t TRAP_EXCEPTIONS, --trap-exceptions=TRAP_EXCEPTIONS
                            Capture exceptions at level: pmap, imap, rmap,
                            selector, debug, none
      -x CONTEXT, --context=CONTEXT
                            Pipeline context defining replacement reference.
      -V VERBOSITY, --verbose=VERBOSITY
                            Set verbosity level.
                            
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

    Usage: diff.py [options] <file1> <file2>
            
            Appropriately difference CRDS mapping or reference files.
            
    
    Options:
      -h, --help            show this help message and exit
      -J, --jwst            Locate files using JWST naming conventions.
      -H, --hst             Locate files using HST naming conventions.
      -V VERBOSITY, --verbose=VERBOSITY
                            Set verbosity level.

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


crds.file_bestrefs *(preliminary)*
----------------------------------

crds.file_bestrefs computes the best references for a set of dataset FITS files
with respect to a particular context or contexts::

    Usage: file_bestrefs.py [options] <new_context> <datasets...>
    
    Options:
      -h, --help            show this help message and exit
      -c, --cache-headers   Use and remember critical header parameters in a
                            cache file.
      -f FILELIST, --files=FILELIST
                            Read datasets from FILELIST, one dataset per line.
      -o OLD_CONTEXT, --old-context=OLD_CONTEXT
                            Compare best refs recommendations from two contexts.
      -u, --update-datasets
                            Update dataset headers with new best reference
                            recommendations.
      -V VERBOSITY, --verbose=VERBOSITY
                            Set verbosity level.
                            
*crds.file_bestrefs* can be invoked as::

    % python -m crds.file_bestrefs hst.pmap *_raw.fits
    CRDS        : INFO     New Reference for 'j8bt05njq_raw.fits' 'imphttab' is 'w3m1716tj_imp.fits' was 'undefined'
    CRDS        : INFO     New Reference for 'j8bt05njq_raw.fits' 'npolfile' is 'v9718263j_npl.fits' was 'undefined'
    CRDS        : INFO     New Reference for 'j8bt06o6q_raw.fits' 'imphttab' is 'w3m1716tj_imp.fits' was 'undefined'
    CRDS        : INFO     New Reference for 'j8bt06o6q_raw.fits' 'npolfile' is 'v9718264j_npl.fits' was 'undefined'
    CRDS        : INFO     New Reference for 'j8bt09jcq_raw.fits' 'imphttab' is 'w3m1716tj_imp.fits' was 'undefined'
    CRDS        : INFO     New Reference for 'j8bt09jcq_raw.fits' 'npolfile' is 'v9718260j_npl.fits' was 'undefined'
    Reference Changes:
    {'imphttab': ['j8bt05njq_raw.fits',
                  'j8bt06o6q_raw.fits',
                  'j8bt09jcq_raw.fits'],
     'npolfile': ['j8bt05njq_raw.fits',
                  'j8bt06o6q_raw.fits',
                  'j8bt09jcq_raw.fits']}
    0 errors
    0 warnings
    6 infos

.. crds.sync *(preliminary)*
    -------------------------
    
    crds.sync downloads references and mappings from the CRDS server based on a
    variety of specification mechanisms.


