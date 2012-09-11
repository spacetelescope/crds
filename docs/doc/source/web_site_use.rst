
Using the CRDS Web Site
=======================

CRDS has websites at hst-crds_ and jwst-crds_ which support the submission, use,
and distribution of CRDS reference and mappings files.   Functions on the CRDS
website are either public functions which do not require authentication or private
functions which require a CRDS login account.

.. _crds-hst: http://hst-crds.stsci.edu/
.. _crds-jwst: http://jwst-crds.stsci.edu/

Functions annotated with the word (alpha) are partially completed components of
a future build which may prove useful now.

Public Functions
----------------

The following functions are available for anyone with access to the CRDS web
server and basically serve to distribute information about CRDS files and
recommendations.   

Dataset Best References (alpha)
...............................

The *Dataset Best References* page supports determining the best references for
a single dataset with respect to one CRDS context.   Best references are based 
upon a CRDS context and the parameters of the dataset.

Context
+++++++

The context defines the versions set of CRDS rules used to select best references.
*Edit* is the default context from which most newly created contexts are derived.  
*Operational* is the context currently in use by the pipeline.   *Recent* shows
the most recent contexts.   *User Specified* enables the submitter to type in the
name of any other known context.

Dataset
+++++++

Upload FITS header
!!!!!!!!!!!!!!!!!!

Browser-side code can extract the FITS header of a dataset and upload it to the
server where best references are computed based on dataset parameters.   This
function is implemented in Javascript and reliant on HTML5;  it supports only
parameters present in the FITS primary header.   It avoids uploading most of the
dataset.   It is known to work in Firefox and Chrome but not IE or Safari-5.
  
Upload Dataset
!!!!!!!!!!!!!!

A user's dataset can be uploaded to the server for best references evaluation.

Archived Dataset
!!!!!!!!!!!!!!!!

Datasets can be specified by ID and their best reference input parameters will 
be retrieved from the catalog.

Explore Best References (alpha)
...............................

Explore Best References supports entering best references parameters directly
rather than extracting them from a dataset or catalog.   The first phase of 
exploration is to choose an instrument.   The second phase is to enter the
parameters of a dataset which are relevant to best references selection.  The explorer
currently lists all parameters which might be relevant to any mode of an instrument
and has no knowledge of default values.

Difference Files
................

Difference Files can be used to compare two reference or mapping files.   Either
the name of a file already in CRDS can be specified (known) or any file can be
uploaded via the web (uploaded).


Browse Database
...............

Recent Activity
...............


Private Functions
-----------------

The following functions are restricted to users with accounts on the CRDS website
and support the submission of new reference and mapping files and maintenance
of the overall site.

Certify File
............

Batch Submit References
.......................

Edit Rmap
.........

Submit References
.................

Submit Mappings
...............

Create Contexts
...............


Set File Enable
...............

Set Default Context
...................

Server Version Info
...................

Server Admin
............

