====
CRDS
====

CRDS is a package used for working with astronomical reference files for the
HST and JWST telescopes.  CRDS is useful for performing various operations on
reference files or reference file assignment rules.  CRDS is used to assign,
check, and compare reference files and rules, and also to predict those
datasets which should potentially be reprocessed due to changes in reference
files or assignment rules.  CRDS has versioned rules which define the
assignment of references for each type and instrument configuration.  CRDS has
web sites corresponding to each project (http://hst-crds.stsci.edu or
https://jwst-crds.stsci.edu/) which record information about reference files
and provide related services.

CRDS development is occuring at:
     `Project's github page <https://github.com/spacetelescope/crds>`_.

CRDS is also available for installation as part of ``stenv``:
     `stenv <https://github.com/spacetelescope/stenv>`_.

Basic CRDS Installation
-----------------------

For many roles, CRDS is *automatically installed as a dependency* of the
calibration software.  This default installation supports running calibrations
but not more advanced CRDS activities like submitting files or development.

You can test for an existing installation of CRDS like this::

  $ crds list --status
  CRDS Version = '7.4.0, b7.4.0, daf308e24c8dd37e70c89012e464058861417245'
  CRDS_MODE = 'auto'
  CRDS_PATH = 'undefined'
  CRDS_SERVER_URL = 'undefined'
  Cache Locking = 'enabled, multiprocessing'
  Effective Context = 'jwst_0541.pmap'
  Last Synced = '2019-08-26 07:30:09.254136'
  Python Executable = '/Users/homer/miniconda3/envs/crds-env/bin/python'
  Python Version = '3.7.4.final.0'
  Readonly Cache = False

This output indicates CRDS is installed and configured for processing onsite
using a pre-built cache of CRDS rules and references at */grp/crds/cache*.

File Submission Installation
----------------------------

For performing the file submission role,  CRDS includes additional dependencies
and can be trickier to install.

Addding CRDS to an Existing Environment
+++++++++++++++++++++++++++++++++++++++

You can install/upgrade CRDS and it's dependencies in your current environment
like this::

  git clone https://github.com/spacetelescope/crds.git
  cd crds
  ./crds_setup_crds

It is recommended that you only do this in an environment dedicated to file
submissions.   This may be suitable for e.g. installing/upgrading CRDS in
an active *redcatconda* environment.

Full Environment Install
++++++++++++++++++++++++

Sometimes it's expedient to install an entirely new environment including a
baseline conda,  CRDS,  and all of it's dependencies.  To start from scratch,
you can::

  git clone https://github.com/spacetelescope/crds.git
  cd crds
  ./crds_setup_all

  # open a new terminal window
  conda activate crds-env

To customize a bit more, *crds_setup_all* and *crds_setup_env* support
parameters which can be used to specify OS, shell, and install location.
Substitute the below to specify Linux, c-shell, and a non-default install
location::

  ./crds_setup_all   Linux  csh   $HOME/miniconda_crds

Advanced Install
++++++++++++++++

Below are the current sub-tasks used conceptually for a full featured CRDS
install.    These can serve as an alternative to cloning the CRDS repo and
running the install script(s).  If you already have a python environment
supporting pip,

1. Installing Conda / Astroconda
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Alternate / definitive installation instructions for installing a baseline conda
can be found here::

  https://spacetelescope.github.io/training-library/computer_setup.html#installing-conda

2. Create crds-env Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The CRDS software and basic conda dependencies should be installed in an
isolated conda environment::

  conda create -n crds-env
  conda activate crds-env

You can substitute the environment name of your choice, e.g. *redcatconda* vs. *crds-env*.

3. Add JWST CAL S/W and Dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Installing the JWST CAL S/W will also automatically install many dendencies of
a numerical computing environment::

  pip install --upgrade numpy
  pip install --upgrade git+https://github.com/spacetelescope/jwst

Note that these commands also install the latest version of CRDS from pip which
may not be current enough for ongoing reference file testing and
troubleshooting.

4. Install CRDS and Dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This sequence first removes the CRDS installed automatically as part of
installing the *jwst* package and then installs the latest available CRDS
from github with advanced dependencies not needed for basic operation::

  pip uninstall --yes crds
  pip install --upgrade  git+https://github.com/spacetelescope/crds.git#egg=crds["submission","test"]

A more full featured CRDS install is::

  pip install --upgrade  git+https://github.com/spacetelescope/crds.git#egg=crds["submission","dev","test","docs"]

5. Install Fitsverify
^^^^^^^^^^^^^^^^^^^^^

Since it is a C-based package fitsverify is not available using pip but is
available via conda on the astroconda channel::

  conda config --add channels http://ssb.stsci.edu/astroconda
  conda install --yes fitsverify

As part of an end-user setup installation of fitsverify is optional, CRDS
certify will run without it after issuing a warning, the CRDS server will run
fitsverify as part of its checks unless/until we stop using it altogether.

User's Guide
------------

More documentation about CRDS is available here:

    https://jwst-crds.stsci.edu/static/users_guide/index.html
