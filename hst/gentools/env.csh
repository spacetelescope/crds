# This file defines required environment variables for the CRDS client

# If you don't care to much about CRDS file organization,  use CRDS_PATH
# to define the root of a single tree of CRDS mapping and reference cache files.

# Set the CRDS_PATH to the package where rmaps are installed for development
setenv CRDS_PATH /Users/jmiller/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/crds
# unsetenv CRDS_PATH

# The URL for the CRDS server used by remote service calls,  
#    .e.g. http://etcbrady.stsci.edu:4997
# setenv CRDS_SERVER_URL  http://etcbrady.stsci.edu:4997    # HST demo
# setenv CRDS_SERVER_URL  http://etcbrady.stsci.edu:4995    # JWST demo
setenv CRDS_SERVER_URL  http://localhost:8000

