Command Line Tools
==================

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

crds.uses
---------

crds.uses searches the files in the local cache for mappings which refer to the 
specified files.  Since the local cache is used only mappings present in the local
cache will be included in the results given.  crds.uses is invoked as::

   % python -m crds.uses <observatory=hst|jwst> <mapping or reference>...

e.g.::

   % python -m crds.uses hst s7g1700gl_dead.fits


crds.matches
------------

crds.matches reports the match patterns which are associated with the given
reference files::

    % python -m crds.matches hst.pmap o8u2214fj_dxy.fits
    ('HRC', 'CLEAR1S', 'F220W')
    
    % python -m crds.matches --full hst.pmap o8u2214fj_dxy.fits
    ('hst', 'acs', 'dgeofile', 'HRC', 'CLEAR1S', 'F220W', '2002-03-01', '00:00:00')


crds.sync
---------


