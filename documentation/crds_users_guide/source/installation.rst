Client Installation
===================

In addition to websites, CRDS has client software you can install locally
both as complete programs and as a library you can use in your own scripts.
The client provides tools for downloading rules and reference files,
determining best reference files, updating rules, differencing rules,
checking files, checksumming files, naming files, etc.

While CRDS does have a number of public library calls which can be called from
your own Python scripts, it should currently be viewed more as a system than as
a library, since it includes many active systems (web servers, active database
and shared file system intefaces) in addition to the library discussed here.

The demand for most scriptable interfaces is largely new, so if you have a use
case you'd like to script, don't hesitate to ask for it.

Implicit Installation
---------------------

CRDS is often installed implicitly as a dependency of the HST, JWST and Roman
calibration software.   These basic installations only include sufficient
dependencies to assign best references and fetch them if needed.

To check for CRDS try::

   $ crds list --version
   11.16.7, master, c95d1cc

File Submission Installation
----------------------------

See the CRDS *README.rst* file at github for instructions on more advanced
installations of CRDS.  These give a complete walkthrough for setting up an
environment capable of doing reference file submissions or CRDS development:

`CRDS github`_

.. _`CRDS github`: https://github.com/spacetelescope/crds.git
