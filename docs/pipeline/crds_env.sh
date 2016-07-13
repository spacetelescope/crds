#!/bin/bash
#=========================================================================
#
# crds_env.sh
#   From crds_sync_cache.sh
#
# Invoke the command specified on the command line in the pipeline environment
# using additional environment settings required to run SSB code and CRDS tools.
#
# Usage:  crds_env.sh <command and parameters to execute in SSB environment.>
#
#=========================================================================

umask 2   # Set default file permissions for created files to exclude only "other" write.

# not capturing output; it will all go to stdout/stderr (to the screen)
tstamp=( eval "date '+%Y%j%H%M%S'" )
echo "$("${tstamp[@]}")-I-INFO- $0 Started"

# Active anaconda
PATH=${PATH}:${CONDA_BASEDIR}/bin
echo "activating SSB anaconda... for CONDA_RELEASE ${CONDA_RELEASE} "
source activate ${CONDA_RELEASE}

# setup the CRDS-provided utility
# build the call to the CRDS-provided utility with appropriate parameters

# call the CRDS-provided utility to synchronize the local CRDS online pipeline
# cache ($CRDS_PATH) with the CRDS server ($CRDS_SERVER_URL)
# XXXXXX run the command...
$*
# XXXXXX
cmd_status=$?
if [[ $cmd_status -ne 0 ]]; then
    echo "$("${tstamp[@]}")-E-ERROR ${the_executable} returned non-0 exit status ($cmd_status)"
fi
exit $cmd_status

