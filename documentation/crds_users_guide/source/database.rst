CRDS Database Access
====================

JSON RPC Access
---------------

CRDS supports JSON RPC access to the CRDS catalog via the crds.client API.

Metadata for a single file
..........................

The JSON RPC call `get_file_info()` will return the available info for a single reference
or mapping file from the specified observatory:

  .. code-block:: python

      def get_file_info(observatory, filename):
          """Return a dictionary of CRDS information about `filename`."""


.. tabs::

   .. group-tab:: HST

      Single reference file:

        .. code-block:: python

            >>> from crds.client import api
            >>> api.get_file_info("hst", "lcb12060j_drk.fits")
            {'activation_date': '2021-08-06 10:26:52',
             'aperture': 'wfc2-orampq',
             'blacklisted': 'false',
             'change_level': 'severe',
             'delivery_date': '2021-08-05 14:40:44',
             'derived_from': 'none',
             'description': 'updates to the variance and read noise calculations for subarrays ...',
             'filekind': 'biasfile',
             'instrument': 'acs',
             'name': '5851840kj_bia.fits',
             'observatory': 'hst',
             'pedigree': 'inflight 14/11/2015 14/11/2015',
             'reference_file_type': 'none',
             'rejected': 'false',
             'sha1sum': 'b684c9123da94ff5b9efb72c15316af050ecca62',
             'size': '42390720',
             'state': 'operational',
             'type': 'reference',
             'uploaded_as': '20151022_g2.0_wfc2-orampq_d_bia.fits',
             'useafter_date': '2015-10-22 23:30:54'}

   .. group-tab:: JWST

      Single reference file:

        .. code-block:: python

            >>> from crds.client import api
            >>> api.get_file_info("jwst", "jwst_miri_dark_0072.fits")
            {'activation_date': '2022-03-21 10:23:31',
             'aperture': 'none',
             'blacklisted': 'false',
             'change_level': 'severe',
             'comment': 'dark correction',
             'delivery_date': '2022-03-18 10:11:02',
             'derived_from': 'none',
             'description': 'a set of dummy darks with all zeros for all miri modes ...',
             'filekind': 'dark',
             'instrument': 'miri',
             'name': 'jwst_miri_dark_0072.fits',
             'observatory': 'jwst',
             'pedigree': 'dummy',
             'reference_file_type': 'dark',
             'rejected': 'false',
             'replaced_by_filename': 'jwst_miri_dark_0083.fits',
             'sha1sum': '34c432f1204618f46ed6591e0cb0f959981ba702',
             'size': '342420480',
             'state': 'archived',
             'type': 'reference',
             'uploaded_as': 'miri_ifulong_fastr1_full_dark_09.00.02.fits',
             'useafter_date': '2022-04-01 00:00:00'}

   .. group-tab:: ROMAN

      Single reference file:

        .. code-block:: python

            >>> from crds.client import api
            >>> api.get_file_info("roman", "roman_wfi_dark_0227.asdf")
            {'activation_date': '2022-05-10 12:00:28.216225',
             'aperture': 'none',
             'blacklisted': 'false',
             'change_level': 'severe',
             'delivery_date': '2022-05-10 09:20:43.126986',
             'derived_from': 'none',
             'description': 'updated wfi dark reference files that have new meta data ...',
             'filekind': 'dark',
             'history': 'none',
             'instrument': 'wfi',
             'name': 'roman_wfi_dark_0227.asdf',
             'observatory': 'roman',
             'pedigree': 'none',
             'reference_file_type': 'none',
             'rejected': 'false',
             'sha1sum': 'adc1e6cdf2491a393e439b8f820f29056b41e2ff',
             'size': '872417289',
             'state': 'operational',
             'type': 'reference',
             'uploaded_as': 'roman_dark_wfi01_wfi_image_highlatitudespecsurvey_vold.asdf',
             'useafter_date': '1900-01-01 00:00:00'}


Metadata for several / all files
................................

The JSON RPC call `get_file_info_map()` will return the info for multiple (or all) files
and the specified (or all) fields as a dictionary of dictionaries mapping filename onto info:

  .. code-block:: python

      def get_file_info_map(observatory, files=None, fields=None):
        """Return the info { filename : { info } } on `files` of `observatory`.
        `fields` can be used to limit info returned to specified keys.
        """

If `files` is specified as *None*,  info on all files is returned.

If `fields` are specified as *None*,  info on all available fields is returned.

.. tabs::

   .. group-tab:: HST

       .. code-block:: bash

           $ export CRDS_SERVER_URL=https://hst-crds.stsci.edu

       .. code-block:: python

           >>> from crds.client import api
           >>> api.get_file_info_map("hst", files=["lcb12060j_drk.fits", "n3o1022fj_drk.fits"], fields=["state","size","sha1sum"])
           {'lcb12060j_drk.fits': {
               'sha1sum': '56cfd1107bda5d82cb49a301a50edb45cb64ded6',
               'size': '10549440',
               'state': 'operational'
               },
            'n3o1022fj_drk.fits': {
                'sha1sum': 'cecf11300015df8f39913b638138d8c67de77a02',
                'size': '10526400',
                'state': 'operational'
                }
           }

   .. group-tab:: JWST

       .. code-block:: bash

           $ export CRDS_SERVER_URL=https://jwst-crds.stsci.edu

       .. code-block:: python

           >>> from crds.client import api
           >>> api.get_file_info_map("jwst", files=["jwst_miri_dark_0072.fits", "jwst_miri_dark_0073.fits"], fields=["state","size","sha1sum"])
           {'jwst_miri_dark_0072.fits': {
               'sha1sum': '34c432f1204618f46ed6591e0cb0f959981ba702',
               'size': '10549440',
               'state': 'operational'
               },
            'jwst_miri_dark_0073.fits': {
                'sha1sum': 'ed6591e0cb0f959981ba70234c432f1204618f46',
                'size': '10526400',
                'state': 'operational'
                }
           }

   .. group-tab:: ROMAN

       .. code-block:: bash

           $ export CRDS_SERVER_URL=https://roman-crds.stsci.edu

       .. code-block:: python

           >>> from crds.client import api
           >>> api.get_file_info_map("roman", files=["roman_wfi_dark_0295.asdf","roman_wfi_flat_0227.asdf"], fields=["state","size","sha1sum"])
           {'roman_wfi_dark_0295.asdf': {
               'sha1sum': '2432e01bd0058a485d83e35e74d2701611a191f0',
               'size': '1006635000',
               'state': 'operational'
               },
            'roman_wfi_flat_0227.asdf': {
                'sha1sum': '527f54ed8b8e53ff2e92425d506a23233deae044',
                'size': '200542817',
                'state': 'operational'
                }
            }


Download CRDS catalog for SQLite queries
----------------------------------------

The CRDS catalog stores metadata about references not captured in the .rmap files. It also contains
the history of CRDS context use, the effective dates at which particular contexts where operational in
the pipeline.

You can download a SQLite-3 snapshot of the CRDS catalog like this:

.. tabs::

    .. tab:: bash

        .. code-block:: bash

            $ export CRDS_SERVER_URL=https://hst-crds.stsci.edu
            $ export CRDS_PATH=/home/homer/crds_cache
            $ export crds sync --fetch-sqlite-db
            CRDS - INFO - SQLite database file downloaded to: /home/homer/crds_cache/config/hst/crds_db.sqlite3

    .. tab:: csh

        .. code-block:: csh

            % setenv CRDS_SERVER_URL https://hst-crds.stsci.edu
            % setenv CRDS_PATH /home/homer/crds_cache
            % crds sync --fetch-sqlite-db 
            CRDS - INFO - SQLite database file downloaded to: /home/homer/crds_cache/config/hst/crds_db.sqlite3
    
will snapshot the current CRDS catalog on the CRDS server and download it to your local CRDS cache as a 
SQLite3 database file.  The SQLite database can typically be accessed like this::
    
    $ sqlite3 /home/homer/crds_cache_dev/config/hst/crds_db.sqlite3
    
    sqlite> .tables
    crds_hst_catalog       crds_hst_context_history
    
    sqlite> .mode tabs
    sqlite> .headers on
    sqlite> select * from crds_hst_context_history where state="operational" limit 1;
    id    name    start_date        context     state          description
    2        2013-07-02 15:44:53    hst.pmap    operational    set by system
    \.\.\.
    
The CRDS catalog contains the following meta-data: 

====================        ===========        =============================================================================
Catalog Fields              type               description
====================        ===========        =============================================================================
name                        str                CRDS filename
uploaded_as                 str                Name of file at time of upload / generation
state                       str                uploaded, delivered, submitted, archiving, archived, archiving-failed, bad
blacklisted                 bool/int           True/1 == this mapping,  and all mappings referring to it, are invalid.
rejected                    bool/int           True/1 == this file is considered scientifically invalid
replaced_by_filename        str                Succeeding reference file in chain of contexts.  Weakly defined.
instrument                  str                instrument name file applies to
filekind                    str                reference type. For HST,  also keyword name for dataset headers
type                        str                reference or mapping
description                 str                description given at time of delivery
comment                     str                COMMENT from reference file
aperture                    str                APERTURE from reference file
derived_from                str                Name of mapping this one was derived from
sha1sum                     str                sha1sum of file to verify file integrity
size                        int                length of file in bytes
creator_name                str                author of reference or mapping file
deliverer_user              str                person who submitted the reference or mapping to CRDS
deliverer_email             str                e-mail of person who submitted reference
====================        ===========        =============================================================================
       
*NOTE:* Reference file assignment criteria are encoded in the CRDS rules / mappings and displayed as tables on 
the web site context display.   See also crds.matches for information on displaying matching criteria based on rmaps 
at the command line.
    
