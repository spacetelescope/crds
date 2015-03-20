"""Common imports and defs across all versions of ACS hooks.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys

from crds import rmap, log, utils, timestamp

from collections import defaultdict

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

