# This file defines required environment variables for the CRDS client

# If you don't care too much about CRDS file organization,  use CRDS_PATH
# to define the root of a single tree of CRDS mapping and reference cache files.

# --------------------------------------------------------------------------------------------------------------------
# setenv CRDS_PATH /Users/jmiller/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/crds
# unsetenv CRDS_PATH

# Where reference files are stored,  not necessary except for special cases:
# setenv CRDS_REFPATH  ${CRDS_PATH}/references

# Where mapping files are stored, not necessary except for special cases:
# setenv CRDS_MAPPATH ${CRDS_PATH}/mappings

# Where CRDS server status is stored,  not necessary except for special cases: (should be writeable unless serverless)
# setenv CRDS_CFGPATH ${CRD_PATH}/config

# --------------------------------------------------------------------------------------------------------------------
# The URL used to locate the CRDS server which distributes files, status, and computes best references
# setenv CRDS_SERVER_URL  http://hst-crds.stsci.edu
# setenv CRDS_SERVER_URL  http://jwst-crds.stsci.edu
# setenv CRDS_SERVER_URL  http://crds-non-networked.foo.bar   
setenv CRDS_SERVER_URL  https://hst-crds.stsci.edu
setenv CRDS_PATH ${HOME}/crds_cache_ops
setenv CRDS_READONLY_CACHE 0

# --------------------------------------------------------------------------------------------------------------------
# To override server recommendations for the operational pipeline context (.pmap)
# This override is likewise superceded by the getreferences() function parameter
# which can be used to implement command line overrides in pipeline software.
# setenv CRDS_CONTEXT  jwst.pmap

# --------------------------------------------------------------------------------------------------------------------
# To force where CRDS computes best references,  using local client code,  or server code,
# set CRDS_MODE to "local", "remote", or "auto"
#
#  local  -- CRDS will compute best references using the local installation
#  remote -- CRDS will ask the server to compute best references
#  auto   -- CRDS will only compute best references on the server if the client is deemed obsolete
#            by comparing client and server software versions.   
#
# setenv CRDS_MODE auto

