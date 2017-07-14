Package Overview
================

The CRDS client and command line software is distributed as a single package with
several sub-packages:

   * crds
       - Core package enabling local use and development of mappings
         and reference files.  contains command line utility programs.

   * crds.client
       - Network client library for interacting with the central CRDS server.  This is primarily for internal use in CRDS,  encapsulating JSONRPC interfaces with Python.

   * crds.hst
       - Observatory personality package for HST, defining how HST types, reference file certification constraints, and naming works.

   * crds.jwst
       - Analogous to crds.hst,  for JWST.

CRDS also contains a number of command line tools managed by a top-level *crds* command:

    * crds bestrefs
        - Best references utility for HST FITS files and context-to-context affected datasets computations.

    * crds sync
        - Cache download and maintenance tool, fetches, removes, checks, and repairs rules and references.

    * crds certify
        - Checks constraints and format for CRDS rules and references.

    * crds diff, crds rowdiff
        - Difference utility for rules and references,  also FITS table differences.

    * crds matches
        - Prints out parameter matches for particular references,  or database matching parameters with respect to particular dataset IDs.

    * crds uses
        - Lists files which refer to (are dependent on) some CRDS rules or reference file.

    * crds list
        - Lists cache files and configuration,  prints rules files,  dumps database dataset parameter dictionaries.

Each sub-command can also be invoked as follows::

     $ crds sync --help

to print help information,  where --help must be specified as the first parameter to the sub-command.

 
Installation
============

CRDS is a pure Python software package typically installed in the context of
other larger calibration software installations.  As such, if you already have
HST or JWST calibration software you may also have CRDS.

To check for CRDS try::

   $ crds list --version
   7.0.5, master, c95d1cc

If CRDS is not already installed,  it can be installed using in a variety of
mechanisms including AstroConda contrib, PyPi, and GitHub source code.   

Installation via AstroConda
---------------------------

One way to install CRDS directly is as an AstroConda contributed package.
Doing this requires first setting up both Anaconda (or mini-Conda) and the
AstroConda channel.  If HST or JWST pipeline calibration software is being
installed via a Conda distribution list, there is a good chance CRDS will be
installed as a dependency so explicit action may not be necessary.

Install Continuum's Anaconda
++++++++++++++++++++++++++++

Installing Anaconda gives you a generic environment for numerical programming.  See:

   https://www.continuum.io/downloads

for Anaconda installation instructions.

Set up AstroConda astronomy specific packages
+++++++++++++++++++++++++++++++++++++++++++++

AstroConda is a collaborative effort producing astronomy related packages and making
them available for installation via Conda.

   http://astroconda.readthedocs.io/en/latest/installation.html

Nominally,  setting up AstroConda is something like::

   $ conda config --add channels http://ssb.stsci.edu/astroconda
   $ conda create -n astroconda stsci
   $ source activate astroconda

Install CRDS AstroConda Contributed Package
+++++++++++++++++++++++++++++++++++++++++++

Once AstroConda is installed, CRDS can be installed as an AstroConda
contributed package::

   $ conda install crds

Typically however CRDS is automatically installed as a dependency of 
HST or JWST calibration software distributions.

Pip Installation
----------------

It's possible to install and update CRDS using Python's pip system like this::

   $ pip install crds

Installing CRDS via Conda is preferred since the CRDS version tends to be more
current and all other Python dependencies are more carefully controlled with
a distribution list that specifies component versions.

Installing from Source
----------------------

GitHub Checkout
+++++++++++++++

CRDS source code can be cloned from the GitHub source code repository as follows::

  $ git clone https://github.com/spacetelescope/crds.git CRDS
  $ cd CRDS

  $ # optionally,  switch to release tag
  $ git fetch origin
  $ git checkout <release tag,  e.g. 6.0.1>

Run the Install Script
++++++++++++++++++++++
Installing from source,  run the install script in the root source code directory::

    $ cd CRDS
    $ ./install
    final status 000000

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

OPTIONAL: 
   * jwst.datamodels    needed to run crds certify on JWST references
   * lockfile           needed to synchronize local CRDS cache syncs done by associations

OPTIONAL: For running crds.certify to fully check CRDS rules/mapping files add:
   * Parsley-1.2
   * pyaml  (for certifying and using yaml references)
   * asdf (for certifying and using ASDF references)

OPTIONAL: For building documentation add:
   * docutils
   * sphinx
   * stsci.sphinxext


Best references Basics
======================

The primary function of CRDS is to assign the names of calibration reference files required
to calibrate datasets to their metadata headers.

CRDS bestrefs for HST
---------------------

CRDS provides the crds.bestrefs program for updating dataset headers for HST with the current
best references.   Running bestrefs for HST is accomplished via::

    % crds bestrefs --files dataset*.fits --update-bestrefs

This command updates the files specified by dataset*.fits with the names of the latest best
reference files.

CRDS bestrefs for JWST
----------------------

The crds.bestrefs functionality that assigns best references to datasets is fully integrated with the
JWST calibration software and operates transparently as a consequence of running pipelines::

     % strun calwebb_sloper.cfg dataset.fits

The above command will transparently update the reference files specified in the metadata of dataset.fits.

Default Onsite Use:
-------------------

The CRDS default configuration permits CRDS to operate onsite with no explicit
environment settings.

By default, CRDS operates using /grp/crds/cache with no connection to any CRDS
server.  

Files and settings in /grp/crds/cache define the references that CRDS will
assign to a given dataset.

Offsite and Pipeline Use:
-------------------------

CRDS can be configured to operate from private/local CRDS caches.  See the
instructions below for setting CRDS_PATH and CRDS_SERVER_URL.

A private cache reduces the level of network i/o required for offsite use as
well as eliminating constant dependence on CRDS web servers required to run a
pipeline.  A private cache can also contain writable files suitable for
experimentation.

Onsite pipelines use private caches to reduce file system contention.

Offsite pipelines use private caches to achieve more independence from STScI.

Setting up your Environment
===========================

Configuring CRDS for pipeline or offsite personal use is accomplished by setting
shell environment variables.

Basic Environment
-----------------

Two environment variables which define basic CRDS setup using a private cache::

    % setenv CRDS_SERVER_URL  <some_crds_server>
    % setenv CRDS_PATH        <some_crds_reference_and_rules_cache_directory>

If you are currently working on only a single project,  it may be helpful to declare that project::

    % setenv CRDS_OBSERVATORY   hst (or jwst)

Once the private CRDS cache is synced,  these settings enable CRDS to operate without an
always-on connection to the CRDS server or /grp/crds/cache.

In addition, having a local cache of files can reduce the transparent network
I/O implied by accessing /grp/crds/cache via a VPN based connection to access
gigabytes of data.

Setup for On-site Operational Use (HST or JWST)
-----------------------------------------------

This section describes use of operational reference files onsite at STScI.  It's relevant to fully archived
and operational files,  not development and test.

File Cache Location (CRDS_PATH)
+++++++++++++++++++++++++++++++

The location of the CRDS cache is defined by the CRDS_PATH environment setting.

The defaut value of CRDS_PATH is /grp/crds/cache and requires direct access to that on site file system.

A remote or pipeline user defines a non-default CRDS cache by setting, e.g.::

    % setenv CRDS_PATH   $HOME/crds_cache

Note that the CRDS cache is often used to store reference files and when fully
populated for a particular mission can contain *terabytes* of files.  Hence,
demand-based caching for particular datasets (using crds.bestrefs or strun) is
probably preferred to sync'ing the entire cache using the crds.sync.

Server Selection (CRDS_SERVER_URL)
++++++++++++++++++++++++++++++++++

Since each project (and test systems) is supported by a different CRDS server
a user must define the CRDS server they wish to use.

For **HST**::

    % setenv CRDS_SERVER_URL https://hst-crds.stsci.edu

For **JWST**::

    % setenv CRDS_SERVER_URL https://jwst-crds.stsci.edu

If CRDS cannot determine your project, and you did not specify CRDS_SERVER_URL,  it will be defaulted to::

   % setenv CRDS_SERVER_URL https://crds-serverless-mode.stsci.edu

In serverless mode it is not possible for CRDS to download new files or configuration settings,
so best reference recommendations may become stale.

Onsite CRDS Testing
+++++++++++++++++++

For reference type development, updates are generally made and tested in the
test pipelines at STScI.  For coordinating with those tests, **CRDS_PATH** and
**CRDS_SERVER_URL** must be explicitly set to a test cache and server similar
to this::

    % setenv CRDS_PATH  ${HOME}/crds_cache_test
    % setenv CRDS_SERVER_URL https://hst-crds-test.stsci.edu

Alternative servers for JWST I&T testing are::

    % setenv CRDS_SERVER_URL https://jwst-crds-b5it.stcsi.edu     # build-5
    % setenv CRDS_SERVER_URL https://jwst-crds-b6it.stcsi.edu     # build-6
    % setenv CRDS_SERVER_URL https://jwst-crds-dit.stcsi.edu      # build-7

After syncing this will provide access to CRDS test files and rules in a local cache::

    # Fetch all the test rules
    % crds sync --all

    # Fetch specifically listed test references
    % crds sync --files <test_references_only_the_test_server_has...>

Testing reference type changes (new keywords, new values or value restrictions,
etc) may also require access to development versions of CRDS code.  In
particular, when adding parameters or changing legal parameter values, the
certify tool is modified as "code" on the servers first.  Hence distributed
versions of CRDS will not reflect ongoing type changes.  The test server
Certify Files function should generally reflect the most up-to-date knowledge
CRDS has about ongoing type changes.  To see how new reference files stack up
with changing CRDS code, try submitting the files to Certify Files on the test
server or ask what the status is on crds_team@stsci.edu.

**NOTE:** Without VPN or port forwarding, the test servers are not usable offsite.

Setup for Offsite Use
---------------------

CRDS has been designed to (optionally) automatically fetch and cache references
you need to process your datasets to a personal CRDS cache.  You can create a
small personal cache of rules and references supporting only the datasets you
care about::

    % setenv CRDS_SERVER_URL  https://hst-crds.stsci.edu   # or similar
    % setenv CRDS_PATH  ${HOME}/crds_cache

For **HST**, to fetch the references required to process some FITS datasets::

    % crds bestrefs --files dataset*.fits --sync-references=1  --update-bestrefs

For **JWST**, CRDS is directly integrated with the calibration step code and
will automatically download rules and references as needed.

CRDS Cache Locking
------------------

CRDS cache locking (file-based, currently built upon the lockfile package) has
been added to support JWST associations calibration multi-processing. Since
associations launch multiple concurrent processes, it poses a problem of
simultaneous updates to the shared CRDS cache resource.  Cache locking
addresses that issue and is automatically used for read/write caches typically
associated with offsite use.

There are multiple conditions in CRDS that determine when locking is really
used::

    1. The lockfile package must be installed and importable
    2. The CRDS_LOCK_PATH directory (nominally /tmp) should already exist   
    2. A lockfile lock must be successully created
    3. The CRDS cache must be physically writable
    4. CRDS_USE_LOCKING must be undefined or 1
    5. CRDS_READONLY_CACHE must be undefined or 0

Otherwise, locking is either broken or the sync is impossible or forbidden.

The env var::

  CRDS_READONLY_CACHE=1

currently prevents HST + JWST pipeline installations from using locking.

The readonly nature of::

  /grp/crds/cache

prevents the use of locking for typical onsite users.  /grp/crds/cache is
complete, automatically maintained by CRDS, and needs no user-based updates or
file downloads.

The env var::

  CRDS_LOCK_PATH

can be used to define the location of file locks, defaulting to */tmp*. It
should be noted that the existence of the lock file directory is itself a
concurrency issue, so it must be created or otherwise available before cache
synchronization takes place.

The CRDS command::

  $ crds sync --clear-locks

can be used to remove orphan locks (due to some unexpected failure) that are
blocking processing.

Locking requires installation of the *lockfile* package and CRDS-7.1.4 or later.

Additional HST Settings
+++++++++++++++++++++++

HST calibration software accesses reference files indirectly through
environment variables.  There are two forms of CRDS cache reference file
organization: flat and with instrument subdirectories.  The HST calibration
software environment variable settings depend on the CRDS cache layout.

JWST calibration code refers to explict cache paths at runtime and does 
not require these additional settings.

Flat Cache Layout for /grp/crds/cache
.....................................

The flat cache layout places all references in a single directory.  The
shared group cache at /grp/crds/cache has a flat organization::

  setenv iref ${CRDS_PATH}/references/hst/
  setenv jref ${CRDS_PATH}/references/hst/
  setenv oref ${CRDS_PATH}/references/hst/
  setenv lref ${CRDS_PATH}/references/hst/
  setenv nref ${CRDS_PATH}/references/hst/
  setenv uref ${CRDS_PATH}/references/hst/
  setenv uref_linux $uref

By-Instrument Cache Layout
..........................

The default cache setup for newly created caches for HST is organized by instrument.

Unless you reorganize your cache using the crds.sync tool,  these are the settings
that are most likely to be appropriate for a personal HST cache.

For HST calibration software to use references in a CRDS cache with a by-instrument
organization, set these environment variables::

  setenv iref ${CRDS_PATH}/references/hst/iref/
  setenv jref ${CRDS_PATH}/references/hst/jref/
  setenv oref ${CRDS_PATH}/references/hst/oref/
  setenv lref ${CRDS_PATH}/references/hst/lref/
  setenv nref ${CRDS_PATH}/references/hst/nref/
  setenv uref ${CRDS_PATH}/references/hst/uref/
  setenv uref_linux $uref

Reorganizing CRDS References
............................

The crds.sync tool can be used to reorganize the directory structure of an
existing CRDS cache.   These organizations determine whether or not 
reference files are partitioned into instrument-specific sub-directories.

To switch from flat to by-instrument::

  crds sync --organize=instrument

To switch from by-instrument to flat::

  crds sync --organize=flat

JWST Context
++++++++++++

The CRDS context file defines a version of CRDS rules used to assign best references.

The CRDS context used to evaluate CRDS best references for JWST defaults to jwst-operational.  This
is an indirect name for the context in use or soon-to-be in use in the archive pipeline.

During development jwst-operational corresponds to the latest context which is
sufficiently mature for broad use.  Use of jwst-operational is automatic.

The context used for JWST can be overridden to some specific historical or experimental context by setting
the **CRDS_CONTEXT** environment variable::

    % setenv CRDS_CONTEXT jwst_0057.pmap

**CRDS_CONTEXT** does not override command line switches or parameters passed explicitly to the
crds.getreferences() API function.


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

**CRDS_ALLOW_BAD_RULES**  enable CRDS to use assigment rules which have been
designated as bad files / scientifically invalid.

**CRDS_ALLOW_BAD_REFERENCES** enable CRDS to assign reference files which have
been designated as scientifically invalid after issuing a warning.

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

