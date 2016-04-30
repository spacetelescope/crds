"""This module contains functions for parsing the datetime formats used by the CDBS
HTML tables and HST FITS data sets.   It contains a formatting function which will render
a date and time in a sortable string representation (isoformat).
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import datetime
import re

import crds
from crds import python23, config, exceptions, log

# =======================================================================

def reformat_date(date):
    """Reformat datestring `d` in any recognized format in CRDS standard form."""
    parsed = parse_date(date)
    return format_date(parsed)

def format_date(date):
    """Format a datestring `d` in CRDS standard form.
    
    >>> format_date("Mar 21 2001 12:00:00 am")
    '2001-03-21 00:00:00'
    """
    if isinstance(date, python23.string_types):
        date = parse_date(date)
    return date.isoformat(" ")

T_SEPERATED_DATE_RE = re.compile(r"^\d\d\d\d[-/]\d\d[-/]\d\dT\d\d:\d\d(:\d\d(:\d\d(.\d+)?)?)?$")
ALPHABETICAL_RE = re.compile(r"[A-Za-z]{3,10}")

def parse_date(date):
    """Parse any date-time string into a datetime object.
    
    >>> parse_date("Dec 01 1993 00:00:00 UT")
    datetime.datetime(1993, 12, 1, 0, 0)
    
    >>> parse_date('Feb 08 2006 01:02AM')
    datetime.datetime(2006, 2, 8, 1, 2)
    
    >>> parse_date('12/21/1999 05:42:35')
    datetime.datetime(1999, 12, 21, 5, 42, 35)

    >>> parse_date('1999-12-21T05:42:35')
    datetime.datetime(1999, 12, 21, 5, 42, 35)

    >>> parse_numerical_date('12-21-1999 05:42')
    datetime.datetime(1999, 12, 21, 5, 42)

    >>> parse_date("19970114:053714")
    datetime.datetime(1997, 1, 14, 5, 37, 14)
    
    >>> dtval = parse_date(datetime.datetime.now())
    >>> isinstance(dtval, datetime.datetime)
    True
    """
    if isinstance(date, datetime.datetime):
        date = str(date)

    if date.endswith(" UT"):  # Dec 01 1993 00:00:00 UT
        date = date[:-3]

    if T_SEPERATED_DATE_RE.match(date):
        date = date.replace("T", " ")
        
    if ALPHABETICAL_RE.search(date):
        return parse_alphabetical_date(date)
    else:
        return parse_numerical_date(date)

def now():
    """Returns the timestamp for the current time."""
    return format_date(datetime.datetime.now())

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def month_num(month, initial_date=None):
    """Convert a month name to a month number."""
    try:
        return  MONTHS.index(month[:3].capitalize()) + 1
    except ValueError:
        raise ValueError("Invalid month value " + repr(month) + " in base date " + repr(initial_date))
    
def parse_alphabetical_date(date):
    """Parse date/time strings with alphabetical months into datetime's.

    >>> parse_alphabetical_date('Feb 08 2006 01:02AM')
    datetime.datetime(2006, 2, 8, 1, 2)

    >>> parse_alphabetical_date('feb 08 2006')
    datetime.datetime(2006, 2, 8, 0, 0)

    >>> parse_alphabetical_date('July 27, 1999 00:00:00')
    datetime.datetime(1999, 7, 27, 0, 0)

    >>> parse_alphabetical_date('JULY 27, 1999 00:00:00')
    datetime.datetime(1999, 7, 27, 0, 0)

    >>> parse_alphabetical_date("03-Jan-2013")
    datetime.datetime(2013, 1, 3, 0, 0)
    
    >>> format_date("Mar 21 2001 12:00:00 am")
    '2001-03-21 00:00:00'
    """
    initial_date = date
    while date.lower().endswith(" am"):
        date = date.lower().replace(" am", "am")
    while date.lower().endswith(" pm"):
        date = date.lower().replace(" pm", "pm")
    
    date = date.replace("-", " ")
    date = date.replace("/", " ")

    try:
        month, day, year, time = date.split()    # 'Feb 08 2006 01:02AM'
    except ValueError:
        month, day, year = date.split()          # 'Feb 08 2006'
        time = "00:00AM"

    if day.endswith(","):     # 
        day = day[:-1]

    try:
        imonth = month_num(month, initial_date)
        iday = int(day)
        iyear = int(year)
    except Exception:
        day, month = month, day
        imonth = month_num(month, initial_date)
        iday = int(day)
        iyear = int(year)

    ihour, iminute, isecond, imicrosecond = parse_time(time)

    return datetime.datetime(iyear, imonth, iday, ihour, iminute, isecond, 
                                imicrosecond)

def parse_time(time):
    """Parse a time string into (hour, minute, second, microsecond), 
    including AM/PM.
    
    >>> parse_time('12:00')
    (12, 0, 0, 0)

    >>> parse_time('01:02AM')
    (1, 2, 0, 0)

    >>> parse_time('01:02PM')
    (13, 2, 0, 0)

    >>> parse_time('13:02PM')
    (13, 2, 0, 0)

    >>> parse_time('13:02 PM')
    (13, 2, 0, 0)

    >>> parse_time(' 13:02 PM ')
    (13, 2, 0, 0)
    
    >>> parse_time('12:42 AM')
    (0, 42, 0, 0)

    """
    time = time.strip()
    ampm = "unspecified"
    if time[-2:].upper() in ["AM", "PM"]:
        ampm = time[-2:].upper()
        time = time[:-2]
    try:
        hour, minute = time.split(":")
        second = "00"
    except ValueError:
        hour, minute, second = time.split(":")
    ihour = int(hour)
    iminute = int(minute)
    second = float(second)
    isecond = int(second)   # int rejects float strs
    imicrosecond = int((second-isecond) * 10**6)
    if ampm == "PM":
        if ihour < 12:
            ihour += 12
    elif ampm == "AM":
        if ihour == 12:
            ihour -= 12
    return ihour, iminute, isecond, imicrosecond

MONTH_DAY_YEAR_RE = re.compile(r"^\d\d/\d\d/\d\d\d\d$")
YEAR_MONTH_DAY_RE = re.compile(r"^\d\d\d\d/\d\d/\d\d$")
NINETEEN_HUNDREDS_RE = re.compile(r"^\d\d/\d\d/9\d$")
TWENTY_FIRST_CENT_RE = re.compile(r"^\d\d/\d\d/[0-3]\d$")
DATE_COLON_TIME_RE = re.compile(r"^\d\d\d\d\d\d\d\d:\d\d\d\d\d\d$")

def parse_numerical_date(dstr):
    """Parse a datetime string with the month expressed as a number in various 
    formats.   Return a datetime object.
    
    >>> parse_numerical_date('12/21/1999 05:42')
    datetime.datetime(1999, 12, 21, 5, 42)
    
    >>> parse_numerical_date('12/21/1999 05:42:35')
    datetime.datetime(1999, 12, 21, 5, 42, 35)
    
    >>> parse_numerical_date('1999-12-21 05:42:00')
    datetime.datetime(1999, 12, 21, 5, 42)
    
    >>> parse_numerical_date('12-21-1999 05:42:00')
    datetime.datetime(1999, 12, 21, 5, 42)

    >>> parse_numerical_date('21/12/99 05:42:00 PM')
    datetime.datetime(1999, 12, 21, 17, 42)

    >>> parse_numerical_date('21/12/01 05:42:00')
    datetime.datetime(2001, 12, 21, 5, 42)

    >>> parse_numerical_date('21/12/15 05:42:00')
    datetime.datetime(2015, 12, 21, 5, 42)

    >>> parse_date("19970114:053714")
    datetime.datetime(1997, 1, 14, 5, 37, 14)
    """
    dstr = dstr.replace("-","/")
    parts = dstr.split()
    date = parts[0]
    if len(parts) == 1:
        time = "00:00:00"
    else:
        time = " ".join(parts[1:])
        
    ihour, iminute, isecond, imicrosecond = parse_time(time)

    if MONTH_DAY_YEAR_RE.match(date):
        month, day, year = date.split("/")
    elif YEAR_MONTH_DAY_RE.match(date):
        year, month, day = date.split("/")
    elif NINETEEN_HUNDREDS_RE.match(date):
        day, month, year = date.split("/")
        year = "19" + year
    elif TWENTY_FIRST_CENT_RE.match(date):
        day, month, year = date.split("/")
        year = "20" + year
    elif DATE_COLON_TIME_RE.match(date):
        year = date[:4]
        month = date[4:6]
        day = date[6:8]
        ihour = int(date[9:11])
        iminute = int(date[11:13])
        isecond = int(date[13:15])
        imicrosecond = 0
    else:
        raise ValueError("Unknown numerical date format: " + repr(dstr))
    
    imonth, iday, iyear, = int(month), int(day), int(year)
 
    return datetime.datetime(iyear, imonth, iday, ihour, iminute, isecond, 
                                imicrosecond)

class DateParser(object):
    _format = re.compile("")
    
    def _get_date_dict(self, match):
        raise NotImplementedError("Data Parser is an abstract class.")
    
    @classmethod
    def get_datetime(cls, datestr):
        match = cls._format.match(datestr)
        if not match:
            raise ValueError("Invalid " + repr(cls.__name__) + " format " + repr(datestr))
        return datetime.datetime(**cls._get_date_dict(match))

class Slashdate(DateParser):
    """
    >>> Slashdate.get_datetime("25 / 12 / 2014")
    datetime.datetime(2014, 12, 25, 0, 0)

    >>> Slashdate.get_datetime(r"25 / 12 x 2014")
    Traceback (most recent call last):
    ...
    ValueError: Invalid 'Slashdate' format '25 / 12 x 2014'
    """
    _format = re.compile(r"(?P<day>\d+)\s*/\s*(?P<month>\d+)\s*/\s*(?P<year>\d+)")
    @classmethod
    def _get_date_dict(cls, match):    
        return dict(month=int(match.group("month")),
                    day=int(match.group("day")),
                    year=int(match.group("year")))
        
class Sybdate(DateParser):
    """
    >>> Sybdate.get_datetime("Mar 21 2001")
    datetime.datetime(2001, 3, 21, 0, 0)

    >>> Sybdate.get_datetime("Mar 21 2001 12:00:00")
    datetime.datetime(2001, 3, 21, 12, 0)
    
    >>> Sybdate.get_datetime("Mar 21 2001 12:00:00 am")
    datetime.datetime(2001, 3, 21, 0, 0)
    
    >>> Sybdate.get_datetime("Mar 21 2001 12:00:00 PM")
    datetime.datetime(2001, 3, 21, 12, 0)

    >>> Sybdate.get_datetime("Mar 21 2001 01:00:00 PM")
    datetime.datetime(2001, 3, 21, 13, 0)

    >>> Sybdate.get_datetime("Mxx 21 2001 01:00:00 PM")
    Traceback (most recent call last):
    ...
    ValueError: Invalid month value 'Mxx'
    """
    _format = re.compile(
                r"(?P<month>[A-Za-z]{1,10})\s+" + \
                r"(?P<day>\d{1,2}),?\s+" + \
                r"(?P<year>\d{1,4})" + \
                r"(\s+(?P<hour>\d{1,2}):" + \
                    r"(?P<minute>\d{1,2}):" + \
                    r"(?P<second>\d{1,2})\s*" + \
                    r"(?P<meridian>am|pm|AM|PM)?" + \
                r")?")

    @classmethod
    def _get_date_dict(cls, match):
        items = match.groupdict()
        try:
            items["month"] = month_num(match.group("month"))
        except IndexError:
            raise ValueError("Illegal month " + repr(match.group("month")))
        if items["meridian"]:
            hour = int(items["hour"])
            if items["meridian"].lower() == "pm":
                if hour < 12:
                    hour += 12
            else:
                if hour == 12:
                    hour -= 12
            items["hour"] = str(hour)
            del items["meridian"]
        return dict([(name, int(x)) for (name, x) in items.items() if x])
    
class Jwstdate(DateParser):
    """
    >>> Jwstdate.get_datetime("2001-03-21T00:00:00")
    datetime.datetime(2001, 3, 21, 0, 0)

    >>> Jwstdate.get_datetime("2001-03-21")
    datetime.datetime(2001, 3, 21, 0, 0)

    >>> Jwstdate.get_datetime("2001-03-21 12:00:00")
    Traceback (most recent call last):
    ...
    ValueError: Invalid 'Jwstdate' format '2001-03-21 12:00:00'
    """
    _format = re.compile(
        r"^(?P<year>\d\d\d\d)\-" + \
            r"(?P<month>\d\d)\-" + \
            r"(?P<day>\d\d)(T" + \
            r"(?P<hour>\d\d):" + \
            r"(?P<minute>\d\d):" + \
            r"(?P<second>\d\d))?$"
        )

    @classmethod
    def _get_date_dict(cls, match):
        items = match.groupdict()
        return dict([(name, int(x)) for (name, x) in items.items() if x])
    
class Anydate(DateParser):
    """
    Historically Anydate was an HST format limited to Sybdate and Slashdate:
    
    >>> Anydate.get_datetime("25 / 12 / 2014")
    datetime.datetime(2014, 12, 25, 0, 0)

    >>> Anydate.get_datetime("Mar 21 2001 12:00:00") 
    datetime.datetime(2001, 3, 21, 12, 0)
    
    Consequently, the CRDS (and JWST FITS) internal time format is not an Anydate:
    
    >>> Anydate.get_datetime("2001-03-21T00:00:00")
    Traceback (most recent call last):
    ...
    ValueError: Invalid Anydate format '2001-03-21T00:00:00'

    This is controversial but conservatism suggests limiting the format to historical possibilities in
    case there is any downstream software incapable of handling the newer CRDS/FITS format.
    """
    
    @classmethod
    def get_datetime(cls, datestr):
        try:
            return Slashdate.get_datetime(datestr)
        except ValueError:
            pass
        try:
            return Sybdate.get_datetime(datestr)
        except ValueError:
            raise ValueError("Invalid Anydate format " + repr(datestr))
    

#class Shortdate(DateParser):
#    pass
#
#class DashDate(DateParser):
#    pass
#
#class CdbsDate(DateParser):
#    pass

# ============================================================================

DATETIME_RE_STR = r"^(\d\d\d\d\-\d\d\-\d\d(\s+|T)\d\d:\d\d:\d\d)$"
DATETIME_RE = re.compile(DATETIME_RE_STR)
DATE_RE_STR = r"^\d\d\d\d\-\d\d\-\d\d$"
TIME_RE_STR = r"^\d\d:\d\d:\d\d$"

def is_datetime(datetime_str):
    """Raise an assertion error if `datetime_str` doesn't look like a CRDS date.
    Otherwise return `datetime_str`.   This is used to match the composite
    datetime string used by the UseAfter selector.
    
    >>> is_datetime('2001-03-21T00:00:00')
    '2001-03-21T00:00:00'
    
    >>> is_datetime('2001-03-21 00:00:00')
    '2001-03-21 00:00:00'
    
    >>> is_datetime('2001-03-99 00:00:00')
    Traceback (most recent call last):
    ...
    CrdsError: day is out of range for month
    
    >>> is_datetime('2001-03-21X00:00:00')
    Traceback (most recent call last):
    ...
    AssertionError: Invalid date/time.  Should be YYYY-MM-DD HH:MM:SS
    """
    assert DATETIME_RE.match(datetime_str), \
        "Invalid date/time.  Should be YYYY-MM-DD HH:MM:SS"
    try:
        parse_date(datetime_str)
    except ValueError as exc:
        raise crds.CrdsError(str(exc))
    return datetime_str


# ============================================================================
def reformat_useafter(rmapping, header):
    """Reformat a USEAFTER date in a standard CRDS form which can be split into
    DATE-OBS and TIME-OBS.   Honor the ALLOW_BAD_USEAFTER to provide a safe default
    for early junk USEAFTER values;  1900-01-01T00:00:00.
    """
    useafter = str(header["USEAFTER"])
    try:
        return reformat_date(useafter)
    except Exception:
        if config.ALLOW_BAD_USEAFTER:
            log.warning("Can't parse USEAFTER =", repr(useafter),
                        "in", repr(rmapping.filename), "faking as '1900-01-01T00:00:00'")
            return reformat_date("1900-01-01T00:00:00")
        else:
            raise exceptions.InvalidUseAfterFormat("Bad USEAFTER time format =", repr(useafter))

# ============================================================================

def test():
    """Run module doctests."""
    import doctest
    from crds import timestamp
    return doctest.testmod(timestamp)

if __name__ == "__main__":
    print(test())

