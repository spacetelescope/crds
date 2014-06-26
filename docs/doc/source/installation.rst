Installation
============

Most people will encounter CRDS as software distributed side-by-side with calibration code,
and consequently CRDS will be pre-installed.

Installing with PIP
-------------------

CRDS is available on pypi and explicitly installable using pip::

% pip install crds

Installing from Source
----------------------

Subversion Checkout
++++++++++++++++++++++

Alternately, CRDS source code can be downloaded from the CRDS subversion repository like this::

  % svn co https://aeon.stsci.edu/ssb/svn/crds/trunk  crds
  
Run the Install Script
++++++++++++++++++++++
Installing from source,  run the install script in the root source code directory::

     % cd crds
     % ./install
    final status 000000

Test the installation
---------------------
Basic CRDS client testing can be performed onsite at STScI from the source code directory as follows::

     % cd crds
     % source envs/hst-crds-readonly.csh
     % ./runtests
    ........... lots of dots ....
    ----------------------------------------------------------------------
    Ran 157 tests in 41.232s
    
    OK
    
Test errors will result if the CRDS server at https://hst-crds.stsci.edu or Central Store
file system /grp/crds/hst are not accessible from your network or host.


Dependencies
------------

CRDS was developed in and for an STSCI Python environment suitable for pipeline
processing.   Standard STScI calibration environments should already include it.
Nevertheless, for installing CRDS independently, these dependencies are applicable:

REQUIRED: CRDS requires these dependencies to be installed in your Python environment:

   * numpy
   * astropy
   
OPTIONAL: For executing the unit tests (runtests) add:

   * nose
   * BeautifulSoup
   * stsci.tools
   
OPTIONAL: For running crds.certify to fully check CRDS rules/mapping files add:

   * Parsley-1.1  (included in CRDS subversion under third_party)
   
OPTIONAL: For building documentation add:
   * docutils
   * sphinx
   * stsci.sphinxext   


Package Overview
----------------

CRDS consists of 3 or more Python packages which implement different capabilities:

   * crds
       - core package enabling local use and development of mappings
         and reference files.  contains command line utility programs.
   * crds.client
       - network client library for interacting with the central CRDS server.
   * crds.hst
       - observatory personality package for HST, defining how HST types, reference file
       certification constraints, and naming works.
   * crds.jwst
       - analogous to crds.hst,  for JWST.
   * crds.tobs
       - test observatory supporting artificial rules cases and tests.

Setting up your Environment
===========================

Basic Environment
-----------------

CRDS supports HST and JWST projects using project-specific servers and an explicit cache of CRDS rules and reference
files.   CRDS has two environment variables which define basic setup.   These variables control the server where CRDS 
obtains rules and references and where CRDS caches files to on your local system::

    % setenv CRDS_SERVER_URL  <some_crds_server>
    % setenv CRDS_PATH        <some_crds_reference_and_rules_cache_directory>
    
If you are currently working on only a single project,  it may be helpful to declare that project::

    % setenv CRDS_OBSERVATORY   hst (or jwst)
        
Setup for On Site Operartional Use (HST or JWST)
------------------------------------------------

This section describes use of operational reference files onsite at STScI.  It's relevant to fully archived
operational files,  not development and test.

File Cache Location (CRDS_PATH)
+++++++++++++++++++++++++++++++

For typical onsite use at STScI, CRDS users can share a file cache which contains all rules and references.  The
location of the shared cache initially defaults to::

    /grp/crds/cache
    
/grp/crds/cache is designed to support both HST and JWST with a single defaulted **CRDS_PATH** setting.

Since /grp/crds/cache is the default,  you don't have to explicitly set **CRDS_PATH**.

Since /grp/crds/cache starts out containing all the operational CRDS rules and reference files, file downloads
are not required.

Server Selection (CRDS_SERVER_URL)
++++++++++++++++++++++++++++++++++

Since each project is supported by a different operational server, CRDS must determine which (if any)
server to use.  

Starting with OPUS 2014.3 and crds-1.1,  CRDS does a reasonable job guessing what project you're working on.

CRDS can guess the project you're working on by:
    
* Looking for the string 'hst' or 'jwst' in the file names you're operating on.
* Looking inside files to determine the applicable instrument, and inferring the project from the instrument name.
* If you explicitly set CRDS_SERVER_URL,  CRDS can ask the server which project it supports.

You can tell CRDS which project you're working on by:

* Using command line switches in CRDS utility programs:  ----hst or ----jwst
* Setting CRDS_OBSERVATORY to 'hst' or 'jwst'

If you're working on both projects frequently,  using the command line hints,  e.g. ----hst,  is probably
preferred whenever CRDS has trouble guessing.

If you're primarily working on one project,  definining **CRDS_OBSERVATORY** is probably most convenient
since then you won't need to provide command line hints.
    
If CRDS can determine the project,  and you don't specify CRDS_SERVER_URL,  CRDS will use the default
operational server for your project:

=======         ============================
Project         Implicit CRDS_SERVER_URL
=======         ============================
hst             https://hst-crds.stsci.edu
jwst            https://jwst-crds.stsci.edu
=======         ============================

If CRDS cannot determine your project,  and you did not specify CRDS_SERVER_URL,  it will be defaulted to::

https://crds-serverless-mode.stsci.edu

In serverless mode, dynamic cache updates are not possible so cache information may become stale.  This affects CRDS 
rules and reference updates,  CRDS knowledge of the current operational context, and CRDS knowledge of rules or 
references determined to be bad.   On the other hand,  in serverless-mode you're guaranteed to be working with 
a static system, and no warnings will  be issued because the server is not reachable.

Onsite CRDS Testing
+++++++++++++++++++

For reference type development,  updates are generally made and tested in the test pipelines at STScI.  For
coordinating with those tests,  **CRDS_PATH** and **CRDS_SERVER_URL** must be explicitly set to a test cache and server
similar to this::

    % setenv CRDS_PATH  ${HOME}/crds_cache_test
    % setenv CRDS_SERVER_URL https://hst-crds-test.stsci.edu

After syncing this will provide access to CRDS test files and rules in a local cache::

    # Fetch all the test rules
    % python -m crds.sync --all
    # Fetch specifically listed test references
    % python -m crds.sync --files <test_references_only_the_test_server_has...>   

Testing reference type changes (new keywords,  new values or value restrictions, etc) may also require access to 
development versions of CRDS code.   In particular,  when adding parameters or changing legal parameter values,  
the certify tool is modified as "code" on the servers first.   Hence distributed versions of CRDS will not reflect 
ongoing type changes.

It should be noted that the test server is only visible on site,  not on the open internet.  Without VPN,  the test
servers are not usable off site.

Setup for Offsite Use
---------------------

CRDS has been designed to (optionally) automatically fetch and cache references you need to process your datasets.
Rather than going to a website and downloading a tarball of recommended references,  the CRDS tools,  which know
the references you need,  can go to the website for you and download the files you need to your cache.  Once you've
cached a file,  unless you delete it,  you never have to download it again.

For offsite users without VPN access who are running local calibrations,  you can create a small personal 
cache of rules and references supporting only the datasets you care about::

    % setenv CRDS_PATH  ${HOME}/crds_cache
    
For **HST**, to fetch the latest CRDS rules and references for some FITS datasets::

    % python -m crds.bestrefs --files dataset*.fits --sync-references=1
    
By default crds.bestrefs does not alter your dataset FITS files.   If you also wish to update your dataset FITS 
headers with best references,  add --update-bestrefs.
    
For **JWST**,  CRDS is directly integrated with the calibration step code and will automatically download
rules and references as needed.   Downloads will only be an issue when you set CRDS_PATH and don't already
have the files you need in your cache.   By default CRDS modifies JWST datasets with new best references
which serve as a processing history in the dataset header.


Additional HST Settings
+++++++++++++++++++++++

HST calibration steps access reference files indirectly through environment variables.  Those variables
should be set to point to the appropriate directory under CRDS_PATH::

  % setenv iref ${CRDS_PATH}/references/hst
  % setenv jref ${CRDS_PATH}/references/hst
  % setenv oref ${CRDS_PATH}/references/hst
  % setenv lref ${CRDS_PATH}/references/hst
  % setenv nref ${CRDS_PATH}/references/hst
  % setenv uref ${uref_linux}
  % setenv uref_linux ${CRDS_PATH}/references/hst
  
Currently the CRDS cache is structured so that references from all instruments of a project reside in one common 
directory.


JWST Setups
-----------

JWST Setup for STScI
++++++++++++++++++++

The nominal setup for someone operating on site at STScI for JWST will use a common shared read-only cache 
which contains all of the current CRDS rules and references.   This cache will be automatically synchronized
by CRDS with the CRDS server, pipeline, and archive.     CRDS users cannot modify these references.   
On site CRDS users are not required to download these references. CRDS configuration to use the default
CRDS cache is automatic.

JWST Setup for Offsite Use
++++++++++++++++++++++++++

Offsite without VPN,  /grp/crds/cache is presumed to be unavailable.   If you choose to
create a personal local CRDS cache, do the following::

    % setenv CRDS_SERVER_URL https://jwst-crds.stsci.edu
    % setenv CRDS_PATH  ${HOME}/crds_cache

It should be noted that this configuration can potentially lead to transparent downloads of gigabytes of 
references required to process your datasets,  resulting in long delays until you have the required files in your 
cache.

NOTE:  sites without access to the appropriate CRDS server will not be notified of new references,
assignment changes, or invalid files.   Disconnected sites continue to operate using the last 
information cached from the CRDS server.

JWST Context
++++++++++++

The CRDS context used to evaluate CRDS best references for JWST defaults to jwst-operational,  the changing
symbolic context which is in use in the JWST pipeline.  During early development jwst-operational corresponds
to the latest context which is sufficiently mature for broad use.  Use of jwst-operational is automatic.

The context used for JWST can be overridden to some specific historical or experimental context by setting
the **CRDS_CONTEXT** environment variable::

    % setenv CRDS_CONTEXT jwst_0057.pmap

**CRDS_CONTEXT** does not override command line switches or parameters passed explicitly to crds.getreferences().



Advanced Environment
....................

**CRDS_PATH_SINGLE** supports a cache structure for a single project.  It's
an error to use such a cache for more than one project.   The component paths
implied by **CRDS_PATH_SINGLE** omit the observatory subdirectory,  giving a
simpler and shallower cache structure::

    /cache
        /mappings
            mapping_files...
        /references
            reference files...
        /config
            config files...
    
These variables support caches with parts under different root directories:

    **CRDS_MAPPATH** can be used to override CRDS_PATH and define where 
    only mapping files are stored.   The directory pointed to by 
    CRDS_MAPPATH can be readonly.  CRDS_MAPPATH defaults to 
    ${CRDS_PATH}/mappings.
          
    **CRDS_REFPATH** can be used to override CRDS_PATH and define where 
    only reference files are stored.  The directory pointed to by CRDS_REFPATH
    can be readonly.   CRDS_REFPATH defaults to ${CRDS_PATH}/references.
      
    **CRDS_CFGPATH** can be used to override CRDS_PATH and define where 
    only server configuration information is cached.   The directory
    pointed to by CRDS_CFGPATH should be writable.
    CRDS_CFGPATH defaults to ${CRDS_PATH}/config.
    
    Each of these paths points to a directory containing observatory subdirectories
    which contain actual files.  For example:
    
    Specifying CRDS_MAPPATH = /somewhere when CRDS_OBSERVATORY = hst means that
    mapping files will be located in /somewhere/hst
    
These variables support caches with parts under different root directories, but
supporting only a single observatory.  Hence there is no observatory suffix 
and the given path points directly to a directory containing files,  not one
containing observatory sub-directories.

    **CRDS_MAPPATH_SINGLE** can be used to override CRDS_PATH and 
    define where only mapping files are stored. CRDS_MAPPATH_SINGLE defaults to 
    ${CRDS_PATH}/mappings and is presumed to support only one observatory.
          
    **CRDS_REFPATH_SINGLE** can be used to override CRDS_PATH and define where 
    only reference files are stored.  CRDS_REFPATH_SINGLE defaults to 
    ${CRDS_PATH}/references and is presumed to support only one observatory.
      
    **CRDS_CFGPATH_SINGLE** can be used to override CRDS_PATH and define where 
    only server configuration information is cached.  CRDS_CFGPATH defaults to 
    ${CRDS_PATH}/config.   CRDS_CFGPATH_SINGLE defaults to 
    ${CRDS_PATH}/config and is presumed to support only one observatory.
    
    Each of these paths points to a directory directly containing files of the 
    appropriate kind with no observatory subdirectory implied. For example:
    
    Specifying CRDS_MAPPATH_SINGLE = /somewhere when CRDS_OBSERVATORY = hst means that
    mapping files will be located in /somewhere,  not in /somewhere/hst.
    
    
Developers may find these useful:
    
    **CRDS_VERBOSITY** enables output of CRDS debug messages.   Set to an
    integer,  nominally 50.   Higher values output more information,  lower
    values less information.   Leave it 0 for non-verbose.
    
Institutional pipelines may find these useful:

    **CRDS_MODE** defines whether CRDS should compute best references using
    installed client software only (local),  on the server (remote),  or 
    intelligently "fall up" to the server (when the installed client is deemed
    obsolete relative to the server) or "fall down" to the local installation 
    (when the server cannot be reached) (auto).   The default is auto.
    

      

