Environment Variables
=====================

Configuring CRDS for pipeline or offsite personal use is accomplished by setting
shell environment variables.

Basic Environment
-----------------

By default, onsite at STScI, CRDS runs from a global cache with no connection
to the CRDS Server and typically no user environment setup required to do basic
best references.

For more personalized configurations or one designed for offsite use,  the CRDS
environment needs to define a CRDS server `CRDS_SERVER_URL` and a CRDS file
cache directory `CRDS_PATH`.

File Cache Location `CRDS_PATH`
+++++++++++++++++++++++++++++++

CRDS stores reference files, rules files, and configuration information such as the
current default context in a cache.   The location of the CRDS cache is defined by
the `CRDS_PATH` environment setting.

Default On Site `CRDS_PATH`
...........................

By default, CRDS behaves as if you set your environment like this:

  .. code-block:: bash
    
      $ export CRDS_PATH=/grp/crds/cache


*/grp/crds/cache* is on the Central Store and should be accessible to all users.  It
is a readonly cache containing all rule and reference files associated with
all CRDS projects: HST, JWST and Roman.

While it is configuration free and self-maintaining, limitations of the default cache
include:

    1. A need for a direct connection to the STScI internal network
    2. Weak performance when accessed by VPN over the Internet
    3. Immutable files not well suited for experimentation

User Local CRDS_PATH
....................
To avoid Internet inefficiencies, individual users can construct demand-based CRDS caches
appropriate to their particular datasets. Personal CRDS caches also enable processing and
many basic functions with no network access to the CRDS server.

.. tip::
    
    If using different servers, a different local cache should be used for each one. 
    Using the same cache for different servers will lead to corrupted local cache.

A remote or pipeline user defines a non-default CRDS cache by setting, e.g.:

  .. code-block:: bash
    
      $ export CRDS_PATH=$HOME/crds_cache

Using a personal cache also requires defining the CRDS server.


Server Selection `CRDS_SERVER_URL`
++++++++++++++++++++++++++++++++++

Since each project (and test system) is supported by a different CRDS server,
a user must define any CRDS server they wish to use.

Default Server
..............
By default, the CRDS client bestrefs functionality can run without a server
provided they have access to an up-to-date CRDS cache.

By **default** CRDS behaves as if you set:

  .. code-block:: bash
    
      $ export CRDS_SERVER_URL=https://crds-serverless-mode.stsci.edu

Serverless mode limits CRDS to basic functions (`bestrefs`) but requires no server connection
once the supporting CRDS cache has been synced.


HST Ops Server
..............

A full featured CRDS configuration suitable supporting all server functions available for each mission
can be configured like this:

.. tabs::

   .. group-tab:: HST

       .. code-block:: bash

           $ export CRDS_SERVER_URL=https://hst-crds.stsci.edu

   .. group-tab:: JWST

       .. code-block:: bash

           $ export CRDS_SERVER_URL=https://jwst-crds.stsci.edu

   .. group-tab:: ROMAN

       .. code-block:: bash

           $ export CRDS_SERVER_URL=https://roman-crds.stsci.edu


If CRDS cannot determine your project, and you did not specify CRDS_SERVER_URL,
CRDS_SERVER_URL will be defaulted to:

  .. code-block:: bash
    
      $ export CRDS_SERVER_URL=https://crds-serverless-mode.stsci.edu


The serverless-mode URL directs CRDS to operate from the CRDS cache without contacting
the CRDS server for updates. This works well with the default cache at */grp/crds/cache*
since it is kept up to date by the CRDS server. It is not possible to do cache
updates while in serverless mode since no connection to the server is enabled.


Onsite CRDS Testing
-------------------

For reference type development, updates are generally made and tested in the
test pipelines at STScI.  For coordinating with those tests, **CRDS_PATH** and
**CRDS_SERVER_URL** must be explicitly set to a test cache and server similar
to this:

.. tabs::

   .. group-tab:: HST

       .. code-block:: bash

           $ export CRDS_PATH=${HOME}/crds_cache_test
           $ export CRDS_SERVER_URL=https://hst-crds-test.stsci.edu

   .. group-tab:: JWST

         .. code-block:: bash

             $ export CRDS_PATH=${HOME}/crds_cache_test
             $ export CRDS_SERVER_URL=https://jwst-crds-cit.stcsi.edu

   .. group-tab:: ROMAN

       .. code-block:: bash

           $ export CRDS_PATH=${HOME}/crds_cache_test
           $ export CRDS_SERVER_URL=https://roman-crds-int.stsci.edu


After syncing this will provide access to CRDS test files and rules in a local cache:

  .. code-block:: bash
    
      # Fetch all the test rules
      $ crds sync --all
      
      # Fetch specifically listed test references
      $ crds sync --files <test_references_only_the_test_server_has...>


Testing reference type changes (new keywords, new values or value restrictions,
etc) may also require access to development versions of CRDS code.  In
particular, when adding parameters or changing legal parameter values, the
certify tool is modified as "code" on the servers first.  Hence distributed
versions of CRDS will not reflect ongoing type changes.  The test server
Certify Files function should generally reflect the most up-to-date knowledge
CRDS has about ongoing type changes.  To see how new reference files stack up
with changing CRDS code, try submitting the files to Certify Files on the test
server or ask what the status is on redcat@stsci.edu.

**NOTE:** Without VPN or port forwarding, the test servers are not usable offsite.

Cache Layout Settings
---------------------

.. tabs::

   .. group-tab:: HST

        HST calibration software accesses reference files indirectly through environment variables.  There are two forms of CRDS cache reference file organization - flat or with instrument sub-directories.  The HST calibration software environment variable settings depend on the CRDS cache layout:

        .. tabs::

           .. tab:: Flat Cache Layout for */grp/crds/cache*
                
              The flat cache layout places all references in a single directory. The shared group cache at */grp/crds/cache* has a flat organization:
            
                .. code-block:: bash

                    $ export iref=${CRDS_PATH}/references/hst/
                    $ export jref=${CRDS_PATH}/references/hst/
                    $ export oref=${CRDS_PATH}/references/hst/
                    $ export lref=${CRDS_PATH}/references/hst/
                    $ export nref=${CRDS_PATH}/references/hst/
                    $ export uref=${CRDS_PATH}/references/hst/
                    $ export uref_linux=$uref

           .. tab:: By-Instrument Cache Layout

              The default cache setup for newly created caches for HST is organized by instrument. Unless you reorganize your cache using the crds.sync tool, these are the settings that are most likely to be appropriate for a personal HST cache. 
              
              For HST calibration software to use references in a CRDS cache with a by-instrument organization, set these environment variables:

                .. code-block:: bash

                    $ export iref=${CRDS_PATH}/references/hst/iref/
                    $ export jref=${CRDS_PATH}/references/hst/jref/
                    $ export oref=${CRDS_PATH}/references/hst/oref/
                    $ export lref=${CRDS_PATH}/references/hst/lref/
                    $ export nref=${CRDS_PATH}/references/hst/nref/
                    $ export uref=${CRDS_PATH}/references/hst/uref/
                    $ export uref_linux=$uref

   .. group-tab:: JWST

        JWST calibration code refers to explicit cache paths at runtime and does not require these additional settings. 

   .. group-tab:: ROMAN

        Roman calibration code refers to explicit cache paths at runtime and does not require these additional settings.


Reorganizing CRDS References
++++++++++++++++++++++++++++

The crds.sync tool can be used to reorganize the directory structure of an
existing CRDS cache. These organizations determine whether or not
reference files are partitioned into instrument-specific sub-directories.

To switch from flat to by-instrument:

  .. code-block:: bash
      
      $ crds sync --organize=instrument

To switch from by-instrument to flat:

  .. code-block:: bash
      
      $ crds sync --organize=flat


CRDS Context
------------

The CRDS context file defines a version of CRDS rules used to assign best references.

The CRDS context used to evaluate CRDS best references defaults to `{observatory}`-operational, e.g. `jwst-operational`.  This is an indirect name for the context in use or soon-to-be in use in the archive pipeline.

During development `-operational` corresponds to the latest context which is sufficiently mature for broad use and is automatic.

The context used can be overridden to some specific historical or experimental context by setting
the **CRDS_CONTEXT** environment variable:

.. tabs::

   .. group-tab:: HST

       .. code-block:: bash

           $ export CRDS_CONTEXT=hst_1008.pmap

   .. group-tab:: JWST

       .. code-block:: bash

           $ export CRDS_CONTEXT=jwst_0057.pmap

   .. group-tab:: ROMAN

       .. code-block:: bash

           $ export CRDS_CONTEXT=roman_0037.pmap


**CRDS_CONTEXT** does not override command line switches or parameters passed explicitly to the
crds.getreferences() API function.


AWS
---

The CRDS client can be configured to read files from Amazon's S3 service.  The STScI AWS environment
currently hosts files in the following buckets:

+-----------------+-----------------------+
| Environment     | S3 Bucket Name        |
+=================+=======================+
| HST OPS         | hst-crds-cache-ops    |
+-----------------+-----------------------+
| HST TEST        | hst-crds-cache-test   |
+-----------------+-----------------------+
| ROMAN TEST†     | roman-crds-cache-test |
+-----------------+-----------------------+

† As of this writing, Roman crds cache on AWS is not yet available.

The S3 buckets contain only recent contexts.  They also exclude mapping files, so the client must be
configured to load the context's rules from a pickle file.  Here is an example configuration for the
HST OPS bucket:

  .. code-block:: bash
      
      $ export CRDS_CONFIG_URI=s3://hst-crds-cache-ops/config/hst/
      $ export CRDS_DOWNLOAD_MODE=plugin
      $ export CRDS_DOWNLOAD_PLUGIN='crds_s3_get ${SOURCE_URL} ${OUTPUT_PATH} --file-size ${FILE_SIZE} --file-sha1sum ${FILE_SHA1SUM}'
      $ export CRDS_PATH=/path/to/local/cache
      $ export CRDS_PICKLE_URI=s3://hst-crds-cache-ops/pickles/hst/
      $ export CRDS_REFERENCE_URI=s3://hst-crds-cache-ops/references/hst/
      $ export CRDS_SERVER_URL=https://hst-crds-serverless.stsci.edu
      $ export CRDS_USE_PICKLED_CONTEXTS=1

**NOTE** Your compute environment must be configured with AWS credentials that have been granted access
to the bucket.

Advanced Environment
--------------------

A number of things in CRDS are configurable with environment variables,  most important of which is the
location and structure of the file cache.

CRDS Cache Locking
++++++++++++++++++

CRDS cache locking has been added to support JWST association calibration multi-processing
for users who set up personal demand-based CRDS Caches.  Cache locking prevents simultaneous
transparent CRDS Cache updates from multiple JWST calibration processes.

Single Shell Locking
....................
By default,  CRDS uses Python's built-in multiprocessing locks which are robust and suitable for
running multiprocesses within a single shell or terminal window:

  .. code-block:: bash
    
      $ crds list --status
      CRDS Version = '7.2.0, 7.2.0, 139bbcb'
      ...
      Cache Locking = 'enabled, multiprocessing'
      ...
      Readonly Cache = False

However,  this default CRDS cache locking is not suitable for running calibrations in multiple
terminal windows or for pipeline use.

File Based Locking
..................

Since Python's default multiprocessing locks cannot support multiple process trees or terminal windows,
CRDS also supports file based locking by setting appropriate configuration variables:

  .. code-block:: bash
    
      $ export CRDS_LOCKING_MODE=filelock
      $ crds list --status
      CRDS Version = '7.2.0, 7.2.0, 139bbcb'
      ...
      Cache Locking = 'enabled, filelock'
      ...
      Readonly Cache = False

File based locking is not used by default for several reasons::

    1. They introduce a dependency on a 3rd party package.
    2. File locks created on network or other virtualized file systems may be unreliable.
    3. File lock behavior is OS dependent.

Restrictions on Locking
.......................

There are multiple conditions in CRDS that determine when locking is really used:

    1. `CRDS_READONLY_CACHE` must be undefined or 0
    2. The CRDS cache must be writable as determined by file system permissions
    3. The `CRDS_LOCK_PATH` directory (nominally `/tmp`) should already exist
    4. For file based locking,  a lock must be successfully created
    5. `CRDS_USE_LOCKING` must be undefined or 1
    6. For file based locking, the lockfile or filelock Python package must be installed

The read-only nature of::

  */grp/crds/cache*

prevents the use of locking for typical onsite users.  None should be required.

It should be noted that the existence of any lock file directory is itself a
concurrency issue, so it must be created or otherwise available before cache
synchronization takes place.

The CRDS command:

  .. code-block:: bash
    
      $ crds sync --clear-locks

can be used to remove orphan locks (due to some unexpected failure) that are blocking processing.

Locking requires installation of the *lockfile* package and `CRDS-7.1.4` or later.

Multi-Project Caches
++++++++++++++++++++

**CRDS_PATH** defines a cache structure for multiple projects. Each major branch of a multi-project cache
contains project specific sub-directories::

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
tree specified by `CRDS_PATH`. The remaining directories can be overriden as well or derived
from CRDS_PATH.

**CRDS_MAPPATH** can be used to override `CRDS_PATH` and define where
only mapping files are stored. CRDS_MAPPATH defaults to `${CRDS_PATH}/mappings`
which contains multiple observatory-specific subdirectories.

**CRDS_REFPATH** can be used to override `CRDS_PATH` and define where
only reference files are stored.  `CRDS_REFPATH` defaults to `${CRDS_PATH}/references`
which contains multiple observatory specific subdirectoriers.

**CRDS_CFGPATH** can be used to override `CRDS_PATH` and define where
only configuration information is cached. `CRDS_CFGPATH` defaults to `${CRDS_PATH}/config`
which can contain multiple observatory-spefific subdirectories.

Specifying `CRDS_MAPPATH=/somewhere` when `CRDS_OBSERVATORY=hst`  means that
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
mapping files are stored. `CRDS_MAPPATH_SINGLE` defaults to `${CRDS_PATH}/mappings`
but is presumed to support only one observatory.

**CRDS_REFPATH_SINGLE** can be used to override CRDS_PATH and define where
only reference files are stored.  `CRDS_REFPATH_SINGLE` defaults to `${CRDS_PATH}/references`
but is presumed to support only one observatory.

**CRDS_CFGPATH_SINGLE** can be used to override CRDS_PATH and define where
only server configuration information is cached. `CRDS_CFGPATH_SINGLE` defaults to
`${CRDS_PATH}/config` but is presumed to support only one observatory.

Specifying `CRDS_MAPPATH_SINGLE=/somewhere` when `CRDS_OBSERVATORY=hst` means that
mapping files will be located in /somewhere,  not in /somewhere/hst.

Miscellaneous Variables
+++++++++++++++++++++++

**CRDS_VERBOSITY** enables output of CRDS debug messages.   Set to an
integer,  nominally 50. Higher values output more information, lower
values less information. CRDS also has command line switches
`--verbose (level=50)` and -`-verbosity=<level>`.   Verbosity level
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
(when the server cannot be reached) (auto). The default is `auto`.

**CRDS_CLIENT_RETRY_COUNT** number of times CRDS will attempt a network
transaction with the CRDS server.  Defaults to 1 meaning 1 try with no retries.

**CRDS_CLIENT_RETRY_DELAY_SECONDS** number of seconds CRDS waits after a failed
network transaction before trying again.  Defaults to 0 seconds,  meaning
proceed immediately after fail.

**CRDS_CLIENT_TIMEOUT_SECONDS** number of seconds CRDS will wait for a network
transaction to complete.

**CRDS_USE_LOCKING** boolean enabling/disabling CRDS cache locking,  currently
only used for JWST and defaulting to enabled.   File locking is currently limited
to JWST calibrations so HST sync and bestrefs tools must be run in single
processes or with `CRDS_READONLY_CACHE=1`.

**CRDS_LOCKING_MODE**  chooses between multiprocessing, filelock, or lockfile
based locks.  multiprocessing is the default.  To support multiple
terminal windows or pipeline processing,  file based locking must be used
with filelock recommended and known problems having been observed with the
lockfile package.
