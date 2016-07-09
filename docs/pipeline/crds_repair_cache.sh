#!/bin/bash
#
# Corrects a CRDS cache for bad rules or references,  only reference length is checked
# unless the --check-sha1sum parameter is added on the command line.
#
# --check-sha1sum is definitive but slow and resource intensive.
#
# This is particularly applicable after mirroring the OPS server down to TEST at
# the start of a new test cycle;  there's a fair chance it will correct CRDS rules files
# which have the same names but different contents between TEST and OPS.   Once
# mirrored,  only the CRDS servers are identical,  past pipeline syncs must also be
# corrected as the distributed tail end of mirroring.
#
crds_env.sh crds_repair_cache --all $* 

