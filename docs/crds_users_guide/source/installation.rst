Package Overview
================

The CRDS client and command line software is distributed as a single package with
several sub-packages:

   * crds
       - core package enabling local use and development of mappings
         and reference files.  contains command line utility programs.

   * crds.client
       - network client library for interacting with the central CRDS server.  This is
       primarily for internal use in CRDS,  encapsulating JSONRPC interfaces with Python.

   * crds.hst
       - observatory personality package for HST, defining how HST types, reference file
       certification constraints, and naming works.

   * crds.jwst
       - analogous to crds.hst,  for JWST.

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

CRDS bestrefs for JWST:

The crds.bestrefs functionality which assigns best references to datasets is fully integrated with the
JWST calibration software and operates transparently as a consequence of running pipelines.

Local Use:

The CRDS defaults are set for onsite use at STScI.   These leverage a shared read-only cache of CRDS rules
and references currently located at /grp/crds/cache.  HST users will need to set their iref$-style environment
variables accordingly to use references maintained by CRDS in /grp/crds/cache,  see below.

Remote Use:

CRDS can be configured to operate at remote sites by defining a CRDS server and a local cache directory.  With
this configuration CRDS will transparently download the best references and CRDS rules required to calibrate datasets
on demand.  See below for configuration instructions.

More information can be found on each tool using the command line -- --help switch,  e.g.::

    % python -m crds.bestrefs --help

or in the command line tools section of this document.

Installation
============

Installation via Ureka or Conda
-------------------------------

Most people install CRDS as part of STScI/SSB's (Science Software Branch) Ureka (or now Conda) which is found here:

    http://ssb.stsci.edu/ureka/

Follow the instructions for installing Ureka and afterward you should be able to do the following::

    % python -m crds.list --version
    CRDS  : INFO     crds version 1.9.0 revision 2789:2793M

and get similar output reflecting your installed CRDS version.

Pip Installation
----------------

It's possible to install and update CRDS using Python's pip system like this::

   % pip install crds

Because of the dependencies required by CRDS such as numpy and astropy,  installing via Ureka is preferred
and will provide a system closer or identical to the one in pipeline use.

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

OPTIONAL: For running crds.certify to fully check CRDS rules/mapping files add:

   * Parsley-1.2
   * pyaml  (for certifying and using yaml references)
   * asdf (for certifying and using ASDF references)

OPTIONAL: For building documentation add:
   * docutils
   * sphinx
   * stsci.sphinxext


Setting up your Environment
===========================

CRDS is used in a number of different contexts and consequently is configurable.   The defaults for
CRDS are tuned for onsite use at STScI using operational references,  requiring little or no configuration onsite.
Subsequent instructions are provided for setting up more personalized or offsite environments.

Basic Environment
-----------------

CRDS supports HST and JWST projects using project-specific servers and an explicit cache of CRDS rules and reference
files.   CRDS has two environment variables which define basic setup.   These variables control the server where CRDS
obtains rules and references and where CRDS caches files to on your local system::

    % setenv CRDS_SERVER_URL  <some_crds_server>
    % setenv CRDS_PATH        <some_crds_reference_and_rules_cache_directory>

If you are currently working on only a single project,  it may be helpful to declare that project::

    % setenv CRDS_OBSERVATORY   hst (or jwst)

**NOTE:**  CRDS operates from and manages the CRDS cache.   Direct edits of the cache are not recommended in
most cases,  with the possible exception of in-place edits of personal rules or reference files.   Changes to
other files or directory structure,   including cache creation,  are not recommended.   Files in the cache
are subject to automatic replacement or deletion by the CRDS framework and should be viewed as temporary
working copies only.

Setup for On-site Operartional Use (HST or JWST)
------------------------------------------------

This section describes use of operational reference files onsite at STScI.  It's relevant to fully archived
operational files,  not development and test.

File Cache Location (CRDS_PATH)
+++++++++++++++++++++++++++++++

For typical onsite use at STScI, CRDS users can share a file cache which contains all rules and references.  The
location of the shared cache and default **CRDS_PATH** setting is essentially:

    % setenv CRDS_PATH  /grp/crds/cache

A remote or pipeline user defines a non-default CRDS cache by setting, e.g.:

	% setenv CRDS_PATH   $HOME/crds_cache

Note that the CRDS cache is often used to store reference files and when fully populated for a
particular mission can contain terabytes of files.

Server Selection (CRDS_SERVER_URL)
++++++++++++++++++++++++++++++++++

Since each project is supported by a different operational server, CRDS must determine which (if any)
server to use.

For **HST**::

% setenv CRDS_SERVER_URL https://hst-crds.stsci.edu

For **JWST**::

% setenv CRDS_SERVER_URL https://jwst-crds.stsci.edu

If CRDS cannot determine your project,  and you did not specify CRDS_SERVER_URL,  it will be defaulted to::

% setenv CRDS_SERVER_URL https://crds-serverless-mode.stsci.edu

In serverless mode it is not possible for CRDS to download new files or configuration settings,
so best reference recommendations may become stale.

Onsite CRDS Testing
+++++++++++++++++++

For reference type development,  updates are generally made and tested in the test pipelines at STScI.  For
coordinating with those tests,  **CRDS_PATH** and **CRDS_SERVER_URL** must be explicitly set to a test cache and server
similar to this::

    % setenv CRDS_PATH  ${HOME}/crds_cache_test
    % setenv CRDS_SERVER_URL https://hst-crds-test.stsci.edu

Alternative servers for JWST I&T testing are::

	% setenv CRDS_SERVER_URL https://jwst-crds-b5it.stcsi.edu     # build-5
	% setenv CRDS_SERVER_URL https://jwst-crds-b6it.stcsi.edu     # build-6
	% setenv CRDS_SERVER_URL https://jwst-crds-b7it.stcsi.edu     # build-7

After syncing this will provide access to CRDS test files and rules in a local cache::

    # Fetch all the test rules
    % python -m crds.sync --all

    # Fetch specifically listed test references
    % python -m crds.sync --files <test_references_only_the_test_server_has...>

Testing reference type changes (new keywords,  new values or value restrictions, etc) may also require access to
development versions of CRDS code.   In particular,  when adding parameters or changing legal parameter values,
the certify tool is modified as "code" on the servers first.   Hence distributed versions of CRDS will not reflect
ongoing type changes.   The test server Certify Files function should generally reflect the most up-to-date knowledge
CRDS has about ongoing type changes.  To see how new reference files stack up with changing CRDS code,  try submitting
the files to Certify Files on the test server or ask what the status is on crds_team@stsci.edu.

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

    % python -m crds.bestrefs --files dataset*.fits --sync-references=1  --update-bestrefs

For **JWST**,  CRDS is directly integrated with the calibration step code and will automatically download
rules and references as needed.   Downloads will only be an issue when you set CRDS_PATH and don't already
have the files you need in your cache.   By default CRDS modifies JWST datasets with new best references
which serve as a processing history in the dataset header.

Users of */grp/crds/cache* cannot update the readonly cache so they should not attempt to run crds.sync or
fetch references with crds.bestrefs.  */grp/crds/cache* should always be complete within a few hours of archiving
any new reference or rules delivery,  changing the operational context,  or marking files bad.


Additional HST Settings
+++++++++++++++++++++++

HST calibration steps access reference files indirectly through environment variables.  There are two forms
of CRDS cache reference file organization:  flat and with instrument subdirectories.   The original CRDS cache
format was flat,  and the shared group cache at /grp/crds/cache remains flat.

**Flat CRDS cache** For calibration software to use references in a CRDS cache with a flat reference file
organization, including the default shared group readonly cache at /grp/crds/cache,  set these environment
variables::

  setenv iref ${CRDS_PATH}/references/hst/
  setenv jref ${CRDS_PATH}/references/hst/
  setenv oref ${CRDS_PATH}/references/hst/
  setenv lref ${CRDS_PATH}/references/hst/
  setenv nref ${CRDS_PATH}/references/hst/
  setenv uref ${CRDS_PATH}/references/hst/
  setenv uref_linux $$uref

**By-Instrument CRDS cache** For calibration software to use references in a CRDS cache with a by-instrument
organization, the default for newly created caches in the future, set these environment variables::

  setenv iref ${CRDS_PATH}/references/hst/iref/
  setenv jref ${CRDS_PATH}/references/hst/jref/
  setenv oref ${CRDS_PATH}/references/hst/oref/
  setenv lref ${CRDS_PATH}/references/hst/lref/
  setenv nref ${CRDS_PATH}/references/hst/nref/
  setenv uref ${CRDS_PATH}/references/hst/uref/
  setenv uref_linux $uref

**Reorganizing CRDS References** The crds.sync tool can be used to reorganize the directory structure of a large
existing CRDS cache as follows to switch from flat to by-instrument::

  python -m crds.sync --organize=instrument

  # or to switch from by-instrument to flat

  python -m crds.sync --organize=flat

Another simpler approach is to delete and recreate your existing cache, more feasible for small personal caches
than for complete terabyte-scale caches.

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

