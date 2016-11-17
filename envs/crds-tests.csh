# This environment is used for running unit tests as stand alone modules
# rather than under the control of runtests.

setenv CRDS_SERVER_URL https://hst-crds.stsci.edu

setenv CRDS_TEST_ROOT $HOME

setenv CRDS_PATH ${CRDS_TEST_ROOT}/crds-cache-default-test

setenv CRDS_CACHE_DEFAULT $CRDS_PATH

setenv CRDS_TESTING_CACHE ${CRDS_TEST_ROOT}/crds-cache-test

setenv CRDS_GROUP_CACHE $HOME/crds_cache_ops

