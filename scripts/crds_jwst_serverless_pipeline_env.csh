#
# The settings below should be "sourced" into any shell used to run JWST
# calibration Steps or Pipelines.  These settings ensure that the pipeline
# operates in a serverless mode which is decoupled from the CRDS server and
# relies only on cached CRDS configuration, rules, and references.   These
# settings are intended to be used in conjunction with the "cron_sync"
# CRDS pipeline cache synchronization script.
#
# In addition to the environment defined below,  the pipeline must set
# the location of the pipeline's CRDS cache for JWST by defining the
# environment variable CRDS_PATH.
#

# Prevent calibration code from interacting with the CRDS server,  magic name defines web failures as expected.
setenv CRDS_SERVER_URL https://jwst-serverless-mode.stsci.edu

# Define the default observatory for the pipeline.
setenv CRDS_OBSERVATORY jwst

# Prohibit pipeline steps from modifying the CRDS cache,  only cron_sync should.
setenv CRDS_READONLY_CACHE 1

# Add timestamps to CRDS log messages
setenv CRDS_LOG_TIME 1

# Number of times to try again for CRDS client network fails: 1 == 1 try, no retries.
setenv CRDS_CLIENT_RETRY_COUNT 1

# Seconds to wait between retries,  no wait.
setenv CRDS_CLIENT_RETRY_DELAY_SECONDS 0

