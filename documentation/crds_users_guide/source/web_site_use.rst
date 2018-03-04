
Using the CRDS Web Site
=======================

CRDS has websites at hst-crds.stsci.edu_ and jwst-crds.stsci.edu_ which support the submission, use,
and distribution of CRDS reference and mappings files.   Functions on the CRDS
website are either public functions which do not require authentication or private
functions which require a CRDS login account.

.. _hst-crds.stsci.edu: http://hst-crds.stsci.edu/
.. _jwst-crds.stsci.edu: http://jwst-crds.stsci.edu/

.. figure:: images/web_index.png
   :scale: 50 %
   :alt: home page of CRDS website

Functions annotated with the word (alpha) are partially completed components of
a future build which may prove useful now.

Operational References
----------------------

The *Operational References* table displays the references which are currently in use
by the pipeline associated with this web site.   

Each instrument accordion opens into reference type accordions for that instrument.

Each reference type accordion opens into a table of reference files.

In general,  links to files will either lead to the CRDS catalog details about that
file or to a context display for a different .pmap.

Context History (more)
----------------------

The *Context History* displays the last 4 CRDS contexts which were in operational use by
the pipeline. Clicking on the *(more)* link will bring up the entire context history as 
a separate page as shown below:

.. figure:: images/web_context_history.png
   :scale: 50 %
   :alt: History of CRDS operational contexts
   
Click the *diff* check box for any two contexts in the history and then click the diff button
at the top of the diff column:

.. figure:: images/web_context_diff_1.png
   :scale: 50 %
   :alt: CRDS context diff request

This will display a difference page with an accorion panel for each file which
differed between the two contexts:
    
.. figure:: images/web_context_diff_2.png
   :scale: 50 %
   :alt: CRDS context diff request

Each file accordion opens into two accordions which alternately display logical and simple 
textual differences.

The logical differences display a table of matching parameters and files which were added, 
deleted, or replaced.   The textual differences show raw UNIX diffs of the
two rules files.

Clicking on any *context* link (the .pmap name) in the history table opens a page containing 
the Historical References for some point in the past,  similar to the Operational References display:

.. figure:: images/web_context_table.png
   :scale: 50 %
   :alt: CRDS historical references display


Open Services
-------------

The following functions are available for anyone with access to the CRDS web
server and basically serve to distribute information about CRDS files and
recommendations.   Initially,  the CRDS sites are only visible within the Institute.

Dataset Best References
.......................

The *Dataset Best References* page supports determining the best references for
a single dataset with respect to one CRDS context.   Best references are based 
upon a CRDS context and the parameters of the dataset as determined by the 
dataset file itself or a database catalog entry.

.. figure:: images/web_dataset_bestrefs.png
   :scale: 50 %
   :alt: dataset based best references input page

Context
+++++++

The context defines the set of CRDS rules used to select best references.
*Edit* is the default context from which most newly created contexts are derived.  
*Operational* is the context currently in use by the pipeline.   *Recent* shows
the most recently created contexts.   *User Specified* enables the submitter to 
type in the name of any other known context.

Dataset
+++++++

Upload FITS header
!!!!!!!!!!!!!!!!!!

Browser-side code can extract the FITS header of a dataset and upload it to the
server where best references are computed based on dataset parameters.   This
function is implemented in Javascript and reliant on HTML5;  it supports only
parameters present in the FITS primary header.   It avoids uploading most of the
dataset.   It is known to work in Firefox and Chrome but not IE or Safari-5.
  
Archived Dataset
!!!!!!!!!!!!!!!!

Datasets can be specified by ID and their best reference input parameters will 
be retrieved from the catalog.

Dataset Best References Results
+++++++++++++++++++++++++++++++

.. figure:: images/web_dataset_bestrefs_results.png
   :scale: 50 %
   :alt: dataset based best references results page
   
The results page for dataset best references displays the input parameters which
were extracted from the dataset header on the right side of the page.

Best reference recommendations are displayed on the left side of the page.


Explore Best References
.......................

Explore best references is a sand box that enables evaluating what CRDS will do
given hand picked parameter values.  Explore Best References supports entering
best references parameters directly via menus or write-in text boxes rather
than extracting them from a dataset or catalog.

The first phase of exploration is to choose a pipeline context and instrument
which will be used to define menu driven parameter choices:   

.. figure:: images/web_explore_bestrefs.png
   :scale: 50 %
   :alt: user input based best references

The second phase is to enter the parameters of a dataset which are relevant 
to best references selection.  

.. figure:: images/web_explore_bestrefs_parameters.png
   :scale: 50 %
   :alt: user input based best references

The parameter menus are driven by CRDS rules and do not capture every possible
parameter value.  Text box inputs augment and override the menu inputs to
support entering parameter values not listed in the menus.

The entered parameters are evaluated with respect to the given pipeline context
and best references are determined.   The results are similar or identical to
the *Dataset Best References* results.

Browse Database
...............

The *Browse Database* feature enables examining the metadata and properties of
CRDS reference and mapping files.

.. figure:: images/web_browse_database.png
   :scale: 50 %
   :alt: database browse filter page

The first phase selects and filters files for top level display, one file per
table row.  Leave filter settings as \* to skip that constraint.

.. figure:: images/web_browse_database_files.png
   :scale: 50 %
   :alt: database browse filter page

All file details for a single file can be displayed by clicking the filename
link in the tabular display.
         
.. figure:: images/web_browse_database_details.png
   :scale: 50 %
   :alt: database browse details page
   
The file details page has a number of accordion panes which open when you
click on them.  All file types have these generic panes:

- Database - lists a table of CRDS metadata for the file.

- Contents - shows the text of a mapping or internal details about a reference file.

- Past Actions  - lists website actions which affected this file.

- Used By Files - list known CRDS files which reference this file.

Reference files have these additional panes:

- Lookup Patterns - lists the parameters sets which lead to this reference.

Recent Activity
...............

The *Recent Activity* view shows a table of the tracked actions on CRDS files:

.. figure:: images/web_recent_activity.png
   :scale: 50 %
   :alt: database browse details page
   
The first page lists a number of constraints which can be used to choose
activities of interest.   To ignore any constraint,  leave it set at the default
value of \*.   The result of the activity search is a table of matching actions:

.. figure:: images/web_recent_activity_results.png
   :scale: 50 %
   :alt: database browse details page
   
The default filter of \*.pmap previews contexts that have been submitted but
not yet selected for operational use in the pipeline.

Private Functions
-----------------

The following functions are restricted to authenicated users:

- file submissions
- context selection
  
Login and Instrument Locking
............................

File submissions require locking an instrument to prevent multiple submitters
from accidentally submitting the same files and/or simultaneously modifying the
same .rmap:

.. figure:: images/web_login.png
   :scale: 50 %
   :alt: login page with instrument locking

When a user logs in,  the instrument they've locked and the time remaining on the 
lock are displayed below the login (now logout) button:

.. figure:: images/web_logged_in.png
   :scale: 50 %
   :alt: logged in page with count down timer

The time displayed is the relative time remaining on the lock reservation,  nominally
around 4 hours.

When the user performs an action on the website,  their lock timer is reset to its maximum value.

Other users who attempt to login for the same instrument while it is locked
will be denied.

When a file submission is being performed,  it must be *confirmed* within the timeout period.  If
the lock times out,  the submission is not cancelled,  but other team members have the option to 
take the lock and then cancel or force the submission.   Forced submissions should be carefully
coordinated since by definition locking protections are not in place.

After a submission is cancelled, confirmed, or dropped,  the user's lock is also dropped.

Care should be taken with the locking mechanism and file submissions.  **DO NOT**:

* Don't login from multiple browsers or sites.   The last browser/site you log in from will steal the
  lock from the original login, cancel any original file submission,  and force a logout in the original browser.

* Don't leave the page during an ongoing file submission,  wait for it to finish.   Opening other browser
  tabs should be fine.

* Don't attempt to login for more than one instrument at a time.  One user is assigned one and only one lock.

* Don't attempt to perform multiple file submissions for the same instrument at the same time.  Finish
  and confirm or cancel each file submission before proceeding with the next.

Certify Files
.............

*Certify File* runs crds.certify on the files in the ingest directory.

.. figure:: images/web_certify_file.png
   :scale: 50 %
   :alt: certify file inputs
   
If the certified file is a reference table,  the specified context is used to
locate a comparison file. 


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

Set Context
...........

*Set Context* enables setting the operational, edit, and versions contexts.  

.. figure:: images/web_set_context.png
   :scale: 50 %
   :alt: set context inputs

CRDS enables contexts to be distributed before their adoption as the pipeline default.
Set Context is used to select the default pipeline (operational) context.
   
Setting the operational context changes state on the CRDS server which must be
subsequently sync'ed to remote pipelines and users.

Setting the *operational* context creates a new entry at the top of the Context
History.

Setting the *edit* context sets the default starting point for future file
submissions.

Setting the *versions* context defines the context used to locate the SYSTEM
CALVER reference file used to define calibration software component versions.

Batch Submit References
.......................

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

  % scp /this_delivery/*.fits   dmsinsvm.stsci.edu:/ifs/crds/hst/ops/server_files/ingest/<username>

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

Edit Context is the default context used for editing.   Whenever a new .pmap is created or
added,  it becomes the editing context from which other .pmaps are derived by
default.

Operational Context
!!!!!!!!!!!!!!!!!!!

Operational Context is the .pmap which is nominally in use by
the pipeline.  Generally speaking,  multiple contexts might be added to CRDS as
the Edit Context long before they become operational.   

Recent 
!!!!!!

Recent lists a number of recently added contexts based on delivery time.   

User Specified
!!!!!!!!!!!!!!

Any valid CRDS context can be typed in directly as User Specified.
   
Auto Rename
+++++++++++

Normally files uploaded to CRDS will be assigned new unique names.   During side-by-side
testing with CDBS,  *Auto Rename* can be deselected so that new files added to CRDS
retain their CDBS names for easier comparison.  The CRDS database remembers both
the name of the file the submitter uploaded as well as the new unique name.
   
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

* *Actions on Rmap* provides two accordions showing how the rmap controlling the submitted references was modified.   The logical differences accordion has a table of actions,  either *insert* for completely new files or *replace* for files which replaced an existing file.   The text differences are essentially output from UNIX *diff* for the old and new rmaps.

* *Certify Results* has an accordion panel for each submitted reference file which contains the results from crds.certify.   The submitted name of each file is listed first,  followed by any official name of the file assigned by CRDS.   The status of the certification can be "OK" or "Warnings".   Warnings should be reviewed by opening the accorion panel.
   
**IMPORTANT**  The results page only indicates the files which will be added to
CRDS if the submission is *confirmed*.   Prior to confirmation of the submission,
neither the submitted references nor the generated mappings are officially in CRDS.
Do not *leave the confirmation page* prior to confirming.

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

Submit References
.................

*Submit References* provides a lower level interface for submitting a list of 
references.   No mappings are generated to refer to the submitted files.
Submitted references must still pass through crds.certify.

.. figure:: images/web_submit_references.png
   :scale: 50 %
   :alt: create contexts inputs

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

