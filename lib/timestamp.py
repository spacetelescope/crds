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
    if "T" in d:    # '2010-08-17T17:25:47'
        d = d.replace("T", " ")
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
        
def parse_alphabetical_date(d):
    try:
        month, day, year, time = d.split()    # 'Feb 08 2006 01:02AM'
    except ValueError:
        month, day, year = d.split()          # 'Feb 08 2006'
        time = "00:00AM"
    imonth = MONTHS.index(month.capitalize()) + 1
    iday = int(day)
    iyear = int(year)
    hour, minute = time.split(":")
    ihour = int(hour)
    iminute = int(minute[:-2])
    if "PM" in minute.upper():
        if ihour != 12:
            ihour += 12
    else:
        if ihour == 12:
            ihour -= 12
    return datetime.datetime(iyear, imonth, iday, ihour, iminute)


def parse_numerical_date(d):
    date, time = d.split()
    if re.match("\d\d\d\d", date):
        year, month, day = date.split("-")
    else:
        month, day, year = date.split("-")
    imonth, iday, iyear, = int(month), int(day), int(year)
    hour, minute, second = time.split(":")
    ihour, iminute, isecond = int(hour), int(minute), int(round(float(second)))
    return datetime.datetime(iyear, imonth, iday, ihour, iminute)

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
    _format = re.compile(
                "(?P<month>[A-Za-z]+)\s+" + \
                "(?P<day>\d+)\s+" + \
                "(?P<year>\d+)" + \
                "(\s+(?P<hour>\d+):" + \
                "(?P<minute>\d+):" + \
                "(?P<second>\d+))?")

    @classmethod
    def _get_date_dict(cls, match):
        items = match.groupdict()
        try:
            items["month"] = MONTHS.index(match.group("month").capitalize()) + 1
        except IndexError:
            raise ValueError("Illegal month " + repr(match.group("month")))
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


