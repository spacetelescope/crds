from __future__ import division # confidence high
from __future__ import with_statement
from __future__ import print_function
from __future__ import absolute_import

# ==================================================================================

import os

# ==================================================================================
import numpy as np

from nose.tools import assert_raises, assert_true

# ==================================================================================

from crds.core import utils, log, exceptions
from crds.certify import reftypes
from crds import hst

from crds.tests import test_config

# ==================================================================================


def reftypes_load_type_spec_spec(self):
    """
    >>> old_state = test_config.setup()
    >>> SPEC_FILE = os.path.join(os.path.abspath(hst.HERE), "specs", "acs_biasfile.spec")
    >>> spec = reftypes.TypeSpec.from_file(SPEC_FILE)
    >>> test_config.cleanup(old_state)
    """

def reftypes_load_type_spec_rmap(self):
    """
    >>> old_state = test_config.setup()
    >>> SPEC_FILE = os.path.join(os.path.abspath(hst.HERE), "specs", "cos_xwlkfile.rmap")
    >>> spec = reftypes.TypeSpec.from_file(SPEC_FILE)
    >>> test_config.cleanup(old_state)
    """

# ==================================================================================

class TestReftypes(test_config.CRDSTestCase):

    def setUp(self, *args, **keys):
        super(TestReftypes, self).setUp(*args, **keys)
        self._old_debug = log.set_exception_trap(False)

    def tearDown(self, *args, **keys):
        super(TestReftypes, self).tearDown(*args, **keys)
        log.set_exception_trap(self._old_debug)
        
    # ------------------------------------------------------------------------------
        
    def test_validator_bad_presence(self):
        #         tinfo = certify.TpnInfo('DETECTOR','H','C','Q', ('WFC','HRC','SBC'))
        #         assert_raises(ValueError, certify.validator, tinfo)
        pass
    
# ==================================================================================

def main():
    """Run module tests,  for now just doctests only."""
    import unittest

    suite = unittest.TestLoader().loadTestsFromTestCase(TestReftypes)
    unittest.TextTestRunner().run(suite)

    from crds.tests import test_reftypes, tstmod
    return tstmod(test_reftypes)

if __name__ == "__main__":
    print(main())

