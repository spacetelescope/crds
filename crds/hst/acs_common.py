"""Common imports and defs across all versions of ACS hooks.
"""
import sys
from collections import defaultdict

from crds.core import rmap, log, utils, timestamp

# ===========================================================================

#   This section contains matching customizations.

ACS_HALF_CHIP_COLS = 2048         #used in custom bias selection algorithm

SM4 = timestamp.reformat_date("2009-05-14 00:00:00.000000")
# date beyond which an exposure was
# taken in the SM4 configuration
# (day 2009.134 = May 14 2009,
#  after HST was captured by
#  the shuttle during SM4, and
#  pre-SM4 exposures had ceased)
