Package Overview
================

Currently the CRDS (Calibration Reference Data System) is a collection
of web servers and a client library that manages calibration reference
files (e.g. darks, biases) for HST and JWST.   Relative to its predecessor
CDBS,  the scope of CRDS is considerably broader.

Primary Function:  Reference File Assignment

--------------------------------------------

Like it's predecessor, the primary function of CRDS is to assign the
appropriate reference files to datasets so that they can be
calibrated.  Datasets are assigned based on properties of the
reference files (nominally instrument configurations for which they
were created as well as when they were created) and properties of the
datasets (nominally how an instrument was configured and when
observations were taken.)

For each instrument, there are many types of reference files. The
approach of CDBS was to represent reference file properties in a
database, with one or more tables per instrument.  The reference file
database was matched against either a science exposure database or
dataset file headers to choose appropriate references.  Complex
dynamically constructed SQL queries were used to choose appropriate
reference files.  Every rules file is retained in perpetuity.

In CRDS, the reference file database is replaced with a nested
hierarchy of explicitly versioned rules files. The CRDS rules files,
often referred to as mappings, are encoded as plain text with file
names that include decimal version numbers.  The rules comprise a tree
with 3 tiers: the entire telescope, each instrument, and every
reference type for each instrument.  At any given time, there are
roughly 120 files describing the state of the system.

The two major benefits of CRDS relative to CDBS are:

1. Because CRDS rules are explicitly versioned, the results produced
by CRDS at any given point in time are reproduceable.  In contrast,
the CDBS database was a single state system, effectively a one way
trap door, so as new references arrived CDBS lost the capability of
reproducing past results.

2. Because CRDS rules are encoded as plain text specifications, they
are more transparent to human readers. User's can merely glance at the
rules files, or more generally, glance at the re-rendering of the
rules files on the CRDS web servers.

An important if obvious point to make is that the sets of calibration
rules and references, as well as file checking constraints, are unique
to each supported project.


Common Secondary Functions (Reference Ingest, Certification, File Tracking, Archiving)

--------------------------------------------------------------------------------------

Reference Ingest

++++++++++++++++

For both CRDS and CDBS, an important secondary function is to support
adding new references to the system and archive.  CDBS was based on a
series of command line scripts used to ingest files.  CRDS is based on
web servers that support uploading files.  One challenge of the web
interface is the sheer size of file deliveries, at times requiring
support for dozens or hundreds of files and 10's of gigabytes of data.

File Certification

++++++++++++++++++

In both systems, a certifier program is used to check basic properties
of incoming files to verify that they will be correctly assigned and
contain no obvious mistakes or omissions.  

File Tracking

+++++++++++++

Each system adds incoming files to the gestalt of information that is
tracked.  In CDBS this meant adding files to the reference file
database that tracked both file metadata and assignment criteria. In
CRDS this means incrementally generating a new version of rules files
as well as adding select information to a smaller metadata-only
database.  Once in CRDS, files don't change, they are tracked
bit-for-bit with checksums to ensure repeatability and exposed only
through personal downloads or readonly caches.

Archive Submission

++++++++++++++++++

Once files have been delivered, checked, and added to the assignment
and tracking systems, both CDBS (now retired) and CRDS pass the files
along to downstream archive systems.  An extended chain of systems is
involved but the immediate CRDS delivery interface is known as the
"CRDS pipeline."   The CRDS pipeline is typically left running but
can be started/stopped by pipeline operators manually.

New Features of CRDS (Controlled state transistions, history, file distribution, reprocessing, web services, web displays, differencing)

----------------------------------------------------------------------------------------

File Distribution (cache sync)

+++++++++++++++++++++++++++++

One of the new features of CRDS is provision for the download and
management of rules and reference files.  Aside from exposing
individual files using simple web links, CRDS distribution support
enables demand based downloads appropriate for individual researchers,
as well as complete system downloads appropriate for archive
pipelines.  Because CRDS file sets are explicitly defined by versioned
rules, the CRDS distribution tools can manage a cache of rules and
references that is limited in applicability either to particular
datasets or complete versions of rules.

Distributed files are cached by client systems and so in principle are
downloaded only once.  For the single researcher use case, small sets
of applicable files can be dynamically downloaded as they are defined
or updated by CRDS.  For the pipeline use case, the pipeline's CRDS
cache can be updated with the complete of available references. This
scheme works without the need for the replication of, distribution of,
or authenticated connection to a database.  Although the JWST archive
interface continues to support an intuitive shopping cart design, the
CRDS scheme supports automatic incremental updates and obviates the to
construct tarballs that are effectively unbounded in size.

Pipeline cache synchronization is managed by a CRDS "sync" tool which
is further wrapped by shellscript that handles pipeline concurrency
issues.  It is possible to update the pipeline's CRDS cache in parallel
with pipeline processing of multiple concurrent jobs.

End user on-demand cache synchronization is performed either by the
CRDS bestrefs tool (HST) or by built-in features of the JWST
calibration software.

Once a file cache is established, repeat calibrations can be performed
without additional downloads, with or without a connection to the CRDS
server.  This is particularly important for pipelines, enabling them
to run disconnected from and unaffected by the diverse loads and
public exposure of the CRDS servers.

On site, users and system test efforts typically refer to shared
readonly CRDS caches that are pre-synced with all available files.
Hence, for a majority of users, visible cache syncs never occur.
Pipelines are a clear exception where carefully controlled updates are
a very explicit team process, first distributing and pre-positioning
new files, next actively selecting them for use in a well controlled
way.

Controlled State Transitions (Set Context)

++++++++++++++++++++++++++++++++++++++++++

CRDS state transitions are coordinated by pipeline operators who
manually choose when new reference files and rules become active in
the pipeline by default.  This selection is tracked on the server and
automatically made available to all CRDS users.  These official
transitions can include seamless reversions to prior sets of rules in
the event of failures.  Developers have the capability to override the
set of files they use personally enabling multiple teams to use
different versions of files tracked by the same server.

Context History

+++++++++++++++

CRDS maintains a visible record of every file delivery on the web
site.  CRDS tracks the exact time at which the archive pipeline adopts
new references in a history that is visible on the web site and
accessible via a web service.  Changes can include the addition of new
files as well as adjustments, fixes, and new reference types.


Reprocessing Support

++++++++++++++++++++

One of the new features of CRDS is the ability to recommend the set of
datasets that are candidates for reprocessing based on newly delivered
references.  Determining the limited set of affected datasets enables
a change in system-wide processing strategy, a switch from OTFR (On
the fly reprocessing) to preemptive reprocessing.  Early reprocessing
eliminates delays in delivering freshly calibrated data to end users;
since CRDS generally identifies a reduced set of affected data, it
becomes practical to reprocess all of it prior to user requests.

CRDS computes affected datasets by accessing the science exposure
databases, running relevant parameter sets through past and present
CRDS rules, and indentifying differences in assigned references.   Those
datasets for which reference files change become candidates for reprocessing.

Unlike many systems, despite its complexity the CRDS reprocessing
system is fully autonomous, triggered by the pipeline operator's
activation of a new set of rules.  As rules are updated, the required
CRDS computation occurs, the results are captured permanently and
distributed to the pipeline and remote institutions.


Web Services

++++++++++++

The CRDS servers provide a variety of web services via JSONRPC interfaces.


Web Displays

++++++++++++

The CRDS web servers provide an accurate rendition of the current and
past file assignment criteria in a tabular format.  While it looks
obvious, the thing of note is that such a system simply did not exist
with CDBS, and it's clear that human maintained tables, while
potentially adding more subjective content, become obsolete as formal
systems almost overnight.  In contrast CRDS is entirely self-maintaining.

As part of maintaining versioned rules,  CRDS also provides tracks and 
displays a history of how the rules are changing.   The web display is
automatically updated and display and provides a record of development
and routine updates alike.

The CRDS servers can display detailed metadata and other information
relevant to individual files.   This is essentially a catalog display
augmented with other computable file properties.


State Differencing

++++++++++++++++++

Since CRDS has versioned rules, it also has developed tools for
comparing them and summarizing the differences.  This makes precise
technical descriptions of ongoing changes possible.  Aribtrary context
differences are supported, as well as recursive differences associated
with file replacements.  CRDS has table differencing tools that were,
at least initially, not available elsewere.
