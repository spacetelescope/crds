Best References Basics
======================

The primary function of CRDS is to assign the names of calibration reference files required to calibrate datasets to their metadata headers.

Operating on site using the CRDS cache at */grp/crds/cache* by default,  CRDS "just works" for bestrefs with no extra configuration required.


.. tabs::

   .. group-tab:: HST

      CRDS provides the *crds bestrefs* program for updating dataset headers for HST with the current best references. Running bestrefs for HST is accomplished via:

        .. code-block:: bash

            $ crds bestrefs --files dataset*.fits --update-bestrefs

      This command updates the FITS headers of the files specified by `dataset*.fits` with the names of the latest best reference files known to */grp/crds/cache*.

   .. group-tab:: JWST

      For JWST calibrations, CRDS is fully integrated with the CAL code and operates transparently as a consequence of running pipelines:

        .. code-block:: bash

            $ strun calwebb_sloper.cfg dataset.fits

      The above command will transparently update the reference files specified in the metadata of `dataset.fits`.

   .. group-tab:: ROMAN

      For Roman calibrations, CRDS is fully integrated with the CAL code and operates transparently as a consequence of running pipelines:

        .. code-block:: bash

            $ strun roman_elp dataset.asdf

      The above command will transparently update the reference files specified in the metadata of `dataset.asdf`.


Default Onsite Use
------------------

The CRDS default configuration permits CRDS to operate onsite with no explicit environment settings.

By default, CRDS operates using */grp/crds/cache* with no connection to any CRDS
server.  

Files and settings in */grp/crds/cache* define the references that CRDS will
assign to a given dataset.

Offsite and Pipeline Use
------------------------

CRDS can be configured to operate from private/local CRDS caches.  See the instructions below for setting `CRDS_PATH` and `CRDS_SERVER_URL`.

A private cache reduces the level of network i/o required for offsite use as
well as eliminating constant dependence on CRDS web servers required to run a
pipeline.  A private cache can also contain writable files suitable for
experimentation.

    - Onsite pipelines use private caches to reduce file system contention.

    - Offsite pipelines use private caches to achieve more independence from STScI.

Setup for Offsite Use
---------------------

CRDS has been designed to (optionally) automatically fetch and cache references
you need to process your datasets to a personal CRDS cache.  You can create a
small personal cache of rules and references supporting only the datasets you
care about:


.. tabs::

   .. group-tab:: HST

      To fetch the references required to process some FITS datasets:

        .. code-block:: bash

            $ export CRDS_SERVER_URL=https://hst-crds.stsci.edu   # or similar
            $ export CRDS_PATH=${HOME}/crds_cache
            $ crds bestrefs --files dataset*.fits --sync-references=1  --update-bestrefs

   .. group-tab:: JWST

      CRDS is directly integrated with the calibration step code and will automatically download rules and references.  The only extra setup needed is to define `CRDS_PATH` and `CRDS_SERVER_URL` appropriately prior to *strun*:

        .. code-block:: bash

            $ export CRDS_SERVER_URL=https://jwst-crds.stsci.edu   # or similar
            $ export CRDS_PATH=${HOME}/crds_cache
            $ strun calwebb_sloper.cfg dataset.fits

   .. group-tab:: ROMAN

      CRDS is directly integrated with the calibration step code and will automatically download rules and references.  The only extra setup needed is to define `CRDS_PATH` and `CRDS_SERVER_URL` appropriately prior to *strun*:

        .. code-block:: bash

            $ export CRDS_SERVER_URL=https://roman-crds.stsci.edu   # or similar
            $ export CRDS_PATH=${HOME}/crds_cache
            $ strun roman_elp dataset.asdf


Overriding the Default Context
------------------------------

It's possible to use past or future/experimental CRDS contexts rather than the pipeline's default operational context as follows:

.. tabs::

   .. group-tab:: HST

      To fetch the references required to process some FITS datasets:

        .. code-block:: bash

            $ crds bestrefs --files dataset*.fits --update-bestrefs --new-context hst_0001.pmap

   .. group-tab:: JWST

      By setting an environment variable:

        .. code-block:: bash

            $ export CRDS_CONTEXT=jwst_0001.pmap
            $ strun calwebb_sloper.cfg dataset.fits

   .. group-tab:: ROMAN

      By setting an environment variable:

        .. code-block:: bash

            $ export CRDS_CONTEXT=roman_0001.pmap
            $ strun roman_elp dataset.asdf


Bestrefs by Dataset ID
----------------------

Ensure the appropriate CRDS environment variables are set:

  .. code-block: bash

      $ export CRDS_SERVER_URL=https://roman-crds-test.stsci.edu
      $ export CRDS_PATH=path/to/crds_cache 


.. tabs::

   .. group-tab:: python

      Let's say you want to download best references for a dataset with ID: 'R0000101001001001001_01101_0001.WFI16' from context `roman_0042.pmap`.

        .. code-block:: python

            import crds
            from crds.client import api
            context = "roman_0042.pmap"
            instrument = "wfi"
            datasetid = 'R0000101001001001001_01101_0001.WFI16'
            refs = api.get_best_references_by_ids(context, [datasetid])
            
      The results are now stored in `refs`

        .. code-block:: python

            print(refs)
            {
               'R0000101001001001001_01101_0001.WFI16:R0000101001001001001_01101_0001.WFI16': [
                  True,  {
                     'area': 'NOT FOUND No match found.',
                     'dark': 'roman_wfi_dark_0469.asdf',   
                     'distortion': 'roman_wfi_distortion_0016.asdf',   
                     'flat': 'roman_wfi_flat_0231.asdf',   
                     'gain': 'roman_wfi_gain_0142.asdf',   
                     'inverselinearity': 'NOT FOUND No match found.',   
                     'ipc': 'NOT FOUND No match found.',   
                     'linearity': 'roman_wfi_linearity_0195.asdf',   
                     'mask': 'roman_wfi_mask_0066.asdf',   
                     'photom': 'roman_wfi_photom_0054.asdf',   
                     'readnoise': 'roman_wfi_readnoise_0381.asdf',   
                     'refpix': 'NOT FOUND No match found.',   
                     'saturation': 'roman_wfi_saturation_0191.asdf'
                  }
               ]
            } 

      Store matches in a list and then download:

        .. code-block:: python

            reflist = [v for k,v in refs[datasetid][1].items() if v.split('_')[0] == "roman"]  

            # download them to local crds cache:
            api.dump_references(context, reflist) 

            # or if you only want a specific reference:
            api.dump_references(context, ['roman_wfi_saturation_0191.asdf'])

            CRDS - INFO -  Fetching  /home/developer/crds-cache/references/roman/roman_wfi_saturation_0191.asdf  134.2 M bytes  (1 / 1 files) (0 / 134.2 M bytes)


            # You can also specify which reftypes you want
            refs = api.get_best_references_by_ids(
               context, [dataset_id], reftypes=["dark","distortion","gain"]
            )
      
      View the header information first with `include_headers=True`

        .. code-block:: python

            refs = api.get_best_references_by_ids(
               context,[datasetid], reftypes=["dark"],include_headers=True
            )

            print(refs)
            
            {'headers': {
               'R0000101001001001001_01101_0001.WFI16': {
                  'ROMAN.META.INSTRUMENT.DETECTOR': 'WFI16',   
                  'ROMAN.META.EXPOSURE.MA_TABLE_NUMBER': '1',   
                  'ROMAN.META.EXPOSURE.TYPE': 'WFI_IMAGE',  
                  'productLevel': '2',   
                  'ROMAN.META.INSTRUMENT.NAME': 'WFI',   
                  'ROMAN.META.EXPOSURE.START_TIME': '2021-01-01T00:00:00.0',  
                  'ROMAN.META.INSTRUMENT.OPTICAL_ELEMENT': 'F158',   
                  'PARAMS_SOURCE': 'http://tlrdmsarc1.stsci.edu:8888/crds',   
                  'PARAMS_DATE': '2023-06-07T10:45:16.150628',   
                  'PARAMS_CTX': 'roman_0042.pmap'
               }
            }, 'R0000101001001001001_01101_0001.WFI16': [
               True,  {
                  'dark': 'roman_wfi_dark_0469.asdf'
               }
            ]}


   .. group-tab:: Command-Line

      You can specify files to download using crds.sync on the command line: 

        .. code-block:: bash

            $ crds sync --files 'roman_wfi_saturation_0191.asdf'
