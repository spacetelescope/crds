
Installation
============

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
       - analogous to crds.hst,  for JWST,  not yet developed.

Getting the Source Code
-----------------------

At this stage of development,  installing CRDS is accomplished by checking
CRDS source code out from subversion::

  % svn co https://subversion.assembla.com/svn/crds/trunk  crds
  % cd crds

Setting up your Environment
---------------------------

The CRDS checkout has a template file for the C-shell which defines
environment variables, env.csh.

* CRDS_MAPPATH defines the root location where your mappings files
  will be stored.  If left undefined mappings are installed/cached
  relative to the crds.<observatory> package directory, .e.g. crds.hst.

* CRDS_REFPATH defines the root location where locally cached reference
  files will be stored.   If left undefined references files are cached
  relative to the crds.<observatory>.references package directory.

* CRDS_SERVER_URL defines the base URL for accessing CRDS network
  services.  For non-developers this will always be set to the current
  operational CRDS server in env.csh and need not be changed.

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
  Installing hst
  Installing client
  Installing django-json-rpc
  zip_safe flag not set; analyzing archive contents...


Dependencies
------------

CRDS was developed in and for an STSCI Python environment suitable for pipeline
processing.   CRDS requires these additional packages to be installed in your
Python environment:

   * numpy
   * pyfits

