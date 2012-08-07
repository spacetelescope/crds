
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
at all.   For HST,  at a minimum CRDS_SERVER_URL must be defined.

    * CRDS_PATH defines a common directory tree where CRDS reference files
      and mappings are stored.   CRDS_PATH defaults to "./crds".   Mappings
      are stored in ${CRDS_PATH}/mappings/[hst|jwst].   Reference files are
      stored in ${CRDS_PATH}/references/[hst|jwst].
    
    * CRDS_MAPPATH can be used to override CRDS_PATH and define where 
      only mapping files are stored.
    
    * CRDS_REFPATH can be used to override CRDS_PATH and define where 
      only reference files are stored.
    
    * CRDS_SERVER_URL defines the base URL for accessing CRDS network
      services.  CRDS_SERVER_URL defaults to the jwst test server.
      
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

