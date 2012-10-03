
Installation
============

Getting the Source Code
-----------------------

At this stage of development,  installing CRDS is accomplished by checking
CRDS source code out from subversion::

  % svn co https://subversion.assembla.com/svn/crds/trunk  crds
  % cd crds

Setting up your Environment
---------------------------

The CRDS checkout has a template file for the C-shell which defines
environment variables, env.csh.   For JWST development,  there are
reasonable defaults for everything so you may not need to set these
at all.

Basic Environment
.................

    * **CRDS_PATH** defines a common directory tree where CRDS reference files
      and mappings are stored.   CRDS_PATH defaults to "/grp/crds/jwst".   Mappings
      are stored in ${CRDS_PATH}/mappings/[hst|jwst].   Reference files are
      stored in ${CRDS_PATH}/references/[hst|jwst].
    
    * **CRDS_SERVER_URL** defines the base URL for accessing CRDS network
      services.  CRDS_SERVER_URL defaults to http://not-a-crds-server.stsci.edu.
      Other fallbacks result in operational defaults for JWST only.
      
    * **CRDS_VERBOSITY** enables output of CRDS debug messages.   Set to an
      integer,  nominally 50.   Higher values output more information,  lower
      values less information.
      

Typical Build-1 Environments
............................

A typical build-1 environment for CRDS *within STScI* works by aligning the CRDS
file cache with the CRDS server's master copy of reference and mapping files.   
This makes the master copy of CRDS files on the server appear to be the user's 
personal file cache... with the exception that the files are readonly.   This
approach avoids creating additional copies of the reference files.

HST Settings
++++++++++++
::

  % setenv CRDS_PATH    /grp/crds/hst
  % setenv CRDS_SERVER_URL http://hst-crds.stsci.edu

JWST Settings
+++++++++++++
::
 
  % setenv CRDS_PATH /grp/crds/jwst
  % setenv CRDS_SERVER_URL http://not-a-crds-server.stsci.edu
  
Remote Settings
+++++++++++++++

Even for build-1 it's possible to operate CRDS over the network.  These settings
would create a cache named "crds" in the current working directory when CRDS
tools or functions are run::

   % setenv CRDS_PATH ./crds
   % setenv CRDS_SERVER_URL http://jwst-crds.stsci.edu
  
The main caveat is that the CRDS servers are only visible within STScI so outside
users must port-forward in order to reach the CRDS server.  As an alternative to
port forwarding,  an on-site user can create a local cache which should continue 
to work when they are off-site and don't have access to the server or central store.

Advanced Environment
....................

    * **CRDS_MAPPATH** can be used to override CRDS_PATH and define where 
      only mapping files are stored.   If mappings are pre-installed, the
      directory pointed to by CRDS_MAPPATH can be readonly.
      CRDS_MAPPATH defaults to ${CRDS_PATH}/mappings.
          
    * **CRDS_REFPATH** can be used to override CRDS_PATH and define where 
      only reference files are stored.  If references are pre-installed, the
      directory pointed to by CRDS_REFPATH can be readonly.
      CRDS_REFPATH defaults to ${CRDS_PATH}/references.
      
    * **CRDS_CFGPATH** can be used to override CRDS_PATH and define where 
      only server configuration information is cached.   The directory
      pointed to by CRDS_CFGPATH should be writable.   If CRDS is running in
      server-less mode,  this path is irrelevant.
      CRDS_CFGPATH defaults to ${CRDS_PATH}/config.
    
    * **CRDS_MODE** defines whether CRDS should compute best references using
      client software (local),  server software (remote),  or intelligently
      "fall up" to the server only when the client is deemed obsolete or
      the server cannot be reached (auto).   The default is auto.
      
    * **CRDS_CONTEXT** is an override naming the CRDS pipeline mapping (.pmap)
      used for computing best references.   Ordinarily,  CRDS will contact the 
      server to determine the operational pipeline mapping.
      If the server cannot be reached,  CRDS will look in CRDS_CFGPATH
      to determine the last pipeline context the server recommended.   If there
      is no prior server info available in the cache,  CRDS will fall-back to 
      using the default pre-installed mappings, e.g. jwst.pmap.
      When CRDS_CONTEXT is set, CRDS will ignore server recommendations and 
      availability and use the specified pipeline mapping.   However, CRDS_CONTEXT 
      will only be used when `context` was specified to getreferences() as None.
      If `context` was explicitly specified in a call to getreferences() and
      was not None,  the specified context will override CRDS_CONTEXT.   This
      enables the implementation of command line switches which supercede
      CRDS_CONTEXT.
       
Edit env.csh according to your preferences for where to put CRDS files.
Then source env.csh to define the variables in your environment::

  % source env.csh

Run the Install Script
----------------------

CRDS is partitioned into 3-4 Python packages each of which has it's own
setup.py script.   To make things easier,  the top level directory has a
single "install" script which runs all the individual setup.py scripts
for you::

     % ./install
    Installing lib
    Installing client
    Installing hst
    Installing jwst
    Installing tobs
    final status 000000
  
Test the installation
---------------------
CRDS client testing operates locally and does not require access to the 
server.   Basic CRDS client testing can be done as follows::

     % ./runtests
     ... copious test output...
    ----------------------------------------------------------------------
    Ran 59 tests in 13.749s
    
    OK

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
processing.   CRDS requires these additional packages to be installed in your
Python environment:

   * numpy
   * pyfits
   
For executing the unit tests (runtests) add:

   * nose
   * BeautifulSoup
   * stsci.tools
   
For building documentation add:

   * stsci.sphinxext   

