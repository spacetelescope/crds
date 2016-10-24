
Welcome
=======

Welcome to the Calibration and Reference Data System (CRDS).   CRDS manages
the reference files and the rules which are used to assign appropriate
references to particular data sets.   CRDS has a variety of aspects:

   * CRDS is a Python package usable within the context of the STSCI
     Python environment.   The core library can be used without network
     access.
   * CRDS has an interactive web server which assists with the
     creation and submission of "official" reference files and CRDS
     mappings (rules).   CRDS has a database which tracks delivery 
     metadata for references and mappings.
   * The CRDS web server also provides network services via JSONRPC
     related to best reference determination.
   * CRDS has a Python client package which accesses the network
     services to determine and locally cache the best references
     for a dataset.

