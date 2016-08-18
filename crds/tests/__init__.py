from __future__ import division # confidence high
from __future__ import print_function
from __future__ import absolute_import

# ==============================================================================

def tstmod(module):
    """Wrap test_config.tstmod to configure standard options throughout CRDS test_config."""
    import doctest
    # doctest.ELLIPSIS_MARKER = '-etc-'
    return doctest.testmod(module, optionflags=doctest.ELLIPSIS)

