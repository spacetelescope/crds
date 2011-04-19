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

MONTHS = {
    "Jan" : 1,
    "Feb" : 2,
    "Mar" : 3,
    "Apr" : 4,
    "May" : 5,
    "Jun" : 6,
    "Jul" : 7,
    "Aug" : 8,
    "Sep" : 9,
    "Oct" : 10,
    "Nov" : 11,
    "Dec" : 12,
}

def parse_alphabetical_date(d):
    try:
        month, day, year, time = d.split()    # 'Feb 08 2006 01:02AM'
    except ValueError:
        month, day, year = d.split()          # 'Feb 08 2006'
        time = "00:00AM"
    imonth = MONTHS[month.capitalize()]
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

