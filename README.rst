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


Installing
----------

For developers:

    % git clone https://github.com/spacetelescope/crds.git CRDS
 
    % cd CRDS
 
    % ./install

or if you have AstroConda Contrib set up:

   % conda install crds

or as a last resort (tends to be dated):

   % pip install crds

User's Guide
------------

More documentation about CRDS is available here:

    https://jwst-crds.stsci.edu/static/users_guide/index.html

