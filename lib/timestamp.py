"""This module contains functions for parsing the datetime formats used by the CDBS
HTML tables and HST FITS data sets.   It contains a formatting function which will render
a date and time in a sortable string representation (isoformat).
"""

import datetime
import re

# =======================================================================

def format_date(d):
    if isinstance(d, (str, unicode)):
        d = parse_date(d)
    return d.isoformat(" ")

def parse_date(d):
    if d.endswith(" UT"):  # Dec 01 1993 00:00:00 UT
        d = d[:-3]
    if "T" in d[3:]:    # '2010-08-17T17:25:47',  not 'OCT...'
        d = d[:3] + d[3:].replace("T", " ")
    if re.match("[A-Za-z]", d):
        return parse_alphabetical_date(d)
    else:
        return parse_numerical_date(d)

def reformat_date(d):
    dt = parse_date(d)
    return format_date(dt)

def now():
    """Returns the timestamp for the current time."""
    return format_date(datetime.datetime.now())

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def month_num(month):
    return  MONTHS.index(month[:3].capitalize()) + 1

def parse_alphabetical_date(d):

    try:
        month, day, year, time = d.split()    # 'Feb 08 2006 01:02AM'
    except ValueError:
        month, day, year = d.split()          # 'Feb 08 2006'
        time = "00:00AM"

    imonth = month_num(month)
    iday = int(day)
    iyear = int(year)

    ampm = "AM"
    if time[-2:] in ["AM","am","PM","pm"]:
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
        if ihour != 12:
            ihour += 12
    else:
        if ihour == 12:
            ihour -= 12

    return datetime.datetime(iyear, imonth, iday, ihour, iminute, isecond, 
                                imicrosecond)


def parse_numerical_date(d):
    date, time = d.split()
    if re.match("\d\d\d\d", date):
        year, month, day = date.split("-")
    else:
        month, day, year = date.split("-")
    imonth, iday, iyear, = int(month), int(day), int(year)
    hour, minute, second = time.split(":")
    second = float(second)
    ihour, iminute, isecond = int(hour), int(minute), int(second)
    imicrosecond = int((second-isecond) * 10**6)
    return datetime.datetime(iyear, imonth, iday, ihour, iminute, isecond, 
                                imicrosecond)

class DateParser(object):
    @classmethod
    def get_datetime(cls, datestr):
        match = cls._format.match(datestr)
        if not match:
            raise ValueError("Invalid " + repr(cls.__name__) + " format " + repr(datestr))
        return datetime.datetime(**cls._get_date_dict(match))

class Slashdate(DateParser):
    _format = re.compile("(?P<day>\d+)\s*/\s*(?P<month>\d+)\s*/\s*(?P<year>\d+)")
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
    """
    _format = re.compile(
                "(?P<month>[A-Za-z]+)\s+" + \
                "(?P<day>\d+)\s+" + \
                "(?P<year>\d+)" + \
                "(\s+(?P<hour>\d+):" + \
                    "(?P<minute>\d+):" + \
                    "(?P<second>\d+)\s*" + \
                    "(?P<meridian>am|pm|AM|PM)?" + \
                ")?")

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
    
class Anydate(DateParser):
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

class Shortdate(DateParser):
    pass

class DashDate(DateParser):
    pass

class CdbsDate(DateParser):
    pass

def test():
    import doctest, timestamp
    return doctest.testmod(timestamp)

if __name__ == "__main__":
    print test()

