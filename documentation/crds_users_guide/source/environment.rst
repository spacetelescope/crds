Environment Variables
=====================

Configuring CRDS for pipeline or offsite personal use is accomplished by setting
shell environment variables.

*Looking for AWS configuration? See the* :ref:`aws` *section of this guide.*

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

The CRDS context used to evaluate CRDS best references defaults to `{observatory}`-latest, e.g. `jwst-latest`.  This is an indirect name for the context in use or soon-to-be in use in the archive pipeline.

During development `-latest` corresponds to the latest context which is sufficiently mature for broad use and is automatic.

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


Advanced Environment
--------------------

A number of things in CRDS are configurable with environment variables,  most important of which is the
location and structure of the file cache.


Cache Locking
.............

CRDS cache locking supports both file-based locks and in-memory multiprocessing locks. The `crds_lock()` function is a smart context manager that automatically detects if multiprocessing architecture is active (parent script initialized the multiprocessing manager), or if using a networked path (which defaults to file-based locking). This ensures proper locking behavior across different environments.

There are two distinct locking mechanisms: multiprocessing and file-based locks.

File-based Locking
..................

Synchronizes disks/files for multi-application scaling across multiple processing/terminals/machines, including shared networks. This is the default locking mechanism when multiprocessing is not enabled or when the target path is on a networked filesystem. File locks are implemented using the `filelock` library, which creates a `.lock` file alongside the target file to indicate that it is currently locked. The lock file is automatically cleaned up when the lock is released, but orphaned lock files may remain if a process crashes or is terminated unexpectedly. The `clear_cache_locks()` function can be used to scan for and remove any stale lock files in the cache directory. The CRDS Sync script accepts an optional `--clear-locks` argument to automatically clear any stale locks before proceeding with synchronization.

NOTE: Cache locking is enabled automatically within calls to the CRDS Sync script and heavy_client.getreferences(). Therefore it is not necessary to explicitly enable locking or use the lock context manager when calling these functions.

To ensure locking occurs, you can set verbose logging to see each file lock acquisition and release.

  .. code-block:: python

    from crds.core import log
    from crds.sync import SyncScript

    log.set_verbose(55)
    SyncScript("crds.sync --contexts hst_0006.pmap")()


The CRDS command:

  .. code-block:: bash
    
      $ crds sync --clear-locks

can be used to remove orphan locks (due to some unexpected failure) that are blocking processing.


Multiprocessing Locking
.......................

For multi-core scaling on a single machine/terminal. Synchronizes cores/CPUs. Multiprocessing locks do not work across multiple terminals or machines, and are not safe for networked paths (NFS, SMB, etc.). The multiprocessing locks are managed by a background Manager process that is lazily initialized when needed. This allows for safe sharing of locks across different processes spawned by the same parent script. NOTE: The parent script must call `initialize_multiprocessing_mode()` to set up the Manager and shared locks before any child processes are spawned. The locks are stored in a shared dictionary that is accessible to all child processes.


Examples:

**Locking with multiprocessing.Pool:**

  .. code-block:: python

    import multiprocessing
    from crds.core.cache_locker import crds_lock
    from crds.core.heavy_client import getreferences

    def getrefs_pool_worker(task_args):
        """
        Wrapper function run by Pool workers.
        Acquires the lock dynamically before executing getreferences() 
        to handle the look-lock-download pattern safely.
        """
        worker_id, header, reftypes, observatory, target_file_key = task_args
        try:
            with crds_lock(target_file_key, timeout=30.0):
                start_time = time.time()
                refs = getreferences(
                    parameters=header, 
                    reftypes=reftypes, 
                    observatory=observatory
                )
                end_time = time.time()
                
                return {
                    "worker_id": worker_id,
                    "start": start_time,
                    "end": end_time,
                    "refs_returned": refs,
                    "success": True
                }
        except Exception as e:
            return {"worker_id": worker_id, "success": False, "error": str(e)}


    def test_parallel_getreferences_pool():
        """
        Integration test validating that getreferences acts sequentially
        when mapped concurrently across multiple workers.
        """
        # ACTIVATE MP MULTIPLEXER IN PARENT
        from crds.core.cache_locker import initialize_multiprocessing_mode
        initialize_multiprocessing_mode()
        header = {
            'roman.meta.instrument.name': 'wfi',
            'ROMAN.META.EXPOSURE.START_TIME': '2026-05-29',
            'ROMAN.META.INSTRUMENT.OPTICAL_ELEMENT': 'f184',
        }
        reftypes = ['epsf']
        observatory = "roman"
        target_lock_key = "roman_wfi_epsf" 
        num_workers = 3
        task_arguments = [
            (i, header, reftypes, observatory, target_lock_key) 
            for i in range(num_workers)
        ]

        import crds.core.cache_locker as cache_locker
        shared_dict = cache_locker._MULTIPROCESSING_LOCKS
        manager_instance = cache_locker._MANAGER

        ctx = multiprocessing.get_context()
        
        # Initialize the worker pool, pushing synchronized proxy state down
        print(f"\nLaunching Pool to test parallel getreferences for {target_lock_key}...")
        with ctx.Pool(
            processes=num_workers,
            initializer=initialize_multiprocessing_mode,
            initargs=(shared_dict, manager_instance)
        ) as pool:
            results = pool.map(getrefs_pool_worker, task_arguments)

        # Optionally verify:
        assert len(results) == num_workers
        results.sort(key=lambda x: x["start"])
        print("\n--- Parallel getreferences Timeline ---")
        for r in results:
            assert r["success"], f"Worker {r['worker_id']} collapsed with error: {r.get('error')}"
            print(f"Worker {r['worker_id']}: Entered at {r['start']:.2f}, Left at {r['end']:.2f}")
            print(f"  -> Returned Paths: {r['refs_returned']}")
        for i in range(1, len(results)):
            previous_worker_end = results[i-1]["end"]
            current_worker_start = results[i]["start"]
            assert current_worker_start >= previous_worker_end, (
                f"Lock Failure! Worker {results[i]['worker_id']} overlap detected. "
                f"Entered at {current_worker_start:.2f} before previous left at {previous_worker_end:.2f}."
            )


**Locking with Multiprocessing.Process:**

    .. code-block:: python

        import multiprocessing
        from crds.core.cache_locker import crds_lock
        from crds.core.heavy_client import getreferences

        def getrefs_worker_task(worker_id: int, target_file: str, output_queue: multiprocessing.Queue):
            """Target function executed by independent worker processes under pytest."""
            header = {
                'roman.meta.instrument.name': 'wfi',
                'ROMAN.META.EXPOSURE.START_TIME': '2026-05-29',
                'ROMAN.META.INSTRUMENT.OPTICAL_ELEMENT': 'f184',
            }
            try:
                with crds_lock(target_file, timeout=30.0):
                    start_time = time.time()
                    refs = getreferences(header, reftypes=['epsf'], observatory="roman")
                    end_time = time.time()
                    output_queue.put({
                        "worker_id": worker_id,
                        "start": start_time,
                        "end": end_time,
                        "refs": refs,
                        "success": True
                    })
            except Exception as e:
                output_queue.put({"worker_id": worker_id, "success": False, "error": str(e)})

        def test_getrefs_mp_locking():
            from crds.core.cache_locker import initialize_multiprocessing_mode
            initialize_multiprocessing_mode()
            local_target = str(Path("./test_local_cache_file.tmp").resolve())
            result_queue = multiprocessing.Queue()
            workers = []
            num_workers = 3

            print("Spawning child processes to test multiprocessing locks...")

            # Kick off multiple workers simultaneously
            for i in range(num_workers):
                p = multiprocessing.Process(
                    target=worker_task,
                    args=(i, local_target, result_queue)
                )
                workers.append(p)
                p.start()
            # Wait for all child processes to finish
            for p in workers:
                p.join()

            # OPTIONAL: Gather and analyze results
            results = []
            while not result_queue.empty():
                results.append(result_queue.get())

            # Ensure cleanups
            if Path(local_target).exists():
                Path(local_target).unlink()

            # Assertions and Verifications
            assert len(results) == num_workers, f"Expected {num_workers} results, got {len(results)}"

            # Sort results by their start times to analyze sequence
            results.sort(key=lambda x: x["start"])

            print("\n--- Execution Timeline ---")
            for r in results:
                assert r["success"], f"Worker {r['worker_id']} failed with error: {r.get('error')}"
                print(f"Worker {r['worker_id']}: Entered at {r['start']:.2f}, Left at {r['end']:.2f}")
            # Ensure worker N did not enter the lock until worker N-1 completely left.
            for i in range(1, len(results)):
                previous_worker_end = results[i-1]["end"]
                current_worker_start = results[i]["start"]

                assert current_worker_start >= previous_worker_end, (
                    f"Lock Failure! Worker {results[i]['worker_id']} entered at {current_worker_start:.2f} "
                    f"before the previous worker left at {previous_worker_end:.2f}."
                )


Restrictions on Locking
.......................

Cache locking is only enabled for writable caches:

    1. `CRDS_READONLY_CACHE` must be undefined or 0
    2. The CRDS cache must be writable as determined by file system permissions


The read-only nature of::

  */grp/crds/cache*

prevents the use of locking for typical onsite users.  None should be required.



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

- *config* contains system configuration information like latest context and bad files

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
