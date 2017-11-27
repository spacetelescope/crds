CRDS Database Access
====================

JSON RPC Access
---------------

CRDS supports JSON RPC access to the CRDS catalog via the crds.client API.

Metadata for a single file
..........................

The JSON RPC call get_file_info() will return the avalailble info for a single reference
or mapping file from the specified observatory::

   def get_file_info(observatory, filename):
        """Return a dictionary of CRDS information about `filename`."""
    
    >>> from crds.client import api

    >>> api.get_file_info("hst", file="lcb12060j_drk.fits")
    {'activation_date': '2001-12-14 20:47:00',
     'blacklisted': 'false',
     'change_level': 'severe',
     'delivery_date': '2013-07-10 11:26:23',
     'derived_from': 'none',
     'filekind': 'darkfile',
     'instrument': 'acs',
     'name': 'lcb12060j_drk.fits',
     'observatory': 'hst',
     'pedigree': 'ground',
     'rejected': 'false',
     'sha1sum': '56cfd1107bda5d82cb49a301a50edb45cb64ded6',
     'size': '10549440',
     'state': 'operational',
     'type': 'reference',
     'useafter_date': '1992-01-01 00:00:00'}
    
Metadata for several / all files
................................

The JSON RPC call get_file_info_map() will return the info for multiple (or all) files
and the specified (or all) fields as a dictionary of dictionaries mapping filename onto info::

    def get_file_info_map(observatory, files=None, fields=None):
        """Return the info { filename : { info } } on `files` of `observatory`.
        `fields` can be used to limit info returned to specified keys.
        """
        
    % setenv CRDS_SERVER_URL https://hst-crds.stsci.edu
        
    >>> from crds.client import api

    >>> api.get_file_info_map("hst", ["lcb12060j_drk.fits", "n3o1022fj_drk.fits"], fields=["state","size","sha1sum"])
    {'lcb12060j_drk.fits': {'sha1sum': '56cfd1107bda5d82cb49a301a50edb45cb64ded6',
      'size': '10549440',
      'state': 'operational'},
     'n3o1022fj_drk.fits': {'sha1sum': 'cecf11300015df8f39913b638138d8c67de77a02',
      'size': '10526400',
      'state': 'operational'}}

If files is specified as *None*,  info on all files is returned.

If fields are specified as *None*,  info on all available fields is returned.


Download CRDS catalog for SQLite queries
----------------------------------------

The CRDS catalog stores metadata about references not captured in the .rmap files.   It also contains
the history of CRDS context use,  the effective dates at which particular contexts where operational in
the pipeline.

You can download a SQLite-3 snapshot of the CRDS catalog like this::
    
    % setenv CRDS_SERVER_URL https://hst-crds.stsci.edu
    % setenv CRDS_PATH /home/homer/crds_cache
    % crds sync --fetch-sqlite-db 
    CRDS - INFO - SQLite database file downloaded to: /home/homer/crds_cache/config/hst/crds_db.sqlite3
    
will snapshot the current CRDS catalog on the CRDS server and download it to your local CRDS cache as a 
SQLite3 database file.  The SQLite database can typically be accessed like this::
    
    % sqlite3 /home/homer/crds_cache_dev/config/hst/crds_db.sqlite3
    
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
    
