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

CRDS is also available for installation as part of AstroConda Contrib:
     `AstroConda Contrib <https://github.com/astroconda/astroconda-contrib>`_.

Basic CRDS Installation
-----------------------

For many applications CRDS is automatically installed as a dependency of the
calibration software.  This default installation supports running calibrations
but not more advanced CRDS activities like submitting files or development. You
can test for the installation of CRDS like this::

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

Full Environment Install
++++++++++++++++++++++++
While the Advanced Installation instructions below detail the installation
of a complete CRDS evironment,  you may find it more convenient to clone
CRDS from github and run the *crds_setup_env* script which performs the same
steps::

  git clone https://github.com/spacetelescope/crds.git
  cd crds
  ./crds_setup_env os-x  # or linux

Accept all default responses to installation script prompts.

Advanced CRDS Installation
--------------------------

Users performing more advanced activities like CRDS file submissions or
development will need additional CRDS dependencies.

Install Conda
+++++++++++++

Typical CRDS installations are based on installing a barebones Miniconda
environment and then adding most packages via pip::

  if [ "$1" == "os-x" ]; then
    export CONDA_INSTALLER=Miniconda3-latest-MacOSX-x86_64.sh
  elif [ "$1" == "linux" ]; then
      export CONDA_INSTALLER=Miniconda3-latest-Linux-x86_64.sh
  else
      echo "usage:  crds_setup_env  [os-x|linux]"
  fi
  echo "Installing $CONDA_INSTALLER"

  rm -rf ~/miniconda3.old
  mv ~/miniconda3 ~/miniconda3.old
  rm -f Miniconda3-latest-*.sh*

  curl https://repo.anaconda.com/miniconda/${CONDA_INSTALLER}  >${CONDA_INSTALLER}
  sh ${CONDA_INSTALLER}
  rm -f ${CONDA_INSTALLER}
  conda update --yes -n base -c  conda

Accept all default responses to the install script's quesions.

Add Astroconda channel
++++++++++++++++++++++
Some CRDS dependencies are only available through the conda channel Astroconda.
Configure the conda environment to use Astroconda::

  conda config --add channels http://ssb.stsci.edu/astroconda

Create crds-env Environment
+++++++++++++++++++++++++++

The CRDS software and basic conda dependencies should be installed in an
isolated conda environment::

  conda create -n crds-env python=3.7
  conda activate crds-env

Add JWST CAL S/W and Dependencies
+++++++++++++++++++++++++++++++++
Installing the JWST CAL S/W will also automatically install many dendencies
of a numerical computing environment::

  pip install numpy
  pip install git+https://github.com/spacetelescope/jwst

Install CRDS and Dependencies
+++++++++++++++++++++++++++++
This sequence first removes the CRDS installed automatically as part of
installing the *jwst* package and then installs the latest available CRDS
from github with advanced dependencies not needed for basic operation::

  pip uninstall --yes crds
  pip install git+https://github.com/spacetelescope/crds.git#egg=crds["submission","test","dev","docs"]
  conda install --yes fitsverify

User's Guide
------------

More documentation about CRDS is available here:

    https://jwst-crds.stsci.edu/static/users_guide/index.html
