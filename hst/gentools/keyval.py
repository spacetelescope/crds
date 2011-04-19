"""This module defines HST's approach to parkeys as they are specified
during the scraping process,  as well as rules used to condition the parameter
values which are matched during the lookup process.  Value conditioning is
project specific and can potentially be avoided altogether.
"""

import re

# ==============================================================================

def parse_parkey(parkey):
    """Break a parkey value into it's parts: special, var, default.

    special:   '*', '%', '!', or ''
        *  -- parkey is optional
        %  -- look inside reffile for parkey,  parkey optional if missing
        !  -- look inside reffile for parkey,  parkey required
        '' -- parkey is required

     var: name of the parkey

     default:  str or None
        value assigned to a * or % parkey which isn't defined by dataset,
        otherwise missing keywords default to *

    >>> parse_parkey('foo=1.0')
    (None, 'foo', '1.0')
    >>> parse_parkey('*foo')
    ('*', 'foo', None)
    >>> parse_parkey('%foo=1.0')
    ('%', 'foo', '1.0')
    >>> parse_parkey('foo')
    (None, 'foo', None)
    """
    if parkey.startswith(("*","%","!")):
        special = parkey[0]
        var = parkey[1:]
    else:
        special = None
        var = parkey
    if "=" in var:
        var, default = var.split("=")
    else:
        default = None
    return special, var, default

def compose_parkey(special, var, default):
    """Re-assemble a parkey from it's parts."""
    if special:
        parkey = special + var
    else:
        parkey = var
    if default:
        parkey =  parkey + "=" + default
    return parkey

# ==============================================================================

DONT_CARE_RE = re.compile("^" + "|".join(["ANY","-999","-999\.0","N/A","\(\)"]) + "$|^$")

NUMBER_RE = re.compile("^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$")

def condition_value(value):
    """Condition `value`,  ostensibly taken from a FITS header or CDBS
    reference file table,  such that it is suitable for appearing in or
    matching an rmap MatchingSelector key.

    >>> condition_value('ANY')
    '*'
    >>> condition_value('-999')
    '*'
    >>> condition_value('-999.0')
    '*'
    >>> condition_value('N/A')
    '*'
    >>> condition_value('')
    '*'
    >>> condition_value(False)
    'F'
    >>> condition_value(True)
    'T'
    >>> condition_value(1)
    '1.0'
    >>> condition_value('-9')
    '-9.0'
    >>> condition_value('1.0')
    '1.0'
    >>> condition_value('foo')
    'FOO'
    >>> condition_value('iref$uaf12559i_drk.fits')
    'IREF$UAF12559I_DRK.FITS'
    """
    value = str(value).strip().upper()
    if NUMBER_RE.match(value):
        value = str(float(value))
    if DONT_CARE_RE.match(value):
        value = "*"
    elif value in ["T", "TRUE"]:
        value = "T"
    elif value in ["F", "FALSE"]:
        value = "F"
    return value

def test():
    import doctest, keyval
    return doctest.testmod(keyval)

if __name__ == "__main__":
    print test()

