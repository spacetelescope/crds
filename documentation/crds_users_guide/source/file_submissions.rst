File Submissions
================

CRDS provides a number of functions used to submit new reference files or
rules.

This section describes the processes of submitting files to CRDS.  It does not
detail the requirements of *creating* files which are described better
elsewhere and *fundamental* to what you're doing.
  
Extended Batch Submit References (new)
......................................

The most common form of file submission is to submit new reference files and
have CRDS automatically check them and merge them into the CRDS file assignment
rules,  i.e. generate new rmaps, imap, and pmap based on header keywords in
the submitted reference files.

The *Extended Batch Submit References* process adds a number of additional form
fields used to characterize your submission.  These fields were previously
captured by ReDCaT file submission scripts.  This metadata is tracked in the
CRDS server database.  Aside from adding metadata, the Extended Batch Submit
References process is essentially identical to the original Batch Submit
References process.

The new web form, which begins as shown, fully supersedes the old form:

.. figure:: images/extend_batch_submit.png
   :scale: 50 %
   :alt: extended batch reference submission inputs

.. figure:: images/extend_batch_submit_2.png
   :scale: 50 %
   :alt: extended batch reference submission inputs 2

.. figure:: images/extend_batch_submit_3.png
   :scale: 50 %
   :alt: extended batch reference submission inputs 3

.. figure:: images/extend_batch_submit_4.png
   :scale: 50 %
   :alt: extended batch reference submission inputs 4

**NOTE:** *Checked* or *Yes* answers for many fields are required for your
submission to succeed; many of the form fields are reminders of the ReDCaT
requirements for submitting files to CRDS.

Batch Submit References (deprecated)
....................................

*Batch Submit References* is intended to handle the majority of CRDS reference
submissions, both checking and ingesting files and automatically generating the
corresponding CRDS rules updates.  It accepts a number of reference files and
metadata which applies to all of them.

The specified reference files are checked on the server using crds.certify and
if they pass are submitted to CRDS.  

.. figure:: images/web_batch_submit_references.png
   :scale: 50 %
   :alt: batch reference submission inputs
   
Upload Files
++++++++++++

The first task involved with *Batch Submit References* is transferring the
submitted files to the server.  There are two approaches for getting files on
the server, web based and shell based.  Each CRDS user has their own ingest
directory.  This section applies equally to all of the file submission pages
that have an *Upload Files* accordion.

Web Approach
!!!!!!!!!!!!

On the file submission pages,  the *Upload Files* accordion opens to support
uploading submitted files to a user's CRDS ingest directory via the browser.

.. figure:: images/web_upload_files.png
   :scale: 50 %
   :alt: file upload accordion

Uploading files is accomplished by:

* Opening the accordion panel by clicking on it.

* Add files to the upload list by clicking on the *Add Files...* button.

* Click *Start Upload* to initiate the file transfer.   When the upload successfully completes the buttons will change to *delete*.

* Click *Delete* for any file added by mistake or for failed uploads.

* Click *Cancel Upload* to abort a file transfer during the upload.

* Close the accordion panel by clicking on it.

**IMPORTANT**  Just adding files to the file list does not upload them.   You
must click *Start upload* to initiate the file transfer.

Shell Approach
!!!!!!!!!!!!!!

In the shell approach a user must login to UNIX (in some fashion) and transfer
files into their CRDS ingest directory manually.   For instance::

  % scp /this_delivery/*.fits   pldmsins1.stsci.edu:/ifs/crds/hst/ops/server_files/ingest/<username>

to copy references into my ingest directory *as-if* I had uploaded them through
the uploads panel.

The submitted reference files should now be your ingest directory on the server
and the CRDS server will behave as if they had been uploaded through web
interface.  Refreshing the file submission web page should make manually copied
files show up in the *Upload Files* accordion.

Using cp or scp improves the efficiency and reliability of file transfers
should that become an issue.  Telecommuters working offsite by VPN can use this
technique to avoid inefficient transfers.

Derive From Context 
+++++++++++++++++++

The specified context is used as the starting point for new automatically 
generated context files and also determines any predecessors of the submitted 
references for comparison during certification.   If all the submitted reference
files pass certification,  a new .rmap, .imap, and .pmap are generated
automatically to refer to the newly entered references.    Based on their
header parameters,  references are automatically assigned to appropriate
match locations in the .rmap file.

.. figure:: images/web_derive_from_context.png
   :scale: 50 %
   :alt: context specification

There are two special contexts in CRDS which are tracked:

Edit Context
!!!!!!!!!!!!

Edit Context is the default context used for adding new files.  Whenever a new
.pmap is created or added, it becomes the editing context from which future
.pmaps are derived by default.

Operational Context
!!!!!!!!!!!!!!!!!!!

Operational Context is the .pmap which is nominally in use by
the pipeline.   While it's common to make new files operational as each
context is added,  it's possible for the operational context to lag
behind the edit context where new files are being added.

Recent 
!!!!!!

Recent lists a number of recently added contexts based on delivery time.   

User Specified
!!!!!!!!!!!!!!

Any valid CRDS context can be typed in directly as User Specified.
   
Auto Rename
+++++++++++

Normally files uploaded to CRDS will be assigned new unique names. Unchecking
Auto Rename will request that CRDS use the uploaded file name as the official
name.  The CRDS database remembers both the name of the file the submitter
uploaded as well as the new unique name.

Turning off Auto Rename should be done judiciously if at all.   It's
appropriate in situations where uploaded files already have known unique names
which it is desirable to keep.

  * For JWST calibration references, in general Auto Rename should not be
    turned off.

  * For HST calibration references which are assigned unique names prior to
    being submitted to CRDS, it is appropriate to turn Auto Rename off.

  * For SYNPHOT references,  in general it is appropriate to turn Auto
    Rename off.

  * For hand-edited CRDS rules files (pmaps, imaps, rmaps) it can be
    appropriate to turn Auto Rename off if file naming and header fields
    have already been properly assigned.

Compare Old Reference
+++++++++++++++++++++

When checked CRDS will certify incoming tabular references against the files
they replace with respect to the derivation context.   For other references this 
input is irrelevant and ignored.

Results
+++++++

.. figure:: images/web_batch_submit_results.png
   :scale: 50 %
   :alt: batch submission results
   
The results page lists the following items:

* *Starting Context* is the context this submission derove from.

* *Generated New Mappings* lists the new mapping files which provide the generated context for using the submitted references.

* *Actions on Rmap* provides two accordions showing how the rmap controlling
  the submitted references was modified.  The logical differences accordion has
  a table of actions, either *insert* for completely new files or *replace* for
  files which replaced an existing file.  The text differences are essentially
  output from UNIX *diff* for the old and new rmaps.

* *Certify Results* has an accordion panel for each submitted reference file
  which contains the results from crds.certify.  The submitted name of each
  file is listed first, followed by any official name of the file assigned by
  CRDS.  The status of a successful certification can be "OK" or "Warnings".
  The status of a failed certification will be "ERRORS".  Failed certifications
  automatically cancel a file submission.
  
  Warnings should be reviewed by opening the accordion panel.  Some CRDS
  warnings describe conditions which *MUST* be addressed by future manual rmap
  updates or cancelling the submission.   In particular,
   
**IMPORTANT**  The results page only indicates the files which will be added to
CRDS if the submission is *confirmed*.   Prior to confirmation of the submission,
neither the submitted references nor the generated mappings are officially in CRDS.

If you loose track of the submission log or confirmation pages,  you can find
links to them in the *STARTED* and *READY* e-mails that CRDS sends out
when a submission is initiated or CRDS has completed submission checkout
and is ready for confirmation or cancellation.

Collisions
++++++++++

Under some circumstances,  a *Collision Warning* accordion will be present.
It should be carefully examined to ensure that overlapping edits of the
same context file have not occurred.   Overlaps can be resolved by cancelling
the current submission and re-doing it, or by accepting the current submission
and manually correcting the mappings involved.   Failure to correctly resolve
a collision will most likely result in one of two sets of conflicting changes
being lost.

.. figure:: images/web_collision_warnings.png
   :scale: 50 %
   :alt: collision warnings
   
Collision tracking for CRDS mappings files is done based upon header fields,
nominally the *name* and *derived_from* fields.  These fields are automatically
updated when mappings are submitted or generated.

Collision tracking for reference files is currently filename based.   The submitted
name of a reference file is assumed to be the same as the file it 
was derived from.   This fits a work-flow where a reference is first downloaded
from CRDS, modified under the same name,  and re-uploaded.   Nominally,  submitted
files are automatically re-named.

Confirm, Force, Cancel
++++++++++++++++++++++

If everything looks good the last step is to click the *Confirm* button.
Confirming finalizes the submission process,  submits the files
for archive pickup,  and makes them a permanent part of CRDS visible in the 
database browser and potentially redistributable.   

A confirmed submission cannot be revoked,  but neither will it go into use until 
the pipeline or a user requests it either by updating the default context on 
the CRDS server or by specifying the new rules explicitly.

*Cancelling* a batch submission based on warnings or bad rmap modifications
removes the submission from CRDS.   In particular temporary database records
and file copies are removed.

*Forcing* a batch submission can be performed by any team member once the instrument
lock of the original submitter has been dropped or times out.

Following any CRDS batch reference submission,  the default *edit* context
is updated to that pipeline mapping making it the default starting point for
future submissions.

Submit Mappings
...............

*Submit Mappings* provides a basic interface for submitting a list of mapping
files which don't have to be related.   This can be used to submit context files
which refer to files from *Submit References* and with fewer restrictions on
allowable changes.   Typically only .rmaps are submitted this way.   Mappings
submitted this way must also pass through crds.certify.   

.. figure:: images/web_submit_mappings.png
   :scale: 50 %
   :alt: create contexts inputs

   
Mapping Change Procedure
++++++++++++++++++++++++

The manual rmap update process is to:

1.  Download the starting rmap from the web site or get it out of /grp/crds/cache/mappings/{hst,jwst}/.

2.  **DO NOT** change the name of the mapping or alter the internal name links
    like *derived_from* in the mapping header.  Leave the naming properties exactly as-is.

3.  Modify the mapping in any text editor and verify the mapping as best you
    can.  Use great care, CRDS certify cannot check many of the mapping properties.

4. Run crds.certify on the resulting mapping, using the current edit context as
   the point of comparison::

     % crds certify ./jwst_miri_dark_0004.rmap  --comparison-context jwst-edit

   You may/will see an rmap checksum warning since you modified the contents of
   the rmap.

   Note: the ./ seen in the example command is important,  it tells CRDS to
   use the file in the current directory instead of attempting to find it in
   the CRDS cache.

   By default, most tools in CRDS will not load a mapping with an incorrect
   checksum.  Run crds.checksum on the mapping to update the internal sha1sum
   if you wish to load the context into Python to do other tests with the
   .rmap::

     % crds checksum ./jwst_miri_dark_0004.rmap
    
   The internal checksum is also used to verify the upload integrity when you
   finally submit the file to CRDS.  An out-of-date checksum or corrupted file
   will generate a warning and the server will automatically fix it.  However,
   it is then possible for upload errors to go undetected since a warning is
   expected.

6. Typically for rmaps, **DO** check Generate Contexts as that will derive new a
   imap and pmap referring to your modified rmap.

7. As you submit, **DO** check Auto-Rename.  In addition to renaming your
   modified rmap, this automatically handles the internal rmap header naming
   properties correctly. 

Following this process is the key to maintaining the rmap's internal naming
links.  The internal naming links are used to track the derivation of rmaps
and generate the Edit Collision Warnings.  Edit Collision warnings indicate
when two rmaps were derived from the same source and can mean that one of the
two change sets will be lost if the delivery is not corrected.

Imap and Pmap Differences
+++++++++++++++++++++++++

Note that submissions of imaps and pmaps do not support Generate Context.  In
addition, CRDS doesn't accept files that refer to other files not already in
CRDS.  This means that pmaps and new imaps they refer to cannot be handled in
one submission.

The general practice of not manually modifying CRDS mapping name properties
holds for imaps and pmaps as well: it's better to leave filenames unchanged,
and header naming properties unchanged, and let CRDS do Auto-rename and related
header updates.

Hence, it is recommended to do imap and pmap work in two phases: First, modify
and submit the imaps, generating and/or reserving official CRDS names.  Next
manually modify the pmap as needed to refer to the newly generated imap names.

Mark Files Bad
..............

*Mark Files Bad* supports marking a file as scientifically invalid and
also supports reversing the decision and marking it good once more.

The CRDS procedure for marking files bad requires three steps:

1. Create a clean context which does not contain any prospective bad files.
2. Make the clean context operational using Set Context.
3. Mark the prospective bad files actually bad using Mark Bad Files.

This procedure maintains the invariant that the operational pipeline context
contains no known bad files.  The designation as bad files does not take effect
until the pipeline CRDS cache is synchronized with the server.

Creating a clean context can be done in arbitrary ways,  but the two most
common ways will likely be:

1. Submit replacement files for the bad files to create a clean context.
2. Use Delete References to generate a new context without the bad files.

.. figure:: images/web_mark_files_bad.png
   :scale: 50 %
   :alt: mark files bad inputs

Marking a rules file (mapping) as bad implicitly marks all the files
which refer to it as bad.  Hence,  marking a .rmap as bad will make
any .imap which refers to it bad as well,  and will also taint all .pmaps
which refer to the bad .imaps.   Whenever a rules file is marked bad,
it becomes an error to use the containing context.

Marking a reference file as bad only invalidates that reference in every
context that includes it.  An error is issued for a bad reference only when
it is actually recommended by CRDS,  it is not an error to use the containing
context.

By default, bestrefs assignment of bad references or use of bad rules are errors.
The default command line behavior can be overridden by setting environment variables:
*CRDS_ALLOW_BAD_RULES* and/or *CRDS_ALLOW_BAD_REFERENCES*.

Delete References
.................

*Delete References* supports supports removing references (but not rules) from
a context generating a new context.  Delete References provides one
straightforward way to generate clean rules prior to marking the deleted files
as bad.

.. figure:: images/web_delete_references.png
   :scale: 50 %
   :alt: delete references

Delete References does not remove the files from CRDS, it only removes them
from the specified set of rules.  The references remain available under any
contexts which still refer to them.

Files are specified for Delete References by listing their names in the Deleted
Files field of the input form, separated by spaces, commas, and/or newlines.

Changes to rules which result from delete references are presented on a results
page which must be confirmed or cancelled as with other file submissions.

Add References
..............

*Add References* supports adding existing CRDS references to a CRDS context
which does not contain them already.  Add References is the inverse of Delete
References and generates new CRDS rules without requiring the re-submission of
files to CRDS.

.. figure:: images/web_add_references.png
   :scale: 50 %
   :alt: add references

Add references can be used to undo the effects of Delete References in a
perhaps distant descendant context containing other changes.  Add references
can also be used to add tested references from a branched context into the
current operational context.

Files are specified for Add References by listing their names in the Added
Files field of the input form, separated by spaces, commas, and/or newlines.

Changes to rules which result from add references are presented on a results
page which must be confirmed or cancelled as with other file submissions.
Rules changes from add references should be carefully reviewed to ensure that
the resulting rmap update is as intended.  

In particular, other rmap differences from a branched context are not added,
so additional test parameters or other header and structural changes of any
test rmap are not carried over by Add References,  only the reference files
themselves.

Submission Warnings and Errors
..............................

Identical Files
+++++++++++++++

CRDS can detect if your submitted files are bit-for-bit-identical to any
existing files or to each other by checking their sha1sums against the CRDS
database.  CRDS rejects identical files as errors since there is a reasonable
likelihood that intended files are missing.

**SOLUTION:**  remove the duplicate files from your submission and re-submit.

Certification Errors and Warnings
+++++++++++++++++++++++++++++++++

CRDS has a certification program that is used to check incoming reference and
rules files.  The certify program applies several kinds of checks which can
result in warnings or errors on the website.  (The certify program is also
installed with the CRDS client and can be run locally alone or embedded in
other file submission toolchains.  See command line tools.)

Internal CRDS Constraints
!!!!!!!!!!!!!!!!!!!!!!!!!

CRDS defines some constraints using specifications called .tpn files. These
specifications and checks can be reviewed on the website by looking up the
details of any particular reference file of the same instrument and type:

.. figure:: images/certify_tpn_listing.png
   :scale: 50 %
   :alt: add references

JWST Data Model Constraints
!!!!!!!!!!!!!!!!!!!!!!!!!!!

The JWST calibration software (CAL) models the structure and valild keyword
values for reference files in its jwst.datamodels package.  Effectively, the
CAL datamodels define a formatting contract your references are expected to
fulfill.  File which don't fulfill this contract will either result in
perpetual warnings or outright pipeline failures if CAL rejects a file.

As part of CRDS file checking, crds certify invokes datamodels.open() to verify
datamodels compliance for your reference files.

This message::

  CRDS - WARNING - Missing suggested keyword 'META.MODEL_TYPE [DATAMODL]'

indicates that the JWST CAL Data Models were not used to create your reference
files.  Datamodels.open() needs the DATAMODL keyword to define the correct
model to validate your file.

You have the option of ignoring this warning, but it means that CRDS is not
using the strictest and most appropriate model to validate your file, only a
more generic fallback model.  When your file later is processed by the CAL
software, the CAL software will use the correct model, so it may notice
contractual issues and reject your file.

**SOLUTION:** The best solution is to coordinate more closely with the JWST CAL
s/w group to learn how to use the datamodels to create your reference files.
Using the correct version of datamodels should guaranteee that your files are
compliant when you create them, as well as correctly populate the DATAMODL
keyword, reducing this CRDS check to a rubber stamp.  More information about
CAL reference file formats and the datamodels can be found here: `JWST CAL
Documentation`_.

.. _`JWST CAL Documentation`: https://jwst-pipeline.readthedocs.io/en/latest/jwst/package_index.html

Fitsverify Failures
!!!!!!!!!!!!!!!!!!!

For FITS files, as part of certification CRDS normally runs HEASARC's
fitsverify program to verify that file formats are broadly compliant and should
work with cfitsio as well as astropy.

1. Checksum errors

   CRDS classifies FITS checksum errors detected by fitsverify as errors::

   CRDS - ERROR -  >> RECATEGORIZED *** Warning: Data checksum is not consistent with  the DATASUM keyword
   CRDS - ERROR -  >> RECATEGORIZED *** Warning: HDU checksum is not in agreement with CHECKSUM.

   CRDS leaves Astropy checksum warnings alone::

   CRDS - WARNING -  AstropyUserWarning : astropy.io.fits.hdu.base : Checksum verification failed for HDU ('', 1).
   CRDS - WARNING -  AstropyUserWarning : astropy.io.fits.hdu.base : Datasum verification failed for HDU ('', 1).
   
   Checksums are not required, but if you do define them they should be correct
   so that file users are not bombarded with warnings from FITS libraries.
   Hence,  the CRDS server rejects files with bad checksums based on the errors
   defined for fitsverify.
   
   **SOLUTION 1:** Use your FITS s/w or *crds checksum* to update your CHECKSUM
    and DATASUM keywords::

     $ crds checksum *.fits

   **SOLUTION 2:** Use crds checksum or your FITS s/w to remove CHECKSUM and
   DATASUM keywords::

     $ crds checksum --remove *.fits

2. Other fitsverify anomalies

   fitsverify can detect other anomalies such as file truncation.

   By default warnings are merely echoed but errors will lead to the rejection
   of your files.  On request, CRDS can be easily modified to ignore or remap
   fitsverify warnings and errors.
   
No Comparison Reference Warning
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

For selected tables, CRDS attempts to perform a comparison between the new
version of a table and any table it replaces in the CRDS rules.  This check is
intended to detect accidental loss of table rows/modes and unexpected duplicate
rows.

When CRDS cannnot find a suitable comparison table,  CRDS issues a warning like::

    CRDS - WARNING - No comparison reference for 'test_jwst_nircam_photom_0039.fits' in context 'jwst_0503.pmap'. Skipping tables comparison.

to let you know that table checks are not being performed.  If it's expected
that some comparison table should exist, further investigation is warranted but
not required.  If this is a new table or inexact replacement (e.g. subsequent
USEAFTER date), the warning can be ignored.

Rmap Update Errors
++++++++++++++++++

As part of a typical reference file submission,  CRDS automatically adds new
files to the appropriate rmap and generates new context files.   This phase
can detect some forms of errors which should be addressed.

Exact Matching Duplicates
!!!!!!!!!!!!!!!!!!!!!!!!!

Given the task of adding N reference files to an rmap,  CRDS checks that N new
files really do appear in the new rmap.  It is possible for new reference files
to have different sha1sums, i.e. not be bit-for-bit-identical,  but also to use
exactly the same CRDS matching criteria.  With identical matching criteria,
both files would occupy the same location in the .rmap,  and one file would
replace the other. This is almost certainly an error so CRDS rejects the file
submission with a message like this::

    CRDS - ERROR -  ----------------------------------------
    Both 's7g1700gl_dead_dup2.fits' and 's7g1700gl_dead_dup1.fits' identically match case:
     ((('DETECTOR', 'FUV'),), (('DATE-OBS', '1996-10-01'), ('TIME-OBS', '00:00:00'))) 
    Each reference would replace the other in the rmap.
    Either reference file matching parameters need correction
    or additional matching parameters should be added to the rmap
    to enable CRDS to differentiate between the two files.

**SOLUTION 1:** Generally this means there was an error generating or handling
the reference files and the fix is to sort of the problem and re-submit.

**SOLUTION 2:** Update the rmap to add additional matching parameters so that
CRDS can differentiate between your files.  Resubmit the rmap using the
Submit Mappings page.  Resubmit your reference files.

Equal Weight Match Cases
!!!!!!!!!!!!!!!!!!!!!!!!

When adding files which are characterized as "similar but different",  CRDS can
issue an WARNING like this::

    CRDS - WARNING -  ----------------------------------------
    Match case
     (('DETECTOR', 'FUV'),) 
    is an equal weight special case of
     (('DETECTOR', 'FUV|NUV'),) 
    For some parameter sets, CRDS interprets both matches as equally good.  For
    instance, when reading the web table, some parameter sets will have 'two
    answers' not just the first seen.  This makes CRDS reference assignments hard
    to understand so CRDS for JWST disallows this.  It may indicate a mistake
    characterizing references for CRDS, i.e. one set of files should be
    parameterized differently.  It is POSSIBLE to confirm these files.  However,
    the rmap should be immediately updated to consolidate or separate these
    overlapping cases.  For JWST, it is an error to encounter equal weight cases at
    runtime.  Alternately, cancel the submission and update the reference file
    matching parameters to avoid the conflict.
    ----------------------------------------

Conceptually a CRDS reference file lookup should be a tree descent.  First the
instrument is used to select an imap, then a type keyword is used to select an
rmap within the imap, then matching parameters are used to define categories
(instrument configs) of references in the rmap, and finally a USEAFTER
comparison is used to select the most recent viable reference file for a
specific category.

