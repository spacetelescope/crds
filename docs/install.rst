Installation for someone with sh access (e.g. Linux) should be simple:

% tar zxf crds-1.0.tar.gz
% cd crds-1.0
% python setup.py install

will install the CRDS library and starter HST and JWST rules (rmaps).

Onsite at STScI,  basic checkout of the CRDS client/library can be accomplished by:

% source envs/hst-crds-dev.csh
% ./runtests

Running ./runtests requires the CRDS dev server at https://hst-crds-dev.stsci.edu.

