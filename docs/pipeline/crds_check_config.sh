#!/bin/bash
# Runs the CRDS list configuration command to dump out key environment variables
# and properties of the current CRDS environment.

crds_env.sh   python -m crds.list --config --readonly-cache $*

