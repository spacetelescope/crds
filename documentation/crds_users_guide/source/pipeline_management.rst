Pipeline Management
===================

This section discusses CRDS activities relevant to DMS pipeline operators.

Operator Overview
.................

When new reference files are delivered,  CRDS requires the following DMS
operator work flow:

Run DMS CRDS poller
+++++++++++++++++++

When new references are delivered to CRDS, a DMS operator runs the "CRDS
poller" to copy files from a CRDS server delivery directory into the archive.
This is done by running a DMS script

Wait for Checkout
+++++++++++++++++

Once new CRDS files are archived, there is a chance for INS to preview files
exactly as they will run in the pipeline by calibrating relative to the CRDS
"edit" context.  The "edit" context tracks CRDS files which are not yet
operational, i.e. it tracks the (default) context into which new files are
added rather than the context which is being used for pipeline calibrations.
At this stage the DMS operator is waiting for authorization to update CRDS and
the pipeline.

Set (Default CRDS) Context
++++++++++++++++++++++++++

When an instrument team is satisfied that new references are working as
intended within CRDS, they request a DMS operator to update the default /
"operational" CRDS context by using the CRDS server *Set Context* page
described below.

Sync Pipeline CRDS Cache
++++++++++++++++++++++++

CRDS Server Repro Runs
++++++++++++++++++++++

When the operator updates the default CRDS context, a CRDS server cron
job will notice and determine if any data should be reprocesssed.  When
the cron job is complete, the CRDS server issues a descriptive e

Set Context
...........

*Set Context* enables setting the operational, edit, and versions contexts.  

.. figure:: images/web_set_context.png
   :scale: 50 %
   :alt: set context inputs

CRDS enables contexts to be distributed before their adoption as the pipeline
default.  Set Context is used to select the default pipeline (operational)
context.
   
Setting the operational context changes state on the CRDS server which must be
subsequently sync'ed to remote pipelines and users.

Setting the *operational* context creates a new entry at the top of the Context
History.

Setting the *edit* context sets the default starting point for future file
submissions.

Setting the *versions* context defines the context used to locate the SYSTEM
CALVER reference file used to define calibration software component versions.

