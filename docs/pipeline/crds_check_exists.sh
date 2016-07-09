#!/bin/bash
# Verifies the existence and correct length of all rule and reference files in the CRDS cache.

crds_env.sh  cron_sync --all --log-time --check-files --fetch-references --readonly-cache --verbose
