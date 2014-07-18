Package Overview
================

The CRDS client and command line software is distributed as a single package with
several sub-packages:

   * crds
       - core package enabling local use and development of mappings
         and reference files.  contains command line utility programs.

   * crds.cache
        - prototype cache which contains the original baseline CRDS mappings generated
        for HST and JWST,  also demonstrating cache structure for a dual project cache.

   * crds.client
       - network client library for interacting with the central CRDS server.  This is
       primarily for internal use in CRDS,  encapsulating JSONRPC interfaces with Python.
   
   * crds.hst
       - observatory personality package for HST, defining how HST types, reference file
       certification constraints, and naming works.
   
   * crds.jwst
       - analogous to crds.hst,  for JWST.
   
   * crds.tobs
       - test observatory supporting artificial rules cases and tests.
       
CRDS also contains a number of command line tools:

    * crds.bestrefs
        - Best references utility for HST FITS files and context-to-context affected datasets computations.
    
    * crds.sync
        - Cache download and maintenance tool, fetches, removes, checks, and repairs rules and references.
        
    * crds.certify
        - Checks constraints and format for CRDS rules and references. 
    
    * crds.diff, crds.rowdiff
        - Difference utility for rules and references,  also FITS table differences.
    
    * crds.matches
        - Prints out parameter matches for particular references,  or database matching parameters with
        respect to particular dataset IDs.
    
    * crds.uses
        - Lists files which refer to (are dependent on) some CRDS rules or reference file.
        
    * crds.list
        - Lists cache files and configuration,  prints rules files,  dumps database dataset parameter dictionaries.
        
More information can be found on each tool using the command line -- --help switch,  e.g.::

    % python -m crds.bestrefs --help
    
or in the command line tools section of this document.

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


Setting up your Environment
===========================

CRDS is used in a number of different contexts and consequently is configurable.   The defaults for 
CRDS are tuned for onsite use at STScI using operational references,  requiring little or no configuration.

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

**NOTE:** the test server is only visible on-site,  not on the internet.  Without VPN or port forwarding,  the test
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
    
For **HST**, to fetch the references required to process some FITS datasets::

    % python -m crds.bestrefs --files dataset*.fits --sync-references=1
    
By default crds.bestrefs does not alter your dataset FITS files.   If you also wish to update your dataset FITS 
headers with best references,  add --update-bestrefs.
    
For **JWST**,  CRDS is directly integrated with the calibration step code and will automatically download
rules and references as needed.   Downloads will only be an issue when you set CRDS_PATH and don't already
have the files you need in your cache.   By default CRDS modifies JWST datasets with new best references
which serve as a processing history in the dataset header.

Users of */grp/crds/cache* cannot update the readonly cache so they should not attempt to run crds.sync or
fetch references with crds.bestrefs.  */grp/crds/cache* should always be complete within a few hours of archiving
any new reference or rules delivery,  changing the operational context,  or marking files bad.


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
--------------------

A number of things in CRDS are configurable with envionment variables,  most important of which is the
location and structure of the file cache.

Multi-Project Caches
++++++++++++++++++++

**CRDS_PATH** defines a cache structure for multiple projects. Each major branch of a multi-project cache 
contains project specific subdirectories::

    /cache
        /mappings
            /hst
                hst mapping files...
            /jwst
                jwst mapping files...
        /references
            /hst
                hst reference files...
            /jwst
                jwst reference files...
        /config
            /hst
                hst config files...
            /jwst
                jwst config files...
                
- *mappings* contains versioned rules files for CRDS reference file assignments

- *references* contains reference files themselves

- *config* contains system configuration information like operational context and bad files

Inidivdual branches of a cache can be overriden to locate that branch outside the directory
tree specified by CRDS_PATH.   The remaining directories can be overriden as well or derived 
from CRDS_PATH.

**CRDS_MAPPATH** can be used to override CRDS_PATH and define where 
only mapping files are stored.  CRDS_MAPPATH defaults to ${CRDS_PATH}/mappings
which contains multiple observatory-specific subdirectories.
      
**CRDS_REFPATH** can be used to override CRDS_PATH and define where 
only reference files are stored.  CRDS_REFPATH defaults to ${CRDS_PATH}/references
which contains multiple observatory specific subdirectoriers.
  
**CRDS_CFGPATH** can be used to override CRDS_PATH and define where 
only configuration information is cached. CRDS_CFGPATH defaults to ${CRDS_PATH}/config
which can contain multiple observatory-spefific subdirectories.

Specifying CRDS_MAPPATH = /somewhere when CRDS_OBSERVATORY = hst means that
mapping files will be located in /somewhere/hst.

While it can be done,  it's generally considered an error to use a multi-project cache
with different servers for the *same observatory*, e.g. both hst-test and hst-ops.

Single Project Caches
+++++++++++++++++++++    

**CRDS_PATH_SINGLE** defines a cache structure for a single project.  The component paths 
implied by **CRDS_PATH_SINGLE**  omit the observatory subdirectory,  giving a simpler and 
shallower cache structure::

    /cache
        /mappings
            mapping_files...
        /references
            reference files...
        /config
            config files...
    
It's an error to use a single project cache with more than one project or server.  It is
inadvisable to mix multi-project (no _SINGLE) and single-project (_SINGLE) configuration
variables,  set one or the other form,  not both.

As with **CRDS_PATH**,  there are overrides for each cache branch which can locate it
independently.

**CRDS_MAPPATH_SINGLE** can be used to override CRDS_PATH and define where only 
mapping files are stored. CRDS_MAPPATH_SINGLE defaults to ${CRDS_PATH}/mappings
but is presumed to support only one observatory.
      
**CRDS_REFPATH_SINGLE** can be used to override CRDS_PATH and define where 
only reference files are stored.  CRDS_REFPATH_SINGLE defaults to ${CRDS_PATH}/references
but is presumed to support only one observatory.
  
**CRDS_CFGPATH_SINGLE** can be used to override CRDS_PATH and define where 
only server configuration information is cached.   CRDS_CFGPATH_SINGLE defaults to 
${CRDS_PATH}/config but is presumed to support only one observatory.

Specifying CRDS_MAPPATH_SINGLE = /somewhere when CRDS_OBSERVATORY = hst means that
mapping files will be located in /somewhere,  not in /somewhere/hst.
    
Miscellaneous Variables
+++++++++++++++++++++++    
    
**CRDS_VERBOSITY** enables output of CRDS debug messages.   Set to an
integer,  nominally 50.   Higher values output more information,  lower
values less information.   CRDS also has command line switches 
--verbose (level=50) and --verbosity=<level>.   Verbosity level 
ranges from 0 to 100 and defaults to 0 (no verbose output).

**CRDS_IGNORE_MAPPING_CHECKSUM** causes CRDS to waive mapping checksums 
when set to True,  useful when you're editing them.

**CRDS_READONLY_CACHE** limits tools to readonly access to the cache when set 
to True.  Eliminates cache writes which occur implicitly.  This is mostly 
useful in CRDS server user cases which want to ensure not modifying the server
CRDS cache but cannot write protect it effectively.

**CRDS_MODE** defines whether CRDS should compute best references using
installed client software only (local),  on the server (remote),  or 
intelligently "fall up" to the server (when the installed client is deemed
obsolete relative to the server) or "fall down" to the local installation 
(when the server cannot be reached) (auto).   The default is auto.

**CRDS_CLIENT_RETRY_COUNT** number of times CRDS will attempt a network 
transaction with the CRDS server.  Defaults to 1 meaning 1 try with no retries.

**CRDS_CLIENT_RETRY_DELAY_SECONDS** number of seconds CRDS waits after a failed
network transaction before trying again.  Defaults to 0 seconds,  meaning 
proceed immediately after fail.

