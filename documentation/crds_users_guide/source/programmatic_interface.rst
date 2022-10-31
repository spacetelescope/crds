Using the Programmatic Python Interface to submit reference files
=================================================================

As an alternative to command-line and web submissions of reference files,
there is a programmatic interface that allows users to perform the tasks
of reference file submission using Python.  It requires crds version 7.3.1 or higher.

Required CRDS Account
.....................

Submitting files to CRDS requires obtaining a CRDS account authorizing you to
do so.  These permissions are managed by CRDS and checked automatically after
your MyST identity is verified.

To obtain a CRDS account,  please file a ticket with the `CRDS Jira`_
project requesting authorization so submit files.

.. _`CRDS Jira`:  https://jira.stsci.edu/projects/CRDS/issues

**IMPORTANT** Your MyST identity is connected to your CRDS permissions via your
MyST e-mail.  You should specify your MyST e-mail when applying for a CRDS
account.

Authenticating
..............

To utilize the programmatic API you are required to have a CRDS account and to
authenticate via MyST and auth.mast_.  MyST will ask you to enter your AD
password unless you have already authenticated.  auth.mast_ supports the
creation and revocation of secret token_ values.

.. _auth.mast: https://auth.mast.stsci.edu/
.. _token: https://auth.mast.stsci.edu/tokens

The string value of this token must be inserted into the environment
variable MAST_API_TOKEN:

  .. code-block:: python

      import os
      os.environ['MAST_API_TOKEN'] = 'LongStringObtainedFromAuth.mast.stsciPage'

A typical auth.mast token looks something like::

  1b73d91d0db55b1800847529a3b6f91e

**IMPORTANT:** Since CRDS now uses MyST and auth.mast to identify you, never
never directly enter your AD password (MyST password) on the CRDS server or in
response to a CRDS prompt.

**NOTE:** CRDS passwords for existing CRDS file submitters and operators are
obsolete and no longer work.

API Description
...............

To use this functionality, import the Submission class from crds:

  .. code-block:: python

      from crds.submit import Submission

The primary object that a user interacts with is a Submission
object.  This can be instantiated using the following syntax:

  .. code-block:: python

      s = Submission(observatory, server, context=None)

where

    - **observatory**: String of the observatory to modify. Examples: 'jwst', 'hst', or 'roman'
    - **server**: The server string to be delivered to. Examples: 'ops', 'test', or 'dev'
    - **context**: The derive-from context. If None, the current edit context is used. Examples: 'jwst_775.pmap'

For example, to instantiate a JWST submission to be delivered to the OPS server deriving from the edit context, use::

    s = Submission('jwst', 'ops')
    

The Submission object has several methods, not the least a `.help()`
method that gives the full information on all the fields to be filled::

    s.help()
    deliverer (str)
    ---------
    Name of deliverer
    Who are you?

    other_email (str, optional)
    -----------
    Other e-mail adresses to send notifications
    Comma-delimited list (optional)

    instrument (str)
    ----------
    Instrument  (All submitted files should match this instrument.  This
    instrument will be locked for your submission exclusively)
    Valid choices:
      {'fgs', 'miri', 'nircam', 'niriss', 'nirspec', 'system'}

    file_type (str)
    ---------
    Type of files (Bias, Dark, etc.)

    history_updated (bool, optional)
    ---------------
    Has HISTORY section in the primary header been updated to describe in
    detail the reason for delivery and how the files were created?
    Valid choices:
      {'False', 'True'}

    pedigree_updated (bool, optional)
    ----------------
    Has PEDIGREE keyword been checked and updated as necessary?
    Valid choices:
      {'False', 'True'}

    keywords_checked (bool, optional)
    ----------------
    Have REFTYPE and AUTHOR been checked and updated as necessary?
    Valid choices:
      {'False', 'True'}

    descrip_updated (bool, optional)
    ---------------
    Was the DESCRIP keyword updated with a summary of why the files were
    updated or created?
    Valid choices:
      {'False', 'True'}

    useafter_updated (bool, optional)
    ----------------
    Has the USEAFTER keyword been checked, and if necessary, updated?
    Valid choices:
      {'False', 'True'}

    useafter_matches (str)
    ----------------
    If the reference files are replacing previous versions, do the new
    USEAFTER dates exactly match the old ones?
    N/A for ETC Files Only
    Valid choices:
      {'N/A', 'No', 'Yes'}

    compliance_verified (str)
    -------------------
    Verification for compliance complete (fits, json, asdf compliant,
    certify, etc. or N/A)
    optional
    Valid choices:
      {'N/A', 'No', 'Yes'}

    ingest_files (bool, optional)
    ------------
    Should the affected files be reprocessed?
    Valid choices:
      {'False', 'True'}

    etc_delivery (bool, optional)
    ------------
    Should the files be submitted to the ETC?
    Valid choices:
      {'False', 'True'}

    jwst_etc (bool, optional)
    --------
    Are these JWST ETC files?
    Valid choices:
      {'False', 'True'}

    calpipe_version (str)
    ---------------
    Files run through the current version of the calibration software
    being used by the pipeline or PYSYNPHOT and ETC (yes/no and version
    number)

    replacement_files (bool, optional)
    -----------------
    Are any files replacing old reference files (deliveries can be a mix
    of files that are or are not replacing old files) (yes/no)
    Valid choices:
      {'False', 'True'}

    old_reference_files (str, optional)
    -------------------
    If yes, list them here

    replacing_badfiles (str)
    ------------------
    If the files being replaced are bad (resulting in scientifically
    invalid results), and should not be used with any data, please
    indicate this here
    ... or crashing the system.
    Valid choices:
      {'N/A', 'No', 'Yes'}

    jira_issue (str, optional)
    ----------
    Any JIRA issues filed in regard to the references being delivered
    (e.g. "REDCAT-25")
    Comma-delimited list (optional)

    table_rows_changed (str, optional)
    ------------------
    If files are tables, please indicate exactly which rows have changed

    modes_affected (str)
    --------------
    Please indicate which modes (e.g. all the STIS, FUVMAMA, E140L modes)
    are affected by the changes in the files

    change_level (str)
    ------------
    Degree that new files are expected to impact science results.
    Valid choices:
      {'TRIVIAL', 'SEVERE', 'MODERATE'}

    correctness_testing (str)
    -------------------
    Description of how the files were tested for correctness

    additional_considerations (str, optional)
    -------------------------
    Additional considerations

    description (str)
    -----------
    Information about file changes and expected impacts, include
    instrument and type.  Formatting note: only alphanumeric, periods,
    commas, dashes, and underscores are allowed

The fields of the submission object can be filled using (key, value)
assignments as is done with Python dictionaries::

    s['deliverer'] = 'Scarlet Feline'
    s['other_email'] = 'redcat@stsci.edu'
    s['instrument'] = 'miri'

The value of s['instrument'] is limited to the set of valid instruments for the
observatory specified in the constructor for s.  If you try to set s['instrument']
to something other than one of these instruments, an exception will occur.
Similarly, if you try to set s['chicken'], or some other keyword not in the
set of allowed keywords, and exception will occur::

    s['file_type']                  = 'DARK'
    s['history_updated']            = True
    s['pedigree_updated']           = True
    s['keywords_checked']           = True
    s['descrip_updated']            = True
    s['useafter_updated']           = True
    s['useafter_matches']           = True
    s['compliance_verified']        = 'N/A'
    s['ingest_files']               = False
    s['etc_delivery']               = False
    s['jwst_etc']                   = False
    s['calpipe_version']            = '0.9.1'
    s['replacement_files']          = False
    #s['old_reference_files']       = ''
    s['replacing_badfiles']         = 'N/A'
    #s['jira_issue']                = ''
    s['table_rows_changed']         = 'All rows'
    s['modes_affected']             = 'All MIRI observations starting 2017-Jan-03'
    s['correctness_testing']        = 'DARK was run on all MIRI data and verified '
    #s['additional_considerations'] = ''
    s['change_level']               = 'MODERATE'
    s['description']                = 'Updating MIRI DARK starting 2017-Jan-03.'

The assignments that are commented out are unnecessary as the default values are empty strings.
To add files to the submission, use the add_file() method::

    s.add_file('miri_dark_file.fits')

You can also remove files::

    s.remove_file('miri_dark_file.fits')

And finally, when the files to be submitted have been added and the fields
of the Submission have been filled in, the Submission can be submitted::

    result = s.submit()
    2019-04-24 12:24:50,823 - CRDS - INFO -  =============================== setting up ===============================
    2019-04-24 12:24:51,038 - CRDS - INFO -  Symbolic context 'jwst-edit' resolves to 'jwst_0511.pmap'
    2019-04-24 12:24:51,038 - CRDS - INFO -  ########################################
    2019-04-24 12:24:51,038 - CRDS - INFO -  Certifying './miri_dark_test.fits' (1/1) as 'FITS' relative to context 'jwst_0511.pmap'
    2019-04-24 12:24:55,166 - CRDS - INFO -  FITS file 'miri_dark_test.fits' conforms to FITS standards.
    2019-04-24 12:24:56,219 - CRDS - WARNING -  Missing suggested keyword 'META.MODEL_TYPE [DATAMODL]'
    2019-04-24 12:24:56,298 - CRDS - INFO -  [0] DETECTOR MIRIMAGE 
    2019-04-24 12:24:56,298 - CRDS - INFO -  [0] EXP_TYPE MIR_IMAGE 
    2019-04-24 12:24:56,302 - CRDS - INFO -  META.AUTHOR [AUTHOR] = 'JANE MORRISON'
    2019-04-24 12:24:56,302 - CRDS - INFO -  META.DESCRIPTION [DESCRIP] = 'MIRI Dark Correction for MIRI'
    2019-04-24 12:24:56,302 - CRDS - INFO -  META.EXPOSURE.GROUPGAP [GROUPGAP] = 0
    2019-04-24 12:24:56,303 - CRDS - INFO -  META.EXPOSURE.NFRAMES [NFRAMES] = 1
    2019-04-24 12:24:56,303 - CRDS - INFO -  META.EXPOSURE.NGROUPS [NGROUPS] = 200
    2019-04-24 12:24:56,303 - CRDS - INFO -  META.EXPOSURE.READPATT [READPATT] = 'FAST'
    2019-04-24 12:24:56,303 - CRDS - INFO -  META.EXPOSURE.TYPE [EXP_TYPE] = 'MIR_IMAGE'
    2019-04-24 12:24:56,303 - CRDS - INFO -  META.HISTORY [HISTORY] = 'SEE MIRI-TN-00007-UA-Mean-Dark.PDF for details\nFit was done correcting for nonlinearity and RSCD Correction\nOne solution rejected first 10 frames and last frame\nSecond solution corrected all the frames for nonlinearity and RSCD\nBecause of drifting zero points, first solution was used to find frame v\nframe value at time = 0 was subtracted off all the data\nresulting residuals were binned and average\n a linear fits was performed on the residuals to extrapolate the dark re\n the number of frames used in the fit is defined by NGVALID\n The mean dark residuals were used for frames with valid data, out side\nDATA USED: to create dark CV3  IMG_RAD_01, IMG_RAD_13\nDOCUMENT: MIRI-TR-00007-UA-Dark_06.00.pdf\nSOFTWARE: idl code create_dark_CDP6.pro merge_int_CDP6\nDIFFERENCES: darks now have two integrations\nCreated from: MiriDarkReferenceModel'
    2019-04-24 12:24:56,303 - CRDS - INFO -  META.INSTRUMENT.BAND [BAND] = 'UNDEFINED'
    2019-04-24 12:24:56,303 - CRDS - INFO -  META.INSTRUMENT.CHANNEL [CHANNEL] = 'UNDEFINED'
    2019-04-24 12:24:56,303 - CRDS - INFO -  META.INSTRUMENT.CORONAGRAPH [CORONMSK] = 'UNDEFINED'
    2019-04-24 12:24:56,303 - CRDS - INFO -  META.INSTRUMENT.DETECTOR [DETECTOR] = 'MIRIMAGE'
    2019-04-24 12:24:56,303 - CRDS - INFO -  META.INSTRUMENT.FILTER [FILTER] = 'ANY'
    2019-04-24 12:24:56,303 - CRDS - INFO -  META.INSTRUMENT.GRATING [GRATING] = 'UNDEFINED'
    2019-04-24 12:24:56,303 - CRDS - INFO -  META.INSTRUMENT.NAME [INSTRUME] = 'MIRI'
    2019-04-24 12:24:56,303 - CRDS - INFO -  META.INSTRUMENT.PUPIL [PUPIL] = 'UNDEFINED'
    2019-04-24 12:24:56,303 - CRDS - INFO -  META.MODEL_TYPE [DATAMODL] = 'UNDEFINED'
    2019-04-24 12:24:56,303 - CRDS - INFO -  META.PEDIGREE [PEDIGREE] = 'GROUND'
    2019-04-24 12:24:56,303 - CRDS - INFO -  META.REFTYPE [REFTYPE] = 'DARK'
    2019-04-24 12:24:56,303 - CRDS - INFO -  META.SUBARRAY.FASTAXIS [FASTAXIS] = 1
    2019-04-24 12:24:56,303 - CRDS - INFO -  META.SUBARRAY.NAME [SUBARRAY] = 'FULL'
    2019-04-24 12:24:56,303 - CRDS - INFO -  META.SUBARRAY.SLOWAXIS [SLOWAXIS] = 2
    2019-04-24 12:24:56,304 - CRDS - INFO -  META.SUBARRAY.XSIZE [SUBSIZE1] = 1032
    2019-04-24 12:24:56,304 - CRDS - INFO -  META.SUBARRAY.XSTART [SUBSTRT1] = 1
    2019-04-24 12:24:56,304 - CRDS - INFO -  META.SUBARRAY.YSIZE [SUBSIZE2] = 1024
    2019-04-24 12:24:56,304 - CRDS - INFO -  META.SUBARRAY.YSTART [SUBSTRT2] = 1
    2019-04-24 12:24:56,304 - CRDS - INFO -  META.TELESCOPE [TELESCOP] = 'JWST'
    2019-04-24 12:24:56,304 - CRDS - INFO -  META.USEAFTER [USEAFTER] = '2015-08-02T00:00:00'
    2019-04-24 12:24:56,304 - CRDS - INFO -  Running fitsverify.
    2019-04-24 12:24:56,315 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,315 - CRDS - INFO -  >>               fitsverify 4.18 (CFITSIO V3.440)              
    2019-04-24 12:24:56,315 - CRDS - INFO -  >>               --------------------------------              
    2019-04-24 12:24:56,315 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,315 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,315 - CRDS - INFO -  >> File: ./miri_dark_test.fits
    2019-04-24 12:24:56,316 - CRDS - INFO -  >> 
    2019-04-24 12:24:56,316 - CRDS - INFO -  >> 7 Header-Data Units in this file.
    2019-04-24 12:24:56,316 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,316 - CRDS - INFO -  >> =================== HDU 1: Primary Array ===================
    2019-04-24 12:24:56,316 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,316 - CRDS - INFO -  >>  57 header keywords
    2019-04-24 12:24:56,316 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,316 - CRDS - INFO -  >>  Null data array; NAXIS = 0 
    2019-04-24 12:24:56,316 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,316 - CRDS - INFO -  >> =================== HDU 2: Image Exten. ====================
    2019-04-24 12:24:56,316 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,316 - CRDS - INFO -  >>  15 header keywords
    2019-04-24 12:24:56,316 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,316 - CRDS - INFO -  >> SCI 32-bit floating point pixels,  4 axes (1032 x 1024 x 200 x 2), 
    2019-04-24 12:24:56,316 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,316 - CRDS - INFO -  >> =================== HDU 3: Image Exten. ====================
    2019-04-24 12:24:56,316 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,316 - CRDS - INFO -  >>  15 header keywords
    2019-04-24 12:24:56,316 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,316 - CRDS - INFO -  >> ERR 32-bit floating point pixels,  4 axes (1032 x 1024 x 200 x 2), 
    2019-04-24 12:24:56,316 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,316 - CRDS - INFO -  >> =================== HDU 4: Image Exten. ====================
    2019-04-24 12:24:56,316 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,317 - CRDS - INFO -  >>  16 header keywords
    2019-04-24 12:24:56,317 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,317 - CRDS - INFO -  >> DQ 32-bit integer pixels,  4 axes (1032 x 1024 x 1 x 2), 
    2019-04-24 12:24:56,317 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,317 - CRDS - INFO -  >> =================== HDU 5: BINARY Table ====================
    2019-04-24 12:24:56,317 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,317 - CRDS - INFO -  >>  21 header keywords
    2019-04-24 12:24:56,317 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,317 - CRDS - INFO -  >>  DQ_DEF  (4 columns x 2 rows)
    2019-04-24 12:24:56,317 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,317 - CRDS - INFO -  >>  Col# Name (Units)       Format
    2019-04-24 12:24:56,317 - CRDS - INFO -  >>    1 BIT                  J         
    2019-04-24 12:24:56,317 - CRDS - INFO -  >>    2 VALUE                J         
    2019-04-24 12:24:56,317 - CRDS - INFO -  >>    3 NAME                 40A       
    2019-04-24 12:24:56,317 - CRDS - INFO -  >>    4 DESCRIPTION          80A       
    2019-04-24 12:24:56,317 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,317 - CRDS - INFO -  >> =================== HDU 6: Image Exten. ====================
    2019-04-24 12:24:56,317 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,317 - CRDS - INFO -  >>  8 header keywords
    2019-04-24 12:24:56,317 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,317 - CRDS - INFO -  >> METADATA 8-bit integer pixels,  1 axes (1605), 
    2019-04-24 12:24:56,317 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,317 - CRDS - INFO -  >> =================== HDU 7: Image Exten. ====================
    2019-04-24 12:24:56,318 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,318 - CRDS - INFO -  >>  9 header keywords
    2019-04-24 12:24:56,318 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,318 - CRDS - INFO -  >> FITERR 32-bit floating point pixels,  2 axes (1032 x 1024), 
    2019-04-24 12:24:56,318 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,318 - CRDS - INFO -  >> ++++++++++++++++++++++ Error Summary  ++++++++++++++++++++++
    2019-04-24 12:24:56,318 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,318 - CRDS - INFO -  >>  HDU#  Name (version)       Type             Warnings  Errors
    2019-04-24 12:24:56,318 - CRDS - INFO -  >>  1                          Primary Array    0         0     
    2019-04-24 12:24:56,318 - CRDS - INFO -  >>  2     SCI                  Image Array      0         0     
    2019-04-24 12:24:56,318 - CRDS - INFO -  >>  3     ERR                  Image Array      0         0     
    2019-04-24 12:24:56,318 - CRDS - INFO -  >>  4     DQ                   Image Array      0         0     
    2019-04-24 12:24:56,318 - CRDS - INFO -  >>  5     DQ_DEF               Binary Table     0         0     
    2019-04-24 12:24:56,318 - CRDS - INFO -  >>  6     METADATA             Image Array      0         0     
    2019-04-24 12:24:56,318 - CRDS - INFO -  >>  7     FITERR               Image Array      0         0     
    2019-04-24 12:24:56,318 - CRDS - INFO -  >>  
    2019-04-24 12:24:56,318 - CRDS - INFO -  >> **** Verification found 0 warning(s) and 0 error(s). ****
    2019-04-24 12:24:56,318 - CRDS - INFO -  Checking JWST datamodels.
    2019-04-24 12:24:56,347 - CRDS - WARNING -  NoTypeWarning : jwst.datamodels.util : model_type not found. Opening ./miri_dark_test.fits as a ReferenceQuadModel
    2019-04-24 12:24:56,396 - CRDS - INFO -  ########################################
    2019-04-24 12:24:56,436 - CRDS - INFO -  Logging in aquiring lock.
    2019-04-24 12:24:57,489 - CRDS - INFO -  =============================== wipe files ===============================
    2019-04-24 12:24:57,613 - CRDS - INFO -  Preparing server logging.
    2019-04-24 12:24:57,723 - CRDS - INFO -  ============================== ingest files ==============================
    2019-04-24 12:24:57,724 - CRDS - INFO -  Uploading 1 file(s) totalling   3.4 G bytes
    2019-04-24 12:24:57,825 - CRDS - INFO -  Upload started './miri_dark_test.fits' [ 1 / 1  files ] [   3.4 G /   3.4 G  bytes ]
    2019-04-24 12:26:07,683 - CRDS - INFO -  ===========================================================================
    2019-04-24 12:26:07,683 - CRDS - INFO -  Posting web request for '/submission_form/redcat_submit/'
    CRDS - INFO -  ======= monitoring server on 'e8e0f1d3-45d4-44cd-a2b8-1aa279f5dd33' =======
    CRDS - INFO -  >> Starting submission processing.
    CRDS - INFO -  >> Certifying 'miri_dark_test.fits'
    CRDS - INFO -  >> Resolved old rmap as 'jwst_miri_dark_0033.rmap' based on context 'jwst_0511.pmap'
    CRDS - INFO -  >> Doing trial insertion of 1 references into 'jwst_miri_dark_0033.rmap'
    CRDS - INFO -  >> Processing 'miri_dark_test.fits' [1 / 1 files] [  3.4 G /   3.4 G /   3.4 G bytes]
    CRDS - INFO -  >> Renaming 'miri_dark_test.fits' --> 'jwst_miri_dark_0075.fits'
    CRDS - INFO -  >> Linking miri_dark_test.fits --> jwst_miri_dark_0075.fits
    CRDS - INFO -  >> Adding file 'miri_dark_test.fits' to database.
    CRDS - INFO -  >> Generating new rmap 'jwst_miri_dark_0034.rmap' from 'jwst_miri_dark_0033.rmap'.
    CRDS - INFO -  >> Adding file 'jwst_miri_dark_0034.rmap' to database.
    CRDS - INFO -  >> Certifying 'jwst_miri_dark_0034.rmap'
    CRDS - INFO -  >> Checking for derivation collisions.
    CRDS - INFO -  >> Computing file differences.
    CRDS - INFO -  >> Differencing 'jwst_miri_dark_0033.rmap' vs. 'jwst_miri_dark_0034.rmap'
    CRDS - INFO -  >> COMPLETED: https://jwst-crds-test.stsci.edu//display_result/f01bdb8b-6d70-46a8-95e1-e2bdb6ce1f9c
    CRDS - INFO -  ========================= monitoring server done =========================
    CRDS - INFO -  0 errors
    CRDS - INFO -  2 warnings
    CRDS - INFO -  132 infos
    CRDS - INFO -  STARTED 2019-04-24 12:24:50.81
    CRDS - INFO -  STOPPED 2019-04-24 12:27:41.93
    CRDS - INFO -  ELAPSED 0:02:51.11

This will validate the submission by making sure all of the fields that need values
have them and by ensuring that there is at least 1 file to submit before performing
the submission.

The return value of `submit()` includes error and warning counts, as well as
a link to the Review/Confirm page for the submission::

    result.error_count
    result.warning_count
    result.ready_url

The `open_ready_url()` function will attempt to open the Review/Confirm page in
your system's default browser::

    result.open_ready_url()

Note that the page's *confirm*, *cancel*, and *force* buttons will not be available
unless authenticated.  If they seem to be missing, try logging in with the *Login*
button at the upper right-hand corner of the page.

* Submission `file_map` Attribute

   As of `v11.16.12`, the submission object includes a `file_map` property which returns a dictionary of uploaded reference filenames, "old" mappings (keys) paired with automatically renamed references, newly generated mappings (values).

   .. code-block:: python

       s.file_map

       {'miri_dark_test.fits': 'jwst_miri_dark_0075.fits',
       'jwst_miri_dark_0033.rmap': 'jwst_miri_dark_0034.rmap',
       'jwst_0511.pmap': 'jwst_0512.pmap',
       'jwst_miri_0513.imap': 'jwst_miri_0514.imap'}
  
   Note that before a new context has been set, the new mapping names are hypothetical.
   If the submission has not yet been confirmed, the same is true of the new reference filenames. 

