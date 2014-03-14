
Installation
============

Getting the Source Code
-----------------------

CRDS source code can be downloaded from the *planned* CRDS subversion repository like this::

  % svn co https://aeon.stsci.edu/ssb/svn/crds/trunk  crds

Historically,  and at the time of build-1.0 release,  CRDS is maintained on Assembla::

  % svn co https://subversion.assembla.com/svn/crds/trunk  crds
  
Setting up your Environment
---------------------------

Basic Environment
.................

The following environment variables are necessary for basic CRDS setup.

    **CRDS_PATH** defines the location of the CRDS cache of reference files and file assignment rules (aka mappings).   
    
    On site at STScI, set CRDS_PATH to the appropriate read only cache at /grp/crds/hst or /grp/crds/jwst.
    
    Off site, set CRDS_PATH to a directory for the working set of references required to process your data sets, e.g. ${HOME}/crds_cache.
    
    CRDS provides mechanisms downloading missing files to the cache defined by CRDS_PATH.   The readonly caches
    under /grp/crds should be complete and hence wont require user-specific downloads.
    
    The nominal size of a completely populated CRDS cache is currently 1.5 terabytes.
    
    **CRDS_SERVER_URL** defines the CRDS web server your CRDS client will interact with.   The CRDS server is 
    used to supply rules and reference files, to define the current file assignment rules, and to notify you of the
    use of any scientifically invalid files.

On Site HST Settings
++++++++++++++++++++
For working with any HST context or reference on site, in its unmodified form, with no download required::

  % setenv CRDS_PATH    /grp/crds/hst
  % setenv CRDS_SERVER_URL https://hst-crds.stsci.edu

On Site JWST Settings
+++++++++++++++++++++
For working with any JWST context or reference on site, in its unmodified form, with no download required::
 
  % setenv CRDS_PATH /grp/crds/jwst
  % setenv CRDS_SERVER_URL https://jwst-crds.stsci.edu

Off Site / Personal Settings
++++++++++++++++++++++++++++
For working with a small personal set of reference files, in a writable form, downloading files to 
your private cache::

   % setenv CRDS_PATH ${HOME}/crds_cache
   % setenv CRDS_SERVER_URL https://jwst-crds.stsci.edu
        or 
   % setenv CRDS_SERVER_URL https://hst-crds.stsci.edu
   
The JWST pipeline will transparently download the required rules and references to your local cache.  

For HST, the crds.bestrefs tool is used to update raw datasets and to sync required rules and 
references to your local cache.

Once files are downloaded to a personal cache, you can compute and utilize best references without
access to the CRDS server.

NOTE:  sites without access to the appropriate CRDS server will not be notified of new references,
assignment changes, or invalid files.   Disconnected sites continue to operate using the last 
information cached from the CRDS server.

Additional HST Settings
+++++++++++++++++++++++

HST calibration steps access reference files indirectly through environment variables.  Those variables
should be set to point to the appropriate directory under CRDS_PATH::

  % setenv iref ${CRDS_PATH}/references/hst
  % setenv jref ${CRDS_PATH}/references/hst
  % setenv oref ${CRDS_PATH}/references/hst
  % setenv iref ${CRDS_PATH}/references/hst
  % setenv lref ${CRDS_PATH}/references/hst
  % setenv nref ${CRDS_PATH}/references/hst
  % setenv upsf ${CRDS_PATH}/references/hst
  % setenv uref unsupported or ${uref_linux}
  % setenv uref_linux ${CRDS_PATH}/references/hst

Advanced Environment
....................

Developers may find these useful:
    
    **CRDS_CONTEXT** is an override naming the CRDS pipeline mapping
    used for computing best references,  e.g. jwst_0011.pmap.   CRDS_CONTEXT 
    overrides the server definition of the operational context and is 
    primarily used by JWST.   CRDS_CONTEXT does not override internal 
    function parameters passed to crds.getreferences(),  neither does it 
    override command line switches.
       
    **CRDS_VERBOSITY** enables output of CRDS debug messages.   Set to an
    integer,  nominally 50.   Higher values output more information,  lower
    values less information.   Leave it 0 for non-verbose.
    
Institutional pipelines may find these useful:

    **CRDS_MODE** defines whether CRDS should compute best references using
    installed client software only (local),  on the server (remote),  or 
    intelligently "fall up" to the server (when the installed client is deemed
    obsolete relative to the server) or "fall down" to the local installation 
    (when the server cannot be reached) (auto).   The default is auto.
    
These support caches with parts under different root directories:

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
      
Run the Install Script
----------------------
CRDS is installed by running the install script in the root source code directory::

     % cd crds
     % ./install
    final status 000000

Test the installation
---------------------
Basic CRDS client testing can be performed from the source code directory as follows::

     % cd crds
     % source envs/hst-crds-readonly.csh
     % ./runtests
    ........... lots of dots ....
    ----------------------------------------------------------------------
    Ran 157 tests in 41.232s
    
    OK
    
Test errors will result if the CRDS server at https://hst-crds.stsci.edu is not accessible
from your network.

Package Overview
----------------

From the perspective of an end user,  CRDS consists of 3 or more Python
packages which implement different capabilities:

   * crds
       - core package enabling local use and development of mappings
         and reference files.
   * crds.client
       - network client library for interacting with the central CRDS server.
   * crds.hst
       - observatory personality package for HST,  with initial mappings for
         bootstrapping CRDS and defining how HST files are named, located, and
         certified.
   * crds.jwst
       - analogous to crds.hst,  for JWST.

Dependencies
------------

CRDS was developed in and for an STSCI Python environment suitable for pipeline
processing.   Standard STScI calibration environments should already include it.
Nevertheless, for installing CRDS independently, these dependencies are applicable:

REQUIRED: CRDS requires these dependencies to be installed in your Python environment:

   * numpy
   * pyfits
   * astropy
   
OPTIONAL: For executing the unit tests (runtests) add:

   * nose
   * BeautifulSoup
   * stsci.tools
   
OPTIONAL: For running crds.certify to fully check CRDS rules/mapping files add:

   * Parsley-1.1  (included in the CRDS source distribution under third_party)
   
OPTIONAL: For building documentation add:

   * stsci.sphinxext   

