import os
import os.path

import crds

try:
    CRDS_ROOT = os.environ["CRDS"]
except:
    CRDS_ROOT = os.path.dirname(crds.__file__) or "./"

