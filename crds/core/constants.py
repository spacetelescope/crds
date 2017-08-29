from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

# ============================================================================

# List of all the observatory package names
ALL_OBSERVATORIES = ["hst", "jwst", "tobs"]

# keywords used to identify instrument from headers
INSTRUMENT_KEYWORDS = ["INSTRUME", "META.INSTRUMENT.NAME",
                       "META_INSTRUMENT_NAME", "INSTRUMENT", 
                       "META.INSTRUMENT.TYPE", "META_INSTRUMENT_TYPE"]

