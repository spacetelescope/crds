import pytest
import sys
import re
import datetime
sys.path.append("../../")
from crds.bestrefs import bestrefs as br
from crds.core.timestamp import format_date, parse_date
from astropy.time import Time


@pytest.mark.parametrize('line, expected',
                         [
                             (None, None),
                             ('auto', 'auto'),
                             ('Mar 21 2001 12:00:00 am', '2001-03-21 00:00:00'),
                             ('Dec 01 1993 00:00:00 UT', '1993-12-01 00:00:00'),
                             ('Feb 08 2006 01:02AM', '2006-02-08 01:02:00'),
                             ('12/21/1999 05:42:35', '1999-12-21 05:42:35'),
                             ('1999-12-21T05:42:35', '1999-12-21 05:42:35'),
                             ('12-21-1999 05:42', '1999-12-21 05:42:00'),
                             ('19970114:053714', '1997-01-14 05:37:14'),
                         ])
def test_reformat_date_or_auto(line, expected):
    """Test should return date if argument is none, 'auto' if arg is a variation of 'auto',
    or a reformatted date otherwise."""
    assert br.reformat_date_or_auto(line) == expected


@pytest.mark.parametrize('line, expected',
                         [
                             ('\u0068\u0065\u006C\u006C\u006F', "'hello'"),
                         ])
def test_sreprlow(line, expected):
    """Test should return lowercase repr() of input."""
    assert br.sreprlow(line) == expected


