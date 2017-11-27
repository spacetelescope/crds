Installation
============

Implicit Installation
---------------------

CRDS is installed implicitly with the conda installation of HST or JWST calibration software.

To check for CRDS try::

   $ crds list --version
   7.0.5, master, c95d1cc

If CRDS is not already installed,  it can be installed using in a variety of mechanisms including AstroConda 
contrib, PyPi, and GitHub source code.   

Installation via AstroConda
---------------------------

One way to install CRDS directly is as an AstroConda contributed package:

1.  Install Continuum's Anaconda or Miniconda

Installing Anaconda gives you a generic environment for numerical programming.  See:

   https://www.continuum.io/downloads

for Anaconda installation instructions.

2. Set up AstroConda astronomy specific packages

AstroConda is a collaborative effort producing astronomy related packages and making
them available for installation via Conda.

   http://astroconda.readthedocs.io/en/latest/installation.html

Nominally,  setting up AstroConda is something like::

   $ conda config --add channels http://ssb.stsci.edu/astroconda
   $ conda create -n astroconda stsci
   $ source activate astroconda

Pip Installation
----------------

It's also possible to install and update CRDS using PyPi system like this::

   $ pip install crds

Installing CRDS via Conda is preferred.

Installing from Source
----------------------

CRDS source code can be cloned from the GitHub source code repository as follows::

  $ git clone https://github.com/spacetelescope/crds.git CRDS
  $ cd CRDS

  $ # optionally,  switch to release tag
  $ git fetch origin
  $ git checkout <release tag,  e.g. 6.0.1>

Run the ./install script in the root source code directory to install from source code::

    $ cd CRDS
    $ ./install
    final status 000000

Dependencies
------------

CRDS was developed in and for an STSCI Python environment suitable for pipeline
processing.   Standard STScI calibration environments should already include it.
Nevertheless, for installing CRDS independently, these dependencies are applicable:

REQUIRED: CRDS requires these dependencies to be installed in your Python environment:
   * numpy
   * astropy

OPTIONAL: Additional 3rd party supporting packages are needed for more advanced CRDS functions:

.. table:: Optional Supporting Packages
    :widths: auto
    
    ===============    =======================================================================
    Package            Supports Task
    ===============    =======================================================================
    jwst               to run crds certify for JWST
    firelock           for lock file based CRDS cache locking for multiprocessing (preferred)
    lockfile           for lock file based CRDS cache locking for multiprocessing (deprecated)
    fitsverify         for running fitsverify under certify
    lxml               for command line submission interface
    requests           for command line submission interface
    Parsley-1.3        for certifying CRDS rules files
    pyaml              for certifying and using yaml references
    asdf               for certifying and using ASDF references
    docutils           for building documentation
    sphinx             for building documentation
    stsci.sphinxext    for building documentation
    nose               for running CRDS unit tests
    ===============    =======================================================================


