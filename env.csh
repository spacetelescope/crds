# This file defines required environment variables for the CRDS client

# Where you want your CRDS mapping cache to be rooted.   Map files will
# be stored relative to this directory based on a scheme defined in the
# observatory package.  defaults to site-packages/crds/<observatory>
setenv CRDS_MAPPATH /home/jmiller/CRDS/hst/mappings
# unsetenv CRDS_MAPPATH

# Where you want your CRDS reference cache to be rooted.   Reference files
# will be stored relative to this directory based on a scheme defined in the
# observatory package. defaults to site-packages/crds/<observatory>/references
setenv CRDS_REFPATH /home/jmiller/CRDS/hst/references
# unsetenv CRDS_REFPATH

# The URL for the CRDS server used by remote service calls,  
#    .e.g. http://etcbrady.stsci.edu:4997
# setenv CRDS_SERVER_URL  http://etcbrady.stsci.edu:4997
setenv CRDS_SERVER_URL  http://localhost:8000

